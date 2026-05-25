import { workflow, node, trigger, newCredential, expr } from '@n8n/workflow-sdk';

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook - LinkedIn State Upsert',
    parameters: {
      httpMethod: 'POST',
      path: 'lt-linkedin-connection-state-upsert',
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
    name: 'Normalize LinkedIn State Payload',
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
const now = new Date().toISOString();
const requestMessage = clean(first(body.request_message, body.requestMessage));
const requestMessageHash = clean(first(body.request_message_hash, body.requestMessageHash));
const payloadJson = body.payload_json && typeof body.payload_json === 'object' ? body.payload_json : body;
const metadataJson = body.metadata_json && typeof body.metadata_json === 'object' ? body.metadata_json : {};
const connectionStatus = clean(first(body.connection_status, body.connectionStatus, body.status, body.connection_state)) || (parseDate(body.connected_at) ? 'connected' : 'requested');

return [{
  json: {
    ghl_contact_id: first(body.ghl_contact_id, body.contact_id, body.contactId, body.ghlContactId),
    location_id: first(body.location_id, body.locationId),
    unipile_account_id: first(body.unipile_account_id, body.unipileAccountId),
    linkedin_profile_url: first(body.linkedin_profile_url, body.linkedinProfileUrl, body.profile_url, body.profileUrl, body.liUrl),
    linkedin_public_identifier: first(body.linkedin_public_identifier, body.linkedinPublicIdentifier, body.public_identifier, body.publicIdentifier, body.identifier),
    linkedin_provider_id: first(body.linkedin_provider_id, body.linkedinProviderId, body.provider_id, body.providerId),
    connection_request_tag: first(body.connection_request_tag, body.connectionRequestTag, 'linkedin_connection_requested'),
    connection_status: connectionStatus,
    request_sent_at: parseDate(first(body.request_sent_at, body.requestSentAt, body.sent_at, body.sentAt)),
    connected_at: parseDate(first(body.connected_at, body.connectedAt)),
    dm_sequence_started_at: parseDate(first(body.dm_sequence_started_at, body.dmSequenceStartedAt)),
    last_checked_at: parseDate(first(body.last_checked_at, body.lastCheckedAt, now)) || now,
    request_message: requestMessage,
    request_message_hash: requestMessageHash,
    sequence_step: Number.isFinite(Number(body.sequence_step ?? body.sequenceStep)) ? Number(body.sequence_step ?? body.sequenceStep) : 0,
    payload_json: payloadJson,
    metadata_json: metadataJson,
    source_workflow_name: first(body.source_workflow_name, body.sourceWorkflowName),
    source_key: first(body.source_key, body.sourceKey),
    status_note: first(body.status_note, body.statusNote),
    raw_body: body,
  },
}];`,
    },
    position: [520, 320],
  },
  output: [{ json: { ghl_contact_id: 'contact-123', connection_status: 'requested' } }],
});

const upsert = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert LinkedIn Connection State',
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
  location_id = COALESCE(NULLIF(EXCLUDED.location_id, ''), linkedin_connection_state.location_id),
  unipile_account_id = COALESCE(NULLIF(EXCLUDED.unipile_account_id, ''), linkedin_connection_state.unipile_account_id),
  linkedin_profile_url = COALESCE(NULLIF(EXCLUDED.linkedin_profile_url, ''), linkedin_connection_state.linkedin_profile_url),
  linkedin_public_identifier = COALESCE(NULLIF(EXCLUDED.linkedin_public_identifier, ''), linkedin_connection_state.linkedin_public_identifier),
  linkedin_provider_id = COALESCE(NULLIF(EXCLUDED.linkedin_provider_id, ''), linkedin_connection_state.linkedin_provider_id),
  connection_request_tag = COALESCE(NULLIF(EXCLUDED.connection_request_tag, ''), linkedin_connection_state.connection_request_tag),
  connection_status = CASE
    WHEN linkedin_connection_state.connection_status = 'connected' AND EXCLUDED.connection_status <> 'connected'
      THEN linkedin_connection_state.connection_status
    ELSE EXCLUDED.connection_status
  END,
  request_sent_at = COALESCE(linkedin_connection_state.request_sent_at, EXCLUDED.request_sent_at),
  connected_at = COALESCE(linkedin_connection_state.connected_at, EXCLUDED.connected_at),
  dm_sequence_started_at = COALESCE(linkedin_connection_state.dm_sequence_started_at, EXCLUDED.dm_sequence_started_at),
  last_checked_at = EXCLUDED.last_checked_at,
  request_message = COALESCE(NULLIF(linkedin_connection_state.request_message, ''), NULLIF(EXCLUDED.request_message, '')),
  request_message_hash = COALESCE(NULLIF(linkedin_connection_state.request_message_hash, ''), NULLIF(EXCLUDED.request_message_hash, '')),
  sequence_step = GREATEST(linkedin_connection_state.sequence_step, EXCLUDED.sequence_step),
  payload_json = EXCLUDED.payload_json,
  metadata_json = EXCLUDED.metadata_json,
  updated_at = NOW()
RETURNING ghl_contact_id, connection_status, linkedin_provider_id, linkedin_public_identifier, request_sent_at, connected_at, sequence_step;`,
      options: {
        queryReplacement: expr('{{ [ $json.ghl_contact_id, $json.location_id, $json.unipile_account_id, $json.linkedin_profile_url, $json.linkedin_public_identifier, $json.linkedin_provider_id, $json.connection_request_tag, $json.connection_status, $json.request_sent_at || null, $json.connected_at || null, $json.dm_sequence_started_at || null, $json.last_checked_at || null, $json.request_message || null, $json.request_message_hash || null, Number($json.sequence_step || 0), JSON.stringify($json.payload_json || {}), JSON.stringify($json.metadata_json || {}) ] }}'),
        queryBatching: 'independently',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [760, 320],
  },
  output: [{ json: { ghl_contact_id: 'contact-123', connection_status: 'requested' } }],
});

const result = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - Upsert State',
    parameters: {
      respondWith: 'json',
      responseBody: '={{ { ok: true, contact_id: $json.ghl_contact_id, connection_status: $json.connection_status, provider_id: $json.linkedin_provider_id || null, identifier: $json.linkedin_public_identifier || null, sequence_step: $json.sequence_step || 0 } }}',
      options: {},
    },
    position: [1000, 320],
  },
});

export default workflow('lt-linkedin-connection-state-upsert', 'LT - LinkedIn Connection State Upsert')
  .add(webhook)
  .to(normalize)
  .to(upsert)
  .to(result);
