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

## 3A) Current Platform Note
- n8n target version is `2.33.3`.
- Recurring workflows use native n8n `Schedule Trigger` nodes; do not add OS, Coolify, or external cron jobs.
- If a workflow looks different after the upgrade, verify live behavior before editing node fields.

## 3B) Partnership Pipeline
Use this pipeline for content partnership outreach — independent of the main sales funnel.

### `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`)
- Purpose: Track content partnership conversations (guest spots, co-written pieces, newsletter features). This pipeline runs alongside the main sales pipelines and is not a qualification gate for Warm/Sales Outreach.
- Owner: Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- Contacts: 131 total — 98 via email + 33 LinkedIn-only
- All contacts are tagged `partner_candidate_email` or `partner_candidate_linkedin` (or both)

#### Pipeline Stages
1. **New Partner Lead** (`ccc3d423-ff86-46b4-bd53-064458910eba`): Initial entry when a contact replies to email or LinkedIn DM. Opportunity is automatically created by the Reply Handler workflow.
2. **Contacted**: Actively engaged in conversation.
3. **Proposal Sent**: Partnership proposal delivered.
4. **Closed**: Partnership confirmed or declined.

#### Outbound Sequences
- **Email**: 4-step sequence from `cameron@livetransparent.com`, 60/day max, 11am ET Mon-Fri, 2-weekday intervals. Managed by `LT - Partnership Email Dispatcher` (`Xshck23cKo1yXL9D`). It is currently `defaultDryRun=true`; no release-log rows exist until live launch approval.
- **LinkedIn**: 30 connection requests/day, 3pm CT Mon-Fri, handled by `LT - Partnership LinkedIn Dispatcher` (`crKIsaL5k3YBfqDZ`). The dispatcher seeds 127 `ready` partnership state rows before queue fetch. Connected contacts receive 4-step DM cadence via `LT - Partnership LinkedIn DM Sequence` (`nspggypNF245xzeL`). Both LinkedIn workflows are currently `defaultDryRun=true`; dry-run executions planned 30 requests and sent 0.

#### Reply Detection
- Email replies: polled every 5 minutes by `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`). On detection, the Reply Handler tags the contact `partner_replied`, creates a Partnership Pipeline opportunity, and posts to Slack.
- LinkedIn replies: detected by the patched `LT - LinkedIn Reply Backfill` and `LT - LinkedIn Unipile New Messages` workflows, which now query `partnership_linkedin_connection_state`.

#### Terminal Tags
- `partner_replied`: Stops all outbound sequences, creates opportunity
- `partner_not_interested`: Manual override
- `partner_do_not_contact`: Manual override
- `partner_email_sequence_completed`: All 4 emails sent
- `partner_linkedin_sequence_completed`: All 4 LinkedIn DMs sent

#### Reporting
- Campaign Channel Summary includes "Partnership emails" row via `partnership_release_log`
- Executive Report renders the campaign channel table with partnership metrics
- GHL Custom Report partnership widgets pending. The GHL PIT can read CRM REST data, but widget configuration requires the authenticated GHL browser/Firebase report-builder session or an approved internal API path.

## 3C) Original Pipelines

## 4) Pipeline Definitions and Stage Criteria

### A) Warm Pipeline
Use this pipeline for newly identified warm intent before full sales outreach or nurture decisions.

#### 1. `New`
Definition:
- Contact has a warm signal but has not been verified by Janvi's AI assessment.
Entry criteria:
- New warm tag/source is captured.
Exit criteria:
- AI-qualified as a cannabis business and promoted to Sales Outreach, routed to nurture, or explicitly rejected.

#### 2. `Qualified (MQL)`
Definition:
- Contact has an approved marketing-qualified signal. This stage is not, by itself, the SDR work-queue gate.
Entry criteria:
- Lead quality checks pass (fit + intent), and the contact came from an approved MQL path.
Exit criteria:
- AI-qualified as a cannabis business and promoted to Sales Outreach, routed to nurture, or disqualified.

#### 3. `Routed to Outreach`
Definition:
- Contact passed the AI cannabis-business gate and is approved for direct SDR outreach.
Entry criteria:
- Janvi's AI result explicitly equals the approved cannabis qualification value, or an SDR manually claims a successful Vapi warm transfer.
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
- AI-qualified cannabis lead has entered the SDR work queue and is awaiting first touch.
Entry criteria:
- Handoff from Warm after Janvi's AI qualification, or manual promotion after a successful Vapi warm transfer.
- Resolve ownership on entry:
  - one existing owner: align the other record;
  - matching owners: preserve;
  - conflicting owners: flag for review;
  - no owners: assign Jason or Marc using the deterministic 50/50 allocator.
