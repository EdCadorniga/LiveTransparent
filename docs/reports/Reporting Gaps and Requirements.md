# Reporting Gaps and Requirements

**Updated:** 2026-08-08
**Status:** Campaign attribution, SMS delivery diagnostics, opportunity counts, LinkedIn activity, and partnership reply attribution are live. Remaining: OAuth-backed social statistics ingestion, native GHL stage/tag/email/custom-metric widgets, and reporting owner dimensions.

## Purpose

This document records what is missing from the native GHL report and the external Executive Report, and defines exactly what each report must show. It is the reporting acceptance checklist for the active DAN, Emerald, SMS, Vapi, LinkedIn, and Partnership systems.

## Verified Current State

### Executive Report

- Host: `https://reports.livetransparent.com`
- Current build: `2026-08-08-v18-opportunity-attribution`
- Selected-period controls and prior equal-length comparison are live.
- Campaign Channel Summary is live and returns named campaign rows.
- Campaign rows remain separate for `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary`; Vapi activity is no longer rolled into DAN.
- Campaign rows include selected-window distinct opportunity counts matched from current campaign tags in `report_raw_ghl_opportunities`.
- SMS summary includes sent, failed, replies, and normalized failure reasons. The verified 2026-07-09 through 2026-08-07 window returned 294 sent, 1,095 failed, 0 replies; failure reasons were provider failure 1,010, duplicate send 63, unknown 16, invalid phone 5, and idempotent webhook error 1.
- In the current 30-day window, `Partnership emails` shows 59 sends, 1 reply, and a 1.69% response rate.
- In the current 30-day window, `Partnership LinkedIn` shows 17 invites and 1 reply.
- The two historical replies are stored with verified provider timestamps: Strider Peterson email at `2026-08-03T15:41:03Z` and Jaret Christopher LinkedIn at `2026-08-01T03:05:55Z`.
- Social post totals currently show 24 likes, 3 comments, and 4 shares. The UI also exposes saves, reach, and impressions, but the PIT-based post ingest currently supplies none of those fields.
- The Executive Report is the only current surface that can combine Postgres state, Unipile activity, GHL CRM data, and campaign joins.
- Outgoing Call Detail is live at the bottom of the report. It loads the seven most recent completed days, paginates at 100 rows, and displays contact ID/name fallback, phone, disposition, duration, first-attempt flag, campaign, and lazy signed recording playback.
- Outgoing Call Detail API: `GET /api/report/executive/outgoing-calls?range=7d&limit=100&offset=0`; nginx proxies to `GET /webhook/lt-report-outgoing-calls`.
- The detail endpoint is backed by n8n workflow `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`), published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`.
- The aggregate `GHL Calls` panel and the outgoing Vapi detail table are separate surfaces: aggregate GHL call status facts remain sourced from `report_raw_ghl_call_outcomes`, while the detail table is sourced from `voice_call_attempt` plus `voice_call_queue`.

### Native GHL Report

- Report ID: `6a67dce4a51a4360c60963a3`
- The report is intended for operational CRM facts. Its saved date range is `Last 30 days`; the duplicate page-3 `Outgoing calls by status` widget was removed on 2026-08-08 and the report still has three content pages.
- The report-builder UI requires an authenticated GHL browser/Firebase session.
- A location PIT can read CRM data but cannot mutate native report widget layouts.
- `Campaign Opportunities` is filtered to `Pipeline Is Partnership Pipeline`.
- `Contacts by tag` uses `Tags Is one of` with `partner_candidate_email` + `partner_candidate_linkedin`, group-by Tags surfaces the full partner tag distribution (email 122, LinkedIn 93, email queued 59, LinkedIn requested 10 for the verified window).
- Added **Partnership Pipeline Opportunities** (count, `Pipeline Is Partnership Pipeline`), **Partnership Pipeline by Status** (grouped by Status, same pipeline), and **Closed Won Revenue** (`Won Opportunity value`).
- GHL offers **no native stage-group dimension** for opportunity widgets and **no group-by on the `Owner` custom field**; a per-row Pipeline dependency blocks a reliable Stage filter in the builder. MQL, Sales Outreach funnel, and owner breakdown therefore remain Executive Report / GHL opportunity-view concerns.
- No native widget currently represents Unipile LinkedIn invitations, LinkedIn acceptance, or LinkedIn DM activity.
- The native report must not be treated as a cross-channel campaign warehouse.

## Missing Items

### P0: LinkedIn Activity Ledger

The 10 live connection requests were sent through Unipile and are visible in the aggregate LinkedIn metric, but they are not attributed to the Partnership campaign. The reporting system needs a durable activity row for every LinkedIn action.

Use the existing `linkedin_activity_events` pattern or create a partnership-specific table that is UNIONed into it. Each event must contain:

- `event_id`: stable idempotency key
- `event_at`: provider/action timestamp
- `ghl_contact_id` and `location_id`
- `source_key`: `partnership`, `dan`, or another canonical campaign source
- `campaign_key`: `partnership_linkedin`
- `channel`: `linkedin`
- `event_type`: `connection_request_sent`, `connection_accepted`, `dm_sent`, `reply_received`, `sequence_completed`, `suppressed`, or `send_failed`
- `linkedin_profile_url`, `linkedin_public_identifier`, and `linkedin_provider_id`
- `unipile_account_id`
- `provider_message_id` or invitation id when available
- `workflow_id` and workflow name
- `status`: `sent`, `accepted`, `replied`, `failed`, `skipped`, or `suppressed`
- `error_code` and sanitized `error_detail` for failures
- `metadata_json` and `created_at`

The dispatcher must write `connection_request_sent` only after the Unipile request succeeds. The state-upsert response must be checked and failures must be recorded separately rather than silently ignored.

### P0: Partnership LinkedIn Campaign Attribution

Add a durable `Partnership LinkedIn` catalog row to the campaign summary and populate it from the activity ledger. The row must show invitations sent, invitations failed, connections accepted, DMs by step, replies, sequence completions, suppressions, response rate, acceptance rate, and current ready/requested/connected/completed state counts.

**Implemented 2026-07-31 through 2026-08-01**: the full LinkedIn activity ledger is now instrumented across all send/reply/suppression paths, all writing idempotently to `linkedin_activity_events`:

- `connection_request_sent` — Partnership LinkedIn Dispatcher (`crKIsaL5k3YBfqDZ`, after Unipile success) + reconciliation backfill from requested/connected state rows. The verified 2026-07-31 run shows 10 invites.
- `connection_accepted` — LinkedIn Connection Acceptance Checker (`3ttEvr5NMcQCS4Hp`), keyed per contact+provider, with partnership campaign routing via `source_table`.
- `dm_sent` — Canonical LinkedIn DM Sequence (`d0tEtijajisIsYcs`, parallel flatten→record path) and Partnership LinkedIn DM Sequence (`nspggypNF245xzeL`, `campaign_type='partnership'`).
- `reply_received` — LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`, per contact) and LinkedIn Unipile New Messages (`7o5EBdvwAuIaWW7k`, per inbound message). Reply Backfill now also carries `source_table` so partnership rows route correctly.
- `suppressed` + `sequence_completed` — LinkedIn DM Suppression from GHL Tag (`IPN8jnR3XSurX0o1`), written when a contact is suppressed.

