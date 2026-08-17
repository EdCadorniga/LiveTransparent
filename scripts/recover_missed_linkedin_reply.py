"""Idempotently recover the malformed August 13 LinkedIn inbound event."""

from __future__ import annotations

import copy
import json
import os
import uuid

import requests
from dotenv import load_dotenv


N8N_BASE = "https://automations.livetransparent.com/api/v1"
WEBHOOK_BASE = "https://automations.livetransparent.com/webhook"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"
TEMP_WEBHOOK_NAME = "Recovery - Missed LinkedIn Reply"
TEMP_POSTGRES_NAME = "Recovery - Insert Missed LinkedIn Reply"
TEMP_PATH = "lt-recover-linkedin-reply-20260813"
MESSAGE_ID = "4pX8FcptXnSl5aADrrfm8A"
PROVIDER_ID = "ACoAAAICCKwBdZbjiMZny8kjkv6qyfs6GfKtP1Q"
SYNTHETIC_CONTACT_ID = f"linkedin:unattributed:{PROVIDER_ID}"


def request(api_key: str, path: str, method: str = "GET", payload: dict | None = None) -> dict:
    response = requests.request(
        method,
        f"{N8N_BASE}{path}",
        headers={"X-N8N-API-KEY": api_key, "Accept": "application/json", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def save(api_key: str, workflow: dict) -> dict:
    allowed_settings = {
        "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
        "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy",
    }
    return request(api_key, f"/workflows/{WORKFLOW_ID}", "PUT", {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": {key: value for key, value in workflow.get("settings", {}).items() if key in allowed_settings},
    })


def assert_published(workflow: dict) -> None:
    if workflow.get("versionId") != workflow.get("activeVersionId") or not workflow.get("active"):
        raise RuntimeError("Workflow update was not published")


load_dotenv()
api_key = os.getenv("N8N_API_KEY_LT", "").strip()
if not api_key:
    raise RuntimeError("N8N_API_KEY_LT is missing")

workflow = request(api_key, f"/workflows/{WORKFLOW_ID}")
if workflow.get("versionId") != workflow.get("activeVersionId"):
    raise RuntimeError("Refusing recovery while the workflow has an unpublished draft")
if any(node.get("name") in {TEMP_WEBHOOK_NAME, TEMP_POSTGRES_NAME} for node in workflow["nodes"]):
    raise RuntimeError("Temporary recovery nodes already exist")

postgres_template = next(node for node in workflow["nodes"] if node.get("name") == "Record Reply Events")
recovery = copy.deepcopy(workflow)
recovery_sql = f"""WITH inserted AS (
  INSERT INTO linkedin_activity_events (
    event_key,event_type,event_at,ghl_contact_id,location_id,source_key,campaign_key,channel,
    linkedin_provider_id,unipile_account_id,workflow_id,workflow_name,status,error_code,error_detail,
    payload_json,metadata_json
  ) VALUES (
    'reply_received:{SYNTHETIC_CONTACT_ID}:{MESSAGE_ID}','reply_received','2026-08-13T20:10:07.142Z'::timestamptz,
    '{SYNTHETIC_CONTACT_ID}','Zwz4relUXVPxx8uohnjV','linkedin_unattributed','linkedin_unattributed','linkedin',
    '{PROVIDER_ID}','V9eiHiDpRmCtan0YNdzsQw','7o5EBdvwAuIaWW7k',
    'LT - LinkedIn Unipile New Messages','replied',NULL,NULL,
    jsonb_build_object('chat_id','IydEpTZFUa-c3rRiOKE93Q','message_id','{MESSAGE_ID}'),
    jsonb_build_object('source','malformed_webhook_recovery')
  ) ON CONFLICT (event_key) DO NOTHING
  RETURNING event_key
)
SELECT COUNT(*)::int AS inserted FROM inserted;"""
recovery["nodes"].extend([
    {
        "id": str(uuid.uuid4()),
        "name": TEMP_WEBHOOK_NAME,
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2.1,
        "position": [240, 720],
        "parameters": {"httpMethod": "POST", "path": TEMP_PATH, "responseMode": "lastNode", "options": {}},
        "webhookId": str(uuid.uuid4()),
    },
    {
        **postgres_template,
        "id": str(uuid.uuid4()),
        "name": TEMP_POSTGRES_NAME,
        "position": [500, 720],
        "parameters": {"resource": "database", "operation": "executeQuery", "query": recovery_sql, "options": {}},
    },
])
recovery["connections"][TEMP_WEBHOOK_NAME] = {
    "main": [[{"node": TEMP_POSTGRES_NAME, "type": "main", "index": 0}]],
}

try:
    assert_published(save(api_key, recovery))
    first = requests.post(f"{WEBHOOK_BASE}/{TEMP_PATH}", json={"recovery": MESSAGE_ID}, timeout=90)
    first.raise_for_status()
    second = requests.post(f"{WEBHOOK_BASE}/{TEMP_PATH}", json={"recovery": MESSAGE_ID}, timeout=90)
    second.raise_for_status()
    print(json.dumps({"first": first.json(), "second": second.json()}))
finally:
    current = request(api_key, f"/workflows/{WORKFLOW_ID}")
    current["nodes"] = [
        node for node in current["nodes"] if node.get("name") not in {TEMP_WEBHOOK_NAME, TEMP_POSTGRES_NAME}
    ]
    current["connections"].pop(TEMP_WEBHOOK_NAME, None)
    assert_published(save(api_key, current))
    print(json.dumps({"cleanup": "published", "workflowId": WORKFLOW_ID}))
