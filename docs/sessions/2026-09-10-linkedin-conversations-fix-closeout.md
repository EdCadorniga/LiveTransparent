# LinkedIn Conversations Inbound Fix — Session Closeout

Date: 2026-09-10
Objective: Fix GHL `/conversations/messages` 422 errors in `LT - LinkedIn Unipile New Messages` and enable proper inbound message posting to GHL Conversations.

## What Was Done

### Root Cause Identified
- `Create LinkedIn Contact and Add Inbound Message` node in n8n workflow `7o5EBdvwAuIaWW7k` was posting to wrong GHL endpoint `https://services.leadconnectorhq.com/conversations/messages` instead of `/conversations/messages/inbound`
- Node used `this.helpers.request()` (deprecated) with `uri` and `simple: false` options
- This caused GHL to return HTTP 422 (and earlier 404) errors

### Fix Applied
- Changed `this.helpers.request(` → `this.helpers.httpRequest(`
- Changed `uri: GHL_BASE + '/conversations/messages/inbound'` → `url: GHL_BASE + '/conversations/messages/inbound'`  
- Removed `simple: false` option
- Published workflow version `127504a5-08ae-41b4-ad5c-f2a39a068e82` (versionId == activeVersionId)
- Verified via direct GHL API testing that the correct endpoint is `/conversations/messages/inbound` with body `{"type":"Custom","contactId":"<ghl_contact_id>","message":"<text>","conversationProviderId":"6a58a14ff3023bea3783c152"}`
- Verified correct flow: POST `/oauth/locationToken` with PIT token → get `access_token` → use as Bearer for `/conversations/messages/inbound`

### Additional Discoveries
- GHL PIT token (`pit-d25ac994-226d-41ab-8ea9-f3458b6cc845`) works for main API but returns 401 for `/oauth/locationToken` — the OAuth token must come from `ghl_oauth_access_token` stored in Postgres `linkedin_conversation_map` table
- Postgres database is NOT accessible from local machine (connection refused on port 5432)
- The n8n webhook at `https://automations.livetransparent.com/webhook/lt-unipile-linkedin-new-messages` accepts POSTs but returns 200 with empty body — workflow execution may be timing out at Postgres-dependent nodes (`Find LinkedIn State Row By Provider`, `Lookup LinkedIn Map and OAuth Token`)
- The `responseMode: "responseNode"` on the webhook node means n8n waits for `Respond - Mark Conversation Active` node output

### Key GHL API Details Verified
- Correct endpoint: `https://services.leadconnectorhq.com/conversations/messages/inbound`
- Required header: `Authorization: Bearer <location_access_token>` (NOT the PIT token)
- Required header: `Version: 2021-07-28`, `Content-Type: application/json`, `Accept: application/json`
- Location ID: `Zwz4relUXVPxx8uohnjV`, Company ID: `7vMmm4at5OrjQplRN3EO`, LinkedIn provider ID: `6a58a14ff3023bea3783c152`
- OAuth token source: Postgres `linkedin_conversation_map.ghl_oauth_access_token` (inaccessible locally)

## Current Live State

- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active and published, version `127504a5-08ae-41b4-ad5c-f2a39a068e82`
- `Create LinkedIn Contact and Add Inbound Message` node now uses `this.helpers.httpRequest(` with `url: GHL_BASE + '/conversations/messages/inbound'`
- Workflow has 20 nodes including Postgres-dependent nodes that require `ghl_oauth_access_token` from Postgres
- Webhook node confirmed: POST method, path `lt-unipile-linkedin-new-messages`, `responseMode: "responseNode"`
- `LT - LinkedIn Conversation Backfill` (`JUvrA7qMa24SwAZG`) remains inactive (separate workflow from the earlier session)
- Earlier session's 5-chat backfill execution `930588` successfully posted 6 messages, but Gretchen's 2 historical outbound messages returned HTTP 422

## Blockers and Risks

1. **Postgres not accessible locally** — cannot retrieve `ghl_oauth_access_token` to test GHL Conversations API directly from local scripts
2. **Webhook POST returns empty 200** — the n8n workflow likely times out at Postgres nodes; needs investigation of execution logs
3. **Gretchen's 422 failures** — two historical outbound messages in the earlier backfill returned HTTP 422; may be the same endpoint issue or payload shape problems
4. **`responseMode: "responseNode"`** — means webhook waits indefinitely if downstream nodes don't produce output; could cause hanging webhook calls
5. **Contact ID inconsistency** — GHL contact search (`GET /contacts/?query=<provider_id>`) may return different IDs for the same LinkedIn profile on different calls, risking incorrect message attribution

## Next Steps

1. **Verify n8n workflow execution** — check n8n execution logs for `7o5EBdvwAuIaWW7k` to confirm the fix to `Create LinkedIn Contact and Add Inbound Message` node works end-to-end; if Postgres nodes are timing out, investigate if n8n's Postgres connection is healthy
2. **Resolve Postgres access** — either SSH into the VPS to query `linkedin_conversation_map` for `ghl_oauth_access_token`, or confirm n8n's internal Postgres connection is working so the webhook workflow executes fully
3. **Test the webhook with a proper Unipile payload** — POST to `https://automations.livetransparent.com/webhook/lt-unipile-linkedin-new-messages` with fields: `event: 'message_received'`, `account_id`, `account_info: {user_id: '<ed_user_id>'}`, `chat_id`, `sender: {attendee_provider_id: '<different_from_user_id>'}`, `message` — ensuring `sender.attendee_provider_id !== account_info.user_id` to pass the `isInbound` check
4. **Diagnose Gretchen's 422 failures** — if the `/conversations/messages/inbound` fix works, retry Gretchen's messages with the corrected endpoint
5. **Consider broader backfill scope** — only after the 6-message backfill and Gretchen issues are resolved

