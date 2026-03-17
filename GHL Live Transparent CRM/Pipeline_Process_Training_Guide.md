# Live Transparent CRM Pipeline Process and Training Guide

## 1) Purpose
This document defines how to use the Live Transparent CRM pipelines consistently so leads are routed, worked, and reported correctly.

## 2) Scope
This process applies to:
- Warm lead identification and triage
- Sales outreach follow-up
- Sales progression through close

## 3) Pipeline Overview
- `Warm`: intake, qualification, and early sorting
- `Sales Outreach`: active contact attempts and meeting conversion
- `Sales`: deal progression from discovery to close

## 4) Pipeline Definitions and Stage Criteria

### A) Warm Pipeline
Use this pipeline for newly identified warm intent before full sales outreach or nurture decisions.

#### 1. `New`
Definition:
- Contact has a warm signal but has not been reviewed.
Entry criteria:
- New warm tag/source is captured.
Exit criteria:
- Qualified into MQL, routed to outreach, routed to nurture, or disqualified.

#### 2. `Qualified (MQL)`
Definition:
- Contact matches minimum quality criteria for sales attention.
Entry criteria:
- Lead quality checks pass (fit + intent), and the contact came from an approved MQL path.
Exit criteria:
- Routed to outreach, nurture, or disqualified.

#### 3. `Routed to Outreach`
Definition:
- Contact is approved for direct outreach and handed to outreach process.
Entry criteria:
- Assigned to outreach owner/queue.
Exit criteria:
- Opportunity moved to `Sales Outreach` pipeline.

#### 4. `Nurture Active`
Definition:
- Contact is warm but not ready for direct outreach; nurture is active.
Entry criteria:
- Enrolled in nurture program.
Exit criteria:
- New intent signal qualifies for outreach, or disqualified.

#### 5. `Disqualified`
Definition:
- Contact is not currently a viable opportunity.
Entry criteria:
- Wrong fit, invalid contact, or no valid path forward.
Exit criteria:
- Only if new material data re-qualifies lead.

---

### B) Sales Outreach Pipeline
Use this pipeline once a lead is approved for direct contact and meeting conversion.

#### 1. `New`
Definition:
- Lead has entered outreach and is awaiting first touch.
Entry criteria:
- Handoff from Warm pipeline.
Exit criteria:
- First outreach attempt is completed.

#### 2. `Attempting Contact`
Definition:
- Active attempts underway (email, SMS, call, DM).
Entry criteria:
- At least one outreach action sent.
Exit criteria:
- Lead engages, meeting requested, or becomes unresponsive.

#### 3. `Engaged`
Definition:
- Lead has replied or meaningfully interacted.
Entry criteria:
- Verified reply or two-way interaction.
Exit criteria:
- Meeting requested/booked or stalled.

#### 4. `Meeting Requested`
Definition:
- Scheduling conversation is active but not yet booked.
Entry criteria:
- Lead expressed interest in meeting.
Exit criteria:
- Meeting booked or outreach stalls.

#### 5. `Booked`
Definition:
- Meeting is confirmed.
Entry criteria:
- Date/time confirmed.
Exit criteria:
- Opportunity is handed to `Sales` pipeline.

#### 6. `Unresponsive`
Definition:
- Outreach sequence completed with no meaningful response.
Entry criteria:
- Attempt threshold reached without engagement.
Exit criteria:
- New inbound engagement restarts outreach or routes to nurture.

---

### C) Sales Pipeline
Use this pipeline for active opportunities after meeting/booked handoff.

#### 1. `Discovery Scheduled`
Definition:
- Discovery meeting is booked and pending.
Entry criteria:
- Confirmed booked meeting from outreach.
Exit criteria:
- Discovery completed or no-show/cancel path handled.

#### 2. `Discovery Completed`
Definition:
- Discovery completed and next-step decision made.
Entry criteria:
- Discovery call held.
Exit criteria:
- Proposal prepared/sent or opportunity paused/lost.

