"""Harden the booking-click intake: capture legacy booking-link UTMs too.

Updates the active n8n-lt workflow through the official n8n-lt REST API. The
Postgres password is moved from Code into a workflow Config node; no key is
printed or written to the repository.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW_ID = "1diZyFmTqWQUEny3"
N8N_HOST = "https://automations.livetransparent.com"


def read_env():
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = read_env()
n8n_key = env.get("N8N_LT_API_KEY")
pg_password = env.get("POSTGRES_PASSWORD")
if not n8n_key or not pg_password:
    raise SystemExit("Required n8n-lt/Postgres key unavailable")


def api(path, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(N8N_HOST + path, data=data, method=method, headers={"X-N8N-API-KEY": n8n_key, "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as response:
            text = response.read().decode()
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"n8n API HTTP {exc.code}: {exc.read().decode(errors='replace')[:500]}") from exc


workflow = api(f"/api/v1/workflows/{WORKFLOW_ID}")[1]
backup_dir = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "Temp" / "booking_click_workflow_backups"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / f"{WORKFLOW_ID}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json").write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")

code_node = next(node for node in workflow["nodes"] if node.get("name") == "Process Click")
code = code_node["parameters"]["jsCode"]
config_line = re.compile(r"const cfg = \{ host:'postgres', port:5432, database:'postgres', user:'postgres', password:.*? \};")
if not config_line.search(code):
    if "$('Config').first().json.pgPassword" not in code:
        raise SystemExit("Expected DB config literal not found; no update performed")
else:
    code = config_line.sub("const cfgValues = $('Config').first().json;\nconst cfg = { host:'postgres', port:5432, database:'postgres', user:'postgres', password:cfgValues.pgPassword };", code, count=1)

legacy_anchor = " 'DYoKxOSoet48F4GHzPBE': ['Peptides','peptidesequence','peptides_brands_oct_2026']\n};"
legacy_replacement = " 'DYoKxOSoet48F4GHzPBE': ['Peptides','peptidesequence','peptides_brands_oct_2026','email','booking'],\n 'quqSUM8bckKaOIktVvgU': ['Cannabis Brands','email','wl_seq_cannabis_ads','outreach','book_meeting'],\n 'nqLFBlEsdm7qccr8Yyog': ['Cannabis Brands','email','johnCannabis','outreach','book_meeting_john']\n};"
if legacy_anchor in code:
    code = code.replace(legacy_anchor, legacy_replacement, 1)
elif "'quqSUM8bckKaOIktVvgU'" not in code or "'nqLFBlEsdm7qccr8Yyog'" not in code:
    raise SystemExit("Booking-link map anchor changed; no update performed")

old_insert = "[contactId, linkId, linkName, m[0], m[1], m[2], 'email', ip, ua]"
new_insert = "[contactId, linkId, linkName, m[0], m[1], m[2], m[3] || 'email', ip, ua]"
if old_insert in code:
    code = code.replace(old_insert, new_insert, 1)
elif new_insert not in code:
    raise SystemExit("Booking-click insert mapping anchor changed; no update performed")
old_out = "out.push({ json: { ok: true, vertical: m[0], contact_id: contactId } });"
new_out = "out.push({ json: { ok: true, vertical: m[0], contact_id: contactId, utm_source: m[1], utm_campaign: m[2], utm_medium: m[3] || 'email', utm_content: m[4] || 'booking' } });"
if old_out in code:
    code = code.replace(old_out, new_out, 1)
elif new_out not in code:
    raise SystemExit("Booking-click result anchor changed; no update performed")
code_node["parameters"]["jsCode"] = code

config_node = next((node for node in workflow["nodes"] if node.get("name") == "Config"), None)
if not config_node:
    config_node = {
        "id": "booking-click-config-postgres",
        "name": "Config",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [460, 300],
        "parameters": {"mode": "manual", "includeOtherFields": True, "assignments": {"assignments": [{"id": "booking-click-postgres-password", "name": "pgPassword", "value": pg_password, "type": "string"}]}},
    }
    workflow["nodes"].append(config_node)

if not any(node.get("name") == "Has Mapped UTM?" for node in workflow["nodes"]):
    workflow["nodes"].append({
        "id": "booking-click-has-utm",
        "name": "Has Mapped UTM?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.3,
        "position": [760, 300],
        "parameters": {"conditions": {"combinator": "and", "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"leftValue": "={{ String(!!$json.utm_source) }}", "rightValue": "true", "operator": {"type": "string", "operation": "equals"}}]}, "options": {}},
    })
if not any(node.get("name") == "Update Contact Last UTM Fields" for node in workflow["nodes"]):
    workflow["nodes"].append({
        "id": "booking-click-update-contact-utms",
        "name": "Update Contact Last UTM Fields",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.4,
        "position": [1010, 220],
        "credentials": {"httpBearerAuth": {"id": "LIgX7IrOQoG1BusR", "name": "GHL API - Intake Poller"}},
        "parameters": {
            "method": "PUT",
            "url": "={{ 'https://services.leadconnectorhq.com/contacts/' + encodeURIComponent($json.contact_id) }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpBearerAuth",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Version", "value": "2021-07-28"}, {"name": "Content-Type", "value": "application/json"}, {"name": "Accept", "value": "application/json"}]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ { customFields: [{ id: 'p0X1vD2jDj5AZjXJ6Bcg', field_value: $json.utm_source }, { id: 'WsfJa98NxTuXV9lKIL05', field_value: $json.utm_medium }, { id: 'IUQRaxhOZQT8tiPZKL1z', field_value: $json.utm_campaign }, { id: '9wRews3knMzLhAtqvQog', field_value: $json.utm_content }] } }}",
            "options": {},
        },
    })

connections = workflow["connections"]
connections["Webhook"] = {"main": [[{"node": "Config", "type": "main", "index": 0}]]}
connections["Config"] = {"main": [[{"node": "Process Click", "type": "main", "index": 0}]]}
connections["Process Click"] = {"main": [[{"node": "Has Mapped UTM?", "type": "main", "index": 0}]]}
connections["Has Mapped UTM?"] = {"main": [[{"node": "Update Contact Last UTM Fields", "type": "main", "index": 0}], [{"node": "Respond", "type": "main", "index": 0}]]}
connections["Update Contact Last UTM Fields"] = {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
workflow["connections"] = connections

api(f"/api/v1/workflows/{WORKFLOW_ID}/deactivate", "POST")
settings = dict(workflow.get("settings") or {})
settings.pop("availableInMCP", None)
api(f"/api/v1/workflows/{WORKFLOW_ID}", "PUT", {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow["connections"], "settings": settings})
api(f"/api/v1/workflows/{WORKFLOW_ID}/activate", "POST")
_, verified = api(f"/api/v1/workflows/{WORKFLOW_ID}")
updated_code = next(node["parameters"]["jsCode"] for node in verified["nodes"] if node.get("name") == "Process Click")
if verified.get("versionId") != verified.get("activeVersionId") or "quqSUM8bckKaOIktVvgU" not in updated_code or "nqLFBlEsdm7qccr8Yyog" not in updated_code or "password:cfgValues.pgPassword" not in updated_code or not any(node.get("name") == "Update Contact Last UTM Fields" for node in verified["nodes"]):
    raise SystemExit("Booking click workflow verification failed")
print(json.dumps({"workflowId": WORKFLOW_ID, "name": verified.get("name"), "active": verified.get("active"), "versionId": verified.get("versionId"), "activeVersionId": verified.get("activeVersionId"), "legacyBookingLinksMapped": 2, "updatesLastTouchFieldsOnly": True, "postgresPasswordMovedToConfig": True}, indent=2))
