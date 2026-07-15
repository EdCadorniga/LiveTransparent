import { workflow, node, trigger, newCredential } from '@n8n/workflow-sdk';
import { SOCIAL_OUTREACH_TEMPLATES } from './social_outreach_templates';

const schedule = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '0 12-22 * * 1-5' }] } },
    position: [240, 300],
  },
  output: [{}],
});

const manual = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [240, 480] },
  output: [{}],
});

const config = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: '1', name: 'workflowName', type: 'string', value: 'LT - Instagram DM Sequence (Unipile)' },
          { id: '2', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: '3', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: '4', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: '5', name: 'pageSize', type: 'number', value: 200 },
          { id: '6', name: 'maxPages', type: 'number', value: 5 },
          { id: '7', name: 'maxCandidates', type: 'number', value: 500 },
          { id: '8', name: 'maxSendsPerRun', type: 'number', value: 10 },
          { id: '9', name: 'templateVariant', type: 'string', value: 'v1' },
          { id: '10', name: 'stateUpsertUrl', type: 'string', value: 'https://automations.livetransparent.com/webhook/lt-instagram-dm-state-upsert' },
        ],
      },
    },
    position: [500, 380],
  },
  output: [{ json: {} }],
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
    position: [740, 380],
  },
  output: [{}],
});

const loadState = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Load Instagram State',
    parameters: {
      operation: 'executeQuery',
      query: `SELECT
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
  metadata_json
FROM instagram_dm_state
WHERE unipile_account_id = $1
ORDER BY updated_at DESC
LIMIT 5000;`,
      options: {
        queryReplacement: '={{ [ $node[\"Config\"].json.unipileAccountId ] }}',
      },
    },
    credentials: { postgres: newCredential('Postgres account') },
    alwaysOutputData: true,
    position: [980, 380],
  },
  output: [{ json: { state_key: '' } }],
});

const processNode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Process Instagram Outreach',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const TEMPLATE_REGISTRY = ${JSON.stringify(SOCIAL_OUTREACH_TEMPLATES)};
const cfg = $node['Config'].json || {};
const CFG = {
  workflowName: String(cfg.workflowName || 'LT - Instagram DM Sequence (Unipile)').trim(),
  unipileApiBaseUrl: String(cfg.unipileApiBaseUrl || 'https://api42.unipile.com:17256/api/v1').replace(/\\/+$/, ''),
  unipileApiKey: String(cfg.unipileApiKey || '').trim(),
  unipileAccountId: String(cfg.unipileAccountId || '').trim(),
  pageSize: Math.max(1, Math.min(200, Number(cfg.pageSize || 200))),
  maxPages: Math.max(1, Math.min(20, Number(cfg.maxPages || 5))),
  maxCandidates: Math.max(1, Math.min(5000, Number(cfg.maxCandidates || 500))),
  maxSendsPerRun: Math.max(1, Math.min(50, Number(cfg.maxSendsPerRun || 10))),
  templateVariant: String(cfg.templateVariant || 'v1').trim().toLowerCase(),
  stateUpsertUrl: String(cfg.stateUpsertUrl || 'https://automations.livetransparent.com/webhook/lt-instagram-dm-state-upsert').trim(),
};

function sanitizeMessage(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/\u00A0/g, ' ')
    .replace(/\u0393\u00C7[\u00D6\u00FF]/g, "'")
    .replace(/\u0393\u00C7[\u00A3\u00A5]/g, '"')
    .replace(/\u0393\u00C7[\u00F4\u00F6]/g, '-')
    .replace(/\u0393\u00C7\u00AA/g, '...')
    .replace(/\u00E2\u20AC[\u02DC\u2122]/g, "'")
    .replace(/\u00E2\u20AC[\u0153\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u0094]/g, '-')
    .replace(/\u00E2\u20AC\u00A6/g, '...');
}

