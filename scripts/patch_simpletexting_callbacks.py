from __future__ import annotations

import json
from pathlib import Path

import requests


BASE = "https://automations.livetransparent.com/api/v1"
API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiYWUyNDg2MmUtZTUyZS00NWMwLWIzNWQtNjQ3ZGFiN2YyMjM1IiwiaWF0IjoxNzc0MzQ3MzE5LCJleHAiOjE3ODIxMTE2MDB9."
    "wC0h35JV_ZvN37pVeweKo-h7xnfy7QBclcmLB4X0lkw"
)
HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
}


inbound_js = r"""const src = $json || {};
const body = src.body || {};
const headers = src.headers || {};
const values = (body.values && typeof body.values === 'object' && !Array.isArray(body.values)) ? body.values : {};

const cfg = {
  defaultDryRun: !!src.defaultDryRun,
  authHeaderName: String(src.authHeaderName || 'x-lt-webhook-key').toLowerCase(),
  authHeaderValue: String(src.authHeaderValue || ''),
  provider: String(src.provider || 'SimpleTexting').trim(),
  eventType: String(src.eventType || 'inbound_reply').trim(),
  ghlLocationId: String(src.ghlLocationId || '').trim(),
  ghlApiBaseUrl: String(src.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, ''),
  ghlApiKey: String(src.ghlApiKey || '').trim(),
  tagOngoing: String(src.tagOngoing || 'simpletext_ongoing').trim(),
  tagStop: String(src.tagStop || 'simpletext_stop').trim(),
};

const incomingAuth = headers[cfg.authHeaderName] || headers[cfg.authHeaderName.toLowerCase()] || '';
if (cfg.authHeaderValue && incomingAuth !== cfg.authHeaderValue) {
  return [{ json: { ok: false, error: 'unauthorized', message: 'Invalid webhook auth header' } }];
}

function clean(v) { return String(v ?? '').trim(); }
function parseBoolean(v, fallback) {
  if (v === undefined || v === null || v === '') return fallback;
  if (typeof v === 'boolean') return v;
  const s = String(v).trim().toLowerCase();
  if (['true','1','yes','y'].includes(s)) return true;
  if (['false','0','no','n'].includes(s)) return false;
  return fallback;
}
function normalizePhone(v) {
  const digits = clean(v).replace(/\D/g, '');
  if (!digits) return '';
  if (digits.length === 11 && digits.startsWith('1')) return digits.slice(1);
  return digits;
}
function formatPhone(v) {
  const digits = normalizePhone(v);
  if (!digits) return '';
  if (digits.length === 10) return `+1 ${digits.slice(0,3)}-${digits.slice(3,6)}-${digits.slice(6)}`;
  return `+${digits}`;
}
function normalizeMediaItems(source) {
  const items = [];
  if (Array.isArray(source.mediaItems)) items.push(...source.mediaItems);
  if (Array.isArray(source.mediaUrls)) items.push(...source.mediaUrls);
  if (source.mediaUrl) items.push(source.mediaUrl);
  return items.map((item) => clean(item)).filter(Boolean);
}
function normalizeTagList(value) {
  if (Array.isArray(value)) return value.map((item) => clean(typeof item === 'string' ? item : item?.name || item?.value)).filter(Boolean);
  if (typeof value === 'string') return value.split(',').map((item) => clean(item)).filter(Boolean);
  return [];
}
function getContactsArray(data) {
  if (Array.isArray(data?.contacts)) return data.contacts;
  if (Array.isArray(data?.data?.contacts)) return data.data.contacts;
  return [];
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ method, url, headers, body }) {
  const options = { method, url, headers, json: true };
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
async function resolveGhlContact(phone, explicitGhlContactId) {
  if (explicitGhlContactId) return { contactId: explicitGhlContactId, resolvedVia: 'input_contactId' };
  if (!cfg.ghlApiKey || !cfg.ghlLocationId || !phone) return { contactId: '', resolvedVia: 'unavailable' };
  const lookup = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/?locationId=${encodeURIComponent(cfg.ghlLocationId)}&query=${encodeURIComponent(phone)}&limit=10`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
    },
  });
  if (!lookup.ok) return { contactId: '', resolvedVia: 'lookup_failed', details: lookup.data };
  const match = getContactsArray(lookup.data).find((contact) => normalizePhone(contact?.phone) === phone);
  if (!match?.id) return { contactId: '', resolvedVia: 'phone_lookup_no_match' };
  return { contactId: match.id, resolvedVia: 'phone_lookup', existingTags: normalizeTagList(match.tags || []) };
}
async function createGhlNote(contactId, noteBody) {
  return await apiRequest.call(this, {
    method: 'POST',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/notes`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { body: noteBody },
  });
}
async function addTags(contactId, tags) {
  const normalized = normalizeTagList(tags);
  if (!contactId || !normalized.length) return { attempted: false, ok: true, tags: normalized };
  return await apiRequest.call(this, {
    method: 'POST',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/tags`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { tags: normalized },
  });
}
async function removeTags(contactId, tags) {
  const normalized = normalizeTagList(tags);
  if (!contactId || !normalized.length) return { attempted: false, ok: true, tags: normalized };
  return await apiRequest.call(this, {
    method: 'DELETE',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/tags`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { tags: normalized },
  });
}

const dryRun = parseBoolean(body.dryRun, cfg.defaultDryRun);
const reportType = clean(body.type || body.reportType || values.type || 'INCOMING_MESSAGE');
const explicitGhlContactId = clean(body.ghlContactId || body.externalGhlContactId);
const from = normalizePhone(values.contactPhone || body.contactPhone || body.from || body.phone || body.mobile || body.senderPhone);
const to = normalizePhone(values.accountPhone || body.accountPhone || body.to || body.destination || body.number);
const message = clean(values.text || body.text || body.message || body.body || body.smsBody);
const subject = clean(values.subject || body.subject);
const mediaItems = normalizeMediaItems(values).length ? normalizeMediaItems(values) : normalizeMediaItems(body);
const providerMessageId = clean(values.messageId || body.messageId || body.message_id || body.id || body.smsid);
const providerContactId = clean(values.contactId || body.contactId);
const receivedAt = clean(values.timestamp || body.receivedAt || body.timestamp || body.createdAt || body.date || new Date().toISOString());
const category = clean(values.category || body.category);
const referenceType = clean(values.referenceType || body.referenceType);
const normalizedKeyword = message.toLowerCase().replace(/[^a-z]/g, '');
const unsubscribeKeyword = ['stop','stopall','unsubscribe','cancel','end','quit'].includes(normalizedKeyword);

if (!from) return [{ json: { ok: false, error: 'missing_from_phone', message: 'Provide values.contactPhone or a fallback from/phone field' } }];
if (!message && mediaItems.length === 0) return [{ json: { ok: false, error: 'missing_message', message: 'Provide values.text or mediaItems' } }];

const resolvedContact = await resolveGhlContact.call(this, from, explicitGhlContactId);
const noteBody = [
  unsubscribeKeyword ? 'SMS STOP reply received via SimpleTexting' : 'SMS reply received via SimpleTexting',
  `Received At: ${receivedAt}`,
  `From: ${formatPhone(from) || from}`,
  to ? `To: ${formatPhone(to) || to}` : '',
  providerMessageId ? `Provider Message ID: ${providerMessageId}` : '',
  providerContactId ? `Provider Contact ID: ${providerContactId}` : '',
  subject ? `Subject: ${subject}` : '',
  category ? `Category: ${category}` : '',
  referenceType ? `Reference Type: ${referenceType}` : '',
  unsubscribeKeyword ? 'Opt-Out: STOP keyword detected' : '',
  'Message:',
  message || '[media only reply]',
  mediaItems.length ? `Media Items: ${mediaItems.join(', ')}` : '',
].filter(Boolean).join('\n');

if (dryRun) {
  return [{ json: {
    ok: true,
    dryRun,
    provider: cfg.provider,
    eventType: cfg.eventType,
    reportType,
    from,
    to,
    message,
    subject,
    mediaItems,
    providerMessageId,
    providerContactId,
    receivedAt,
    category,
    referenceType,
    unsubscribeKeyword,
    ghlNotePreview: noteBody,
    ghlContactResolution: resolvedContact,
    requestedTagAdds: unsubscribeKeyword ? [cfg.tagStop] : [],
    requestedTagRemovals: unsubscribeKeyword ? [cfg.tagOngoing] : [],
    rawBody: body,
    rawValues: values,
    nextStep: 'draft_only_no_side_effects'
  } }];
}

let noteSync = { attempted: false, contactId: resolvedContact.contactId || '', resolvedVia: resolvedContact.resolvedVia || '', ok: false };
let tagSync = { attempted: false, contactId: resolvedContact.contactId || '', added: [], removed: [], addOk: false, removeOk: false };
if (cfg.ghlApiKey && cfg.ghlLocationId && resolvedContact.contactId) {
  const noteRes = await createGhlNote.call(this, resolvedContact.contactId, noteBody);
  noteSync.attempted = true;
  noteSync.ok = noteRes.ok;
  noteSync.details = noteRes.ok ? (noteRes.data?.note || noteRes.data || {}) : noteRes.data;

  if (unsubscribeKeyword) {
    tagSync.attempted = true;
    tagSync.added = [cfg.tagStop];
    tagSync.removed = [cfg.tagOngoing];
    const addRes = await addTags.call(this, resolvedContact.contactId, [cfg.tagStop]);
    tagSync.addOk = !!addRes.ok;
    tagSync.addDetails = addRes.ok ? (addRes.data?.contact || addRes.data || {}) : addRes.data;
    const removeRes = await removeTags.call(this, resolvedContact.contactId, [cfg.tagOngoing]);
    tagSync.removeOk = !!removeRes.ok;
    tagSync.removeDetails = removeRes.ok ? (removeRes.data?.contact || removeRes.data || {}) : removeRes.data;
  }
}

return [{ json: {
  ok: true,
  dryRun,
  provider: cfg.provider,
  eventType: cfg.eventType,
  reportType,
  from,
  to,
  message,
  subject,
  mediaItems,
  providerMessageId,
  providerContactId,
  receivedAt,
  category,
  referenceType,
  unsubscribeKeyword,
  ghlNoteSync: noteSync,
  ghlTagSync: tagSync,
  rawBody: body,
  rawValues: values,
  nextStep: unsubscribeKeyword ? 'reply_logged_and_contact_stopped' : (noteSync.ok ? 'reply_logged_to_ghl' : 'reply_logged_pending_manual_review')
} }];"""


