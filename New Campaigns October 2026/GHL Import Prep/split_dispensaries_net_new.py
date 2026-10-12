import csv
import time
import json
import urllib.error
import urllib.request
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
SENDER_FIELD = "LT Campaign Cannabis Dispensaries Brands Oct 2026 Sender Email"
BASE_COLS = [
    "First Name", "Last Name", "Email", "Phone", "Corporate Phone", "Title",
    "Business Name", "Apollo Person LinkedIn URL", "Website", "State", "Country",
    "Vertical", "Source", "Apollo Company LinkedIn URL", "Apollo Facebook URL",
    "Apollo Twitter URL",
]
VERT_FIELD = "ODs8fBt5te5HEfSJ91pY"
SENDER_ID = "wR5Az25TIyETr5E3NwoN"

env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
PIT = env.get("GHL_PIT") or env.get("GHL_API_KEY")
BASE = "https://services.leadconnectorhq.com"
H = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
     "Accept": "application/json", "User-Agent": "Mozilla/5.0"}


def get(url):
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(min(2 ** a, 20)); continue
            return {"_http": e.code}
        except Exception:
            if a == 5:
                return {"_err": "fail"}
            time.sleep(1 + a)
    return {"_err": "retries"}


def norm_phone(p):
    d = "".join(ch for ch in (p or "") if ch.isdigit())
    return d[-10:] if len(d) >= 10 else d


# matched keys (rows with a Contact ID)
def matched_keys(fname, kind):
    out = {}
    with (PREP / fname).open(encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        fields = rd.fieldnames or []
        key_col = "Key" if "Key" in fields else ("Source Value" if "Source Value" in fields else fields[0])
        for r in rd:
            cid = (r.get("Contact ID") or "").strip()
            kv = (r.get(key_col) or "").strip()
            if cid and kv:
                out[kv] = cid
    return out


matched_email = matched_keys("Cannabis Dispensaries Contacts - Exact Email GHL Reconciliation.csv", "email")
matched_phone = matched_keys("Cannabis Dispensaries Contacts - Exact Phone GHL Reconciliation.csv", "phone")
# normalize phone keys to last-10 digits so they align with source norm_phone()
matched_phone = {norm_phone(k): v for k, v in matched_phone.items() if norm_phone(k)}
print(f"matched emails: {len(matched_email)} | matched phones: {len(matched_phone)}")

# source rows (dedup by email, keep first)
src_rows = list(csv.DictReader((NC / "Cannabis Dispenseries - Leads - Personal Phone Enriched.csv").open(encoding="utf-8-sig", newline="")))
seen_em, rows = set(), []
for r in src_rows:
    em = (r.get("Email") or "").strip().lower()
    if em and em in seen_em:
        continue
    if em:
        seen_em.add(em)
    rows.append(r)

net_new, rows_by_cid = [], {}
for r in rows:
    em = (r.get("Email") or "").strip().lower()
    ph = norm_phone(r.get("Phone Number"))
    cids = []
    if em and em in matched_email:
        cids.append((matched_email[em], "email"))
    if ph and len(ph) == 10 and ph in matched_phone:
        cids.append((matched_phone[ph], "phone"))
    if cids:
        for cid, by in cids:
            rows_by_cid.setdefault(cid, {"by": set(), "rows": []})
            rows_by_cid[cid]["by"].add(by)
            rows_by_cid[cid]["rows"].append(r)
    else:
        net_new.append(r)

# create-only net-new file, rebalanced sender
out = PREP / "Cannabis Dispensaries Brands - GHL Import + Sender (Net-New).csv"
with out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=BASE_COLS + [SENDER_FIELD], extrasaction="ignore")
    w.writeheader()
    for i, row in enumerate(net_new):
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
            "Vertical": "Cannabis Dispensaries",
            "Source": (row.get("Source") or "Apollo").strip() or "Apollo",
            "Apollo Company LinkedIn URL": (row.get("Company Linkedin Url") or "").strip(),
            "Apollo Facebook URL": (row.get("Facebook Url") or "").strip(),
            "Apollo Twitter URL": (row.get("Twitter Url") or "").strip(),
            SENDER_FIELD: SENDERS[i % len(SENDERS)],
        })
counts = Counter(SENDERS[i % len(SENDERS)] for i in range(len(net_new)))
print(f"net-new create file: {len(net_new)} rows -> {out.name}")
print(f"   sender split: com={counts[SENDERS[0]]} co={counts[SENDERS[1]]} agency={counts[SENDERS[2]]} org={counts[SENDERS[3]]}")

# hold report: unique overlap contacts with live detail
uniq = rows_by_cid
print(f"overlap contacts (unique IDs): {len(uniq)}")

hold = []
for i, (cid, meta) in enumerate(uniq.items(), 1):
    d = get(f"{BASE}/contacts/{cid}") or {}
    c = d.get("contact") or {}
    vert = sender = ""
    for f_ in (c.get("customFields") or []):
        if f_.get("id") == VERT_FIELD:
            vert = str(f_.get("value", ""))
        if f_.get("id") == SENDER_ID:
            sender = str(f_.get("value", ""))
    r0 = meta["rows"][0]
    hold.append({
        "Contact ID": cid,
        "Matched By": "+".join(sorted(meta["by"])),
        "Source Email": (r0.get("Email") or "").strip(),
        "Source Phone": (r0.get("Phone Number") or "").strip(),
        "Source Name": f"{(r0.get('First Name') or '').strip()} {(r0.get('Last Name') or '').strip()}".strip(),
        "Source Company": (r0.get("Business Name") or "").strip(),
        "Existing Vertical": vert,
        "Existing Dispensaries Sender": sender,
        "Existing Tags": "; ".join(c.get("tags") or []),
    })
    if i % 20 == 0:
        print(f"   detail {i}/{len(uniq)}", flush=True)
    time.sleep(0.15)

hold_out = PREP / "Cannabis Dispensaries Brands - GHL Overlaps (Hold).csv"
with hold_out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Contact ID", "Matched By", "Source Email", "Source Phone",
                                      "Source Name", "Source Company", "Existing Vertical",
                                      "Existing Dispensaries Sender", "Existing Tags"])
    w.writeheader(); w.writerows(hold)
vv = Counter(h["Existing Vertical"] or "(blank)" for h in hold)
print(f"hold report: {len(hold)} rows -> {hold_out.name}")
print(f"   existing verticals: {dict(vv)}")
print(f"   with a Dispensaries sender already set: {sum(1 for h in hold if h['Existing Dispensaries Sender'])}")
