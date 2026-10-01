"""Read only: summarize n8n-lt container errors without printing payloads."""
from __future__ import annotations

import io
import re
import socket
from pathlib import Path

import paramiko

key = paramiko.Ed25519Key.from_private_key(
    io.StringIO((Path.home() / ".ssh" / "local-upload").read_text())
)
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
ssh.connect(
    socket.gethostbyname("automations.livetransparent.com"),
    username="root",
    pkey=key,
    timeout=10,
    look_for_keys=False,
)
try:
    _, stdout, _ = ssh.exec_command("docker ps --format '{{.Names}} {{.Image}}'", timeout=15)
    containers = []
    for line in stdout.read().decode().splitlines():
        name, _, image = line.partition(" ")
        if "n8n" in name.lower() or "n8n" in image.lower():
            containers.append(name)
    results = []
    for name in containers:
        command = (
            f"docker logs --since 2026-10-01T12:13:00Z "
            f"--until 2026-10-01T12:16:30Z {name}"
        )
        _, out, err = ssh.exec_command(command, timeout=20)
        lines = (out.read() + err.read()).decode("utf-8", "replace").splitlines()
        relevant = []
        safe_errors = []
        for line in lines:
            lower = line.lower()
            if not any(word in lower for word in ("error", "failed", "workflow", "unipile")):
                continue
            # Keep only known error categories; logs may contain message bodies.
            categories = [
                word for word in (
                    "401", "403", "404", "422", "429", "500", "502", "503",
                    "timeout", "credential", "unauthorized", "forbidden",
                    "error", "failed", "workflow", "unipile",
                )
                if word in lower
            ]
            if categories:
                relevant.append(sorted(set(categories)))
            if any(word in lower for word in ("credential", "401")) and not any(
                word in lower for word in ("body", "payload", "header", "text")
            ):
                cleaned = re.sub(r"[A-Za-z0-9_+/=-]{16,}", "[redacted]", line)
                safe_errors.append(cleaned[:200])
        results.append({"container": name, "logLineCount": len(lines), "errorCategoryLines": relevant[:30], "safeErrorLines": safe_errors[:8]})
    print(results)
finally:
    ssh.close()
