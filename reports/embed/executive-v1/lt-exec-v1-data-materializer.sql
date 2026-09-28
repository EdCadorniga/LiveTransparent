-- Executive Report V1 derived facts. Execute through the dedicated n8n workflow.
-- This is additive and idempotent; raw reporting tables remain untouched.

CREATE TABLE IF NOT EXISTS lt_exec_v1_contact_provenance (
  contact_id TEXT PRIMARY KEY,
  first_seen_at TIMESTAMPTZ,
  source TEXT,
  medium TEXT,
  campaign TEXT,
  acquisition_mechanism TEXT NOT NULL DEFAULT 'unknown',
  mechanism_evidence TEXT,
  is_backfill BOOLEAN NOT NULL DEFAULT FALSE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_contact_provenance_mechanism_idx ON lt_exec_v1_contact_provenance (acquisition_mechanism);
CREATE INDEX IF NOT EXISTS lt_exec_v1_contact_provenance_first_seen_idx ON lt_exec_v1_contact_provenance (first_seen_at);

WITH latest AS (
  SELECT DISTINCT ON (source_key) NULLIF(source_key, '') AS contact_id, payload_json, dimensions_json, report_date, loaded_at
  FROM report_raw_ghl_contacts
  WHERE NULLIF(source_key, '') IS NOT NULL
  ORDER BY source_key, report_date DESC, loaded_at DESC
), normalized AS (
  SELECT contact_id,
    COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz) AS first_seen_at,
    COALESCE(NULLIF(payload_json->>'source',''), NULLIF(dimensions_json->>'source',''), NULLIF(payload_json->>'leadSource','')) AS source,
    COALESCE(NULLIF(payload_json->>'medium',''), NULLIF(dimensions_json->>'medium','')) AS medium,
    COALESCE(NULLIF(payload_json->>'campaign',''), NULLIF(dimensions_json->>'campaign','')) AS campaign,
    payload_json, lower(payload_json::text || ' ' || dimensions_json::text) AS haystack
  FROM latest
), classified AS (
  SELECT *,
    CASE
      WHEN haystack LIKE '%historical backfill%' OR haystack LIKE '%unipile-backfill%' OR haystack LIKE '%linkedin via unipile%' THEN 'linkedin_backfill'
      WHEN haystack LIKE '%apollo%' THEN 'apollo_upload'
      WHEN haystack LIKE '%form%' OR haystack LIKE '%website lead intake%' THEN 'form'
      WHEN haystack LIKE '%booking_widget%' OR haystack LIKE '%appointment%' THEN 'booking'
      WHEN COALESCE(source,'') <> '' OR COALESCE(medium,'') <> '' OR COALESCE(campaign,'') <> '' THEN 'attributed_source'
      ELSE 'unknown'
    END AS acquisition_mechanism,
    (haystack LIKE '%historical backfill%' OR haystack LIKE '%unipile-backfill%' OR haystack LIKE '%linkedin via unipile%') AS is_backfill
  FROM normalized
)
INSERT INTO lt_exec_v1_contact_provenance
  (contact_id, first_seen_at, source, medium, campaign, acquisition_mechanism, mechanism_evidence, is_backfill, payload_json, loaded_at)
SELECT contact_id, first_seen_at, source, medium, campaign, acquisition_mechanism,
  left(regexp_replace(haystack, '[\r\n]+', ' ', 'g'), 500), is_backfill, payload_json, NOW()
FROM classified
ON CONFLICT (contact_id) DO UPDATE SET
  first_seen_at=EXCLUDED.first_seen_at, source=EXCLUDED.source, medium=EXCLUDED.medium,
  campaign=EXCLUDED.campaign, acquisition_mechanism=EXCLUDED.acquisition_mechanism,
  mechanism_evidence=EXCLUDED.mechanism_evidence, is_backfill=EXCLUDED.is_backfill,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();

