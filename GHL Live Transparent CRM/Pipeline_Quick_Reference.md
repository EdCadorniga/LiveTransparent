# Live Transparent CRM Pipeline Quick Reference

## Pipeline Flow
`Warm` -> `Sales Outreach` -> `Sales`

## Current Platform Note
- n8n is now on `2.14.2`
- no manual node-version refresh is planned right now
- escalate if a workflow editor view looks different after the upgrade

## Warm
1. `New`: New warm signal captured, not reviewed yet.
2. `Qualified (MQL)`: Meets minimum fit + intent.
3. `Routed to Outreach`: Approved and handed to outreach.
4. `Nurture Active`: Not ready for direct outreach; nurture running.
5. `Disqualified`: Not currently viable.

## Sales Outreach
1. `New`: Entered outreach queue, no first touch yet.
2. `Attempting Contact`: Active outbound attempts in progress.
3. `Engaged`: Two-way interaction confirmed.
4. `Meeting Requested`: Scheduling discussion active.
5. `Booked`: Meeting confirmed (handoff to Sales).
6. `Unresponsive`: Attempt threshold hit, no meaningful response.

## Sales
1. `Discovery Scheduled`: Discovery booked and pending.
2. `Discovery Completed`: Discovery done; next step decided.
3. `Proposal Sent`: Proposal delivered.
4. `Negotiation`: Terms/scope/pricing discussion active.
5. `Closed Won`: Deal accepted.
6. `Closed Lost`: Deal not moving forward.

## Stage Movement Rules
- Move forward only.
- Do not skip stages without manager approval.
- Do not move backward unless correcting a documented error.
- Use `Booked` as the handoff point into `Discovery Scheduled`.
- Current automated booked handoff is only for `Regulated Ads On Social/Search` / normalized keys `regulated-ads` or `regulated-ads-on-social-search`.

## MQL Rules
- `mql` is not applied to every warm contact.
- Approved `mql` sources:
- `LinkedIn Lead Form`
- `Meta Lead Form`
- `Website` lead forms only
- `Referral`
- Booking only when calendar is `Regulated Ads On Social/Search`
- normalized key may appear as `regulated-ads` or `regulated-ads-on-social-search`
- Do not use `Warm  Referral` for normal bookings/appointments.
- Non-regulated-ads bookings must not receive `mql`.
- Regulated ads bookings should also receive tag `SQL`.
- Regulated ads bookings should end in `Sales -> Discovery Scheduled`.

## Booking Slack Rule
- `#leads` booking alerts are sent from the filtered GHL booking automation.
- Only `Regulated Ads On Social/Search` bookings should post to Slack.
- GHL posts the filtered booking to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`.
- n8n workflow `WL - Webhook to Slack Channel Update` sends the Slack message and handles the `SQL` + Sales handoff logic.
- Do not add duplicate Slack-send actions for the same booking in other workflows.

## Live Validation Note
- Live validation completed on `2026-03-19`.
- The test appointment was removed after the run.
- The test contact and opportunity were intentionally left in GHL for teammate review.

## Required Actions Per Stage Change
- Update stage immediately after meaningful interaction.
- Add a note with reason for movement.
- Confirm owner is assigned.
- Set next follow-up task if opportunity is still open.

## Daily Rep Checklist
1. Clear all records in `New` (Sales Outreach).
2. Progress active records in `Attempting Contact`.
3. Push engaged leads toward `Meeting Requested` and `Booked`.
4. Close stale opportunities to correct terminal stage (`Unresponsive` or `Closed Lost`).
5. Verify no opportunity is left without owner or next action.

## Warm Entry Channels (Last Known Rollout 2026-02-24)
- Active/Configured in GHL UI: `LinkedIn`, `LinkedIn DM`, `LinkedIn Lead Form`, `Meta Lead Form`, `Email Inbound`, `Email Outbound`, `SMS`, `Referral`
- Pending channel connection: `Instagram`, `Facebook Messenger`
- Referral intake trigger: add tag `Referral - Intake` (workflow converts to `Warm  Referral` and removes intake tag at end)
- Build/verification pending: `Meta Traffic`, `Meta Remarketing`, `Website`
- Master verification pending: all `Warm  ...` tags included in trigger set; booked handoff and sequence stop rules validated
- Re-verify current status in `AGENTS.md` and GHL UI before operational changes.

## Cannabis Ads Cold-Outreach Quick Rules (Live)
- Enrollment path: `cold-outreach` contacts -> n8n sender dispatcher -> `Enrollment Queue - Cannabis Ads` -> GHL A/B router.
- Sender in emails must stay dynamic:
- `From Email = {{contact.marketing_sender_email}}`
- Dispatch window:
- `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`
- Sundays are summary-only (no dispatch).
- Contact local-hour rule:
- only dispatch when contact local time is `8:00 AM-4:59 PM`.
- Sender caps:
- Week 1 `50/day`, Week 2 `75/day`, Week 3+ `100/day` per sender.
- Cap is total outbound load per sender/day (in-flight + newly released).

## Apollo Phone Enrichment Quick Rules (Live)
- Trigger from GHL field: `Enrich Phone via Apollo` (`contact.enrich_phone_via_apollo`).
- Runtime status field: `Apollo Phone Enrichment Status` (`contact.apollo_phone_enrichment_status`).
- Timestamp field: `Apollo Phone Enriched At` (`contact.apollo_phone_enriched_at`) written as `YYYY-MM-DD`.
- Runtime paths:
- intake `ghl-apollo-phone-enrichment-intake-v3`
- callback `ghl-apollo-phone-enrichment-callback-v4`
- Status meanings:
- `queued`: Apollo matched a person and callback is still pending
- `enriched`: profile/phone update completed
- `no_match`: no usable direct phone was available after intake/callback handling
- `error`: workflow/API failure or duplicate-phone block
- On successful enrich, guardrail fields are set:
- `Contact already Enriched` = `Yes`
- `Enrich via Apollo` = `No`
- `Enrich Phone via Apollo` = `No`
- `Apollo Contact Id` is only written on successful phone enrichment and should align to Apollo `contact.id` when present.
- Phone extraction now prioritizes person-level direct phone sources and callback payloads.
- Any candidate matching existing `Corporate Phone` or `Company Phone` is treated as a company/trunkline number and ignored for direct phone writes.

## RB2B Intake Quick Rules (Live)
- n8n workflow: `rb2b leads` (`3kjsIUeoEQFx26cC`)
- Webhook path: `/webhook/rb2b_leads_v3`
- GHL contact resolution order:
- email duplicate lookup first
- exact full-name fallback second
- Contact action:
- update if found, upsert/create if missing
- Tags appended (non-destructive):
- `rb2b_website_visitor`
- `mql`
- Postgres persistence:
- upsert into `RB2B_Leads` by `lead_key`
- Follow-up task:
- title `New RB2B contact - Call`
- assigned to John
