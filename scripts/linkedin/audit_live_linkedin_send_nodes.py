"""Read live LinkedIn workflow send nodes without mutating n8n."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOWS = {
    "main_dispatcher": "fXxw5lanZcDmUrst",
    "partnership_dispatcher": "crKIsaL5k3YBfqDZ",
    "main_dm": "d0tEtijajisIsYcs",
    "partnership_dm": "nspggypNF245xzeL",
    "inbound": "7o5EBdvwAuIaWW7k",
}


def request(workflow_id: str) -> dict:
    key = os.environ.get("N8N_API_KEY_LT", "")
    if not key:
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("N8N_API_KEY_LT="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise RuntimeError("N8N_API_KEY_LT is required")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        headers={"X-N8N-API-KEY": key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


for label, workflow_id in WORKFLOWS.items():
    workflow = request(workflow_id)
    print(f"\n## {label} {workflow_id} {workflow.get('versionId')} active={workflow.get('activeVersionId')}")
    for node in workflow.get("nodes", []):
        if node.get("type") not in {"n8n-nodes-base.code", "n8n-nodes-base.postgres"}:
            continue
        name = node.get("name", "")
        code = node.get("parameters", {}).get("jsCode")
        query = node.get("parameters", {}).get("query")
        if code is not None:
            print(f"NODE {name} CODE {len(code)}")
            for needle in ("firstName", "first_name", "/chats", "/users/invite", "conversations/messages", "dm_sent", "message_received"):
                positions = [i for i in range(len(code)) if code.startswith(needle, i)]
                if positions:
                    print(f"  {needle}: {positions[:12]}")
                    for position in positions[-2:]:
                        width = 1600 if needle in {"/chats", "/users/invite"} else 420
                        print("    ..." + code[max(0, position - 220):position + width].replace("\n", " ") + "...")
        elif query is not None:
            print(f"NODE {name} SQL {len(query)}")
            for needle in ("connection_status", "dm_sent", "conversations/messages", "ghl_oauth_tokens"):
                if needle in query:
                    print(f"  contains {needle}")
