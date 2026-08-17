import base64

import paramiko


QUERY = """
SELECT 'linkedin_status' AS section, connection_status AS key, count(*)::text AS value
FROM linkedin_connection_state
GROUP BY connection_status
UNION ALL
SELECT 'partnership_status', connection_status, count(*)::text
FROM partnership_linkedin_connection_state
GROUP BY connection_status
UNION ALL
SELECT 'social_platform_status', COALESCE(platform, 'null') || ':' || COALESCE(status, 'null'), count(*)::text
FROM report_raw_ghl_social_posts
GROUP BY platform, status
UNION ALL
SELECT 'social_freshness', 'row_count', count(*)::text
FROM report_raw_ghl_social_posts
UNION ALL
SELECT 'social_freshness', 'latest_loaded_at', COALESCE(MAX(loaded_at)::text, '')
FROM report_raw_ghl_social_posts
UNION ALL
SELECT 'social_freshness', 'latest_published_at', COALESCE(MAX(published_at)::text, '')
FROM report_raw_ghl_social_posts
UNION ALL
SELECT 'oauth_columns', column_name, data_type
FROM information_schema.columns
WHERE table_name = 'ghl_oauth_tokens'
UNION ALL
SELECT 'oauth_rows', COALESCE(active::text, 'null'), COALESCE(length(access_token), 0)::text
FROM ghl_oauth_tokens
UNION ALL
SELECT 'linkedin_events', event_type, count(*)::text
FROM linkedin_activity_events
GROUP BY event_type
UNION ALL
SELECT 'instagram_events', event_type, count(*)::text
FROM instagram_activity_events
GROUP BY event_type
ORDER BY section, key;
"""


key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)
try:
    _, stdout, _ = client.exec_command("docker ps --format '{{.Names}}' | grep '^postgres-'")
    postgres = stdout.read().decode().strip().splitlines()[0]
    _, stdout, _ = client.exec_command(f"docker exec {postgres} env")
    environment = dict(line.split("=", 1) for line in stdout.read().decode().splitlines() if "=" in line)
    encoded = base64.b64encode(QUERY.encode()).decode()
    command = (
        f"docker exec {postgres} sh -lc 'echo {encoded} | base64 -d | "
        f"psql -U {environment.get('POSTGRES_USER', 'postgres')} "
        f"-d {environment.get('POSTGRES_DB', 'postgres')} -At -F \"|\"'"
    )
    _, stdout, stderr = client.exec_command(command)
    print(stdout.read().decode(), end="")
    print(stderr.read().decode(), end="")
finally:
    client.close()
