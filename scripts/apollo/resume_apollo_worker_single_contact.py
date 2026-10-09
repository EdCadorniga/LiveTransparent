"""Resume the Apollo schedule conservatively for a one-contact first run.

Default mode is dry-run. Passing --apply enables the existing 5-minute
Schedule Trigger with maxPerRun=1 and adds only sanitized Apollo HTTP status
metadata to future per-contact error results. No execution is started here.
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
EXPECTED_VERSION = "9c8c63ab-588d-4519-925f-72469781d05c"
SCHEDULE_NAME = "Schedule Trigger - Apollo Rate-Limited Batch"
CONFIG_NAME = "Config"
WORKER_NAME = "Enrich Contacts via Apollo"
OLD_CATCH = '''  } catch (e) { errors++; results.push({ contact_id: cid, status: "apollo_error" }); if (statusFid) await ghl("PUT", "/contacts/" + cid, { customFields: [{ id: statusFid, value: "error" }] }); continue; }
'''
NEW_CATCH = '''  } catch (e) {
    errors++;
    var httpStatus = Number(e?.statusCode || e?.response?.statusCode || e?.httpCode || 0) || null;
    var responseBody = e?.response?.body;
    var errorCode = responseBody && typeof responseBody === "object" && typeof responseBody.error_code === "string" ? responseBody.error_code : null;
    results.push({ contact_id: cid, status: "apollo_error", http_status: httpStatus, error_code: errorCode });
    if (statusFid) await ghl("PUT", "/contacts/" + cid, { customFields: [{ id: statusFid, value: "error" }] });
    continue;
  }
'''


def load_key() -> str:
    key = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not key:
        raise RuntimeError("n8n-lt API credential unavailable")
    return str(key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Resume the live schedule at one contact/run")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"X-N8N-API-KEY": load_key(), "Content-Type": "application/json"})

    health = session.get(f"{BASE}/healthz/readiness", timeout=20)
    if health.status_code != 200:
        raise RuntimeError("n8n-lt readiness failed")
    response = session.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    response.raise_for_status()
    workflow = response.json()
    if workflow.get("versionId") != EXPECTED_VERSION or workflow.get("activeVersionId") != EXPECTED_VERSION:
        raise RuntimeError("Live Apollo workflow version drifted; inspect before resuming")
    if not workflow.get("active") or workflow.get("isArchived"):
        raise RuntimeError("Apollo poller is not active/non-archived")

    pending = {}
    for state in ("new", "running", "waiting"):
        r = session.get(f"{BASE}/api/v1/executions", params={"workflowId": WORKFLOW_ID, "status": state, "limit": 100, "includeData": "false"}, timeout=30)
        r.raise_for_status()
        pending[state] = len(r.json().get("data", []))
    if any(pending.values()):
        raise RuntimeError(f"Worker has pending/active executions; refusing resume: {pending}")

    nodes = [dict(n) for n in workflow.get("nodes", [])]
    schedule = next((n for n in nodes if n.get("name") == SCHEDULE_NAME), None)
    config = next((n for n in nodes if n.get("name") == CONFIG_NAME), None)
    worker = next((n for n in nodes if n.get("name") == WORKER_NAME), None)
    if not schedule or not config or not worker or schedule.get("disabled") is not True:
        raise RuntimeError("Expected paused schedule graph was not found")

    interval = schedule.get("parameters", {}).get("rule", {}).get("interval", [])
    if not interval or interval[0].get("minutesInterval") != 5:
        raise RuntimeError("Expected 5-minute schedule is not configured")
    assignments = config.get("parameters", {}).get("assignments", {}).get("assignments", [])
    cap = next((a for a in assignments if a.get("name") == "maxPerRun"), None)
    if not cap or cap.get("type") != "number" or int(cap.get("value", 0)) != 10:
        raise RuntimeError("Expected numeric maxPerRun=10 was not found")

    code = worker.get("parameters", {}).get("jsCode", "")
    if code.count(OLD_CATCH) != 1:
        raise RuntimeError("Expected Apollo catch block was not found exactly once")
    if code.count('url: apolloBase + "/v1/people/match"') != 1 or "reveal_phone_number: true" not in code:
        raise RuntimeError("Expected consolidated Apollo request pattern was not found")
    worker["parameters"]["jsCode"] = code.replace(OLD_CATCH, NEW_CATCH, 1)
    cap["value"] = 1
    schedule["disabled"] = False

    allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy"}
    payload = {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": workflow.get("connections", {}),
        "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in allowed},
    }
    report = {
        "workflowId": WORKFLOW_ID,
        "beforeVersionId": workflow.get("versionId"),
        "webhookAckPathRetained": True,
        "scheduleEveryMinutes": 5,
        "beforeMaxPerRun": 10,
        "afterMaxPerRun": 1,
        "addsOnlyHttpStatusAndErrorCodeToApolloErrors": True,
        "pendingBefore": pending,
        "writeRequested": args.apply,
    }
    if not args.apply:
        print(json.dumps(report, indent=2))
        return 0

    put = session.put(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", json=payload, timeout=60)
    if put.status_code not in (200, 201):
        raise RuntimeError(f"n8n-lt update failed: HTTP {put.status_code}")
    verify = session.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    verify.raise_for_status()
    saved = verify.json()
    saved_nodes = saved.get("nodes", [])
    saved_schedule = next(n for n in saved_nodes if n.get("name") == SCHEDULE_NAME)
    saved_config = next(n for n in saved_nodes if n.get("name") == CONFIG_NAME)
    saved_worker = next(n for n in saved_nodes if n.get("name") == WORKER_NAME)
    saved_cap = next(a.get("value") for a in saved_config["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun")
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId") != saved.get("activeVersionId"):
        raise RuntimeError("Resumed workflow did not verify active/published")
    if saved_schedule.get("disabled") is True or saved_cap != 1 or NEW_CATCH not in saved_worker["parameters"]["jsCode"]:
        raise RuntimeError("Resumed one-contact configuration did not verify")
    report.update({
        "afterVersionId": saved.get("versionId"),
        "afterActiveVersionId": saved.get("activeVersionId"),
        "afterActive": saved.get("active"),
        "afterArchived": saved.get("isArchived"),
        "nodeCount": len(saved_nodes),
        "scheduleEnabled": True,
        "verifiedMaxPerRun": saved_cap,
        "manualExecutionStarted": False,
    })
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
