import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

queries = [
    ("Databases", "SELECT datname FROM pg_database WHERE datistemplate = false;"),
    ("Tables in n8n", "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND table_type = 'BASE TABLE' ORDER BY table_schema, table_name;"),
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

# Also check what Postgres credentials are in the n8n container env
stdin, stdout, stderr = ssh.exec_command("docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{json .Config.Env}}' | python3 -c \"import json,sys; env=json.loads(sys.stdin.read()); [print(e) for e in env if 'POSTGRES' in e.upper() or 'DB_' in e or 'DATABASE' in e or 'REPORT' in e]\"")
print("=== n8n DB env (all DB_) ===")
sys.stdout.write(''.join(stdout.readlines()))

ssh.close()
