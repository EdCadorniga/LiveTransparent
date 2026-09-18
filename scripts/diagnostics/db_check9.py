import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Check networks to see what containers talk to each other
stdin, stdout, stderr = ssh.exec_command("docker network ls --format '{{.Name}} {{.Driver}}'")
print("=== Networks ===")
sys.stdout.write(''.join(stdout.readlines()))

# Check all ports being listened on
stdin, stdout, stderr = ssh.exec_command("ss -tlnp | grep -E '5432|3306' || netstat -tlnp 2>/dev/null | grep -E '5432|3306' || echo 'no matches'")
print("=== DB listening ports ===")
sys.stdout.write(''.join(stdout.readlines()))

# Look for env files in /data-caddy  
stdin, stdout, stderr = ssh.exec_command("find /data-caddy -type f -name '*.env' -o -name '*.yml' -o -name '*.yaml' -o -name '*.conf' 2>/dev/null | head -30")
print("=== /data-caddy config files ===")
sys.stdout.write(''.join(stdout.readlines()))

# Look for any n8n-related env/config outside Docker
stdin, stdout, stderr = ssh.exec_command("find / -maxdepth 4 -name 'n8n*' -type f 2>/dev/null | grep -v proc | grep -v sys | head -20")
print("=== n8n files ===")
sys.stdout.write(''.join(stdout.readlines()))

# Try to access the postgres-uokgs4 container as root
stdin, stdout, stderr = ssh.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -c '\\l'")
print("=== All databases on postgres-uokgs4 ===")
sys.stdout.write(''.join(stdout.readlines()))

ssh.close()
