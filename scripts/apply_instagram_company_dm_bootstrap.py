import base64
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "postgres" / "instagram-company-dm-bootstrap.sql"
SSH_KEY = Path(r"C:\Users\edmon\.ssh\local-upload")


def run(client, command):
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(error or output or f"Remote command failed with status {status}")
    return output


key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)

try:
    containers = run(client, "docker ps --format '{{.Names}}\\t{{.Image}}' | grep -i postgres")
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
    database = "n8n"
    encoded_sql = base64.b64encode(SQL_PATH.read_bytes()).decode()
    command = (
        f"docker exec {postgres} sh -lc "
        f"'echo {encoded_sql} | base64 -d | psql -v ON_ERROR_STOP=1 -U {user} -d {database}'"
    )
    run(client, command)

    verify = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'instagram_company_dm_state',
    'instagram_company_dm_send_log',
    'instagram_company_dm_run',
    'instagram_inbound_reply_events'
  )
ORDER BY table_name;

SELECT campaign_key || '|' || COUNT(1)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
GROUP BY campaign_key
ORDER BY MIN(campaign_priority);

SELECT 'total|' || COUNT(1)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg';

SELECT 'duplicate_handles|' || COUNT(1)
FROM (
  SELECT normalized_username
  FROM instagram_company_dm_state
  WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
  GROUP BY normalized_username
  HAVING COUNT(1) > 1
) duplicates;

SELECT 'association_status|' || campaign_key || '|' ||
  COUNT(1) FILTER (WHERE CARDINALITY(associated_ghl_contact_ids) > 0) || '|' ||
  COALESCE(SUM(CARDINALITY(associated_ghl_contact_ids)), 0)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
GROUP BY campaign_key
ORDER BY MIN(campaign_priority);

SELECT 'send_log_rows|' || COUNT(1)
FROM instagram_company_dm_send_log;

SELECT 'send_log_status|' || status || '|' || COUNT(1)
FROM instagram_company_dm_send_log
WHERE workflow_run_id LIKE 'partnership_sender:%'
GROUP BY status
ORDER BY status;

SELECT 'crashed_claimed|' || COUNT(1) || '|' || STRING_AGG(claim_owner, ',')
FROM instagram_company_dm_state
WHERE workflow_run_id LIKE 'partnership_sender:759621%'
  AND claim_owner <> ''
GROUP BY claim_owner;

SELECT 'identity_status|' || identity_status || '|' || COUNT(1)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
GROUP BY identity_status
ORDER BY identity_status;

SELECT 'identity_campaign_status|' || campaign_key || '|' || identity_status || '|' || COUNT(1)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
GROUP BY campaign_key, identity_status
ORDER BY MIN(campaign_priority), identity_status;

SELECT 'identity_failure|' || failure_reason || '|' || COUNT(1)
FROM instagram_company_dm_state
WHERE unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
  AND failure_reason <> ''
GROUP BY failure_reason
ORDER BY COUNT(1) DESC, failure_reason;

SELECT 'pool_company_match|' || s.campaign_key || '|' || COUNT(DISTINCT s.id) || '|' || COUNT(DISTINCT epc.ghl_contact_id)
FROM instagram_company_dm_state s
JOIN emerging_pool_contacts epc
  ON REGEXP_REPLACE(LOWER(s.company_name), '[^a-z0-9]+', '', 'g') =
     REGEXP_REPLACE(LOWER(epc.company_name), '[^a-z0-9]+', '', 'g')
 AND epc.ghl_contact_id IS NOT NULL
 AND epc.ghl_contact_id <> ''
WHERE s.unipile_account_id = 'F2UprZ8aQc6Qm9CYYWU6cg'
GROUP BY s.campaign_key
ORDER BY MIN(s.campaign_priority);

SELECT 'report_contact_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'report_raw_ghl_contacts'
ORDER BY ordinal_position;

SELECT 'partnership_release_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'partnership_release_log'
ORDER BY ordinal_position;

SELECT 'partnership_state_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'partnership_linkedin_connection_state'
ORDER BY ordinal_position;

SELECT 'partnership_payload_key|' || key || '|' || COUNT(1)
FROM partnership_linkedin_connection_state,
LATERAL JSONB_OBJECT_KEYS(payload_json) AS key
GROUP BY key
ORDER BY COUNT(1) DESC, key;

SELECT 'partnership_metadata_key|' || key || '|' || COUNT(1)
FROM partnership_linkedin_connection_state,
LATERAL JSONB_OBJECT_KEYS(metadata_json) AS key
GROUP BY key
ORDER BY COUNT(1) DESC, key;

SELECT 'email_event_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'Email_Events'
ORDER BY ordinal_position;

SELECT 'linkedin_activity_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'linkedin_activity_events'
ORDER BY ordinal_position;

SELECT 'email_event_type|' || LOWER(event_type) || '|' || COUNT(1)
FROM "Email_Events"
GROUP BY LOWER(event_type)
ORDER BY COUNT(1) DESC, LOWER(event_type);

SELECT 'linkedin_event_type|' || LOWER(event_type) || '|' || COUNT(1)
FROM linkedin_activity_events
GROUP BY LOWER(event_type)
ORDER BY COUNT(1) DESC, LOWER(event_type);

SELECT 'instagram_activity_column|' || column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'instagram_activity_events'
ORDER BY ordinal_position;
"""
    encoded_verify = base64.b64encode(verify.encode()).decode()
    result = run(
        client,
        f"docker exec {postgres} sh -lc "
        f"'echo {encoded_verify} | base64 -d | psql -v ON_ERROR_STOP=1 -U {user} -d {database} -At'",
    )
    print(result, end="")
finally:
    client.close()
