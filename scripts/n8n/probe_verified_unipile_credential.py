"""Read only: exercise the replacement Unipile credential inside n8n-lt."""
from __future__ import annotations

import json
import secrets
import urllib.request

from wire_sales_navigator_v2_workflows import api

PATH = "lt-salesnav-credential-probe-" + secrets.token_hex(12)
NODES = [
    {
        "id": "probe-webhook",
        "name": "Read Only Probe",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2.1,
        "position": [0, 0],
        "parameters": {"httpMethod": "GET", "path": PATH, "responseMode": "responseNode", "options": {}},
    },
    {
        "id": "probe-http",
        "name": "Read Sales Navigator Inbox",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [250, 0],
        "parameters": {
            "method": "GET",
            "url": "https://api.unipile.com/v2/acc_01m3sefk22e8jvnmvvfx333pye/inboxes/SALES_NAVIGATOR_PRIMARY/chats?limit=1",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "httpHeaderAuth",
            "options": {"response": {"response": {
                "neverError": True, "responseFormat": "json", "fullResponse": True,
            }}},
        },
        "credentials": {"httpHeaderAuth": {
            "id": "calCid5lrBNnl78y",
            "name": "LT Sales Navigator Unipile V2 API (verified)",
        }},
    },
    {
        "id": "probe-code",
        "name": "Summarize Status",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [500, 0],
        "parameters": {
            "mode": "runOnceForAllItems",
            "jsCode": "const r=$input.first()?.json||{},b=r.body||r;return [{json:{providerStatus:Number(r.statusCode||0),hasChatList:Array.isArray(b.data)}}];",
        },
    },
    {
        "id": "probe-response",
        "name": "Respond",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.5,
        "position": [750, 0],
        "parameters": {"respondWith": "json", "responseBody": "={{ $json }}", "options": {}},
    },
]
CONNECTIONS = {
    "Read Only Probe": {"main": [[{"node": "Read Sales Navigator Inbox", "type": "main", "index": 0}]]},
    "Read Sales Navigator Inbox": {"main": [[{"node": "Summarize Status", "type": "main", "index": 0}]]},
    "Summarize Status": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
}
workflow_id = None
try:
    created = api("/workflows", "POST", {
        "name": "LT - Temporary Sales Navigator Credential Probe",
        "nodes": NODES,
        "connections": CONNECTIONS,
        "settings": {
            "saveDataErrorExecution": "none",
            "saveDataSuccessExecution": "none",
            "saveManualExecutions": False,
            "saveExecutionProgress": False,
        },
    })
    workflow_id = created["id"]
    api(f"/workflows/{workflow_id}/activate", "POST", {})
    with urllib.request.urlopen(
        "https://automations.livetransparent.com/webhook/" + PATH,
        timeout=30,
    ) as response:
        result = json.load(response)
    print(json.dumps({"providerStatus": result.get("providerStatus"), "hasChatList": result.get("hasChatList")}))
    if result.get("providerStatus") != 200 or result.get("hasChatList") is not True:
        raise SystemExit(1)
finally:
    if workflow_id:
        try:
            api(f"/workflows/{workflow_id}/deactivate", "POST", {})
            api(f"/workflows/{workflow_id}", "DELETE")
        except Exception:
            print(json.dumps({"temporaryWorkflowId": workflow_id, "cleanupNeeded": True}))
