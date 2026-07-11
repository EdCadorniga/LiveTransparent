import { workflow, node, trigger } from '@n8n/workflow-sdk';
import { SOCIAL_OUTREACH_TEMPLATES } from './workflows/social_outreach_templates';

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

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook Trigger',
    parameters: {
      httpMethod: 'POST',
      path: 'lt-ghl-linkedin-connect-dispatcher',
      responseMode: 'lastNode',
      options: {},
    },
    position: [240, 140],
  },
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
          { id: 'wfn', name: 'workflowName', type: 'string', value: 'LT - GHL LinkedIn Connect Dispatcher (Unipile)' },
          { id: 'loc', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: 'gBase', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: 'gKey', name: 'ghlApiKey', type: 'string', value: 'pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86' },
          { id: 'uBase', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: 'uKey', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: 'uAcct', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: 'tag', name: 'ghlSuccessTag', type: 'string', value: 'linkedin_connection_requested' },
          { id: 'cfName', name: 'linkedinCustomFieldName', type: 'string', value: 'Apollo Person Linkedin URL' },
          { id: 'maxQ', name: 'maxQueueSize', type: 'number', value: 50 },
          { id: 'maxB', name: 'batchSize', type: 'number', value: 15 },
          { id: 'dailyLimit', name: 'dailyLimit', type: 'number', value: 60 },
          { id: 'stateUrl', name: 'connectionStateUpsertUrl', type: 'string', value: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert' },
          { id: 'dRun', name: 'defaultDryRun', type: 'boolean', value: false },
          { id: 'msg', name: 'defaultMessage', type: 'string', value: SOCIAL_OUTREACH_TEMPLATES.linkedin.invite },
        ],
      },
    },
    position: [464, 380],
  },
  output: [{ json: {} }],
});

