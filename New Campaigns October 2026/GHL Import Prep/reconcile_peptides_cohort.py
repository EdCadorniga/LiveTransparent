import csv
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROOTNC = ROOT / "New Campaigns October 2026"
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
PIT = env.get("GHL_PIT") or env.get("GHL_API_KEY")
LOC = env.get("GHL_LOCATION_ID", "Zwz4relUXVPxx8uohnjV")
BASE = "https://services.leadconnectorhq.com"
H = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
     "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
VERT_FIELD = "ODs8fBt5te5HEfSJ91pY"

SRC = ROOTNC / "Peptides - Leads - Personal Phone Enriched.csv"


def get(url):
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
                return __import__("json").loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(min(2 ** a, 20)); continue
            return {"_http": e.code}
        except Exception:
            if a == 5: return {"_err": "fail"}
            time.sleep(1 + a)
    return {"_err": "retries"}


def norm_phone(p):
    d = "".join(ch for ch in (p or "") if ch.isdigit())
    return d[-10:] if len(d) >= 10 else d


rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig", newline="")))
emails = sorted({(r.get("Email") or "").strip().lower() for r in rows if (r.get("Email") or "").strip()})
phones = sorted({norm_phone(r.get("Phone Number")) for r in rows if norm_phone(r.get("Phone Number")) and len(norm_phone(r.get("Phone Number"))) == 10})
print(f"Peptides source rows: {len(rows)}; unique emails: {len(emails)}; unique 10-digit phones: {len(phones)}")

import json

def reconcile(keys, kind):
    out = []
    for i, key in enumerate(keys, 1):
        res = get(f"{BASE}/contacts/?locationId={LOC}&query={urllib.parse.quote(key)}&limit=100")
        matches = []
        for c in (res.get("contacts") or []):
            if kind == "email" and (c.get("email") or "").strip().lower() == key:
                matches.append(c)
            elif kind == "phone" and norm_phone(c.get("phone")) == key:
                matches.append(c)
        for c in matches:
            detail = get(f"{BASE}/contacts/{c.get('id')}") or {}
            d = detail.get("contact") or detail
            vert = ""
            for f in (d.get("customFields") or []):
                if f.get("id") == VERT_FIELD:
                    vert = str(f.get("value", "")); break
            out.append({"Key": key, "Kind": kind, "Contact ID": c.get("id"),
                        "Existing Email": d.get("email", ""), "Existing Name": d.get("name", ""),
                        "Existing Vertical": vert, "Existing Tags": "; ".join(d.get("tags") or [])})
        if not matches:
            out.append({"Key": key, "Kind": kind, "Contact ID": "", "Existing Email": "",
                        "Existing Name": "", "Existing Vertical": "", "Existing Tags": ""})
        if i % 25 == 0:
            print(f"  {kind} {i}/{len(keys)}", flush=True)
        time.sleep(0.12)
    return out

import urllib.parse
email_rows = reconcile(emails, "email")
phone_rows = reconcile(phones, "phone")

for name, data in [("Peptides Contacts - Exact Email GHL Reconciliation.csv", email_rows),
                   ("Peptides Contacts - Exact Phone GHL Reconciliation.csv", phone_rows)]:
    with (HERE / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Key", "Kind", "Contact ID", "Existing Email", "Existing Name", "Existing Vertical", "Existing Tags"])
        w.writeheader(); w.writerows(data)

em = [r for r in email_rows if r["Contact ID"]]
ph = [r for r in phone_rows if r["Contact ID"]]
print(f"\nExact EMAIL matches: {len({r['Key'] for r in em})}; exact PHONE matches: {len({r['Key'] for r in ph})}")
for r in (em + ph)[:20]:
    print("  ", r["Kind"], r["Key"], "->", r["Contact ID"], r["Existing Vertical"], "|", r["Existing Tags"][:60])
