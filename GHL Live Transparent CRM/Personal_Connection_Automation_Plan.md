# Personal Connection Automation Plan

## Purpose
Build a practical automation layer that makes outreach feel personal without relying on unsafe or unsupported LinkedIn connection-request or DM automation.

The objective is not to fully automate human relationship-building. The objective is to automate:
- context gathering
- speed-to-contact
- next-best-action routing
- owner preparation
- message drafting
- follow-up consistency

This plan is designed for the current Live Transparent stack:
- GHL for CRM, workflows, tasks, tags, opportunities, and outbound messaging
- n8n for orchestration, webhook intake, enrichment, routing, and internal notifications
- Postgres for supporting event/memory logs where needed
- Slack for internal alerts

## Core Principle
Use automation to make the owner more informed and more timely, not to make the contact experience feel robotic.

That means:
- automate internal prep aggressively
- automate external messaging selectively
- keep high-value touches owner-assisted where tone matters most
- use channel context to make every touch feel relevant

## What We Should Optimize For
1. Respond quickly when intent is fresh.
2. Make every message reference real context.
3. Give owners a clear next action at every stage.
4. Prevent leads from sitting idle.
5. Preserve a human owner for the highest-value moments.

## What We Should Not Optimize For
- Mass generic sequence sends with no context.
- Fully automated outreach pretending to be human on unsupported channels.
- Duplicate or conflicting follow-ups across email, SMS, Slack, and tasks.
- Pipeline movement without clear event logic.

## Current Stack We Can Leverage

### Already Available
- Warm lead intake tagging and channel micro-automations in GHL
- Master warm routing logic in GHL
- Website intake webhooks in n8n
- RB2B website visitor intake workflow in n8n
- Apollo enrichment workflows in n8n
- Slack notification workflows in n8n
- GHL opportunities and pipeline structure
- Sender assignment and sequencing assets

### Practical Opportunity
The stack is already strong enough to support a personal-connection system if we add a thin orchestration layer around:
- owner briefing
- contextual message drafting
- behavior-triggered task creation
- follow-up timing
- lightweight memory capture

## Personal Connection System Architecture

### Layer 1: Contact Intake Context
Every qualifying intake event should produce a normalized context record for the contact.

Required inputs:
- source channel
- trigger type
- funnel or website origin
- page or offer context
- referral context when available
- Apollo/RB2B/company enrichment context
- existing owner and current stage
- last inbound/outbound activity

Primary current sources:
- website hero/footer forms
- funnel forms
- referral
- email inbound/outbound
- SMS
- RB2B website visitor webhook
- lead form sources already wired in GHL

### Layer 2: Contact Memory
For each important contact, maintain a concise internal memory summary that can be reused in future touches.

Target memory fields:
- `Warm Source`
- `Primary Engagement Channel`
- `Warm Trigger Type`
- `Lead Temperature`
- `Warm Date`
- owner
- current pipeline + stage
- last meaningful touch date
- last meaningful touch channel
- outreach status summary
- pain-point hypothesis
- offer-fit hypothesis
- recommended next step

Preferred storage:
- GHL notes for readable human context
- GHL custom fields only for short structured values
- optional Postgres support table later if cross-workflow memory becomes too large for notes/fields

### Layer 3: Owner Copilot
Automation should prepare the owner before or at the moment a manual touch is needed.

Outputs:
- short contact brief
- suggested opener
- suggested follow-up message
- call opener
- recommended CTA
- risk/objection note

Delivery options:
- GHL task body
- GHL note on contact/opportunity
- Slack alert to owner or shared channel

### Layer 4: Behavior-Triggered Next Best Action
When a contact acts, automation should decide what should happen next.

Examples:
- new warm lead -> create first-touch task + owner brief
- website revisit after no reply -> create check-in task
- CTA click without booking -> create case-study follow-up task
- reply received -> stop sequence + move to engaged handling
- booking created -> handoff to sales and stop outreach

### Layer 5: Selective Contact-Facing Automation
Only low-risk, high-value messages should be sent automatically.

Good candidates:
- immediate acknowledgment email after form submission
- meeting confirmation/reminder flows
- short warm SMS after explicit opt-in or warm interaction
- nurture content for contacts not yet ready for direct owner outreach

Owner-assisted candidates:
- first personalized outreach after warm qualification
- RB2B prospect first-touch
- re-engagement after silence
- objection handling
- post-call custom follow-up

## Recommended Build Order

### Phase 1: Owner Copilot for Warm Leads
Build an internal-only automation for new warm leads.

