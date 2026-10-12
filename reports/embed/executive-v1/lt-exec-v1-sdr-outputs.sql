sdr_output_owners AS (
  SELECT DISTINCT ON (o.source_key) o.source_key AS opportunity_id,
    COALESCE(NULLIF(o.dimensions_json->>'assigned_to',''),NULLIF(o.payload_json->>'assignedTo',''),'unassigned') AS owner_id
  FROM report_raw_ghl_opportunities o
  ORDER BY o.source_key,o.report_date DESC,o.loaded_at DESC
), sdr_output_events AS (
  SELECT COALESCE(o.owner_id,'unassigned') AS owner_id,'mqls' AS metric, m.opportunity_id AS event_id
  FROM feedback_mql m LEFT JOIN sdr_output_owners o USING(opportunity_id)
  WHERE m.entered_at BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT COALESCE(o.owner_id,'unassigned'),'sqls',s.opportunity_id
  FROM feedback_sql s LEFT JOIN sdr_output_owners o USING(opportunity_id)
  WHERE s.entered_at BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT COALESCE(o.owner_id,'unassigned'),'converted',s.opportunity_id
  FROM feedback_sql s JOIN feedback_mql m USING(opportunity_id)
  LEFT JOIN sdr_output_owners o USING(opportunity_id)
  WHERE s.entered_at BETWEEN $1::date AND $2::date AND m.entered_at<=s.entered_at
), sdr_booking_contacts AS (
  SELECT DISTINCT ON(a.contact_id) a.contact_id,
    COALESCE(origin.user_id,creator.user_id,'unassigned') AS owner_id
  FROM lt_exec_v1_appointment_facts a
  LEFT JOIN LATERAL (
    SELECT c.payload_json FROM report_raw_ghl_contacts c
    WHERE regexp_replace(c.source_key,'^contact:','')=a.contact_id
    ORDER BY c.report_date DESC,c.loaded_at DESC LIMIT 1
  ) c ON TRUE
  LEFT JOIN LATERAL (
    SELECT r.user_id FROM jsonb_array_elements(CASE WHEN jsonb_typeof(c.payload_json->'customFields')='array' THEN c.payload_json->'customFields' ELSE '[]'::jsonb END) cf
    JOIN report_sdr_registry r ON lower(COALESCE(cf->>'value',cf->>'fieldValue','')) IN (lower(r.user_id),lower(r.email)) AND r.is_sdr
    WHERE cf->>'id'='wBGXjev0rKowcfxTSWNa' LIMIT 1
  ) origin ON TRUE
  LEFT JOIN report_sdr_registry creator ON creator.user_id=a.payload_json->'createdBy'->>'userId' AND creator.is_sdr
  WHERE a.calendar_id='SrtXcFVyea7pFl3nTiIK' AND NULLIF(a.contact_id,'') IS NOT NULL
    AND (a.start_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  ORDER BY a.contact_id,(origin.user_id IS NOT NULL OR creator.user_id IS NOT NULL) DESC,a.start_at,a.appointment_id
), sdr_output_rows AS (
  SELECT owners.owner_id,COALESCE(r.user_name,CASE WHEN owners.owner_id='unassigned' THEN 'Unassigned / unattributed' ELSE 'Unknown owner' END) AS owner_name,
    COALESCE(r.is_sdr,FALSE) AS is_sdr,
    (SELECT COUNT(*) FROM sdr_output_events e WHERE e.owner_id=owners.owner_id AND metric='mqls')::int AS mqls,
    (SELECT COUNT(*) FROM sdr_output_events e WHERE e.owner_id=owners.owner_id AND metric='sqls')::int AS sqls,
    (SELECT COUNT(*) FROM sdr_output_events e WHERE e.owner_id=owners.owner_id AND metric='converted')::int AS converted,
    (SELECT COUNT(*) FROM sdr_booking_contacts b WHERE b.owner_id=owners.owner_id)::int AS booked
  FROM (SELECT user_id AS owner_id FROM report_sdr_registry WHERE is_sdr
    UNION SELECT owner_id FROM sdr_output_events UNION SELECT owner_id FROM sdr_booking_contacts) owners
  LEFT JOIN report_sdr_registry r ON r.user_id=owners.owner_id
), band_source_events AS (
  SELECT opportunity_id,contact_id,'opportunities' AS metric FROM latest_feedback_opps WHERE created_date BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT m.opportunity_id,o.contact_id,'mqls' FROM feedback_mql m JOIN latest_feedback_opps o USING(opportunity_id) WHERE m.entered_at BETWEEN $1::date AND $2::date
  UNION ALL
  SELECT s.opportunity_id,o.contact_id,'sqls' FROM feedback_sql s JOIN latest_feedback_opps o USING(opportunity_id) WHERE s.entered_at BETWEEN $1::date AND $2::date
), band_source_details AS (
  SELECT e.*,COALESCE(NULLIF(c.dimensions_json->>'utm_source_first',''),NULLIF(c.dimensions_json->>'source',''),NULLIF(c.payload_json->>'source',''),'Unknown / Unattributed') AS source
  FROM band_source_events e
  LEFT JOIN LATERAL (
    SELECT c.dimensions_json,c.payload_json FROM report_raw_ghl_contacts c
    WHERE regexp_replace(c.source_key,'^contact:','')=e.contact_id
    ORDER BY c.report_date DESC,c.loaded_at DESC LIMIT 1
  ) c ON TRUE
), band_source_rows AS (
  SELECT source,COUNT(*) FILTER(WHERE metric='opportunities')::int AS opportunities,
    COUNT(*) FILTER(WHERE metric='mqls')::int AS mqls,COUNT(*) FILTER(WHERE metric='sqls')::int AS sqls
  FROM band_source_details GROUP BY source
)
