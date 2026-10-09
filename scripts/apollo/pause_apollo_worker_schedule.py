"""Pause only the scheduled Apollo worker while retaining webhook ack path.

Default mode is dry-run. Pass --apply to disable the Schedule Trigger on the
active n8n-lt Apollo poller; no execution is started by this script.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[2]
BASE = "https://automations.livetransparent.com"
WORKFLOW_ID = "JH8ShfpglWmLMZ3l"
EXPECTED_VERSION = "d84f21d8-2026-4b70-a0c4-7a5b18215a93"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Disable the live Schedule Trigger")
    args = parser.parse_args()
    key = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not key:
        raise RuntimeError("n8n-lt API credential unavailable")
    s = requests.Session()
    s.headers.update({"X-N8N-API-KEY": str(key), "Content-Type": "application/json"})

    if s.get(f"{BASE}/healthz/readiness", timeout=20).status_code != 200:
        raise RuntimeError("n8n-lt readiness failed")
    r = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    r.raise_for_status()
    w = r.json()
    if w.get("versionId") != EXPECTED_VERSION or w.get("activeVersionId") != EXPECTED_VERSION:
        raise RuntimeError("Live Apollo workflow version drifted; inspect before pausing")
    if not w.get("active") or w.get("isArchived"):
        raise RuntimeError("Apollo workflow is not active/non-archived")

    for state in ("new", "running", "waiting"):
        e = s.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=30)
        e.raise_for_status()
        if e.json().get("data"):
            raise RuntimeError(f"Worker has {state} executions; wait for them to finish before changing schedule")

    nodes = [dict(n) for n in w.get("nodes", [])]
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    if schedule is None:
        raise RuntimeError("Expected Apollo Schedule Trigger not found")
    if schedule.get("disabled") is True:
        print(json.dumps({"alreadyPaused": True, "versionId": w.get("versionId")}))
        return 0
    schedule["disabled"] = True

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {
        "name": w["name"],
        "nodes": nodes,
        "connections": w.get("connections", {}),
        "settings": {k: v for k, v in (w.get("settings") or {}).items() if k in allowed},
    }
    report = {"workflowId": WORKFLOW_ID, "scheduleNode": SCHEDULE_NAME, "writeRequested": args.apply, "webhookAckPathRetained": True}
    if not args.apply:
        print(json.dumps(report, indent=2))
        return 0

    put = s.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if put.status_code not in (200, 201):
        raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    check = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    check.raise_for_status()
    after = check.json()
    paused = next(n for n in after.get("nodes", []) if n.get("name") == SCHEDULE_NAME).get("disabled") is True
    if not after.get("active") or after.get("isArchived") or after.get("versionId") != after.get("activeVersionId") or not paused:
        raise RuntimeError("Schedule pause did not verify in the active workflow")
    report.update({"versionId": after.get("versionId"), "activeVersionId": after.get("activeVersionId"), "active": after.get("active"), "nodeCount": len(after.get("nodes", [])), "scheduleDisabled": paused})
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
