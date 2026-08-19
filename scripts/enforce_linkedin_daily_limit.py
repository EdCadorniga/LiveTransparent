"""Enforce the Dispatcher daily invite limit (config declares 60/day but it is not applied)."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
DISPATCHER = "fXxw5lanZcDmUrst"
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


def main() -> None:
    wf = request(DISPATCHER)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished Dispatcher draft")
    node = None
    for n in wf.get("nodes", []):
        if n.get("name") == "Dispatch LinkedIn Requests":
            node = n
            break
    if node is None:
        raise RuntimeError("Dispatch LinkedIn Requests node not found")

    code = str(node["parameters"]["jsCode"])

    guard_block = (
        "const results = [];\n"
        "const { Client } = require('pg');\n"
        "let batchTarget;\n"
        "const pgClient = new Client({ host: 'postgres', port: 5432, database: 'postgres', user: 'postgres', password: String((cfg && cfg.pgPassword) || 'P@ssDatabase%!'), connectionTimeoutMillis: 10000 });\n"
        "try {\n"
        "  await pgClient.connect();\n"
        "  const sentRow = await pgClient.query(\"SELECT count(*)::int AS n FROM linkedin_connection_state WHERE connection_status = 'requested' AND request_sent_at IS NOT NULL AND request_sent_at >= (NOW() AT TIME ZONE 'America/Los_Angeles')::date\");\n"
        "  await pgClient.end();\n"
        "  const sentToday = Number((sentRow.rows && sentRow.rows[0] && sentRow.rows[0].n) || 0);\n"
        "  const dailyLimit = Math.max(1, Number(cfg.dailyLimit || 60));\n"
        "  batchTarget = Math.min(queue.length, CFG.batchSize, Math.max(0, dailyLimit - sentToday));\n"
        "  if (batchTarget <= 0) {\n"
        "    return [{ json: { ok: true, queue_found: queue.length, batch_size: 0, sent: 0, dry_runs: 0, failed: 0, errors: 0, api_calls: apiCalls, results: [], note: 'Daily invite limit reached (' + sentToday + '/' + dailyLimit + ')' } }];\n"
        "  }\n"
        "} catch (pgErr) {\n"
        "  await pgClient.end().catch(function() {});\n"
        "  batchTarget = Math.min(queue.length, CFG.batchSize);\n"
        "}\n"
        "for (const row of queue.slice(0, batchTarget)) {"
    )
    old_loop = "const results = [];\nfor (const row of queue.slice(0, CFG.batchSize)) {"
    code = must_replace(code, old_loop, guard_block, "dispatcher daily limit")

    node["parameters"]["jsCode"] = code
    updated = update_workflow(wf)
    print(json.dumps({
        "patch": "dispatcher_daily_limit",
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
    }))


if __name__ == "__main__":
    main()