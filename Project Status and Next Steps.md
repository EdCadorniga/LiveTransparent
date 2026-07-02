# LiveTransparent Project Status and Next Steps

Updated: 2026-07-02 (Emerging pool imported to Postgres; Apollo re-enrichment on bad numbers added to callback)

## Source Of Truth

This document is the canonical project status and next-steps reference.
It supersedes the duplicated planning notes in:

- [plan.md](./plan.md)
- [LiveTransparent Report Plan.md](./LiveTransparent%20Report%20Plan.md)

## Current State

- The outbound voice stack is **paused** (since 2026-06-05). Queue cleanup completed 2026-07-01: 1,005 stale `pending` rows marked `failed`. Pool audit complete: 23,726 GHL contacts, 1,045 unique already called via V1, ~16k Emerald pool as primary target for new campaigns.
- **Vapi Campaign Rollout Phase 1 complete (2026-07-01)**: Two Vapi assistants created (Brand/Alex `1d7c5d42`, Dispensary/Jordan `056f2e50`) with full system prompts from campaign docx files, 9 tools each. GHL campaign tags created. Vapi org tools cleaned up (2 deprecated deleted, 1 dangling ref removed). `ok_transfer_to_john` → `ok_transfer_to_jason` migration across all assistants, prompts, and n8n callback. See `plan.md` for next phases.
- **Vapi classifier path fixed (2026-07-02)**: `LT - Campaign Contact Classifier` now runs from Postgres `Emerald_Contacts` plus `voice_call_attempt` exclusion instead of live GHL pagination. The old PIT rate-limit / Code-node-loop failure path is gone.
- **Current rollout blocker (2026-07-02)**: the synced Emerald supply with both GHL IDs and phones is executive-only. We currently have 5 not-called rows available, all from executive source files, and zero reachable marketing / dispensary / retail-sales rows for the two new campaigns.
- **Mis-tag rollback completed (2026-07-02)**: a 5-contact smoke test proved the old `sso` substring heuristic incorrectly routes executive rows into Brand. Those accidental `vapi_campaign_brand` tags were removed immediately.
- **Queue feeder workflow added (2026-07-02)**: `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) now exists to gradually feed already-approved campaign-tagged contacts into `voice_call_queue`. Latest manual test found 3 candidates and queued 0 new rows; follow-up audit confirmed those same 3 contacts were already in `voice_call_queue` as `pending`, so the duplicate guard is working correctly.
- **Activation-readiness audit (2026-07-02)**: the 3 currently staged campaign rows are still `pending` with `attempt_count = 0` and no `voice_call_attempt` rows yet, so they are safe to keep as the seed cohort. The paused Vapi workflows still show the expected campaign-routing updates and no fresh executions since the pause, so the next real gate is controlled reactivation plus manual assistant test calls.
- **Bug discoveries during audit**: `voice_call_queue` has no `pipeline_stage` column — dequeue query filter `AND pipeline_stage = 'queued'` means dequeue webhook has NEVER picked up poller-inserted rows (V1 worked through dialer cron). Callback had hardcoded `trackedAssistants` array — now includes both new campaign assistants.
- **Emerging Pool import (2026-07-02)**: Two brand/dispensary Emerald CSV files imported into Postgres `emerging_pool_contacts` (13,868 total). GHL-ready CSVs prepared with correct column mapping. Two n8n workflows created. Apollo re-enrichment on bad numbers added to callback workflow.
- The reporting stack is live: GA4 and GHL ingestion are in production, data is flowing into Postgres, and the Executive Report is live in GHL.
- Report rollups, attribution bridge, QA/alerts, and the executive summary API are already running.
- Emerald email-marketing ingest workflows are **PAUSED 2026-06-05** (9 workflows unpublished). See [Plan - VAPI Pause & Queued Goals.md](./Plan%20-%20VAPI%20Pause%20%26%20Queued%20Goals.md) for the full list and resumption playbook. **GHL email sequences still need to be paused manually in the GHL UI** for already-enrolled contacts.
- Emerald intro backfill is staged in live GHL: 500 additional eligible contacts have now been tagged `seq emerald - intro backfill pending`, the live pending queue increased to 3,566, and 1,719 enrolled contacts remain eligible for controlled staging.
- LinkedIn outreach pipeline is fully operational and verified (2026-06-03):
  - `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) seeds `linkedin_connection_state` from GHL contacts with LinkedIn URLs, resolved through Unipile profile lookups. Verified: `scanned: 101, matched: 100, upserted: 100`, schedule `15 */6 * * *`.
  - `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`, replaces archived `S32vc8pjJIBZZHLK`) reads the Postgres queue, sends LinkedIn connection requests via Unipile `POST /users/invite`. Verified: `sent: 10`, schedule `0 15-21 * * 1-5`.
  - `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) polls connected contacts, includes automatic connection detection from Unipile chats, enforces a daily DM limit of 200 with carry-forward, and sends up to 40 DMs per progression step. Verified: `sent: 2`, schedule `0 12-22 * * 1-5`.
  - `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is the webhook receiver for state table upserts (ON CONFLICT with smart merging).
  - `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) marks active conversations to stop DM sequences on reply.
  - Working GHL token: `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28`. The alternate `pit-2d2ed8c3-...` is broken (401).
  - Code node regex safety: always use `[/]` character class instead of `\/` in regex literals to avoid SDK JSON serialization corruption.
  - State table `linkedin_connection_state`: 171 contacts with `status='ready'`, 34 with `status='connected'`, 10 invites sent, 2 DMs delivered.
- SimpleTexting SMS campaign workflow exports are now staged in repo from `outreach_messages.docx`: sender, pool dispatcher, sequencer, inbound reply, delivery events, and unsubscribe events are all represented as separate workflows.
- The SMS stack still needs live deployment and a final GHL pool filter body for the dispatcher, but the message registry, batching shape, reply-stop handling, and Slack `#lead` notification path are now defined in the repo artifacts.
- GSC still needs workflow verification / cleanup.
- Meta Ads API access is validated, but spend ingest is still deferred.

