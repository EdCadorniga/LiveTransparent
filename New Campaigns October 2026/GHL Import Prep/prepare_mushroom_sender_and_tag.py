import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "audit_vertical_sender_fields.csv"
OUT = HERE / "Mushroom Brands - Sender Assignment - Reimport.csv"

SENDER_FIELD = "LT Campaign Mushroom Brands Oct 2026 Sender Email"
SENDERS = [
    "cameron@livetransparent.com",
    "cameron@livetransparent.co",
    "cameron@livetransparent.agency",
    "cameron@livetransparent.org",
]

rows = list(csv.DictReader(AUDIT.open(encoding="utf-8-sig", newline="")))
mush = [r for r in rows if r["Vertical"] == "mushroom"]
mush.sort(key=lambda r: (r["Email"] or "").lower())

with OUT.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Email", SENDER_FIELD])
    w.writeheader()
    for i, r in enumerate(mush):
        w.writerow({
            "Email": r["Email"].strip(),
            SENDER_FIELD: SENDERS[i % len(SENDERS)],
        })

counts = Counter(SENDERS[i % len(SENDERS)] for i in range(len(mush)))
print(f"Rows: {len(mush)}")
print(f"Sender split: {dict(counts)}")
print(f"Output: {OUT}")
