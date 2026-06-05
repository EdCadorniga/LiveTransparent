import { workflow, node, trigger } from '@n8n/workflow-sdk';

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '15 */6 * * *' }] } },
    position: [240, 300],
  },
  output: [{}],
});

const manualTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [240, 460] },
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
          { id: 'workflowName', name: 'workflowName', type: 'string', value: 'LT - LinkedIn Connection State Sync (Unipile)' },
          { id: 'locationId', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: 'ghlApiBaseUrl', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
           { id: 'ghlApiKey', name: 'ghlApiKey', type: 'string', value: 'pit-b278b3ad-96bd-41fb-ba03-9f927039eb28' },
          { id: 'unipileApiBaseUrl', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: 'unipileApiKey', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: 'unipileAccountId', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: 'requestTag', name: 'requestTag', type: 'string', value: 'linkedin_connection_requested' },
          { id: 'linkedinCustomFieldName', name: 'linkedinCustomFieldName', type: 'string', value: 'Apollo Person Linkedin URL' },
          { id: 'stateUpsertUrl', name: 'stateUpsertUrl', type: 'string', value: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert' },
          { id: 'pageSize', name: 'pageSize', type: 'number', value: 50 },
          { id: 'maxPages', name: 'maxPages', type: 'number', value: 20 },
          { id: 'maxContacts', name: 'maxContacts', type: 'number', value: 1000 },
          { id: 'dryRun', name: 'dryRun', type: 'boolean', value: false },
        ],
      },
    },
    position: [480, 380],
  },
  output: [{ json: {} }],
});

