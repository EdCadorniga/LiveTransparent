# GHL Automations Guide

This guide explains the main automations our GHL users should know about.

## What This Guide Is For

- Understand what the system does on its own
- Know which changes are expected
- Know when to review a lead instead of guessing

## What This Guide Is Not For

- Deep setup steps
- n8n build details
- API details
- Admin-only troubleshooting

## Main Idea

Automations help us:

- tag leads the right way
- route leads to the right pipeline
- create or update follow-up work
- keep the team from missing good leads

## Current System Note

- n8n is on `2.25.3` (upgraded June 2026 from `2.19.5`)
- do not manually refresh/update node versions unless an admin runbook says to
- if an automation looks different in the editor after an upgrade, stop and escalate before changing node fields

## Main Automations You Will See

### Website Form Leads

When someone fills out the website Hero or Footer form:

- the system creates the contact if needed
- the system updates the contact if it already exists
- the contact is tagged as a website lead
- the lead can enter the warm-lead process

### Website Hero Consent

The GHL hero form uses the built-in T&C elements for consent.

- `T&C 1` is the non-marketing SMS consent checkbox
- `T&C 2` is the marketing SMS consent checkbox
- these are built-in GHL form consent elements, not separate contact custom fields
- if automation needs to branch on consent, use GHL's built-in T&C workflow filters on the form submission
- unsubscribe handling in SMS or email does not replace the need to collect consent up front

## Website Visitor Leads

When the website visitor system can identify a person or company:

- the system looks for a match in GHL
- the system creates or updates the contact
- the system adds `rb2b_website_visitor`
- the system adds `mql`
- the system creates task `New RB2B contact - Call`

## Warm Lead Source Automations

These automations help mark where a warm lead came from.

Current examples include:

- LinkedIn
- LinkedIn DM
- LinkedIn Lead Form
- Meta Lead Form
- Email Inbound
- Email Outbound
- SMS
- Referral

What these automations do:

- add the correct warm-source tag
- set source details
- send the lead into the main warm-routing process

What they do not do:

- they do not do every sales action by themselves
- they do not mean every lead is MQL

## MQL Automation

`mql` is only added on approved paths.

If `mql` is added:

- the system checks for an opportunity
- if needed, it creates or updates the opportunity in `Warm -> Qualified (MQL)`

Important:

- not every warm lead gets `mql`
- not every booked meeting gets `mql`

## Regulated Ads Booking Automation

This is the most important booking rule for users to know.

Only this meeting should trigger the full booking automation:

- `Regulated Ads On Social/Search`

The normalized key may also appear as:

- `regulated-ads`
- `regulated-ads-on-social-search`

When that meeting is booked:

- the `#leads` Slack alert is sent
- the contact gets tag `SQL`
- the opportunity is moved to `Sales -> Discovery Scheduled`
- if no open opportunity exists, one is created there

If a different meeting is booked:

- do not expect the `#leads` Slack alert from this rule
- do not expect `SQL` from this rule
- do not expect the Sales handoff from this rule

## Tags You May See

These are the main tags documented in our system and what they mean.

### Warm Source Tags

- `Warm  Instagram`: warm lead came from Instagram
- `Warm  Facebook`: warm lead came from Facebook or Messenger
- `Warm  LinkedIn`: warm lead came from general LinkedIn activity
- `Warm  LinkedIn DM`: warm lead came from a LinkedIn direct message
- `Warm  LinkedIn Lead Form`: warm lead came from a LinkedIn lead form
- `Warm  Meta Lead Form`: warm lead came from a Meta lead form
- `Warm  Meta Traffic`: warm lead came from Meta traffic activity
- `Warm  Meta Remarketing`: warm lead came from Meta remarketing activity
- `Warm  Email Inbound`: warm lead came from an inbound email
- `Warm  Email Outbound`: warm lead came from an outbound email flow
- `Warm  SMS`: warm lead came from SMS activity
- `Warm  Website`: warm lead came from the website
- `Warm  Referral`: warm lead truly came from a referral

### Routing and Sales Tags

- `Lead Status: Warm`: contact is in the warm-lead process
- `Stage: MQL`: older system tag that marks an MQL-type path
- `mql`: current working tag for approved marketing-qualified leads
- `SQL`: sales-qualified lead tag used on the regulated ads booking path
- `meeting booked`: qualifying booked meeting signal, not a generic any-calendar booking tag

### Intake and Referral Tags

- `Referral - Intake`: temporary referral trigger tag that should be removed at the end of the referral workflow
- `rb2b_website_visitor`: lead came from the website-visitor identification system

### Email Follow-Up Tags

- `Email Open 3x - Pending Assign`: contact opened emails enough times to trigger a review, but assignment has not finished yet
- `open email 3x`: tag used when the contact is assigned after the 3-open check

### Outreach and Sequence Tags

- `cold-outreach`: contact is in the cold-outreach pool
- `10-100m`: contact came from a list of companies with `10` to `100` million in funding
- `100m+`: contact came from a list of companies with more than `100` million in funding
- `Enrollment Queue - Cannabis Ads`: contact is waiting to be enrolled into the Cannabis Ads sequence
- `Seq Enrolled - Cannabis Ads`: contact has already been enrolled in that sequence
- `Seq Variant A`: contact is in A path of the Cannabis Ads sequence
- `Seq Variant B`: contact is in B path of the Cannabis Ads sequence

### Other Tags Seen in Live Records

- `sms_drip`: contact is in an SMS drip path

## Tag Rules To Remember

- Not every warm tag means the lead is an `mql`
- Not every booked meeting means the lead is an `SQL`
- `meeting booked` should only be trusted for the current regulated ads booking path and a small set of legacy Cameron 30-minute records kept after cleanup
- `Warm  Referral` should only be used for real referrals
- `Referral - Intake` is a temporary workflow tag, not a final source tag
- `Stage: MQL` is still seen in docs and older logic, but `mql` is the main working tag users should watch
- `10-100m` and `100m+` tell you which funding list the contact came from
- funding-list tags do not automatically mean the lead is qualified

## Email Open Follow-Up

If a contact opens emails 3 times:

- the system waits 45 minutes
- the system checks if the lead already booked
- if not booked, the contact is assigned to John

This helps the team catch warm leads who are paying attention.

## What Users Should Check in GHL

When a lead changes on its own, check:

- contact name
- tags
- owner
- open tasks
- current pipeline and stage
- next step

## What Users Should Not Do

- Do not remove tags unless you know why they were added
- Do not assume every booked meeting is an SQL
- Do not use `Warm  Referral` for normal bookings
- Do not create duplicate manual tasks if the automation already did it
- Do not move leads backward unless you are fixing a real mistake

## If Something Looks Wrong

Ask these questions first:

- Did the lead come from an approved source?
- Did the lead book the regulated ads meeting or a different one?
- Did the contact already have an open opportunity?
- Did the automation already add a task, tag, or stage update?

## Simple Rule

If GHL changed something and you are not sure why:

- check the tags
- check the stage
- check the task list
- then check this guide before changing anything
