"""Check LT - Voice Agent V1 Outbound Dialer (Vapi) executions since the fix (~14:53 UTC) to confirm ECONNREFUSED resolved."""
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

WID = "r7UjWLndmc6EqEUW"  # LT - Voice Agent V1 Outbound Dialer (Vapi)
st, body = api(f"/api/v1/executions?workflowId={WID}&limit=20&includeData=true")
if st != 200:
    print("ERR", body); raise SystemExit
fix_ts = datetime(2026,9,7,14,53,0,tzinfo=timezone.utc)
print(f"executions for Voice Agent V1 (last {len(body.get('data',[]))}):")
for ex in body.get("data", []):
    ts_s = ex.get("startedAt") or ""
    status = ex.get("status")
    try:
        ts = datetime.fromisoformat(ts_s.replace("Z","+00:00"))
        after = "POST-FIX" if ts >= fix_ts else "pre-fix"
    except Exception:
        after="?"
    # error marker
    err = ""
    if status != "success":
        d = ex.get("data") or {}
        e = (d.get("resultData") or {}).get("error") or {}
        err = str(e.get("message"))[:60]
    print(f"  [{after}] {ts_s} status={status} err={err}")
