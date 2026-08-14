# LinkedIn and Instagram via Unipile -> GHL Bidirectional Integration

Updated: 2026-08-14 (company Instagram-page delivery planning added; existing inbound/outbound bridge remains authoritative)

Next-session handoff for the bidirectional GHL Custom Conversation Provider integration using Unipile for LinkedIn and Instagram.

## Goal

Make GHL Conversations the operator-facing inbox for LinkedIn and Instagram conversations while Unipile remains the transport layer.

1. Inbound LinkedIn/Instagram message arrives in Unipile.
2. n8n receives the Unipile webhook, resolves or creates the matching GHL contact, and adds the message into GHL Conversations under the correct custom provider tab.
3. GHL user replies from the LinkedIn via Unipile or Instagram via Unipile custom provider tab.
4. GHL posts the outbound provider webhook to n8n.
5. n8n resolves the mapped Unipile chat/profile and sends the reply through the correct Unipile account.
6. Reply/inbound state feeds back into the outbound automation guardrails so automated DMs stop.

## Company Instagram Page Outreach Contract (2026-08-14)

The approved Instagram/FB DM copy is unchanged. The planned outbound audience is the company's Instagram page, not the employee represented by the GHL contact. GHL contacts remain the attribution and suppression records; the company-page Instagram identity is a separate operational identity.

### Source and audience selectors

- Brands: GHL tag `brands_pool`; source file `data/Brands.csv`.
- Dispensaries: GHL tag `dispensaries_pool`; source file `data/Dispensaries.csv`.
- Partnerships: GHL tag `partner_candidate_email` or `partner_candidate_linkedin`; the current Partnership CSVs do not contain reliable Instagram/Facebook URL fields and require separate enrichment before activation.

The Brands and Dispensaries source files provide `Company non-LinkedIn URL(s)`, `Location non-LinkedIn URL(s)`, and `Contact non-LinkedIn URL(s)`. Preliminary audit counts are Brands 3,224/3,668 rows with Instagram URL occurrences and 2,799/3,668 with Facebook URL occurrences; Dispensaries 6,875/10,200 with Instagram URL occurrences and 6,431/10,200 with Facebook URL occurrences. These are not validated page counts.

### GHL field contract

The existing contact-level fields are protected and continue to serve the inbound contact bridge:

| Field | ID |
|------|----|
| Instagram Username | `8k6vF61VBIysdIXXFQD5` |
| Instagram Profile URL | `beGMXoidqHdYqAQDORWX` |
| Instagram Profile Provider ID | `fYYUrFLABP5l0w7RdK7Y` |
| Instagram Chat Attendee ID | `SQdQw0MNvk8uQbr4yDZU` |
| Instagram Chat ID | `ab6euY7qo5klhUSe7VWu` |

Create separate contact custom fields, all `TEXT`, with these exact names:

- `Company Instagram Username`
- `Company Instagram Profile URL`
- `Company Instagram Profile Provider ID`
- `Company Instagram Chat Attendee ID`
- `Company Instagram Chat ID`
- `Company Facebook Page URL`
- `Company Facebook Page ID`
- `Company Facebook Messenger PSID`

Do not repurpose `Apollo Facebook URL`. A public Facebook Page URL or Page ID is reference/enrichment data only; a Messenger PSID may only be captured from an eligible GHL Messenger interaction and must never be inferred from a URL.

### Enrichment and identity resolution