## Voice Workflows

### Live Voice System

- Phone: `+1 (562) 534 1977`
- Vapi Assistant IDs: V1 Outbound `3f9bbfd2...`, V1 Inbound `43f379ff...`, Brand (Alex) `1d7c5d42...`, Dispensary (Jordan) `056f2e50...`
- Canonical webhook: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`
- Target n8n version: `2.25.3` (upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue)
- Canonical MCP: `n8n-lt`

### Active Workflows

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) — **Manual**, now reads from `Emerald_Contacts` + `voice_call_attempt`; code path is working, but current campaign-relevant source supply is empty
- `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) — **Inactive helper**, runs every 30 minutes when enabled and stages approved `vapi_campaign_*` contacts into the queue with pacing + duplicate guards
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — **ACTIVE 2026-07-02**, merged callback plus 4 tools, all 4 campaign assistants tracked
- `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — **ACTIVE 2026-07-02**, receives GHL call webhooks, upserts Postgres, Slack alerts for missed inbound
- `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — **ACTIVE 2026-07-02**, webhook-triggered dequeue, campaign-aware assistant routing
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — **ACTIVE 2026-07-02**, webhook enqueue with dedup guard
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — **PAUSED** (intentionally held for quality gate), queue dialer, contact-TZ-aware, campaign routing
- `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — **PAUSED** (intentionally held for quality gate), polls campaign tags, Apollo enrichment
- **4 of 6 VAPI workflows are now active.** Dialer and intake poller remain paused pending quality gate test calls. GHL-side infrastructure (reaper, Apollo callbacks) remains independent.
- **Voice queue cleanup (2026-07-01)**: 1,005 stale `pending` queue rows from the V1 pause marked `failed`. Post-cleanup queue: 86 completed, 1,005 failed, 0 pending. The 86 completed represent calls with callback dispositions; the remaining V1 contacts with `attempt_count > 0` but no completion are safe to re-enqueue into new campaigns.
- `LT - Apollo Queued Timeout Reaper` (`RL5ZyUoshSPbmVA1`) — active, hourly, flips GHL contacts stuck with `Apollo Phone Enrichment Status = queued` AND `Apollo Phone Enrichment Queued At < NOW - 24h` (or missing queued_at) to `callback_timeout` so the Vapi poller unblocks them. Verified first run (execution `75153`): scanned 500, stuck 500, updated 499, 1 contact (Joey Evans `nayDFnGCCcrVO9oTg4ls`) hit a transient 400 in the reaper log but the status field was actually written to `callback_timeout` (GHL dateUpdated confirms) and the Vapi poller will pick him up on a later batch. Source: `n8n/workflows/lt-apollo-queued-timeout-reaper.ts`.

### Dialer Pipeline

- Cron runs Monday through Friday, 9am to 5pm CT.
- The dialer fetches and locks queue rows, checks the contact, applies a timezone-safe calling window, and places the Vapi call.
- The pipeline then increments attempt counts, sets `next_attempt_at` to `NOW + 72h`, and writes the GHL note.
- The dialer prefers internal Coolify service-to-service communication where possible.

### Intake Pipeline

- Cron runs every 10 minutes.
- The intake poller searches GHL for `vapi_queue` contacts.
- Valid E.164 numbers are enqueued.
- Invalid or missing phone numbers are skipped when enrichment is not sufficient.

### Callback Changes (2026-07-02)
- Added `Should Re-enrich Phone` IF node + `HTTP - Set Apollo Enrichment` to the end-of-call flow
- When Vapi returns `wrong_number` or `contact_disconnected` disposition, the callback sets `Enrich Phone via Apollo = Yes` so Apollo can find a new number
- Only those 2 dispositions trigger re-enrichment — all others skip this step
- Uses existing `LT - Apollo Phone Enrichment Intake V3` for the actual lookup

### Callback Tools

- `update_lead_status` updates the GHL tag and the Postgres disposition.
- `add_to_dnc` sets `voice_call_queue.dnc=true` and adds the GHL DNC tag.
- `log_call_outcome` upserts `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales` posts lead name and summary into `#leads`.

