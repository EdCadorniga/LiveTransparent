-- Additive LinkedIn vertical state. All timestamps are timestamptz; caps use Pacific days.
CREATE TABLE IF NOT EXISTS lt_li_vertical_control (
  account_id text PRIMARY KEY,
  next_vertical integer NOT NULL DEFAULT 0 CHECK (next_vertical BETWEEN 0 AND 7),
  enabled boolean NOT NULL DEFAULT false,
  dm_enabled boolean NOT NULL DEFAULT false,
  stopped_reason text,
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS lt_li_vertical_queue (
  contact_id text PRIMARY KEY,
  account_id text NOT NULL,
  vertical text NOT NULL,
  vertical_index integer NOT NULL CHECK (vertical_index BETWEEN 0 AND 7),
  profile_slug text NOT NULL,
  provider_id text,
  status text NOT NULL DEFAULT 'ready' CHECK (status IN
    ('ready','requested','connected','completed','suppressed','held','missing_profile')),
  reason text,
  enrolled_at timestamptz NOT NULL DEFAULT now(),
  invite_sent_at timestamptz,
  accepted_at timestamptz,
  acceptance_basis text,
  dm_step integer NOT NULL DEFAULT 0 CHECK (dm_step BETWEEN 0 AND 2),
  dm1_sent_at timestamptz,
  dm2_sent_at timestamptz,
  chat_id text,
  salesnav_provider_id text,
  last_checked_at timestamptz,
  refreshed_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (account_id,profile_slug)
);
CREATE INDEX IF NOT EXISTS lt_li_vertical_work_idx ON lt_li_vertical_queue(status,vertical_index,last_checked_at);
CREATE TABLE IF NOT EXISTS lt_li_outbound_attempts (
  id bigserial PRIMARY KEY,
  account_id text NOT NULL,
  identity_key text NOT NULL,
  contact_id text NOT NULL,
  kind text NOT NULL CHECK (kind IN ('invite','dm1','dm2')),
  source text NOT NULL,
  status text NOT NULL DEFAULT 'intent' CHECK (status IN ('intent','sent','uncertain','rejected')),
  reserved_at timestamptz NOT NULL DEFAULT now(),
  sent_at timestamptz,
  provider_id text,
  provider_result_id text,
  message_text text,
  message_sha256 text,
  error_code text,
  UNIQUE(account_id,identity_key,kind)
);
CREATE INDEX IF NOT EXISTS lt_li_outbound_pacing_idx ON lt_li_outbound_attempts(account_id,kind,reserved_at);

-- A single transaction lock serializes reservations from every participating sender.
-- Attempts including uncertain/rejected outcomes consume capacity conservatively.
CREATE OR REPLACE FUNCTION lt_li_reserve_invite(p_account text,p_identity text,p_contact text,p_source text)
RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE result_id bigint; day_n integer; hour_n integer;
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended('lt_li_invite:'||p_account,0));
  IF EXISTS(SELECT 1 FROM lt_li_outbound_attempts WHERE account_id=p_account AND identity_key=p_identity AND kind='invite') THEN
    RETURN NULL;
  END IF;
  -- Legacy successes and new intents dedupe by identity, not by contact/queue row.
  WITH all_attempts AS (
    SELECT identity_key AS identity,reserved_at AS at FROM lt_li_outbound_attempts WHERE account_id=p_account AND kind='invite'
    UNION ALL
    SELECT coalesce(nullif(linkedin_provider_id,''),lower(linkedin_public_identifier),ghl_contact_id),request_sent_at
    FROM linkedin_connection_state WHERE unipile_account_id=p_account AND request_sent_at IS NOT NULL
    UNION ALL
    SELECT coalesce(nullif(linkedin_provider_id,''),lower(linkedin_public_identifier),ghl_contact_id),request_sent_at
    FROM partnership_linkedin_connection_state WHERE unipile_account_id=p_account AND request_sent_at IS NOT NULL
  ) SELECT count(DISTINCT identity) FILTER(WHERE (at AT TIME ZONE 'America/Los_Angeles')::date=(now() AT TIME ZONE 'America/Los_Angeles')::date),
           count(DISTINCT identity) FILTER(WHERE at>now()-interval '60 minutes')
    INTO day_n,hour_n FROM all_attempts;
  IF day_n>=20 OR hour_n>=5 THEN RETURN NULL; END IF;
  INSERT INTO lt_li_outbound_attempts(account_id,identity_key,contact_id,kind,source)
  VALUES(p_account,p_identity,p_contact,'invite',p_source) RETURNING id INTO result_id;
  RETURN result_id;
END $$;

-- Future legacy queue claims must use the same account-wide capacity ledger.
-- Existing paused workflows are not edited or reactivated.
CREATE OR REPLACE FUNCTION lt_li_legacy_invite_gate() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE identity text; reservation bigint;
BEGIN
  IF NEW.unipile_account_id<>'V9eiHiDpRmCtan0YNdzsQw' THEN RETURN NEW; END IF;
  IF NEW.connection_status='requested_pending' AND
     (TG_OP='INSERT' OR OLD.connection_status IS DISTINCT FROM 'requested_pending') THEN
    IF EXISTS(SELECT 1 FROM lt_li_vertical_queue WHERE account_id=NEW.unipile_account_id AND
      (contact_id=NEW.ghl_contact_id OR profile_slug=lower(NEW.linkedin_public_identifier) OR
       (provider_id IS NOT NULL AND provider_id=NEW.linkedin_provider_id))) THEN
      RAISE EXCEPTION 'Vertical LinkedIn identity is owned by the vertical dispatcher';
    END IF;
    identity:=coalesce(nullif(NEW.linkedin_provider_id,''),nullif(lower(NEW.linkedin_public_identifier),''),NEW.ghl_contact_id);
    reservation:=lt_li_reserve_invite(NEW.unipile_account_id,identity,NEW.ghl_contact_id,'legacy:'||TG_TABLE_NAME);
    IF reservation IS NULL THEN RAISE EXCEPTION 'LinkedIn account-wide capacity or identity hold'; END IF;
  END IF;
  RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS lt_li_shared_pacing ON linkedin_connection_state;
CREATE TRIGGER lt_li_shared_pacing BEFORE INSERT OR UPDATE ON linkedin_connection_state
FOR EACH ROW EXECUTE FUNCTION lt_li_legacy_invite_gate();
DROP TRIGGER IF EXISTS lt_li_shared_pacing ON partnership_linkedin_connection_state;
CREATE TRIGGER lt_li_shared_pacing BEFORE INSERT OR UPDATE ON partnership_linkedin_connection_state
FOR EACH ROW EXECUTE FUNCTION lt_li_legacy_invite_gate();
