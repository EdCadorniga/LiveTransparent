import paramiko, io

key_data = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqgAAAKArF/VtKxf1
bQAAAAtzc2gtZWQyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqg
AAAEA/o9sR01By1+26drEX03KrwY2sB/47/87xZsDzflmJBSru6ifk5XZ5S4YvY9xofz/x
ce9jDj03kLRRjZ0Y55mqAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----"""

key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Test query on coolify-db
_, stdout, _ = ssh.exec_command("docker exec -e PGPASSWORD=P@ssDatabase%! postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -h localhost -c 'SELECT source_list, COUNT(*) as cnt FROM emerging_pool_contacts GROUP BY source_list' 2>&1")
print('Result:', stdout.read().decode().strip()[:500])

ssh.close()
