"""Patch V1 Band 1 raw-fact dating and conversion metrics via n8n-lt REST.

Workflow JSON backups are written to the user temp directory; API keys are
loaded in memory only and are never emitted.
"""

from __future__ import annotations

import json
import os
import pathlib
import ssl
import urllib.error
import urllib.request
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
N8N_HOST = "https://automations.livetransparent.com"
FACTS_ID = "oxYDg6XnRBKhl1Xd"
MATERIALIZER_ID = "knc2wxe4pyYIJ5tw"


def env_values():
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


ENV = env_values()
KEY = ENV.get("N8N_LT_API_KEY")
if not KEY:
    raise SystemExit("N8N_LT_API_KEY unavailable")


def api(path, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(N8N_HOST + path, data=data, method=method, headers={"X-N8N-API-KEY": KEY, "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as res:
            text = res.read().decode()
            return res.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"n8n API HTTP {exc.code}: {exc.read().decode(errors='replace')[:600]}") from exc


def backup(workflow):
    base = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "Temp" / "v1_band1_workflow_backups"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{workflow['id']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")


CONTACT_CTE = """contact_creation_facts AS (
  SELECT source_key,
    MIN(COALESCE(
      (NULLIF(payload_json->>'createdAt','')::timestamptz AT TIME ZONE 'America/Los_Angeles')::date,
      (NULLIF(payload_json->>'dateAdded','')::timestamptz AT TIME ZONE 'America/Los_Angeles')::date
    )) AS created_date,
    MIN(report_date)::date AS first_observed_date,
    BOOL_OR(LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%historical backfill%'
         OR LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%unipile-backfill%'
         OR LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%linkedin via unipile%') AS is_linkedin_backfill
  FROM report_raw_ghl_contacts
  WHERE source_system='ghl' AND NULLIF(source_key,'') IS NOT NULL
  GROUP BY source_key
), authoritative_ghl_counts AS ("""

OLD_CONTACT_COUNT = """'new_contacts', (
      SELECT COUNT(DISTINCT NULLIF(source_key,''))::int
      FROM report_raw_ghl_contacts
      WHERE (COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz)
             AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
    ),"""
NEW_CONTACT_COUNT = """'new_contacts', (
      SELECT COUNT(*)::int FROM contact_creation_facts
      WHERE COALESCE(created_date, first_observed_date) BETWEEN $1::date AND $2::date
        AND NOT COALESCE(is_linkedin_backfill,FALSE)
    ),
    'linkedin_backfill_contacts', (
      SELECT COUNT(*)::int FROM contact_creation_facts
      WHERE COALESCE(created_date, first_observed_date) BETWEEN $1::date AND $2::date
        AND COALESCE(is_linkedin_backfill,FALSE)
    ),
    'new_contacts_date_unavailable', (
      SELECT COUNT(*)::int FROM contact_creation_facts
      WHERE first_observed_date BETWEEN $1::date AND $2::date AND created_date IS NULL
        AND NOT COALESCE(is_linkedin_backfill,FALSE)
    ),"""


facts = api(f"/api/v1/workflows/{FACTS_ID}")[1]
backup(facts)
fact_node = next(n for n in facts["nodes"] if n["name"] == "Build V1 Facts Query")
fact_code = fact_node["parameters"]["jsCode"]
cte_start = fact_code.find("WITH contact_creation_facts AS (")
cte_marker = "), authoritative_ghl_counts AS ("
cte_end = fact_code.find(cte_marker, cte_start) if cte_start >= 0 else -1
if cte_start >= 0 and cte_end >= 0:
    fact_code = fact_code[:cte_start] + "WITH " + CONTACT_CTE + fact_code[cte_end + len(cte_marker):]
elif "contact_creation_facts AS (" not in fact_code:
    if "WITH authoritative_ghl_counts AS (" not in fact_code:
        raise SystemExit("Facts SQL CTE anchor changed; no mutation performed")
    fact_code = fact_code.replace("WITH authoritative_ghl_counts AS (", "WITH " + CONTACT_CTE, 1)
if OLD_CONTACT_COUNT in fact_code:
    fact_code = fact_code.replace(OLD_CONTACT_COUNT, NEW_CONTACT_COUNT, 1)
elif NEW_CONTACT_COUNT not in fact_code:
    raise SystemExit("New-contact SQL anchor changed; no mutation performed")

old_booking_class = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN 'sdr' ELSE 'calendar_link' END AS booked_via,"
new_booking_class = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN 'sdr' WHEN a.appointment_id IS NOT NULL THEN 'calendar_link' ELSE 'unattributed' END AS booked_via,"
if old_booking_class in fact_code:
    fact_code = fact_code.replace(old_booking_class, new_booking_class, 1)
elif new_booking_class not in fact_code:
    raise SystemExit("SQL booking classification anchor changed; no mutation performed")

old_calendar_name = """CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN NULL
         ELSE COALESCE(ba.booked_via_campaign, ba.booked_via_vertical, NULLIF(c.dimensions_json->>'utm_content_last',''),
                       NULLIF(c.dimensions_json->>'utm_content_first',''),
                       NULLIF(a.payload_json->>'title',''), NULLIF(a.calendar_id,''),
                       'Calendar link (name not recorded)') END AS calendar_link_name,"""
new_calendar_name = """CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN NULL
         WHEN a.appointment_id IS NULL THEN 'No verified appointment/booking record'
         ELSE COALESCE(ba.booked_via_campaign, ba.booked_via_vertical, NULLIF(c.dimensions_json->>'utm_content_last',''),
                       NULLIF(c.dimensions_json->>'utm_content_first',''),
                       NULLIF(a.payload_json->>'title',''), NULLIF(a.calendar_id,''),
                       'Calendar link (name not recorded)') END AS calendar_link_name,"""
if old_calendar_name in fact_code:
    fact_code = fact_code.replace(old_calendar_name, new_calendar_name, 1)
elif new_calendar_name not in fact_code:
    raise SystemExit("SQL booking-detail label anchor changed; no mutation performed")

old_utm_gate = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN ''"
new_utm_gate = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr OR a.appointment_id IS NULL THEN ''"
if old_utm_gate in fact_code:
    fact_code = fact_code.replace(old_utm_gate, new_utm_gate, 1)
elif new_utm_gate not in fact_code:
    raise SystemExit("SQL booking UTM gate anchor changed; no mutation performed")

if "'sql_to_closed_rate'" not in fact_code:
    anchor = """'closed_lost_sqls',(SELECT COUNT(*)::int FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed lost','lost','closed_lost') AND observed_date BETWEEN $1::date AND $2::date),"""
    insert = anchor + """
    'sql_to_closed_rate',(SELECT CASE WHEN COUNT(*)=0 THEN NULL ELSE ROUND(
      (COUNT(*) FILTER (WHERE lower(COALESCE(o.stage_name,o.opp_status,'')) IN('closed won','won','closed_won','closed lost','lost','closed_lost')))::numeric/COUNT(*),4) END
      FROM feedback_sql s LEFT JOIN latest_feedback_opps o USING(opportunity_id)
      WHERE s.entered_at BETWEEN $1::date AND $2::date),"""
    if anchor not in fact_code:
        raise SystemExit("Funnel close-rate SQL anchor changed; no mutation performed")
    fact_code = fact_code.replace(anchor, insert, 1)

old_booking_class = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN 'sdr' ELSE 'calendar_link' END AS booked_via,"
new_booking_class = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN 'sdr' WHEN a.appointment_id IS NOT NULL THEN 'calendar_link' ELSE 'unattributed' END AS booked_via,"
if old_booking_class in fact_code:
    fact_code = fact_code.replace(old_booking_class, new_booking_class, 1)
elif new_booking_class not in fact_code:
    raise SystemExit("SQL booking classification anchor changed; no mutation performed")

old_calendar_name = """CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN NULL
         ELSE COALESCE(ba.booked_via_campaign, ba.booked_via_vertical, NULLIF(c.dimensions_json->>'utm_content_last',''),
                       NULLIF(c.dimensions_json->>'utm_content_first',''),
                       NULLIF(a.payload_json->>'title',''), NULLIF(a.calendar_id,''),
                       'Calendar link (name not recorded)') END AS calendar_link_name,"""
new_calendar_name = """CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN NULL
         WHEN a.appointment_id IS NULL THEN 'No verified appointment/booking record'
         ELSE COALESCE(ba.booked_via_campaign, ba.booked_via_vertical, NULLIF(c.dimensions_json->>'utm_content_last',''),
                       NULLIF(c.dimensions_json->>'utm_content_first',''),
                       NULLIF(a.payload_json->>'title',''), NULLIF(a.calendar_id,''),
                       'Calendar link (name not recorded)') END AS calendar_link_name,"""
if old_calendar_name in fact_code:
    fact_code = fact_code.replace(old_calendar_name, new_calendar_name, 1)
elif new_calendar_name not in fact_code:
    raise SystemExit("SQL booking detail label anchor changed; no mutation performed")

old_utm_gate = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr THEN ''"
new_utm_gate = "CASE WHEN origin_owner.is_sdr OR creator_owner.is_sdr OR a.appointment_id IS NULL THEN ''"
if old_utm_gate in fact_code:
    fact_code = fact_code.replace(old_utm_gate, new_utm_gate, 1)
elif new_utm_gate not in fact_code:
    raise SystemExit("SQL booking UTM gate anchor changed; no mutation performed")
fact_node["parameters"]["jsCode"] = fact_code

_, old_materializer = api(f"/api/v1/workflows/{MATERIALIZER_ID}")
backup(old_materializer)
mat_node = next(n for n in old_materializer["nodes"] if n.get("type") == "n8n-nodes-base.postgres")
mat_query = mat_node["parameters"].get("query", "")
old_first_seen = "COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz) AS first_seen_at,"
new_first_seen = """COALESCE(
      (SELECT MIN(COALESCE(NULLIF(r2.payload_json->>'createdAt','')::timestamptz,
                           NULLIF(r2.payload_json->>'dateAdded','')::timestamptz))
       FROM report_raw_ghl_contacts r2
       WHERE r2.source_system='ghl' AND r2.source_key=latest.contact_id
         AND COALESCE(NULLIF(r2.payload_json->>'createdAt','')::timestamptz,
                      NULLIF(r2.payload_json->>'dateAdded','')::timestamptz) IS NOT NULL),
      (SELECT MIN(r2.report_date)::timestamptz
       FROM report_raw_ghl_contacts r2
       WHERE r2.source_system='ghl' AND r2.source_key=latest.contact_id)
    ) AS first_seen_at,"""
if old_first_seen in mat_query:
    mat_query = mat_query.replace(old_first_seen, new_first_seen, 1)
elif "AS first_seen_at" not in mat_query or "dateAdded" not in mat_query:
    raise SystemExit("Materializer first-seen SQL anchor changed; no mutation performed")
old_filter = "WHERE NULLIF(source_key, '') IS NOT NULL\n  ORDER BY source_key, report_date DESC, loaded_at DESC"
new_filter = "WHERE source_system='ghl' AND NULLIF(source_key, '') IS NOT NULL\n  ORDER BY source_key, report_date DESC, loaded_at DESC"
if old_filter in mat_query:
    mat_query = mat_query.replace(old_filter, new_filter, 1)
elif "WHERE source_system='ghl' AND NULLIF(source_key, '') IS NOT NULL" not in mat_query:
    raise SystemExit("Materializer source filter anchor changed; no mutation performed")
mat_node["parameters"]["query"] = mat_query


def update_workflow(workflow):
    settings = dict(workflow.get("settings") or {})
    settings.pop("availableInMCP", None)
    api(f"/api/v1/workflows/{workflow['id']}", "PUT", {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow["connections"], "settings": settings})
    result = api(f"/api/v1/workflows/{workflow['id']}")[1]
    if result.get("versionId") != result.get("activeVersionId"):
        raise SystemExit(f"Workflow {workflow['id']} draft was not activated")
    return result


facts_after = update_workflow(facts)
mat_after = update_workflow(old_materializer)
print(json.dumps({"factsWorkflow": {"id": facts_after["id"], "name": facts_after["name"], "active": facts_after.get("active"), "versionId": facts_after.get("versionId"), "activeVersionId": facts_after.get("activeVersionId")}, "materializerWorkflow": {"id": mat_after["id"], "name": mat_after["name"], "active": mat_after.get("active"), "versionId": mat_after.get("versionId"), "activeVersionId": mat_after.get("activeVersionId")}}, indent=2))
