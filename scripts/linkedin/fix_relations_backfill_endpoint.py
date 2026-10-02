"""Fix `LT - LinkedIn Relations Backfill (Unipile)` silent no-op.

Root cause (verified live 2026-10-02): the workflow called
`GET /users/connections?account_id=...`, which returns the account's own
single profile object, not a list. `res.data.items` is always undefined, so
every daily run short-circuits with backfilled: 0 and never reconciles
requested -> connected.

The correct Unipile endpoint is `GET /users/relations` returning
`{ object: "UserRelationsList", items: [...], cursor }`. Relation items expose
the provider id as `member_id` and the URL as `public_profile_url`. Also adds
a 240s deadline so the loop cannot exceed the runner task timeout.

Publishes via REST PUT (auto-activates). No LinkedIn message is sent.
"""

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
N8N_BASE = "https://automations.livetransparent.com"
WF_ID = "VPiHfBwzOHaJnHBY"
NODE = "Backfill LinkedIn Relations"

R1_OLD = "  let url = `${unipileApiBaseUrl}/users/connections?account_id=${encodeURIComponent(unipileAccountId)}&limit=200`;"
R1_NEW = "  let url = `${unipileApiBaseUrl}/users/relations?account_id=${encodeURIComponent(unipileAccountId)}&limit=200`;"

R2_OLD = (
    "    const providerId = clean(conn.provider_id || conn.providerId);\n"
    "    const publicId = clean(conn.public_identifier || conn.publicIdentifier);\n"
    "    const profileUrl = conn.profile_url || conn.profileUrl || `https://www.linkedin.com/in/${publicId}`;"
)
R2_NEW = (
    "    const providerId = clean(conn.provider_id || conn.providerId || conn.member_id);\n"
    "    const publicId = clean(conn.public_identifier || conn.publicIdentifier);\n"
    "    const profileUrl = conn.profile_url || conn.profileUrl || conn.public_profile_url || `https://www.linkedin.com/in/${publicId}`;"
)

R3_OLD = "const maxPages = 20;\n\nfor (let page = 0; page < maxPages; page++) {\n  const { items, next } = await fetchUnipileConnections(cursor);\n  if (!items.length) break;\n  for (const conn of items) {"
R3_NEW = "const maxPages = 20;\nconst deadline = Date.now() + 240000;\n\nfor (let page = 0; page < maxPages; page++) {\n  if (Date.now() >= deadline) break;\n  const { items, next } = await fetchUnipileConnections(cursor);\n  if (!items.length) break;\n  for (const conn of items) {\n    if (Date.now() >= deadline) break;"


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api(method, path, key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(N8N_BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": key, "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode() or "{}")


def main():
    load_env()
    key = os.environ["N8N_LT_API_KEY"]
    w = api("GET", f"/api/v1/workflows/{WF_ID}", key)
    node = next(n for n in w["nodes"] if n["name"] == NODE)
    code = node["parameters"]["jsCode"]
    if "/users/relations" in code:
        print("already patched; nothing to do")
        return
    for old in (R1_OLD, R2_OLD, R3_OLD):
        if old not in code:
            raise SystemExit("expected block not found — live code drifted; aborting")
    code = code.replace(R1_OLD, R1_NEW, 1).replace(R2_OLD, R2_NEW, 1).replace(R3_OLD, R3_NEW, 1)
    node["parameters"]["jsCode"] = code
    settings = {k: v for k, v in (w.get("settings") or {}).items() if k != "availableInMCP"}
    body = {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"], "settings": settings}
    api("PUT", f"/api/v1/workflows/{WF_ID}", key, body)
    back = api("GET", f"/api/v1/workflows/{WF_ID}", key)
    live = next(n for n in back["nodes"] if n["name"] == NODE)["parameters"]["jsCode"]
    print(json.dumps({
        "versionId": back.get("versionId"),
        "activeVersionId": back.get("activeVersionId"),
        "active": back.get("active"),
        "relations_endpoint": "/users/relations" in live,
        "member_id_fallback": "conn.member_id" in live,
        "deadline": "deadline" in live,
    }, indent=2))


if __name__ == "__main__":
    main()
