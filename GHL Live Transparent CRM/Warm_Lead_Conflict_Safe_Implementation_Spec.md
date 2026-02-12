# Warm Lead Intake and Routing: Conflict-Safe Implementation Spec

## 1) Objective
Implement the Warm Lead plan without breaking existing CRM behavior by enforcing deterministic routing, idempotency, and collision controls.

## 2) Non-Breaking Rules
- Owner overwrite restrictions are deferred for a later phase.
- Do not downgrade funnel stage (only move forward unless manually overridden by sales).
- Do not enroll a contact into the same follow-up sequence more than once within the cooldown window.
- Do not update stage/pipeline if a higher-priority route was applied recently.

## 3) Canonical Definitions (Use IDs, Not Names)
Store all of these in one config source (GHL custom values or n8n static config):
- `pipeline_warm_leads_id`
- `pipeline_sales_outreach_id`
- `pipeline_sales_id`
- `stage_warm_id`
- `stage_mql_id`
- `stage_booked_pending_id`
- `stage_active_outreach_id`
- `stage_closed_won_id`
- `stage_closed_lost_id`
- `sales_admin_user_id`

Do not branch logic on label text like `Booked or Pending` vs `Booked or Ready`.

## 4) Required Contact Fields
Create and use these custom fields:
- `lt_last_routing_reason` (text)
- `lt_last_routing_channel` (text)
- `lt_last_routed_at` (datetime UTC)
- `lt_route_lock_until` (datetime UTC)
- `lt_routing_priority` (number)
- `lt_last_event_fingerprint` (text)
- `lt_last_event_at` (datetime UTC)
- `lt_owner_lock` (boolean)

## 5) Tag Taxonomy
Entry tags (channel tags):
- `Warm - Instagram`
- `Warm - Facebook`
- `Warm - LinkedIn`
- `Warm - LinkedIn DM`
- `Warm - LinkedIn Lead Form`
- `Warm - Meta Lead Form`
- `Warm - Meta Traffic`
- `Warm - Meta Remarketing`
- `Warm - Email Outbound`
- `Warm - Email Inbound`
- `Warm - SMS`
- `Warm - Website`
- `Warm - Referral`

System tags:
- `Lead Status: Warm`
- `Stage: MQL`
- `LT Routed`
- `LT Route Locked`
- `LT Nurture Active`
- `LT Outreach Active`

## 6) Priority Model (Highest Wins)
- `100`: Referral
- `90`: LinkedIn Lead Form, Meta Lead Form
- `80`: Email Inbound, SMS reply, LinkedIn DM reply
- `70`: Website intent, Meta Traffic, Meta Remarketing
- `60`: Instagram DM, Facebook Messenger, social click-only

If two events arrive close together, keep the higher priority and ignore lower-priority updates during lock window.

## 7) Idempotency + Locking
Use event fingerprint:
- `fingerprint = contact_id + channel + source_event_id + event_date_bucket`

Rules:
- If `fingerprint == lt_last_event_fingerprint`, stop.
- If `now < lt_route_lock_until` and incoming priority `< lt_routing_priority`, stop.
- If `now < lt_route_lock_until` and incoming priority `>= lt_routing_priority`, allow only if route outcome differs materially (pipeline/stage/sequence).

Default lock windows:
- Referral: 72h
- Lead forms: 48h
- Direct replies (email/SMS/DM): 36h
- Website/traffic events: 24h

## 8) Micro-Automation Contract
Each channel micro-automation only does:
1. Validate event quality (real reply/intent, not bot/noise).
2. Apply exactly one `Warm - [Channel]` tag.
3. Set source metadata fields (`source`, `utm_*` when present).
4. Exit.

Micro-automations must not move stages, assign owners, or start long sequences.

## 9) Master Workflow Logic
Trigger:
- Contact gets any `Warm - [Channel]` tag.

Flow:
1. Resolve channel and priority.
2. Run idempotency checks.
3. Apply standard tags (`Lead Status: Warm`, `Stage: MQL`).
4. Ensure minimum stage/pipeline:
- Move to Warm Leads pipeline + MQL stage only if contact is not already further in sales progression.
5. Route by highest-priority channel:
- Referral:
  - Move to Sales pipeline at booked/pending stage.
  - Assign owner using current default assignment behavior (no overwrite restriction in this phase).
  - Notify sales admin.
  - Do not enter nurture.
- Lead forms (LinkedIn/Meta):
  - Move to Sales Outreach pipeline, active outreach stage.
  - Assign `sales_admin_user_id` using current default assignment behavior.
  - Start 7-day outreach if `LT Outreach Active` absent.
- Direct replies (Email/SMS/LinkedIn DM):
  - Move to Sales Outreach pipeline.
  - Start direct response follow-up if not active.
