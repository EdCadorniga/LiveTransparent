"""Read-only preflight audit for the October 2026 Nicotine contact import.

Loads GHL_PIT from the repository .env without printing it, then searches the
official GHL Contacts endpoint by source email and corporate phone. This script
does not create or update contacts and writes no response artifacts.
"""

from __future__ import annotations

import csv
import argparse
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
SOURCE = ROOT / "New Campaigns October 2026" / "Nicotine Leads (1).csv"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE_URL = "https://services.leadconnectorhq.com/contacts/"
VERSION = "2021-07-28"
VERTICAL_FIELD_ID = "ODs8fBt5te5HEfSJ91pY"
SENDER_FIELD_ID = "oFHCH0QL8wsrkHiXKE3F"
SENDER_FIELD_NAME = "LT Campaign Nicotine Brands Oct 2026 Sender Email"
NONBRAND_RE = re.compile(
    r"the breathing association|wequit\s*-\s*stoppen met roken en vapen|"
    r"allen carr france|parents against vaping|truth initiative|quit with jones|"
    r"quitsure|quittas|baby\s*&\s*me tobacco free program|satori recovery|"
    r"tobacco free florida",
    re.I,
)


def normalize_phone(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def read_source() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def search_contacts(token: str, query: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": VERSION,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 LiveTransparentImportPreflight/1.0",
    }
    for attempt in range(5):
        response = requests.get(
            BASE_URL,
            headers=headers,
            params={"locationId": LOCATION_ID, "query": query, "limit": 100},
            timeout=30,
        )
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


def custom_field(contact: dict, field_id: str) -> str:
    for field in contact.get("customFields", []) or []:
        if str(field.get("id")) == field_id:
            return str(field.get("value") or "")
    return ""


def csv_write(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="write import/review CSVs after the read-only GHL reconciliation",
    )
    args = parser.parse_args()

    token = dotenv_values(ROOT / ".env").get("GHL_PIT")
    if not token:
        print(json.dumps({"error": "GHL_PIT is unavailable in the repository .env"}))
        return 2

    rows = read_source()
    email_to_rows: dict[str, list[int]] = defaultdict(list)
    phone_to_rows: dict[str, list[int]] = defaultdict(list)
    phone_raw: dict[str, str] = {}
    blank_email = 0
    blank_phone = 0
    for row_number, row in enumerate(rows, start=2):
        email = (row.get("Email") or "").strip().casefold()
        phone = (row.get("Corporate Phone") or "").strip()
        normalized_phone = normalize_phone(phone)
        if email:
            email_to_rows[email].append(row_number)
        else:
            blank_email += 1
        if normalized_phone:
            phone_to_rows[normalized_phone].append(row_number)
            phone_raw.setdefault(normalized_phone, phone)
        else:
            blank_phone += 1

    email_queries = sorted(email_to_rows)
    with ThreadPoolExecutor(max_workers=4) as pool:
        email_results = list(pool.map(lambda email: search_contacts(token, email), email_queries))

    existing_by_email: dict[str, list[dict]] = defaultdict(list)
    email_http_errors: Counter = Counter()
    for email, result in zip(email_queries, email_results):
        status = result.get("_status")
        if status is not None:
            email_http_errors[str(status)] += 1
            continue
        for contact in result.get("contacts", []) or []:
            if (contact.get("email") or "").strip().casefold() == email:
                existing_by_email[email].append(contact)

    # Search unique source phones in GHL and compare returned *primary* phone
    # values exactly after digit normalization; custom Corporate Phone values do
    # not count as the GHL primary phone.
    unique_phone_queries = sorted(phone_to_rows)
    with ThreadPoolExecutor(max_workers=4) as pool:
        phone_results = list(
            pool.map(lambda number: search_contacts(token, phone_raw[number]), unique_phone_queries)
        )

    global_phone_hits: dict[str, set[str]] = defaultdict(set)
    phone_http_errors: Counter = Counter()
    for queried_phone, result in zip(unique_phone_queries, phone_results):
        status = result.get("_status")
        if status is not None:
            phone_http_errors[str(status)] += 1
            continue
        for contact in result.get("contacts", []) or []:
            contact_phone = normalize_phone(contact.get("phone"))
            if contact_phone and contact_phone == queried_phone:
                global_phone_hits[queried_phone].add(str(contact.get("id") or "unknown"))

    vertical_counts = Counter()
    sender_counts = Counter()
    current_primary_collisions: Counter = Counter()
    nicotine_primary_phones: Counter = Counter()
    matches_multiple = 0
    for email, contacts in existing_by_email.items():
        if len(contacts) > 1:
            matches_multiple += 1
        for contact in contacts:
            vertical = custom_field(contact, VERTICAL_FIELD_ID) or "(blank)"
            vertical_counts[vertical] += 1
            sender_counts[custom_field(contact, SENDER_FIELD_ID) or "(blank)"] += 1
            primary = normalize_phone(contact.get("phone"))
            if primary:
                current_primary_collisions[primary] += 1
                if vertical == "Nicotine":
                    nicotine_primary_phones[primary] += 1

    nonbrand_rows = [
        row
        for row in rows
        if NONBRAND_RE.search(" ".join([row.get("Business Name", ""), row.get("Website", "")]))
    ]
    existing_verticals_by_email = {
        email: [custom_field(contact, VERTICAL_FIELD_ID) for contact in contacts]
        for email, contacts in existing_by_email.items()
    }
    cross_vertical_emails = {
        email
        for email, verticals in existing_verticals_by_email.items()
        if any(value and value != "Nicotine" for value in verticals)
    }
    existing_same_campaign_emails = set(existing_by_email) - cross_vertical_emails
    cross_vertical_rows = [
        row for row in rows if (row.get("Email") or "").strip().casefold() in cross_vertical_emails
    ]
    missing_email_brand_rows = [
        row
        for row in rows
        if not (row.get("Email") or "").strip()
        and not NONBRAND_RE.search(" ".join([row.get("Business Name", ""), row.get("Website", "")]))
    ]
    nonbrand_emails = {
        (row.get("Email") or "").strip().casefold() for row in nonbrand_rows if (row.get("Email") or "").strip()
    }
    excluded_emails = cross_vertical_emails | nonbrand_emails
    eligible_rows = [row for row in rows if (row.get("Email") or "").strip().casefold() not in excluded_emails and not NONBRAND_RE.search(" ".join([row.get("Business Name", ""), row.get("Website", "")]))]
    import_rows = [
        row.copy()
        for row in eligible_rows
        if (row.get("Email") or "").strip()
        and (row.get("Email") or "").strip().casefold() not in existing_by_email
    ]
    existing_update_rows = [
        row.copy()
        for row in eligible_rows
        if (row.get("Email") or "").strip().casefold() in existing_same_campaign_emails
    ]
    for row in import_rows:
        row["Vertical"] = "Nicotine"

    eligible_phone_counts = Counter(
        normalize_phone(row.get("Corporate Phone"))
        for row in eligible_rows
        if normalize_phone(row.get("Corporate Phone"))
    )
    phone_update_rows = [
        {"Email": row["Email"].strip(), "Phone": row["Corporate Phone"].strip()}
        for row in import_rows
        if normalize_phone(row.get("Corporate Phone"))
        and eligible_phone_counts[normalize_phone(row.get("Corporate Phone"))] == 1
        and not global_phone_hits.get(normalize_phone(row.get("Corporate Phone")))
    ]

    sender_addresses = [
        "cameron@livetransparent.com",
        "cameron@livetransparent.co",
        "cameron@livetransparent.agency",
        "cameron@livetransparent.org",
    ]
    sender_rows = []
    sender_candidate_rows = [
        row
        for row in eligible_rows
        if (row.get("Email") or "").strip()
        and (row.get("Email") or "").strip().casefold() not in existing_by_email
    ]
    for index, row in enumerate(sorted(sender_candidate_rows, key=lambda r: r["Email"].strip().casefold())):
        sender_rows.append(
            {
                "Email": row["Email"].strip(),
                SENDER_FIELD_NAME: sender_addresses[index % len(sender_addresses)],
            }
        )

    if args.prepare:
        prep = SOURCE.parent / "GHL Import Prep"
        columns = list(rows[0].keys())
        csv_write(prep / "Nicotine New Contacts - Create.csv", columns, import_rows)
        if existing_update_rows:
            csv_write(
                prep / "Nicotine Existing Contacts - Vertical Updates.csv",
                ["Email", "Vertical"],
                [{"Email": r["Email"], "Vertical": "Nicotine"} for r in existing_update_rows],
            )
        csv_write(
            prep / "Nicotine New Contacts - Unique Corporate Phones - Primary Phone Update.csv",
            ["Email", "Phone"],
            phone_update_rows,
        )
        csv_write(prep / "Nicotine Sender Assignment.csv", ["Email", SENDER_FIELD_NAME], sender_rows)
        csv_write(prep / "Nicotine Review - Existing Cross-Vertical Contacts.csv", columns, cross_vertical_rows)
        csv_write(prep / "Nicotine Review - Nonbrand Rows.csv", columns, nonbrand_rows)
        csv_write(prep / "Nicotine Review - Missing Email Rows.csv", columns, missing_email_brand_rows)

    output = {
        "source_rows": len(rows),
        "source_vertical_values": dict(Counter((r.get("Vertical") or "").strip() for r in rows)),
        "nonblank_unique_emails": len(email_queries),
        "blank_email_rows": blank_email,
        "duplicate_source_email_groups": sum(len(v) > 1 for v in email_to_rows.values()),
        "existing_email_match_count": len(existing_by_email),
        "existing_email_match_rows": sum(len(v) for v in existing_by_email.values()),
        "email_with_multiple_ghl_matches": matches_multiple,
        "existing_cross_vertical_source_rows": [
            {"row": email_to_rows[email][0], "verticals": existing_verticals_by_email.get(email, [])}
            for email in sorted(existing_by_email)
            if email in email_to_rows and email in cross_vertical_emails
        ],
        "existing_vertical_counts": dict(vertical_counts),
        "existing_sender_field_counts": dict(sender_counts),
        "nicotine_email_matched_contacts_with_primary_phone": sum(nicotine_primary_phones.values()),
        "duplicate_primary_phone_groups_within_nicotine_email_matches": sum(
            count > 1 for count in nicotine_primary_phones.values()
        ),
        "source_rows_with_corporate_phone": len(rows) - blank_phone,
        "source_rows_without_corporate_phone": blank_phone,
        "unique_normalized_source_phones": len(phone_to_rows),
        "shared_source_phone_groups": sum(len(v) > 1 for v in phone_to_rows.values()),
        "rows_in_shared_source_phone_groups": sum(len(v) for v in phone_to_rows.values() if len(v) > 1),
        "extra_rows_in_shared_source_phone_groups": sum(len(v) - 1 for v in phone_to_rows.values() if len(v) > 1),
        "source_phone_values_matching_existing_primary_phone": sum(bool(v) for v in global_phone_hits.values()),
        "nicotine_rows_with_source_phones_matching_existing_primary_phone": sum(
            len(phone_to_rows[number]) for number, ids in global_phone_hits.items() if ids
        ),
        "ghl_primary_phone_values_returned_for_multiple_existing_contacts": sum(
            len(ids) > 1 for ids in global_phone_hits.values()
        ),
        "email_search_errors": dict(email_http_errors),
        "phone_search_errors": dict(phone_http_errors),
        "phone_search_completeness": f"{len(unique_phone_queries) - sum(phone_http_errors.values())}/{len(unique_phone_queries)}",
        "clear_nonbrand_rows_held_for_review": len(nonbrand_rows),
        "existing_cross_vertical_rows_held_for_review": len(cross_vertical_rows),
        "missing_email_rows_held_for_review": len(missing_email_brand_rows),
        "new_email_contact_rows_prepared": len(import_rows),
        "existing_same_campaign_vertical_update_rows_prepared": len(existing_update_rows),
        "eligible_email_rows_including_existing": len(sender_candidate_rows),
        "unique_nonshared_primary_phone_updates_prepared": len(phone_update_rows),
        "sender_assignments_prepared": len(sender_rows),
        "preparation_files_written": bool(args.prepare),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not email_http_errors and not phone_http_errors else 1


if __name__ == "__main__":
    sys.exit(main())
