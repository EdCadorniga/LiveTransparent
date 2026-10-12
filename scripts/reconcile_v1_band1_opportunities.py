"""Read-only ID-level comparison: V1 raw opportunity facts vs live GHL."""

from __future__ import annotations

import json
import pathlib
import ssl
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
N8N_HOST = "https://automations.livetransparent.com"
GHL_HOST = "https://services.leadconnectorhq.com"
LOCATION_ID = "Zwz4relUXVPxx8uohnjV"
PG_CREDENTIAL = {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = read_env()
n8n_key = env.get("N8N_LT_API_KEY")
ghl_key = env.get("GHL_PIT") or env.get("GHL_API_KEY")
if not n8n_key or not ghl_key:
    raise SystemExit("Required API key unavailable")

periods = [("2026-10-04", "2026-10-10"), ("2026-09-27", "2026-10-03")]


def n8n(path: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(N8N_HOST + path, data=data, method=method, headers={"X-N8N-API-KEY": n8n_key, "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as response:
            text = response.read().decode()
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"n8n API {exc.code}: {exc.read().decode(errors='replace')[:500]}") from exc


def ghl_opportunities(from_date: str, to_date: str) -> set[str]:
    tz = ZoneInfo("America/Los_Angeles")
    start = int(datetime.fromisoformat(from_date).replace(tzinfo=tz).timestamp() * 1000)
    end = int((datetime.fromisoformat(to_date) + timedelta(days=1)).replace(tzinfo=tz).timestamp() * 1000) - 1
    ids: set[str] = set()
    cursor = cursor_id = ""
    for _ in range(10):
        query = {"location_id": LOCATION_ID, "status": "all", "date": str(start), "endDate": str(end), "limit": "100"}
        if cursor:
            query["startAfter"] = cursor
        if cursor_id:
            query["startAfterId"] = cursor_id
        url = GHL_HOST + "/opportunities/search?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ghl_key}", "Version": "2021-07-28", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as response:
            result = json.loads(response.read())
        ids.update(str(row.get("id")) for row in result.get("opportunities", []) if row.get("id"))
        meta = result.get("meta", {})
        if not meta.get("nextPageUrl") or not meta.get("startAfter") or not meta.get("startAfterId"):
            break
        cursor, cursor_id = str(meta["startAfter"]), str(meta["startAfterId"])
    return ids


def normalize_rows(value):
    while isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, dict):
        for key in ("data", "rows", "result", "body"):
            if key in value and isinstance(value[key], (list, str, dict)):
                value = value[key]
                break
    if isinstance(value, dict):
        value = [value]
    if isinstance(value, list) and value and isinstance(value[0], dict) and isinstance(value[0].get("json"), dict):
        value = [item["json"] for item in value]
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise TypeError("Temporary raw-ID query returned an unexpected response shape")
    return value


sql_rows = """
WITH normalized AS (
  SELECT NULLIF(source_key,'') AS opportunity_id,
    COALESCE(NULLIF(dimensions_json->>'source_created_at','')::timestamptz,
             NULLIF(payload_json->>'createdAt','')::timestamptz,
             NULLIF(payload_json->>'dateAdded','')::timestamptz) AS source_created_at,
    COALESCE(NULLIF(dimensions_json->>'source_created_at','')::timestamptz,
             NULLIF(payload_json->>'createdAt','')::timestamptz,
             NULLIF(payload_json->>'dateAdded','')::timestamptz,
             report_date::timestamptz) AS effective_created_at,
    report_date
  FROM report_raw_ghl_opportunities
  WHERE NULLIF(source_key,'') IS NOT NULL
), first_seen AS (
  SELECT opportunity_id,
    MIN((effective_created_at AT TIME ZONE 'America/Los_Angeles')::date) AS effective_date,
    MIN((source_created_at AT TIME ZONE 'America/Los_Angeles')::date) FILTER (WHERE source_created_at IS NOT NULL) AS actual_source_date,
    BOOL_OR(source_created_at IS NULL) AS has_fallback_timestamp
  FROM normalized GROUP BY opportunity_id
)
SELECT COALESCE(json_agg(row_to_json(x) ORDER BY x.opportunity_id), '[]'::json) AS rows
FROM (
  SELECT opportunity_id, effective_date::text, actual_source_date::text, has_fallback_timestamp
  FROM first_seen
  WHERE effective_date BETWEEN '{{FROM}}'::date AND '{{TO}}'::date
) x
"""


workflow_path = "v1-band1-opportunity-id-audit-" + uuid.uuid4().hex
nodes = [
    {"id": str(uuid.uuid4()), "webhookId": str(uuid.uuid4()), "name": "Audit Request", "type": "n8n-nodes-base.webhook", "typeVersion": 2.1, "position": [240, 300], "parameters": {"httpMethod": "POST", "path": workflow_path, "responseMode": "lastNode", "options": {}}},
    {"id": str(uuid.uuid4()), "name": "Read V1 Raw IDs", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6, "position": [500, 300], "parameters": {"operation": "executeQuery", "query": sql_rows.replace("{{FROM}}", "2026-10-04").replace("{{TO}}", "2026-10-10"), "options": {}}, "credentials": PG_CREDENTIAL},
]
connections = {"Audit Request": {"main": [[{"node": "Read V1 Raw IDs", "type": "main", "index": 0}]]}}

created_id = ""
try:
    _, created = n8n("/api/v1/workflows", "POST", {"name": "TEMP - V1 Band 1 Opportunity ID Reconciliation", "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1", "saveDataSuccessExecution": "none", "saveDataErrorExecution": "none"}})
    created_id = str(created.get("id") or "")
    if not created_id:
        raise SystemExit("Temporary reconciliation workflow was not created")
    n8n(f"/api/v1/workflows/{created_id}/activate", "POST")
    webhook_url = N8N_HOST + "/webhook/" + workflow_path
    webhook_req = urllib.request.Request(webhook_url, data=b"{}", method="POST", headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(webhook_req, timeout=90, context=ssl.create_default_context()) as response:
        raw_rows = json.loads(response.read())
    raw_rows = normalize_rows(raw_rows)
    for start_date, end_date in periods:
        # The temporary query's fixed bounds are overwritten per period by the
        # same SQL text using n8n's credentialed PostgreSQL execution.
        sql = sql_rows.replace("{{FROM}}", start_date).replace("{{TO}}", end_date)
        if (start_date, end_date) == periods[0]:
            raw = {str(x["opportunity_id"]): x for x in raw_rows if x.get("opportunity_id")}
        else:
            # Re-run the read-only SQL through the same temporary workflow by
            # updating its query parameter, then call its webhook again.
            _, wf = n8n(f"/api/v1/workflows/{created_id}")
            node = next(x for x in wf["nodes"] if x["name"] == "Read V1 Raw IDs")
            node["parameters"]["query"] = sql
            n8n(f"/api/v1/workflows/{created_id}/deactivate", "POST")
            n8n(f"/api/v1/workflows/{created_id}", "PUT", {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {})})
            n8n(f"/api/v1/workflows/{created_id}/activate", "POST")
            with urllib.request.urlopen(webhook_req, timeout=90, context=ssl.create_default_context()) as response:
                raw_rows = json.loads(response.read())
            raw_rows = normalize_rows(raw_rows)
            raw = {str(x["opportunity_id"]): x for x in raw_rows if x.get("opportunity_id")}
        live = ghl_opportunities(start_date, end_date)
        print(json.dumps({"window": [start_date, end_date], "raw_snapshot_ids": len(raw), "live_api_ids": len(live), "snapshot_only": sorted(set(raw)-live), "live_only": sorted(live-set(raw)), "snapshot_only_fallback_timestamp": sorted(k for k,v in raw.items() if k not in live and v.get("has_fallback_timestamp"))}, sort_keys=True))
finally:
    if created_id:
        try:
            n8n(f"/api/v1/workflows/{created_id}/deactivate", "POST")
            n8n(f"/api/v1/workflows/{created_id}", "DELETE")
        except Exception:
            pass
