"""Patch live LinkedIn senders for strict identity handling and GHL mirroring.

The script refuses to mutate a workflow if an expected live-code anchor is missing.
Run without --apply for a dry-run summary; run with --apply only when the resulting
patch summary is reviewed. n8n REST PUT publishes the resulting workflow version.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
WORKFLOWS = {
    "main_dispatcher": "fXxw5lanZcDmUrst",
    "partnership_dispatcher": "crKIsaL5k3YBfqDZ",
    "main_dm": "d0tEtijajisIsYcs",
    "partnership_dm": "nspggypNF245xzeL",
}
ALLOWED_SETTINGS = {
    "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
    "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "callerPolicy",
    "errorWorkflow", "binaryMode", "availableInMCP",
}


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY_LT", "")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[2] / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("N8N_API_KEY_LT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("N8N_API_KEY_LT is required")


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def nodes(workflow: dict) -> dict[str, dict]:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def replace_once(code: str, old: str, new: str, label: str) -> str:
    count = code.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return code.replace(old, new, 1)


def inject_once(code: str, anchor: str, insertion: str, label: str) -> str:
    return replace_once(code, anchor, anchor + insertion, label)


def update(workflow: dict) -> dict:
    payload = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": {k: v for k, v in (workflow.get("settings") or {}).items() if k in ALLOWED_SETTINGS},
    }
    return request(workflow["id"], "PUT", payload)


def syntax_check(workflow: dict) -> None:
    for node in workflow.get("nodes", []):
        code = node.get("parameters", {}).get("jsCode")
        if not code:
            continue
        wrapped = "async function __n8n_code_check() {\n" + code + "\n}\n"
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(wrapped)
            path = handle.name
        try:
            result = subprocess.run(["node", "--check", path], capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(f"{workflow.get('name')} / {node.get('name')} ({path}): {result.stderr.strip()}")
            Path(path).unlink(missing_ok=True)
        finally:
            pass


COMMON_MIRROR = r'''
async function mirrorLinkedInToGhl(contactId, messageText, altId, firstName, sourceName) {
  const { Client } = require('pg');
  const client = new Client({ host: 'postgres', port: 5432, database: 'postgres', user: 'postgres', password: String((typeof CFG !== 'undefined' && CFG.pgPassword) || (typeof cfg !== 'undefined' && cfg.pgPassword) || 'P@ssDatabase%!!'), connectionTimeoutMillis: 10000 });
  try {
    await client.connect();
    const tokenRows = await client.query("SELECT access_token FROM ghl_oauth_tokens WHERE active IS TRUE AND COALESCE(access_token, '') <> '' ORDER BY received_at DESC LIMIT 1");
    const locationToken = String(tokenRows.rows?.[0]?.access_token || '').trim();
    if (!locationToken) return { ok: false, reason: 'missing_active_ghl_oauth_token' };
    const response = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://services.leadconnectorhq.com/conversations/messages',
      headers: { Authorization: 'Bearer ' + locationToken, Version: '2021-07-28', Accept: 'application/json', 'Content-Type': 'application/json' },
      body: {
        type: 'Custom',
        contactId: String(contactId),
        message: String(messageText),
        conversationProviderId: '6a58a14ff3023bea3783c152',
        altId: String(altId || ('linkedin:profile:' + String(contactId))),
        date: new Date().toISOString(),
      },
      json: true,
      returnFullResponse: true,
    });
    const status = Number(response?.statusCode || 200);
    return { ok: status >= 200 && status < 300, status, source: sourceName, first_name: firstName };
  } catch (error) {
    return { ok: false, reason: String(error?.message || error).slice(0, 300), source: sourceName, first_name: firstName };
  } finally {
    await client.end().catch(() => {});
  }
}
'''


def patch_main_dispatcher(workflow: dict) -> None:
    node = nodes(workflow)["Dispatch LinkedIn Requests"]
    code = node["parameters"]["jsCode"]
    code = inject_once(code, "function buildOutboundMessage(template, firstName) {", COMMON_MIRROR, "main dispatcher mirror helper")
    old_name = "const firstName = clean(contact?.firstName || unipileProfile.data?.first_name || 'there');"
    new_name = """const firstName = clean(contact?.firstName);
  const linkedinFirstName = clean(unipileProfile.data?.first_name || unipileProfile.data?.firstName || '');
  if (!firstName) { errors.push({ contact_id: contactId, stage: 'identity', error: 'missing_ghl_first_name' }); results.push({ contactId, status: 'identity_failed', error: 'missing_ghl_first_name' }); continue; }
  if (linkedinFirstName && linkedinFirstName.toLowerCase() !== firstName.toLowerCase()) { errors.push({ contact_id: contactId, stage: 'identity', error: 'first_name_mismatch' }); results.push({ contactId, status: 'identity_failed', error: 'first_name_mismatch', ghl_first_name: firstName, linkedin_first_name: linkedinFirstName }); continue; }"""
    code = replace_once(code, old_name, new_name, "main dispatcher strict first name")
    old_send = """  if (!invite.ok) { errors.push({ contact_id: contactId, stage: 'unipile_invite', status: invite.status, error: invite.error }); results.push({ contactId, status: 'invite_failed', error: invite.error }); continue; }"""
    new_send = old_send + """
  const mirror = await mirrorLinkedInToGhl.call(this, contactId, message, 'linkedin:profile:' + providerId, firstName, 'connection_request');"""
    code = replace_once(code, old_send, new_send, "main dispatcher conversation mirror")
    code = replace_once(code, "results.push({ contactId, status: !state.ok ? 'sent_state_failed' : (tag.ok ? 'sent' : 'sent_tag_failed'), error: state.ok ? undefined : state.error, providerId, identifier: liId, linkedin_profile_url: profileUrl, first_name: firstName, linkedin_public_identifier: liId, linkedin_provider_id: providerId });", "results.push({ contactId, status: !state.ok ? 'sent_state_failed' : (tag.ok ? 'sent' : 'sent_tag_failed'), error: state.ok ? undefined : state.error, mirror_status: mirror.ok ? 'mirrored' : 'mirror_failed', mirror_error: mirror.ok ? undefined : mirror.reason, providerId, identifier: liId, linkedin_profile_url: profileUrl, first_name: firstName, linkedin_public_identifier: liId, linkedin_provider_id: providerId });", "main dispatcher mirror result")
    node["parameters"]["jsCode"] = code


def patch_partnership_dispatcher(workflow: dict) -> None:
    node = nodes(workflow)["Dispatch LinkedIn Requests"]
    code = node["parameters"]["jsCode"]
    code = inject_once(code, "function sanitizeMessage(text) {", COMMON_MIRROR, "partnership dispatcher mirror helper")
    anchor = "if (!providerId) { errors++; continue; }"
    identity = """if (!firstName) { errors++; out.push({ json: { status: 'identity_failed', contact_id: contactId, error: 'missing_ghl_first_name' } }); continue; }
