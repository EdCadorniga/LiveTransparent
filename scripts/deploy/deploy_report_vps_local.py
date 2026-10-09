import os
import posixpath
import time

import paramiko


HOST = "89.117.21.29"
APP_DIR = "/data/coolify/applications/v3ud1lum1svamymuor21upog"
SOURCE_DIR = "/tmp/livetransparent-report-local"
IMAGE = "v3ud1lum1svamymuor21upog:executive-v1-20261009-sql-booking-attribution"
BUILD_STAMP = "2026-10-09-v1-sql-booking-attribution"
LOCAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))


def run(client, label, command):
    print(f"STEP {label}")
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if output:
        print(output, end="")
    if error:
        print(error, end="")
    status = stdout.channel.recv_exit_status()
    if status:
        raise RuntimeError(f"{label} failed with exit code {status}")


def upload_tree(sftp, local_root, remote_root):
    for root, dirs, files in os.walk(local_root):
        relative = os.path.relpath(root, local_root).replace(os.sep, "/")
        remote_dir = remote_root if relative == "." else posixpath.join(remote_root, relative)
        try:
            sftp.mkdir(remote_dir)
        except IOError:
            pass
        for filename in files:
            local_path = os.path.join(root, filename)
            remote_path = posixpath.join(remote_dir, filename)
            sftp.put(local_path, remote_path)


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username="root", pkey=paramiko.Ed25519Key.from_private_key_file(
    r"C:\Users\edmon\.ssh\local-upload"
), timeout=30)

try:
    run(client, "prepare", f"rm -rf {SOURCE_DIR} && mkdir -p {SOURCE_DIR}")
    sftp = client.open_sftp()
    upload_tree(sftp, LOCAL_DIR, SOURCE_DIR)
    sftp.close()
    run(client, "build", f"docker build -t {IMAGE} {SOURCE_DIR}")
    run(client, "verify-nginx-config", f"docker run --rm --network coolify-shared {IMAGE} nginx -t")
    run(client, "backup-compose", f"cp {APP_DIR}/docker-compose.yaml {APP_DIR}/docker-compose.yaml.pre-campaign-accuracy")
    run(client, "select-image", f"sed -E -i \"s#^        image: .*#        image: '{IMAGE}'#\" {APP_DIR}/docker-compose.yaml")
    run(client, "recreate", f"docker compose -f {APP_DIR}/docker-compose.yaml up -d --force-recreate")
    run(client, "attach-shared-network", "docker network connect coolify-shared reports-livetransparent 2>/dev/null || true")
    run(client, "restart-after-network", "docker restart reports-livetransparent")
    time.sleep(5)
    run(client, "verify-container", "docker ps --filter name=reports-livetransparent --format '{{.ID}}\t{{.Image}}\t{{.Status}}'")
    run(client, "verify-v1-build", f"curl -fsS https://reports.livetransparent.com/embed/executive-v1/index.html | grep -o '{BUILD_STAMP}'")
    run(client, "verify-legacy-report", "curl -fsS https://reports.livetransparent.com/embed/executive/index.html | grep -o '2026-08-17-v27-social-mql'")
finally:
    client.close()