delivery_js = r"""const src = $json || {};
const body = src.body || {};
const headers = src.headers || {};
const values = (body.values && typeof body.values === 'object' && !Array.isArray(body.values)) ? body.values : {};

const cfg = {
  defaultDryRun: !!src.defaultDryRun,
  authHeaderName: String(src.authHeaderName || 'x-lt-webhook-key').toLowerCase(),
  authHeaderValue: String(src.authHeaderValue || ''),
  provider: String(src.provider || 'SimpleTexting').trim(),
  eventType: String(src.eventType || 'delivery_event').trim(),
  ghlLocationId: String(src.ghlLocationId || '').trim(),
  ghlApiBaseUrl: String(src.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, ''),
  ghlApiKey: String(src.ghlApiKey || '').trim(),
};

const incomingAuth = headers[cfg.authHeaderName] || headers[cfg.authHeaderName.toLowerCase()] || '';
if (cfg.authHeaderValue && incomingAuth !== cfg.authHeaderValue) {
  return [{ json: { ok: false, error: 'unauthorized', message: 'Invalid webhook auth header' } }];
}

function clean(v) { return String(v ?? '').trim(); }
function parseBoolean(v, fallback) {
  if (v === undefined || v === null || v === '') return fallback;
  if (typeof v === 'boolean') return v;
  const s = String(v).trim().toLowerCase();
  if (['true','1','yes','y'].includes(s)) return true;
  if (['false','0','no','n'].includes(s)) return false;
  return fallback;
}
function normalizePhone(v) {
  const digits = clean(v).replace(/\D/g, '');
  if (!digits) return '';
  if (digits.length === 11 && digits.startsWith('1')) return digits.slice(1);
  return digits;
}
function formatPhone(v) {
  const digits = normalizePhone(v);
  if (!digits) return '';
  if (digits.length === 10) return `+1 ${digits.slice(0,3)}-${digits.slice(3,6)}-${digits.slice(6)}`;
  return `+${digits}`;
}
function getContactsArray(data) {
  if (Array.isArray(data?.contacts)) return data.contacts;
  if (Array.isArray(data?.data?.contacts)) return data.data.contacts;
  return [];
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ method, url, headers, body }) {
  const options = { method, url, headers, json: true };
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
async function resolveGhlContact(phone, explicitGhlContactId) {
  if (explicitGhlContactId) return { contactId: explicitGhlContactId, resolvedVia: 'input_contactId' };
  if (!cfg.ghlApiKey || !cfg.ghlLocationId || !phone) return { contactId: '', resolvedVia: 'unavailable' };
  const lookup = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/?locationId=${encodeURIComponent(cfg.ghlLocationId)}&query=${encodeURIComponent(phone)}&limit=10`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
    },
  });
  if (!lookup.ok) return { contactId: '', resolvedVia: 'lookup_failed', details: lookup.data };
  const match = getContactsArray(lookup.data).find((contact) => normalizePhone(contact?.phone) === phone);
  if (!match?.id) return { contactId: '', resolvedVia: 'phone_lookup_no_match' };
  return { contactId: match.id, resolvedVia: 'phone_lookup' };
}
async function createGhlNote(contactId, noteBody) {
  return await apiRequest.call(this, {
    method: 'POST',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/notes`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { body: noteBody },
  });
}

const dryRun = parseBoolean(body.dryRun, cfg.defaultDryRun);
const reportType = clean(body.type || body.reportType || values.type || 'DELIVERY_REPORT');
const rawStatus = clean(values.status || body.status || body.deliveryStatus || body.state || body.messageStatus).toLowerCase();
const normalizedStatus = rawStatus || (reportType === 'NON_DELIVERED_REPORT' ? 'non_delivered' : (reportType === 'DELIVERY_REPORT' ? 'delivered' : 'unknown'));
const providerMessageId = clean(values.messageId || body.messageId || body.message_id || body.id || body.smsid);
const to = normalizePhone(values.contactPhone || body.contactPhone || body.to || body.phone || body.mobile || body.destination);
const from = normalizePhone(values.accountPhone || body.accountPhone || body.from || body.senderPhone);
const eventAt = clean(values.timestamp || body.deliveredAt || body.timestamp || body.updatedAt || body.date || new Date().toISOString());
const carrier = clean(values.carrier || body.carrier);
const errorCode = clean(values.errorCode || body.errorCode || body.code || body.error_code);
const errorMessage = clean(values.errorMessage || body.errorMessage || body.error || body.reason);
const contactId = clean(values.contactId || body.contactId || body.ghlContactId || body.externalContactId);
const conversationKey = clean(body.conversationId || body.threadId || body.externalId || providerMessageId);
const category = clean(values.category || body.category);
const referenceType = clean(values.referenceType || body.referenceType);

if (!providerMessageId && !to) {
  return [{ json: { ok: false, error: 'missing_identifiers', message: 'Provide values.messageId or values.contactPhone' } }];
}

const resolvedContact = await resolveGhlContact.call(this, to, contactId);
const noteBody = [
  'SMS delivery event received via SimpleTexting',
  `Status: ${normalizedStatus}`,
  `Reported At: ${eventAt}`,
  providerMessageId ? `Provider Message ID: ${providerMessageId}` : '',
  to ? `To: ${formatPhone(to) || to}` : '',
  from ? `From: ${formatPhone(from) || from}` : '',
  carrier ? `Carrier: ${carrier}` : '',
  errorCode ? `Error Code: ${errorCode}` : '',
  errorMessage ? `Error Message: ${errorMessage}` : '',
  category ? `Category: ${category}` : '',
  referenceType ? `Reference Type: ${referenceType}` : '',
  conversationKey ? `Conversation Key: ${conversationKey}` : '',
].filter(Boolean).join('\n');

if (dryRun) {
  return [{ json: {
    ok: true,
    dryRun,
    provider: cfg.provider,
    eventType: cfg.eventType,
    reportType,
    normalizedStatus,
    providerMessageId,
    to,
    from,
    eventAt,
    carrier,
    errorCode,
    errorMessage,
    contactId,
    conversationKey,
    category,
    referenceType,
    ghlNotePreview: noteBody,
    ghlContactResolution: resolvedContact,
    rawBody: body,
    rawValues: values,
    nextStep: 'draft_only_no_side_effects'
  } }];
}

let noteSync = { attempted: false, contactId: resolvedContact.contactId || '', resolvedVia: resolvedContact.resolvedVia || '', ok: false };
if (cfg.ghlApiKey && cfg.ghlLocationId && resolvedContact.contactId) {
  const noteRes = await createGhlNote.call(this, resolvedContact.contactId, noteBody);
  noteSync.attempted = true;
  noteSync.ok = noteRes.ok;
  noteSync.details = noteRes.ok ? (noteRes.data?.note || noteRes.data || {}) : noteRes.data;
}

return [{ json: {
  ok: true,
  dryRun,
  provider: cfg.provider,
  eventType: cfg.eventType,
  reportType,
  normalizedStatus,
  providerMessageId,
  to,
  from,
  eventAt,
  carrier,
  errorCode,
  errorMessage,
  contactId,
  conversationKey,
  category,
  referenceType,
  ghlNoteSync: noteSync,
  rawBody: body,
  rawValues: values,
  nextStep: noteSync.ok ? 'delivery_event_logged_to_ghl' : 'delivery_event_pending_manual_review'
} }];"""


