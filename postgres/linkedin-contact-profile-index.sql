-- Exact LinkedIn member-profile lookup for inbound message contact resolution.
-- The index is refreshed from the same GHL contact snapshots as report_raw_ghl_contacts.
CREATE TABLE IF NOT EXISTS linkedin_contact_profile_index (
  ghl_contact_id TEXT NOT NULL,
  normalized_profile_slug TEXT NOT NULL,
  profile_url TEXT,
  contact_name TEXT,
  linkedin_provider_ids TEXT[] NOT NULL DEFAULT '{}',
  refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (ghl_contact_id, normalized_profile_slug)
);

ALTER TABLE linkedin_contact_profile_index ADD COLUMN IF NOT EXISTS profile_url TEXT;
ALTER TABLE linkedin_contact_profile_index ADD COLUMN IF NOT EXISTS contact_name TEXT;
ALTER TABLE linkedin_contact_profile_index ADD COLUMN IF NOT EXISTS linkedin_provider_ids TEXT[] NOT NULL DEFAULT '{}';

CREATE INDEX IF NOT EXISTS linkedin_contact_profile_index_slug_idx
  ON linkedin_contact_profile_index (normalized_profile_slug, ghl_contact_id);
CREATE INDEX IF NOT EXISTS linkedin_contact_profile_index_provider_ids_idx
  ON linkedin_contact_profile_index USING GIN (linkedin_provider_ids);

