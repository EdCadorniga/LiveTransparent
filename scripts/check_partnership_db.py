import base64
import paramiko


key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key, timeout=30)
try:
    _, stdout, _ = client.exec_command("docker ps --format '{{.Names}}\\t{{.Image}}' | grep -i postgres")
    rows = stdout.read().decode().strip().splitlines()
    print("containers:", rows)
    postgres = next(row.split("\t")[0] for row in rows if row.split("\t")[0].startswith("postgres-"))
    query = """
SELECT 'release_log' AS table_name, count(*) AS rows FROM partnership_release_log
UNION ALL
SELECT 'li_state', count(*) FROM partnership_linkedin_connection_state;
SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE 'partnership%' ORDER BY tablename, indexname;
SELECT source_key, count(*) FROM partnership_linkedin_connection_state GROUP BY source_key;
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('linkedin_activity_events', 'SimpleTexting_Campaign_Event_Log', 'Email_Events', 'DAN_Release_Log', 'Emerald_Release_Log')
ORDER BY table_name, ordinal_position;
SELECT COALESCE(campaign_type, ''), COALESCE(source_key, ''), event_type, count(*)
FROM linkedin_activity_events
WHERE event_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
SELECT campaign_key, event_type, count(*)
FROM "SimpleTexting_Campaign_Event_Log"
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1, 2
ORDER BY 1, 2;
"""
    _, env_out, _ = client.exec_command(f"docker exec {postgres} env")
    environment = {}
    for line in env_out.read().decode().splitlines():
        if "=" in line:
            key_name, value = line.split("=", 1)
            environment[key_name] = value
    user = environment.get("POSTGRES_USER", "postgres")
    database = environment.get("POSTGRES_DB", "postgres")
    encoded_query = base64.b64encode(query.encode()).decode()
    command = f"docker exec {postgres} sh -lc 'echo {encoded_query} | base64 -d | psql -U {user} -d {database} -At'"
    _, stdout, stderr = client.exec_command(command)
    print(stdout.read().decode(), end="")
    print(stderr.read().decode(), end="")
finally:
    client.close()
