import csv
from pathlib import Path


root = Path(__file__).resolve().parents[1]
source = root / "Crypto - Leads - Personal Phone Enriched.csv"
destination = root / "GHL Import Prep" / "Crypto Brands - GHL Import Prep.csv"

columns = [
    "First Name",
    "Last Name",
    "Email",
    "Phone",
    "Corporate Phone",
    "Title",
    "Business Name",
    "Apollo Person LinkedIn URL",
    "Website",
    "State",
    "Country",
    "Vertical",
    "Source",
    "Apollo Company LinkedIn URL",
    "Apollo Facebook URL",
    "Apollo Twitter URL",
]

with source.open(encoding="utf-8-sig", newline="") as source_file:
    records = list(csv.DictReader(source_file))

with destination.open("w", encoding="utf-8-sig", newline="") as output_file:
    writer = csv.DictWriter(output_file, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in records:
        writer.writerow(
            {
                "First Name": row.get("First Name", "").strip(),
                "Last Name": row.get("Last Name", "").strip(),
                "Email": row.get("Email", "").strip(),
                "Phone": row.get("Phone Number", "").strip(),
                "Corporate Phone": row.get("Corporate Phone", "").strip(),
                "Title": row.get("Title", "").strip(),
                "Business Name": row.get("Business Name", "").strip(),
                "Apollo Person LinkedIn URL": row.get("LinkedIn URL", "").strip(),
                "Website": row.get("Website", "").strip(),
                "State": row.get("State", "").strip(),
                "Country": row.get("Country", "").strip(),
                "Vertical": "Crypto",
                "Source": row.get("Source", "").strip(),
                "Apollo Company LinkedIn URL": row.get("Company Linkedin Url", "").strip(),
                "Apollo Facebook URL": row.get("Facebook Url", "").strip(),
                "Apollo Twitter URL": row.get("Twitter Url", "").strip(),
            }
        )

print(f"Prepared {len(records)} source records: {destination}")
