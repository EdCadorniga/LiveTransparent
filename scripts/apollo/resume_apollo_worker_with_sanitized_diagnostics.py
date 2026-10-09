"""Resume one-contact Apollo diagnostics without launching a manual batch.

Default mode is dry-run. Passing --apply adds sanitized Apollo HTTP error
metadata to the worker output and enables its existing schedule at maxPerRun=1.
The next scheduled run is the only test; this script never calls Apollo.
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
EXPECTED_VERSION = "7cdef5ce-c3be-4cff-95fd-e8b17f594538"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"
CONFIG_NAME = "Config"
WORKER_NAME = "Enrich Contacts via Apollo"
OLD_RESULT = 'results.push({ contact_id: cid, status: "apollo_error", http_status: httpStatus, error_code: errorCode });'
NEW_RESULT = '''var safeErrorMessage = String(e?.message || e?.name || "Request failed").slice(0, 250)
      .replace(/https?:\\/\\/[^\\s)]+/gi, "[URL]")
      .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}/gi, "[EMAIL]")
      .replace(/(x-api-key|api[_-]?key|webhookkey)(\\s*[:=]\\s*)[^\\s&]+/gi, "$1=[REDACTED]");
    if (!httpStatus) {
      var statusMatch = safeErrorMessage.match(/status code[^0-9]*(\\d{3})/i);
      if (statusMatch) httpStatus = Number(statusMatch[1]);
    }
    results.push({ contact_id: cid, status: "apollo_error", http_status: httpStatus, error_code: errorCode, error_message: safeErrorMessage });'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Enable the diagnostic 1-contact schedule")
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
        raise RuntimeError("Apollo workflow version drifted; inspect before diagnostic resume")
    if not w.get("active") or w.get("isArchived"):
        raise RuntimeError("Apollo poller is not active/non-archived")

    pending = {}
    for state in ("new", "running", "waiting"):
        e = s.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=25)
        e.raise_for_status()
        pending[state] = len(e.json().get("data", []))
    if any(pending.values()):
        raise RuntimeError(f"Worker has pending/active executions; refusing diagnostic resume: {pending}")

    nodes = [dict(n) for n in w.get("nodes", [])]
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    if not schedule or schedule.get("disabled") is not True or not config or not worker:
        raise RuntimeError("Expected paused schedule graph not found")
    code = worker.get("parameters", {}).get("jsCode", "")
    if code.count(OLD_RESULT) != 1 or code.count('url: apolloBase + "/v1/people/match"') != 1:
        raise RuntimeError("Expected single-call Apollo error handling was not found")
    worker["parameters"]["jsCode"] = code.replace(OLD_RESULT, NEW_RESULT, 1)

    assignments = config.get("parameters", {}).get("assignments", {}).get("assignments", [])
    cap = next((a for a in assignments if a.get("name") == "maxPerRun"), None)
    if cap is None or int(cap.get("value", 0)) != 1:
        raise RuntimeError("Expected maxPerRun=1 diagnostic cap not found")
    schedule["disabled"] = False

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {"name": w["name"], "nodes": nodes, "connections": w.get("connections", {}), "settings": {k:v for k,v in (w.get("settings") or {}).items() if k in allowed}}
    report = {"workflowId": WORKFLOW_ID, "beforeVersionId": w.get("versionId"), "scheduleMinutes": 5, "maxPerRun": 1, "errorFields": ["http_status", "error_code", "sanitized error_message"], "pendingBefore": pending, "writeRequested": args.apply}
    if not args.apply:
        print(json.dumps(report, indent=2))
        return 0

    put = s.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if put.status_code not in (200, 201):
        raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    check = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    check.raise_for_status()
    saved = check.json(); saved_nodes = saved.get("nodes", [])
    saved_schedule = next(n for n in saved_nodes if n.get("name") == SCHEDULE_NAME)
    saved_config = next(n for n in saved_nodes if n.get("name") == CONFIG_NAME)
    saved_worker = next(n for n in saved_nodes if n.get("name") == WORKER_NAME)
    saved_cap = next(a.get("value") for a in saved_config["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun")
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId") != saved.get("activeVersionId") or saved_schedule.get("disabled") is True or saved_cap != 1 or NEW_RESULT not in saved_worker["parameters"]["jsCode"]:
        raise RuntimeError("Post-update schedule/diagnostic state did not verify")
    report.update({"afterVersionId": saved.get("versionId"), "afterActiveVersionId": saved.get("activeVersionId"), "active": saved.get("active"), "scheduleEnabled": True, "nodeCount": len(saved_nodes), "manualExecutionStarted": False})
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