### Pool Tags (created 2026-07-02)
- `brands_pool` — contacts from Brands.csv
- `dispensaries_pool` — contacts from Dispensaries.csv

### Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

### Vapi Campaign Tags (created 2026-07-01)

- `vapi_campaign_brand` (`exfU7DXbFF1c314Z1QXQ`)
- `vapi_campaign_dispensary` (`FiYEwJdMSIyKZa059wRY`)
- `vapi_already_called` (`HhkfhzocuEdOFOxeeHu2`)

### Call History Summary (voice_call_attempt)

- **1,711** total attempts across **1,045** unique contacts
- Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18
- All V1 calls were against the Emerald MSO/SSO contact pool

### Voice Hardening Remaining

- Move remaining secrets out of workflow `Config` nodes into credentials or env-backed config.
- Verify the dashboard still points all tools and the end-of-call webhook to the canonical callback URL.
- Diagnose why the Apollo phone-enrichment callback URL (`/webhook/ghl-apollo-phone-enrichment-callback-v4`) has had zero deliveries since 2026-05-13 even though the intake workflow still flips contacts to `queued` (synthetic POST to that webhook should be tested, and the Apollo dashboard webhook delivery log should be inspected). Reaper exists as a backstop but the root cause needs fixing.
- ~~The reaper's first run identified contact `nayDFnGCCcrVO9oTg4ls` (Joey Evans) as a 400 on the GHL update; investigate why the standard `PUT /v1/contacts/{id}` payload failed for that one contact and decide whether the reaper needs a defensive retry path.~~ **Resolved 2026-06-05**: GHL dateUpdated confirms the reaper did write `callback_timeout` despite the 400 in the log (transient blip on the 500th sequential PUT). Vapi poller will pick him up on a later batch since his dateAdded is older than the first 40 already processed.

### Apollo API Key Rotation (Done 2026-06-05)