The one-time enrichment workflow must be read-only until its review output is approved. Match source rows to GHL in this order: Emerald Contact ID; source-file/import metadata; exact normalized email; exact normalized phone; company-plus-contact-name as a review-only fallback. Extract and normalize company/location Instagram URLs, remove tracking parameters, resolve the profile through Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`, and reject personal, unrelated, ambiguous, or conflicting profiles.

Several GHL contacts may refer to one company page. Deduplicate by `(Unipile account ID, normalized Instagram handle)` and retain all associated GHL contact IDs plus one primary attribution contact. Update only the new `Company ...` fields after approval. Preserve the original `Em_*Non_LinkedIn_URLs` source metadata and never overwrite a validated contact-level Instagram identity with a company identity.

### Authoritative Postgres state

Create a dedicated company-page identity/state model, proposed name `instagram_company_dm_state`, authoritative for delivery and lifecycle. At minimum it must store campaign key, Unipile account/profile/chat identifiers, normalized username, profile URL, company name, source tag, primary and associated GHL IDs, step/status, started/last-sent/next-due timestamps, last message ID/hash, reply/suppression state, failure reason, and audit timestamps.

Enforce identity uniqueness by `(campaign_key, unipile_account_id, instagram_profile_provider_id)` and send idempotency by `(campaign_key, instagram_profile_provider_id, message_step)`. Use direct `require('pg')` transactions for writes because the n8n Postgres v2.5+ `queryReplacement` path is not reliable in this environment.

Before Message 1, check prior inbound/reply evidence for every associated GHL contact and company page across `instagram_conversation_map`, GHL Conversations, existing social state, and relevant email/LinkedIn reply state. Any reply or suppression from any associated contact stops the whole company-page sequence. Identity or reply-check errors fail closed and skip the send.

Cadence is Message 1 on the first eligible weekday, Message 2 two business days later, and Message 3 two business days after Message 2. Do not send on weekends. Lifecycle remains in Postgres; do not add lifecycle tags for this campaign.

### Build and verification gates

1. Produce source extraction, URL normalization, match, duplicate, personal-profile, ambiguous-profile, and unresolved reports.
2. Create the eight company-level GHL fields.
3. Resolve and review company Instagram identities through Unipile.
4. Update approved GHL company fields and import the authoritative Postgres identity state.
5. Run a five-page dry-run sample for Brands and Dispensaries.
6. Run one controlled live Instagram test per campaign only after explicit approval.
7. Verify Unipile profile/chat/message IDs, GHL mapping, Postgres persistence, and reply suppression.
8. Publish and activate the weekday dispatcher only after all gates pass.

The existing `instagram_conversation_map` remains the contact-level inbound/GHL bridge. It must not be silently changed into the company-page campaign state table.

## What's Working

### Instagram Inbound Bridge (WORKING)

Messages flow end-to-end from Unipile webhook -> GHL contact create/update -> GHL Conversation under "Instagram via Unipile" tab.

**Key innovation**: The stored OAuth token is agency-scoped and can't access conversation providers. The fix: each inbound call first converts the agency token to a location token via `POST /oauth/locationToken`, then uses that for the inbound message API. This avoids needing a location-scoped token at install time.

**Flow**:
- Webhook `/webhook/lt-unipile-instagram-new-messages`
- Normalize Instagram Message (Code) -> parses Unipile payload
- Lookup Mapping and OAuth Token (Postgres) -> finds/creates `instagram_conversation_map`, reads active OAuth token
- Create Contact and Add Inbound Message (Code) -> conservatively resolves an existing GHL contact, calls `/oauth/locationToken` to convert agency->location token, posts inbound with `type: "Custom"`
- Upsert Instagram Mapping (Postgres) -> persists chat mapping

**Inbound message type**: `type: "Custom"` works. `type: "SMS"` returns `CONVERSATIONS_MSG_CONVERSATION_PROVIDER_MISMATCH` for our SMS-type custom providers.

**Dedup / merge status 2026-07-16:** Initial Instagram replay reused pre-merge contact `sZjiGh8zJbG2DFhDCFBD`; that contact was later merged into canonical GHL contact `XZ4yChllGBdcsVxhFRDe`. After a stale-map replay created temporary duplicate `4V2oTmM7lWya3Nmtmp1Y`, map row `1` was repaired to `XZ4yChllGBdcsVxhFRDe` and the duplicate was deleted. Avoid artificial inbound replays unless needed because they create visible conversation messages.

**Location token API**: `POST https://services.leadconnectorhq.com/oauth/locationToken` with `companyId: "7vMmm4at5OrjQplRN3EO"` and `locationId: "Zwz4relUXVPxx8uohnjV"`.

### LinkedIn Inbound Bridge (WORKING)

Same architecture as Instagram but with `linkedin_conversation_map` table and canonical provider `6a58a14ff3023bea3783c152`. Contact create/update + map + inbound posting + existing DM suppression preservation are active.

