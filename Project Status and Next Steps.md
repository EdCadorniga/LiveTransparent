# LiveTransparent Project Status and Next Steps

Updated: 2026-07-31 (partnership marketing pipeline activated, campaign-level reporting attribution, live host verification, native GHL report access check, plus prior SimpleTexting, voice, classification, ownership, and PIT-rotation work)

## Source Of Truth

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Voice stack**: ACTIVE since 2026-07-14, hardened 2026-07-16, optimized 2026-07-20, and call-path hardened 2026-07-23. All 3 outbound assistants (Jordan/Dispensary, Alex/Brand, Savannah/V1) updated: compliance disclosure removed from voicemail, discovery questions restructured to one-at-a-time with turn-taking enforcement, IVR/voicemail disambiguation added, stage-direction/throat-clearing ban, pronunciation fixes, `{{contact_name}}`→`{{first_name}}` variable corrected. On 2026-07-25, the Brand assistant and dialer were patched to remove the unresolved `{{company_name}}` opener dependency, pass `company_name` from GHL when available, and explicitly guard against missing placeholders. The dialer uses n8n's native Schedule Trigger every 2 minutes plus a timezone-aware business-hours guard; no external cron job is used. The callback webhook no longer automatically invokes the dequeue helper, and `LT - Voice Dequeue Next` is unpublished so it cannot start unscheduled calls. Callback metadata extraction, GHL note JSON handling, queue completion parameters, tag failure handling, and the 8-tag plus DNC suppression blocklist were hardened. The dialer now marks selected rows `in_progress` before the Vapi request, preventing ambiguous request failures from retrying the same contact; no-phone and outside-hours branches restore `pending`. Poller searches 4 tag pools with rotation, 30/cycle, and removes the source campaign tag after enqueueing. On 2026-07-25, the dialer was changed to continue fetching and filtering blocked/invalid contacts within the same execution, up to 25 queue checks, instead of waiting two minutes after every skipped contact. On 2026-07-30, the dialer and Call Outcome Ingest were repaired after a prolonged outage: GHL `Version` header corrected from `2023-02-21`→`2021-07-28`, the same-run loop guard was rewritten to read from Code-node items instead of invisible Postgres `RETURNING` columns, an empty-queue guard was added before GHL contact lookup, and the ingest workflow's `new Date()` expression was removed from the `queryReplacement` path. The 1,047 failed + 4 cooling_down queue rows were reset to `pending`, restoring 1,051 contacts to the active dialing pool.
- **n8n runtime**: upgraded to target `2.31.5`. Native Schedule Trigger is the standard for recurring workflows. The Python task-runner warning during deployment is expected for JavaScript-only workflows; the transient database ping timeout recovered during startup. The stale queued-execution incident was resolved by deleting 745 orphaned `new` executions after the initial targeted cleanup, leaving legitimate `waiting` executions intact. The dialer was unpublished/republished, manually smoke-tested, and confirmed to select different queue contacts. It is active and published with the same-run queue loop.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences. Reply suppression was repaired in GHL on 2026-07-26 after an inbound email continued into a later sequence step.
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (65/run every 30 min, 1,560/day capacity). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery.
- **Apollo phone enrichment**: ACTIVE and hardened 2026-07-16. Production path is polling + V4 callback + reaper. Legacy staged webhook orphans were canceled, poller now re-discovers `queued_phone`, callback provider failures map to `callback_failed`, and known blank contacts were backfilled into `queued_phone`.
- **LinkedIn**: Production path is dispatcher -> acceptance/state sync -> canonical 4-message DM sequence. Follower DM and misconfigured Instagram DM sender paths are unpublished. The dispatcher now explicitly reads Config, atomically claims `ready` rows as `requested_pending`, performs immediate GHL tag/reply checks, and fails closed on provider/state errors. State sync uses direct HTTP requests, bounded contact/API budgets, retries/timeouts, explicit error reporting, and preserves terminal/replied state. The shared state-upsert workflow promotes explicit terminal payloads to `completed` and preserves active replies. The state-upsert webhook now requires the protected `X-LT-LinkedIn-State-Secret` header; all discovered callers were updated and published, and unauthorized requests return `403`.
- **Instagram**: old DM Sequence is unpublished after it was found using the LinkedIn Unipile account. New inbound bridge is active and posts messages into GHL Conversations under `Instagram via Unipile`.
- **Social provider bridge**: Instagram and LinkedIn inbound both work through SMS-type custom conversation providers (`LinkedIn: 6a58a14ff3023bea3783c152`, `Instagram: 6a58a1193cdfc36997580a68`). Inbound uses `type: "Custom"`, not `SMS`, and avoids dummy phone/email data. GHL duplicate cleanup consolidated Edmundo Cadorniga to canonical contact `XZ4yChllGBdcsVxhFRDe`; both Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` now map there. GHL Conversations is the operator-facing inbox; no dedicated macro dashboard or alert digest is live yet. Detailed handoff and operator runbook live in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **Reporting**: GA4, GHL, and GSC ingestion are live. `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on version `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`; it finalizes success, empty, partial, and failed fetch states, does not advance watermarks on fetch failure, and preserves raw-row idempotency. The reconnected GA4 credential was verified by execution `276731`; pinned failure execution `276747` confirmed health finalization followed by an intentional n8n error. `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`; it uses ingest-date snapshots, bounded cursor/retry guards, fail-closed finalization, and health key `ghl_opportunities` to avoid collision with leads. Execution `276626` processed 7,683 opportunities and 7,683 history rows successfully. The Executive Report is deployed as build `2026-07-31-v10-partnership`; its campaign/channel table and selected-period comparison are live, and the campaign summary endpoint returns HTTP 200 with named rows including `Partnership emails`. Native GHL report `6a67dce4a51a4360c60963a3` remains the operational CRM view, but its widget configuration is still blocked by a real authenticated-page 404 plus Firebase token/permission errors.
- **SMS campaign**: SimpleTexting dispatcher is live as of 2026-07-18. On 2026-07-24, the send boundary was fixed and published: campaign messages use `AUTO` mode, failed provider claims are retryable, and GHL conversation mirroring requires a real provider message ID. On 2026-07-29/30, the campaign runner (`dUyOfxllvkxZavaw`) and phone backfill (`8hQKQi1PooYDFxNR`) were published and verified. The backfill is recovering 10 phones every 2 minutes; runner failures correctly finalize as `send_failed` without false sent tags, notes, or provider IDs. SimpleTexting still returns HTTP `409` on sends. Diagnostics confirmed the bearer token, provisioned primary number, and target contact/opt-in are valid; the remaining blocker is provider-side message acceptance/account policy. The idempotent boundary (`gwaEpWDpTIwsafi8`) is published as `a56d28c0-11f1-4938-8eea-08c6d665c3d8` with E.164 normalization and safe provider-error capture. Do not resume success-volume testing until the provider 409 is resolved.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.
- **Regulated-business classification / SDR boundary (contract clarified 2026-07-30)**: `qualified` means the contact's business is related to a regulated vertical such as nicotine, cannabis, CBD, vape, or hemp; `not qualified` means it is not a regulated business. The live classifier now writes the canonical classification tags and the Vapi intake is published with a `qualified` gate. Qualified opportunities now enter `Sales Outreach -> Qualified` through published GHL workflow version 10. Existing contact/opportunity ownership alignment is handled separately; the live Jason/Marc allocator handles records entering that stage without a native owner.
- **SDR ownership synchronization**: Published GHL workflow `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, version 7) now keeps contact owner, native opportunity owner, custom opportunity `Owner`, and routing audit fields aligned for Jason and Marc when the opportunity owner changes. It does not replace the unresolved Janvi qualification gate or allocate unowned Warm records.
- **Classification and promotion implementation (2026-07-30)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is published on version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`; `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) is published on version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`; and GHL workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) is published as version 10 with both opportunity actions targeting `Sales Outreach -> Qualified`.
- **Ownership double-handling audit (2026-07-30)**: No active duplicate owner writer was found. The classifier writes tags only; Vapi intake writes queue/Apollo state only; the active n8n MQL workflow creates or updates Warm opportunities without owners; and the GHL promotion workflow changes pipeline stage only. The sole active owner-alignment path is GHL `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, published version 7), triggered by an opportunity `assignedTo` change. It assigns the contact and updates the custom opportunity `Owner` plus routing fields, but does not assign the opportunity owner. The staged n8n workflow `VI39o4X954fYDjOQ` is inactive and must not be activated as-is because it would duplicate those contact/custom-field writes.
- **Legacy-owner migration (2026-07-30)**: Migrated the open Sales Outreach opportunities whose custom opportunity `Owner` was John or Kevin. The initial scope was 307 records (305 John, 2 Kevin). The final authoritative opportunity search returned zero remaining John/Kevin custom-owner records; native opportunity owners and the published GHL alignment cascade are now the source of truth. The staged n8n owner-sync workflow remains inactive.
- **Jason/Marc no-owner allocator (2026-07-30)**: Published n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) on a 30-minute native Schedule Trigger. It fetches open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, assigns Jason (`yU85G6kfhtW4vUtx3QE6`) or Marc (`sqGx5rp3oAUG610NXyjU`) using deterministic opportunity-ID hashing, and writes only native opportunity ownership. The first controlled run assigned 73 records successfully; sample verification confirmed contact owner and custom opportunity `Owner` cascaded correctly through GHL workflow version 7. Remaining unowned Qualified records are draining in bounded batches.
- **Follow-up sender routing - COMPLETE (2026-07-29, audited 2026-07-30)**: Workflow `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`) is published as version 39 with Jason workflow defaults (`Jason from Transparent eCom` / `jason@livetransparent.com`). All 7 Send Email actions use `From Name = {{opportunity.owner}} from Transparent eCom` and `From Email = {{user.email}}`. The six templates (one reused by 2 actions) retain literal Jason sender metadata as safe fallback. The workflow triggers on Sales Outreach stages: New, Attempting Contact 1st Attempt, 2nd Attempt, 3rd Attempt, Engaged. Marc routing path (`sqGx5rp3oAUG610NXyjU`) is configured but untested — zero Marc-owned opportunities have entered a trigger stage. Do not send a live test email unless explicitly requested.
- **Vapi transfer hardening**: Live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants now use neutral Sales Lead wording while preserving the compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- **RB2B assignment hardening**: Live workflow `3kjsIUeoEQFx26cC` no longer runs its hardcoded Kevin task during Warm intake. The legacy task node is disconnected/disabled and the workflow is published with contact persistence ending at `Result`.
- **PIT token rotation (2026-07-30)**: Full GHL PIT token rotation completed and verified. The old token was replaced with the rotated PIT across both Config nodes that embedded it (Intake Poller `bYk1Ai6MJLyhTsDZ`, Dialer `r7UjWLndmc6EqEUW`). Full REST API audit of all 67 active n8n workflows confirmed zero occurrences of the old token remain in live production paths. Both modified workflows were published with matching `versionId === activeVersionId`. Documentation (`AGENTS.md`, `repomix-output.md`, `Operating Snapshot.md`) updated. Archive/backup files in `n8n/backups/`, `n8n/voice-agent/`, and `scripts/` retain historical snapshots.

## Prioritized Next Steps

1. ~~**Deploy and verify the Executive Report**~~ **Done 2026-07-31**: the public host serves build `2026-07-31-v10-partnership`; campaign/channel rows, selected-period controls, prior-period comparison, and the HTTP 200 campaign endpoint were verified. Coolify's Git webhook did not deploy `main`, so the verified image was rebuilt from `main` and applied to the managed VPS container; the generated compose file was backed up before replacement.
2. **Complete native GHL report configuration**: restore a valid authenticated GHL UI session or obtain an explicitly approved internal API path, then verify/configure the MQL table, Brands/Dispensaries email widgets, custom open/click/response metrics, pipeline context, campaign rows, and shared date behavior. Do not use undocumented API guesses. The native report baseline exists, but its current page and widgets are not verified.
3. **Resolve SimpleTexting provider 409**: coordinate with SimpleTexting support/account settings or test the account through an approved provider console/API path. The n8n boundary, token, primary sender number, recipient contact, opt-in status, E.164 normalization, retry state, and GHL mirroring guards are verified. After the provider accepts one controlled message with a real provider ID, resume low-volume production verification and then complete the STOP-tag guard audit.
4. **Run controlled Vapi verification (dialer now operational)**: the 1,051 pending contacts are being processed. Monitor a live Brand call and a live Dispensary call from the next few dialer executions; confirm the Vapi dashboard callback/tools are present, no unresolved placeholders, no voicemail disclosure, correct one-question turn-taking, and correct outcome/queue completion via the repaired Call Outcome Ingest workflow.
5. ~~Implement Jason/Marc no-owner allocation~~ **Done 2026-07-30** — workflow `eeksgD0fbGHUqh4r` is active, 73 records assigned in first run, remaining unowned Qualified records draining in bounded batches.
6. **Harden remaining public boundaries**: authenticate Warm intake and SimpleTexting send webhooks, then migrate active Config-node secrets into protected credentials/runtime configuration. n8n Code nodes cannot access managed credentials, so this migration requires replacing direct Code-node HTTP calls with credentialed HTTP Request nodes or an approved protected runtime-variable path; do not move the same secrets into another Set/Config node.
7. **Finish reporting backlog**: retry GSC ingest, add approved Meta Ads spend/click/impression ingest, normalize Top Page formatting, and add remaining trigger-link, Unipile, and social metrics where source data supports the selected period.
8. **Migrate remaining embedded Config secrets**: replace active hardcoded GHL/Unipile values with protected credentials or approved runtime configuration, then rotate values exposed during migration. The LinkedIn state-upsert boundary is already authenticated and verified.

### Explicit Reporting Notes

- The campaign summary workflow is live and published as `64641979-71f3-466c-8a09-36013be6bc0e`; manual execution `276517` succeeded, and live 7-day/30-day endpoint checks returned named rows.
- The `2026-07-20` through `2026-07-26` email engagement gap is a historical `Email_Events` coverage gap; no event-ingest executions existed in that window. Do not change valid aggregation logic or fabricate rates.
- Four credential-bearing response captures remain intentionally untracked and must not be committed.

## Newly Confirmed Gaps

### Follow-up Sender Routing Handoff

- **User requirement**: follow-up email sender name and email must follow the opportunity/contact owner; if neither record has an owner, use Jason.
- **Workflow**: `Jason Followup Emails and SMS`, ID `f6b44e34-779e-4959-b41d-b05641f134e7`, currently published version `38`.
- **Template folder**: `Jason Follow Up Emails`, ID `69e0c9069af5986541802d88`.
- **Affected template IDs**:
  - `69e0d86b9af59801b580f4b5`
  - `69e0db27d6a707bbf190d022`
  - `69e0db9ab02114c1ba3c29d3`
  - `69e0dc56d6a707c0ac90e074`
  - `69e0dcad8ffabf47b4d987c5`
  - `69e0ddd0b021145bab3c4569`
- **Current template state**: all six have literal `fromName = Jason from Transparent eCom` and `fromEmail = jason@livetransparent.com`. Keep this as a safe fallback; the live workflow actions already override it for owned records.
- **Current workflow state**: all 7 Send Email actions use owner-driven sender fields. Verify or set Jason as the no-owner fallback user in the workflow UI. Do not hard-code Jason as the sender for owned opportunities/contacts.
- **API limitation**: `PATCH /emails/builder/{templateId}` accepts literal sender emails but rejects `{{user.email}}` with HTTP 422 (`fromEmail must be an email`). The public `GET /workflows/` endpoint confirms metadata/status/version only; workflow action definitions are not writable through the public API.
- **Browser status**: authenticated GHL workflow access was used to set and publish the Jason defaults. The published version 39 API response confirms `senderAddress` and `status: published`.
- **No test send**: no live email was sent during this investigation or patch.
- **Next session exact order**:
  1. Open the authenticated GHL workflow URL from the user-provided link.
  2. Monitor the next normal follow-up execution; do not send a live test email solely for sender verification.
  5. Reopen the workflow and verify all 7 Send Email actions and the published version.
  6. Do not change template HTML or send a live test without explicit approval.

- ~~**Dialer credential rotation**: verified against GHL, full audit of 67 active workflows confirmed PIT rotation complete. Both Config nodes updated and published.~~ **Done 2026-07-30**
- **Callback authentication**: Vapi server authentication is configured on all four tracked assistants and enforced at the callback boundary with `X-Vapi-Secret`. Unauthorized callback, status, and tool payloads are rejected before routing.
- **SMS and Warm webhook authentication**: several live intake/send webhooks have empty shared-secret configuration and require an authentication pass before continued public use.
- **Credential storage**: active n8n Config nodes still contain API keys and webhook secrets. Migrate to n8n credentials or protected runtime configuration, then rotate exposed values.
- **LinkedIn state-upsert boundary**: `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on version `d9168bbc-9c96-44fd-a356-12e645a2ec3d` with terminal-state promotion, reply preservation, and protected `httpHeaderAuth`. All discovered callers are published with the shared header; unauthorized verification returned `403` and malformed authorized verification reached validation without writing state.
- **Ingest hardening (2026-07-31)**: GA4 empty/failure finalization, sales snapshot-date and cursor guards, sales `ghl_opportunities` health isolation, LinkedIn sync budgets/retries, dispatcher pre-invite claims, and terminal-state promotion are live and published. Dispatcher and sync were not live-executed during verification because they can mutate LinkedIn state or send invites.
- **Reporting owner dimensions**: contact owner, opportunity custom `Owner`, owner conflicts, and canonical SDR identity are not normalized into the reporting read model.
- **Campaign-level reporting dimensions**: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`, published `64641979-71f3-466c-8a09-36013be6bc0e`) now returns named campaign/channel rows. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list`, and Vapi uses queue campaign IDs. `General outbound`, `Partnership emails`, `xyz`, and `abc` are present as catalog rows but remain zero until matching source events exist. Emerald event attribution still has an `Emerald - attributed` fallback, and LinkedIn rows currently show zero in the tested window because no attributable activity events were stored.
- **Tag-based attribution audit (2026-07-30)**: DAN has reliable queue tags (`Enrollment Queue - DAN - Brands/Dispensaries`) plus `DAN_Release_Log.campaign` and `enrollment_tag`; `brands_pool`/`dispensaries_pool` should remain supporting audience evidence. Emerald has eight bucket-specific queue tags and matching `Seq Emerald - ...` tags, with stronger backend fields in `Emerald_Campaign_Contacts.bucket/email_campaign` and `Emerald_Release_Log.bucket`. SMS has lifecycle tags but its durable campaign identifier is `SimpleTexting_Campaign_State/Event_Log.campaign_key`; `sms_drip` is only the eligibility pool. LinkedIn has lifecycle/suppression tags but no durable campaign tag, so current Brand/Dispensary attribution must use `emerging_pool_contacts.source_list` or historical pool-tag observations until a campaign key is added to state.
- **Vapi correlation**: end-of-call callbacks now recover missing `queue_id` values from prior `voice_call_attempt` records when possible. The dialer also reclaims stale `in_progress` locks after 15 minutes, while unresolved provider correlation remains observable through the callback execution path.
- **Gap fixes applied 2026-07-25**: silent human Vapi answers now classify as `interest_unknown`; dialer global hours are 9am-5pm CT; invalid campaign tags fail closed; source-tag cleanup is dynamic; report config/publish schedules are connected and tested; superseded Apollo Sheet First webhook is unpublished.
- **Vapi hardening applied 2026-07-27**: intake, direct enqueue, and dialer paths require the `not qualified` suppression guard plus an open Warm → New opportunity; callback requests require the Vapi server secret; tool outcomes complete queue rows; timer scheduling uses an atomic Postgres claim; stale queue locks are reclaimed; timer and GHL cleanup requests retry transient failures. The intake still needs to require positive `qualified` classification so raw pool tags cannot bypass the classifier.

