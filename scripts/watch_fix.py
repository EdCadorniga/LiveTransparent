"""LiveTransparent 'watch email and fix' loop.

Checks Gmail (from:me, last 24h) for new [LiveTransparent] monitor alert emails.
For a NEW runner-network alert, applies the bounded auto-fix (backup compose,
remove runner extra_hosts, add coolify-shared, recreate runner) then verifies
and emails a resolution/confirmation. Tracks processed message ids in a state
file so each alert is acted on once. Only auto-fixes the known runner-network
problem; postgres/db/pool-closure alerts are escalated (email note) not auto-fixed.

Usage: python watch_fix.py [--dry-run]
"""
import os, sys, json, re, time, datetime, subprocess, argparse, ssl, urllib.request, urllib.parse

PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
SCRIPTS = os.path.join(PROJ, "scripts")
STATE_DIR = os.path.join(PROJ, ".monitor")
os.makedirs(STATE_DIR, exist_ok=True)
PROCESSED = os.path.join(STATE_DIR, "watch_processed.json")
LOG = os.path.join(STATE_DIR, "watch_fix.log")
RECIPIENT = "edmundocadorniga@gmail.com"
GH = r"C:\1_Ed's Active Work\AI\Hermes"

def load_env(path):
    vals = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k, _, v = line.partition("=")
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")
    print(f"{ts} {msg}")

def load_processed():
    try:
        with open(PROCESSED) as f: return json.load(f)
    except Exception: return {"ids": []}

def save_processed(p):
    with open(PROCESSED, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)

def run_script(args, inp=None, timeout=120):
    py = os.path.join(GH, "hermes-agent", "venv", "Scripts", "python.exe")
    return subprocess.run([py] + args, input=inp, capture_output=True, text=True, timeout=timeout)

def list_alerts():
    r = run_script([os.path.join(SCRIPTS, "gmail_read.py"), "--query", "from:me newer_than:1d", "--max", "25"], timeout=90)
    try:
        msgs = json.loads(r.stdout)
    except Exception:
        log("gmail_read parse failed: " + r.stdout[:200]); return []
    out = []
    for m in msgs:
        subj = m.get("subject","") + " " + m.get("snippet","")
        # Only real monitor alert subjects: [LiveTransparent] UNHEALTHY/RECOVERED/ALERT: n8n/postgres/runner monitor
        if re.search(r"LiveTransparent", subj, re.I) and re.search(r"UNHEALTHY|RECOVERED|ALERT", subj):
            out.append(m)
    return out

def send_email(subject, body):
    raw = "To: " + RECIPIENT + "\r\nFrom: " + RECIPIENT + "\r\nSubject: " + subject + "\r\n\r\n" + body
    r = run_script([os.path.join(SCRIPTS, "gmail_send.py"), "--stdin"], inp=raw, timeout=90)
    return "SENT_OK" in r.stdout

def ssh_connect():
    env = load_env(os.path.join(PROJ, ".env"))
    host = env.get("VPS_HOST"); user = env.get("VPS_USER")
    key = env.get("VPS_SSH_KEY_PATH","")
    import re as _re
    key = _re.sub(r"%(\w+)%", lambda m: os.environ.get(m.group(1), m.group(0)), key)
    import paramiko
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname=host, username=user, key_filename=key, timeout=25, look_for_keys=False, allow_agent=False)
    return c

def applier_ssh(cmd, timeout=90):
    c = ssh_connect()
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8","ignore"); err = stderr.read().decode("utf-8","ignore")
    c.close()
    return out, err

