"""Verify n8n health + runner task offer + identify GHL ingest workflow, via n8n REST API (redacted)."""
import os, re
PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
def load_env(path, keys):
    vals = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1); vals[k.strip()]=v.strip().strip('"').strip("'")
    return vals
env = load_env(os.path.join(PROJ,".env"),["VPS_HOST","VPS_USER","VPS_SSH_KEY_PATH"])
HOST,USER=env["VPS_HOST"],env["VPS_USER"]
KEY=os.path.expanduser(re.sub(r"%(\w+)%", lambda m: os.environ.get(m.group(1),m.group(0)), env["VPS_SSH_KEY_PATH"]))
import paramiko
key=None
for kcls in [paramiko.RSAKey,paramiko.Ed25519Key,paramiko.ECDSAKey]:
    try: key=kcls.from_private_key_file(KEY); break
    except Exception: continue
c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(hostname=HOST,username=USER,pkey=key,timeout=20,auth_timeout=20,banner_timeout=20,
          look_for_keys=False,allow_agent=False)
def run(cmd, timeout=90):
    i,o,e=c.exec_command(cmd,timeout=timeout)
    out=o.read().decode("utf-8","replace"); err=e.read().decode("utf-8","replace")
    rc=o.channel.recv_exit_status(); return rc,out.strip(),err.strip()

# healthz endpoint inside n8n container (no auth needed)
print("--- n8n /healthz (in-container) ---")
rc,out,err=run("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'wget -qO- http://127.0.0.1:5678/healthz || echo FAIL'")
print("healthz:", out[:300])

# runner task offer / connected status from n8n logs
print("\n--- n8n main logs: runner/broker lines (last 40) ---")
rc,out,err=run("docker logs --tail 40 n8n-n44wksswcocwk88ogcog8c48 2>&1 | grep -iE 'runner|broker|task|offer|connect|error' | tail -20")
print(out[:2000])

# runner logs now
print("\n--- runner logs (last 15) ---")
rc,out,err=run("docker logs --tail 15 n8n-runner-n44wksswcocwk88ogcog8c48 2>&1")
print(out[:1500])
c.close(); print("CLOSED")
