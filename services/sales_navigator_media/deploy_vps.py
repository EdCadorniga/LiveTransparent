"""Deploy the Sales Navigator attachment media service to the LiveTransparent VPS.

Idempotent: reuses the existing remote MEDIA_SERVICE_KEY on redeploy and reuses
an existing n8n httpHeaderAuth credential of the same name, so redeploys never
rotate the shared secret. Prints only non-secret identifiers.

Usage: python services/sales_navigator_media/deploy_vps.py [--no-n8n]
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.request

import paramiko

ROOT = r"C:\1_Ed's Active Work\Projects\LiveTransparent"
SERVICE_DIR = os.path.join(ROOT, "services", "sales_navigator_media")
REMOTE_DIR = "/srv/livetransparent/sales-navigator-media"
CREDENTIAL_NAME = "LT Sales Navigator Media Service"
PUBLIC_HEALTHZ = "https://reports.livetransparent.com/sales-navigator-attachments/v1/healthz"


def load_env(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def set_local_env(path: str, key: str, value: str) -> None:
    lines: list[str] = []
    found = False
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.strip().startswith(key + "="):
                lines.append(f"{key}={value}\n")
                found = True
            else:
                lines.append(line)
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(f"{key}={value}\n")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.writelines(lines)


def connect(env: dict) -> paramiko.SSHClient:
    keypath = os.path.expandvars(os.path.expanduser(env["VPS_SSH_KEY_PATH"]))
    key = None
    for cls in (paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey):
        try:
            key = cls.from_private_key_file(keypath)
            break
        except Exception:
            continue
    if key is None:
        raise RuntimeError("VPS key could not be loaded")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=env["VPS_HOST"], username=env["VPS_USER"], pkey=key,
                   timeout=20, look_for_keys=False, allow_agent=False)
    return client


def run(client: paramiko.SSHClient, command: str, timeout: int = 300) -> tuple[int, str, str]:
    _, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def read_remote_key(sftp: paramiko.SFTPClient) -> str:
    try:
        with sftp.open(REMOTE_DIR + "/.env", "r") as handle:
            for line in handle.read().decode("utf-8", "replace").splitlines():
                if line.strip().startswith("MEDIA_SERVICE_KEY="):
                    return line.split("=", 1)[1].strip()
    except IOError:
        pass
    return ""


def n8n_credentials(env: dict) -> tuple[str, str]:
    base = (env.get("N8N_EDITOR_BASE_URL") or
            f"{env.get('N8N_PROTOCOL', 'https')}://{env['N8N_HOST']}").rstrip("/")
    request = urllib.request.Request(
        base + "/api/v1/credentials?limit=250",
        headers={"X-N8N-API-KEY": env["N8N_LT_API_KEY"], "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    for item in payload.get("data", []):
        if item.get("name") == CREDENTIAL_NAME:
            return base, item["id"]
    return base, ""


def create_credential(env: dict, media_key: str) -> tuple[str, str]:
    base, existing = n8n_credentials(env)
    if existing:
        return base, existing
    body = json.dumps({
        "name": CREDENTIAL_NAME,
        "type": "httpHeaderAuth",
        "data": {"name": "X-Bridge-Media-Key", "value": media_key},
    }).encode()
    request = urllib.request.Request(
        base + "/api/v1/credentials", data=body, method="POST",
        headers={"X-N8N-API-KEY": env["N8N_LT_API_KEY"], "Accept": "application/json",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return base, json.load(response)["id"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"credential create failed HTTP {exc.code}: {detail[:400]}") from None


def wait_health(client: paramiko.SSHClient) -> bool:
    probe = ("docker compose exec -T sales-navigator-media python -c "
             "\"import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/healthz',timeout=5).status)\"")
    for _ in range(20):
        code, out, _ = run(client, f"cd {REMOTE_DIR} && {probe}")
        if code == 0 and "200" in out:
            return True
        time.sleep(3)
    return False


def public_health() -> bool:
    context = ssl.create_default_context()
    for _ in range(15):
        try:
            with urllib.request.urlopen(PUBLIC_HEALTHZ, timeout=10, context=context) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(4)
    return False


def verify_roundtrip(media_key: str) -> dict:
    import base64
    body = json.dumps({"filename": "bridge-selftest.pdf", "content_type": "application/pdf",
                       "data": base64.b64encode(b"bridge-selftest").decode()}).encode()
    request = urllib.request.Request(
        "https://reports.livetransparent.com/sales-navigator-attachments/v1/store",
        data=body, method="POST",
        headers={"X-Bridge-Media-Key": media_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        url = json.load(response)["url"]
    with urllib.request.urlopen(url, timeout=20) as response:
        fetched = response.read()
    return {"store_roundtrip": fetched == b"bridge-selftest", "url_prefix_ok": url.startswith(
        "https://reports.livetransparent.com/sales-navigator-attachments/")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-n8n", action="store_true", help="deploy the container only")
    parser.add_argument("--verify", action="store_true", help="only verify the live store roundtrip")
    args = parser.parse_args()

    env = load_env(os.path.join(ROOT, ".env"))
    if args.verify:
        client = connect(env)
        try:
            sftp = client.open_sftp()
            key = read_remote_key(sftp)
            sftp.close()
        finally:
            client.close()
        if not key:
            raise RuntimeError("remote media key not found")
        print(json.dumps(verify_roundtrip(key)))
        return

    client = connect(env)
    try:
        run(client, f"mkdir -p {REMOTE_DIR}")
        sftp = client.open_sftp()
        media_key = read_remote_key(sftp)
        if not media_key:
            media_key = secrets.token_hex(32)
            with sftp.open(REMOTE_DIR + "/.env", "w") as handle:
                handle.write(f"MEDIA_SERVICE_KEY={media_key}\n")
            sftp.chmod(REMOTE_DIR + "/.env", 0o600)
        for name in ("server.py", "Dockerfile", "docker-compose.yml"):
            sftp.put(os.path.join(SERVICE_DIR, name), f"{REMOTE_DIR}/{name}")
        sftp.close()
        # The container runs as the unprivileged `media` user (uid 100); the bind
        # mount must be owned by it, or startup fails on /data/files.
        run(client, f"mkdir -p {REMOTE_DIR}/data && chown 100:101 {REMOTE_DIR}/data || chmod 777 {REMOTE_DIR}/data")

        code, out, err = run(client, f"cd {REMOTE_DIR} && docker compose up -d --build 2>&1")
        if code != 0:
            raise RuntimeError(f"compose up failed: {(out + err)[:800]}")

        local_ok = wait_health(client)
        if not local_ok:
            raise RuntimeError("container health did not pass on the VPS")
        print(json.dumps({"container": "up", "local_healthz": True}))

        if args.no_n8n:
            print(json.dumps({"n8n_credential": "skipped"}))
            return
        base, credential_id = create_credential(env, media_key)
        print(json.dumps({"n8n_credential_id": credential_id, "n8n_base": base}))
        set_local_env(os.path.join(ROOT, ".env"), "SN_MEDIA_CREDENTIAL_ID", credential_id)
        print(json.dumps({"public_healthz": public_health(), "env_updated": "SN_MEDIA_CREDENTIAL_ID"}))
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)[:800]}))
        sys.exit(1)
