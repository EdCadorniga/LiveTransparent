"""Add an idempotent retry queue for LinkedIn inbound messages blocked by GHL OAuth 401s."""
from __future__ import annotations

import json
import os
import urllib.request
import uuid
from pathlib import Path

BASE = "https://automations.livetransparent.com/api/v1"
INBOUND_ID = "7o5EBdvwAuIaWW7k"
RETRY_NAME = "LT - LinkedIn Inbound OAuth Retry"

def load_env():
    values = {}
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
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

def allowed_settings(settings):
    names = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}
    return {k: v for k, v in (settings or {}).items() if k in names}

def publish(workflow):
    return api(f"/workflows/{workflow['id']}", "PUT", {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": allowed_settings(workflow.get("settings")),
    })

# 1. Persist OAuth-401 inbound failures in the existing map-upsert SQL node.
inbound = api(f"/workflows/{INBOUND_ID}")
target = next(n for n in inbound["nodes"] if n.get("name") == "Build Upsert Map SQL")
code = target["parameters"]["jsCode"]
if "linkedin_inbound_retry_queue" not in code:
    code = code.replace(
        "const rawPayload = esc(JSON.stringify(row || {}));\n\nconst sql = `",
        """const rawPayload = esc(JSON.stringify(row || {}));
const errorReason = esc(row.reason || '');

const retrySql = `CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue (
  id BIGSERIAL PRIMARY KEY,
  message_id TEXT NOT NULL UNIQUE,
  ghl_contact_id TEXT NOT NULL,
  linkedin_chat_id TEXT NOT NULL,
  linkedin_provider_id TEXT,
  unipile_account_id TEXT,
  message_text TEXT NOT NULL,
  message_timestamp TIMESTAMPTZ,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','processing','completed','failed')),
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_attempt_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO linkedin_inbound_retry_queue (
  message_id, ghl_contact_id, linkedin_chat_id, linkedin_provider_id,
  unipile_account_id, message_text, message_timestamp, payload_json, last_error
)
SELECT
  ${esc(messageId)}, ${esc(contactId)}, ${esc(chatId)}, ${esc(providerId)},
  ${esc(accountId)}, ${esc(row.message_text || '')}, ${esc(timestamp)}::timestamptz,
  ${rawPayload}::jsonb, ${errorReason}
WHERE ${shouldUpsert}::boolean
  AND ${esc(status)}::text = 'error'
  AND ${errorReason}::text ILIKE '%401%'
ON CONFLICT (message_id) DO UPDATE SET
  updated_at = NOW(),
  last_error = EXCLUDED.last_error,
  status = CASE WHEN linkedin_inbound_retry_queue.status = 'completed' THEN 'completed' ELSE 'pending' END,
  next_attempt_at = NOW();
`;

""" + "const mapSql = `",
    )
    code = code.replace(
        "return [{ json: { ...row, sqlQuery: sql } }];",
        "const sqlQuery = retrySql + '\\n' + mapSql;\nreturn [{ json: { ...row, sqlQuery } }];",
    )
    target["parameters"]["jsCode"] = code
    pub = publish(inbound)
    if pub.get("versionId") != pub.get("activeVersionId") or not pub.get("active"):
        raise RuntimeError("Inbound workflow did not remain active/published")

# 2. Create/update a no-code-triggered retry workflow. The only Code node is
# bounded to the retry worker and does not contain credentials or secrets.
retry_code = r'''const row = $input.first()?.json || {};
const GHL_BASE = 'https://services.leadconnectorhq.com';
const VERSION = '2021-07-28';
const COMPANY_ID = '7vMmm4at5OrjQplRN3EO';
const LOCATION_ID = 'Zwz4relUXVPxx8uohnjV';
const PROVIDER_ID = '6a58a14ff3023bea3783c152';
const clean = (v) => v === null || v === undefined ? '' : String(v).trim();
const fail = (reason) => [{ json: { ...row, retry_status: 'retry', retry_error: clean(reason).slice(0, 500) } }];

if (!row.id || !row.agency_access_token) return fail('missing queue id or OAuth access token');
try {
  const tokenResponse = await this.helpers.httpRequest({
    method: 'POST', url: GHL_BASE + '/oauth/locationToken', json: true,
    headers: { Authorization: 'Bearer ' + clean(row.agency_access_token), Version: VERSION, Accept: 'application/json', 'Content-Type': 'application/json' },
    body: { companyId: COMPANY_ID, locationId: LOCATION_ID },
  });
  const locationToken = clean(tokenResponse?.access_token);
  if (!locationToken) return fail('location token exchange returned no access token');
  const response = await this.helpers.httpRequest({
    method: 'POST', url: GHL_BASE + '/conversations/messages/inbound', json: true, returnFullResponse: true,
    headers: { Authorization: 'Bearer ' + locationToken, Version: VERSION, Accept: 'application/json', 'Content-Type': 'application/json' },
    body: { type: 'Custom', contactId: clean(row.ghl_contact_id), message: row.message_text, conversationProviderId: PROVIDER_ID, altId: clean(row.linkedin_chat_id), date: row.message_timestamp || new Date().toISOString() },
  });
  const status = Number(response?.statusCode || response?.status || 0);
  if (status >= 200 && status < 300) return [{ json: { ...row, retry_status: 'completed', retry_error: '', ghl_response: response.body || {} } }];
  return fail('GHL inbound retry failed with HTTP ' + status);
} catch (error) {
  return fail(error?.message || error);
}'''

