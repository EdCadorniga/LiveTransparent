import { workflow, node, trigger, newCredential, expr } from '@n8n/workflow-sdk';

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: { name: 'Schedule Trigger', position: [240, 160], parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 1440 }] } } },
  output: [{}]
});

const manualTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [240, 320] },
  output: [{}]
});

const config = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    position: [480, 240],
    parameters: {
      mode: 'manual',
      assignments: { assignments: [
        { id: 'workflowName', name: 'workflowName', type: 'string', value: 'LT - GHL Daily Leads Ingest' },
        { id: 'locationId', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
        { id: 'locationName', name: 'locationName', type: 'string', value: 'Live Transparent' },
        { id: 'timezone', name: 'timezone', type: 'string', value: 'America/Los_Angeles' },
        { id: 'apiBaseUrl', name: 'apiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
        { id: 'apiKey', name: 'apiKey', type: 'string', value: 'pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86' },
        { id: 'sourceSystem', name: 'sourceSystem', type: 'string', value: 'ghl' },
        { id: 'pageSize', name: 'pageSize', type: 'number', value: 50 },
        { id: 'overlapDays', name: 'overlapDays', type: 'number', value: 7 },
        { id: 'staleAfterHours', name: 'staleAfterHours', type: 'number', value: 48 },
        { id: 'maxPages', name: 'maxPages', type: 'number', value: 10 },
        { id: 'writeMode', name: 'writeMode', type: 'boolean', value: true }
      ] }
    }
  },
  output: [{ workflowName: 'LT - GHL Daily Leads Ingest', locationId: 'Zwz4relUXVPxx8uohnjV', apiKey: 'pit-xxx', sourceSystem: 'ghl' }]
});