var identityProfile = await unipileReq('GET', '/users/' + encodeURIComponent(identifier) + '?account_id=' + encodeURIComponent(unipileAccountId));
var identityFirstName = identityProfile.ok && identityProfile.data ? clean(identityProfile.data.first_name || identityProfile.data.firstName || '') : '';
if (identityFirstName && identityFirstName.toLowerCase() !== firstName.toLowerCase()) { errors++; out.push({ json: { status: 'identity_failed', contact_id: contactId, error: 'first_name_mismatch', ghl_first_name: firstName, linkedin_first_name: identityFirstName } }); continue; }"""
    code = inject_once(code, anchor, "\n" + identity, "partnership dispatcher strict first name")
    old_normal = """if (!inv.ok) { errors++; out.push({ json: { status: \"invite_failed\", contact_id: contactId, first_name: firstName, provider_id: providerId, error: String(inv.data).slice(0, 200) } }); continue; } sent++; var nowTs = new Date().toISOString();"""
    new_normal = old_normal + " var mirror = await mirrorLinkedInToGhl.call(this, contactId, msg, 'linkedin:profile:' + providerId, firstName, 'connection_request');"
    code = replace_once(code, old_normal, new_normal, "partnership dispatcher conversation mirror")
    old_company = """if (cInv.ok) { sent++; var nowTs2 = new Date().toISOString();"""
    new_company = old_company + " var mirrorCompany = await mirrorLinkedInToGhl.call(this, contactId, cMsg, 'linkedin:profile:' + cProf.data.provider_id, firstName, 'connection_request');"
    code = replace_once(code, old_company, new_company, "partnership company fallback mirror")
    code = replace_once(code, "out.push({ json: { status: \"sent\", contact_id: contactId, first_name: firstName, li_url: liUrl, provider_id: providerId, run_id: runId } });", "out.push({ json: { status: \"sent\", contact_id: contactId, first_name: firstName, li_url: liUrl, provider_id: providerId, run_id: runId, mirror_status: mirror && mirror.ok ? 'mirrored' : 'mirror_failed' } });", "partnership dispatcher mirror result")
    code = replace_once(code, "out.push({ json: { status: \"sent\", contact_id: contactId, first_name: firstName, li_url: coLiUrl2, provider_id: cProf.data.provider_id, run_id: runId, company_fallback: true } });", "out.push({ json: { status: \"sent\", contact_id: contactId, first_name: firstName, li_url: coLiUrl2, provider_id: cProf.data.provider_id, run_id: runId, company_fallback: true, mirror_status: mirrorCompany && mirrorCompany.ok ? 'mirrored' : 'mirror_failed' } });", "partnership company fallback mirror result")
    node["parameters"]["jsCode"] = code


def patch_main_dm(workflow: dict) -> None:
    node = nodes(workflow)["Send DM Sequence Messages"]
    code = node["parameters"]["jsCode"]
    code = inject_once(code, "function buildOutboundMessage(template, firstName) {", COMMON_MIRROR, "main DM mirror helper")
    old_name = """var firstName = clean(contact.firstName || 'there');
              if ((!firstName || firstName === 'there') && profileResp && profileResp.ok && profileResp.data) {
                firstName = clean(profileResp.data.first_name || profileResp.data.firstName || 'there');
              }"""
    new_name = """var firstName = clean(contact.firstName);
              var linkedinFirstName = profileResp && profileResp.ok && profileResp.data ? clean(profileResp.data.first_name || profileResp.data.firstName || '') : '';
              if (!firstName) { results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'missing_ghl_first_name' }); return processNext.call(self, index + 1); }
              if (linkedinFirstName && linkedinFirstName.toLowerCase() !== firstName.toLowerCase()) { results.push({ contactId: contactId, step: step, newStep: newStep, status: 'identity_failed', error: 'first_name_mismatch', ghl_first_name: firstName, linkedin_first_name: linkedinFirstName }); return processNext.call(self, index + 1); }"""
    code = replace_once(code, old_name, new_name, "main DM strict first name")
    state_anchor = "var upsertBody = {"
    code = replace_once(code, ".then(function(chatResp) {", ".then(async function(chatResp) {", "main DM awaitable send callback")
    code = replace_once(code, state_anchor, "var mirrorResult = await mirrorLinkedInToGhl.call(self, contactId, message, chatId || ('linkedin:profile:' + providerId), firstName, 'dm');\n              " + state_anchor, "main DM conversation mirror call")
    # Store the first name used for the send in durable state for later audit.
    code = replace_once(code, "payload_json: { last_chat_id: chatId, last_message_step: newStep, sent_at: new Date().toISOString() },", "payload_json: { last_chat_id: chatId, last_message_step: newStep, sent_at: new Date().toISOString(), first_name_used: firstName, mirror_status: mirrorResult.ok ? 'mirrored' : 'mirror_failed' },", "main DM first-name audit")
    node["parameters"]["jsCode"] = code


def patch_partnership_dm(workflow: dict) -> None:
    node = nodes(workflow)["Send DM Sequence Messages"]
    node["parameters"]["jsCode"] = r'''// Partnership LinkedIn DM Sequence
const cfg = $item(0).$node["Config"].json || {};
const dryRun = !!cfg.defaultDryRun;
const batchSize = Math.max(1, Number(cfg.batchSize || 30));
const base = String(cfg.unipileApiBaseUrl || "https://api42.unipile.com:17256/api/v1").replace(/\/$/, "");
const apiKey = String(cfg.unipileApiKey || "").trim();
const accountId = String(cfg.unipileAccountId || "").trim();
const ghlBase = String(cfg.ghlApiBaseUrl || "https://services.leadconnectorhq.com").replace(/\/$/, "");
const ghlKey = String(cfg.ghlApiKey || "").trim();
const locationId = String(cfg.locationId || "").trim();
const stateUrl = "https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert";
const stateSecret = String(cfg.stateUpsertSecret || "").trim();
const completionTag = "partner_linkedin_sequence_completed";
const runId = new Date().toISOString() + "__partnership_linkedin_dm";
const out = [];
function clean(value) { return String(value || "").trim(); }
function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
function sanitize(value) { return String(value || "").replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"').replace(/\u2013|\u2014/g, "-").replace(/\u2026/g, "...").replace(/\u00A0/g, " "); }
async function http(url, options) { try { return { ok: true, data: await this.helpers.httpRequest({ ...options, url, timeout: 30000, json: true }) }; } catch (error) { return { ok: false, error: String(error?.message || error).slice(0, 300), data: error?.response?.body || null }; } }
async function ghl(path, method, body) { return http.call(this, ghlBase + path, { method, headers: { Authorization: "Bearer " + ghlKey, Version: "2021-07-28", Accept: "application/json", "Content-Type": "application/json" }, ...(body === undefined ? {} : { body }) }); }
async function unipile(path, method, body) { return http.call(this, base + path, { method, headers: { "X-API-KEY": apiKey, Accept: "application/json", "Content-Type": "application/json" }, ...(body === undefined ? {} : { body }) }); }
async function mirror(contactId, text, chatId, firstName) {
  const { Client } = require("pg");
  const client = new Client({ host: "postgres", port: 5432, database: "postgres", user: "postgres", password: String(cfg.pgPassword || "P@ssDatabase%!!"), connectionTimeoutMillis: 10000 });
  try {
    await client.connect();
    const token = await client.query("SELECT access_token FROM ghl_oauth_tokens WHERE active IS TRUE AND COALESCE(access_token, '') <> '' ORDER BY received_at DESC LIMIT 1");
    const accessToken = clean(token.rows?.[0]?.access_token);
    if (!accessToken) return { ok: false, reason: "missing_active_ghl_oauth_token" };
    const response = await this.helpers.httpRequest({ method: "POST", url: ghlBase + "/conversations/messages", headers: { Authorization: "Bearer " + accessToken, Version: "2021-07-28", Accept: "application/json", "Content-Type": "application/json" }, body: { type: "Custom", contactId, message: text, conversationProviderId: "6a58a14ff3023bea3783c152", altId: chatId || ("linkedin:profile:" + contactId), date: new Date().toISOString() }, json: true, returnFullResponse: true });
    return { ok: Number(response?.statusCode || 200) >= 200, first_name: firstName };
  } catch (error) { return { ok: false, reason: String(error?.message || error).slice(0, 300), first_name: firstName }; }
  finally { await client.end().catch(() => {}); }
}
const rows = ($items("Fetch Connected Contacts") || []).map((item) => item.json || {});
if (!rows.length) return [{ json: { status: "summary", summary: { ok: true, dryRun, runId, candidates: 0, sent: 0 } } }];
const templates = ["", "Hey {first_name}, thanks for connecting. Quick context - we help regulated brands get their ads approved on Meta/Google instead of getting blurred or banned. Open to a quick chat on a possible collab?", "Hey {first_name}, following up - a few concrete options are a guest spot, webinar, co-written piece, or newsletter mention. Who is the right person for content partnerships on your end?", "Hey {first_name}, one more note on this. If timing is off, no worries - just let me know a better window or who else to loop in.", "Hey {first_name}, keeping this short. If a collab is not a fit right now, totally fine - just say so and I will stop following up."];
let sent = 0, skipped = 0, errors = 0, completed = 0;
for (const row of rows.slice(0, batchSize)) {
  const contactId = clean(row.ghl_contact_id), providerId = clean(row.linkedin_provider_id), currentStep = Number(row.sequence_step || 0);
  if (!contactId || !providerId) { skipped++; continue; }
  if (row.payload_json?.dm_conversation_status === "active") { skipped++; continue; }
  const nextStep = row.dm_sequence_started_at ? currentStep + 1 : 1;
  if (nextStep > 4) { completed++; await ghl.call(this, "/contacts/" + encodeURIComponent(contactId) + "/tags", "POST", { tags: [completionTag] }); continue; }
  if (dryRun) { out.push({ json: { status: "planned", contact_id: contactId, next_step: nextStep, run_id: runId } }); continue; }
  const contactRes = await ghl.call(this, "/contacts/" + encodeURIComponent(contactId), "GET");
  const contact = contactRes.ok ? (contactRes.data?.contact || contactRes.data || {}) : {};
  const firstName = clean(contact.firstName || contact.first_name);
  if (!contactRes.ok || !firstName) { errors++; out.push({ json: { status: "identity_failed", contact_id: contactId, error: contactRes.ok ? "missing_ghl_first_name" : "ghl_contact_lookup_failed" } }); continue; }
  const replyCheck = await ghl.call(this, "/conversations/search?contactId=" + encodeURIComponent(contactId) + "&lastMessageDirection=inbound&status=all&limit=1", "GET");
  if (!replyCheck.ok) { errors++; out.push({ json: { status: "reply_check_failed", contact_id: contactId, error: replyCheck.error } }); continue; }
  const conversations = Array.isArray(replyCheck.data?.conversations) ? replyCheck.data.conversations : [];
  if (conversations.length) { skipped++; out.push({ json: { status: "inbound_reply", contact_id: contactId } }); continue; }
  const message = sanitize(templates[nextStep].replace(/\{first_name\}/gi, firstName));
  if (!message || /[{}]/.test(message) || /[^\x20-\x7E\n\r]/.test(message)) { errors++; out.push({ json: { status: "message_validation_failed", contact_id: contactId, step: nextStep } }); continue; }
  const sentResult = await unipile.call(this, "/chats", "POST", { account_id: accountId, provider_id: providerId, text: message });
  if (!sentResult.ok) { errors++; out.push({ json: { status: "dm_failed", contact_id: contactId, step: nextStep, error: sentResult.error } }); continue; }
  sent++;
  const chatId = clean(sentResult.data?.chat_id || sentResult.data?.chatId);
  const mirrored = await mirror.call(this, contactId, message, chatId || ("linkedin:profile:" + providerId), firstName);
  const now = new Date().toISOString();
  const state = await http.call(this, stateUrl, { method: "POST", headers: { "X-LT-LinkedIn-State-Secret": stateSecret, Accept: "application/json", "Content-Type": "application/json" }, body: { ghl_contact_id: contactId, location_id: locationId, unipile_account_id: accountId, linkedin_provider_id: providerId, connection_status: "connected", sequence_step: nextStep, source_key: "partnership", table: "partnership_linkedin_connection_state", payload_json: { dm_sequence_status: "active", first_name_used: firstName, last_chat_id: chatId, mirror_status: mirrored.ok ? "mirrored" : "mirror_failed" }, metadata_json: { campaign: "partnership", run_id: runId, last_dm_step: nextStep, last_dm_at: now } } });
  out.push({ json: { status: "sent", contact_id: contactId, step: nextStep, first_name_used: firstName, mirror_status: mirrored.ok ? "mirrored" : "mirror_failed", state_status: state.ok ? "persisted" : "state_upsert_failed", run_id: runId } });
  await sleep(500);
}
out.push({ json: { status: "summary", summary: { ok: errors === 0, dryRun, runId, candidates: rows.length, sent, completed, skipped, errors } } });
return out;'''


def patch_all(apply: bool) -> None:
    loaded = {label: request(workflow_id) for label, workflow_id in WORKFLOWS.items()}
    for workflow in loaded.values():
        if workflow.get("versionId") != workflow.get("activeVersionId"):
            raise RuntimeError(f"Refusing unpublished draft: {workflow.get('name')}")
    patch_main_dispatcher(loaded["main_dispatcher"])
    patch_partnership_dispatcher(loaded["partnership_dispatcher"])
    patch_main_dm(loaded["main_dm"])
    patch_partnership_dm(loaded["partnership_dm"])
    for workflow in loaded.values():
        syntax_check(workflow)
    for label, workflow in loaded.items():
        print(json.dumps({"workflow": label, "id": workflow["id"], "changed": True, "apply": apply}))
        if apply:
            updated = update(workflow)
            print(json.dumps({"workflow": label, "versionId": updated.get("versionId"), "activeVersionId": updated.get("activeVersionId")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    patch_all(args.apply)
