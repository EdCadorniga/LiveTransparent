"""LiveTransparent 'watch email and fix' loop.

Checks Gmail (from:me, last 24h) for new [LiveTransparent] monitor alert emails.
Classifies each NEW alert into one of:
  - 'recovered': resolution notice (Severity: recovered / RECOVERED subject).
              Log + mark processed, NO email, never escalated.
  - 'pool':   n8n PostgreSQL pool-closure signature (Cannot use a pool after
              calling end on the pool). Auto-remediates by restarting ONLY the
              n8n main container (never postgres/redis/keys), with live
              preconditions, cooldown, evidence capture, and verification.
  - 'runner': runner->postgres network issue. VERIFY FIRST; only mutate the
              runner if verification actually fails (prevents pointless
              re-creates when the network is healthy).
  - 'escalate': anything else -> email note, no auto-fix.
Tracks processed message ids in a state file so each alert is acted on once.

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

N8N_CONTAINER = "n8n-n44wksswcocwk88ogcog8c48"
PG_CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
RUNNER_CONTAINER = "n8n-runner-n44wksswcocwk88ogcog8c48"
READINESS_URL = "https://automations.livetransparent.com/healthz/readiness"
POOL_SIG = "Cannot use a pool after calling end on the pool"
RESTART_COOLDOWN_S = 300          # n8n must have been up >=5min before we restart it
RESTART_MAX_PER_HOUR = 3          # auto-restart rate limit

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
    except Exception: return {"ids": [], "pool_restarts": []}

def save_processed(p):
    with open(PROCESSED, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)

def run_script(args, inp=None, timeout=120):
    py = os.path.join(GH, "hermes-agent", "venv", "Scripts", "python.exe")
    return subprocess.run([py] + args, input=inp, capture_output=True, text=True, timeout=timeout)

def gmail_fetch(query, maxn=25, with_body=True):
    args = [os.path.join(SCRIPTS, "gmail_read.py"), "--query", query, "--max", str(maxn)]
    if with_body:
        args.append("--body")
    r = run_script(args, timeout=90)
    try:
        return json.loads(r.stdout)
    except Exception:
        log("gmail_read parse failed: " + r.stdout[:200])
        return []

def list_alerts():
    msgs = gmail_fetch("from:me newer_than:1d", maxn=25)
    out = []
    for m in msgs:
        subj = m.get("subject", "") + " " + m.get("body", "") + " " + m.get("snippet", "")
        if re.search(r"LiveTransparent", subj, re.I) and re.search(r"UNHEALTHY|RECOVERED|ALERT", subj):
            out.append(m)
    return out

def send_email(subject, body):
    raw = "To: " + RECIPIENT + "\nFrom: " + RECIPIENT + "\nSubject: " + subject + "\n\n" + body
    r = run_script([os.path.join(SCRIPTS, "gmail_send.py"), "--stdin"], inp=raw, timeout=90)
    return "SENT_OK" in r.stdout

def ssh_connect():
    env = load_env(os.path.join(PROJ, ".env"))
    host = env.get("VPS_HOST"); user = env.get("VPS_USER")
    key = env.get("VPS_SSH_KEY_PATH", "")
    key = re.sub(r"%(\w+)%", lambda m: os.environ.get(m.group(1), m.group(0)), key)
    import paramiko
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname=host, username=user, key_filename=key, timeout=25, look_for_keys=False, allow_agent=False)
    return c

def applier_ssh(cmd, timeout=90):
    c = ssh_connect()
    try:
        stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore"); err = stderr.read().decode("utf-8", "ignore")
    finally:
        c.close()
    return out, err

# ---------------------------------------------------------------- classification

def classify_alert(m):
    """Evidence-based class: 'recovered' > 'pool' > 'runner' > 'escalate'.
    'recovered' is a resolution notice and must never be auto-fixed or escalated.
    The word 'runner' in the subject alone is NEVER enough for the runner class
    (every alert subject contains all three component names)."""
    text = (m.get("subject", "") + " " + m.get("body", "") + " " + m.get("snippet", "")).lower()
    if re.search(r"severity:\s*recovered|\[livetransparent\]\s*recovered:", text):
        return "recovered"
    if re.search(r"pool after calling end|cannot use a pool|pool-closure|pool_sig|pool.*end", text):
        return "pool"
    rn_sig = re.search(r"econnrefused|10\.0\.0\.1|getent|nslookup|\bdns\b.*\btcp\b|network path|runner.*(reachable|unreachable)", text)
    if rn_sig and ("runner" in text or "postgres" in text):
        return "runner"
    return "escalate"

# ---------------------------------------------------------------- pool fix

def pool_precheck():
    """Live preconditions before restarting n8n main. Returns (ok, evidence)."""
    ev = {}
    out, err = applier_ssh(f"docker logs --since 600s {N8N_CONTAINER} 2>&1 | grep -c '{POOL_SIG}'", timeout=60)
    ev["fresh_pool_errors"] = (out.strip() or "0")
    out, err = applier_ssh(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 20 {READINESS_URL}", timeout=45)
    ev["readiness_code"] = (out.strip() or "no-response")
    out, err = applier_ssh(f"docker inspect -f '{{{{.State.Health.Status}}}}' {PG_CONTAINER}", timeout=30)
    ev["postgres_health"] = (out.strip() or "unknown")
    out, err = applier_ssh(f"docker inspect -f '{{{{.State.StartedAt}}}}' {N8N_CONTAINER}", timeout=30)
    ev["n8n_started_at"] = (out.strip() or "")
    ok = True
    reasons = []
    try:
        if int(ev["fresh_pool_errors"]) <= 0:
            ok = False; reasons.append(f"no fresh pool-closure errors (count={ev['fresh_pool_errors']})")
    except Exception:
        ok = False; reasons.append("could not parse fresh pool error count")
    if ev["readiness_code"] == "200":
        ok = False; reasons.append(f"readiness already 200 (code={ev['readiness_code']})")
    if ev["postgres_health"] != "healthy":
        ok = False; reasons.append(f"postgres not healthy ({ev['postgres_health']})")
    try:
        started = datetime.datetime.fromisoformat(ev["n8n_started_at"].replace("Z", "+00:00"))
        age = (datetime.datetime.now(datetime.timezone.utc) - started).total_seconds()
        ev["n8n_uptime_s"] = int(age)
        if age < RESTART_COOLDOWN_S:
            ok = False; reasons.append(f"n8n up only {int(age)}s (<{RESTART_COOLDOWN_S}s cooldown)")
    except Exception:
        ok = False; reasons.append("could not parse n8n StartedAt")
    if not ok:
        ev["skip_reasons"] = "; ".join(reasons)
    return ok, ev

def pool_rate_limited(p):
    now = time.time()
    p["pool_restarts"] = [t for t in p.get("pool_restarts", []) if now - t < 3600]
    if len(p["pool_restarts"]) >= RESTART_MAX_PER_HOUR:
        return True, p
    return False, p

def apply_pool_fix(p):
    """Restart ONLY the n8n main container after live preconditions pass."""
    c = ssh_connect()
    try:
        before, err = applier_ssh(f"docker logs --since 600s {N8N_CONTAINER} 2>&1 | grep -c '{POOL_SIG}'; echo ---; docker inspect -f '{{{{.State.StartedAt}}}}' {N8N_CONTAINER}", timeout=60)
        steps = [("before", before.strip())]
        out, err = applier_ssh(f"docker restart {N8N_CONTAINER} 2>&1 | tail -3", timeout=300)
        steps.append(("restart", out.strip(), err.strip()[:200]))
        # wait for readiness up to 150s
        rd = ""
        for _ in range(15):
            time.sleep(10)
            out, _ = applier_ssh(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 15 {READINESS_URL}", timeout=40)
            rd = out.strip() or "no-response"
            if rd == "200":
                break
        after_started, _ = applier_ssh(f"docker inspect -f '{{{{.State.StartedAt}}}}' {N8N_CONTAINER}", timeout=30)
        after_errs, _ = applier_ssh(f"docker logs --since 300s {N8N_CONTAINER} 2>&1 | grep -c '{POOL_SIG}'", timeout=60)
        verified = rd == "200" and (after_errs.strip() or "0") == "0"
        steps.append(("after", f"readiness={rd} started={after_started.strip()} pool_errors_300s={after_errs.strip()}"))
        return verified, steps, rd
    finally:
        c.close()

# ---------------------------------------------------------------- runner fix

def apply_runner_fix(compose_path="/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml"):
    """Backup + edit runner networks + recreate runner. Bounded: runner only."""
    steps = []
    out, err = applier_ssh(f"cp {compose_path} {compose_path}.bak-watchfix-$(date -u +%Y%m%dT%H%M%SZ) && echo BACKUP_OK")
    steps.append(("backup", out.strip(), err.strip()[:200]))
    if "BACKUP_OK" not in out:
        return False, steps
    pyedit = r'''
import sys, re, io
p = sys.argv[1]
s = io.open(p, encoding="utf-8").read()
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
    out, err = applier_ssh(f"cd /data/coolify/services/n44wksswcocwk88ogcog8c48 && docker compose config -q && echo CONFIG_VALID", timeout=60)
    steps.append(("validate", out.strip(), err.strip()[:200]))
    if "CONFIG_VALID" not in out:
        return False, steps
    out, err = applier_ssh(f"cd /data/coolify/services/n44wksswcocwk88ogcog8c48 && docker compose up -d --force-recreate n8n-runner 2>&1 | tail -5", timeout=240)
    steps.append(("recreate", out.strip(), err.strip()[:200]))
    return True, steps

def verify_fix():
    dns, err1 = applier_ssh(f"docker exec {RUNNER_CONTAINER} getent hosts postgres 2>&1", timeout=30)
    tcp, err2 = applier_ssh(f"docker exec {RUNNER_CONTAINER} sh -c 'nc -z -w3 postgres 5432 && echo TCP_OK || echo TCP_FAIL'", timeout=30)
    dns_ok = bool(re.search(r"10\.0\.2\.\d+", dns)) and "10.0.0.1" not in dns
    tcp_ok = "TCP_OK" in tcp
    return dns_ok and tcp_ok, {"dns": dns.strip(), "tcp": tcp.strip()}

# ---------------------------------------------------------------- main

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
        cls = classify_alert(m)
        log(f"  classified as: {cls}")
        if args.dry_run:
            log(f"  [dry-run] would handle id={mid} as {cls}")
            p["ids"].append(mid)
            acted = True
            continue
        if cls == "recovered":
            # Resolution/recovery notice: log + mark processed, NO email, never escalate.
            log(f"  recovered/resolution notice; no action needed (not escalated, no email)")
        elif cls == "pool":
            ok, ev = pool_precheck()
            if not ok:
                send_email("[LiveTransparent] AUTO-FIX SKIPPED: n8n pool alert, conditions unmet",
                           f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                           f"Pool-closure alert received, but live preconditions said no action:\n{ev}\n\n"
                           f"Review manually per docs/sessions.\n")
                log("  pool precondition unmet; SKIPPED email SENT")
            else:
                limited, p = pool_rate_limited(p)
                if limited:
                    send_email("[LiveTransparent] AUTO-FIX SKIPPED: pool restart rate-limited",
                               f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                               f"n8n pool-closure confirmed but >={RESTART_MAX_PER_HOUR} auto-restarts in the last hour. Manual review required.\n")
                    log("  pool restart rate-limited; SKIPPED email SENT")
                else:
                    verified, steps, rd = apply_pool_fix(p)
                    for s in steps:
                        log(f"    {s[0]}: {s[1][:200]}{(' ERR ' + s[2][:120]) if len(s) > 2 and s[2] else ''}")
                    if verified:
                        send_email("[LiveTransparent] AUTO-FIX COMPLETED: n8n main pool restored",
                                   f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                                   f"n8n main was restarted (only n8n; postgres/redis/keys untouched) because its\n"
                                   f"PostgreSQL pool was ended and self-recovery had not restored it.\n\n"
                                   f"Pre: {steps[0][1]}\nRestart: {steps[1][1]}\nPost: {steps[2][1]}\n\n"
                                   f"Fresh pool-closure errors after restart: 0. Readiness: {rd}\n")
                        log("  pool fix verified; COMPLETED email SENT")
                    else:
                        send_email("[LiveTransparent] AUTO-FIX INCOMPLETE: n8n restarted but not verified",
                                   f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                                   f"n8n main was restarted but post-restart verification did not pass.\n"
                                   f"Steps:\n" + "\n".join(f"{s[0]}: {s[1]}" for s in steps) + "\n"
                                   f"Readiness: {rd}\nPlease review.\n")
                        log("  pool fix incomplete; INCOMPLETE email SENT")
                    p.setdefault("pool_restarts", []).append(time.time())
        elif cls == "runner":
            verified, v = verify_fix()
            if verified:
                send_email("[LiveTransparent] AUTO-CHECK OK: runner network already healthy",
                           f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                           f"The runner->postgres network path was checked and is healthy; no mutation applied.\n"
                           f"DNS postgres: {v['dns']}\nTCP postgres:5432: {v['tcp']}\n\n"
                           f"If the alert is about something else (e.g. an n8n pool-closure), it is being handled\n"
                           f"by the pool class; check the alert body and docs/sessions.\n")
                log("  runner already healthy; no mutation; AUTO-CHECK email SENT")
            else:
                log("  runner verification FAILED -> applying runner-network auto-fix ...")
                ok, steps = apply_runner_fix()
                for s, o, e in steps:
                    log(f"    {s}: {o[:120]}{(' ERR ' + e[:120]) if e else ''}")
                if ok:
                    verified2, v2 = verify_fix()
                    log(f"  fix applied; verified={verified2} dns={v2['dns']} tcp={v2['tcp']}")
                    if verified2:
                        send_email("[LiveTransparent] AUTO-FIX COMPLETED: runner network path restored",
                                   f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                                   f"The runner->postgres network path was re-applied and verified.\n"
                                   f"DNS postgres: {v2['dns']}\nTCP postgres:5432: {v2['tcp']}\n")
                        log("  resolution email SENT")
                    else:
                        send_email("[LiveTransparent] AUTO-FIX INCOMPLETE: manual review needed",
                                   f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\n"
                                   f"The fix was applied but verification failed.\nDNS: {v2['dns']}\nTCP: {v2['tcp']}\n"
                                   f"Please review docs/sessions and the VPS.\n")
                        log("  incomplete-fix email SENT")
                else:
                    send_email("[LiveTransparent] AUTO-FIX FAILED: manual review needed",
                               f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\n\nSteps:\n"
                               + "\n".join(f"{s}: {o}" for s, o, e in steps) + "\n")
                    log("  failed-fix email SENT")
        else:
            log(f"  escalating (non-network non-pool issue): {m.get('subject','')[:120]}")
            send_email("[LiveTransparent] ESCALATED: non-network alert needs review",
                       f"UTC: {datetime.datetime.utcnow().isoformat()}\nAlert id: {mid}\nSubject: {m.get('subject','')}\n\n"
                       f"This alert is not a known auto-fix class; no action applied. Review manually.\n")
            log("  escalation email SENT")
        p["ids"].append(mid)
        acted = True
    save_processed(p)
    log("watch_fix done" if acted else "watch_fix: no new actionable alerts")

if __name__ == "__main__":
    main()