const sync = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Sync LinkedIn Connection State',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const cfg = $node['Config'].json || {};
const workflowName = String(cfg.workflowName || 'LT - LinkedIn Connection State Sync (Unipile)').trim();
const locationId = String(cfg.locationId || '').trim();
const ghlApiBaseUrl = String(cfg.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\\/$/, '');
const ghlApiKey = String(cfg.ghlApiKey || '').trim();
const unipileApiBaseUrl = String(cfg.unipileApiBaseUrl || 'https://api42.unipile.com:17256/api/v1').replace(/\\/$/, '');
const unipileApiKey = String(cfg.unipileApiKey || '').trim();
const unipileAccountId = String(cfg.unipileAccountId || '').trim();
const requestTag = String(cfg.requestTag || 'linkedin_connection_requested').trim();
const linkedinCustomFieldName = String(cfg.linkedinCustomFieldName || 'Apollo Person Linkedin URL').trim().toLowerCase();
const stateUpsertUrl = String(cfg.stateUpsertUrl || 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert').trim();
const pageSize = Math.max(10, Math.min(100, Number(cfg.pageSize || 50)));
const maxPages = Math.max(1, Math.min(100, Number(cfg.maxPages || 20)));
const maxContacts = Math.max(1, Math.min(5000, Number(cfg.maxContacts || 1000)));
const dryRun = !!cfg.dryRun;

if (!locationId) throw new Error('Missing locationId');
if (!ghlApiKey) throw new Error('Missing GHL apiKey');
if (!unipileApiKey) throw new Error('Missing Unipile apiKey');
if (!unipileAccountId) throw new Error('Missing Unipile accountId');

function clean(v) {
  if (v === undefined || v === null) return '';
  return String(v).trim();
}
function hasTag(contact, tagName) {
  const tags = Array.isArray(contact?.tags) ? contact.tags : [];
  return tags.some((t) => (typeof t === 'string' ? t : clean(t?.name || t?.value || '')).trim() === tagName);
}
function extractUrls(raw) {
  const value = clean(raw);
  if (!value) return [];
  return Array.from(new Set((value.match(/https?:\\/\\/[^\\s,]+/gi) || []).map((u) => clean(u).replace(/[).,;]+$/, ''))));
}
function getLinkedInUrl(contact) {
  const fields = Array.isArray(contact?.customFields) ? contact.customFields : [];
  if (linkedinCustomFieldName) {
    const preferred = fields.find((f) => clean(f?.name || f?.label || f?.key || '').toLowerCase() === linkedinCustomFieldName);
    if (preferred) {
      const urls = extractUrls(preferred.value).filter((u) => /linkedin\\.com/i.test(u) && /\\/in\\//i.test(u));
      if (urls.length > 0) return urls[0];
    }
  }
  for (const f of fields) {
    const urls = extractUrls(f?.value).filter((u) => /linkedin\\.com/i.test(u) && /\\/in\\//i.test(u));
    if (urls.length > 0) return urls[0];
  }
  return '';
}
function linkedinIdentifier(input) {
  const raw = clean(input);
  if (!raw) return '';
  const urls = extractUrls(raw);
  const linkedinUrl = urls.find((u) => /linkedin\\.com/i.test(u));
  const candidate = linkedinUrl || raw;
  if (!/^https?:\\/\\//i.test(candidate)) return decodeURIComponent(candidate).replace(/^@/, '').replace(/\\/$/, '').trim();
  const withoutScheme = candidate.replace(/^https?:\\/\\//i, '');
  const host = withoutScheme.split('/')[0].split('?')[0].toLowerCase();
  if (host !== 'linkedin.com' && !host.endsWith('.linkedin.com')) {
    if (linkedinUrl) return linkedinIdentifier(linkedinUrl);
    return '';
  }
  const path = withoutScheme.slice(withoutScheme.indexOf('/') >= 0 ? withoutScheme.indexOf('/') : withoutScheme.length).split('?')[0].split('#')[0];
  const parts = path.split('/').filter(Boolean);
  const idx = parts.findIndex((p) => p.toLowerCase() === 'in');
  const val = idx >= 0 && parts[idx + 1] ? parts[idx + 1] : parts[parts.length - 1];
  return decodeURIComponent(val || '').replace(/^@/, '').replace(/\\/$/, '').trim();
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest(method, url, body, extraHeaders = {}) {
  try {
    const data = await doHttpRequest.call(this, {
      method,
      url,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...extraHeaders,
      },
      json: true,
      body,
    });
    return { ok: true, data };
  } catch (err) {
    return { ok: false, data: err?.response?.body || err?.message || err };
  }
}
async function ghlSearch(page, fieldName) {
  return await apiRequest.call(this, 'POST', ghlApiBaseUrl + '/contacts/search', {
    locationId,
    pageLimit: pageSize,
    page,
    filters: [{ field: fieldName, operator: 'exists' }],
  }, {
    Authorization: 'Bearer ' + ghlApiKey,
    Version: '2021-07-28',
  });
}

const matched = [];
const errors = [];
let scanned = 0;
let upserted = 0;
const seenContactIds = new Set();

for (const fieldName of ['customFields.apollo_person_linkedin_url', 'customFields.em_contact_linkedin_urls']) {
  for (let page = 1; page <= maxPages; page += 1) {
    const resp = await ghlSearch.call(this, page, fieldName);
    const contacts = Array.isArray(resp?.data?.contacts) ? resp.data.contacts : Array.isArray(resp?.data?.data) ? resp.data.data : Array.isArray(resp?.data) ? resp.data : [];
    if (!contacts.length) break;

    for (const contact of contacts) {
      scanned += 1;
      if (matched.length >= maxContacts) break;
      const contactId = clean(contact?.id || '');
      if (!contactId || seenContactIds.has(contactId)) continue;
      if (hasTag(contact, requestTag)) continue;
      if (hasTag(contact, 'linkedin_connected')) continue;
      const liUrl = getLinkedInUrl(contact);
      const identifier = linkedinIdentifier(liUrl);
      if (!liUrl || !identifier) continue;

      const profile = await apiRequest.call(this, 'GET', unipileApiBaseUrl + '/users/' + encodeURIComponent(identifier) + '?account_id=' + encodeURIComponent(unipileAccountId), undefined, { 'X-API-KEY': unipileApiKey });
      const providerId = clean(profile.data?.provider_id || profile.data?.providerId || profile.data?.id || '');
      const firstName = clean(contact?.firstName || profile.data?.first_name || profile.data?.firstName || 'there');

      if (!profile.ok || !providerId) {
        errors.push({ contact_id: contactId, identifier, reason: 'profile_lookup_failed' });
        continue;
      }

      const payload = {
        ghl_contact_id: contactId,
        location_id: locationId,
        unipile_account_id: unipileAccountId,
        linkedin_profile_url: liUrl,
        linkedin_public_identifier: identifier,
        linkedin_provider_id: providerId,
        connection_request_tag: requestTag,
        connection_status: 'ready',
        request_sent_at: null,
        connected_at: null,
        request_message: '',
        sequence_step: 0,
        source_workflow_name: workflowName,
        source_key: 'contact:' + contactId,
        payload_json: {
          contactId,
          firstName,
          liUrl,
          identifier,
          providerId,
          status: 'ready',
          source: 'state_sync',
        },
        metadata_json: {
          source: 'backfill_sync',
          workflow: workflowName,
        },
      };

      if (!dryRun) {
        const upsert = await apiRequest.call(this, 'POST', stateUpsertUrl, payload);
        if (upsert.ok) upserted += 1;
        else errors.push({ contact_id: payload.ghl_contact_id, identifier, reason: 'state_upsert_failed' });
      }

      seenContactIds.add(contactId);
      matched.push({ contact_id: payload.ghl_contact_id, identifier, provider_id: providerId, li_url: liUrl });
    }

    if (matched.length >= maxContacts || contacts.length < pageSize) break;
  }
}

return [{
  json: {
    ok: true,
    workflow_name: workflowName,
    scanned,
    matched: matched.length,
    upserted,
    dry_run: dryRun,
    errors: errors.length,
    sample: matched.slice(0, 10),
    error_sample: errors.slice(0, 10),
  },
}];`,
    },
    position: [720, 380],
  },
  output: [{ json: { ok: true, scanned: 0, matched: 0, upserted: 0 } }],
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
          { id: 'matched', name: 'matched', type: 'number', value: '={{ $json.matched }}' },
          { id: 'upserted', name: 'upserted', type: 'number', value: '={{ $json.upserted }}' },
          { id: 'errors', name: 'errors', type: 'number', value: '={{ $json.errors }}' },
          { id: 'dry_run', name: 'dry_run', type: 'boolean', value: '={{ $json.dry_run }}' },
        ],
      },
    },
    position: [960, 380],
  },
  output: [{ json: { ok: true, scanned: 0, matched: 0, upserted: 0 } }],
});

export default workflow('lt-linkedin-connection-state-sync', 'LT - LinkedIn Connection State Sync (Unipile)')
  .add(scheduleTrigger)
  .to(config)
  .to(sync)
  .to(result)
  .add(manualTrigger)
  .to(config);
