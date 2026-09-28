"""Replace the LinkedIn OAuth retry worker's Code node with native n8n nodes."""
from __future__ import annotations

import json
import os
import uuid
import urllib.request
from pathlib import Path

BASE = "https://automations.livetransparent.com/api/v1"
WORKFLOW_ID = "4Qww6KyTxnoRAs9m"


def load_env():
    values = {}
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


cfg = load_env()
api_key = os.environ.get("N8N_API_KEY_LT") or cfg.get("N8N_API_KEY_LT")
if not api_key:
    raise RuntimeError("N8N_API_KEY_LT is required")


def api(path, method="GET", payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method=method,
        headers={"X-N8N-API-KEY": api_key, "Accept": "application/json", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


def node_id():
    return str(uuid.uuid4())


def set_node(name, position, assignments):
    return {
        "parameters": {
            "assignments": {"assignments": [{"id": node_id(), "name": k, "value": v, "type": "string"} for k, v in assignments.items()]},
            "includeOtherFields": True,
            "options": {},
        },
        "id": node_id(), "name": name, "type": "n8n-nodes-base.set", "typeVersion": 3.4, "position": position,
    }


schedule = {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "10 */6 * * *"}]}}, "id": node_id(), "name": "Every 6 Hours + 10 Minutes", "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.3, "position": [0, 0]}
fetch = {"parameters": {"operation": "executeQuery", "query": """CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue (
  id BIGSERIAL PRIMARY KEY,
  message_id TEXT NOT NULL UNIQUE,
  ghl_contact_id TEXT NOT NULL,
  linkedin_chat_id TEXT NOT NULL,
  linkedin_provider_id TEXT,
  unipile_account_id TEXT,
  message_text TEXT NOT NULL,
  message_timestamp TIMESTAMPTZ,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT, next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_attempt_at TIMESTAMPTZ, completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
WITH claimed AS (
  UPDATE linkedin_inbound_retry_queue
  SET status='processing', attempts=attempts+1, last_attempt_at=NOW(), updated_at=NOW()
  WHERE id IN (
    SELECT id FROM linkedin_inbound_retry_queue
    WHERE status='pending' AND next_attempt_at <= NOW() AND attempts < 5
    ORDER BY created_at LIMIT 50 FOR UPDATE SKIP LOCKED
  )
  RETURNING *
)
SELECT c.*, t.access_token AS agency_access_token
FROM claimed c
LEFT JOIN LATERAL (
  SELECT access_token FROM ghl_oauth_tokens WHERE active IS TRUE AND access_token <> ''
  ORDER BY updated_at DESC NULLS LAST LIMIT 1
) t ON TRUE;""", "options": {"queryBatching": "independently"}}, "id": node_id(), "name": "Claim Pending LinkedIn OAuth Retries", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [220, 0], "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}}
exchange = {"parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/oauth/locationToken", "sendHeaders": True, "headerParameters": {"parameters": [
    {"name": "Authorization", "value": "=Bearer {{$json.agency_access_token}}"}, {"name": "Version", "value": "2021-07-28"}, {"name": "Accept", "value": "application/json"}, {"name": "Content-Type", "value": "application/json"}
]}, "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { companyId: '7vMmm4at5OrjQplRN3EO', locationId: 'Zwz4relUXVPxx8uohnjV' } }}", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}}, "id": node_id(), "name": "Exchange Retry OAuth Location Token", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [460, 0]}
context = set_node("Set Retry Context", [680, 0], {
    "id": "={{ $('Claim Pending LinkedIn OAuth Retries').item.json.id }}",
    "ghl_contact_id": "={{ $('Claim Pending LinkedIn OAuth Retries').item.json.ghl_contact_id }}",
    "linkedin_chat_id": "={{ $('Claim Pending LinkedIn OAuth Retries').item.json.linkedin_chat_id }}",
    "message_text": "={{ $('Claim Pending LinkedIn OAuth Retries').item.json.message_text }}",
    "message_timestamp": "={{ $('Claim Pending LinkedIn OAuth Retries').item.json.message_timestamp }}",
    "retry_location_token": "={{ $json.body?.access_token || $json.access_token || '' }}",
    "retry_exchange_status": "={{ $json.statusCode || $json.status || 0 }}",
    "retry_exchange_error": "={{ $json.body?.message || $json.message || '' }}",
})
gate = {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": node_id(), "leftValue": "={{ $json.retry_location_token }}", "rightValue": "", "operator": {"type": "string", "operation": "notEmpty"}}], "combinator": "and"}}, "id": node_id(), "name": "Retry OAuth Token Available?", "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [900, 0]}
post = {"parameters": {"method": "POST", "url": "https://services.leadconnectorhq.com/conversations/messages/inbound", "sendHeaders": True, "headerParameters": {"parameters": [
    {"name": "Authorization", "value": "=Bearer {{$json.retry_location_token}}"}, {"name": "Version", "value": "2021-07-28"}, {"name": "Accept", "value": "application/json"}, {"name": "Content-Type", "value": "application/json"}
]}, "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ { type: 'Custom', contactId: $json.ghl_contact_id, message: $json.message_text, conversationProviderId: '6a58a14ff3023bea3783c152', altId: $json.linkedin_chat_id, date: $json.message_timestamp || new Date().toISOString() } }}", "options": {"response": {"response": {"neverError": True, "responseFormat": "json", "fullResponse": True}}}}, "id": node_id(), "name": "Post Retried LinkedIn Inbound", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [1140, -100]}
success = set_node("Mark Retry Result", [1360, -100], {
    "id": "={{ $('Set Retry Context').item.json.id }}",
    "retry_status": "={{ Number($json.statusCode || $json.status || 0) >= 200 && Number($json.statusCode || $json.status || 0) < 300 ? 'completed' : 'retry' }}",
    "retry_error": "={{ Number($json.statusCode || $json.status || 0) >= 200 && Number($json.statusCode || $json.status || 0) < 300 ? '' : ('GHL inbound retry HTTP ' + ($json.statusCode || $json.status || 0)) }}",
})
failure = set_node("Mark OAuth Retry Pending", [1140, 120], {
    "id": "={{ $('Set Retry Context').item.json.id }}",
    "retry_status": "retry",
    "retry_error": "={{ 'OAuth location token exchange failed: ' + ($('Set Retry Context').item.json.retry_exchange_error || $('Set Retry Context').item.json.retry_exchange_status || 'unknown') }}",
})
finalize = {"parameters": {"operation": "executeQuery", "query": """UPDATE linkedin_inbound_retry_queue
SET status = CASE WHEN $2 = 'completed' THEN 'completed' WHEN attempts >= 5 THEN 'failed' ELSE 'pending' END,
    last_error = NULLIF($3, ''),
    next_attempt_at = CASE WHEN $2 = 'completed' OR attempts >= 5 THEN next_attempt_at ELSE NOW() + INTERVAL '10 minutes' END,
    completed_at = CASE WHEN $2 = 'completed' THEN NOW() ELSE completed_at END,
    updated_at = NOW()
WHERE id = $1;""", "options": {"queryBatching": "independently", "queryReplacement": "={{ [ $json.id, $json.retry_status || 'retry', $json.retry_error || '' ] }}"}}, "id": node_id(), "name": "Finalize LinkedIn OAuth Retry", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [1600, 0], "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}}

nodes = [schedule, fetch, exchange, context, gate, post, success, failure, finalize]
connections = {
    schedule["name"]: {"main": [[{"node": fetch["name"], "type": "main", "index": 0}]]},
    fetch["name"]: {"main": [[{"node": exchange["name"], "type": "main", "index": 0}]]},
    exchange["name"]: {"main": [[{"node": context["name"], "type": "main", "index": 0}]]},
    context["name"]: {"main": [[{"node": gate["name"], "type": "main", "index": 0}]]},
    gate["name"]: {"main": [[{"node": post["name"], "type": "main", "index": 0}], [{"node": failure["name"], "type": "main", "index": 0}]]},
    post["name"]: {"main": [[{"node": success["name"], "type": "main", "index": 0}]]},
    success["name"]: {"main": [[{"node": finalize["name"], "type": "main", "index": 0}]]},
    failure["name"]: {"main": [[{"node": finalize["name"], "type": "main", "index": 0}]]},
}
workflow = api(f"/workflows/{WORKFLOW_ID}")
settings = {k: v for k, v in (workflow.get("settings") or {}).items() if k in {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}}
updated = api(f"/workflows/{WORKFLOW_ID}", "PUT", {"name": workflow["name"], "nodes": nodes, "connections": connections, "settings": settings})
api(f"/workflows/{WORKFLOW_ID}/activate", "POST", {})
checked = api(f"/workflows/{WORKFLOW_ID}")
print(json.dumps({"workflow": WORKFLOW_ID, "active": checked.get("active"), "versionId": checked.get("versionId"), "activeVersionId": checked.get("activeVersionId"), "published": checked.get("versionId") == checked.get("activeVersionId"), "codeNodes": [n["name"] for n in checked.get("nodes", []) if n.get("type") == "n8n-nodes-base.code"]}, indent=2))