**Verified 2026-07-16:** LinkedIn replay for chat `60Ult1SrWhOuvuZp1u7nXw` posted to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`, message `XubHwhlqdFAMQnZ4DAsm`. GHL conversation search showed `lastMessageType = TYPE_CUSTOM_PROVIDER_SMS`, `lastMessageDirection = inbound`, and `lastMessageConversationProviderId = 6a58a14ff3023bea3783c152`.

**Live webhook verification:** A real LinkedIn message, `Sending another test message`, arrived from Unipile as an `application/x-www-form-urlencoded` object whose single key contained the JSON payload. `Normalize Unipile Message Event` now parses that shape. Replay posted the message to GHL conversation `Ze8o3KbsrwuAXQ3KK5ge` as `TYPE_CUSTOM_PROVIDER_SMS` with provider `6a58a14ff3023bea3783c152`.

**Fixes applied:** `Upsert LinkedIn Map` now creates missing columns, avoids `ON CONFLICT` because the live table has no unique constraint, accepts blank LinkedIn profile URLs, and maps chat `60Ult1SrWhOuvuZp1u7nXw` to the real GHL contact. Lookup now prefers real `linkedin_connection_state` contacts over provisional map rows, and the final state lookup prefers real GHL contact IDs over synthetic `linkedin:follower:*` rows.

### Outbound Router (WORKING for direct webhook tests)

POST path of `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`):
- Lookup Outbound Chat ID (Postgres) -> queries `instagram_conversation_map` and `linkedin_conversation_map`
- Route Outbound to Unipile (Code) -> maps conversationProviderId to Unipile account, sends via `POST /chats/{id}/messages`

**Fixed 2026-07-16 Session 3:**
- POST webhook now uses `responseMode: responseNode`; prior `onReceived` + connected Respond node caused `Unused Respond to Webhook node found in the workflow` and immediate 40ms failures.
- Lookup node now creates missing map tables defensively before selecting. The missing `linkedin_conversation_map` table was crashing Instagram-only lookups.
- Lookup node preserves `message_text`/`alt_id` for the Code node; the previous query discarded the original webhook body before routing.
- Code node no longer uses `process.env` (task-runner sandbox returned `process is not defined`) and uses the working Unipile base URL `https://api42.unipile.com:17256/api/v1`.
- Direct smoke test to `/webhook/lt-social-provider-outbound` for canonical contact `XZ4yChllGBdcsVxhFRDe` routed successfully to Instagram with Unipile message id `vjdEYSk9XD6R0I46oPWLwA`.
- Direct smoke test through the canonical Instagram SMS custom provider `6a58a1193cdfc36997580a68` routed successfully with Unipile message id `sQJlo6mxUUO2dEMWzdi1OA`.
- Live GHL UI reply from the Instagram provider tab routed through n8n to Unipile successfully with Unipile message id `iEJO1vnvWVGwbk7ril1__A`.

### Contact Data Rule

Do not add dummy phone or email data for LinkedIn/Instagram provider routing. The working inbound payload uses `type: "Custom"` with `conversationProviderId` and `altId`, so provider routing does not require contact phone/email shims.

## What's Blocked

### Canonical SMS Custom Providers (Fixed 2026-07-16)

Email-type providers were deleted because they forced GHL to render LinkedIn/Instagram replies as email compose boxes with From/To/Subject fields. The working setup is **SMS-type additional custom conversation providers** paired with inbound message `type: "Custom"`.

Canonical provider IDs:
1. `Instagram via Unipile` -> `6a58a1193cdfc36997580a68`
2. `LinkedIn via Unipile` -> `6a58a14ff3023bea3783c152`

Provider setup requirements:
1. Type: `SMS`
2. Check `Is this a Custom Conversation Provider`
3. Check `Always show this Conversation Provider`
4. Do not select these providers under `Settings > Phone Numbers > Advanced Settings > SMS Provider`
5. Delivery URL: `https://automations.livetransparent.com/webhook/lt-social-provider-outbound`

Inbound message API payload must use `type: "Custom"` with `conversationProviderId` and `altId`. Do not use `type: "SMS"` for these providers; GHL returned `CONVERSATIONS_MSG_CONVERSATION_PROVIDER_MISMATCH`. Do not include `emailTo`, `emailFrom`, `subject`, or any dummy phone/email fields.

