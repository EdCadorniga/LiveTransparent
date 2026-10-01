"""Read only: report Unipile V2 account ownership without printing credentials."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from wire_sales_navigator_v2_workflows import ENV

BASE = "https://api.unipile.com/v2"
KEY = ENV["UNIPILE_v2_MIGRATION_SERVICE_API_KEY"]
TARGET = "acc_01m3sefk22e8jvnmvvfx333pye"


def get(path: str) -> dict:
    request = urllib.request.Request(
        BASE + path,
        headers={"X-API-KEY": KEY, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def row(account: dict) -> dict:
    metadata = account.get("metadata") or {}
    return {
        "id": account.get("id"),
        "name": account.get("name"),
        "user_id": account.get("user_id"),
        "provider": account.get("provider"),
        "status": account.get("status"),
        "products_connection_status": metadata.get("products_connection_status"),
    }


result = get("/accounts")
accounts = result.get("items", result.get("data", result)) if isinstance(result, dict) else result
if isinstance(accounts, dict):
    accounts = accounts.get("items", accounts.get("data", []))
print(json.dumps({"accounts": [row(a) for a in accounts], "target": row(get("/accounts/" + TARGET))}, indent=2))

target = get("/accounts/" + TARGET)
owner_id = target.get("user_id")
chat_id = "SALES_NAVIGATOR_2-ZWUzNTFlZTgtMWZkZC00NTU2LTg2MjItMmFhNzRlY2JiMDZhXzEwMA=="
chat = get("/" + TARGET + "/chats/" + urllib.parse.quote(chat_id, safe=""))
peer_id = chat.get("user_id")
def profile(uid: str) -> dict:
    result = get("/" + TARGET + "/users/" + urllib.parse.quote(uid, safe="") + "?variant=linkedin_sales_navigator")
    data = result.get("data", result)
    return {key: data.get(key) for key in ("id", "name", "first_name", "last_name", "profile_url", "provider_id")}

print(json.dumps({
    "account_owner_profile": profile(owner_id) if owner_id else None,
    "chat": {key: chat.get(key) for key in ("id", "account_id", "user_id", "inbox_id", "name", "title", "participants")},
    "chat_peer_profile": profile(peer_id) if peer_id else None,
}, indent=2))

messages = get("/" + TARGET + "/chats/" + urllib.parse.quote(chat_id, safe="") + "/messages?limit=15")
message_rows = messages.get("items", messages.get("data", []))
print(json.dumps({"recent_message_metadata": [
    {key: message.get(key) for key in ("id", "timestamp", "is_sender", "sender_id", "from", "sender", "account_id", "chat_id", "inbox_id")}
    for message in message_rows[:10]
]}, indent=2))
