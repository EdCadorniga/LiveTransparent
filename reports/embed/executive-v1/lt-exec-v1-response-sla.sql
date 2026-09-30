-- Same-channel response-time facts for Executive Report V1.
-- The workflow uses the first later outbound event on the same channel/contact.

CREATE TABLE IF NOT EXISTS lt_exec_v1_response_sla (
  inbound_event_key TEXT PRIMARY KEY,
  contact_id TEXT,
  channel TEXT NOT NULL,
  inbound_event_type TEXT NOT NULL,
  inbound_at TIMESTAMPTZ NOT NULL,
  response_event_key TEXT,
  response_at TIMESTAMPTZ,
  response_seconds BIGINT,
  response_status TEXT NOT NULL,
  campaign_key TEXT,
  source_workflow TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_response_sla_window_idx ON lt_exec_v1_response_sla (channel, inbound_at);
CREATE INDEX IF NOT EXISTS lt_exec_v1_response_sla_status_idx ON lt_exec_v1_response_sla (response_status, channel);

-- Read-only review state. The approved reconciler may write this table after
-- detecting an existing GHL InternalComment; CRM note creation remains
-- intentionally outside this workflow.
CREATE TABLE IF NOT EXISTS lt_exec_v1_response_sla_reviews (
  inbound_event_key TEXT PRIMARY KEY REFERENCES lt_exec_v1_response_sla(inbound_event_key) ON DELETE CASCADE,
  review_status TEXT NOT NULL CHECK (review_status IN ('internal_note_done')),
  reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  reviewer TEXT,
  note_reference TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS lt_exec_v1_response_sla_reviews_status_idx
  ON lt_exec_v1_response_sla_reviews (review_status, reviewed_at);

WITH marketing_email_sends AS (
  SELECT contact_id, release_ts AS sent_at
  FROM "DAN_Release_Log"
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, release_ts
  FROM "Emerald_Release_Log"
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, release_ts
  FROM partnership_release_log
  WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL AND release_ts IS NOT NULL
  UNION ALL
  SELECT ghl_contact_id, sent_at
  FROM newsletter_send_log
  WHERE status IN ('sent','delivered','opened','clicked') AND sent_at IS NOT NULL AND NULLIF(ghl_contact_id,'') IS NOT NULL
), inbound AS (
  SELECT 'linkedin:' || event_key AS inbound_event_key, ghl_contact_id AS contact_id, 'linkedin' AS channel,
    event_type AS inbound_event_type, event_at AS inbound_at, campaign_key, workflow_name AS source_workflow
  FROM linkedin_activity_events
  WHERE event_type IN ('reply_received','inbound_reply') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:' || COALESCE(NULLIF(e.source_event_id,''), e.id::text), e.contact_id, 'email', lower(e.event_type), e.event_ts,
    e.campaign_key, e.workflow_id
  FROM "Email_Events" e
  WHERE lower(e.event_type) IN ('replied','reply','inbound_reply','reply_received') AND NULLIF(e.contact_id,'') IS NOT NULL
    AND EXISTS (SELECT 1 FROM marketing_email_sends m WHERE m.contact_id=e.contact_id AND m.sent_at < e.event_ts)
  UNION ALL
  SELECT 'call:ghl:' || call_id, contact_id, 'phone', 'inbound_call', started_at, NULL, 'report_raw_ghl_calls'
  FROM report_raw_ghl_calls
  WHERE lower(COALESCE(direction,'')) = 'inbound' AND NULLIF(contact_id,'') IS NOT NULL AND started_at IS NOT NULL
), outbound AS (
  SELECT 'linkedin:' || event_key AS response_event_key, ghl_contact_id AS contact_id, 'linkedin' AS channel, event_at AS response_at, campaign_key
  FROM linkedin_activity_events WHERE event_type = 'dm_sent' AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:dan:' || id::text, contact_id, 'email', release_ts, campaign_key
  FROM "DAN_Release_Log" WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:emerald:' || id::text, ghl_contact_id, 'email', release_ts, campaign_key
  FROM "Emerald_Release_Log" WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:partnership:' || id::text, ghl_contact_id, 'email', release_ts, campaign_key
  FROM partnership_release_log WHERE COALESCE(status,'sent') NOT IN ('failed','error','cancelled') AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'email:newsletter:' || id::text, ghl_contact_id, 'email', sent_at, campaign_key
  FROM newsletter_send_log WHERE status IN ('sent','delivered','opened','clicked') AND sent_at IS NOT NULL AND NULLIF(ghl_contact_id,'') IS NOT NULL
  UNION ALL
  SELECT 'call:ghl:' || call_id, contact_id, 'phone', started_at, NULL
  FROM report_raw_ghl_calls
  WHERE lower(COALESCE(direction,'')) = 'outbound' AND NULLIF(contact_id,'') IS NOT NULL AND started_at IS NOT NULL
  UNION ALL
  SELECT 'call:vapi:' || a.call_id::text, a.contact_id, 'phone', a.started_at, NULL
  FROM voice_call_attempt a
  WHERE NULLIF(a.contact_id,'') IS NOT NULL AND a.started_at IS NOT NULL
), matched AS (
  SELECT i.*, o.response_event_key, o.response_at,
    EXTRACT(EPOCH FROM (o.response_at - i.inbound_at))::bigint AS response_seconds,
    CASE WHEN o.response_event_key IS NULL THEN 'unmatched'
         WHEN o.same_timestamp_count > 1 THEN 'ambiguous'
         ELSE 'responded' END AS response_status,
    COALESCE(o.campaign_key, i.campaign_key) AS final_campaign_key
  FROM inbound i
  LEFT JOIN LATERAL (
    SELECT o.response_event_key, o.response_at, o.campaign_key,
      COUNT(*) OVER (PARTITION BY o.response_at) AS same_timestamp_count
    FROM outbound o
    WHERE o.contact_id=i.contact_id AND o.channel=i.channel AND o.response_at > i.inbound_at
    ORDER BY o.response_at, o.response_event_key
    LIMIT 1
  ) o ON TRUE
)
INSERT INTO lt_exec_v1_response_sla
  (inbound_event_key, contact_id, channel, inbound_event_type, inbound_at, response_event_key, response_at, response_seconds, response_status, campaign_key, source_workflow, loaded_at)
SELECT inbound_event_key, contact_id, channel, inbound_event_type, inbound_at, response_event_key, response_at, response_seconds, response_status, final_campaign_key, source_workflow, NOW()
FROM matched
ON CONFLICT (inbound_event_key) DO UPDATE SET
  contact_id=EXCLUDED.contact_id, channel=EXCLUDED.channel, inbound_event_type=EXCLUDED.inbound_event_type,
  inbound_at=EXCLUDED.inbound_at, response_event_key=EXCLUDED.response_event_key, response_at=EXCLUDED.response_at,
  response_seconds=EXCLUDED.response_seconds, response_status=EXCLUDED.response_status,
  campaign_key=EXCLUDED.campaign_key, source_workflow=EXCLUDED.source_workflow, loaded_at=NOW();

INSERT INTO report_source_health
  (source_system,status,last_success_at,last_attempt_at,last_row_count,stale_after_hours,last_error,metadata,updated_at)
SELECT 'exec_v1_response_sla', CASE WHEN COUNT(*)=0 THEN 'no_data' ELSE 'ready' END, NOW(), NOW(), COUNT(*)::int, 48, NULL,
  jsonb_build_object('workflow_name','LT - Executive Report V1 Response SLA Materializer',
    'responded',COUNT(*) FILTER (WHERE response_status='responded'),
    'unmatched',COUNT(*) FILTER (WHERE response_status='unmatched'),
    'ambiguous',COUNT(*) FILTER (WHERE response_status='ambiguous'),
    'internal_note_done',COUNT(*) FILTER (WHERE response_status='internal_note_done'),
    'channels',jsonb_object_agg(channel,channel_count)), NOW()
FROM lt_exec_v1_response_sla s
JOIN (SELECT channel,COUNT(*) channel_count FROM lt_exec_v1_response_sla GROUP BY channel) c USING(channel)
ON CONFLICT (source_system) DO UPDATE SET status=EXCLUDED.status,last_success_at=NOW(),last_attempt_at=NOW(),last_row_count=EXCLUDED.last_row_count,last_error=NULL,metadata=EXCLUDED.metadata,updated_at=NOW();

SELECT json_build_object('status','completed','facts',(SELECT COUNT(*) FROM lt_exec_v1_response_sla),'responded',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='responded'),'unmatched',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='unmatched'),'ambiguous',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='ambiguous'),'internal_note_done',(SELECT COUNT(*) FROM lt_exec_v1_response_sla WHERE response_status='internal_note_done')) AS result;
