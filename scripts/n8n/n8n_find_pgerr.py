"""Find which workflow executions show the postgres 10.0.0.1 ECONNREFUSED failure."""
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

# Pull recent error executions with data, look for 10.0.0.1 / ECONNREFUSED
st, body = api("/api/v1/executions?limit=50&includeData=true&status=error")
if st != 200:
    print("ERR", body); raise SystemExit
print("error executions returned:", len(body.get("data", [])))
for ex in body.get("data", []):
    blob = json.dumps(ex)
    if "10.0.0.1" in blob or "ECONNREFUSED" in blob:
        print("---")
        print(" exec id:", ex.get("id"), "started:", ex.get("startedAt"), "wf:", ex.get("workflowId"), ex.get("workflowData",{}).get("name") if isinstance(ex.get("workflowData"),dict) else "")
        # error message
        err = ex.get("data",{}).get("resultData",{}).get("error",{}) if isinstance(ex.get("data"),dict) else {}
        print("   msg:", str(err.get("message"))[:200])