## Email Campaign — Emerald (Active 2026-07-07)

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (All Published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed}
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Reply Suppression Repair (2026-07-26)

- **Incident**: Christy Essex replied on 2026-07-23 that she had left Vangst and referred new/current-project questions to Logan Humiston. An automated Emerald follow-up was still sent on 2026-07-26.
- **Root cause**: `WL - Seq - Stop on Booked/Reply/Closed` had the correct `Customer Replied to Sequence Emails` trigger filtered to Email, but its `Remove from Workflow` action only removed the legacy Variant A/B workflows. It did not include the Emerald sequence workflows.
- **Fix**: Through the GHL UI, added all 12 Emerald sequence workflows, including P2 variants, to the removal action. Published as version 17.
- **Immediate containment**: Removed Christy's `seq enrolled - emerald` and `seq emerald - executives sso` tags. Her Warm/MQL context and opportunity were preserved.
- **Boundary**: n8n `LT - Email Event Ingest` remains reporting-only; it stores events in `Email_Events` and is not the sequence suppression mechanism.

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,165 | ~14,702 pending, ~5,463 released |
| Emerald_Release_Log | 250+ | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## Email Campaign — DAN Brands & Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Status

- Templates: CREATED (10/10 -- 5 Brand + 5 Dispensary)
- Tags: CREATED (5/5 -- deployed via GHL API)
- Dispatcher: LIVE (toUG1yPDmFG48KEP, active with defaultDryRun=false, every 30 min, candidateLimit=65)
- GHL Workflows: ALL PUBLISHED (3/3)
- Deck Download automations: CREATED in GHL
- ghl_contact_id backfill: COMPLETED 2026-07-13 (13,705 IDs backfilled via email/phone/name matching)
- **5,373 contacts now eligible for DAN dispatch (up from 13 before backfill)**
- **First dispatches confirmed**: Emails sending via GHL (TYPE_EMAIL outbound automated verified)
- **Rate limiting fix**: 250ms delay added between GHL API calls — errors dropped from 40% to 0%
- **2026-07-15 audit**: 5 fixes applied (brand starvation, HTTP wrapper, sender rotation, error logging, jitter)
- **GHL templates verified**: All 10 DAN templates in GHL match repo HTML files exactly

