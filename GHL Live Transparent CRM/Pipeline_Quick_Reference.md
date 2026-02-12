# Live Transparent CRM Pipeline Quick Reference

## Pipeline Flow
`Warm Leads` -> `Sales Outreach` -> `Sales`

## Warm Leads
1. `Warm - New`: New warm signal captured, not reviewed yet.
2. `Warm - Qualified (MQL)`: Meets minimum fit + intent.
3. `Warm - Routed to Outreach`: Approved and handed to outreach.
4. `Warm - Nurture Active`: Not ready for direct outreach; nurture running.
5. `Warm - Disqualified`: Not currently viable.

## Sales Outreach
1. `Outreach - New`: Entered outreach queue, no first touch yet.
2. `Outreach - Attempting Contact`: Active outbound attempts in progress.
3. `Outreach - Engaged`: Two-way interaction confirmed.
4. `Outreach - Meeting Requested`: Scheduling discussion active.
5. `Outreach - Booked`: Meeting confirmed (handoff to Sales).
6. `Outreach - Unresponsive`: Attempt threshold hit, no meaningful response.

## Sales
1. `Sales - Discovery Scheduled`: Discovery booked and pending.
2. `Sales - Discovery Completed`: Discovery done; next step decided.
3. `Sales - Proposal Sent`: Proposal delivered.
4. `Sales - Negotiation`: Terms/scope/pricing discussion active.
5. `Sales - Closed Won`: Deal accepted.
6. `Sales - Closed Lost`: Deal not moving forward.

## Stage Movement Rules
- Move forward only.
- Do not skip stages without manager approval.
- Do not move backward unless correcting a documented error.
- Use `Outreach - Booked` as the handoff point into `Sales - Discovery Scheduled`.

## Required Actions Per Stage Change
- Update stage immediately after meaningful interaction.
- Add a note with reason for movement.
- Confirm owner is assigned.
- Set next follow-up task if opportunity is still open.

## Daily Rep Checklist
1. Clear all records in `Outreach - New`.
2. Progress active records in `Outreach - Attempting Contact`.
3. Push engaged leads toward `Meeting Requested` and `Booked`.
4. Close stale opportunities to correct terminal stage (`Unresponsive` or `Closed Lost`).
5. Verify no opportunity is left without owner or next action.
