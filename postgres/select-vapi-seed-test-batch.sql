-- Select a small first-batch Brand / Dispensary seed cohort for manual Vapi testing.
--
-- Intended use:
-- - After ghl_contact_id backfill
-- - Before broad classifier reruns or dialer reactivation
-- - Manual review of the exact first contacts to tag / queue

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
    epc.tags AS pool_tags,
    lgc.dimensions_json->>'tags' AS ghl_tags,
    lgc.loaded_at,
    CASE
      WHEN epc.source_list = 'brands' THEN 'brand'
      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'
      ELSE NULL
    END AS campaign_id,
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
  campaign_id,
  emerging_pool_row_id,
  emerald_contact_id,
  contact_id,
  ghl_opportunity_id,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  pool_tags,
  ghl_tags,
  loaded_at
FROM base_candidates
WHERE campaign_id IS NOT NULL
  AND pool_rank <= 5
ORDER BY campaign_id, pool_rank;
