"""Inspect prior network-fix backup + runners dir + live runner DNS/TCP state (read-only)."""
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
    i,o,e=c.exec_command(cmd,timeout=60); out=o.read().decode("utf-8","replace"); err=e.read().decode("utf-8","replace")
    rc=o.channel.recv_exit_status(); return rc,out.strip(),err.strip()

DIR="/data/coolify/services/n44wksswcocwk88ogcog8c48"
# prior network-fix backup runner block
rc,out,err=run(f"grep -nA3 -E 'extra_hosts|networks:' {DIR}/docker-compose.yml.bak-network-fix-20260902 | head -60")
print("=== bak-network-fix-20260902 runner networks/extra_hosts ==="); print(out[:1200])

# runners dir listing
rc,out,err=run(f"find {DIR}/runners -maxdepth 3 -type f | head -30; echo '---'; ls -la {DIR}/runners 2>/dev/null | head")
print("\n=== runners dir ==="); print(out[:1500])

# today's force-redeploy backup runner block
rc,out,err=run(f"grep -nA3 -E 'extra_hosts|networks:' {DIR}/docker-compose.yml.bak-20260907T132321Z | head -60")
print("\n=== bak-20260907t132321z (force redeploy) runner networks/extra_hosts ==="); print(out[:1200])

# Live runner: DNS + TCP probe FROM INSIDE the runner
runr="n8n-runner-n44wksswcocwk88ogcog8c48"
rc,out,err=run(f"docker exec {runr} sh -c 'echo \"-- getent hosts postgres --\"; getent hosts postgres || echo NO_ENTRY; echo \"-- postgres via hosts file --\"; grep postgres /etc/hosts || echo NONE; echo \"-- broker n8n --\"; getent hosts n8n || echo NO_BROKER'")
print("\n=== LIVE RUNNER DNS ==="); print(out[:1200])
rc,out,err=run(f"timeout 8 docker exec {runr} sh -c 'echo | nc -w 4 postgres 5432 && echo TCP_OK || echo TCP_FAIL' 2>&1 | head -5")
print("\n=== LIVE RUNNER TCP 5432 ==="); print(out[:600])

# n8n main currently healthy to its own postgres? test from n8n container
rc,out,err=run("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'getent hosts postgres; echo | nc -w 4 postgres 5432 && echo TCP_OK || echo TCP_FAIL' 2>&1 | head")
print("\n=== N8N MAIN -> postgres ==="); print(out[:600])
c.close()
print("\nCLOSED")
