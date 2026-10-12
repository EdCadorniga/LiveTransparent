"""Read-only ID-level comparison: V1 raw opportunity facts vs live GHL."""

from __future__ import annotations

import json
import base64
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

sql_contact_audit = """
WITH rows AS (
  SELECT source_key,report_date,
    NULLIF(payload_json->>'createdAt','')::timestamptz AS created_at,
    NULLIF(payload_json->>'dateAdded','')::timestamptz AS date_added,
    COALESCE(NULLIF(dimensions_json->>'contact_id',''),NULLIF(payload_json->>'contactId',''),NULLIF(payload_json->>'contact_id','')) AS contact_id,
    lower(CONCAT_WS(' ',COALESCE(dimensions_json->>'source',''),COALESCE(payload_json->>'source',''),COALESCE(dimensions_json->>'utm_source_first',''),COALESCE(dimensions_json->>'utm_source_last',''),COALESCE(dimensions_json->>'tags',''),COALESCE(payload_json->>'tags',''))) AS marker
  FROM report_raw_ghl_contacts
), backfill_contacts AS (
  SELECT DISTINCT contact_id FROM rows
  WHERE NULLIF(contact_id,'') IS NOT NULL AND marker LIKE '%backfill%' AND (marker LIKE '%unipile%' OR marker LIKE '%historical%')
), summary_period AS (
  SELECT DISTINCT r.contact_id FROM rows r
  WHERE NULLIF(r.contact_id,'') IS NOT NULL
    AND DATE(COALESCE(r.created_at,r.date_added,NOW()) AT TIME ZONE 'America/Los_Angeles') BETWEEN '2026-10-04'::date AND '2026-10-10'::date
    AND NOT EXISTS (SELECT 1 FROM backfill_contacts b WHERE b.contact_id=r.contact_id)
), v1_exact AS (
  SELECT DISTINCT source_key FROM rows
  WHERE (COALESCE(created_at,report_date::timestamptz) AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04'::date AND '2026-10-10'::date
), actual_period AS (
  SELECT DISTINCT source_key FROM rows
  WHERE COALESCE(created_at,date_added) IS NOT NULL
    AND (COALESCE(created_at,date_added) AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04'::date AND '2026-10-10'::date
)
SELECT (SELECT COUNT(*) FROM v1_exact)::int AS current_v1_row_rule_count,
       (SELECT COUNT(*) FROM actual_period)::int AS actual_timestamp_count,
       (SELECT COUNT(*) FROM summary_period)::int AS executive_summary_like_count,
       (SELECT COUNT(*) FROM backfill_contacts b JOIN summary_period s USING(contact_id))::int AS backfill_in_summary_period,
       (SELECT COUNT(*) FROM v1_exact v WHERE NOT EXISTS (SELECT 1 FROM actual_period a WHERE a.source_key=v.source_key))::int AS v1_snapshot_fallback_excess
"""

