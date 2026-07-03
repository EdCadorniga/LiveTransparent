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

# Get n8n volume mountpoint
_, stdout, _ = ssh.exec_command("docker volume inspect n44wksswcocwk88ogcog8c48_n8n-data --format '{{.Mountpoint}}'")
vol_path = stdout.read().decode().strip()
print('Volume path:', vol_path)

sftp = ssh.open_sftp()

local_brands = r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv'
local_disp = r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Dispensaries.csv'

sftp.put(local_brands, vol_path + '/GHL_Ready_Brands.csv')
print(f'Copied Brands ({os.path.getsize(local_brands) / 1024:.0f} KB)')
sftp.put(local_disp, vol_path + '/GHL_Ready_Dispensaries.csv')
print(f'Copied Dispensaries ({os.path.getsize(local_disp) / 1024:.0f} KB)')

sftp.close()

# Verify from inside container
_, stdout, _ = ssh.exec_command("docker exec n8n-n44wksswcocwk88ogcog8c48 sh -c 'ls -la /home/node/.n8n/GHL_Ready_*.csv'")
print('\nInside container:')
print(stdout.read().decode().strip())

ssh.close()
print('Done!')
