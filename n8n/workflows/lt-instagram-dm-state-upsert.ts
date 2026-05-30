import { workflow, node, trigger, newCredential, expr } from '@n8n/workflow-sdk';

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook - Instagram State Upsert',
    parameters: {
      httpMethod: 'POST',
      path: 'lt-instagram-dm-state-upsert',
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
    name: 'Normalize Instagram State Payload',
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
const payloadJson = body.payload_json && typeof body.payload_json === 'object' ? body.payload_json : body;
const metadataJson = body.metadata_json && typeof body.metadata_json === 'object' ? body.metadata_json : {};
const now = new Date().toISOString();

return [{
  json: {
    state_key: first(body.state_key, body.stateKey, body.identifier_key, body.identifierKey),
    unipile_account_id: first(body.unipile_account_id, body.unipileAccountId),
    platform: first(body.platform, 'instagram'),
    identifier: first(body.identifier, body.public_identifier, body.publicIdentifier),
    relation: first(body.relation, body.relationship_status, body.relationshipStatus),
    display_name: first(body.display_name, body.displayName, body.name),
    profile_url: first(body.profile_url, body.profileUrl, body.profile_url_last),
    attendee_id: first(body.attendee_id, body.attendeeId, body.provider_id),
    connection_status: first(body.connection_status, body.connectionStatus, body.status, parseDate(body.completed_at) ? 'completed' : 'requested') || 'requested',
    dm_sequence_started_at: parseDate(first(body.dm_sequence_started_at, body.dmSequenceStartedAt)),
    last_checked_at: parseDate(first(body.last_checked_at, body.lastCheckedAt, now)) || now,
    first_seen_at: parseDate(first(body.first_seen_at, body.firstSeenAt, now)) || now,
    last_sent_at: parseDate(first(body.last_sent_at, body.lastSentAt)),
    last_chat_id: first(body.last_chat_id, body.lastChatId),
    last_message: first(body.last_message, body.lastMessage),
    completed_at: parseDate(first(body.completed_at, body.completedAt)),
    sequence_step: Number.isFinite(Number(body.sequence_step ?? body.sequenceStep)) ? Number(body.sequence_step ?? body.sequenceStep) : 0,
    source_workflow_name: first(body.source_workflow_name, body.sourceWorkflowName),
    source_key: first(body.source_key, body.sourceKey),
    payload_json: payloadJson,
    metadata_json: metadataJson,
    raw_body: body,
  },
}];`,
    },
    position: [520, 320],
  },
  output: [{ json: { state_key: 'instagram:example', connection_status: 'requested' } }],
});

const ensureTable = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Ensure Table Exists',
    parameters: {
      operation: 'executeQuery',
      query: `CREATE TABLE IF NOT EXISTS instagram_dm_state (
  state_key              TEXT PRIMARY KEY,
  unipile_account_id     TEXT NOT NULL DEFAULT '',
  platform               TEXT NOT NULL DEFAULT 'instagram',
  identifier             TEXT NOT NULL DEFAULT '',
  relation               TEXT NOT NULL DEFAULT '',
  display_name           TEXT NOT NULL DEFAULT '',
  profile_url            TEXT NOT NULL DEFAULT '',
  attendee_id            TEXT NOT NULL DEFAULT '',
  connection_status      TEXT NOT NULL DEFAULT 'requested',
  dm_sequence_started_at TIMESTAMPTZ,
  last_checked_at        TIMESTAMPTZ,
  first_seen_at          TIMESTAMPTZ,
  last_sent_at           TIMESTAMPTZ,
  last_chat_id           TEXT NOT NULL DEFAULT '',
  last_message           TEXT,
  completed_at           TIMESTAMPTZ,
  sequence_step          INTEGER NOT NULL DEFAULT 0,
  source_workflow_name   TEXT NOT NULL DEFAULT '',
  source_key             TEXT NOT NULL DEFAULT '',
  payload_json           JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json          JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);`,
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [760, 320],
  },
  output: [{}],
});

const upsert = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert Instagram State',
    parameters: {
      operation: 'executeQuery',
      query: `INSERT INTO instagram_dm_state (
  state_key,
  unipile_account_id,
  platform,
  identifier,
  relation,
  display_name,
  profile_url,
  attendee_id,
  connection_status,
  dm_sequence_started_at,
  last_checked_at,
  first_seen_at,
  last_sent_at,
  last_chat_id,
  last_message,
  completed_at,
  sequence_step,
  source_workflow_name,
  source_key,
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
  $9,
  $10::timestamptz,
  $11::timestamptz,
  $12::timestamptz,
  $13::timestamptz,
  $14,
  $15,
  $16::timestamptz,
  $17,
  $18,
  $19,
  $20::jsonb,
  $21::jsonb,
  NOW(),
  NOW()
)
ON CONFLICT (state_key) DO UPDATE SET
  unipile_account_id = COALESCE(NULLIF(EXCLUDED.unipile_account_id, ''), instagram_dm_state.unipile_account_id),
  platform = COALESCE(NULLIF(EXCLUDED.platform, ''), instagram_dm_state.platform),
  identifier = COALESCE(NULLIF(EXCLUDED.identifier, ''), instagram_dm_state.identifier),
  relation = COALESCE(NULLIF(EXCLUDED.relation, ''), instagram_dm_state.relation),
  display_name = COALESCE(NULLIF(EXCLUDED.display_name, ''), instagram_dm_state.display_name),
  profile_url = COALESCE(NULLIF(EXCLUDED.profile_url, ''), instagram_dm_state.profile_url),
  attendee_id = COALESCE(NULLIF(EXCLUDED.attendee_id, ''), instagram_dm_state.attendee_id),
  connection_status = CASE
    WHEN instagram_dm_state.connection_status = 'completed' AND EXCLUDED.connection_status <> 'completed'
      THEN instagram_dm_state.connection_status
    ELSE EXCLUDED.connection_status
  END,
  dm_sequence_started_at = COALESCE(instagram_dm_state.dm_sequence_started_at, EXCLUDED.dm_sequence_started_at),
  last_checked_at = EXCLUDED.last_checked_at,
  first_seen_at = COALESCE(instagram_dm_state.first_seen_at, EXCLUDED.first_seen_at),
  last_sent_at = COALESCE(EXCLUDED.last_sent_at, instagram_dm_state.last_sent_at),
  last_chat_id = COALESCE(NULLIF(EXCLUDED.last_chat_id, ''), instagram_dm_state.last_chat_id),
  last_message = COALESCE(NULLIF(EXCLUDED.last_message, ''), instagram_dm_state.last_message),
  completed_at = COALESCE(instagram_dm_state.completed_at, EXCLUDED.completed_at),
  sequence_step = GREATEST(instagram_dm_state.sequence_step, EXCLUDED.sequence_step),
  source_workflow_name = COALESCE(NULLIF(EXCLUDED.source_workflow_name, ''), instagram_dm_state.source_workflow_name),
  source_key = COALESCE(NULLIF(EXCLUDED.source_key, ''), instagram_dm_state.source_key),
  payload_json = EXCLUDED.payload_json,
  metadata_json = EXCLUDED.metadata_json,
  updated_at = NOW()
RETURNING state_key, connection_status, sequence_step, last_sent_at, completed_at;`,
      options: {
        queryReplacement: expr('{{ [ $("Normalize Instagram State Payload").item.json.state_key, $("Normalize Instagram State Payload").item.json.unipile_account_id, $("Normalize Instagram State Payload").item.json.platform, $("Normalize Instagram State Payload").item.json.identifier, $("Normalize Instagram State Payload").item.json.relation, $("Normalize Instagram State Payload").item.json.display_name, $("Normalize Instagram State Payload").item.json.profile_url, $("Normalize Instagram State Payload").item.json.attendee_id, $("Normalize Instagram State Payload").item.json.connection_status, $("Normalize Instagram State Payload").item.json.dm_sequence_started_at || null, $("Normalize Instagram State Payload").item.json.last_checked_at || null, $("Normalize Instagram State Payload").item.json.first_seen_at || null, $("Normalize Instagram State Payload").item.json.last_sent_at || null, $("Normalize Instagram State Payload").item.json.last_chat_id || null, $("Normalize Instagram State Payload").item.json.last_message || null, $("Normalize Instagram State Payload").item.json.completed_at || null, Number($("Normalize Instagram State Payload").item.json.sequence_step || 0), $("Normalize Instagram State Payload").item.json.source_workflow_name || null, $("Normalize Instagram State Payload").item.json.source_key || null, JSON.stringify($("Normalize Instagram State Payload").item.json.payload_json || {}), JSON.stringify($("Normalize Instagram State Payload").item.json.metadata_json || {}) ] }}'),
        queryBatching: 'independently',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [760, 520],
  },
  output: [{ json: { state_key: 'instagram:example', connection_status: 'requested' } }],
});

const result = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - Upsert State',
    parameters: {
      respondWith: 'json',
      responseBody: '={{ { ok: true, state_key: $json.state_key, connection_status: $json.connection_status, sequence_step: $json.sequence_step || 0 } }}',
      options: {},
    },
    position: [1000, 420],
  },
});

export default workflow('lt-instagram-dm-state-upsert', 'LT - Instagram DM State Upsert')
  .add(webhook)
  .to(normalize)
  .to(ensureTable)
  .to(upsert)
  .to(result);
