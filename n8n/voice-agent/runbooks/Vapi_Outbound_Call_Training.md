# Vapi Outbound Call Training

This document explains how the two production voice workflows work together with Vapi to place outbound calls in LiveTransparent.

## Production Workflows

- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`)
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)

These two workflows are the live production pair.

## Outbound Agent Behavior

The Vapi assistant is configured as a LiveTransparent outbound call representative.

### Identity and tone

- Speak as a LiveTransparent team member.
- Keep responses concise, polite, and natural.
- Use the company pronunciation `liv transparent`.

### Disclosure policy

- Do not say or imply that you are an AI, bot, robot, virtual assistant, or automated system.
- If asked directly, keep the answer brief and neutral, then redirect back to helping the prospect.

### Business positioning

- Describe LiveTransparent as helping marketing teams manage and understand marketing performance for regulated products.
- Use the phrase `marketing regulated products` when giving a high-level explanation.
- Only mention named client examples if the prospect asks for them.

### Call flow

The assistant should:

1. Open politely.
2. Confirm who is being called and whether it is a good time.
3. Give a short high-level explanation of LiveTransparent.
4. Qualify interest and fit.
5. If the contact is still AI-pending/unverified and the conversation qualifies them, offer a meeting with Cameron.
6. If the prospect asks for a human or a warm transfer, use the shared SDR transfer tool without naming Cameron.
7. If not interested or explicitly rejected, close politely.

### Booking behavior

The outbound agent has tools to:

- pull context from GHL
- review Cameron’s calendar for `Regulated Ads`
- create a new booking when the prospect fits and wants to meet
- transfer a live call to the shared SDR number when a human handoff is required

Booking should only happen after qualification and explicit interest.

## What Each Workflow Does

### 1. Outbound Dialer

The dialer workflow is responsible for starting calls.

It runs from n8n's native Schedule Trigger, pulls the next eligible row from `voice_call_queue`, and tells Vapi to place the call using:

- the Vapi phone number ID
- the Vapi assistant ID
- the contact phone number
- queue metadata needed later by the callback workflow

It also writes a GHL note so the team can see that the call started.

### 2. Callback + Tools

The callback workflow is the single inbound entry point for Vapi.

It handles two kinds of requests on the same webhook:

- end-of-call callbacks
- live tool calls from the assistant

It normalizes the incoming payload, routes tool calls by `tool.name`, writes call outcome records to Postgres, and updates GHL and Slack where needed.

## How The Tools Fit Together

### GHL lookup

The outbound assistant can use GHL context to understand the prospect before or during the call.

Typical uses:

- confirm contact details
- look up prior interaction context
- understand fit or history before offering a meeting

### Cameron calendar lookup

The assistant can check Cameron’s calendar for `Regulated Ads` availability.

Use this only after the prospect:

- shows real interest
- appears to fit the target profile
- agrees to explore a meeting

### Warm transfer to the SDR team

- Vapi uses the live `transferCall` tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb`.
- The destination is the shared SDR number, not an individual Jason or Marc number.
- Transfer language should say `our sales team` or `our Sales Lead`, not Cameron, Jason, Marc, John, or another named owner.
- Warm transfer and Cameron booking are separate outcomes. A transfer does not book Cameron's calendar.
- After a successful transfer, the answering SDR manually assigns the contact and opportunity to themselves and moves the record into Sales Outreach.

### Booking a meeting

If the prospect is qualified and wants to meet:

1. confirm their timezone
2. fetch up to three available slots
3. offer the slots clearly
4. book the selected time
5. confirm the next step before ending the call

## End-to-End Call Flow

1. The dialer runs every 2 minutes through n8n's native Schedule Trigger. No external cron job is used.
2. It selects the next queue row from `voice_call_queue` where:
   - `status = 'pending'`
   - `dnc = false`
   - `attempt_count < max_attempts`
   - `next_attempt_at` is due or empty
   - `locked_at` is either empty or stale enough to be reclaimed
3. The dialer selects the lowest `attempt_count` tier first, then the oldest `created_at` row inside that tier.
4. The dialer atomically claims that row by setting `locked_at`, `lock_owner`, and the in-progress state before the contact lookup.
5. If GHL shows a terminal Vapi/DNC block, the phone is invalid, or the contact is outside its local calling hours, the row is released and the dialer immediately checks the next row in the same execution.
6. Same-run queue advancement is capped at 25 queue checks to prevent an unbounded execution or excessive GHL traffic. No call is placed unless an eligible contact passes the blocklist, phone, and timezone checks.
7. The dialer sends a `POST` request to Vapi to create the outbound call.
8. The dialer passes `assistantOverrides` so Vapi receives:
   - `contact_id`
   - `queue_id`
   - `campaign_id`
   - `lead_timezone`
   - `first_name`
9. Vapi places the call using the configured assistant.
10. During the live call, Vapi can call tools back into the merged callback webhook.
11. When the call ends, Vapi posts the end-of-call payload to the same webhook.
12. The callback workflow records the call result, adds GHL notes, and updates any tool-specific state.
13. AI-qualified contacts are excluded from the Vapi queue; Vapi is the Warm verification path for AI-pending/unverified contacts.
14. If a warm transfer is answered, the SDR manually claims the contact and opportunity and promotes the record to `Sales Outreach -> New`.

