# LiveTransparent Project Status and Next Steps

Updated: 2026-07-15 (LinkedIn DM suppression automation deployed, dispatcher Feeder tag gap fixed)

## Source Of Truth

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Voice stack**: ACTIVE since 2026-07-14. Intake Poller + Outbound Dialer published. Poller searches 4 tag pools with rotation, 30/cycle. Dialer fires `*/2 13-22 UTC Mon-Fri` (9am ET start). State-to-timezone inference for business hours. 28 contacts initially enqueued.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences.
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (65/run every 30 min, 1,560/day capacity). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery.
- **Apollo phone enrichment**: REPAIRED 2026-07-14. New polling workflow replaces dead webhook-based pipeline. Profile data syncing immediately, phone numbers via async callback.
- **LinkedIn**: 8 workflows re-enabled 2026-07-10. All pipeline fixes verified intact, including a fail-closed DM reply check, a terminal DM completion tag, and a cycled connect dispatcher on 2026-07-11.
- **Instagram**: DM Sequence active, cron 0 12-22 * * 1-5.
- **Reporting**: GA4, GHL, GSC ingestion live. Executive report live in GHL.
- **SMS campaign**: Workflow exports staged in repo. Not yet deployed.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.

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
- **8 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Bucket} + P2 per bucket
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed, WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

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
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Webhook |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Manual |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (polls `*/2 13-22 UTC Mon-Fri`, ET-forward schedule) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **ET-forward dialer schedule**: cron shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. Initial business hours guard widened from 9-17 to 8-18 CT so it doesn't gate early ET calls.

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

### Queue State

~28 contacts initially enqueued from enriched vapi_campaign_brand/dispensary pools. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer picks up from queue during business hours (13-22 UTC Mon-Fri, ET-forward).

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

LT - Instagram DM Sequence (Unipile) (iCnY6ccdHhfJg3sf) -- active, cron 0 12-22 * * 1-5. Sends 4-message sequence to mutual followers. State tracked in instagram_dm_state (Postgres). Unipile account V9eiHiDpRmCtan0YNdzsQw at api42.unipile.com:17256.

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
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** | Was causing stuck executions |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active, hourly | Flips stale `queued` + `queued_phone` to `callback_timeout` |

## SMS Campaign (Staged)

Workflow exports staged in repo from docs/outreach/outreach_messages.docx. Not yet live deployed. Requires final GHL pool filter body for dispatcher.

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

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools — verify dedup (Fix #3) prevents double-enqueue
- Monitor Outbound Dialer when it activates at 14:00 UTC today — verify atomic lock (Fix #1) prevents duplicate calls
- Watch for GHL rate limiting on downstream nodes (Trigger Apollo Enrichment, Remove Tag nodes) — continueOnFail (Fix #4) prevents workflow crashes from flaky deletions
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback
- Run adversarial test calls against both campaign assistants
- Monitor timer system for duplicate warning/end-call events — 60s dedup window (Fix #5) should prevent this

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
- ~~Verify V4 callback handler starts receiving Apollo async phone responses~~ — Confirmed: 489 callbacks received, working
- ~~Confirm `queued_phone` contacts transition to `enriched` as callbacks arrive~~ — Pipeline confirmed end-to-end. Reaper now monitors both statuses.
- ~~Retune maxPerRun and schedule if Apollo rate limits appear~~ — 429 retry with 5s delay added to all 3 search sources
- **ACTIVE MONITORING**: Watch Reaper Slack reports for `queued_phone` reaping counts
- **ACTIVE MONITORING**: Confirm polling `Queued At` dates flow correctly so Reaper aging works
- **ACTIVE MONITORING**: Watch for Apollo API rate limits on async phone callback requests (currently silent failure)

### 8. LinkedIn Dispatcher Monitoring

- Monitor first dispatcher runs to confirm Fetch Ready Queue picks up the 14,987 `ready` contacts
- Verify dispatcher sends invites (successTag: `linkedin_connection_requested`) and updates state table correctly
- Watch for GHL rate limiting on dispatcher's per-contact API calls (tag check + LinkedIn URL extraction)
- Confirm Acceptance Checker correctly processes new connections and applies `linkedin_connected` tag

### 9. Cleanup and Adjacent Automation

- ~~Build automated LinkedIn DM suppression workflow~~ — DONE 2026-07-15. GHL tag `stop_linkedin_dms` → webhook → state table terminal. Full audit confirms all 3 send paths blocked.
- Deploy staged SimpleTexting SMS workflows with live GHL pool query
- Confirm SimpleTexting reply handler posts to #lead and suppresses future sends
- Retry and enable blocked GSC ingest workflow
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state lag after the fail-closed patch
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- ~~Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder~~ (verified already removed 2026-07-15)
- Delete GHL export CSVs after DAN backfill confirmed healthy

## Working Order

1. **LinkedIn dispatcher** — monitor first runs now that 14,987 `ready` contacts are queued. Verify invites send, tags apply, state table updates.
2. **DAN ramp** — active dispatching (5 fixes applied 2026-07-15), monitor deliverability, track pool exhaustion (~4 days at 1,200/day)
3. **Vapi monitoring** — verify dialer fires, calls route to correct assistants
4. **Apollo enrichment** — monitor polling runs, verify V4 callback receiving phones
5. **Voice hardening** — secret management, webhook verification, adversarial testing
6. **Emerald ramp** — monitor dispatcher, verify data quality
7. Reporting depth
8. Meta attribution
9. Cleanup and adjacent automation
