# Reporting Gaps and Requirements

**Updated:** 2026-08-01
**Status:** LinkedIn activity ledger fully instrumented (connection_accepted, dm_sent, reply_received, suppressed, sequence_completed), partnership campaign attribution live, and the core native GHL partnership widgets implemented and saved. Remaining: MQL/owner widgets in the native GHL report (builder limitations), partnership email event coverage verification, and source-health follow-ups.

## Purpose

This document records what is missing from the native GHL report and the external Executive Report, and defines exactly what each report must show. It is the reporting acceptance checklist for the active DAN, Emerald, SMS, Vapi, LinkedIn, and Partnership systems.

## Verified Current State

### Executive Report

- Host: `https://reports.livetransparent.com`
- Current build: `2026-07-31-v11-campaign-breakdown`
- Selected-period controls and prior equal-length comparison are live.
- Campaign Channel Summary is live and returns named campaign rows.
- `Partnership emails` currently shows 10 email sends for the verified 7-day window.
- Overall LinkedIn activity shows 10 LinkedIn invites for the same window after the live partnership test.
- The campaign table shows `Partnership LinkedIn` with 10 durable `connection_request_sent` events for the verified 2026-07-31 test.
- The Executive Report is the only current surface that can combine Postgres state, Unipile activity, GHL CRM data, and campaign joins.

### Native GHL Report

- Report ID: `6a67dce4a51a4360c60963a3`
- The report has **15 widgets** (verified persisted after reload on 2026-08-01) and is intended for operational CRM facts.
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

All six workflows are active and published (versionId == activeVersionId). The Campaign Channel Summary routes partnership events to `Partnership LinkedIn` via `campaign_type`/`source_key = 'partnership'` and exposes `linkedin_invites`/`linkedin_accepted` columns. Still open: resulting acceptance/reply/completion rates surfaced in the report API, and natural (non-suppression) `sequence_completed` events from the DM sequence completion branch.

### P0: Partnership Email Event Coverage

Partnership emails are sent inline through `POST /conversations/messages`, not through GHL template actions. Confirm that GHL open, click, bounce, complaint, unsubscribe, and reply events are emitted for these messages.

If GHL does not emit events consistently, correlate events using GHL message ID, conversation ID, contact ID, sender email, campaign key, and event timestamp. Do not fabricate engagement rates. Show `unavailable` or a source-coverage warning when event data is missing.

### P1: Native GHL Partnership Configuration

**Implemented 2026-08-01** through the authenticated GHL UI (15 widgets saved and verified):

- `Campaign Opportunities`: filtered to `Pipeline Is Partnership Pipeline`.
- `Contacts by tag` and `Contacts counts by tags (Partnership Campaign)`: `Tags Is one of` with `partner_candidate_email` + `partner_candidate_linkedin`; group-by Tags surfaces the full partner tag family distribution.
- Added `Partnership Pipeline Opportunities` (count), `Partnership Pipeline by Status` (grouped by Status), and `Closed Won Revenue` (`Won Opportunity value`).
- Shared report date range confirmed (`This week`, Jul 26 – Aug 1, 2026) with no per-widget overrides.

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

Columns must include channel, campaign, SMS sent/replies, email sent/opened/open rate/clicked/click rate/replies/response rate/bounced, LinkedIn invites or DMs/replies, and Vapi calls/answered/qualified/booked.

Required partnership rows:

- `Partnership emails`
- `Partnership LinkedIn`

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
5. Update Campaign Channel Summary to aggregate `Partnership LinkedIn` from the ledger. — **done** (linkedin_invites/linkedin_accepted columns).
6. Add event coverage and error counts to the Executive Report API payload.
7. Verify partnership email event delivery and correlate message IDs. — **partially done**: the Partnership Email Dispatcher (`Xshck23cKo1yXL9D`) already stores `ghl_message_id`/`ghl_conversation_id` per send in `partnership_release_log`, and the Campaign Channel Summary now attributes partnership email opens/clicks via a release-log fallback keyed on `contact_id`. Verified live (active version `076dcabc`): `Partnership emails` shows 59 sent / 4 opened, Emerald Executives SSO 358 sent / 1782 opened / 41 clicked, brands 101 opened, dispensaries 541 opened, and `Email - unattributed` dropped to 59 (was 2510). Still open: confirming GHL actually emits per-message open/click webhooks for inline `POST /conversations/messages` sends and that the message IDs correlate.
8. Add owner dimensions and conflict state to the reporting read model.
9. Reconnect GSC OAuth and resume GSC ingestion.
10. Resolve the SimpleTexting provider HTTP 409 before counting provider sends as delivered.
11. Configure native GHL widgets through authenticated UI access; do not guess undocumented report-builder APIs. **Done for the partnership widgets (2026-08-01)**; MQL, owner, and stage-split widgets remain open because the builder has no stage-group dimension, no Owner-custom-field group-by, and a per-row Pipeline dependency on the Stage filter.
12. Add QA assertions for the 10-contact test: 10 invite events, 10 campaign-attributed LinkedIn requests, 10 state transitions or explicit state-upsert failures, and no duplicate event IDs.

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

## References

- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/GHL Reports Configuration Plan.md`
- `GHL Live Transparent CRM/Report Data Contract.md`
- `docs/audits/partnership-campaign-audit-plan.md`
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`
- `n8n/reporting/Embedded_Report_Host_Spec.md`