#### 3. `Proposal Sent`
Definition:
- Proposal delivered and awaiting review.
Entry criteria:
- Proposal sent to decision-maker.
Exit criteria:
- Negotiation starts, win, or loss.

#### 4. `Negotiation`
Definition:
- Terms, scope, or price discussion in progress.
Entry criteria:
- Active negotiation exchanges underway.
Exit criteria:
- Closed Won or Closed Lost.

#### 5. `Closed Won`
Definition:
- Deal accepted and converted.
Entry criteria:
- Verbal/written acceptance and onboarding path confirmed.
Exit criteria:
- None (terminal stage).

#### 6. `Closed Lost`
Definition:
- Deal not moving forward.
Entry criteria:
- Prospect declined, went dark long-term, or was disqualified late-stage.
Exit criteria:
- None (terminal stage; reopen only with explicit reactivation).

## 5) Handoff Rules (Operational)
- Warm-to-Outreach handoff: move only after qualification or strong engagement.
- Outreach-to-Sales handoff: move at `Booked`.
- Do not skip stages unless manager-approved.
- Do not move backward except documented correction.

## 5A) MQL Tag Rules (Current)
- `mql` is not a universal warm tag.
- `mql` should only be added on approved high-intent paths.
- Current approved paths:
- `Warm  LinkedIn Lead Form`
- `Warm  Meta Lead Form`
- `Warm  Website` when created by the website Hero or Footer lead forms
- `Warm  Referral`
- Booking path only when the booked calendar is `cameron-1on1-30min`
- Standard bookings/appointments must not receive `Warm  Referral` unless the lead is actually referral-sourced.
- Non-Cameron bookings must not receive `mql`.
- The downstream n8n workflow `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)` only reacts after `mql` is present; it does not add the tag itself.

## 5B) Booking Slack Rule (Current)
- Booking alerts for `#leads` are owned by the filtered GHL booking automation, not by broad warm-routing logic.
- Only bookings for calendar `cameron-1on1-30min` should be sent to `WL - Webhook to Slack Channel Update`.
- Avoid adding separate Slack-send steps for the same booking event elsewhere in GHL to prevent duplicates.

## 6) Ownership and Accountability
- Marketing/Automation owner:
  - Keeps Warm pipeline clean and routed.
- SDR/Outreach owner:
  - Works `Sales Outreach` stages daily.
- Sales owner:
  - Owns `Sales` stages and close outcomes.

## 7) Daily Usage Standard
- Update stage immediately after each meaningful interaction.
- Add note for every stage change with reason.
- Keep one active owner on every open opportunity.
- Close stale records into correct terminal stage.

## 8) Reporting Standard
Track weekly:
- Volume entering `Warm -> New`
- Conversion `Warm Qualified -> Outreach Booked`
- Conversion `Outreach Booked -> Sales Closed Won`
- Loss reasons at `Closed Lost`
- Time-in-stage by pipeline

## 9) Training Checklist for New Team Members
1. Can explain purpose of each pipeline.
2. Can define each stage without ambiguity.
3. Can state entry and exit criteria for assigned stages.
4. Can perform stage updates and add required notes.
5. Can identify when to escalate stalled opportunities.

## 10) Governance
- Stage names are controlled terms; do not rename without approval.
- Any process change must be reflected in this guide before rollout.

## 11) Cannabis Ads Cold-Outreach Process (Current Live)
This process is separate from warm lead stage movement and is controlled by automation.

### A) What Triggers Enrollment
- Contacts are sourced from Postgres `Apollo_Contacts` with tag `cold-outreach`.
- Release automation sets `marketing_sender_email`, then adds `Enrollment Queue - Cannabis Ads`.
- GHL router workflow enrolls into Variant A/B only when routing guards pass.

### B) Sender + Pace Controls
- Sender field used by all Cannabis Ads email actions:
- `From Email = {{contact.marketing_sender_email}}`
- Warm-up caps:
- Week 1 `50/day` per sender
- Week 2 `75/day` per sender
- Week 3+ `100/day` per sender
- Cap includes in-flight sequence load, not only new enrollments.