Verified 2026-07-16:
- Instagram inbound replay succeeded with provider `6a58a1193cdfc36997580a68` and returned message `er8mbcB9Lj8ao6Y0H2nJ` in conversation `yPLDgs90sEU5dbedA1gW`.
- GHL conversation search showed `lastMessageType = TYPE_CUSTOM_PROVIDER_SMS`, `lastMessageBody = Patched Instagram custom-provider inbound test`, and `lastMessageConversationProviderId = 6a58a1193cdfc36997580a68`.
- Canonical merged contact `XZ4yChllGBdcsVxhFRDe` retained real email/phone plus Instagram and LinkedIn routing fields; no dummy provider phone/email shims were added.
- Direct outbound router smoke test through new Instagram provider routed to Unipile message `sQJlo6mxUUO2dEMWzdi1OA`.
- LinkedIn inbound replay succeeded with provider `6a58a14ff3023bea3783c152`, canonical contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`, and GHL message `XubHwhlqdFAMQnZ4DAsm`.

### Outbound Router Webhook (FIXED 2026-07-16 Session 3)

The POST webhook at `/webhook/lt-social-provider-outbound` was erroring immediately (40ms execution). Root cause found in n8n container logs:

```text
Unused Respond to Webhook node found in the workflow
Error in handling webhook request POST /webhook/lt-social-provider-outbound: Unused Respond to Webhook node found in the workflow
```

Fixes applied:
- Removed `rawBody: true` (conflicting with `responseMode: responseNode`)
- Changed GET webhook to different path to avoid sharing `/webhook/lt-social-provider-outbound`
- Set Postgres credential on Lookup Outbound Chat ID node
- Final clean PUT via REST API with full JSON
- Changed POST webhook from `responseMode: onReceived` to `responseMode: responseNode`
- Added defensive table creation for `instagram_conversation_map` and `linkedin_conversation_map`
- Preserved outbound payload fields through the lookup
- Removed sandbox-blocked `process.env` access in Route Outbound to Unipile

Current direct test result with the canonical Instagram SMS custom provider:

```json
{
  "ok": true,
  "accepted": true,
  "service": "lt-social-provider-outbound",
  "routing": {
    "routed": true,
    "provider_id": "6a58a1193cdfc36997580a68",
    "contact_id": "XZ4yChllGBdcsVxhFRDe",
    "provider_type": "INSTAGRAM",
    "provider_name": "Instagram via Unipile",
    "chat_id": "yx-R-9J6XdWaFpGOQd1JFA",
    "unipile_message_id": "vjdEYSk9XD6R0I46oPWLwA"
  }
}
```

A quick diagnostic: test the POST path directly with curl and check n8n container logs:
```bash
curl -X POST https://automations.livetransparent.com/webhook/lt-social-provider-outbound \
  -H "Content-Type: application/json" \
  -d '{"conversationProviderId":"6a58a1193cdfc36997580a68","contactId":"XZ4yChllGBdcsVxhFRDe","message":"test","type":"Custom","altId":"yx-R-9J6XdWaFpGOQd1JFA"}'
