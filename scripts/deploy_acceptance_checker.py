import json, urllib.request, uuid

# Read API key
key0 = open(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\.env').read()
env = {}
for line in key0.splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        name, value = line.split('=', 1)
        env[name.strip()] = value.strip().strip('"')
token = env['N8N_API_KEY_LT']
ghl_pit = env['GHL_PIT']

def make_id():
    return str(uuid.uuid4())

normalize_code = r"""function clean(v) {
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
    if (current.body && typeof current.body === 'object') { current = current.body; continue; }
    if (current.data && typeof current.data === 'object') { current = current.data; continue; }
    break;
  }
  if (current && typeof current === 'object') {
    const keys = Object.keys(current);
    if (keys.length === 1 && keys[0].trim().startsWith('{')) {
      try { return JSON.parse(keys[0]); } catch (e) {
        try { return JSON.parse(decodeURIComponent(keys[0])); } catch (ignored) {}
      }
    }
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
const attendees = Array.isArray(body.attendees) ? body.attendees : [];
const attendee = attendees.find((value) => value && value.attendee_specifics?.network_distance !== 'SELF') || attendees[0] || {};
const event = first(body.event, body.type, body.action, body.name) || 'new_relation';
const now = new Date().toISOString();
return [{
  json: {
    event_type: event,
    unipile_account_id: first(body.account_id, body.accountId, body.user_account_id, user.account_id, user.accountId),
    linkedin_provider_id: first(attendee.attendee_provider_id, attendee.provider_id, attendee.attendee_id, body.user_provider_id, body.provider_id, user.provider_id, user.id),
    linkedin_public_identifier: first(attendee.attendee_public_identifier, body.user_public_identifier, body.public_identifier, body.publicIdentifier, user.public_identifier),
    linkedin_profile_url: first(attendee.attendee_profile_url, body.user_profile_url, body.profile_url, body.profileUrl, user.profile_url, user.profileUrl),
    accepted_at: parseDate(first(body.accepted_at, body.acceptedAt, body.created_at, body.createdAt, body.timestamp, now)) || now,
    raw_body: body,
  },
}];"""

build_payload_code = r"""function clean(v) {
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
const row = $input.first()?.json || {};
const now = new Date().toISOString();
const matched = !!clean(row.ghl_contact_id);

if (!matched) {
  return [{ json: { matched: false, accepted_at: event.accepted_at || now, event_type: event.event_type || 'new_relation' } }];
}

const payload = {
  ghl_contact_id: row.ghl_contact_id,
  location_id: row.location_id || config.GHL_LOCATION_ID || '',
  unipile_account_id: row.unipile_account_id || event.unipile_account_id || config.UNIPILE_ACCOUNT_ID || '',
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
  payload_json: { matched: true, event: event.raw_body || {}, state_row: row },
  metadata_json: { source: 'acceptance_checker', event_type: event.event_type || 'new_relation' },
};

// Call the state upsert webhook
const upsertResp = await this.helpers.httpRequest({
  method: 'POST',
  url: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert',
  headers: { 'Content-Type': 'application/json' },
  body: payload,
  json: true,
});

// Apply linkedin_connected tag to GHL contact
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
    body: { tags: ['linkedin_connected'] },
    json: true,
  });
  tag_ok = true;
} catch (e) {
  tag_error = e?.message || String(e);
}

return [{
  json: {
    matched: true,
    accepted_at: payload.connected_at,
    ghl_contact_id: row.ghl_contact_id,
    connection_status: 'connected',
    provider_id: row.linkedin_provider_id || event.linkedin_provider_id || '',
    identifier: row.linkedin_public_identifier || event.linkedin_public_identifier || '',
    upsert_ok: !!upsertResp,
    tag_ok,
    tag_error,
  },
}];"""

postgres_query = r"""WITH match AS (
SELECT ghl_contact_id, location_id, unipile_account_id, linkedin_profile_url, linkedin_public_identifier, linkedin_provider_id, connection_request_tag, connection_status, request_sent_at, connected_at, dm_sequence_started_at, last_checked_at, request_message, request_message_hash, sequence_step, payload_json, metadata_json
FROM linkedin_connection_state
WHERE (($1 <> '' AND unipile_account_id = $1 AND linkedin_provider_id = $2 AND $2 <> '') OR ($1 <> '' AND unipile_account_id = $1 AND linkedin_public_identifier = $3 AND $3 <> '') OR (linkedin_profile_url = $4 AND $4 <> ''))
LIMIT 1
)
SELECT * FROM match
UNION ALL
SELECT NULL::text AS ghl_contact_id, NULL::text AS location_id, NULL::text AS unipile_account_id, NULL::text AS linkedin_profile_url, NULL::text AS linkedin_public_identifier, NULL::text AS linkedin_provider_id, NULL::text AS connection_request_tag, NULL::text AS connection_status, NULL::timestamptz AS request_sent_at, NULL::timestamptz AS connected_at, NULL::timestamptz AS dm_sequence_started_at, NULL::timestamptz AS last_checked_at, NULL::text AS request_message, NULL::text AS request_message_hash, 0::integer AS sequence_step, '{}'::jsonb AS payload_json, '{}'::jsonb AS metadata_json
WHERE NOT EXISTS (SELECT 1 FROM match);"""

nodes = [
    {
        'id': make_id(),
        'name': 'Webhook - LinkedIn Acceptance',
        'type': 'n8n-nodes-base.webhook',
        'typeVersion': 2.1,
        'position': [240, 320],
        'parameters': {
            'httpMethod': 'POST',
            'path': 'lt-linkedin-connection-accepted',
            'responseMode': 'responseNode',
            'options': {},
        },
        'webhookId': str(uuid.uuid4()),
    },
    {
        'id': make_id(),
        'name': 'Config',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [360, 120],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'language': 'javaScript',
            'jsCode': f"const input = $input.first()?.json || {{}};\nreturn [{{ json: {{\n  ...input,\n  UNIPILE_ACCOUNT_ID: 'V9eiHiDpRmCtan0YNdzsQw',\n  GHL_API_KEY: {json.dumps(ghl_pit)},\n  GHL_LOCATION_ID: 'Zwz4relUXVPxx8uohnjV',\n  GHL_API_BASE_URL: 'https://services.leadconnectorhq.com'\n}} }}];",
        },
    },
    {
        'id': make_id(),
        'name': 'Normalize LinkedIn Acceptance Event',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [480, 320],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'language': 'javaScript',
            'jsCode': normalize_code,
        },
    },
    {
        'id': make_id(),
        'name': 'Find LinkedIn State Row',
        'type': 'n8n-nodes-base.postgres',
        'typeVersion': 2.6,
        'position': [720, 320],
        'parameters': {
            'operation': 'executeQuery',
            'query': postgres_query,
            'options': {
                'queryReplacement': '={{ [ $json.unipile_account_id || $("Config").item.json.UNIPILE_ACCOUNT_ID || "", $json.linkedin_provider_id || "", $json.linkedin_public_identifier || "", $json.linkedin_profile_url || "" ] }}',
                'queryBatching': 'independently',
            },
        },
        'credentials': {
            'postgres': {
                'id': 'pgAzUqpwOiGkGXzO',
                'name': 'Postgres account',
            },
        },
    },
    {
        'id': make_id(),
        'name': 'Build Acceptance Upsert Payload',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [960, 320],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'language': 'javaScript',
            'jsCode': build_payload_code,
        },
    },
    {
        'id': make_id(),
        'name': 'Respond - Acceptance',
        'type': 'n8n-nodes-base.respondToWebhook',
        'typeVersion': 1.3,
        'position': [1200, 320],
        'parameters': {
            'respondWith': 'json',
            'responseBody': '={{ { ok: true, matched: $("Build Acceptance Upsert Payload").item.json.matched || false, contact_id: $("Build Acceptance Upsert Payload").item.json.ghl_contact_id || null, connection_status: $("Build Acceptance Upsert Payload").item.json.connection_status || "unmatched", accepted_at: $("Build Acceptance Upsert Payload").item.json.accepted_at || null } }}',
            'options': {},
        },
    },
]

