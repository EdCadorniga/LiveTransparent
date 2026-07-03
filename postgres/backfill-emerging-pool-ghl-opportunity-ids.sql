-- Backfill GHL opportunity IDs after ghl_contact_id has already been populated.
--
-- Selection rule:
-- - Prefer open opportunities over won/lost/abandoned when multiple exist.
-- - Within the same status tier, prefer the most recently loaded opportunity snapshot.
--
-- Assumptions:
-- - report_raw_ghl_opportunities contains a contact identifier either in dimensions_json
--   or payload_json from LT - GHL Daily Sales Ingest.
-- - emerging_pool_contacts.ghl_contact_id has already been backfilled.

WITH latest_opportunities AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^opportunity:', '') AS ghl_opportunity_id,
    report_date,
    loaded_at,
    payload_json,
    dimensions_json
  FROM report_raw_ghl_opportunities
  WHERE source_system = 'ghl'
    AND source_key LIKE 'opportunity:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
normalized_opportunities AS (
  SELECT
    ghl_opportunity_id,
    NULLIF(TRIM(COALESCE(
      dimensions_json->>'contact_id',
      dimensions_json->>'contactId',
      payload_json->>'contactId',
      payload_json->>'contact_id',
      payload_json->'contact'->>'id',
      payload_json->'contact'->>'contactId',
      ''
    )), '') AS ghl_contact_id,
    lower(NULLIF(TRIM(COALESCE(
      dimensions_json->>'status',
      payload_json->>'status',
      payload_json->'opportunity'->>'status',
      ''
    )), '')) AS opportunity_status,
    COALESCE(
      NULLIF(TRIM(COALESCE(
        payload_json->>'dateUpdated',
        payload_json->>'updatedAt',
        payload_json->>'lastUpdated',
        dimensions_json->>'updated_at',
        ''
      )), '')::timestamptz,
      loaded_at
    ) AS recency_ts,
    report_date,
    loaded_at
  FROM latest_opportunities
),
ranked_opportunities AS (
  SELECT
    ghl_opportunity_id,
    ghl_contact_id,
    opportunity_status,
    recency_ts,
    ROW_NUMBER() OVER (
      PARTITION BY ghl_contact_id
      ORDER BY
        CASE
          WHEN opportunity_status = 'open' THEN 0
          WHEN opportunity_status = 'won' THEN 1
          WHEN opportunity_status = 'lost' THEN 2
          WHEN opportunity_status = 'abandoned' THEN 3
          ELSE 4
        END,
        recency_ts DESC,
        ghl_opportunity_id DESC
    ) AS rn
  FROM normalized_opportunities
  WHERE ghl_contact_id IS NOT NULL
),
chosen_opportunities AS (
  SELECT
    ghl_contact_id,
    ghl_opportunity_id,
    opportunity_status,
    recency_ts
  FROM ranked_opportunities
  WHERE rn = 1
),
updated_rows AS (
  UPDATE emerging_pool_contacts epc
  SET
    ghl_opportunity_id = co.ghl_opportunity_id,
    ghl_import_status = CASE
      WHEN epc.ghl_import_status IS NULL OR epc.ghl_import_status = '' THEN 'matched_contact_and_opportunity'
      WHEN epc.ghl_import_status = 'matched_by_emerald_contact_id' THEN 'matched_contact_and_opportunity'
      ELSE epc.ghl_import_status
    END,
    updated_at = NOW()
  FROM chosen_opportunities co
  WHERE epc.ghl_contact_id = co.ghl_contact_id
    AND (epc.ghl_opportunity_id IS NULL OR epc.ghl_opportunity_id = '')
  RETURNING epc.id, epc.source_list, epc.ghl_contact_id, epc.ghl_opportunity_id
)
SELECT
  source_list,
  COUNT(*) AS updated_count
FROM updated_rows
GROUP BY source_list
ORDER BY source_list;

-- Verification 1: opportunity coverage by pool.
SELECT
  source_list,
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE ghl_contact_id IS NOT NULL) AS rows_with_contact_id,
  COUNT(*) FILTER (WHERE ghl_opportunity_id IS NOT NULL AND ghl_opportunity_id <> '') AS rows_with_opportunity_id
FROM emerging_pool_contacts
GROUP BY source_list
ORDER BY source_list;

-- Verification 2: sample chosen opportunities.
SELECT
  epc.source_list,
  epc.ghl_contact_id,
  epc.ghl_opportunity_id
FROM emerging_pool_contacts epc
WHERE epc.ghl_opportunity_id IS NOT NULL
  AND epc.ghl_opportunity_id <> ''
ORDER BY epc.updated_at DESC
LIMIT 25;
