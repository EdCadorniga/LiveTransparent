"""Confirm GA4 ingest failure root cause from execution data (redacted), + check any workflow with runner pg usage."""
import os, re, json, urllib.request, ssl
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

# GA4 ingest failures: list executions
st, body = api("/api/v1/executions?workflowId=6pCSGzFmrMDFL5Yq&limit=10&includeData=true")
if st == 200:
    for ex in body.get("data", []):
        if ex.get("status") == "error":
            print("ERR EXEC", ex.get("startedAt"))
            data = ex.get("data") or {}
            result = data.get("resultData", {}).get("error", {})
            print("  error msg:", str(result.get("message"))[:300])
            print("  node:", result.get("node"))
            # search whole exec for 10.0.0.1 / ECONNREFUSED
            import json as J
            blob = J.dumps(data)
            for pat in ["ECONNREFUSED", "10.0.0.1", "postgres"]:
                idx = blob.find(pat)
                if idx>=0:
                    print("  contains", pat, "->", blob[max(0,idx-120):idx+180].replace("\\n"," "))
            break
else:
    print("ERR", body)
