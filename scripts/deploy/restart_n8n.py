import paramiko, io, sys, time

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

# Restart n8n container
stdin, stdout, stderr = ssh.exec_command('docker restart n8n-n44wksswcocwk88ogcog8c48')
print('Restart output:')
sys.stdout.write(''.join(stdout.readlines()))
err = ''.join(stderr.readlines())
if err.strip():
    print('STDERR:', err)

time.sleep(5)

# Check if it's healthy
stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}} {{.Status}}" | grep n8n')
print('Status:')
sys.stdout.write(''.join(stdout.readlines()))

# Check n8n health
import urllib.request
for attempt in range(6):
    try:
        resp = urllib.request.urlopen('https://automations.livetransparent.com/healthz', timeout=10)
        print(f'Health check attempt {attempt+1}: {resp.status}')
        if resp.status == 200:
            break
    except Exception as e:
        print(f'Health check attempt {attempt+1}: {str(e)[:100]}')
    time.sleep(10)

ssh.close()
