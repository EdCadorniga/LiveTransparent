"""Read-only transition checks. Emit only allowlisted metadata, never node parameters."""

import json
import pathlib
import re
import shlex

import paramiko
from dotenv import dotenv_values

from inventory_n8n_readonly import BASE, ROOT, get_json


def workflows():
    key = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not key or BASE != "https://automations.livetransparent.com/api/v1":
        print("n8n-lt key or expected endpoint unavailable; skipped")
        return
    prior = json.loads((pathlib.Path(__file__).parent / "n8n-workflow-inventory-2026-11-04.json").read_text(encoding="utf-8"))
    for row in prior["workflows"]:
        if not row["active"] or not re.search(r"draft|staged|temp", row["name"], re.I):
            continue
        w = get_json("/workflows/" + row["id"], key)
        triggers = []
        for n in w.get("nodes", []):
            if n.get("type", "").endswith(("webhook", "scheduleTrigger")):
                p = n.get("parameters") or {}
                triggers.append({"type": n["type"].split(".")[-1], "disabled": n.get("disabled", False),
                                 "method": p.get("httpMethod", "GET") if n["type"].endswith("webhook") else None,
                                 "path": p.get("path") if n["type"].endswith("webhook") else None})
        print(json.dumps({"id": w["id"], "name": w["name"], "active": w.get("active"),
                          "archived": w.get("isArchived"), "draft": w.get("versionId"),
                          "published": w.get("activeVersionId"), "triggers": triggers,
                          "nodeTypes": sorted(set(n.get("type", "").split(".")[-1] for n in w.get("nodes", [])))},
                         ensure_ascii=True))


def host():
    key_path = pathlib.Path.home() / ".ssh" / "local-upload"
    if not key_path.exists():
        print("SSH key unavailable; host skipped")
        return
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("89.117.21.29", username="root",
                   pkey=paramiko.Ed25519Key.from_private_key_file(str(key_path)), timeout=15)
    commands = {
        "mounts": "docker ps --format '{{.Names}}' | while read c; do docker inspect --format '{{.Name}}|{{range .Mounts}}{{.Type}}:{{.Name}}:{{.Destination}},{{end}}|{{range $k,$v := .NetworkSettings.Networks}}{{$k}},{{end}}' \"$c\"; done",
        "backup_metadata": "find /root/n8n-upgrade-backups /data/coolify/backups /data/coolify/databases -maxdepth 2 -type f -printf '%h|%f|%s|%TY-%Tm-%Td\n' 2>/dev/null | head -60",
        "compose_names": r"find /data/coolify/services /data/coolify/applications /srv/livetransparent -maxdepth 3 \( -name 'docker-compose.y*ml' -o -name 'Dockerfile' \) -printf '%p\n' 2>/dev/null | head -80",
    }
    try:
        for label, cmd in commands.items():
            _, out, _ = client.exec_command(cmd, timeout=30)
            print(label, out.read().decode("utf-8", errors="replace")[:12000])
        files = {
            "n8n": "/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml",
            "postgres": "/data/coolify/services/uokgs4c04ko0s4scccg40cgg/docker-compose.yml",
            "reports": "/data/coolify/applications/v3ud1lum1svamymuor21upog/docker-compose.yaml",
            "media": "/srv/livetransparent/sales-navigator-media/docker-compose.yml",
            "landing": "/data/coolify/applications/vkrlibgdjdi4u6iz8hokue00/docker-compose.yaml",
        }
        for label, path in files.items():
            _, out, err = client.exec_command("docker compose -f " + shlex.quote(path) + " config --format json", timeout=30)
            raw = out.read().decode("utf-8", errors="replace")
            code = out.channel.recv_exit_status()
            if code:
                print("compose", label, "unavailable (exit code)", code)
                continue
            parsed = json.loads(raw)
            for name, service in parsed.get("services", {}).items():
                env = service.get("environment", {})
                mounts = service.get("volumes", [])
                print("compose", json.dumps({"project": label, "service": name,
                      "image": service.get("image", "[build]"),
                      "buildContext": bool(service.get("build")),
                      "envNames": sorted(env if isinstance(env, dict) else
                                         [x.split("=", 1)[0] for x in env]),
                      "dependsOn": list(service.get("depends_on", {})),
                      "networks": list(service.get("networks", {})),
                      "volumes": [{"type": x.get("type"), "source": x.get("source"),
                                   "target": x.get("target")} for x in mounts if isinstance(x, dict)],
                      "healthcheck": bool(service.get("healthcheck")),
                      "restart": service.get("restart"),
                      "labelsNames": sorted(service.get("labels", {})) if isinstance(service.get("labels"), dict) else [],
                      "ports": service.get("ports", [])}, ensure_ascii=True))
    finally:
        client.close()


if __name__ == "__main__":
    workflows()
    host()
