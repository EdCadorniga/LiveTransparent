"""Investigate why runner TCP to postgres still fails despite DNS resolving to 10.0.2.3."""
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

RUNR="n8n-runner-n44wksswcocwk88ogcog8c48"
# Proper network membership: list network names via inspect -f with simple template
rc,out,err=run(f"docker inspect {RUNR} --format '{{{{range \\$k, \\$v := .NetworkSettings.Networks}}{{\\$k}} {{end}}}}'")
print("RUNNER NETWORKS:", out)

# /etc/hosts inside runner
rc,out,err=run(f"docker exec {RUNR} sh -c 'cat /etc/hosts'")
print("RUNNER /etc/hosts:\n",out)

# direct TCP to the postgres IP on coolify-shared
rc,out,err=run(f"timeout 10 docker exec {RUNR} sh -c 'echo > /dev/tcp/10.0.2.3/5432 && echo TCP_OK_IP || echo TCP_FAIL_IP'")
print("TCP to 10.0.2.3:5432:", out)

# also check from n8n main right now for comparison
rc,out,err=run("timeout 10 docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'echo > /dev/tcp/postgres/5432 && echo N8N_TCP_OK || echo N8N_TCP_FAIL'")
print("n8n main TCP to postgres:", out)

# postgres listening ports - which networks, published ports
rc,out,err=run("docker port postgres-uokgs4c04ko0s4scccg40cgg")
print("postgres published ports:", out)
rc,out,err=run("docker inspect postgres-uokgs4c04ko0s4scccg40cgg --format '{{json .HostConfig.PortBindings}}'")
print("postgres port bindings:", out)

# recent postgres logs for auth/reject
rc,out,err=run("docker logs --tail 30 postgres-uokgs4c04ko0s4scccg40cgg 2>&1 | tail -30")
print("postgres logs tail:\n",out[:2000])
c.close(); print("\nCLOSED")