sql_booking_audit = """
WITH opp_rows AS (
  SELECT NULLIF(source_key,'') AS opportunity_id,
    COALESCE(NULLIF(dimensions_json->>'contact_id',''),NULLIF(dimensions_json->>'contact.id',''),NULLIF(payload_json->>'contactId',''),NULLIF(payload_json->>'contact_id','')) AS contact_id,
    COALESCE(NULLIF(dimensions_json->>'pipeline_id',''),NULLIF(payload_json->>'pipelineId','')) AS pipeline_id,
    report_date::date AS observed_date, loaded_at, payload_json
  FROM report_raw_ghl_opportunities WHERE NULLIF(source_key,'') IS NOT NULL
), sql_cohort AS (
  SELECT opportunity_id,MIN(observed_date) AS entered_at,
    (ARRAY_AGG(contact_id ORDER BY observed_date,loaded_at) FILTER (WHERE NULLIF(contact_id,'') IS NOT NULL))[1] AS contact_id,
    (ARRAY_AGG(payload_json ORDER BY observed_date,loaded_at))[1] AS opportunity_payload
  FROM opp_rows WHERE pipeline_id='dhdlf3O4tymxFtHk4aqq'
  GROUP BY opportunity_id HAVING MIN(observed_date) BETWEEN '2026-10-04'::date AND '2026-10-10'::date
), contact_latest AS (
  SELECT c.*,r.source_key AS contact_key,r.dimensions_json AS contact_dimensions,r.payload_json AS contact_payload
  FROM sql_cohort c
  LEFT JOIN LATERAL (
    SELECT source_key,dimensions_json,payload_json FROM report_raw_ghl_contacts r
    WHERE COALESCE(NULLIF(r.dimensions_json->>'contact_id',''),NULLIF(r.payload_json->>'contactId',''),NULLIF(r.payload_json->>'contact_id',''),REPLACE(r.source_key,'contact:',''))=c.contact_id
    ORDER BY report_date DESC,loaded_at DESC LIMIT 1
  ) r ON TRUE
), appointment_latest AS (
  SELECT c.*,a.appointment_id,a.calendar_id,a.appointment_payload
  FROM contact_latest c
  LEFT JOIN LATERAL (
    SELECT appointment_id,calendar_id,payload_json AS appointment_payload FROM lt_exec_v1_appointment_facts
    WHERE contact_id=c.contact_id AND NULLIF(calendar_id,'') IS NOT NULL
      AND COALESCE(NULLIF(payload_json->>'dateAdded','')::timestamptz,start_at)
          BETWEEN ((c.entered_at::timestamp AT TIME ZONE 'America/Los_Angeles')-interval '365 days')
              AND ((c.entered_at::timestamp AT TIME ZONE 'America/Los_Angeles')+interval '30 days')
    ORDER BY ABS(EXTRACT(EPOCH FROM (COALESCE(NULLIF(payload_json->>'dateAdded','')::timestamptz,start_at)
      -(c.entered_at::timestamp AT TIME ZONE 'America/Los_Angeles')))) ASC,appointment_id LIMIT 1
  ) a ON TRUE
), attrs AS (
  SELECT a.*,
    EXISTS (SELECT 1 FROM jsonb_array_elements(CASE WHEN jsonb_typeof(a.opportunity_payload->'attributions')='array' THEN a.opportunity_payload->'attributions' ELSE '[]'::jsonb END) u
      WHERE COALESCE(NULLIF(u->>'utmSource',''),NULLIF(u->>'utmSessionSource',''),NULLIF(u->>'utmMedium',''),NULLIF(u->>'utmCampaign','')) IS NOT NULL) AS opp_has_utm,
    EXISTS (SELECT 1 FROM jsonb_array_elements(CASE WHEN jsonb_typeof(a.appointment_payload->'attributions')='array' THEN a.appointment_payload->'attributions' ELSE '[]'::jsonb END) u
      WHERE COALESCE(NULLIF(u->>'utmSource',''),NULLIF(u->>'utmSessionSource',''),NULLIF(u->>'utmMedium',''),NULLIF(u->>'utmCampaign','')) IS NOT NULL) AS appointment_has_utm,
    EXISTS (SELECT 1 FROM jsonb_array_elements(CASE WHEN jsonb_typeof(a.contact_payload->'attributions')='array' THEN a.contact_payload->'attributions' ELSE '[]'::jsonb END) u
      WHERE COALESCE(NULLIF(u->>'utmSource',''),NULLIF(u->>'utmSessionSource',''),NULLIF(u->>'utmMedium',''),NULLIF(u->>'utmCampaign','')) IS NOT NULL) AS contact_has_utm
  FROM appointment_latest a
), click_counts AS (
  SELECT contact_id,COUNT(*)::int AS clicks,MAX(clicked_at) AS last_click_at,
    MAX(NULLIF(utm_source,'')) AS click_source,MAX(NULLIF(utm_campaign,'')) AS click_campaign
  FROM lt_booking_link_clicks GROUP BY contact_id
)
SELECT COUNT(*)::int AS sql_count,
       COUNT(*) FILTER (WHERE contact_key IS NOT NULL)::int AS contact_snapshot_matches,
       COUNT(*) FILTER (WHERE contact_has_utm)::int AS contact_payload_attribution,
       COUNT(*) FILTER (WHERE opp_has_utm)::int AS opportunity_payload_attribution,
       COUNT(*) FILTER (WHERE appointment_has_utm)::int AS appointment_payload_attribution,
       COUNT(*) FILTER (WHERE COALESCE(c.clicks,0)>0)::int AS contacts_with_booking_clicks,
       COALESCE(SUM(c.clicks),0)::int AS booking_click_rows,
       COALESCE(json_agg(json_build_object('opp',a.opportunity_id,'sql_entered_at',a.entered_at,'contact',a.contact_id,'contact_key',a.contact_key,
         'contact_utms',a.contact_payload->'attributions','opportunity_utms',a.opportunity_payload->'attributions',
         'appointment_id',a.appointment_id,'calendar_id',a.calendar_id,'appointment_utms',a.appointment_payload->'attributions',
         'clicks',COALESCE(c.clicks,0),'last_click_at',c.last_click_at,'click_source',c.click_source,'click_campaign',c.click_campaign)
         ORDER BY a.opportunity_id),'[]'::json)::text AS details
FROM attrs a LEFT JOIN click_counts c USING(contact_id)
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
    _, wf = n8n(f"/api/v1/workflows/{created_id}")
    node = next(x for x in wf["nodes"] if x["name"] == "Read V1 Raw IDs")
    node["parameters"]["query"] = sql_contact_audit
    n8n(f"/api/v1/workflows/{created_id}/deactivate", "POST")
    n8n(f"/api/v1/workflows/{created_id}", "PUT", {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {})})
    n8n(f"/api/v1/workflows/{created_id}/activate", "POST")
    with urllib.request.urlopen(webhook_req, timeout=90, context=ssl.create_default_context()) as response:
        raw_rows = normalize_rows(json.loads(response.read()))
    print(json.dumps({"window": ["2026-10-04", "2026-10-10"], "contact_reconciliation": raw_rows[0]}, sort_keys=True))
    _, wf = n8n(f"/api/v1/workflows/{created_id}")
    node = next(x for x in wf["nodes"] if x["name"] == "Read V1 Raw IDs")
    node["parameters"]["query"] = sql_booking_audit
    n8n(f"/api/v1/workflows/{created_id}/deactivate", "POST")
    n8n(f"/api/v1/workflows/{created_id}", "PUT", {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {})})
    n8n(f"/api/v1/workflows/{created_id}/activate", "POST")
    with urllib.request.urlopen(webhook_req, timeout=90, context=ssl.create_default_context()) as response:
        raw_rows = normalize_rows(json.loads(response.read()))
    audit = raw_rows[0]
    detail_rows = json.loads(audit.get("details") or "[]")
    link_counts = {}
    contact_link_ids = {}
    latest_touch_links = {}
    all_link_records = {}
    for item in detail_rows:
        contact_id = str(item.get("contact") or "")
        for group in (item.get("contact_utms"), item.get("opportunity_utms"), item.get("appointment_utms")):
            for attribution in group if isinstance(group, list) else []:
                for field in ("url", "pageUrl", "referrer"):
                    value = str(attribution.get(field) or "")
                    marker = "/links/r/2/"
                    if marker not in value:
                        continue
                    token = value.split(marker, 1)[1].split("?", 1)[0]
                    try:
                        payload = token.split(".")[1]
                        payload += "=" * (-len(payload) % 4)
                        body = json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
                        link_id = str(body.get("link_id") or "")
                        if link_id:
                            link_counts[link_id] = link_counts.get(link_id, 0) + 1
                            contact_link_ids.setdefault(contact_id, set()).add(link_id)
                            sent_at = int(body.get("sentAt") or 0)
                            if sent_at:
                                key = (contact_id, link_id)
                                prev = all_link_records.get(key)
                                if not prev or sent_at > prev["sent_at"]:
                                    all_link_records[key] = {"contact_id": contact_id, "link_id": link_id, "sent_at": sent_at, "sql_entered_at": item.get("sql_entered_at")}
                            if attribution.get("isLast") and sent_at:
                                previous = latest_touch_links.get(contact_id)
                                if not previous or sent_at > previous["sent_at"]:
                                    latest_touch_links[contact_id] = {"link_id": link_id, "sent_at": sent_at, "sql_entered_at": item.get("sql_entered_at")}
                    except Exception:
                        pass
    recognized_links = {"dxi49iAhAFbdW5cXacD7": "Cannabis Ads website (email/outreach/wl_seq_cannabis_ads/visit_site)", "fRvpZgP1WOghlgY1ARiB": "Follow-up website (email/outreach/johnCannabis/visit_site_john)", "quqSUM8bckKaOIktVvgU": "Cannabis Ads booking (email/outreach/wl_seq_cannabis_ads/book_meeting)"}
    mapped = []
    for contact_id, value in latest_touch_links.items():
        if value["link_id"] in recognized_links:
            mapped.append({"contact_id": contact_id, "link_id": value["link_id"], "link_mapping": recognized_links[value["link_id"]], "clicked_at": datetime.fromtimestamp(value["sent_at"] / 1000, timezone.utc).isoformat(), "sql_entered_at": str(value["sql_entered_at"])})
    booking_ids = {"rmFtop1jXctXpz4kJa1l", "jxGQ0wfSQ3S4UcQsPHCQ", "FiHvJKjHuxfeg1arFRUj", "TEkdL5xGyUxXeCmYmAnb", "6fqPSWbqb3HVVZdlzk5N", "DUh8OO86BA4xPgub1neh", "ENEHOrItPwan00GnzyZZ", "DYoKxOSoet48F4GHzPBE", "quqSUM8bckKaOIktVvgU", "nqLFBlEsdm7qccr8Yyog"}
    booking_click_records = [dict(x, clicked_at=datetime.fromtimestamp(x["sent_at"] / 1000, timezone.utc).isoformat()) for x in all_link_records.values() if x["link_id"] in booking_ids]
    print(json.dumps({k: audit.get(k) for k in ["sql_count", "contact_snapshot_matches", "last_touch_utm_populated", "first_touch_utm_populated", "contacts_with_click_rows", "click_ledger_rows", "appointment_payload_attribution", "opportunity_payload_attribution"]} | {"attribution_link_id_counts": link_counts, "recognized_latest_touch_links": mapped, "booking_link_click_records": booking_click_records}, sort_keys=True))
finally:
    if created_id:
        try:
            n8n(f"/api/v1/workflows/{created_id}/deactivate", "POST")
            n8n(f"/api/v1/workflows/{created_id}", "DELETE")
        except Exception:
            pass
