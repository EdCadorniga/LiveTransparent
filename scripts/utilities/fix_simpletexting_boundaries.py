"""Harden the live SimpleTexting send boundaries without sending messages."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = REPO_ROOT / "local-archive" / "n8n" / "workflows"
SEND_WORKFLOW_ID = "Q3Ivnwe4z2Y3cD7A"
PROVIDER_WORKFLOW_ID = "f4VoO1lBWkYRcQai"
IDEMPOTENT_WORKFLOW_ID = "gwaEpWDpTIwsafi8"
CALLBACK_WORKFLOWS = {
    "i0pROHpFtN4LYR0Q": "Validate + Normalize Reply",
    "AEi1VCzkLvaYFr4U": "Validate + Normalize Delivery",
    "IyBKMkpYQ7pa0C8V": "Validate + Normalize Unsubscribe",
}
SAFE_SCHEDULES = {
    "dUyOfxllvkxZavaw": "dryRun",
    "dZQLlbTLkpE1843X": "defaultDryRun",
    "usxYXSuc4ahw40V3": "defaultDryRun",
}
ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
}


TEMPLATES = {
    "john_sms1": "Hi, Jason from Transparent eCom, just gave you a call. Saw you were interested in learning about ads for regulated industries on social/search.\n\nWe run ads for Mood, Cookies, and more! Interested in learning how?",
    "john_sms2": "Hey {{first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?\n\nI can show you how top regulated-industry brands are doing it in 10 mins.",
    "john_sms3": "Hi {{first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?",
    "john_sms4": "Hi {{first_name}} - last follow-up on ads for regulated industries. Is it timing, or is there a better contact?",
    "john_sms5": "Good chatting about ads for regulated industries earlier - based on what you shared, this looks like a strong fit.\n\nWe're onboarding a few brands this month - grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}",
    "sms_1": "Hi - thanks for checking out regulated ads on social/search.\n\nI'm Cameron, founder of Transparent eCom. We help regulated brands run ads that most agencies can't, including Mood, Cookies, and Lucy.\n\nYou can learn more at https://livetransparent.com/\n\nAre you currently running ads, restricted from advertising, or just exploring options?",
    "sms_2": "Hey, Cameron again.\nIf you're curious, our site has free walkthroughs on how brands run ads in regulated industries on platforms like Meta and Google.\nSome companies do it themselves - totally fine. But we also have a few capabilities most brands and agencies don't that allow actual product advertising at scale.\nWant me to send it over?",
    "sms_3": "Quick follow-up -\n\nWe've helped brands like Mood, Lucy, and GPen scale ads profitably in regulated spaces.\n\nWould it be helpful if I showed you what has worked for them?",
    "sms_4": "Fun fact:\nWe can run product ads with regulated-industry mentions directly in the ad.\nWould you like me to send a short overview?",
    "sms_5": "If you're a dispensary, this might be interesting:\n\nWe help dispensaries connect digital ad activity to in-store purchases, so they can measure actual ROI from social and search campaigns.\n\nMore details are available at https://livetransparent.com/\n\nShould I send over a quick example?",
    "sms_6": "Hey - Cameron again.\nI don't want to keep bothering you, so this will be my last message.\nIf you ever want to learn how brands are running regulated ads on social/search, just reply here and I'm happy to help.",
    "emerald_mso_executive_intro": "Hi {{first_name}}, Cameron from Transparent eCom. Most regulated-industry brands still cannot properly run Meta ads - we help teams get live through compliant accounts and keep them running without constant restrictions. Let me know if this is relevant.",
    "emerald_mso_marketing_intro": "Hi {{first_name}}, Cameron from Transparent eCom. Most teams still cannot fully run paid social - we help marketing teams get live and keep campaigns running without disruption. Let me know if this is relevant.",
    "emerald_mso_finance_intro": "Hi {{first_name}}, Cameron from Transparent eCom. Many still cannot fully use paid social as a revenue channel - we help teams unlock and maintain it reliably. Let me know if this is relevant.",
    "emerald_mso_retail_sales_intro": "Hi {{first_name}}, Cameron from Transparent eCom. When Meta ads go down, traffic and sales usually drop too - we help teams get live and keep things running without constant restrictions. Let me know if this is relevant.",
    "emerald_sso_executive_intro": "Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where teams have to reset more often than they should when ads get interrupted. Let me know if this sounds familiar.",
    "emerald_sso_marketing_intro": "Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where campaigns get interrupted mid-execution, causing teams to lose momentum. Let me know if this sounds familiar.",
    "emerald_sso_finance_intro": "Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where revenue becomes uneven when advertising gets interrupted. Let me know if this sounds familiar.",
    "emerald_sso_retail_sales_intro": "Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where interruptions in advertising quietly create gaps in traffic and conversions. Let me know if this is something you have noticed.",
}


SEND_CODE = r"""const src = $json || {};
const cfg = src;
const clean = (value) => String(value ?? '').trim();
const stripQuotes = (value) => { if (typeof value !== 'string') return value; const text = value.trim(); return text.length >= 2 && text.startsWith('"') && text.endsWith('"') ? text.slice(1, -1) : text; };
const cleanObject = (value) => {
  let source = value;
  if (!source) return {};
  if (typeof source === 'string') { try { source = JSON.parse(source); } catch { return {}; } }
  if (!source || typeof source !== 'object' || Array.isArray(source)) return {};
  return Object.fromEntries(Object.entries(source).map(([key, item]) => [stripQuotes(key), stripQuotes(item)]));
};
const parseBoolean = (value, fallback) => {
  if (value === undefined || value === null || value === '') return fallback;
  if (typeof value === 'boolean') return value;
  return ['true', '1', 'yes', 'on'].includes(clean(value).toLowerCase());
};
const parseList = (value) => {
  if (Array.isArray(value)) return value.map(clean).filter(Boolean);
  if (typeof value !== 'string' || !value.trim()) return [];
  try { const parsed = JSON.parse(value); if (Array.isArray(parsed)) return parsed.map(clean).filter(Boolean); } catch {}
  return value.split(',').map(clean).filter(Boolean);
};
const mediaCandidates = (value) => {
  if (Array.isArray(value)) return value;
  if (value === undefined || value === null || value === '') return [];
  if (typeof value === 'string') {
    try { const parsed = JSON.parse(value); if (Array.isArray(parsed)) return parsed; } catch {}
    return [value];
  }
  return [value];
};
const mediaUrl = (value) => {
  if (typeof value === 'string') return clean(value);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
  return clean(value.url || value.downloadUrl || value.mediaUrl || value.href || value.src);
};
const validMediaUrl = (value) => value.length <= 2048 && /^https?:\/\/[^\s/@]+(?:[/?#][^\s]*)?$/i.test(value);
const normalizePhone = (value) => {
  const digits = clean(value).replace(/\D/g, '');
  if (digits.length === 10) return { digits, e164: `+1${digits}` };
  if (digits.length === 11 && digits.startsWith('1')) return { digits: digits.slice(1), e164: `+${digits}` };
  return { digits: '', e164: '' };
};
const http = async (options) => {
  try { return { ok: true, data: await this.helpers.httpRequest({ ...options, json: true }) }; }
  catch (error) { return { ok: false, status: error?.statusCode || error?.httpCode || error?.status || 500, data: error?.response?.body || error?.response?.data || error?.message || String(error) }; }
};

const headers = Object.fromEntries(Object.entries(src.headers || {}).map(([key, value]) => [clean(key).toLowerCase(), clean(value)]));
const expectedKey = clean(cfg.authHeaderValue);
const suppliedKey = headers['x-lt-simpletexting-key'] || '';
const suppliedLegacyKey = headers['x-lt-webhook-key'] || '';
const legacyExpectedKey = clean(cfg.legacyAuthHeaderValue);
const authorized = !!expectedKey && (suppliedKey === expectedKey || (!!legacyExpectedKey && suppliedLegacyKey === legacyExpectedKey));
if (!authorized) return [{ json: { ok: false, error: 'unauthorized' } }];

const envelope = cleanObject(src.body && typeof src.body === 'object' ? src.body : src);
const customData = cleanObject(envelope.customData || src.customData);
const body = { ...envelope, ...customData };
const nestedContact = cleanObject(body.contact);
const contactId = clean(body.contactId || body.contact_id || body.ghlContactId);
const phone = normalizePhone(body.contactPhone || body.phone || body.to || nestedContact.phone);
const templateKey = clean(body.templateKey || body.template_key || body.template);
const source = clean(body.source || 'ghl_workflow');
const dryRun = parseBoolean(body.dryRun ?? body.dry_run, parseBoolean(cfg.defaultDryRun, true));
const firstName = clean(body.first_name || body.firstName || nestedContact.first_name || nestedContact.firstName);
const triggerLinks = cleanObject(body.trigger_link || body.triggerLink);
const tagsToAdd = parseList(body.addTags || body.add_tags);
const mediaRaw = body.mediaItems ?? body.media_items ?? body.attachments ?? body.mediaUrls ?? body.mediaUrl;
const mediaValues = mediaCandidates(mediaRaw);
const normalizedMediaValues = mediaValues.map(mediaUrl);
if (normalizedMediaValues.some((url) => !validMediaUrl(url))) return [{ json: { ok: false, error: 'invalid_attachment_url', contactId } }];
if (normalizedMediaValues.length > 1) return [{ json: { ok: false, error: 'multiple_attachments_unsupported', contactId, attachmentCount: normalizedMediaValues.length } }];
const mediaItems = normalizedMediaValues;
const requestedMode = clean(body.mode || body.sendMode || body.send_mode).toUpperCase();
const validModes = new Set(['AUTO', 'SINGLE_SMS_STRICTLY', 'MMS_PREFERRED']);
if (requestedMode && !validModes.has(requestedMode)) return [{ json: { ok: false, error: 'invalid_send_mode', mode: requestedMode } }];
const mode = mediaItems.length ? 'MMS_PREFERRED' : (requestedMode || clean(cfg.defaultSendMode || 'AUTO').toUpperCase());
const requestedFallbackText = clean(body.fallbackText || body.fallback_text || body.mmsFallbackText);
if (!contactId) return [{ json: { ok: false, error: 'missing_contact_id' } }];
if (!phone.e164) return [{ json: { ok: false, error: 'invalid_phone', contactId } }];

let registry = {};
try { registry = JSON.parse(clean(cfg.templateRegistryJson || '{}') || '{}'); }
catch { return [{ json: { ok: false, error: 'invalid_template_registry' } }]; }
const entry = registry[templateKey];
let text = clean(body.text || body.message || body.message_body || body.smsBody || (entry && entry.message));
if (!text && !mediaItems.length) return [{ json: { ok: false, error: templateKey ? 'unknown_template_key' : 'missing_text', templateKey } }];
text = text
  .replace(/\{\{\s*(?:contact\.)?first_name\s*\}\}/gi, firstName)
  .replace(/\{\{\s*trigger_link\.nqLFBlEsdm7qccr8Yyog\s*\}\}/gi, clean(triggerLinks.nqLFBlEsdm7qccr8Yyog || body.bookingUrl));
if (/\{\{[^}]+\}\}/.test(text)) return [{ json: { ok: false, error: 'unresolved_merge_field', templateKey } }];
const fallbackText = requestedFallbackText || (mediaItems.length ? [text, ...mediaItems].filter(Boolean).join('\n') : '');

if (!dryRun && parseBoolean(cfg.enforceBusinessHours, true)) {
  const timeZone = clean(cfg.businessTimezone || 'America/New_York');
  const parts = new Intl.DateTimeFormat('en-US', { timeZone, weekday: 'short', hour: '2-digit', hour12: false }).formatToParts(new Date());
  const local = Object.fromEntries(parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]));
  const dayMap = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  const allowedDays = new Set(clean(cfg.businessDaysCsv || '1,2,3,4,5').split(',').map(Number));
  const hour = Number(local.hour) % 24;
  if (!allowedDays.has(dayMap[local.weekday]) || hour < Number(cfg.businessStartHour ?? 10) || hour >= Number(cfg.businessEndHour ?? 17)) {
    return [{ json: { ok: false, error: 'outside_business_hours', contactId, contactPhone: phone.digits, templateKey } }];
  }
}

