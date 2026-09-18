-- Generic GHL email-template mass-delivery ledger.
-- Apply as a bounded migration/schema operation only; sender workflows remain inactive.
-- Safe to re-run. This schema is intentionally separate from legacy newsletter tables.

BEGIN;

CREATE TABLE IF NOT EXISTS lt_mass_email_campaigns (
  id BIGSERIAL PRIMARY KEY,
  idempotency_key TEXT NOT NULL UNIQUE,
  campaign_key TEXT NOT NULL UNIQUE,
  template_id TEXT NOT NULL,
  template_name_snapshot TEXT,
  campaign_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'accepted',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS lt_mass_email_deliveries (
  id BIGSERIAL PRIMARY KEY,
  campaign_id BIGINT NOT NULL REFERENCES lt_mass_email_campaigns(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,
  recipient_email TEXT NOT NULL,
  sender_email TEXT NOT NULL,
  provider_message_id TEXT,
  provider_conversation_id TEXT,
  status TEXT NOT NULL DEFAULT 'planned',
  error TEXT,
  planned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  first_opened_at TIMESTAMPTZ,
  last_opened_at TIMESTAMPTZ,
  first_clicked_at TIMESTAMPTZ,
  last_clicked_at TIMESTAMPTZ,
  unsubscribed_at TIMESTAMPTZ,
  bounced_at TIMESTAMPTZ,
  UNIQUE (campaign_id, contact_id)
);

CREATE TABLE IF NOT EXISTS lt_mass_email_events (
  id BIGSERIAL PRIMARY KEY,
  delivery_id BIGINT NOT NULL REFERENCES lt_mass_email_deliveries(id) ON DELETE CASCADE,
  campaign_id BIGINT NOT NULL REFERENCES lt_mass_email_campaigns(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  event_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  link_url TEXT,
  ip TEXT,
  user_agent TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Additive columns required by the queue/dispatcher claim model. Safe to re-run;
-- column ordering of lt_mass_email_campaign_metrics is unaffected.
ALTER TABLE lt_mass_email_campaigns ADD COLUMN IF NOT EXISTS subject TEXT;
ALTER TABLE lt_mass_email_campaigns ADD COLUMN IF NOT EXISTS queued_at TIMESTAMPTZ;
ALTER TABLE lt_mass_email_campaigns ADD COLUMN IF NOT EXISTS planned_count INTEGER;
ALTER TABLE lt_mass_email_deliveries ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMPTZ;
ALTER TABLE lt_mass_email_deliveries ADD COLUMN IF NOT EXISTS run_id TEXT;

CREATE INDEX IF NOT EXISTS lt_mass_email_deliveries_campaign_status_idx
  ON lt_mass_email_deliveries (campaign_id, status);
CREATE INDEX IF NOT EXISTS lt_mass_email_deliveries_status_idx
  ON lt_mass_email_deliveries (status);
CREATE INDEX IF NOT EXISTS lt_mass_email_deliveries_provider_idx
  ON lt_mass_email_deliveries (provider_message_id)
  WHERE provider_message_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS lt_mass_email_events_campaign_type_idx
  ON lt_mass_email_events (campaign_id, event_type, event_ts);
CREATE INDEX IF NOT EXISTS lt_mass_email_events_delivery_type_idx
  ON lt_mass_email_events (delivery_id, event_type, event_ts);

-- Use correlated event aggregates so one delivery with repeated events cannot
-- multiply campaign-level planned/sent/delivered/bounced counts.
CREATE OR REPLACE VIEW lt_mass_email_campaign_metrics AS
SELECT
  c.id AS campaign_id,
  c.campaign_key,
  c.template_id,
  c.template_name_snapshot,
  c.campaign_name,
  COUNT(d.id)::int AS planned,
  COUNT(d.id) FILTER (WHERE d.status IN ('sent', 'delivered', 'opened', 'clicked'))::int AS sent,
  COUNT(d.id) FILTER (WHERE d.status = 'delivered')::int AS delivered,
  COUNT(d.id) FILTER (WHERE d.status = 'bounced')::int AS bounced,
  COALESCE(ev.unique_opens, 0)::int AS unique_opens,
  COALESCE(ev.total_opens, 0)::int AS total_opens,
  COALESCE(ev.unique_clicks, 0)::int AS unique_clicks,
  COALESCE(ev.total_clicks, 0)::int AS total_clicks,
  COALESCE(ev.unsubscribes, 0)::int AS unsubscribes,
  COALESCE(ev.complaints, 0)::int AS complaints,
  COALESCE(ev.replies, 0)::int AS replies,
  COALESCE(ev.failures, 0)::int AS failures
FROM lt_mass_email_campaigns c
LEFT JOIN lt_mass_email_deliveries d ON d.campaign_id = c.id
LEFT JOIN LATERAL (
  SELECT
    COUNT(*) FILTER (WHERE e.event_type = 'opened') AS total_opens,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'opened') AS unique_opens,
    COUNT(*) FILTER (WHERE e.event_type = 'clicked') AS total_clicks,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'clicked') AS unique_clicks,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'unsubscribed') AS unsubscribes,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'complained') AS complaints,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'replied') AS replies,
    COUNT(DISTINCT e.delivery_id) FILTER (WHERE e.event_type = 'failed') AS failures
  FROM lt_mass_email_events e
  WHERE e.campaign_id = c.id
) ev ON TRUE
GROUP BY c.id, c.campaign_key, c.template_id, c.template_name_snapshot,
         c.campaign_name, ev.total_opens, ev.unique_opens, ev.total_clicks,
         ev.unique_clicks, ev.unsubscribes, ev.complaints, ev.replies, ev.failures;

COMMIT;
