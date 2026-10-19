canonical_contacts AS (
  SELECT DISTINCT ON(regexp_replace(source_key,'^contact:',''))
    regexp_replace(source_key,'^contact:','') AS contact_id,payload_json,dimensions_json
  FROM report_raw_ghl_contacts ORDER BY regexp_replace(source_key,'^contact:',''),report_date DESC,loaded_at DESC
), canonical_mql AS (
  SELECT DISTINCT ON(contact_id) contact_id,source,added_at
  FROM mql_tag_events WHERE tag='mql'
    AND (added_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  ORDER BY contact_id,added_at
), canonical_bookings AS (
  SELECT DISTINCT ON(a.contact_id) a.*,
    COALESCE(NULLIF(a.payload_json->>'dateAdded','')::timestamptz,a.start_at) AS booked_at
  FROM lt_exec_v1_appointment_facts a
  WHERE a.calendar_id IN ('SrtXcFVyea7pFl3nTiIK','WS6lacfQK2XOhqN7mRaF') AND NULLIF(a.contact_id,'') IS NOT NULL
    AND (a.start_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  ORDER BY a.contact_id,a.start_at,a.appointment_id
), canonical_appointment_origins AS (
  SELECT a.*,NULLIF(a.payload_json->>'dateAdded','')::timestamptz AS booked_at,
    COALESCE(pre.owner_id,pre_contact.owner_id,'unassigned') AS owner_id,
    COALESCE(ba.attributed,FALSE) AS campaign_attributed
  FROM lt_exec_v1_appointment_facts a
  LEFT JOIN LATERAL (
    SELECT COALESCE(NULLIF(o.dimensions_json->>'assigned_to',''),NULLIF(o.payload_json->>'assignedTo','')) AS owner_id
    FROM report_raw_ghl_opportunities o
    WHERE COALESCE(o.dimensions_json->>'contact_id',o.payload_json->>'contactId')=a.contact_id
      AND o.loaded_at < NULLIF(a.payload_json->>'dateAdded','')::timestamptz
    ORDER BY o.loaded_at DESC LIMIT 1
  ) pre ON TRUE
  LEFT JOIN LATERAL (
    SELECT NULLIF(c.payload_json->>'assignedTo','') AS owner_id
    FROM report_raw_ghl_contacts c
    WHERE regexp_replace(c.source_key,'^contact:','')=a.contact_id
      AND c.loaded_at<NULLIF(a.payload_json->>'dateAdded','')::timestamptz
    ORDER BY c.loaded_at DESC LIMIT 1
  ) pre_contact ON TRUE
  LEFT JOIN lt_booking_attribution ba USING(appointment_id)
  WHERE a.calendar_id IN ('SrtXcFVyea7pFl3nTiIK','WS6lacfQK2XOhqN7mRaF') AND NULLIF(a.contact_id,'') IS NOT NULL
), canonical_booking_owners AS (
  SELECT DISTINCT ON(contact_id) * FROM canonical_appointment_origins
  WHERE (start_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  ORDER BY contact_id,start_at,appointment_id
), canonical_new_bookings AS (
  SELECT DISTINCT ON(contact_id) * FROM canonical_appointment_origins
  WHERE (booked_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  ORDER BY contact_id,booked_at,appointment_id
), canonical_first_qualified_booking AS (
  SELECT DISTINCT ON(contact_id) * FROM canonical_appointment_origins
  WHERE booked_at IS NOT NULL AND
    (owner_id IN ('yU85G6kfhtW4vUtx3QE6','sqGx5rp3oAUG610NXyjU','03p5GatJBH7i9zjMaIzm') OR campaign_attributed)
  ORDER BY contact_id,booked_at,appointment_id
), canonical_sql AS (
  SELECT appointment_id AS qualification_id,contact_id,appointment_id,calendar_id,owner_id
  FROM canonical_first_qualified_booking
  WHERE (booked_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
), canonical_sdr_events AS (
  SELECT COALESCE(NULLIF(c.payload_json->>'assignedTo',''),'unassigned') AS owner_id,'mqls' AS metric,m.contact_id AS event_id
  FROM canonical_mql m LEFT JOIN canonical_contacts c USING(contact_id)
  UNION ALL SELECT owner_id,'booked',contact_id FROM canonical_new_bookings
  UNION ALL SELECT owner_id,'sqls',qualification_id FROM canonical_sql
), canonical_sdr AS (
  SELECT owners.owner_id,COALESCE(r.user_name,'Unassigned / unattributed') AS owner_name,COALESCE(r.is_sdr,FALSE) AS is_sdr,
    COUNT(DISTINCT e.event_id) FILTER(WHERE metric='mqls')::int AS mqls,
    COUNT(DISTINCT e.event_id) FILTER(WHERE metric='sqls')::int AS sqls,
    COUNT(DISTINCT e.event_id) FILTER(WHERE metric='booked')::int AS booked
  FROM (SELECT user_id AS owner_id FROM report_sdr_registry WHERE is_sdr
    UNION SELECT owner_id FROM canonical_sdr_events) owners
  LEFT JOIN report_sdr_registry r ON r.user_id=owners.owner_id
  LEFT JOIN canonical_sdr_events e ON e.owner_id=owners.owner_id GROUP BY 1,2,3
), canonical_counts AS (
  SELECT (SELECT COUNT(*) FROM canonical_mql)::int AS mqls,
    (SELECT COUNT(DISTINCT contact_id) FROM canonical_sql)::int AS sqls,
    (SELECT COUNT(*) FROM canonical_bookings)::int AS meetings,
    (SELECT COUNT(*) FROM canonical_new_bookings)::int AS new_bookings,
    (SELECT COUNT(DISTINCT s.contact_id) FROM canonical_sql s JOIN canonical_mql m USING(contact_id))::int AS converted
), canonical_opportunity_creators AS (
  SELECT COALESCE(NULLIF(e.workflow_name,''),e.creator_kind,'Creator evidence pending') AS origin_kind,
    COUNT(DISTINCT o.source_key)::int AS opportunities
  FROM report_raw_ghl_opportunities o LEFT JOIN v1_opportunity_creator_evidence e ON e.opportunity_id=o.source_key
  WHERE (COALESCE(NULLIF(o.dimensions_json->>'source_created_at','')::timestamptz,
    NULLIF(o.payload_json->>'createdAt','')::timestamptz,NULLIF(o.payload_json->>'dateAdded','')::timestamptz,o.report_date::timestamptz)
    AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
  GROUP BY 1
), canonical_payload AS (
  SELECT _base.payload || jsonb_build_object(
    'metricVersion','verified-booking-v2',
    'reportRevision','booking-created-v1',
    'pipelineEntries',_base.payload->'funnel'->'sqls_entered',
    'mqlStageEntries',_base.payload->'funnel'->'mqls_entered',
    'funnel',(_base.payload->'funnel') || jsonb_build_object('mqls_entered',c.mqls,'sqls_entered',c.sqls,
      'mql_to_sql_rate',CASE WHEN c.mqls=0 THEN NULL ELSE round(c.converted::numeric/c.mqls,4) END,
      'mql_to_sql_converted',c.converted,
      'sql_to_closed_rate',NULL,'closed_won_sqls',NULL,'closed_lost_sqls',NULL,
      'basis','MQL: distinct tag-ledger contacts, recovered signals use original receipt time; SQL: first qualified approved-calendar booking by creation date, with pre-booking assignee or captured campaign attribution; no Sales Outreach-entry prerequisite'),
    'meetingSummary',jsonb_build_object('unique_contacts',c.meetings,'new_bookings_created',c.new_bookings,'basis','Meetings use scheduled Pacific date; new bookings use recorded appointment creation date'),
    'bookingAttributionPending',(SELECT COUNT(*) FROM canonical_new_bookings WHERE owner_id='unassigned' AND NOT campaign_attributed),
    'opportunityOrigin',(SELECT jsonb_agg(to_jsonb(x) ORDER BY opportunities DESC) FROM canonical_opportunity_creators x),
    'bookingClickers',(SELECT COALESCE(jsonb_agg(to_jsonb(x) ORDER BY last_click DESC),'[]'::jsonb) FROM (
      SELECT b.contact_id,MAX(COALESCE(c.payload_json->>'name',b.contact_id)) AS contact_name,
        MIN(b.clicked_at) AS first_click,MAX(b.clicked_at) AS last_click,COUNT(*) AS recorded_clicks,
        string_agg(DISTINCT b.vertical,', ') AS vertical
      FROM lt_booking_link_clicks b LEFT JOIN canonical_contacts c USING(contact_id)
      WHERE (b.clicked_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN $1::date AND $2::date
      GROUP BY b.contact_id) x),
    'meetingCalendars',(SELECT jsonb_agg(to_jsonb(x)) FROM (SELECT cal AS calendar_id,
      (SELECT COUNT(DISTINCT contact_id) FROM canonical_bookings b WHERE b.calendar_id=cal) AS contacts
      FROM unnest(ARRAY['SrtXcFVyea7pFl3nTiIK','WS6lacfQK2XOhqN7mRaF']) cal) x),
    'appointmentDetails',(SELECT COALESCE(jsonb_agg(to_jsonb(b)),'[]'::jsonb) FROM canonical_booking_owners b),
    'sdrOutputs',(SELECT jsonb_agg(to_jsonb(s) ORDER BY owner_name) FROM canonical_sdr s),
    'mqlsAdded',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (SELECT source AS origin_kind,COUNT(*) AS contacts FROM canonical_mql GROUP BY source) x),
    'mqlSourcesByForm',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (SELECT source,COUNT(*) AS contacts FROM canonical_mql GROUP BY source) x),
    'sqlBooking',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (SELECT calendar_id,'Verified appointment' AS booked_via,COUNT(DISTINCT contact_id) AS sqls FROM canonical_sql GROUP BY calendar_id) x),
    'sqlBookingBreakdown','[]'::jsonb,
    'bookingsBySource',(SELECT COALESCE(jsonb_agg(to_jsonb(x)),'[]'::jsonb) FROM (
      SELECT ba.booked_via_utm_source AS utm_source,ba.booked_via_medium AS utm_medium,ba.booked_via_campaign AS utm_campaign,COUNT(DISTINCT b.contact_id) AS contacts
      FROM canonical_new_bookings b LEFT JOIN lt_booking_attribution ba USING(appointment_id) GROUP BY 1,2,3) x),
    'verticalPerformance',(SELECT jsonb_agg(v || jsonb_build_object('mqls',
      (SELECT COUNT(*) FROM canonical_mql m JOIN canonical_contacts cc USING(contact_id)
       WHERE COALESCE((SELECT cf->>'value' FROM jsonb_array_elements(COALESCE(cc.payload_json->'customFields','[]'::jsonb)) cf WHERE cf->>'id'='ODs8fBt5te5HEfSJ91pY' LIMIT 1),'Unclassified')=v->>'vertical'),
      'sqls',(SELECT COUNT(*) FROM canonical_sql s JOIN canonical_contacts cc USING(contact_id)
       WHERE COALESCE((SELECT cf->>'value' FROM jsonb_array_elements(COALESCE(cc.payload_json->'customFields','[]'::jsonb)) cf WHERE cf->>'id'='ODs8fBt5te5HEfSJ91pY' LIMIT 1),'Unclassified')=v->>'vertical')))
      FROM jsonb_array_elements(_base.payload->'verticalPerformance') v)
  ) AS payload FROM _base CROSS JOIN canonical_counts c
)
SELECT payload FROM canonical_payload
