# Reporting Gaps and Requirements

**Updated:** 2026-07-31
**Status:** Requirements captured; implementation remains open

## Purpose

This document records what is missing from the native GHL report and the external Executive Report, and defines exactly what each report must show. It is the reporting acceptance checklist for the active DAN, Emerald, SMS, Vapi, LinkedIn, and Partnership systems.

## Verified Current State

### Executive Report

- Host: `https://reports.livetransparent.com`
- Current build: `2026-07-31-v10-partnership`
- Selected-period controls and prior equal-length comparison are live.
- Campaign Channel Summary is live and returns named campaign rows.
- `Partnership emails` currently shows 10 email sends for the verified 7-day window.
- Overall LinkedIn activity shows 10 LinkedIn invites for the same window after the live partnership test.
- The campaign table does not yet show a `Partnership LinkedIn` row with those 10 invites.
- The Executive Report is the only current surface that can combine Postgres state, Unipile activity, GHL CRM data, and campaign joins.

### Native GHL Report

- Report ID: `6a67dce4a51a4360c60963a3`
- The report has 11 widgets and is intended for operational CRM facts.
- The report-builder UI requires an authenticated GHL browser/Firebase session.
- A location PIT can read CRM data but cannot mutate native report widget layouts.
- `Campaign Opportunities` has no verified Partnership Pipeline condition.
- `Contacts by tag` has no verified partnership-specific tag conditions.
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

The current zero-safe catalog row is not sufficient unless live invite events are stored and joined to `campaign_key = partnership_linkedin`.

### P0: Partnership Email Event Coverage

Partnership emails are sent inline through `POST /conversations/messages`, not through GHL template actions. Confirm that GHL open, click, bounce, complaint, unsubscribe, and reply events are emitted for these messages.

If GHL does not emit events consistently, correlate events using GHL message ID, conversation ID, contact ID, sender email, campaign key, and event timestamp. Do not fabricate engagement rates. Show `unavailable` or a source-coverage warning when event data is missing.

### P1: Native GHL Partnership Configuration

Through the authenticated GHL UI, configure and verify:

- `Campaign Opportunities`: filter to `Partnership Pipeline` and show stage counts.
- `Contacts by tag`: add `partner_candidate_email`, `partner_candidate_linkedin`, `partner_email_queued`, `partner_linkedin_requested`, `partner_replied`, `partner_not_interested`, and `partner_do_not_contact` where supported.
- A Partnership Pipeline view showing New Partner Lead, Contacted, Proposal Sent, and Closed.
- Shared report date behavior with no independent widget overrides.
- Location-team sharing and read-only operator access.

Native GHL still will not show Unipile activity unless it is synchronized into GHL objects supported by the widget. The Executive Report remains authoritative for provider activity.

### P1: Reporting Owner Dimensions

Normalize contact owner, native opportunity owner, custom opportunity `Owner`, canonical SDR identity, owner conflict flag, assignment source, assignment timestamp, and unassigned Sales Outreach count in the reporting read model.

### P1: Source Health and Coverage

Expose last successful sync, latest attempt, row count, selected-window coverage, and failure message for GHL contacts, opportunities, pipeline history, calls, appointments, email events, SimpleTexting events, Unipile LinkedIn activity, Vapi queue/outcomes, GA4, and GSC. GSC is currently live after OAuth renewal and must retain its health/coverage status. SimpleTexting sends remain blocked by provider HTTP 409.

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

1. Contacts created by reporting period.
2. Contacts by source or campaign tag.
3. Opportunities by pipeline and stage.
4. Partnership Pipeline opportunities by stage.
5. MQL opportunities and MQL-to-SQL movement.
6. Meetings and appointments by calendar/status.
7. Outbound email counts and engagement where GHL supports the event.
8. Outbound SMS counts and replies where GHL supports the event.
9. Outbound call counts and answered status.
10. Closed-won count and revenue.
11. Owner and assignment breakdown.
12. Partnership contact and suppression tags.

Every widget must use the shared report date range, have a documented filter, and identify whether it reads contacts, opportunities, conversations, appointments, or tags. No widget may imply it includes Unipile activity unless that activity has been synchronized into a supported GHL object.

## Data and API Work Required

1. Instrument the Partnership LinkedIn Dispatcher to write activity events after successful invite requests.
2. Instrument the Partnership LinkedIn DM Sequence to write DM, reply, suppression, and completion events.
3. Instrument acceptance and inbound-message workflows to write partnership-scoped LinkedIn events.
4. Add `campaign_key` and `source_key` to every new LinkedIn event.
5. Update Campaign Channel Summary to aggregate `Partnership LinkedIn` from the ledger.
6. Add event coverage and error counts to the Executive Report API payload.
7. Verify partnership email event delivery and correlate message IDs.
8. Add owner dimensions and conflict state to the reporting read model.
9. Reconnect GSC OAuth and resume GSC ingestion.
10. Resolve the SimpleTexting provider HTTP 409 before counting provider sends as delivered.
11. Configure native GHL widgets through authenticated UI access; do not guess undocumented report-builder APIs.
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
- Source health identifies GSC OAuth and SimpleTexting provider blockers.
- No report contains credentials, PITs, OAuth tokens, or signed URLs.

## References

- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/GHL Reports Configuration Plan.md`
- `GHL Live Transparent CRM/Report Data Contract.md`
- `docs/audits/partnership-campaign-audit-plan.md`
- `n8n/reporting/LiveTransparent_Report_Workflow_Spec.md`
- `n8n/reporting/Embedded_Report_Host_Spec.md`
