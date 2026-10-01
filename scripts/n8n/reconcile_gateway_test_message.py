"""Complete the one GHL test message blocked by Unipile's invalid old key.

The script first searches the verified chat for the exact unique test text.
It sends only if absent, then attaches Unipile's message ID to the existing
processing GHL claim. Never run for a different message without re-verifying it.
"""
from __future__ import annotations

import base64
import io
import json
import socket
import urllib.parse
import urllib.request
from pathlib import Path

import paramiko

from wire_sales_navigator_v2_workflows import ENV

ACCOUNT = "acc_01m3sefk22e8jvnmvvfx333pye"
CHAT = "SALES_NAVIGATOR_2-ZWUzNTFlZTgtMWZkZC00NTU2LTg2MjItMmFhNzRlY2JiMDZhXzEwMA=="
GHL_MESSAGE = "43VUp6aZNwLr5KlOKAOK"
TEXT = "Sales Navigator bridge verification from GHL"
BASE = f"https://api.unipile.com/v2/{ACCOUNT}/chats/{urllib.parse.quote(CHAT, safe='')}/messages"
KEY = ENV["UNIPILE_v2_MIGRATION_SERVICE_API_KEY"]


def unipile(path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = urllib.request.Request(
        BASE + path,
        data=body,
        method="GET" if body is None else "POST",
        headers={
            "X-API-KEY": KEY,
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def mark_posted(message_id: str) -> bool:
    sql = f"""
UPDATE sales_navigator_v2_message_events
SET status='posted',unipile_message_id='{message_id}',failure_code=NULL,updated_at=NOW()
WHERE unipile_account_id='{ACCOUNT}' AND event_id='ghl:{GHL_MESSAGE}'
  AND unipile_chat_id='{CHAT}'
  AND (status='processing' OR (status='posted' AND unipile_message_id='{message_id}'))
RETURNING id;
"""
    encoded = base64.b64encode(sql.encode()).decode()
    command = (
        "docker exec postgres-uokgs4c04ko0s4scccg40cgg sh -c "
        f"'echo {encoded} | base64 -d | psql -X -v ON_ERROR_STOP=1 -A -t -U postgres -d postgres'"
    )
    key = paramiko.Ed25519Key.from_private_key(
        io.StringIO((Path.home() / ".ssh" / "local-upload").read_text())
    )
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect(
        socket.gethostbyname("automations.livetransparent.com"),
        username="root", pkey=key, timeout=10, look_for_keys=False,
    )
    try:
        _, stdout, stderr = ssh.exec_command(command, timeout=20)
        output = stdout.read().decode().strip()
        status = stdout.channel.recv_exit_status()
        return status == 0 and any(line.isdigit() for line in output.splitlines())
    finally:
        ssh.close()


def main() -> None:
    prior = unipile("?limit=25")
    existing = [
        item for item in prior.get("data", [])
        if item.get("is_sender") is True and item.get("text") == TEXT
    ]
    if len(existing) > 1:
        raise RuntimeError("more than one matching Unipile message; manual reconciliation needed")
    created = False
    if existing:
        message_id = existing[0]["id"]
    else:
        response = unipile("/send", {"text": TEXT})
        raw_id = response.get("message_id") or response.get("id")
        if isinstance(raw_id, list):
            if len(raw_id) != 1:
                raise RuntimeError("send returned multiple message IDs")
            raw_id = raw_id[0]
        if not isinstance(raw_id, str) or not raw_id:
            raise RuntimeError("send response lacks a message ID; inspect Unipile before retrying")
        message_id = raw_id
        created = True
    posted = mark_posted(message_id)
    print(json.dumps({"unipileMessageId": message_id, "sentNew": created, "ledgerPosted": posted}))
    if not posted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
