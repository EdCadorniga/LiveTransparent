import paramiko

key = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('89.117.21.29', username='root', pkey=key, timeout=15)

    cmds = [
        'docker exec n8n-runner sh -c "find /usr/local -name npm 2>/dev/null; ls /usr/local/lib/node_modules/ 2>/dev/null; apk add npm 2>&1 | head -10"',
    ]
    for cmd in cmds:
        print(f'$ {cmd[:100]}')
        stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out: print(out)
        if err: print(f'[err] {err}')
        print(f'[exit] {exit_code}')

finally:
    client.close()