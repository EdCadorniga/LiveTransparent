# Website Visitor Leads

This guide explains what happens when the system creates a lead from website visitor data.

## What This Is

Sometimes the system can identify a company or person from website traffic.

When that happens, the lead can be sent into GHL for follow-up.

## What the System Does

- looks for a matching contact by email first
- uses exact full name as a backup match
- updates the contact if it already exists
- creates the contact if it does not exist

## Tags Used

These tags are added:

- `rb2b_website_visitor`
- `mql`

## Follow-Up Task

The system creates this task:

- `New RB2B contact - Call`

## Why Sales Should Care

- These are not random leads
- They came from website activity
- They should be checked quickly

## What To Review in GHL

- Contact name
- Company name
- Tags
- Open task
- Owner
- Next step

## Important Note

This is a special intake path.

Do not mix it up with:

- normal form fills
- normal booked meetings
- referral leads
