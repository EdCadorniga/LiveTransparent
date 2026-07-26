# Project Specifications: Outbound Voice Agent and Social Outreach

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This file defines boundaries, guardrails, and contracts; it does not repeat the architecture.

## Purpose

Production outbound calling flow for Vapi + n8n + GHL. The agent introduces LiveTransparent, qualifies intent and fit, records call context, and routes outcomes through tool calls.

## Canonical Status

- Current live state and priority order: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

## System Boundaries

- Vapi: realtime voice runtime.
- n8n: queueing, dispatch, callback routing, persistence, CRM sync.
- GHL: contact, opportunity, note, and tag system of record.
- Postgres: call-attempt and transcript metadata store.

### Qualification and SDR Boundary

- Warm is the unassigned intake and verification layer.
- Janvi's AI assessment is the promotion gate once its authoritative workflow and result field/tag are confirmed.
- Only an explicit `qualified cannabis business` result may promote a contact/opportunity to `Sales Outreach -> New`.
- SDR assignment happens only at Sales Outreach entry: align a single existing owner, preserve matching owners, flag conflicting owners, or assign Jason/Marc 50/50 when neither record has an owner.
- Contact native `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` must remain aligned.
- Vapi handles AI-pending/unverified contacts in Warm. AI-qualified and explicitly rejected/non-cannabis contacts are excluded from the Vapi queue.
- A successful Vapi warm transfer is manually claimed by the answering SDR and promoted to Sales Outreach. Vapi booking remains on Cameron's Regulated Ads calendar.

### Scheduling Contract

- Recurring n8n workflows must use n8n's native `Schedule Trigger` node.
- Do not create OS, Coolify, or external cron jobs for workflow scheduling.
- The Vapi dialer runs from a two-minute Schedule Trigger and applies its timezone-aware business-hours guard before dispatching a call.
- `LT - Voice Dequeue Next` is an unpublished helper and must not be used as an automatic call-start path. Callback completion must not trigger another dequeue request.
- `LT - Voice Queue Enqueue` is authenticated with `X-LT-Voice-Queue-Secret` using the `VOICE_QUEUE_ENQUEUE_SECRET` deployment/reference value.
- Callback timer state is deduplicated within 60 seconds and pruned after 30 minutes.

## Live Workflows

| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Queue poller, timezone guard, call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | End-of-call webhook plus 4 tool endpoints |

## Social Outreach Scope

### Current Live LinkedIn State

- `LT - GHL LinkedIn Connect Dispatcher (Unipile)` is active and uses the invite copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn DM Sequence (Unipile)` is active and uses the LinkedIn DM copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn Unipile New Messages` is active and marks active conversations when inbound replies arrive.
- LinkedIn DM sends are blocked when `payload_json.dm_conversation_status = 'active'`.

### LinkedIn Timing

- The current LinkedIn DM cadence is approximately day 0, day 3, day 7, and day 10, with terminal completion at day 14.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.
- If someone responds on LinkedIn, immediately suppress them from all remaining automated LinkedIn DMs and persist that suppression in the shared state.

### SMS Campaign Scope

- `outreach_messages.docx` is the source of truth for SMS copy.
- SMS is implemented as a SimpleTexting campaign stack, not as one-off ad hoc messages.
- The campaign uses a controlled pool dispatcher, a sequencer, and a shared send endpoint.
- The SMS workflow needs per-contact send tracking so each message can be marked as sent once and never repeated.
- The SMS workflow also needs response ingestion so replies update the same canonical state used by the send workflow.
- The SMS workflow should preserve unsubscribe handling and should not send to opted-out contacts.
- Replies should trigger a Slack notification in `#lead` so the team can respond without checking n8n first.
- The preferred model is a shared Postgres state table or a tightly controlled send-state plus response-state pair, but the same contact record must be authoritative for both send and reply logic.

### SMS Missing Steps

1. Normalize SMS copy from `outreach_messages.docx` into a template registry.
2. Define the SMS state schema and idempotency keys.
3. Build the SimpleTexting send workflow with batching controls.
4. Wire inbound reply and delivery webhooks into the same state model.
5. Confirm opt-out / unsubscribe propagation.
6. Run a low-volume smoke test before batch sends.
7. Deploy the staged SMS workflows into live n8n and verify the live webhook routes.

## Queue Contract

Minimum live `voice_call_queue` fields:

`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

Injected Vapi variables:

`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

Planned qualification extension: add `ai_qualification_state` only after the authoritative qualification workflow and field/tag contract has been identified and migrated through the live queue, dialer, and callback paths.

Normalized callback output:

`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration

- Secrets: `GHL_PIT` aliased as `GHL_API_KEY`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- Voice write actions: add `vapi_*` tags per outcome, create contact notes for completed calls

## Guardrails

- Do not call `dnc=true` contacts.
- Respect `attempt_count < max_attempts`.
- Enforce 72h cooldown between attempts.
- Call only Mon-Fri 9am-5pm CT.
- The native Schedule Trigger controls polling frequency; the workflow guard controls call eligibility.
- Fall back to GHL contact timezone when queue timezone is missing; use CT 12-2pm safe window if neither is available.
- Keep secrets in env/credentials; do not hardcode them in workflow JSON.
- Do not enqueue AI-qualified or explicitly rejected/non-cannabis contacts for Vapi. Vapi queue eligibility is limited to AI-pending/unverified Warm contacts.
- Keep Vapi warm transfer separate from Cameron calendar booking. Transfer uses the shared SDR number; booking uses Cameron's Regulated Ads calendar.
- Preserve n8n graph integrity when editing workflows.
- For social outreach, never send duplicate messages. Every send workflow must check and update shared state before and after send.
- For social outreach, reply-handling workflows must mark the contact as in conversation so follow-up sequences stop.
- For SMS, keep the batch size controlled until reply capture, opt-out propagation, and Slack alerts have all been verified live.

## Callback Tools

- `update_lead_status`: GHL tag plus Postgres disposition update.
- `add_to_dnc`: set `voice_call_queue.dnc=true` and add the GHL DNC tag.
- `log_call_outcome`: upsert `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales`: post lead name and summary into `#leads`.
- Vapi API-managed `transferCall`: warm-transfer to the shared SDR number using neutral Sales Lead language.

## Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

## Smoke Test

1. Seed one queue row with a controlled test number.
2. Run the outbound workflow manually.
3. Confirm the Vapi request includes expected metadata.
4. Send a simulated callback payload.
5. Confirm Postgres insert plus GHL note creation.
6. Replay the callback and confirm no duplicate record.
7. Confirm AI-qualified contacts are excluded from the Vapi queue and a successful warm transfer remains manually claimable by the answering SDR.

## Social Outreach Smoke Test

1. Verify LinkedIn invite and DM copy are still sourced from `outreach_messages.v2.docx`.
2. Send one LinkedIn test DM and confirm `linkedin_connection_state` advances exactly one step.
3. Simulate an inbound LinkedIn reply and confirm `dm_conversation_status` becomes `active`.
4. Confirm the active conversation is excluded from both LinkedIn DM send paths.
5. Confirm a replied LinkedIn contact stays excluded from all later automated DM steps, not just the next scheduled run.
6. Prepare a single SMS test contact and confirm one SMS send is tagged in state.
7. Simulate an inbound SMS reply and confirm the response workflow updates the same canonical state.
8. Confirm unsubscribe handling blocks any future SMS sends for opted-out contacts.