### GHL Workflows

| Workflow | ID |
|----------|-----|
| DAN - Brands Sequence | 5d25147c-cd63-4c4f-ba49-a0e62c53ee0c |
| DAN - Dispensaries Sequence | ec24cbb8-bd0b-4e6e-8607-d93886a02034 |
| DAN - Stop on Reply or Booked | d7ff2fc2-cdc2-4952-afa7-71cd9edfc490 |

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Template IDs (Brands, folder 6a4f6b06a3e9bfb4f9ebe8ad)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fdf525ebffbb911d88c | DAN - Brand 1 - Quick Question |
| 2 | 6a4f6fe0f34b953ec0cfcf5d | DAN - Brand 2 - How It Works |
| 3 | 6a4f6fe15e7d25184dafed44 | DAN - Brand 3 - Housing Works |
| 4 | 6a4f6fe2525ebffbb911d899 | DAN - Brand 4 - Short Version |
| 5 | 6a4f6fe3890f1fb4ac750664 | DAN - Brand 5 - Closing |

### Template IDs (Dispensaries, folder 6a4f6b128c6f614ebf8ba9e9)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fe4890f1fb4ac750680 | DAN - Dispensary 1 - Foot Traffic |
| 2 | 6a4f6fe41ad559bda229477d | DAN - Dispensary 2 - How It Works |
| 3 | 6a4f6fe55e7d25184dafed8a | DAN - Dispensary 3 - Housing Works |
| 4 | 6a4f6fe6f74b73e4b5b9ad8d | DAN - Dispensary 4 - Founding Partner |
| 5 | 6a4f6fe71ad559bda2294793 | DAN - Dispensary 5 - Closing |

