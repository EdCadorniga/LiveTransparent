"""Apply the corrected shared LinkedIn profile index SQL on n8n-lt Postgres."""
from __future__ import annotations

import base64
import io
import socket
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]
HOST = "automations.livetransparent.com"
CONTAINER = "postgres-uokgs4c04ko0s4scccg40cgg"
SQL = "BEGIN;\n" + (ROOT / "postgres" / "linkedin-contact-profile-index.sql").read_text() + "\nCOMMIT;\n"


def main() -> None:
    key = paramiko.Ed25519Key.from_private_key(
        io.StringIO((Path.home() / ".ssh" / "local-upload").read_text())
    )
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect(socket.gethostbyname(HOST), username="root", pkey=key, timeout=10, look_for_keys=False)
    try:
        encoded = base64.b64encode(SQL.encode()).decode("ascii")
        command = (
            f"docker exec {CONTAINER} sh -c "
            f"'echo {encoded} | base64 -d | psql -X -v ON_ERROR_STOP=1 -A -t -F \"|\" -U postgres -d postgres'"
        )
        _, stdout, stderr = ssh.exec_command(command, timeout=180)
        output = stdout.read().decode("utf-8", "replace").strip()
        error = stderr.read().decode("utf-8", "replace")
        status = stdout.channel.recv_exit_status()
        if status:
            raise RuntimeError(f"index repair failed: status={status}, databaseError={error[:300]!r}")
        print({"database": "n8n-lt Postgres", "lastOutput": output.splitlines()[-2:]})
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
