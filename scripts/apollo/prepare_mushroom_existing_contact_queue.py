"""Stage Apollo queue updates for reconciled Mushroom contacts already in GHL.

The exact-email matches were reclassified in GHL. Two are already Apollo
enriched, so only the five remaining eligible contacts are included here.
This writes a local CSV only; it does not call GHL or Apollo.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "New Campaigns October 2026" / "GHL Import Prep"
SOURCE = PREP / "Mushroom Review - Cross-Vertical and Jill Holds.csv"
OUTPUT = PREP / "Mushroom Existing Contacts - Vertical and Apollo Phone Enrichment.csv"

# Contact IDs were reconciled to exact source emails and freshly read from GHL
# on 2026-10-08. Jill and Christopher already have Apollo status `enriched`.
QUEUE_CONTACTS = {
    "kylee@ommushrooms.com": "4nosJTSPqasgf8hWTXTR",
    "cnadeau@koicbd.com": "UqcKoEkyKsDbGQb7q1HO",
    "madison@foursigmatic.com": "gDEeKCPhfaMXcNQDrUOv",
    "matt@grassandco.com": "s0K1jYuXlL2R8IBoBbkw",
    "aaron@drinkbrez.com": "qE3Xx8kZIdOLrLcioOwz",
}
ALREADY_ENRICHED = {"jill@foursigmatic.com", "cshields11@gmail.com"}


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        rows = list(csv.DictReader(source_file))

    source_emails = {(row.get("Email") or "").strip().casefold() for row in rows}
    expected = set(QUEUE_CONTACTS) | ALREADY_ENRICHED
    if source_emails != expected:
        raise ValueError(
            "The cross-vertical review CSV changed; reconcile IDs before regenerating. "
            f"Missing={sorted(expected - source_emails)}, extra={sorted(source_emails - expected)}"
        )

    output_rows = [
        {
            "Contact Id": contact_id,
            "Vertical": "Mushroom",
            "Enrich Phone via Apollo": "Yes",
        }
        for email, contact_id in QUEUE_CONTACTS.items()
    ]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["Contact Id", "Vertical", "Enrich Phone via Apollo"],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Existing Mushroom contacts queued: {len(output_rows)}")
    print(f"Already Apollo-enriched; skipped: {len(ALREADY_ENRICHED)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
