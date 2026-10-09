"""Read-only GHL preflight and local CSV preparation for Mushroom outreach.

The script performs exact-email reconciliation and phone-collision checks via
the documented Contacts API. It only writes local prep CSVs; it never mutates
GHL contacts, sender fields, tags, or workflow enrollment.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "New Campaigns October 2026" / "Mushroom Brands Leads - Leads (1).csv"
PREP = SOURCE.parent / "GHL Import Prep"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE_URL = "https://services.leadconnectorhq.com/contacts/"
VERSION = "2021-07-28"
VERTICAL_FIELD_ID = "ODs8fBt5te5HEfSJ91pY"
SENDER_FIELD_ID = "IJ1yrUihuKD7DkLgWHYM"
SENDER_FIELD_NAME = "LT Campaign Mushroom Brands Oct 2026 Sender Email"
JILL_EMAIL = "jill@foursigmatic.com"
SENDERS = [
    "cameron@livetransparent.com",
    "cameron@livetransparent.co",
    "cameron@livetransparent.agency",
    "cameron@livetransparent.org",
]


def norm_email(value: str | None) -> str:
    return (value or "").strip().casefold()


def norm_phone(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def read_source() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    PREP.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def search_contacts(token: str, query: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": VERSION,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 LiveTransparentMushroomPreflight/1.0",
    }
    for attempt in range(5):
        try:
            response = requests.get(
                BASE_URL,
                headers=headers,
                params={"locationId": LOCATION_ID, "query": query, "limit": 100},
                timeout=30,
            )
        except requests.RequestException as exc:
            if attempt == 4:
                return {"_status": f"request_error:{type(exc).__name__}"}
            time.sleep(0.5 * (attempt + 1))
            continue
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(0.5 * (attempt + 1))
            continue
        if response.status_code != 200:
            return {"_status": response.status_code}
        try:
            return response.json()
        except ValueError:
            return {"_status": "invalid_json"}
    return {"_status": "retry_exhausted"}


def field_value(contact: dict, field_id: str) -> str:
    for field in contact.get("customFields", []) or []:
        if str(field.get("id")) == field_id:
            return str(field.get("value") or "")
    return ""


def main() -> int:
    token = dotenv_values(ROOT / ".env").get("GHL_PIT")
    if not token:
        print(json.dumps({"error": "GHL_PIT is unavailable in the repository .env"}))
        return 2

    rows = read_source()
    if not rows:
        print(json.dumps({"error": "Mushroom source CSV is empty"}))
        return 2

    emails: dict[str, list[int]] = defaultdict(list)
    phones: dict[str, list[int]] = defaultdict(list)
    raw_phone: dict[str, str] = {}
    for row_number, row in enumerate(rows, start=2):
        email = norm_email(row.get("Email"))
        phone = (row.get("Corporate Phone") or "").strip()
        if email:
            emails[email].append(row_number)
        normalized = norm_phone(phone)
        if normalized:
            phones[normalized].append(row_number)
            raw_phone.setdefault(normalized, phone)

    unique_emails = sorted(emails)
    with ThreadPoolExecutor(max_workers=4) as pool:
        email_results = list(pool.map(lambda e: search_contacts(token, e), unique_emails))

    matches: dict[str, list[dict]] = defaultdict(list)
    email_errors: Counter = Counter()
    for email, result in zip(unique_emails, email_results):
        status = result.get("_status")
        if status is not None:
            email_errors[str(status)] += 1
            continue
        for contact in result.get("contacts", []) or []:
            if norm_email(contact.get("email")) == email:
                matches[email].append(contact)

    unique_phones = sorted(phones)
    with ThreadPoolExecutor(max_workers=4) as pool:
        phone_results = list(pool.map(lambda p: search_contacts(token, raw_phone[p]), unique_phones))

    ghl_primary_by_phone: dict[str, set[str]] = defaultdict(set)
    phone_errors: Counter = Counter()
    for number, result in zip(unique_phones, phone_results):
        status = result.get("_status")
        if status is not None:
            phone_errors[str(status)] += 1
            continue
        for contact in result.get("contacts", []) or []:
            if norm_phone(contact.get("phone")) == number:
                ghl_primary_by_phone[number].add(str(contact.get("id") or "unknown"))

    jill_rows = [row.copy() for row in rows if norm_email(row.get("Email")) == JILL_EMAIL]
    cross_vertical_emails = {
        email
        for email, contacts in matches.items()
        if any((field_value(c, VERTICAL_FIELD_ID) or "") != "Mushroom" for c in contacts)
    }
    held_emails = cross_vertical_emails | {JILL_EMAIL}
    existing_rows = [
        row.copy()
        for row in rows
        if norm_email(row.get("Email")) in matches and norm_email(row.get("Email")) not in held_emails
    ]
    new_rows = [
        row.copy()
        for row in rows
        if norm_email(row.get("Email")) not in matches
        and norm_email(row.get("Email")) not in held_emails
        and norm_email(row.get("Email"))
    ]
    for row in new_rows:
        row["Vertical"] = "Mushroom"

    # Source Corporate Phone groups are treated as company-level only. A primary
    # phone update is prepared only when the value is unique in the source and
    # no existing GHL contact already uses it as a primary phone.
    shared_phones = {number for number, source_rows in phones.items() if len(source_rows) > 1}
    phone_update_rows = [
        {"Email": row["Email"].strip(), "Phone": (row.get("Corporate Phone") or "").strip()}
        for row in new_rows
        if norm_phone(row.get("Corporate Phone"))
        and norm_phone(row.get("Corporate Phone")) not in shared_phones
        and not ghl_primary_by_phone.get(norm_phone(row.get("Corporate Phone")))
    ]

    # Preserve existing values and balance only the prepared new-contact cohort.
    sender_counts = Counter(
        field_value(contact, SENDER_FIELD_ID)
        for contacts in matches.values()
        for contact in contacts
        if field_value(contact, VERTICAL_FIELD_ID) == "Mushroom"
        and field_value(contact, SENDER_FIELD_ID) in SENDERS
    )
    sender_rows: list[dict[str, str]] = []
    for row in sorted(new_rows, key=lambda r: norm_email(r.get("Email"))):
        sender = min(SENDERS, key=lambda candidate: (sender_counts[candidate], SENDERS.index(candidate)))
        sender_rows.append({"Email": row["Email"].strip(), SENDER_FIELD_NAME: sender})
        sender_counts[sender] += 1

    columns = list(rows[0].keys())
    write_csv(PREP / "Mushroom New Contacts - Create.csv", columns, new_rows)
    write_csv(PREP / "Mushroom Review - Existing Contacts.csv", columns, existing_rows)
    write_csv(PREP / "Mushroom Review - Cross-Vertical and Jill Holds.csv", columns, [r.copy() for r in rows if norm_email(r.get("Email")) in held_emails])
    write_csv(PREP / "Mushroom Review - Shared Corporate Phones.csv", columns, [r.copy() for r in rows if norm_phone(r.get("Corporate Phone")) in shared_phones])
    write_csv(PREP / "Mushroom Sender Assignment.csv", ["Email", SENDER_FIELD_NAME], sender_rows)
    write_csv(PREP / "Mushroom New Contacts - Unique Corporate Phones - Primary Phone Update.csv", ["Email", "Phone"], phone_update_rows)

    vertical_counts = Counter(
        field_value(contact, VERTICAL_FIELD_ID) or "(blank)"
        for contacts in matches.values()
        for contact in contacts
    )
    report = {
        "source_rows": len(rows),
        "unique_nonblank_emails": len(unique_emails),
        "duplicate_source_email_groups": {email: rownums for email, rownums in emails.items() if len(rownums) > 1},
        "existing_exact_email_groups": len(matches),
        "existing_exact_email_contacts": sum(map(len, matches.values())),
        "existing_vertical_counts": dict(vertical_counts),
        "cross_vertical_email_holds": sorted(cross_vertical_emails),
        "jill_hold_rows": emails.get(JILL_EMAIL, []),
        "source_shared_corporate_phone_groups": len(shared_phones),
        "rows_with_shared_corporate_phones": sum(len(phones[p]) for p in shared_phones),
        "primary_phone_update_candidates": len(phone_update_rows),
        "new_contact_rows_prepared": len(new_rows),
        "existing_same_vertical_rows_review_only": len(existing_rows),
        "sender_assignment_candidates": len(sender_rows),
        "prepared_sender_counts": dict(Counter(r[SENDER_FIELD_NAME] for r in sender_rows)),
        "email_search_errors": dict(email_errors),
        "phone_search_errors": dict(phone_errors),
        "phone_search_completeness": f"{len(unique_phones) - sum(phone_errors.values())}/{len(unique_phones)}",
        "files_written_under": str(PREP.relative_to(ROOT)),
        "writes_to_ghl": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not email_errors and not phone_errors else 1


if __name__ == "__main__":
    sys.exit(main())
