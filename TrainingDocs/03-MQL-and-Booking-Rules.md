# MQL and Booking Rules

This guide explains who should get the `mql` tag and how bookings should be handled.

## What `mql` Means

`mql` means the lead is ready for stronger sales attention.

It does not mean:

- every warm lead
- every website visitor
- every booked call

## Approved MQL Sources

Add `mql` only when the lead came from one of these:

- `Warm  LinkedIn Lead Form`
- `Warm  Meta Lead Form`
- `Warm  Website` when the lead came from the website Hero form
- `Warm  Website` when the lead came from the website Footer form
- `Warm  Referral`
- A booking on calendar `cameron-1on1-30min`

## Do Not Add `mql` For

- Meta traffic by itself
- remarketing by itself
- general social activity
- normal bookings on other calendars
- leads that are warm but not strong enough yet

## Referral Rule

Use `Warm  Referral` only when the lead truly came from a referral.

Do not use it:

- for regular booked calls
- for calendar routing
- as a shortcut to force MQL

## Booking Rule

If a contact books the right meeting:

- calendar must be `cameron-1on1-30min`
- then the lead can get `mql`

If the contact books a different meeting:

- do not add `mql`

## Slack Rule

The `#leads` booking alert is sent by a filtered GHL booking automation.

Only this should happen:

- `cameron-1on1-30min` booking -> send to `#leads`

This should not happen:

- all bookings -> send to `#leads`
- duplicate Slack sends from multiple workflows

## What Happens After `mql` Is Added

After `mql` is added:

- GHL sends the contact into the MQL follow-up logic
- n8n can create or update the `Warm -> Qualified (MQL)` opportunity

Important:

- n8n does not decide who gets `mql`
- the GHL rules decide that first
