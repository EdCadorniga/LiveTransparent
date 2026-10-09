import csv
import json
import time
import urllib.error
import urllib.request
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
MUSH_SENDER = "IJ1yrUihuKD7DkLgWHYM"

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
        print("stopped at page", page, res); break
    for c in res.get("contacts", []):
        cf = {f.get("id"): f.get("value") for f in (c.get("customFields") or [])}
        if str(cf.get(VERT_FIELD) or "").strip() == "Mushroom":
            rows.append({
                "Contact Id": c.get("id"),
                "Email": c.get("email") or "",
                "HasMushSender": "YES" if (cf.get(MUSH_SENDER) or "").strip() else "NO",
                "MushSenderValue": (cf.get(MUSH_SENDER) or "").strip(),
                "Tags": "|".join(c.get("tags") or []),
            })
    meta = res.get("meta") or {}
    nxt = meta.get("nextPageUrl")
    url = nxt if nxt else None
    if page % 50 == 0:
        print(f"  page {page}, mushrooms so far {len(rows)}", flush=True)
    time.sleep(0.15)

out = HERE / "audit_mushroom_vertical_contacts.csv"
with out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Contact Id", "Email", "HasMushSender", "MushSenderValue", "Tags"])
    w.writeheader(); w.writerows(rows)

no = [r for r in rows if r["HasMushSender"] == "NO"]
print(f"\nPages scanned: {page}")
print(f"Vertical=Mushroom total: {len(rows)}")
print(f"  with sender: {len(rows) - len(no)}")
print(f"  MISSING sender: {len(no)}")
print("Report:", out)
