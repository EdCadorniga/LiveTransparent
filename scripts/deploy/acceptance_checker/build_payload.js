function clean(v) {
  if (v === undefined || v === null) return '';
  return String(v).trim();
}
function first() {
  for (const value of arguments) {
    const s = clean(value);
    if (s) return s;
  }
  return '';
}
const event = $node['Normalize LinkedIn Acceptance Event'].json || {};
const config = $node['Config'].json || {};
const now = new Date().toISOString();
const rows = $input.all().map((item) => item.json || {}).filter((row) => clean(row.ghl_contact_id));

if (!rows.length) {
  return [{
    json: {
      matched: false,
      connected: event.is_connected === true,
      reason: event.is_connected === true ? 'no_state_row' : 'not_connected',
      network_distance: event.network_distance || '',
      accepted_at: event.accepted_at || now,
      event_type: event.event_type || 'new_relation',
      provider_id: event.linkedin_provider_id || '',
      identifier: event.linkedin_public_identifier || '',
      profile_url: event.linkedin_profile_url || '',
      tag_ok: false,
      upsert_ok: false,
    },
  }];
}

const results = [];
for (const row of rows) {
  const sourceTable = clean(row.source_table) || 'linkedin_connection_state';
  const isPartnership = sourceTable === 'partnership_linkedin_connection_state';
  const payload = {
    ghl_contact_id: row.ghl_contact_id,
    location_id: row.location_id || config.GHL_LOCATION_ID || '',
    unipile_account_id: row.unipile_account_id || event.unipile_account_id || config.UNIPILE_ACCOUNT_ID || '',
    linkedin_profile_url: row.linkedin_profile_url || event.linkedin_profile_url || '',
    linkedin_public_identifier: row.linkedin_public_identifier || event.linkedin_public_identifier || '',
    linkedin_provider_id: row.linkedin_provider_id || event.linkedin_provider_id || '',
    connection_request_tag: row.connection_request_tag || (isPartnership ? 'partner_linkedin_requested' : 'linkedin_connection_requested'),
    connection_status: 'connected',
    request_sent_at: row.request_sent_at || null,
    connected_at: event.accepted_at || now,
    dm_sequence_started_at: row.dm_sequence_started_at || null,
    last_checked_at: now,
    request_message: row.request_message || '',
    request_message_hash: row.request_message_hash || '',
    sequence_step: Number(row.sequence_step || 0),
    payload_json: {
      matched: true,
      event_type: event.event_type || 'new_relation',
      is_sender: event.is_sender === true,
      network_distance: event.network_distance || '',
      is_relationship: event.is_relationship === true,
      accepted_at: event.accepted_at || now,
      prior_status: row.connection_status || '',
    },
    metadata_json: { source: 'acceptance_checker', event_type: event.event_type || 'new_relation', is_relationship: event.is_relationship === true },
  };
  if (isPartnership) {
    payload.table = sourceTable;
    payload.source_key = 'partnership';
  }

  let upsert_ok = false;
  let upsert_error = '';
  try {
    await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert',
      headers: { 'X-LT-LinkedIn-State-Secret': String(config.stateUpsertSecret || ''), 'Content-Type': 'application/json' },
      body: payload,
      json: true,
    });
    upsert_ok = true;
  } catch (e) {
    upsert_error = (e && e.message) || String(e);
  }

  const tagName = isPartnership ? 'partner_linkedin_connected' : 'linkedin_connected';
  let tag_ok = false;
  let tag_error = '';
  try {
    await this.helpers.httpRequest({
      method: 'POST',
      url: (config.GHL_API_BASE_URL || 'https://services.leadconnectorhq.com') + '/contacts/' + encodeURIComponent(row.ghl_contact_id) + '/tags',
      headers: {
        Authorization: 'Bearer ' + String(config.GHL_API_KEY || ''),
        Version: '2021-07-28',
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: { tags: [tagName] },
      json: true,
    });
    tag_ok = true;
  } catch (e) {
    tag_error = (e && e.message) || String(e);
  }

  results.push({
    json: {
      matched: true,
      connected: true,
      accepted_at: payload.connected_at,
      ghl_contact_id: row.ghl_contact_id,
      connection_status: 'connected',
      provider_id: row.linkedin_provider_id || event.linkedin_provider_id || '',
      identifier: row.linkedin_public_identifier || event.linkedin_public_identifier || '',
      profile_url: row.linkedin_profile_url || event.linkedin_profile_url || '',
      source_table: sourceTable,
      is_partnership: isPartnership,
      tag_applied: tagName,
      upsert_ok,
      upsert_error,
      tag_ok,
      tag_error,
    },
  });
}
return results;