const ghlBase = clean(cfg.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, '');
const ghlHeaders = { Authorization: `Bearer ${clean(cfg.ghlApiKey)}`, Version: '2021-07-28', Accept: 'application/json', 'Content-Type': 'application/json' };
if (!dryRun) {
  const lookup = await http({ method: 'GET', url: `${ghlBase}/contacts/${encodeURIComponent(contactId)}`, headers: ghlHeaders });
  if (!lookup.ok) return [{ json: { ok: false, error: 'ghl_contact_lookup_failed', statusCode: lookup.status, details: lookup.data, contactId } }];
  const contact = lookup.data?.contact || lookup.data || {};
  const tags = (Array.isArray(contact.tags) ? contact.tags : []).map((tag) => clean(tag).toLowerCase());
  const hardBlocks = new Set([clean(cfg.tagStop).toLowerCase(), 'do not contact', 'do not nurture', 'unsubscribed', 'opted out']);
  if (contact.dnd === true || tags.some((tag) => hardBlocks.has(tag))) return [{ json: { ok: false, error: 'contact_opted_out', contactId, contactPhone: phone.digits } }];
  if (source !== 'ghl_workflow' && tags.includes(clean(cfg.tagReplied).toLowerCase())) return [{ json: { ok: false, error: 'contact_replied', contactId, contactPhone: phone.digits } }];
}

