"""Point the two n8n-lt Sales Navigator workflows at the verified V2 credential."""
from __future__ import annotations

import json

from wire_sales_navigator_v2_workflows import api

OLD_ID = "xfQeYq9i3A0TrEnT"
NEW_ID = "calCid5lrBNnl78y"
NEW_NAME = "LT Sales Navigator Unipile V2 API (verified)"
WORKFLOWS = (
    ("ZiYEBuP7xdddhnUB", ("Send Existing V2 Chat Message",)),
    ("CfpedDQWxoJLEMdL", (
        "Fetch V2 Sender Profile",
        "Fetch Outbound Chat Messages",
        "Fetch Outbound Peer Profile",
    )),
)


def wire(workflow_id: str, node_names: tuple[str, ...]) -> dict:
    workflow = api(f"/workflows/{workflow_id}")
    if not workflow.get("active") or workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError("workflow version is not active")
    nodes = workflow["nodes"]
    for name in node_names:
        node = next(node for node in nodes if node["name"] == name)
        credential = node["credentials"]["httpHeaderAuth"]
        if credential["id"] not in (OLD_ID, NEW_ID):
            raise RuntimeError("workflow credential differs from expected")
        credential.update({"id": NEW_ID, "name": NEW_NAME})
    payload = {key: workflow[key] for key in ("name", "nodes", "connections", "settings")}
    if "staticData" in workflow:
        payload["staticData"] = workflow["staticData"]
    api(f"/workflows/{workflow_id}", "PUT", payload)
    readback = api(f"/workflows/{workflow_id}")
    if readback.get("versionId") != readback.get("activeVersionId"):
        api(f"/workflows/{workflow_id}/activate", "POST", {})
        readback = api(f"/workflows/{workflow_id}")
    if (
        not readback.get("active")
        or readback.get("versionId") != readback.get("activeVersionId")
        or any(
            next(n for n in readback["nodes"] if n["name"] == name)["credentials"]["httpHeaderAuth"]["id"] != NEW_ID
            for name in node_names
        )
    ):
        raise RuntimeError("credential wiring did not publish")
    return {
        "workflowId": workflow_id,
        "active": True,
        "versionId": readback["versionId"],
        "credentialNodeCount": len(node_names),
    }


if __name__ == "__main__":
    for workflow_id, names in WORKFLOWS:
        try:
            print(json.dumps(wire(workflow_id, names)))
        except Exception:
            print(json.dumps({"workflowId": workflow_id, "error": "credential wiring failed; details withheld"}))
            raise SystemExit(1) from None
