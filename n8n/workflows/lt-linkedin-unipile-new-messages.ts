import { workflow, node, trigger, newCredential } from '@n8n/workflow-sdk';

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook - Unipile New LinkedIn Messages',
    parameters: {
      httpMethod: 'POST',
      path: 'lt-unipile-linkedin-new-messages',
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
    name: 'Normalize Unipile Message Event',
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
  for (let i = 0; i < 3; i += 1) {
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
const accountInfo = body.account_info && typeof body.account_info === 'object' ? body.account_info : {};
const sender = body.sender && typeof body.sender === 'object' ? body.sender : {};
const attendees = Array.isArray(body.attendees) ? body.attendees : [];
const userId = first(accountInfo.user_id, accountInfo.userId);
const senderProviderId = first(sender.attendee_provider_id, sender.attendeeProviderId);
const senderName = first(sender.attendee_name, sender.attendeeName);
const senderProfileUrl = first(sender.attendee_profile_url, sender.attendeeProfileUrl);
const event = first(body.event, body.type, body.action, body.name);
const eventType = event || 'message_received';
const accountType = first(body.account_type, accountInfo.type).toUpperCase();
const messageId = first(body.message_id, body.messageId);
const chatId = first(body.chat_id, body.chatId);
const messageText = first(body.message, body.text);
const timestamp = parseDate(first(body.timestamp, body.created_at, body.createdAt, new Date().toISOString()));
const isInbound = eventType === 'message_received' && !!senderProviderId && !!userId && senderProviderId !== userId;

return [{
  json: {
    ok: true,
    account_id: first(body.account_id, body.accountId),
    account_type: accountType,
    account_user_id: userId,
    event_type: eventType,
    chat_id: chatId,
    message_id: messageId,
    message_text: messageText,
    sender_provider_id: senderProviderId,
    sender_name: senderName,
    sender_profile_url: senderProfileUrl,
    attendee_provider_ids: attendees.map((item) => first(item && item.attendee_provider_id, item && item.attendeeProviderId)).filter(Boolean),
    timestamp: timestamp,
    is_inbound: isInbound,
    raw_body: body,
  },
}];`,
    },
    position: [480, 320],
  },
  output: [{ json: { ok: true, is_inbound: false } }],
});

const lookup = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Find LinkedIn State Row By Provider',
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
WHERE linkedin_provider_id = $1
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
        queryReplacement: '={{ [ $("Normalize Unipile Message Event").item.json.sender_provider_id || "" ] }}',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    alwaysOutputData: true,
    position: [720, 320],
  },
  output: [{ json: { ghl_contact_id: '', payload_json: {} } }],
});

const processNode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Mark Conversation Active',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `function clean(v) {
  if (v === undefined || v === null) return '';
  return String(v).trim();
}

function describeError(err) {
  if (err instanceof Error) return err.stack || err.message || err.name || 'Unknown error';
  if (typeof err === 'string') return err;
  if (err && typeof err === 'object') {
    const parts = [];
    if ('message' in err && err.message) parts.push(String(err.message));
    if ('statusCode' in err) parts.push('statusCode=' + String(err.statusCode));
    const body = err?.response?.body ?? err?.body ?? err?.data;
    if (body !== undefined) {
      if (typeof body === 'string') parts.push('body=' + body);
      else {
        try { parts.push('body=' + JSON.stringify(body)); }
        catch (e) { parts.push('body=' + String(body)); }
      }
    }
    if (parts.length > 0) return parts.join(' | ');
    try { return JSON.stringify(err); } catch (e) { return String(err); }
  }
  return String(err);
}

const event = $node['Normalize Unipile Message Event'].json || {};
const row = $input.first()?.json || {};
const matched = !!clean(row.ghl_contact_id);
const inbound = !!event.is_inbound;
const accountType = clean(event.account_type).toUpperCase();

if (!inbound || accountType !== 'LINKEDIN' || !matched) {
  return [{
    json: {
      ok: true,
      skipped: true,
      reason: !inbound ? 'not_inbound' : accountType !== 'LINKEDIN' ? 'not_linkedin' : 'no_state_row',
      should_update: false,
      chat_id: event.chat_id || '',
      message_id: event.message_id || '',
      sender_provider_id: event.sender_provider_id || '',
      provider_id: clean(row.linkedin_provider_id || ''),
      payload_json: {},
      metadata_json: {},
    },
  }];
}

const now = new Date().toISOString();
const inboundPayload = {
  dm_conversation_status: 'active',
  dm_conversation_started_at: row.payload_json?.dm_conversation_started_at || now,
  dm_last_inbound_at: now,
  dm_last_inbound_message_id: event.message_id || '',
  dm_last_inbound_chat_id: event.chat_id || '',
  dm_last_inbound_message: event.message_text || '',
  dm_last_inbound_sender_provider_id: event.sender_provider_id || '',
  dm_last_inbound_sender_name: event.sender_name || '',
  dm_last_inbound_sender_profile_url: event.sender_profile_url || '',
};

return [{
  json: {
    ok: true,
    skipped: false,
    should_update: true,
    reason: '',
    contact_id: clean(row.ghl_contact_id || ''),
    provider_id: clean(row.linkedin_provider_id || event.sender_provider_id || ''),
    chat_id: event.chat_id || '',
    message_id: event.message_id || '',
    payload_json: {
      ...(row.payload_json && typeof row.payload_json === 'object' ? row.payload_json : {}),
      ...inboundPayload,
    },
    metadata_json: {
      source: 'unipile_new_messages_webhook',
      event_type: 'message_received',
      account_type: accountType,
      chat_id: event.chat_id || '',
      message_id: event.message_id || '',
    },
  },
}];`,
    },
    position: [960, 320],
  },
  output: [{ json: { ok: true, skipped: false } }],
});

const updateState = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Update LinkedIn Conversation State',
    parameters: {
      operation: 'executeQuery',
      query: `WITH updated AS (
UPDATE linkedin_connection_state
SET
  payload_json = COALESCE(linkedin_connection_state.payload_json, '{}'::jsonb) || $2::jsonb,
  metadata_json = COALESCE(linkedin_connection_state.metadata_json, '{}'::jsonb) || $3::jsonb,
  last_checked_at = NOW(),
  updated_at = NOW()
WHERE $1 <> '' AND $4::boolean = true AND ghl_contact_id = $1
RETURNING ghl_contact_id, linkedin_provider_id
)
SELECT
  COALESCE((SELECT ghl_contact_id FROM updated LIMIT 1), $1::text) AS ghl_contact_id,
  COALESCE((SELECT linkedin_provider_id FROM updated LIMIT 1), $5::text) AS linkedin_provider_id,
  $4::boolean AS should_update,
  CASE
    WHEN $4::boolean = true THEN false
    ELSE true
  END AS skipped,
  $6::text AS reason,
  $7::text AS chat_id,
  $8::text AS message_id;`,
      options: {
        queryReplacement: '={{ [ $json.contact_id || "", JSON.stringify($json.payload_json || {}), JSON.stringify($json.metadata_json || {}), !!$json.should_update, $json.provider_id || "", $json.reason || "", $json.chat_id || "", $json.message_id || "" ] }}',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [1200, 320],
  },
  output: [{ json: { ghl_contact_id: '', should_update: false } }],
});

const result = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - Mark Conversation Active',
    parameters: {
      respondWith: 'json',
      responseBody: '={{ { ok: true, skipped: $json.skipped || false, reason: $json.reason || null, contact_id: $json.ghl_contact_id || null, provider_id: $json.linkedin_provider_id || null, chat_id: $json.chat_id || null, message_id: $json.message_id || null, updated: $json.should_update || false } }}',
      options: {},
    },
    position: [1200, 320],
  },
});

export default workflow('lt-linkedin-unipile-new-messages', 'LT - LinkedIn Unipile New Messages')
  .add(webhook)
  .to(normalize)
  .to(lookup)
  .to(processNode)
  .to(updateState)
  .to(result);
