import csv
import time
from collections import Counter
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT / "GHL Import Prep"
SOURCE = ROOT / "Crypto - Leads - Personal Phone Enriched.csv"
OUTPUT = PREP / "Crypto Contacts - Exact Email GHL Reconciliation.csv"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE = "https://services.leadconnectorhq.com"
VERTICAL_FIELD_ID = "ODs8fBt5te5HEfSJ91pY"


def get_pit():
    for line in Path(__file__).resolve().parents[2].joinpath(".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("GHL_PIT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GHL_PIT not found in repository .env")


HEADERS = {
    "Authorization": "Bearer " + get_pit(),
    "Version": "2021-07-28",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
SESSION = requests.Session()


def get_json(url, params=None):
    for attempt in range(6):
        response = SESSION.get(url, headers=HEADERS, params=params, timeout=30)
        if response.status_code == 429:
            time.sleep(min(2 ** attempt, 20))
            continue
        if response.status_code >= 500:
            time.sleep(min(2 ** attempt, 20))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("GHL read remained rate-limited or unavailable after retries")


with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    source_rows = list(csv.DictReader(f))

emails = sorted({(row.get("Email") or "").strip().lower() for row in source_rows if (row.get("Email") or "").strip()})
result_rows = []
errors = 0
vertical_counts = Counter()

for index, email in enumerate(emails, start=1):
    try:
        payload = get_json(
            f"{BASE}/contacts/",
            {"locationId": LOCATION_ID, "query": email, "limit": 100},
        )
        matches = [
            contact
            for contact in payload.get("contacts", [])
            if (contact.get("email") or "").strip().lower() == email
        ]
        matched_by = "email" if matches else "none"
        detail_rows = []
        for contact in matches:
            cid = contact.get("id", "")
            if not cid:
                continue
            detail_payload = get_json(f"{BASE}/contacts/{cid}")
            detail = detail_payload.get("contact") or detail_payload
            vertical = ""
            for field in detail.get("customFields", []) or []:
                if field.get("id") == VERTICAL_FIELD_ID:
                    vertical = str(field.get("value", ""))
                    break
            vertical_counts[vertical or "(blank)"] += 1
            detail_rows.append(
                {
                    "Contact ID": cid,
                    "Existing Email": detail.get("email", ""),
                    "Existing Name": detail.get("name", ""),
                    "Existing Vertical": vertical,
                    "Existing Phone": detail.get("phone", ""),
                    "Existing Tags": "; ".join(detail.get("tags", []) or []),
                }
            )

        if not detail_rows:
            detail_rows = [{
                "Contact ID": "",
                "Existing Email": "",
                "Existing Name": "",
                "Existing Vertical": "",
                "Existing Phone": "",
                "Existing Tags": "",
            }]
        status = "no_match" if not matches else ("exact_one_email_match" if len(matches) == 1 else "multiple_exact_email_matches")
        source = next(row for row in source_rows if (row.get("Email") or "").strip().lower() == email)
        for detail in detail_rows:
            result_rows.append(
                {
                    "Source Email": email,
                    "Source Name": " ".join(filter(None, [source.get("First Name", "").strip(), source.get("Last Name", "").strip()])),
                    "Source Company": source.get("Business Name", ""),
                    "Match Status": status,
                    "Matched By": matched_by if matches else "none",
                    **detail,
                }
            )
    except Exception as exc:
        errors += 1
        source = next(row for row in source_rows if (row.get("Email") or "").strip().lower() == email)
        result_rows.append(
            {
                "Source Email": email,
                "Source Name": " ".join(filter(None, [source.get("First Name", "").strip(), source.get("Last Name", "").strip()])),
                "Source Company": source.get("Business Name", ""),
                "Match Status": "lookup_error",
                "Matched By": "lookup_error",
                "Contact ID": "",
                "Existing Email": "",
                "Existing Name": "",
                "Existing Vertical": "",
                "Existing Phone": "",
                "Existing Tags": "",
            }
        )
    if index % 25 == 0:
        print(f"Read-only email matches checked: {index}/{len(emails)}")
    time.sleep(0.15)

fields = ["Source Email", "Source Name", "Source Company", "Match Status", "Matched By", "Contact ID", "Existing Email", "Existing Name", "Existing Vertical", "Existing Phone", "Existing Tags"]
with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(result_rows)

status_counts = Counter(row["Match Status"] for row in result_rows)
print(f"Source rows: {len(source_rows)}; unique source emails: {len(emails)}")
print(f"Exact email matches: {status_counts['exact_one_email_match']}; multiple exact-email matches: {status_counts['multiple_exact_email_matches']}; no exact email match: {status_counts['no_match']}; lookup errors: {errors}")
print(f"Matched-contact existing Vertical values: {dict(vertical_counts)}")
print(f"Read-only reconciliation saved: {OUTPUT}")
