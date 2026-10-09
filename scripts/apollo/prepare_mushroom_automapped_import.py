"""Prepare a Mushroom GHL import CSV with GHL-recognizable column headers.

Reads the staged new-contact + Apollo CSV and writes a normalized copy. This
script does not call GHL/Apollo or modify CRM records.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "New Campaigns October 2026" / "GHL Import Prep"
SOURCE = PREP / "Mushroom New Contacts - Create + Apollo Phone Enrichment.csv"
OUTPUT = PREP / "Mushroom New Contacts - Auto-Mapped + Apollo Phone Enrichment.csv"

HEADER_RENAMES = {
    "Business Name": "Company Name",
    "LinkedIn URL": "Apollo Person LinkedIn URL",
    "Company Linkedin Url": "Apollo Company LinkedIn URL",
    "Facebook Url": "Apollo Facebook URL",
    "Twitter Url": "Apollo Twitter URL",
}
DROP_IF_BLANK = {
    "",  # unnamed empty source column
    "Source Detail (the specific campaign, form, or calendar link tag)",
    "Shared with Ed?",
}
OUTPUT_HEADERS = [
    "First Name",
    "Last Name",
    "Email",
    "Title",
    "Company Name",
    "Corporate Phone",
    "Apollo Person LinkedIn URL",
    "Website",
    "State",
    "Country",
    "Vertical",
    "Source",
    "Apollo Company LinkedIn URL",
    "Apollo Facebook URL",
    "Apollo Twitter URL",
    "Enrich Phone via Apollo",
]


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        source_headers = reader.fieldnames or []
        rows = list(reader)

    required = {
        "First Name",
        "Last Name",
        "Email",
        "Title",
        "Corporate Phone",
        "LinkedIn URL",
        "Business Name",
        "Website",
        "State",
        "Country",
        "Vertical",
        "Source",
        "Company Linkedin Url",
        "Facebook Url",
        "Twitter Url",
        "Enrich Phone via Apollo",
    }
    missing = required.difference(source_headers)
    if missing:
        raise ValueError(f"Prepared CSV is missing source columns: {sorted(missing)}")
    if len(rows) != 111:
        raise ValueError(f"Expected 111 new Mushroom contacts, found {len(rows)}")

    emails = [(row.get("Email") or "").strip().casefold() for row in rows]
    if any(not email for email in emails) or len(set(emails)) != len(emails):
        raise ValueError("Source CSV has blank or duplicate emails")
    if any((row.get("Vertical") or "").strip() != "Mushroom" for row in rows):
        raise ValueError("Unexpected Vertical value in source CSV")
    if any((row.get("Enrich Phone via Apollo") or "").strip() != "Yes" for row in rows):
        raise ValueError("Every new Mushroom contact must retain Apollo queue value Yes")

    for header in DROP_IF_BLANK:
        if header in source_headers and any((row.get(header) or "").strip() for row in rows):
            raise ValueError(f"Refusing to drop nonblank source column: {header!r}")

    output_rows = []
    for row in rows:
        renamed = {
            HEADER_RENAMES.get(header, header): value
            for header, value in row.items()
            if header not in DROP_IF_BLANK
        }
        output_rows.append(renamed)

    if set(output_rows[0]) != set(OUTPUT_HEADERS):
        raise ValueError(
            "Output header mismatch: "
            f"missing={sorted(set(OUTPUT_HEADERS) - set(output_rows[0]))}, "
            f"extra={sorted(set(output_rows[0]) - set(OUTPUT_HEADERS))}"
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Rows: {len(output_rows)}")
    print(f"Unique emails: {len(set(emails))}")
    print(f"Apollo flag Yes: {sum(r['Enrich Phone via Apollo'] == 'Yes' for r in output_rows)}")
    print(f"Nonblank Corporate Phone values: {sum(bool(r['Corporate Phone'].strip()) for r in output_rows)}")
    print(f"Output: {OUTPUT}")
    print("Output headers: " + ", ".join(OUTPUT_HEADERS))


if __name__ == "__main__":
    main()
