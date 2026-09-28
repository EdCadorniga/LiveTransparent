"""Move the LinkedIn GHL mirror helper to top-level Code-node scope."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE = "https://automations.livetransparent.com/api/v1/workflows/"
TARGETS = {
    "fXxw5lanZcDmUrst": ("Dispatch LinkedIn Requests", "function buildOutboundMessage(template, firstName) {"),
    "crKIsaL5k3YBfqDZ": ("Dispatch LinkedIn Requests", "function sanitizeMessage(text) {"),
    "d0tEtijajisIsYcs": ("Send DM Sequence Messages", "function buildOutboundMessage(template, firstName) {"),
}
ALLOWED = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}


def key() -> str:
    value = os.environ.get("N8N_API_KEY_LT", "")
    if value:
        return value
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("N8N_API_KEY_LT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("N8N_API_KEY_LT is required")


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(BASE + workflow_id, data=body, method=method, headers={"X-N8N-API-KEY": key(), "Accept": "application/json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def repair(workflow_id: str, node_name: str, anchor: str) -> None:
    workflow = request(workflow_id)
    node = next(node for node in workflow["nodes"] if node["name"] == node_name)
    code = node["parameters"]["jsCode"]
    marker = "async function mirrorLinkedInToGhl(contactId, messageText, altId, firstName, sourceName) {"
    start = code.find(marker)
    if start < 0:
        raise RuntimeError(f"mirror helper missing in {workflow_id}")
    depth = 0
    end = None
    for index in range(start, len(code)):
        if code[index] == "{":
            depth += 1
        elif code[index] == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise RuntimeError(f"mirror helper is unbalanced in {workflow_id}")
    helper = code[start:end]
    code = code[:start] + code[end:]
    anchor_index = code.find(anchor)
    if anchor_index < 0:
        raise RuntimeError(f"anchor missing in {workflow_id}")
    code = code[:anchor_index] + helper + "\n" + code[anchor_index:]
    node["parameters"]["jsCode"] = code
    payload = {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow["connections"], "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in ALLOWED}}
    updated = request(workflow_id, "PUT", payload)
    print(json.dumps({"workflow": workflow_id, "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


for workflow_id, (node_name, anchor) in TARGETS.items():
    repair(workflow_id, node_name, anchor)