- Old key `W7j2vbChZDN8bfoS-wVJ2Q` replaced in all live n8n workflows with new key `CIgACIqwFAXuvYUQKHZcLA` from `.env` line 39.
- Live workflows touched: `WuxgTa0EEL1mb2SA` (Apollo Phone Enrichment intake V3) and `WmKAhG7mIaXonNsh` (Sheet First).
- Smoke test on V3 webhook `https://automations.livetransparent.com/webhook/ghl-apollo-phone-enrichment-intake-v3` (execution `75289`) confirmed the new apolloApiKey loads at runtime; downstream code errored on test payload (unrelated to key).
- **Critical**: MCP `n8n-lt` `updateNodeParameters` silently corrupts Set v3.4 Config nodes (wraps `assignments.assignments` in `{item: [...]}`, stringifies booleans and `options`). Recovery was via direct n8n REST `PUT /api/v1/workflows/{id}` using the reaper's known-good Config as a reference. Documented in `AGENTS.md` Tooling section.

### Marketing Email Pause (Done 2026-06-05)

- 9 marketing email workflows unpublished in n8n. See [Plan - VAPI Pause & Queued Goals.md](./Plan%20-%20VAPI%20Pause%20%26%20Queued%20Goals.md) for the full list, resumption playbook, and a list of channels (LinkedIn, Instagram, SimpleTexting SMS) that are still active.
- **Required owner action (outside n8n)**: open GHL location `Zwz4relUXVPxx8uohnjV` and manually pause any active marketing email sequences. Pausing the n8n workflows stops CSV imports and intake routing, but the GHL sequences themselves keep running for already-enrolled contacts.

## Next Steps

### 0. Emerging Pool Import (DONE 2026-07-02)
- **13,868 Emerald contacts** imported into Postgres `emerging_pool_contacts` (3,668 brands + 10,200 dispensaries)
- **GHL-ready CSVs** created at `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_{Brands,Dispensaries}.csv` with columns matching existing GHL `Em_*` custom fields
- Tags: `brands_pool,emerald` / `dispensaries_pool,emerald`
- Two n8n workflows created: `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`) and `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`)
- **Next**: Import CSVs into GHL via UI (Contacts → Import), then backfill `ghl_contact_id` in Postgres

### 1. Vapi Campaign Rollout (Phases 1+3 DONE, Phase 2 DATA-BLOCKED — 2026-07-02)

See `plan.md` for full details. Progress:
- **Phase 1**: **DONE** — 2 assistants created, tools cleanup, John→Jason migration, GHL tags created
- **Quality gate (PENDING)**: Manual test call per assistant (Alex + Jordan) via Vapi dashboard
- **Phase 2**: **DATA-BLOCKED** — The classifier workflow is fixed, but the current data supply is not.
  - `Cannabis-Retail-SSO-Executive-2`: 464 rows, 6 with GHL+phone, 4 not previously called
  - `Cannabis-Retail-SSO-Executive-1`: 84 rows, 1 with GHL+phone, 1 not previously called
  - No current marketing / dispensary / retail-sales source rows have the required combination of `ghl_contact_id`, usable phone, and not-called status
  - Old `sso` matching is no longer safe because it routes executives into Brand
  - To unblock: sync refreshed marketing / dispensary rows into `Emerald_Contacts`, manually approve a GHL test cohort, or define executive routing intentionally
- **Phase 3**: **DONE** — All 6 infra changes deployed (dialer mapping, intake poller campaign tags, enqueue dedup, dequeue bugfix + routing, callback trackedAssistants, Config includeOtherFields)
- **Phase 4**: **BLOCKED** — Needs quality gate plus an approved Brand/Dispensary cohort first
- **Supporting helper**: Queue feeder workflow exists and its no-op behavior has been verified as expected when candidates are already pending in `voice_call_queue`

### 2. Voice Hardening

- Move remaining secrets out of workflow `Config` nodes into n8n credentials or env-backed config.
- Verify the Vapi dashboard still points all tools and the end-of-call webhook at the current callback URL.

### 3. Reporting Depth

- Expand the contact-capture panel by channel and landing page.
- Build matched funnel views by channel, campaign, and landing page.

### 4. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Keep the user-facing emphasis on attribution first, then cost reporting.

