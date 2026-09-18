import paramiko, time
from pathlib import Path

key = paramiko.Ed25519Key.from_private_key_file(str(Path(r'C:\Users\edmon\.ssh\local-upload')))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('89.117.21.29', username='root', pkey=key, timeout=30)

def run(cmd):
    _, o, e = client.exec_command(cmd)
    r = o.read().decode()
    err = e.read().decode()
    status = o.channel.recv_exit_status()
    result = r + err
    print(f"EXIT {status}: {result[:500]}")
    return status

run('docker exec -u 0 n8n-runner sh -c "npm install pg@8.13.0 --prefix /opt/pg-node_modules 2>&1"')
time.sleep(2)
run('docker restart n8n-runner')
time.sleep(5)
run('docker logs n8n-runner --tail 5')
client.close()