-- Check whether newly imported Emerald pool contacts have landed in report_raw_ghl_contacts.
--
-- Run this after the GHL CSV import completes. When the counts here look healthy,
-- you can safely run postgres/backfill-emerging-pool-ghl-ids.sql.

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
      cf->>'value',
      cf->>'field_value',
      cf->>'fieldValue',
      ''
    )), '') AS emerald_contact_id,
    NULLIF(TRIM(COALESCE(
      cf_source->>'value',
      cf_source->>'field_value',
      cf_source->>'fieldValue',
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
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array'
          THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array'
          THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array'
          THEN lgc.payload_json->'customFields'->'data'
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
  ) emerald_cf ON true
  LEFT JOIN LATERAL (
    SELECT elem
    FROM jsonb_array_elements(
      CASE
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array'
          THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array'
          THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array'
          THEN lgc.payload_json->'customFields'->'data'
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
  ) source_cf(cf_source) ON true
  LEFT JOIN LATERAL (SELECT emerald_cf.elem AS cf) emerald_cf_alias ON true
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
  inferred_pool,
  COUNT(*) AS landed_contacts,
  COUNT(*) FILTER (WHERE emerald_contact_id IS NOT NULL) AS with_emerald_contact_id,
  MIN(loaded_at) AS first_loaded_at,
  MAX(loaded_at) AS last_loaded_at
FROM pool_contacts
WHERE inferred_pool IS NOT NULL
GROUP BY inferred_pool
ORDER BY inferred_pool;

-- Compare landed GHL contacts to imported Postgres pool rows.
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    payload_json,
    dimensions_json
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
pool_ids AS (
  SELECT
    NULLIF(TRIM(COALESCE(
      cf->>'value',
      cf->>'field_value',
      cf->>'fieldValue',
      ''
    )), '') AS emerald_contact_id,
    CASE
      WHEN lower(COALESCE(tags_text, '')) LIKE '%brands_pool%' THEN 'brands'
      WHEN lower(COALESCE(tags_text, '')) LIKE '%dispensaries_pool%' THEN 'dispensaries'
      WHEN lower(COALESCE(em_source_file, '')) LIKE '%brand%' THEN 'brands'
      WHEN lower(COALESCE(em_source_file, '')) LIKE '%dispensary%' THEN 'dispensaries'
      ELSE NULL
    END AS inferred_pool
  FROM latest_ghl_contacts lgc
  CROSS JOIN LATERAL (
    SELECT NULLIF(TRIM(COALESCE(
      lgc.dimensions_json->>'tags',
      lgc.payload_json->>'tags',
      ''
    )), '') AS tags_text
  ) tags
  LEFT JOIN LATERAL (
    SELECT elem AS cf
    FROM jsonb_array_elements(
      CASE
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array'
          THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array'
          THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array'
          THEN lgc.payload_json->'customFields'->'data'
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
  ) emerald_cf ON true
  LEFT JOIN LATERAL (
    SELECT NULLIF(TRIM(COALESCE(
      elem->>'value',
      elem->>'field_value',
      elem->>'fieldValue',
      ''
    )), '') AS em_source_file
    FROM jsonb_array_elements(
      CASE
        WHEN jsonb_typeof(lgc.payload_json->'customFields') = 'array'
          THEN lgc.payload_json->'customFields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'fields') = 'array'
          THEN lgc.payload_json->'customFields'->'fields'
        WHEN jsonb_typeof(lgc.payload_json->'customFields'->'data') = 'array'
          THEN lgc.payload_json->'customFields'->'data'
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
  ) source_cf ON true
)
SELECT
  epc.source_list,
  COUNT(*) AS imported_rows,
  COUNT(*) FILTER (
    WHERE epc.emerald_contact_id::text IN (
      SELECT emerald_contact_id
      FROM pool_ids
      WHERE inferred_pool = epc.source_list
        AND emerald_contact_id IS NOT NULL
    )
  ) AS landed_in_report_raw_contacts
FROM emerging_pool_contacts epc
GROUP BY epc.source_list
ORDER BY epc.source_list;

-- Sample recent landed contacts for spot-checking.
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    loaded_at,
    payload_json,
    dimensions_json
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
)
SELECT
  ghl_contact_id,
  loaded_at,
  dimensions_json->>'contact_name' AS contact_name,
  dimensions_json->>'email' AS email,
  dimensions_json->>'phone' AS phone,
  dimensions_json->>'company_name' AS company_name
FROM latest_ghl_contacts
WHERE lower(COALESCE(dimensions_json->>'tags', '')) LIKE '%brands_pool%'
   OR lower(COALESCE(dimensions_json->>'tags', '')) LIKE '%dispensaries_pool%'
ORDER BY loaded_at DESC
LIMIT 25;
