"""Add sanitized Apollo response diagnostics for the one-contact worker run.

Default is dry-run. Pass --apply to update/publish the active n8n-lt poller.
The script does not execute the worker or call Apollo.
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
EXPECTED_VERSION = "87e57ba1-6690-40e3-a2cf-df0489d34de9"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"
CONFIG_NAME = "Config"
WORKER_NAME = "Enrich Contacts via Apollo"
OLD_BLOCK = '''    var responseBody = e?.response?.body;
    var errorCode = responseBody && typeof responseBody === "object" && typeof responseBody.error_code === "string" ? responseBody.error_code : null;
    var safeErrorMessage = String(e?.message || e?.name || "Request failed").slice(0, 250)'''
NEW_BLOCK = '''    var rawResponseBody = e?.response?.body ?? e?.response?.data ?? e?.body;
    var responseBody = rawResponseBody;
    if (typeof responseBody === "string") { try { responseBody = JSON.parse(responseBody); } catch {} }
    var errorCode = responseBody && typeof responseBody === "object" ? (responseBody.error_code || responseBody.code || null) : null;
    var bodyMessage = responseBody && typeof responseBody === "object" ? (responseBody.message || responseBody.error_message || responseBody.error_description || "") : String(rawResponseBody || "");
    var safeErrorMessage = (String(e?.message || e?.name || "Request failed") + (bodyMessage ? " | " + String(bodyMessage) : "")).slice(0, 500)'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply the sanitized error-diagnostic change")
    args = parser.parse_args()
    key = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not key:
        raise RuntimeError("n8n-lt API credential unavailable")
    s = requests.Session()
    s.headers.update({"X-N8N-API-KEY": str(key), "Content-Type": "application/json"})
    if s.get(f"{BASE}/healthz/readiness", timeout=20).status_code != 200:
        raise RuntimeError("n8n-lt readiness failed")
    r = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    r.raise_for_status(); w = r.json()
    if w.get("versionId") != EXPECTED_VERSION or w.get("activeVersionId") != EXPECTED_VERSION or not w.get("active"):
        raise RuntimeError("Live Apollo workflow version/state drifted")
    for state in ("new", "running", "waiting"):
        q = s.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=25)
        q.raise_for_status()
        if q.json().get("data"):
            raise RuntimeError(f"Worker has {state} executions; refusing diagnostic update")

    nodes = [dict(n) for n in w.get("nodes", [])]
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    if not schedule or schedule.get("disabled") is True or not config or not worker:
        raise RuntimeError("Expected active one-contact schedule graph was not found")
    cap = next((a.get("value") for a in config["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun"), None)
    if cap != 1:
        raise RuntimeError("Diagnostic worker cap is not one contact/run")
    code = worker["parameters"]["jsCode"]
    if code.count(OLD_BLOCK) != 1:
        raise RuntimeError("Expected current sanitized error block not found")
    worker["parameters"]["jsCode"] = code.replace(OLD_BLOCK, NEW_BLOCK, 1)

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {"name": w["name"], "nodes": nodes, "connections": w.get("connections", {}), "settings": {k:v for k,v in (w.get("settings") or {}).items() if k in allowed}}
    report = {"workflowId": WORKFLOW_ID, "beforeVersionId": w.get("versionId"), "scheduleMinutes": schedule["parameters"]["rule"]["interval"][0].get("minutesInterval"), "maxPerRun": cap, "diagnostics": "HTTP status/code and redacted response message only", "manualExecutionStarted": False, "writeRequested": args.apply}
    if not args.apply:
        print(json.dumps(report, indent=2)); return 0

    put = s.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if put.status_code not in (200, 201): raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    check = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30); check.raise_for_status(); saved=check.json()
    saved_code=next(n["parameters"]["jsCode"] for n in saved["nodes"] if n.get("name")==WORKER_NAME)
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId")!=saved.get("activeVersionId") or NEW_BLOCK not in saved_code:
        raise RuntimeError("Post-update diagnostics did not verify")
    report.update({"afterVersionId":saved.get("versionId"),"afterActiveVersionId":saved.get("activeVersionId"),"active":saved.get("active"),"nodeCount":len(saved.get("nodes",[]))})
    print(json.dumps(report,indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
