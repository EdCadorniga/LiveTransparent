# Email Open 3x -> Assign John (GHL)

## Goal
When a contact accumulates 3 email opens (across any sequence emails), wait 45 minutes, then:
- If booked: do nothing.
- If not booked: assign contact owner to John and assign/create opportunity to John.

Current owner:
- Name: John
- Use John's current GHL user ID in the live workflow.

## Required Field + Tags
Create/confirm:
- Custom field (Number): `email_open_count_total`
- Tag: `Email Open 3x - Pending Assign`
- Tag: `open email 3x`

Use existing booked signal tags/states if already present:
- `Meeting Booked`
- `Do Not Nurture` (optional guard)

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
- If tag `Meeting Booked` exists -> End.

3. Update contact field
- `email_open_count_total = {{contact.email_open_count_total}} + 1`
- If your GHL UI does not support arithmetic in field update, use the fallback section below.

4. If/Else
- Condition: `email_open_count_total >= 3`
- AND tag `Email Open 3x - Pending Assign` does NOT exist
- True branch:
  - Add tag `Email Open 3x - Pending Assign`

## Workflow 2: Delayed Assignment + Booking Exception
Name:
- `WL - Seq - Email Open 3x Assign John`

Trigger:
- Contact tag added: `Email Open 3x - Pending Assign`
- Re-entry: disabled.

Steps:
1. Wait
- `45 minutes`

2. If/Else booking check
- If ANY of these are true, stop routing:
  - Tag `Meeting Booked` exists
  - Opportunity is in booked/closed stage (if you use these statuses)
  - Appointment status is booked (if available in your location workflow conditions)

True branch (booked):
- Remove tag `Email Open 3x - Pending Assign`
- End.

False branch (not booked):
3. Assign contact owner
- Assign to John's current GHL user ID

4. Create/Update opportunity
- Pipeline: `Sales Outreach`
- Stage: `Engaged` (or your preferred working stage)
- Status: `Open`
- Owner: John
- Behavior: update existing open opportunity if present; otherwise create one.

5. Tags
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