### C) Live Dispatch Windows
- Automation runs hourly.
- Dispatch occurs only:
- `Mon-Sat`
- `8:00 AM ET` to `5:00 PM PT`
- Sundays: summary-only runs, no dispatch.
- Additional contact-local gate: contact local `8:00 AM-4:59 PM` required.
- Timezone resolution order:
- use explicit contact timezone field when available
- fallback from state/country values (supports full US state names and CA province names, plus code formats)

### D) What Users Should Do in GHL
- Verify sender emails under `Marketing > Emails > Settings > Verified sender emails`.
- Keep Cannabis Ads Router guard requiring `marketing_sender_email` not empty.
- Confirm Variant A/B workflow email actions keep dynamic sender merge field.
- Monitor queue and sequence tags:
- `Enrollment Queue - Cannabis Ads`
- `Seq Enrolled - Cannabis Ads`
- `Seq Variant A` / `Seq Variant B`
- If dispatcher is creating new contacts, expect a built-in `200ms` upsert throttle to reduce API rate-limit errors.

### E) What Users Should Not Do
- Do not manually bulk-add `Enrollment Queue - Cannabis Ads` without sender field populated.
- Do not overwrite `marketing_sender_email` mid-sequence unless intentional.
- Do not treat sender cap as \"new contacts/day only\".
- Do not manually log or force-release failed upsert rows; they are intentionally retried on future dispatcher runs.

## 12) Warm Channel Entry Status (Last Known 2026-02-24)
Use this status when training users on what should currently fire automatically.

### Active/Configured in GHL UI
- `WL - Micro - LinkedIn`
- `WL - Micro - LinkedIn DM`
- `WL - Micro - LinkedIn Lead Form`
- `WL - Micro - Meta Lead Form`
- `WL - Micro - Email Inbound`
- `WL - Micro - Email Outbound`
- `WL - Micro - SMS`
- `WL - Micro - Referral`

### Built but Not Trigger-Ready
- `WL - Micro - Instagram`: actions configured, trigger pending Instagram page connection.
- `WL - Micro - Facebook`: pending Facebook page/Messenger connection before trigger can be enabled.

### Referral Intake Pattern (Current)
- Referral micro entry is tag-based:
  - intake tag added: `Referral - Intake`
  - micro workflow trigger: `Contact Tag Added` on `Referral - Intake`
  - workflow adds `Warm  Referral`, sets source/UTM metadata, then removes `Referral - Intake` at end.
- `Warm  Referral` is a source tag only for true referrals. It should not be used as a substitute booking tag for general appointments.

## 13) Warm Automation Coverage Checklist (Last Known 2026-02-24)
Use this list during onboarding to avoid assuming all channel triggers are already active.

### Configured
- `WL - Micro - LinkedIn`
- `WL - Micro - LinkedIn DM`
- `WL - Micro - LinkedIn Lead Form`
- `WL - Micro - Meta Lead Form`
- `WL - Micro - Email Inbound`
- `WL - Micro - Email Outbound`
- `WL - Micro - SMS`
- `WL - Micro - Referral`

### Pending Trigger Connection
- `WL - Micro - Instagram`
- `WL - Micro - Facebook`

### Build/Verification Pending
- `WL - Micro - Meta Traffic`
- `WL - Micro - Meta Remarketing`
- `WL - Micro - Website`

### Master Routing Verification Pending
- Confirm master trigger listens to all warm tags (including `Warm  Meta Remarketing`).
- Confirm booked handoff path from `Sales Outreach` -> `Sales` is active.
- Confirm outreach/nurture sequences stop on booked/closed outcomes.
- Re-verify current status in `AGENTS.md` and GHL UI before rollout decisions.

## 14) Apollo Phone Enrichment Operations (Current)
This section is for training users who trigger Apollo phone/profile enrichment from GHL.

### A) Trigger and Control Fields
- Trigger/control field: `Enrich Phone via Apollo` (`contact.enrich_phone_via_apollo`)
- Status field: `Apollo Phone Enrichment Status` (`contact.apollo_phone_enrichment_status`)
- Timestamp field: `Apollo Phone Enriched At` (`contact.apollo_phone_enriched_at`)

