"""Load the reviewed LinkedIn backfill worklist into the live Postgres database."""
import json
import os
import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKLIST = os.path.join(ROOT, "local-scripts", "unipile_backfill_worklist.json")


def env_values():
    values = {}
    with open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def sql_literal(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


env = env_values()
with open(WORKLIST, encoding="utf-8") as handle:
    rows = json.load(handle)

values = []
for row in rows:
    counts = row.get("counts") or {}
    status = "needs_profile" if row.get("profile_error") else "pending"
    values.append(
        "(" + ", ".join(
            [
                sql_literal(row.get("chat_id")),
                sql_literal(row.get("attendee_provider_id")),
                sql_literal(row.get("profile_full_name") or row.get("attendee_name")),
                sql_literal(row.get("profile_public_identifier")),
                sql_literal(row.get("profile_url")),
                sql_literal(row.get("last_ts")),
                str(int(counts.get("messages") or 0)),
                str(int(counts.get("inbound") or 0)),
                str(int(counts.get("outbound") or 0)),
                sql_literal(status),
                sql_literal(row.get("profile_error")),
                "NOW()",
            ]
        ) + ")"
    )

sql = """
CREATE TABLE IF NOT EXISTS linkedin_backfill_worklist (
  chat_id TEXT PRIMARY KEY,
  attendee_provider_id TEXT NOT NULL,
  profile_full_name TEXT,
  profile_public_identifier TEXT,
  profile_url TEXT,
  last_ts TIMESTAMPTZ NOT NULL,
  total_messages INTEGER NOT NULL DEFAULT 0,
  inbound_messages INTEGER NOT NULL DEFAULT 0,
  outbound_messages INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','processing','done','error','needs_profile')),
  posted_count INTEGER NOT NULL DEFAULT 0,
  skipped_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  claimed_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS linkedin_backfill_worklist_status_ts
  ON linkedin_backfill_worklist (status, last_ts);
INSERT INTO linkedin_backfill_worklist
  (chat_id, attendee_provider_id, profile_full_name, profile_public_identifier, profile_url,
   last_ts, total_messages, inbound_messages, outbound_messages, status, last_error, updated_at)
VALUES
""" + ",\n".join(values) + """
ON CONFLICT (chat_id) DO UPDATE SET
  attendee_provider_id = EXCLUDED.attendee_provider_id,
  profile_full_name = COALESCE(EXCLUDED.profile_full_name, linkedin_backfill_worklist.profile_full_name),
  profile_public_identifier = COALESCE(EXCLUDED.profile_public_identifier, linkedin_backfill_worklist.profile_public_identifier),
  profile_url = COALESCE(EXCLUDED.profile_url, linkedin_backfill_worklist.profile_url),
  last_ts = EXCLUDED.last_ts,
  total_messages = EXCLUDED.total_messages,
  inbound_messages = EXCLUDED.inbound_messages,
  outbound_messages = EXCLUDED.outbound_messages,
  status = CASE WHEN linkedin_backfill_worklist.status IN ('done','processing') THEN linkedin_backfill_worklist.status ELSE EXCLUDED.status END,
  last_error = EXCLUDED.last_error,
  updated_at = NOW();
"""

key_path = os.path.expandvars(os.path.expanduser(env.get("VPS_SSH_KEY_PATH", "")))
key = None
for key_type in (paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey):
    try:
        key = key_type.from_private_key_file(key_path)
        break
    except Exception:
        pass
if key is None:
    raise SystemExit("SSH key load failed")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(env.get("VPS_HOST") or env.get("VPS_HOSTNAME"), username=env.get("VPS_USER"), pkey=key,
               timeout=20, auth_timeout=20, banner_timeout=20, look_for_keys=False, allow_agent=False)
try:
    command = "docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -v ON_ERROR_STOP=1 -X -q"
    stdin, stdout, stderr = client.exec_command(command, timeout=180)
    stdin.write(sql)
    stdin.channel.shutdown_write()
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    if err.strip():
        print(err[:4000])
    if not out and err.strip():
        raise SystemExit(1)
finally:
    client.close()

print(f"Loaded {len(rows)} rows ({sum(1 for row in rows if row.get('profile_error'))} needs_profile)")
