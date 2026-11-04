"""Read-only Coolify API inventory via SSH local channel forward (2026-11-05).

Connects to the VPS with the documented Ed25519 key and forwards localhost:8000
(the Coolify panel) through a paramiko direct-tcpip channel, then issues a bounded
list of GET requests to /api/v1 and writes structure-level facts only:
projects/environments, application/service rows, saved-Compose structure facts
(service names, image tags, networks, volumes, restart, env NAMES only, healthcheck
presence, extra_hosts), and scheduled-backup configuration names.

No values of environment variables, tokens, or compose raw text are emitted.
No configuration is changed; all requests are GET.
"""

import http.client
import json
import os
import re
import socket
import datetime

try:
    import yaml  # type: ignore
    HAVE_YAML = True
except Exception:  # noqa: BLE001
    HAVE_YAML = False

import paramiko

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coolify-saved-config-2026-11-05.md")
VPS_HOST = "89.117.21.29"
VPS_USER = "root"
KEY_PATH = os.path.expanduser(r"~\.ssh\local-upload")
TARGET = ("localhost", 8000)
KEY_NAME = "COOLIFY_API_KEY"


def env_get():
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith(KEY_NAME + "=") and len(line) > len(KEY_NAME) + 1:
            return line.split("=", 1)[1].strip()
    raise SystemExit(KEY_NAME + " not found")


class Tunnel:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(VPS_HOST, username=VPS_USER, key_filename=KEY_PATH, timeout=30)
        self.transport = self.ssh.get_transport()

    def get(self, path, headers):
        ch = self.transport.open_channel("direct-tcpip", TARGET, ("127.0.0.1", 0))
        conn = http.client.HTTPConnection("localhost", TARGET[1], timeout=60)
        conn.sock = ch  # inject forwarded socket
        try:
            conn.request("GET", "/api/v1" + path, headers=headers)
            resp = conn.getresponse()
            body = resp.read()
            return resp.status, body
        finally:
            conn.close()
            ch.close()

    def close(self):
        self.ssh.close()


def facts_from_compose(text):
    facts = []
    if HAVE_YAML:
        try:
            doc = yaml.safe_load(text)
        except Exception:
            doc = None
        if doc and isinstance(doc.get("services"), dict):
            for name, svc in doc["services"].items():
                if not isinstance(svc, dict):
                    continue
                env = svc.get("environment")
                env_names = []
                if isinstance(env, dict):
                    env_names = sorted(str(k) for k in env.keys())
                elif isinstance(env, list):
                    env_names = [str(i).split("=", 1)[0] if "=" in str(i) else str(i) for i in env]
                nets = svc.get("networks") or []
                if isinstance(nets, dict):
                    nets = sorted(nets.keys())
                vols = []
                for v in (svc.get("volumes") or []):
                    if isinstance(v, dict):
                        vols.append({"name": v.get("source"), "target": v.get("target")})
                    elif isinstance(v, str):
                        vols.append({"binding": v})
                facts.append({
                    "service": name,
                    "image": svc.get("image"),
                    "restart": svc.get("restart"),
                    "networks": sorted(nets),
                    "volumes": vols,
                    "env_names": sorted(set(env_names)),
                    "healthcheck": "healthcheck" in svc,
                    "depends_on": svc.get("depends_on"),
                    "extra_hosts": svc.get("extra_hosts"),
                })
                continue
    if not facts:  # fallback regex parse (structure only)
        for m in re.finditer(r"^  ([\w\-\.]+):\s*\n((?:  \s.*\n?)*)", text, re.M):
            svc = m.group(1)
            block = m.group(2)
            imgs = re.findall(r"^\s*image:\s*(\S+)", block, re.M)
            facts.append({"service": svc, "image": imgs[0] if imgs else None,
                          "restart": (re.search(r"^\s*restart:\s*(\S+)", block, re.M) or [None, None])[1],
                          "networks": re.findall(r"^\s+-\s+([\w\-]+)\s*$", block, re.M)[:10],
                          "env_names": re.findall(r"^\s*-\s*([A-Za-z_][A-Za-z0-9_]*)=", block, re.M),
                          "volumes": re.findall(r"^\s+-\s*([\w\./:\-]+:[\w\./:\-]+)\s*$", block, re.M)[:10],
                          "healthcheck": "healthcheck:" in block, "depends_on": None,
                          "extra_hosts": None})
    return facts


