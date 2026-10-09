"""Route Apollo flag webhooks to a paced scheduled worker on n8n-lt.

Default mode is dry-run. Pass --apply to update/publish the live n8n-lt
workflow. Webhook calls become acknowledgements; the schedule worker scans the
GHL Enrich Phone via Apollo flag and processes at most five contacts per run.
"""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import requests
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
BASE_URL = "https://automations.livetransparent.com"
WORKFLOW_ID = "JH8ShfpglWmLMZ3l"
EXPECTED_VERSION = "d3ddd510-1157-42a5-b640-44c058fc7c5b"
WORKER_NODE = "Enrich Contacts via Apollo"
CONFIG_NODE = "Config"
WEBHOOK_NODE = "Webhook"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"

ACK = '''const isWebhookRun = !!(cfg && cfg.webhookUrl);
if (isWebhookRun) {
  return [{ json: {
    ok: true,
    mode: "webhook_queued_for_scheduled_worker",
    processed: 0,
    note: "The scheduled worker processes Enrich Phone via Apollo flags in capped batches."
  } }];
}'''


def load_key() -> str:
    key = dotenv_values(ENV_FILE).get("N8N_LT_API_KEY")
    if not key:
        raise RuntimeError("N8N_LT_API_KEY is unavailable in repository .env")
    return str(key)


def get_workflow(session: requests.Session) -> dict:
    response = session.get(f"{BASE_URL}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    response.raise_for_status()
    return response.json()


def prepare(workflow: dict) -> dict:
    if workflow.get("id") != WORKFLOW_ID:
        raise RuntimeError("Workflow ID did not match the intended n8n-lt Apollo poller")
    if workflow.get("versionId") != EXPECTED_VERSION or workflow.get("activeVersionId") != EXPECTED_VERSION:
        raise RuntimeError("Live Apollo workflow version drifted; inspect before applying this patch")
    if not workflow.get("active") or workflow.get("isArchived"):
        raise RuntimeError("Apollo workflow is not active/non-archived; refusing to patch")

    nodes = [dict(node) for node in workflow.get("nodes", [])]
    names = {node.get("name") for node in nodes}
    if SCHEDULE_NAME in names or any(node.get("type") == "n8n-nodes-base.scheduleTrigger" for node in nodes):
        raise RuntimeError("A schedule trigger already exists; inspect the live graph before proceeding")
    if names != {CONFIG_NODE, WORKER_NODE, WEBHOOK_NODE}:
        raise RuntimeError(f"Unexpected live graph node names: {sorted(str(n) for n in names)}")

    worker = next(node for node in nodes if node.get("name") == WORKER_NODE)
    code = worker.get("parameters", {}).get("jsCode", "")
    if code.count('const isWebhookRun = !!(cfg && cfg.webhookUrl);') != 1:
        raise RuntimeError("Webhook/schedule branch marker changed; inspect live code before patching")
    if "maxPerRun" not in code or 'Number(cfg.maxPerRun || 30)' not in code:
        raise RuntimeError("Expected batch-cap logic was not found; inspect before patching")
    worker["parameters"]["jsCode"] = code.replace(
        'const isWebhookRun = !!(cfg && cfg.webhookUrl);', ACK, 1
    )

    schedule_node = {
        "parameters": {
            "rule": {"interval": [{"field": "minutes", "minutesInterval": 30}]}
        },
        "id": str(uuid.uuid4()),
        "name": SCHEDULE_NAME,
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [0, -120],
    }
    nodes.append(schedule_node)

    connections = json.loads(json.dumps(workflow.get("connections", {})))
    connections[SCHEDULE_NAME] = {
        "main": [[{"node": CONFIG_NODE, "type": "main", "index": 0}]]
    }

    allowed_settings = {
        "executionOrder",
        "timezone",
        "saveDataErrorExecution",
        "saveDataSuccessExecution",
        "saveManualExecutions",
        "saveExecutionProgress",
        "executionTimeout",
        "callerPolicy",
    }
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in allowed_settings}

    return {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": connections,
        "settings": settings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply and publish this live n8n-lt workflow change")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({"X-N8N-API-KEY": load_key(), "Content-Type": "application/json"})
    health = session.get(f"{BASE_URL}/healthz/readiness", timeout=20)
    if health.status_code != 200:
        raise RuntimeError(f"n8n-lt readiness check failed: HTTP {health.status_code}")

    before = get_workflow(session)
    payload = prepare(before)
    report = {
        "workflowId": WORKFLOW_ID,
        "name": before.get("name"),
        "beforeVersionId": before.get("versionId"),
        "beforeActiveVersionId": before.get("activeVersionId"),
        "beforeNodeCount": len(before.get("nodes", [])),
        "afterNodeCount": len(payload["nodes"]),
        "batchCap": 5,
        "scheduleEveryMinutes": 30,
        "webhookBehavior": "acknowledge only; no contact lookup or Apollo calls",
        "writeRequested": bool(args.apply),
    }
    if not args.apply:
        print(json.dumps(report, indent=2))
        return 0

    response = session.put(f"{BASE_URL}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"n8n-lt update failed: HTTP {response.status_code}")

    after = get_workflow(session)
    after_nodes = after.get("nodes", [])
    worker = next((node for node in after_nodes if node.get("name") == WORKER_NODE), {})
    worker_code = (worker.get("parameters") or {}).get("jsCode", "")
    active_schedule = any(
        node.get("name") == SCHEDULE_NAME
        and node.get("type") == "n8n-nodes-base.scheduleTrigger"
        and node.get("parameters", {}).get("rule", {}).get("interval", [{}])[0].get("minutesInterval") == 30
        for node in after_nodes
    )
    if not after.get("active") or after.get("isArchived") or after.get("versionId") != after.get("activeVersionId"):
        raise RuntimeError("Update returned, but active/published state did not verify")
    if not active_schedule or "webhook_queued_for_scheduled_worker" not in worker_code:
        raise RuntimeError("Update returned, but paced-worker behavior did not verify")

    report.update({
        "afterVersionId": after.get("versionId"),
        "afterActiveVersionId": after.get("activeVersionId"),
        "afterActive": after.get("active"),
        "afterArchived": after.get("isArchived"),
        "afterNodeCount": len(after_nodes),
        "verifiedSchedule": active_schedule,
        "verifiedWebhookAckOnly": True,
    })
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
