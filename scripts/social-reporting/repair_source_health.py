"""Expose report-runtime and appointment-snapshot health in Executive Summary."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


WORKFLOW_ID = "Bukc0mgOD2r7V6ED"
HOST = "https://automations.livetransparent.com"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def request(method: str = "GET", payload: dict | None = None) -> dict:
    env = load_env()
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{HOST}/api/v1/workflows/{WORKFLOW_ID}",
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": os.environ.get("N8N_API_KEY_LT") or env["N8N_API_KEY_LT"],
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    workflow = request()
    if workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError("Refusing to patch an unpublished Executive Summary draft")
    build = next(node for node in workflow["nodes"] if node.get("name") == "Build Query")
    code = build["parameters"]["jsCode"]
    old = """health AS (  SELECT COALESCE(json_agg(row_to_json(t) ORDER BY t.source_system), '[]'::json) AS items FROM (    SELECT btrim(source_system, '\"') AS source_system, CASE WHEN source_system IN ('email_events','linkedin_activity_events') THEN status WHEN last_success_at IS NULL OR (stale_after_hours > 0 AND last_success_at < NOW() - (stale_after_hours || ' hours')::interval) THEN 'stale' ELSE status END AS status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error FROM report_source_health WHERE source_system <> 'undefined' ORDER BY btrim(source_system, '\"')  ) t),"""
    new = """health AS (  SELECT COALESCE(json_agg(row_to_json(t) ORDER BY t.source_system), '[]'::json) AS items FROM (    SELECT btrim(source_system, '\"') AS source_system, CASE WHEN source_system IN ('email_events','linkedin_activity_events') THEN status WHEN last_success_at IS NULL OR (stale_after_hours > 0 AND last_success_at < NOW() - (stale_after_hours || ' hours')::interval) THEN 'stale' ELSE status END AS status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error FROM report_source_health WHERE source_system NOT IN ('undefined', 'n8n', 'postgres', 'appointments')    UNION ALL    SELECT 'appointments', CASE WHEN MAX(loaded_at) IS NULL THEN 'pending' WHEN MAX(loaded_at) < NOW() - INTERVAL '48 hours' THEN 'stale' ELSE 'ready' END, MAX(loaded_at), MAX(loaded_at), COUNT(*)::int, 48, NULL::text FROM report_raw_ghl_appointments    UNION ALL    SELECT 'n8n', 'ready', NOW(), NOW(), 1, 1, NULL::text    UNION ALL    SELECT 'postgres', 'ready', NOW(), NOW(), 1, 1, NULL::text    ORDER BY source_system  ) t),"""
    if old in code:
        code = code.replace(old, new, 1)
    elif "FROM report_source_health WHERE source_system NOT IN ('undefined', 'n8n', 'postgres', 'appointments')" in code and "UNION ALL    SELECT 'appointments'" in code:
        code = code.replace("ORDER BY btrim(source_system, '\"')  ) t),", "ORDER BY source_system  ) t),", 1)
    else:
        raise RuntimeError("Expected health CTE was not found; no change made")
    build["parameters"]["jsCode"] = code
    settings = {k: v for k, v in (workflow.get("settings") or {}).items() if k != "availableInMCP"}
    updated = request("PUT", {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": settings,
    })
    print(json.dumps({
        "workflowId": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
        "active": updated.get("active"),
    }, indent=2))


if __name__ == "__main__":
    main()
