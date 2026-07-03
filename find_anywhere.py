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

# List databases in app postgres
_, o, _ = s.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -c 'SELECT datname FROM pg_database' 2>&1")
print("App PG databases:", o.read().decode().strip())

# List databases in coolify-db
_, o, _ = s.exec_command("docker exec coolify-db psql -U postgres -c 'SELECT datname FROM pg_database' 2>&1")
print("Coolify databases:", o.read().decode().strip())

# Try to find emerging_pool_contacts across all tables in app PG
_, o, _ = s.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -d n8n -c \"SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%%emerging%%'\" 2>&1")
print("Search app PG:", o.read().decode().strip()[:500])

# Try in coolify-db with env user
_, o, _ = s.exec_command("docker exec coolify-db psql -U coolify -d coolify -c \"SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%%emerging%%'\" 2>&1")
print("Search coolify:", o.read().decode().strip()[:500])

s.close()
