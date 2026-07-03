-- Post-import audit checks for Emerald pool -> GHL linkage quality.
--
-- Use after:
-- 1) GHL import completes
-- 2) report_raw_ghl_contacts has landed the imported contacts
-- 3) ghl_contact_id backfill has run

-- Audit 1: Emerald ID uniqueness inside emerging_pool_contacts.
SELECT
  source_list,
  emerald_contact_id::text AS emerald_contact_id,
  COUNT(*) AS row_count
FROM emerging_pool_contacts
GROUP BY source_list, emerald_contact_id::text
HAVING COUNT(*) > 1
ORDER BY row_count DESC, source_list, emerald_contact_id::text;

-- Audit 2: multiple Emerald rows linked to the same GHL contact.
SELECT
  ghl_contact_id,
  COUNT(*) AS linked_rows,
  STRING_AGG(DISTINCT source_list, ', ' ORDER BY source_list) AS source_lists,
  STRING_AGG(DISTINCT emerald_contact_id::text, ', ' ORDER BY emerald_contact_id::text) AS emerald_contact_ids
FROM emerging_pool_contacts
WHERE ghl_contact_id IS NOT NULL
GROUP BY ghl_contact_id
HAVING COUNT(*) > 1
ORDER BY linked_rows DESC, ghl_contact_id;

-- Audit 3: pool contacts landed in report_raw_ghl_contacts but missing Em_Emerald_Contact_ID.
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
pool_contacts AS (
  SELECT
    ghl_contact_id,
    loaded_at,
    dimensions_json->>'contact_name' AS contact_name,
    dimensions_json->>'email' AS email,
    dimensions_json->>'phone' AS phone,
    dimensions_json->>'company_name' AS company_name,
    dimensions_json->>'tags' AS tags_text,
    EXISTS (
      SELECT 1
      FROM jsonb_array_elements(
        CASE
          WHEN jsonb_typeof(payload_json->'customFields') = 'array' THEN payload_json->'customFields'
          WHEN jsonb_typeof(payload_json->'customFields'->'fields') = 'array' THEN payload_json->'customFields'->'fields'
          WHEN jsonb_typeof(payload_json->'customFields'->'data') = 'array' THEN payload_json->'customFields'->'data'
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
    ) AS has_emerald_contact_id
  FROM latest_ghl_contacts
  WHERE lower(COALESCE(dimensions_json->>'tags', '')) LIKE '%brands_pool%'
     OR lower(COALESCE(dimensions_json->>'tags', '')) LIKE '%dispensaries_pool%'
)
SELECT
  ghl_contact_id,
  contact_name,
  email,
  phone,
  company_name,
  tags_text,
  loaded_at
FROM pool_contacts
WHERE has_emerald_contact_id = false
ORDER BY loaded_at DESC
LIMIT 100;

-- Audit 4: current match coverage by pool.
SELECT
  source_list,
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE ghl_contact_id IS NOT NULL) AS with_ghl_contact_id,
  COUNT(*) FILTER (WHERE ghl_opportunity_id IS NOT NULL AND ghl_opportunity_id <> '') AS with_ghl_opportunity_id,
  COUNT(*) FILTER (WHERE primary_phone IS NOT NULL AND primary_phone <> '') AS with_phone,
  COUNT(*) FILTER (WHERE primary_email IS NOT NULL AND primary_email <> '') AS with_email
FROM emerging_pool_contacts
GROUP BY source_list
ORDER BY source_list;

-- Audit 5: queue-linked pool rows.
SELECT
  epc.source_list,
  q.campaign_id,
  q.status,
  COUNT(*) AS row_count
FROM emerging_pool_contacts epc
JOIN voice_call_queue q
  ON q.contact_id = epc.ghl_contact_id
GROUP BY epc.source_list, q.campaign_id, q.status
ORDER BY epc.source_list, q.campaign_id, q.status;

-- Audit 6: queued GHL contacts not linked back to the imported pool.
SELECT
  q.contact_id,
  q.first_name,
  q.phone_e164,
  q.campaign_id,
  q.status,
  q.created_at
FROM voice_call_queue q
LEFT JOIN emerging_pool_contacts epc
  ON epc.ghl_contact_id = q.contact_id
WHERE q.campaign_id IN ('brand', 'dispensary')
  AND epc.id IS NULL
ORDER BY q.created_at DESC
LIMIT 100;
