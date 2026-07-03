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

# Find the database name by listing all databases
cmd = """docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -c "SELECT source_list, COUNT(*), COUNT(DISTINCT emerald_contact_id) as unique_ids FROM emerging_pool_contacts GROUP BY source_list;" 2>/dev/null || docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c "SELECT source_list, COUNT(*), COUNT(DISTINCT emerald_contact_id) as unique_ids FROM emerging_pool_contacts GROUP BY source_list;" 2>/dev/null || echo 'Trying with env password...'"""

_, stdout, _ = ssh.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U n8n -d n8n -c 'SELECT source_list, COUNT(*) as count, COUNT(DISTINCT emerald_contact_id) as unique_ids FROM emerging_pool_contacts GROUP BY source_list;' 2>&1")
out = stdout.read().decode().strip()
print(out)

_, stdout, _ = ssh.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c 'SELECT source_list, COUNT(*) as count FROM emerging_pool_contacts GROUP BY source_list;' 2>&1")
out2 = stdout.read().decode().strip()
print('\nWith postgres user:', out2)

ssh.close()
