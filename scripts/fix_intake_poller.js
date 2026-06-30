import { workflow, node, trigger, switchCase, expr } from '@n8n/workflow-sdk';

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Every 10 Minutes',
    parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 10 }] } },
    position: [0, -16]
  },
  output: [{}]
});

const configNode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Config',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "return [{ json: {\n  GHL_API_KEY: 'pit-b278b3ad-96bd-41fb-ba03-9f927039eb28',\n  GHL_LOCATION_ID: 'Zwz4relUXVPxx8uohnjV',\n  BASE_URL: 'https://services.leadconnectorhq.com',\n  ENRICHMENT_STATUS_FIELD_ID: 'rgYJ7UqoznGoe3WeUAtH',\n  ENRICH_PHONE_FIELD_ID: 'gdJDuZelIxEBE6n9i5Q6'\n} }];"
    },
    position: [224, -16]
  },
  output: [{ GHL_API_KEY: 'pit_xxx', GHL_LOCATION_ID: 'Zwz4relUXVPxx8uohnjV', BASE_URL: 'https://services.leadconnectorhq.com', ENRICHMENT_STATUS_FIELD_ID: 'rgYJ7UqoznGoe3WeUAtH', ENRICH_PHONE_FIELD_ID: 'gdJDuZelIxEBE6n9i5Q6' }]
});

const prepareSearch = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Prepare Search',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const cfg = $(\"Config\").item.json;\nreturn [{ json: { locationId: cfg.GHL_LOCATION_ID, pageLimit: 20, filters: [{ field: 'tags', operator: 'contains', value: 'vapi_queue' }] } }];"
    },
    position: [672, -16]
  },
  output: [{ locationId: 'loc_xxx', filters: [] }]
});

const searchGhl = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Search GHL Contacts',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const cfg = $("Config").item.json;
const baseUrl = String(cfg.BASE_URL || 'https://services.leadconnectorhq.com').replace(/\\/$/, '');
const apiKey = String(cfg.GHL_API_KEY || '').trim();
const locationId = String($json.locationId || cfg.GHL_LOCATION_ID || '').trim();
const pageLimit = Number($json.pageLimit || 20);
const filters = Array.isArray($json.filters) ? $json.filters : [];

if (!apiKey) throw new Error('Missing GHL API key');
if (!locationId) throw new Error('Missing GHL locationId');

async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}

const requestOptions = {
  method: 'POST',
  url: \`\${baseUrl}/contacts/search\`,
  headers: {
    Authorization: \`Bearer \${apiKey}\`,
    Version: '2021-07-28',
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  json: true,
  body: { locationId, pageLimit, filters },
};

try {
  const data = await doHttpRequest.call(this, requestOptions);
  return [{ json: { contacts: Array.isArray(data?.contacts) ? data.contacts : [], raw: data || {} } }];
} catch (err) {
  const status = err?.statusCode || err?.httpCode || err?.cause?.statusCode || 500;
  const detail = err?.response?.body || err?.message || String(err);
  throw new Error(\`GHL search failed: \${status} \${typeof detail === 'string' ? detail : JSON.stringify(detail)}\`);
}`
    },
    position: [896, -16]
  },
  output: [{ contacts: [] }]
});

