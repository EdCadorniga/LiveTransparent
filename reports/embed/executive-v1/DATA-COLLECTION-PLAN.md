# V1 data collection plan

This is the implementation contract for making every mockup detail real and auditable. It is deliberately separate from the UI so data work can be completed and tested before deployment.

## Required canonical facts

### 1. Contact acquisition provenance

Create or expose one row per contact with:

- `contact_id`, `created_at`, `source`, `medium`, `campaign`
- `acquisition_mechanism`: `linkedin_backfill`, `apollo_upload`, `form`, `manual`, `booking`, `other`, or `unknown`
- `mechanism_evidence`: sanitized import name, workflow/event ID, or form ID
- `is_backfill`, `is_duplicate`, `is_in_period`

Rules: classify once per contact, use deterministic precedence, and reconcile the mechanism total to the New Contacts headline card.

### 2. Appointment detail and outcomes

Expose one row per appointment with:

- appointment/contact IDs, contact name, calendar/link, start time, status
- assigned SDR, originating SDR, attribution path, attribution confidence
- created time, updated time, rescheduled-from ID, cancellation reason

Rules: booked is based on `start_at` in the selected window; showed/no-show/cancelled/rescheduled are recorded statuses only; never infer an outcome from elapsed time.

For the Cameron headline KPI, count `COUNT(DISTINCT contact_id)` over Cameron-assigned appointment rows in the selected window, excluding blank contact IDs. Multiple appointment rows for the same contact—including cancellation followed by reschedule—count once. Preserve the raw appointment rows separately for audit and outcome detail.

### 3. Pipeline-to-work and action queue

Expose one row per actionable opportunity/task with:

- opportunity/contact ID, pipeline, stage, owner, stage-entered time
- next-action type, next-action due time, last activity time
- SLA rule version, overdue flag, suppression/closed flag

Rules: define “qualified remaining” and “overdue” in code and return the rule version with the counts. The action queue total must reconcile to the underlying actionable rows.

### 4. Same-channel response speed and follow-up

Persist each inbound response opportunity and the first later outbound response on the same channel:

- LinkedIn inbound DM/reply → later LinkedIn DM
- inbound call → later outbound call
- marketing-email reply → later marketing email send
- contact ID, inbound/outbound event IDs and timestamps, channel, campaign, actor/workflow
- elapsed seconds, `responded`/`unmatched`/`ambiguous` status, source-health status

Rules: match by contact and channel with a strictly later timestamp; mark multiple same-timestamp candidates as ambiguous; publish average and median only from unambiguous matched responses with explicit denominators; keep unmatched and ambiguous inbound events visible; do not label them overdue until an approved response-time target exists.

### 5. Voicemail disposition and callback facts

For the selected period, select the latest non-empty `voice_call_attempt.disposition` per unique contact and expose:

- unique contacts with a latest disposition
- unique contacts whose latest disposition is `voicemail`/`voicemail_left`
- unique contacts whose latest disposition is an explicit callback request
- disposition breakdown and source freshness

Rules: selecting the voicemail custom disposition is the approved indicator that a voicemail was left. Use the latest disposition per unique contact and do not count a contact more than once in the drops, delivered, or callback totals.

### 6. Channel delivery facts

For each email, LinkedIn, SMS, and voicemail event, expose:

- stable event ID, campaign key, contact ID, event timestamp
- sent/delivered/opened/clicked/replied/bounced/failed/callback status as applicable
- provider ID, source workflow, deduplication key, attribution confidence

Rules: aggregate distinct recipients where the mockup implies people; keep raw event counts separate; do not turn missing provider events into zero.

### 7. SDR inputs

Expose one canonical call-attempt fact with:

- call ID, contact ID, SDR, campaign, attempt time
- connected/no-answer/busy/failed/wrong-number disposition
- provider and workflow IDs, duplicate key

Rules: use `report_raw_ghl_calls` as the current GHL source of truth and include Vapi attempts as a separate source in the canonical fact table. Calls-attempted must equal connected + no-answer + busy/failed + wrong-number + explicit unknown/other; per-SDR totals must reconcile to the team strip without treating missing owner attribution as zero.

### 8. Social account statistics

Ingest platform/account/day facts for posts, impressions, reach, engagement, and followers, with:

- platform, account ID, date, metric name/value, provider response timestamp
- source-health status and timezone

Rules: do not mix post-placement counts with account statistics; label metrics unavailable when OAuth/statistics data is absent.

## QA gates

1. Each selected period returns non-empty JSON and source-health rows.
2. Every headline metric has a denominator/basis and a reconciliation query.
3. Source breakdowns sum to the headline or expose an explicit Unknown/Unattributed remainder.
4. SDR rows sum to team totals; owner conflicts and Unassigned are visible.
5. Channel tables reconcile to channel totals and preserve campaign keys.
6. Appointment detail reconciles to booked and outcome totals.
7. No metric is silently defaulted to zero when its source field is missing.
8. Run the same checks for 7d, 30d, 90d, and a custom period.
9. Capture a desktop and approximately 390px mobile screenshot; confirm no horizontal overflow.
10. Validate the original Executive Report URL remains unchanged before any V1 deployment.
