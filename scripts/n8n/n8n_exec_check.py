"""Check last executions of key pg-using workflows to see post-fix success (after 14:53 UTC)."""
import os, re, json, urllib.request, ssl
from datetime import datetime, timezone
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys):
    vals = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1); vals[k.strip()]=v.strip().strip('"').strip("'")
    return vals
env = load_env(os.path.join(PROJ,".env"),["N8N_API_KEY_LT","n8n_API_Key","N8N_HOST"])
key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = env.get("N8N_HOST") or "https://automations.livetransparent.com"
if not host.startswith("http"): host = "https://"+host
def api(path):
    req = urllib.request.Request(host.rstrip("/")+path, method="GET", headers={"X-N8N-API-KEY":key,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return None, str(e)

# workflows of interest: GHL Daily Sales Ingest, GHL Daily Leads Ingest, GA4 Daily Ingest, Emerald->PG
wf_ids = {
 "GHL_Daily_Sales": "aYT5oHcgmBALzHy5",
 "GHL_Daily_Leads": "dIQascjRloXs4FNB",
 "GA4_Daily_Ingest": "6pCSGzFmrMDFL5Yq",
}
fix_ts = datetime(2026,9,7,14,53,0,tzinfo=timezone.utc)
for label, wid in wf_ids.items():
    st, body = api(f"/api/v1/executions?workflowId={wid}&limit=4")
    if st != 200:
        print(label, "ERR", body); continue
    print(f"\n=== {label} (wf {wid}) last executions ===")
    for ex in body.get("data", []):
        ts_s = ex.get("startedAt") or ex.get("stoppedAt") or ""
        status = ex.get("status")
        try:
            ts = datetime.fromisoformat(ts_s.replace("Z","+00:00"))
            after = ts >= fix_ts
            mark = "AFTER-FIX" if after else "before-fix"
        except Exception:
            mark = "?"
        print(f"  status={status} started={ts_s} ({mark})")