const classifyContacts = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Classify Contacts',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const cfg = $(\"Config\").item.json;\nconst ENRICHMENT_STATUS = cfg.ENRICHMENT_STATUS_FIELD_ID;\nconst TERMINAL_STATUSES = ['no_match', 'error', 'callback_failed', 'callback_timeout'];\n\nfunction normalizeText(value) {\n  return String(value || '').trim().toLowerCase();\n}\n\nfunction getContactTags(contact) {\n  const rawTags = Array.isArray(contact.tags) ? contact.tags : [];\n  return rawTags\n    .map(tag => {\n      if (typeof tag === 'string') return tag;\n      if (tag && typeof tag === 'object') return tag.name || tag.label || tag.tag || tag.id || '';\n      return '';\n    })\n    .map(normalizeText)\n    .filter(Boolean);\n}\n\nfunction hasContactTag(contact, tagName) {\n  const target = normalizeText(tagName);\n  if (!target) return false;\n  return getContactTags(contact).includes(target);\n}\n\nconst contacts = $json.contacts || [];\nif (contacts.length === 0) { return [{ json: { action: 'noop', message: 'no contacts with vapi_queue tag found' } }]; }\n\nconst results = [];\nfor (const contact of contacts) {\n  const contactId = contact.id;\n  const phone = (contact.phone || '').trim();\n  const firstName = contact.firstName || contact.name || '';\n  const timezone = contact.timezone || '';\n  const removeFromQueue = hasContactTag(contact, 'vapi_voicemail') || hasContactTag(contact, 'vapi_qualified');\n  const cfMap = {};\n  if (contact.customFields) { for (const cf of contact.customFields) { cfMap[cf.id] = cf.value; } }\n  const enrichmentStatus = cfMap[ENRICHMENT_STATUS];\n\n  if (removeFromQueue) {\n    await removeTag(contactId);\n    results.push({ action: 'skipped', reason: 'queue_removal_tag_present', contact_id: contactId, first_name: firstName });\n    continue;\n  }\n\n  if (TERMINAL_STATUSES.includes(enrichmentStatus)) {\n    results.push({ action: 'skip', reason: 'terminal: ' + enrichmentStatus, contact_id: contactId, first_name: firstName });\n    continue;\n  }\n\n  if (enrichmentStatus === 'enriched') {\n    if (phone) {\n      results.push({ action: 'enqueue', contact_id: contactId, first_name: firstName, phone_e164: phone, lead_timezone: timezone, campaign_id: 'default' });\n    } else {\n      results.push({ action: 'skip', reason: 'enriched_no_phone', contact_id: contactId, first_name: firstName });\n    }\n    continue;\n  }\n\n  if (enrichmentStatus === 'queued') {\n    results.push({ action: 'waiting', reason: 'enrichment_in_progress', contact_id: contactId, first_name: firstName });\n    continue;\n  }\n\n  results.push({ action: 'enrich', contact_id: contactId, first_name: firstName, phone_e164: phone || '', lead_timezone: timezone });\n}\n\nreturn results.filter(Boolean).map(r => ({ json: r }));"
    },
    position: [1120, -16]
  },
  output: [{ action: 'enqueue', contact_id: 'abc', first_name: 'John' }]
});

const routeAction = switchCase({
  version: 3.4,
  config: {
    name: 'Route Action',
    parameters: {
      rules: {
        values: [
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
              conditions: [
                { leftValue: '={{$json.action}}', rightValue: 'enqueue', operator: { type: 'string', operation: 'equals' }, id: 'switch-enqueue' }
              ],
              combinator: 'and'
            }
          },
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
              conditions: [
                { leftValue: '={{$json.action}}', rightValue: 'enrich', operator: { type: 'string', operation: 'equals' }, id: 'switch-enrich' }
              ],
              combinator: 'and'
            }
          },
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
              conditions: [
                { leftValue: '={{$json.action}}', rightValue: 'skip', operator: { type: 'string', operation: 'equals' }, id: 'switch-skip' }
              ],
              combinator: 'and'
            }
          },
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
              conditions: [
                { leftValue: '={{$json.action}}', rightValue: 'waiting', operator: { type: 'string', operation: 'equals' }, id: 'switch-waiting' }
              ],
              combinator: 'and'
            }
          },
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 3 },
              conditions: [
                { leftValue: '={{$json.action}}', rightValue: 'noop', operator: { type: 'string', operation: 'equals' }, id: 'switch-noop' }
              ],
              combinator: 'and'
            }
          }
        ]
      },
      options: {}
    },
    position: [1344, -16]
  }
});

