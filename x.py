import paramiko, io
k = paramiko.Ed25519Key.from_private_key(io.StringIO("""-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqgAAAKArF/VtKxf1
bQAAAAtzc2gtZWQyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqg
AAAEA/o9sR01By1+26drEX03KrwY2sB/47/87xZsDzflmJBSru6ifk5XZ5S4YvY9xofz/x
ce9jDj03kLRRjZ0Y55mqAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----"""))
s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect("89.117.21.29", username="root", pkey=k, timeout=10)
_, o, _ = s.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -d postgres -c 'SELECT table_name FROM information_schema.tables WHERE table_name LIKE '"'"'%emerging%'"'"'' 2>&1")
print("postgres db:", o.read().decode().strip()[:200])
_, o, _ = s.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -d n8n -c 'SELECT current_database(), current_schema()' 2>&1")
print("current context:", o.read().decode().strip()[:200])
# Check what PG_Settings says in credential
_, o, _ = s.exec_command("docker exec coolify-db psql -U coolify -c 'SELECT value FROM key_value WHERE key='"'"'N8N_ENCRYPTION_KEY'"'"'' 2>&1")
print("encryption key:", o.read().decode().strip()[:200])
s.close()