All six workflows are active and published (versionId == activeVersionId). The Campaign Channel Summary routes partnership events to `Partnership LinkedIn` via `campaign_type`/`source_key = 'partnership'` and exposes `linkedin_invites`/`linkedin_accepted`/`linkedin_replies` columns. The selected-window row now shows 17 invites and 1 verified historical reply. Still open: acceptance/completion rates and natural (non-suppression) `sequence_completed` events from the DM sequence completion branch.

### P0: Partnership Email Event Coverage

Partnership emails are sent inline through `POST /conversations/messages`, not through GHL template actions. Confirm that GHL open, click, bounce, complaint, unsubscribe, and reply events are emitted for these messages.

If GHL does not emit events consistently, correlate events using GHL message ID, conversation ID, contact ID, sender email, campaign key, and event timestamp. Do not fabricate engagement rates. Show `unavailable` or a source-coverage warning when event data is missing.

### P1: Native GHL Partnership Configuration

**Implemented 2026-08-01** through the authenticated GHL UI (15 widgets saved and verified):

- `Campaign Opportunities`: filtered to `Pipeline Is Partnership Pipeline`.
- `Contacts by tag` and `Contacts counts by tags (Partnership Campaign)`: `Tags Is one of` with `partner_candidate_email` + `partner_candidate_linkedin`; group-by Tags surfaces the full partner tag family distribution.
- Added `Partnership Pipeline Opportunities` (count), `Partnership Pipeline by Status` (grouped by Status), and `Closed Won Revenue` (`Won Opportunity value`).
- Shared report date range confirmed as `Last 30 days` (saved 2026-08-08) with no per-widget overrides.