function sanitizeTemplateRegistry(value) {
  if (typeof value === 'string') return sanitizeMessage(value);
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i += 1) value[i] = sanitizeTemplateRegistry(value[i]);
    return value;
  }
  if (value && typeof value === 'object') {
    Object.keys(value).forEach((key) => { value[key] = sanitizeTemplateRegistry(value[key]); });
  }
  return value;
}

const DAY = 24 * 60 * 60 * 1000;
const STEP_WINDOWS = [0, 3 * DAY, 6 * DAY, 11 * DAY];
sanitizeTemplateRegistry(TEMPLATE_REGISTRY);
const MESSAGE_TEMPLATES = (TEMPLATE_REGISTRY.instagram[CFG.templateVariant] || TEMPLATE_REGISTRY.instagram.v1);

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

function describeError(err) {
  if (err instanceof Error) return err.stack || err.message || err.name || 'Unknown error';
  if (typeof err === 'string') return err;
  if (err && typeof err === 'object') {
    const parts = [];
    if ('message' in err && err.message) parts.push(String(err.message));
    if ('statusCode' in err && err.statusCode !== undefined) parts.push('statusCode=' + String(err.statusCode));
    const body = err?.response?.body ?? err?.body ?? err?.data;
    if (body !== undefined) {
      if (typeof body === 'string') parts.push('body=' + body);
      else {
        try { parts.push('body=' + JSON.stringify(body)); } catch (e) { parts.push('body=' + String(body)); }
      }
    }
    if (parts.length > 0) return parts.join(' | ');
    try { return JSON.stringify(err); } catch (e) { return String(err); }
  }
  return String(err);
}

function buildUrl(path, params = {}) {
  const query = [];
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    query.push(encodeURIComponent(key) + '=' + encodeURIComponent(String(value)));
  }
  return CFG.unipileApiBaseUrl + path + (query.length ? '?' + query.join('&') : '');
}

async function apiRequest(method, path, body, params = {}) {
  const options = {
    method,
    url: buildUrl(path, params),
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-API-KEY': CFG.unipileApiKey,
    },
    json: true,
  };
  if (body !== undefined) options.body = body;
  return await this.helpers.httpRequest(options);
}

function extractItems(resp) {
  if (Array.isArray(resp?.items)) return resp.items;
  if (Array.isArray(resp?.data?.items)) return resp.data.items;
  if (Array.isArray(resp?.data)) return resp.data;
  if (Array.isArray(resp)) return resp;
  return [];
}

function extractCursor(resp) {
  const cursor = resp?.cursor ?? resp?.data?.cursor ?? resp?.next_cursor ?? resp?.data?.next_cursor ?? '';
  if (!cursor) return '';
  if (typeof cursor === 'string') return cursor;
  if (typeof cursor === 'object') return first(cursor.next, cursor.cursor, cursor.value, cursor.token, cursor.id);
  return '';
}

function normalizeIdentifier(item) {
  return first(item?.public_identifier, item?.username, item?.identifier, item?.publicIdentifier, item?.messaging_id, item?.member_id, item?.id);
}

function normalizeAttendeeId(item, profile) {
  return first(
    item?.messaging_id,
    item?.provider_messaging_id,
    item?.member_id,
    item?.id,
    profile?.messaging_id,
    profile?.provider_messaging_id,
    profile?.member_id,
    profile?.id
  );
}

function normalizeName(item, profile) {
  return first(
    item?.name,
    item?.first_name && item?.last_name ? String(item.first_name) + ' ' + String(item.last_name) : '',
    item?.first_name,
    profile?.name,
    profile?.first_name && profile?.last_name ? String(profile.first_name) + ' ' + String(profile.last_name) : '',
    profile?.first_name,
    normalizeIdentifier(item)
  );
}

function normalizeProfileUrl(item, identifier) {
  return first(item?.profile_url, item?.public_profile_url, item?.profileUrl, ('https://instagram.com/' + identifier).replace(/\/+$/, ''));
}

function firstNameFromDisplay(displayName, identifier) {
  const base = clean(displayName || identifier || 'there').replace(/[._]+/g, ' ');
  const token = first(base.split(/\s+/)[0], 'there');
  if (!token) return 'there';
  return token.charAt(0).toUpperCase() + token.slice(1);
}

