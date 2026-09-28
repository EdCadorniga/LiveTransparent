-- Authoritative V1 count definitions.
-- These counts read raw GHL snapshots, not report_daily_summary or daily rollups.
-- The raw snapshot ingest must be healthy; the API exposes freshness separately.

authoritative_ghl_counts AS (
  SELECT jsonb_build_object(
    'new_contacts', (
      SELECT COUNT(DISTINCT NULLIF(source_key,''))::int
      FROM report_raw_ghl_contacts
      WHERE (COALESCE(NULLIF(payload_json->>'createdAt','')::timestamptz, report_date::timestamptz)
             AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
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
