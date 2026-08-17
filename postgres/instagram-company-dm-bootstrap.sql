-- Company Instagram page outreach state and audit tables.
-- Apply as a deployment migration; production workflows must not run DDL.

CREATE TABLE IF NOT EXISTS instagram_company_dm_state (
  id BIGSERIAL PRIMARY KEY,
  campaign_key TEXT NOT NULL CHECK (campaign_key IN ('partnerships', 'dan_brands', 'dan_dispensaries')),
  campaign_priority SMALLINT NOT NULL CHECK (campaign_priority BETWEEN 1 AND 3),
  platform TEXT NOT NULL DEFAULT 'instagram' CHECK (platform = 'instagram'),
  source_sheet TEXT NOT NULL,
  source_row INTEGER,
  source_tag TEXT NOT NULL,
  company_name TEXT NOT NULL,
  normalized_username TEXT NOT NULL,
  profile_url TEXT NOT NULL,
  unipile_account_id TEXT NOT NULL,
  instagram_profile_provider_id TEXT NOT NULL DEFAULT '',
  instagram_chat_attendee_id TEXT NOT NULL DEFAULT '',
  instagram_chat_id TEXT NOT NULL DEFAULT '',
  primary_ghl_contact_id TEXT NOT NULL DEFAULT '',
  associated_ghl_contact_ids TEXT[] NOT NULL DEFAULT '{}',
  identity_status TEXT NOT NULL DEFAULT 'candidate',
  identity_account_type TEXT NOT NULL DEFAULT '',
  identity_is_business BOOLEAN,
  identity_category TEXT NOT NULL DEFAULT '',
  resolution_method TEXT NOT NULL DEFAULT 'source_sheet',
  resolution_confidence TEXT NOT NULL DEFAULT 'review_required',
  message_step INTEGER NOT NULL DEFAULT 0 CHECK (message_step BETWEEN 0 AND 3),
  sequence_status TEXT NOT NULL DEFAULT 'pending',
  first_week_message1_only BOOLEAN NOT NULL DEFAULT true,
  started_at TIMESTAMPTZ,
  last_sent_at TIMESTAMPTZ,
  next_due_at TIMESTAMPTZ,
  last_message_id TEXT NOT NULL DEFAULT '',
  last_message_hash TEXT NOT NULL DEFAULT '',
  reply_status TEXT NOT NULL DEFAULT '',
  reply_detected_at TIMESTAMPTZ,
  suppressed_at TIMESTAMPTZ,
  failure_reason TEXT NOT NULL DEFAULT '',
  claim_owner TEXT NOT NULL DEFAULT '',
  claimed_at TIMESTAMPTZ,
  workflow_run_id TEXT NOT NULL DEFAULT '',
  raw_source JSONB NOT NULL DEFAULT '{}'::jsonb,
  profile_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (unipile_account_id, normalized_username)
);

CREATE UNIQUE INDEX IF NOT EXISTS instagram_company_dm_state_profile_uq
  ON instagram_company_dm_state (unipile_account_id, instagram_profile_provider_id)
  WHERE instagram_profile_provider_id <> '';

CREATE UNIQUE INDEX IF NOT EXISTS instagram_company_dm_state_chat_uq
  ON instagram_company_dm_state (unipile_account_id, instagram_chat_id)
  WHERE instagram_chat_id <> '';

CREATE INDEX IF NOT EXISTS instagram_company_dm_state_dispatch_idx
  ON instagram_company_dm_state (sequence_status, identity_status, campaign_priority, created_at)
  WHERE sequence_status IN ('pending', 'ready');

CREATE INDEX IF NOT EXISTS instagram_company_dm_state_ghl_idx
  ON instagram_company_dm_state (primary_ghl_contact_id)
  WHERE primary_ghl_contact_id <> '';

CREATE TABLE IF NOT EXISTS instagram_company_dm_send_log (
  id BIGSERIAL PRIMARY KEY,
  state_id BIGINT NOT NULL REFERENCES instagram_company_dm_state(id),
  campaign_key TEXT NOT NULL,
  message_step INTEGER NOT NULL CHECK (message_step BETWEEN 1 AND 3),
  message_text TEXT NOT NULL,
  message_hash TEXT NOT NULL,
  unipile_message_id TEXT NOT NULL DEFAULT '',
  unipile_chat_id TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL,
  error_status TEXT NOT NULL DEFAULT '',
  error_message TEXT NOT NULL DEFAULT '',
  workflow_run_id TEXT NOT NULL DEFAULT '',
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (state_id, message_step)
);

CREATE INDEX IF NOT EXISTS instagram_company_dm_send_log_date_idx
  ON instagram_company_dm_send_log (sent_at DESC, status);

CREATE TABLE IF NOT EXISTS instagram_company_dm_run (
  id BIGSERIAL PRIMARY KEY,
  run_date DATE NOT NULL,
  workflow_run_id TEXT NOT NULL,
  mode TEXT NOT NULL CHECK (mode IN ('dry_run', 'live')),
  daily_cap INTEGER NOT NULL DEFAULT 45,
  claimed_count INTEGER NOT NULL DEFAULT 0,
  sent_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  skipped_count INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (run_date, mode)
);

CREATE TABLE IF NOT EXISTS instagram_inbound_reply_events (
  id BIGSERIAL PRIMARY KEY,
  message_id TEXT NOT NULL UNIQUE,
  provider_message_id TEXT,
  unipile_account_id TEXT NOT NULL,
  instagram_chat_id TEXT,
  instagram_profile_provider_id TEXT,
  instagram_username TEXT,
  display_name TEXT,
  message_text TEXT NOT NULL,
  message_timestamp TIMESTAMPTZ,
  mapped_ghl_contact_id TEXT,
  campaign_key TEXT,
  company_name TEXT,
  raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  slack_claimed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS instagram_inbound_reply_events_identity_idx
  ON instagram_inbound_reply_events (unipile_account_id, instagram_profile_provider_id, instagram_chat_id);

CREATE INDEX IF NOT EXISTS instagram_inbound_reply_events_username_idx
  ON instagram_inbound_reply_events (unipile_account_id, LOWER(instagram_username));

CREATE TABLE IF NOT EXISTS instagram_activity_events (
  event_id BIGSERIAL PRIMARY KEY,
  event_key TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  event_at TIMESTAMPTZ NOT NULL,
  ghl_contact_id TEXT NOT NULL DEFAULT '',
  campaign_key TEXT NOT NULL DEFAULT 'instagram',
  chat_id TEXT NOT NULL DEFAULT '',
  message_id TEXT NOT NULL DEFAULT '',
  provider_id TEXT NOT NULL DEFAULT '',
  workflow_name TEXT NOT NULL DEFAULT '',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS instagram_activity_events_at_idx
  ON instagram_activity_events (event_at DESC);

CREATE INDEX IF NOT EXISTS instagram_activity_events_type_at_idx
  ON instagram_activity_events (event_type, event_at DESC);
