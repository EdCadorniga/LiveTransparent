"""Show only the n8n-runner service block from the Coolify compose (redacted)."""
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
def run(cmd):
    i,o,e=c.exec_command(cmd,timeout=60); out=o.read().decode("utf-8","replace"); rc=o.channel.recv_exit_status()
    return rc,out.strip()

# Extract just the n8n-runner service block using awk from '  n8n-runner:' to next top-level service or end
cmd = r"""awk '/^  n8n-runner:/{f=1} f&&/^  [a-z]/&&!/^  n8n-runner:/{if(seen)exit} f{print} f{seen=1}' /data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml"""
rc,out=run(cmd)
RED = ['N8N_RUNNERS_AUTH_TOKEN','password','PASSWORD','SECRET','API_KEY','apikey']
def redact(line):
    for s in RED:
        if s in line and '=' in line:
            return line.split('=',1)[0]+'=<redacted>'
    return line
print("=== n8n-runner service block ===")
for l in out.splitlines():
    print(redact(l))
c.close()
print("\nCLOSED")
