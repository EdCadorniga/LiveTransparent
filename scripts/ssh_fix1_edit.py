"""Apply the runner network fix on the VPS for LiveTransparent n8n.

Fix: in the generated Coolify compose, modify the n8n-runner service to:
  - remove the 'extra_hosts: postgres:host-gateway' mapping (it makes postgres
    resolve to the host gateway 10.0.0.1, which refuses TCP 5432)
  - add the 'coolify-shared' network so DNS resolves postgres -> app postgres
    (10.0.2.3) which serves 5432.

Steps: backup, edit in place, validate YAML, (apply is done by caller), verify.
Requires explicit current-session approval (granted by user). No secrets printed.
"""
import os, re, sys, json
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

DIR="/data/coolify/services/n44wksswcocwk88ogcog8c48"
COMPOSE=DIR+"/docker-compose.yml"
TS="$(date +%Y%m%dT%H%M%SZ)"
BAK=f"{COMPOSE}.bak-{TS}-network-fix"

PYEDIT = r'''
import re, sys
p = sys.argv[1]
with open(p) as f:
    lines = f.readlines()
# We operate on the n8n-runner service block only.
# Locate the n8n-runner service's extra_hosts + networks section.
# Strategy: find '  n8n-runner:' then scan until the next '^  [a-zA-Z0-9]' service at col0-2 that isn't deeper.
out = []
i = 0
n = len(lines)
txt = "".join(lines)

# Find the n8n-runner service start
m = re.search(r"\n  n8n-runner:\n", txt)
assert m, "n8n-runner service not found"
start = m.start()+1  # position of '  n8n-runner:'
# find next top-level service start (two-space indent key followed by ':')
rest = txt[start:]
m2 = re.match(r"(?s).*?\n(?=\S)", rest)  # until last non-indented ... use service boundary
# Instead: split into lines relative to start
seg_lines = txt[start:].split("\n")

def is_toplevel_service(l):
    # a line like '  somename:' at exactly 2-space indent, not under networks (which is deeper)
    return re.match(r"^  [a-zA-Z0-9_-]+:$", l) is not None

# find end of n8n-runner block
end = None
for j, l in enumerate(seg_lines):
    if j>0 and is_toplevel_service(l):
        end = j
        break
if end is None:
    end = len(seg_lines)
block = seg_lines[:end]
btxt = "\n".join(block)

# Remove extra_hosts block: lines '    extra_hosts:' then indented items
btxt2 = re.sub(r"\n    extra_hosts:\n(?:      [^\n]*\n)+", "\n", btxt, count=1)
assert "extra_hosts" not in btxt2, "extra_hosts not fully removed: "+btxt2

# Add coolify-shared to networks within this block
# Find '    networks:' then its children '      n44...: null'
mm = re.search(r"\n    networks:\n(      [^\n]*\n)+", btxt2)
assert mm, "networks block not found in runner"
netblock = mm.group(0)
if "coolify-shared" not in netblock:
    netblock2 = netblock + "      coolify-shared: null\n"
    btxt2 = btxt2.replace(netblock, netblock2, 1)

new_block = btxt2
new_seg = new_block.split("\n")
new_lines = ["  n8n-runner:\n"] + new_seg[1:end]

result = txt[:start] + "\n".join(new_lines) + "\n" + "\n".join(seg_lines[end:])
with open(p,"w") as f:
    f.write(result)
print("EDIT_OK")
'''

# 1) Backup
rc,out,err=run(f"cp {COMPOSE} {BAK} && echo BACKUP_OK {BAK}")
print(out); 
if rc!=0 or "BACKUP_OK" not in out: 
    print("FATAL backup failed", err); sys.exit(1)

# 2) Edit in place via python on VPS (pass compose path as argv)
rc,out,err=run(f"python3 - {COMPOSE} <<'PY'\n{PYEDIT}\nPY", timeout=60)
print("EDIT rc",rc, out, err)

# 3) Validate
rc,out,err=run(f"cd {DIR} && docker compose -f {COMPOSE} config -q && echo CONFIG_VALID", timeout=90)
print("VALIDATE rc",rc,out,err)

# 4) Confirm the runner block now
rc,out,err=run(f"awk '/^  n8n-runner:/{{f=1}} f&&/^  [a-z]/&&!/^  n8n-runner:/{{if(seen)exit}} f{{print}} f{{seen=1}}' {COMPOSE} | grep -nE 'extra_hosts|networks:|coolify-shared|n44' ")
print("NEW RUNNER NET BLOCK:\n",out[:1500])

c.close(); print("CLOSED")
