import paramiko

key = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('89.117.21.29', username='root', pkey=key, timeout=15)

    cmds = [
        'docker exec n8n-runner sh -c "ls /opt/pg-node_modules/node_modules/pg/package.json 2>/dev/null && head -5 /opt/pg-node_modules/node_modules/pg/package.json"',
        'docker exec n8n-runner sh -c "NODE_PATH=/opt/pg-node_modules/node_modules node -e \"console.log(require(\\\"pg/package.json\\\").version)\""',
    ]
    for cmd in cmds:
        print(f'$ {cmd[:100]}')
        stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out: print(out)
        if err: print(f'[err] {err}')

finally:
    client.close()