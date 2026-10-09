import csv
from collections import Counter
from pathlib import Path


root = Path(__file__).resolve().parents[1]
source = root / "Crypto - Leads - Personal Phone Enriched.csv"
destination = root / "GHL Import Prep" / "Crypto Brands - Sender Assignment Prep.csv"
field_name = "LT Campaign Crypto Brands Oct 2026 Sender Email"
senders = [
    "cameron@livetransparent.com",
    "cameron@livetransparent.co",
    "cameron@livetransparent.agency",
    "cameron@livetransparent.org",
]

with source.open(encoding="utf-8-sig", newline="") as f:
    source_rows = list(csv.DictReader(f))

with destination.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Email", field_name])
    writer.writeheader()
    for index, row in enumerate(source_rows):
        writer.writerow({"Email": row["Email"].strip(), field_name: senders[index % len(senders)]})

with destination.open(encoding="utf-8-sig", newline="") as f:
    assignment_rows = list(csv.DictReader(f))
counts = Counter(row[field_name] for row in assignment_rows)
print(f"Prepared {len(assignment_rows)} email-keyed sender assignments: {dict(counts)}")
print("No GHL contacts were updated; apply only after authorized import and post-import contact reconciliation.")
