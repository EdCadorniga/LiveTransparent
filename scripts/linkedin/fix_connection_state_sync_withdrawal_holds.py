"""Make the LinkedIn state sync honor the durable invitation-withdrawal hold."""
from __future__ import annotations

import copy
import json
import pathlib
import urllib.request
import uuid


ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = "https://automations.livetransparent.com"
WORKFLOW_ID = "ceaKnz6E3onQrZpt"
POSTGRES_CREDENTIAL_ID = "pgAzUqpwOiGkGXzO"
POSTGRES_CREDENTIAL_NAME = "Postgres account"
ACCOUNT_ID = "V9eiHiDpRmCtan0YNdzsQw"


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


ENV = read_env()
API_KEY = ENV.get("N8N_LT_API_KEY") or ENV.get("N8N_API_KEY_LT")
if not API_KEY:
    raise SystemExit("Missing n8n-lt API key in .env")


def api(method: str, path: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)


workflow = api("GET", f"/api/v1/workflows/{WORKFLOW_ID}")
if not workflow.get("active") or workflow.get("versionId") != workflow.get("activeVersionId"):
    raise SystemExit("Workflow must be active and published before applying this patch")

nodes = copy.deepcopy(workflow["nodes"])
connections = copy.deepcopy(workflow["connections"])
config = next(node for node in nodes if node["name"] == "Config")
sync = next(node for node in nodes if node["name"] == "Sync LinkedIn Connection State")
if any(node["name"] == "Read Invitation Withdrawal Holds" for node in nodes):
    raise SystemExit("Withdrawal-hold read node already exists; inspect before rerunning")

query = (
    "SELECT COALESCE(json_agg(json_build_object("
    "'ghl_contact_id', ghl_contact_id, "
    "'candidate_contact_ids', candidate_contact_ids, "
    "'invited_user_public_id', invited_user_public_id, "
    "'invited_user_provider_id', invited_user_provider_id)), '[]'::json) AS holds "
    "FROM linkedin_invitation_withdrawals "
    f"WHERE dispatcher_hold IS TRUE AND unipile_account_id = '{ACCOUNT_ID}';"
)
hold_node = {
    "id": str(uuid.uuid4()),
    "name": "Read Invitation Withdrawal Holds",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 2.6,
    "position": [config["position"][0] + 220, config["position"][1]],
    "parameters": {
        "resource": "database",
        "operation": "executeQuery",
        "query": query,
        "options": {},
    },
    "credentials": {
        "postgres": {"id": POSTGRES_CREDENTIAL_ID, "name": POSTGRES_CREDENTIAL_NAME}
    },
}

source = sync["parameters"]["jsCode"]
anchor = "const errors = [];\nlet apiCalls = 0;"
if source.count(anchor) != 1:
    raise SystemExit("Could not locate the expected sync-code initialization anchor")
source = source.replace(
    anchor,
    """const errors = [];
let heldRows = $input.first()?.json?.holds || [];
if (typeof heldRows === 'string') { try { heldRows = JSON.parse(heldRows); } catch { heldRows = []; } }
if (!Array.isArray(heldRows)) heldRows = [];
const heldContactIds = new Set();
const heldIdentifiers = new Set();
const heldProviderIds = new Set();
function addHeld(set, value) { const normalized = clean(value).toLowerCase(); if (normalized) set.add(normalized); }
for (const hold of heldRows) {
  addHeld(heldContactIds, hold.ghl_contact_id);
  addHeld(heldIdentifiers, hold.invited_user_public_id);
  addHeld(heldProviderIds, hold.invited_user_provider_id);
  let candidates = hold.candidate_contact_ids;
  if (typeof candidates === 'string') { try { candidates = JSON.parse(candidates); } catch {} }
  if (Array.isArray(candidates)) for (const id of candidates) addHeld(heldContactIds, id);
  else if (candidates && typeof candidates === 'object') for (const id of Object.keys(candidates)) addHeld(heldContactIds, id);
}
let heldSkipped = 0;
let apiCalls = 0;""",
    1,
)
anchor = """      const publicIdentifier = identifier(url);
      const profile = await resolveUnipileProfile.call(this, publicIdentifier);"""
if source.count(anchor) != 1:
    raise SystemExit("Could not locate the expected identity-resolution anchor")
source = source.replace(
    anchor,
    """      const publicIdentifier = identifier(url);
      if (heldContactIds.has(contactId.toLowerCase()) || heldIdentifiers.has(publicIdentifier.toLowerCase())) {
        heldSkipped += 1;
        continue;
      }
      const profile = await resolveUnipileProfile.call(this, publicIdentifier);
      if (profile?.provider_id && heldProviderIds.has(String(profile.provider_id).toLowerCase())) {
        heldSkipped += 1;
        continue;
      }""",
    1,
)
source = source.replace(
    "return [{ json: { ok: errors.length === 0, processed, synced, errors: errors.length, api_calls: apiCalls, deadline_reached: Date.now() >= deadline, error_sample: errors.slice(0, 10) } }];",
    "return [{ json: { ok: errors.length === 0, processed, synced, held_skipped: heldSkipped, errors: errors.length, api_calls: apiCalls, deadline_reached: Date.now() >= deadline, error_sample: errors.slice(0, 10) } }];",
    1,
)
if "held_skipped: heldSkipped" not in source:
    raise SystemExit("Could not update the sync result summary")
sync["parameters"]["jsCode"] = source

nodes.append(hold_node)
connections["Config"]["main"][0] = [
    {"node": hold_node["name"], "type": "main", "index": 0}
]
connections[hold_node["name"]] = {
    "main": [[{"node": sync["name"], "type": "main", "index": 0}]]
}

settings = copy.deepcopy(workflow.get("settings") or {})
settings.pop("availableInMCP", None)
payload = {
    "name": workflow["name"],
    "nodes": nodes,
    "connections": connections,
    "settings": settings,
}
saved = api("PUT", f"/api/v1/workflows/{WORKFLOW_ID}", payload)
verified = api("GET", f"/api/v1/workflows/{WORKFLOW_ID}")
if not verified.get("active") or verified.get("versionId") != verified.get("activeVersionId"):
    raise SystemExit("Saved workflow is not active with its latest version")
saved_sync = next(node for node in verified["nodes"] if node["name"] == sync["name"])
saved_hold_node = next(node for node in verified["nodes"] if node["name"] == hold_node["name"])
if "held_skipped: heldSkipped" not in saved_sync["parameters"]["jsCode"]:
    raise SystemExit("Saved sync code did not pass readback")
if saved_hold_node["parameters"]["query"] != query:
    raise SystemExit("Saved hold query did not pass readback")
print(json.dumps({
    "workflowId": WORKFLOW_ID,
    "active": verified.get("active"),
    "versionId": verified.get("versionId"),
    "activeVersionId": verified.get("activeVersionId"),
    "holdReadNodePresent": True,
    "syncReportsHeldSkips": True,
}))
