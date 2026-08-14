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
- A booking on an MQL-qualified calendar:
  - `Regulated Ads On Social/Search` (ID: `SrtXcFVyea7pFl3nTiIK`) — MQL + SQL
  - `Book a demo` (ID: `WS6lacfQK2XOhqN7mRaF`) — MQL + SQL
  - `Book 1:1 with Cameron` (ID: `w6lgGxG2zOKyw24LTpjD`) — MQL only

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

## Website Hero Consent Rule

The website hero form uses GHL's built-in consent elements.

- `T&C 1` = non-marketing SMS consent
- `T&C 2` = marketing SMS consent
- these are built-in GHL form consent elements, not separate contact custom fields
- if a workflow needs to branch on consent, use GHL's built-in T&C workflow filters on the form submission
- unsubscribe handling in SMS or email does not replace collecting consent at the form step

## Booking Rule

### Website Booking URL

The website must send demo visitors directly to the approved GHL booking widget so they enter their contact details once:

```text
https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK
```

The `/apply/` page should embed the same widget instead of the legacy Calendly URL. Do not place the GHL hero form `kxrHpS9bX16nzkIbr2py` before the booking widget because it duplicates name, email, and phone collection.

If a contact books the right meeting:

- calendar must be one of the MQL-qualified calendars (`Regulated Ads On Social/Search`, `Book a demo`, `Book 1:1 with Cameron`)
- then the lead can get `mql`
- then the lead should also get `SQL` (except `Book 1:1 with Cameron` which is MQL-only)
- then the lead can keep `meeting booked`
- then the opportunity should be moved to `Sales -> Discovery Scheduled`, or created there if none exists

If the contact books a different meeting:

- do not add `mql`
- do not add `SQL`
- do not keep or rely on `meeting booked` from that booking
- do not send the `#leads` Slack alert
- do not move/create the Sales opportunity from this rule

## Slack Rule

The `#leads` booking alert is sent by a filtered GHL booking automation that calls n8n.

Only this should happen:

- `Regulated Ads On Social/Search` booking -> send webhook -> n8n -> send to `#leads`

This should not happen:

- all bookings -> send to `#leads`
- duplicate Slack sends from multiple workflows

Current implementation:

- GHL filters the regulated ads booking before firing the webhook
- GHL posts to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`
- n8n workflow `WL - Webhook to Slack Channel Update` sends the Slack alert
- the same n8n workflow adds `SQL`
- the same n8n workflow moves or creates the opportunity in `Sales -> Discovery Scheduled`

## What Happens After `mql` Is Added

After `mql` is added:

- GHL sends the contact into the MQL follow-up logic
- n8n can create or update the `Warm -> Qualified (MQL)` opportunity
- for the regulated ads booking path, n8n also creates or updates the `Sales -> Discovery Scheduled` opportunity state

Important:

- n8n does not decide who gets `mql`
- the GHL rules decide that first

## Validation Note

- This regulated ads booking path was live-tested on `2026-03-19`
- The test appointment was deleted after the test
- The test contact and opportunity were left in GHL intentionally so the team can review the result
- The `meeting booked` tag population was audited on `2026-03-24`; non-qualifying bookings and unrelated contacts were cleaned up
