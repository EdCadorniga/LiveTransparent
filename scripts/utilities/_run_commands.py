import paramiko
import time

key = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

NPM = '/usr/local/lib/node_modules/corepack/shims/npm'

try:
    client.connect('89.117.21.29', username='root', pkey=key, timeout=15)
    print('[SSH] Connected successfully')

    commands = [
        (1, f'docker exec n8n-runner {NPM} install pg@8.13.0 --prefix /opt/pg-node_modules'),
        (2, 'docker restart n8n-runner'),
        (3, 'sleep 3'),
        (4, 'docker logs n8n-runner --tail 5'),
    ]

    for num, cmd in commands:
        label = cmd[:90] + '...' if len(cmd) > 90 else cmd
        print(f'\n=== Command {num}: {label}')
        stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out: print(out)
        if err: print(err)
        if exit_code != 0:
            print(f'[exit code] {exit_code}')

    # Verify the new pg version
    print('\n=== Verifying installed pg version ===')
    stdin, stdout, stderr = client.exec_command(
        'docker exec n8n-runner sh -c \'cat /opt/pg-node_modules/pg/package.json | grep version | head -1\'',
        timeout=10
    )
    out = stdout.read().decode('utf-8', errors='replace').strip()
    print(out)

    print('\n=== All commands completed ===')

except Exception as e:
    print(f'[ERROR] {e}')
finally:
    client.close()