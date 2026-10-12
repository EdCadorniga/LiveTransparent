-- Authoritative V1 count definitions.
-- These counts read raw GHL snapshots, not report_daily_summary or daily rollups.
-- Contact creation is deduplicated by source_key and uses a stable source
-- timestamp (createdAt/dateAdded/source_created_at). A daily snapshot date is
-- only a last-resort first-observed date; it must not make the same contact
-- look newly created on every later snapshot. LinkedIn historical backfills
-- are reported separately and excluded from ordinary new-contact volume.

contact_creation_facts AS (
  SELECT source_key,
    MIN(COALESCE(
      (NULLIF(payload_json->>'createdAt','')::timestamptz AT TIME ZONE 'America/Los_Angeles')::date,
      (NULLIF(payload_json->>'dateAdded','')::timestamptz AT TIME ZONE 'America/Los_Angeles')::date
    )) AS created_date,
    MIN(report_date)::date AS first_observed_date,
    BOOL_OR(LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%historical backfill%'
         OR LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%unipile-backfill%'
         OR LOWER(payload_json::text || ' ' || dimensions_json::text) LIKE '%linkedin via unipile%') AS is_linkedin_backfill
  FROM report_raw_ghl_contacts
  WHERE source_system='ghl' AND NULLIF(source_key,'') IS NOT NULL
  GROUP BY source_key
), authoritative_ghl_counts AS (
  SELECT jsonb_build_object(
    'new_contacts', (
      SELECT COUNT(*)::int
      FROM contact_creation_facts
      WHERE COALESCE(created_date, first_observed_date) BETWEEN $1::date AND $2::date
        AND NOT COALESCE(is_linkedin_backfill,FALSE)
    ),
    'linkedin_backfill_contacts', (
      SELECT COUNT(*)::int FROM contact_creation_facts
      WHERE COALESCE(created_date, first_observed_date) BETWEEN $1::date AND $2::date
        AND COALESCE(is_linkedin_backfill,FALSE)
    ),
    'new_contacts_date_unavailable', (
      SELECT COUNT(*)::int FROM contact_creation_facts
      WHERE first_observed_date BETWEEN $1::date AND $2::date AND created_date IS NULL
        AND NOT COALESCE(is_linkedin_backfill,FALSE)
    ),
    'opportunities_created', (
      SELECT COUNT(DISTINCT NULLIF(source_key,''))::int
      FROM report_raw_ghl_opportunities
      WHERE (COALESCE(NULLIF(dimensions_json->>'source_created_at','')::timestamptz,
                      NULLIF(payload_json->>'createdAt','')::timestamptz,
                      NULLIF(payload_json->>'dateAdded','')::timestamptz,
                      report_date::timestamptz)
             AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
    ),
    'mqls_entered', (
      SELECT COUNT(*)::int FROM (
        SELECT source_key, MIN(report_date)::date AS first_mql_date
        FROM report_raw_ghl_opportunities
        WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id',''), NULLIF(payload_json->>'pipelineId','')) = 'FRjpDZ1HWj3UPgczsu3t'
          AND COALESCE(NULLIF(dimensions_json->>'pipeline_stage_id',''), NULLIF(payload_json->>'pipelineStageId','')) = '3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2'
        GROUP BY source_key
      ) x WHERE first_mql_date BETWEEN $1::date AND $2::date
    ),
    'sqls_entered', (
      SELECT COUNT(*)::int FROM (
        SELECT source_key, MIN(report_date)::date AS first_sql_date
        FROM report_raw_ghl_opportunities
        WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id',''), NULLIF(payload_json->>'pipelineId','')) = 'dhdlf3O4tymxFtHk4aqq'
        GROUP BY source_key
      ) x WHERE first_sql_date BETWEEN $1::date AND $2::date
    ),
    'basis', 'raw GHL snapshot facts; distinct contact/opportunity IDs; America/Los_Angeles dates'
  ) AS payload
)
