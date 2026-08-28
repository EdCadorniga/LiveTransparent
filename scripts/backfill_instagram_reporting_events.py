"""Copy authoritative Instagram activity events from n8n DB to report DB."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import paramiko


SSH_KEY = Path(r"C:\Users\edmon\.ssh\local-upload")
HOST = "89.117.21.29"
CONTAINER_QUERY = "docker ps --format '{{.Names}}' | grep '^postgres-' | head -1"


def shell(ssh: paramiko.SSHClient, command: str) -> str:
    _, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0:
        raise RuntimeError(error or output or "remote command failed")
    return output


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def psql(ssh: paramiko.SSHClient, container: str, database: str, sql: str) -> str:
    encoded = base64.b64encode(sql.encode()).decode()
    command = (
        f"docker exec {container} sh -lc "
        f"\"echo {encoded} | base64 -d | psql -v ON_ERROR_STOP=1 -U postgres -d {database} -At\""
    )
    return shell(ssh, command)


def main() -> None:
    key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username="root", pkey=key, timeout=30)
    try:
        container = shell(ssh, CONTAINER_QUERY).strip()
        if not container:
            raise RuntimeError("Postgres container not found")

        ddl = """
CREATE TABLE IF NOT EXISTS instagram_activity_events (
  event_id BIGSERIAL PRIMARY KEY,
  event_key TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  event_at TIMESTAMPTZ NOT NULL,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  campaign_key TEXT NOT NULL DEFAULT 'instagram',
  chat_id TEXT NOT NULL DEFAULT '',
  message_id TEXT NOT NULL DEFAULT '',
  provider_id TEXT NOT NULL DEFAULT '',
  workflow_name TEXT NOT NULL DEFAULT '',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
        psql(ssh, container, "postgres", ddl)
        raw = psql(
            ssh,
            container,
            "n8n",
            "SELECT row_to_json(e)::text FROM instagram_activity_events e ORDER BY event_at, event_id;",
        )
        events = [json.loads(line) for line in raw.splitlines() if line.strip()]
        statements = []
        for event in events:
            payload = json.dumps(event.get("payload_json") or {}, separators=(",", ":"))
            sql = """INSERT INTO instagram_activity_events
              (event_key, event_type, event_at, ghl_contact_id, campaign_key, chat_id,
               message_id, provider_id, workflow_name, payload_json)
            VALUES ({event_key}, {event_type}, {event_at}::timestamptz, {contact}, {campaign},
                    {chat}, {message}, {provider}, {workflow}, {payload}::jsonb)
            ON CONFLICT (event_key) DO NOTHING;""".format(
                event_key=sql_literal(event.get("event_key")),
                event_type=sql_literal(event.get("event_type")),
                event_at=sql_literal(event.get("event_at")),
                contact=sql_literal(event.get("ghl_contact_id") or ""),
                campaign=sql_literal(event.get("campaign_key") or "instagram"),
                chat=sql_literal(event.get("chat_id") or ""),
                message=sql_literal(event.get("message_id") or ""),
                provider=sql_literal(event.get("provider_id") or ""),
                workflow=sql_literal(event.get("workflow_name") or ""),
                payload=sql_literal(payload),
            )
            statements.append(sql)
        if statements:
            psql(ssh, container, "postgres", "BEGIN;\n" + "\n".join(statements) + "\nCOMMIT;")
        count = psql(ssh, container, "postgres", "SELECT COUNT(*) FROM instagram_activity_events;").strip()
        print(json.dumps({"sourceEvents": len(events), "reportEventCount": int(count or 0)}))
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
