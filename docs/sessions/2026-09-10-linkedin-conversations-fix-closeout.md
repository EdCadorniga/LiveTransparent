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