connections = {
    'Webhook - LinkedIn Acceptance': {
        'main': [[{'node': 'Config', 'type': 'main', 'index': 0}]],
    },
    'Config': {
        'main': [[{'node': 'Normalize LinkedIn Acceptance Event', 'type': 'main', 'index': 0}]],
    },
    'Normalize LinkedIn Acceptance Event': {
        'main': [[{'node': 'Find LinkedIn State Row', 'type': 'main', 'index': 0}]],
    },
    'Find LinkedIn State Row': {
        'main': [[{'node': 'Build Acceptance Upsert Payload', 'type': 'main', 'index': 0}]],
    },
    'Build Acceptance Upsert Payload': {
        'main': [[{'node': 'Respond - Acceptance', 'type': 'main', 'index': 0}]],
    },
}

workflow = {
    'name': 'LT - LinkedIn Connection Acceptance Checker (Unipile)',
    'nodes': nodes,
    'connections': connections,
    'settings': {},
}

# POST to n8n API
body = json.dumps(workflow).encode()
req = urllib.request.Request('https://automations.livetransparent.com/api/v1/workflows', data=body)
req.add_header('X-N8N-API-KEY', token)
req.add_header('Content-Type', 'application/json')

try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode())
    print('Created workflow:', result.get('id'), result.get('name'))
    print('Node count:', len(result.get('nodes', [])))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    print(e.read().decode()[:2000])
