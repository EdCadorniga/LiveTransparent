"""Request Apollo profile match and async phone reveal in one call/contact.

Default is dry-run. Pass --apply to update/publish the current n8n-lt poller.
The scheduled 5-minute/10-contact cap is preserved; this script never starts
an execution or sends an Apollo request.
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
EXPECTED_VERSION = "d1b08e39-6152-427d-b409-a7429647b290"
WORKER = "Enrich Contacts via Apollo"
OLD_MATCH_BODY = (
    'body: { first_name: fn || void 0, last_name: ln || void 0, email: email || void 0, '
    'organization_name: co || void 0, linkedin_url: li || void 0 },'
)
NEW_MATCH_BODY = (
    'body: { first_name: fn || void 0, last_name: ln || void 0, email: email || void 0, '
    'organization_name: co || void 0, linkedin_url: li || void 0, '
    'reveal_phone_number: true, reveal_personal_emails: false, '
    'webhook_url: callbackUrl + "?contactId=" + encodeURIComponent(cid) + "&webhookKey=" + webhookKey },'
)
SECOND_REQUEST = '''  var revealRes = null;
  var revealErr = false;
  try {
    revealRes = await this.helpers.httpRequest({
      method: "POST", url: apolloBase + "/v1/people/match",
      headers: { "X-Api-Key": apolloKey, "Content-Type": "application/json", Accept: "application/json" },
      body: { id: person.id, reveal_phone_number: true, reveal_personal_emails: false, webhook_url: callbackUrl + "?contactId=" + encodeURIComponent(cid) + "&webhookKey=" + webhookKey },
      json: true
    });
  } catch (pe) { revealErr = true; }
  if (revealErr) apolloPhoneRequestFailed++;
'''
REPLACEMENT = '''  var revealRes = aRes;
  var revealErr = false;
'''


def load_key() -> str:
    value = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not value:
        raise RuntimeError("n8n-lt API credential unavailable")
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply/publish this n8n-lt change")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"X-N8N-API-KEY": load_key(), "Content-Type": "application/json"})

    health = session.get(f"{BASE}/healthz/readiness", timeout=20)
    if health.status_code != 200:
        raise RuntimeError(f"n8n-lt readiness failed: HTTP {health.status_code}")
    response = session.get(f"{BASE}/api/v1/workflows/{WORKFLOW_ID}", timeout=30)
    response.raise_for_status()
    workflow = response.json()
    if workflow.get("versionId") != EXPECTED_VERSION or workflow.get("activeVersionId") != EXPECTED_VERSION:
        raise RuntimeError("Live poller version drifted; inspect before changing the Code node")
    if not workflow.get("active") or workflow.get("isArchived"):
        raise RuntimeError("Apollo poller is not active/non-archived")

    pending = {}
    for status in ("new", "running", "waiting"):
        r = session.get(
            f"{BASE}/api/v1/executions",
            params={"workflowId": WORKFLOW_ID, "status": status, "limit": 100, "includeData": "false"},
            timeout=30,
        )
        r.raise_for_status()
        pending[status] = len(r.json().get("data", []))
    if any(pending.values()):
        raise RuntimeError(f"Worker has pending/active executions; refusing Code update: {pending}")

    nodes = [dict(n) for n in workflow.get("nodes", [])]
    node = next((n for n in nodes if n.get("name") == WORKER), None)
    if not node:
        raise RuntimeError("Apollo Code node not found")
    code = node.get("parameters", {}).get("jsCode", "")
    if code.count(OLD_MATCH_BODY) != 1 or code.count(SECOND_REQUEST) != 1:
        raise RuntimeError("Expected two-call code pattern was not found exactly once; refusing patch")

    updated_code = code.replace(OLD_MATCH_BODY, NEW_MATCH_BODY, 1).replace(SECOND_REQUEST, REPLACEMENT, 1)
    if updated_code.count('url: apolloBase + "/v1/people/match"') != 1:
        raise RuntimeError("Expected exactly one Apollo people/match request after consolidation")
    node["parameters"]["jsCode"] = updated_code

    allowed_settings = {
        "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
        "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy",
    }
    payload = {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": workflow.get("connections", {}),
        "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in allowed_settings},
    }
    report = {
        "workflowId": WORKFLOW_ID,
        "beforeVersionId": workflow.get("versionId"),
        "active": workflow.get("active"),
        "nodeCount": len(nodes),
        "scheduleMinutes": next(n for n in nodes if n.get("type") == "n8n-nodes-base.scheduleTrigger")["parameters"]["rule"]["interval"][0].get("minutesInterval"),
        "maxPerRun": next(a.get("value") for a in next(n for n in nodes if n.get("name") == "Config")["parameters"]["assignments"]["assignments"] if a.get("name") == "maxPerRun"),
        "apolloMatchCallsPerContact": 1,
        "phoneReveal": "same people/match request, asynchronous webhook result mapped by GHL Contact ID",
        "pendingExecutionsBefore": pending,
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
    saved_code = next(n["parameters"]["jsCode"] for n in saved.get("nodes", []) if n.get("name") == WORKER)
    if not saved.get("active") or saved.get("isArchived") or saved.get("versionId") != saved.get("activeVersionId"):
        raise RuntimeError("Updated poller did not verify active with matching versions")
    if saved_code.count('url: apolloBase + "/v1/people/match"') != 1 or "reveal_phone_number: true" not in saved_code:
        raise RuntimeError("Single-request phone reveal did not verify in saved Code node")
    report.update({
        "afterVersionId": saved.get("versionId"),
        "afterActiveVersionId": saved.get("activeVersionId"),
        "afterNodeCount": len(saved.get("nodes", [])),
        "afterActive": saved.get("active"),
        "verifiedSingleApolloCall": True,
        "manualExecutionStarted": False,
    })
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
