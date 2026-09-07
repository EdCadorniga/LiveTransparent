"""Post-fix verification of the runner network path."""
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
print("--- runner networks + extra_hosts (docker inspect) ---")
rc,out,err=run(f"docker inspect {RUNR} --format 'extra_hosts={{json .HostConfig.ExtraHosts}} | networks={{json .NetworkSettings.Networks}}'")
print(out[:1500])
print("keys seen:", list(dict.fromkeys(re.findall(r'"(coolify-shared|n44[^"]*)"', out))))
print("extra_hosts present:", '"postgres:host-gateway"' in out or "postgres:host-gateway" in out)

print("\n--- DNS from inside runner ---")
rc,out,err=run(f"docker exec {RUNR} sh -c 'getent hosts postgres || echo NO_ENTRY'")
print("postgres ->", out)
rc,out,err=run(f"docker exec {RUNR} sh -c 'getent hosts n8n'")
print("n8n ->", out)

print("\n--- TCP 5432 from inside runner ---")
rc,out,err=run(f"timeout 10 docker exec {RUNR} sh -c 'echo > /dev/tcp/postgres/5432 && echo TCP_OK || echo TCP_FAIL'")
print(out)

print("\n--- runner status/health ---")
rc,out,err=run(f"docker ps --filter name={RUNR} --format '{{{{.Status}}}}'")
print("status:", out)

print("\n--- recent runner logs (last 25 lines, redacted) ---")
rc,out,err=run(f"docker logs --tail 25 {RUNR} 2>&1 | sed -E 's/(auth_token|token|password|secret)=[^ &]+/\\1=<redacted>/gi'")
print(out[:2500])
c.close(); print("\nCLOSED")
