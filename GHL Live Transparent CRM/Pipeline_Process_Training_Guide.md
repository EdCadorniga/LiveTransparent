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
- Lead quality checks pass (fit + intent).
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

## 11) Warm Channel Entry Status (2026-02-14)
Use this status when training users on what should currently fire automatically.

### Active/Configured in GHL UI
- `WL - Micro - LinkedIn`
- `WL - Micro - LinkedIn DM`
- `WL - Micro - LinkedIn Lead Form`
- `WL - Micro - Meta Lead Form`

### Built but Not Trigger-Ready
- `WL - Micro - Instagram`: actions configured, trigger pending Instagram page connection.
- `WL - Micro - Facebook`: pending Facebook page/Messenger connection before trigger can be enabled.

### Referral Intake Pattern (Current)
- Referral micro entry is tag-based:
  - intake tag added: `Referral - Intake`
  - micro workflow trigger: `Contact Tag Added` on `Referral - Intake`
  - workflow adds `Warm  Referral`, sets source/UTM metadata, then removes `Referral - Intake` at end.

## 12) Warm Automation Coverage Checklist (2026-02-14)
Use this list during onboarding to avoid assuming all channel triggers are already active.

### Configured
- `WL - Micro - LinkedIn`
- `WL - Micro - LinkedIn DM`
- `WL - Micro - LinkedIn Lead Form`
- `WL - Micro - Meta Lead Form`

### Pending Trigger Connection
- `WL - Micro - Instagram`
- `WL - Micro - Facebook`

### Build/Verification Pending
- `WL - Micro - Referral` final trigger + cleanup verification (`Referral - Intake` add/remove flow)
- `WL - Micro - Meta Traffic`
- `WL - Micro - Meta Remarketing`
- `WL - Micro - Email Outbound`
- `WL - Micro - Email Inbound`
- `WL - Micro - SMS`
- `WL - Micro - Website`

### Master Routing Verification Pending
- Confirm master trigger listens to all warm tags (including `Warm  Meta Remarketing`).
- Confirm booked handoff path from `Sales Outreach` -> `Sales` is active.
- Confirm outreach/nurture sequences stop on booked/closed outcomes.
