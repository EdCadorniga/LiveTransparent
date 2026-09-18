import paramiko, io

key = paramiko.Ed25519Key.from_private_key(io.StringIO('''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqgAAAKArF/VtKxf1
bQAAAAtzc2gtZWQyNTUxOQAAACAq7uon5OV2eUuGL2PcaH8/8XHvYw49N5C0UY2dGOeZqg
AAAEA/o9sR01By1+26drEX03KrwY2sB/47/87xZsDzflmJBSru6ifk5XZ5S4YvY9xofz/x
ce9jDj03kLRRjZ0Y55mqAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----'''))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Check n8n containers
_, stdout, _ = ssh.exec_command("docker ps --filter name=n8n --format '{{.Names}}'")
containers = stdout.read().decode().strip().split()
print('n8n containers:', containers)

# Check mounts for each n8n container
for c in containers:
    cmd = f"docker inspect {c} --format '{{json .Mounts}}'"
    _, stdout, _ = ssh.exec_command(cmd)
    import json
    try:
        mounts = json.loads(stdout.read().decode().strip())
        print(f'\nMounts for {c}:')
        for m in mounts:
            print(f"  {m.get('Source')} -> {m.get('Destination')} (type: {m.get('Type')})")
    except:
        print(f'Could not parse mounts for {c}')

# Check data directories
_, stdout, _ = ssh.exec_command('ls -la /data/coolify/ 2>/dev/null || echo "NO_COOLIFY_DATA"')
print(f'\nCoolify data:\n{stdout.read().decode().strip()[:1000]}')

# Find n8n related directories
_, stdout, _ = ssh.exec_command('find /data/coolify -maxdepth 1 -type d 2>/dev/null')
print(f'\nCoolify dirs:\n{stdout.read().decode().strip()[:500]}')

# Check n8n config for file locations
_, stdout, _ = ssh.exec_command("docker exec $(docker ps -q --filter name=n8n) sh -c 'ls -la /files/ 2>/dev/null || ls -la /data/ 2>/dev/null || echo NO_DATA_DIR' 2>/dev/null")
result = stdout.read().decode().strip()[:500]
print(f'\nn8n internal dirs:\n{result}')

# Check for shared volumes
_, stdout, _ = ssh.exec_command("docker volume ls --filter name=n8n --format '{{.Name}}' 2>/dev/null")
vols = stdout.read().decode().strip()
print(f'\nn8n volumes:\n{vols}')

ssh.close()
