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
          { id: '1', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: '2', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: '3', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: '4', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: '5', name: 'ghlApiKey', type: 'string', value: 'pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86' },
          { id: '6', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: '7', name: 'stateUpsertUrl', type: 'string', value: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert' },
          { id: '8', name: 'templateVariant', type: 'string', value: 'v2' },
          { id: '9', name: 'maxPages', type: 'number', value: 5 },
          { id: '10', name: 'pageSize', type: 'number', value: 100 },
          { id: '11', name: 'maxFollowersPerRun', type: 'number', value: 30 },
        ],
      },
    },
    position: [500, 380],
  },
  output: [{ json: {} }],
});

const query = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Load LinkedIn Follower State',
    parameters: {
      operation: 'executeQuery',
      query: `SELECT
  ghl_contact_id,
  location_id,
  unipile_account_id,
  linkedin_profile_url,
  linkedin_public_identifier,
  linkedin_provider_id,
  connection_status,
  sequence_step,
  payload_json,
  metadata_json
FROM linkedin_connection_state
WHERE connection_status IN ('follower', 'follower_messaged')
   OR ghl_contact_id LIKE 'linkedin:follower:%'
ORDER BY updated_at ASC;`,
    },
    credentials: { postgres: newCredential('Postgres account') },
    alwaysOutputData: true,
    position: [740, 380],
  },
  output: [{ ghl_contact_id: 'linkedin:follower:sample' }],
});

const syncFollowers = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Sync LinkedIn Followers',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `var CFG = (function() {
  var c = $node['Config'].json || {};
  return {
    unipileApiBaseUrl: String(c.unipileApiBaseUrl || 'https://api42.unipile.com:17256/api/v1').replace(/\\/+$/, ''),
    unipileApiKey: String(c.unipileApiKey || '').trim(),
    unipileAccountId: String(c.unipileAccountId || '').trim(),
    locationId: String(c.locationId || '').trim(),
    stateUpsertUrl: String(c.stateUpsertUrl || '').trim(),
    maxPages: Math.max(1, Math.min(10, Number(c.maxPages || 5))),
    pageSize: Math.max(1, Math.min(200, Number(c.pageSize || 100))),
    maxFollowersPerRun: Math.max(1, Math.min(500, Number(c.maxFollowersPerRun || 100))),
  };
})();

function clean(v) {
  if (v == null) return '';
  if (typeof v === 'string') return v.trim();
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  return '';
}

function first() {
  for (var i = 0; i < arguments.length; i++) {
    var s = clean(arguments[i]);
    if (s) return s;
  }
  return '';
}

