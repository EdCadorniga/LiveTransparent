import os

import paramiko


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_CONFIG = os.path.join(ROOT, "reports", "nginx.conf")
REMOTE_CONFIG = "/tmp/livetransparent-report-nginx.conf"

key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key)

sftp = client.open_sftp()
sftp.put(LOCAL_CONFIG, REMOTE_CONFIG)
sftp.close()

commands = [
    f"docker cp {REMOTE_CONFIG} reports-livetransparent:/etc/nginx/conf.d/default.conf",
    "docker exec reports-livetransparent nginx -t",
    "docker exec reports-livetransparent nginx -s reload",
    "docker exec reports-livetransparent sh -lc 'wget -qO- -T 20 http://n8n:5678/healthz'",
]

for command in commands:
    _, stdout, stderr = client.exec_command(command)
    print(f"$ {command}\n{stdout.read().decode().strip()}")
    error = stderr.read().decode().strip()
    if error:
        print(error)

client.close()