Still open (builder limitations, not yet reliable via the report-builder UI):

- A Partnership Pipeline **stage** split (GHL opportunity widgets group by Status, not stage).
- The full `partner_*` tag set as explicit `Is one of` values where the tag list is virtualized; add `partner_email_queued`, `partner_linkedin_requested`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact` when editing through a stable UI path.
- MQL / Sales Outreach funnel widget (per-row Pipeline dependency on the Stage filter).
- Owner and assignment breakdown widget (no group-by on the `Owner` custom field `Wpg7FGrQTgAY1GoKcdEJ`).
- Location-team sharing and read-only operator access confirmation.

Native GHL still will not show Unipile activity unless it is synchronized into GHL objects supported by the widget. The Executive Report remains authoritative for provider activity.

### P1: Reporting Owner Dimensions

Normalize contact owner, native opportunity owner, custom opportunity `Owner`, canonical SDR identity, owner conflict flag, assignment source, assignment timestamp, and unassigned Sales Outreach count in the reporting read model.

### P1: Source Health and Coverage

Expose last successful sync, latest attempt, row count, selected-window coverage, and failure message for GHL contacts, opportunities, pipeline history, calls, appointments, email events, SimpleTexting events, Unipile LinkedIn activity, Vapi queue/outcomes, GA4, and GSC. GSC is currently live after OAuth renewal and must retain its health/coverage status. SimpleTexting sends remain blocked by provider HTTP 409.

**Coverage probe added (2026-08-01)**: `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) now upserts `report_source_health` rows for `email_events` and `linkedin_activity_events` (max event freshness, row count, 24h staleness) on every hourly run before evaluating QA. Verified live: `email_events` ready/22,613 rows; `linkedin_activity_events` ready/10 rows (the verified partnership invites). Because the Executive Summary API reads all `report_source_health` rows dynamically, these now appear in the report `health` section without query changes.

**Social statistics blocker confirmed (2026-08-04)**: the official GHL Social Planner statistics endpoint returned 152 impressions and 61 reach for its current seven-day OAuth window. The PIT returns 401 for that endpoint, and n8n has no usable GHL OAuth credential. The source data exists, but scheduled ingestion cannot be completed until OAuth is connected.

**Known minor limitation (2026-08-04)**: the Executive Summary API's `linkedinWeeklyActivity.inboundReplies`/`uniqueResponders` still count only `event_type = 'inbound_reply'` (not `reply_received`), and `linkedinFunnel` has no `suppressed` count. The Campaign Channel Summary (the primary campaign surface) already counts both reply event types and the LinkedIn funnel suppression is available in the state table. The report's campaign table is authoritative for the verified partnership reply until the weekly KPI query is adjusted.

## Executive Report Requirements

### Shared Controls

- Range presets: `7d`, `30d`, `90d`, and `custom`.
- Custom dates: `from=YYYY-MM-DD` and `to=YYYY-MM-DD`.
- Shared sub-account reporting timezone.
- Selected period plus immediately preceding equal-length period.
- Current value, prior value, absolute change, and percentage change for every comparable metric.
- One selected window across all widgets.
- Explicit `unmatched`, `unknown`, and `source unavailable` buckets.

### Executive KPI Cards

