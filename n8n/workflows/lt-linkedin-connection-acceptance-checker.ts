import { workflow, node, trigger, newCredential } from '@n8n/workflow-sdk';

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook - LinkedIn Acceptance',
    parameters: {
      httpMethod: 'POST',
      path: 'lt-linkedin-connection-accepted',
      responseMode: 'responseNode',
      options: {},
    },
    position: [240, 320],
  },
  output: [{ body: {} }],
});

const normalize = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Normalize LinkedIn Acceptance Event',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `function clean(v) {
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
function unwrap(value) {
  let current = value;
  for (let i = 0; i < 3; i++) {
    if (!current || typeof current !== 'object') break;
    if (current.body && typeof current.body === 'object') {
      current = current.body;
      continue;
    }
    if (current.data && typeof current.data === 'object') {
      current = current.data;
      continue;
    }
    break;
  }
  return current;
}
function parseDate(v) {
  const s = clean(v);
  if (!s) return '';
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? s : d.toISOString();
}

const raw = unwrap($json || {});
const body = raw && typeof raw === 'object' ? raw : {};
const user = body.user && typeof body.user === 'object' ? body.user : {};
const event = first(body.event, body.type, body.action, body.name) || 'new_relation';
const now = new Date().toISOString();

return [{
  json: {
    event_type: event,
    unipile_account_id: first(body.account_id, body.accountId, body.user_account_id, user.account_id, user.accountId),
    linkedin_provider_id: first(body.user_provider_id, body.provider_id, body.providerId, user.provider_id, user.providerId, user.id),
    linkedin_public_identifier: first(body.user_public_identifier, body.public_identifier, body.publicIdentifier, user.public_identifier, user.publicIdentifier, user.public_identifier),
    linkedin_profile_url: first(body.user_profile_url, body.profile_url, body.profileUrl, user.profile_url, user.profileUrl),
    accepted_at: parseDate(first(body.accepted_at, body.acceptedAt, body.created_at, body.createdAt, body.timestamp, now)) || now,
    raw_body: body,
  },
}];`,
    },
    position: [480, 320],
  },
  output: [{ json: { event_type: 'new_relation' } }],
});

const queryMatch = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Find LinkedIn State Row',
    parameters: {
      operation: 'executeQuery',
      query: `WITH match AS (
SELECT
  ghl_contact_id,
  location_id,
  unipile_account_id,
  linkedin_profile_url,
  linkedin_public_identifier,
  linkedin_provider_id,
  connection_request_tag,
  connection_status,
  request_sent_at,
  connected_at,
  dm_sequence_started_at,
  last_checked_at,
  request_message,
  request_message_hash,
  sequence_step,
  payload_json,
  metadata_json
FROM linkedin_connection_state
WHERE
  (
    ($1 <> '' AND unipile_account_id = $1 AND linkedin_provider_id = $2 AND $2 <> '')
    OR ($1 <> '' AND unipile_account_id = $1 AND linkedin_public_identifier = $3 AND $3 <> '')
    OR (linkedin_profile_url = $4 AND $4 <> '')
  )
LIMIT 1
)
SELECT * FROM match
UNION ALL
SELECT
  NULL::text AS ghl_contact_id,
  NULL::text AS location_id,
  NULL::text AS unipile_account_id,
  NULL::text AS linkedin_profile_url,
  NULL::text AS linkedin_public_identifier,
  NULL::text AS linkedin_provider_id,
  NULL::text AS connection_request_tag,
  NULL::text AS connection_status,
  NULL::timestamptz AS request_sent_at,
  NULL::timestamptz AS connected_at,
  NULL::timestamptz AS dm_sequence_started_at,
  NULL::timestamptz AS last_checked_at,
  NULL::text AS request_message,
  NULL::text AS request_message_hash,
  0::integer AS sequence_step,
  '{}'::jsonb AS payload_json,
  '{}'::jsonb AS metadata_json
WHERE NOT EXISTS (SELECT 1 FROM match);`,
      options: {
        queryReplacement: '={{ [ $json.unipile_account_id || $env.UNIPILE_ACCOUNT_ID || "", $json.linkedin_provider_id || "", $json.linkedin_public_identifier || "", $json.linkedin_profile_url || "" ] }}',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [720, 320],
  },
  output: [{ ghl_contact_id: 'contact-123' }],
});

const updateState = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Acceptance Upsert Payload',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `function clean(v) {
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
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
const event = $node['Normalize LinkedIn Acceptance Event'].json || {};
const row = $input.first()?.json || {};
const now = new Date().toISOString();
const matched = !!clean(row.ghl_contact_id);

if (!matched) {
  return [{ json: { matched: false, accepted_at: event.accepted_at || now, event_type: event.event_type || 'new_relation' } }];
}

const payload = {
  ghl_contact_id: row.ghl_contact_id,
  location_id: row.location_id || '',
  unipile_account_id: row.unipile_account_id || event.unipile_account_id || '',
  linkedin_profile_url: row.linkedin_profile_url || event.linkedin_profile_url || '',
  linkedin_public_identifier: row.linkedin_public_identifier || event.linkedin_public_identifier || '',
  linkedin_provider_id: row.linkedin_provider_id || event.linkedin_provider_id || '',
  connection_request_tag: row.connection_request_tag || 'linkedin_connection_requested',
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
    event: event.raw_body || {},
    state_row: row,
  },
  metadata_json: {
    source: 'acceptance_checker',
    event_type: event.event_type || 'new_relation',
  },
};