### B) Status Values Used
- `queued`: Apollo match succeeded, no acceptable direct phone was returned synchronously, and the workflow is waiting on Apollo callback
- `enriched`: enrichment completed and phone/profile updates were applied
- `no_match`: Apollo returned no usable direct phone after synchronous processing or callback handling
- `error`: API/runtime error occurred, or a duplicate-phone block prevented a direct phone write

### C) What Gets Updated in GHL
- Standard contact fields (when present): `phone`, `firstName`, `lastName`, `email`, `companyName`, `city`, `state`, `country`
- Apollo custom fields: profile fields plus `Title`
- `Apollo Contact Id` is only written once a real phone enrichment succeeds, and it should align to Apollo `contact.id` when present
- Guardrail fields on successful enrich runs:
- `Contact already Enriched` -> `Yes`
- `Enrich via Apollo` -> `No`
- `Enrich Phone via Apollo` -> `No`

### D) Phone Source Priority (Apollo Payload)
- Intake webhook path: `ghl-apollo-phone-enrichment-intake-v3`
- Callback webhook path: `ghl-apollo-phone-enrichment-callback-v4`
- Intake evaluates person-level direct phone candidates first, including nested `person.contact.phone_numbers` / `person.phone_numbers`
- Callback V4 parses Apollo webhook payloads from `people[]` or `person`
- Company/trunkline sources in `Corporate Phone` and `Company Phone` are explicitly excluded from direct phone writes
- First valid normalized direct phone is written to GHL and persisted to Postgres `Apollo_Contacts.phone`

### E) Common Troubleshooting Checks
1. Confirm `Apollo Phone Enrichment Status` moved off `queued` only after giving Apollo callback time to arrive.
2. If contact remains `queued`, verify callback executions are landing on `GHL Apollo Phone Enrichment - Callback Handler V4`.
3. If `no_match`, inspect the `Enriched Contacts` sheet row for `enrichment_reason`, `normalized_phone`, and `raw_result`.
4. If a returned phone matches the contact’s `Corporate Phone` or `Company Phone`, treat it as a blocked trunkline rather than a usable direct number.
5. If phone is present in callback payload but not in GHL, inspect `update_request_body_used` and field-level constraints.
6. Verify timestamp format in custom field is `YYYY-MM-DD`.
7. Re-verify workflow active state and webhook paths in `AGENTS.md` before escalation.

## 15) RB2B Website Visitor Intake (Current)
This process handles anonymous website-visitor enrichment events sent from RB2B and converts them into actionable follow-up.

### A) Runtime and Trigger
- n8n workflow: `rb2b leads` (`3kjsIUeoEQFx26cC`)
- Trigger path: `/webhook/rb2b_leads_v2`

### B) Contact Resolution and Update Rules
- Match order in GHL:
1. duplicate lookup by email
2. fallback exact full-name match
- If existing contact is found: update contact fields.
- If no contact is found: upsert/create contact.

### C) Tagging Rules
- Always append these tags in GHL:
- `rb2b_website_visitor`
- `mql`
- Tagging is additive; existing tags must not be overwritten.

### D) Postgres Persistence
- Table: `RB2B_Leads`
- Upsert key: `lead_key` (email-based when available, otherwise name+company fallback key)
- Existing row is updated on conflict.

### E) Follow-Up Task Rule
- Create one task on processed contact:
- Title: `New RB2B contact - Call`
- Assigned user: Kevin (`7s3brzxGF4WSiz95DPkF`)

### F) Troubleshooting
1. If task node returns `Cannot POST /contacts//tasks`, verify task node URL references `ghl_contact_id` from `Prepare + Upsert GHL Contact`.
2. If contact write fails in code node, verify `Config` node still passes `locationId`, `apiBaseUrl`, `apiKey`, and `rb2bTag`.
3. If row upsert fails with null key, verify `lead_key` is present before Postgres node execution.