Show current, prior, change, and definition for recorded visits/users, GHL contacts, MQLs, SQL contacts, opportunities, meetings, closed-won opportunities, closed-won revenue, email sent/opened/clicked/bounced/complained/unsubscribed, email rates, SMS sent/delivered/replied/failed/opted out, LinkedIn invites/accepted/DMs/replies, and Vapi calls/answered/qualified/booked.

### Campaign Channel Table

Columns must include channel, campaign, SMS sent/failed/replies, email sent/opened/open rate/clicked/click rate/replies/response rate/bounced, LinkedIn invites or DMs/replies, Vapi calls/answered/qualified/booked, and selected-window distinct opportunities.

Required partnership rows:

- `Partnership emails`
- `Partnership LinkedIn`

### Outgoing Call Detail

The Executive Report must keep the following call-detail contract:

- Use only the seven most recent completed calendar days in `America/Los_Angeles`.
- Return a stable JSON payload with `calls`, `total`, `limit`, `offset`, and `range`.
- Cap one page at 100 rows and support non-negative offsets.
- Include call ID, contact ID/name fallback, phone, started/ended timestamps, status/disposition, duration seconds, first-attempt flag, campaign, and recording URL.
- Calculate duration from `ended_at - started_at`; null or missing end time falls back to zero-duration behavior rather than failing the whole report.
- Load recordings lazily and preserve provider-signed URL handling; do not put signed URLs in documentation or source control.
- Preserve an explicit contact-ID fallback when raw contact snapshots do not include a name.
- Keep this read-only endpoint separate from aggregate GHL call reporting and Vapi queue mutation workflows.

The 10 live test invites must appear in `Partnership LinkedIn`, not only in the overall LinkedIn KPI.

### LinkedIn Funnel

Show current state and selected-period activity for Ready, Requested, Connected, DM Active, DM Completed, Suppressed, requests sent, requests accepted, DMs by step, replies, acceptance rate, reply rate, completion rate, and provider/API failures.

Filters must include campaign key, source list, Brand versus Dispensary versus Partnership, owner, date window, and LinkedIn account.

### Partnership Detail

Show candidate counts by email and LinkedIn eligibility, email step distribution, email release status, LinkedIn request status, accepted connections, DM step and next eligible date, reply/suppression status, Partnership Pipeline stage, owner, contact/company/email/LinkedIn URL, and last activity timestamp.

## Native GHL Report Requirements

The native report should remain an operational CRM report, not a replacement for the Executive Report.

Required widgets:

1. Contacts created by reporting period. — **present** (via tag/contact widgets).
2. Contacts by source or campaign tag. — **present** (`Contacts by tag`, `Contacts counts by tags (Partnership Campaign)`).
3. Opportunities by pipeline and stage. — **partial**: `Opportunity counts by status` groups by Status; no native stage-group.
4. Partnership Pipeline opportunities by stage. — **partial**: `Partnership Pipeline Opportunities` (count) and `Partnership Pipeline by Status` (Status split) present; stage split not natively available.
5. MQL opportunities and MQL-to-SQL movement. — **open** (builder limitation; Executive Report `mqlSummary` is the current source).
6. Meetings and appointments by calendar/status. — **present** (`Appointment count by status`).
7. Outbound email counts and engagement where GHL supports the event. — **present** (Accepted/Opened/Clicked/Hard bounced).
8. Outbound SMS counts and replies where GHL supports the event. — **present** (`SMS by status`).
9. Outbound call counts and answered status. — **present** (`Outgoing calls by status`).
10. Closed-won count and revenue. — **revenue present** (`Closed Won Revenue`); won-count is in `Opportunity counts by status`.
11. Owner and assignment breakdown. — **open** (no group-by on the `Owner` custom field; stays in GHL opportunity views / Executive Report).
12. Partnership contact and suppression tags. — **present** (partner tag widgets).

Every widget must use the shared report date range, have a documented filter, and identify whether it reads contacts, opportunities, conversations, appointments, or tags. No widget may imply it includes Unipile activity unless that activity has been synchronized into a supported GHL object.

## Data and API Work Required

