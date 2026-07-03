-- Select eligible imported Emerald pool contacts for Brand / Dispensary Vapi tagging.
--
-- This is the intended selection basis for rebuilding
-- LT - Campaign Contact Classifier (`IduCoT5YOs0g2faT`).
--
-- Eligibility rules:
-- - imported pool row has been linked to a GHL contact
-- - source_list determines campaign directly
-- - has a usable phone on the imported row
-- - has not already been called
-- - is not already pending/in-progress in the queue
-- - is not already tagged with a terminal Vapi outcome or DNC in GHL raw contact data

WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    payload_json,
    dimensions_json,
    loaded_at
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
eligible_contacts AS (
  SELECT
    epc.id AS emerging_pool_row_id,
    epc.emerald_contact_id,
    epc.source_list,
    epc.first_name,
    epc.last_name,
    epc.primary_email,
    epc.primary_phone,
    epc.company_name,
    epc.tags AS pool_tags,
    epc.ghl_contact_id AS contact_id,
    epc.ghl_opportunity_id,
    lgc.dimensions_json->>'tags' AS ghl_tags,
    lgc.dimensions_json->>'phone' AS ghl_phone,
    lgc.dimensions_json->>'email' AS ghl_email,
    CASE
      WHEN epc.source_list = 'brands' THEN 'brand'
      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'
      ELSE NULL
    END AS campaign_id,
    CASE
      WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'
      WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'
      ELSE NULL
    END AS campaign_tag
  FROM emerging_pool_contacts epc
  LEFT JOIN latest_ghl_contacts lgc
    ON lgc.ghl_contact_id = epc.ghl_contact_id
  WHERE epc.ghl_contact_id IS NOT NULL
    AND epc.source_list IN ('brands', 'dispensaries')
    AND COALESCE(epc.primary_phone, '') <> ''
    AND NOT EXISTS (
      SELECT 1
      FROM voice_call_attempt a
      WHERE a.contact_id = epc.ghl_contact_id
    )
    AND NOT EXISTS (
      SELECT 1
      FROM voice_call_queue q
      WHERE q.contact_id = epc.ghl_contact_id
        AND q.status IN ('pending', 'in_progress')
    )
    AND NOT EXISTS (
      SELECT 1
      WHERE lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_already_called%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_call_attempted%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_dnc%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%do not contact%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_human_answered%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_not_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interest_unknown%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail_left%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_no_answer%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_busy%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_wrong_number%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_contact_disconnected%'
    )
)
SELECT
  emerging_pool_row_id,
  emerald_contact_id,
  source_list,
  contact_id,
  campaign_id,
  campaign_tag,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  ghl_phone,
  ghl_email
FROM eligible_contacts
WHERE campaign_tag IS NOT NULL
ORDER BY source_list, emerging_pool_row_id;

-- Summary by pool.
WITH candidate_rows AS (
  SELECT * FROM (
    WITH latest_ghl_contacts AS (
      SELECT DISTINCT ON (source_key)
        source_key,
        regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
        dimensions_json
      FROM report_raw_ghl_contacts
      WHERE source_system = 'ghl'
        AND source_key LIKE 'contact:%'
      ORDER BY source_key, report_date DESC, loaded_at DESC
    )
    SELECT
      epc.source_list
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
        SELECT 1 FROM voice_call_queue q
        WHERE q.contact_id = epc.ghl_contact_id
          AND q.status IN ('pending', 'in_progress')
      )
  ) t
)
SELECT source_list, COUNT(*) AS eligible_count
FROM candidate_rows
GROUP BY source_list
ORDER BY source_list;
