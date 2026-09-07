"""Read-only live baseline probe for LiveTransparent VPS via Paramiko.
Connects using project .env credentials, runs bounded read-only commands,
prints results (no secrets)."""
import os, sys, json, re

PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
ENV = os.path.join(PROJ, ".env")

# --- parse required keys without logging values ---
def load_env(path, keys):
    vals = {}
    if not os.path.exists(path):
        raise SystemExit("ENV_MISSING " + path)
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip(); v = v.strip().strip('"').strip("'")
            if k in keys:
                vals[k] = v
    return vals

need = ["VPS_HOST", "VPS_USER", "VPS_SSH_KEY_PATH"]
env = load_env(ENV, need)
missing = [k for k in need if not env.get(k)]
if missing:
    raise SystemExit("MISSING_KEYS " + ",".join(missing))

HOST = env["VPS_HOST"]; USER = env["VPS_USER"]; KEY = env["VPS_SSH_KEY_PATH"]
# Expand Windows env-var style tokens like %USERPROFILE%
def _expand(m):
    return os.environ.get(m.group(1), m.group(0))
if "%" in KEY:
    KEY = re.sub(r"%(\w+)%", _expand, KEY)
if KEY.startswith("~"):
    KEY = os.path.expanduser(KEY)
if not os.path.exists(KEY):
    raise SystemExit("KEY_MISSING " + KEY)

import paramiko

key = None
for kcls in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
    try:
        key = kcls.from_private_key_file(KEY)
        break
    except Exception:
        continue
if key is None:
    raise SystemExit("KEY_LOAD_FAILED")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, pkey=key, timeout=20,
               auth_timeout=20, banner_timeout=20,
               look_for_keys=False, allow_agent=False)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=45)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    rc = stdout.channel.recv_exit_status()
    return rc, out.strip(), err.strip()

print("CONNECTED", HOST, USER)
rc, out, err = run("id -un && hostname && uname -a")
print("IDENTITY rc=", rc)
print(out)
if err: print("STDERR:", err[:500])

probes = {
  "DOCKER_PS": "docker ps --format '{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Networks}}'",
  "COOLIFY_COMPOSE_RUNNER": r"cd /data/coolify/applications 2>/dev/null && find . -maxdepth 3 -name 'docker-compose.yml' 2>/dev/null | head -20",
  "N8N_DIR_LOOKUP": r"find /data/coolify -maxdepth 3 -type d -iname '*nn8*' -o -maxdepth 3 -type d -iname '*runner*' 2>/dev/null | head -20",
}
for name, cmd in probes.items():
    rc, out, err = run(cmd)
    print(f"\n=== {name} rc={rc} ===")
    print(out[:2000])
    if err: print("ERR:", err[:300])

client.close()
print("\nCLOSED")