CREATE TABLE IF NOT EXISTS linkedin_contact_profile_claims (
  normalized_identity_key TEXT PRIMARY KEY,
  owner_key TEXT NOT NULL,
  source_workflow TEXT NOT NULL,
  claim_token UUID NOT NULL DEFAULT gen_random_uuid(),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved')),
  ghl_contact_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS linkedin_contact_profile_claims_updated_idx
  ON linkedin_contact_profile_claims (updated_at) WHERE status = 'pending';

CREATE OR REPLACE FUNCTION linkedin_extract_profile_slugs(p_payload JSONB)
RETURNS TABLE(normalized_profile_slug TEXT)
LANGUAGE SQL IMMUTABLE PARALLEL SAFE AS $$
  SELECT DISTINCT lower(trim(trailing '/' FROM m.parts[1]))
  FROM (
    SELECT COALESCE(p_payload->>'website', '') AS field_value
    UNION ALL
    SELECT COALESCE(cf->>'value', cf->>'fieldValue', cf->>'field_value', '')
    FROM jsonb_array_elements(CASE
      WHEN jsonb_typeof(p_payload->'customFields') = 'array' THEN p_payload->'customFields'
      WHEN jsonb_typeof(p_payload->'customFields'->'fields') = 'array' THEN p_payload->'customFields'->'fields'
      WHEN jsonb_typeof(p_payload->'customFields'->'data') = 'array' THEN p_payload->'customFields'->'data'
      ELSE '[]'::jsonb
    END) cf
  ) v
  CROSS JOIN LATERAL regexp_matches(
    lower(v.field_value), '(?:https?://)?(?:[[:alnum:]-]+[.])?linkedin[.]com/in/([^[:space:],;<>?/#)]+)', 'g'
  ) AS m(parts)
  WHERE m.parts[1] <> '';
$$;

CREATE OR REPLACE FUNCTION linkedin_refresh_contact_profile_index()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE contact_id TEXT;
BEGIN
  IF NEW.source_system <> 'ghl' OR NEW.source_key NOT LIKE 'contact:%' THEN
    RETURN NEW;
  END IF;
  contact_id := split_part(NEW.source_key, ':', 2);
  IF contact_id !~ '^[A-Za-z0-9]{20}$' THEN RETURN NEW; END IF;
  DELETE FROM linkedin_contact_profile_index i
  WHERE i.ghl_contact_id = contact_id
    AND i.normalized_profile_slug NOT LIKE 'provider:%'
    AND NOT EXISTS (
      SELECT 1 FROM linkedin_extract_profile_slugs(NEW.payload_json) s
      WHERE s.normalized_profile_slug = i.normalized_profile_slug
    );
  INSERT INTO linkedin_contact_profile_index
    (ghl_contact_id, normalized_profile_slug, profile_url, contact_name, linkedin_provider_ids, refreshed_at)
  SELECT contact_id, s.normalized_profile_slug,
         'https://www.linkedin.com/in/' || s.normalized_profile_slug,
         COALESCE(NULLIF(concat_ws(' ', NEW.payload_json->>'firstName', NEW.payload_json->>'lastName'), ''), NULLIF(NEW.payload_json->>'name', '')),
         '{}'::text[], NOW()
  FROM linkedin_extract_profile_slugs(NEW.payload_json) s
  ON CONFLICT (ghl_contact_id, normalized_profile_slug)
  DO UPDATE SET profile_url = EXCLUDED.profile_url,
    contact_name = COALESCE(EXCLUDED.contact_name, linkedin_contact_profile_index.contact_name),
    refreshed_at = EXCLUDED.refreshed_at;
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION linkedin_claim_contact_profile(
  p_slug TEXT, p_provider_id TEXT, p_owner_key TEXT, p_source TEXT
) RETURNS TABLE(claim_action TEXT, ghl_contact_id TEXT, claim_token UUID, match_count INTEGER)
LANGUAGE plpgsql AS $$
DECLARE normalized_key TEXT; candidate_count INTEGER; candidate_contact TEXT; inserted_token UUID; existing RECORD; attempt INTEGER;
BEGIN
  normalized_key := NULLIF(lower(trim(both '/' FROM COALESCE(p_slug, ''))), '');
  IF normalized_key IS NULL THEN
    normalized_key := NULLIF('provider:' || lower(trim(COALESCE(p_provider_id, ''))), 'provider:');
  END IF;
  IF normalized_key IS NULL THEN
    RETURN QUERY SELECT 'missing_identity'::text, NULL::text, NULL::uuid, 0;
    RETURN;
  END IF;

  SELECT COUNT(DISTINCT i.ghl_contact_id)::integer, MIN(i.ghl_contact_id)
    INTO candidate_count, candidate_contact
  FROM linkedin_contact_profile_index i
  WHERE i.ghl_contact_id ~ '^[A-Za-z0-9]{20}$'
    AND ((normalized_key NOT LIKE 'provider:%' AND i.normalized_profile_slug = normalized_key)
      OR (p_provider_id IS NOT NULL AND p_provider_id <> '' AND i.linkedin_provider_ids @> ARRAY[p_provider_id]::text[]));
  IF candidate_count = 1 THEN
    RETURN QUERY SELECT 'matched'::text, candidate_contact, NULL::uuid, candidate_count;
    RETURN;
  ELSIF candidate_count > 1 THEN
    RETURN QUERY SELECT 'ambiguous'::text, NULL::text, NULL::uuid, candidate_count;
    RETURN;
  END IF;

  INSERT INTO linkedin_contact_profile_claims(normalized_identity_key, owner_key, source_workflow, status, updated_at)
  VALUES(normalized_key, p_owner_key, p_source, 'pending', NOW())
  ON CONFLICT (normalized_identity_key) DO NOTHING
  RETURNING claim_token INTO inserted_token;
  IF inserted_token IS NOT NULL THEN
    RETURN QUERY SELECT 'owner'::text, NULL::text, inserted_token, 0;
    RETURN;
  END IF;

  -- Let the current owner finish contact creation and persist it to the shared
  -- index. This handles two messages arriving in the same second without allowing
  -- the waiter to create a second contact.
  FOR attempt IN 1..20 LOOP
    SELECT c.* INTO existing FROM linkedin_contact_profile_claims c
    WHERE c.normalized_identity_key = normalized_key;
    IF FOUND AND existing.status = 'resolved'
      AND existing.ghl_contact_id ~ '^[A-Za-z0-9]{20}$' THEN
      RETURN QUERY SELECT 'matched'::text, existing.ghl_contact_id, existing.claim_token, 1;
      RETURN;
    END IF;
    SELECT COUNT(DISTINCT i.ghl_contact_id)::integer, MIN(i.ghl_contact_id)
      INTO candidate_count, candidate_contact
    FROM linkedin_contact_profile_index i
    WHERE i.ghl_contact_id ~ '^[A-Za-z0-9]{20}$'
      AND ((normalized_key NOT LIKE 'provider:%' AND i.normalized_profile_slug = normalized_key)
        OR (p_provider_id IS NOT NULL AND p_provider_id <> '' AND i.linkedin_provider_ids @> ARRAY[p_provider_id]::text[]));
    IF candidate_count = 1 THEN
      RETURN QUERY SELECT 'matched'::text, candidate_contact, NULL::uuid, candidate_count;
      RETURN;
    ELSIF candidate_count > 1 THEN
      RETURN QUERY SELECT 'ambiguous'::text, NULL::text, NULL::uuid, candidate_count;
      RETURN;
    END IF;
    PERFORM pg_sleep(0.5);
  END LOOP;
  -- Pending claims never expire automatically: reclaiming one could duplicate a
  -- GHL contact if the creator succeeded but stopped before recording its ID.
  RETURN QUERY SELECT 'busy'::text, NULL::text, existing.claim_token, 0;
END;
$$;

CREATE OR REPLACE FUNCTION linkedin_resolve_contact_profile_claim(
  p_identity_key TEXT, p_claim_token UUID, p_contact_id TEXT, p_slug TEXT,
  p_profile_url TEXT, p_contact_name TEXT, p_provider_id TEXT
) RETURNS BOOLEAN LANGUAGE plpgsql AS $$
DECLARE claim_owner TEXT;
BEGIN
  SELECT c.normalized_identity_key INTO claim_owner
  FROM linkedin_contact_profile_claims c
  WHERE c.normalized_identity_key = p_identity_key
    AND c.claim_token = p_claim_token AND c.status = 'pending'
  FOR UPDATE;
  IF NOT FOUND OR p_contact_id !~ '^[A-Za-z0-9]{20}$' THEN RETURN FALSE; END IF;

  IF NULLIF(p_slug, '') IS NOT NULL OR NULLIF(p_provider_id, '') IS NOT NULL THEN
    INSERT INTO linkedin_contact_profile_index
      (ghl_contact_id, normalized_profile_slug, profile_url, contact_name, linkedin_provider_ids, refreshed_at)
    VALUES (p_contact_id, COALESCE(NULLIF(lower(trim(both '/' from p_slug)), ''), 'provider:' || lower(p_provider_id)), NULLIF(p_profile_url, ''), NULLIF(p_contact_name, ''),
      CASE WHEN NULLIF(p_provider_id, '') IS NULL THEN '{}'::text[] ELSE ARRAY[p_provider_id]::text[] END, NOW())
    ON CONFLICT (ghl_contact_id, normalized_profile_slug) DO UPDATE SET
      profile_url = COALESCE(EXCLUDED.profile_url, linkedin_contact_profile_index.profile_url),
      contact_name = COALESCE(EXCLUDED.contact_name, linkedin_contact_profile_index.contact_name),
      linkedin_provider_ids = ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids || EXCLUDED.linkedin_provider_ids)),
      refreshed_at = NOW();
  END IF;
  UPDATE linkedin_contact_profile_claims SET status='resolved', ghl_contact_id=p_contact_id, updated_at=NOW()
  WHERE normalized_identity_key=p_identity_key AND claim_token=p_claim_token AND status='pending';
  RETURN TRUE;
