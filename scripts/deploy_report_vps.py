import sys

import paramiko


HOST = "89.117.21.29"
APP_DIR = "/data/coolify/applications/v3ud1lum1svamymuor21upog"
IMAGE = "v3ud1lum1svamymuor21upog:8620a18"
SOURCE_DIR = "/tmp/livetransparent-report-8620"


def run(client, label, command):
    print(f"STEP {label}")
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if output:
        print(output, end="")
    if error:
        print(error, file=sys.stderr, end="")
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(f"{label} failed with exit code {status}")


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username="root", pkey=paramiko.Ed25519Key.from_private_key_file(
    r"C:\Users\edmon\.ssh\local-upload"
), timeout=30)

try:
    run(client, "clone", f"rm -rf {SOURCE_DIR} && git clone --depth 1 --branch main https://github.com/EdCadorniga/LiveTransparent.git {SOURCE_DIR}")
    run(client, "build", f"docker build -t {IMAGE} {SOURCE_DIR}/reports")
    run(client, "backup-compose", f"cp {APP_DIR}/docker-compose.yaml {APP_DIR}/docker-compose.yaml.pre-8620a18")
    run(client, "select-image", f"sed -E -i \"s#^        image: .*#        image: '{IMAGE}'#\" {APP_DIR}/docker-compose.yaml")
    run(client, "recreate", f"docker compose -f {APP_DIR}/docker-compose.yaml up -d --force-recreate")
    run(client, "verify", "docker ps --filter name=reports-livetransparent --format '{{.ID}}\\t{{.Image}}\\t{{.Status}}'")
finally:
    client.close()
