import paramiko

key = paramiko.Ed25519Key.from_private_key_file('C:\\Users\\edmon\\.ssh\\local-upload')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=15)

# Use the raw IDs file directly (no tab suffix needed for single column COPY)
# COPY single column just needs the value on each line

# Copy the raw IDs file into the container
stdin, stdout, stderr = ssh.exec_command("docker cp /tmp/enrolled_ghl_ids.txt postgres-uokgs4c04ko0s4scccg40cgg:/tmp/enrolled_ghl_ids.txt")
out = stdout.read().decode()
err = stderr.read().decode()
print(f"docker cp: '{err[:200]}'")

# Pipe SQL via stdin
sql = """
DROP TABLE IF EXISTS enrolled_ids;
CREATE TEMP TABLE enrolled_ids (ghl_contact_id TEXT PRIMARY KEY);
\\copy enrolled_ids FROM '/tmp/enrolled_ghl_ids.txt'
UPDATE "Emerald_Campaign_Contacts" SET release_status='released', released_at=NOW()
  WHERE ghl_contact_id IN (SELECT ghl_contact_id FROM enrolled_ids)
  AND COALESCE(release_status,'pending') <> 'released';
SELECT COUNT(*) FILTER (WHERE e.ghl_contact_id IN (SELECT ghl_contact_id FROM enrolled_ids)) AS matched,
       COUNT(*) FILTER (WHERE e.ghl_contact_id NOT IN (SELECT ghl_contact_id FROM enrolled_ids)) AS unmatched
  FROM "Emerald_Campaign_Contacts" e;
SELECT release_status, COUNT(*) FROM "Emerald_Campaign_Contacts" GROUP BY release_status ORDER BY release_status;
DROP TABLE IF EXISTS enrolled_ids;
"""

stdin, stdout, stderr = ssh.exec_command("docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -v ON_ERROR_STOP=1")
stdin.write(sql)
stdin.channel.shutdown_write()
out = stdout.read().decode()
err = stderr.read().decode()
print("STDOUT:")
print(out)
if err.strip():
    print(f"STDERR: {err[:500]}")

ssh.close()
