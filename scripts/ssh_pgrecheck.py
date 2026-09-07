"""Re-check postgres connectivity from both n8n main and runner; determine refused vs timeout; check postgres IP stability."""
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

PG="postgres-uokgs4c04ko0s4scccg40cgg"
print("--- postgres current status ---")
rc,out,err=run(f"docker ps --filter name={PG} --format '{{{{.Status}}}}'")
print("pg status:", out)

print("\n--- postgres networks (proper template, quoted) ---")
rc,out,err=run(f"docker inspect {PG} --format '{{{{.NetworkSettings.Networks}}}}'")
print(out[:800])

print("\n--- is postgres still on coolify-shared? ---")
rc,out,err=run(f"docker network inspect coolify-shared --format '{{{{range .Containers}}}}%v {{end}}}}' --format '{{json .Containers}}' | tr ',' '\\n' | grep -iE 'postgres|n8n' ")
print(out[:1200])

print("\n--- n8n main -> postgres TCP now (refused vs timeout) ---")
rc,out,err=run("timeout 6 docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'echo | nc -w 3 postgres 5432; echo rc=$?'")
print("n8n main nc:", out, "| err:", err[:300])

print("\n--- runner -> postgres TCP now ---")
rc,out,err=run("timeout 6 docker exec n8n-runner-n44wksswcocwk88ogcog8c48 sh -c 'echo | nc -w 3 postgres 5432; echo rc=$?'")
print("runner nc:", out, "| err:", err[:300])

print("\n--- n8n main /etc/hosts (is postgres pinned?) ---")
rc,out,err=run("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'cat /etc/hosts'")
print(out[:800])

print("\n--- runner resolves + route (ip route) ---")
rc,out,err=run("docker exec n8n-runner-n44wksswcocwk88ogcog8c48 sh -c 'getent hosts postgres; ip route 2>/dev/null | head'")
print(out[:800])
c.close(); print("\nCLOSED")
