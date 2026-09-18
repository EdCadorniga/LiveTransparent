import base64
import json
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "Partnership Marketing" / "partnership_master.json"
SSH_KEY = Path(r"C:\Users\edmon\.ssh\local-upload")
INSTAGRAM_ACCOUNT_ID = "F2UprZ8aQc6Qm9CYYWU6cg"


def run(client, command):
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(error or output or f"Remote command failed with status {status}")
    return output


partnership_rows = []
for contact in json.loads(MASTER_PATH.read_text(encoding="utf-8")):
    company_name = str(contact.get("company_name") or "").strip()
    if not company_name:
        continue
    emails = {str(value or "").strip().lower() for value in contact.get("all_emails", [])}
    linkedin_urls = {str(value or "").strip().lower() for value in contact.get("all_linkedin_urls", [])}
    if contact.get("email"):
        emails.add(str(contact["email"]).strip().lower())
    if contact.get("linkedin_url"):
        linkedin_urls.add(str(contact["linkedin_url"]).strip().lower())
    for email in sorted(value for value in emails if value):
        partnership_rows.append({"company_name": company_name, "email": email, "linkedin_url": ""})
    for linkedin_url in sorted(value for value in linkedin_urls if value):
        partnership_rows.append({"company_name": company_name, "email": "", "linkedin_url": linkedin_url})

source_json = json.dumps(partnership_rows, separators=(",", ":"), ensure_ascii=False)
source_base64 = base64.b64encode(source_json.encode()).decode()
sql = f"""
BEGIN;

CREATE TEMP TABLE partnership_source_map AS
SELECT company_name, email, linkedin_url
FROM JSONB_TO_RECORDSET(
  CONVERT_FROM(DECODE('{source_base64}', 'base64'), 'UTF8')::jsonb
) AS source(company_name TEXT, email TEXT, linkedin_url TEXT);

WITH partnership_pairs AS (
  SELECT
    REGEXP_REPLACE(LOWER(source.company_name), '[^a-z0-9]+', '', 'g') AS company_key,
    state.ghl_contact_id
  FROM partnership_source_map source
  JOIN partnership_linkedin_connection_state state
    ON source.linkedin_url <> ''
   AND (
     REGEXP_REPLACE(SPLIT_PART(LOWER(source.linkedin_url), '?', 1), '/+$', '', 'g') =
       REGEXP_REPLACE(SPLIT_PART(LOWER(state.linkedin_profile_url), '?', 1), '/+$', '', 'g')
     OR REGEXP_REPLACE(
       REGEXP_REPLACE(SPLIT_PART(LOWER(source.linkedin_url), '?', 1), '/+$', '', 'g'),
       '^.*/', '', 'g'
     ) = LOWER(state.linkedin_public_identifier)
   )
  WHERE state.ghl_contact_id <> ''

  UNION

  SELECT
    REGEXP_REPLACE(LOWER(source.company_name), '[^a-z0-9]+', '', 'g') AS company_key,
    release.ghl_contact_id
  FROM partnership_source_map source
  JOIN partnership_release_log release
    ON source.email <> ''
   AND LOWER(source.email) = LOWER(release.contact_email)
  WHERE release.ghl_contact_id <> ''
), partnership_matches AS (
  SELECT company_key, ARRAY_AGG(DISTINCT ghl_contact_id ORDER BY ghl_contact_id) AS contact_ids
  FROM partnership_pairs
  GROUP BY company_key
)
UPDATE instagram_company_dm_state state
SET associated_ghl_contact_ids = matches.contact_ids,
    primary_ghl_contact_id = matches.contact_ids[1],
    updated_at = NOW()
FROM partnership_matches matches
WHERE state.unipile_account_id = '{INSTAGRAM_ACCOUNT_ID}'
  AND state.campaign_key = 'partnerships'
  AND REGEXP_REPLACE(LOWER(state.company_name), '[^a-z0-9]+', '', 'g') = matches.company_key;

WITH pool_matches AS (
  SELECT
    state.id,
    ARRAY_AGG(DISTINCT pool.ghl_contact_id ORDER BY pool.ghl_contact_id) AS contact_ids
  FROM instagram_company_dm_state state
  JOIN emerging_pool_contacts pool
    ON REGEXP_REPLACE(LOWER(state.company_name), '[^a-z0-9]+', '', 'g') =
       REGEXP_REPLACE(LOWER(pool.company_name), '[^a-z0-9]+', '', 'g')
   AND pool.ghl_contact_id IS NOT NULL
   AND pool.ghl_contact_id <> ''
   AND (
     (state.campaign_key = 'dan_brands' AND LOWER(pool.source_list) LIKE '%brand%') OR
     (state.campaign_key = 'dan_dispensaries' AND LOWER(pool.source_list) LIKE '%dispensar%')
   )
  WHERE state.unipile_account_id = '{INSTAGRAM_ACCOUNT_ID}'
  GROUP BY state.id
)
UPDATE instagram_company_dm_state state
SET associated_ghl_contact_ids = matches.contact_ids,
    primary_ghl_contact_id = matches.contact_ids[1],
    updated_at = NOW()
FROM pool_matches matches
WHERE state.id = matches.id;

COMMIT;

SELECT 'partnership_source_urls|' || COUNT(1)
FROM partnership_source_map
WHERE linkedin_url <> '';

SELECT 'partnership_state_rows|' || COUNT(1) || '|' ||
  COUNT(1) FILTER (WHERE linkedin_public_identifier <> '') || '|' ||
  COUNT(1) FILTER (WHERE linkedin_profile_url <> '')
FROM partnership_linkedin_connection_state;

SELECT 'partnership_identifier_matches|' || COUNT(1)
FROM partnership_source_map source
JOIN partnership_linkedin_connection_state state
  ON source.linkedin_url <> ''
 AND REGEXP_REPLACE(
   REGEXP_REPLACE(SPLIT_PART(LOWER(source.linkedin_url), '?', 1), '/+$', '', 'g'),
   '^.*/', '', 'g'
 ) = LOWER(state.linkedin_public_identifier);

SELECT
  campaign_key || '|' ||
  COUNT(1) FILTER (WHERE CARDINALITY(associated_ghl_contact_ids) > 0) || '|' ||
  COALESCE(SUM(CARDINALITY(associated_ghl_contact_ids)), 0) || '|' ||
  COUNT(1) FILTER (WHERE primary_ghl_contact_id <> '')
FROM instagram_company_dm_state
WHERE unipile_account_id = '{INSTAGRAM_ACCOUNT_ID}'
GROUP BY campaign_key
ORDER BY MIN(campaign_priority);
"""

key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)

try:
    containers = run(client, "docker ps --format '{{.Names}}\t{{.Image}}' | grep -i postgres")
    postgres = next(
        row.split("\t")[0]
        for row in containers.strip().splitlines()
        if row.split("\t")[0].startswith("postgres-")
    )
    environment = {}
    for line in run(client, f"docker exec {postgres} env").splitlines():
        if "=" in line:
            name, value = line.split("=", 1)
            environment[name] = value
    user = environment.get("POSTGRES_USER", "postgres")
    encoded_sql = base64.b64encode(sql.encode()).decode()
    command = (
        f"docker exec {postgres} sh -lc "
        f"'echo {encoded_sql} | base64 -d | psql -v ON_ERROR_STOP=1 -U {user} -d n8n -At'"
    )
    print(run(client, command), end="")
finally:
    client.close()
