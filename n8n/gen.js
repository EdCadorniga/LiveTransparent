const fs = require('fs');
const path = require('path');

const lines = [
  'const CFG = {',
  '  ghlApiBaseUrl: String($json.ghlApiBaseUrl || "https://services.leadconnectorhq.com").replace(/[/]+$/, ""),',
  '  ghlApiKey: String($json.ghlApiKey || "").trim(),',
  '  locationId: String($json.locationId || "").trim(),',
  '  unipileApiBaseUrl: String($json.unipileApiBaseUrl || "https://api13.unipile.com:14300/api/v1").replace(/[/]+$/, ""),',
  '  unipileApiKey: String($json.unipileApiKey || "").trim(),',
  '  unipileAccountId: String($json.unipileAccountId || "").trim(),',
  '  successTag: String($json.ghlSuccessTag || "linkedin_connection_requested").trim(),',
  '  cfName: String($json.linkedinCustomFieldName || "Apollo Person Linkedin URL").trim(),',
  '  defaultMessage: String($json.defaultMessage || "").trim(),',
  '  defaultDryRun: !!$json.defaultDryRun,',
  '  maxQueueSize: Math.max(1, Math.min(200, Number($json.maxQueueSize || 50))),',
  '  batchSize: Math.max(1, Number($json.batchSize || 10)),',
  '};',
  '',
  'function clean(v) { return String(v ?? "").trim(); }',
  '',
  'async function ghlSearchContacts(pageLimit, page) {',
  '  const body = {',
  '    locationId: CFG.locationId,',
  '    pageLimit: pageLimit,',
  '    page: page,',
  '    filters: [',
  '      {',
  '        field: "customFields.apollo_person_linkedin_url",',
  '        operator: "exists",',
  '      },',
  '    ],',
  '  };',
  '  return await this.helpers.httpRequest({',
  '    method: "POST",',
  '    url: CFG.ghlApiBaseUrl + "/contacts/search",',
  '    headers: { Authorization: "Bearer " + CFG.ghlApiKey, Version: "2021-07-28", "Content-Type": "application/json" },',
  '    body,',
  '    json: true,',
  '  });',
  '}',
  '',
'function getLinkedInUrl(contact) {',
'  const fields = Array.isArray(contact?.customFields) ? contact.customFields : [];',
'  for (const f of fields) {',
'    const v = String(f.value || "").trim();',
'    if (/linkedin\\.com/i.test(v)) return v;',
'  }',
'  return "";',
'}',
  '',
  'function hasTag(contact, tagName) {',
  '  const tags = Array.isArray(contact?.tags) ? contact.tags : [];',
  '  return tags.some((t) => (typeof t === "string" ? t : (t.name || t.value || "").trim()) === tagName);',
  '}',
  '',
  'function linkedinId(input) {',
  '  const raw = clean(input);',
  '  if (!raw) return "";',
  '  if (!/^https?:\\/\\//i.test(raw)) return decodeURIComponent(raw).replace(/^@/, "").replace(/[/]+$/, "").trim();',
  '  const w = raw.replace(/^https?:\\/\\//i, "");',
  '  const host = w.split("/")[0].split("?")[0].toLowerCase();',
  '  if (host !== "linkedin.com" && !host.endsWith(".linkedin.com")) throw new Error("Not LinkedIn: " + raw);',
  '  const path = w.slice(w.indexOf("/") >= 0 ? w.indexOf("/") : w.length).split("?")[0].split("#")[0];',
  '  const parts = path.split("/").filter(Boolean);',
  '  const idx = parts.findIndex((p) => p.toLowerCase() === "in");',
  '  const val = idx >= 0 && parts[idx + 1] ? parts[idx + 1] : parts[parts.length - 1];',
  '  return decodeURIComponent(val || "").replace(/^@/, "").replace(/[/]+$/, "").trim();',
  '}',
  '',
  'async function unipileReq(method, url, body, extraH = {}) {',
  '  const opts = { method, url, headers: { Accept: "application/json", "Content-Type": "application/json", ...extraH }, json: true };',
  '  if (body !== undefined) opts.body = body;',
  '  try { const d = await this.helpers.httpRequest(opts); return { ok: true, data: d }; }',
  '  catch (err) { return { ok: false, sc: err?.statusCode || null, data: err?.response?.body || err?.message || err }; }',
  '}',
  '',
  'const eligible = [];',
  'let scanned = 0;',
  'for (let page = 1; page <= 5; page++) {',
  '  const resp = await ghlSearchContacts(50, page);',
  '  const contacts = (resp && Array.isArray(resp.contacts)) ? resp.contacts : [];',
  '  if (contacts.length === 0) break;',
  '  for (const c of contacts) {',
  '    scanned++;',
  '    if (eligible.length >= CFG.maxQueueSize) break;',
  '    if (hasTag(c, CFG.successTag)) continue;',
'    const liUrl = getLinkedInUrl(c);',
'    if (!liUrl) continue;',
  '    eligible.push({ id: c.id, firstName: String(c.firstName || "").trim(), lastName: String(c.lastName || "").trim(), liUrl });',
  '  }',
  '  if (eligible.length >= CFG.maxQueueSize || contacts.length < 50) break;',
  '}',
  '',
  'const batch = eligible.slice(0, CFG.batchSize);',
  'const results = [];',
  'for (const contact of batch) {',
  '  const id = linkedinId(contact.liUrl);',
  '  if (!id) { results.push({ contactId: contact.id, status: "skipped", reason: "invalid_url" }); continue; }',
  '',
  '  const profile = await unipileReq("GET", CFG.unipileApiBaseUrl + "/users/" + encodeURIComponent(id) + "?account_id=" + encodeURIComponent(CFG.unipileAccountId), undefined, { "X-API-KEY": CFG.unipileApiKey });',
  '  const providerId = clean(profile.data?.provider_id || profile.data?.providerId || profile.data?.id || "");',
  '  const firstName = contact.firstName || clean(profile.data?.first_name || "there");',
  '',
  '  if (CFG.defaultDryRun || !profile.ok || !providerId) {',
  '    results.push({ contactId: contact.id, firstName, liUrl: contact.liUrl, identifier: id, status: CFG.defaultDryRun ? "dry_run" : "profile_failed", profileOk: profile.ok });',
  '    continue;',
  '  }',
  '',
  '  const msgRaw = CFG.defaultMessage.replace(/\\{first_name\\}/gi, firstName);',
  '  const msg = msgRaw.length > 300 ? msgRaw.slice(0, 300) : msgRaw;',
  '  const inv = await unipileReq("POST", CFG.unipileApiBaseUrl + "/users/invite", { account_id: CFG.unipileAccountId, provider_id: providerId, ...(msg ? { message: msg } : {}) }, { "X-API-KEY": CFG.unipileApiKey });',
  '',
  '  if (inv.ok) {',
  '    try {',
  '      await this.helpers.httpRequest({ method: "POST", url: CFG.ghlApiBaseUrl + "/contacts/" + encodeURIComponent(contact.id) + "/tags", headers: { Authorization: "Bearer " + CFG.ghlApiKey, Version: "2021-07-28", "Content-Type": "application/json" }, body: { tags: [CFG.successTag] }, json: true });',
  '    } catch (e) { }',
  '  }',
  '',
  '  results.push({ contactId: contact.id, firstName, liUrl: contact.liUrl, identifier: id, status: inv.ok ? "sent" : "invite_failed", inviteOk: inv.ok });',
  '}',
  '',
  'const sent = results.filter((r) => r.status === "sent").length;',
  'const dryRuns = results.filter((r) => r.status === "dry_run").length;',
  'const failed = results.filter((r) => r.status !== "sent" && r.status !== "dry_run").length;',
  '',
  'const today = new Date().toISOString().slice(0, 10);',
  'const prev = this.getWorkflowStaticData("global");',
  'const dailySent = (prev.date === today ? (prev.sentToday || 0) : 0) + sent;',
  'prev.date = today;',
  'prev.sentToday = dailySent;',
  '',
  'return [{ json: {',
  '  queue_found: eligible.length,',
  '  batch_size: batch.length,',
  '  sent,',
  '  dry_runs: dryRuns,',
  '  failed,',
  '  sent_today: dailySent,',
  '  results,',
  '  scanned,',
  '  note: CFG.defaultDryRun ? "DRY RUN MODE - no invites sent" : (sent + " invites sent"),',
  '} }];',
];

