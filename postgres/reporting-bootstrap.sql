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

CREATE TABLE IF NOT EXISTS report_raw_ghl_call_outcomes (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  source_system TEXT NOT NULL DEFAULT 'ghl',
  source_key TEXT NOT NULL,
  call_date TIMESTAMPTZ,
  direction TEXT,
  duration_seconds INTEGER,
  disposition TEXT,
  disposition_label TEXT,
  from_number TEXT,
  to_number TEXT,
  contact_id TEXT,
  contact_name TEXT,
  user_id TEXT,
  user_name TEXT,
  ghL_message_id TEXT,
  ghL_conversation_id TEXT,
  ghL_alt_id TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_uq
  ON report_raw_ghl_call_outcomes (source_system, report_date, source_key);

CREATE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_report_date_idx
  ON report_raw_ghl_call_outcomes (report_date);

CREATE INDEX IF NOT EXISTS report_raw_ghl_call_outcomes_disposition_idx
  ON report_raw_ghl_call_outcomes (disposition);

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
  emails_sent INTEGER NOT NULL DEFAULT 0,
  emails_opened INTEGER NOT NULL DEFAULT 0,
  emails_clicked INTEGER NOT NULL DEFAULT 0,
  emails_bounced INTEGER NOT NULL DEFAULT 0,
  emails_unsubscribed INTEGER NOT NULL DEFAULT 0,
  emails_complained INTEGER NOT NULL DEFAULT 0,
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

-- Pipeline velocity: per-stage avg days computed from actual pipeline history event timestamps
CREATE TABLE IF NOT EXISTS report_stage_velocity_summary (
  id SERIAL PRIMARY KEY,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  opp_count INTEGER NOT NULL DEFAULT 0,
  avg_days_in_stage NUMERIC(10,2) NOT NULL DEFAULT 0,
  min_days INTEGER NOT NULL DEFAULT 0,
  max_days INTEGER NOT NULL DEFAULT 0,
  median_days NUMERIC(10,2) NOT NULL DEFAULT 0,
  total_transitions INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (pipeline, stage)
);

-- Pipeline cycle: per-opportunity stage progression with timestamps
CREATE TABLE IF NOT EXISTS report_opp_stage_timeline (
  id SERIAL PRIMARY KEY,
  opportunity_id TEXT NOT NULL,
  pipeline TEXT NOT NULL,
  stage TEXT NOT NULL,
  entered_at TIMESTAMPTZ,
  exited_at TIMESTAMPTZ,
  days_in_stage NUMERIC(10,2) NOT NULL DEFAULT 0,
  is_final BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_opp_stage_timeline_opp ON report_opp_stage_timeline (opportunity_id);
CREATE INDEX IF NOT EXISTS idx_report_opp_stage_timeline_pipeline_stage ON report_opp_stage_timeline (pipeline, stage);

-- Light-touch bootstrap values so the workflows have a predictable baseline.
INSERT INTO report_source_registry (source_system, source_name, is_required, enabled, notes)
VALUES
  ('ga4', 'Google Analytics 4', TRUE, TRUE, 'Traffic source; active in production.'),
  ('gsc', 'Google Search Console', TRUE, TRUE, 'Organic search source.'),
  ('ghl', 'GoHighLevel', TRUE, TRUE, 'CRM source of truth for leads and sales.'),
  ('velocity', 'Pipeline Velocity', FALSE, TRUE, 'Per-stage avg days from pipeline history timestamps.')
ON CONFLICT (source_system) DO UPDATE
SET source_name = EXCLUDED.source_name,
    is_required = EXCLUDED.is_required,
    enabled = EXCLUDED.enabled,
    notes = EXCLUDED.notes,
  updated_at = NOW();

-- GHL Social Planner posts — ingested from /social-media-posting/{locationId}/posts/list
CREATE TABLE IF NOT EXISTS report_raw_ghl_social_posts (
  post_id TEXT PRIMARY KEY,
  account_id TEXT,
  platform TEXT,
  type TEXT,
  status TEXT,
  summary TEXT,
  error_message TEXT,
  published_at TIMESTAMPTZ,
  scheduled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  insights JSONB NOT NULL DEFAULT '{}'::jsonb,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_social_posts_platform ON report_raw_ghl_social_posts (platform, status);
CREATE INDEX IF NOT EXISTS idx_raw_social_posts_published ON report_raw_ghl_social_posts (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_social_posts_account ON report_raw_ghl_social_posts (account_id);

-- GHL Social Planner account statistics — ingested from /social-media-posting/statistics.
-- Stores rolled-up per-window totals (scope='all') plus per-platform rows so the report
-- can read exact completed 7/30/90-day windows. Reach/impressions/saves/engagement are
-- account analytics supplied by GHL, distinct from the post-placement ledger.
CREATE TABLE IF NOT EXISTS report_ghl_social_statistics (
  id BIGSERIAL PRIMARY KEY,
  window_start DATE NOT NULL,
  window_end DATE NOT NULL,
  scope TEXT NOT NULL,
  platform TEXT,
  posts INT,
  likes INT,
  followers INT,
  impressions INT,
  reach INT,
  comments INT,
  saves INT,
  source TEXT NOT NULL DEFAULT 'ghl_statistics',
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT report_ghl_social_statistics_uq UNIQUE (window_start, window_end, scope)
);

CREATE INDEX IF NOT EXISTS idx_ghl_social_statistics_window
  ON report_ghl_social_statistics (window_start, window_end);

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

-- GHL calls — raw conversation data for voice call tracking
CREATE TABLE IF NOT EXISTS report_raw_ghl_calls (
  call_id TEXT PRIMARY KEY,
  contact_id TEXT,
  assigned_user_id TEXT,
  location_id TEXT,
  direction TEXT,
  status TEXT,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  answered_at TIMESTAMPTZ,
  recording_url TEXT,
  notes TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_contact ON report_raw_ghl_calls (contact_id);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_status ON report_raw_ghl_calls (status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_calls_started_at ON report_raw_ghl_calls (started_at DESC);

-- GHL appointments — calendar event data for meeting tracking
CREATE TABLE IF NOT EXISTS report_raw_ghl_appointments (
  appointment_id TEXT PRIMARY KEY,
  contact_id TEXT,
  calendar_id TEXT,
  assigned_user_id TEXT,
  location_id TEXT,
  title TEXT,
  status TEXT,
  start_at TIMESTAMPTZ,
  end_at TIMESTAMPTZ,
  notes TEXT,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  batch_id TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_contact ON report_raw_ghl_appointments (contact_id);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_status ON report_raw_ghl_appointments (status, start_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_ghl_appts_start_at ON report_raw_ghl_appointments (start_at DESC);

-- Voice agent queue + transcript schema (v1)
CREATE TABLE IF NOT EXISTS voice_call_queue (
  queue_id uuid PRIMARY KEY,
  contact_id text NOT NULL,
  first_name text,
  phone_e164 text NOT NULL,
  campaign_id text NOT NULL,
  lead_timezone text,
  status text NOT NULL default 'pending',
  dnc boolean NOT NULL default false,
  max_attempts integer NOT NULL default 3,
  attempt_count integer NOT NULL default 0,
  phone_candidates jsonb,
  phone_index integer NOT NULL default 0,
  last_attempt_at timestamptz,
  next_attempt_at timestamptz,
  locked_at timestamptz,
  lock_owner text,
  created_at timestamptz NOT NULL default now(),
  updated_at timestamptz NOT NULL default now()
);

CREATE INDEX IF NOT EXISTS idx_voice_call_queue_status_next_attempt
  ON voice_call_queue(status, next_attempt_at);

CREATE TABLE IF NOT EXISTS voice_call_attempt (
  call_id uuid PRIMARY KEY,
  queue_id uuid NOT NULL REFERENCES voice_call_queue(queue_id),
  contact_id text NOT NULL,
  provider_call_id text,
  idempotency_key text NOT NULL UNIQUE,
  started_at timestamptz NOT NULL default now(),
  ended_at timestamptz,
  disposition text NOT NULL,
  qualified_intent_fit boolean NOT NULL default false,
  booking_attempted boolean NOT NULL default false,
  booking_result text NOT NULL default 'not_attempted',
  handoff_required boolean NOT NULL default false,
  handoff_reason text,
  summary text,
  transcript_url text,
  recording_url text,
  created_at timestamptz NOT NULL default now()
);

CREATE INDEX IF NOT EXISTS idx_voice_call_attempt_queue_id
  ON voice_call_attempt(queue_id);

CREATE TABLE IF NOT EXISTS voice_call_transcript_turn (
  turn_id bigserial PRIMARY KEY,
  call_id uuid NOT NULL REFERENCES voice_call_attempt(call_id) ON DELETE CASCADE,
  turn_index integer NOT NULL,
  speaker text NOT NULL,
  utterance text NOT NULL,
  timestamp_utc timestamptz NOT NULL,
  created_at timestamptz NOT NULL default now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_voice_call_transcript_turn_unique
  ON voice_call_transcript_turn(call_id, turn_index);

-- Meta Ads campaign/adset/ad name map — populated from Graph API
-- Used to resolve URL-encoded UTM values to human-readable campaign names
CREATE TABLE IF NOT EXISTS report_meta_campaign_map (
  id SERIAL PRIMARY KEY,
  ad_account_id TEXT NOT NULL,
  ad_account_name TEXT,
  campaign_id TEXT,
  campaign_name TEXT,
  campaign_status TEXT,
  adset_id TEXT,
  adset_name TEXT,
  adset_status TEXT,
  ad_id TEXT,
  ad_name TEXT,
  ad_status TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (ad_account_id, COALESCE(campaign_id, ''), COALESCE(adset_id, ''), COALESCE(ad_id, ''))
);

CREATE INDEX IF NOT EXISTS idx_meta_campaign_map_campaign_name
  ON report_meta_campaign_map (campaign_name);

CREATE INDEX IF NOT EXISTS idx_meta_campaign_map_adset_name
  ON report_meta_campaign_map (adset_name);

-- Meta Ads daily performance — time-series data from Insights API
CREATE TABLE IF NOT EXISTS report_meta_ads_daily_summary (
  report_date DATE NOT NULL,
  ad_account_id TEXT NOT NULL,
  ad_account_name TEXT,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  adset_id TEXT,
  adset_name TEXT,
  ad_id TEXT NOT NULL,
  ad_name TEXT NOT NULL,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  spend NUMERIC(12,2) DEFAULT 0,
  leads INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (report_date, ad_id)
);

CREATE INDEX IF NOT EXISTS idx_meta_ads_daily_date
  ON report_meta_ads_daily_summary (report_date DESC);

CREATE INDEX IF NOT EXISTS idx_meta_ads_daily_campaign
  ON report_meta_ads_daily_summary (campaign_name);

-- Seed campaign map from live Meta API query (2026-05-07)
-- act_975543647768982 — Livetransparent
INSERT INTO report_meta_campaign_map (ad_account_id, ad_account_name, campaign_id, campaign_name, campaign_status, adset_id, adset_name, adset_status, ad_id, ad_name, ad_status) VALUES
('act_975543647768982','Livetransparent','120247206237760159','Transparent-LeadForm-List','ACTIVE','120247206237750159','List-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120246336171860159','LV-Template','PAUSED','120246336171870159','New Traffic Ad Set','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120246017455700159','Transparent-Posts','PAUSED','120246017455690159','List-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241213439880159','Transparent-LeadForm-MJBizCon','ACTIVE','120241213439870159','Convention-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241212056450159','Transparent-Traffic-MJBiz','ACTIVE','120241300131650159','ConventionLAL-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241212056450159','Transparent-Traffic-MJBiz','ACTIVE','120241212056430159','Convention-11.20.25','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241058805550159','Transparent-Traffic','ACTIVE','120248139310460159','List-11.20.25 - Copy','ACTIVE',null,null,null),
('act_975543647768982','Livetransparent','120241058805550159','Transparent-Traffic','ACTIVE','120241058805570159','List-11.20.25','PAUSED',null,null,null),
('act_975543647768982','Livetransparent','120240619542520159','Transparent-LeadForm-Rem','ACTIVE','120240619542530159','List-11.20.25','ACTIVE',null,null,null),
-- act_24843211111954088 — Livetransparent-2 (HYPE)
('act_24843211111954088','Livetransparent-2','120244608199430363','HYPE-Stilo Supply - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244608199420363','Stilo Supply - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244608146670363','HYPE-Chkn''n Wafflez - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244608182680363','Chkn''n Wafflez - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244518262720363','Hyperwolf - Template','PAUSED','120244518262730363','Hyperwolf - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null),
('act_24843211111954088','Livetransparent-2','120244443459370363','HYPE-Hyperwolf - Shop Now V1 - April (Evergreen) - DTS','ACTIVE','120244443459380363','Hyperwolf - Shop Now V1 Ad 1 - April 22 to Evergreen - DTS','ACTIVE',null,null,null)
ON CONFLICT (ad_account_id, COALESCE(campaign_id, ''), COALESCE(adset_id, ''), COALESCE(ad_id, '')) DO UPDATE SET
  campaign_name = EXCLUDED.campaign_name, campaign_status = EXCLUDED.campaign_status,
  adset_name = EXCLUDED.adset_name, adset_status = EXCLUDED.adset_status,
  updated_at = NOW();

-- LinkedIn connection state store
CREATE TABLE IF NOT EXISTS linkedin_connection_state (
  ghl_contact_id TEXT PRIMARY KEY,
  location_id TEXT NOT NULL,
  unipile_account_id TEXT NOT NULL DEFAULT '',
  linkedin_profile_url TEXT NOT NULL DEFAULT '',
  linkedin_public_identifier TEXT NOT NULL DEFAULT '',
  linkedin_provider_id TEXT NOT NULL DEFAULT '',
  connection_request_tag TEXT NOT NULL DEFAULT 'linkedin_connection_requested',
  connection_status TEXT NOT NULL DEFAULT 'requested',
  request_sent_at TIMESTAMPTZ,
  connected_at TIMESTAMPTZ,
  dm_sequence_started_at TIMESTAMPTZ,
  last_checked_at TIMESTAMPTZ,
  request_message TEXT,
  request_message_hash TEXT,
  sequence_step INTEGER NOT NULL DEFAULT 0,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS linkedin_connection_state_provider_uq
  ON linkedin_connection_state (unipile_account_id, linkedin_provider_id)
  WHERE linkedin_provider_id <> '';

CREATE UNIQUE INDEX IF NOT EXISTS linkedin_connection_state_identifier_uq
  ON linkedin_connection_state (unipile_account_id, linkedin_public_identifier)
  WHERE linkedin_public_identifier <> '';

CREATE INDEX IF NOT EXISTS linkedin_connection_state_status_idx
  ON linkedin_connection_state (connection_status, updated_at DESC);
