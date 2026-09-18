import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Check Emerald_Campaign_Contacts in the reports database
# The reporting tables might be in a separate database
for dbname in ['n8n', 'postgres', 'reports', 'reporting']:
    sql = "SELECT table_schema FROM information_schema.tables WHERE table_name = 'emerald_campaign_contacts' LIMIT 1;"
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = "docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo " + b64 + " | base64 -d | psql -U n8n -d " + dbname + "\" 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = ''.join(stdout.readlines())
    if 'does not exist' not in out and 'authentication' not in out.lower():
        print('Found in database:', dbname)
        print(out[:200])
    else:
        print('Not in ' + dbname)

# Also check the coolify-db
for dbname in ['coolify', 'postgres']:
    sql = "SELECT table_schema FROM information_schema.tables WHERE table_name = 'emerald_campaign_contacts' LIMIT 1;"
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = "docker exec coolify-db sh -c \"echo " + b64 + " | base64 -d | psql -U coolify -d " + dbname + "\" 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = ''.join(stdout.readlines())

ssh.close()
