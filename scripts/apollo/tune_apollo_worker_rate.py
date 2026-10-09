"""Tune the scheduled Apollo worker's pace on n8n-lt.

Default mode is dry-run. Pass --apply to update/publish the live workflow.
This changes only the Schedule Trigger interval and Config.maxPerRun; it does
not start an execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ID = "JH8ShfpglWmLMZ3l"
EXPECTED_VERSION = "cb8e76e4-a190-43b4-97fc-05ca971cfaf8"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"
WORKER_NAME = "Enrich Contacts via Apollo"
CONFIG_NAME = "Config"


def load_key() -> str:
    key = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not key:
        raise RuntimeError("N8N_LT_API_KEY is unavailable in repository .env")
    return str(key)


def read_workflow(session: requests.Session) -> dict:
    response = session.get(
        f"https://automations.livetransparent.com/api/v1/workflows/{WORKFLOW_ID}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def prepare(workflow: dict) -> tuple[dict, int, int]:
    if workflow.get("versionId") != EXPECTED_VERSION or workflow.get("activeVersionId") != EXPECTED_VERSION:
        raise RuntimeError("Apollo workflow version drifted; inspect live state before tuning")
    if not workflow.get("active") or workflow.get("isArchived"):
        raise RuntimeError("Apollo poller is not active/non-archived")

    nodes = [dict(node) for node in workflow.get("nodes", [])]
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    if not schedule or not config or not worker or len(nodes) != 4:
        raise RuntimeError("Expected 4-node paced Apollo graph not found")

    intervals = schedule.get("parameters", {}).get("rule", {}).get("interval", [])
    if len(intervals) != 1 or intervals[0].get("field") != "minutes":
        raise RuntimeError("Unexpected schedule interval configuration")
    old_minutes = int(intervals[0].get("minutesInterval", 0))
    intervals[0]["minutesInterval"] = 5

    assignments = config.get("parameters", {}).get("assignments", {}).get("assignments", [])
    cap = next((a for a in assignments if a.get("name") == "maxPerRun"), None)
    if cap is None or int(cap.get("value", 0)) != 5 or cap.get("type") != "number":
        raise RuntimeError("Expected numeric Config.maxPerRun=5; inspect before tuning")
    cap["value"] = 10

    allowed_settings = {
        "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
        "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy",
    }
    settings = {k: v for k, v in (workflow.get("settings") or {}).items() if k in allowed_settings}
    payload = {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": workflow.get("connections", {}),
        "settings": settings,
    }
    return payload, old_minutes, int(cap.get("value"))


def execution_count(session: requests.Session, status: str) -> int:
    r = session.get(
        "https://automations.livetransparent.com/api/v1/executions",
        params={"workflowId": WORKFLOW_ID, "status": status, "limit": 100, "includeData": "false"},
        timeout=30,
    )
    r.raise_for_status()
    return len(r.json().get("data", []))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply/publish the live n8n-lt change")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({"X-N8N-API-KEY": load_key(), "Content-Type": "application/json"})
    health = session.get("https://automations.livetransparent.com/healthz/readiness", timeout=20)
    if health.status_code != 200:
        raise RuntimeError(f"n8n-lt readiness failed: HTTP {health.status_code}")
    before = read_workflow(session)
    payload, old_minutes, new_cap = prepare(before)
    active_runs = {s: execution_count(session, s) for s in ("new", "running", "waiting")}
    if any(active_runs.values()):
        raise RuntimeError(f"Worker has pending/active executions; refusing tune: {active_runs}")

    report = {
        "workflowId": WORKFLOW_ID,
        "beforeVersionId": before.get("versionId"),
        "beforeActiveVersionId": before.get("activeVersionId"),
        "beforeIntervalMinutes": old_minutes,
        "afterIntervalMinutes": 5,
        "beforeMaxPerRun": 5,
        "afterMaxPerRun": new_cap,
        "pendingOrActiveBefore": active_runs,
        "writeRequested": args.apply,
    }
    if not args.apply:
        print(json.dumps(report, indent=2))
        return 0

    response = session.put(
        f"https://automations.livetransparent.com/api/v1/workflows/{WORKFLOW_ID}",
        json=payload,
        timeout=60,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"n8n-lt workflow update failed: HTTP {response.status_code}")

    after = read_workflow(session)
    _, interval, cap = prepare_after(after)
    if not after.get("active") or after.get("isArchived") or after.get("versionId") != after.get("activeVersionId"):
        raise RuntimeError("Updated workflow is not active with matching draft/active versions")
    if interval != 5 or cap != 10:
        raise RuntimeError("Post-update readback did not match the requested pace/cap")
    report.update({
        "afterVersionId": after.get("versionId"),
        "afterActiveVersionId": after.get("activeVersionId"),
        "afterActive": after.get("active"),
        "afterArchived": after.get("isArchived"),
        "afterNodeCount": len(after.get("nodes", [])),
        "verifiedIntervalMinutes": interval,
        "verifiedMaxPerRun": cap,
        "note": "No manual execution was started.",
    })
    print(json.dumps(report, indent=2))
    return 0


def prepare_after(workflow: dict) -> tuple[dict, int, int]:
    nodes = workflow.get("nodes", [])
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    if not schedule or not config:
        raise RuntimeError("Post-update readback missing schedule/config nodes")
    minutes = int(schedule.get("parameters", {}).get("rule", {}).get("interval", [{}])[0].get("minutesInterval", 0))
    assignments = config.get("parameters", {}).get("assignments", {}).get("assignments", [])
    cap = next((int(a.get("value")) for a in assignments if a.get("name") == "maxPerRun"), 0)
    return workflow, minutes, cap


if __name__ == "__main__":
    raise SystemExit(main())