## Safety Gates

- Do NOT publish or activate any new workflow versions without explicit approval
- Do NOT rerun the full 5-chat backfill workflow (not idempotent, could duplicate messages)
- Do NOT commit GHL PITs, OAuth tokens, or credential values to any file
- Any production webhook triggers require explicit user approval recorded outside this document

---

## Follow-Up Session (2026-09-11) — Two Live Bugs Fixed, E2E Verified, Gretchen Resolved

User approved all three actions in this section (E2E test, test-message cleanup, Gretchen retry).

### Diagnosis update (corrects the "Blockers and Risks" above)

Execution `934032` data disproved several prior assumptions:

1. **Postgres is NOT timing out.** `Lookup LinkedIn Map and OAuth Token` completed in ~126 ms and returned a valid OAuth token from `ghl_oauth_tokens`. The full workflow ran in ~2 seconds. The earlier "empty 200 / Postgres timeout" theory was wrong.
2. **Bug 1 — response misinterpretation in `Create LinkedIn Contact and Add Inbound Message`.** The node used `resolveWithFullResponse: true` with `this.helpers.httpRequest`. That option belongs to the deprecated `this.helpers.request` helper and is silently ignored, so `resp` was the response BODY (not a full response) and `resp.statusCode`/`resp.body` were undefined — every successful post was misclassified as `inbound_failed: status=undefined body={}`. The v2 and v3 test posts actually LANDED in GHL (conversation `B6Enrm2D2LtsXPhi1qLY`, verified before deletion). Fix: `returnFullResponse: true` (returns `{body, headers, statusCode, statusMessage}`) plus a hardened `describeError` that surfaces `statusCode` and the axios `error` body.
3. **Bug 2 — jsonb literal corruption in all 6 `Build * SQL` Code nodes.** `esc()` doubled backslashes (`.replace(/\\/g, '\\\\')`). With `standard_conforming_strings` on, backslashes in SQL single-quoted strings are literal, so the `'...'::jsonb` literal built from `JSON.stringify` contained `\\\"` sequences — invalid JSON. This crashed `Upsert LinkedIn Map` with "invalid input syntax for type json" whenever the payload contained an embedded quote (e.g. `sentBody`), so `linkedin_conversation_map` rows were never persisted. Fix: removed the backslash doubling, kept `'` → `''`.
4. **Gretchen 422 root cause confirmed.** The backfill workflow routed historical OUTBOUND messages (`is_sender === 1`) to the nonexistent direction path `/conversations/messages/outbound` → HTTP 422. Outbound custom-provider mirroring uses `POST /conversations/messages` (same body shape); inbound posts use `/conversations/messages/inbound`.

### Fixes applied and published

- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`): published version `3dab7e61-b2e4-45c6-8e6d-055b8c05623e` (`versionId == activeVersionId`), active, 19 nodes intact. Applied via `scripts/fix_linkedin_inbound_response_and_jsonb.py` (surgical REST PUT; dry-run + node syntax check first).
- `LT - LinkedIn Conversation Backfill` (`JUvrA7qMa24SwAZG`, inactive): outbound posts routed to `/conversations/messages`, conversation-message dedup added (skips bodies already present in the contact's LinkedIn conversation), and Config gained `only_chat_id` (set to Gretchen's chat `8NOmhtWSUpKbsec3YdsxlA`) so the retry touched only Gretchen. Applied via `scripts/fix_linkedin_backfill_outbound_direction.py`.

### Verification (all user-approved)

- **E2E test (exec `934088`)**: one labeled `DRY RUN TEST v4 - post-fix verification` message posted via the production webhook. Result: `status: "processed"`, `ghl_conversation_id: B6Enrm2D2LtsXPhi1qLY`, `ghl_message_id: MyyQ56WLSD4YBWnH1IDJ`, `Upsert LinkedIn Map` succeeded with `mapping_row_id: 42`. Webhook returned HTTP 200 through the Respond node.
- **Cleanup**: GHL does not support per-message DELETE (404); the test conversation `B6Enrm2D2LtsXPhi1qLY` (which held exactly the 3 test messages) was deleted via `DELETE /conversations/{id}` using a fresh location token. The synthetic `Test Sender` contact (`6PohGQltrE97YyWCQp7k`) remains by user choice.
- **Gretchen retry (exec `934099`)**: manual run, Gretchen-only via `only_chat_id`. Result: `total_messages_backfilled: 2, errors: []`, Summarize completed. Verified in GHL: conversation `I3w8fRaPzecv7CXnI8oe` (contact `5xaxXklF7Cn1PkAv2t7B`) holds both historical outbound messages with `LinkedIn via Unipile` provider attribution. Note: GHL stamps `dateAdded` at post time; the historical `date` body field does not backdate the message timestamp.
- No executions were left in `new`, `running`, or `waiting`. The backfill workflow remains inactive with `only_chat_id` still set to Gretchen's chat (clear it before any broader backfill).

### Operational notes for next time

- Local python scripts calling `services.leadconnectorhq.com` must send a browser-like `User-Agent`; Cloudflare Error 1010 blocks `python-urllib` with 403 regardless of auth.
- The active OAuth token lives in Postgres `ghl_oauth_tokens` (reachable over SSH; token kept in memory only). The PIT does not authenticate `/oauth/locationToken`.
- `linkedin_conversation_map` mapping rows now persist (row id 42 written for the test chat); historical row coverage for the 5 backfilled chats was created by the original backfill run's own upserts.
