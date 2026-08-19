"""Fix the LinkedIn DM pipeline: dispatcher regex, DM send chat routing, reply-backfill suppression."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
DISPATCHER = "fXxw5lanZcDmUrst"
DM_SEQUENCE = "d0tEtijajisIsYcs"
REPLY_BACKFILL = "QfJ2EZcc7lZwNgxj"
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


def must_sub(code: str, pattern: str, replacement: str, label: str, count: int = 1) -> str:
    new_code, found = re.subn(pattern, replacement, code, flags=re.DOTALL)
    if found != count:
        raise RuntimeError(f"{label}: expected {count} regex match(es), found {found}")
    return new_code


def patch_dispatcher() -> None:
    wf = request(DISPATCHER)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished Dispatcher draft")
    node = node_map(wf)["Dispatch LinkedIn Requests"]
    code = str(node["parameters"]["jsCode"])
    old = "replace(/^https?:\\\\/\\\\//i, '')"
    new = "replace(/^https?:[/][/]/i, '')"
    code = must_replace(code, old, new, "dispatcher identifier regex")
    node["parameters"]["jsCode"] = code
    updated = update_workflow(wf)
    print(json.dumps({"patch": "dispatcher", "id": updated.get("id"), "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


def patch_dm_sequence() -> None:
    wf = request(DM_SEQUENCE)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished DM Sequence draft")
    node = node_map(wf)["Send DM Sequence Messages"]
    code = str(node["parameters"]["jsCode"])

    # Route to the existing Unipile chat when one already exists; otherwise start a new chat.
    old_send = (
        "return unipileReq.call(self, 'POST', CFG.unipileApiBaseUrl + '/chats', {\n"
        "                account_id: CFG.unipileAccountId,\n"
        "                attendees_ids: [providerId],\n"
        "                text: message,\n"
        "              }, { 'X-API-KEY': CFG.unipileApiKey });"
    )
    new_send = (
        "var existingChatId = clean(payload.last_chat_id || d.last_chat_id || '');\n"
        "              if (existingChatId) {\n"
        "                return unipileReq.call(self, 'POST', CFG.unipileApiBaseUrl + '/chats/' + encodeURIComponent(existingChatId) + '/messages', {\n"
        "                  account_id: CFG.unipileAccountId,\n"
        "                  text: message,\n"
        "                }, { 'X-API-KEY': CFG.unipileApiKey });\n"
        "              }\n"
        "              return unipileReq.call(self, 'POST', CFG.unipileApiBaseUrl + '/chats', {\n"
        "                account_id: CFG.unipileAccountId,\n"
        "                attendees_ids: [providerId],\n"
        "                text: message,\n"
        "              }, { 'X-API-KEY': CFG.unipileApiKey });"
    )
    code = must_replace(code, old_send, new_send, "dm sequence chat routing")

    # Capture the provider response body (including err.cause) so future 422s are diagnosable.
    old_err = "var data = (err && err.response && err.response.body) || (err && err.message) || err;"
    new_err = "var body = (err && err.response && err.response.body) || (err && err.cause && err.cause.response && err.cause.response.body); var data = body || (err && err.message) || err;"
    code = must_replace(code, old_err, new_err, "dm sequence error capture")

    node["parameters"]["jsCode"] = code
    updated = update_workflow(wf)
    print(json.dumps({"patch": "dm_sequence", "id": updated.get("id"), "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


def patch_reply_backfill() -> None:
    wf = request(REPLY_BACKFILL)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished Reply Backfill draft")
    node = node_map(wf)["Check Reply Backfill State"]
    code = str(node["parameters"]["jsCode"])
    old = "const shouldRemainActive = existingActive || backfillStatus === 'error' || replyDetected;"
    new = "const shouldRemainActive = existingActive || replyDetected;"
    code = must_replace(code, old, new, "reply backfill suppression")
    node["parameters"]["jsCode"] = code
    updated = update_workflow(wf)
    print(json.dumps({"patch": "reply_backfill", "id": updated.get("id"), "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


def main() -> None:
    patch_dispatcher()
    patch_dm_sequence()
    patch_reply_backfill()


if __name__ == "__main__":
    main()