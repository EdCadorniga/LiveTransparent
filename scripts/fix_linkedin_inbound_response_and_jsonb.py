"""Fix response interpretation + jsonb literal bugs in LT - LinkedIn Unipile New Messages (2026-09-11).

Two live bugs confirmed from execution 934032:

1. ``Create LinkedIn Contact and Add Inbound Message`` used
   ``resolveWithFullResponse: true`` with ``this.helpers.httpRequest``. That option
   belongs to the deprecated ``this.helpers.request`` helper and is silently
   ignored, so ``resp`` is the response BODY and ``resp.statusCode``/``resp.body``
   are undefined. GHL actually returned HTTP 200 and created the message
   (conversation B6Enrm2D2LtsXPhi1qLY), but the node classified it as
   ``inbound_failed: status=undefined body={}``. Fix: use ``returnFullResponse``
   and harden ``describeError`` to surface ``statusCode``/``error`` body from
   axios-style errors.

2. Every ``Build * SQL`` Code node's ``esc()`` doubled backslashes
   (``.replace(/\\/g, '\\\\')``). With standard_conforming_strings on, backslashes
   in SQL single-quoted strings are literal, so a ``'...'::jsonb`` literal built
   from ``JSON.stringify`` ends up with ``\\\"`` sequences, which is invalid JSON
   (``\\`` then a string-terminating quote). Any payload containing an embedded
   quote (e.g. ``sentBody``) crashes ``Upsert LinkedIn Map`` with
   "invalid input syntax for type json", so ``linkedin_conversation_map`` rows
   were never persisted. Fix: drop the backslash doubling, keep ``'`` -> ``''``.

Usage:
  python scripts/fix_linkedin_inbound_response_and_jsonb.py          # report only
  python scripts/fix_linkedin_inbound_response_and_jsonb.py --apply  # apply + verify
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"

ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
    "availableInMCP",
}

# Exact JS substring as stored in the live workflow.
BACKSLASH_DOUBLE = r".replace(/\\/g, '\\\\')"
RESOLVE_FULL = "resolveWithFullResponse: true"
RETURN_FULL = "returnFullResponse: true"

OLD_DESCRIBE = """function describeError(e) {
  const body = e && (e.response?.body || e.body || e.data);
  if (body) {
    try { return typeof body === 'string' ? body : JSON.stringify(body); } catch (_) {}
  }
  return str(e && e.message ? e.message : e).substring(0, 500);
}"""

NEW_DESCRIBE = """function describeError(e) {
  const body = e && (e.error || e.response?.body || e.response?.data || e.body || e.data);
  const code = e && (e.statusCode !== undefined && e.statusCode !== null ? e.statusCode : e.status);
  const prefix = code !== undefined && code !== null ? code + ' - ' : '';
  if (body) {
    try { return prefix + (typeof body === 'string' ? body : JSON.stringify(body)); } catch (_) {}
  }
  return str(prefix + (e && e.message ? e.message : e)).substring(0, 500);
}"""


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
    if not key:
        raise RuntimeError("N8N_API_KEY_LT is required")
    return key


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    import urllib.request

    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def update_workflow(workflow: dict) -> dict:
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
    payload = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": settings,
    }
    return request(WORKFLOW_ID, method="PUT", payload=payload)


def syntax_check(nodes: list[dict], report: list[str]) -> None:
    node_by_code: dict[str, str] = {}
    for node in nodes:
        if node.get("type") == "n8n-nodes-base.code":
            code = (node.get("parameters") or {}).get("jsCode")
            if isinstance(code, str) and code:
                node_by_code[code] = node.get("name", "?")
    with tempfile.TemporaryDirectory() as tmp:
        for code, name in node_by_code.items():
            path = Path(tmp) / "check.js"
            # n8n Code nodes run in an async context; wrap so top-level await/return check cleanly.
            path.write_text("async function __n8n_wrap__() {\n" + code + "\n}\n__n8n_wrap__();", encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(path)], capture_output=True, text=True
            )
            if result.returncode != 0:
                report.append(f"    SYNTAX FAIL [{name}]: {result.stderr.strip()[:300]}")


def process(apply: bool) -> None:
    wf = request(WORKFLOW_ID)
    report: list[str] = []
    changed = False

    for node in wf.get("nodes", []):
        if node.get("type") != "n8n-nodes-base.code":
            continue
        params = node.get("parameters") or {}
        code = params.get("jsCode")
        if not isinstance(code, str) or not code:
            continue
        name = node.get("name", "?")

        if BACKSLASH_DOUBLE in code:
            hits = code.count(BACKSLASH_DOUBLE)
            code = code.replace(BACKSLASH_DOUBLE, "")
            report.append(f"    [{name}] removed backslash doubling from esc(): {hits}")
        if RESOLVE_FULL in code:
            code = code.replace(RESOLVE_FULL, RETURN_FULL)
            report.append(f"    [{name}] resolveWithFullResponse -> returnFullResponse")
        if OLD_DESCRIBE in code:
            code = code.replace(OLD_DESCRIBE, NEW_DESCRIBE)
            report.append(f"    [{name}] hardened describeError (statusCode + error body)")

        if code != params.get("jsCode"):
            params["jsCode"] = code
            changed = True

    syntax_check(wf.get("nodes", []), report)

    print(f"{WORKFLOW_ID} {wf.get('name')}")
    print("\n".join(report) if report else "    no changes needed")

    if changed and apply:
        update_workflow(wf)
        checked = request(WORKFLOW_ID)
        remaining_resolve = []
        remaining_backslash = []
        for node in checked.get("nodes", []):
            if node.get("type") != "n8n-nodes-base.code":
                continue
            code = (node.get("parameters") or {}).get("jsCode") or ""
            if RESOLVE_FULL in code:
                remaining_resolve.append(node.get("name"))
            if BACKSLASH_DOUBLE in code:
                remaining_backslash.append(node.get("name"))
        verify_report: list[str] = []
        syntax_check(checked.get("nodes", []), verify_report)
        print(
            json.dumps(
                {
                    "applied": True,
                    "active": checked.get("active"),
                    "draft_is_active": checked.get("versionId") == checked.get("activeVersionId"),
                    "resolveWithFullResponse_remaining_in": remaining_resolve,
                    "backslash_doubling_remaining_in": remaining_backslash,
                    "syntax_errors": verify_report,
                },
                indent=2,
            )
        )
        if remaining_resolve or remaining_backslash or verify_report:
            raise RuntimeError("Verification failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is report-only dry run)")
    args = parser.parse_args()
    print(f"Mode: {'APPLY' if args.apply else 'REPORT (dry run)'}")
    process(apply=args.apply)


if __name__ == "__main__":
    main()