**Duplicate**: 6a4f6fcdf74b73e4b5b9ac0b — already removed from GHL (verified 2026-07-15)

## Voice Workflows

Phone: +1 (562) 534 1977
Callback webhook: https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback

### Active

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Webhook |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Webhook |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Unpublished helper |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (native Schedule Trigger every 10 min, 30 contacts/cycle, tag rotation) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is active on a native 15-minute Schedule Trigger.
- It selects up to 10 Brand and 10 Dispensary candidates per run, uses live GHL suppression checks, and applies Vapi campaign tags only after DeepSeek acceptance or a qualified-domain match.
- `vapi_qualified_domains` is updated only after a successful campaign-tag write; free-email domains, cleanup rows, failed writes, and rejected model output are excluded.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes.

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **Historical ET-forward timing**: the previous cron-based schedule shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. The current implementation uses a native two-minute Schedule Trigger; the timezone-aware business-hours guard remains authoritative.

### Fixes Applied — Round 2 (2026-07-14, Full Vapi Audit)

A comprehensive logic/code/optimization audit of all 12 Vapi workflows found 5 bugs across 3 active workflows, all fixed and published:

**1. Race condition: Dialer could send duplicate calls** (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` was a read-only `SELECT...LIMIT 1`. Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item. Fixed: changed to `UPDATE...FROM...RETURNING` that atomically locks the row at fetch time.

**2. `report_referral` tool was dead code** (fx4UvKUWbqJEY3LK)
Routed to end-of-call handler that checked `endedReason`/`analysis.summary` — absent on tool call payloads. Node returned `[]` silently. Fixed: re-routed to `Respond - 200`.

**3. Intake Poller could create duplicate queue entries** (bYk1Ai6MJLyhTsDZ)
INSERT lacked `WHERE NOT EXISTS` dedup check. Fixed: wrapped INSERT with `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also fixed `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing).

**4. Workflow-crashing tag removals** (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes lacked `continueOnFail`. A flaky GHL API call crashed the workflow after enqueue/enrich/skip already succeeded. Fixed: enabled `continueOnFail: true` on all three.

**5. Timer race condition** (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain. Fixed: replaced `timersScheduled` boolean with `timersScheduledAt` timestamp and 60-second dedup window.

### Fixes Applied — Call-Path and Callback Hardening (2026-07-22 to 2026-07-23)

- **Unscheduled call path removed**: the callback workflow previously posted to `LT - Voice Dequeue Next` after every end-of-call event. That helper could start another Vapi call without the dialer's Schedule Trigger. The callback trigger was removed and `LT - Voice Dequeue Next` was unpublished; it is now an explicit helper only.
- **Callback payload recovery**: the callback Config Set node replaced the webhook input before detection. `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` item directly.
- **End-of-call metadata coverage**: the normalizer now reads IDs from Vapi `assistant.metadata`, `assistant.variableValues`, and `artifact.variables` paths.
- **GHL note safety**: completion-note JSON now uses an object expression instead of interpolating unescaped summaries into a JSON string. Note and tag writes are non-blocking so a CRM note failure cannot prevent queue completion.
- **Queue completion safety**: `Postgres - Mark Queue Completed` now passes query replacements as an array, preventing the scalar-parameter error that previously stopped completion.
- **Scheduler standardization**: the outbound dialer uses a fresh native Schedule Trigger with a two-minute interval. The business-hours guard remains the call eligibility authority. Resolved 2026-07-30: the dialer was crashing on every execution due to three separate bugs (GHL `Version` header, Postgres `RETURNING` visibility, empty-queue 403) — fixed and verified end-to-end.

### Fixes Applied — Brand Prompt and Variable Context (2026-07-25)

- **Execution audit**: callback execution `241579` received an `in-progress` status update and entered the background timer as designed. The corresponding end-of-call callback `241581` completed successfully for queue `7aed3bdb-fe22-4b98-a4ce-33b9018fe32b`, normalized the outcome as `voicemail`, applied `vapi_voicemail` and `vapi_voicemail_left`, inserted the call attempt, and marked the queue row completed.
- **Brand assistant prompt** (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`): removed `{{company_name}}` from the first-message opener so a missing company value cannot be spoken as an unresolved placeholder. Added explicit runtime-variable handling, IVR-versus-voicemail disambiguation, one-question turn-taking, and no-stage-direction rules. The live-call AI/recording disclosure remains system-prompt-only and is excluded from voicemail.
- **Outbound dialer** (`r7UjWLndmc6EqEUW`): `Code - Check Phone` now extracts `company_name` from the GHL contact; `Build Vapi Body` passes it through `assistantOverrides.variableValues` and metadata. The workflow was republished and verified with matching `versionId` and `activeVersionId`.

