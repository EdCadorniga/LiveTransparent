"""Replace the old five-chat LinkedIn backfill with the worklist-driven batch path."""
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_ID = "JUvrA7qMa24SwAZG"
BASE = "https://automations.livetransparent.com/api/v1"


def env_values():
    values = {}
    with open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = env_values()
api_key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_KEY")
if not api_key:
    raise SystemExit("N8N_API_KEY_LT is required")
unipile_key = env.get("UNIPILE_TOKEN")
if not unipile_key:
    raise SystemExit("UNIPILE_TOKEN is required")


def request(method, url, body=None):
    headers = {"X-N8N-API-KEY": api_key, "Accept": "application/json"}
    payload = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(body).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode())


workflow = request("GET", f"{BASE}/workflows/{WORKFLOW_ID}")
nodes = workflow["nodes"]
by_name = {node["name"]: node for node in nodes}

config = by_name["Config"]
assignments = config["parameters"]["assignments"]["assignments"]
assignments = [item for item in assignments if item["name"] != "only_chat_id"]
assignments.extend([
    {"id": "batch", "name": "batch_size", "value": 30, "type": "number"},
    {"id": "since", "name": "since", "value": "2026-07-12T00:00:00Z", "type": "string"},
])
config["parameters"]["assignments"]["assignments"] = assignments

fetch = by_name["Fetch Latest GHL OAuth Token"]
fetch["parameters"]["query"] = """
WITH claimed AS (
  UPDATE linkedin_backfill_worklist
  SET status = 'processing', claimed_at = NOW(), updated_at = NOW()
  WHERE chat_id IN (
    SELECT chat_id
    FROM linkedin_backfill_worklist
    WHERE status = 'pending'
    ORDER BY last_ts ASC
    LIMIT 30
    FOR UPDATE SKIP LOCKED
  )
  RETURNING chat_id, attendee_provider_id, profile_full_name, profile_public_identifier,
            profile_url, last_ts, total_messages, inbound_messages, outbound_messages
), token AS (
  SELECT access_token
  FROM ghl_oauth_tokens
  WHERE active IS TRUE AND access_token <> ''
  ORDER BY received_at DESC NULLS LAST
  LIMIT 1
)
SELECT token.access_token,
       COALESCE((SELECT json_agg(claimed ORDER BY claimed.last_ts) FROM claimed), '[]'::json) AS worklist
FROM token;
""".strip()

