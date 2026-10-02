#!/usr/bin/env python3
"""Patch-deploy the LinkedIn Connection Acceptance Checker (Unipile).

Workflow: LT - LinkedIn Connection Acceptance Checker (Unipile)
ID:       3ttEvr5NMcQCS4Hp  (n8n-lt only)

2026-10-02 fix
--------------
Root cause 1 (parse): the webhook is subscribed to Unipile `message_received`,
and the form-encoded single-JSON-key body is frequently malformed (unescaped
`":"` inside `occupation`). `JSON.parse` threw, the catch was silent, every
identity field came back empty, and no state row matched.

Root cause 2 (signal): `message_received` also fires on outbound invite-note /
DM echoes (is_sender:true, attendee_specifics network_distance DISTANCE_2).
Unipile documents this as the real-time signal for note-bearing invitations,
but the acceptance must be confirmed with a relation lookup. We now call
`GET /users/{id}?account_id=...` and require `network_distance == FIRST_DEGREE`
or `is_relationship == true` before marking a contact connected.

Root cause 3 (duplicates): the match returned LIMIT 1, so only one of multiple
duplicate state rows/contacts would ever be tagged. The match now returns all
rows and the payload/accept steps iterate every match.

This script is intentionally patch-style: it fetches the live workflow and
preserves the Config node's existing GHL PIT + stateUpsertSecret (never stored
in the repo). The Unipile API key is read from `.env` (`UNIPILE_TOKEN`).
"""
import json
import os
import re
import sys
import urllib.request

WORKFLOW_ID = "3ttEvr5NMcQCS4Hp"
STATE_UPSERT_ID = "Old7ZvyVYgFaJgDr"
N8N_BASE = "https://automations.livetransparent.com"
NODE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acceptance_checker")
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_CANDIDATES = [
    os.path.join(REPO_ROOT, ".env"),
    r"C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\.env",
]


def load_env():
    env = {}
    for path in ENV_CANDIDATES:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if "=" in line and not line.lstrip().startswith("#"):
                    name, value = line.split("=", 1)
                    env[name.strip()] = value.strip().strip('"')
        break
    return env


ENV = load_env()
TOKEN = ENV.get("N8N_LT_API_KEY") or ENV.get("N8N_API_KEY_LT")
UNIPILE_KEY = ENV.get("UNIPILE_TOKEN", "").strip()
if not TOKEN:
    sys.exit("Missing N8N_LT_API_KEY in .env")
if not UNIPILE_KEY:
    sys.exit("Missing UNIPILE_TOKEN in .env")


def api(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-N8N-API-KEY", TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}


def read_js(name):
    with open(os.path.join(NODE_DIR, name), "r", encoding="utf-8") as fh:
        return fh.read().replace("\r\n", "\n").rstrip("\n")


def extract_value(code, key):
    match = re.search(key + r"""\s*:\s*['"]([^'"]*)['"]""", code)
    return match.group(1) if match else ""


def build_config_code(ghl_pit, state_secret):
    return (
        "const input = $input.first()?.json || {};\n"
        "return [{ json: {\n"
        "  ...input,\n"
        "  UNIPILE_ACCOUNT_ID: 'V9eiHiDpRmCtan0YNdzsQw',\n"
        "  UNIPILE_API_BASE_URL: 'https://api42.unipile.com:17256/api/v1',\n"
        "  UNIPILE_API_KEY: " + json.dumps(UNIPILE_KEY) + ",\n"
        "  GHL_API_KEY: " + json.dumps(ghl_pit) + ",\n"
        "  GHL_LOCATION_ID: 'Zwz4relUXVPxx8uohnjV',\n"
        "  GHL_API_BASE_URL: 'https://services.leadconnectorhq.com',\n"
        "  stateUpsertSecret: " + json.dumps(state_secret) + "\n"
        "} }];"
    )


RESPOND_BODY = (
    '={{ (() => { const rows = $("Build Acceptance Upsert Payload").all().map(i => i.json); '
    'const matched = rows.filter(r => r.matched === true); const first = rows[0] || {}; '
    'return { ok: true, matched: matched.length > 0, matched_count: matched.length, '
    'connected: first.connected === true, '
    'reason: first.reason || (matched.length ? null : "unmatched"), '
    'contacts: matched.map(r => ({ contact_id: r.ghl_contact_id, tag_ok: r.tag_ok, upsert_ok: r.upsert_ok, tag_error: r.tag_error || "" })), '
    'provider_id: first.provider_id || "", identifier: first.identifier || "", '
    'network_distance: first.network_distance || "", accepted_at: first.accepted_at || null }; })() }}'
)


def main():
    live = api("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}")
    nodes = live["nodes"]
    by_name = {n["name"]: n for n in nodes}

    ghl_pit = ENV.get("GHL_PIT", "").strip()
    upsert = api("GET", f"{N8N_BASE}/api/v1/workflows/{STATE_UPSERT_ID}")
    upsert_cfg = next(n for n in upsert["nodes"] if n["name"] == "Config")["parameters"]["jsCode"]
    state_secret = extract_value(upsert_cfg, "stateUpsertSecret")
    if not ghl_pit or not state_secret:
        sys.exit("Could not resolve GHL_PIT (from .env) or stateUpsertSecret (from state-upsert Config)")

    config_code = build_config_code(ghl_pit, state_secret)
    replacements = {
        "Config": ("jsCode", config_code),
        "Normalize LinkedIn Acceptance Event": ("jsCode", read_js("normalize.js")),
        "Build Find SQL": ("jsCode", read_js("build_find_sql.js")),
        "Build Acceptance Upsert Payload": ("jsCode", read_js("build_payload.js")),
        "Build Accept SQL": ("jsCode", read_js("build_accept_sql.js")),
        "Respond - Acceptance": ("responseBody", RESPOND_BODY),
    }
    for name, (key, value) in replacements.items():
        by_name[name]["parameters"][key] = value

    # Return all matches even when the relation check is negative / no rows.
    by_name["Find LinkedIn State Row"]["alwaysOutputData"] = True
    # Ensure the response node runs even when the activity-event no-op returns no rows.
    by_name["Record LinkedIn Acceptance Event"]["alwaysOutputData"] = True

    settings = dict(live.get("settings") or {})
    settings.pop("availableInMCP", None)

    payload = {
        "name": live["name"],
        "nodes": nodes,
        "connections": live["connections"],
        "settings": settings,
    }
    result = api("PUT", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", payload)
    print("PUT ok:", result.get("id"), result.get("name"))
    print("nodes:", len(result.get("nodes", [])))

    verify = api("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}")
    print("active:", verify.get("active"))
    print("versionId:", verify.get("versionId"))
    print("activeVersionId:", verify.get("activeVersionId"))
    print("MATCH:", verify.get("versionId") == verify.get("activeVersionId"))


if __name__ == "__main__":
    main()