## 2026-07-23 Production Hardening

- n8n is upgraded to `2.33.3`; recurring schedules use native Schedule Trigger nodes, not OS or Coolify cron.
- The callback no longer calls `LT - Voice Dequeue Next`; that workflow is unpublished and remains an explicit helper only.
- Callback timer state uses a 60-second duplicate guard and is pruned after 30 minutes.
- Queue insertion requires `X-LT-Voice-Queue-Secret` from `VOICE_QUEUE_ENQUEUE_SECRET`.
- Apollo phone-request failures are counted for monitoring, and the timeout reaper Slack summary is connected.

## 2026-07-25 Scheduler and Queue Recovery

- Stale n8n execution records were removed after queued runs remained in “Starting soon” for multiple days. Legitimate `waiting` executions were preserved.
- The dialer was unpublished and republished, then manually verified against four different queue contacts.
- The native two-minute Schedule Trigger is healthy; no Redis, worker pool, OS cron, or Coolify cron is required for the current single-container deployment.
- The old `End - No Phone` and `End - Outside Contact Hours` nodes are now disconnected because their branches feed the same-run loop. They are legacy display nodes and may be removed during a future cleanup.

## Dialer Workflow Walkthrough

The dialer workflow is intentionally simple.

### Trigger

- An n8n Schedule Trigger runs every 2 minutes.
- The workflow's business-hours guard prevents calls outside the allowed Mon-Fri window.
- Do not replace this with an OS or Coolify cron job.

### Queue lookup

- The workflow queries `voice_call_queue` for the next eligible row.
- It returns queue and contact fields needed for the call.
- It currently reads:
  - `queue_id`
  - `contact_id`
  - `first_name`
  - `phone_e164`
  - `campaign_id`
  - `lead_timezone`
   - `max_attempts`
   - `attempt_count`
   - AI qualification state/verification status when available

### Guard

- If no queue row is found, the workflow stops.
- If a row is found, it is passed forward as the call target.

### Vapi call start

- The workflow sends a `POST` request to Vapi.
- It includes:
  - `phoneNumberId`
  - `customer.number`
  - `assistantId`
  - `assistantOverrides.variableValues`
  - `assistantOverrides.metadata`

### Why the metadata matters

The metadata attached by the dialer is what lets the callback workflow recover context later.

Without `contact_id`, `queue_id`, and `campaign_id`, the callback workflow would not know which queue row or contact the completed call belongs to.

### GHL note

- After the call is started, the dialer writes a note to the contact in GHL.
- This gives the sales team immediate visibility that the call began.

### Practical implication

The dialer does not qualify the lead itself. Its job is to get the call started with the right metadata so the assistant can do the conversational work and the callback workflow can log the results.

## Callback + Tools Workflow Walkthrough

The callback workflow is the operational core of the voice integration.

### Trigger

- A single webhook listens on:
  - `/webhook/lt-voice-agent-vapi-callback`

### Request detection

- The workflow checks whether the incoming body contains `tool.name`.
- If yes, it treats the payload as a live tool call.
- If not, it treats the payload as an end-of-call callback.

### Live tool calls

Supported tools:

- `update_lead_status`
- `add_to_dnc`
- `log_call_outcome`
- `notify_sales`
- Vapi API-managed `transferCall` to the shared SDR number

Tool behavior:

- `update_lead_status`
  - marks the queue row completed
  - adds the `vapi_call_attempted` tag in GHL
- `add_to_dnc`
  - marks the queue row as DNC and completed
  - adds the `vapi_dnc` tag in GHL
- `log_call_outcome`
  - upserts a `voice_call_attempt` row
- `notify_sales`
  - sends a Slack message to `#reaper`
- `report_referral`
  - checks GHL for the referred contact
  - sends a Slack message if the referred contact is new
  - returns the referral contact details when found:
    - `referral_contact_name`
    - `referral_contact_email`
    - `referral_contact_phone`
    - `referral_contact_company`
    - `referral_match_method`
    - `referral_lookup_status`

### Call qualification and booking tools

The assistant may also use GHL and calendar-related tools during the live conversation to:

- fetch contact context
- inspect Cameron’s calendar availability
- create a booking when the prospect is a fit and wants to meet
- report a better contact when the current prospect refers us elsewhere

This booking behavior belongs in the assistant conversation flow, not in the dialer workflow.

### End-of-call handling

When the payload is not a tool call, the workflow:

- normalizes the Vapi call result
- derives a disposition and matching `vapi_*` tags from `call.endedReason`:
  - `no_answer` — customer did not answer
  - `voicemail` — voicemail left
  - `busy` — customer was busy
  - `wrong_number` — wrong number reached
  - `contact_disconnected` — customer dropped during call
  - `interested` — human answered and was interested (`analysis.successEvaluation = true`)
  - `not_interested` — human answered but not interested (`analysis.successEvaluation = false`)
  - `interest_unknown` — human answered but Vapi could not confidently classify the outcome