fetch_query = """CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue (
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
) t ON TRUE;"""

finalize_query = """UPDATE linkedin_inbound_retry_queue
SET status = CASE WHEN $2 = 'completed' THEN 'completed' WHEN attempts >= 5 THEN 'failed' ELSE 'pending' END,
    last_error = NULLIF($3, ''),
    next_attempt_at = CASE WHEN $2 = 'completed' OR attempts >= 5 THEN next_attempt_at ELSE NOW() + INTERVAL '10 minutes' END,
    completed_at = CASE WHEN $2 = 'completed' THEN NOW() ELSE completed_at END,
    updated_at = NOW()
WHERE id = $1;"""

nodes = [
    {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "10 */6 * * *"}]}}, "id": str(uuid.uuid4()), "name": "Every 6 Hours + 10 Minutes", "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.3, "position": [0, 0]},
    {"parameters": {"operation": "executeQuery", "query": fetch_query, "options": {"queryBatching": "independently"}}, "id": str(uuid.uuid4()), "name": "Claim Pending LinkedIn OAuth Retries", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [220, 0], "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}},
    {"parameters": {"mode": "runOnceForEachItem", "language": "javaScript", "jsCode": retry_code}, "id": str(uuid.uuid4()), "name": "Retry LinkedIn Inbound to GHL", "type": "n8n-nodes-base.code", "typeVersion": 2.2, "position": [460, 0]},
    {"parameters": {"operation": "executeQuery", "query": finalize_query, "options": {"queryBatching": "independently", "queryReplacement": "={{ [ $json.id, $json.retry_status || 'retry', $json.retry_error || '' ] }}"}}, "id": str(uuid.uuid4()), "name": "Finalize LinkedIn OAuth Retry", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [720, 0], "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}},
]
connections = {"Every 6 Hours + 10 Minutes": {"main": [[{"node": "Claim Pending LinkedIn OAuth Retries", "type": "main", "index": 0}]]}, "Claim Pending LinkedIn OAuth Retries": {"main": [[{"node": "Retry LinkedIn Inbound to GHL", "type": "main", "index": 0}]]}, "Retry LinkedIn Inbound to GHL": {"main": [[{"node": "Finalize LinkedIn OAuth Retry", "type": "main", "index": 0}]]}}
existing = None
for item in (api("/workflows?limit=200").get("data") or []):
    if item.get("name") == RETRY_NAME:
        existing = api(f"/workflows/{item['id']}")
        break
if existing:
    existing["nodes"] = nodes; existing["connections"] = connections
    result = publish(existing)
    retry_id = existing["id"]
else:
    result = api("/workflows", "POST", {"name": RETRY_NAME, "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1", "timezone": "UTC", "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all", "saveExecutionProgress": True, "executionTimeout": 300}})
    retry_id = result["id"]
api(f"/workflows/{retry_id}/activate", "POST", {})
checked = api(f"/workflows/{retry_id}")
print(json.dumps({"inboundWorkflow": INBOUND_ID, "retryWorkflow": retry_id, "retryName": checked.get("name"), "retryActive": checked.get("active"), "retryVersionId": checked.get("versionId"), "retryActiveVersionId": checked.get("activeVersionId"), "published": checked.get("versionId") == checked.get("activeVersionId"), "schedule": "10 */6 * * *", "queueInsertAdded": "linkedin_inbound_retry_queue" in target["parameters"]["jsCode"]}, indent=2))