CREATE TABLE IF NOT EXISTS lt_exec_v1_appointment_facts (
  appointment_id TEXT PRIMARY KEY,
  contact_id TEXT,
  contact_name TEXT,
  calendar_id TEXT,
  assigned_user_id TEXT,
  status TEXT,
  start_at TIMESTAMPTZ,
  end_at TIMESTAMPTZ,
  attribution_confidence TEXT NOT NULL DEFAULT 'unresolved',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO lt_exec_v1_appointment_facts
  (appointment_id, contact_id, contact_name, calendar_id, assigned_user_id, status, start_at, end_at, attribution_confidence, payload_json, loaded_at)
SELECT a.appointment_id, a.contact_id,
  COALESCE(NULLIF(c.payload_json->>'name',''), NULLIF(trim(concat_ws(' ', c.payload_json->>'firstName', c.payload_json->>'lastName')), '')),
  a.calendar_id, a.assigned_user_id, a.status, a.start_at, a.end_at,
  CASE WHEN NULLIF(a.contact_id,'') IS NULL THEN 'unresolved' WHEN NULLIF(a.assigned_user_id,'') IS NOT NULL THEN 'appointment_assigned' ELSE 'contact_only' END,
  a.payload_json, NOW()
FROM report_raw_ghl_appointments a
LEFT JOIN LATERAL (
  SELECT payload_json FROM report_raw_ghl_contacts c
  WHERE c.source_key=a.contact_id ORDER BY c.report_date DESC, c.loaded_at DESC LIMIT 1
) c ON TRUE
ON CONFLICT (appointment_id) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, contact_name=EXCLUDED.contact_name, calendar_id=EXCLUDED.calendar_id,
  assigned_user_id=EXCLUDED.assigned_user_id, status=EXCLUDED.status, start_at=EXCLUDED.start_at,
  end_at=EXCLUDED.end_at, attribution_confidence=EXCLUDED.attribution_confidence,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();

CREATE TABLE IF NOT EXISTS lt_exec_v1_call_facts (
  call_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  contact_id TEXT,
  sdr_user_id TEXT,
  direction TEXT,
  disposition TEXT,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  campaign_id TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO lt_exec_v1_call_facts
  (call_key, source_system, contact_id, sdr_user_id, direction, disposition, started_at, ended_at, campaign_id, payload_json, loaded_at)
SELECT 'ghl:' || call_id, 'ghl', contact_id, assigned_user_id, direction, status, started_at,
  COALESCE(ended_at, started_at + make_interval(secs => GREATEST(COALESCE(duration_ms,0),0)::double precision / 1000.0)), NULL, payload_json, NOW()
FROM report_raw_ghl_calls WHERE NULLIF(call_id,'') IS NOT NULL
ON CONFLICT (call_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, sdr_user_id=EXCLUDED.sdr_user_id, direction=EXCLUDED.direction,
  disposition=EXCLUDED.disposition, started_at=EXCLUDED.started_at, ended_at=EXCLUDED.ended_at,
  payload_json=EXCLUDED.payload_json, loaded_at=NOW();
INSERT INTO lt_exec_v1_call_facts
  (call_key, source_system, contact_id, sdr_user_id, direction, disposition, started_at, ended_at, campaign_id, payload_json, loaded_at)
SELECT 'vapi:' || a.call_id::text, 'vapi', a.contact_id, NULL, 'outbound', a.disposition, a.started_at, a.ended_at,
  q.campaign_id, to_jsonb(a), NOW()
FROM voice_call_attempt a JOIN voice_call_queue q ON q.queue_id=a.queue_id
ON CONFLICT (call_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, disposition=EXCLUDED.disposition, started_at=EXCLUDED.started_at,
  ended_at=EXCLUDED.ended_at, campaign_id=EXCLUDED.campaign_id, payload_json=EXCLUDED.payload_json, loaded_at=NOW();

INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_contact_provenance', CASE WHEN (SELECT COUNT(*) FROM lt_exec_v1_contact_provenance)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), (SELECT COUNT(*)::int FROM lt_exec_v1_contact_provenance), 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'mechanism_counts',
    jsonb_object_agg(COALESCE(acquisition_mechanism,'unknown'), cnt)), NOW()
FROM (SELECT acquisition_mechanism, COUNT(*) cnt FROM lt_exec_v1_contact_provenance GROUP BY acquisition_mechanism) x
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_appointment_facts', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'unresolved', COUNT(*) FILTER (WHERE attribution_confidence='unresolved')), NOW()
FROM lt_exec_v1_appointment_facts
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();
INSERT INTO report_source_health
  (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at)
SELECT 'exec_v1_call_facts', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Data Materializer', 'source_counts',
    COALESCE((SELECT jsonb_object_agg(source_system,cnt) FROM (SELECT source_system, COUNT(*) cnt FROM lt_exec_v1_call_facts GROUP BY source_system) q), '{}'::jsonb)), NOW()
FROM lt_exec_v1_call_facts
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();

SELECT json_build_object('status','completed','contacts',(SELECT COUNT(*) FROM lt_exec_v1_contact_provenance),'appointments',(SELECT COUNT(*) FROM lt_exec_v1_appointment_facts),'calls',(SELECT COUNT(*) FROM lt_exec_v1_call_facts)) AS result;
