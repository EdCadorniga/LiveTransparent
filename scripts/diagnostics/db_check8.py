import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Try to find tables in postgres database (different from n8n database)
# The "Postgres account" might connect to a completely different database
databases_to_check = ["postgres", "n8n"]

for db in databases_to_check:
    sql = f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND table_type = 'BASE TABLE' ORDER BY table_name;"
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d {db}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = ''.join(stdout.readlines())
    err = ''.join(stderr.readlines())
    if 'does not exist' in err or 'does not exist' in out:
        print(f"=== DB '{db}' does not exist or not accessible ===")
    elif 'authentication failed' in err.lower() or 'authentication failed' in out.lower():
        print(f"=== DB '{db}' auth failed ===")
    else:
        print(f"=== Tables in DB '{db}' ===")
        sys.stdout.write(out)
    if err.strip() and 'does not exist' not in err and 'authentication' not in err.lower():
        print(f"ERR: {err[:200]}")

# Check if there's an external Postgres in /data-caddy directory
cmd3 = "cat /data-caddy/docker-compose.yml 2>/dev/null | head -100"
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print("=== docker-compose (top) ===")
sys.stdout.write(''.join(stdout3.readlines()))

ssh.close()