const jsCode = `const CFG = {
  workflowName: String(\$json.workflowName || "LT - GHL LinkedIn Connect Dispatcher (Unipile)").trim(),
  ghlApiBaseUrl: String(\$json.ghlApiBaseUrl || "https://services.leadconnectorhq.com").replace(/[/]+\$/, ""),
  ghlApiKey: String(\$json.ghlApiKey || "").trim(),
  locationId: String(\$json.locationId || "").trim(),
  unipileApiBaseUrl: String(\$json.unipileApiBaseUrl || "https://api42.unipile.com:17256/api/v1").replace(/[/]+\$/, ""),
  unipileApiKey: String(\$json.unipileApiKey || "").trim(),
  unipileAccountId: String(\$json.unipileAccountId || "").trim(),
  successTag: String(\$json.ghlSuccessTag || "linkedin_connection_requested").trim(),
  linkedinCustomFieldName: String(\$json.linkedinCustomFieldName || "Apollo Person Linkedin URL").trim(),
  defaultMessage: String(\$json.defaultMessage || "").trim(),
  defaultDryRun: !!\$json.defaultDryRun,
  maxQueueSize: Math.max(1, Math.min(200, Number(\$json.maxQueueSize || 50))),
  batchSize: Math.max(1, Number(\$json.batchSize || 15)),
  dailyLimit: Math.max(1, Number(\$json.dailyLimit || 60)),
  connectionStateUpsertUrl: String(\$json.connectionStateUpsertUrl || "https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert").trim(),
};

function clean(v) {
  if (v == null) return "";
  if (typeof v === "string") return v.normalize("NFC").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  if (typeof v === "number" || typeof v === "boolean" || typeof v === "bigint") return String(v);
  try { return JSON.stringify(v).normalize("NFC").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim(); } catch (e) { return String(v).normalize("NFC").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim(); }
}

function extractConversationItems(resp) {
  if (!resp) return [];
  if (Array.isArray(resp.conversations)) return resp.conversations;
  if (Array.isArray(resp.items)) return resp.items;
  if (Array.isArray(resp.data?.conversations)) return resp.data.conversations;
  if (Array.isArray(resp.data?.items)) return resp.data.items;
  if (Array.isArray(resp.data)) return resp.data;
  return [];
}

function describeError(err) {
  if (err instanceof Error) return err.stack || err.message || err.name || "Unknown error";
  if (typeof err === "string") return err;
  if (err && typeof err === "object") {
    const parts = [];
    if ("message" in err && err.message) parts.push(String(err.message));
    if ("statusCode" in err && err.statusCode !== undefined) parts.push("statusCode=" + String(err.statusCode));
    if ("code" in err && err.code !== undefined) parts.push("code=" + String(err.code));
    const body = err?.response?.body ?? err?.body ?? err?.data;
    if (body !== undefined) {
      if (typeof body === "string") parts.push("body=" + body);
      else {
        try { parts.push("body=" + JSON.stringify(body)); } catch (e) { parts.push("body=" + String(body)); }
      }
    }
    if (parts.length > 0) return parts.join(" | ");
    try { return JSON.stringify(err); } catch (e) { return String(err); }
  }
  return String(err);
}

async function ghlSearchContacts(pageLimit, page, fieldName) {
  const body = {
    locationId: CFG.locationId,
    pageLimit: pageLimit,
    page: page,
    filters: [
      {
        field: fieldName,
        operator: "exists",
      },
    ],
  };
  return await this.helpers.httpRequest({
    method: "POST",
    url: CFG.ghlApiBaseUrl + "/contacts/search",
    headers: { Authorization: "Bearer " + CFG.ghlApiKey, Version: "2021-07-28", "Content-Type": "application/json" },
    body,
    json: true,
  });
}

async function hasInboundConversation(contactId) {
  if (!contactId) return { blocked: true, reason: "missing_contact_id" };
  try {
    const resp = await this.helpers.httpRequest({
      method: "GET",
      url: CFG.ghlApiBaseUrl + "/conversations/search?contactId=" + encodeURIComponent(contactId) + "&lastMessageDirection=inbound&status=all&limit=1",
      headers: {
        Authorization: "Bearer " + CFG.ghlApiKey,
        Version: "2021-07-28",
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      json: true,
    });
    const items = extractConversationItems(resp);
    return { blocked: items.length > 0, reason: items.length > 0 ? "inbound_conversation" : "" };
  } catch (err) {
    return { blocked: true, reason: "conversation_check_failed", error: describeError(err) };
  }
}

function extractUrls(raw) {
  const value = clean(raw);
  if (!value) return [];
  return Array.from(new Set((value.match(/https?:\\/\\/[^\\s,]+/gi) || []).map((u) => clean(u).replace(/[).,;]+\$/, ""))));
}

function normalizeLinkedInFieldName(input) {
  return clean(input).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function getLinkedInUrl(contact) {
  const fields = Array.isArray(contact?.customFields) ? contact.customFields : [];
  const preferredName = normalizeLinkedInFieldName(CFG.linkedinCustomFieldName || "");
  const fieldAliases = new Set([
    "apollo_person_linkedin_url",
    "em_contact_linkedin_urls",
  ]);
  if (preferredName) fieldAliases.add(preferredName);
  for (const f of fields) {
    const name = normalizeLinkedInFieldName(f?.name || f?.label || f?.key || "");
    if (!fieldAliases.has(name)) continue;
    const urls = extractUrls(f.value).filter((u) => /linkedin\\.com/i.test(u));
    if (urls.length > 0) return urls[0];
  }
  for (const f of fields) {
    const urls = extractUrls(f.value).filter((u) => /linkedin\\.com/i.test(u));
    if (urls.length > 0) return urls[0];
  }
  return "";
}

function hasTag(contact, tagName) {
  const tags = Array.isArray(contact?.tags) ? contact.tags : [];
  return tags.some((t) => (typeof t === "string" ? t : (t.name || t.value || "").trim()) === tagName);
}

function linkedinId(input) {
  const raw = clean(input);
  if (!raw) return "";
  const urls = extractUrls(raw);
  const linkedinUrl = urls.find((u) => /linkedin\\.com/i.test(u));
  const candidate = linkedinUrl || raw;
  if (!/^https?:\\/\\//i.test(candidate)) return decodeURIComponent(candidate).replace(/^@/, "").replace(/[/]+\$/, "").trim();
  const w = candidate.replace(/^https?:\\/\\//i, "");
  const host = w.split("/")[0].split("?")[0].toLowerCase();
  if (host !== "linkedin.com" && !host.endsWith(".linkedin.com")) {
    if (linkedinUrl) return linkedinId(linkedinUrl);
    throw new Error("Not LinkedIn: " + raw);
  }
  const path = w.slice(w.indexOf("/") >= 0 ? w.indexOf("/") : w.length).split("?")[0].split("#")[0];
  const parts = path.split("/").filter(Boolean);
  const idx = parts.findIndex((p) => p.toLowerCase() === "in");
  const val = idx >= 0 && parts[idx + 1] ? parts[idx + 1] : parts[parts.length - 1];
  return decodeURIComponent(val || "").replace(/^@/, "").replace(/[/]+\$/, "").trim();
}

async function unipileReq(method, url, body, extraH = {}) {
  const opts = { method, url, headers: { Accept: "application/json", "Content-Type": "application/json", ...extraH }, json: true };
  if (body !== undefined) opts.body = body;
  try { const d = await this.helpers.httpRequest(opts); return { ok: true, data: d }; }
  catch (err) { return { ok: false, sc: err?.statusCode || null, data: err?.response?.body || err?.message || err }; }
}

async function sendFailureAlert(error, context = {}) {
  const alertEmail = "ed@livetransparent.com";
  const alertText = [
    "LinkedIn dispatcher failed",
    "Workflow: " + CFG.workflowName,
    "Error: " + describeError(error),
    context.contactId ? "Contact ID: " + clean(context.contactId) : "",
    context.liUrl ? "LinkedIn URL: " + clean(context.liUrl) : "",
    context.details ? "Details: " + clean(context.details) : "",
    context.scanned !== undefined ? "Scanned: " + clean(context.scanned) : "",
    context.queueSize !== undefined ? "Queue size: " + clean(context.queueSize) : "",
    error?.stack ? "Stack: " + clean(error.stack) : "",
  ].filter(Boolean).join("\\n");

  const search = await this.helpers.httpRequest({
    method: "POST",
    url: CFG.ghlApiBaseUrl + "/contacts/search",
    headers: {
      Authorization: "Bearer " + CFG.ghlApiKey,
      Version: "2021-07-28",
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: {
      locationId: CFG.locationId,
      pageLimit: 10,
      page: 1,
      filters: [{ field: "email", operator: "contains", value: alertEmail }],
    },
    json: true,
  });

  const alertContact = Array.isArray(search?.contacts) ? search.contacts.find((c) => clean(c?.email || c?.contactEmail || "").toLowerCase() === alertEmail) || search.contacts[0] : null;
  const contactId = clean(alertContact?.id || "");
  if (!contactId) throw new Error("Unable to resolve alert contact for " + alertEmail);

  await this.helpers.httpRequest({
    method: "POST",
    url: CFG.ghlApiBaseUrl + "/conversations/messages",
    headers: {
      Authorization: "Bearer " + CFG.ghlApiKey,
      Version: "2021-07-28",
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: {
      contactId,
      type: "Email",
      emailFrom: alertEmail,
      emailTo: alertEmail,
      subject: "[LT] LinkedIn dispatcher failed",
      message: alertText,
      html: "<pre>" + alertText.replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch])) + "</pre>",
    },
    json: true,
  });
}

const eligible = [];
let scanned = 0;
try {
  const searchFields = [
    "customFields.apollo_person_linkedin_url",
    "customFields.em_contact_linkedin_urls",
  ];
  const seenContactIds = new Set();
  for (const searchField of searchFields) {
    for (let page = 1; page <= 5; page++) {
      let resp;
      try {
        resp = await ghlSearchContacts(50, page, searchField);
      } catch (searchErr) {
        const statusCode = searchErr?.statusCode || searchErr?.response?.statusCode || searchErr?.response?.status || null;
        const message = clean(searchErr?.message || searchErr?.response?.body?.message || searchErr?.response?.body?.detail || "");
        if (statusCode === 422) {
          console.warn("Skipping invalid GHL search field " + searchField + ": " + message);
          break;
        }
        throw searchErr;
      }
      const contacts = (resp && Array.isArray(resp.contacts)) ? resp.contacts : [];
      if (contacts.length === 0) break;
      for (const c of contacts) {
        scanned++;
        if (eligible.length >= CFG.maxQueueSize) break;
        const contactId = clean(c?.id || "");
        if (!contactId || seenContactIds.has(contactId)) continue;
        if (hasTag(c, CFG.successTag)) continue;
        if (hasTag(c, "linkedin_connected")) continue;
        const liUrl = getLinkedInUrl(c);
        if (!liUrl) continue;

        const inbound = await hasInboundConversation.call(this, contactId);
        if (inbound.blocked) continue;

        seenContactIds.add(contactId);
        eligible.push({ id: c.id, firstName: String(c.firstName || "").trim(), lastName: String(c.lastName || "").trim(), liUrl });
      }
      if (eligible.length >= CFG.maxQueueSize || contacts.length < 50) break;
    }
  }

  const results = [];
  let sentCount = 0;
  let dailySentCount = 0;
  if (typeof this.getWorkflowStaticData === "function") {
    const prev = this.getWorkflowStaticData("global");
    const today = new Date().toISOString().slice(0, 10);
    dailySentCount = prev.date === today ? Number(prev.sentToday || 0) : 0;
    if (dailySentCount >= CFG.dailyLimit) {
      return [{ json: {
        queue_found: eligible.length,
        batch_size: 0,
        sent: 0,
        dry_runs: 0,
        failed: 0,
        sent_today: dailySentCount,
        results: [],
        scanned,
        note: "DAILY LIMIT REACHED - no invites sent",
      } }];
    }
  }
  for (const contact of eligible) {
    if (sentCount >= CFG.batchSize) break;
    if (dailySentCount >= CFG.dailyLimit) break;

    const id = linkedinId(contact.liUrl);
    if (!id) { results.push({ contactId: contact.id, status: "skipped", reason: "invalid_url" }); continue; }

    const profile = await unipileReq("GET", CFG.unipileApiBaseUrl + "/users/" + encodeURIComponent(id) + "?account_id=" + encodeURIComponent(CFG.unipileAccountId), undefined, { "X-API-KEY": CFG.unipileApiKey });
    const providerId = clean(profile.data?.provider_id || profile.data?.providerId || profile.data?.id || "");
    const firstName = contact.firstName || clean(profile.data?.first_name || "there");
    const requestSentAt = new Date().toISOString();

    const inbound = await hasInboundConversation.call(this, contact.id);
    if (inbound.blocked) {
      results.push({
        contactId: contact.id,
        firstName,
        liUrl: contact.liUrl,
        identifier: id,
        providerId,
        status: "skipped",
        reason: inbound.reason,
        inboundError: inbound.error || "",
      });
      continue;
    }

    if (hasTag(contact, 'linkedin_connected')) {
      results.push({
        contactId: contact.id,
        firstName,
        liUrl: contact.liUrl,
        identifier: id,
        providerId,
        status: 'skipped',
        reason: 'already_connected',
      });
      continue;
    }

    if (CFG.defaultDryRun || !profile.ok || !providerId) {
      results.push({
        contactId: contact.id,
        firstName,
        liUrl: contact.liUrl,
        identifier: id,
        providerId,
        status: CFG.defaultDryRun ? "dry_run" : "profile_failed",
        profileOk: profile.ok,
        profileError: clean(profile.data?.detail || profile.data?.title || profile.data?.message || ""),
      });
      continue;
    }

    const msgRaw = clean(CFG.defaultMessage).replace(/\\{first_name\\}/gi, firstName);
    const msg = msgRaw.length > 300 ? msgRaw.slice(0, 300) : msgRaw;
    const inv = await unipileReq("POST", CFG.unipileApiBaseUrl + "/users/invite", { account_id: CFG.unipileAccountId, provider_id: providerId, ...(msg ? { message: msg } : {}) }, { "X-API-KEY": CFG.unipileApiKey });
    let stateSyncOk = false;
    let stateSyncError = "";

    if (inv.ok) {
      try {
        await this.helpers.httpRequest({ method: "POST", url: CFG.ghlApiBaseUrl + "/contacts/" + encodeURIComponent(contact.id) + "/tags", headers: { Authorization: "Bearer " + CFG.ghlApiKey, Version: "2021-07-28", "Content-Type": "application/json" }, body: { tags: [CFG.successTag] }, json: true });
      } catch (e) { }
      try {
        await this.helpers.httpRequest({
          method: "POST",
          url: CFG.connectionStateUpsertUrl,
          headers: { Accept: "application/json", "Content-Type": "application/json" },
          body: {
            ghl_contact_id: contact.id,
            location_id: CFG.locationId,
            unipile_account_id: CFG.unipileAccountId,
            linkedin_profile_url: contact.liUrl,
            linkedin_public_identifier: id,
            linkedin_provider_id: providerId,
            connection_request_tag: CFG.successTag,
            connection_status: "requested",
            request_sent_at: requestSentAt,
            request_message: msg,
            sequence_step: 0,
            source_workflow_name: CFG.workflowName,
            source_key: "contact:" + contact.id,
            payload_json: {
              contactId: contact.id,
              firstName,
              liUrl: contact.liUrl,
              identifier: id,
              providerId,
              status: "sent",
              inviteOk: true,
            },
            metadata_json: {
              source: "dispatcher",
              workflow: CFG.workflowName,
            },
          },
          json: true,
        });
        stateSyncOk = true;
      } catch (stateErr) {
        stateSyncError = describeError(stateErr);
      }
    }

    if (inv.ok) sentCount += 1;
    if (inv.ok) dailySentCount += 1;

    results.push({ contactId: contact.id, firstName, liUrl: contact.liUrl, identifier: id, providerId, status: inv.ok ? "sent" : "invite_failed", inviteOk: inv.ok, stateSyncOk, stateSyncError, requestSentAt });
  }

  const sent = results.filter((r) => r.status === "sent").length;
  const dryRuns = results.filter((r) => r.status === "dry_run").length;
  const failed = results.filter((r) => r.status !== "sent" && r.status !== "dry_run").length;

  const today = new Date().toISOString().slice(0, 10);
  let dailySent = sent;
  if (typeof this.getWorkflowStaticData === "function") {
    const prev = this.getWorkflowStaticData("global");
    dailySent = (prev.date === today ? (prev.sentToday || 0) : 0) + sent;
    prev.date = today;
    prev.sentToday = dailySent;
  }

  return [{ json: {
    queue_found: eligible.length,
    batch_size: sent,
    sent,
    dry_runs: dryRuns,
    failed,
    sent_today: dailySent,
    results,
    scanned,
    note: CFG.defaultDryRun ? "DRY RUN MODE - no invites sent" : (sent + " invites sent"),
  } }];
} catch (err) {
  const failure = err instanceof Error ? err : new Error(describeError(err));
  try {
    await sendFailureAlert.call(this, failure, {
      scanned,
      queueSize: eligible.length,
      details: "Fatal failure while dispatching LinkedIn requests",
    });
  } catch (alertErr) {
    failure.message = failure.message + " | alert email failed: " + describeError(alertErr);
  }
  throw failure;
}`;

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
  output: [{ json: { queue_found: 50, batch_size: 10, sent: 0, dry_runs: 10, failed: 0, sent_today: 0, scanned: 250, note: 'LIVE MODE - ready to send' } }],
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

export default workflow('lt-ghl-linkedin-dispatcher', 'LT - GHL LinkedIn Connect Dispatcher (Unipile)')
  .add(schedule)
  .to(config)
  .to(dispatch)
  .to(result)
  .add(webhook)
  .to(config)
  .add(manual)
  .to(config);
