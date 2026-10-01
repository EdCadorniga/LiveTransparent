-- Dedicated Unipile V2 Sales Navigator bridge state.
-- This schema is intentionally disjoint from Classic/Instagram identity maps.

-- OAuth state, access tokens, and refresh tokens are managed by the dedicated
-- n8n OAuth2 credential. Do not copy token material into this database.

CREATE TABLE IF NOT EXISTS sales_navigator_v2_conversation_map (
  id BIGSERIAL PRIMARY KEY,
  unipile_account_id TEXT NOT NULL CHECK (unipile_account_id = 'acc_01m3sefk22e8jvnmvvfx333pye'),
  provider_profile_id TEXT NOT NULL,
  unipile_chat_id TEXT NOT NULL,
  ghl_contact_id TEXT NOT NULL,
  ghl_conversation_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (unipile_account_id, provider_profile_id, unipile_chat_id),
  UNIQUE (unipile_account_id, unipile_chat_id)
);

CREATE TABLE IF NOT EXISTS sales_navigator_v2_message_events (
  id BIGSERIAL PRIMARY KEY,
  unipile_account_id TEXT NOT NULL CHECK (unipile_account_id = 'acc_01m3sefk22e8jvnmvvfx333pye'),
  event_id TEXT NOT NULL,
  message_id TEXT NOT NULL,
  unipile_message_id TEXT,
  unipile_chat_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'processing', 'posted', 'failed', 'held')),
  claim_token UUID,
  claimed_at TIMESTAMPTZ,
  ghl_contact_id TEXT,
  ghl_conversation_id TEXT,
  ghl_message_id TEXT,
  failure_code TEXT,
  direction TEXT CHECK (direction IN ('inbound', 'outbound', 'ghl_outbound')),
  message_text TEXT,
  attachment_manifest JSONB NOT NULL DEFAULT '[]'::jsonb,
  provider_profile_id TEXT,
  provider_timestamp TIMESTAMPTZ,
  payload_sha256 TEXT,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  last_reconciled_at TIMESTAMPTZ,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (unipile_account_id, event_id),
  UNIQUE (unipile_account_id, message_id)
);

ALTER TABLE sales_navigator_v2_message_events
  ADD COLUMN IF NOT EXISTS unipile_message_id TEXT;
ALTER TABLE sales_navigator_v2_message_events
  ADD COLUMN IF NOT EXISTS direction TEXT,
  ADD COLUMN IF NOT EXISTS message_text TEXT,
  ADD COLUMN IF NOT EXISTS attachment_manifest JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS provider_profile_id TEXT,
  ADD COLUMN IF NOT EXISTS provider_timestamp TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS payload_sha256 TEXT,
  ADD COLUMN IF NOT EXISTS attempt_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_reconciled_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS reconcile_attempts INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS held_reason TEXT;

-- Widen the status contract for existing deployments: 'held' marks an uncertain
-- external write that reconciliation could neither prove nor safely retry.
ALTER TABLE sales_navigator_v2_message_events
  DROP CONSTRAINT IF EXISTS sales_navigator_v2_message_events_status_check;
ALTER TABLE sales_navigator_v2_message_events
  ADD CONSTRAINT sales_navigator_v2_message_events_status_check
  CHECK (status IN ('pending', 'processing', 'posted', 'failed', 'held'));

CREATE INDEX IF NOT EXISTS sales_navigator_v2_message_events_reconcile_idx
  ON sales_navigator_v2_message_events (COALESCE(last_reconciled_at, claimed_at, received_at))
  WHERE status IN ('processing', 'failed');
CREATE INDEX IF NOT EXISTS sales_navigator_v2_message_events_held_idx
  ON sales_navigator_v2_message_events (updated_at)
  WHERE status = 'held';
CREATE UNIQUE INDEX IF NOT EXISTS sales_navigator_v2_message_events_unipile_message_idx
  ON sales_navigator_v2_message_events (unipile_account_id, unipile_message_id)
  WHERE unipile_message_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS sales_navigator_v2_message_events_retry_idx
  ON sales_navigator_v2_message_events (updated_at)
  WHERE status IN ('pending', 'failed');

CREATE INDEX IF NOT EXISTS sales_navigator_v2_message_events_claim_idx
  ON sales_navigator_v2_message_events (claimed_at)
  WHERE status = 'processing';

COMMENT ON TABLE sales_navigator_v2_conversation_map IS
  'V2 Sales Navigator only: maps Unipile account/profile/chat to an already-confirmed GHL contact and conversation.';
COMMENT ON TABLE sales_navigator_v2_message_events IS
  'V2 Sales Navigator only idempotency ledger for message.new events; no contact auto-creation.';
