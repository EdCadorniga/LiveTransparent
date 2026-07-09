import paramiko, io, sys, base64

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

queries = [
    ("Find Sameer in state", "SELECT ghl_contact_id, connection_status, sequence_step, linkedin_profile_url FROM linkedin_connection_state WHERE ghl_contact_id IN (SELECT id FROM contacts WHERE first_name ILIKE '%sameer%' OR last_name ILIKE '%kanasagara%') OR linkedin_public_identifier ILIKE '%sameer%' OR payload_json->>'firstName' ILIKE '%sameer%' LIMIT 5;"),
    ("Find Alex Baker in state", "SELECT ghl_contact_id, connection_status, sequence_step, linkedin_profile_url, linkedin_public_identifier FROM linkedin_connection_state WHERE ghl_contact_id IN ('1VU2KMcSEIq1mTP3geiQ','oBgu2UcVK8SN6sTIfkxl') LIMIT 5;"),
    ("Find Sameer in contacts table", "SELECT id, first_name, last_name, email FROM contacts WHERE first_name ILIKE '%sameer%' OR last_name ILIKE '%kanasagara%' LIMIT 5;"),
]

for label, sql in queries:
    b64 = base64.b64encode(sql.encode()).decode()
    cmd = f"docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c \"echo {b64} | base64 -d | psql -U n8n -d n8n\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'=== {label} ===')
    sys.stdout.write(''.join(stdout.readlines()))
    err = ''.join(stderr.readlines())
    if err.strip():
        print(f'ERR: {err}')

ssh.close()
