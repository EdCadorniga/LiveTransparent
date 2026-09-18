import base64
from pathlib import Path

import paramiko


SSH_KEY = Path(r"C:\Users\edmon\.ssh\local-upload")
FAILED_RUN_ID = "instagram_company_dm_test_5_v1:758995"


def run(client, command):
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(error or output or f"Remote command failed with status {status}")
    return output


sql = f"""
BEGIN;

WITH failed AS (
  DELETE FROM instagram_company_dm_send_log
  WHERE workflow_run_id = '{FAILED_RUN_ID}'
    AND status = 'failed'
    AND error_status = '401'
  RETURNING state_id
)
UPDATE instagram_company_dm_state state
SET failure_reason = '',
    claim_owner = '',
    claimed_at = NULL,
    updated_at = NOW()
WHERE state.id IN (SELECT state_id FROM failed)
  AND state.message_step = 0;

COMMIT;

SELECT 'remaining_failed_rows|' || COUNT(1)
FROM instagram_company_dm_send_log
WHERE workflow_run_id = '{FAILED_RUN_ID}';

SELECT 'successful_test_sends|' || COUNT(1)
FROM instagram_company_dm_send_log
WHERE workflow_run_id LIKE 'instagram_company_dm_test_5_v1:%'
  AND status = 'sent';
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
