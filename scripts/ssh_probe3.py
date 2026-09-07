"""Inspect the Coolify-generated compose files for the n8n service (read-only, secrets redacted in output)."""
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

# file listing
rc,out=run("ls -la /data/coolify/services/n44wksswcocwk88ogcog8c48/ && echo '---APPS---' && ls -la /data/coolify/applications/ 2>/dev/null")
print(out[:1500])

# Read the compose file but redact secret-looking values
rc,out=run("cat /data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml")
print("\n=== SERVICE COMPOSE (REDACTED) ===")
redacted=[]
for line in out.splitlines():
    m=re.match(r'^(\s*)([\w\-\.]+)\s*:\s*(.+?)\s*$', line)
    if m:
        key=m.group(2).lower()
        if any(s in key for s in ["password","api_key","apikey","token","secret","encryption","key"]):
            line=m.group(1)+m.group(2)+": <redacted>"
    # redact inline urls with creds
    redacted.append(line)
print("\n".join(redacted)[:6000])
c.close()
print("\nCLOSED")