unsubscribe_js = r"""const src = $json || {};
const body = src.body || {};
const headers = src.headers || {};
const values = (body.values && typeof body.values === 'object' && !Array.isArray(body.values)) ? body.values : {};

const cfg = {
  defaultDryRun: !!src.defaultDryRun,
  authHeaderName: String(src.authHeaderName || 'x-lt-webhook-key').toLowerCase(),
  authHeaderValue: String(src.authHeaderValue || ''),
  provider: String(src.provider || 'SimpleTexting').trim(),
  eventType: String(src.eventType || 'unsubscribe_event').trim(),
  ghlLocationId: String(src.ghlLocationId || '').trim(),
  ghlApiBaseUrl: String(src.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, ''),
  ghlApiKey: String(src.ghlApiKey || '').trim(),
  tagOngoing: String(src.tagOngoing || 'simpletext_ongoing').trim(),
  tagStop: String(src.tagStop || 'simpletext_stop').trim(),
};

const incomingAuth = headers[cfg.authHeaderName] || headers[cfg.authHeaderName.toLowerCase()] || '';
if (cfg.authHeaderValue && incomingAuth !== cfg.authHeaderValue) {
  return [{ json: { ok: false, error: 'unauthorized', message: 'Invalid webhook auth header' } }];
}

function clean(v) { return String(v ?? '').trim(); }
function parseBoolean(v, fallback) {
  if (v === undefined || v === null || v === '') return fallback;
  if (typeof v === 'boolean') return v;
  const s = String(v).trim().toLowerCase();
  if (['true','1','yes','y'].includes(s)) return true;
  if (['false','0','no','n'].includes(s)) return false;
  return fallback;
}
function normalizePhone(v) {
  const digits = clean(v).replace(/\D/g, '');
  if (!digits) return '';
  if (digits.length === 11 && digits.startsWith('1')) return digits.slice(1);
  return digits;
}
function formatPhone(v) {
  const digits = normalizePhone(v);
  if (!digits) return '';
  if (digits.length === 10) return `+1 ${digits.slice(0,3)}-${digits.slice(3,6)}-${digits.slice(6)}`;
  return `+${digits}`;
}
function normalizeTagList(value) {
  if (Array.isArray(value)) return value.map((item) => clean(typeof item === 'string' ? item : item?.name || item?.value)).filter(Boolean);
  if (typeof value === 'string') return value.split(',').map((item) => clean(item)).filter(Boolean);
  return [];
}
function getContactsArray(data) {
  if (Array.isArray(data?.contacts)) return data.contacts;
  if (Array.isArray(data?.data?.contacts)) return data.data.contacts;
  return [];
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ method, url, headers, body }) {
  const options = { method, url, headers, json: true };
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
async function resolveGhlContact(phone, explicitGhlContactId) {
  if (explicitGhlContactId) return { contactId: explicitGhlContactId, resolvedVia: 'input_contactId' };
  if (!cfg.ghlApiKey || !cfg.ghlLocationId || !phone) return { contactId: '', resolvedVia: 'unavailable' };
  const lookup = await apiRequest.call(this, {
    method: 'GET',
    url: `${cfg.ghlApiBaseUrl}/contacts/?locationId=${encodeURIComponent(cfg.ghlLocationId)}&query=${encodeURIComponent(phone)}&limit=10`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
    },
  });
  if (!lookup.ok) return { contactId: '', resolvedVia: 'lookup_failed', details: lookup.data };
  const match = getContactsArray(lookup.data).find((contact) => normalizePhone(contact?.phone) === phone);
  if (!match?.id) return { contactId: '', resolvedVia: 'phone_lookup_no_match' };
  return { contactId: match.id, resolvedVia: 'phone_lookup', existingTags: normalizeTagList(match.tags || []) };
}
async function createGhlNote(contactId, noteBody) {
  return await apiRequest.call(this, {
    method: 'POST',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/notes`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { body: noteBody },
  });
}
async function addTags(contactId, tags) {
  const normalized = normalizeTagList(tags);
  if (!contactId || !normalized.length) return { attempted: false, ok: true, tags: normalized };
  return await apiRequest.call(this, {
    method: 'POST',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/tags`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { tags: normalized },
  });
}
async function removeTags(contactId, tags) {
  const normalized = normalizeTagList(tags);
  if (!contactId || !normalized.length) return { attempted: false, ok: true, tags: normalized };
  return await apiRequest.call(this, {
    method: 'DELETE',
    url: `${cfg.ghlApiBaseUrl}/contacts/${encodeURIComponent(contactId)}/tags`,
    headers: {
      Authorization: `Bearer ${cfg.ghlApiKey}`,
      Version: '2021-07-28',
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: { tags: normalized },
  });
}

const dryRun = parseBoolean(body.dryRun, cfg.defaultDryRun);
const reportType = clean(body.type || body.reportType || values.type || 'UNSUBSCRIBE_REPORT');
const phone = normalizePhone(values.phone || values.contactPhone || body.phone || body.mobile || body.from || body.contactPhone);
const keyword = clean(values.keyword || body.keyword || body.reply || body.reason || 'STOP').toUpperCase();
const unsubscribedAt = clean(values.timestamp || body.unsubscribedAt || body.timestamp || body.createdAt || body.date || new Date().toISOString());
const contactId = clean(values.contactId || body.contactId || body.ghlContactId || body.externalContactId);
const sourceCampaign = clean(values.campaignKey || body.campaignKey || body.sequenceKey || body.list || body.keywordGroup);
const accountPhone = normalizePhone(values.accountPhone || body.accountPhone || body.to || body.number);

if (!phone) {
  return [{ json: { ok: false, error: 'missing_phone', message: 'Provide values.phone or a fallback phone field' } }];
}

const resolvedContact = await resolveGhlContact.call(this, phone, contactId);
const noteBody = [
  'SMS unsubscribe received via SimpleTexting',
  `Unsubscribed At: ${unsubscribedAt}`,
  `From: ${formatPhone(phone) || phone}`,
  accountPhone ? `To: ${formatPhone(accountPhone) || accountPhone}` : '',
  `Keyword: ${keyword || 'STOP'}`,
  sourceCampaign ? `Source Campaign: ${sourceCampaign}` : '',
  `Report Type: ${reportType}`,
].filter(Boolean).join('\n');

if (dryRun) {
  return [{ json: {
    ok: true,
    dryRun,
    provider: cfg.provider,
    eventType: cfg.eventType,
    reportType,
    phone,
    keyword,
    unsubscribedAt,
    contactId,
    sourceCampaign,
    accountPhone,
    ghlNotePreview: noteBody,
    ghlContactResolution: resolvedContact,
    requestedTagAdds: [cfg.tagStop],
    requestedTagRemovals: [cfg.tagOngoing],
    rawBody: body,
    rawValues: values,
    nextStep: 'draft_only_no_side_effects'
  } }];
}

let noteSync = { attempted: false, contactId: resolvedContact.contactId || '', resolvedVia: resolvedContact.resolvedVia || '', ok: false };
let tagSync = { attempted: false, contactId: resolvedContact.contactId || '', added: [], removed: [], addOk: false, removeOk: false };
if (cfg.ghlApiKey && cfg.ghlLocationId && resolvedContact.contactId) {
  const noteRes = await createGhlNote.call(this, resolvedContact.contactId, noteBody);
  noteSync.attempted = true;
  noteSync.ok = noteRes.ok;
  noteSync.details = noteRes.ok ? (noteRes.data?.note || noteRes.data || {}) : noteRes.data;

  tagSync.attempted = true;
  tagSync.added = [cfg.tagStop];
  tagSync.removed = [cfg.tagOngoing];
  const addRes = await addTags.call(this, resolvedContact.contactId, [cfg.tagStop]);
  tagSync.addOk = !!addRes.ok;
  tagSync.addDetails = addRes.ok ? (addRes.data?.contact || addRes.data || {}) : addRes.data;
  const removeRes = await removeTags.call(this, resolvedContact.contactId, [cfg.tagOngoing]);
  tagSync.removeOk = !!removeRes.ok;
  tagSync.removeDetails = removeRes.ok ? (removeRes.data?.contact || removeRes.data || {}) : removeRes.data;
}

return [{ json: {
  ok: true,
  dryRun,
  provider: cfg.provider,
  eventType: cfg.eventType,
  reportType,
  phone,
  keyword,
  unsubscribedAt,
  contactId,
  sourceCampaign,
  accountPhone,
  ghlNoteSync: noteSync,
  ghlTagSync: tagSync,
  rawBody: body,
  rawValues: values,
  nextStep: noteSync.ok ? 'unsubscribe_logged_and_contact_stopped' : 'unsubscribe_pending_manual_review'
} }];"""