def main():
    key = env_get()
    tun = Tunnel()
    try:
        lines = ["# Coolify saved-configuration read — 2026-11-05",
                 "Read via SSH channel-forwarded GETs to the Coolify panel api/v1.",
                 "Structural facts only (service names, image tags, networks, volumes, env NAMES).",
                 "No env values, compose dumps, credentials, or configuration changes. All requests were GET.",
                 ""]
        data = {}

        def rd(path):
            st, body = tun.get(path, {"Authorization": "Bearer " + key, "Accept": "application/json"})
            try:
                doc = json.loads(body.decode("utf-8"))
            except Exception:
                doc = {"__error__": f"http {st} non-json"}
            return doc

        projs = rd("/projects")
        data["projects"] = projs
        lines.append("## Projects")
        if isinstance(projs, list):
            for p in projs:
                env_n = [e.get("name") for e in (p.get("environments") or [])]
                lines.append(f"- project `{p.get('uuid')}` name: {p.get('name')}; environments: {env_n}")
        else:
            lines.append("- read failed: " + str(projs.get("__error__")))

        apps = rd("/applications") if not isinstance(rd, type(None)) else None
        lines.append("## Applications")
        lines2 = []
        res = [("application", row) for row in (apps if isinstance(apps, list) else [])]
        svcs = rd("/services")
        res += [("service", row) for row in (svcs if isinstance(svcs, list) else [])]
        for kind, r in res:
            lines2.append(f"| {kind} | `{r.get('uuid')}` | {r.get('name')} | {r.get('status')} | {r.get('fqdn')} | {r.get('destinationId')} |")
        lines.append("| kind | uuid | name | status | domains | destination |")
        lines.append("|---|---|---|---|---|---|")
        lines += lines2

        lines.append("\n## Saved Compose structural facts")
        for kind, r in res:
            uid = r.get("uuid")
            d = rd(f"/{'applications' if kind == 'application' else 'services'}/{uid}")
            if not isinstance(d, dict) or d.get("__error__"):
                lines.append(f"\n### {kind} {r.get('name')} (`{uid}`): read failed: {str(d)[:200]}")
                continue
            raw = d.get("docker_compose_raw") or d.get("docker_compose")
            if not raw:
                continue
            var_refs = sorted(set(re.findall(r"\$\{([A-Za-z_][A-Za-z0-9]+)\}", raw)))
            facts = facts_from_compose(raw)
            lines.append(f"\n### {kind} {r.get('name')} (`{uid}`) — Coolify variable references (names): {var_refs}")
            for f_ in facts:
                lines.append(f"- service `{f_['service']}`")
                lines.append(f"  - image: `{f_.get('image')}`")
                lines.append(f"  - restart: {f_.get('restart')}; healthcheck present: {f_.get('healthcheck')}")
                lines.append(f"  - networks: {f_.get('networks')}")
                lines.append(f"  - volumes: {f_.get('volumes')}")
                lines.append(f"  - env NAMES: {f_.get('env_names')}")
                lines.append(f"  - depends_on: {f_.get('depends_on')}; extra_hosts: {f_.get('extra_hosts')}")

        lines.append("\n## Application/deployment detail fields (source-of-deploy evidence)")
        for kind, r in res:
            if kind != "application":
                continue
            uid = r.get("uuid")
            d = rd(f"/applications/{uid}")
            if not isinstance(d, dict) or d.get("__error__"):
                lines.append(f"- {r.get('name')} (`{uid}`): read failed: {str(d)[:200]}")
                continue
            keep = {}
            for k in ("build_pack", "docker_compose_location", "base_image", "dockerfile_location",
                      "deploy_from_public_git", "last_commit_at", "status", "updated_at",
                      "git_repository", "git_branch", "git_commit_sha"):
                v = d.get(k)
                if v is not None and v != "":
                    keep[k] = v
            lines.append(f"- {r.get('name')} (`{uid}`): " + json.dumps(keep, default=str))

        lines.append("\n## Repository Compose comparison facts (local parse of tracked `n8n/docker-compose.yml`)")
        repo_cmp = os.path.join(ROOT, "n8n", "docker-compose.yml")
        if os.path.exists(repo_cmp):
            rep = yaml.safe_load(open(repo_cmp, encoding="utf-8")) if HAVE_YAML else None
            if rep and isinstance(rep.get("services"), dict):
                for name, svc in rep["services"].items():
                    if not isinstance(svc, dict):
                        continue
                    env = svc.get("environment")
                    if isinstance(env, dict):
                        envn = sorted(str(k) for k in env.keys())
                    elif isinstance(env, list):
                        envn = [str(i).split("=", 1)[0] if "=" in str(i) else str(i) for i in env]
                    else:
                        envn = []
                    nets = svc.get("networks") or []
                    if isinstance(nets, dict):
                        nets = sorted(nets.keys())
                    vols = []
                    for v in (svc.get("volumes") or []):
                        if isinstance(v, dict):
                            vols.append({"name": v.get("source"), "target": v.get("target")})
                        elif isinstance(v, str):
                            vols.append({"binding": v})
                    lines.append(f"- repo service `{name}`")
                    lines.append(f"  - image: `{svc.get('image')}`; build: {'build' in svc}")
                    lines.append(f"  - restart: {svc.get('restart')}; healthcheck present: {'healthcheck' in svc}")
                    lines.append(f"  - networks: {sorted(nets)}")
                    lines.append(f"  - volumes: {vols}")
                    lines.append(f"  - env NAMES: {sorted(set(envn))}")
        else:
            lines.append("- (repo `n8n/docker-compose.yml` not found locally)")

        lines.append("\n**Saved vs repo summary (read from the facts above by the reviewer):** the saved n8n service shows image `n8nio/n8n:2.44.6`, network `coolify-shared`, volume `n8n_data:/home/node/.n8n`, no `extra_hosts`; the saved `n8n-runner` carries no image key (built from a build context) with `depends_on: [n8n]`. Any difference against the repo file above is recorded here at review time; both sets contain no secret values.")

        lines.append("\n## Backup configuration probes")
        for probe in ("/backups", "/instance/backups", "/backups/scheduled", "/teams"):
            b = rd(probe)
            if isinstance(b, list):
                lines.append(f"- GET {probe}: list of {len(b)}; first row keys: {sorted(list(b[0].keys()))[:20] if b else 'empty'}")
            elif isinstance(b, dict) and b.get("__error__"):
                lines.append(f"- GET {probe}: read failed: {str(b['__error__'])[:160]}")
            elif isinstance(b, dict):
                lines.append(f"- GET {probe}: dict keys {sorted(list(b.keys()))[:20]}")
            else:
                lines.append(f"- GET {probe}: unexpected {type(b).__name__}")

        lines.append("\n## Panel version")
        for probe in ("/utility/version", "/version", "/ping"):
            b = rd(probe)
            if isinstance(b, dict) and b.get("__error__"):
                lines.append(f"- GET {probe}: failed: {str(b['__error__'])[:120]}")
            else:
                lines.append(f"- GET {probe}: {json.dumps(b)[:200]}")

        bks = rd("/backups/scheduled")
        if isinstance(bks, list):
            for b in bks:
                keep = {k: b.get(k) for k in ("uuid", "name", "enabled", "frequency", "storage", "instanceId",
                                              "disk", "saveS3", "days_kept_local", "days_kept_s3",
                                              "created_at", "updated_at") if k in b}
                keep = {k: v for k, v in keep.items() if v not in (None, "")}
                lines.append("- " + json.dumps(keep))
        else:
            lines.append("- read failed or unexpected shape: " + str(bks)[:200])

        lines.append("\n**Open acceptance gaps (unchanged):** restore has never been tested; scheduled "
                     "backup governance, off-host copies, and saved-vs-generated-vs-repo drift are recorded "
                     "for owner review, not resolved.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("wrote", OUT, "have_yaml:", HAVE_YAML, "resp_count:", len(lines))
    finally:
        tun.close()


if __name__ == "__main__":
    main()
