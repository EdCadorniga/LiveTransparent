import paramiko, io, sys

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Get n8n DB_URL from docker inspect
stdin, stdout, stderr = ssh.exec_command("docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{json .Config.Env}}' | python3 -c \"import json,sys; env=json.loads(sys.stdin.read()); [print(e) for e in env if 'DB_' in e or 'POSTGRES' in e or 'DATABASE' in e]\"")
print("=== n8n DB env vars ===")
sys.stdout.write(''.join(stdout.readlines()))
err = ''.join(stderr.readlines())
if err.strip():
    print("ERR:", err)

# Try connecting to the postgres-uokgs4c04ko0s4scccg40cgg container directly
# First check if we can reach it from host
stdin, stdout, stderr = ssh.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -d n8n -c 'SELECT 1;' 2>&1 || echo 'FAILED'")
print("=== Test n8n Postgres connection ===")
sys.stdout.write(''.join(stdout.readlines()))

ssh.close()
