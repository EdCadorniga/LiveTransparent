const cfg = $json || {};

function str(v) { const s = String(v ?? '').trim(); return s || null; }
function normalizePhone(phoneRaw, countryHint) {
  const raw = str(phoneRaw);
  if (!raw) return null;
  const keepPlus = raw.startsWith('+');
  let digits = raw.replace(/\D+/g, '');
  if (!digits) return null;
  if (keepPlus) return `+${digits}`;
  if (digits.length === 10 && String(countryHint || '').toUpperCase() === 'US') return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`;
  return `+${digits}`;
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ method, url, headers, body, json = true }) {
  const options = { method, url, headers, json };
  if (body !== undefined) options.body = body;
  try {
    const data = await doHttpRequest.call(this, options);
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      status: err?.statusCode || err?.httpCode || err?.cause?.statusCode || 500,
      data: err?.response?.body || err?.message || err,
    };
  }
}

const smartHeaders = {
  'token-id': cfg.smartListToken,
  'Version': '2021-07-28',
  'source': 'WEB_USER',
  'channel': 'APP',
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'User-Agent': 'Mozilla/5.0',
};
const ghlHeaders = {
  Authorization: `Bearer ${cfg.ghlApiKey}`,
  Version: '2021-07-28',
  'Content-Type': 'application/json',
  Accept: 'application/json',
};
const n8nHeaders = {
  'X-N8N-API-KEY': cfg.n8nApiKey,
  Accept: 'application/json',
  'User-Agent': 'Mozilla/5.0',
};

async function getSmartListDefinition() {
  return await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/smartlist/${encodeURIComponent(cfg.smartListId)}?transform=true`,
    headers: smartHeaders,
  });
}

async function getQueuedContacts() {
  const defRes = await getSmartListDefinition.call(this);
  if (!defRes.ok) throw new Error(`Failed to fetch smart list definition: ${JSON.stringify(defRes.data)}`);
  const smartList = defRes.data?.smartList || {};
  const filters = smartList?.filterSpecs?.filters || [];
  const sort = smartList?.sortSpecs || [];
  const pageLimit = Number(cfg.pageLimit || 100);
  const maxPages = Number(cfg.maxPages || 20);
  const contacts = [];
  let page = 1;
  while (page <= maxPages) {
    const res = await apiRequest.call(this, {
      method: 'POST',
      url: `${cfg.ghlApiBaseUrl}/contacts/search/2`,
      headers: smartHeaders,
      body: {
        filters,
        locationId: cfg.locationId,
        page,
        pageLimit,
        sort,
      },
    });
    if (!res.ok) throw new Error(`Failed to fetch queued contacts page ${page}: ${JSON.stringify(res.data)}`);
    const batch = Array.isArray(res.data?.contacts) ? res.data.contacts : [];
    contacts.push(...batch);
    if (batch.length < pageLimit) break;
    page += 1;
  }
  return contacts;
}

function extractNodeJson(execution) {
  const runData = execution?.data?.resultData?.runData || {};
  const names = ['Apollo Phone + Profile Enrichment -> Update GHL', 'Finalize Response'];
  for (const name of names) {
    const json = runData?.[name]?.[0]?.data?.main?.[0]?.[0]?.json;
    if (json && typeof json === 'object') return json;
  }
  return null;
}

async function buildExecutionMap(targetContactIds) {
  const execRes = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.n8nApiBaseUrl}/executions?workflowId=${encodeURIComponent(cfg.sourceWorkflowId)}&limit=${encodeURIComponent(String(cfg.executionLimit || 250))}`,
    headers: n8nHeaders,
  });
  if (!execRes.ok) throw new Error(`Failed to list source executions: ${JSON.stringify(execRes.data)}`);
  const executions = Array.isArray(execRes.data?.data) ? execRes.data.data : [];
  const map = new Map();
  for (const exec of executions) {
    if (map.size >= targetContactIds.size) break;
    const detailRes = await apiRequest.call(this, {
      method: 'GET',
      url: `${cfg.n8nApiBaseUrl}/executions/${encodeURIComponent(exec.id)}?includeData=true`,
      headers: n8nHeaders,
    });
    if (!detailRes.ok) continue;
    const nodeJson = extractNodeJson(detailRes.data);
    const contactId = str(nodeJson?.contactId);
    if (!contactId || !targetContactIds.has(contactId) || map.has(contactId)) continue;
    map.set(contactId, { executionId: exec.id, data: nodeJson });
  }
  return map;
}

async function getContact(contactId) {
  const res = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}`,
    headers: ghlHeaders,
  });
  if (!res.ok) throw new Error(`Failed to fetch contact ${contactId}: ${JSON.stringify(res.data)}`);
  return res.data?.contact || res.data || {};
}

