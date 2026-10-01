"""Exercise only the rejected-signature branches of the n8n-lt webhooks."""
from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request

BASE = "https://automations.livetransparent.com/webhook/"
BODY = b'{"probe":"signed-body-buffer"}'
PROBES = (
    (
        "ghl-provider",
        "lt-sales-navigator-provider",
        "X-GHL-Signature",
        base64.b64encode(bytes(64)).decode(),
    ),
    (
        "unipile-v2",
        "lt-unipile-sales-navigator-new-messages",
        "unipile-signature",
        f"t={int(time.time())},v0={'0' * 64}",
    ),
)


def probe(name: str, path: str, header: str, signature: str) -> dict:
    request = urllib.request.Request(
        BASE + path,
        data=BODY,
        method="POST",
        headers={"Content-Type": "application/json", header: signature},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    try:
        error = json.loads(raw).get("error")
    except (ValueError, AttributeError):
        error = None
    return {"route": name, "status": status, "error": error}


if __name__ == "__main__":
    results = [probe(*item) for item in PROBES]
    print(json.dumps(results))
    if any(result["status"] != 401 or result["error"] != "invalid_signature" for result in results):
        raise SystemExit(1)