async function fetchPaged(path, userId) {
  const items = [];
  let cursor = '';
  for (let page = 0; page < CFG.maxPages; page += 1) {
    const resp = await apiRequest.call(this, 'GET', path, undefined, {
      account_id: CFG.unipileAccountId,
      user_id: userId || undefined,
      cursor: cursor || undefined,
      limit: CFG.pageSize,
    });
    const pageItems = extractItems(resp);
    items.push(...pageItems);
    cursor = extractCursor(resp);
    if (!cursor || pageItems.length === 0 || items.length >= CFG.maxCandidates) break;
  }
  return items.slice(0, CFG.maxCandidates);
}

async function resolveProfile(identifier) {
  try {
    return await apiRequest.call(this, 'GET', '/users/' + encodeURIComponent(identifier), undefined, {
      account_id: CFG.unipileAccountId,
    });
  } catch (err) {
    return { __error: describeError(err) };
  }
}

async function sendDirectMessage(attendeeId, text) {
  return await apiRequest.call(this, 'POST', '/chats', {
    account_id: CFG.unipileAccountId,
    attendees_ids: [attendeeId],
    text,
  });
}

async function persistState(state, candidate, action, extra = {}) {
  const payload = {
    state_key: state.stateKey,
    unipile_account_id: CFG.unipileAccountId,
    platform: 'instagram',
    identifier: state.identifier,
    relation: state.relation,
    display_name: state.displayName,
    profile_url: state.profileUrl,
    attendee_id: state.attendeeId,
    connection_status: state.connectionStatus,
    dm_sequence_started_at: state.dmSequenceStartedAt || null,
    last_checked_at: state.lastCheckedAt || null,
    first_seen_at: state.firstSeenAt || null,
    last_sent_at: state.lastSentAt || null,
    last_chat_id: state.lastChatId || '',
    last_message: state.lastMessage || '',
    completed_at: state.completedAt || null,
    sequence_step: Number(state.sequenceStep || 0),
    source_workflow_name: CFG.workflowName,
    source_key: state.sourceKey || '',
    payload_json: {
      action,
      candidate,
      ...extra.payload_json,
    },
    metadata_json: {
      source: 'instagram_dm_sequence',
      template_variant: CFG.templateVariant,
      action,
      relation: state.relation,
      step: Number(state.sequenceStep || 0),
      ...extra.metadata_json,
    },
  };
  try {
    await this.helpers.httpRequest({
      method: 'POST',
      url: CFG.stateUpsertUrl,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: payload,
      json: true,
    });
    return true;
  } catch (err) {
    return false;
  }
}

const followers = await fetchPaged.call(this, '/users/followers');
const following = await fetchPaged.call(this, '/users/following');
const existingRows = typeof $input?.all === 'function' ? $input.all() : [];

const followerMap = new Map();
const followingMap = new Map();
const stateMap = new Map();

for (const row of existingRows) {
  const json = row?.json || {};
  const key = clean(json.state_key || '');
  if (key) stateMap.set(key, json);
}

for (const item of followers) {
  const identifier = normalizeIdentifier(item);
  if (!identifier) continue;
  followerMap.set(identifier.toLowerCase(), item);
}

for (const item of following) {
  const identifier = normalizeIdentifier(item);
  if (!identifier) continue;
  followingMap.set(identifier.toLowerCase(), item);
}

const merged = [];
const allIdentifiers = new Set([...followerMap.keys(), ...followingMap.keys()]);
for (const key of allIdentifiers) {
  const follower = followerMap.get(key) || {};
  const followee = followingMap.get(key) || {};
  const identifier = normalizeIdentifier(follower) || normalizeIdentifier(followee);
  if (!identifier) continue;

  const relation =
    followerMap.has(key) && followingMap.has(key)
      ? 'mutual'
      : followerMap.has(key)
        ? 'followers_only'
        : 'following_only';

  const baseItem = relation === 'following_only' ? followee : follower;
  const displayName = normalizeName(baseItem, {});
  const profileUrl = normalizeProfileUrl(baseItem, identifier);
  const attendeeId = normalizeAttendeeId(baseItem, {});

  merged.push({
    identifier,
    identifierKey: key,
    relation,
    displayName,
    profileUrl,
    attendeeId,
    sourceItem: baseItem,
  });
}

