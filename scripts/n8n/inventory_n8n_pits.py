"""Inventory live n8n workflow nodes containing PIT-like values."""

from __future__ import annotations

import json
import os
import hashlib
import re
import subprocess

from review_company_instagram_sources import load_env_file


def main() -> None:
    env = load_env_file()
    api_key = os.environ.get("N8N_API_KEY_LT") or env.get("N8N_API_KEY_LT", "")
    result = subprocess.run(
        [
            "curl.exe", "-sS",
            "-H", f"X-N8N-API-KEY: {api_key}",
            "https://automations.livetransparent.com/api/v1/workflows?limit=200",
        ],
        check=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout.decode("utf-8", errors="replace"))
    matches = []
    token_workflows = {}
    for workflow in payload.get("data", []):
        nodes = workflow.get("nodes", [])
        matching_nodes = []
        for node in nodes:
            serialized = json.dumps(node.get("parameters", {}))
            if "pit-" in serialized.lower():
                matching_nodes.append(node.get("name", ""))
                for value in node.get("parameters", {}).values():
                    text = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                    for token in re.findall(r"pit-[a-z0-9-]+", text, flags=re.I):
                        token_workflows.setdefault(token, []).append(workflow.get("name"))
        if matching_nodes:
            matches.append({"id": workflow.get("id"), "name": workflow.get("name"), "nodes": matching_nodes})
    print(json.dumps(matches, indent=2))
    for token, names in token_workflows.items():
        status = subprocess.run(
            [
                "curl.exe", "-sS", "-o", "NUL", "-w", "%{http_code}",
                "-H", f"Authorization: Bearer {token}",
                "-H", "Version: 2021-07-28",
                "-H", "Accept: application/json",
                "https://services.leadconnectorhq.com/locations/Zwz4relUXVPxx8uohnjV",
            ],
            check=True,
            capture_output=True,
        ).stdout.decode("ascii", errors="replace")
        print(json.dumps({
            "fingerprint": hashlib.sha256(token.encode()).hexdigest()[:12],
            "length": len(token),
            "prefix": token[:4],
            "status": status,
            "workflow_count": len(set(names)),
            "workflows": sorted(set(names)),
        }))


if __name__ == "__main__":
    main()
