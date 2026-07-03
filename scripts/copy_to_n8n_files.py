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

# Copy files to the .n8n-files directory inside container
commands = [
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'mkdir -p /home/node/.n8n-files'",
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'cp /home/node/.n8n/GHL_Ready_Brands.csv /home/node/.n8n-files/'",
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'cp /home/node/.n8n/GHL_Ready_Dispensaries.csv /home/node/.n8n-files/'",
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'ls -la /home/node/.n8n-files/GHL_Ready_*.csv'"
]
for cmd in commands:
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        print('ERR:', err)

ssh.close()
print('Done')
