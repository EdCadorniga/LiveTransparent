-- Partnership Marketing Pipeline — Postgres Tables
-- Bootstrap via n8n or run directly against the Postgres database.

-- LinkedIn connection state (mirrors linkedin_connection_state for partnership contacts)
CREATE TABLE IF NOT EXISTS partnership_linkedin_connection_state (
  ghl_contact_id TEXT PRIMARY KEY,
  location_id TEXT NOT NULL DEFAULT 'Zwz4relUXVPxx8uohnjV',
  unipile_account_id TEXT NOT NULL DEFAULT 'V9eiHiDpRmCtan0YNdzsQw',
  linkedin_profile_url TEXT NOT NULL DEFAULT '',
  linkedin_public_identifier TEXT NOT NULL DEFAULT '',
  linkedin_provider_id TEXT NOT NULL DEFAULT '',
  connection_request_tag TEXT NOT NULL DEFAULT 'partner_linkedin_requested',
  connection_status TEXT NOT NULL DEFAULT 'ready',
  request_sent_at TIMESTAMPTZ,
  connected_at TIMESTAMPTZ,
  dm_sequence_started_at TIMESTAMPTZ,
  last_checked_at TIMESTAMPTZ,
  request_message TEXT,
  request_message_hash TEXT,
  sequence_step INTEGER NOT NULL DEFAULT 0,
  source_key TEXT NOT NULL DEFAULT 'partnership',
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS partnership_linkedin_connection_state_provider_uq
  ON partnership_linkedin_connection_state (unipile_account_id, linkedin_provider_id)
  WHERE linkedin_provider_id <> '';

CREATE UNIQUE INDEX IF NOT EXISTS partnership_linkedin_connection_state_identifier_uq
  ON partnership_linkedin_connection_state (unipile_account_id, linkedin_public_identifier)
  WHERE linkedin_public_identifier <> '';

CREATE INDEX IF NOT EXISTS partnership_linkedin_connection_state_status_idx
  ON partnership_linkedin_connection_state (connection_status, updated_at DESC);

CREATE INDEX IF NOT EXISTS partnership_linkedin_connection_state_source_idx
  ON partnership_linkedin_connection_state (source_key);

-- Email release log (tracks every sent email for deduplication and reporting)
CREATE TABLE IF NOT EXISTS partnership_release_log (
  id BIGSERIAL PRIMARY KEY,
  ghl_contact_id TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  email_step INTEGER NOT NULL CHECK (email_step BETWEEN 1 AND 4),
  status TEXT NOT NULL DEFAULT 'queued',
  ghl_message_id TEXT,
  ghl_conversation_id TEXT,
  sender_email TEXT NOT NULL DEFAULT 'cameron@livetransparent.com',
  release_date DATE NOT NULL DEFAULT CURRENT_DATE,
  release_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  run_id TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS partnership_release_log_uidx_contact_step
  ON partnership_release_log (ghl_contact_id, email_step);

CREATE INDEX IF NOT EXISTS partnership_release_log_idx_sender_date
  ON partnership_release_log (sender_email, release_date);

CREATE INDEX IF NOT EXISTS partnership_release_log_idx_status
  ON partnership_release_log (status, release_date);