if (dryRun) return [{ json: { ok: true, dryRun: true, action: 'would_send_message', contactId, contactPhone: phone.digits, normalizedPhone: phone.e164, templateKey, message: text, mediaItems, mode, fallbackText } }];
const send = await http({ method: 'POST', url: 'https://automations.livetransparent.com/webhook/lt-sms-send', headers: { 'Content-Type': 'application/json', 'x-lt-simpletexting-key': clean(cfg.internalSendHeaderValue) }, body: { contact_id: contactId, phone: phone.e164, workflow_id: 'Q3Ivnwe4z2Y3cD7A', template_id: templateKey, message_body: text, media_items: mediaItems, mode, fallback_text: fallbackText, simulate: false } });
if (!send.ok) return [{ json: { ok: false, error: 'idempotent_webhook_error', details: send.data } }];
const result = send.data || {};
if (clean(result.status).toLowerCase() === 'duplicate') return [{ json: { ok: false, error: 'duplicate_send', sent_at: result.sent_at || null } }];
const providerResponse = result.provider_response || result;
const providerError = result.error || providerResponse?.error || '';
const deliveryMode = clean(result.delivery_mode || providerResponse?.deliveryMode || (mediaItems.length ? 'MMS' : 'SMS'));
const fallbackUsed = result.fallback_used === true || providerResponse?.fallbackUsed === true;
const providerMessageId = clean(providerResponse?.id || providerResponse?.messageId || providerResponse?.fallbackProviderResponse?.id || providerResponse?.fallbackProviderResponse?.messageId || result.providerMessageId);
if (providerError || clean(result.status).toLowerCase() === 'error' || !providerMessageId) return [{ json: { ok: false, error: 'simpletext_provider_failed', message: providerError || 'No provider message ID returned', providerResponse, providerMessageId: '' } }];