### Queue State

**1,051 contacts pending** (reset 2026-07-30 from 1,047 failed + 4 cooling_down), 1,615 completed. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer is configured for a native two-minute Schedule Trigger and picks up from queue only during timezone-aware business hours. Blocked/invalid/outside-hours candidates are released and skipped within the same execution, capped at 25 queue checks.

### Final Production Hardening — 2026-07-23

- Callback timer state now has the existing 60-second duplicate-start guard plus 30-minute pruning of ended/inactive records.
- `LT - Voice Queue Enqueue` now requires `X-LT-Voice-Queue-Secret`; callers use `VOICE_QUEUE_ENQUEUE_SECRET` and unauthenticated requests fail closed before queue insertion.
- Apollo phone-request failures are counted as `apollo_phone_request_failed` for monitoring.
- `LT - Apollo Queued Timeout Reaper` now connects its Slack summary builder to `Post to Slack #leads`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- All modified live workflow versions were verified published with matching `versionId` and `activeVersionId`.

### LinkedIn Queue State

Legacy step-4 LinkedIn DM rows are now marked with `linkedin_dm_sequence_completed` and excluded from future DM selection. The GHL connect dispatcher was stuck with 0 `ready` contacts because its feeder tag check was broken (never detected blocking tags). Fixed 2026-07-14 by unwrapping GHL's nested `contact.tags` response. 14,987 contacts from CSV bulk-upserted as `connection_status = 'ready'` on 2026-07-13. Dispatcher should now find contacts on its next scheduled run.

### Call History Summary (voice_call_attempt)

1,711 total attempts across 1,045 unique contacts. Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18.

## LinkedIn Workflows (Production Active + Duplicate Send Paths Stopped)

| Workflow | ID | Schedule | Notes |
|----------|----|----------|-------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | 0 12-22 * * 1-5 | Fixed trailing backtick in jsCode; added template pre-sanitize + send-time sanitize in both DM sender nodes |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished | Redundant one-touch follower DM path; stopped 2026-07-16 after canonical connected-contact DM sequence was confirmed as the only production DM path |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | */15 15-21 * * 1-5 | Fixed GHL response unwrap in tag check; added send-time sanitize for invites; added linkedin_dm_sequence_completed to Feeder tag block |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | 15 */6 * * * | Reduced maxPages 15→5, maxContacts 200→50 |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Webhook | Replaced $env.UNIPILE_ACCOUNT_ID with hardcoded value |
| LT - LinkedIn Connection State Upsert (Unipile) | Old7ZvyVYgFaJgDr | Webhook | No changes |
| LT - LinkedIn Unipile New Messages (Unipile) | 7o5EBdvwAuIaWW7k | Webhook | No changes |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual only | No changes |
| **LT - LinkedIn DM Suppression from GHL Tag** | **IPN8jnR3XSurX0o1** | **Webhook** | **NEW 2026-07-15. GHL tag stop_linkedin_dms → webhook → Unipile lookup → GHL tag + state table terminal** |

Intentionally stopped non-canonical sender: `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) is unpublished. It was using the LinkedIn Unipile account ID and sending Instagram templates as LinkedIn DMs via `instagram_dm_state`.

Guardrails: John-branded copy blocked before Unipile send. Invite defaults say Transparent eCom (not LiveTransparent).

Outbound guardrails: DM sends now fail closed if the reply lookup fails, and both DM / request paths skip when an inbound conversation is already present.

### 2026-07-15 Unicode Encoding Fix
All audited Unipile message sender nodes now sanitize message text before API calls, and template registries are pre-sanitized where present. Coverage includes LinkedIn DM Sequence (`Sync Connected from Unipile` and `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. `sanitizeMessage()` handles smart punctuation plus mojibake forms like `canâ€™t` / `canΓÇÖt`. Final live audit passed: active versions published, send-time sanitization present, registry pre-sanitization present where applicable, and no remaining bad literal template text in audited sender nodes. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.

### 2026-07-16 Sender Path Cleanup
Malformed LinkedIn screenshot messages were traced to `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM Sequence. Unpublished both `iCnY6ccdHhfJg3sf` and redundant `pq7XVajNFnnwMUTr`; production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.

### 2026-07-14 Fixes Summary
- **Connection Acceptance Checker**: `$env.UNIPILE_ACCOUNT_ID` blocked by N8N_BLOCK_ENV_ACCESS_IN_NODE → hardcoded
- **Connection State Sync**: Code node timed out at 300s → reduced batch sizes
- **Follower DM Sequence**: Code referenced missing Config fields → added them
- **DM Sequence**: Trailing backtick in `jsCode` caused syntax error → removed
- **Dispatcher feeder tag check**: `GET /contacts/{id}` returns tags at `contact.tags`, not flat `tags`. Whole pipeline was stuck because blocking tags were never detected. Fixed by unwrapping through `.contact` first.

### Dispatcher Queue State
The `linkedin_connection_state` table was exhausted (all contacts at `requested`/`connected` from June). User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook as `connection_status = 'ready'`. Dispatcher's Fetch Ready Queue should now find contacts on next run.

## Instagram

### Active

| Workflow | ID | Status | Notes |
|----------|----|--------|-------|
| LT - Instagram Unipile New Messages | pISlgYUsyJIrLuJd | Active webhook | Receives Unipile Instagram inbound payloads at `/webhook/lt-unipile-instagram-new-messages`, normalizes identity, creates/updates GHL contacts, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token, and posts inbound messages into GHL Conversations under `Instagram via Unipile`. |

### Stopped

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished | It was using LinkedIn Unipile account `V9eiHiDpRmCtan0YNdzsQw` and could send Instagram templates as LinkedIn DMs through `instagram_dm_state`. Do not republish until rebuilt with Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, account-type guard, reply suppression, and safe cadence. |

### 2026-07-16 Inbound Mapping Status

- Detailed build context, endpoint contracts, known test payload, and next steps: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Confirmed real Instagram Unipile account: `F2UprZ8aQc6Qm9CYYWU6cg` (`Transparent eCom`).
- Confirmed test inbound identity: `edmundocadorniga`, profile provider ID `6361495593`, messaging/provider ID `109928757071246`, chat ID `yx-R-9J6XdWaFpGOQd1JFA`.
- Created GHL custom fields for Instagram username/profile URL/profile provider ID/chat attendee ID/chat ID.
- Post-merge cleanup: GHL duplicate contacts for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; `instagram_conversation_map.id = 1` now maps chat `yx-R-9J6XdWaFpGOQd1JFA` to that canonical contact.
- Inbound OAuth fix: the workflow converts the stored agency token to a location token inline before calling GHL inbound APIs.
- Direct outbound router test: POST to `/webhook/lt-social-provider-outbound` routed the known Instagram contact/chat to Unipile successfully with message id `DOfjxs8_Xm26V5Ee1IO7PQ`.
- Map repair verification: temporary maintenance workflow `nuuB3qCKxr7J6iPw` repointed Instagram map row `1` and LinkedIn map row `2` to `XZ4yChllGBdcsVxhFRDe`, then was archived. Direct outbound router checks succeeded for Instagram (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn (`C7I9944kWsSKutX2XhZEpA`).
- GHL UI outbound verification: message `this is a test reply from GHL to Instagram` routed through `LT - Social Provider Outbound Router` to Unipile message `iEJO1vnvWVGwbk7ril1__A`.

### Social Provider Next Steps

- Monitor the next real Instagram inbound after duplicate cleanup; avoid artificial replays unless needed because they create visible conversation messages.
- Confirm Unipile Instagram webhook delivery to `/webhook/lt-unipile-instagram-new-messages` in production.
- `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) direct webhook path is fixed and routes canonical contact `XZ4yChllGBdcsVxhFRDe` to Instagram and LinkedIn via Unipile successfully using canonical provider IDs.
- Optionally run a controlled LinkedIn GHL UI outbound reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Build and verify a lightweight macro alert/digest path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.
- Rebuild Instagram outbound/follower DM only after the bidirectional inbox path is stable and guarded.

