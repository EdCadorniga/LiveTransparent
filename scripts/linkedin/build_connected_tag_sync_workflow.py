"""Build + deploy `LT - LinkedIn Connected Tag Sync` to n8n-lt.

Durable companion to the 2026-10-02 one-time backfill: a daily, idempotent,
read-mostly job that ensures every GHL contact corresponding to a
`connected`/`completed` LinkedIn state row carries `linkedin_connected`
(main) or `partner_linkedin_connected` (partnership).

Resolution mirrors the backfill tool:
  - state rows with a real GHL contact id, and
  - synthetic `linkedin:relation:<slug>` rows resolved through
    `linkedin_contact_profile_index`.

It only writes when the tag is missing (GET then conditional POST), so steady
state is ~one GET per connected contact per day. No LinkedIn message is sent.

Usage:
  python build_connected_tag_sync_workflow.py            # build + activate
  python build_connected_tag_sync_workflow.py --update <id>
"""

import argparse
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
N8N_BASE = "https://automations.livetransparent.com"
WF_NAME = "LT - LinkedIn Connected Tag Sync"
JS_FILE = ROOT / "scripts" / "linkedin" / "connected_tag_sync.js"


def load_env():
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api(method, path, key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(N8N_BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": key, "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}")


def assignment(i, n, t, v):
    return {"id": i, "name": n, "type": t, "value": v}


def build_workflow(cron, dry_run):
    js_code = JS_FILE.read_text(encoding="utf-8")
    config = {
        "mode": "manual",
        "assignments": {"assignments": [
            assignment("workflowName", "workflowName", "string", WF_NAME),
            assignment("locationId", "locationId", "string", "Zwz4relUXVPxx8uohnjV"),
            assignment("ghlApiBaseUrl", "ghlApiBaseUrl", "string", "https://services.leadconnectorhq.com"),
            assignment("ghlApiKey", "ghlApiKey", "string", os.environ["GHL_PIT"]),
            assignment("mainTag", "mainTag", "string", "linkedin_connected"),
            assignment("partnerTag", "partnerTag", "string", "partner_linkedin_connected"),
            assignment("maxPerRun", "maxPerRun", "number", 800),
            assignment("delayMs", "delayMs", "number", 120),
            assignment("dryRun", "dryRun", "boolean", dry_run),
            assignment("pgHost", "pgHost", "string", "postgres"),
            assignment("pgPort", "pgPort", "number", 5432),
            assignment("pgDatabase", "pgDatabase", "string", "postgres"),
            assignment("pgUser", "pgUser", "string", "postgres"),
            assignment("pgPassword", "pgPassword", "string", os.environ["POSTGRES_PASSWORD"]),
        ]}
    }
    nodes = [
        {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": cron}]}},
         "id": "sync-sched-0001", "name": "Schedule Trigger", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [0, 0]},
        {"parameters": config, "id": "sync-cfg-0002", "name": "Config", "type": "n8n-nodes-base.set",
         "typeVersion": 3.4, "position": [224, 96]},
        {"parameters": {"jsCode": js_code}, "id": "sync-code-0003", "name": "Tag Connected Contacts",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [448, 96]},
        {"parameters": {"mode": "manual", "assignments": {"assignments": [
            assignment("ok", "ok", "boolean", "={{ $json.ok }}"),
            assignment("scanned", "scanned", "number", "={{ $json.scanned }}"),
            assignment("already_tagged", "already_tagged", "number", "={{ $json.already_tagged }}"),
            assignment("tagged", "tagged", "number", "={{ $json.tagged }}"),
            assignment("failed", "failed", "number", "={{ $json.failed }}"),
            assignment("not_found", "not_found", "number", "={{ $json.not_found }}"),
            assignment("errors", "errors", "number", "={{ $json.errors }}"),
            assignment("dry_run", "dry_run", "boolean", "={{ $json.dry_run }}"),
        ]}}, "id": "sync-res-0004", "name": "Result", "type": "n8n-nodes-base.set",
         "typeVersion": 3.4, "position": [672, 96]},
        {"parameters": {}, "id": "sync-man-0005", "name": "Manual Trigger",
         "type": "n8n-nodes-base.manualTrigger", "typeVersion": 1, "position": [0, 192]},
    ]
    conn = {"main": [[{"node": "Config", "type": "main", "index": 0}]]}
    conn_code = {"main": [[{"node": "Tag Connected Contacts", "type": "main", "index": 0}]]}
    conn_res = {"main": [[{"node": "Result", "type": "main", "index": 0}]]}
    connections = {
        "Schedule Trigger": conn,
        "Config": conn_code,
        "Tag Connected Contacts": conn_res,
        "Manual Trigger": conn,
    }
    return {
        "name": WF_NAME,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1", "timezone": "America/Los_Angeles",
                     "saveDataSuccessExecution": "all", "saveDataErrorExecution": "all"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", default=None, help="workflow id to update in place")
    ap.add_argument("--no-activate", action="store_true")
    ap.add_argument("--cron", default="0 4 * * *", help="schedule cron expression")
    ap.add_argument("--dry-run", action="store_true", help="set Config dryRun=true (no tag writes)")
    args = ap.parse_args()
    load_env()
    key = os.environ["N8N_LT_API_KEY"]
    body = build_workflow(args.cron, args.dry_run)
    if args.update:
        wf = api("PUT", f"/api/v1/workflows/{args.update}", key, body)
    else:
        wf = api("POST", "/api/v1/workflows", key, body)
    wid = wf.get("id")
    print(f"workflow id={wid} versionId={wf.get('versionId')} nodes={len(wf.get('nodes', []))}")
    if not args.no_activate:
        act = api("POST", f"/api/v1/workflows/{wid}/activate", key)
        print(f"activated={act.get('active')} activeVersionId={act.get('activeVersionId')}")


if __name__ == "__main__":
    main()
