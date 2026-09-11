"""Patch LT - LinkedIn Conversation Backfill (JUvrA7qMa24SwAZG), 2026-09-11.

Root cause of Gretchen Gailey's two HTTP 422s (execution 930588): the backfill
routed historical OUTBOUND messages (``is_sender === 1``) to the nonexistent
direction path ``/conversations/messages/outbound``. The correct mirroring shape
for outbound custom-provider messages is ``POST /conversations/messages`` (same
body: type Custom + contactId + message + conversationProviderId + altId + date),
and inbound posts use ``POST /conversations/messages/inbound`` (verified live).

Changes:
1. Outbound posts -> ``/conversations/messages``; inbound posts stay on
   ``/conversations/messages/inbound``.
2. Message-level dedup: before posting, collect existing message bodies from the
   contact's LinkedIn-provider conversations and skip already-present bodies.
3. Config gains ``only_chat_id`` (set to Gretchen's chat id) and the chat loop
   respects it, so the retry touches only Gretchen and never reruns the six
   successful messages.

Usage:
  python scripts/fix_linkedin_backfill_outbound_direction.py          # report only
  python scripts/fix_linkedin_backfill_outbound_direction.py --apply  # apply + verify
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOW_ID = "JUvrA7qMa24SwAZG"

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

OLD_ENDPOINT = "GHL_BASE + '/conversations/messages/' + direction"
NEW_ENDPOINT = "GHL_BASE + '/conversations/messages' + (direction === 'inbound' ? '/inbound' : '')"

OLD_LOOP = "for (const chat of chatsToBackfill) {"
NEW_LOOP = "const activeChats = cfg.only_chat_id ? chatsToBackfill.filter(c => c.chat_id === cfg.only_chat_id) : chatsToBackfill;\nif (!activeChats.length) { return [{ json: { error: 'only_chat_id matched no chats', results: [] } }]; }\nfor (const chat of activeChats) {"

DEDUP_ANCHOR = "    for (const msg of recent) {"
DEDUP_BLOCK = """    const existingBodies = new Set();
    try {
      const convSearch = await httpReq.call(this, 'GET', GHL_BASE + '/conversations/search?contactId=' + encodeURIComponent(contactId) + '&limit=10', {
        Authorization: 'Bearer ' + LOC_TOKEN, Version: '2021-07-28', Accept: 'application/json'
      });
      const convs = convSearch.ok && Array.isArray(convSearch.data?.conversations)
        ? convSearch.data.conversations.filter(c => c.lastMessageConversationProviderId === LINKEDIN_PROVIDER_ID)
        : [];
      for (const conv of convs) {
        const msgs = await httpReq.call(this, 'GET', GHL_BASE + '/conversations/' + conv.id + '/messages?limit=50', {
          Authorization: 'Bearer ' + LOC_TOKEN, Version: '2021-07-28', Accept: 'application/json'
        });
        if (msgs.ok && Array.isArray(msgs.data?.messages?.messages)) {
          for (const m of msgs.data.messages.messages) existingBodies.add(String(m.body || '').trim());
        }
      }
    } catch (dedupErr) {
      cr.errors.push('dedup_lookup: ' + String(dedupErr.message || dedupErr).slice(0, 120));
    }

    for (const msg of recent) {"""

SKIP_EXISTING = "      if (existingBodies.has(String(msg.text || '').trim())) { cr.skipped_existing = (cr.skipped_existing || 0) + 1; await new Promise(r => setTimeout(r, 100)); continue; }\n"
SKIP_ANCHOR = "      const direction = msg.is_sender === 1 ? 'outbound' : 'inbound';"

CONFIG_ASSIGNMENTS_ANCHOR = '{"id":"lid","name":"location_id","value":"Zwz4relUXVPxx8uohnjV","type":"string"}'
CONFIG_ONLY_CHAT_ASSIGNMENT = '{"id":"ocid","name":"only_chat_id","value":"8NOmhtWSUpKbsec3YdsxlA","type":"string"}'


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


def request(method: str = "GET", payload: dict | None = None) -> dict:
    import urllib.request

    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + WORKFLOW_ID,
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


def syntax_check(nodes: list[dict], report: list[str]) -> None:
    for node in nodes:
        if node.get("type") != "n8n-nodes-base.code":
            continue
        code = (node.get("parameters") or {}).get("jsCode")
        if not isinstance(code, str) or not code:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "check.js"
            path.write_text("async function __n8n_wrap__() {\n" + code + "\n}\n__n8n_wrap__();", encoding="utf-8")
            result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
            if result.returncode != 0:
                report.append(f"    SYNTAX FAIL [{node.get('name')}]: {result.stderr.strip()[:300]}")


def process(apply: bool) -> None:
    wf = request()
    report: list[str] = []
    changed = False

    for node in wf.get("nodes", []):
        name = node.get("name", "?")

        if node.get("type") == "n8n-nodes-base.code":
            params = node.get("parameters") or {}
            code = params.get("jsCode")
            if isinstance(code, str) and code:
                if OLD_ENDPOINT in code:
                    code = code.replace(OLD_ENDPOINT, NEW_ENDPOINT)
                    report.append(f"    [{name}] outbound endpoint -> /conversations/messages")
                if OLD_LOOP in code:
                    code = code.replace(OLD_LOOP, NEW_LOOP)
                    report.append(f"    [{name}] only_chat_id filter added")
                if DEDUP_ANCHOR in code and "existingBodies" not in code:
                    code = code.replace(DEDUP_ANCHOR, DEDUP_BLOCK)
                    report.append(f"    [{name}] conversation-message dedup lookup added")
                if SKIP_ANCHOR in code and "existingBodies.has" not in code:
                    code = code.replace(SKIP_ANCHOR, SKIP_EXISTING + SKIP_ANCHOR)
                    report.append(f"    [{name}] skip-already-posted guard added")
                if code != params.get("jsCode"):
                    params["jsCode"] = code
                    changed = True

        if node.get("type") == "n8n-nodes-base.set" and name == "Config":
            params = node.get("parameters") or {}
            assignments = params.get("assignments") or {}
            items = assignments.get("assignments") or []
            if not any(a.get("name") == "only_chat_id" for a in items):
                import copy

                template = copy.deepcopy(items[0]) if items else {}
                template.update({"id": "ocid", "name": "only_chat_id", "value": "8NOmhtWSUpKbsec3YdsxlA", "type": "string"})
                items.append(template)
                assignments["assignments"] = items
                params["assignments"] = assignments
                node["parameters"] = params
                report.append(f"    [Config] added only_chat_id = Gretchen chat id")
                changed = True

    syntax_check(wf.get("nodes", []), report)

    print(f"{WORKFLOW_ID} {wf.get('name')}")
    print("\n".join(report) if report else "    no changes needed")

    if changed and apply:
        settings = {k: v for k, v in (wf.get("settings") or {}).items() if k in ALLOWED_SETTINGS}
        request(method="PUT", payload={
            "name": wf.get("name"),
            "nodes": wf.get("nodes") or [],
            "connections": wf.get("connections") or {},
            "settings": settings,
        })
        checked = request()
        remaining: list[str] = []
        for node in checked.get("nodes", []):
            if node.get("type") != "n8n-nodes-base.code":
                continue
            code = (node.get("parameters") or {}).get("jsCode") or ""
            if OLD_ENDPOINT in code or OLD_LOOP in code:
                remaining.append(node.get("name"))
        verify_report: list[str] = []
        syntax_check(checked.get("nodes", []), verify_report)
        print(json.dumps({
            "applied": True,
            "active": checked.get("active"),
            "old_patterns_remaining_in": remaining,
            "syntax_errors": verify_report,
        }, indent=2))
        if remaining or verify_report:
            raise RuntimeError("Verification failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(f"Mode: {'APPLY' if args.apply else 'REPORT (dry run)'}")
    process(apply=args.apply)


if __name__ == "__main__":
    main()