merged.sort((a, b) => {
  const rank = { mutual: 0, following_only: 1, followers_only: 2 };
  return (rank[a.relation] ?? 9) - (rank[b.relation] ?? 9) || a.identifier.localeCompare(b.identifier);
});

let sent = 0;
let skipped = 0;
let failed = 0;
let eligible = 0;
let persisted = 0;
const actions = [];

for (const candidate of merged) {
  const stateKey = CFG.unipileAccountId + ':' + candidate.identifierKey;
  const existing = stateMap.get(stateKey) || {};
  const state = {
    stateKey,
    identifier: candidate.identifier,
    unipileAccountId: CFG.unipileAccountId,
    relation: candidate.relation,
    displayName: candidate.displayName || existing.display_name || candidate.identifier,
    profileUrl: candidate.profileUrl || existing.profile_url || '',
    attendeeId: existing.attendee_id || candidate.attendeeId || '',
    connectionStatus: existing.connection_status || 'requested',
    dmSequenceStartedAt: existing.dm_sequence_started_at || '',
    lastCheckedAt: existing.last_checked_at || new Date().toISOString(),
    firstSeenAt: existing.first_seen_at || new Date().toISOString(),
    lastSentAt: existing.last_sent_at || '',
    lastChatId: existing.last_chat_id || '',
    lastMessage: existing.last_message || '',
    completedAt: existing.completed_at || '',
    sequenceStep: Number(existing.sequence_step || 0),
    sourceWorkflowName: existing.source_workflow_name || CFG.workflowName,
    sourceKey: existing.source_key || ('candidate:' + candidate.identifierKey),
  };
  state.relation = candidate.relation;

  if (!state.attendeeId) state.attendeeId = candidate.attendeeId || '';
  if (!state.attendeeId) {
    const profile = await resolveProfile.call(this, candidate.identifier);
    state.attendeeId = normalizeAttendeeId(candidate.sourceItem, profile) || normalizeAttendeeId(profile, {});
    state.displayName = normalizeName(candidate.sourceItem, profile) || state.displayName;
    if (!state.profileUrl) state.profileUrl = normalizeProfileUrl(candidate.sourceItem, candidate.identifier);
  }

  if (!state.attendeeId) {
    skipped += 1;
    state.lastCheckedAt = new Date().toISOString();
    const ok = await persistState.call(this, state, candidate, 'skipped', { payload_json: { reason: 'missing_attendee_id' } });
    if (ok) persisted += 1;
    actions.push({ identifier: candidate.identifier, status: 'skipped', reason: 'missing_attendee_id' });
    continue;
  }

  const currentStep = Number(state.sequenceStep || 0);
  const nextStep = currentStep + 1;
  const startedAt = state.dmSequenceStartedAt ? Date.parse(state.dmSequenceStartedAt) : NaN;
  const now = Date.now();
  const due =
    nextStep === 1
      ? !state.dmSequenceStartedAt
      : Number.isFinite(startedAt) && now - startedAt >= STEP_WINDOWS[nextStep - 1];

  eligible += 1;
  state.lastCheckedAt = new Date().toISOString();

  if (!due || nextStep >= MESSAGE_TEMPLATES.length || !MESSAGE_TEMPLATES[nextStep]) {
    skipped += 1;
    state.connectionStatus = state.connectionStatus || 'requested';
    actions.push({
      identifier: candidate.identifier,
      status: 'skipped',
      relation: candidate.relation,
      step: currentStep,
      next_step: nextStep,
      reason: due ? 'no_message_for_step' : 'not_due_yet',
    });
    const ok = await persistState.call(this, state, candidate, 'skipped', {
      payload_json: { reason: due ? 'no_message_for_step' : 'not_due_yet' },
    });
    if (ok) persisted += 1;
    continue;
  }

  const firstName = firstNameFromDisplay(state.displayName, candidate.identifier);
  const message = sanitizeMessage(String(MESSAGE_TEMPLATES[nextStep]).replace(/\\{first_name\\}/gi, firstName));

  try {
    const chatResp = await sendDirectMessage.call(this, state.attendeeId, message);
    const chatId = first(chatResp?.chat_id, chatResp?.id, chatResp?.data?.chat_id, chatResp?.data?.id);

    state.sequenceStep = nextStep;
    state.dmSequenceStartedAt = state.dmSequenceStartedAt || new Date().toISOString();
    state.lastSentAt = new Date().toISOString();
    state.lastChatId = chatId || state.lastChatId || '';
    state.lastMessage = message;
    state.connectionStatus = nextStep >= 4 ? 'completed' : 'messaged';
    if (nextStep >= 4) state.completedAt = state.completedAt || new Date().toISOString();

    sent += 1;
    actions.push({
      identifier: candidate.identifier,
      status: 'sent',
      relation: candidate.relation,
      step: nextStep,
      chat_id: chatId || '',
    });
    const ok = await persistState.call(this, state, candidate, 'sent', {
      payload_json: { last_chat_id: chatId || '', last_message: message },
      metadata_json: { chat_id: chatId || '' },
    });
    if (ok) persisted += 1;
  } catch (err) {
    failed += 1;
    state.lastCheckedAt = new Date().toISOString();
    actions.push({
      identifier: candidate.identifier,
      status: 'failed',
      relation: candidate.relation,
      step: nextStep,
      error: describeError(err),
    });
    const ok = await persistState.call(this, state, candidate, 'failed', {
      payload_json: { error: describeError(err) },
    });
    if (ok) persisted += 1;
  }

  if (sent >= CFG.maxSendsPerRun) break;
}

