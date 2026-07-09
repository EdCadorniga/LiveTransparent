import paramiko, json, subprocess

# Use the Python on the VPS with requests via pip
# First check if requests is installed
key = paramiko.Ed25519Key.from_private_key_file('C:\\Users\\edmon\\.ssh\\local-upload')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

ghl_key = "pit-b278b3ad-96bd-41fb-ba03-9f927039eb28"

# Write a Python script on the VPS
script = '''
import json, urllib.request, ssl

# Create SSL context that allows the connection
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ghl_key = "pit-b278b3ad-96bd-41fb-ba03-9f927039eb28"

for cid in ["qtLFbvZjCgF5vGx9BMPJ", "M2xe3EOAMuQnxFxebEoU", "oCqFGNBVhM8Xs6cd7StB", "UuhCDZkzX114U73waEmV", "4PDGQNUWX2iqfjo9sVlR"]:
    for base_url in ["https://services.leadconnectorhq.com", "https://rest.gohighlevel.com"]:
        req = urllib.request.Request(
            f"{base_url}/v1/contacts/{cid}",
            headers={"Authorization": f"Bearer {ghl_key}", "Version": "2021-07-28", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read())
                if "contact" in data:
                    c = data["contact"]
                    print(f"\\n=== {base_url} / {cid} ===")
                    print(f"{c.get('firstName','')} {c.get('lastName','')} <{c.get('email','')}>")
                    tags = c.get("tags", [])
                    print(f"Tags ({len(tags)}): {json.dumps(tags[:20])}")
                    cf = c.get("customField", c.get("customFields", []))
                    print(f"customField count: {len(c.get('customField',[]))}")
                    for f in cf:
                        print(f"  CF: {json.dumps(f)}")
                    print(f"dnd: {c.get('dnd')}, DND: {c.get('DND')}")
                else:
                    print(f"\\n{base_url}: {json.dumps(data)[:200]}")
                break  # success, skip second URL
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if "contact" not in body:
                print(f"\\n{base_url}/{cid}: HTTP {e.code}: {body}")
        except Exception as e:
            print(f"\\n{base_url}/{cid}: {type(e).__name__}: {e}")
'''

# Write to temp file on VPS
stdin, stdout, stderr = ssh.exec_command('cat > /tmp/check_ghl.py')
stdin.write(script)
stdin.channel.shutdown_write()
stdout.read()

# Run it
stdin, stdout, stderr = ssh.exec_command('python3 /tmp/check_ghl.py')
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err.strip():
    print(f"STDERR: {err}")

ssh.close()
