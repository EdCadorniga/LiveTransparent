-- LiveTransparent executive report bootstrap
-- Safe to apply on a fresh Postgres volume. The n8n workflows use these
-- tables as the durable reporting store for GA4, Search Console, and GHL.

CREATE TABLE IF NOT EXISTS report_config (
  config_key TEXT PRIMARY KEY,
  config_value JSONB NOT NULL DEFAULT '{}'::jsonb,
  notes TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_source_registry (
  source_system TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  is_required BOOLEAN NOT NULL DEFAULT TRUE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  notes TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_sync_watermarks (
  workflow_name TEXT NOT NULL,
  source_system TEXT NOT NULL,
  watermark_key TEXT NOT NULL,
  watermark_value TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (workflow_name, source_system, watermark_key)
);

CREATE TABLE IF NOT EXISTS report_sync_runs (
  run_id BIGSERIAL PRIMARY KEY,
  workflow_name TEXT NOT NULL,
  source_system TEXT,
  report_date DATE,
  batch_id TEXT,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  row_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  retry_count INTEGER NOT NULL DEFAULT 0,
  cursor_value TEXT,
  error_message TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS report_sync_runs_workflow_name_idx
  ON report_sync_runs (workflow_name, started_at DESC);

CREATE INDEX IF NOT EXISTS report_sync_runs_status_idx
  ON report_sync_runs (status, started_at DESC);

CREATE TABLE IF NOT EXISTS report_sync_errors (
  error_id BIGSERIAL PRIMARY KEY,
  run_id BIGINT,
  workflow_name TEXT NOT NULL,
  source_system TEXT,
  source_key TEXT,
  report_date DATE,
  error_category TEXT NOT NULL,
  error_message TEXT NOT NULL,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS report_sync_errors_run_id_idx
  ON report_sync_errors (run_id, created_at DESC);

CREATE INDEX IF NOT EXISTS report_sync_errors_workflow_name_idx
  ON report_sync_errors (workflow_name, created_at DESC);

CREATE TABLE IF NOT EXISTS report_source_health (
  source_system TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  last_success_at TIMESTAMPTZ,
  last_attempt_at TIMESTAMPTZ,
  last_row_count INTEGER NOT NULL DEFAULT 0,
  stale_after_hours INTEGER NOT NULL DEFAULT 48,
  last_error TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Raw layer

CREATE TABLE IF NOT EXISTS report_raw_ga4_sessions (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_sessions_uq
  ON report_raw_ga4_sessions (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ga4_sessions_report_date_idx
  ON report_raw_ga4_sessions (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ga4_pages (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_pages_uq
  ON report_raw_ga4_pages (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ga4_pages_report_date_idx
  ON report_raw_ga4_pages (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ga4_events (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ga4',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ga4_events_uq
  ON report_raw_ga4_events (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ga4_events_report_date_idx
  ON report_raw_ga4_events (report_date);

CREATE TABLE IF NOT EXISTS report_raw_gsc_queries (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_queries_uq
  ON report_raw_gsc_queries (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_gsc_queries_report_date_idx
  ON report_raw_gsc_queries (report_date);

CREATE TABLE IF NOT EXISTS report_raw_gsc_pages (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_pages_uq
  ON report_raw_gsc_pages (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_gsc_pages_report_date_idx
  ON report_raw_gsc_pages (report_date);

CREATE TABLE IF NOT EXISTS report_raw_gsc_site (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'gsc',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_gsc_site_uq
  ON report_raw_gsc_site (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_gsc_site_report_date_idx
  ON report_raw_gsc_site (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ghl_contacts (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_contacts_uq
  ON report_raw_ghl_contacts (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ghl_contacts_report_date_idx
  ON report_raw_ghl_contacts (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ghl_forms (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_forms_uq
  ON report_raw_ghl_forms (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ghl_forms_report_date_idx
  ON report_raw_ghl_forms (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ghl_opportunities (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_opportunities_uq
  ON report_raw_ghl_opportunities (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ghl_opportunities_report_date_idx
  ON report_raw_ghl_opportunities (report_date);

CREATE TABLE IF NOT EXISTS report_raw_ghl_pipeline_history (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  source_window_start DATE,
  source_window_end DATE,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  dimensions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  run_id BIGINT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_pipeline_history_uq
  ON report_raw_ghl_pipeline_history (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ghl_pipeline_history_report_date_idx
  ON report_raw_ghl_pipeline_history (report_date);

-- Bridge layer

CREATE TABLE IF NOT EXISTS report_bridge_identity_map (
  identity_type TEXT NOT NULL,
  identity_value TEXT NOT NULL,
  normalized_value TEXT NOT NULL,
  ghl_contact_id TEXT,
  ghl_opportunity_id TEXT,
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  first_seen_at TIMESTAMPTZ,
  last_seen_at TIMESTAMPTZ,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (identity_type, identity_value)
);

CREATE INDEX IF NOT EXISTS report_bridge_identity_map_normalized_idx
  ON report_bridge_identity_map (normalized_value);

CREATE TABLE IF NOT EXISTS report_bridge_traffic_to_lead (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  ga_session_id TEXT NOT NULL DEFAULT '',
  traffic_source TEXT,
  medium TEXT,
  campaign TEXT,
  landing_page TEXT,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  match_reason TEXT,
  source_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_bridge_traffic_to_lead_uq
  ON report_bridge_traffic_to_lead (report_date, ga_session_id, COALESCE(ghl_contact_id, ''));

CREATE INDEX IF NOT EXISTS report_bridge_traffic_to_lead_contact_idx
  ON report_bridge_traffic_to_lead (ghl_contact_id, report_date);

CREATE TABLE IF NOT EXISTS report_bridge_lead_to_sale (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  ghl_opportunity_id TEXT NOT NULL DEFAULT '',
  pipeline TEXT,
  stage TEXT,
  match_confidence NUMERIC(5,2) NOT NULL DEFAULT 0,
  match_rule TEXT,
  match_reason TEXT,
  source_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_bridge_lead_to_sale_uq
  ON report_bridge_lead_to_sale (report_date, COALESCE(ghl_contact_id, ''), COALESCE(ghl_opportunity_id, ''));

CREATE INDEX IF NOT EXISTS report_bridge_lead_to_sale_contact_idx
  ON report_bridge_lead_to_sale (ghl_contact_id, report_date);

-- Rollup layer

CREATE TABLE IF NOT EXISTS report_daily_summary (
  report_date DATE PRIMARY KEY,
  sessions INTEGER NOT NULL DEFAULT 0,
  users INTEGER NOT NULL DEFAULT 0,
  new_users INTEGER NOT NULL DEFAULT 0,
  engaged_sessions INTEGER NOT NULL DEFAULT 0,
  engagement_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  gsc_clicks INTEGER NOT NULL DEFAULT 0,
  gsc_impressions INTEGER NOT NULL DEFAULT 0,
  gsc_ctr NUMERIC(10,4) NOT NULL DEFAULT 0,
  gsc_position NUMERIC(10,4) NOT NULL DEFAULT 0,
  contacts_created INTEGER NOT NULL DEFAULT 0,
  form_submissions INTEGER NOT NULL DEFAULT 0,
  opportunities_created INTEGER NOT NULL DEFAULT 0,
  meetings_booked INTEGER NOT NULL DEFAULT 0,
  closed_won_count INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  closed_lost_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_channel_daily_summary (
  report_date DATE NOT NULL,
  channel TEXT NOT NULL,
  traffic_source TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT '',
  medium TEXT NOT NULL DEFAULT '',
  sessions INTEGER NOT NULL DEFAULT 0,
  users INTEGER NOT NULL DEFAULT 0,
  new_users INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, channel, traffic_source, source, medium)
);

CREATE TABLE IF NOT EXISTS report_funnel_daily_summary (
  report_date DATE PRIMARY KEY,
  traffic INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  sales INTEGER NOT NULL DEFAULT 0,
  contact_to_opportunity_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  opportunity_to_win_rate NUMERIC(10,4) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_pipeline_daily_summary (
  report_date DATE NOT NULL,
  pipeline TEXT NOT NULL,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  booked INTEGER NOT NULL DEFAULT 0,
  closed_won_count INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  closed_lost_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, pipeline)
);

CREATE TABLE IF NOT EXISTS report_stage_daily_summary (
  report_date DATE NOT NULL,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  stage_count INTEGER NOT NULL DEFAULT 0,
  moved_in_count INTEGER NOT NULL DEFAULT 0,
  moved_out_count INTEGER NOT NULL DEFAULT 0,
  won_count INTEGER NOT NULL DEFAULT 0,
  lost_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, pipeline, stage)
);

CREATE TABLE IF NOT EXISTS report_utm_daily_summary (
  report_date DATE NOT NULL,
  source TEXT NOT NULL DEFAULT '',
  medium TEXT NOT NULL DEFAULT '',
  campaign TEXT NOT NULL DEFAULT '',
  content TEXT NOT NULL DEFAULT '',
  term TEXT NOT NULL DEFAULT '',
  landing_page TEXT NOT NULL DEFAULT '',
  sessions INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, source, medium, campaign, content, term, landing_page)
);

CREATE TABLE IF NOT EXISTS report_landing_page_daily_summary (
  report_date DATE NOT NULL,
  landing_page TEXT NOT NULL,
  sessions INTEGER NOT NULL DEFAULT 0,
  engaged_sessions INTEGER NOT NULL DEFAULT 0,
  leads INTEGER NOT NULL DEFAULT 0,
  opportunities INTEGER NOT NULL DEFAULT 0,
  form_submissions INTEGER NOT NULL DEFAULT 0,
  closed_won_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, landing_page)
);

-- Light-touch bootstrap values so the workflows have a predictable baseline.
INSERT INTO report_source_registry (source_system, source_name, is_required, enabled, notes)
VALUES
  ('ga4', 'Google Analytics 4', TRUE, TRUE, 'Traffic source; blocked until property ID arrives.'),
  ('gsc', 'Google Search Console', TRUE, TRUE, 'Organic search source.'),
  ('ghl', 'GoHighLevel', TRUE, TRUE, 'CRM source of truth for leads and sales.')
ON CONFLICT (source_system) DO UPDATE
SET source_name = EXCLUDED.source_name,
    is_required = EXCLUDED.is_required,
    enabled = EXCLUDED.enabled,
    notes = EXCLUDED.notes,
    updated_at = NOW();

-- Idempotent SMS send log
-- Records each attempted send and prevents duplicate sends for the same
-- (contact_id, workflow_id, message_hash) combination.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS report_sms_sent (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id text NOT NULL,
  phone text NOT NULL,
  workflow_id text NOT NULL,
  template_id text,
  message_hash text NOT NULL,
  sent_at timestamptz NOT NULL DEFAULT now(),
  provider_response jsonb,
  CONSTRAINT ux_report_sms_unique UNIQUE (contact_id, workflow_id, message_hash)
);

CREATE INDEX IF NOT EXISTS idx_report_sms_sent_sent_at ON report_sms_sent (sent_at);
