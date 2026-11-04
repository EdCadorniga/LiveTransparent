"""Read-only Traefik route map capture for the developer transition (2026-11-05).

Connects to the VPS with the documented Ed25519 key and reads container Docker labels only
(`docker inspect --format {{json .Config.Labels}}`) for running containers — no other
metadata and no secrets are read. Emits a route map in `docs/transition/coolify-route-map-2026-11-05.md`.
No container, label, or proxy configuration was changed.
"""

import json
import os

import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coolify-route-map-2026-11-05.md")
VPS_HOST = "89.117.21.29"
VPS_USER = "root"
KEY_PATH = os.path.expanduser(r"~\.ssh\local-upload")

SCRIPT = r"""
names=$(docker ps --format '{{.Names}}')
for n in $names; do
  echo "### $n"
  docker inspect --format '{{json .Config.Labels}}' "$n" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k in sorted(d):
    if 'coolify' in k or 'traefik' in k or k.startswith('proxy') or 'fqdn' in k.lower():
        print(k + '=' + str(d[k]))
"
done
"""


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, key_filename=KEY_PATH, timeout=30)
    stdin, out, err = ssh.exec_command("bash -s", timeout=240)
    stdin.write(SCRIPT)
    stdin.channel.shutdown_write()
    txt = out.read().decode()
    _err = err.read().decode()
    ssh.close()

    blocks = []
    cur = None
    for line in txt.splitlines():
        if line.startswith("### "):
            cur = {"name": line[4:].strip(), "labels": []}
            blocks.append(cur)
        elif cur is not None and line.strip():
            cur["labels"].append(line)

    lines = ["# Coolify/Traefik route map — 2026-11-05", "",
             "Captured from running-container Docker labels only (`docker inspect … Config.Labels`),",
             "supplemented by the generated proxy dynamic directory listing recorded in the ledger",
             "note. Traefik `coolify-proxy` discovers routes via Docker labels; the dynamic directory",
             "contains only `default_redirect_503.yaml` (catch-all 503, router priority −1000) and a",
             "Caddyfile stub that imports `*.caddy` (unused when Traefik is the provider).",
             "Nothing was changed.", ""]

    def summary(b):
        host_rules = []
        ports = []
        nets = []
        extras = []
        for lab in b["labels"]:
            if ".rule=" in lab:
                host_rules.append(lab.split(".rule=", 1)[1])
            if "loadbalancer.server.port=" in lab:
                p = lab.split("loadbalancer.server.port=", 1)[1]
                if p not in ports:
                    ports.append(p)
            if "traefik.docker.network" in lab:
                nets.append(lab.split("=", 1)[1])
            if "priority" in lab or "certresolver" in lab or "gzip" in lab:
                extras.append(lab.split("=", 1)[0] if "=" in lab else lab)
        return host_rules, sorted(set(ports)), sorted(set(nets)), sorted(set(extras))[:4]

    lines += ["| container | host rule | port | network pinning | priority/cert/gzip extras |",
              "|---|---|---|---|---|"]
    for b in blocks:
        rules, ports, nets, extras = summary(b)
        lines.append(f"| `{b['name']}` | {', '.join('`'+r+'`' for r in sorted(set(rules))) or '—'} | {', '.join(ports) or '—'} | {', '.join('`'+n+'`' for n in nets) or '—'} | {', '.join(extras) or '—'} |")

    lines += ["", "### Long-form label detail (all coolify-*/traefik-* labels, non-secret)", ""]
    for b in blocks:
        lines.append(f"#### `{b['name']}`")
        for lab in b["labels"]:
            lines.append(f"- `{lab}`")

    lines += ["", "### Observations (2026-11-05)",
              "- `reports.livetransparent.com` HTTP service points at the reports container's own nginx (port 80),",
              "  which then proxies the known API/report paths onward (see `reports/nginx.conf`); the",
              "  `/sales-navigator-attachments/*` path is instead served by the",
              "  `sales-navigator-media-*` container (router priority 100 beats the reports catch-approach).",
              "- `automations.livetransparent.com` HTTP service points at n8n port 5678 with a `gzip-sse`",
              "  middleware on the HTTPS router and `traefik.docker.network=coolify-shared` pinning.",
              "- Two containers share the same host rule for the sample landing page preview",
              "  (`vkrlibgdjdi4u6iz8hokue00-200808650013` and `vkrlibgdjdi4u6iz8hokue00` on the",
              "  `vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io` host); both have `traefik.enable=true`,",
              "  so request routing between them for the http entrypoint is ambiguous — record as an",
              "  owner decision/check (preview-only impact, not a live product domain).",
              "- `sample-landing-registry` runs without any proxy route.",
              "- Internal Coolify components (`coolify`, `coolify-db`, `coolify-redis`, `coolify-proxy`,",
              "  `coolify-sentinel`, `postgres-shared`, `n8n`/`n8n-runner` UI) do not expose HTTP via",
              "  this proxy (`postgres`/redis DBs listen internally only; n8n's DB and the runner",
              "  communicate over the Docker networks documented earlier).",
              "- TLS 4.1.2/4.5.0 Coolify versions are recorded on labels; no upgrade authorized."]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "containers:", len(blocks))


if __name__ == "__main__":
    main()
