import paramiko
from pathlib import Path

key = paramiko.Ed25519Key.from_private_key_file(str(Path(r'C:\Users\edmon\.ssh\local-upload')))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('89.117.21.29', username='root', pkey=key, timeout=30)

def run(cmd):
    _, o, e = client.exec_command(cmd)
    r = o.read().decode().strip()
    err = e.read().decode().strip()
    status = o.channel.recv_exit_status()
    print(f"EXIT {status}")
    if r: print(r[:2000])
    if err: print("ERR:", err[:2000])
    return status

# Find the pg-protocol messages.js file
run("docker exec -u 0 n8n-runner sh -c 'find /opt/pg-node_modules -name messages.js -path \"*pg-protocol*\" 2>/dev/null'")

# Check npm alternative: corepack or node binary
run("docker exec -u 0 n8n-runner sh -c 'ls /usr/local/lib/node_modules/npm/bin/npm-cli.js 2>/dev/null || echo no_npm_cli'")
run("docker exec -u 0 n8n-runner sh -c 'ls /usr/local/bin/corepack 2>/dev/null || echo no_corepack'")

# Check if there's a node_modules with pg in the standard path
run("docker exec -u 0 n8n-runner sh -c 'ls /usr/local/lib/node_modules/ 2>/dev/null | head -20'")

client.close()