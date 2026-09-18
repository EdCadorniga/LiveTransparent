"""Make LinkedIn inbound reporting fall back to conversation-map rows.

Some older LinkedIn contacts have a valid ``linkedin_conversation_map`` row but
no corresponding ``linkedin_connection_state`` row.  Inbound messages already
reach GHL through the map, but the state lookup then returns no row and the
``reply_received`` report event is skipped.  The fallback below preserves the
normal state-table precedence, ignores synthetic ``linkedin:`` contact IDs,
and uses the mapped real GHL contact only for reporting/state reconciliation.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"
NODE_NAME = "Build Find State SQL"

ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
    "availableInMCP",
}

NEW_CODE = r'''function esc(v) {
  if (v === null || v === undefined) return 'NULL';
  return "'" + String(v).replace(/'/g, "''") + "'";
}

const row = $input.first().json || {};
const event = $node['Normalize Unipile Message Event'].json || {};
const providerId = row.linkedin_provider_id || row.sender_provider_id || event.sender_provider_id || '';
const accountId = row.unipile_account_id || row.account_id || event.account_id || '';
const isInbound = row.is_inbound !== undefined ? !!row.is_inbound : !!event.is_inbound;

const stateColumns = `
  ghl_contact_id, location_id, unipile_account_id, linkedin_profile_url,
  linkedin_public_identifier, linkedin_provider_id, connection_request_tag,
  connection_status, request_sent_at, connected_at, dm_sequence_started_at,
  last_checked_at, request_message, request_message_hash, sequence_step,
  payload_json, metadata_json, source_table`;

const sql = `WITH main_match AS (
  SELECT ${stateColumns.replace('source_table', "'linkedin_connection_state'::text AS source_table")}
  FROM linkedin_connection_state
  WHERE ${isInbound}::boolean
    AND linkedin_provider_id = ${esc(providerId)}
    AND unipile_account_id = ${esc(accountId)}
    AND ghl_contact_id NOT LIKE 'linkedin:%'
  ORDER BY updated_at DESC NULLS LAST, last_checked_at DESC NULLS LAST
  LIMIT 1
), partnership_match AS (
  SELECT ${stateColumns.replace('source_table', "'partnership_linkedin_connection_state'::text AS source_table")}
  FROM partnership_linkedin_connection_state
  WHERE ${isInbound}::boolean
    AND NOT EXISTS (SELECT 1 FROM main_match)
    AND linkedin_provider_id = ${esc(providerId)}
    AND unipile_account_id = ${esc(accountId)}
    AND ghl_contact_id NOT LIKE 'linkedin:%'
  ORDER BY updated_at DESC NULLS LAST, last_checked_at DESC NULLS LAST
  LIMIT 1
), map_match AS (
  SELECT
    m.ghl_contact_id,
    'Zwz4relUXVPxx8uohnjV'::text AS location_id,
    m.unipile_account_id,
    m.linkedin_profile_url,
    ''::text AS linkedin_public_identifier,
    m.linkedin_provider_id,
    'linkedin_connection_requested'::text AS connection_request_tag,
    'requested'::text AS connection_status,
    NULL::timestamptz AS request_sent_at,
    NULL::timestamptz AS connected_at,
    NULL::timestamptz AS dm_sequence_started_at,
    NULL::timestamptz AS last_checked_at,
    NULL::text AS request_message,
    NULL::text AS request_message_hash,
    0::integer AS sequence_step,
    COALESCE(m.raw_payload, m.payload_json, '{}'::jsonb) AS payload_json,
    jsonb_build_object('source', 'linkedin_conversation_map_fallback') AS metadata_json,
    'linkedin_connection_state'::text AS source_table
  FROM linkedin_conversation_map m
  WHERE ${isInbound}::boolean
    AND NOT EXISTS (SELECT 1 FROM main_match)
    AND NOT EXISTS (SELECT 1 FROM partnership_match)
    AND m.ghl_contact_id IS NOT NULL
    AND m.ghl_contact_id <> ''
    AND (
      (m.linkedin_provider_id = ${esc(providerId)} AND m.unipile_account_id = ${esc(accountId)})
      OR (m.linkedin_chat_id = ${esc(event.chat_id || '')})
    )
  ORDER BY m.updated_at DESC NULLS LAST
  LIMIT 1
)
SELECT * FROM main_match
UNION ALL SELECT * FROM partnership_match
UNION ALL SELECT * FROM map_match;`;

return [{ json: { ...row, sqlQuery: sql } }];'''


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    root = Path(__file__).resolve().parents[2]
    for raw in (root / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
    if not key:
        raise RuntimeError("N8N_API_KEY_LT is required")
    return key


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def syntax_check(code: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "check.js"
        path.write_text("async function __n8n_wrap__() {\n" + code + "\n}\n__n8n_wrap__();", encoding="utf-8")
        result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())


def main() -> None:
    workflow = request(WORKFLOW_ID)
    nodes = workflow.get("nodes") or []
    target = next((node for node in nodes if node.get("name") == NODE_NAME), None)
    if not target:
        raise RuntimeError(f"node not found: {NODE_NAME}")
    syntax_check(NEW_CODE)
    target.setdefault("parameters", {})["jsCode"] = NEW_CODE
    settings = {k: v for k, v in (workflow.get("settings") or {}).items() if k in ALLOWED_SETTINGS}
    payload = {
        "name": workflow.get("name"),
        "nodes": nodes,
        "connections": workflow.get("connections") or {},
        "settings": settings,
    }
    updated = request(WORKFLOW_ID, method="PUT", payload=payload)
    checked = request(WORKFLOW_ID)
    checked_node = next(node for node in checked.get("nodes") or [] if node.get("name") == NODE_NAME)
    if (checked_node.get("parameters") or {}).get("jsCode") != NEW_CODE:
        raise RuntimeError("verification failed: live code mismatch")
    print(json.dumps({
        "workflow_id": WORKFLOW_ID,
        "workflow_name": checked.get("name"),
        "updated": bool(updated),
        "active": checked.get("active"),
        "version_id": checked.get("versionId"),
        "active_version_id": checked.get("activeVersionId"),
        "draft_is_active": checked.get("versionId") == checked.get("activeVersionId"),
        "node": NODE_NAME,
        "syntax": "ok",
    }, indent=2))


if __name__ == "__main__":
    main()
