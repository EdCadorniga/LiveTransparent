import csv
from collections import Counter
from pathlib import Path

NC = Path("New Campaigns October 2026")
PREP = NC / "GHL Import Prep"

SENDERS = ["cameron@livetransparent.com", "cameron@livetransparent.co",
           "cameron@livetransparent.agency", "cameron@livetransparent.org"]
BASE_COLS = ["First Name", "Last Name", "Email", "Phone", "Corporate Phone", "Title",
             "Business Name", "Apollo Person LinkedIn URL", "Website", "State", "Country",
             "Vertical", "Source", "Apollo Company LinkedIn URL", "Apollo Facebook URL", "Apollo Twitter URL"]
VERTICAL = "Cannabis Dispensaries"
FIELD = "LT Campaign Cannabis Dispensaries Brands Oct 2026 Sender Email"


def digits(s):
    return "".join(ch for ch in (s or "") if ch.isdigit())


em, ph = set(), set()
with (PREP / "Cannabis Dispensaries Contacts - Exact Email GHL Reconciliation.csv").open(encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        if r.get("Match Status") == "exact_match":
            em.add((r["Source Value"] or "").lower())
with (PREP / "Cannabis Dispensaries Contacts - Exact Phone GHL Reconciliation.csv").open(encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        if r.get("Match Status") == "exact_match":
            ph.add(digits(r["Source Value"]))

rows = list(csv.DictReader((NC / "Cannabis Dispenseries - Leads - Personal Phone Enriched.csv").open(encoding="utf-8-sig", newline="")))

new_rows, existing_rows = [], []
for i, r in enumerate(rows):
    sender = SENDERS[i % len(SENDERS)]
    is_existing = (r.get("Email") or "").strip().lower() in em or digits(r.get("Phone Number")) in ph
    if is_existing:
        existing_rows.append({
            "First Name": (r.get("First Name") or "").strip(), "Last Name": (r.get("Last Name") or "").strip(),
            "Email": (r.get("Email") or "").strip(), "Phone": (r.get("Phone Number") or "").strip(),
            "Business Name": (r.get("Business Name") or "").strip(),
            "Existing Vertical": "Cannabis (per GHL readback)",
            FIELD: sender,
        })
    else:
        new_rows.append({
            "First Name": (r.get("First Name") or "").strip(), "Last Name": (r.get("Last Name") or "").strip(),
            "Email": (r.get("Email") or "").strip(), "Phone": (r.get("Phone Number") or "").strip(),
            "Corporate Phone": (r.get("Corporate Phone") or "").strip(), "Title": (r.get("Title") or "").strip(),
            "Business Name": (r.get("Business Name") or "").strip(),
            "Apollo Person LinkedIn URL": (r.get("LinkedIn URL") or "").strip(), "Website": (r.get("Website") or "").strip(),
            "State": (r.get("State") or "").strip(), "Country": (r.get("Country") or "").strip(),
            "Vertical": VERTICAL, "Source": (r.get("Source") or "").strip(),
            "Apollo Company LinkedIn URL": (r.get("Company Linkedin Url") or "").strip(),
            "Apollo Facebook URL": (r.get("Facebook Url") or "").strip(), "Apollo Twitter URL": (r.get("Twitter Url") or "").strip(),
            FIELD: sender,
        })

with (PREP / "Cannabis Dispensaries Brands - GHL Import + Sender.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=BASE_COLS + [FIELD], extrasaction="ignore"); w.writeheader(); w.writerows(new_rows)
with (PREP / "Cannabis Dispensaries Existing Contacts - Review.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["First Name", "Last Name", "Email", "Phone", "Business Name", "Existing Vertical", FIELD], extrasaction="ignore"); w.writeheader(); w.writerows(existing_rows)

print(f"Net-new Dispensaries import: {len(new_rows)} rows | sender={dict(Counter(r[FIELD] for r in new_rows))}")
print(f"Existing Dispensaries contacts (review): {len(existing_rows)} rows")
