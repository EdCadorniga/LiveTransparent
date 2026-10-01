"""Read only: inspect recent Unipile V2 Sales Navigator chat IDs and shapes."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ACCOUNT = "acc_01m3sefk22e8jvnmvvfx333pye"
ENV: dict[str, str] = {}
for line in (Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip().strip('"').strip("'")

def get(path: str) -> dict:
    request = urllib.request.Request(
        "https://api.unipile.com/v2/" + ACCOUNT + path,
        headers={"X-API-KEY": ENV["UNIPILE_v2_MIGRATION_SERVICE_API_KEY"], "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


result = get("/inboxes/SALES_NAVIGATOR_PRIMARY/chats?limit=100")
chats = result.get("data", []) if isinstance(result, dict) else []
recent = chats[0] if chats else {}
profile = get("/users/" + urllib.parse.quote(recent["user_id"], safe="") + "?variant=linkedin_sales_navigator") if recent.get("user_id") else {}
profile_data = profile.get("data", profile) if isinstance(profile, dict) else {}
messages = get("/chats/" + urllib.parse.quote(recent["id"], safe="") + "/messages?limit=5") if recent.get("id") else {}
message_rows = messages.get("data", []) if isinstance(messages, dict) else []
print({
    "count": len(chats),
    "resultKeys": sorted(result) if isinstance(result, dict) else [],
    "chatKeys": sorted(chats[0]) if chats else [],
    "recent": [
        {
            "id": chat.get("id"),
            "inbox_id": chat.get("inbox_id"),
            "last_message_at": chat.get("last_message_at"),
            "last_message_timestamp": chat.get("last_message_timestamp"),
            "user_id": chat.get("user_id"),
        }
        for chat in chats[:3]
    ],
    "latestPeerProfileUrl": profile_data.get("profile_url"),
    "matchesEdTestProfile": "edmundo-c-a06372166" in str(profile_data.get("profile_url", "")).lower(),
    "latestMessages": [
        {"id": m.get("id"), "timestamp": m.get("timestamp"), "is_sender": m.get("is_sender")}
        for m in message_rows
    ],
})