- Website/Traffic/Remarketing:
  - Add engaged visitor tag.
  - Start 14-day nurture if `LT Nurture Active` absent.
6. Persist routing metadata fields and lock values.
7. Add `LT Routed`.

## 10) Field-Level Collision Policy
- `owner`: follow current default assignment behavior (owner protection deferred).
- `pipeline/stage`: write only if target rank is higher than current rank.
- `lead status`: safe overwrite to `Warm`.
- `sequence enrollments`: check active enrollment/tag guard first.
- `utm` fields: do not overwrite non-empty `first-touch`; write to `last-touch`.

## 11) Duplicate Prevention
- Maintain both tag guard and field guard:
- Tag guard: `LT Outreach Active`, `LT Nurture Active`.
- Field guard: `lt_last_event_fingerprint`, `lt_last_routed_at`.
- Stop if same contact receives same route outcome within 24h unless priority increased.

## 12) Observability and Audit
Log each route decision with:
- contact id
- incoming channel
- incoming priority
- decision (`applied` or `ignored`)
- reason (`duplicate`, `locked_lower_priority`, `no_material_change`, etc.)
- previous and new pipeline/stage

Store logs in n8n execution data and optionally post summary note to contact timeline.

## 13) Rollout Plan
1. Build in dry-run mode (`decision only`, no writes) for 2 days.
2. Enable writes for Tier 1 channels only.
3. Expand to Tier 2, then Tier 3 after verification.
4. Weekly review for ignored events and false negatives.

## 14) Test Matrix (Minimum)
- Same lead submits Meta form twice in 5 minutes: one routing action only.
- Lead gets website tag then referral within 1 hour: referral wins.
- Existing owned deal receives low-priority website signal: verify assignment behavior matches current default policy.
- Email reply after nurture enrollment: transition to outreach without duplicate enrollments.
- Stage naming mismatch in labels: flow still works via IDs.

## 15) Implementation Notes
- Keep channel detection and routing as separate steps to simplify debugging.
- Keep all IDs and lock durations in one config object so domain/cutover changes are low-risk.
- If workflow/node parameter availability is uncertain, stop and verify against current n8n/GHL node schemas before deployment.

## 16) Implementation Progress (Completed)
Date completed: 2026-02-12

Completed in GHL sub-account `Live Transparent` (`Zwz4relUXVPxx8uohnjV`) via n8n workflow `GHL Warm Lead Setup - Fields and Tags` (`BYvEuUMUQFlXoxRj`).

### Contact Custom Fields Created
- `Lead Temperature` (`h7AEoiSE81GCNxI7dlTS`) - `DROPDOWN_SINGLE`
- `Primary Engagement Channel` (`e2OsKzZCf4On2vKPnNrz`) - `DROPDOWN_SINGLE`
- `Warm Date` (`3XhbeFiYESQor0GJZSFT`) - `DATETIME`
- `Warm Source` (`olS5L76mtvyGUUwosjPj`) - `DROPDOWN_SINGLE`
- `Warm Trigger Type` (`2pry8UETsoDBHJ7f3QRc`) - `DROPDOWN_SINGLE`

### Visual Tags Created
- `Warm  Instagram`
- `Warm  Facebook`
- `Warm  LinkedIn`
- `Warm  LinkedIn DM`
- `Warm  LinkedIn Lead Form`
- `Warm  Meta Lead Form`
- `Warm  Meta Traffic`
- `Warm  Meta Remarketing`
- `Warm  Email Outbound`
- `Warm  Email Inbound`
- `Warm  SMS`
- `Warm  Website`
- `Warm  Referral`
- `Lead Status: Warm`
- `Stage: MQL`

### Notes
- Pipelines were not modified.
- Existing workflows were not modified.
- No rename/delete actions were performed.

## 17) Next Action
- Setup Chatbot with AI Agent to make knowledgebase available to users.

## 18) Locked Pipeline and Stage ID Map (Canonical)
Location: `Live Transparent` (`Zwz4relUXVPxx8uohnjV`)
Locked on: `2026-02-12`

### Warm Pipeline
- Pipeline Name: `Warm`
- Pipeline ID: `FRjpDZ1HWj3UPgczsu3t`
- Stages:
- `New` -> `b961de1f-34fd-4b66-b032-f21225654868`
- `Qualified (MQL)` -> `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2`
- `Routed to Outreach` -> `477c0b59-4a64-4566-81d6-63e233362520`
- `Nurture Active` -> `98775f02-0018-4629-9e69-0b1fcab293eb`
- `Disqualified` -> `dae2ddc5-a031-4ffa-bcdb-79d5c9afe91b`