```

## GHL Setup Reference

### Marketplace App

| Field | Value |
|-------|-------|
| App ID | `6a57dec68099a1e7cf68a266` |
| Client ID | `6a57dec68099a1e7cf68a266-mrmh8fl9` |
| Client Secret | `56f564ab-9eed-4797-9d4e-0df367e1acd4` |
| App Name | Transparent eCom Social Inbox |
| Developer | Transparent eCom |
| Target User | Sub-account |
| Who can install | Agency + Sub-Account |
| App Type | Private |

### Scopes (all correct)
`contacts.readonly`, `contacts.write`, `conversations.readonly`, `conversations.write`, `conversations/message.readonly`, `conversations/message.write`

### Conversation Providers

| Provider | Type | Alias | ID |
|----------|------|-------|-----|
| LinkedIn via Unipile | SMS custom provider | LinkedIn via Unipile | `6a58a14ff3023bea3783c152` |
| Instagram via Unipile | SMS custom provider | Instagram via Unipile | `6a58a1193cdfc36997580a68` |

Deleted Email provider IDs, do not use:
- LinkedIn via Unipile Email: `6a5892b9107668309b3f85ac`
- Instagram via Unipile Email: `6a5893d11e9368345005f66e`

Legacy SMS provider IDs retained only for transition/reference:
- LinkedIn via Unipile SMS: `6a5853a51e93687696053bf8`
- Instagram via Unipile SMS: `6a5853d33cdfc31a8c572766`

### Delivery URL (for both providers)
```
https://automations.livetransparent.com/webhook/lt-social-provider-outbound
```

### GHL Locations

| Field | Value |
|-------|-------|
| Location ID | `Zwz4relUXVPxx8uohnjV` |
| Location Name | Live Transparent |
| Company ID | `7vMmm4at5OrjQplRN3EO` |

### Unipile Accounts

| Platform | Account Name | Account ID |
|----------|--------------|------------|
| LinkedIn | Cameron Karkut | `V9eiHiDpRmCtan0YNdzsQw` |
| Instagram | Transparent eCom | `F2UprZ8aQc6Qm9CYYWU6cg` |

### OAuth Install URL (full scopes)
```
https://marketplace.gohighlevel.com/v2/oauth/chooselocation?response_type=code&redirect_uri=https%3A%2F%2Fautomations.livetransparent.com%2Fwebhook%2Flt-social-provider-outbound&client_id=6a57dec68099a1e7cf68a266-mrmh8fl9&scope=contacts.readonly+contacts.write+conversations.readonly+conversations.write+conversations%2Fmessage.readonly+conversations%2Fmessage.write&version_id=6a57dec68099a1e7cf68a266
```

Note: marketplace.gohighlevel.com has session issues. Use app.gohighlevel.com integration pages to uninstall/reinstall instead.

## n8n Workflows

### Active / Published

| Workflow | ID | Status |
|----------|----|--------|
| LT - Social Provider Outbound Router | `kqIi8i1RjFAZKrK3` | Active (outbound working for direct tests and Instagram GHL UI reply) |
| LT - Instagram Unipile New Messages | `pISlgYUsyJIrLuJd` | Active (inbound working; dedup verified) |
| LT - LinkedIn Unipile New Messages | `7o5EBdvwAuIaWW7k` | Active; published `f96dafba-9818-4aab-8656-c2e4e2ab8480` (inbound working; malformed form-payload fallback live) |
| LT - GHL OAuth Callback | `UnSWPnVoUy3tNJkX` | Active |

### Stopped

| Workflow | ID | Status |
|----------|----|--------|
| LT - Instagram DM Sequence (Unipile) | `iCnY6ccdHhfJg3sf` | Unpublished |
| LT - LinkedIn Follower DM Sequence (Unipile) | `pq7XVajNFnnwMUTr` | Unpublished |

## Data Tables

### `instagram_conversation_map`
Created by `pISlgYUsyJIrLuJd`. Maps `ghl_contact_id` <-> `instagram_chat_id` (UNIQUE).

### `linkedin_conversation_map`
Created by `7o5EBdvwAuIaWW7k`. Maps `ghl_contact_id` <-> `linkedin_chat_id` (UNIQUE).

### `ghl_oauth_tokens`
Stores OAuth tokens from marketplace app installs. Queried by inbound workflows with `WHERE active IS TRUE`.

### `ghl_oauth_install_events`
Logs OAuth install events (codes, exchanges).

## Known Test Identity (Instagram)

| Field | Value |
|-------|-------|
| Contact name | Edmundo Cadorniga |
| GHL Contact ID | `XZ4yChllGBdcsVxhFRDe` |
| Instagram username | `edmundocadorniga` |
| Chat ID | `yx-R-9J6XdWaFpGOQd1JFA` |
| Profile provider ID | `6361495593` |
| Messaging provider ID | `109928757071246` |
| Map row ID | `1` |
| Email | `ed@livetransparent.com` |
| Phone | `+63471666523` |

### 2026-07-16 Merge Cleanup

- Historical GHL duplicates for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; GHL search now returns one matching contact.
- Temporary verification duplicate `4V2oTmM7lWya3Nmtmp1Y` was deleted after map repair.
- Temporary workflow `LT - Temp Social Map Maintenance 2026-07-16` (`nuuB3qCKxr7J6iPw`) repointed `instagram_conversation_map.id = 1` and `linkedin_conversation_map.id = 2` to `XZ4yChllGBdcsVxhFRDe`, then was archived.
- Post-repair outbound router verification succeeded for Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` (`C7I9944kWsSKutX2XhZEpA`).

