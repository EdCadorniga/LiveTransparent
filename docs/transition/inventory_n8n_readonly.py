"""Create a sanitized point-in-time inventory from the authorized n8n-lt API.

Reads N8N_LT_API_KEY from the repository .env without displaying it. The output
intentionally excludes node parameter values and credential contents.
"""

from __future__ import annotations

import json
import pathlib
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import dotenv_values


ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = "https://automations.livetransparent.com/api/v1"
OUT = pathlib.Path(__file__).resolve().parent


def get_json(path: str, token: str) -> dict:
    request = urllib.request.Request(
        BASE + path,
        headers={"X-N8N-API-KEY": token, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def target_id(value) -> str:
    if isinstance(value, dict):
        for key in ("value", "id"):
            if key in value:
                found = target_id(value[key])
                if found:
                    return found
        for nested in value.values():
            found = target_id(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = target_id(nested)
            if found:
                return found
    elif isinstance(value, str) and len(value) >= 12:
        return value
    return ""


def safe_url(value) -> str:
    if not isinstance(value, str) or value.startswith("=") or "{{" in value:
        return "[dynamic/expression URL]" if value else ""
    try:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}{safe_path(parsed.path)}"
    except ValueError:
        pass
    return "[nonliteral URL]"


def safe_path(value) -> str:
    """Redact token-like path segments while retaining recognizable route names."""
    if not isinstance(value, str):
        return ""
    value = re.sub(r"[0-9a-fA-F]{24,}", "[redacted-token-like-segment]", value)
    return value


def read_workflow(summary: dict, token: str) -> dict:
    workflow = get_json("/workflows/" + urllib.parse.quote(summary["id"]), token)
    nodes = workflow.get("nodes", [])
    row = {
        "id": summary.get("id", ""),
        "name": summary.get("name", ""),
        "active": summary.get("active", False),
        "archived": summary.get("isArchived", False),
        "draft": workflow.get("versionId") or summary.get("versionId"),
        "activeVersion": workflow.get("activeVersionId"),
        "updated": summary.get("updatedAt", ""),
        "nodeCount": len(nodes),
        "types": {},
        "triggers": [],
        "webhooks": [],
        "schedules": [],
        "calls": [],
        "internalHttp": [],
    }
    for node in nodes:
        node_type = node.get("type", "")
        name = node.get("name", "")
        params = node.get("parameters") or {}
        row["types"][node_type] = row["types"].get(node_type, 0) + 1
        lowered = node_type.lower()
        is_webhook_trigger = lowered.endswith(".webhook")
        if "trigger" in lowered or "schedule" in lowered or is_webhook_trigger:
            row["triggers"].append({"node": name, "type": node_type})
        if is_webhook_trigger:
            row["webhooks"].append(
                {"node": name, "method": params.get("httpMethod", "GET"),
                 "path": safe_path(params.get("path", ""))}
            )
        if "schedule" in lowered or "cron" in lowered:
            row["schedules"].append({"node": name, "type": node_type})
        if node_type.endswith("executeWorkflow"):
            destination = target_id(params.get("workflowId") or {})
            if destination:
                row["calls"].append({"node": name, "workflowId": destination})
        if node_type.endswith("httpRequest"):
            url = safe_url(params.get("url", ""))
            if "automations.livetransparent.com" in url:
                row["internalHttp"].append({"node": name, "endpoint": url})
    return row


def cell(value) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def main() -> None:
    token = dotenv_values(ROOT / ".env").get("N8N_LT_API_KEY")
    if not token:
        raise SystemExit("N8N_LT_API_KEY unavailable; no request made")
    listing = get_json("/workflows?limit=250", token)
    summaries = listing.get("data", [])
    if listing.get("nextCursor"):
        raise SystemExit("Pagination returned; refusing to claim complete coverage")
    rows, errors = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(read_workflow, item, token): item for item in summaries}
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except Exception as exc:  # report only ID and exception class
                errors.append((futures[future].get("id", ""), type(exc).__name__))
    rows.sort(key=lambda row: row["id"])
    (OUT / "n8n-workflow-inventory-2026-11-04.json").write_text(
        json.dumps({"listed": len(summaries), "errors": errors, "workflows": rows},
                   indent=2), encoding="utf-8"
    )
    lines = [
        "# n8n-lt Workflow Inventory — 2026-11-04", "",
        "**Source:** read-only n8n-lt REST API at `automations.livetransparent.com`.",
        f"**Coverage:** {len(rows)} definitions read of {len(summaries)} listed; "
        f"{len(errors)} detail-read failures. **Active:** "
        f"{sum(bool(row['active']) for row in rows)}; **archived:** "
        f"{sum(bool(row['archived']) for row in rows)}.",
        "**Safety:** parameter values and credential contents are omitted.", "",
        "| Workflow | ID | Active | Archived | Draft version | Active version | Nodes | Triggers / webhooks / schedules |",
        "|---|---|---:|---:|---|---|---:|---|",
    ]
    for row in rows:
        triggers = ", ".join(x["node"] + " (" + x["type"].split(".")[-1] + ")"
                              for x in row["triggers"]) or "—"
        webhooks = ", ".join(str(x["method"]) + " /" + str(x["path"])
                              for x in row["webhooks"]) or "—"
        schedules = ", ".join(x["node"] for x in row["schedules"]) or "—"
        lines.append(
            f"| {cell(row['name'])} | `{row['id']}` | {row['active']} | "
            f"{row['archived']} | `{row['draft'] or ''}` | "
            f"`{row['activeVersion'] or ''}` | {row['nodeCount']} | "
            f"triggers: {cell(triggers)}; webhooks: {cell(webhooks)}; "
            f"schedules: {cell(schedules)} |"
        )
    lines += ["", "## Review flags", "",
              "- Treat API activation/version fields as observed state; workflow names are not authoritative.",
              "- Reconcile names containing ‘DRAFT’ or ‘STAGED’ with `active` and active-version state.",
              "- External GHL/provider callers require separate read-only portal verification.", ""]
    (OUT / "n8n-workflow-inventory-2026-11-04.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    relations = [
        "# n8n-lt Workflow Relationships — 2026-11-04", "",
        "Explicit execute-workflow targets and literal same-instance HTTP URLs only; "
        "dynamic destinations are not inferred.", "",
    ]
    for row in rows:
        edges = [f"execute node `{edge['node']}` → workflow `{edge['workflowId']}`"
                 for edge in row["calls"]]
        edges += [f"HTTP node `{edge['node']}` → {edge['endpoint']}"
                  for edge in row["internalHttp"]]
        if edges:
            relations.append(f"## {row['name']} (`{row['id']}`)")
            relations.extend("- " + edge for edge in edges)
    relations += ["", "## Coverage limits", "",
                  "- GHL and external-provider subscriptions/callers are not discoverable from n8n alone.",
                  "- URL query strings and dynamic expressions are omitted to protect secrets and avoid guessing.", ""]
    (OUT / "n8n-workflow-relationships-2026-11-04.md").write_text(
        "\n".join(relations), encoding="utf-8"
    )
    print(f"listed={len(summaries)} details={len(rows)} errors={len(errors)}")
    print("active=" + str(sum(bool(row["active"]) for row in rows)))
    print("archived=" + str(sum(bool(row["archived"]) for row in rows)))
    print("inventory generated under docs/transition; no configuration values emitted")
    for row in rows:
        if row["active"] and any(term in row["name"].lower()
                                 for term in ("draft", "staged", "temp")):
            print(f"REVIEW {row['id']} active=true name={row['name']}")


if __name__ == "__main__":
    main()
