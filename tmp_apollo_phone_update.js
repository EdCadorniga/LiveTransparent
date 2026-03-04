const input = $json || {};
const source = (input.body && typeof input.body === 'object') ? input.body : input;
const body = source && typeof source === 'object' ? source : {};
const headers = input.headers || {};
const cfg = $item(0).$node['Config'].json || {};

function str(v) { const s = String(v ?? '').trim(); return s || null; }
function num(v) { if (v === null || v === undefined || v === '') return null; const n = Number(String(v).replace(/[^0-9.-]/g, '')); return Number.isFinite(n) ? n : null; }
function int(v) { const n = num(v); return n === null ? null : Math.trunc(n); }
function bool(v) { if (v === null || v === undefined || v === '') return null; const s = String(v).trim().toLowerCase(); if (['true','1','yes','y'].includes(s)) return true; if (['false','0','no','n'].includes(s)) return false; return null; }
function dateIso(v) { if (!v) return null; const d = new Date(v); return Number.isNaN(d.getTime()) ? null : d.toISOString(); }
function normalizeLinkedinUrl(v) {
  const s = String(v ?? '').trim();
  if (!s) return null;
  try {
    const u = new URL(s);
    const host = u.hostname.toLowerCase();
    if (host === 'linkedin.com' || host.endsWith('.linkedin.com')) return s;
    return null;
  } catch { return null; }
}
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
function toJsonObject(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'object') return v;
  return { message: String(v) };
}
async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ baseUrl, method, path, headers, body, fullUrl, json = true }) {
  const options = { method, url: fullUrl || `${String(baseUrl).replace(/\/$/, '')}${path}`, headers, json };
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

const contactId = body.customData?.contactId || body.contactId || body.contact_id || body.contact?.id || body.id || input.contactId || input.contact_id || input.id;
if (!contactId) throw new Error('Missing contactId in webhook payload');

const enrichToggle = str(body.enrichPhoneViaApollo || body.customData?.enrichPhoneViaApollo || body['contact.enrich_phone_via_apollo']);
// Do not hard-skip from payload value alone; GHL trigger is the source of truth for when this workflow runs.

const webhookKeyHeader = headers['x-lt-webhook-key'] || headers['X-LT-Webhook-Key'] || null;
const webhookKeyBody = body.webhookKey || body.customData?.webhookKey || null;
const expectedWebhookKey = str(cfg.webhookKey);
if (expectedWebhookKey) {
  const candidate = str(webhookKeyHeader || webhookKeyBody);
  if (!candidate || candidate !== expectedWebhookKey) throw new Error('Webhook key missing or mismatch');
}

const forceOverwritePhone = bool(body.forceOverwritePhone);
const shouldOverwritePhone = forceOverwritePhone === null ? bool(cfg.defaultForceOverwritePhone) === true : forceOverwritePhone === true;

const ghlHeaders = {
  Authorization: `Bearer ${cfg.ghlApiKey}`,
  Version: '2021-07-28',
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

const contactRes = await apiRequest.call(this, {
  baseUrl: cfg.ghlApiBaseUrl,
  method: 'GET',
  path: `/contacts/${contactId}`,
  headers: ghlHeaders,
});
if (!contactRes.ok) throw new Error(`Failed to fetch contact ${contactId}: ${JSON.stringify(contactRes.data)}`);
const contact = contactRes.data?.contact || contactRes.data || {};

const existingPhone = str(contact.phone);
if (existingPhone && !shouldOverwritePhone) {
  return [{ json: { ok: true, skipped: true, reason: 'phone_already_present', contactId, existingPhone, debugCallbackUrl: null } }];
}

const fieldsRes = await apiRequest.call(this, {
  baseUrl: cfg.ghlApiBaseUrl,
  method: 'GET',
  path: `/locations/${cfg.locationId}/customFields?model=contact`,
  headers: ghlHeaders,
});
if (!fieldsRes.ok) throw new Error(`Failed to fetch custom fields: ${JSON.stringify(fieldsRes.data)}`);
const customFields = Array.isArray(fieldsRes.data?.customFields)
  ? fieldsRes.data.customFields
  : Array.isArray(fieldsRes.data?.data?.customFields)
    ? fieldsRes.data.data.customFields
    : Array.isArray(fieldsRes.data?.data)
      ? fieldsRes.data.data
      : [];
const fieldByName = new Map(customFields.map((f) => [String(f.name || '').trim(), f]));

const email = str(body.email || body.customData?.email || contact.email);
const firstName = str(body.first_name || body.firstName || body.customData?.firstName || contact.firstName || contact.first_name);
const lastName = str(body.last_name || body.lastName || body.customData?.lastName || contact.lastName || contact.last_name);
const company = str(body.company_name || body.companyName || contact.companyName || contact.company);
const linkedin = normalizeLinkedinUrl(body.linkedin_url || body.linkedinUrl || null);
const domain = str(body.domain || (company && company.includes('.') ? company : null));
const apolloPhoneWebhookUrl = str(body.apolloPhoneWebhookUrl || body.customData?.apolloPhoneWebhookUrl || cfg.apolloPhoneWebhookUrl);
const callbackUrlWithContactId = apolloPhoneWebhookUrl ? `${apolloPhoneWebhookUrl}${apolloPhoneWebhookUrl.includes('?') ? '&' : '?'}contactId=${encodeURIComponent(contactId)}${expectedWebhookKey ? `&webhookKey=${encodeURIComponent(expectedWebhookKey)}` : ''}` : null;

function findDuplicatePhoneConflict(...attemptGroups) {
  for (const group of attemptGroups) {
    for (const attempt of group || []) {
      const resp = attempt?.response || {};
      if (resp?.message === 'This location does not allow duplicated contacts.' && resp?.meta?.matchingField === 'phone') {
        return {
          contactId: resp?.meta?.contactId || null,
          contactName: resp?.meta?.contactName || null,
          matchingField: resp?.meta?.matchingField || null,
        };
      }
    }
  }
  return null;
}

async function updateContactWithFallback(standard, customFieldUpdates) {
  const standardClean = Object.fromEntries(Object.entries(standard || {}).filter(([,v]) => v !== null && v !== undefined && String(v).trim() !== ''));
  const customFieldObject = Object.fromEntries((customFieldUpdates || []).map((u) => [u.id, u.value]));
  const customFieldArray = (customFieldUpdates || []).map((u) => ({ id: u.id, value: u.value }));
  const customFieldArrayFieldValue = (customFieldUpdates || []).map((u) => ({ id: u.id, field_value: u.value }));

  const updateBodies = [
    { ...standardClean, locationId: cfg.locationId, customField: customFieldObject },
    { ...standardClean, customField: customFieldObject },
    { ...standardClean, locationId: cfg.locationId, customFields: customFieldArray },
    { ...standardClean, customFields: customFieldArray },
    { ...standardClean, locationId: cfg.locationId, customFields: customFieldArrayFieldValue },
    { ...standardClean, customFields: customFieldArrayFieldValue },
    { ...standardClean, locationId: cfg.locationId },
  ];

  const updateAttempts = [];
  for (const bodyTry of updateBodies) {
    const updateRes = await apiRequest.call(this, {
      baseUrl: cfg.ghlApiBaseUrl,
      method: 'PUT',
      path: `/contacts/${contactId}`,
      headers: ghlHeaders,
      body: bodyTry,
    });
    if (updateRes.ok) return { ok: true, bodyUsed: bodyTry };
    updateAttempts.push({ body: bodyTry, status: updateRes.status, response: updateRes.data });
  }
  return { ok: false, updateAttempts };
}

function cf(name, value) {
  if (value === null || value === undefined || String(value).trim() === '') return null;
  const f = fieldByName.get(name);
  if (!f?.id) return null;

  let normalized = value;

  // GHL TEXT fields can reject oversized payloads; trim conservatively.
  if (f.dataType === 'TEXT' && typeof normalized === 'string' && normalized.length > 255) {
    normalized = normalized.slice(0, 255);
  }

  // DATE custom fields expect YYYY-MM-DD (not full ISO datetime).
  if (f.dataType === 'DATE' && typeof normalized === 'string') {
    const d = new Date(normalized);
    if (!Number.isNaN(d.getTime())) normalized = d.toISOString().slice(0, 10);
  }

  return { id: f.id, value: normalized };
}

if (!cfg.apolloApiKey) throw new Error('Missing Apollo API key');

// Mark as queued immediately so GHL can show in-flight state.
const queuedUpdates = [
  cf('Apollo Phone Enrichment Status', 'queued'),
].filter(Boolean);
if (queuedUpdates.length) {
  await updateContactWithFallback.call(this, {}, queuedUpdates);
}

const terminalNoMatchUpdates = [
  cf('Apollo Phone Enrichment Status', 'no_match'),
  cf('Enrich Phone via Apollo', 'No'),
].filter(Boolean);

if (!email && !linkedin && !(firstName && lastName && (company || domain))) {
  if (terminalNoMatchUpdates.length) await updateContactWithFallback.call(this, {}, terminalNoMatchUpdates);
  return [{ json: {
    ok: true,
    skipped: true,
    reason: 'insufficient_data_for_apollo_match',
    contactId,
    ingestRecord: {
      apollo_contact_id: null,
      apollo_account_id: null,
      first_name: firstName,
      last_name: lastName,
      title: null,
      company_name: company,
      email,
      email_status: null,
      seniority: null,
      departments: null,
      sub_departments: null,
      employees_count: null,
      industry: null,
      keywords: null,
      person_linkedin_url: linkedin,
      company_linkedin_url: null,
      facebook_url: null,
      twitter_url: null,
      city: null,
      state: null,
      country: null,
      company_phone: null,
      technologies: null,
      annual_revenue: null,
      total_funding: null,
      latest_funding: null,
      latest_funding_amount: null,
      last_raised_at: null,
      secondary_email: null,
      secondary_email_status: null,
      tertiary_email: null,
      tertiary_email_status: null,
      primary_intent_topic: null,
      primary_intent_score: null,
      secondary_intent_topic: null,
      secondary_intent_score: null,
      source: 'apollo_phone_enrichment_no_match',
      raw_payload: null,
    },
  } }];
}

const apolloHeaders = {
  'X-Api-Key': cfg.apolloApiKey,
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

const matchCandidates = [];
if (email) matchCandidates.push({ email });
if (linkedin) matchCandidates.push({ linkedin_url: linkedin });
if (firstName && lastName && company) matchCandidates.push({ first_name: firstName, last_name: lastName, organization_name: company });
if (firstName && lastName && domain) matchCandidates.push({ first_name: firstName, last_name: lastName, domain });
if (!matchCandidates.length) matchCandidates.push({ first_name: firstName || undefined, last_name: lastName || undefined, organization_name: company || undefined, domain: domain || undefined });

let person = null;
let apolloError = null;
for (const candidate of matchCandidates) {
  const apolloBody = {
    ...candidate,
    reveal_personal_emails: false,
    reveal_phone_number: !!callbackUrlWithContactId,
    webhook_url: callbackUrlWithContactId || undefined,
  };
  Object.keys(apolloBody).forEach((k) => apolloBody[k] === undefined && delete apolloBody[k]);

  const apolloRes = await apiRequest.call(this, {
    baseUrl: cfg.apolloApiBaseUrl,
    method: 'POST',
    path: '/v1/people/match',
    headers: apolloHeaders,
    body: apolloBody,
  });

  if (apolloRes.ok && apolloRes.data?.person) {
    person = apolloRes.data.person;
    apolloError = null;
    break;
  }

  apolloError = apolloRes;
}

if (!person) {
  const statusVal = (apolloError?.status && apolloError.status >= 500) ? 'error' : 'no_match';
  const terminalUpdates = [
    cf('Apollo Phone Enrichment Status', statusVal),
    cf('Enrich Phone via Apollo', 'No'),
  ].filter(Boolean);
  if (terminalUpdates.length) await updateContactWithFallback.call(this, {}, terminalUpdates);
  return [{ json: {
    ok: true,
    contactId,
    foundPhone: false,
    status: statusVal,
    apolloErrorStatus: apolloError?.status || null,
    apolloError: apolloError?.data || null,
    ingestRecord: {
      apollo_contact_id: null,
      apollo_account_id: null,
      first_name: firstName,
      last_name: lastName,
      title: null,
      company_name: company,
      email,
      email_status: null,
      seniority: null,
      departments: null,
      sub_departments: null,
      employees_count: null,
      industry: null,
      keywords: null,
      person_linkedin_url: linkedin,
      company_linkedin_url: null,
      facebook_url: null,
      twitter_url: null,
      city: null,
      state: null,
      country: null,
      company_phone: null,
      technologies: null,
      annual_revenue: null,
      total_funding: null,
      latest_funding: null,
      latest_funding_amount: null,
      last_raised_at: null,
      secondary_email: null,
      secondary_email_status: null,
      tertiary_email: null,
      tertiary_email_status: null,
      primary_intent_topic: null,
      primary_intent_score: null,
      secondary_intent_topic: null,
      secondary_intent_score: null,
      source: statusVal === 'error' ? 'apollo_phone_enrichment_error' : 'apollo_phone_enrichment_no_match',
      raw_payload: toJsonObject(apolloError?.data),
    },
  } }];
}

const org = person.organization || {};
const phoneCandidates = [
  str(person.phone),
  str(person.mobile_phone),
  str(person.sanitized_phone),
  str(org.phone),
  str(org.sanitized_phone),
  str(org.primary_phone?.number),
  str(org.primary_phone?.sanitized_number),
  str(person.contact?.sanitized_phone),
  ...(Array.isArray(person.contact?.phone_numbers)
    ? person.contact.phone_numbers.map((p) => typeof p === 'string' ? p : (p?.raw_number || p?.sanitized_number || p?.number || null))
    : []),
  ...(Array.isArray(person.phone_numbers)
    ? person.phone_numbers.map((p) => typeof p === 'string' ? p : (p?.raw_number || p?.sanitized_number || p?.number || null))
    : []),
].filter(Boolean);

const normalizedPhone = normalizePhone(phoneCandidates[0] || null, org.country || contact.country || null);

const standard = {
  firstName: str(person.first_name),
  lastName: str(person.last_name),
  email: str(person.email),
  companyName: str(org.name),
  city: str(org.city),
  state: str(org.state),
  country: str(org.country),
};
if (normalizedPhone && (!existingPhone || shouldOverwritePhone)) standard.phone = normalizedPhone;

let duplicatePhoneConflict = null;
if (normalizedPhone) {
  const duplicateSearchRes = await apiRequest.call(this, {
    baseUrl: cfg.ghlApiBaseUrl,
    method: 'GET',
    path: `/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(normalizedPhone)}&limit=5`,
    headers: ghlHeaders,
  });
  if (duplicateSearchRes.ok) {
    const possibleMatches = Array.isArray(duplicateSearchRes.data?.contacts)
      ? duplicateSearchRes.data.contacts
      : Array.isArray(duplicateSearchRes.data?.data?.contacts)
        ? duplicateSearchRes.data.data.contacts
        : [];
    const duplicateMatch = possibleMatches.find((c) => c?.id && c.id !== contactId && normalizePhone(c.phone, c.country || contact.country || null) === normalizedPhone);
    if (duplicateMatch) {
      duplicatePhoneConflict = {
        contactId: duplicateMatch.id,
        contactName: duplicateMatch.contactName || [duplicateMatch.firstName, duplicateMatch.lastName].filter(Boolean).join(' ') || null,
        matchingField: 'phone',
      };
    }
  }
}

const customByName = {
  'Apollo Contact Id': str(person.id),
  'Apollo Account Id': str(org.id || person.organization_id),
  'Apollo Email Status': str(person.email_status),
  'Title': str(person.title || person?.title),
  'Apollo Seniority': str(person.seniority),
  'Apollo Departments': Array.isArray(person.departments) ? person.departments.join(', ') : null,
  'Apollo Sub Departments': Array.isArray(person.subdepartments) ? person.subdepartments.join(', ') : null,
  'Apollo Company Employees': int(org.estimated_num_employees),
  'Apollo Industry': str(org.industry),
  'Apollo Keywords': Array.isArray(org.keywords) ? org.keywords.join(', ') : null,
  'Apollo Person LinkedIn URL': normalizeLinkedinUrl(person.linkedin_url),
  'Apollo Company LinkedIn URL': normalizeLinkedinUrl(org.linkedin_url),
  'Apollo Facebook URL': str(person.facebook_url || org.facebook_url),
  'Apollo Twitter URL': str(person.twitter_url || org.twitter_url),
  'Apollo Technologies': Array.isArray(org.technology_names) ? org.technology_names.join(', ') : null,
  'Apollo Annual Revenue': num(org.annual_revenue),
  'Apollo Total Funding': num(org.total_funding),
  'Apollo Latest Funding': str(org.latest_funding_stage),
  'Apollo Last Raised At': dateIso(org.latest_funding_round_date),
  'Contact already Enriched': 'Yes',
  'Enrich via Apollo': 'No',
  'Enrich Phone via Apollo': 'No',
  'Apollo Phone Enrichment Status': normalizedPhone ? 'enriched' : 'no_match',
  'Apollo Phone Enriched At': new Date().toISOString().slice(0, 10),
};

if (Array.isArray(org.funding_events) && org.funding_events.length) {
  const latestEvent = org.funding_events
    .map((e) => ({ e, ts: new Date(e?.date || 0).getTime() || 0 }))
    .sort((a, b) => b.ts - a.ts)[0]?.e;
  if (latestEvent?.amount) customByName['Apollo Latest Funding Amount'] = num(latestEvent.amount);
}

const customFieldUpdates = Object.entries(customByName)
  .map(([name, value]) => cf(name, value))
  .filter(Boolean);

const ingestRecord = {
  apollo_contact_id: str(person.id),
  apollo_account_id: str(org.id || person.organization_id),
  first_name: str(person.first_name),
  last_name: str(person.last_name),
  title: str(person.title),
  company_name: str(org.name),
  email: str(person.email),
  email_status: str(person.email_status),
  seniority: str(person.seniority),
  departments: Array.isArray(person.departments) ? person.departments.join(', ') : null,
  sub_departments: Array.isArray(person.subdepartments) ? person.subdepartments.join(', ') : null,
  employees_count: int(org.estimated_num_employees),
  industry: str(org.industry),
  keywords: Array.isArray(org.keywords) ? org.keywords.join(', ') : null,
  person_linkedin_url: normalizeLinkedinUrl(person.linkedin_url),
  company_linkedin_url: normalizeLinkedinUrl(org.linkedin_url),
  facebook_url: str(person.facebook_url || org.facebook_url),
  twitter_url: str(person.twitter_url || org.twitter_url),
  city: str(org.city),
  state: str(org.state),
  country: str(org.country),
  company_phone: str(org.phone || org.sanitized_phone || org.primary_phone?.number || org.primary_phone?.sanitized_number || person.contact?.sanitized_phone || person.contact?.phone_numbers?.[0]?.sanitized_number || person.contact?.phone_numbers?.[0]?.raw_number),
  technologies: Array.isArray(org.technology_names) ? org.technology_names.join(', ') : null,
  annual_revenue: num(org.annual_revenue),
  total_funding: num(org.total_funding),
  latest_funding: str(org.latest_funding_stage),
  latest_funding_amount: num(customByName['Apollo Latest Funding Amount']),
  last_raised_at: dateIso(org.latest_funding_round_date),
  secondary_email: null,
  secondary_email_status: null,
  tertiary_email: null,
  tertiary_email_status: null,
  primary_intent_topic: null,
  primary_intent_score: null,
  secondary_intent_topic: null,
  secondary_intent_score: null,
  source: 'apollo_phone_enrichment',
  raw_payload: toJsonObject(person),
};

const minimalStandard = {};
if (normalizedPhone && (!existingPhone || shouldOverwritePhone)) minimalStandard.phone = normalizedPhone;

const minimalCustomFieldUpdates = [
  cf('Apollo Phone Enrichment Status', normalizedPhone ? 'enriched' : 'no_match'),
  cf('Apollo Phone Enriched At', new Date().toISOString().slice(0, 10)),
  cf('Contact already Enriched', 'Yes'),
  cf('Enrich via Apollo', 'No'),
  cf('Enrich Phone via Apollo', 'No'),
].filter(Boolean);

if (duplicatePhoneConflict) {
  const duplicateStatusUpdates = [
    cf('Apollo Phone Enrichment Status', 'error'),
    cf('Enrich Phone via Apollo', 'No'),
  ].filter(Boolean);
  if (duplicateStatusUpdates.length) {
    await updateContactWithFallback.call(this, {}, duplicateStatusUpdates);
  }
  return [{ json: {
    ok: true,
    contactId,
    source: 'apollo_phone_enrichment',
    foundPhone: !!normalizedPhone,
    normalizedPhone: normalizedPhone || null,
    status: 'error',
    reason: 'duplicate_phone_blocked',
    duplicatePhoneConflict,
    ingestRecord,
  } }];
}

let upd = await updateContactWithFallback.call(this, standard, customFieldUpdates);
if (!upd.ok) {
  const minimalUpd = await updateContactWithFallback.call(this, minimalStandard, minimalCustomFieldUpdates);
  if (minimalUpd.ok) {
    upd = minimalUpd;
  } else {
    const duplicatePhoneConflict = findDuplicatePhoneConflict(upd.updateAttempts, minimalUpd.updateAttempts);
    const errorUpdates = [
      cf('Apollo Phone Enrichment Status', 'error'),
      cf('Enrich Phone via Apollo', 'No'),
    ].filter(Boolean);
    if (errorUpdates.length) {
      await updateContactWithFallback.call(this, {}, errorUpdates);
    }
    if (duplicatePhoneConflict) {
      return [{ json: {
        ok: true,
        contactId,
        source: 'apollo_phone_enrichment',
        foundPhone: !!normalizedPhone,
        normalizedPhone: normalizedPhone || null,
        status: 'error',
        reason: 'duplicate_phone_blocked',
        duplicatePhoneConflict,
        ingestRecord,
      } }];
    }
    throw new Error(`GHL update failed after Apollo returned enrichment data for contact ${contactId}: ${JSON.stringify({ full: upd.updateAttempts, minimal: minimalUpd.updateAttempts })}`);
  }
}

return [{ json: {
  ok: true,
  contactId,
  source: 'apollo_phone_enrichment',
  apolloPersonId: person.id || null,
  foundPhone: !!normalizedPhone,
  normalizedPhone: normalizedPhone || null,
  updatedCustomFieldCount: customFieldUpdates.length,
  updateRequestBodyUsed: upd.bodyUsed,
  ingestRecord,
} }];