# Pipeline Training Guide

This guide explains how the sales team should use the pipelines in GHL.

## The 3 Main Pipelines

- `Warm`: new leads that need review
- `Sales Outreach`: leads the team is actively trying to contact
- `Sales`: real deals that are moving toward a close

## Warm Pipeline

### `New`

Use this when:

- A warm lead just came in
- Nobody has reviewed it yet

Move it out when:

- It is ready for MQL
- It should go to outreach
- It should go to nurture
- It should be disqualified

### `Qualified (MQL)`

Use this when:

- The lead looks like a real fit
- The lead has shown enough interest

Important:

- Not every warm lead should become MQL
- MQL only gets added on approved paths

### `Routed to Outreach`

Use this when:

- The lead is approved for direct follow-up
- It should be worked by the outreach team

### `Nurture Active`

Use this when:

- The lead is warm
- The lead is not ready for direct sales follow-up yet

### `Disqualified`

Use this when:

- The lead is not a fit
- The contact details are bad
- There is no good next step

## Sales Outreach Pipeline

### `New`

Use this when:

- The lead has entered outreach
- No first touch has been made yet

### `Attempting Contact`

Use this when:

- Email, call, SMS, or DM is in progress

### `Engaged`

Use this when:

- The lead replied
- There is real two-way contact

### `Meeting Requested`

Use this when:

- The lead wants to book
- The meeting is not confirmed yet

### `Booked`

Use this when:

- The meeting is on the calendar

Important:

- `Booked` is the handoff point into Sales
- The current automated booked handoff is only for the regulated ads booking path

### `Unresponsive`

Use this when:

- Outreach has been tried enough times
- The lead is not replying

## Sales Pipeline

### `Discovery Scheduled`

Use this when:

- A discovery call is booked

Important:

- The current automated booking handoff is for `Regulated Ads On Social/Search`
- The normalized internal key can appear as `regulated-ads` or `regulated-ads-on-social-search`
- That path adds `SQL` and ensures the opportunity is in `Sales -> Discovery Scheduled`

### `Discovery Completed`

Use this when:

- The call happened
- A next-step decision was made

### `Proposal Sent`

Use this when:

- A proposal was sent

### `Negotiation`

Use this when:

- Price, scope, or terms are being discussed

### `Closed Won`

Use this when:

- The deal is accepted

### `Closed Lost`

Use this when:

- The deal is not moving forward

## MQL Rules

`mql` is not for every warm lead.

Use `mql` only for:

- `Warm  LinkedIn Lead Form`
- `Warm  Meta Lead Form`
- `Warm  Website` from the website Hero or Footer forms
- `Warm  Referral`
- Bookings only when the calendar is `Regulated Ads On Social/Search`
- The normalized internal key can appear as `regulated-ads` or `regulated-ads-on-social-search`

Do not use `mql` for:

- Random warm traffic
- Standard bookings on other calendars
- General social engagement

## Referral Rule

`Warm  Referral` means the lead really came from a referral source.

Do not use `Warm  Referral` for:

- normal bookings
- normal appointments
- a shortcut to make someone MQL

## Booking Slack Rule

The `#leads` Slack booking alert is controlled by a filtered GHL booking automation that posts into n8n.

That means:

- only `Regulated Ads On Social/Search` bookings should go to `#leads`
- not every booking should go to `#leads`

Current implementation:

- GHL workflow filters the regulated ads booking
- GHL sends `POST https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`
- n8n workflow `WL - Webhook to Slack Channel Update` sends the Slack alert
- the same n8n flow adds `SQL` and moves or creates the opportunity in `Sales -> Discovery Scheduled`

Live validation:

- This booking path was live-tested on `2026-03-19`
- The test appointment was removed after validation so the regulated ads slot is clear
- The test contact and opportunity were intentionally left in GHL so teammates can inspect the result

## Simple Stage Rules

- Move leads forward only
- Do not skip stages unless a manager says so
- Do not move leads backward unless you are fixing a mistake

## What To Do Every Time You Move a Lead

- Update the stage right away
- Add a note that explains why
- Make sure there is an owner
- Make sure there is a next step if the lead is still open
