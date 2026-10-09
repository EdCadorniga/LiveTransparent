import csv
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
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

VERTICALS = {
    "alcohol":  ("lt_campaign_alcohol_brands_oct_2026_enroll",  "AIzg8FR3PEDr7PSGMuXN"),
    "cannabis": ("lt_campaign_cannabis_brands_oct_2026_enroll", "qoQxuEiX5kwKvvrOvDVm"),
    "nicotine": ("lt_campaign_nicotine_brands_oct_2026_enroll", "oFHCH0QL8wsrkHiXKE3F"),
    "mushroom": ("lt_campaign_mushroom_brands_oct_2026_enroll", "IJ1yrUihuKD7DkLgWHYM"),
    "crypto":   ("lt_campaign_crypto_brands_oct_2026_enroll",   "UKLWo0PbkyZh34XExfHc"),
    "peptides": ("lt_campaign_peptides_brands_oct_2026_enroll", "ADJQKqlJzjhnGiCpQQgg"),
}
TAG_TO_VERT = {v[0]: k for k, v in VERTICALS.items()}

def get(url):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 + a * 3); continue
            return {"_http": e.code}
        except Exception:
            if a == 4: return {"_err": "fail"}
            time.sleep(1 + a)
    return {"_err": "retries"}

rows = []
url = f"{BASE}/contacts/?locationId={LOC}&limit=100"
page = 0
while url:
    page += 1
    res = get(url)
    if "_http" in res or "_err" in res:
        print("stopped page", page, res); break
    for c in res.get("contacts", []):
        tags = c.get("tags") or []
        matched = [TAG_TO_VERT[t] for t in tags if t in TAG_TO_VERT]
        cf = {f.get("id"): f.get("value") for f in (c.get("customFields") or [])}
        vertical = str(cf.get(VERT_FIELD) or "").strip()
        if not matched and vertical not in VERTICALS.values():
            continue
        sender_presence = {}
        for v, (_tag, fid) in VERTICALS.items():
            val = (cf.get(fid) or "").strip()
            sender_presence[v] = val
        rows.append({
            "Contact Id": c.get("id"),
            "Email": c.get("email") or "",
            "VerticalField": vertical,
            "EnrolledVerticals": "|".join(matched),
            **{f"{v}_sender": sender_presence[v] for v in VERTICALS},
            "Tags": "|".join(tags),
        })
    nxt = (res.get("meta") or {}).get("nextPageUrl")
    url = nxt if nxt else None
    if page % 50 == 0:
        print(f"  page {page}, collected {len(rows)}", flush=True)
    time.sleep(0.15)

out = HERE / "audit_all_vertical_senders.csv"
with out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
    w.writeheader(); w.writerows(rows)

print(f"\nPages: {page}; collected {len(rows)}")
print("\n=== Per vertical: enrolled (by tag) but MISSING its sender ===")
for v in VERTICALS:
    enrolled = [r for r in rows if v in r["EnrolledVerticals"].split("|")]
    missing = [r for r in enrolled if not r[f"{v}_sender"]]
    print(f"{v:9s}: enrolled={len(enrolled):5d}  has_sender={len(enrolled)-len(missing):5d}  MISSING={len(missing):4d}")
print("\nReport:", out)