const jsCodeContent = lines.join('\n');
const escapedForTpl = jsCodeContent.replace(/\$/g, '\\$').replace(/`/g, '\\`');

const tsContent = `import { workflow, node, trigger } from '@n8n/workflow-sdk';

const schedule = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '0 15-21 * * 1-5' }] } },
    position: [240, 300],
  },
  output: [{}],
});

const manual = trigger({
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
          { id: 'wfn', name: 'workflowName', type: 'string', value: 'LT - GHL LinkedIn Connect Dispatcher' },
          { id: 'loc', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: 'gBase', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: 'gKey', name: 'ghlApiKey', type: 'string', value: 'pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86' },
          { id: 'uBase', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api13.unipile.com:14300/api/v1' },
          { id: 'uKey', name: 'unipileApiKey', type: 'string', value: 'WuuwgOoB.dLVVDvxyWrBVzoWib+g8qe+f2CuJKhtH09xuzykSheM=' },
          { id: 'uAcct', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: 'tag', name: 'ghlSuccessTag', type: 'string', value: 'linkedin_connection_requested' },
          { id: 'cfName', name: 'linkedinCustomFieldName', type: 'string', value: 'Apollo Person Linkedin URL' },
          { id: 'maxQ', name: 'maxQueueSize', type: 'number', value: 50 },
          { id: 'maxB', name: 'batchSize', type: 'number', value: 10 },
          { id: 'dRun', name: 'defaultDryRun', type: 'boolean', value: false },
          { id: 'msg', name: 'defaultMessage', type: 'string', value: 'Hey {first_name} — quick connect. John here with Transparent eCom.' },
        ],
      },
    },
    position: [464, 380],
  },
  output: [{ json: {} }],
});

const jsCode = \`${escapedForTpl}\`;

const dispatch = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Dispatch LinkedIn Requests',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode,
    },
    position: [688, 380],
  },
  output: [{ json: { queue_found: 50, batch_size: 10, sent: 0, dry_runs: 10, failed: 0, scanned: 250, note: 'LIVE MODE - ready to send' } }],
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
          { id: 'qf', name: 'queue_found', type: 'number', value: '={{ $json.queue_found }}' },
          { id: 'bs', name: 'batch_size', type: 'number', value: '={{ $json.batch_size }}' },
          { id: 's', name: 'sent', type: 'number', value: '={{ $json.sent }}' },
          { id: 'dr', name: 'dry_runs', type: 'number', value: '={{ $json.dry_runs }}' },
          { id: 'f', name: 'failed', type: 'number', value: '={{ $json.failed }}' },
          { id: 'st', name: 'sent_today', type: 'number', value: '={{ $json.sent_today }}' },
          { id: 'n', name: 'note', type: 'string', value: '={{ $json.note }}' },
        ],
      },
    },
    position: [912, 380],
  },
  output: [{ json: { queue_found: 50, batch_size: 10, sent: 0, dry_runs: 10, failed: 0, sent_today: 0, note: 'LIVE MODE - ready to send' } }],
});

export default workflow('lt-ghl-linkedin-dispatcher', 'LT - GHL LinkedIn Connect Dispatcher')
  .add(schedule)
  .to(config)
  .to(dispatch)
  .to(result)
  .add(manual)
  .to(config);
`;

const outPath = path.join(__dirname, 'lt-linkedin-dispatcher.ts');
fs.writeFileSync(outPath, tsContent);
console.log('Written', tsContent.length, 'bytes');
