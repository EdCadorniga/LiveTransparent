import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

sql = "SELECT ghl_contact_id, connection_status, sequence_step, dm_sequence_started_at IS NOT NULL as dm_active FROM linkedin_connection_state WHERE ghl_contact_id IN ('1VU2KMcSEIq1mTP3geiQ','oBgu2UcVK8SN6sTIfkxl','7Cz6mHUUCUICxbEyKeDG');"
b64 = base64.b64encode(sql.encode()).decode()
cmd = "docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo " + b64 + " | base64 -d | psql -U n8n -d n8n\""
stdin, stdout, stderr = ssh.exec_command(cmd)
sys.stdout.write(''.join(stdout.readlines()))
err = ''.join(stderr.readlines())
if err.strip():
    print('ERR:', err[:200])
ssh.close()
