import paramiko, io

key = paramiko.Ed25519Key.from_private_key(io.StringIO("""-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqgAAAKArF/VtKxf1
bQAAAAtzc2gtZWQyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqg
AAAEA/o9sR01By1+26drEX03KrwY2sB/47/87xZsDzflmJBSru6ifk5XZ5S4YvY9xofz/x
ce9jDj03kLRRjZ0Y55mqAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----"""))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Check if psql exists on host
_, stdout, _ = ssh.exec_command("which psql 2>/dev/null || apt list --installed 2>/dev/null | grep postgresql-client || echo 'no psql'")
print('psql check:', stdout.read().decode().strip()[:200])

# Check DATABASE_URL from n8n container env
_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 env | grep DATABASE_URL")
db_url = stdout.read().decode().strip()
print(f'DATABASE_URL found: {bool(db_url)}')
if db_url:
    # Extract host:port
    print(f'  (first 50 chars): {db_url[:50]}...')

# Try using n8n's built-in pg connection via node
_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 node -e \"const { Client } = require('pg'); console.log('pg module available')\" 2>/dev/null || echo 'pg module not found'")
print(stdout.read().decode().strip()[:100])

ssh.close()
