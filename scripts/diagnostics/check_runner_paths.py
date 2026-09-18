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
    if r: print(r[:500])
    if err: print("ERR:", err[:500])
    return status

run("docker exec -u 0 n8n-runner sh -c 'which node || echo no_node'")
run("docker exec -u 0 n8n-runner sh -c 'which npm || echo no_npm'")
run("docker exec -u 0 n8n-runner sh -c 'ls /usr/local/lib/node_modules/.pnpm/pg*/node_modules/pg-protocol/dist/messages.js 2>/dev/null || echo no_pg_protocol'")
run("docker exec -u 0 n8n-runner sh -c 'ls /opt/pg-node_modules/ 2>/dev/null | head -5 || echo no_opt_pg'")
run("docker exec -u 0 n8n-runner sh -c 'node -e \"console.log(process.version)\" 2>/dev/null || echo no_node'")
client.close()