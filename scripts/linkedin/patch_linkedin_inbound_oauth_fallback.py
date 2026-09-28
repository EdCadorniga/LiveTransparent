"""Add a location-PIT fallback for expired GHL OAuth tokens in the live inbound bridge."""
from __future__ import annotations
import json, os, urllib.request
from pathlib import Path

BASE = "https://automations.livetransparent.com/api/v1"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"
NODE_NAME = "Create LinkedIn Contact and Add Inbound Message"

cfg = {}
for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1); cfg[k.strip()] = v.strip().strip('"').strip("'")
key = os.environ.get("N8N_API_KEY_LT") or cfg.get("N8N_API_KEY_LT")
if not key: raise RuntimeError("N8N_API_KEY_LT is required")

def api(method="GET", payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(f"{BASE}/workflows/{WORKFLOW_ID}", data=body, method=method, headers={"X-N8N-API-KEY": key, "Accept": "application/json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response: return json.loads(response.read())

workflow = api()
node = next(n for n in workflow["nodes"] if n.get("name") == NODE_NAME)
code = node["parameters"]["jsCode"]
old = """  } catch (e) {
    return { ...base, status: 'error', reason: 'loc_tok_err: ' + describeError(e) };
  }

  var sentBody = {"""
new = """  } catch (e) {
    // OAuth access tokens expire; use the bounded location PIT fallback only on 401.
    var exchangeError = describeError(e);
    var statusCode = e && (e.statusCode !== undefined ? e.statusCode : e.status);
    if (String(statusCode) === '401' || exchangeError.includes('401')) locToken = GHL_PIT;
    else return { ...base, status: 'error', reason: 'loc_tok_err: ' + exchangeError };
  }

  var sentBody = {"""
if old not in code: raise RuntimeError("expected OAuth exchange block not found")
node["parameters"]["jsCode"] = code.replace(old, new)
allowed = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}
payload = {"name": workflow.get("name"), "nodes": workflow["nodes"], "connections": workflow.get("connections", {}), "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in allowed}}
api("PUT", payload)
checked = api()
checked_node = next(n for n in checked["nodes"] if n.get("name") == NODE_NAME)
print(json.dumps({"workflowId": WORKFLOW_ID, "node": NODE_NAME, "active": checked.get("active"), "versionId": checked.get("versionId"), "activeVersionId": checked.get("activeVersionId"), "published": checked.get("versionId") == checked.get("activeVersionId"), "fallbackPresent": "locToken = GHL_PIT" in checked_node["parameters"].get("jsCode", "")}, indent=2))
