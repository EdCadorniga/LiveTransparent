"""LiveTransparent n8n/postgres/runner health monitor.

SSHs to the VPS (project .env), checks n8n + postgres container health, the
external runner's network path, and bounded recent log signatures. When a
problem is found it sends an alert email to the configured recipient via
Gmail API (deduplicated by incident fingerprint). Bounded auto-remediation is
available but disabled unless --auto-fix is passed (never touches postgres/redis/keys).

Usage: python monitor.py [--auto-fix]
Writes: state file + bounded log under the project .monitor dir. No secrets printed.
"""
import os, sys, re, json, time, datetime, subprocess, argparse

PROJ = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
ENV_PATH = os.path.join(PROJ, ".env")
SCRIPTS = os.path.join(PROJ, "scripts")
STATE_DIR = os.path.join(PROJ, ".monitor")
os.makedirs(STATE_DIR, exist_ok=True)
STATE_FILE = os.path.join(STATE_DIR, "state.json")
LOG_FILE = os.path.join(STATE_DIR, "monitor.log")
RECIPIENT = "edmundocadorniga@gmail.com"
QUIET = False

def load_env(path):
    vals = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals

def expand_key(k):
    import re as _re
    def _sub(m):
        return os.environ.get(m.group(1), m.group(0))
    return _re.sub(r"%(\w+)%", _sub, k)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts} {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    if not QUIET:
        print(line)

def ssh_run(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "ignore")
    err = stderr.read().decode("utf-8", "ignore")
    return out, err

def main():
    global QUIET
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-fix", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    QUIET = args.quiet

    env = load_env(ENV_PATH)
    host = env.get("VPS_HOST"); user = env.get("VPS_USER")
    key = expand_key(env.get("VPS_SSH_KEY_PATH",""))
    runner = env.get("RUNNER_CONTAINER") or "n8n-runner-n44wksswcocwk88ogcog8c48"
    if not (host and user and key and os.path.exists(key)):
        log("FATAL: missing SSH config"); sys.exit(1)

    try:
        import paramiko
    except Exception as e:
        log(f"FATAL: paramiko unavailable: {e}"); sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=user, key_filename=key, timeout=25, look_for_keys=False, allow_agent=False)
    except Exception as e:
        log(f"FATAL: ssh connect failed: {e}")
        send_alert("SSH connect failed to VPS during monitor", f"Could not SSH to {host}: {e}")
        sys.exit(1)

    problems = []
    evidence = []

    # 1) Container health
    out, _ = ssh_run(client, "docker ps --format '{{.Names}}\\t{{.Status}}' | grep -E 'n8n|postgres|runner'")
    evidence.append("CONTAINERS:\n" + out)
    log("containers:\n" + out)

    # 2) n8n readiness via public HTTPS health endpoint (n8n image has no curl)
    import urllib.request, ssl as _ssl
    healthz_txt = "N8N_UNREACHABLE"
    try:
        with urllib.request.urlopen("https://automations.livetransparent.com/healthz", timeout=20,
                                    context=_ssl.create_default_context()) as _r:
            healthz_txt = ("HTTP%d " % _r.status) + _r.read().decode("utf-8","ignore")[:120]
    except Exception as e:
        healthz_txt = "N8N_HEALTH_ERR: " + str(e)[:120]
    evidence.append("N8N_HEALTHZ: " + healthz_txt)
    log("n8n healthz: " + healthz_txt)
    if "status" not in healthz_txt or "ok" not in healthz_txt.lower():
        problems.append("n8n readiness healthz not ok: " + healthz_txt)

    # 3) postgres health
    out, _ = ssh_run(client, "docker ps --format '{{.Names}}\\t{{.Status}}' | grep -iE 'postgres' || echo NO_POSTGRES")
    pg_line = out.strip()
    evidence.append("POSTGRES: " + pg_line)
    log("postgres: " + pg_line)
    if "NO_POSTGRES" in pg_line or "unhealthy" in pg_line.lower() or "Up" not in pg_line:
        problems.append("postgres container not healthy: " + pg_line[:200])

    # 4) runner network + dns + tcp from runner
    out, _ = ssh_run(client, f"docker exec {runner} getent hosts postgres 2>&1 || echo GETENT_FAIL")
    dns_line = out.strip()
    evidence.append("RUNNER_DNS postgres: " + dns_line)
    log("runner dns postgres: " + dns_line)
    if "10.0.0.1" in dns_line or "GETENT_FAIL" in dns_line or not re.search(r"10\.0\.2\.\d+", dns_line):
        problems.append("runner postgres DNS resolves to stale/host-gateway or fails: " + dns_line)

    out, _ = ssh_run(client, f"docker exec {runner} sh -c 'nc -z -w3 postgres 5432 && echo TCP_OK || echo TCP_FAIL'" )
    tcp_line = out.strip()
    evidence.append("RUNNER_TCP postgres:5432: " + tcp_line)
    log("runner tcp postgres:5432: " + tcp_line)
    if "TCP_OK" not in tcp_line:
        problems.append("runner TCP to postgres:5432 failed: " + tcp_line)
    # omit broken line

    # 5) bounded recent log signatures
    out, _ = ssh_run(client, f"docker logs --since=60m {runner} 2>&1 | grep -E 'ECONNREFUSED|10\\\\.0\\\\.0\\\\.1|Cannot use a pool|pool.*end|pool.*closed' | tail -20")
    sig = out.strip()
    evidence.append("LOG_SIGNATURES(60m runner):\n" + (sig or "(none)"))
    log("log signatures (60m runner): " + (sig[:300] or "(none)"))
    if sig:
        problems.append("runner log signature found: " + sig[:300])

    out, _ = ssh_run(client, "docker logs --since=60m $(docker ps -q -f name=n8n-n4) 2>&1 | grep -E 'Cannot use a pool|pool.*end|pool.*closed' | tail -10")
    pool = out.strip()
    if pool:
        problems.append("n8n pool-closure signature: " + pool[:300])
        evidence.append("POOL_SIG:\n" + pool)

    client.close()

    severity = "healthy"
    if problems:
        severity = "unhealthy"
    fingerprint = "|".join(sorted(problems))[:400] if problems else ""

    # Dedup: only email again when fingerprint changes OR recovery happened OR reminder interval elapsed
    should_send = False
    prev = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                prev = json.load(f)
        except Exception:
            prev = {}
    now = time.time()
    reminder_interval = 6 * 3600  # re-alert if still broken after 6h
    if problems:
        if prev.get("fingerprint") != fingerprint:
            should_send = True
        elif prev.get("severity") != severity:
            should_send = True
        elif prev.get("last_alert", 0) and (now - prev["last_alert"]) > reminder_interval:
            should_send = True
    else:
        # recovery: alert once that it's healthy again (resolution notice)
        if prev.get("severity") == "unhealthy":
            should_send = True
            severity = "recovered"

    alert_sent = False
    if should_send:
        subject = f"[LiveTransparent] {severity.upper()}: n8n/postgres/runner monitor"
        body_lines = ["UTC time: " + datetime.datetime.utcnow().isoformat(), "Severity: " + severity]
        body_lines += ["Action: ALERT / escalate (no auto-restart performed)"] if problems else ["Action: issue cleared"]
        body_lines.append("")
        body_lines += evidence
        body_lines.append("")
        body_lines.append("Next: check docs/sessions in the LiveTransparent repo; do not restart postgres/redis or rotate keys without explicit approval.")
        raw = "To: " + RECIPIENT + "\nFrom: " + RECIPIENT + "\nSubject: " + subject + "\n\n" + "\n".join(body_lines)
        rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gmail_send.py"), "--stdin"], input=raw,
                            capture_output=True, text=True, timeout=60)
        if "SENT_OK" in rc.stdout:
            log(f"ALERT EMAIL SENT: {subject}")
            alert_sent = True
        else:
            log(f"ALERT EMAIL FAILED: {rc.stdout.strip()[:200]} {rc.stderr[:200]}")

    new_last_alert = prev.get("last_alert", 0)
    if alert_sent:
        new_last_alert = now
    # persist state
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"timestamp": now, "severity": severity, "problems": problems,
                   "fingerprint": fingerprint,
                   "last_alert": new_last_alert},
                  f, indent=2)

    if args.auto_fix and problems and not any("postgres" in p for p in problems):
        # bounded auto-fix: at most one runner or n8n recreate, never db
        log("AUTO-FIX requested but disabled in this build (requires separate approved job).")
    elif problems and severity == "unhealthy":
        log("MONITOR RESULT: unhealthy (no auto-fix run; escalate)")

    if not QUIET:
        print("RESULT severity=", severity)
    sys.exit(0 if severity in ("healthy","recovered") else 2)

def send_alert(subject, body):
    raw = "To: " + RECIPIENT + "\nFrom: " + RECIPIENT + "\nSubject: " + subject + "\n\n" + body
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "gmail_send.py"), "--stdin"], input=raw,
                   capture_output=True, text=True, timeout=60)

if __name__ == "__main__":
    main()
