import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import urllib.request
import urllib.error

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / "Export_Contacts_Verticals Enrolled but no sender_Oct_2026_10_01_PM.csv"
OUT = HERE / "audit_vertical_sender_fields.csv"

def load_env():
    env = {}
    envf = ROOT / ".env"
    for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
PIT = ENV.get("GHL_PIT") or ENV.get("GHL_API_KEY")
if not PIT:
    sys.exit("No GHL_PIT in .env")

BASE = "https://services.leadconnectorhq.com"

VERTICALS = {
    "nicotine": ("lt_campaign_nicotine_brands_oct_2026_enroll", "oFHCH0QL8wsrkHiXKE3F"),
    "alcohol": ("lt_campaign_alcohol_brands_oct_2026_enroll", "AIzg8FR3PEDr7PSGMuXN"),
    "mushroom": ("lt_campaign_mushroom_brands_oct_2026_enroll", "IJ1yrUihuKD7DkLgWHYM"),
    "cannabis": ("lt_campaign_cannabis_brands_oct_2026_enroll", "qoQxuEiX5kwKvvrOvDVm"),
}
SHARED_FIELD = "wjV8dgGMe7tL5Uny4Wgy"  # marketing_sender_email

def vertical_for(tags):
    for v, (tag, _fid) in VERTICALS.items():
        if tag in tags:
            return v
    return None

def get_contact(cid):
    url = f"{BASE}/contacts/{cid}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {PIT}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                import json
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 + attempt * 2)
                continue
            return {"_http_error": e.code}
        except Exception as e:
            if attempt == 3:
                return {"_error": str(e)}
            time.sleep(1 + attempt)
    return {"_error": "retries_exhausted"}

rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig", newline="")))

def work(row):
    cid = row["Contact Id"]
    tags = (row.get("Tags") or "")
    v = vertical_for(tags)
    data = get_contact(cid)
    contact = (data or {}).get("contact") or {}
    cf = {f.get("id"): f.get("value") for f in (contact.get("customFields") or [])}
    fid = VERTICALS[v][1] if v else None
    sender_val = (cf.get(fid) or "").strip() if fid else ""
    shared_val = (cf.get(SHARED_FIELD) or "").strip()
    return {
        "Contact Id": cid,
        "Email": row.get("Email", ""),
        "Vertical": v or "UNKNOWN",
        "EnrollTag": VERTICALS[v][0] if v else "",
        "SenderFieldId": fid or "",
        "HasVerticalSender": "YES" if sender_val else "NO",
        "VerticalSenderValue": sender_val,
        "HasSharedSender": "YES" if shared_val else "NO",
        "SharedSenderValue": shared_val,
        "LiveTags": "|".join(contact.get("tags") or []),
        "Error": data.get("_error") or (f"http_{data['_http_error']}" if data.get("_http_error") else ""),
    }

results = []
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(work, r): r["Contact Id"] for r in rows}
    done = 0
    for fut in as_completed(futs):
        results.append(fut.result())
        done += 1
        if done % 100 == 0:
            print(f"  ...{done}/{len(rows)}", flush=True)

fields = ["Contact Id", "Email", "Vertical", "EnrollTag", "SenderFieldId",
          "HasVerticalSender", "VerticalSenderValue", "HasSharedSender",
          "SharedSenderValue", "LiveTags", "Error"]
with OUT.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(results)

from collections import Counter
print("\n=== Missing per-vertical sender, by vertical ===")
missing = [r for r in results if r["HasVerticalSender"] == "NO"]
print(dict(Counter(r["Vertical"] for r in missing)))
print("\n=== Has per-vertical sender, by vertical ===")
has = [r for r in results if r["HasVerticalSender"] == "YES"]
print(dict(Counter(r["Vertical"] for r in has)))
print(f"\nTotal rows: {len(results)}; missing vertical sender: {len(missing)}")
errored = [r for r in results if r["Error"]]
print(f"Errors: {len(errored)}")
print(f"Report: {OUT}")