1. Instrument the Partnership LinkedIn Dispatcher to write activity events after successful invite requests. — **done** (`crKIsaL5k3YBfqDZ`).
2. Instrument the Partnership LinkedIn DM Sequence to write DM, reply, suppression, and completion events. — **done** (DM in `nspggypNF245xzeL`; reply in `QfJ2EZcc7lZwNgxj`/`7o5EBdvwAuIaWW7k`; suppression/completion in `IPN8jnR3XSurX0o1`).
3. Instrument acceptance and inbound-message workflows to write partnership-scoped LinkedIn events. — **done** (`3ttEvr5NMcQCS4Hp`, `7o5EBdvwAuIaWW7k`).
4. Add `campaign_key` and `source_key` to every new LinkedIn event. — **done** for partnership events; non-partnership events route via `emerging_pool_contacts.ghl_contact_id` join.
5. Update Campaign Channel Summary to aggregate `Partnership LinkedIn` from the ledger. — **done** (linkedin_invites/linkedin_accepted/linkedin_replies columns).
6. Add event coverage and error counts to the Executive Report API payload.
7. Verify partnership email event delivery and correlate message IDs. — **partially done**: the Partnership Email Dispatcher (`Xshck23cKo1yXL9D`) stores `ghl_message_id`/`ghl_conversation_id` per send in `partnership_release_log`, and the Campaign Channel Summary attributes partnership email opens/clicks via a release-log fallback keyed on `contact_id`. The known historical reply is backfilled and the selected-window row shows 59 sent / 1 reply / 1.69%. Still open: confirming GHL emits all per-message open/click webhooks for inline `POST /conversations/messages` sends and correlating those events consistently.
8. Add owner dimensions and conflict state to the reporting read model.
9. Reconnect GSC OAuth and resume GSC ingestion.
10. Resolve the SimpleTexting provider HTTP 409 before counting provider sends as delivered. The reporting layer now exposes normalized failure reasons; the dominant selected-window cause is `simpletext_provider_failed` with provider HTTP 409 responses.
11. Configure native GHL widgets through authenticated UI access; do not guess undocumented report-builder APIs. **Partially done**: saved `Last 30 days` and removed the duplicate page-3 outgoing-call widget on 2026-08-08. MQL, owner, stage-split, campaign-tag, email-detail, page-name, and custom-metric widgets remain open because the builder has no stage-group dimension, no Owner-custom-field group-by, and some tag selections are virtualized.
12. Add QA assertions for the 10-contact test: 10 invite events, 10 campaign-attributed LinkedIn requests, 10 state transitions or explicit state-upsert failures, and no duplicate event IDs.
13. Add a GHL OAuth credential to n8n and ingest Social Planner statistics by platform/day, including saves, reach, and impressions.

## Acceptance Criteria

- Native GHL report loads in an authenticated session and has documented widget filters.
- Partnership Pipeline opportunities appear in native GHL widgets.
- Partnership tags appear in native GHL contact widgets.
- Executive Report shows `Partnership emails` and `Partnership LinkedIn` rows.
- The 10 live LinkedIn requests appear as 10 in both the overall LinkedIn KPI and the Partnership LinkedIn campaign row.
- LinkedIn activity can be filtered by Partnership, Brand, and Dispensary.
- Email engagement rates show event coverage and do not silently treat missing events as zero.
- Selected-period and previous-period values agree across KPI cards and campaign rows.
- Email open/click rates use unique contacts rather than raw open events, or the report documents that rates are event-based (current Campaign Channel Summary `email_open_rate` counts raw events, so multi-open contacts can exceed 100%).
- Source health identifies GSC OAuth and SimpleTexting provider blockers.
- No report contains credentials, PITs, OAuth tokens, or signed URLs.
- Outgoing Call Detail returns HTTP 200 with a valid empty payload when the selected seven-day window has no rows.
- Outgoing Call Detail production and manual smoke executions complete without Postgres, Code-node, or webhook-response errors.

## References

- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/GHL Reports Configuration Plan.md`
- `GHL Live Transparent CRM/Report Data Contract.md`
- `docs/audits/partnership-campaign-audit-plan.md`
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`
- `n8n/reporting/Embedded_Report_Host_Spec.md`