END;
$$;

DROP TRIGGER IF EXISTS report_raw_ghl_contacts_linkedin_profile_idx ON report_raw_ghl_contacts;
CREATE TRIGGER report_raw_ghl_contacts_linkedin_profile_idx
AFTER INSERT OR UPDATE OF payload_json ON report_raw_ghl_contacts
FOR EACH ROW EXECUTE FUNCTION linkedin_refresh_contact_profile_index();

-- One-time seed from each contact's newest available GHL snapshot.
INSERT INTO linkedin_contact_profile_index (ghl_contact_id, normalized_profile_slug, profile_url, contact_name, refreshed_at)
SELECT split_part(c.source_key, ':', 2), s.normalized_profile_slug,
       'https://www.linkedin.com/in/' || s.normalized_profile_slug,
       COALESCE(NULLIF(concat_ws(' ', c.payload_json->>'firstName', c.payload_json->>'lastName'), ''), NULLIF(c.payload_json->>'name', '')),
       NOW()
FROM (
  SELECT DISTINCT ON (source_key) source_key, payload_json
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl' AND source_key ~ '^contact:[A-Za-z0-9]{20}$'
  ORDER BY source_key, loaded_at DESC, id DESC
) c
CROSS JOIN LATERAL linkedin_extract_profile_slugs(c.payload_json) s
ON CONFLICT (ghl_contact_id, normalized_profile_slug)
DO UPDATE SET profile_url = COALESCE(EXCLUDED.profile_url, linkedin_contact_profile_index.profile_url),
  contact_name = COALESCE(EXCLUDED.contact_name, linkedin_contact_profile_index.contact_name),
  refreshed_at = EXCLUDED.refreshed_at;

