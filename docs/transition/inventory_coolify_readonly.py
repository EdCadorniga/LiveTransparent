"""Read sanitized Docker/Coolify host metadata over SSH; never reads env values."""

from __future__ import annotations

import pathlib
import json

import paramiko


HOST = "89.117.21.29"
USER = "root"
KEY = pathlib.Path.home() / ".ssh" / "local-upload"


def main() -> None:
    if not KEY.exists():
        raise SystemExit(f"SSH key not found at expected path: {KEY}")
    key = paramiko.Ed25519Key.from_private_key_file(str(KEY))
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(HOST, username=USER, pkey=key, timeout=15, banner_timeout=15)
        commands = {
            "docker_version": "docker version --format '{{.Server.Version}}'",
            "compose_projects": "docker compose ls --all --format json",
            "containers": "docker ps -a --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'",
            "networks": "docker network ls --format '{{.Name}}|{{.Driver}}|{{.Scope}}'",
            "volumes": "docker volume ls --format '{{.Name}}|{{.Driver}}'",
        }
        results = {}
        for name, command in commands.items():
            _stdin, stdout, stderr = client.exec_command(command, timeout=30)
            output = stdout.read().decode("utf-8", errors="replace").strip()
            error = stderr.read().decode("utf-8", errors="replace").strip()
            status = stdout.channel.recv_exit_status()
            results[name] = {"exit": status, "output": output, "error": error[:500]}
    finally:
        client.close()
    (pathlib.Path(__file__).resolve().parent /
     "coolify-host-inventory-2026-11-04.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    lines = [
        "# Coolify Host Inventory — 2026-11-04", "",
        "**Source:** read-only SSH queries to the Coolify VPS; commands list Docker metadata only.",
        "**Boundary:** no container environment, service secrets, Compose contents, or application data were read.",
        "**Docker server version:** " + results["docker_version"]["output"], "",
        "## Compose projects", "",
        "| Project | Status | Compose file(s) |", "|---|---|---|",
    ]
    projects = json.loads(results["compose_projects"]["output"] or "[]")
    for project in projects:
        lines.append("| " + " | ".join(str(project.get(key, "")) for key in
                                          ("Name", "Status", "ConfigFiles")) + " |")
    lines += ["", "## Containers", "", "| Name | Image | Status | Ports |",
              "|---|---|---|---|"]
    for row in results["containers"]["output"].splitlines():
        fields = row.split("|", 3)
        if len(fields) == 4:
            lines.append("| " + " | ".join(field.replace("|", "\\|") for field in fields) + " |")
    lines += ["", "## Networks", "", "| Name | Driver | Scope |", "|---|---|---|"]
    for row in results["networks"]["output"].splitlines():
        fields = row.split("|", 2)
        if len(fields) == 3:
            lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "## Volumes", "", "| Name | Driver |", "|---|---|"]
    for row in results["volumes"]["output"].splitlines():
        fields = row.split("|", 1)
        if len(fields) == 2:
            lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "## Limitations", "",
              "- This Docker snapshot is not a complete Coolify project/service configuration audit.",
              "- Saved and generated Compose drift, volume-to-service ownership, domains, health-check definitions, backups, and restore procedures remain to be verified.",
              "- Exited Playwright helper containers and the review landing-page stack are listed as observed; no cleanup or lifecycle change was made.", ""]
    (pathlib.Path(__file__).resolve().parent /
     "coolify-host-inventory-2026-11-04.md").write_text("\n".join(lines), encoding="utf-8")
    print("Coolify host inventory saved under docs/transition; metadata only")
    print("compose_projects=" + str(len(projects)))
    print("containers=" + str(len(results["containers"]["output"].splitlines())))
    print("networks=" + str(len(results["networks"]["output"].splitlines())))
    print("volumes=" + str(len(results["volumes"]["output"].splitlines())))


if __name__ == "__main__":
    main()
