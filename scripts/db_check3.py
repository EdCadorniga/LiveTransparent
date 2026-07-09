import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

queries = [
    ("Row count", "SELECT count(1) FROM linkedin_connection_state;"),
    ("Status distribution", "SELECT connection_status, count(1) as cnt FROM linkedin_connection_state GROUP BY connection_status ORDER BY cnt DESC;"),
    ("Ready rows sample", q := "SELECT ghl_contact_id, connection_status, linkedin_profile_url IS NULL OR linkedin_profile_url = '' as empty_url, created_at, updated_at FROM linkedin_connection_state WHERE connection_status = $$ready$$ LIMIT 5;"),
    ("All distinct statuses", "SELECT distinct connection_status FROM linkedin_connection_state ORDER BY connection_status;"),
    ("Important tables size", "SELECT tablename, n_live_tup FROM pg_stat_user_tables WHERE schemaname = $$public$$ ORDER BY n_live_tup DESC;"),
]

for label, sql in queries:
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d n8n\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"=== {label} ===")
    sys.stdout.write(''.join(stdout.readlines()))
    err = ''.join(stderr.readlines())
    if err.strip():
        print(f"ERR: {err}")

ssh.close()