### Test Payload
```json
{"account_id":"F2UprZ8aQc6Qm9CYYWU6cg","account_type":"INSTAGRAM","id":"yx-R-9J6XdWaFpGOQd1JFA","chat_id":"yx-R-9J6XdWaFpGOQd1JFA","lastMessage":{"id":"test-msg","chat_id":"yx-R-9J6XdWaFpGOQd1JFA","text":"test message","is_sender":0,"sender_id":"109928757071246","timestamp":"2026-07-17T00:00:00.000Z","account_id":"F2UprZ8aQc6Qm9CYYWU6cg"},"profile":{"provider_id":"6361495593","public_identifier":"edmundocadorniga","full_name":"Edmundo Cadorniga"}}
```

## Operator Inbox and Monitoring Runbook

### Current Operator Inbox

GHL Conversations is the canonical operator-facing inbox for LinkedIn and Instagram messages. Inbound Unipile messages are written into GHL as custom-provider messages, and GHL replies are routed back through `LT - Social Provider Outbound Router` to Unipile.

Operators should monitor GHL Conversations at the conversation level, not by opening each contact record manually. Use the provider tabs named `LinkedIn via Unipile` and `Instagram via Unipile` when replying so outbound messages route through the correct custom conversation provider.

### Response Rules

- Reply from the correct GHL custom provider tab: `LinkedIn via Unipile` for LinkedIn, `Instagram via Unipile` for Instagram.
- Do not reply through normal SMS, email, or manually typed phone/email fields for social messages.
- Do not add dummy phone or email values to make social replies work; routing depends on `conversationProviderId` and `altId`.
- If a person replies on LinkedIn, confirm the automated LinkedIn sequence is suppressed by `dm_conversation_status = active` or the `linkedin_dm_sequence_completed` tag/state.
- Do not remove the LinkedIn inbound normalizer's malformed form-payload fallback. Unipile can deliver unescaped JSON as the sole `application/x-www-form-urlencoded` body key; the fallback recovers sender, chat, message, and timestamp fields needed for GHL mirroring, suppression, and reporting.
- If a contact asks to stop LinkedIn DMs, use the suppression runbook in `AGENTS.md` or add the GHL tag `stop_linkedin_dms`.

### Macro-Level Visibility

The system currently supports macro review through GHL Conversations, but there is no dedicated social inbox dashboard or alert digest documented as live. Any macro alerting or dashboard should be treated as a new enhancement unless a live workflow is added and verified.

Recommended macro views:

- GHL Conversations filtered to recent inbound messages from `LinkedIn via Unipile` and `Instagram via Unipile`.
- GHL Conversations filtered to unread or unreplied conversations when available in the GHL UI.
- A future n8n digest that lists new inbound LinkedIn/Instagram messages across all contacts.
- A future dashboard backed by GHL Conversations plus `instagram_conversation_map` and `linkedin_conversation_map`.

### Recommended Alert Workflow

Not currently documented as live. If alerting is needed, build a workflow or extend the inbound bridges after the GHL message write succeeds.

Recommended flow:

```text
Unipile inbound webhook
-> Normalize platform/message/contact
-> Post inbound message to GHL Conversations
-> Upsert social conversation map
-> Send Slack/email alert or write digest row
```

Recommended alert fields:

- Platform: LinkedIn or Instagram
- Sender name and profile identifier
- Message text
- GHL contact ID and contact link
- GHL conversation ID when available
- Unipile chat ID / `altId`
- Automation suppression status
- Workflow execution ID

Recommended alert cadence:

- Real-time alert for every inbound message until operator confidence is high.
- Hourly digest for unread or unreplied social conversations.
- Daily QA summary showing inbound count, outbound reply count, routing failures, and unmapped chats.

### Health Checks

Run these checks after any workflow/provider change and at least weekly while the bridge is in active use.

