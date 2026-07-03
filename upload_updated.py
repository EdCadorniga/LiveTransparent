import paramiko, io, os

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
sftp = ssh.open_sftp()

vol_path = '/var/lib/docker/volumes/n44wksswcocwk88ogcog8c48_n8n-data/_data'
local_brands = r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv'
local_disp = r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Dispensaries.csv'

sftp.put(local_brands, vol_path + '/GHL_Ready_Brands.csv')
sftp.put(local_disp, vol_path + '/GHL_Ready_Dispensaries.csv')
print(f'Uploaded Brands ({os.path.getsize(local_brands)/1024:.0f} KB)')
print(f'Uploaded Dispensaries ({os.path.getsize(local_disp)/1024:.0f} KB)')

_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'cp /home/node/.n8n/GHL_Ready_*.csv /home/node/.n8n-files/' && echo COPIED")
print(stdout.read().decode().strip())

# Verify tags and enrichment columns
_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'head -3 /home/node/.n8n-files/GHL_Ready_Brands.csv | cut -d, -f1-9'")
print('Brands headers + 1st row:')
print(stdout.read().decode().strip()[:500])

_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'tail -1 /home/node/.n8n-files/GHL_Ready_Brands.csv | cut -d, -f9,10'")
print('Tags column sample:', stdout.read().decode().strip()[:100])

sftp.close()
ssh.close()