function describeError(err) {
  if (err instanceof Error) return err.stack || err.message || err.name || 'Unknown error';
  if (typeof err === 'string') return err;
  if (err && typeof err === 'object') {
    var parts = [];
    if ('message' in err && err.message) parts.push(String(err.message));
    if ('statusCode' in err && err.statusCode !== undefined) parts.push('statusCode=' + String(err.statusCode));
    var body = err?.response?.body ?? err?.body ?? err?.data;
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

function buildUrl(path, params) {
  var query = [];
  params = params || {};
  for (var key in params) {
    if (!Object.prototype.hasOwnProperty.call(params, key)) continue;
    var value = params[key];
    if (value === undefined || value === null || value === '') continue;
    query.push(encodeURIComponent(key) + '=' + encodeURIComponent(String(value)));
  }
  return CFG.unipileApiBaseUrl + path + (query.length ? '?' + query.join('&') : '');
}

async function apiRequest(method, path, body, params) {
  var options = {
    method: method,
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
  var cursor = resp?.cursor ?? resp?.data?.cursor ?? resp?.next_cursor ?? resp?.data?.next_cursor ?? '';
  if (!cursor) return '';
  if (typeof cursor === 'string') return cursor;
  if (typeof cursor === 'object') return first(cursor.next, cursor.cursor, cursor.value, cursor.token, cursor.id);
  return '';
}

function normalizeIdentifier(item) {
  return first(item?.public_identifier, item?.username, item?.identifier, item?.publicIdentifier, item?.messaging_id, item?.member_id, item?.id);
}

function normalizeProfileUrl(profile, identifier) {
  return first(profile?.profile_url, profile?.public_profile_url, profile?.profileUrl, 'https://www.linkedin.com/in/' + identifier);
}

function normalizeName(profile, item, identifier) {
  return first(
    profile?.name,
    profile?.first_name && profile?.last_name ? String(profile.first_name) + ' ' + String(profile.last_name) : '',
    profile?.first_name,
    item?.name,
    item?.first_name && item?.last_name ? String(item.first_name) + ' ' + String(item.last_name) : '',
    item?.first_name,
    identifier
  );
}

function firstNameFromDisplay(displayName, identifier) {
  var base = clean(displayName || identifier || 'there').replace(/[._]+/g, ' ');
  var token = first(base.split(/\s+/)[0], 'there');
  if (!token) return 'there';
  return token.charAt(0).toUpperCase() + token.slice(1);
}

async function fetchPaged(path) {
  var items = [];
  var cursor = '';
  for (var page = 0; page < CFG.maxPages; page += 1) {
    var resp = await apiRequest.call(this, 'GET', path, undefined, {
      account_id: CFG.unipileAccountId,
      cursor: cursor || undefined,
      limit: CFG.pageSize,
    });
    var pageItems = extractItems(resp);
    items.push.apply(items, pageItems);
    cursor = extractCursor(resp);
    if (!cursor || pageItems.length === 0 || items.length >= CFG.maxFollowersPerRun) break;
  }
  return items.slice(0, CFG.maxFollowersPerRun);
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

const followers = await fetchPaged.call(this, '/users/followers');
const seen = new Set();
const rows = [];
const errors = [];

for (var i = 0; i < followers.length; i += 1) {
  var item = followers[i] || {};
  var identifier = normalizeIdentifier(item);
  if (!identifier) continue;
  var key = identifier.toLowerCase();
  if (seen.has(key)) continue;
  seen.add(key);

  var profile = await resolveProfile.call(this, identifier);
  var providerId = clean(profile?.provider_id || profile?.providerId || profile?.id || item?.provider_id || item?.providerId || item?.id || '');
  if (!providerId) {
    errors.push({ identifier: identifier, reason: 'missing_provider_id' });
    continue;
  }

  var displayName = normalizeName(profile, item, identifier);
  var firstName = firstNameFromDisplay(displayName, identifier);
  var profileUrl = normalizeProfileUrl(profile, identifier);
  var now = new Date().toISOString();

  rows.push({
    ghl_contact_id: 'linkedin:follower:' + providerId,
    location_id: CFG.locationId,
    unipile_account_id: CFG.unipileAccountId,
    linkedin_profile_url: profileUrl,
    linkedin_public_identifier: identifier,
    linkedin_provider_id: providerId,
    connection_request_tag: 'linkedin_follower_sync',
    connection_status: 'follower',
    request_sent_at: null,
    connected_at: null,
    dm_sequence_started_at: null,
    last_checked_at: now,
    request_message: '',
    request_message_hash: '',
    sequence_step: 0,
    source_workflow_name: 'LT - LinkedIn Followers Sync (Unipile)',
    source_key: 'follower:' + providerId,
    payload_json: {
      source: 'follower_sync',
      identifier: identifier,
      provider_id: providerId,
      first_name: firstName,
      display_name: displayName,
      profile_url: profileUrl,
    },
    metadata_json: {
      source: 'follower_sync',
    },
  });
}

var upserted = 0;
for (var j = 0; j < rows.length; j += 1) {
  try {
    await this.helpers.httpRequest({
      method: 'POST',
      url: CFG.stateUpsertUrl,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: rows[j],
      json: true,
    });
    upserted += 1;
  } catch (err) {
    errors.push({ identifier: rows[j].linkedin_public_identifier || '', reason: describeError(err) });
  }
}

return [{
  json: {
    ok: true,
    workflow_name: 'LT - LinkedIn Followers Sync (Unipile)',
    scanned: followers.length,
    upserted: upserted,
    errors: errors.length,
    sample: rows.slice(0, 10),
    error_sample: errors.slice(0, 10),
  },
}];`,
    },
    position: [760, 380],
  },
  output: [{ json: { ok: true, scanned: 0, upserted: 0, errors: 0 } }],
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
          { id: 'scanned', name: 'scanned', type: 'number', value: '={{ $json.scanned }}' },
          { id: 'upserted', name: 'upserted', type: 'number', value: '={{ $json.upserted }}' },
          { id: 'errors', name: 'errors', type: 'number', value: '={{ $json.errors }}' },
        ],
      },
    },
    position: [1020, 380],
  },
  output: [{ json: { ok: true, scanned: 0, upserted: 0, errors: 0 } }],
});

export default workflow('lt-linkedin-follower-sync', 'LT - LinkedIn Followers Sync (Unipile)')
  .add(schedule)
  .to(config)
  .to(syncFollowers)
  .to(result)
  .add(manual)
  .to(config);