const postgresInsertQueue = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Postgres - Insert Queue',
    parameters: {
      operation: 'executeQuery',
      query: "INSERT INTO voice_call_queue (queue_id, contact_id, first_name, phone_e164, campaign_id, lead_timezone) VALUES (gen_random_uuid(), $1, $2, $3, $4, $5) RETURNING queue_id, contact_id, first_name;",
      options: {
        queryBatching: 'independently',
        queryReplacement: expr('={{ [$json.contact_id, $json.first_name, $json.phone_e164, $json.campaign_id, $json.lead_timezone] }}')
      }
    },
    position: [1568, -208]
  },
  output: [{ queue_id: 1, contact_id: 'abc', first_name: 'John' }]
});

const transformPostgresOutput = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Transform Postgres Output',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const items = $input.all();\nreturn items.map(({ json }, index) => {\n  let contact_id = json.contact_id;\n  if (!contact_id && json.rows && json.rows.length > 0) {\n    contact_id = json.rows[0].contact_id;\n  }\n  if (!contact_id) {\n    throw new Error('Could not extract contact_id from Postgres output item ' + index + '. Keys: ' + Object.keys(json).join(', '));\n  }\n  return { json: { contact_id } };\n});"
    },
    position: [1568, 0]
  },
  output: [{ contact_id: 'abc' }]
});

const removeTagEnqueued = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Remove Tag - Enqueued',
    parameters: {
      method: 'DELETE',
      url: expr('={{ $("Config").item.json.BASE_URL + "/contacts/" + $json.contact_id + "/tags" }}'),
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $("Config").item.json.GHL_API_KEY }}') },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('={"tags":["vapi_queue"]}'),
      options: {}
    },
    position: [1792, -208]
  },
  output: [{ contact_id: 'abc', tag_removed: true }]
});

const cleanupDeletedContact = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Remove Tag - Enriching',
    parameters: {
      method: 'DELETE',
      url: expr('={{ $("Config").item.json.BASE_URL + "/contacts/" + $json.contact_id + "/tags" }}'),
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $("Config").item.json.GHL_API_KEY }}') },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('={"tags":["vapi_queue"]}'),
      options: {}
    },
    position: [1568, 192]
  },
  output: [{ contact_id: 'abc', tag_removed: true }]
});

const triggerApolloNode = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Trigger Apollo Enrichment',
    parameters: {
      method: 'PUT',
      url: expr('={{ $("Config").item.json.BASE_URL + "/contacts/" + $json.contact_id }}'),
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $("Config").item.json.GHL_API_KEY }}') },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('={{ { customFields: [{ id: "gdJDuZelIxEBE6n9i5Q6", value: "Yes" }] } }}')
    },
    position: [1568, -16]
  },
  output: [{ status: 'ok' }]
});

const removeTagSkipped = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Remove Tag - Skipped',
    parameters: {
      method: 'DELETE',
      url: expr('={{ $("Config").item.json.BASE_URL + "/contacts/" + $json.contact_id + "/tags" }}'),
      sendHeaders: true,
      specifyHeaders: 'keypair',
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $("Config").item.json.GHL_API_KEY }}') },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('={"tags":["vapi_queue"]}'),
      options: {}
    },
    position: [1568, 176]
  },
  output: [{ contact_id: 'abc', tag_removed: true }]
});

export default workflow('bYk1Ai6MJLyhTsDZ', 'LT - Voice Queue Vapi Intake Poller')
  .add(scheduleTrigger)
  .to(configNode)
  .to(prepareSearch)
  .to(searchGhl)
  .to(classifyContacts)
  .to(routeAction
    .onCase(0, postgresInsertQueue.to(transformPostgresOutput.to(removeTagEnqueued)))
    .onCase(1, triggerApolloNode.to(cleanupDeletedContact))
    .onCase(2, removeTagSkipped));