## Apollo Phone Enrichment (Repaired 2026-07-14, Audited + Hardened 2026-07-15)

### Before Fix (2026-07-14)

All 3 webhook-based workflows had 0 executions since 2026-05-13. 1,279 contacts collected `callback_timeout`. Entire pipeline was dead.

### After Fix (2026-07-14)

New **LT - Apollo Phone Enrichment Polling** (JH8ShfpglWmLMZ3l) replaces the webhook-based intake:

1. **Sync profile match**: Calls Apollo `/v1/people/match`, writes name/email/company/LinkedIn/title/dept/revenue to GHL immediately
2. **Async phone request**: Calls Apollo with `webhook_url` pointing to existing V4 callback handler
3. **V4 callback** receives phone data and updates GHL

State as of activation (first hour): 60 contacts enriched, 30/run at 30-min cadence.

### 2026-07-15 Full Audit (7 workflows)

Full review found 2 CRITICAL bugs (`queued_phone` invisible to reaper, Intake Poller re-trigger), 2 HIGH issues (HTTP wrapper, V3 no error handling), and several medium/low cleanups. **10 fixes applied across 6 workflows**:

| # | Severity | Fix |
|---|----------|-----|
| 1 | CRITICAL | Reaper now monitors both `queued` + `queued_phone`; polling writes `Queued At` date |
| 2 | CRITICAL | Intake Poller routes `queued_phone` to `waiting` (was defaulting to `enrich`) |
| 3 | CRITICAL | Sheet First SQL injection fixed — parameterized query replacing template literal |
| 4 | HIGH | `doHttpRequest` wrapper removed from all 4 active workflows (V4, V3, Intake Poller, Sheet First) |
| 5 | HIGH | V3 callback: added error handling catch block with `callback_failed`, then **unpublished** V3 |
| 6 | MEDIUM | Polling `ghl()` now returns status codes; 429 triggers 5s retry on all 3 search sources |
| 7 | MEDIUM | V4 `Apollo Contact Id` now always set (was phone-gated) |
| 8 | LOW | Reaper Config node corruption cleaned (nested `parameters.parameters` removed) |
| 9 | LOW | Intake Poller `removeTag()` — removed `$httpRequest` fallback, now direct `this.helpers.httpRequest` |
| 10 | N/A | `$httpRequest` reference eliminated from all Apollo workflows |

### Pipeline Status (end-to-end)

| Step | Workflow | Handles |
|------|----------|---------|
| Discovery | Intake Poller (bYk1) | Tags contacts, sets `Enrich Phone via Apollo = Yes` |
| Sync match | Polling (JH8Sh) | Apollo `/v1/people/match` → writes profile, sets `queued_phone` + date |
| Async phone | Polling (JH8Sh) | Apollo with webhook → V4 callback |
| Phone callback | V4 Callback (U7c6) | Writes phone to GHL + `enriched` status |
| Re-enqueue | Intake Poller (bYk1) | Finds `enriched` contacts → inserts to voice_call_queue |
| Timeout | Reaper (RL5Zy) | Hourly scan for `queued` + `queued_phone` → `callback_timeout` after 24h |

### Workflow Summary

| Workflow | ID | Status | Purpose |
|----------|-----|--------|---------|
| LT - Apollo Phone Enrichment Polling | JH8ShfpglWmLMZ3l | Active, every 30 min | Polls GHL, calls Apollo sync+async, writes profile + triggers phone callback |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active, webhook | Receives Apollo async phone callbacks, writes phone to GHL |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** | Legacy V3, fully superseded by V4 |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active, webhook | 0 executions — superseded by polling, SQL injection fixed |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** | Legacy path. 1,008 orphaned webhook executions canceled on 2026-07-16; not part of production enrichment |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active, hourly | Flips stale `queued` + `queued_phone` to `callback_timeout` |

### 2026-07-16 Production Hardening

- Verified live production workflows are active and published:
  - Polling `JH8ShfpglWmLMZ3l`
  - Callback V4 `U7c6byTLXAMgcS75`
  - Reaper `RL5ZyUoshSPbmVA1`
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed past the `Webhook` node.
- Polling workflow fix: orphan status rediscovery now includes both `queued` and `queued_phone`.
- Callback V4 fix: Apollo provider-level callback failures now map to `callback_failed` rather than silently landing as `no_match`.
- Polling write-path fix: hardened GHL `PUT /contacts/{id}` fallback after reproducing live API behavior.
  Working update shape is `customFields` without `locationId`; payloads containing `locationId` or `customField` can return `422`.
- Polling now has a minimal fallback write so contacts are not left blank when the full Apollo profile write fails.
- Backfilled 6 previously blank contacts into `queued_phone` on 2026-07-16:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

## SMS Campaign — SimpleTexting via GHL (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

### Live n8n Workflow State

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Receives GHL outbound messages at `/webhook/lt-simpletexting-provider-outbound`, validates provider ID, normalizes phone to E.164, sends via idempotent boundary → SimpleTexting API. Skips business-hours guard for human replies. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Slack alert preserved. Now also posts inbound messages to GHL Conversations under `SimpleTexting SMS` via `type: "Custom"` + `conversationProviderId`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Mirrors successful outbound campaign sends into GHL Conversations under `SimpleTexting SMS`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated SMS boundary. Called by outbound router and campaign send paths. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Active | `sms_drip`, 10/run, weekdays 10:15am + 3:00pm ET, `defaultDryRun=false`. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Active | 6-step flow, 2-day inter-step delay. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | No changes needed. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | No changes needed. |

### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- SimpleTexting send boundary uses `AUTO` mode so multi-segment campaign messages are accepted; provider errors are persisted for diagnosis and can be reclaimed on retry.
- Campaign mirroring is gated on `action = message_sent` and a non-empty provider message ID. Dry runs, blocked sends, duplicates, and provider errors do not call GHL Conversations.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

### Current Template Registry