def apply_runner_fix(compose_path="/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml"):
    """Backup + edit runner networks + recreate runner. Bounded: runner only."""
    steps = []
    # 1) backup
    out, err = applier_ssh(f"cp {compose_path} {compose_path}.bak-watchfix-$(date -u +%Y%m%dT%H%M%SZ) && echo BACKUP_OK")
    steps.append(("backup", out.strip(), err.strip()[:200]))
    if "BACKUP_OK" not in out:
        return False, steps
    # 2) edit with python (idempotent): remove extra_hosts under n8n-runner, add coolify-shared
    pyedit = r'''
import sys, re, io
p = sys.argv[1]
s = io.open(p, encoding="utf-8").read()
# remove the extra_hosts block immediately after the n8n-runner: service
# locate service block
m = re.search(r"(?ms)^  n8n-runner:.*?^  [a-zA-Z0-9_-]+:", s)
if not m:
    sys.exit("NO_RUNNER_BLOCK")
block = m.group(0)
new_block = re.sub(r"(?m)^    extra_hosts:\n(?:      .*\n?)+", "", block)
new_block = re.sub(r"(?m)^    networks:\n(      [^\n]+\n)(    depends_on:)",
                   r"    networks:\n\1      coolify-shared: null\n\2", new_block)
s = s[:m.start()] + new_block + s[m.end():]
io.open(p, "w", encoding="utf-8").write(s)
print("EDIT_DONE")
'''
    out, err = applier_ssh(f"python3 - {compose_path} <<'PY'\n{pyedit}\nPY", timeout=60)
    steps.append(("edit", out.strip(), err.strip()[:200]))
    if "EDIT_DONE" not in out:
        return False, steps
    # 3) validate
    out, err = applier_ssh(f"cd /data/coolify/services/n44wksswcocwk88ogcog8c48 && docker compose config -q && echo CONFIG_VALID", timeout=60)
    steps.append(("validate", out.strip(), err.strip()[:200]))
    if "CONFIG_VALID" not in out:
        return False, steps
    # 4) recreate runner only
    out, err = applier_ssh(f"cd /data/coolify/services/n44wksswcocwk88ogcog8c48 && docker compose up -d --force-recreate n8n-runner 2>&1 | tail -5", timeout=240)
    steps.append(("recreate", out.strip(), err.strip()[:200]))
    return True, steps

def verify_fix(runner="n8n-runner-n44wksswcocwk88ogcog8c48"):
    """Confirm runner postgres DNS + TCP after the fix."""
    dns, err1 = applier_ssh(f"docker exec {runner} getent hosts postgres 2>&1", timeout=30)
    tcp, err2 = applier_ssh(f"docker exec {runner} sh -c 'nc -z -w3 postgres 5432 && echo TCP_OK || echo TCP_FAIL'", timeout=30)
    dns_ok = bool(re.search(r"10\.0\.2\.\d+", dns)) and "10.0.0.1" not in dns
    tcp_ok = "TCP_OK" in tcp
    return dns_ok and tcp_ok, {"dns": dns.strip(), "tcp": tcp.strip()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    alerts = list_alerts()
    if not alerts:
        log("no new [LiveTransparent] alert emails in last 24h")
        return
    log(f"found {len(alerts)} alert email(s)")
    p = load_processed()
    acted = False
    for m in alerts:
        mid = m["id"]
        if mid in p["ids"]:
            continue
        log(f"NEW alert id={mid} subject={m.get('subject','')[:80]}")
        subj = (m.get("subject","") + " " + m.get("snippet",""))
        is_runner = bool(re.search(r"runner|postgres DNS|TCP|ECONNREFUSED|10\\.0\\.0\\.1", subj, re.I)) and not re.search(r"pool|Cannot use a pool", subj, re.I)
        if args.dry_run:
            log(f"  [dry-run] would {'auto-fix' if is_runner else 'escalate'} id={mid}")
            p["ids"].append(mid)
            acted = True
            continue
        if is_runner:
            log(f"  applying runner-network auto-fix ...")
            ok, steps = apply_runner_fix()
            for s, o, e in steps:
                log(f"    {s}: {o[:120]}{(' ERR ' + e[:120]) if e else ''}")
            if ok:
                verified, v = verify_fix()
                log(f"  fix applied; verified={verified} dns={v['dns']} tcp={v['tcp']}")
                if verified:
                    send_email("[LiveTransparent] AUTO-FIX COMPLETED: runner network path restored",
                               f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\nThe runner->postgres network path was re-applied and verified.\nDNS postgres: {v['dns']}\nTCP postgres:5432: {v['tcp']}\n")
                    log("  resolution email SENT")
                else:
                    send_email("[LiveTransparent] AUTO-FIX INCOMPLETE: manual review needed",
                               f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\nThe fix was applied but verification failed.\nDNS: {v['dns']}\nTCP: {v['tcp']}\nPlease review docs/sessions and the VPS.\n")
                    log("  incomplete-fix email SENT")
            else:
                send_email("[LiveTransparent] AUTO-FIX FAILED: manual review needed",
                           f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\nSteps:\n" + "\n".join(f"{s}: {o}" for s,o,e in steps) + "\n")
                log("  failed-fix email SENT")
        else:
            log(f"  escalating (non-network issue): {subj[:120]}")
            send_email("[LiveTransparent] ESCALATED: non-network alert needs review",
                       f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\nSubject: {m.get('subject','')}\n\nThis alert is not the known runner-network class; no auto-fix applied. Review manually.\n")
            log("  escalation email SENT")
        p["ids"].append(mid)
        acted = True
    save_processed(p)
    log("watch_fix done" if acted else "watch_fix: no new actionable alerts")

if __name__ == "__main__":
    main()