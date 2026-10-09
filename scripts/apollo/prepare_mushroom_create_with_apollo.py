"""Prepare the staged Mushroom contact-create CSV with Apollo phone queue flag.

Reads only the previously reconciled local creation CSV and writes a new local
CSV. It does not call GHL/Apollo or modify CRM records.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "New Campaigns October 2026" / "GHL Import Prep"
SOURCE = PREP / "Mushroom New Contacts - Create.csv"
OUTPUT = PREP / "Mushroom New Contacts - Create + Apollo Phone Enrichment.csv"
APOLLO_FIELD = "Enrich Phone via Apollo"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        rows = list(reader)
        original_fields = reader.fieldnames or []

    required = {"First Name", "Last Name", "Email", "Corporate Phone", "Vertical"}
    missing = required.difference(original_fields)
    if missing:
        raise ValueError(f"Prepared source CSV is missing columns: {sorted(missing)}")
    if APOLLO_FIELD in original_fields:
        raise ValueError(f"Source already contains {APOLLO_FIELD}; refusing duplicate column")

    emails = [(row.get("Email") or "").strip().casefold() for row in rows]
    if any(not email for email in emails):
        raise ValueError("Prepared create CSV contains a blank email")
    if len(emails) != len(set(emails)):
        raise ValueError("Prepared create CSV contains duplicate emails")
    if any((row.get("Vertical") or "").strip() != "Mushroom" for row in rows):
        raise ValueError("Prepared create CSV contains an unexpected Vertical value")

    for row in rows:
        row[APOLLO_FIELD] = "Yes"

    fields = [*original_fields, APOLLO_FIELD]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    phone_rows = sum(bool((row.get("Corporate Phone") or "").strip()) for row in rows)
    print(f"Prepared Mushroom contacts: {len(rows)}")
    print(f"Unique nonblank emails: {len(set(emails))}")
    print(f"Source phones preserved as Corporate Phone: {phone_rows}")
    print(f"Apollo flag Yes: {sum(row[APOLLO_FIELD] == 'Yes' for row in rows)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
