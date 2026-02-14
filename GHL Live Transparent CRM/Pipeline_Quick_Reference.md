# Live Transparent CRM Pipeline Quick Reference

## Pipeline Flow
`Warm` -> `Sales Outreach` -> `Sales`

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

## Warm Entry Channels (Current Rollout 2026-02-14)
- Active/Configured: `LinkedIn`, `LinkedIn DM`, `LinkedIn Lead Form`, `Meta Lead Form`
- Pending channel connection: `Instagram`, `Facebook Messenger`
- Referral intake trigger: add tag `Referral - Intake` (workflow converts to `Warm  Referral` and removes intake tag at end)
- Build/verification pending: `Meta Traffic`, `Meta Remarketing`, `Email Outbound`, `Email Inbound`, `SMS`, `Website`
- Master verification pending: all `Warm  ...` tags included in trigger set; booked handoff and sequence stop rules validated
