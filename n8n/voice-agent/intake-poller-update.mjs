import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Every 10 Minutes',
    position: [0, 0],
    parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 10, triggerAtMinute: 0 }] } }
  },
  output: [{}]
});

const processCode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Process Tagged Contacts',
    position: [224, 0],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const GHL_API_KEY = $env.GHL_PIT || $env.GHL_API_KEY;
const GHL_LOCATION_ID = $env.GHL_LOCATION_ID || 'Zwz4relUXVPxx8uohnjV';
const BASE_URL = 'https://services.leadconnectorhq.com';
const ENQUEUE_URL = 'https://automations.livetransparent.com/webhook/voice-queue-enqueue';
const ENRICHMENT_STATUS = 'rgYJ7UqoznGoe3WeUAtH';
const ENRICH_PHONE_VIA_APOLLO = 'gdJDuZelIxEBE6n9i5Q6';

const TERMINAL_STATUSES = ['no_match', 'error', 'callback_failed', 'callback_timeout'];

const headers = {
  'Authorization': \`Bearer \${GHL_API_KEY}\`,
  'Version': '2021-07-28',
  'Content-Type': 'application/json'
};

async function searchContacts() {
  const res = await fetch(\`\${BASE_URL}/contacts/search\`, {
    method: 'POST', headers,
    body: JSON.stringify({
      locationId: GHL_LOCATION_ID,
      pageLimit: 20,
      filters: [{ field: 'tags', operator: 'contains', value: 'vapi_queue' }]
    })
  });
  if (!res.ok) throw new Error(\`GHL search failed: \${res.status} \${await res.text()}\`);
  const data = await res.json();
  return (data.contacts || []).sort((a, b) => new Date(b.createdDate || 0) - new Date(a.createdDate || 0));
}

async function removeTag(contactId) {
  const res = await fetch(\`\${BASE_URL}/contacts/\${contactId}/tags\`, {
    method: 'DELETE', headers,
    body: JSON.stringify({ tags: ['vapi_queue'] })
  });
  return res.ok;
}

async function setEnrichFlag(contactId) {
  const res = await fetch(\`\${BASE_URL}/contacts/\${contactId}\`, {
    method: 'PUT', headers,
    body: JSON.stringify({ customFields: [{ id: ENRICH_PHONE_VIA_APOLLO, value: 'Yes' }] })
  });
  return res.ok;
}

async function enqueueContact(contactId, phone, firstName, timezone) {
  const res = await fetch(ENQUEUE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contact_id: contactId, phone, first_name: firstName,
      campaign_id: 'default', timezone
    })
  });
  return await res.json();
}

function normalizeText(value) {
  return String(value || '').trim().toLowerCase();
}

function getContactTags(contact) {
  const rawTags = Array.isArray(contact.tags) ? contact.tags : [];
  return rawTags
    .map(tag => {
      if (typeof tag === 'string') return tag;
      if (tag && typeof tag === 'object') return tag.name || tag.label || tag.tag || tag.id || '';
      return '';
    })
    .map(normalizeText)
    .filter(Boolean);
}

function hasContactTag(contact, tagName) {
  const target = normalizeText(tagName);
  if (!target) return false;
  return getContactTags(contact).includes(target);
}

function resolveTimezone(contact) {
  const explicit = String(contact.timezone || contact.timeZone || contact.time_zone || '').trim();
  if (explicit) return explicit;

  const country = String(contact.country || contact.countryCode || contact.country_code || '').trim().toUpperCase();
  const state = normalizeText(contact.state || contact.stateName || contact.region || contact.province || contact.state_code);

  const usStateAbbrevMap = {
    al: 'alabama',
    ak: 'alaska',
    az: 'arizona',
    ar: 'arkansas',
    ca: 'california',
    co: 'colorado',
    ct: 'connecticut',
    de: 'delaware',
    dc: 'district of columbia',
    fl: 'florida',
    ga: 'georgia',
    hi: 'hawaii',
    id: 'idaho',
    il: 'illinois',
    in: 'indiana',
    ia: 'iowa',
    ks: 'kansas',
    ky: 'kentucky',
    la: 'louisiana',
    me: 'maine',
    md: 'maryland',
    ma: 'massachusetts',
    mi: 'michigan',
    mn: 'minnesota',
    ms: 'mississippi',
    mo: 'missouri',
    mt: 'montana',
    ne: 'nebraska',
    nv: 'nevada',
    nh: 'new hampshire',
    nj: 'new jersey',
    nm: 'new mexico',
    ny: 'new york',
    nc: 'north carolina',
    nd: 'north dakota',
    oh: 'ohio',
    ok: 'oklahoma',
    or: 'oregon',
    pa: 'pennsylvania',
    ri: 'rhode island',
    sc: 'south carolina',
    sd: 'south dakota',
    tn: 'tennessee',
    tx: 'texas',
    ut: 'utah',
    vt: 'vermont',
    va: 'virginia',
    wa: 'washington',
    wv: 'west virginia',
    wi: 'wisconsin',
    wy: 'wyoming'
  };

  const caProvinceAbbrevMap = {
    bc: 'british columbia',
    ab: 'alberta',
    sk: 'saskatchewan',
    mb: 'manitoba',
    on: 'ontario',
    qc: 'quebec',
    nb: 'new brunswick',
    ns: 'nova scotia',
    pe: 'prince edward island',
    nl: 'newfoundland and labrador',
    nt: 'northwest territories',
    yt: 'yukon',
    nu: 'nunavut'
  };

  const provinceMap = {
    'british columbia': 'America/Vancouver',
    'alberta': 'America/Edmonton',
    'saskatchewan': 'America/Regina',
    'manitoba': 'America/Winnipeg',
    'ontario': 'America/Toronto',
    'quebec': 'America/Toronto',
    'new brunswick': 'America/Halifax',
    'nova scotia': 'America/Halifax',
    'prince edward island': 'America/Halifax',
    'newfoundland and labrador': 'America/St_Johns',
    'northwest territories': 'America/Edmonton',
    'yukon': 'America/Whitehorse',
    'nunavut': 'America/Iqaluit'
  };

  const stateMap = {
    'alabama': 'America/Chicago',
    'alaska': 'America/Anchorage',
    'arizona': 'America/Phoenix',
    'arkansas': 'America/Chicago',
    'california': 'America/Los_Angeles',
    'colorado': 'America/Denver',
    'connecticut': 'America/New_York',
    'delaware': 'America/New_York',
    'district of columbia': 'America/New_York',
    'florida': 'America/New_York',
    'georgia': 'America/New_York',
    'hawaii': 'Pacific/Honolulu',
    'idaho': 'America/Denver',
    'illinois': 'America/Chicago',
    'indiana': 'America/New_York',
    'iowa': 'America/Chicago',
    'kansas': 'America/Chicago',
    'kentucky': 'America/New_York',
    'louisiana': 'America/Chicago',
    'maine': 'America/New_York',
    'maryland': 'America/New_York',
    'massachusetts': 'America/New_York',
    'michigan': 'America/New_York',
    'minnesota': 'America/Chicago',
    'mississippi': 'America/Chicago',
    'missouri': 'America/Chicago',
    'montana': 'America/Denver',
    'nebraska': 'America/Chicago',
    'nevada': 'America/Los_Angeles',
    'new hampshire': 'America/New_York',
    'new jersey': 'America/New_York',
    'new mexico': 'America/Denver',
    'new york': 'America/New_York',
    'north carolina': 'America/New_York',
    'north dakota': 'America/Chicago',
    'ohio': 'America/New_York',
    'oklahoma': 'America/Chicago',
    'oregon': 'America/Los_Angeles',
    'pennsylvania': 'America/New_York',
    'rhode island': 'America/New_York',
    'south carolina': 'America/New_York',
    'south dakota': 'America/Chicago',
    'tennessee': 'America/Chicago',
    'texas': 'America/Chicago',
    'utah': 'America/Denver',
    'vermont': 'America/New_York',
    'virginia': 'America/New_York',
    'washington': 'America/Los_Angeles',
    'west virginia': 'America/New_York',
    'wisconsin': 'America/Chicago',
    'wyoming': 'America/Denver'
  };

  if (country === 'CA' && provinceMap[state]) return provinceMap[state];
  if (country === 'US' && stateMap[state]) return stateMap[state];
  if (country === 'US' && usStateAbbrevMap[state]) return stateMap[usStateAbbrevMap[state]];
  if (country === 'CA' && caProvinceAbbrevMap[state]) return provinceMap[caProvinceAbbrevMap[state]];
  if (stateMap[state]) return stateMap[state];
  if (provinceMap[state]) return provinceMap[state];
  if (usStateAbbrevMap[state]) return stateMap[usStateAbbrevMap[state]];
  if (caProvinceAbbrevMap[state]) return provinceMap[caProvinceAbbrevMap[state]];
  return '';
}

const results = [];
let contacts;
try { contacts = await searchContacts(); } catch (err) { return [{ json: { action: 'error', error: 'search failed: ' + err.message } }]; }
if (contacts.length === 0) { return [{ json: { action: 'noop', message: 'no contacts with vapi_queue tag found' } }]; }

for (const contact of contacts) {
  const contactId = contact.id;
  const phone = contact.phone || '';
  const firstName = contact.firstName || contact.name || '';
  const timezone = resolveTimezone(contact);
  const removeFromQueue = hasContactTag(contact, 'vapi_voicemail') || hasContactTag(contact, 'vapi_qualified');

  if (removeFromQueue) {
    await removeTag(contactId);
    results.push({ contactId, firstName, action: 'skipped', reason: 'queue_removal_tag_present' });
    continue;
  }

  const cfMap = {};
  if (contact.customFields) { for (const cf of contact.customFields) { cfMap[cf.id] = cf.value; } }
  const enrichmentStatus = cfMap[ENRICHMENT_STATUS];

  try {
    if (TERMINAL_STATUSES.includes(enrichmentStatus)) {
      await removeTag(contactId);
      results.push({ contactId, firstName, action: 'skipped', reason: 'terminal_status: ' + enrichmentStatus });
      continue;
    }

    if (enrichmentStatus === 'enriched') {
      await removeTag(contactId);
      const enqData = await enqueueContact(contactId, phone, firstName, timezone);
      results.push({ contactId, firstName, action: 'enqueued', queue_id: enqData.queue_id, ok: enqData.ok === true, phone_present: !!phone, timezone_present: !!timezone });
      continue;
    }

    if (enrichmentStatus === 'queued') {
      results.push({ contactId, firstName, action: 'skipped', reason: 'enrichment_in_progress' });
      continue;
    }

    // No enrichment status yet — trigger enrichment AND enqueue immediately
    const enrichOk = await setEnrichFlag(contactId);
    if (!enrichOk) {
      results.push({ contactId, firstName, action: 'error', step: 'set_enrich', reason: 'GHL API failed' });
      continue;
    }
    const enqData = await enqueueContact(contactId, phone, firstName, timezone);
    await removeTag(contactId);
    results.push({
      contactId, firstName, action: 'enrich_triggered_enqueued',
      queue_id: enqData.queue_id, ok: enqData.ok === true, phone_present: !!phone, timezone_present: !!timezone
    });
  } catch (err) {
    results.push({ contactId, action: 'error', error: err.message });
  }
  await new Promise(r => setTimeout(r, 200));
}

return results.map(r => ({ json: r }));`
    }
  },
  output: [{ json: { action: '' } }]
});

export default workflow('bYk1Ai6MJLyhTsDZ', 'LT - Voice Queue Vapi Intake Poller')
  .add(scheduleTrigger)
  .to(processCode);
