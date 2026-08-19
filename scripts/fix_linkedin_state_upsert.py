"""Fix the LinkedIn state-upsert so requested_pending can advance to requested after a real invite."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
STATE_UPSERT = "Old7ZvyVYgFaJgDr"
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
    wf = request(STATE_UPSERT)
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("Refusing to patch unpublished State Upsert draft")
    node = None
    for n in wf.get("nodes", []):
        if n.get("name") == "Build Upsert SQL":
            node = n
            break
    if node is None:
        raise RuntimeError("Build Upsert SQL node not found")

    code = str(node["parameters"]["jsCode"])
    # The active-conversation preservation clause blocks requested_pending -> requested for any
    # row whose payload was stamped dm_conversation_status='active' (which the old reply backfill
    # did on conversation-check errors, not only on real replies). Real replies are guarded at the
    # send sites (dispatcher/DM reply checks fail closed), so this preservation is both harmful
    # and unnecessary for progression.
    old_clause = (
        " WHEN linkedin_connection_state.payload_json->>'dm_conversation_status'='active'"
        " AND EXCLUDED.payload_json->>'dm_conversation_status' IS DISTINCT FROM 'active'"
        " THEN linkedin_connection_state.connection_status"
    )
    code = must_replace(code, old_clause, "", "state upsert active-preservation clause")
    node["parameters"]["jsCode"] = code

    updated = update_workflow(wf)
    print(json.dumps({
        "patch": "state_upsert_progression",
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
    }))


if __name__ == "__main__":
    main()