function esc(v) {
  if (v === null || v === undefined) return 'NULL';
  return "'" + String(v).replace(/'/g, "''") + "'";
}

const row = $input.first().json;
const c = (k) => row[k] || '';
const isConnected = row.is_connected === true;
const unipileAcctId = c('unipile_account_id') || $('Config').item.json.UNIPILE_ACCOUNT_ID || '';
const providerId = c('linkedin_provider_id');
const identifier = c('linkedin_public_identifier');
const profileUrl = c('linkedin_profile_url');

const predicates = `((${esc(unipileAcctId)} <> '' AND unipile_account_id = ${esc(unipileAcctId)} AND linkedin_provider_id = ${esc(providerId)} AND ${esc(providerId)} <> '') OR (${esc(unipileAcctId)} <> '' AND unipile_account_id = ${esc(unipileAcctId)} AND linkedin_public_identifier = ${esc(identifier)} AND ${esc(identifier)} <> '') OR (linkedin_profile_url = ${esc(profileUrl)} AND ${esc(profileUrl)} <> ''))`;
const gate = isConnected ? predicates : 'false';

const sql = `WITH main AS (
SELECT ghl_contact_id, location_id, unipile_account_id, linkedin_profile_url, linkedin_public_identifier, linkedin_provider_id, connection_request_tag, connection_status, request_sent_at, connected_at, dm_sequence_started_at, last_checked_at, request_message, request_message_hash, sequence_step, payload_json, metadata_json, 'linkedin_connection_state'::text AS source_table
FROM linkedin_connection_state
WHERE ${gate}
)
SELECT * FROM main
UNION ALL
SELECT ghl_contact_id, location_id, unipile_account_id, linkedin_profile_url, linkedin_public_identifier, linkedin_provider_id, connection_request_tag, connection_status, request_sent_at, connected_at, dm_sequence_started_at, last_checked_at, request_message, request_message_hash, sequence_step, payload_json, metadata_json, 'partnership_linkedin_connection_state'::text AS source_table
FROM partnership_linkedin_connection_state
WHERE NOT EXISTS (SELECT 1 FROM main)
  AND ${gate}`;

return [{ json: { ...row, sqlQuery: sql } }];