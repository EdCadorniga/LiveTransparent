"""Patch the V1 Facts API with a small, verified reporting-only contract."""

import json, os, urllib.request
from pathlib import Path
HOST = "https://automations.livetransparent.com"
ID = "oxYDg6XnRBKhl1Xd"

def env():
    d={}
    for line in (Path(__file__).resolve().parents[2]/".env").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            k,v=line.split("=",1); d[k.strip()]=v.strip().strip('"').strip("'")
    return d

def call(method="GET", payload=None):
    key=os.environ.get("N8N_API_KEY_LT") or env()["N8N_API_KEY_LT"]
    req=urllib.request.Request(f"{HOST}/api/v1/workflows/{ID}",
        data=None if payload is None else json.dumps(payload).encode(),
        method=method, headers={"X-N8N-API-KEY":key,"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r: return json.loads(r.read().decode())

CTES=r"""
, feedback_opps AS (
  SELECT NULLIF(o.source_key,'') AS opportunity_id,
    COALESCE(NULLIF(o.dimensions_json->>'contact_id',''),NULLIF(o.dimensions_json->>'contact.id',''),NULLIF(o.payload_json->>'contactId',''),NULLIF(o.payload_json->>'contact_id','')) AS contact_id,
    COALESCE(NULLIF(o.dimensions_json->>'pipeline_id',''),NULLIF(o.payload_json->>'pipelineId','')) AS pipeline_id,
    COALESCE(NULLIF(o.dimensions_json->>'pipeline_stage_id',''),NULLIF(o.payload_json->>'pipelineStageId','')) AS stage_id,
    COALESCE(NULLIF(o.dimensions_json->>'pipeline_stage_name',''),NULLIF(o.payload_json->>'pipelineStageName',''),NULLIF(o.payload_json->>'stage','')) AS stage_name,
    COALESCE(NULLIF(o.payload_json->>'status',''),NULLIF(o.dimensions_json->>'status','')) AS opp_status,
    COALESCE(NULLIF(o.payload_json->>'monetaryValue','')::numeric,NULLIF(o.payload_json->>'value','')::numeric,0)::numeric AS revenue,
    o.report_date::date AS observed_date,o.loaded_at
  FROM report_raw_ghl_opportunities o WHERE NULLIF(o.source_key,'') IS NOT NULL
), latest_feedback_opps AS (
  SELECT DISTINCT ON (opportunity_id) * FROM feedback_opps ORDER BY opportunity_id,observed_date DESC,loaded_at DESC
), feedback_mql AS (
  SELECT opportunity_id,MIN(observed_date) AS entered_at FROM feedback_opps WHERE stage_id='3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2' GROUP BY opportunity_id
), feedback_sql AS (
  SELECT opportunity_id,MIN(observed_date) AS entered_at FROM feedback_opps WHERE pipeline_id='dhdlf3O4tymxFtHk4aqq' GROUP BY opportunity_id
), feedback_funnel AS (
  SELECT jsonb_build_object(
    'available',EXISTS(SELECT 1 FROM feedback_opps WHERE observed_date BETWEEN $1::date AND $2::date),
    'opportunities_created',(SELECT COUNT(DISTINCT opportunity_id)::int FROM feedback_opps WHERE observed_date BETWEEN $1::date AND $2::date),
    'mqls_entered',(SELECT COUNT(*)::int FROM feedback_mql WHERE entered_at BETWEEN $1::date AND $2::date),
    'sqls_entered',(SELECT COUNT(*)::int FROM feedback_sql WHERE entered_at BETWEEN $1::date AND $2::date),
    'mql_to_sql_rate',(SELECT CASE WHEN COUNT(*)=0 THEN NULL ELSE ROUND(COUNT(*) FILTER(WHERE s.opportunity_id IS NOT NULL)::numeric/COUNT(*),4) END FROM feedback_mql m LEFT JOIN feedback_sql s USING(opportunity_id) WHERE m.entered_at BETWEEN $1::date AND $2::date),
    'closed_won_sqls',(SELECT COUNT(*)::int FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed won','won','closed_won') AND observed_date BETWEEN $1::date AND $2::date),
    'closed_lost_sqls',(SELECT COUNT(*)::int FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed lost','lost','closed_lost') AND observed_date BETWEEN $1::date AND $2::date),
    'revenue',(SELECT NULLIF(SUM(revenue),0) FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed won','won','closed_won') AND observed_date BETWEEN $1::date AND $2::date),
    'basis','distinct opportunity_id; first observed stage entry/latest outcome; America/Los_Angeles dates',
    'source_health','report_raw_ghl_opportunities'
  ) AS payload
), feedback_closed_source AS (
  SELECT COALESCE(NULLIF(cp.source,''),NULLIF(cp.campaign,''),'Unknown / Unattributed') AS source,
    COUNT(*) FILTER(WHERE lower(COALESCE(o.stage_name,o.opp_status,'')) IN('closed won','won','closed_won'))::int AS won,
    COUNT(*) FILTER(WHERE lower(COALESCE(o.stage_name,o.opp_status,'')) IN('closed lost','lost','closed_lost'))::int AS lost,
    NULLIF(SUM(o.revenue) FILTER(WHERE lower(COALESCE(o.stage_name,o.opp_status,'')) IN('closed won','won','closed_won')),0) AS revenue
  FROM latest_feedback_opps o LEFT JOIN lt_exec_v1_contact_provenance cp ON cp.contact_id=o.contact_id
  WHERE o.observed_date BETWEEN $1::date AND $2::date
  GROUP BY 1 ORDER BY won DESC,lost DESC,source
), feedback_weekly AS (
  SELECT COALESCE(jsonb_agg(jsonb_build_object(
    'week_start',w.week_start::date,
    'new_contacts',(SELECT COUNT(DISTINCT contact_id)::int FROM lt_exec_v1_contact_provenance WHERE (first_seen_at AT TIME ZONE 'America/Los_Angeles')::date>=w.week_start::date AND (first_seen_at AT TIME ZONE 'America/Los_Angeles')::date < w.week_start::date + 7),
    'mqls_entered',(SELECT COUNT(*)::int FROM feedback_mql WHERE entered_at>=w.week_start::date AND entered_at < w.week_start::date + 7),
    'sqls_entered',(SELECT COUNT(*)::int FROM feedback_sql WHERE entered_at>=w.week_start::date AND entered_at < w.week_start::date + 7),
    'later_stage_entries',(SELECT COUNT(DISTINCT opportunity_id)::int FROM feedback_opps WHERE observed_date>=w.week_start::date AND observed_date < w.week_start::date + 7 AND lower(COALESCE(stage_name,'')) IN('booked','meeting requested','discovery scheduled','proposal sent','negotiation','closed won','closed lost'))
  ) ORDER BY w.week_start),'[]'::jsonb) AS rows
  FROM generate_series(date_trunc('week',$1::date)::date,$2::date,interval '7 days') w(week_start)
), feedback_retargeting AS (
  SELECT jsonb_build_object(
    'available',EXISTS(SELECT 1 FROM newsletter_send_log WHERE sent_at >= $1::date AND sent_at < ($2::date+interval '1 day')),
    'audience_contacts',(SELECT COUNT(DISTINCT ghl_contact_id)::int FROM newsletter_send_log WHERE status='sent' AND sent_at >= $1::date AND sent_at < ($2::date+interval '1 day')),
    'clickers',(SELECT COUNT(DISTINCT contact_id)::int FROM newsletter_events WHERE lower(event_type) IN('clicked','click') AND event_ts >= $1::date AND event_ts < ($2::date+interval '1 day')),
    'suppressed_or_replied',(SELECT COUNT(DISTINCT contact_id)::int FROM newsletter_events WHERE lower(event_type) IN('unsubscribed','replied','reply') AND event_ts >= $1::date AND event_ts < ($2::date+interval '1 day')),
    'next_action_pending',NULL,
    'latest_touchpoints', '[]'::jsonb,
    'send_authorized',false,
    'basis','newsletter send/event ledgers; distinct contact IDs; read-only audience visibility'
  ) AS payload
), feedback_acquisition AS (
  SELECT COALESCE(jsonb_agg(jsonb_build_object('mechanism',acquisition_mechanism,'count',cnt,'backfill',backfill) ORDER BY cnt DESC),'[]'::jsonb) AS rows
  FROM(SELECT acquisition_mechanism,COUNT(*)::int AS cnt,BOOL_OR(is_backfill) AS backfill FROM lt_exec_v1_contact_provenance WHERE (first_seen_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date GROUP BY acquisition_mechanism)x
)
"""
def main():
    wf=call()
    if wf.get("versionId") != wf.get("activeVersionId"): raise RuntimeError("draft is not active")
    node=next(n for n in wf["nodes"] if n.get("name")=="Build V1 Facts Query")
    code=node["parameters"]["jsCode"]
    # Restore to the known-good query if a failed experimental extension is present.
    if "feedback_opps AS (" in code:
        original=json.loads(Path("tmp_v1_facts_workflow.json").read_text(encoding="utf-8"))
        node=next(n for n in original["nodes"] if n.get("name")=="Build V1 Facts Query")
        code=node["parameters"]["jsCode"]
        wf["nodes"]=original["nodes"]
    code=code.replace(", response_events AS (", CTES+", response_events AS (", 1)
    additions="""  'funnel',(SELECT payload FROM feedback_funnel),
  'closedBySource',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM feedback_closed_source x),
  'weeklyLeadFlow',(SELECT rows FROM feedback_weekly),
  'verticalPerformance', '[]'::jsonb,
  'retargeting',(SELECT payload FROM feedback_retargeting),
  'contactAcquisition',(SELECT rows FROM feedback_acquisition),
"""
    code=code.replace("  'window', jsonb_build_object('from',$1::date,'to',$2::date),",additions+"  'window', jsonb_build_object('from',$1::date,'to',$2::date),",1)
    node=next(n for n in wf["nodes"] if n.get("name")=="Build V1 Facts Query")
    node["parameters"]["jsCode"]=code
    settings={k:v for k,v in (wf.get("settings") or {}).items() if k!="availableInMCP"}
    saved=call("PUT",{"name":wf["name"],"nodes":wf["nodes"],"connections":wf["connections"],"settings":settings})
    print(json.dumps({"versionId":saved.get("versionId"),"activeVersionId":saved.get("activeVersionId"),"active":saved.get("active")} ,indent=2))
if __name__=="__main__": main()
