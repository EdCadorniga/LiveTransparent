"""Use the personal LinkedIn profile first name for the personal send path."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE = "https://automations.livetransparent.com/api/v1/workflows/"
ALLOWED = {"executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy", "errorWorkflow", "binaryMode", "availableInMCP"}


def api_key() -> str:
    value = os.environ.get("N8N_API_KEY_LT", "")
    if value:
        return value
    for line in (Path(__file__).resolve().parents[2] / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("N8N_API_KEY_LT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("N8N_API_KEY_LT is required")


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(BASE + workflow_id, data=body, method=method, headers={"X-N8N-API-KEY": api_key(), "Accept": "application/json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def update(workflow_id: str, node_name: str, replacements: list[tuple[str, str]]) -> None:
    workflow = request(workflow_id)
    node = next(node for node in workflow["nodes"] if node["name"] == node_name)
    code = node["parameters"]["jsCode"]
    for old, new in replacements:
        count = code.count(old)
        if count != 1:
            raise RuntimeError(f"expected one match in {workflow_id}/{node_name}, found {count}: {old[:80]}")
        code = code.replace(old, new, 1)
    node["parameters"]["jsCode"] = code
    payload = {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow["connections"], "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in ALLOWED}}
    updated = request(workflow_id, "PUT", payload)
    print(json.dumps({"workflow": workflow_id, "node": node_name, "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


update("fXxw5lanZcDmUrst", "Dispatch LinkedIn Requests", [(
    "  const firstName = clean(contact?.firstName);\n  const linkedinFirstName = clean(unipileProfile.data?.first_name || unipileProfile.data?.firstName || '');\n  if (!firstName) { errors.push({ contact_id: contactId, stage: 'identity', error: 'missing_ghl_first_name' }); results.push({ contactId, status: 'identity_failed', error: 'missing_ghl_first_name' }); continue; }\n  if (linkedinFirstName && linkedinFirstName.toLowerCase() !== firstName.toLowerCase()) { errors.push({ contact_id: contactId, stage: 'identity', error: 'first_name_mismatch' }); results.push({ contactId, status: 'identity_failed', error: 'first_name_mismatch', ghl_first_name: firstName, linkedin_first_name: linkedinFirstName }); continue; }",
    "  const ghlFirstName = clean(contact?.firstName);\n  const linkedinFirstName = clean(unipileProfile.data?.first_name || unipileProfile.data?.firstName || '');\n  if (!linkedinFirstName) { errors.push({ contact_id: contactId, stage: 'identity', error: 'missing_linkedin_first_name' }); results.push({ contactId, status: 'identity_failed', error: 'missing_linkedin_first_name', ghl_first_name: ghlFirstName }); continue; }\n  const firstName = linkedinFirstName;"
)])

update("d0tEtijajisIsYcs", "Sync Connected from Unipile", [(
    "              var firstName = clean(contact.firstName || 'there');\n              if ((!firstName || firstName === 'there') && profileResp && profileResp.ok && profileResp.data) {\n                firstName = clean(profileResp.data.first_name || profileResp.data.firstName || 'there');\n              }",
    "              var ghlFirstName = clean(contact.firstName || '');\n              var firstName = profileResp && profileResp.ok && profileResp.data ? clean(profileResp.data.first_name || profileResp.data.firstName || '') : '';\n              if (!firstName) {\n                results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'missing_linkedin_first_name', ghl_first_name: ghlFirstName });\n                return processNext.call(self, index + 1);\n              }"
)])

update("d0tEtijajisIsYcs", "Send DM Sequence Messages", [(
            "              var firstName = clean(contact.firstName);\n              var linkedinFirstName = profileResp && profileResp.ok && profileResp.data ? clean(profileResp.data.first_name || profileResp.data.firstName || '') : '';\n              if (!firstName) { results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'missing_ghl_first_name' }); return processNext.call(self, index + 1); }\n              if (linkedinFirstName && linkedinFirstName.toLowerCase() !== firstName.toLowerCase()) { results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'first_name_mismatch', ghl_first_name: firstName, linkedin_first_name: linkedinFirstName }); return processNext.call(self, index + 1); }",
            "              var ghlFirstName = clean(contact.firstName || '');\n              var firstName = profileResp && profileResp.ok && profileResp.data ? clean(profileResp.data.first_name || profileResp.data.firstName || '') : '';\n              if (!firstName) { results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'missing_linkedin_first_name', ghl_first_name: ghlFirstName }); return processNext.call(self, index + 1); }"
)])
