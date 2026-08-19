"""Prevent downgrading 'requested' state rows back to 'ready'/'requested_pending' in the shared state upsert."""

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
    old = (
        "WHEN linkedin_connection_state.connection_status='requested_pending'"
        " AND EXCLUDED.connection_status='ready'"
        " THEN linkedin_connection_state.connection_status"
    )
    new = (
        old
        + " WHEN linkedin_connection_state.connection_status='requested'"
        " AND EXCLUDED.connection_status IN ('ready','requested_pending')"
        " THEN linkedin_connection_state.connection_status"
    )
    code = must_replace(code, old, new, "state upsert requested downgrade guard")
    node["parameters"]["jsCode"] = code

    updated = update_workflow(wf)
    print(json.dumps({
        "patch": "state_upsert_requested_guard",
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
    }))


if __name__ == "__main__":
    main()