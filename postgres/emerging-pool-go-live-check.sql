-- Consolidated go-live check for imported Emerald pool contacts.
--
-- Run after GHL import processing finishes. This combines:
-- - readiness / landing checks
-- - linkage coverage snapshot
-- - first seed cohort preview

-- Section 1: imported contacts landed in report_raw_ghl_contacts.
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    report_date,
    loaded_at,
    payload_json,
    dimensions_json
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
normalized_custom_fields AS (
  SELECT
    lgc.ghl_contact_id,
    lgc.report_date,
    lgc.loaded_at,
    NULLIF(TRIM(COALESCE(
      emerald_cf->>'value',
      emerald_cf->>'field_value',
      emerald_cf->>'fieldValue',
      ''
    )), '') AS emerald_contact_id,
    NULLIF(TRIM(COALESCE(
      source_cf->>'value',
      source_cf->>'field_value',
      source_cf->>'fieldValue',
      ''
    )), '') AS em_source_file,
    NULLIF(TRIM(COALESCE(
      lgc.dimensions_json->>'tags',
      lgc.payload_json->>'tags',
      ''
    )), '') AS tags_text
  FROM latest_ghl_contacts lgc
  LEFT JOIN LATERAL (
    SELECT elem
    FROM jsonb_array_elements(
      CASE
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array' THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array' THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array' THEN lgc.payload_json->'customFields'->'data'
        ELSE '[]'::jsonb
      END
    ) AS elem
    WHERE lower(trim(COALESCE(
      elem->>'name',
      elem->>'label',
      elem->>'fieldName',
      elem->>'key',
      elem->>'field_key',
      ''
    ))) = lower('Em_Emerald_Contact_ID')
       OR COALESCE(elem->>'id', '') = 'R0wbDRyzZz34PMlQSRWN'
    LIMIT 1
  ) emerald_lateral(emerald_cf) ON true
  LEFT JOIN LATERAL (
    SELECT elem
    FROM jsonb_array_elements(
      CASE
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array' THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array' THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array' THEN lgc.payload_json->'customFields'->'data'
        ELSE '[]'::jsonb
      END
    ) AS elem
    WHERE lower(trim(COALESCE(
      elem->>'name',
      elem->>'label',
      elem->>'fieldName',
      elem->>'key',
      elem->>'field_key',
      ''
    ))) = lower('Em_Source_File')
       OR COALESCE(elem->>'id', '') = 'ILurFacMbAaHz2DdGjPa'
    LIMIT 1
  ) source_lateral(source_cf) ON true
),
pool_contacts AS (
  SELECT
    ghl_contact_id,
    report_date,
    loaded_at,
    emerald_contact_id,
    em_source_file,
    tags_text,
    CASE
      WHEN lower(COALESCE(tags_text, '')) LIKE '%brands_pool%' THEN 'brands'
      WHEN lower(COALESCE(tags_text, '')) LIKE '%dispensaries_pool%' THEN 'dispensaries'
      WHEN lower(COALESCE(em_source_file, '')) LIKE '%brand%' THEN 'brands'
      WHEN lower(COALESCE(em_source_file, '')) LIKE '%dispensary%' THEN 'dispensaries'
      ELSE NULL
    END AS inferred_pool
  FROM normalized_custom_fields
)
SELECT
  'readiness' AS section,
  inferred_pool AS bucket,
  COUNT(*)::text AS metric_1,
  COUNT(*) FILTER (WHERE emerald_contact_id IS NOT NULL)::text AS metric_2,
  COALESCE(to_char(MIN(loaded_at), 'YYYY-MM-DD HH24:MI:SS'), '') AS metric_3,
  COALESCE(to_char(MAX(loaded_at), 'YYYY-MM-DD HH24:MI:SS'), '') AS metric_4
FROM pool_contacts
WHERE inferred_pool IS NOT NULL
GROUP BY inferred_pool
ORDER BY inferred_pool;

-- Section 2: current linkage coverage in emerging_pool_contacts.
SELECT
  'coverage' AS section,
  source_list AS bucket,
  COUNT(*)::text AS metric_1,
  COUNT(*) FILTER (WHERE ghl_contact_id IS NOT NULL)::text AS metric_2,
  COUNT(*) FILTER (WHERE ghl_opportunity_id IS NOT NULL AND ghl_opportunity_id <> '')::text AS metric_3,
  COUNT(*) FILTER (WHERE primary_phone IS NOT NULL AND primary_phone <> '')::text AS metric_4
FROM emerging_pool_contacts
GROUP BY source_list
ORDER BY source_list;

-- Section 3: first seed cohort preview.
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    dimensions_json,
    loaded_at
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
base_candidates AS (
  SELECT
    epc.id AS emerging_pool_row_id,
    epc.source_list,
    epc.emerald_contact_id,
    epc.ghl_contact_id AS contact_id,
    epc.ghl_opportunity_id,
    epc.first_name,
    epc.last_name,
    epc.primary_email,
    epc.primary_phone,
    epc.company_name,
    lgc.dimensions_json->>'tags' AS ghl_tags,
    ROW_NUMBER() OVER (
      PARTITION BY epc.source_list
      ORDER BY epc.id ASC
    ) AS pool_rank
  FROM emerging_pool_contacts epc
  LEFT JOIN latest_ghl_contacts lgc
    ON lgc.ghl_contact_id = epc.ghl_contact_id
  WHERE epc.ghl_contact_id IS NOT NULL
    AND epc.source_list IN ('brands', 'dispensaries')
    AND COALESCE(epc.primary_phone, '') <> ''
    AND NOT EXISTS (
      SELECT 1 FROM voice_call_attempt a WHERE a.contact_id = epc.ghl_contact_id
    )
    AND NOT EXISTS (
      SELECT 1
      FROM voice_call_queue q
      WHERE q.contact_id = epc.ghl_contact_id
        AND q.status IN ('pending', 'in_progress')
    )
)
SELECT
  source_list,
  pool_rank,
  contact_id,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  ghl_opportunity_id,
  ghl_tags
FROM base_candidates
WHERE pool_rank <= 5
ORDER BY source_list, pool_rank;
