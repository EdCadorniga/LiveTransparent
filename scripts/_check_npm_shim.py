import paramiko

key = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('89.117.21.29', username='root', pkey=key, timeout=15)

    # Try installing pg via npm using corepack shim or direct path
    cmds = [
        'docker exec n8n-runner sh -c "/usr/local/lib/node_modules/corepack/shims/npm --version 2>&1 || echo npm-shim-failed"',
        'docker exec n8n-runner sh -c "cd /opt/pg-node_modules && ls package.json 2>/dev/null || echo no-pkg"',
        'docker exec n8n-runner sh -c "cat /opt/pg-node_modules/pg/package.json | head -3"',
    ]
    for cmd in cmds:
        print(f'$ {cmd[:100]}')
        stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out: print(out)
        if err: print(f'[err] {err}')
        print()

finally:
    client.close()