"""Harden the live SimpleTexting send boundaries without sending messages."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
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
if (!contactId) return [{ json: { ok: false, error: 'missing_contact_id' } }];
if (!phone.e164) return [{ json: { ok: false, error: 'invalid_phone', contactId } }];

let registry = {};
try { registry = JSON.parse(clean(cfg.templateRegistryJson || '{}') || '{}'); }
catch { return [{ json: { ok: false, error: 'invalid_template_registry' } }]; }
const entry = registry[templateKey];
let text = clean(body.text || body.message || body.message_body || body.smsBody || (entry && entry.message));
if (!text) return [{ json: { ok: false, error: templateKey ? 'unknown_template_key' : 'missing_text', templateKey } }];
text = text
  .replace(/\{\{\s*(?:contact\.)?first_name\s*\}\}/gi, firstName)
  .replace(/\{\{\s*trigger_link\.nqLFBlEsdm7qccr8Yyog\s*\}\}/gi, clean(triggerLinks.nqLFBlEsdm7qccr8Yyog || body.bookingUrl));
if (/\{\{[^}]+\}\}/.test(text)) return [{ json: { ok: false, error: 'unresolved_merge_field', templateKey } }];

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

if (dryRun) return [{ json: { ok: true, dryRun: true, action: 'would_send_message', contactId, contactPhone: phone.digits, normalizedPhone: phone.e164, templateKey, message: text } }];
const send = await http({ method: 'POST', url: 'https://automations.livetransparent.com/webhook/lt-sms-send', headers: { 'Content-Type': 'application/json', 'x-lt-simpletexting-key': clean(cfg.internalSendHeaderValue) }, body: { contact_id: contactId, phone: phone.e164, workflow_id: 'Q3Ivnwe4z2Y3cD7A', template_id: templateKey, message_body: text, simulate: false } });
if (!send.ok) return [{ json: { ok: false, error: 'idempotent_webhook_error', details: send.data } }];
const result = send.data || {};
if (clean(result.status).toLowerCase() === 'duplicate') return [{ json: { ok: false, error: 'duplicate_send', sent_at: result.sent_at || null } }];
const providerResponse = result.provider_response || result;
const providerError = result.error || providerResponse?.error || '';
const providerMessageId = clean(providerResponse?.id || providerResponse?.messageId || result.providerMessageId);
if (providerError || clean(result.status).toLowerCase() === 'error' || !providerMessageId) return [{ json: { ok: false, error: 'simpletext_provider_failed', message: providerError || 'No provider message ID returned', providerResponse, providerMessageId: '' } }];

let tagSync = { attempted: false, ok: true };
let noteSync = { attempted: false, ok: true };
if (tagsToAdd.length) {
  const tagResult = await http({ method: 'POST', url: `${ghlBase}/contacts/${encodeURIComponent(contactId)}/tags`, headers: ghlHeaders, body: { tags: tagsToAdd } });
  tagSync = { attempted: true, ok: tagResult.ok, details: tagResult.ok ? undefined : tagResult.data };
}
const note = ['SMS sent via SimpleTexting', `To: ${phone.e164}`, `Provider Message ID: ${providerMessageId}`, templateKey ? `Template: ${templateKey}` : '', 'Message:', text].filter(Boolean).join('\n');
const noteResult = await http({ method: 'POST', url: `${ghlBase}/contacts/${encodeURIComponent(contactId)}/notes`, headers: ghlHeaders, body: { body: note } });
noteSync = { attempted: true, ok: noteResult.ok, details: noteResult.ok ? undefined : noteResult.data };
return [{ json: { ok: true, action: 'message_sent', provider: 'SimpleTexting', contactId, contactPhone: phone.digits, normalizedPhone: phone.e164, templateKey, message: text, providerResponse, providerMessageId, ghlTagSync: tagSync, ghlNoteSync: noteSync } }];"""