const fetchNormalizeLeads = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Fetch + Normalize Leads',
    position: [740, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      jsCode: `const cfg = $node['Config'].json || {};
const workflowName = String(cfg.workflowName || 'LT - GHL Daily Leads Ingest').trim();
const locationId = String(cfg.locationId || '').trim();
const apiBaseUrl = String(cfg.apiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\\/$/, '');
const apiKey = String(cfg.apiKey || '').trim();
const pageSize = Math.max(10, Math.min(100, Number(cfg.pageSize || 100)));
const maxPages = Math.max(1, Math.min(1000, Number(cfg.maxPages || 1000)));
const timezone = String(cfg.timezone || 'America/Los_Angeles');
const overlapDays = Math.max(0, Math.min(30, Number(cfg.overlapDays || 3)));
const runStartedAt = new Date().toISOString();

if (!locationId) throw new Error('Missing locationId');
if (!apiKey) throw new Error('Missing GHL apiKey');

function localDateParts(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(date);
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return \`\${map.year}-\${map.month}-\${map.day}\`;
}
function shiftDate(dateStr, days) {
  const d = new Date(\`\${dateStr}T12:00:00Z\`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}
function str(v) { return String(v ?? '').trim(); }
function clean(v) { return str(v); }
function normalizeTags(value) {
  if (Array.isArray(value)) return value.map((v) => clean(typeof v === 'string' ? v : v?.name || v?.value || v)).filter(Boolean);
  if (typeof value === 'string') return value.split(',').map((v) => clean(v)).filter(Boolean);
  return [];
}
function customFieldsMap(contact) {
  const fields = Array.isArray(contact?.customFields)
    ? contact.customFields
    : Array.isArray(contact?.customFields?.fields)
      ? contact.customFields.fields
      : Array.isArray(contact?.customFields?.data)
        ? contact.customFields.data
        : [];
  const map = new Map();
  for (const item of fields) {
    const name = clean(item?.name || item?.label || item?.fieldName || item?.key || item?.field_key || '');
    const value = item?.value ?? item?.field_value ?? item?.fieldValue ?? '';
    if (name) map.set(name.toLowerCase(), value);
  }
  return map;
}
function getField(contact, name) {
  const map = customFieldsMap(contact);
  return clean(map.get(String(name).trim().toLowerCase()) || '');
}
function contactName(contact) {
  return clean(contact?.contactName || contact?.name || [contact?.firstName, contact?.lastName].filter(Boolean).join(' '));
}
function pickEmail(contact) { return clean(contact?.email || contact?.emailAddress || contact?.primaryEmail || ''); }
function pickPhone(contact) { return clean(contact?.phone || contact?.phoneNumber || contact?.primaryPhone || ''); }
function firstNonEmpty(...values) { for (const v of values) { const s = clean(v); if (s) return s; } return ''; }
async function apiGet(path) {
  const options = {
    method: 'GET',
    url: \`\${apiBaseUrl}\${path}\`,
    headers: {
      Authorization: \`Bearer \${apiKey}\`,
      Version: '2021-07-28',
      Accept: 'application/json',
    },
    json: true,
  };
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      return await this.helpers.httpRequest(options);
    } catch (error) {
      const status = Number(error?.statusCode || error?.httpCode || error?.response?.status || error?.cause?.statusCode || 0);
      if (status !== 429 || attempt === 3) throw error;
      const retryAfter = Number(error?.response?.headers?.['retry-after'] || error?.headers?.['retry-after'] || 0);
      const delayMs = retryAfter > 0 ? Math.max(1000, retryAfter * 1000) : 1000 * (2 ** attempt);
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
}
function getContacts(data) {
  if (Array.isArray(data?.contacts)) return data.contacts;
  if (Array.isArray(data?.data?.contacts)) return data.data.contacts;
  if (Array.isArray(data?.data)) return data.data;
  if (Array.isArray(data)) return data;
  return [];
}

const runReportDate = localDateParts();
function resolveContactReportDate(contact) {
  const sourceCreatedAt = firstNonEmpty(contact?.createdAt, contact?.created_at, contact?.dateAdded, contact?.date_added);
  if (!sourceCreatedAt) return runReportDate;
  const dt = new Date(sourceCreatedAt);
  return Number.isNaN(dt.getTime()) ? runReportDate : dt.toISOString().slice(0, 10);
}
const sourceWindowEnd = runReportDate;
const sourceWindowStart = shiftDate(runReportDate, -overlapDays);
const batchId = \`\${workflowName}__\${runReportDate}__\${Date.now()}\`;
const rows = [];

let startAfterId = '';
for (let page = 0; page < maxPages; page += 1) {
  let path = \`/contacts/?locationId=\${encodeURIComponent(locationId)}&limit=\${pageSize}\`;
  if (startAfterId) path += \`&startAfterId=\${encodeURIComponent(startAfterId)}\`;
  const response = await apiGet.call(this, path);
  const contacts = getContacts(response);
  if (!contacts.length) break;

  for (const contact of contacts) {
    const contactId = clean(contact?.id || contact?.contactId || contact?._id || '');
    if (!contactId) continue;
    const dims = {
      contact_id: contactId,
      contact_name: contactName(contact),
      first_name: clean(contact?.firstName || contact?.first_name || ''),
      last_name: clean(contact?.lastName || contact?.last_name || ''),
      email: pickEmail(contact),
      phone: pickPhone(contact),
      company_name: firstNonEmpty(contact?.companyName, contact?.company_name, getField(contact, 'Company Name for Emails')),
      source: clean(contact?.source || contact?.leadSource || ''),
      tags: normalizeTags(contact?.tags).join(', '),
      lead_temperature: getField(contact, 'Lead Temperature'),
      warm_source: getField(contact, 'Warm Source'),
      warm_trigger_type: getField(contact, 'Warm Trigger Type'),
      lt_last_routing_channel: getField(contact, 'LT Last Routing Channel'),
      lt_last_routing_reason: getField(contact, 'LT Last Routing Reason'),
      lt_last_routed_at: getField(contact, 'LT Last Routed At'),
      lt_route_lock_until: getField(contact, 'LT Route Lock Until'),
      lt_routing_priority: getField(contact, 'LT Routing Priority'),
      lt_last_event_fingerprint: getField(contact, 'LT Last Event Fingerprint'),
      lt_last_event_at: getField(contact, 'LT Last Event At'),
      utm_source_first: getField(contact, 'UTM Source First'),
      utm_medium_first: getField(contact, 'UTM Medium First'),
      utm_campaign_first: getField(contact, 'UTM Campaign First'),
      utm_content_first: getField(contact, 'UTM Content First'),
      utm_term_first: getField(contact, 'UTM Term First'),
      utm_landing_page_first: getField(contact, 'UTM Landing Page First'),
      utm_source_last: getField(contact, 'UTM Source Last'),
      utm_medium_last: getField(contact, 'UTM Medium Last'),
      utm_campaign_last: getField(contact, 'UTM Campaign Last'),
      utm_content_last: getField(contact, 'UTM Content Last'),
      utm_term_last: getField(contact, 'UTM Term Last'),
      utm_landing_page_last: getField(contact, 'UTM Landing Page Last'),
      company_name_for_emails: getField(contact, 'Company Name for Emails'),
      em_company_operating_state: getField(contact, 'Em_Company_Operating_State'),
      em_company_research_snippet: getField(contact, 'Em_Company_Research_Snippet'),
      em_cannabis_marketing_signal: getField(contact, 'Em_Cannabis_Marketing_Signal'),
      em_email4_personalization_ready: getField(contact, 'Em_Email4_Personalization_Ready'),
      em_email4_personalization_reason: getField(contact, 'Em_Email4_Personalization_Reason'),
    };

    rows.push({
      report_date: resolveContactReportDate(contact),
      source_system: 'ghl',
      source_key: \`contact:\${contactId}\`,
      source_window_start: sourceWindowStart,
      source_window_end: sourceWindowEnd,
      payload_json: contact,
      dimensions_json: dims,
      metrics_json: { contact_count: 1 },
      batch_id: batchId,
      run_id: null,
      loaded_at: new Date().toISOString(),
    });
  }

  const meta = response?.meta || {};
  const nextStartAfterId = clean(meta.startAfterId || meta.nextStartAfterId || '');
  if (nextStartAfterId) startAfterId = nextStartAfterId;
  else if (contacts.length >= pageSize) startAfterId = clean(contacts[contacts.length - 1]?.id || contacts[contacts.length - 1]?._id || '');
  else break;
  await new Promise((resolve) => setTimeout(resolve, 500));
}

return rows.map((row) => ({ json: row }));`
    }
  },
  output: [{ report_date: '2026-04-26', source_system: 'ghl', source_key: 'contact:123', batch_id: 'batch1' }]
});