- maps each disposition to the corresponding `vapi_*` GHL tags, including the interest tags below
- inserts a `voice_call_attempt` row
- marks voicemail queue rows completed so they do not re-enter the campaign queue
- applies the `vapi_*` tags to the GHL contact via `GHL - Apply Tags`
- writes a GHL contact note with the disposition, summary, and recording link
- does not trigger another dequeue call; the unpublished dequeue helper is not an automatic call-start path

## Data Written By The System

### Postgres

The voice system uses these tables:

- `voice_call_queue`
- `voice_call_attempt`
- `voice_call_transcript_turn`

### GHL Tags

Every end-of-call event applies `vapi_call_attempted` plus one outcome-specific tag:

| GHL Tag | Applies When |
|---------|-------------|
| `vapi_call_attempted` | Always — every completed call attempt |
| `vapi_no_answer` | `call.endedReason` contains `customer-did-not-answer` or `no-answer` |
| `vapi_voicemail` | `call.endedReason` contains `voicemail` (paired with `vapi_voicemail_left`) |
| `vapi_voicemail_left` | Same as `vapi_voicemail` — both applied together |
| `vapi_busy` | `call.endedReason` contains `customer-busy` or `busy` |
| `vapi_wrong_number` | `call.endedReason` contains `wrong-number` |
| `vapi_contact_disconnected` | `call.endedReason` contains `customer-dropped` |
| `vapi_human_answered` | Human answered (base tag for all human-connected outcomes) |
| `vapi_interested` | Human answered and `analysis.successEvaluation = true` |
| `vapi_not_interested` | Human answered and `analysis.successEvaluation = false` |
| `vapi_interest_unknown` | Human answered, but Vapi could not confidently classify the outcome |
| `vapi_dnc` | Added by the `add_to_dnc` tool (manual DNC action) |
| `vapi_voicemail` / `vapi_voicemail_left` | Voicemail disposition also completes the queue row for the current campaign |

**Important**: Calls with disposition `failed` or `null` in `voice_call_attempt` never connected to Vapi, so no end-of-call webhook fires and no `vapi_*` tags are automatically applied. Those contacts must be handled outside the voice system.

### GHL notes

The workflows write:

- call-start notes
- call-completion notes with disposition, summary, and recording link

### Slack

If the assistant calls `notify_sales`, the callback workflow posts a lead alert to Slack.

## Vapi Dashboard Setup

Vapi should be configured to use:

- the LiveTransparent assistant ID
- the LiveTransparent phone number ID
- the merged callback URL:
  - `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`

The four existing tools in Vapi should match the callback workflow exactly.
The referral tool should be added as a fifth tool named `report_referral`.

Tool names and expected parameters:

- `update_lead_status`
  - `ghl_contact_id`
  - `disposition`
  - `notes`
  - `followUpAt`
- `add_to_dnc`
  - `ghl_contact_id`
  - `reason`
- `log_call_outcome`
  - `call_id`
  - `disposition`
  - `notes`
  - `followUpAt`
  - `handoff_required`
- `notify_sales`
  - `lead_name`
  - `company`
  - `disposition`
  - `notes`
  - `contact_id`
- `report_referral`
  - `referral_name`
  - `referral_phone`
  - `referral_email`
  - `referral_role`
  - `referral_company`
  - `referrer_name`
- `report_referral` returns:
  - `existsInGhl`
  - `referral_contact_id`
  - `referral_contact_name`
  - `referral_contact_email`
  - `referral_contact_phone`
  - `referral_contact_company`
  - `referral_match_method`
  - `referral_lookup_status`

## What A New Team Member Should Remember

- The dialer starts calls.
- The callback workflow receives the tool calls and the call completion event.
- Both workflows depend on the metadata passed from the dialer.
- The merged callback webhook is the canonical Vapi endpoint.
- Production traffic should only use the two workflows listed at the top of this document. `LT - Voice Dequeue Next` is unpublished and must not be reactivated as a call-start path without an explicit design review.

## Operational Checks

Before changing either workflow, verify:

- the production workflow IDs are still active
- the merged callback webhook path is unchanged
- the Vapi assistant still points at the merged callback URL
- the four tool names still match the callback routing logic
- the queue table still exposes eligible rows for the dialer
- the dialer still uses an n8n Schedule Trigger rather than an external cron job

When validating end to end, test in this order:

1. queue row selection
2. Vapi call start
3. live tool callback
4. end-of-call callback
5. Postgres attempt row
6. GHL note write

## Common Failure Modes

- Duplicate calls:
  - the same queue row can be selected again if queue-claim logic is not enforced.
- Missing contact context:
  - Vapi tool calls will fail to route cleanly if the dialer does not pass the right metadata.
- Wrong webhook URL:
  - Vapi tool calls and end-of-call callbacks must both point to the merged callback path.
- Tool name mismatch:
  - the callback workflow routes strictly by `tool.name`.
- Overbooking or premature booking:
  - do not offer a meeting before qualification and explicit interest are established.
- Disclosure drift:
  - do not let the assistant mention AI, automation, or bot-like language unless a direct question requires a brief neutral redirect.
