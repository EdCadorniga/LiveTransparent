"""Create a replacement encrypted n8n-lt Header Auth credential from the working V2 key."""
from __future__ import annotations

import json

from wire_sales_navigator_v2_workflows import ENV, api

NAME = "LT Sales Navigator Unipile V2 API (verified)"


def main() -> None:
    key = ENV["UNIPILE_v2_MIGRATION_SERVICE_API_KEY"]
    if not key:
        raise RuntimeError("working Unipile V2 key is unavailable")
    try:
        credential = api(
            "/credentials",
            "POST",
            {
                "name": NAME,
                "type": "httpHeaderAuth",
                "data": {
                    "name": "X-API-KEY",
                    "value": key,
                    "allowedHttpRequestDomains": "all",
                },
            },
        )
    except Exception:
        raise RuntimeError("n8n-lt credential creation failed; response withheld") from None
    print(json.dumps({
        "id": credential.get("id"),
        "name": credential.get("name"),
        "type": credential.get("type"),
        "keyStored": bool(credential.get("id")),
    }))


if __name__ == "__main__":
    main()