Trigger:
- contact receives approved warm or MQL tag
- or opportunity enters `Sales Outreach -> New`

Actions:
- create/update internal context summary
- generate owner brief
- create owner follow-up task
- send Slack alert with high-signal summary

Output format:
- who they are
- why they are warm
- what they did
- what we think they care about
- best next action
- suggested opener

Why first:
- highest value
- lowest risk
- minimal compliance exposure
- directly improves personal connection quality

### Phase 2: Behavior-Based Task Engine
Add event-driven tasks based on contact behavior.

Initial triggers:
- email open threshold
- email click
- website revisit
- booking started but not completed
- reply received
- no response after timed delay

Actions:
- create task with exact reason
- set due date
- assign to correct owner
- append brief suggested copy

Goal:
Owners stop guessing what to do next.

### Phase 3: Contextual Message Drafting
Create workflow-generated first-draft copy for owners.

Message variants by source:
- website form lead
- funnel lead
- referral lead
- inbound email lead
- RB2B visitor lead
- engaged but unbooked lead
- no-response re-engagement

Draft output should include:
- subject line
- short email
- short SMS
- call opener

Rule:
The system drafts. The owner sends.

### Phase 4: Re-Engagement Automation
Build softer follow-up logic for contacts that went quiet.

Examples:
- no reply after 2 touches -> generate softer “worth a quick chat?” task
- re-visit to site after silence -> create “timing check-in” task
- click on case-study/proof asset -> create “social proof follow-up” task

Goal:
Re-engagement should feel timely and relevant, not repetitive.

### Phase 5: Post-Booking Prep Automation
Once a lead books, automate internal preparation.

Outputs:
- contact summary
- source summary
- company summary
- prior touch summary
- likely objections
- recommended discovery angle

Delivery:
- Slack booking alert
- GHL note
- optional task/checklist for owner

Goal:
The booked call feels more personal because the rep is prepared.

## Specific Automations To Build

## Automation 1: New Warm Lead Owner Brief

### Trigger
- GHL contact tagged with approved warm tag
- or MQL qualification event

### Recommended implementation
- GHL workflow handles qualification routing
- n8n webhook receives normalized contact payload
- n8n composes internal brief
- n8n writes note or posts Slack alert
- GHL creates or updates owner task

### Suggested outputs
- lead source
- touch context
- company and role
- why now
- suggested first message
- suggested next action in one sentence

## Automation 2: RB2B Personal Follow-Up Prep

### Trigger
- RB2B intake workflow completes successfully

### Actions
- evaluate if contact already exists or was newly created
- create owner brief focused on likely interest/pain
- create call task with specific opener
- optional same-day email draft suggestion

### Why this matters
RB2B leads often need context-heavy outreach. Automation should help the owner sound informed, not generic.

## Automation 3: Website/Funnel Intent Escalation

### Trigger
- repeat website visits
- repeated visits to offer/pricing/booking pages
- CTA click without booking

### Actions
- create high-intent task
- mark escalation note in contact record
- optionally notify owner in Slack

### Goal
Turn silent interest into timely owner action.

## Automation 4: Sequence Assist Stop/Resume Logic

### Trigger
- reply
- booking
- stage moved to terminal or handoff stage
- no response after threshold

### Actions
- stop automation-driven sequence actions
- create owner task if manual follow-up is now appropriate
- update memory summary

### Goal
Prevent tone-deaf or duplicate outreach.

## Automation 5: Relationship Memory Refresh

### Trigger
- major contact event
- reply
- new source interaction
- booking
- task completion

### Actions
- update short structured fields
- append concise internal summary note

### Goal
Each new owner touch starts from memory, not from scratch.

## Channel Strategy

### Email
Best for:
- personalized first-touch after warm signal
- follow-up with proof or case-study
- post-call recap

Automation use:
- auto-send only for low-risk acknowledgments and nurture
- draft owner-assisted emails for high-value first-touch

### SMS
Best for:
- short warm follow-up
- reminders
- simple check-ins

Automation use:
- only when consent and context support it
- keep messages short and owner-sounding

### Phone
Best for:
- high-intent leads
- referrals
- RB2B leads
- reactivated leads

Automation use:
- automate the task, opener, and prep
- do not automate the actual call

### LinkedIn
Best for:
- manual owner follow-up where relationship fit is strong
- accepted connection follow-up when the contact has explicitly connected

Automation use:
- track LinkedIn as a preferred channel
- create task and suggested opener
- detect accepted connections in a separate state-sync workflow
- use Postgres as the connection-state index for matching accepted profiles back to CRM contacts
- start the follow-up sequence only after acceptance is confirmed
- do not automate unsupported connection requests or DMs

