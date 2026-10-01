"""Repair signed webhook byte handling on the two n8n-lt Sales Navigator routes.

Only the Config binary passthrough option and signature validator code change.
No webhook is invoked and no message is sent by this script.
"""
from __future__ import annotations

import json

from wire_sales_navigator_v2_workflows import (
    VALIDATE_INBOUND,
    VALIDATE_OUTBOUND,
    api,
)


ROUTES = (
    ("ZiYEBuP7xdddhnUB", "Validate Callback or Provider", VALIDATE_OUTBOUND),
    ("CfpedDQWxoJLEMdL", "Verify HMAC + Allowlist", VALIDATE_INBOUND),
)


def repair(workflow_id: str, validator_name: str, source: str) -> dict:
    workflow = api(f"/workflows/{workflow_id}")
    if not workflow.get("active") or workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError("workflow is not active at its saved version")
    nodes = workflow["nodes"]
    config = next(node for node in nodes if node["name"] == "Config")
    validator = next(node for node in nodes if node["name"] == validator_name)
    previous = validator["parameters"]["jsCode"]
    if previous != source and "rawBody" not in previous:
        raise RuntimeError("validator differs from the expected pre-repair version")
    config["parameters"].setdefault("options", {})["includeBinary"] = True
    validator["parameters"]["jsCode"] = source
    payload = {key: workflow[key] for key in ("name", "nodes", "connections", "settings")}
    if "staticData" in workflow:
        payload["staticData"] = workflow["staticData"]
    api(f"/workflows/{workflow_id}", "PUT", payload)
    readback = api(f"/workflows/{workflow_id}")
    if readback.get("versionId") != readback.get("activeVersionId"):
        api(f"/workflows/{workflow_id}/activate", "POST", {})
        readback = api(f"/workflows/{workflow_id}")
    updated_config = next(node for node in readback["nodes"] if node["name"] == "Config")
    updated_validator = next(node for node in readback["nodes"] if node["name"] == validator_name)
    if (
        not readback.get("active")
        or readback.get("versionId") != readback.get("activeVersionId")
        or updated_config["parameters"].get("options", {}).get("includeBinary") is not True
        or updated_validator["parameters"]["jsCode"] != source
    ):
        raise RuntimeError("repair did not publish correctly")
    return {
        "workflowId": workflow_id,
        "active": True,
        "versionId": readback["versionId"],
        "versionMatches": True,
        "binaryPassthrough": True,
        "validatorUpdated": True,
    }


if __name__ == "__main__":
    for route in ROUTES:
        try:
            print(json.dumps(repair(*route)))
        except Exception as exc:
            print(json.dumps({"workflowId": route[0], "errorType": type(exc).__name__}))
            raise SystemExit(1) from None