const upsertRawLeads = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert Raw Leads',
    position: [1040, 240],
    parameters: {
      operation: 'executeQuery',
      query: 'INSERT INTO report_raw_ghl_contacts (report_date, source_system, source_key, source_window_start, source_window_end, payload_json, dimensions_json, metrics_json, batch_id, run_id, loaded_at) VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb, $8::jsonb, $9, $10, $11::timestamptz) ON CONFLICT (source_system, report_date, source_key) DO UPDATE SET source_window_start = EXCLUDED.source_window_start, source_window_end = EXCLUDED.source_window_end, payload_json = EXCLUDED.payload_json, dimensions_json = EXCLUDED.dimensions_json, metrics_json = EXCLUDED.metrics_json, batch_id = EXCLUDED.batch_id, run_id = EXCLUDED.run_id, loaded_at = EXCLUDED.loaded_at;',
      options: {
        queryBatching: 'independently',
        queryReplacement: expr('{{ [ $json.report_date, $json.source_system, $json.source_key, $json.source_window_start, $json.source_window_end, JSON.stringify($json.payload_json || {}), JSON.stringify($json.dimensions_json || {}), JSON.stringify($json.metrics_json || {}), $json.batch_id, null, $json.loaded_at ] }}')
      }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ count: 1 }]
});

const summarizeRun = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Summarize Run',
    position: [1280, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      jsCode: `const cfg = $node['Config'].json || {};
const rows = $items('Fetch + Normalize Leads').map((i) => i.json || {});
const runReportDate = new Date().toISOString().slice(0, 10);
const reportDate = rows.reduce((max, row) => row?.report_date && row.report_date > max ? row.report_date : max, runReportDate);
const batchId = rows[0]?.batch_id || \`\${String(cfg.workflowName || 'LT - GHL Daily Leads Ingest')}__\${Date.now()}\`;
const now = new Date().toISOString();
const rowCount = rows.length;
return [{
  json: {
    workflow_name: String(cfg.workflowName || 'LT - GHL Daily Leads Ingest'),
    source_system: 'ghl',
    report_date: reportDate,
    batch_id: batchId,
    status: rowCount ? 'success' : 'empty',
    started_at: rows[0]?.loaded_at || now,
    finished_at: now,
    row_count: rowCount,
    error_count: 0,
    retry_count: 0,
    cursor_value: rows[rowCount - 1]?.source_key || '',
    error_message: null,
    metadata: {
      workflow: String(cfg.workflowName || 'LT - GHL Daily Leads Ingest'),
      snapshot: 'contacts',
      timezone: String(cfg.timezone || 'America/Los_Angeles'),
      source_window_start: rows[0]?.source_window_start || '',
      source_window_end: rows[0]?.source_window_end || '',
      contact_count: rowCount,
    },
  },
}];`
    }
  },
  output: [{ workflow_name: 'LT - GHL Daily Leads Ingest', source_system: 'ghl', report_date: '2026-04-26', status: 'success', row_count: 50 }]
});

