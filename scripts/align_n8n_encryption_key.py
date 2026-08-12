import paramiko


HOST = "89.117.21.29"
KEY = r"C:\Users\edmon\.ssh\local-upload"
SERVICE_DIR = "/data/coolify/services/n44wksswcocwk88ogcog8c48"


key = paramiko.Ed25519Key.from_private_key_file(KEY)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username="root", pkey=key)

command = (
    f"cp {SERVICE_DIR}/.env {SERVICE_DIR}/.env.bak-20260812-encryption-key "
    f"&& key=$(grep '^N8N_ENCRYPTION_KEY=' {SERVICE_DIR}/.env | cut -d= -f2-) "
    f"&& sed -i \"s/^N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=$key/\" {SERVICE_DIR}/.env "
    f"&& docker rm -f n8n-n44wksswcocwk88ogcog8c48 "
    f"&& cd {SERVICE_DIR} && docker compose up -d n8n "
    f"&& docker restart n8n-runner"
)
stdin, stdout, stderr = client.exec_command(command)
print(stdout.read().decode())
print(stderr.read().decode())
client.close()