async function getCustomFields() {
  const res = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/locations/${encodeURIComponent(cfg.locationId)}/customFields?model=contact`,
    headers: ghlHeaders,
  });
  if (!res.ok) throw new Error(`Failed to fetch custom fields: ${JSON.stringify(res.data)}`);
  const customFields = Array.isArray(res.data?.customFields)
    ? res.data.customFields
    : Array.isArray(res.data?.data?.customFields)
      ? res.data.data.customFields
      : Array.isArray(res.data?.data)
        ? res.data.data
        : [];
  return new Map(customFields.map((f) => [String(f.name || '').trim(), f]));
}

function cf(fieldByName, name, value) {
  if (value === null || value === undefined || String(value).trim() === '') return null;
  const f = fieldByName.get(name);
  if (!f?.id) return null;
  let normalized = value;
  if (f.dataType === 'TEXT' && typeof normalized === 'string' && normalized.length > 255) normalized = normalized.slice(0, 255);
  if (f.dataType === 'DATE' && typeof normalized === 'string') {
    const d = new Date(normalized);
    if (!Number.isNaN(d.getTime())) normalized = d.toISOString().slice(0, 10);
  }
  return { id: f.id, value: normalized };
}

function customUpdatesFromHistorical(history) {
  const body = history?.updateRequestBodyUsed || history?.updateAttempts?.find((a) => a?.body)?.body || {};
  if (body.customField && typeof body.customField === 'object') {
    return Object.entries(body.customField).map(([id, value]) => ({ id, value }));
  }
  if (Array.isArray(body.customFields)) {
    return body.customFields.map((item) => ({ id: item.id, value: item.value ?? item.field_value ?? null })).filter((i) => i.id);
  }
  return [];
}

function standardFromHistorical(history) {
  const body = history?.updateRequestBodyUsed || history?.updateAttempts?.find((a) => a?.body)?.body || {};
  const standard = { ...body };
  delete standard.locationId;
  delete standard.customField;
  delete standard.customFields;
  return standard;
}

function findDuplicatePhoneConflict(...attemptGroups) {
  for (const group of attemptGroups) {
    for (const attempt of group || []) {
      const resp = attempt?.response || {};
      if (resp?.message === 'This location does not allow duplicated contacts.' && resp?.meta?.matchingField === 'phone') {
        return { contactId: resp?.meta?.contactId || null, contactName: resp?.meta?.contactName || null, matchingField: resp?.meta?.matchingField || null };
      }
    }
  }
  return null;
}

async function updateContactWithFallback(contactId, standard, customFieldUpdates) {
  const standardClean = Object.fromEntries(Object.entries(standard || {}).filter(([,v]) => v !== null && v !== undefined && String(v).trim() !== ''));
  const customFieldObject = Object.fromEntries((customFieldUpdates || []).map((u) => [u.id, u.value]));
  const customFieldArray = (customFieldUpdates || []).map((u) => ({ id: u.id, value: u.value }));
  const customFieldArrayFieldValue = (customFieldUpdates || []).map((u) => ({ id: u.id, field_value: u.value }));
  const bodies = [
    { ...standardClean, locationId: cfg.locationId, customField: customFieldObject },
    { ...standardClean, customField: customFieldObject },
    { ...standardClean, locationId: cfg.locationId, customFields: customFieldArray },
    { ...standardClean, customFields: customFieldArray },
    { ...standardClean, locationId: cfg.locationId, customFields: customFieldArrayFieldValue },
    { ...standardClean, customFields: customFieldArrayFieldValue },
    { ...standardClean, locationId: cfg.locationId },
  ];
  const attempts = [];
  for (const body of bodies) {
    const res = await apiRequest.call(this, {
      method: 'PUT',
      url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}`,
      headers: ghlHeaders,
      body,
    });
    if (res.ok) return { ok: true, bodyUsed: body };
    attempts.push({ body, status: res.status, response: res.data });
  }
  return { ok: false, updateAttempts: attempts };
}

