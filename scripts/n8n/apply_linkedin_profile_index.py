"""Create and seed the indexed LinkedIn profile lookup on n8n-lt's Postgres."""
from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV: dict[str, str] = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip().strip('"').strip("'")

BASE = ENV.get("N8N_EDITOR_BASE_URL") or f"{ENV.get('N8N_PROTOCOL', 'https')}://{ENV['N8N_HOST']}"
API_KEY = ENV["N8N_LT_API_KEY"]
PATH = "lt-linkedin-profile-index-" + secrets.token_hex(12)
SQL = (ROOT / "postgres/linkedin-contact-profile-index.sql").read_text(encoding="utf-8")


def api(path: str, method: str = "GET", data: dict | None = None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        BASE.rstrip("/") + "/api/v1" + path,
        data=body,
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"n8n-lt returned HTTP {exc.code}; response body withheld") from None


def main() -> None:
    nodes = [
        {"id": "linkedin-index-hook", "name": "Apply LinkedIn Profile Index", "type": "n8n-nodes-base.webhook", "typeVersion": 2.1,
         "position": [0, 0], "parameters": {"httpMethod": "POST", "path": PATH, "responseMode": "lastNode", "options": {}}},
        {"id": "linkedin-index-sql", "name": "Create and Seed Indexed Lookup", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6,
         "position": [260, 0], "parameters": {"resource": "database", "operation": "executeQuery", "query": SQL, "options": {}},
         "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}},
    ]
    workflow = {
        "name": "LT - LinkedIn Profile Index Apply (one-time)", "nodes": nodes,
        "connections": {
            "Apply LinkedIn Profile Index": {"main": [[{"node": "Create and Seed Indexed Lookup", "type": "main", "index": 0}]]},
        },
        "settings": {"saveDataErrorExecution": "none", "saveDataSuccessExecution": "none", "saveManualExecutions": False, "saveExecutionProgress": False},
    }
    created = api("/workflows", "POST", workflow)
    workflow_id = created["id"]
    try:
        api(f"/workflows/{workflow_id}/activate", "POST", {})
        trigger = urllib.request.Request(BASE.rstrip("/") + "/webhook/" + PATH, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(trigger, timeout=180) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {"emptyResponse": True}
    finally:
        api(f"/workflows/{workflow_id}/deactivate", "POST", {})
    print(json.dumps({"workflowId": workflow_id, "activeAfterRun": False, "indexSummary": result}, indent=2))


if __name__ == "__main__":
    main()