const upsertResp = await doHttpRequest.call(this, {
  method: 'POST',
  url: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert',
  headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
  body: payload,
  json: true,
});

return [{
  json: {
    matched: true,
    accepted_at: payload.connected_at,
    ghl_contact_id: row.ghl_contact_id,
    connection_status: 'connected',
    provider_id: row.linkedin_provider_id || event.linkedin_provider_id || '',
    identifier: row.linkedin_public_identifier || event.linkedin_public_identifier || '',
    upsert_ok: !!upsertResp,
  },
}];`,
    },
    position: [960, 320],
  },
  output: [{ json: { matched: true } }],
});

const upsert = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Mark LinkedIn Connected',
    parameters: {
      operation: 'executeQuery',
      query: `INSERT INTO linkedin_connection_state (
  ghl_contact_id,
  location_id,
  unipile_account_id,
  linkedin_profile_url,
  linkedin_public_identifier,
  linkedin_provider_id,
  connection_request_tag,
  connection_status,
  request_sent_at,
  connected_at,
  dm_sequence_started_at,
  last_checked_at,
  request_message,
  request_message_hash,
  sequence_step,
  payload_json,
  metadata_json,
  created_at,
  updated_at
) VALUES (
  $1,
  $2,
  $3,
  $4,
  $5,
  $6,
  $7,
  $8,
  $9::timestamptz,
  $10::timestamptz,
  $11::timestamptz,
  $12::timestamptz,
  $13,
  $14,
  $15,
  $16::jsonb,
  $17::jsonb,
  NOW(),
  NOW()
)
ON CONFLICT (ghl_contact_id) DO UPDATE SET
  location_id = EXCLUDED.location_id,
  unipile_account_id = EXCLUDED.unipile_account_id,
  linkedin_profile_url = EXCLUDED.linkedin_profile_url,
  linkedin_public_identifier = EXCLUDED.linkedin_public_identifier,
  linkedin_provider_id = EXCLUDED.linkedin_provider_id,
  connection_request_tag = EXCLUDED.connection_request_tag,
  connection_status = EXCLUDED.connection_status,
  request_sent_at = COALESCE(EXCLUDED.request_sent_at, linkedin_connection_state.request_sent_at),
  connected_at = COALESCE(EXCLUDED.connected_at, linkedin_connection_state.connected_at),
  dm_sequence_started_at = COALESCE(EXCLUDED.dm_sequence_started_at, linkedin_connection_state.dm_sequence_started_at),
  last_checked_at = EXCLUDED.last_checked_at,
  request_message = COALESCE(EXCLUDED.request_message, linkedin_connection_state.request_message),
  request_message_hash = COALESCE(EXCLUDED.request_message_hash, linkedin_connection_state.request_message_hash),
  sequence_step = GREATEST(linkedin_connection_state.sequence_step, EXCLUDED.sequence_step),
  payload_json = COALESCE(linkedin_connection_state.payload_json, '{}'::jsonb) || COALESCE(EXCLUDED.payload_json, '{}'::jsonb),
  metadata_json = COALESCE(linkedin_connection_state.metadata_json, '{}'::jsonb) || COALESCE(EXCLUDED.metadata_json, '{}'::jsonb),
  updated_at = NOW()
RETURNING ghl_contact_id, connection_status, connected_at, linkedin_provider_id, linkedin_public_identifier;`,
      options: {
        queryReplacement: '={{ [ $json.ghl_contact_id, $json.location_id, $json.unipile_account_id, $json.linkedin_profile_url, $json.linkedin_public_identifier, $json.linkedin_provider_id, $json.connection_request_tag, $json.connection_status, $json.request_sent_at || null, $json.connected_at || null, $json.dm_sequence_started_at || null, $json.last_checked_at || null, $json.request_message || null, $json.request_message_hash || null, Number($json.sequence_step || 0), JSON.stringify($json.payload_json || {}), JSON.stringify($json.metadata_json || {}) ] }}',
        queryBatching: 'independently',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [1200, 320],
  },
  output: [{ json: { ghl_contact_id: 'contact-123', connection_status: 'connected' } }],
});

const notify = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Add LinkedIn Connected Tag',
    parameters: {
      method: 'POST',
      url: '={{ "https://services.leadconnectorhq.com/contacts/" + $json.ghl_contact_id + "/tags" }}',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: '={{ "Bearer " + $env.GHL_API_KEY }}' },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={{ { tags: ["linkedin_connected"] } }}',
      options: { timeout: 30000 },
    },
    position: [1440, 320],
  },
  output: [{ json: {} }],
});

const result = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - Acceptance',
    parameters: {
      respondWith: 'json',
      responseBody: '={{ { ok: true, matched: $("Build Acceptance Upsert Payload").item.json.matched || false, contact_id: $("Build Acceptance Upsert Payload").item.json.ghl_contact_id || null, connection_status: $("Build Acceptance Upsert Payload").item.json.connection_status || "unmatched", accepted_at: $("Build Acceptance Upsert Payload").item.json.accepted_at || null } }}',
      options: {},
    },
    position: [1680, 320],
  },
});

export default workflow('lt-linkedin-connection-acceptance-checker', 'LT - LinkedIn Connection Acceptance Checker (Unipile)')
  .add(webhook)
  .to(normalize)
  .to(queryMatch)
  .to(updateState)
  .to(result);
