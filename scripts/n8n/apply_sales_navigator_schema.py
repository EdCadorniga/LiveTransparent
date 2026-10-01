"""Apply and verify the dedicated Sales Navigator V2 schema once via n8n."""
from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENV = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip().strip('"').strip("'")

BASE = ENV.get("N8N_EDITOR_BASE_URL") or f"{ENV.get('N8N_PROTOCOL', 'https')}://{ENV['N8N_HOST']}"
API_KEY = ENV["N8N_LT_API_KEY"]
PATH = "lt-sn-v2-schema-" + secrets.token_hex(16)
SCHEMA = (ROOT / "n8n/sales-navigator/sales_navigator_v2_schema.sql").read_text(encoding="utf-8")
QUERY = SCHEMA + "\nSELECT to_regclass('public.sales_navigator_v2_conversation_map') AS conversation_map, to_regclass('public.sales_navigator_v2_message_events') AS message_events;"


def api(path: str, method: str = "GET", data: dict | None = None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        BASE.rstrip("/") + "/api/v1" + path,
        data=body,
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Accept": "application/json", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def main() -> None:
    nodes = [
        {
            "id": "sn-schema-webhook",
            "name": "Apply V2 Schema",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [0, 0],
            "parameters": {"httpMethod": "POST", "path": PATH, "responseMode": "responseNode", "options": {}},
        },
        {
            "id": "sn-schema-postgres",
            "name": "Apply and Verify Postgres Schema",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [260, 0],
            "parameters": {"resource": "database", "operation": "executeQuery", "query": QUERY, "options": {}},
            "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
        },
        {
            "id": "sn-schema-respond",
            "name": "Return Schema Status",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.5,
            "position": [520, 0],
            "parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {"responseCode": "={{ 200 }}"}},
        },
    ]
    workflow = {
        "name": "LT - Sales Navigator V2 Schema Apply (one-time)",
        "nodes": nodes,
        "connections": {
            "Apply V2 Schema": {"main": [[{"node": "Apply and Verify Postgres Schema", "type": "main", "index": 0}]]},
            "Apply and Verify Postgres Schema": {"main": [[{"node": "Return Schema Status", "type": "main", "index": 0}]]},
        },
        "settings": {"saveDataErrorExecution": "none", "saveDataSuccessExecution": "none", "saveManualExecutions": False, "saveExecutionProgress": False},
    }
    created = api("/workflows", "POST", workflow)
    workflow_id = created["id"]
    try:
        api(f"/workflows/{workflow_id}/activate", "POST", {})
        trigger = urllib.request.Request(BASE.rstrip("/") + "/webhook/" + PATH, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(trigger, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    finally:
        api(f"/workflows/{workflow_id}/deactivate", "POST", {})
    print(json.dumps({"workflowId": workflow_id, "activeAfterRun": False, "schema": result}, indent=2))


if __name__ == "__main__":
    main()