### Sales Outreach Pipeline
- Pipeline Name: `Sales Outreach`
- Pipeline ID: `dhdlf3O4tymxFtHk4aqq`
- Stages:
- `New` -> `3529dd3d-cab0-4279-967c-1aea203de4fb`
- `Attempting Contact` -> `b97e42b1-b4c2-4759-8212-33596a085cf2`
- `Engaged` -> `9ced8010-dfd7-4d5b-aa9c-c2eb58fca94d`
- `Meeting Requested` -> `1ab47457-c945-4d16-9dd7-305583823114`
- `Booked` -> `1f95dd0a-1cf2-4d31-abad-825d97d3ef69`
- `Unresponsive` -> `23276991-fbb3-4b0f-8d65-35c737b62bdd`

### Sales Pipeline
- Pipeline Name: `Sales`
- Pipeline ID: `MThKauqlvnEFuFmAkyWX`
- Stages:
- `Discovery Scheduled` -> `6f5aa304-a190-40da-8556-7c65bbc52733`
- `Discovery Completed` -> `facd3d31-c634-40c5-9271-17d608b4379c`
- `Proposal Sent` -> `42b12e59-9b51-4c82-b597-4a9c972322c9`
- `Negotiation` -> `f9022c83-7791-45c9-903d-381668454b2f`
- `Closed Won` -> `f6b65baa-eac8-4f02-b91e-2ab0c8841b2d`
- `Closed Lost` -> `d7784617-96f4-4ae4-8b3e-e2088b62627d`

## 19) Master Warm Routing Workflow Build Spec (Phase 1)
Scope:
- Build routing with stage/pipeline safety, dedupe, and priority.
- Do not enforce owner overwrite restrictions in this phase.

Workflow name:
- `WF - Master Warm Intake and Routing`

Trigger:
- Contact tag added where tag starts with `Warm  `.

Node sequence:
1. `Trigger - Warm Tag Added`
- Input: contact id, tag name, timestamp.
2. `Normalize Event`
- Map channel from tag name.
- Map priority:
- Referral `100`
- LinkedIn/Meta Lead Form `90`
- Email Inbound, SMS, LinkedIn DM `80`
- Website/Meta Traffic/Meta Remarketing `70`
- Instagram/Facebook/other social `60`
3. `Read Contact Context`
- Fetch current tags, custom fields, and latest opportunity state.
4. `Build Fingerprint`
- `contact_id + channel + source_event_id + event_date_bucket`.
5. `Idempotency Guard`
- Stop if fingerprint equals `lt_last_event_fingerprint`.
- Stop if same route outcome within last 24h and no priority increase.
6. `Lock Guard`
- If `now < lt_route_lock_until` and incoming priority lower than stored priority, stop.
7. `Apply Standard Warm Markers`
- Ensure tags: `Lead Status: Warm`, `Stage: MQL`.
- Set fields: `Lead Temperature=Warm`, `Warm Date=now`, `Warm Source=<channel>`.
8. `Ensure Warm Pipeline Baseline`
- Move to `Warm` pipeline stage `Qualified (MQL)` only if contact is not already in a more advanced lifecycle stage.
9. `Route Decision`
- Referral:
- Move to `Sales` -> `Discovery Scheduled`.
- Ensure `LT Nurture Active` removed (if present).
- Lead Form (LinkedIn/Meta):
- Move to `Sales Outreach` -> `New`.
- Start outreach sequence if `LT Outreach Active` absent.
- Direct reply (Email/SMS/LinkedIn DM):
- Move to `Sales Outreach` -> `Attempting Contact`.
- Start direct follow-up if not active.
- Website/Traffic/Remarketing:
- Move to `Warm` -> `Nurture Active`.
- Start nurture sequence if `LT Nurture Active` absent.
10. `Persist Routing Metadata`
- `lt_last_routing_reason`
- `lt_last_routing_channel`
- `lt_last_routed_at`
- `lt_routing_priority`
- `lt_last_event_fingerprint`
- `lt_last_event_at`
- `lt_route_lock_until` (based on priority class)
11. `Audit Note`
- Add concise timeline note with decision, priority, and target stage.
12. `Exit`
- Success or explicit ignored reason (`duplicate`, `locked_lower_priority`, `no_material_change`).

ID bindings (must use IDs, not names):
- Warm pipeline: `FRjpDZ1HWj3UPgczsu3t`
- Warm `Qualified (MQL)`: `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2`
- Warm `Nurture Active`: `98775f02-0018-4629-9e69-0b1fcab293eb`
- Sales Outreach pipeline: `dhdlf3O4tymxFtHk4aqq`
- Sales Outreach `New`: `3529dd3d-cab0-4279-967c-1aea203de4fb`
- Sales Outreach `Attempting Contact`: `b97e42b1-b4c2-4759-8212-33596a085cf2`
- Sales pipeline: `MThKauqlvnEFuFmAkyWX`
- Sales `Discovery Scheduled`: `6f5aa304-a190-40da-8556-7c65bbc52733`
