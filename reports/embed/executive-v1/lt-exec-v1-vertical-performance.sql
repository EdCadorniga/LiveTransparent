-- Contact Vertical comes from the latest raw GHL contact, not campaign names.
-- Counts match the existing V1 cohort/date rules. Missing contact/field -> Unclassified.
-- Responses are captured inbound SLA events, not proof of campaign response.
-- Sends/revenue stay unavailable until complete contact-level sources reconcile.
vertical_contacts AS (
  SELECT regexp_replace(source_key,'^contact:','') AS contact_id,
    COALESCE(NULLIF(trim((SELECT f->>'value'
      FROM jsonb_array_elements(CASE WHEN jsonb_typeof(payload_json->'customFields')='array'
        THEN payload_json->'customFields' ELSE '[]'::jsonb END) f
      WHERE f->>'id'='ODs8fBt5te5HEfSJ91pY' LIMIT 1)),''),'Unclassified') AS vertical
  FROM (SELECT DISTINCT ON (source_key) source_key,payload_json
    FROM report_raw_ghl_contacts WHERE source_system='ghl'
    ORDER BY source_key,report_date DESC,loaded_at DESC) c
), vertical_events AS (
  SELECT regexp_replace(source_key,'^contact:','') AS contact_id,'leads'::text AS metric,source_key AS event_id
  FROM contact_creation_facts WHERE COALESCE(created_date,first_observed_date) BETWEEN $1::date AND $2::date
    AND NOT COALESCE(is_linkedin_backfill,FALSE)
  UNION ALL
  SELECT regexp_replace(source_key,'^contact:',''),'linkedin_backfills',source_key
  FROM contact_creation_facts WHERE COALESCE(created_date,first_observed_date) BETWEEN $1::date AND $2::date
    AND COALESCE(is_linkedin_backfill,FALSE)
  UNION ALL
  SELECT regexp_replace(o.contact_id,'^contact:',''),'sqls',s.opportunity_id
  FROM feedback_sql s LEFT JOIN latest_feedback_opps o USING(opportunity_id)
  WHERE s.entered_at BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT regexp_replace(o.contact_id,'^contact:',''),'mqls',m.opportunity_id
  FROM feedback_mql m LEFT JOIN latest_feedback_opps o USING(opportunity_id)
  WHERE m.entered_at BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT DISTINCT regexp_replace(contact_id,'^contact:',''),'meetings',contact_id
  FROM lt_exec_v1_appointment_facts
  WHERE (start_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
    AND calendar_id='SrtXcFVyea7pFl3nTiIK' AND NULLIF(contact_id,'') IS NOT NULL
  UNION ALL
  SELECT regexp_replace(contact_id,'^contact:',''),'responses',source_event_id
  FROM response_events
  UNION ALL
  SELECT regexp_replace(contact_id,'^contact:',''),'won',opportunity_id
  FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed won','won','closed_won')
    AND observed_date BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT regexp_replace(contact_id,'^contact:',''),'lost',opportunity_id
  FROM latest_feedback_opps WHERE lower(COALESCE(stage_name,opp_status,'')) IN('closed lost','lost','closed_lost')
    AND observed_date BETWEEN $1::date AND $2::date
), vertical_totals AS (
  SELECT COALESCE(c.vertical,'Unclassified') AS vertical,
    COUNT(*) FILTER(WHERE metric='leads')::int AS leads,
    COUNT(*) FILTER(WHERE metric='linkedin_backfills')::int AS linkedin_backfills,
    COUNT(*) FILTER(WHERE metric='mqls')::int AS mqls,
    COUNT(*) FILTER(WHERE metric='sqls')::int AS sqls,
    COUNT(*) FILTER(WHERE metric='meetings')::int AS meetings,
    COUNT(*) FILTER(WHERE metric='responses')::int AS responses,
    COUNT(*) FILTER(WHERE metric='won')::int AS won,
    COUNT(*) FILTER(WHERE metric='lost')::int AS lost
  FROM vertical_events e LEFT JOIN vertical_contacts c USING(contact_id) GROUP BY 1
), vertical_performance AS (
  SELECT v.vertical,COALESCE(t.leads,0) AS leads,COALESCE(t.linkedin_backfills,0) AS linkedin_backfills,
    COALESCE(t.mqls,0) AS mqls,COALESCE(t.sqls,0) AS sqls,COALESCE(t.meetings,0) AS meetings,
    COALESCE(t.responses,0) AS responses,COALESCE(t.won,0) AS won,COALESCE(t.lost,0) AS lost,
    NULL::int AS sends,NULL::numeric AS revenue,
    'Latest contact Vertical; LA date rules; responses = captured inbound events; sends/revenue unavailable'::text AS basis
  FROM (SELECT DISTINCT vertical FROM vertical_contacts UNION SELECT 'Unclassified') v
  LEFT JOIN vertical_totals t USING(vertical)
)
