-- Backfill GHL contact IDs onto imported Emerald pool rows.
--
-- Primary match strategy:
-- 1) Read the latest raw GHL contact snapshot per contact ID
-- 2) Extract Em_Emerald_Contact_ID from contact custom fields
-- 3) Update emerging_pool_contacts.ghl_contact_id for matching Emerald rows
--
-- Notes:
-- - This intentionally only fills ghl_contact_id.
-- - Leave ghl_opportunity_id for a second pass after contact matching is verified.

WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    payload_json
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
contact_custom_fields AS (
  SELECT
    lgc.ghl_contact_id,
    NULLIF(
      TRIM(
        COALESCE(
          cf->>'value',
          cf->>'field_value',
          cf->>'fieldValue',
          ''
        )
      ),
      ''
    ) AS emerald_contact_id
  FROM latest_ghl_contacts lgc
  CROSS JOIN LATERAL jsonb_array_elements(
    CASE
      WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array'
        THEN lgc.payload_json->'customFields'
      WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array'
        THEN lgc.payload_json->'customFields'->'fields'
      WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array'
        THEN lgc.payload_json->'customFields'->'data'
      ELSE '[]'::jsonb
    END
  ) AS cf
  WHERE lower(trim(COALESCE(
    cf->>'name',
    cf->>'label',
    cf->>'fieldName',
    cf->>'key',
    cf->>'field_key',
    ''
  ))) = lower('Em_Emerald_Contact_ID')
     OR COALESCE(cf->>'id', '') = 'R0wbDRyzZz34PMlQSRWN'
),
deduped_matches AS (
  SELECT DISTINCT
    emerald_contact_id,
    ghl_contact_id
  FROM contact_custom_fields
  WHERE emerald_contact_id IS NOT NULL
    AND ghl_contact_id IS NOT NULL
),
updated_rows AS (
  UPDATE emerging_pool_contacts epc
  SET
    ghl_contact_id = dm.ghl_contact_id,
    ghl_import_status = 'matched_by_emerald_contact_id',
    updated_at = NOW()
  FROM deduped_matches dm
  WHERE epc.ghl_contact_id IS NULL
    AND epc.emerald_contact_id::text = dm.emerald_contact_id
  RETURNING epc.id, epc.source_list, epc.emerald_contact_id, epc.ghl_contact_id
)
SELECT
  source_list,
  COUNT(*) AS updated_count
FROM updated_rows
GROUP BY source_list
ORDER BY source_list;

-- Verification 1: overall match coverage by pool.
SELECT
  source_list,
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE ghl_contact_id IS NOT NULL) AS matched_rows,
  COUNT(*) FILTER (WHERE ghl_contact_id IS NULL) AS unmatched_rows
FROM emerging_pool_contacts
GROUP BY source_list
ORDER BY source_list;

-- Verification 2: rows already tied to live queued contacts.
SELECT
  epc.source_list,
  COUNT(*) AS queued_rows,
  COUNT(*) FILTER (WHERE epc.ghl_contact_id IS NOT NULL) AS queued_with_ghl_contact_id,
  COUNT(*) FILTER (WHERE q.campaign_id = 'brand') AS queued_brand_rows,
  COUNT(*) FILTER (WHERE q.campaign_id = 'dispensary') AS queued_dispensary_rows
FROM emerging_pool_contacts epc
JOIN voice_call_queue q
  ON q.contact_id = epc.ghl_contact_id
GROUP BY epc.source_list
ORDER BY epc.source_list;

-- Verification 3: inspect a small sample of still-unmatched rows.
SELECT
  source_list,
  emerald_contact_id,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  tags
FROM emerging_pool_contacts
WHERE ghl_contact_id IS NULL
ORDER BY source_list, id
LIMIT 50;
