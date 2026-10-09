import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NC = ROOT / "New Campaigns October 2026"
PREP = NC / "GHL Import Prep"

SENDERS = [
    "cameron@livetransparent.com",
    "cameron@livetransparent.co",
    "cameron@livetransparent.agency",
    "cameron@livetransparent.org",
]

BASE_COLS = [
    "First Name", "Last Name", "Email", "Phone", "Corporate Phone", "Title",
    "Business Name", "Apollo Person LinkedIn URL", "Website", "State", "Country",
    "Vertical", "Source", "Apollo Company LinkedIn URL", "Apollo Facebook URL",
    "Apollo Twitter URL",
]

# Crypto: reuse the already-mapped prep file, just append the sender column.
crypto_src = PREP / "Crypto Brands - GHL Import Prep.csv"
crypto_field = "LT Campaign Crypto Brands Oct 2026 Sender Email"
crypto_out = PREP / "Crypto Brands - GHL Import + Sender.csv"

with crypto_src.open(encoding="utf-8-sig", newline="") as f:
    crypto_rows = list(csv.DictReader(f))
with crypto_out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=BASE_COLS + [crypto_field], extrasaction="ignore")
    w.writeheader()
    for i, row in enumerate(crypto_rows):
        out = {c: row.get(c, "") for c in BASE_COLS}
        out[crypto_field] = SENDERS[i % len(SENDERS)]
        w.writerow(out)

# Peptides: map the raw source the same way, plus sender.
pep_src = NC / "Peptides - Leads - Personal Phone Enriched.csv"
pep_field = "LT Campaign Peptides Brands Oct 2026 Sender Email"
pep_out = PREP / "Peptides Brands - GHL Import + Sender.csv"

with pep_src.open(encoding="utf-8-sig", newline="") as f:
    pep_rows = list(csv.DictReader(f))
with pep_out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=BASE_COLS + [pep_field], extrasaction="ignore")
    w.writeheader()
    for i, row in enumerate(pep_rows):
        w.writerow({
            "First Name": (row.get("First Name") or "").strip(),
            "Last Name": (row.get("Last Name") or "").strip(),
            "Email": (row.get("Email") or "").strip(),
            "Phone": (row.get("Phone Number") or "").strip(),
            "Corporate Phone": (row.get("Corporate Phone") or "").strip(),
            "Title": (row.get("Title") or "").strip(),
            "Business Name": (row.get("Business Name") or "").strip(),
            "Apollo Person LinkedIn URL": (row.get("LinkedIn URL") or "").strip(),
            "Website": (row.get("Website") or "").strip(),
            "State": (row.get("State") or "").strip(),
            "Country": (row.get("Country") or "").strip(),
            "Vertical": "Peptides",
            "Source": (row.get("Source") or "").strip(),
            "Apollo Company LinkedIn URL": (row.get("Company Linkedin Url") or "").strip(),
            "Apollo Facebook URL": (row.get("Facebook Url") or "").strip(),
            "Apollo Twitter URL": (row.get("Twitter Url") or "").strip(),
            pep_field: SENDERS[i % len(SENDERS)],
        })

for label, rows, field, out in [
    ("Crypto", crypto_rows, crypto_field, crypto_out),
    ("Peptides", pep_rows, pep_field, pep_out),
]:
    counts = Counter(SENDERS[i % len(SENDERS)] for i in range(len(rows)))
    print(f"{label}: {len(rows)} rows -> {out.name}")
    print(f"   sender split: {dict(counts)}")
