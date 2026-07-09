import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# List all n8n credentials - get id, name, type
sql = "SELECT id, name, type, created_at FROM credentials_entity ORDER BY created_at DESC LIMIT 20;"
b64 = base64.b64encode(sql.encode()).decode()
cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d n8n\""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("=== n8n credentials (id, name, type) ===")
sys.stdout.write(''.join(stdout.readlines()))
err = ''.join(stderr.readlines())
if err.strip():
    print(f"ERR: {err}")

# Check all .env files for POSTGRES/DB connection strings
# Use find on the VPS
cmd2 = "find /data-caddy -name '*.env' -o -name '*.conf' -o -name '*.yml' -o -name '*.yaml' 2>/dev/null | head -20"
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print("=== Config files in /data-caddy ===")
sys.stdout.write(''.join(stdout2.readlines()))

# Check Coolify's database for application configurations
# Coolify might store connection details for services
cmd3 = "docker exec coolify-db psql -U coolify -c 'SELECT datname FROM pg_database;' 2>&1 | head -10"
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print("=== Coolify databases ===")
sys.stdout.write(''.join(stdout3.readlines()))

ssh.close()
