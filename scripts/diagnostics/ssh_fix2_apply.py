"""Apply the runner network fix: recreate the n8n-runner container with new network config, then verify."""
import os, re, sys
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
def run(cmd, timeout=120):
    i,o,e=c.exec_command(cmd,timeout=timeout)
    out=o.read().decode("utf-8","replace"); err=e.read().decode("utf-8","replace")
    rc=o.channel.recv_exit_status(); return rc,out.strip(),err.strip()

DIR="/data/coolify/services/n44wksswcocwk88ogcog8c48"
COMPOSE=DIR+"/docker-compose.yml"
RUNR="n8n-runner-n44wksswcocwk88ogcog8c48"

# Apply: recreate start the runner (will also start n8n if needed; no service removal)
rc,out,err=run(f"cd {DIR} && docker compose -f {COMPOSE} up -d --force-recreate n8n-runner", timeout=180)
print("APPLY rc",rc); print(out[:2500]); print("ERR:",err[:1500])
c.close(); print("CLOSED")