PROVIDER_PROCESS_CODE = r"""const cfg = $('Config').item.json || {};
const body = $('POST - GHL Provider Outbound').item.json.body || {};
const clean = (value) => String(value ?? '').trim();
const contactId = clean(body.contactId || body.contact_id);
const message = clean(body.message || body.text || body.body);
const providerId = clean(body.conversationProviderId || body.providerId || body.provider_id);
const digits = clean(body.phone || body.to || body.contactPhone).replace(/\D/g, '');
const normalizedPhone = digits.length === 10 ? `+1${digits}` : (digits.length === 11 && digits.startsWith('1') ? `+${digits}` : '');
const result = { routed: false, accepted: false, duplicate: false, contact_id: contactId, normalized_phone: normalizedPhone, error: '', step: '' };
if (!clean(cfg.providerId) || providerId !== clean(cfg.providerId)) { result.step = 'validate_provider'; result.error = 'invalid_provider'; return [{ json: { routing: result } }]; }
if (!contactId || !message || !normalizedPhone) { result.step = 'validate_input'; result.error = 'missing_required_fields'; return [{ json: { routing: result } }]; }
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
    body: { contact_id: contactId, phone: normalizedPhone, workflow_id: 'provider_outbound', message_body: message, simulate: false },
    json: true,
    timeout: 15000,
  });
  const status = clean(sendResponse?.status).toLowerCase();
  result.duplicate = status === 'duplicate';
  result.routed = status === 'sent' || result.duplicate;
  result.accepted = result.routed;
  result.step = status === 'sent' ? 'sent' : (result.duplicate ? 'duplicate_accepted' : 'idempotent_blocked');
  result.error = result.routed ? '' : clean(sendResponse?.error || 'provider_send_failed');
  result.provider_message_id = clean(sendResponse?.provider_response?.id || sendResponse?.provider_response?.messageId);
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
const parseBoolean = (value, fallback) => {
  if (value === undefined || value === null || value === '') return fallback;
  if (typeof value === 'boolean') return value;
  return ['true', '1', 'yes', 'on'].includes(String(value).trim().toLowerCase());
};
const simulate = parseBoolean(body.simulate, true);
const validationError = !contact_id ? 'missing_contact_id' : (!phone ? 'invalid_phone' : (!workflow_id ? 'missing_workflow_id' : (!message_body ? 'missing_message_body' : '')));
const yyyymmdd = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const dedupeKey = template_id ? `template:${template_id}` : `body:${message_body}`;
function hashHex(input) {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) { h ^= input.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const message_hash = hashHex(`${contact_id}|${workflow_id}|${dedupeKey}|${yyyymmdd}`);
return [{ json: { contact_id, phone, workflow_id, template_id, message_body, simulate, message_hash, validationError } }];"""


def load_env() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[1] / ".env"
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
    nodes["Mirror to GHL Conversations"]["parameters"]["jsonBody"] = '={{ { type: "Custom", contactId: $json.contactId, message: $json.message, conversationProviderId: $("Config").item.json.conversationProviderId, altId: "simpletexting:" + ($json.normalizedPhone || ("+1" + $json.contactPhone)) } }}'
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
        raise RuntimeError("idempotent boundary webhook key was not found")
    nodes["Prepare Request"]["parameters"]["jsCode"] = IDEMPOTENT_PREPARE_CODE.replace("__EXPECTED_WEBHOOK_KEY__", json.dumps(match.group(1)))
    claim_options = nodes["Claim Send"]["parameters"].setdefault("options", {})
    claim_options["queryReplacement"] = "={{ [ $json.contact_id || null, $json.phone || null, $json.workflow_id || null, $json.template_id || null, $json.message_hash || null, $json.authRejected !== true && !$json.validationError ] }}"
    finalize_code = str(nodes["Finalize Send"]["parameters"].get("jsCode") or "")
    validation_guard = "if (ctx.validationError) return [{ json: { status: 'error', error: ctx.validationError, provider_response: null } }];"
    if validation_guard not in finalize_code:
        marker = "if (row.authorized === false) return [{ json: { status: 'error', error: 'unauthorized', provider_response: null } }];"
        if marker not in finalize_code:
            raise RuntimeError("idempotent finalize auth guard changed")
        finalize_code = finalize_code.replace(marker, validation_guard + "\n\n" + marker, 1)
    nodes["Finalize Send"]["parameters"]["jsCode"] = finalize_code


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
    schedules = {workflow_id: request(workflow_id) for workflow_id in SAFE_SCHEDULES}
    callbacks = {workflow_id: request(workflow_id) for workflow_id in CALLBACK_WORKFLOWS}
    patch_send_boundary(send)
    patch_provider_boundary(provider)
    patch_idempotent_boundary(idempotent)
    for workflow_id, assignment_name in SAFE_SCHEDULES.items():
        patch_safe_schedule(schedules[workflow_id], assignment_name)
    for workflow_id, node_name in CALLBACK_WORKFLOWS.items():
        patch_callback_auth(callbacks[workflow_id], node_name)
    results = [request(SEND_WORKFLOW_ID, "PUT", payload(send)), request(PROVIDER_WORKFLOW_ID, "PUT", payload(provider)), request(IDEMPOTENT_WORKFLOW_ID, "PUT", payload(idempotent))]
    results.extend(request(workflow_id, "PUT", payload(workflow)) for workflow_id, workflow in schedules.items())
    results.extend(request(workflow_id, "PUT", payload(workflow)) for workflow_id, workflow in callbacks.items())
    for result in results:
        print(json.dumps({"id": result.get("id"), "name": result.get("name"), "active": result.get("active"), "versionId": result.get("versionId")}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply() if args.apply else inspect()


if __name__ == "__main__":
    main()
