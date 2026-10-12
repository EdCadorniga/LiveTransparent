import csv
import time
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
NC = ROOT / "New Campaigns October 2026"
PREP = NC / "GHL Import Prep"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
BASE = "https://services.leadconnectorhq.com"
VERTICAL_FIELD_ID = "ODs8fBt5te5HEfSJ91pY"

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

CONFIGS = [
    {
        "label": "Gambling",
        "src": NC / "Gambling - Leads - Personal Phone Enriched.csv",
        "vertical": "Gambling",
        "sender_field": "LT Campaign Gambling Brands Oct 2026 Sender Email",
        "import_out": PREP / "Gambling Brands - GHL Import + Sender.csv",
    },
    {
        "label": "Cannabis Dispensaries",
        "src": NC / "Cannabis Dispenseries - Leads - Personal Phone Enriched.csv",
        "vertical": "Cannabis Dispensaries",
        "sender_field": "LT Campaign Cannabis Dispensaries Brands Oct 2026 Sender Email",
        "import_out": PREP / "Cannabis Dispensaries Brands - GHL Import + Sender.csv",
    },
]


def get_pit():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("GHL_PIT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GHL_PIT not found in repository .env")


HEADERS = {
    "Authorization": "Bearer " + get_pit(),
    "Version": "2021-07-28",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}
SESSION = requests.Session()


def get_json(url, params=None):
    for attempt in range(6):
        r = SESSION.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(2 ** attempt, 20))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("GHL read remained rate-limited/unavailable after retries")


def digits(s):
    return "".join(ch for ch in (s or "") if ch.isdigit())


def reconcile(rows, label, key, out_name, matcher):
    values = sorted({key(r) for r in rows if key(r)})
    out_rows = []
    matches = 0
    errors = 0
    for i, v in enumerate(values, start=1):
        try:
            payload = get_json(f"{BASE}/contacts/", {"locationId": LOCATION_ID, "query": v, "limit": 100})
            found = [c for c in payload.get("contacts", []) if matcher(c, v)]
            if not found:
                out_rows.append({"Source Value": v, "Match Status": "no_match", "Contact ID": "", "Existing Email": "", "Existing Name": "", "Existing Phone": ""})
            else:
                matches += len(found)
                for c in found:
                    out_rows.append({"Source Value": v, "Match Status": "exact_match", "Contact ID": c.get("id", ""), "Existing Email": c.get("email", ""), "Existing Name": c.get("name", ""), "Existing Phone": c.get("phone", "")})
        except Exception as exc:
            errors += 1
            out_rows.append({"Source Value": v, "Match Status": "lookup_error", "Contact ID": "", "Existing Email": "", "Existing Name": "", "Existing Phone": ""})
        if i % 40 == 0:
            print(f"  [{label}] {out_name}: {i}/{len(values)} checked")
        time.sleep(0.12)
    out = PREP / out_name
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Source Value", "Match Status", "Contact ID", "Existing Email", "Existing Name", "Existing Phone"])
        w.writeheader()
        w.writerows(out_rows)
    return len(values), matches, errors, out.name


summary = []
for cfg in CONFIGS:
    with cfg["src"].open(encoding="utf-8-sig", newline="") as f:
        src_rows = list(csv.DictReader(f))

    import_rows = []
    for i, row in enumerate(src_rows):
        import_rows.append({
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
            "Vertical": cfg["vertical"],
            "Source": (row.get("Source") or "").strip(),
            "Apollo Company LinkedIn URL": (row.get("Company Linkedin Url") or "").strip(),
            "Apollo Facebook URL": (row.get("Facebook Url") or "").strip(),
            "Apollo Twitter URL": (row.get("Twitter Url") or "").strip(),
            cfg["sender_field"]: SENDERS[i % len(SENDERS)],
        })

    with cfg["import_out"].open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BASE_COLS + [cfg["sender_field"]], extrasaction="ignore")
        w.writeheader()
        w.writerows(import_rows)

    sender_counts = Counter(SENDERS[i % len(SENDERS)] for i in range(len(src_rows)))
    blank_email = sum(1 for r in import_rows if not r["Email"])
    summary.append({
        "label": cfg["label"],
        "rows": len(src_rows),
        "import_file": cfg["import_out"].name,
        "sender_split": dict(sender_counts),
        "blank_email": blank_email,
    })

    # Read-only reconciliation (email + phone)
    e_vals, e_match, e_err, e_name = reconcile(import_rows, cfg["label"], lambda r: (r["Email"] or "").lower(), f"{cfg['label']} Contacts - Exact Email GHL Reconciliation.csv",
                                               lambda c, v: (c.get("email") or "").strip().lower() == v)
    p_vals, p_match, p_err, p_name = reconcile(import_rows, cfg["label"], lambda r: digits(r["Phone"]), f"{cfg['label']} Contacts - Exact Phone GHL Reconciliation.csv",
                                               lambda c, v: digits(c.get("phone"))[-10:] == v[-10:] if v else False)
    summary[-1]["email_recon"] = f"{e_vals} emails, {e_match} matched, {e_err} errors -> {e_name}"
    summary[-1]["phone_recon"] = f"{p_vals} phones, {p_match} matched, {p_err} errors -> {p_name}"

print("\n=== SUMMARY ===")
for s in summary:
    print(f"{s['label']}: {s['rows']} rows -> {s['import_file']}")
    print(f"   sender split: {s['sender_split']}; blank emails: {s['blank_email']}")
    print(f"   email recon: {s['email_recon']}")
    print(f"   phone recon: {s['phone_recon']}")
