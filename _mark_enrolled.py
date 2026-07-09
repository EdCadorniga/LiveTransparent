import paramiko

key = paramiko.Ed25519Key.from_private_key_file('C:\\Users\\edmon\\.ssh\\local-upload')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=15)

# Write a shell script directly
sh_script = '''#!/bin/sh
set -e
PG="docker exec -i postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d postgres -c"

echo "Creating temp table..."
$PG "CREATE TEMP TABLE enrolled_ids (ghl_contact_id TEXT PRIMARY KEY);"

echo "Inserting IDs..."
i=0
while read -r cid; do
  $PG "INSERT INTO enrolled_ids VALUES ('$cid') ON CONFLICT DO NOTHING;" >/dev/null 2>&1
  i=$((i+1))
  if [ $((i % 500)) -eq 0 ]; then
    echo "  Inserted $i"
  fi
done < /tmp/enrolled_ghl_ids.txt
echo "  Inserted $i total"

echo ""
echo "=== Matching count ==="
$PG "SELECT COUNT(*) FILTER (WHERE e.ghl_contact_id IN (SELECT ghl_contact_id FROM enrolled_ids)) AS matched, COUNT(*) FILTER (WHERE e.ghl_contact_id NOT IN (SELECT ghl_contact_id FROM enrolled_ids)) AS unmatched FROM \\"Emerald_Campaign_Contacts\\" e WHERE COALESCE(e.release_status,'pending') <> 'released';"

echo ""
echo "=== Updating matched to released ==="
$PG "UPDATE \\"Emerald_Campaign_Contacts\\" SET release_status='released', released_at=NOW() WHERE ghl_contact_id IN (SELECT ghl_contact_id FROM enrolled_ids) AND COALESCE(release_status,'pending') <> 'released';"

echo ""
echo "=== Final state ==="
$PG "SELECT release_status, COUNT(*) FROM \\"Emerald_Campaign_Contacts\\" GROUP BY release_status ORDER BY release_status;"

echo ""
echo "=== Cleanup ==="
$PG "DROP TABLE IF EXISTS enrolled_ids;"
echo "Done"
'''

stdin, stdout, stderr = ssh.exec_command('cat > /tmp/mark_enrolled.sh && chmod +x /tmp/mark_enrolled.sh')
stdin.write(sh_script)
stdin.channel.shutdown_write()
stdout.read()

stdin, stdout, stderr = ssh.exec_command('/tmp/mark_enrolled.sh 2>&1')
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err.strip():
    print(f"STDERR: {err[:500]}")

ssh.close()
