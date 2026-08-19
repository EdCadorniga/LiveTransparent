"""Fix double-escaped regex corruption in Unipile send-path workflows (2026-08-19).

Root cause: jsCode of Code nodes contains double-escaped regex sequences such as
``/\\u2018/`` (two literal backslashes) where a single escape ``/\u2018/`` was
intended. Inside a character class this makes the sanitizer match the literal
letters in the sequence (``u``, ``C``, ``D`` and digits) instead of smart-quote
characters, corrupting outbound LinkedIn/Instagram message text (e.g.
"I'm Cameron..." -> 'I"m "ameron...'). The same class of bug breaks the
``{first_name}`` placeholder replacement (``/\\{first_name\\}/gi`` only matches a
backslashed, brace-wrapped literal, so placeholders are sent unreplaced).

Usage:
  python scripts/fix_linkedin_sanitize_double_escape.py          # report only
  python scripts/fix_linkedin_sanitize_double_escape.py --apply  # apply + verify
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"

# Live Unipile send-path workflows plus the state-upsert webhook (stores request_message).
TARGETS = {
    "fXxw5lanZcDmUrst": "LT - GHL LinkedIn Connect Dispatcher",
    "d0tEtijajisIsYcs": "LT - LinkedIn DM Sequence (Unipile)",
    "crKIsaL5k3YBfqDZ": "LT - Partnership LinkedIn Dispatcher",
    "nspggypNF245xzeL": "LT - Partnership LinkedIn DM Sequence",
    "IeovbYnhCsetXS89": "LT - Instagram Company Page Partnership Sender",
    "Old7ZvyVYgFaJgDr": "LT - LinkedIn Connection State Upsert",
}

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

# 2 literal backslashes + 'u' + 4 hex digits -> 1 backslash + 'u' + hex.
DOUBLE_ESCAPED_UNICODE = re.compile(r"\\\\u([0-9A-Fa-f]{4})")
# 2 literal backslashes around the first_name placeholder (brace closes AFTER
# the trailing backslashes in the corrupted form: /\\{first_name\\}/gi).
FIRST_NAME_DOUBLE = "\\\\{first_name\\\\}"
FIRST_NAME_SINGLE = "\\{first_name\\}"
# URL character class with incorrectly escaped whitespace token.
WS_CLASS_DOUBLE = "[^\\\\s,]"
WS_CLASS_SINGLE = "[^\\s,]"


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
    return request(workflow["id"], method="PUT", payload=payload)


def fix_code(code: str, report: list[str], node_name: str) -> str:
    unicode_hits = DOUBLE_ESCAPED_UNICODE.findall(code)
    if unicode_hits:
        report.append(f"    [{node_name}] double-escaped unicode escapes: {len(unicode_hits)} -> collapsing")
        code = DOUBLE_ESCAPED_UNICODE.sub(r"\\u\1", code)
    first_name_hits = code.count(FIRST_NAME_DOUBLE)
    if first_name_hits:
        report.append(f"    [{node_name}] double-escaped {{first_name}} regex: {first_name_hits} -> collapsing")
        code = code.replace(FIRST_NAME_DOUBLE, FIRST_NAME_SINGLE)
    ws_hits = code.count(WS_CLASS_DOUBLE)
    if ws_hits:
        report.append(f"    [{node_name}] URL whitespace class [^\\\\s,]: {ws_hits} -> [^\\s,]")
        code = code.replace(WS_CLASS_DOUBLE, WS_CLASS_SINGLE)
    return code


def non_ascii_report(code: str) -> list[str]:
    found = sorted({ch for ch in code if ord(ch) > 127})
    return [f"U+{ord(ch):04X} {ch!r}" for ch in found]


def process(workflow_id: str, apply: bool) -> bool:
    wf = request(workflow_id)
    changed = False
    report: list[str] = []
    for node in wf.get("nodes", []):
        if node.get("type") != "n8n-nodes-base.code":
            continue
        params = node.get("parameters") or {}
        code = params.get("jsCode")
        if not isinstance(code, str) or not code:
            continue
        non_ascii = non_ascii_report(code)
        if non_ascii:
            report.append(f"    [{node.get('name')}] non-ASCII chars present: {', '.join(non_ascii)}")
        new_code = fix_code(code, report, node.get("name", "?"))
        if new_code != code:
            params["jsCode"] = new_code
            changed = True
    name = wf.get("name", workflow_id)
    if report:
        print(f"{workflow_id} {name}")
        print("\n".join(report))
    else:
        print(f"{workflow_id} {name}: clean")
    if changed and apply:
        updated = update_workflow(wf)
        checked = request(workflow_id)
        ok_pub = checked.get("versionId") == checked.get("activeVersionId")
        remaining = []
        for node in checked.get("nodes", []):
            if node.get("type") != "n8n-nodes-base.code":
                continue
            code = (node.get("parameters") or {}).get("jsCode") or ""
            if DOUBLE_ESCAPED_UNICODE.search(code) or FIRST_NAME_DOUBLE in code or WS_CLASS_DOUBLE in code:
                remaining.append(node.get("name"))
        print(
            json.dumps(
                {
                    "applied": True,
                    "id": updated.get("id"),
                    "active": checked.get("active"),
                    "draft_is_active": checked.get("versionId") == checked.get("activeVersionId"),
                    "corruption_remaining_in": remaining,
                },
                indent=2,
            )
        )
        if remaining:
            raise RuntimeError(f"Verification failed for {workflow_id}")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is report-only dry run)")
    args = parser.parse_args()
    mode = "APPLY" if args.apply else "REPORT (dry run)"
    print(f"Mode: {mode}")
    for workflow_id in TARGETS:
        process(workflow_id, apply=args.apply)


if __name__ == "__main__":
    main()
