"""Repair the two failed PIT workflows through the n8n REST fallback."""

from __future__ import annotations

import json
import os
import subprocess

from review_company_instagram_sources import load_env_file


N8N_BASE = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_IDS = ["NTpQnMrpjzusPXHX", "dZQLlbTLkpE1843X"]


def api_key() -> str:
    return os.environ.get("N8N_API_KEY_LT") or load_env_file().get("N8N_API_KEY_LT", "")


def pit_values() -> tuple[str, str]:
    env = load_env_file()
    old = os.environ.get("GHL_OLD_PIT") or env.get("GHL_OLD_PIT", "")
    new = os.environ.get("GHL_PIT") or env.get("GHL_PIT", "")
    if not old or not new:
        raise RuntimeError("Set GHL_OLD_PIT and GHL_PIT before running the repair")
    return old, new


def curl(args: list[str], body: bytes | None = None) -> dict:
    result = subprocess.run(
        ["curl.exe", "-sS", *args],
        input=body,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout.decode("utf-8", errors="replace"))


def replace_value(value):
    old, new = pit_values()
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [replace_value(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_value(item) for key, item in value.items()}
    return value


def main() -> None:
    key = api_key()
    pit_values()
    headers = ["-H", f"X-N8N-API-KEY: {key}", "-H", "Accept: application/json"]
    allowed_settings = {
        "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
        "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy",
        "errorWorkflow", "binaryMode",
    }
    for workflow_id in WORKFLOW_IDS:
        current = curl([*headers, N8N_BASE + workflow_id])
        settings = {k: v for k, v in (current.get("settings") or {}).items() if k in allowed_settings}
        nodes = current.get("nodes") or []
        changed = False
        for node in nodes:
            if node.get("name") != "Config":
                continue
            params = node.get("parameters") or {}
            if "parameters" in params:
                params.pop("parameters", None)
                changed = True
            replaced = replace_value(params)
            if replaced != params:
                changed = True
            node["parameters"] = replaced
        if not changed:
            raise RuntimeError(f"No repairable PIT assignment found in {workflow_id}")
        body = json.dumps({
            "name": current.get("name"),
            "nodes": nodes,
            "connections": current.get("connections") or {},
            "settings": settings,
        }, ensure_ascii=True).encode("utf-8")
        updated = curl([
            *headers,
            "-X", "PUT",
            "-H", "Content-Type: application/json",
            N8N_BASE + workflow_id,
            "--data-binary", "@-",
        ], body)
        print(json.dumps({
            "id": workflow_id,
            "name": updated.get("name"),
            "versionId": updated.get("versionId"),
            "activeVersionId": updated.get("activeVersionId"),
            "active": updated.get("active"),
        }))


if __name__ == "__main__":
    main()
