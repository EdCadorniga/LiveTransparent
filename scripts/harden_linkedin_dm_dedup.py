"""Harden the LinkedIn DM sequence against duplicate sends.

- Records a durable dm_sent event (idempotent on event_key) right after a successful
  Unipile send and BEFORE the state upsert, so a state-upsert failure cannot cause a
  duplicate re-send of the same step.
- Excludes rows from the DM queue that already have a dm_sent event for their pending
  next step.
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
DM_SEQUENCE = "d0tEtijajisIsYcs"
ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
    "availableInMCP",
}


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
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


def node_map(workflow: dict) -> dict[str, dict]:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def update_workflow(workflow: dict) -> dict:
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
    payload = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": settings,
    }
    return request(workflow["id"], method="PUT", payload=payload)


def must_replace(code: str, old: str, new: str, label: str, count: int = 1) -> str:
    found = code.count(old)
    if found != count:
        raise RuntimeError(f"{label}: expected {count} match(es), found {found}")
    return code.replace(old, new)


HELPER = """        function recordDmSentEvent(contactId, providerId, stepNum, chatId) {
          const { Client } = require('pg');
          var pgPassword = String((CFG && CFG.pgPassword) || 'P@ssDatabase%!');
          var client = new Client({ host: 'postgres', port: 5432, database: 'postgres', user: 'postgres', password: pgPassword, connectionTimeoutMillis: 10000 });
          return client.connect().then(function() {
            return client.query(
              "INSERT INTO linkedin_activity_events (event_key, event_type, event_at, ghl_contact_id, location_id, channel, provider_id, campaign_key, workflow_name, payload_json) VALUES ($1, 'dm_sent', NOW(), $2, 'Zwz4relUXVPxx8uohnjV', 'linkedin', $3, 'dan_linkedin', 'LT - LinkedIn DM Sequence (Unipile)', $4::jsonb) ON CONFLICT (event_key) DO NOTHING",
              ['dm_sent:' + contactId + ':' + stepNum, contactId, providerId || '', JSON.stringify({ step: stepNum, chat_id: chatId || '' })]
            );
          }).then(function() {
            return client.end();
          }, function(err) {
            return client.end().catch(function() {}).then(function() { return Promise.reject(err); });
          }).catch(function() { /* best-effort durable marker */ });
        }

        var inputItems = [];"""


def patch_dm_sequence() -> None:
    wf = request(DM_SEQUENCE)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished DM Sequence draft")

    # 1) Config: expose pgPassword (empty -> fallback in helper)
    config = node_map(wf)["Config"]
    code = str(config["parameters"]["jsCode"]) if config.get("parameters", {}).get("jsCode") else ""
    if "jsCode" in config.get("parameters", {}):
        old_cfg = "            stateUpsertUrl: String(c.stateUpsertUrl || '').trim(),\n            templateVariant:"
        new_cfg = "            stateUpsertUrl: String(c.stateUpsertUrl || '').trim(),\n            pgPassword: String(c.pgPassword || ''),\n            templateVariant:"
        code = must_replace(code, old_cfg, new_cfg, "dm config pgPassword")
        config["parameters"]["jsCode"] = code
    else:
        # Set v3.4 config node: assignments (mode manual). Append pgPassword assignment.
        assignments = (config.get("parameters") or {}).get("assignments", {})
        items = (assignments or {}).get("assignments") or []
        items.append({"id": "pg-password", "name": "pgPassword", "type": "string", "value": ""})
        assignments["assignments"] = items
        config["parameters"]["assignments"] = assignments

    # 2) Send node: add helper before inputItems
    send = node_map(wf)["Send DM Sequence Messages"]
    s_code = str(send["parameters"]["jsCode"])
    anchor = "        var inputItems = [];"
    s_code = must_replace(s_code, anchor, HELPER, "dm send helper insert")

    # 3) Send node: chain the durable marker before the state upsert
    old_chain = (
        "              return self.helpers.httpRequest({\n"
        "                method: 'POST',\n"
        "                url: CFG.stateUpsertUrl,\n"
        "                headers: { Accept: 'application/json', 'Content-Type': 'application/json' },\n"
        "                body: upsertBody,\n"
        "                json: true,\n"
        "              }).then(function() {"
    )
    new_chain = (
        "              return recordDmSentEvent.call(self, contactId, providerId, newStep, chatId).then(function() {\n"
        "                return self.helpers.httpRequest({\n"
        "                  method: 'POST',\n"
        "                  url: CFG.stateUpsertUrl,\n"
        "                  headers: { Accept: 'application/json', 'Content-Type': 'application/json' },\n"
        "                  body: upsertBody,\n"
        "                  json: true,\n"
        "                });\n"
        "              }).then(function() {"
    )
    s_code = must_replace(s_code, old_chain, new_chain, "dm send marker chain")

    send["parameters"]["jsCode"] = s_code

    # 4) Find query: skip steps already sent
    find = node_map(wf)["Find Contacts Ready for DM"]
    query = str(find["parameters"]["query"])
    old_query = "ORDER BY sequence_step ASC, dm_sequence_started_at ASC NULLS FIRST\nLIMIT 40;"
    new_query = (
        "  AND NOT EXISTS (\n"
        "    SELECT 1 FROM linkedin_activity_events e\n"
        "    WHERE e.event_type = 'dm_sent'\n"
        "      AND e.ghl_contact_id = linkedin_connection_state.ghl_contact_id\n"
        "      AND e.event_key = 'dm_sent:' || linkedin_connection_state.ghl_contact_id || ':' || (linkedin_connection_state.sequence_step + 1)\n"
        "  )\n"
        "ORDER BY sequence_step ASC, dm_sequence_started_at ASC NULLS FIRST\n"
        "LIMIT 40;"
    )
    find["parameters"]["query"] = must_replace(query, old_query, new_query, "dm find dedup guard")

    updated = update_workflow(wf)
    print(json.dumps({
        "patch": "dm_dedup_harden",
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
    }))


if __name__ == "__main__":
    patch_dm_sequence()