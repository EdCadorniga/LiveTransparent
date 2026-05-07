-- Company MQL Report - SQL Query
-- Run this in Postgres to get the data, then export to CSV for Google Sheets

SELECT 
  COALESCE(e.company_domain_key, c.dimensions_json->>'company_name') AS company_key,
  COALESCE(e.company_name, c.dimensions_json->>'company_name', 'Unknown') AS company_name,
  COUNT(DISTINCT c.contact_id) AS contact_count,
  STRING_AGG(DISTINCT c.email, ', ' ORDER BY c.email) AS contact_emails,
  STRING_AGG(DISTINCT o.pipeline_name, '|' ORDER BY o.pipeline_name) AS pipelines,
  STRING_AGG(DISTINCT o.stage_name, '|' ORDER BY o.stage_name) AS stages,
  MAX(e.company_operating_state) AS operating_state,
  MAX(e.company_cannabis_marketing_signal) AS marketing_signal,
  MAX(c.created_at::date) AS latest_contact_date
FROM report_raw_ghl_contacts c
JOIN report_raw_ghl_opportunities o 
  ON o.contact_id = c.contact_id
LEFT JOIN "Emerald_Contacts" e 
  ON e.ghl_contact_id = c.contact_id
WHERE o.pipeline_name IN ('Warm', 'Sales Outreach')
  AND o.stage_name NOT IN ('Disqualified', 'Closed Lost', 'Closed Won')
GROUP BY company_key, company_name, e.company_operating_state, e.company_cannabis_marketing_signal
HAVING COUNT(DISTINCT c.contact_id) >= 1
ORDER BY contact_count DESC, latest_contact_date DESC
LIMIT 500;
