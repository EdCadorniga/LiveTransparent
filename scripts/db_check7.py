import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# List n8n credentials with correct camelCase column names
sql = 'SELECT id, name, type, "createdAt" FROM credentials_entity ORDER BY "createdAt" DESC LIMIT 30;'
b64 = base64.b64encode(sql.encode()).decode()
cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d n8n\""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("=== n8n credentials ===")
sys.stdout.write(''.join(stdout.readlines()))
err = ''.join(stderr.readlines())
if err.strip():
    print(f"ERR: {err}")

# Check for other postgres services
cmd2 = "docker ps --format '{{.Names}} {{.Image}} {{.Ports}}' | grep -i postgres"
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print("=== Postgres containers ===")
sys.stdout.write(''.join(stdout2.readlines()))

# Check if host has a postgres listening on standard port
cmd3 = "ss -tlnp | grep 5432 || netstat -tlnp 2>/dev/null | grep 5432 || echo 'no host postgres'"
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print("=== Postgres on host ===")
sys.stdout.write(''.join(stdout3.readlines()))

# Check n8n Postgres account credential specifically
sql2 = "SELECT id, name, type, substring(data::text, 1, 200) as data_preview FROM credentials_entity WHERE id = 'pgAzUqpwOiGkGXzO';"
b64 = base64.b64encode(sql2.encode()).decode()
cmd3 = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d n8n\""
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print("=== Credential pgAzUqpwOiGkGXzO ===")
sys.stdout.write(''.join(stdout3.readlines()))
err3 = ''.join(stderr3.readlines())
if err3.strip():
    print(f"ERR: {err3}")

ssh.close()
