"""Verify Unipile HMAC acceptance with an intentionally unsupported event.

The signing secret stays in memory; the event cannot enter any CRM write path.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request

from wire_sales_navigator_v2_workflows import api

workflow = api("/workflows/CfpedDQWxoJLEMdL")
config = next(node for node in workflow["nodes"] if node["name"] == "Config")
secret = next(
    assignment["value"]
    for assignment in config["parameters"]["assignments"]["assignments"]
    if assignment["name"] == "unipileWebhookSecret"
)
if not isinstance(secret, str) or not secret or secret.startswith("="):
    raise RuntimeError("signing secret is unavailable as a Config value")
body = json.dumps(
    {"id": "probe-invalid-event", "type": "probe.invalid", "account_id": "acc_01m3sefk22e8jvnmvvfx333pye", "payload": {}},
    separators=(",", ":"),
).encode()
timestamp = str(int(time.time()))
signature = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
request = urllib.request.Request(
    "https://automations.livetransparent.com/webhook/lt-unipile-sales-navigator-new-messages",
    data=body,
    method="POST",
    headers={
        "Content-Type": "application/json",
        "unipile-signature": f"t={timestamp},v0={signature}",
    },
)
try:
    with urllib.request.urlopen(request, timeout=25) as response:
        status, raw = response.status, response.read()
except urllib.error.HTTPError as exc:
    status, raw = exc.code, exc.read()
error = json.loads(raw).get("error")
print(json.dumps({"status": status, "error": error}))
if status != 400 or error != "event_rejected":
    raise SystemExit(1)
