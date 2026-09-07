"""Deeper read-only probe: container inspect (redacted), networks, compose files, DNS/TCP from runner."""
import os, sys, json, re

PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
ENV = os.path.join(PROJ, ".env")

def load_env(path, keys):
    vals = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals

env = load_env(ENV, ["VPS_HOST", "VPS_USER", "VPS_SSH_KEY_PATH"])
HOST, USER = env["VPS_HOST"], env["VPS_USER"]
KEY = re.sub(r"%(\w+)%", lambda m: os.environ.get(m.group(1), m.group(0)), env["VPS_SSH_KEY_PATH"])
KEY = os.path.expanduser(KEY)

import paramiko
key = None
for kcls in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
    try:
        key = kcls.from_private_key_file(KEY); break
    except Exception: continue
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, pkey=key, timeout=20, auth_timeout=20,
               banner_timeout=20, look_for_keys=False, allow_agent=False)

def run(cmd):
    i,o,e = client.exec_command(cmd, timeout=60)
    out = o.read().decode("utf-8","replace"); err = e.read().decode("utf-8","replace")
    rc = o.channel.recv_exit_status()
    return rc, out.strip(), err.strip()

# 1. Locate compose files
rc, out, err = run("find /data/coolify -maxdepth 4 -name 'docker-compose.yml' 2>/dev/null")
print("=== COMPOSE FILES ==="); print(out[:3000])

# 2. Inspect runner: networks, aliases, extra_hosts, Hostname, env keys (names only)
rc, out, err = run("docker inspect n8n-runner-n44wksswcocwk88ogcog8c48 "
                   "--format '{{json .HostConfig.ExtraHosts}}|{{json .NetworkSettings.Networks}}|{{.Config.Hostname}}'")
print("\n=== RUNNER extra_hosts|networks|hostname ==="); print(out[:3000])

# 3. Inspect n8n main: networks + DB host env + aliases
rc, out, err = run("docker inspect n8n-n44wksswcocwk88ogcog8c48 "
                   "--format '{{json .NetworkSettings.Networks}}'")
print("\n=== N8N networks ==="); print(out[:2000])
rc, out, err = run("docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{range .Config.Env}}{{println .}}{{end}}'"
                   " | grep -iE 'N8N_DB|DB_HOST|DB_PORT|DB_TYPE|DB_NAME|DB_USER|EXECUTIONS' ")
print("\n=== N8N DB env (redacted: keys + non-secret values) ===")
lines = [l for l in out.splitlines() if l.strip()]
for l in lines:
    # show key only for password-ish, else key=value
    k = l.split("=",1)[0]
    if any(s in k.upper() for s in ["PASS","KEY","SECRET","TOKEN","ENCRYPT"]):
        print("  ", k, "=<redacted>")
    else:
        print("  ", l)

# 4. postgres app container aliases on coolify-shared
rc, out, err = run("docker inspect postgres-uokgs4c04ko0s4scccg40cgg "
                   "--format '{{json .NetworkSettings.Networks}}'")
print("\n=== APP POSTGRES networks/aliases ==="); print(out[:2500])

# 5. coolify-shared network details: containers + aliases
rc, out, err = run("docker network inspect coolify-shared --format '{{json .Containers}}'")
print("\n=== coolify-shared containers ==="); print(out[:4000])

client.close()
print("\nCLOSED")