- Send webhook: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`.
- Canonical keys: `sms_1` through `sms_6`.
- Updated 2026-07-26: `sms_1`, `sms_3`, and `sms_5`.
- Unchanged 2026-07-26: `sms_2` and `sms_6`.
- Updated 2026-07-29: `sms_4` removed cannabis product terms and the unreliable Facebook ad preview link while retaining `regulated-industry` positioning. The published active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- Existing `john_sms1` through `john_sms5` payload aliases remain in place for compatibility and were not renamed.

### 2026-07-24 Fix And Next-Run Check

- Root cause of the `409` provider errors: `LT - SMS Idempotent Send` hardcoded `SINGLE_SMS_STRICTLY`, while SMS 1 is 320 characters and requires multi-segment delivery.
- Root cause of the GHL `404 Contact id not given`: `LT - SimpleTexting SMS Send` mirrored blocked and dry-run outcomes instead of only successful provider sends.
- Fixed and published workflows: `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`) and `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`).
- Safe checks passed: idempotent `simulate:true` execution `241272`; campaign dry run `241275` stopped before the mirror node.
- **Next scheduled dispatcher check:** confirm at least one `status = sent` result with a real SimpleTexting provider message ID, no HTTP `409`, no GHL `Contact id not given` errors, and a matching `report_sms_sent.provider_response` record. Then confirm the campaign state advances to `sent_step_1` only for an actual provider send.

## Partnership Marketing Pipeline (LIVE 2026-07-31)

131 content partnership contacts imported from two CSV lists ("Email" and "LinkedIn") and merged/deduplicated. Two parallel outbound sequences run from Cameron's accounts: a 4-step email sequence (60/day, 11am ET Mon-Fri) and a 4-step LinkedIn DM cadence dispatched through Unipile (30 connection requests/day, 3pm CT Mon-Fri). Both sequences use 2-weekday intervals between steps. All infrastructure is fully isolated from the main DAN/Emerald pipelines (separate Postgres tables, separate n8n workflows, separate GHL pipeline).

### Import

- 131 unique contacts after dedup/merge (script: `scripts/clean_partnership_data.py`)
- 98 email contacts imported via n8n batch workflow (`zmrYrUjVcyXaS7PJ`, webhook `/webhook/lt-partnership-bulk-import`)
- 33 LinkedIn-only contacts created in GHL via MCP (no email; LinkedIn URLs set via `ew6uQQnAjgCbjeGn` webhook)
- All contacts assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- Tags: `partner_candidate_email` (email contacts), `partner_candidate_linkedin` (LinkedIn contacts), or both
- 14 contacts excluded from original CSV due to wrong company/email domain mismatches — awaiting corrections from user
- Test contact `NVAp2GdpbWXLheyUgVf2` (edmundocadorniga@gmail.com) cleaned — partnership tags removed

### GHL Pipeline

- Pipeline: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`)
- Stages: New Partner Lead (`ccc3d423-ff86-46b4-bd53-064458910eba`) → Contacted → Proposal Sent → Closed
- Opportunities created automatically by Reply Handler when a contact replies (email or LinkedIn)

### Email Templates

4 templates created in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`), populated with HTML via PATCH API and `{{contact.first_name}}` merge fields:

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher currently sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The templates exist for open tracking and deliverability but are not the primary send path. The dispatcher's inline HTML in the Code node is the canonical message content.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'`. Tracks connection status, sequence step, and DM state. |
| `partnership_release_log` | Tracks every sent email (contact, step, status, message ID). UNIQUE on `(ghl_contact_id, email_step)`. |

### GHL API Key

PIT token `pit-48a3b580-6906-418b-8215-3257599fd551` is the live API key for this pipeline, embedded in dispatcher Config nodes and used by the Reply Poller via `$env.GHL_PIT`.

### Tags