-- Carry known Unipile provider IDs into the shared contact index. These legacy
-- identity sources are migration inputs only; inbound resolution uses this index.
DO $$
DECLARE source_table TEXT;
BEGIN
  FOREACH source_table IN ARRAY ARRAY['linkedin_connection_state', 'partnership_linkedin_connection_state', 'linkedin_conversation_map'] LOOP
    IF to_regclass('public.' || source_table) IS NOT NULL THEN
      EXECUTE format($sql$
        INSERT INTO linkedin_contact_profile_index
          (ghl_contact_id, normalized_profile_slug, profile_url, contact_name, linkedin_provider_ids, refreshed_at)
        SELECT x.ghl_contact_id, x.profile_key, MIN(x.profile_url), NULL,
          array_agg(DISTINCT x.provider_id), NOW()
        FROM (
          SELECT m.ghl_contact_id, s.normalized_profile_slug AS profile_key,
            NULLIF(m.linkedin_profile_url, '') AS profile_url, m.linkedin_provider_id AS provider_id
          FROM %I m
          CROSS JOIN LATERAL linkedin_extract_profile_slugs(jsonb_build_object('website', m.linkedin_profile_url)) s
          WHERE m.ghl_contact_id ~ '^[A-Za-z0-9]{20}$' AND NULLIF(m.linkedin_provider_id, '') IS NOT NULL
          UNION ALL
          SELECT m.ghl_contact_id, 'provider:' || lower(m.linkedin_provider_id), NULL, m.linkedin_provider_id
          FROM %I m WHERE m.ghl_contact_id ~ '^[A-Za-z0-9]{20}$' AND NULLIF(m.linkedin_provider_id, '') IS NOT NULL
        ) x
        GROUP BY x.ghl_contact_id, x.profile_key
        ON CONFLICT (ghl_contact_id, normalized_profile_slug) DO UPDATE SET
          profile_url = COALESCE(EXCLUDED.profile_url, linkedin_contact_profile_index.profile_url),
          linkedin_provider_ids = ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids || EXCLUDED.linkedin_provider_ids)),
          refreshed_at = NOW()
      $sql$, source_table, source_table);
    END IF;
  END LOOP;
END;
$$;

DO $$
BEGIN
  IF to_regclass('public.sales_navigator_v2_conversation_map') IS NOT NULL THEN
    INSERT INTO linkedin_contact_profile_index
      (ghl_contact_id, normalized_profile_slug, linkedin_provider_ids, refreshed_at)
    SELECT DISTINCT m.ghl_contact_id, 'provider:' || lower(m.provider_profile_id), ARRAY[m.provider_profile_id]::text[], NOW()
    FROM sales_navigator_v2_conversation_map m
    WHERE m.ghl_contact_id ~ '^[A-Za-z0-9]{20}$' AND NULLIF(m.provider_profile_id, '') IS NOT NULL
    ON CONFLICT (ghl_contact_id, normalized_profile_slug) DO UPDATE SET
      linkedin_provider_ids = ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids || EXCLUDED.linkedin_provider_ids)),
      refreshed_at = NOW();
  END IF;
END;
$$;

-- Legacy relation keys such as linkedin:relation:<slug> are not GHL contact IDs.
-- Earlier seed runs accidentally added them to the contact index.
DELETE FROM linkedin_contact_profile_index
WHERE ghl_contact_id LIKE 'linkedin:%';

SELECT (SELECT COUNT(*) FROM linkedin_contact_profile_index) AS indexed_profiles,
       (SELECT COUNT(DISTINCT ghl_contact_id) FROM linkedin_contact_profile_index) AS indexed_contacts,
       (SELECT COUNT(*) FROM linkedin_contact_profile_claims) AS contact_claims,
       to_regclass('public.linkedin_contact_profile_index_slug_idx') AS lookup_index;