- Keep contact native `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned.
Exit criteria:
- First outreach attempt is completed.

#### 2. `Attempting Contact 1st Attempt`
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
- Current booked automation scope is not universal:
  - only `Regulated Ads On Social/Search` / normalized keys `regulated-ads` or `regulated-ads-on-social-search` are auto-routed into `Sales -> Discovery Scheduled`

## 5A) Website Hero Consent Rule (Current)
- The website hero form uses GHL's built-in T&C consent elements.
- `T&C 1` is the non-marketing SMS consent checkbox.
- `T&C 2` is the marketing SMS consent checkbox.
- These are built-in form consent elements, not separate contact custom fields.
- If workflow branching is needed, use GHL's built-in T&C form-submission filters.
- Unsubscribe behavior in later SMS or email traffic does not replace collecting consent at the form step.

## 5B) MQL Tag Rules (Current)
- `mql` is not a universal warm tag.
- `mql` should only be added on approved high-intent paths.
- Current approved paths:
- `Warm  LinkedIn Lead Form` for LinkedIn lead form submissions
- `Warm  Meta Lead Form`
- `Warm  Website` when created by the website Hero or Footer lead forms
- `Warm  Referral`
- Booking path only when the booked calendar is `Regulated Ads On Social/Search`
- The normalized internal key can appear as `regulated-ads` or `regulated-ads-on-social-search`
- Standard bookings/appointments must not receive `Warm  Referral` unless the lead is actually referral-sourced.
- Non-regulated-ads bookings must not receive `mql`.
- The downstream n8n workflow `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)` only reacts after `mql` is present; it does not add the tag itself.
- The regulated ads booking path separately adds `SQL` and ensures the opportunity is in `Sales -> Discovery Scheduled`.

## 5C) Booking Slack Rule (Current)
- Booking alerts for `#leads` are owned by the filtered GHL booking automation, not by broad warm-routing logic.
- Only bookings for calendar `Regulated Ads On Social/Search` should be sent to `WL - Webhook to Slack Channel Update`.
- GHL sends the webhook to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`.
- n8n workflow `WL - Webhook to Slack Channel Update` is the component that sends the Slack message, adds `SQL`, and creates or moves the Sales opportunity.
- Avoid adding separate Slack-send steps for the same booking event elsewhere in GHL to prevent duplicates.

## 5D) Live Validation Note (2026-03-19)
- The regulated ads booking path was validated with a real public-widget booking, not just an API-created appointment.
- Validation confirmed:
  - GHL booking automation fired the webhook
  - n8n sent the Slack alert
  - n8n added tag `SQL`
  - n8n moved the opportunity into `Sales -> Discovery Scheduled`
- The test appointment was deleted after validation.
- The test contact and opportunity were intentionally left in GHL for internal review visibility.

## 6) Ownership and Accountability
- Marketing/Automation owner:
  - Keeps Warm pipeline clean, unassigned, and verified through Janvi's AI assessment.
- SDR/Outreach owner:
  - Works `Sales Outreach` stages daily and manually claims successful Vapi warm transfers.
- Sales owner:
  - Owns `Sales` stages and close outcomes.

### Ownership Resolution at Sales Outreach Entry
- Do not assign SDR ownership during ordinary Warm intake or Vapi queueing.
- If exactly one of the contact or opportunity has an owner, align the other record to that owner.
- If both owners match, make no ownership change.
- If both owners differ, flag the conflict for review and do not overwrite automatically.
- If neither has an owner, assign Jason or Marc with the deterministic 50/50 allocator.
- The custom opportunity `Owner` field must mirror the native opportunity owner through the canonical SDR mapping.

## 7) Daily Usage Standard
- Update stage immediately after each meaningful interaction.
- Add note for every stage change with reason.
- Keep one active owner on every open opportunity.
- Close stale records into correct terminal stage.

## 8) Reporting Standard
Track weekly:
- Volume entering `Warm -> New`
- AI-qualified cannabis contacts entering `Sales Outreach -> New`
- AI-pending/unverified contacts sent to Vapi
- AI-rejected/non-cannabis contacts suppressed from Vapi
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
- LinkedIn lead form submissions use the exact tag `Warm  LinkedIn Lead Form`.
- The two-space `Warm  ...` pattern is intentional and must be preserved in docs, workflows, and searches.

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
- Do not create an SDR task while the RB2B contact remains in Warm.
- After Janvi-qualified promotion into Sales Outreach, create the follow-up task using the resolved owner ID.

### F) Troubleshooting
1. If task node returns `Cannot POST /contacts//tasks`, verify task node URL references `ghl_contact_id` from `Prepare + Upsert GHL Contact`.
2. If contact write fails in code node, verify `Config` node still passes `locationId`, `apiBaseUrl`, `apiKey`, and `rb2bTag`.
3. If row upsert fails with null key, verify `lead_key` is present before Postgres node execution.

## 16) Vapi Campaign Eligibility Classifier (Current)

This is a cold-campaign eligibility gate for the Vapi Brand and Dispensary pools. It is separate from Janvi's CRM qualification gate and does not promote contacts into Sales Outreach.

### A) Runtime
- n8n workflow: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)
- Schedule: native n8n Schedule Trigger every 15 minutes
- Selection: up to 10 Brand and 10 Dispensary candidates per execution
- Source: `emerging_pool_contacts`, with live GHL contact and suppression checks

### B) Acceptance Rules
- Brand candidates receive `vapi_campaign_brand` only when DeepSeek accepts the regulated-business fit or the email domain is already in `vapi_qualified_domains`.
- Dispensary candidates receive `vapi_campaign_dispensary` under the same rule.
- Suppressed, terminal, already-called, queued, or already-tagged contacts are excluded or cleaned up.
- A live GHL phone is an allowed fallback when the imported pool phone is blank.
- Common free-email domains are never added to the qualified-domain list.

### C) Domain Persistence
- Table: `vapi_qualified_domains`
- A domain is written only after the GHL response confirms the campaign tag was added.
- Cleanup responses, failed writes, and rejected model outputs cannot qualify a domain.

### D) Operator Checks
1. Confirm the latest execution is successful.
2. Confirm `failed_write_count = 0` in the `Summarize Tags` output.
3. Review accepted contacts and campaign tags in GHL before allowing the queue feeder to stage them.
4. Treat this workflow's acceptance as Vapi campaign eligibility, not Janvi's authoritative cannabis qualification or Sales Outreach ownership assignment.