| Tag | Purpose |
|-----|---------|
| `partner_candidate_email` | Import tag — marks contact for email sequence |
| `partner_candidate_linkedin` | Import tag — marks contact for LinkedIn sequence |
| `partner_email_queued` | Applied after first email send — marks contact as active in email sequence |
| `partner_linkedin_requested` | Applied after LinkedIn connection request sent |
| `partner_email_sequence_completed` | Terminal — all 4 emails sent |
| `partner_replied` | Terminal — contact replied (stops all sequences, creates opportunity) |
| `partner_not_interested` | Terminal — manual override |
| `partner_do_not_contact` | Terminal — manual override |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | Sends 4-step email sequence via GHL Conversations API. 60/day cap, 11am ET Mon-Fri, 2-weekday intervals. |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | Sends LinkedIn connection requests via Unipile. 30/day cap, 3pm CT Mon-Fri. Atomic ready→requested_pending claim. |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step LinkedIn DM cadence for connected partnership contacts. 2-weekday intervals. |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | POST `/webhook/lt-partnership-reply`. Tags contact `partner_replied`, creates opportunity in Partnership Pipeline → New Partner Lead, posts Slack alert. |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Schedule Trigger every 5 min. Polls GHL for inbound email replies from `partner_email_queued` contacts, triggers Reply Handler on detection. |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | Bulk-imported 98 email contacts into GHL. |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on 33 LinkedIn-only contacts. |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows were patched to also query `partnership_linkedin_connection_state`:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION to include partnership rows; `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL select + separate Update node for partnership table |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing node + separate partnership update |

### Audit (2026-07-31)

Full post-build audit completed:
- All 7 partnership workflows published and active
- 3 patched LinkedIn workflows verified with correct partnership table queries, routing, and update nodes
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL includes `partnership_release_log` via UNION ALL (published version `6641aa9a`)
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped and verified
- Executive Report frontend deployed as build `2026-07-31-v10-partnership`
- GHL contacts verified: 98 with `partner_candidate_email`, 127 with `partner_candidate_linkedin` (94 overlap), 131 total
- 4 email templates confirmed in folder `Partnership Email Campaign`, all with correct HTML content
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected

### Remaining

- **GHL Custom Report**: Add partnership metrics to native report `6a67dce4a51a4360c60963a3` — requires authenticated browser session
- **Reply Poller API gap resolved 2026-07-31**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) now uses `POST /conversations/search`, records lookup failures, and fails closed instead of treating an ambiguous lookup as no reply. Published version `04cf007e-0ed1-41c7-abf5-4d1174b4bc9f`; manual execution `277923` succeeded with no active partnership email queue.
- **14 excluded contacts**: User to provide corrected company names; re-import when available
- **Marc-owned follow-up sender routing**: Untested — zero Marc-owned opportunities exist in trigger stages

## Reporting

### Active Workflows

| Workflow | ID |
|----------|-----|
| LT - GHL Daily Leads Ingest | osIJOgBmWITF5Yuv |
| LT - GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 |
| LT - GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l |
| LT - GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG |
| LT - GHL Daily Social Ingest | QZoqCaTwDhbym80O |
| LT - GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq |
| LT - GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi |
| LT - GSC Daily Ingest | xHqmCC1vOeZ11gCd |
| LT - GSC Rollup Bridge | fOVBHwti9rC3qrLV |
| LT - Report Attribution Bridge | Y0TU7Il71JswxOBp |
| LT - Report Daily Rollups | EUeOiRttoVLQ9zF9 |
| LT - Report Executive Summary API | Bukc0mgOD2r7V6ED |
| LT - Report QA and Alerts | M5mXcDTFSko6EdHb |
| LT - Report Config Sync | aomO3Z4AXJIgEvvN |
| LT - Report Publish Refresh | 3gXztCnBEN6sGINb |
| LT - Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 |
| LT - Report Pipeline Velocity | iFfwh0jpYUZoDhDR |
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV |

### State

GA4, GHL, and GSC ingestion are all live. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

### 2026-07-25 GHL Leads Ingest Rate-Limit Hardening

- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) failed in `Fetch + Normalize Leads` with GHL HTTP `429 Too Many Requests` during paginated contact retrieval (execution `241845`).
- Replaced the task-runner-incompatible HTTP wrapper with direct `this.helpers.httpRequest` calls.
- Added bounded 429 handling: up to four attempts per page, honoring `Retry-After` when available and otherwise using exponential backoff.
- Added a 500 ms delay between pagination requests to reduce GHL rate-limit pressure.
- Published workflow version `c740c006-fef5-4873-91b5-d2d4218872de` and confirmed it is the active version.
- Manual production-path validation execution `241894` succeeded: 500 contacts fetched, raw lead upserts completed, sync watermark and source health updated, and final status was `success`.
- Updated local reporting SDK snapshots (`leads_ingest_sdk_v2.ts`, `leads_ingest_sdk_v2_clean.ts`, and `leads_ingest_sdk_v3.ts`) with the same HTTP hardening.

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- ~~Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools~~ — Confirmed: poller running successfully every 10 min throughout 2026-07-20 dialer outage
- ~~Monitor Outbound Dialer~~ — Dialer recovered 2026-07-20 after stuck-queue fix (contact `AX3wfQNpRwm6DG0HgUE2` deleted from GHL, `neverError: true` applied to lookup, `onError: continueRegularOutput` on call note)
- Watch for GHL rate limiting on downstream nodes
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Test live calls with both Brand and Dispensary assistants after system prompt updates (discovery questions should flow one-at-a-time, no disclosure on voicemail, no "clears throat", "from Transparent eCom" not "with a transparent")
- Consider switching Jordan's voice from Nico to Emma/Layla (both already fallbacks) to eliminate remaining TTS artifacts
- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback

### 3. Emerald Email Campaign Ramp

Monitor first week of dispatcher runs. Verify Email_Events data quality. Increase warmup caps as sender reputation builds. Currently ~250/hr, ~1,200/day capacity with 4 senders.

### 4. Reporting Depth

- Expand contact-capture panel by channel and landing page
- Build matched funnel views by channel, campaign, and landing page

### 5. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics

### 6. DAN Email Campaign Ramp

- Monitor dispatcher runs at 65/cycle every 30 min — verify consistent deliverability (5 fixes applied 2026-07-15)
- Track Email_Events for DAN campaign data quality (opens, clicks, bounces)
- Monitor DAN_Release_Log growth — ~1,200/day target should exhaust eligible pool in ~4 days
- Recurring DNC contacts (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms) are not written to release log but reappear each run — address stale tags in report_raw_ghl_contacts to reduce waste
- Verify sender rotation (4 senders) doesn't trigger GHL domain limits

### 7. Apollo Enrichment — MONITORING (audited + hardened 2026-07-15)

- ~~Watch polling workflow runs to confirm steady 30/cycle consumption~~ — Confirmed: batch size 50, steady 30-min runs, all successful
- ~~Verify V4 callback handler starts receiving Apollo async phone responses~~ — Confirmed: 1,058+ callbacks received by 2026-07-16, working
- ~~Confirm `queued_phone` contacts transition to `enriched` as callbacks arrive~~ — Pipeline confirmed end-to-end. Reaper now monitors both statuses.
- ~~Retune maxPerRun and schedule if Apollo rate limits appear~~ — 429 retry with 5s delay added to all 3 search sources
- ~~Ensure legacy blank contacts are not left invisible after poller write failures~~ — Fixed 2026-07-16 with hardened poller fallback + 6-contact backfill to `queued_phone`
- **ACTIVE MONITORING**: Watch Reaper Slack reports for `queued_phone` reaping counts
- **ACTIVE MONITORING**: Confirm polling `Queued At` dates flow correctly so Reaper aging works
- **ACTIVE MONITORING**: Watch for Apollo API rate limits / Apollo credit exhaustion on async phone callback requests; V4 now maps provider failures to `callback_failed`

### 8. Partnership Marketing Monitoring

- Monitor first Partnership Email Dispatcher run at 11am ET — confirm emails send, release log writes, and `partner_email_queued` tag applied
- Monitor first Partnership LinkedIn Dispatcher run at 3pm CT — confirm connection requests send, state table updated, `partner_linkedin_requested` applied
- Verify Partnership Reply Poller detects any inbound replies and triggers Reply Handler correctly
- Confirm Partnership LinkedIn DM Sequence picks up connected contacts after Acceptance Checker processes them
- Verify 3 patched LinkedIn workflows (Acceptance Checker, Reply Backfill, Unipile New Messages) handle partnership rows correctly
- Monitor for GHL rate limiting on per-contact API calls (250ms delay between contacts)
- After first email sends complete, verify the campaign summary endpoint reflects non-zero "Partnership emails" catalog row (may lag until reporting rollup runs)

### 9. LinkedIn Dispatcher Monitoring

- Monitor first dispatcher runs to confirm Fetch Ready Queue picks up the 14,987 `ready` contacts
- Verify dispatcher sends invites (successTag: `linkedin_connection_requested`) and updates state table correctly
- Watch for GHL rate limiting on dispatcher's per-contact API calls (tag check + LinkedIn URL extraction)
- Confirm Acceptance Checker correctly processes new connections and applies `linkedin_connected` tag

### 9. Cleanup and Adjacent Automation

- ~~Build automated LinkedIn DM suppression workflow~~ — DONE 2026-07-15. GHL tag `stop_linkedin_dms` → webhook → state table terminal. Full audit confirms all 3 send paths blocked.
- Build the separate `SimpleTexting SMS` GHL Custom Conversation Provider bridge after the user provides `conversationProviderId`; keep the existing SimpleTexting dispatcher live at low volume.
- Confirm first real SimpleTexting inbound reply posts to the existing Slack alert and suppresses future automated sends; then add GHL Conversations posting as the primary operator inbox.
- Retry and enable blocked GSC ingest workflow
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state lag after the fail-closed patch
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- ~~Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder~~ (verified already removed 2026-07-15)
- Delete GHL export CSVs after DAN backfill confirmed healthy

## Working Order

1. **Partnership Marketing** — monitor first email dispatcher at 11am ET, LinkedIn dispatcher at 3pm CT. Verify both sequences fire, release logs write, reply polling works.
2. **LinkedIn dispatcher** — monitor first runs now that 14,987 `ready` contacts are queued. Verify invites send, tags apply, state table updates.
2. **DAN ramp** — active dispatching (5 fixes applied 2026-07-15), monitor deliverability, track pool exhaustion (~4 days at 1,200/day)
3. **Vapi monitoring** — verify dialer fires, calls route to correct assistants
4. **Apollo enrichment** — monitor polling runs, verify V4 callback receiving phones
5. **Voice hardening** — secret management, webhook verification, adversarial testing
6. **Emerald ramp** — monitor dispatcher, verify data quality
7. Reporting depth
8. Meta attribution
9. SimpleTexting GHL Conversations provider bridge
10. Cleanup and adjacent automation
