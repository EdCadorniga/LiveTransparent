"""Prepare a GHL import file to queue contacts for Apollo phone enrichment.

This script only writes a local CSV. It does not call Apollo or modify GHL.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "New Campaigns October 2026" / "Export_Contacts_All Verticals Oct 2026 Outbound_Oct_2026_8_24_PM.csv"
OUTPUT = ROOT / "New Campaigns October 2026" / "GHL Import Prep" / "All Verticals - Apollo Phone Enrichment Queue.csv"
CORPORATE_PHONE_OUTPUT = ROOT / "New Campaigns October 2026" / "GHL Import Prep" / "All Verticals - Preserve Existing Phones as Corporate Phone.csv"
ALREADY_ENRICHED_CONTACT_IDS = {"FTCWeS26CKKKGDCOTIWS"}  # Courtney McElligott test completed successfully.


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        required = {"Contact Id", "Phone", "Email"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Source CSV is missing required columns: {sorted(missing)}")

        rows = list(reader)

    seen_ids: set[str] = set()
    queued: list[dict[str, str]] = []
    corporate_phone_rows: list[dict[str, str]] = []
    duplicate_ids: list[str] = []
    for row in rows:
        contact_id = (row.get("Contact Id") or "").strip()
        if not contact_id:
            continue
        if contact_id in seen_ids:
            duplicate_ids.append(contact_id)
            continue
        seen_ids.add(contact_id)

        if contact_id in ALREADY_ENRICHED_CONTACT_IDS:
            continue

        queued.append({"Contact Id": contact_id, "Enrich Phone via Apollo": "Yes"})
        existing_phone = (row.get("Phone") or "").strip()
        if existing_phone:
            corporate_phone_rows.append(
                {"Contact Id": contact_id, "Corporate Phone": existing_phone}
            )

    if duplicate_ids:
        raise ValueError(f"Duplicate Contact Id values found: {sorted(set(duplicate_ids))}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["Contact Id", "Enrich Phone via Apollo"],
        )
        writer.writeheader()
        writer.writerows(queued)

    with CORPORATE_PHONE_OUTPUT.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["Contact Id", "Corporate Phone"],
        )
        writer.writeheader()
        writer.writerows(corporate_phone_rows)

    print(f"Source rows: {len(rows)}")
    print(f"Unique contacts: {len(seen_ids)}")
    print(f"Already enriched test contact; excluded: {len(ALREADY_ENRICHED_CONTACT_IDS)}")
    print(f"Existing phone values staged for Corporate Phone: {len(corporate_phone_rows)}")
    print(f"Queued for Apollo: {len(queued)}")
    print(f"Prepared import: {OUTPUT}")
    print(f"Prepared phone-preservation import: {CORPORATE_PHONE_OUTPUT}")


if __name__ == "__main__":
    main()