const insertSyncRun = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Insert Sync Run',
    position: [1520, 240],
    parameters: {
      operation: 'executeQuery',
      query: 'INSERT INTO report_sync_runs (workflow_name, source_system, report_date, batch_id, status, started_at, finished_at, row_count, error_count, retry_count, cursor_value, error_message, metadata) VALUES ($1, $2, $3, $4, $5, $6::timestamptz, $7::timestamptz, $8, $9, $10, $11, $12, $13::jsonb);',
      options: {
        queryReplacement: expr('{{ [ $json.workflow_name, $json.source_system, $json.report_date, $json.batch_id, $json.status, $json.started_at, $json.finished_at, $json.row_count, $json.error_count, $json.retry_count, $json.cursor_value, $json.error_message, JSON.stringify($json.metadata || {}) ] }}')
      }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ count: 1 }]
});

const upsertWatermark = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert Watermark',
    position: [1760, 240],
    parameters: {
      operation: 'executeQuery',
      query: 'INSERT INTO report_sync_watermarks (workflow_name, source_system, watermark_key, watermark_value, updated_at) VALUES ($1, $2, $3, $4, NOW()) ON CONFLICT (workflow_name, source_system, watermark_key) DO UPDATE SET watermark_value = EXCLUDED.watermark_value, updated_at = NOW();',
      options: {
        queryReplacement: expr('{{ [ $("Summarize Run").item.json.workflow_name, $("Summarize Run").item.json.source_system, "last_complete_report_date", $("Summarize Run").item.json.report_date ] }}')
      }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ count: 1 }]
});

const upsertSourceHealth = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Upsert Source Health',
    position: [2000, 240],
    parameters: {
      operation: 'executeQuery',
      query: 'INSERT INTO report_source_health (source_system, status, last_success_at, last_attempt_at, last_row_count, stale_after_hours, last_error, metadata, updated_at) VALUES ($1, $2, $3::timestamptz, $4::timestamptz, $5, $6, $7, $8::jsonb, NOW()) ON CONFLICT (source_system) DO UPDATE SET status = EXCLUDED.status, last_success_at = EXCLUDED.last_success_at, last_attempt_at = EXCLUDED.last_attempt_at, last_row_count = EXCLUDED.last_row_count, stale_after_hours = EXCLUDED.stale_after_hours, last_error = EXCLUDED.last_error, metadata = EXCLUDED.metadata, updated_at = NOW();',
      options: {
        queryReplacement: expr('{{ [ $("Summarize Run").item.json.source_system, $("Summarize Run").item.json.status, $("Summarize Run").item.json.finished_at, $("Summarize Run").item.json.finished_at, $("Summarize Run").item.json.row_count, 48, null, JSON.stringify({ workflow: $("Summarize Run").item.json.workflow_name, source: "ghl", snapshot: "contacts" }) ] }}')
      }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ count: 1 }]
});

const result = node({
  type: 'n8n-nodes-base.set',
  version: 2,
  config: {
    name: 'Result',
    position: [2240, 240],
    parameters: {
      values: {
        string: [
          { name: 'status', value: expr('{{ $("Summarize Run").item.json.status }}') },
          { name: 'workflow_name', value: expr('{{ $("Summarize Run").item.json.workflow_name }}') },
          { name: 'source_system', value: expr('{{ $("Summarize Run").item.json.source_system }}') },
          { name: 'report_date', value: expr('{{ $("Summarize Run").item.json.report_date }}') },
          { name: 'batch_id', value: expr('{{ $("Summarize Run").item.json.batch_id }}') },
          { name: 'window_start', value: expr('{{ $("Summarize Run").item.json.metadata.source_window_start }}') },
          { name: 'window_end', value: expr('{{ $("Summarize Run").item.json.metadata.source_window_end }}') }
        ],
        number: [
          { name: 'row_count', value: expr('{{ $("Summarize Run").item.json.row_count }}') },
          { name: 'error_count', value: expr('{{ $("Summarize Run").item.json.error_count }}') }
        ]
      }
    }
  },
  output: [{ status: 'success', workflow_name: 'LT - GHL Daily Leads Ingest', row_count: 50 }]
});

export default workflow('lt-ghl-daily-leads-ingest', 'LT - GHL Daily Leads Ingest')
  .add(scheduleTrigger)
  .to(config)
  .add(manualTrigger)
  .to(config)
  .to(fetchNormalizeLeads)
  .to(upsertRawLeads)
  .to(summarizeRun)
  .to(insertSyncRun)
  .to(upsertWatermark)
  .to(upsertSourceHealth)
  .to(result);

