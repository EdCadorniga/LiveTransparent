"""Probe n8n API to find GHL ingest workflow + last executions. Key handled in-memory, never printed."""
import os, re, json, subprocess, urllib.request, ssl
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
if not host.startswith("http"):
    host = "https://" + host
print("using host:", host, "| key present:", bool(key))

def api(path, method="GET"):
    url = host.rstrip("/") + path
    req = urllib.request.Request(url, method=method, headers={"X-N8N-API-KEY": key, "Accept":"application/json"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.status, json.loads(resp.read().decode())
    except Exception as e:
        return None, str(e)

st, body = api("/api/v1/workflows?limit=100")
if st:
    wfs = body.get("data", [])
    print("workflows:", len(wfs))
    # find GHL / ingest / sales related
    for w in wfs:
        name = (w.get("name") or "")
        if any(k in name.lower() for k in ["ghl","ingest","sales","lead","contact","import"]):
            print("  WF id=", w.get("id"), "| name=", name, "| active=", w.get("active"))
else:
    print("workflows error:", body)
