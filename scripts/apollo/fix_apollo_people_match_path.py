"""Correct the Apollo People Enrichment API base path in n8n-lt.

Default mode is dry-run. Pass --apply to update/publish the current one-contact
diagnostic worker. This script does not execute the workflow or call Apollo.
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
EXPECTED_VERSION = "6b5f50f4-867c-4d72-a634-476d3bda3eb0"
WORKER_NAME = "Enrich Contacts via Apollo"
OLD = 'var phoneRevealUrl = apolloBase + "/v1/people/match?reveal_phone_number=true&reveal_personal_emails=false&webhook_url=" + encodeURIComponent(webhookUrl);'
NEW = 'var phoneRevealUrl = apolloBase + "/api/v1/people/match?reveal_phone_number=true&reveal_personal_emails=false&webhook_url=" + encodeURIComponent(webhookUrl);'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply/publish the API path correction")
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
        raise RuntimeError("Live poller version/state drifted; inspect before changing API path")

    for state in ("new", "running", "waiting"):
        q = s.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=25)
        q.raise_for_status()
        if q.json().get("data"):
            raise RuntimeError(f"Worker has {state} executions; refusing API path change")

    nodes = [dict(n) for n in w.get("nodes", [])]
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    if worker is None:
        raise RuntimeError("Apollo worker Code node not found")
    code = worker.get("parameters", {}).get("jsCode", "")
    if code.count(OLD) != 1:
        raise RuntimeError("Expected one legacy Apollo API path not found")
    worker["parameters"]["jsCode"] = code.replace(OLD, NEW, 1)

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {"name": w["name"], "nodes": nodes, "connections": w.get("connections", {}), "settings": {k:v for k,v in (w.get("settings") or {}).items() if k in allowed}}
    report = {"workflowId": WORKFLOW_ID, "beforeVersionId": w.get("versionId"), "schedulePaused": next(n for n in nodes if n.get("name") == "Schedule Trigger - Apollo Rate-Limited Batch").get("disabled", False), "maxPerRun": next(a.get("value") for a in next(n for n in nodes if n.get("name") == "Config")["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun"), "apiPath": "/api/v1/people/match", "writeRequested": args.apply}
    if not args.apply:
        print(json.dumps(report, indent=2)); return 0

    put = s.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if put.status_code not in (200, 201): raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    check = s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30); check.raise_for_status(); saved=check.json()
    saved_code=next(n["parameters"]["jsCode"] for n in saved["nodes"] if n.get("name")==WORKER_NAME)
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId")!=saved.get("activeVersionId") or NEW not in saved_code:
        raise RuntimeError("Post-update API path verification failed")
    report.update({"afterVersionId":saved.get("versionId"),"afterActiveVersionId":saved.get("activeVersionId"),"active":saved.get("active"),"nodeCount":len(saved.get("nodes",[])),"manualExecutionStarted":False})
    print(json.dumps(report,indent=2));return 0


if __name__ == "__main__":
    raise SystemExit(main())
