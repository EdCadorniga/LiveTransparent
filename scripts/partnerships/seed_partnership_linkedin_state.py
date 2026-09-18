"""Seed partnership LinkedIn state rows without sending invitations or DMs."""

import base64
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
TAG = "partner_candidate_linkedin"


def load_env():
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def ghl_contacts():
    token = os.environ["GHL_PIT"]
    contacts = {}
    start_after = None
    start_after_id = None
    while True:
        params = {"locationId": LOCATION_ID, "query": TAG, "limit": 100}
        if start_after is not None:
            params["startAfter"] = start_after
            params["startAfterId"] = start_after_id
        request = urllib.request.Request(
            "https://services.leadconnectorhq.com/contacts/?" + urllib.parse.urlencode(params),
            headers={
                "Authorization": f"Bearer {token}",
                "Version": "2021-07-28",
                "Accept": "application/json",
                "User-Agent": "curl/8.0",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            rows = json.loads(response.read().decode("utf-8")).get("contacts", [])
        for contact in rows:
            tags = set(contact.get("tags") or [])
            if contact.get("source") != "partnership_outreach" or TAG not in tags:
                continue
            url = ""
            for field in contact.get("customFields") or []:
                value = str(field.get("value") or "").strip()
                if "linkedin.com/in/" in value.lower():
                    url = value
                    break
            if url:
                identifier = re.sub(r"/$", "", url.split("?", 1)[0]).rsplit("/", 1)[-1]
                contacts[contact["id"]] = (url, identifier)
        if len(rows) < 100:
            break
        cursor = rows[-1].get("startAfter") or []
        if len(cursor) != 2:
            raise RuntimeError("Missing GHL pagination cursor")
        start_after, start_after_id = cursor
        time.sleep(0.5)
    return contacts


def sql_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


load_env()
contacts = ghl_contacts()
values = []
for contact_id, (url, identifier) in contacts.items():
    values.append(
        "(" + ", ".join([
            sql_literal(contact_id),
            sql_literal(LOCATION_ID),
            sql_literal(url),
            sql_literal(identifier),
            sql_literal("partnership"),
            sql_literal("ready"),
        ]) + ")"
    )

if not values:
    raise SystemExit("No partnership LinkedIn contacts with URLs found")

query = """
CREATE TABLE IF NOT EXISTS partnership_linkedin_connection_state (
  ghl_contact_id TEXT PRIMARY KEY,
  location_id TEXT NOT NULL DEFAULT 'Zwz4relUXVPxx8uohnjV',
  unipile_account_id TEXT NOT NULL DEFAULT 'V9eiHiDpRmCtan0YNdzsQw',
  linkedin_profile_url TEXT NOT NULL DEFAULT '',
  linkedin_public_identifier TEXT NOT NULL DEFAULT '',
  linkedin_provider_id TEXT NOT NULL DEFAULT '',
  connection_request_tag TEXT NOT NULL DEFAULT 'partner_linkedin_requested',
  connection_status TEXT NOT NULL DEFAULT 'ready',
  sequence_step INTEGER NOT NULL DEFAULT 0,
  source_key TEXT NOT NULL DEFAULT 'partnership',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO partnership_linkedin_connection_state
  (ghl_contact_id, location_id, linkedin_profile_url, linkedin_public_identifier, source_key, connection_status)
VALUES
  %s
ON CONFLICT (ghl_contact_id) DO UPDATE SET
  linkedin_profile_url = EXCLUDED.linkedin_profile_url,
  linkedin_public_identifier = EXCLUDED.linkedin_public_identifier,
  updated_at = NOW(),
  connection_status = CASE
    WHEN partnership_linkedin_connection_state.connection_status IN ('requested', 'connected', 'completed')
      THEN partnership_linkedin_connection_state.connection_status
    ELSE 'ready'
  END;
SELECT connection_status, count(*) FROM partnership_linkedin_connection_state
WHERE source_key = 'partnership' GROUP BY connection_status ORDER BY connection_status;
""" % ",\n  ".join(values)

key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)
try:
    _, stdout, _ = client.exec_command("docker ps --format '{{.Names}}' | grep -i postgres | head -1")
    postgres = stdout.read().decode().strip()
    if not postgres:
        raise RuntimeError("Postgres container not found")
    _, env_out, _ = client.exec_command(f"docker exec {postgres} env")
    env = dict(line.split("=", 1) for line in env_out.read().decode().splitlines() if "=" in line)
    encoded = base64.b64encode(query.encode()).decode()
    command = (
        f"docker exec {postgres} sh -lc 'echo {encoded} | base64 -d | "
        f"psql -v ON_ERROR_STOP=1 -U {env.get('POSTGRES_USER', 'postgres')} "
        f"-d {env.get('POSTGRES_DB', 'postgres')} -At'"
    )
    _, output, error = client.exec_command(command)
    if output.channel.recv_exit_status() != 0:
        raise RuntimeError(error.read().decode())
    print(f"Seeded or refreshed {len(contacts)} partnership LinkedIn state rows")
    print(output.read().decode(), end="")
finally:
    client.close()