code = r'''const cfg = $('Config').item.json || {};
const token = String($json.access_token || '').trim();
const worklist = Array.isArray($json.worklist) ? $json.worklist : [];
const LOCATION_ID = cfg.location_id || 'Zwz4relUXVPxx8uohnjV';
const LINKEDIN_PROVIDER_ID = cfg.linkedin_provider_id || '6a58a14ff3023bea3783c152';
const GHL_BASE = 'https://services.leadconnectorhq.com';
const UNIPILE_BASE = 'https://api42.unipile.com:17256/api/v1';
const UNIPILE_KEY = '__UNIPILE_KEY__';
const UNIPILE_ACCOUNT = 'V9eiHiDpRmCtan0YNdzsQw';

const results = [];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const ghlHeaders = { Authorization: 'Bearer ' + token, Version: '2021-07-28', Accept: 'application/json' };
const ghlJsonHeaders = { ...ghlHeaders, 'Content-Type': 'application/json' };

async function http(method, url, headers, body) {
  const options = { method, url, headers, json: true, timeout: 20000 };
  if (body !== undefined) options.body = body;
  return await this.helpers.httpRequest(options);
}

function contactName(contact) {
  return String(contact.contactName || contact.name || [contact.firstName, contact.lastName].filter(Boolean).join(' ') || '').trim().toLowerCase();
}

function contactScore(contact, row) {
  const identifier = String(row.profile_public_identifier || '').toLowerCase();
  const profileUrl = String(row.profile_url || '').toLowerCase();
  const name = String(row.profile_full_name || '').trim().toLowerCase();
  const custom = JSON.stringify(contact.customFields || []).toLowerCase();
  const website = String(contact.website || '').toLowerCase();
  let score = 0;
  if (identifier && (custom.includes(identifier) || website.includes(identifier))) score += 100;
  if (profileUrl && (custom.includes(profileUrl) || website.includes(profileUrl))) score += 90;
  if (name && contactName(contact) === name) score += 30;
  return score;
}

async function resolveContact(row) {
  const queries = [row.profile_public_identifier, row.profile_full_name].filter(Boolean);
  const candidates = [];
  for (const query of queries) {
    const data = await http.call(this, 'GET', GHL_BASE + '/contacts/?query=' + encodeURIComponent(query) + '&locationId=' + LOCATION_ID + '&limit=20', ghlHeaders);
    for (const contact of (Array.isArray(data?.contacts) ? data.contacts : [])) {
      if (!candidates.some(existing => existing.id === contact.id)) candidates.push(contact);
    }
    if (candidates.length) break;
  }
  const scored = candidates.map(contact => ({ contact, score: contactScore(contact, row) })).sort((a, b) => b.score - a.score);
  if (!scored.length) {
    const fullName = String(row.profile_full_name || '').trim();
    if (!fullName) return '';
    const parts = fullName.split(/\s+/);
    const created = await http.call(this, 'POST', GHL_BASE + '/contacts/', ghlJsonHeaders, {
      firstName: parts[0], lastName: parts.slice(1).join(' ') || 'LinkedIn',
      source: 'LinkedIn via Unipile historical backfill',
      website: row.profile_url || ('https://www.linkedin.com/in/' + row.profile_public_identifier),
      locationId: LOCATION_ID
    });
    return created?.contact?.id || created?.id || '';
  }
  if (scored[0].score < 30) return '';
  if (scored.length > 1 && scored[0].score === scored[1].score) return '';
  return scored[0].contact.id || '';
}

async function existingBodies(contactId) {
  const data = await http.call(this, 'GET', GHL_BASE + '/conversations/search?contactId=' + encodeURIComponent(contactId) + '&limit=20', ghlHeaders);
  const conversations = Array.isArray(data?.conversations) ? data.conversations : [];
  const linkedIn = conversations.filter(conversation =>
    conversation.lastMessageConversationProviderId === LINKEDIN_PROVIDER_ID ||
    conversation.conversationProviderId === LINKEDIN_PROVIDER_ID
  );
  const bodies = new Set();
  for (const conversation of linkedIn) {
    const messages = await http.call(this, 'GET', GHL_BASE + '/conversations/' + conversation.id + '/messages?limit=100', ghlHeaders);
    const list = messages?.messages?.messages || messages?.messages || [];
    for (const message of (Array.isArray(list) ? list : [])) bodies.add(String(message.body || message.message || '').trim());
  }
  return bodies;
}

if (!token) return [{ json: { total_chats: 0, total_messages_backfilled: 0, progress: [], errors: ['missing OAuth token'] } }];
for (const row of worklist) {
  const result = { chat_id: row.chat_id, posted_count: 0, skipped_count: 0, error_count: 0, last_error: '', status: 'done' };
  try {
    const contactId = await resolveContact.call(this, row);
    if (!contactId) throw new Error('no unambiguous GHL contact match');
    const data = await http.call(this, 'GET', UNIPILE_BASE + '/chats/' + encodeURIComponent(row.chat_id) + '/messages?account_id=' + UNIPILE_ACCOUNT + '&limit=100', { 'X-API-KEY': UNIPILE_KEY, Accept: 'application/json' });
    const messages = (Array.isArray(data?.items) ? data.items : []).filter(message => new Date(message.timestamp) >= new Date(cfg.since || '2026-07-12T00:00:00Z'));
    const bodies = await existingBodies.call(this, contactId);
    for (const message of messages) {
      const body = String(message.text || '').trim();
      if (!body || bodies.has(body)) { result.skipped_count++; continue; }
      const inbound = message.is_sender !== 1;
      const endpoint = GHL_BASE + '/conversations/messages' + (inbound ? '/inbound' : '');
      await http.call(this, 'POST', endpoint, ghlJsonHeaders, {
        type: 'Custom', contactId, message: message.text, conversationProviderId: LINKEDIN_PROVIDER_ID,
        altId: row.chat_id, date: message.timestamp
      });
      result.posted_count++;
      bodies.add(body);
      await sleep(250);
    }
  } catch (error) {
    result.status = 'error';
    result.error_count = 1;
    result.last_error = String(error?.message || error).slice(0, 300);
  }
  if (result.status === 'error') results.push(result);
  else results.push(result);
}

return [{ json: {
  total_chats: results.length,
  total_messages_backfilled: results.reduce((sum, row) => sum + row.posted_count, 0),
  total_skipped_existing: results.reduce((sum, row) => sum + row.skipped_count, 0),
  errors: results.filter(row => row.status === 'error'),
  progress: results
} }];'''

code_node = by_name["Backfill Conversations"]
code_node["parameters"]["jsCode"] = code.replace("'__UNIPILE_KEY__'", json.dumps(unipile_key))

persist_name = "Persist Worklist Progress"
nodes = [node for node in nodes if node["name"] != persist_name]
persist = {
    "parameters": {
        "operation": "executeQuery",
        "query": """
UPDATE linkedin_backfill_worklist AS w
SET status = p.status,
    posted_count = p.posted_count,
    skipped_count = p.skipped_count,
    error_count = p.error_count,
    last_error = NULLIF(p.last_error, ''),
    completed_at = CASE WHEN p.status = 'done' THEN NOW() ELSE NULL END,
    updated_at = NOW()
FROM jsonb_to_recordset($1::jsonb) AS p(chat_id text, status text, posted_count integer, skipped_count integer, error_count integer, last_error text)
WHERE w.chat_id = p.chat_id;
""".strip(),
        "options": {"queryReplacement": "={{ [ JSON.stringify($json.progress || []) ] }}", "queryBatching": "independently"},
    },
    "id": "linkedin-backfill-persist",
    "name": persist_name,
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 2.6,
    "position": [560, 220],
    "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
}
nodes.append(persist)

summarize = by_name["Summarize"]
connections = workflow["connections"]
connections["Backfill Conversations"]["main"][0] = [{"node": persist_name, "type": "main", "index": 0}]
connections[persist_name] = {"main": [[{"node": "Summarize", "type": "main", "index": 0}]]}

settings = workflow.get("settings") or {}
settings.pop("availableInMCP", None)
payload = {"name": workflow["name"], "nodes": nodes, "connections": connections, "settings": settings}
request("PUT", f"{BASE}/workflows/{WORKFLOW_ID}", payload)
print("patched")
