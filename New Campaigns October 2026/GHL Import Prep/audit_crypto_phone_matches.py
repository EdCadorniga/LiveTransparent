import csv
import re
import time
from collections import Counter
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Crypto - Leads - Personal Phone Enriched.csv"
OUTPUT = ROOT / "GHL Import Prep" / "Crypto Contacts - Exact Phone GHL Reconciliation.csv"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE = "https://services.leadconnectorhq.com"

pit = next(
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in Path(__file__).resolve().parents[2].joinpath(".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("GHL_PIT=")
)
headers = {
    "Authorization": "Bearer " + pit,
    "Version": "2021-07-28",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
session = requests.Session()


def digits(value):
    return re.sub(r"\D", "", value or "")


def find_phone_matches(phone):
    source_digits = digits(phone)
    found = {}
    for query in (phone, source_digits):
        if not query:
            continue
        for attempt in range(6):
            r = session.get(
                f"{BASE}/contacts/",
                headers=headers,
                params={"locationId": LOCATION_ID, "query": query, "limit": 100},
                timeout=30,
            )
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(2 ** attempt, 20))
                continue
            r.raise_for_status()
            for contact in r.json().get("contacts", []):
                if digits(contact.get("phone")) == source_digits and source_digits:
                    found[contact.get("id", "")] = contact
            break
        else:
            raise RuntimeError("GHL phone lookup remained unavailable after retries")
        if found:
            break
    return list(found.values())


with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
phones = {}
for row in rows:
    phone = (row.get("Phone Number") or "").strip()
    if phone:
        phones.setdefault(digits(phone), (phone, row))

out = []
errors = 0
counts = Counter()
for index, (phone, row) in enumerate(phones.values(), start=1):
    try:
        matches = find_phone_matches(phone)
        status = "no_exact_phone_match" if not matches else ("one_exact_phone_match" if len(matches) == 1 else "multiple_exact_phone_matches")
        counts[status] += 1
        if not matches:
            matches = [{}]
        for contact in matches:
            out.append({
                "Source Email": (row.get("Email") or "").strip().lower(),
                "Source Phone": phone,
                "Source Company": row.get("Business Name", ""),
                "Match Status": status,
                "Contact ID": contact.get("id", ""),
                "Existing Email": contact.get("email", ""),
                "Existing Name": contact.get("name", ""),
                "Existing Phone": contact.get("phone", ""),
            })
    except Exception:
        errors += 1
        out.append({
            "Source Email": (row.get("Email") or "").strip().lower(),
            "Source Phone": phone,
            "Source Company": row.get("Business Name", ""),
            "Match Status": "lookup_error",
            "Contact ID": "",
            "Existing Email": "",
            "Existing Name": "",
            "Existing Phone": "",
        })
    if index % 25 == 0:
        print(f"Read-only distinct primary-phone checks: {index}/{len(phones)}")
    time.sleep(0.15)

fields = ["Source Email", "Source Phone", "Source Company", "Match Status", "Contact ID", "Existing Email", "Existing Name", "Existing Phone"]
with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out)

print(f"Distinct populated source primary phones: {len(phones)}")
print(f"Exact phone match summary: {dict(counts)}; lookup errors: {errors}")
print(f"Read-only phone reconciliation saved: {OUTPUT}")
