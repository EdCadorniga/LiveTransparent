#!/usr/bin/env python3
"""Fix the double-backslash `esc()` bug in LT - LinkedIn Connection State Upsert.

Workflow: LT - LinkedIn Connection State Upsert (Old7ZvyVYgFaJgDr, n8n-lt)

`Build Upsert SQL` escaped backslashes (`\\` -> `\\\\`) before embedding JSON
inside `'...'::jsonb`. The database runs with `standard_conforming_strings=on`,
so backslashes are literal and doubling them corrupts the JSON, producing
`invalid input syntax for type json` whenever a payload contains an embedded
quote/backslash (e.g. the malformed Unipile acceptance body). The documented
correct form escapes only single quotes.

This script replaces that one function body and re-publishes.
"""
import json
import os
import sys
import urllib.request

WORKFLOW_ID = "Old7ZvyVYgFaJgDr"
N8N_BASE = "https://automations.livetransparent.com"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_CANDIDATES = [
    os.path.join(REPO_ROOT, ".env"),
    r"C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\.env",
]

OLD_ESC = "return \"'\" + String(v).replace(/\\\\/g, '\\\\\\\\').replace(/'/g, \"''\") + \"'\";"
NEW_ESC = "return \"'\" + String(v).replace(/'/g, \"''\") + \"'\";"


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
if not TOKEN:
    sys.exit("Missing N8N_LT_API_KEY in .env")


def api(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-N8N-API-KEY", TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}


def main():
    live = api("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}")
    node = next(n for n in live["nodes"] if n["name"] == "Build Upsert SQL")
    code = node["parameters"]["jsCode"]
    if OLD_ESC not in code:
        print("esc() already fixed or pattern not found; aborting without change.")
        print("contains double-backslash:", ".replace(/\\\\/g" in code)
        return
    node["parameters"]["jsCode"] = code.replace(OLD_ESC, NEW_ESC)

    settings = dict(live.get("settings") or {})
    settings.pop("availableInMCP", None)
    payload = {
        "name": live["name"],
        "nodes": live["nodes"],
        "connections": live["connections"],
        "settings": settings,
    }
    result = api("PUT", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", payload)
    print("PUT ok:", result.get("id"), result.get("name"), "nodes:", len(result.get("nodes", [])))

    verify = api("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}")
    print("active:", verify.get("active"))
    print("versionId:", verify.get("versionId"))
    print("activeVersionId:", verify.get("activeVersionId"))
    print("MATCH:", verify.get("versionId") == verify.get("activeVersionId"))
    vnode = next(n for n in verify["nodes"] if n["name"] == "Build Upsert SQL")
    print("double-backslash remains:", ".replace(/\\\\/g" in vnode["parameters"]["jsCode"])


if __name__ == "__main__":
    main()