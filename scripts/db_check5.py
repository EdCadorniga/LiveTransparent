import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Check coolify-db for reporting tables
queries_coolify = [
    ("Coolify DB list", "SELECT datname FROM pg_database WHERE datistemplate = false;"),
]

for label, sql in queries_coolify:
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = f"docker exec coolify-db sh -c \"echo {b64} | base64 -d | psql -U coolify\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"=== {label} ===")
    sys.stdout.write(''.join(stdout.readlines()))

# Check if reporting tables are on the same postgres instance but in 'postgres' or different database
# Try each database on the postgres-uokgs4... instance
for dbname in ["postgres", "n8n"]:
    sql = f"SELECT count(1) FROM information_schema.tables WHERE table_schema = 'public';"
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | PGPASSWORD='P@ssn8n%2526!' psql -U n8n -d {dbname} -h localhost\" 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = ''.join(stdout.readlines())
    err = ''.join(stderr.readlines())
    if err.strip():
        print(f"DB {dbname} (n8n pw): ERR - {err.strip()[:200]}")
    else:
        print(f"DB {dbname}: {result.strip()}")

# Try the POSTGRES_PASSWORD=$P@ssDatabase%! on n8n database
sql = "SELECT count(1) FROM information_schema.tables WHERE table_schema = 'public';"
b64 = base64.b64encode(sql.encode()).decode()
cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | PGPASSWORD='P@ssDatabase%25!' psql -U n8n -d n8n -h localhost\" 2>&1 | head -5"
stdin, stdout, stderr = ssh.exec_command(cmd)
result = ''.join(stdout.readlines())
err = ''.join(stderr.readlines())
if err.strip():
    print(f"DB n8n (reports pw): ERR - {err.strip()[:200]}")
else:
    print(f"DB n8n (reports pw): {result.strip()}")

ssh.close()
