-- Company MQL / Active Pipeline Company Report
-- Run this in Postgres to get company-grouped contacts that are currently in active pipelines.
-- The result is ordered by the number of contacts per company so the largest active accounts float to the top.

WITH contacts AS (
  SELECT
    regexp_replace(c.source_key, '^contact:', '') AS ghl_contact_id,
    LOWER(TRIM(COALESCE(
      NULLIF(e.company_domain_key, ''),
      NULLIF(split_part(COALESCE(c.dimensions_json->>'email', c.payload_json->>'email', c.payload_json->>'emailAddress', ''), '@', 2), ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      regexp_replace(c.source_key, '^contact:', '')
    ))) AS company_key,
    COALESCE(
      NULLIF(c.dimensions_json->>'email', ''),
      NULLIF(c.payload_json->>'email', ''),
      NULLIF(c.payload_json->>'emailAddress', ''),
      ''
    ) AS email,
    COALESCE(
      NULLIF(e.company_name, ''),
      NULLIF(c.dimensions_json->>'company_name', ''),
      NULLIF(c.payload_json->>'companyName', ''),
      NULLIF(c.payload_json->>'company_name', ''),
      NULLIF(c.dimensions_json->>'company_name_for_emails', ''),
      NULLIF(c.payload_json->>'company_name_for_emails', ''),
      'Unknown'
    ) AS company_name,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_company_operating_state', ''),
      NULLIF(c.payload_json->>'em_company_operating_state', ''),
      NULLIF(c.dimensions_json->>'company_operating_state', ''),
      NULLIF(c.payload_json->>'company_operating_state', '')
    ) AS operating_state,
    COALESCE(
      NULLIF(c.dimensions_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'em_cannabis_marketing_signal', ''),
      NULLIF(c.dimensions_json->>'company_cannabis_marketing_signal', ''),
      NULLIF(c.payload_json->>'company_cannabis_marketing_signal', '')
    ) AS marketing_signal,
    COALESCE(
      NULLIF(c.payload_json->>'createdAt', ''),
      NULLIF(c.payload_json->>'created_at', ''),
      NULLIF(c.payload_json->>'dateAdded', ''),
      c.loaded_at::text
    )::date AS contact_date
  FROM report_raw_ghl_contacts c
  LEFT JOIN "Emerald_Contacts" e
    ON e.ghl_contact_id = regexp_replace(c.source_key, '^contact:', '')
),
opportunities AS (
  SELECT
    COALESCE(
      NULLIF(o.dimensions_json->>'contact_id', ''),
      NULLIF(o.dimensions_json->>'contact.id', ''),
      NULLIF(o.payload_json->>'contactId', ''),
      NULLIF(o.payload_json->>'contact_id', ''),
      NULLIF(o.payload_json->'contact'->>'id', '')
    ) AS ghl_contact_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineId', ''),
      NULLIF(o.dimensions_json->>'pipeline_id', ''),
      ''
    ) AS pipeline_id,
    COALESCE(
      NULLIF(o.payload_json->>'pipelineStageId', ''),
      NULLIF(o.dimensions_json->>'pipeline_stage_id', ''),
      ''
    ) AS stage_id,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_name', ''),
      NULLIF(o.payload_json->>'pipelineName', ''),
      NULLIF(o.payload_json->'pipeline'->>'name', ''),
      'Warm'
    ) AS pipeline_name,
    COALESCE(
      NULLIF(o.dimensions_json->>'pipeline_stage_name', ''),
      NULLIF(o.payload_json->>'pipelineStageName', ''),
      NULLIF(o.payload_json->'pipelineStage'->>'name', ''),
      NULLIF(o.payload_json->>'stage', ''),
      'MQL'
    ) AS stage_name
  FROM report_raw_ghl_opportunities o
),
company_rollup AS (
  SELECT
    c.company_key,
    COALESCE(NULLIF(MAX(c.company_name), ''), 'Unknown') AS company_name,
    COUNT(DISTINCT c.ghl_contact_id) AS contact_count,
    COUNT(DISTINCT c.ghl_contact_id) FILTER (WHERE o.ghl_contact_id IS NOT NULL) AS pipeline_contact_count,
    STRING_AGG(DISTINCT c.email, ', ' ORDER BY c.email) AS contact_emails,
    STRING_AGG(DISTINCT o.pipeline_name, '|' ORDER BY o.pipeline_name) FILTER (WHERE o.ghl_contact_id IS NOT NULL) AS pipelines,
    STRING_AGG(DISTINCT o.stage_name, '|' ORDER BY o.stage_name) FILTER (WHERE o.ghl_contact_id IS NOT NULL) AS stages,
    MAX(c.operating_state) AS operating_state,
    MAX(c.marketing_signal) AS marketing_signal,
    MAX(c.contact_date) AS latest_contact_date
  FROM contacts c
  LEFT JOIN opportunities o
    ON o.ghl_contact_id = c.ghl_contact_id
   AND COALESCE(o.stage_name, '') NOT IN ('Disqualified', 'Closed Lost', 'Closed Won')
  WHERE c.company_key IS NOT NULL
  GROUP BY c.company_key
  HAVING COUNT(DISTINCT c.ghl_contact_id) FILTER (WHERE o.ghl_contact_id IS NOT NULL) >= 1
)
SELECT
  company_key,
  company_name,
  contact_count,
  pipeline_contact_count,
  contact_emails,
  COALESCE(pipelines, '') AS pipelines,
  COALESCE(stages, '') AS stages,
  operating_state,
  marketing_signal,
  latest_contact_date
FROM company_rollup
ORDER BY pipeline_contact_count DESC, contact_count DESC, latest_contact_date DESC
LIMIT 5000;
