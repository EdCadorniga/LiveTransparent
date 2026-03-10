# Cannabis Ads Sender Routing Runbook (GHL + n8n Dispatcher)

Last updated: `2026-03-08`
Location: `Live Transparent` (`Zwz4relUXVPxx8uohnjV`)

## Purpose
Implement sender locking for Cannabis Ads enrollment using GHL field `marketing_sender_email`, keep A/B split, and control enrollment volume by per-sender daily cap using the n8n release dispatcher.

## Locked Policy
- Queue model: use `Enrollment Queue - Cannabis Ads` as holding queue.
- Sender lock field: `{{contact.marketing_sender_email}}`.
- Week 1 cap: `50/day` per sender.
- Ramp: Week 2 `75/day` per sender, Week 3+ `100/day` per sender.
- Current sender pool: 4 active senders.
- `cameron@livetransparent.com`
- `cameron@livetransparent.co`
- `cameron@livetransparent.agency`
- `cameron@livetransparent.org`
- Sender cap interpretation: cap applies to total emails sent per sender per day (not only new enrollments).
- Dispatcher run window: `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`.
- Sunday behavior: workflow still runs for summary but dispatches `0` contacts.
- Per-contact local-hour gate: contact local `8:00 AM-4:59 PM` only.

## Prerequisites
1. Sender address is verified in GHL (`Marketing > Emails > Settings > Verified sender emails`).
2. Sender domain is configured and verified in GHL Email Services.
3. Contact field exists:
- `marketing_sender_email`
4. Tags exist:
- `Enrollment Queue - Cannabis Ads`
- `Seq Enrolled - Cannabis Ads`
- `Seq Variant A`
- `Seq Variant B`
- `Do Not Nurture`
- `Meeting Booked`

## Workflow Scope
- Router workflow: `WL - Seq Enrollment Router - Cannabis Ads`
- Variant A workflow ID: `716d5fd7-09ef-4535-855b-70a7a73e731b`
- Variant B workflow ID: `1ea5efa6-652b-4213-bf26-f32ff7275d71`
- Sender dispatcher workflow ID: `NTpQnMrpjzusPXHX`

## Implementation Steps

### 1) Configure Email Steps in Sequence Workflows
For both A and B workflows, for every `Email` action:
1. Set `From Email` to `{{contact.marketing_sender_email}}`.
2. Keep `From Name` as desired brand/sender display name.
3. Save each email action.

### 2) Update Router Entry Guards
In `WL - Seq Enrollment Router - Cannabis Ads`:
1. Trigger: tag added `Enrollment Queue - Cannabis Ads`.
2. Add guard checks before split:
- does not have `Seq Enrolled - Cannabis Ads`
- does not have `Meeting Booked`
- does not have `Do Not Nurture`
- DND does not block email
- `marketing_sender_email` is not empty

### 3) Keep A/B Randomizer
1. Keep randomizer at 50/50.
2. In A branch:
- set `Email Campaign = Cannabis Ads Sequence`
- set `Email Variant = A`
- add tag `Seq Variant A`
- add tag `Seq Enrolled - Cannabis Ads`
- remove tag `Enrollment Queue - Cannabis Ads`
- enroll into Variant A workflow
3. In B branch:
- set `Email Campaign = Cannabis Ads Sequence`
- set `Email Variant = B`
- add tag `Seq Variant B`
- add tag `Seq Enrolled - Cannabis Ads`
- remove tag `Enrollment Queue - Cannabis Ads`
- enroll into Variant B workflow

### 4) Automated Queue Release (Cap Control)
Dispatcher workflow runs hourly and handles release automatically:
1. Pull candidates from Postgres `Apollo_Contacts`:
- has email
- has `cold-outreach` tag
- not yet logged in `ColdOutreach_Release_Log`
2. Enforce global release window:
- `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`
3. Enforce per-contact local-hour gate:
- local `8:00 AM-4:59 PM`
- timezone from contact timezone field if present, otherwise state/country fallback
  - fallback supports full US state names and full CA province names (plus code formats)
4. Compute sender remaining capacity:
- `remaining = cap_by_week - in_flight_due_today - safety_buffer`
5. Deterministically assign sender and process contact:
- find existing contact in GHL by email
- if missing, upsert/create in GHL (with `200ms` delay before each upsert call)
- set `marketing_sender_email`
- add `Enrollment Queue - Cannabis Ads`
- write release log row
6. Deferred/failed contacts are retried on future runs because only `queued` rows are written to `ColdOutreach_Release_Log`.

## Capacity Accounting Rule (Critical)
- Do not treat daily cap as \"new contacts allowed\".
- Treat daily cap as \"maximum outbound emails from that sender today\".
- Because a newly enrolled contact receives multiple future emails, each sender's in-flight contacts continue consuming daily quota on later days.
- Always account for active sequence sends due today before adding new contacts to the same sender.

## Adding a New Sender Later
1. Add/verify domain and sender mailbox in GHL first.
2. Start new sender with lower initial volume (for example 10-25/day) until healthy metrics.
3. Set `marketing_sender_email` to new sender for selected queue contacts.
4. Release only that sender's capped batch.
5. Increase toward locked ramp once performance is healthy.

## Validation Checklist
1. Test contact A:
- `marketing_sender_email = <sender_1>`
- confirm all sent emails show sender_1
2. Test contact B (when sender_2 exists):
- `marketing_sender_email = <sender_2>`
- confirm all sent emails show sender_2
3. Confirm no contact enters both A and B.
4. Confirm queue tag is removed after enrollment.
5. Confirm stop workflow removes from both A and B on booked/reply/closed/do-not-nurture.
6. Confirm release math:
- Total sent-today for sender (in-flight + newly released) does not exceed sender daily cap.

## Failure Handling
- If sender is blank/unverified:
1. Do not enroll contact.
2. Add an internal review tag (example: `Sender Missing - Manual Review`).
3. Populate `marketing_sender_email` then re-queue.

- If contact is deferred due to timezone/business-hours:
1. Do not manually force release unless intentionally overriding policy.
2. Fix missing timezone/state/country data if available.
3. Allow normal retry window unless urgent exception is approved.

- If dynamic `From Email` is not honored by GHL in live tests:
1. Fall back to sender-specific cloned A/B workflows.
2. Route by sender first, then A/B within sender.

- If upsert errors show `429`:
1. Do not force-manual requeue in the same run.
2. Keep dispatcher active; failed rows will retry next cycle automatically.
3. If needed, increase throttling/backoff in dispatcher code.
