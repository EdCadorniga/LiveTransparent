"""Build the Apollo phone-reveal URL without relying on the URL global.

Default mode is dry-run. Pass --apply to update/publish the current n8n-lt
poller. This keeps the one-contact diagnostic cap and 5-minute schedule.
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
EXPECTED_VERSION = "cf1b7ff9-dd89-4065-b707-225e70e9966f"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"
CONFIG_NAME = "Config"
WORKER_NAME = "Enrich Contacts via Apollo"
OLD_URL = 'method: "POST", url: phoneRevealUrl.toString(),'
NEW_URL = 'method: "POST", url: phoneRevealUrl,'
OLD_SETUP = '''    var phoneRevealUrl = new URL(apolloBase + "/v1/people/match");
    phoneRevealUrl.searchParams.set("reveal_phone_number", "true");
    phoneRevealUrl.searchParams.set("reveal_personal_emails", "false");
    phoneRevealUrl.searchParams.set("webhook_url", callbackUrl + "?contactId=" + encodeURIComponent(cid) + "&webhookKey=" + webhookKey);'''
NEW_SETUP = '''    var webhookUrl = callbackUrl + "?contactId=" + encodeURIComponent(cid) + "&webhookKey=" + webhookKey;
    var phoneRevealUrl = apolloBase + "/v1/people/match?reveal_phone_number=true&reveal_personal_emails=false&webhook_url=" + encodeURIComponent(webhookUrl);'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply/publish the Apollo query parameter fix")
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
        raise RuntimeError("Live Apollo workflow version/state drifted; inspect before applying")
    for state in ("new", "running", "waiting"):
        q = s.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=25)
        q.raise_for_status()
        if q.json().get("data"):
            raise RuntimeError(f"Worker has {state} executions; refusing code update")

    nodes = [dict(n) for n in w.get("nodes", [])]
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    if not worker or not schedule or not config:
        raise RuntimeError("Expected paused/resume-diagnostic graph is incomplete")
    if schedule.get("disabled") is True:
        raise RuntimeError("Schedule is paused; this change expects the one-contact diagnostic schedule active")
    cap = next((a.get("value") for a in config["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun"), None)
    if cap != 1:
        raise RuntimeError("Expected maxPerRun=1 diagnostic cap")

    code = worker["parameters"]["jsCode"]
    if code.count(OLD_URL) != 1 or code.count(OLD_SETUP) != 1:
        raise RuntimeError("Expected URL-constructor phone-reveal code was not found exactly once")
    code = code.replace(OLD_SETUP, NEW_SETUP, 1).replace(OLD_URL, NEW_URL, 1)
    if code.count('url: phoneRevealUrl,') != 1 or "phoneRevealUrl.searchParams" in code or "new URL(apolloBase" in code:
        raise RuntimeError("Apollo query-parameter fix did not assemble correctly")
    worker["parameters"]["jsCode"] = code

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {"name":w["name"],"nodes":nodes,"connections":w.get("connections",{}),"settings":{k:v for k,v in (w.get("settings") or {}).items() if k in allowed}}
    report={"workflowId":WORKFLOW_ID,"beforeVersionId":w.get("versionId"),"scheduleMinutes":schedule["parameters"]["rule"]["interval"][0].get("minutesInterval"),"maxPerRun":cap,"phoneRevealParams":"URL query string","writeRequested":args.apply}
    if not args.apply:
        print(json.dumps(report,indent=2));return 0

    put=s.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}",json=payload,timeout=60)
    if put.status_code not in (200,201): raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    verify=s.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}",timeout=30);verify.raise_for_status();saved=verify.json()
    saved_code=next(n["parameters"]["jsCode"] for n in saved["nodes"] if n.get("name")==WORKER_NAME)
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId")!=saved.get("activeVersionId") or 'webhook_url=" + encodeURIComponent(webhookUrl)' not in saved_code or "new URL(apolloBase" in saved_code:
        raise RuntimeError("Post-update verification failed")
    report.update({"afterVersionId":saved.get("versionId"),"afterActiveVersionId":saved.get("activeVersionId"),"afterActive":saved.get("active"),"nodeCount":len(saved.get("nodes",[])),"scheduleEnabled":not next(n for n in saved["nodes"] if n.get("name")==SCHEDULE_NAME).get("disabled",False),"manualExecutionStarted":False})
    print(json.dumps(report,indent=2));return 0


if __name__ == "__main__":
    raise SystemExit(main())