## Data Model Recommendations

### Keep or reuse existing fields where possible
- `Warm Source`
- `Primary Engagement Channel`
- `Warm Trigger Type`
- `Lead Temperature`
- `Warm Date`

### Add only if clearly useful
- `last_meaningful_touch_at`
- `last_meaningful_touch_channel`
- `next_best_action`
- `pain_point_hypothesis`
- `contact_brief_version`

### Prefer notes over too many custom fields when:
- value is narrative
- content changes often
- the owner needs readable context more than filter logic

## Suggested Workflow Ownership Split

### GHL should own
- qualification routing
- tag-based triggers
- opportunity stage movement
- task creation where simple rules are enough
- native message sequencing

### n8n should own
- multi-source context assembly
- internal briefing logic
- cross-system orchestration
- Slack notifications
- advanced decision rules
- message draft generation
- event normalization across website, funnel, RB2B, and behavior signals
- LinkedIn acceptance detection and connection-state sync

## Operational Rules

1. One owner at a time.
- Every active opportunity/contact should have a clear owner before personal follow-up tasks are generated.

2. One primary next action at a time.
- Avoid stacking multiple simultaneous “urgent” tasks for the same contact.

3. Stop sequences when conversation becomes human.
- If a real reply arrives, hand control to owner-led follow-up.

4. Use source-specific context in every draft.
- Messages should reference why the lead is in the system.

5. Do not auto-send high-risk “personal” messages without a clear trust basis.
- Draft them instead.

## QA and Rollout Plan

### Stage 1
Launch internal-only owner brief automation.

Test cases:
- website hero lead
- footer lead
- referral lead
- RB2B lead
- duplicate contact with new warm event

Success criteria:
- owner gets brief within minutes
- brief reflects correct source context
- only one task is created

### Stage 2
Launch behavior-triggered task engine.

Test cases:
- CTA click without booking
- revisit after silence
- reply event
- booking event

Success criteria:
- no duplicate tasks
- stop logic works
- tasks contain useful context

### Stage 3
Launch owner-assisted draft generation.

Test cases:
- warm website lead
- referral lead
- RB2B lead
- re-engagement case

Success criteria:
- drafts feel source-aware
- owners can use them with minimal edits

## Initial Build Backlog

### Highest priority
- New warm lead owner brief workflow
- RB2B owner brief and first-touch suggestion
- Website/funnel high-intent revisit task automation
- Sequence stop/resume task logic

### Second priority
- Re-engagement task engine
- Post-booking prep automation
- Contact memory refresh notes

### Later
- richer scoring model
- AI-assisted brief generation if desired
- shared internal dashboard for “who needs personal follow-up now”

## Recommended First Implementation

Build a new n8n workflow:
- name: `LT - Personal Connection Copilot - Warm Lead Brief`

Suggested input triggers:
- GHL webhook for approved warm/MQL tags
- website/funnel intake completions
- RB2B intake success output

Suggested outputs:
- Slack alert
- GHL note
- GHL task body suggestion

Minimum output template:
- Contact: full name, company, title
- Source: exact source and trigger
- Why they matter: fit hypothesis
- Why now: intent signal
- Best next action: call, email, SMS, or hold
- Suggested opener: 1 to 2 sentences

## Recommended Second Implementation

Build a new n8n workflow:
- name: `LT - Personal Connection Copilot - Behavior Follow-Up Tasks`

Suggested triggers:
- click/no-booking
- repeat visit
- reply
- sequence non-response threshold

Suggested outputs:
- owner task
- optional Slack nudge
- updated internal note

## Risks
- Too many tasks will reduce trust in the system.
- Overusing custom fields will create maintenance drag.
- Fully automated personal outreach will degrade quality.
- Channel collisions will happen if stop logic is weak.

## Guardrails
- Personal-touch automations must be contact-aware and stage-aware.
- Do not create a task if another open task for the same purpose already exists.
- Do not auto-send when the lead is already in an active human conversation.
- Do not send unsupported LinkedIn automations.

## Definition of Success
This system is successful when:
- response times improve
- owners have better context before outreach
- messages feel more relevant
- booked-call rate improves from warm leads
- fewer qualified leads go stale without a personal touch

## Final Recommendation
The best next move is not a broad new outbound engine.

The best next move is to build an owner-copilot layer on top of the warm lead system that already exists.

That gives Live Transparent:
- more personal outreach
- faster follow-up
- better owner consistency
- lower platform risk
- better use of the workflows already built
