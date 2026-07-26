# Email Open 3x -> Sales Outreach Ownership Gate (GHL)

## Goal
When a contact accumulates 3 email opens (across any sequence emails), wait 45 minutes, then:
- If booked: do nothing.
- If still in Warm or AI-pending/unverified: record the engagement signal but do not assign an SDR or promote the record.
- If already in Sales Outreach: preserve the existing owner/alignment contract; do not independently allocate an SDR.
- If a later Janvi AI assessment promotes the record into `Sales Outreach -> New`, resolve ownership there using the single-owner/matching-owner/conflict/no-owner rules.

Ownership boundary:
- This workflow must not assign John, Jason, Marc, or any other SDR.
- SDR assignment occurs only when a record enters `Sales Outreach -> New`.

## Required Field + Tags
Create/confirm:
- Custom field (Number): `email_open_count_total`
- Tag: `Email Open 3x - Pending Assign`
- Tag: `open email 3x`

Use existing booked signal tags/states if already present:
- `meeting booked`
- `Do Not Nurture` (optional guard)

Important:
- Treat `meeting booked` as a scoped signal, not a generic \"any booking\" signal.
- Current valid workflow scope is the regulated ads booking calendar.
- Legacy Cameron 30-minute bookings may still retain the tag on older valid records.

## Workflow 1: Count Opens + Queue Assignment
Name:
- `WL - Micro - Email Open Counter`

Trigger:
- `Customer Replied` is NOT used.
- Use `Email Event` / `Email Opened` trigger.
- Re-entry: allowed.

Steps:
1. If/Else guard (skip if already handled)
- If tag `open email 3x` exists -> End.

2. If/Else guard (optional)
- If tag `meeting booked` exists -> End.

3. Update contact field
- `email_open_count_total = {{contact.email_open_count_total}} + 1`
- If your GHL UI does not support arithmetic in field update, use the fallback section below.

4. If/Else
- Condition: `email_open_count_total >= 3`
- AND tag `Email Open 3x - Pending Assign` does NOT exist
- True branch:
  - Add tag `Email Open 3x - Pending Assign`

## Workflow 2: Delayed Engagement Review + Booking Exception
Name:
- Existing legacy GHL workflow: `WL - Seq - Email Open 3x Assign John`
- Target behavior/name: `WL - Seq - Email Open 3x Engagement Review`

Trigger:
- Contact tag added: `Email Open 3x - Pending Assign`
- Re-entry: disabled.

Steps:
1. Wait
- `45 minutes`

2. If/Else booking check
- If ANY of these are true, stop routing:
  - Tag `meeting booked` exists
  - Opportunity is in booked/closed stage (if you use these statuses)
  - Appointment status is booked (if available in your location workflow conditions)

True branch (booked):
- Remove tag `Email Open 3x - Pending Assign`
- End.

False branch (not booked):
3. Preserve the engagement signal
- Do not assign a contact owner from this workflow.
- Do not create or move an opportunity to Sales Outreach from this workflow.
- If the record is already in Sales Outreach, use its existing resolved owner for any follow-up task or notification.

4. Tags
- Add tag `open email 3x`
- Remove tag `Email Open 3x - Pending Assign`

## Important Settings
- Keep Workflow 2 re-entry OFF so John assignment is one-time.
- Workflow 1 can re-enter to continue counting opens, but the `Assigned` tag guard prevents repeated assignment.
- Keep your existing stop workflow (`WL - Seq - Stop on Booked/Reply/Closed`) active; this logic complements it.

## Fallback If Arithmetic Update Is Not Supported in Your GHL UI
If Step 3 in Workflow 1 cannot increment a number field natively:
- Replace Workflow 1 with a webhook action to n8n on each open event.
- n8n increments `email_open_count_total` via GHL API and adds `Email Open 3x - Pending Assign` when count reaches 3.
- Workflow 2 remains exactly the same in GHL.
