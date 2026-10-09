import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
     "Accept": "application/json", "Content-Type": "application/json",
     "User-Agent": "Mozilla/5.0"}
VERT_FIELD = "ODs8fBt5te5HEfSJ91pY"
MUSH_SENDER = "IJ1yrUihuKD7DkLgWHYM"

def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    for a in range(4):
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            t = e.read().decode("utf-8", "ignore")[:500]
            if e.code == 429:
                time.sleep(2 + a * 2); continue
            return e.code, t
        except Exception as e:
            if a == 3: return 0, str(e)
            time.sleep(1 + a)
    return 0, "retries"

# 1) Full records for the 3 shown
print("=== The three shown ===")
for cid in ["qE3Xx8kZIdOLrLcioOwz", "4nosJTSPqasgf8hWTXTR", "UqcKoEkyKsDbGQb7q1HO"]:
    st, res = req("GET", f"/contacts/{cid}")
    c = (res or {}).get("contact", {}) if isinstance(res, dict) else {}
    cf = {f.get("id"): f.get("value") for f in (c.get("customFields") or [])}
    print(f"  {c.get('email')}: vertical={cf.get(VERT_FIELD)} | sender={cf.get(MUSH_SENDER)} | tags={c.get('tags')}")

# 2) Try several search filter shapes for Vertical=Mushroom
print("\n=== Try enumerate Vertical=Mushroom ===")
shapes = [
    {"locationId": LOC, "page": 1, "pageLimit": 100,
     "filters": [{"field": "Vertical", "operator": "eq", "value": "Mushroom"}]},
    {"locationId": LOC, "page": 1, "pageLimit": 100,
     "filters": [{"field": "contact.vertical", "operator": "eq", "value": "Mushroom"}]},
    {"locationId": LOC, "page": 1, "pageLimit": 100,
     "filters": [{"field": "customField", "operator": "eq", "value": "Mushroom"}]},
    {"locationId": LOC, "page": 1, "pageLimit": 100, "query": "Mushroom",
     "filters": [{"field": "tags", "operator": "eq", "value": "lt_campaign_mushroom_brands_oct_2026_enroll"}]},
]
for i, body in enumerate(shapes):
    st, res = req("POST", "/contacts/search", body)
    if isinstance(res, dict):
        print(f"  shape{i}: status={st} total={res.get('total')} returned={len(res.get('contacts', []))}")
    else:
        print(f"  shape{i}: status={st} -> {str(res)[:220]}")
