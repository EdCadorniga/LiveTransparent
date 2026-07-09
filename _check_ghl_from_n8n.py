import paramiko, json

key = paramiko.Ed25519Key.from_private_key_file('C:\\Users\\edmon\\.ssh\\local-upload')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=15)

checker = '''#!/usr/bin/env python3
import json, subprocess

def ghl_get(path):
    cmd = [
        "docker", "exec", "n8n-n44wksswcocwk88ogcog8c48",
        "wget", "-q", "-O-", "--timeout=15",
        "--header=Authorization: Bearer pit-b278b3ad-96bd-41fb-ba03-9f927039eb28",
        "--header=Version: 2021-07-28",
        "--header=Content-Type: application/json",
        "https://services.leadconnectorhq.com" + path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if result.stdout:
        return json.loads(result.stdout)
    return None

# Try various sequence/workflow endpoints
paths = [
    "/workflows/?locationId=Zwz4relUXVPxx8uohnjV",
    "/workflows/sequence/?locationId=Zwz4relUXVPxx8uohnjV",
    "/sequences/?locationId=Zwz4relUXVPxx8uohnjV",
    "/workflows/sequences/?locationId=Zwz4relUXVPxx8uohnjV",
    "/campaigns/?locationId=Zwz4relUXVPxx8uohnjV",
]

for p in paths:
    result = ghl_get(p)
    if result:
        print(f"{p}: {json.dumps(result)[:300]}")
    else:
        print(f"{p}: no response")

# Try the search API with a filter for pending contacts
# Use it to fetch candidates in bulk instead of per-contact GET
print()
print("=== Search for pending contacts with Emerald email campaign ===")
search = {
    "locationId": "Zwz4relUXVPxx8uohnjV",
    "page": 1,
    "pageLimit": 5,
    "filters": [
        {"field": "tags", "operator": "contains", "value": "emerald"},
        {"field": "tags", "operator": "not_contains", "value": "seq enrolled - emerald"}
    ]
}
cmd = [
    "docker", "exec", "n8n-n44wksswcocwk88ogcog8c48",
    "wget", "-q", "-O-", "--timeout=15",
    "--header=Authorization: Bearer pit-b278b3ad-96bd-41fb-ba03-9f927039eb28",
    "--header=Version: 2021-07-28",
    "--header=Content-Type: application/json",
    "--post-data=" + json.dumps(search),
    "https://services.leadconnectorhq.com/contacts/search"
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
if result.stdout:
    data = json.loads(result.stdout)
    print(f"Response keys: {list(data.keys())}")
    print(json.dumps(data, indent=2)[:500])
else:
    print(f"No response (err: {result.stderr[:200]})")

# Check if not_contains filter works
print()
print("=== Simple search without not_contains ===")
search2 = {
    "locationId": "Zwz4relUXVPxx8uohnjV",
    "page": 1,
    "pageLimit": 2,
    "filters": [
        {"field": "customField.5VRDKbOrLyy5aPOXcHKn", "operator": "eq", "value": "Emerald Cannabis Ads"}
    ]
}
cmd2 = [
    "docker", "exec", "n8n-n44wksswcocwk88ogcog8c48",
    "wget", "-q", "-O-", "--timeout=15",
    "--header=Authorization: Bearer pit-b278b3ad-96bd-41fb-ba03-9f927039eb28",
    "--header=Version: 2021-07-28",
    "--header=Content-Type: application/json",
    "--post-data=" + json.dumps(search2),
    "https://services.leadconnectorhq.com/contacts/search"
]
result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=20)
if result2.stdout:
    data2 = json.loads(result2.stdout)
    print(json.dumps(data2, indent=2)[:500])
else:
    print(f"No response (err: {result2.stderr[:200]})")
'''

stdin, stdout, stderr = ssh.exec_command('cat > /tmp/check_ghl_apis2.py && chmod +x /tmp/check_ghl_apis2.py')
stdin.write(checker)
stdin.channel.shutdown_write()
stdout.read()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/check_ghl_apis2.py 2>&1')
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err.strip():
    print(f"STDERR: {err[:500]}")

ssh.close()