let tagSync = { attempted: false, ok: true };
let noteSync = { attempted: false, ok: true };
if (tagsToAdd.length) {
  const tagResult = await http({ method: 'POST', url: `${ghlBase}/contacts/${encodeURIComponent(contactId)}/tags`, headers: ghlHeaders, body: { tags: tagsToAdd } });
  tagSync = { attempted: true, ok: tagResult.ok, details: tagResult.ok ? undefined : tagResult.data };
}
const note = [`${deliveryMode || 'SMS'} sent via SimpleTexting${fallbackUsed ? ' (MMS rejected; link fallback used)' : ''}`, `To: ${phone.e164}`, `Provider Message ID: ${providerMessageId}`, templateKey ? `Template: ${templateKey}` : '', mediaItems.length ? `Media URL: ${mediaItems[0]}` : '', 'Message:', text].filter(Boolean).join('\n');
const noteResult = await http({ method: 'POST', url: `${ghlBase}/contacts/${encodeURIComponent(contactId)}/notes`, headers: ghlHeaders, body: { body: note } });
noteSync = { attempted: true, ok: noteResult.ok, details: noteResult.ok ? undefined : noteResult.data };
return [{ json: { ok: true, action: 'message_sent', provider: 'SimpleTexting', contactId, contactPhone: phone.digits, normalizedPhone: phone.e164, templateKey, message: text, source, mediaItems, mode, deliveryMode, fallbackUsed, providerResponse, providerMessageId, ghlTagSync: tagSync, ghlNoteSync: noteSync } }];"""


PROVIDER_PROCESS_CODE = r"""const cfg = $('Config').item.json || {};
const body = $('POST - GHL Provider Outbound').item.json.body || {};
const clean = (value) => String(value ?? '').trim();
const contactId = clean(body.contactId || body.contact_id);
const message = clean(body.message || body.text || body.body);
const providerId = clean(body.conversationProviderId || body.providerId || body.provider_id);
const digits = clean(body.phone || body.to || body.contactPhone).replace(/\D/g, '');
const normalizedPhone = digits.length === 10 ? `+1${digits}` : (digits.length === 11 && digits.startsWith('1') ? `+${digits}` : '');
const mediaCandidates = (value) => {
  if (Array.isArray(value)) return value;
  if (value === undefined || value === null || value === '') return [];
  if (typeof value === 'string') {
    try { const parsed = JSON.parse(value); if (Array.isArray(parsed)) return parsed; } catch {}
    return [value];
  }
  return [value];
};
const mediaUrl = (value) => {
  if (typeof value === 'string') return clean(value);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
  return clean(value.url || value.downloadUrl || value.mediaUrl || value.href || value.src);
};
const validMediaUrl = (value) => value.length <= 2048 && /^https?:\/\/[^\s/@]+(?:[/?#][^\s]*)?$/i.test(value);
const mediaValues = mediaCandidates(body.attachments || body.mediaItems || body.media_items || body.mediaUrls || body.mediaUrl);
const normalizedMediaValues = mediaValues.map(mediaUrl);
const mediaItems = normalizedMediaValues.filter(Boolean);
const invalidAttachment = normalizedMediaValues.some((url) => !validMediaUrl(url));
const requestedMode = clean(body.mode || body.sendMode || body.send_mode).toUpperCase();
const validModes = new Set(['AUTO', 'SINGLE_SMS_STRICTLY', 'MMS_PREFERRED']);
const mode = mediaItems.length ? 'MMS_PREFERRED' : (requestedMode || 'AUTO');
const fallbackText = clean(body.fallbackText || body.fallback_text || body.mmsFallbackText) || (mediaItems.length ? [message, ...mediaItems].filter(Boolean).join('\n') : '');
const result = { routed: false, accepted: false, duplicate: false, contact_id: contactId, normalized_phone: normalizedPhone, media_items: mediaItems, mode, error: '', step: '' };
if (!clean(cfg.providerId) || providerId !== clean(cfg.providerId)) { result.step = 'validate_provider'; result.error = 'invalid_provider'; return [{ json: { routing: result } }]; }
if (!contactId || (!message && !mediaItems.length) || !normalizedPhone || invalidAttachment || mediaItems.length > 1 || (requestedMode && !validModes.has(requestedMode))) { result.step = 'validate_input'; result.error = invalidAttachment ? 'invalid_attachment_url' : (mediaItems.length > 1 ? 'multiple_attachments_unsupported' : (requestedMode && !validModes.has(requestedMode) ? 'invalid_send_mode' : 'missing_required_fields')); return [{ json: { routing: result } }]; }
try {
  const response = await this.helpers.httpRequest({
    method: 'GET',
    url: `${clean(cfg.ghlApiBaseUrl).replace(/\/$/, '')}/contacts/${encodeURIComponent(contactId)}`,
    headers: { Authorization: `Bearer ${clean(cfg.ghlApiKey)}`, Version: '2021-07-28', Accept: 'application/json' },
    json: true,
  });
  const contact = response?.contact || response || {};
  const tags = (Array.isArray(contact.tags) ? contact.tags : []).map((tag) => clean(tag).toLowerCase());
  if (contact.dnd === true || tags.includes('simpletext_stop')) { result.step = 'contact_opted_out'; result.error = 'contact_opted_out'; return [{ json: { routing: result } }]; }
} catch (error) {
  result.step = 'ghl_contact_lookup_failed';
  result.error = clean(error?.message || error).slice(0, 300);
  return [{ json: { routing: result } }];
}
try {
  const sendResponse = await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://automations.livetransparent.com/webhook/lt-sms-send',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'x-lt-simpletexting-key': clean(cfg.internalSendHeaderValue) },
    body: { contact_id: contactId, phone: normalizedPhone, workflow_id: 'Q3Ivnwe4z2Y3cD7A', message_body: message, media_items: mediaItems, mode, fallback_text: fallbackText, simulate: false },
    json: true,
    timeout: 15000,
  });
  const status = clean(sendResponse?.status).toLowerCase();
  result.duplicate = status === 'duplicate';
  result.routed = status === 'sent' || result.duplicate;
  result.accepted = result.routed;
  result.step = status === 'sent' ? 'sent' : (result.duplicate ? 'duplicate_accepted' : 'idempotent_blocked');
  result.error = result.routed ? '' : clean(sendResponse?.error || 'provider_send_failed');
  result.provider_message_id = clean(sendResponse?.provider_response?.id || sendResponse?.provider_response?.messageId || sendResponse?.provider_response?.fallbackProviderResponse?.id || sendResponse?.provider_response?.fallbackProviderResponse?.messageId);
  result.delivery_mode = clean(sendResponse?.delivery_mode || sendResponse?.provider_response?.deliveryMode || (mediaItems.length ? 'MMS' : 'SMS'));
  result.fallback_used = sendResponse?.fallback_used === true || sendResponse?.provider_response?.fallbackUsed === true;
  result.idempotent_response = sendResponse;
} catch (error) {
  result.step = 'idempotent_failed';
  result.error = clean(error?.message || error);
}
return [{ json: { routing: result } }];"""


IDEMPOTENT_PREPARE_CODE = r"""const src = $json || {};
const body = (src.body && typeof src.body === 'object') ? src.body : src;
const incomingHeaders = src.headers || {};
const expectedWebhookKey = __EXPECTED_WEBHOOK_KEY__;
const incomingWebhookKey = String(incomingHeaders['x-lt-simpletexting-key'] || incomingHeaders['X-LT-SimpleTexting-Key'] || '').trim();
if (!expectedWebhookKey || incomingWebhookKey !== expectedWebhookKey) return [{ json: { authRejected: true } }];
const contact_id = String(body.contact_id || '').trim();
const digits = String(body.phone || '').replace(/\D/g, '');
const phone = digits.length === 10 ? `+1${digits}` : (digits.length === 11 && digits.startsWith('1') ? `+${digits}` : '');
const workflow_id = String(body.workflow_id || '').trim();
const template_id = String(body.template_id || '').trim();
const message_body = String(body.message_body || '').trim();
const mediaCandidates = (value) => {
  if (Array.isArray(value)) return value;
  if (value === undefined || value === null || value === '') return [];
  if (typeof value === 'string') {
    try { const parsed = JSON.parse(value); if (Array.isArray(parsed)) return parsed; } catch {}
    return [value];
  }
  return [value];
};
const mediaUrl = (value) => {
  if (typeof value === 'string') return String(value).trim();
  if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
  return String(value.url || value.downloadUrl || value.mediaUrl || value.href || value.src || '').trim();
};
const validMediaUrl = (value) => value.length <= 2048 && /^https?:\/\/[^\s/@]+(?:[/?#][^\s]*)?$/i.test(value);
const mediaValues = mediaCandidates(body.media_items || body.mediaItems || body.attachments || body.mediaUrl);
const normalizedMediaValues = mediaValues.map(mediaUrl);
const mediaItems = normalizedMediaValues.filter(Boolean);
const invalidAttachment = normalizedMediaValues.some((url) => !validMediaUrl(url));
const requestedMode = String(body.mode || body.sendMode || body.send_mode || '').trim().toUpperCase();
const validModes = new Set(['AUTO', 'SINGLE_SMS_STRICTLY', 'MMS_PREFERRED']);
const mode = mediaItems.length ? 'MMS_PREFERRED' : (requestedMode || 'AUTO');
const fallback_text = String(body.fallback_text || body.fallbackText || body.mmsFallbackText || '').trim() || (mediaItems.length ? [message_body, ...mediaItems].filter(Boolean).join('\n') : '');
const parseBoolean = (value, fallback) => {
  if (value === undefined || value === null || value === '') return fallback;
  if (typeof value === 'boolean') return value;
  return ['true', '1', 'yes', 'on'].includes(String(value).trim().toLowerCase());
};
const simulate = parseBoolean(body.simulate, true);
const validationError = !contact_id ? 'missing_contact_id' : (!phone ? 'invalid_phone' : (!workflow_id ? 'missing_workflow_id' : ((!message_body && !mediaItems.length) ? 'missing_message_body' : (invalidAttachment ? 'invalid_attachment_url' : (mediaItems.length > 1 ? 'multiple_attachments_unsupported' : (requestedMode && !validModes.has(requestedMode) ? 'invalid_send_mode' : ''))))));
const yyyymmdd = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const dedupeKey = `body:${message_body}|media:${mediaItems.join('|')}|mode:${mode}|fallback:${fallback_text}`;
function hashHex(input) {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) { h ^= input.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const message_hash = hashHex(`${contact_id}|${workflow_id}|${dedupeKey}|${yyyymmdd}`);
return [{ json: { contact_id, phone, workflow_id, template_id, message_body, media_items: mediaItems, mode, fallback_text, simulate, message_hash, validationError } }];"""


IDEMPOTENT_FINALIZE_CODE = r"""const row = $json || {};
const ctx = $('Prepare Request').first().json;
if (ctx.validationError) return [{ json: { status: 'error', error: ctx.validationError, provider_response: null } }];
if (row.authorized === false) return [{ json: { status: 'error', error: 'unauthorized', provider_response: null } }];
if (!row.inserted) return [{ json: { status: 'duplicate', sent_at: row.sent_at || null, id: row.id || null, provider_response: null, error: null } }];

const token = String('__SIMPLETEXT_TOKEN__').trim();
if (!token) return [{ json: { status: 'error', error: 'missing_simpletexting_api_key', id: row.id || null, sent_at: row.sent_at || null, provider_response: null } }];

const digits = String(ctx.phone || '').replace(/\D/g, '');
const contactPhone = digits.length === 10 ? `+1${digits}` : `+${digits}`;
const mediaItems = Array.isArray(ctx.media_items) ? ctx.media_items : [];
const mode = mediaItems.length ? 'MMS_PREFERRED' : String(ctx.mode || 'AUTO').toUpperCase();
const fallbackText = String(ctx.fallback_text || [ctx.message_body, ...mediaItems].filter(Boolean).join('\n')).trim();
const providerRequest = { contactPhone, mode, text: ctx.message_body, ...(mediaItems.length ? { mediaItems, fallbackText } : {}) };
const sendProvider = async (requestBody) => {
  try {
    const response = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api-app2.simpletexting.com/v2/api/messages',
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/json', 'Content-Type': 'application/json' },
      body: requestBody,
      json: true,
    });
    const providerId = String(response?.id || response?.messageId || '').trim();
    if (!providerId) return { ok: false, error: 'simpletexting_missing_message_id', response: response || null };
    return { ok: true, response };
  } catch (err) {
    const response = err?.response;
    const responseBody = response?.body ?? response?.data ?? response;
    return { ok: false, error: err?.message || String(err), response: { error: err?.message || String(err), name: err?.name || null, code: err?.code || null, statusCode: err?.statusCode || err?.httpCode || err?.status || response?.status || null, responseBody: typeof responseBody === 'string' ? responseBody.slice(0, 2000) : responseBody, cause: err?.cause?.message || (typeof err?.cause === 'string' ? err.cause : null) } };
  }
};

let deliveryMode = mediaItems.length ? 'MMS' : 'SMS';
let fallbackUsed = false;
let providerResponse;
if (ctx.simulate) {
  providerResponse = { id: 'stubsim', status: 'queued', simulate: true, deliveryMode, fallbackUsed, mediaItems };
} else {
  const primary = await sendProvider(providerRequest);
  if (primary.ok) {
    providerResponse = { ...primary.response, deliveryMode, fallbackUsed, mediaItems };
  } else if (mediaItems.length) {
    const primaryStatus = Number(primary.response?.statusCode || 0);
    const mmsRejected = [400, 409, 413, 415, 422].includes(primaryStatus);
    if (!mmsRejected) return [{ json: { status: 'error', id: row.id, sent_at: row.sent_at || null, provider_response: primary.response, error: 'simpletexting_provider_error' } }];
    const fallback = await sendProvider({ contactPhone, mode: 'AUTO', text: fallbackText });
    if (!fallback.ok) return [{ json: { status: 'error', id: row.id, sent_at: row.sent_at || null, provider_response: { primary: primary.response, fallback: fallback.response }, error: 'simpletexting_provider_error' } }];
    deliveryMode = 'SMS_LINK_FALLBACK';
    fallbackUsed = true;
    providerResponse = { ...fallback.response, deliveryMode, fallbackUsed, mediaItems, primaryError: primary.response, fallbackProviderResponse: fallback.response };
  } else {
    return [{ json: { status: 'error', id: row.id, sent_at: row.sent_at || null, provider_response: primary.response, error: 'simpletexting_provider_error' } }];
  }
}
return [{ json: { status: 'sent', id: row.id, sent_at: row.sent_at || null, provider_response: providerResponse, delivery_mode: deliveryMode, fallback_used: fallbackUsed, error: null } }];"""


def load_env() -> dict[str, str]:
    env_path = REPO_ROOT / ".env"
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    value = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
    if not value:
        raise RuntimeError("N8N_API_KEY_LT is required")
    return value


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=data,
        method=method,
        headers={"X-N8N-API-KEY": api_key(), "Accept": "application/json", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def nodes_by_name(workflow: dict) -> dict[str, dict]:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def assignments(node: dict) -> list[dict]:
    return node["parameters"]["assignments"]["assignments"]


def set_assignment(node: dict, name: str, value: object, value_type: str = "boolean") -> None:
    for item in assignments(node):
        if item.get("name") == name:
            item["value"] = value
            item["type"] = value_type
            return
    assignments(node).append({"id": f"lt_{name.lower()}_repair", "name": name, "value": value, "type": value_type})


def payload(workflow: dict) -> dict:
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
    return {"name": workflow["name"], "nodes": workflow["nodes"], "connections": workflow.get("connections") or {}, "settings": settings}


def backup_workflows(workflows: dict[str, dict]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for workflow_id, workflow in workflows.items():
        backup_path = BACKUP_DIR / f"{workflow_id}-before-simpletexting-mms-{timestamp}.json"
        backup_path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return timestamp


def patch_send_boundary(workflow: dict) -> None:
    nodes = nodes_by_name(workflow)
    required = {"Config", "Validate + Send SMS", "Route Successful SMS Only", "Mirror to GHL Conversations", "Respond with SMS Result"}
    missing = required - set(nodes)
    if missing:
        raise RuntimeError(f"send boundary nodes changed: {sorted(missing)}")
    old_code = nodes["Validate + Send SMS"]["parameters"]["jsCode"]
    match = re.search(r"'x-lt-simpletexting-key':\s*'([^']+)'", old_code)
    config = nodes["Config"]
    configured_internal_value = next((item.get("value") for item in assignments(config) if item.get("name") == "internalSendHeaderValue"), "")
    internal_value = match.group(1) if match else configured_internal_value
    if not internal_value:
        raise RuntimeError("internal send header value was not found")
    set_assignment(config, "internalSendHeaderValue", internal_value, "string")
    set_assignment(config, "defaultDryRun", True)
    set_assignment(config, "templateRegistryJson", json.dumps({key: {"message": value} for key, value in TEMPLATES.items()}, ensure_ascii=True), "string")
    nodes["Validate + Send SMS"]["parameters"]["jsCode"] = SEND_CODE
    route_conditions = nodes["Route Successful SMS Only"]["parameters"]["rules"]["values"][0]["conditions"]["conditions"]
    if not any(condition.get("operator", {}).get("id") == "sms-no-ghl-mirror" for condition in route_conditions):
        route_conditions.append({
            "leftValue": "={{ $json.source }}",
            "rightValue": "ghl_workflow",
            "operator": {"type": "string", "operation": "notEquals", "id": "sms-no-ghl-mirror"},
        })
    nodes["Mirror to GHL Conversations"]["parameters"]["jsonBody"] = '={{ { type: "Custom", contactId: $json.contactId, message: $json.message, attachments: $json.mediaItems || [], conversationProviderId: $("Config").item.json.conversationProviderId, altId: "simpletexting:" + ($json.normalizedPhone || ("+1" + $json.contactPhone)) } }}'
    workflow["nodes"] = [node for node in workflow["nodes"] if node["name"] not in {"Loop Over Items", "Wait 1 Minute"}]
    workflow["connections"] = {
        "Webhook Intake": {"main": [[{"node": "Config", "type": "main", "index": 0}]]},
        "Config": {"main": [[{"node": "Validate + Send SMS", "type": "main", "index": 0}]]},
        "Validate + Send SMS": {"main": [[{"node": "Route Successful SMS Only", "type": "main", "index": 0}]]},
        "Route Successful SMS Only": {"main": [
            [{"node": "Mirror to GHL Conversations", "type": "main", "index": 0}],
            [{"node": "Respond with SMS Result", "type": "main", "index": 0}],
        ]},
        "Mirror to GHL Conversations": {"main": [[{"node": "Respond with SMS Result", "type": "main", "index": 0}]]},
    }


def patch_provider_boundary(workflow: dict) -> None:
    nodes = nodes_by_name(workflow)
    required = {"Config", "Process Provider Outbound", "Respond POST"}
    missing = required - set(nodes)
    if missing:
        raise RuntimeError(f"provider boundary nodes changed: {sorted(missing)}")
    old_code = nodes["Process Provider Outbound"]["parameters"]["jsCode"]
    header_values = re.findall(r"'x-lt-simpletexting-key':\s*'([^']+)'", old_code)
    configured_internal_value = next((item.get("value") for item in assignments(nodes["Config"]) if item.get("name") == "internalSendHeaderValue"), "")
    internal_value = header_values[-1] if header_values else configured_internal_value
    if not internal_value:
        raise RuntimeError("provider internal send header value was not found")
    set_assignment(nodes["Config"], "internalSendHeaderValue", internal_value, "string")
    nodes["Process Provider Outbound"]["parameters"]["jsCode"] = PROVIDER_PROCESS_CODE
    nodes["Respond POST"]["parameters"]["responseBody"] = '={{ { ok: !!($json.routing && $json.routing.routed), accepted: !!($json.routing && $json.routing.accepted), service: "lt-simpletexting-provider-outbound", routing: $json.routing || null } }}'
    nodes["Respond POST"]["parameters"]["options"]["responseCode"] = '={{ $json.routing && $json.routing.routed ? 200 : ($json.routing && $json.routing.step === "ghl_contact_lookup_failed" ? 502 : ($json.routing && $json.routing.step === "contact_opted_out" ? 409 : 400)) }}'


def patch_idempotent_boundary(workflow: dict) -> None:
    nodes = nodes_by_name(workflow)
    required = {"Prepare Request", "Claim Send", "Finalize Send"}
    missing = required - set(nodes)
    if missing:
        raise RuntimeError(f"idempotent boundary nodes changed: {sorted(missing)}")
    prepare_code = str(nodes["Prepare Request"]["parameters"].get("jsCode") or "")
    match = re.search(r"const expectedWebhookKey = '([^']+)';", prepare_code)
    if not match:
        match = re.search(r"const expectedWebhookKey = \"([^\"]+)\";", prepare_code)
    if not match:
        raise RuntimeError("idempotent boundary webhook key was not found")
    nodes["Prepare Request"]["parameters"]["jsCode"] = IDEMPOTENT_PREPARE_CODE.replace("__EXPECTED_WEBHOOK_KEY__", json.dumps(match.group(1)))
    claim_options = nodes["Claim Send"]["parameters"].setdefault("options", {})
    claim_options["queryReplacement"] = "={{ [ $json.contact_id || null, $json.phone || null, $json.workflow_id || null, $json.template_id || null, $json.message_hash || null, $json.authRejected !== true && !$json.validationError ] }}"
    finalize_code = str(nodes["Finalize Send"]["parameters"].get("jsCode") or "")
    token_match = re.search(r"const token = String\('([^']*)'\)", finalize_code)
    if not token_match:
        raise RuntimeError("idempotent SimpleTexting token was not found")
    nodes["Finalize Send"]["parameters"]["jsCode"] = IDEMPOTENT_FINALIZE_CODE.replace("__SIMPLETEXT_TOKEN__", token_match.group(1))


def patch_safe_schedule(workflow: dict, assignment_name: str) -> None:
    config = nodes_by_name(workflow).get("Config")
    if config:
        set_assignment(config, assignment_name, True)
        return
    replacements = 0
    already_safe = False
    for node in workflow.get("nodes", []):
        parameters = node.get("parameters") or {}
        code = str(parameters.get("jsCode") or "")
        if "dryRun: false" in code:
            node["parameters"]["jsCode"] = code.replace("dryRun: false", "dryRun: true")
            replacements += 1
        already_safe = already_safe or "dryRun: true" in code
        json_body = str(parameters.get("jsonBody") or "")
        if "dryRun: false" in json_body:
            node["parameters"]["jsonBody"] = json_body.replace("dryRun: false", "dryRun: true")
            replacements += 1
        already_safe = already_safe or "dryRun: true" in json_body
    if replacements == 0 and not already_safe:
        raise RuntimeError(f"{workflow['id']}: no dry-run control found")


def patch_callback_auth(workflow: dict, node_name: str) -> None:
    nodes = nodes_by_name(workflow)
    if not nodes.get(node_name) or not nodes.get("Build Event Key"):
        raise RuntimeError(f"{workflow['id']}: {node_name} missing")
    event_old = "const incomingEventKey = String(incomingHeaders['x-lt-simpletexting-event-key'] || incomingHeaders['X-LT-SimpleTexting-Event-Key'] || '').trim();"
    event_new = "const incomingEventKey = String(incomingHeaders['x-lt-simpletexting-event-key'] || incomingHeaders['X-LT-SimpleTexting-Event-Key'] || $json.query?.key || '').trim();"
    auth_old = "const incomingAuth = headers[cfg.authHeaderName] || headers[cfg.authHeaderName.toLowerCase()] || '';"
    auth_new = "const incomingAuth = headers[cfg.authHeaderName] || headers[cfg.authHeaderName.toLowerCase()] || $json.query?.key || '';"
    legacy_http_wrapper = "async function doHttpRequest(options) {\n  if (typeof $httpRequest === 'function') return await $httpRequest(options);\n  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);\n  throw new Error('HTTP helper not available');\n}\n"
    legacy_reply_wrapper = "// ---------- HTTP helpers ----------\nasync function doHttpRequest(opts) {\n  if (typeof $httpRequest === 'function') return await $httpRequest(opts);\n  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(opts);\n  throw new Error('No HTTP helper available');\n}\n"
    replacements = 0
    already_patched = 0
    for code_node in workflow.get("nodes", []):
        parameters = code_node.get("parameters") or {}
        if "jsCode" not in parameters:
            continue
        code = str(parameters.get("jsCode") or "")
        replacements += code.count(event_old) + code.count(auth_old)
        already_patched += code.count(event_new) + code.count(auth_new)
        parameters["jsCode"] = code.replace(event_old, event_new).replace(auth_old, auth_new).replace(legacy_http_wrapper, "").replace(legacy_reply_wrapper, "")
    if replacements == 0 and already_patched < 2:
        raise RuntimeError(f"{workflow['id']}: callback auth contract changed")


def inspect() -> None:
    for workflow_id in [SEND_WORKFLOW_ID, PROVIDER_WORKFLOW_ID, IDEMPOTENT_WORKFLOW_ID, *SAFE_SCHEDULES, *CALLBACK_WORKFLOWS]:
        workflow = request(workflow_id)
        print(json.dumps({
            "id": workflow_id,
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "versionId": workflow.get("versionId"),
            "nodeNames": [node.get("name") for node in workflow.get("nodes", [])],
        }))


def apply() -> None:
    send = request(SEND_WORKFLOW_ID)
    provider = request(PROVIDER_WORKFLOW_ID)
    idempotent = request(IDEMPOTENT_WORKFLOW_ID)
    backup_timestamp = backup_workflows({
        SEND_WORKFLOW_ID: send,
        PROVIDER_WORKFLOW_ID: provider,
        IDEMPOTENT_WORKFLOW_ID: idempotent,
    })
    print(json.dumps({"backupTimestamp": backup_timestamp, "backupDirectory": str(BACKUP_DIR)}))
    patch_send_boundary(send)
    patch_provider_boundary(provider)
    patch_idempotent_boundary(idempotent)
    results = [request(SEND_WORKFLOW_ID, "PUT", payload(send)), request(PROVIDER_WORKFLOW_ID, "PUT", payload(provider)), request(IDEMPOTENT_WORKFLOW_ID, "PUT", payload(idempotent))]
    for result in results:
        print(json.dumps({"id": result.get("id"), "name": result.get("name"), "active": result.get("active"), "versionId": result.get("versionId")}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply() if args.apply else inspect()


if __name__ == "__main__":
    main()
