"""Make LinkedIn inbound OAuth 401s queue for post-renewal replay."""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

BASE = "https://automations.livetransparent.com/api/v1"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"


def load_env():
    values = {}
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


cfg = load_env()
api_key = os.environ.get("N8N_API_KEY_LT") or cfg.get("N8N_API_KEY_LT")
if not api_key:
    raise RuntimeError("N8N_API_KEY_LT is required")


def api(path, method="GET", payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method=method,
        headers={"X-N8N-API-KEY": api_key, "Accept": "application/json", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


def allowed_settings(settings):
    names = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}
    return {k: v for k, v in (settings or {}).items() if k in names}


workflow = api(f"/workflows/{WORKFLOW_ID}")
node = next(n for n in workflow["nodes"] if n.get("name") == "Create LinkedIn Contact and Add Inbound Message")
code = node["parameters"]["jsCode"]
old = """  } catch (e) {
    // OAuth access tokens expire; use the bounded location PIT fallback only on 401.
    var exchangeError = describeError(e);
    var statusCode = e && (e.statusCode !== undefined ? e.statusCode : e.status);
    if (String(statusCode) === '401' || exchangeError.includes('401')) locToken = GHL_PIT;
    else return { ...base, status: 'error', reason: 'loc_tok_err: ' + exchangeError };
  }
"""
new = """  } catch (e) {
    // Queue OAuth 401s for the post-renewal retry worker; do not bypass the queue with the PIT.
    var exchangeError = describeError(e);
    var statusCode = e && (e.statusCode !== undefined ? e.statusCode : e.status);
    if (String(statusCode) === '401' || exchangeError.includes('401')) return { ...base, status: 'error', reason: 'oauth_expired_queued: ' + exchangeError };
    return { ...base, status: 'error', reason: 'loc_tok_err: ' + exchangeError };
  }
"""
if old not in code:
    if "oauth_expired_queued:" not in code:
        raise RuntimeError("Expected OAuth fallback block was not found")
else:
    node["parameters"]["jsCode"] = code.replace(old, new)
payload = {
    "name": workflow["name"],
    "nodes": workflow["nodes"],
    "connections": workflow["connections"],
    "settings": allowed_settings(workflow.get("settings")),
}
updated = api(f"/workflows/{WORKFLOW_ID}", "PUT", payload)
if updated.get("versionId") != updated.get("activeVersionId") or not updated.get("active"):
    raise RuntimeError("Inbound workflow did not remain active/published")
print(json.dumps({"workflow": WORKFLOW_ID, "active": updated.get("active"), "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId"), "queued401": "oauth_expired_queued:" in node["parameters"]["jsCode"]}, indent=2))