return [{
  json: {
    ok: true,
    workflow_name: CFG.workflowName,
    followers_scanned: followers.length,
    following_scanned: following.length,
    candidates: merged.length,
    eligible,
    sent,
    skipped,
    failed,
    persisted,
    actions: actions.slice(0, 25),
    message_templates: MESSAGE_TEMPLATES.length - 1,
  },
}];`.trim(),
    },
    position: [760, 380],
  },
  output: [{ json: { ok: true, followers_scanned: 0, following_scanned: 0, candidates: 0, eligible: 0, sent: 0, skipped: 0, failed: 0, persisted: 0 } }],
});

const result = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Result',
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: 'ok', name: 'ok', type: 'boolean', value: '={{ $json.ok }}' },
          { id: 'followers_scanned', name: 'followers_scanned', type: 'number', value: '={{ $json.followers_scanned }}' },
          { id: 'following_scanned', name: 'following_scanned', type: 'number', value: '={{ $json.following_scanned }}' },
          { id: 'candidates', name: 'candidates', type: 'number', value: '={{ $json.candidates }}' },
          { id: 'eligible', name: 'eligible', type: 'number', value: '={{ $json.eligible }}' },
          { id: 'sent', name: 'sent', type: 'number', value: '={{ $json.sent }}' },
          { id: 'skipped', name: 'skipped', type: 'number', value: '={{ $json.skipped }}' },
          { id: 'failed', name: 'failed', type: 'number', value: '={{ $json.failed }}' },
          { id: 'persisted', name: 'persisted', type: 'number', value: '={{ $json.persisted }}' },
        ],
      },
    },
    position: [1020, 380],
  },
  output: [{ json: { ok: true, followers_scanned: 0, following_scanned: 0, candidates: 0 } }],
});

export default workflow('lt-instagram-dm-sequence', 'LT - Instagram DM Sequence (Unipile)')
  .add(schedule)
  .to(config)
  .to(ensureTable)
  .to(loadState)
  .to(processNode)
  .to(result)
  .add(manual)
  .to(config);