def put_workflow(workflow_id: str, modify_fn) -> None:
    response = requests.get(f"{BASE}/workflows/{workflow_id}", headers=HEADERS, timeout=60)
    response.raise_for_status()
    workflow = response.json()
    body = {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": {},
    }
    modify_fn(body)
    update = requests.put(
        f"{BASE}/workflows/{workflow_id}",
        headers=HEADERS,
        data=json.dumps(body),
        timeout=60,
    )
    print(workflow_id, update.status_code)
    print(update.text[:500])
    update.raise_for_status()


def modify_inbound(body: dict) -> None:
    for node in body["nodes"]:
        if node["id"] == "config":
            for assignment in node["parameters"]["assignments"]["assignments"]:
                if assignment["name"] == "defaultDryRun":
                    assignment["value"] = False
        if node["id"] == "normalize":
            node["parameters"]["jsCode"] = inbound_js


def modify_delivery(body: dict) -> None:
    for node in body["nodes"]:
        if node["id"] == "config":
            assignments = node["parameters"]["assignments"]["assignments"]
            by_name = {item["name"]: item for item in assignments}
            by_name["defaultDryRun"]["value"] = False
            extras = [
                ("ghlLocationId", "string", "Zwz4relUXVPxx8uohnjV"),
                ("ghlApiBaseUrl", "string", "https://services.leadconnectorhq.com"),
                ("ghlApiKey", "string", "pit-8a0de81d-3555-4909-a8eb-afecd3794828"),
            ]
            for name, typ, value in extras:
                if name not in by_name:
                    assignments.append({"id": name, "name": name, "type": typ, "value": value})
                else:
                    by_name[name]["value"] = value
        if node["id"] == "normalize":
            node["parameters"]["jsCode"] = delivery_js


def modify_unsubscribe(body: dict) -> None:
    for node in body["nodes"]:
        if node["id"] == "config":
            assignments = node["parameters"]["assignments"]["assignments"]
            by_name = {item["name"]: item for item in assignments}
            by_name["defaultDryRun"]["value"] = False
            extras = [
                ("ghlLocationId", "string", "Zwz4relUXVPxx8uohnjV"),
                ("ghlApiBaseUrl", "string", "https://services.leadconnectorhq.com"),
                ("ghlApiKey", "string", "pit-8a0de81d-3555-4909-a8eb-afecd3794828"),
                ("tagOngoing", "string", "simpletext_ongoing"),
                ("tagStop", "string", "simpletext_stop"),
            ]
            for name, typ, value in extras:
                if name not in by_name:
                    assignments.append({"id": name, "name": name, "type": typ, "value": value})
                else:
                    by_name[name]["value"] = value
        if node["id"] == "normalize":
            node["parameters"]["jsCode"] = unsubscribe_js


if __name__ == "__main__":
    put_workflow("EhAiGey2o7UJT1cv", modify_inbound)
    put_workflow("AEi1VCzkLvaYFr4U", modify_delivery)
    put_workflow("IyBKMkpYQ7pa0C8V", modify_unsubscribe)
