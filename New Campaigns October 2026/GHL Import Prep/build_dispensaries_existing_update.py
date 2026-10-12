import csv
from collections import Counter
from pathlib import Path

NC = Path("New Campaigns October 2026")
PREP = NC / "GHL Import Prep"
SENDERS = ["cameron@livetransparent.com", "cameron@livetransparent.co",
           "cameron@livetransparent.agency", "cameron@livetransparent.org"]
FIELD = "LT Campaign Cannabis Dispensaries Brands Oct 2026 Sender Email"
VERTICAL = "Cannabis Dispensaries"


def digits(s):
    return "".join(ch for ch in (s or "") if ch.isdigit())


emap, pmap = {}, {}
for fname, keyfn, store in [
    ("Cannabis Dispensaries Contacts - Exact Email GHL Reconciliation.csv", lambda v: (v or "").lower(), emap),
    ("Cannabis Dispensaries Contacts - Exact Phone GHL Reconciliation.csv", digits, pmap),
]:
    with (PREP / fname).open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("Match Status") == "exact_match" and r.get("Contact ID"):
                store.setdefault(keyfn(r.get("Source Value")), []).append(r["Contact ID"])

rows = list(csv.DictReader((NC / "Cannabis Dispenseries - Leads - Personal Phone Enriched.csv").open(encoding="utf-8-sig", newline="")))

out = []
seen = set()
for i, r in enumerate(rows):
    ids = emap.get((r.get("Email") or "").strip().lower()) or pmap.get(digits(r.get("Phone Number")))
    if not ids:
        continue
    cid = ids[0]
    if cid in seen:
        continue
    seen.add(cid)
    out.append({
        "Contact ID": cid,
        "Business Name": (r.get("Business Name") or "").strip(),
        "Vertical": VERTICAL,
        FIELD: SENDERS[i % len(SENDERS)],
    })

dest = PREP / "Cannabis Dispensaries Existing Contacts - Update (Business Name + Vertical).csv"
with dest.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Contact ID", "Business Name", "Vertical", FIELD])
    w.writeheader()
    w.writerows(out)

print(f"Existing-contact update rows: {len(out)} -> {dest.name}")
print(f"sender split: {dict(Counter(r[FIELD] for r in out))}")
print("sample:", out[:3])
