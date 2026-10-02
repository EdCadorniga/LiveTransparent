function esc(v) {
  if (v === null || v === undefined) return 'NULL';
  return "'" + String(v).replace(/'/g, "''") + "'";
}

const items = $input.all();
const out = [];
for (const item of items) {
  const row = item.json || {};
  if (row.matched !== true) continue;
  const c = (k) => row[k] || '';
  const acceptedAt = c('accepted_at');
  const contactId = c('ghl_contact_id');
  const providerId = c('provider_id');
  const profileUrl = c('profile_url');
  const identifier = c('identifier');
  const isPartnership = !!(row.is_partnership);
  const sourceTable = c('source_table');

  const sql = `INSERT INTO linkedin_activity_events (event_key,event_type,event_at,ghl_contact_id,location_id,source_key,campaign_key,channel,linkedin_profile_url,linkedin_public_identifier,linkedin_provider_id,unipile_account_id,workflow_id,workflow_name,status,error_code,error_detail,payload_json,metadata_json)
SELECT CONCAT('connection_accepted:', ${esc(contactId)}, ':', COALESCE(NULLIF(${esc(providerId)}, ''), 'unknown')), 'connection_accepted', ${esc(acceptedAt)}::timestamptz, NULLIF(${esc(contactId)}, ''), 'Zwz4relUXVPxx8uohnjV', CASE WHEN ${isPartnership} THEN 'partnership' ELSE 'dan_linkedin' END, CASE WHEN ${isPartnership} THEN 'partnership_linkedin' ELSE 'dan_linkedin' END, 'linkedin', NULLIF(${esc(profileUrl)}, ''), NULLIF(${esc(identifier)}, ''), NULLIF(${esc(providerId)}, ''), 'V9eiHiDpRmCtan0YNdzsQw', '3ttEvr5NMcQCS4Hp', 'LT - LinkedIn Connection Acceptance Checker (Unipile)', 'accepted', NULL, NULL, jsonb_build_object('source_table', ${esc(sourceTable)}, 'matched', true), jsonb_build_object('source', 'acceptance_checker')
WHERE NULLIF(${esc(contactId)}, '') IS NOT NULL AND ${esc(acceptedAt)}::text <> ''
ON CONFLICT (event_key) DO NOTHING;
SELECT ${esc(acceptedAt)}::text AS accepted_at;`;

  out.push({ json: { ...row, sqlQuery: sql } });
}

if (!out.length) {
  out.push({ json: { matched: false, sqlQuery: 'SELECT NULL::text AS accepted_at WHERE false;' } });
}
return out;