### 5. Cleanup And Adjacent Automation

- Finish SimpleTexting secret hardening.
- Deploy the staged SMS workflows and verify the live GHL pool query.
- Fix the GHL-to-LinkedIn supply path so `linkedin_connection_state` is seeded from a working GHL contacts list and the dispatcher can send invites from that queue. [DONE 2026-06-03]
- Verify LinkedIn connection requests and DM sends from execution history. [DONE 2026-06-03]
- Retry and enable the blocked GSC ingest workflow.
- Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.

## Reporting Workflows

### Workflow List

- `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) — active, seeds report settings and runtime flags
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — active, rebuilt replacement for archived `OtqWjqGXZC3OcrXP`
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) — active
- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) — active
- `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) — active
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) — active
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) — active
- `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`) — active
- `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`) — active

### Live Reporting State

- GA4 ingestion is live and feeding the executive report.
- GHL leads and sales ingestion is live and flowing into Postgres.
- The report host is live and secure.
- The GHL `Executive Report` custom menu entry points at the report host.
- The executive summary webhook is live and returns GHL-first report JSON from Postgres.
- `LT - Report Daily Rollups` preserves GA-backed channel, UTM, landing-page, and daily traffic rows.
- Funnel-efficiency metrics are live in the executive summary API and embedded report.

### Current Cohort Notes

- `contactToOpportunityRate` uses a contact-safe cohort metric instead of a raw multi-opportunity total.
- The current 30-day new-contact cohort is still returning `0` matched contact-to-opportunity progression.
- The current attribution coverage result for that same cohort is `97` contacts, `45` with usable source fields, `45` attributed bridge matches, and `22` lead-to-sale matches after normalized raw contact IDs and stored-field fallbacks.

### Report Model

- Raw tables cover GA4 sessions, GA4 pages, GA4 events, GSC queries, GSC pages, GSC site, GHL contacts, GHL opportunities, GHL pipeline history, and GHL forms.
- Bridge tables cover traffic-to-lead, lead-to-sale, and identity mapping.
- Rollup tables cover daily summary, channel summary, funnel summary, pipeline summary, stage summary, UTM summary, and landing page summary.

### Report Next Work

1. Expand the contact-capture panel by channel and landing page.
2. Build matched funnel views by channel, campaign, and landing page.
3. Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
4. Finish SimpleTexting secret hardening.
5. Deploy the staged SMS workflows and verify the live GHL pool query.
6. Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.
7. Fix the GHL-to-LinkedIn supply path so queue rows are created from the working GHL contacts list, then verify connection requests and DM sends from execution history.
8. Retry and enable the blocked GSC ingest workflow.

### Report Dependencies

- GA4 property ID is still the external dependency for any remaining GA4 API wiring work.
- Meta Ads API access is validated on `2026-05-05` against `act_2186975138800404`.
- For GA4 service account wiring, use a secret-backed JSON file in Coolify and keep the credentials out of source control.

## Operating Notes

- Prefer Coolify internal service-to-service communication where possible.
- Verify live state after every mutation: fetch first, patch second, audit live workflow plus recent execution before declaring a fix.
- Preserve graph integrity when editing n8n workflows: keep existing node IDs and keep the connections map aligned.
- For voice automations, prefer `Switch` over `IF`, and use raw JSON import for dialer patches.
- Report end-to-end validation should still span leads ingest, attribution bridge, daily rollups, and executive summary output.
- If LinkedIn troubleshooting is resumed in a fresh session, start by reading this file, `AGENTS.md`, `repomix-output.md`, and the latest executions for `LT - LinkedIn Connection State Sync (Unipile)`, `LT - GHL LinkedIn Connect Dispatcher (Unipile)`, and `LT - LinkedIn DM Sequence (Unipile)`.
- Do not declare LinkedIn fixed until execution history shows nonzero `matched`, `upserted`, and `sent` values on the relevant workflows.

## Working Order

1. Vapi Campaign Rollout (new campaigns, 4 phases — see `plan.md`).
2. Voice hardening.
3. Reporting depth.
4. Meta attribution.
5. Cleanup and adjacent automation.
