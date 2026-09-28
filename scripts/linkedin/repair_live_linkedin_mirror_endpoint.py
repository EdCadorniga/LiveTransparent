"""Use the verified inbound GHL Conversations endpoint for outbound mirroring."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE = "https://automations.livetransparent.com/api/v1/workflows/"
TARGETS = {
    "fXxw5lanZcDmUrst": "Dispatch LinkedIn Requests",
    "crKIsaL5k3YBfqDZ": "Dispatch LinkedIn Requests",
    "d0tEtijajisIsYcs": "Send DM Sequence Messages",
    "nspggypNF245xzeL": "Send DM Sequence Messages",
}
ALLOWED = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}


def api_key() -> str:
    value = os.environ.get("N8N_API_KEY_LT", "")
    if value:
        return value
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("N8N_API_KEY_LT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("N8N_API_KEY_LT is required")


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(BASE + workflow_id, data=body, method=method, headers={"X-N8N-API-KEY": api_key(), "Accept": "application/json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


for workflow_id, node_name in TARGETS.items():
    workflow = request(workflow_id)
    node = next(node for node in workflow["nodes"] if node["name"] == node_name)
    code = node["parameters"]["jsCode"]
    before = code.count("/conversations/messages'") + code.count("/conversations/messages\"")
    code = code.replace("/conversations/messages'", "/conversations/messages/inbound'")
    code = code.replace("/conversations/messages\"", "/conversations/messages/inbound\"")
    if before == 0:
        raise RuntimeError(f"mirror endpoint not found in {workflow_id}")
    node["parameters"]["jsCode"] = code
    payload = {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow["connections"], "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in ALLOWED}}
    updated = request(workflow_id, "PUT", payload)
    print(json.dumps({"workflow": workflow_id, "replaced": before, "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))
