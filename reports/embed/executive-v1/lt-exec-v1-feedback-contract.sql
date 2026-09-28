-- Reporting contract for Executive Report V1 feedback metrics.
-- Apply only after the underlying raw tables exist and the API workflow is reviewed.

CREATE TABLE IF NOT EXISTS lt_exec_v1_inbound_priority_events (
  contact_id TEXT NOT NULL,
  source_event_id TEXT NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('linkedin','call','voicemail','email')),
  event_at TIMESTAMPTZ NOT NULL,
  routing_reason TEXT NOT NULL,
  prior_opportunity_id TEXT,
  prior_stage_id TEXT,
  resulting_opportunity_id TEXT,
  resulting_stage_id TEXT,
  owner_id TEXT,
  disposition TEXT NOT NULL DEFAULT 'pending',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (contact_id, source_event_id)
);

CREATE INDEX IF NOT EXISTS lt_exec_v1_priority_events_at_idx
  ON lt_exec_v1_inbound_priority_events (event_at);
CREATE INDEX IF NOT EXISTS lt_exec_v1_priority_events_channel_idx
  ON lt_exec_v1_inbound_priority_events (channel, disposition);

-- Read-only reconciliation query used by the facts API implementation.
-- Verified live configuration: Sales Outreach = dhdlf3O4tymxFtHk4aqq;
-- Priority = be636da7-3c15-48ab-b589-c75bcd6f9955.
WITH windowed AS (
  SELECT * FROM lt_exec_v1_inbound_priority_events
  WHERE event_at >= $1::date AT TIME ZONE 'America/Los_Angeles'
    AND event_at < (($2::date + 1) AT TIME ZONE 'America/Los_Angeles')
), distinct_events AS (
  SELECT DISTINCT ON (contact_id, source_event_id) *
  FROM windowed ORDER BY contact_id, source_event_id, updated_at DESC
)
SELECT jsonb_build_object(
  'open_count', COUNT(*) FILTER (WHERE disposition IN ('routed','already_priority')),
  'created_in_window', COUNT(*) FILTER (WHERE disposition = 'created'),
  'by_source', COALESCE(jsonb_agg(jsonb_build_object('channel', channel, 'count', channel_count)), '[]'::jsonb),
  'basis', 'distinct contact_id + source_event_id; immutable inbound event key'
)
FROM distinct_events
JOIN (
  SELECT channel, COUNT(*)::int AS channel_count FROM distinct_events GROUP BY channel
) counts USING (channel);