- Confirm `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active and published.
- Confirm `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active and published.
- Confirm `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active and published.
- Confirm `LT - GHL OAuth Callback` (`UnSWPnVoUy3tNJkX`) is active.
- Confirm GHL provider IDs are still canonical: Instagram `6a58a1193cdfc36997580a68`, LinkedIn `6a58a14ff3023bea3783c152`.
- Confirm the provider delivery URL for both providers is `https://automations.livetransparent.com/webhook/lt-social-provider-outbound`.
- Confirm Unipile Instagram webhook points to `/webhook/lt-unipile-instagram-new-messages`.
- Confirm Unipile LinkedIn webhook points to `/webhook/lt-unipile-linkedin-new-messages`.
- Confirm LinkedIn inbound workflow version `f96dafba-9818-4aab-8656-c2e4e2ab8480` or a verified successor retains malformed form-payload field recovery.
- Confirm `ghl_oauth_tokens` has an active token row for the Live Transparent location.
- Confirm `instagram_conversation_map` and `linkedin_conversation_map` contain rows for active social chats.

### Troubleshooting

If an inbound social message does not appear in GHL:

- Check the relevant inbound workflow execution first.
- Confirm the Unipile webhook is firing and the account ID matches the expected platform account.
- Check OAuth conversion to a location token via `POST /oauth/locationToken`.
- Check that the inbound GHL message payload uses `type: "Custom"`, `conversationProviderId`, and `altId`.
- Check for duplicate or stale map rows pointing to a merged/deleted GHL contact.

If a GHL reply does not send through Unipile:

- Check `LT - Social Provider Outbound Router` executions.
- Confirm the webhook body includes `conversationProviderId`, `contactId`, `message`, and `altId`.
- Confirm the matching row exists in `instagram_conversation_map` or `linkedin_conversation_map`.
- Confirm the router uses the working Unipile base URL `https://api42.unipile.com:17256/api/v1`.
- Confirm the reply was sent from the correct provider tab, not normal SMS/email.

If automated LinkedIn DMs continue after a reply:

- Check `linkedin_connection_state.payload_json.dm_conversation_status` for `active`.
- Check whether `linkedin_dm_sequence_completed` is present on the GHL contact when the conversation should be terminal.
- Run the LinkedIn DM suppression path from `AGENTS.md` if the contact needs to be manually suppressed.

### Open Gaps

- No dedicated macro social inbox dashboard exists in this repo.
- No live Slack/email alert workflow is documented for every LinkedIn/Instagram inbound message.
- Social replies remain unassigned in Warm until Janvi's AI assessment verifies a qualified cannabis business. Promotion into `Sales Outreach -> New` applies the documented owner-alignment rule; the social transport itself must not assign an SDR.
- No automated stale-unreplied social conversation report is documented.
- No daily reconciliation job is documented to compare Unipile chats against GHL conversations.

## Next Steps (Priority Order)

1. **Monitor post-merge social inbound**: Map rows now point to canonical contact `XZ4yChllGBdcsVxhFRDe`. Watch the next real Instagram inbound to confirm it lands on the canonical contact without creating a new duplicate.

2. **Optional LinkedIn UI outbound test**: LinkedIn inbound and direct outbound router checks are verified; run a controlled GHL UI reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge` if operator-side confirmation is needed.

3. **Register/confirm Unipile Instagram webhook**: Ensure the production Instagram Unipile webhook points to `/webhook/lt-unipile-instagram-new-messages`.

4. **Add macro alerting/digest**: Build and verify a lightweight n8n notification path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.

5. **Build company-page Instagram outbound DM**: Only after the bidirectional inbox remains stable. Implement source enrichment, the eight company-level GHL fields, `instagram_company_dm_state` (or approved equivalent), company-page/account-type validation, reply suppression, idempotency, and the agreed weekday cadence using Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`.

6. Do NOT republish Instagram DM Sequence or LinkedIn Follower DM Sequence unless explicitly requested.

## Guardrails (Preserved)

- LinkedIn automated sends fail closed if reply lookup errors
- DM suppression blocks all 3 send paths (DM Sequence, Follower DM, Dispatcher)
- `dm_conversation_status = active` set after LinkedIn inbound bridge
- Contact creation conservative (matched by provider IDs, not name)
- `altId` preserved as Unipile chat ID for outbound reply routing
- Live n8n state is source of truth over repo files
