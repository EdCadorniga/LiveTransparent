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

cmds = [
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -c 'SELECT datname FROM pg_database' 2>&1",
    "docker exec coolify-db psql -U postgres -c 'SELECT datname FROM pg_database' 2>&1",
    "docker exec coolify-db psql -U postgres -d postgres -c \"SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%emerging%'\" 2>&1",
]

for cmd in cmds:
    _, stdout, _ = ssh.exec_command(cmd)
    print(stdout.read().decode().strip()[:500])
    print('---')

ssh.close()
