"""Repair the duplicate SQL declaration in the live LinkedIn inbound workflow."""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE = "https://automations.livetransparent.com/api/v1"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"
NODE_NAME = "Build Upsert Map SQL"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(__file__).resolve().parents[2] / ".env"
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def request(api_key: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/workflows/{WORKFLOW_ID}",
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "LiveTransparent-LinkedIn-Inbound-Repair/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


api_key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT")
if not api_key:
    raise RuntimeError("N8N_API_KEY_LT is required")

workflow = request(api_key)
node = next(node for node in workflow["nodes"] if node.get("name") == NODE_NAME)
code = node["parameters"]["jsCode"]
code = code.replace(
    "const sql = `CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue",
    "const retrySql = `CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue",
)
code = code.replace(
    "const sql = `ALTER TABLE linkedin_conversation_map",
    "const mapSql = `ALTER TABLE linkedin_conversation_map",
)
code = code.replace(
    "  next_attempt_at = NOW();\n\nconst mapSql = `",
    "  next_attempt_at = NOW();\n`;\n\nconst mapSql = `",
)
code = code.replace(
    "return [{ json: { ...row, sqlQuery: sql } }];",
    "const sqlQuery = retrySql + '\\n' + mapSql;\nreturn [{ json: { ...row, sqlQuery } }];",
)

required = ("const retrySql = `", "const mapSql = `", "sqlQuery = retrySql")
if not all(value in code for value in required) or "const sql = `" in code:
    raise RuntimeError("LinkedIn inbound SQL repair did not produce the expected code")

node["parameters"]["jsCode"] = code
allowed_settings = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "binaryMode",
}
payload = {
    "name": workflow["name"],
    "nodes": workflow["nodes"],
    "connections": workflow["connections"],
    "settings": {key: value for key, value in workflow.get("settings", {}).items() if key in allowed_settings},
}
updated = request(api_key, "PUT", payload)
print(json.dumps({
    "id": updated["id"],
    "active": updated["active"],
    "versionId": updated["versionId"],
    "activeVersionId": updated.get("activeVersionId"),
    "published": updated["versionId"] == updated.get("activeVersionId"),
}))