async function searchDuplicatePhone(contactId, normalizedPhone, countryHint) {
  const res = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(normalizedPhone)}&limit=5`,
    headers: ghlHeaders,
  });
  if (!res.ok) return null;
  const possible = Array.isArray(res.data?.contacts) ? res.data.contacts : Array.isArray(res.data?.data?.contacts) ? res.data.data.contacts : [];
  const match = possible.find((c) => c?.id && c.id !== contactId && normalizePhone(c.phone, c.country || countryHint || null) === normalizedPhone);
  return match ? { contactId: match.id, contactName: match.contactName || [match.firstName, match.lastName].filter(Boolean).join(' ') || null, matchingField: 'phone' } : null;
}

async function applyStatus(fieldByName, contactId, status, enrichedDate = null) {
  const updates = [];
  if (status === 'enriched') {
    updates.push(cf(fieldByName, 'Apollo Phone Enrichment Status', 'enriched'));
    updates.push(cf(fieldByName, 'Apollo Phone Enriched At', enrichedDate || new Date().toISOString().slice(0, 10)));
    updates.push(cf(fieldByName, 'Contact already Enriched', 'Yes'));
    updates.push(cf(fieldByName, 'Enrich via Apollo', 'No'));
    updates.push(cf(fieldByName, 'Enrich Phone via Apollo', 'No'));
  } else if (status === 'no_match') {
    updates.push(cf(fieldByName, 'Apollo Phone Enrichment Status', 'no_match'));
    updates.push(cf(fieldByName, 'Enrich Phone via Apollo', 'No'));
  } else if (status === 'error') {
    updates.push(cf(fieldByName, 'Apollo Phone Enrichment Status', 'error'));
    updates.push(cf(fieldByName, 'Enrich Phone via Apollo', 'No'));
  }
  const filtered = updates.filter(Boolean);
  if (!filtered.length) return { ok: true, skipped: true };
  return await updateContactWithFallback.call(this, contactId, {}, filtered);
}

const queuedContacts = await getQueuedContacts.call(this);
const targetIds = new Set(queuedContacts.map((c) => c.id).filter(Boolean));
const executionMap = await buildExecutionMap.call(this, targetIds);
const fieldByName = await getCustomFields.call(this);
const results = [];

for (const queued of queuedContacts) {
  const contactId = queued.id;
  const historicalWrapper = executionMap.get(contactId);
  const historical = historicalWrapper?.data;
  if (!historical) {
    results.push({ contactId, contactName: queued.contactName || null, outcome: 'missing_history' });
    continue;
  }
  const liveContact = await getContact.call(this, contactId);
  const historyBody = historical?.updateRequestBodyUsed || historical?.updateAttempts?.find((a) => a?.body)?.body || {};
  const historicalPhone = normalizePhone(historyBody.phone || historical?.normalizedPhone || historical?.ingestRecord?.company_phone || null, liveContact.country || queued.country || null);
  const existingPhone = normalizePhone(liveContact.phone || null, liveContact.country || queued.country || null);

  if (existingPhone) {
    const enrichedDate = (historyBody.customField && historyBody.customField.kovIoEY13dW0mSuhfMPv) || null;
    const upd = await applyStatus.call(this, fieldByName, contactId, 'enriched', enrichedDate);
    results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: upd.ok ? 'status_enriched_from_existing_phone' : 'status_update_failed', existingPhone });
    continue;
  }

  if (!historicalPhone) {
    const upd = await applyStatus.call(this, fieldByName, contactId, 'no_match');
    results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: upd.ok ? 'marked_no_match_from_history' : 'status_update_failed' });
    continue;
  }

  const duplicate = await searchDuplicatePhone.call(this, contactId, historicalPhone, liveContact.country || queued.country || null);
  if (duplicate) {
    const upd = await applyStatus.call(this, fieldByName, contactId, 'error');
    results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: upd.ok ? 'marked_error_duplicate_phone' : 'status_update_failed', normalizedPhone: historicalPhone, duplicatePhoneConflict: duplicate });
    continue;
  }

  const standard = standardFromHistorical(historical);
  const customFieldUpdates = customUpdatesFromHistorical(historical);
  const upd = await updateContactWithFallback.call(this, contactId, standard, customFieldUpdates);
  if (upd.ok) {
    results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: 'replayed_historical_update', normalizedPhone: historicalPhone });
    continue;
  }

  const duplicateConflict = findDuplicatePhoneConflict(upd.updateAttempts);
  if (duplicateConflict) {
    await applyStatus.call(this, fieldByName, contactId, 'error');
    results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: 'marked_error_duplicate_phone_after_replay', normalizedPhone: historicalPhone, duplicatePhoneConflict: duplicateConflict });
    continue;
  }

  results.push({ contactId, contactName: queued.contactName || null, executionId: historicalWrapper.executionId, outcome: 'replay_failed', normalizedPhone: historicalPhone, attempts: upd.updateAttempts });
}

const summary = results.reduce((acc, item) => {
  acc.total += 1;
  acc[item.outcome] = (acc[item.outcome] || 0) + 1;
  return acc;
}, { total: 0 });

return [{ json: { summary, results, tokenExpiresAt: '2026-03-03T15:23:00Z', note: 'This temporary workflow depends on the embedded GHL browser token for smart-list access. Refresh the token in the Config node if it expires before the run.' } }];