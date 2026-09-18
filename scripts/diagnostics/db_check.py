import paramiko, io, sys

key_data = open(r'C:\Users\edmon\.ssh\local-upload').read()
key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)

stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}'")
print("=== All containers ===")
sys.stdout.write(''.join(stdout.readlines()))

stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}} {{.Image}}' | grep -iE 'postgres|n8n'")
print("=== Postgres+n8n ===")
sys.stdout.write(''.join(stdout.readlines()))

stdin, stdout, stderr = ssh.exec_command("which psql && psql --version")
print("=== Host psql ===")
sys.stdout.write(''.join(stdout.readlines()))

ssh.close()
