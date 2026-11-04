# Project Specifications: Outbound Voice Agent and Social Outreach

> This file defines boundaries, guardrails, and contracts. The generated Repomix bundle was retired on 2026-11-04; use the current status, relevant subsystem runbooks, and live system evidence for architecture and operational state.

> **Operational boundary (2026-11-05 local-clock documentation review):** Ed requires production read-only for the developer transition. The implementation/status paragraphs below are dated design or historical observations, not fresh runtime verification or authorization to execute the listed smoke tests, sends, workflow changes, or deployments. Full transition acceptance remains partial; see the [transition ledger](./docs/transition-plan.md) and [closeout decisions](./docs/transition/closeout-decisions-2026-11-05.md).

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
- The canonical classification tags are `qualified` for a regulated business, including nicotine, cannabis, CBD, vape, hemp, and related verticals, and `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate and routes qualified opportunities to `Sales Outreach -> Qualified`.
- SDR assignment happens only at Sales Outreach entry: align a single existing owner, preserve matching owners, flag conflicting owners, or assign Jason/Marc 50/50 when neither record has an owner.
- Contact native `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` must remain aligned.
- Vapi handles classified regulated-business contacts in Warm and excludes `not qualified` contacts. Raw pool tags must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR and promoted to Sales Outreach. Vapi booking remains on Cameron's Regulated Ads calendar.

### Scheduling Contract

- Recurring n8n workflows must use n8n's native `Schedule Trigger` node.
- Do not create OS, Coolify, or external cron jobs for workflow scheduling.
- The Vapi dialer runs from a two-minute Schedule Trigger and applies its timezone-aware business-hours guard before dispatching a call.
- `LT - Voice Dequeue Next` is an unpublished helper and must not be used as an automatic call-start path. Callback completion must not trigger another dequeue request.
- `LT - Voice Queue Enqueue` is authenticated with `X-LT-Voice-Queue-Secret` using the `VOICE_QUEUE_ENQUEUE_SECRET` deployment/reference value.
- Callback timer state is deduplicated within 60 seconds and pruned after 30 minutes.

## Voice workflow identifiers — historical reference (refresh n8n-lt before operation)

| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Queue poller, timezone guard, call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | End-of-call webhook plus 4 tool endpoints |

## Social Outreach Scope

### LinkedIn State — dated evidence, refresh before operation

This specification is not a live workflow inventory. The latest dated project closeout (2026-10-21) records all nine invite/DM-capable n8n-lt workflows as `active=false`; the 2026-11-04 inventory is the current transition snapshot. See [AGENTS.md](./AGENTS.md) and the [dated n8n inventory](./docs/transition/n8n-workflow-inventory-2026-11-04.md) before any operational decision. Do not infer present activation from the historical descriptions below.

- The inbound normalizer's malformed form-payload fallback is a documented implementation guard; preserve it unless a fresh live read and tested replacement justify a change.
- The shared-state reply-suppression requirements below are durable design constraints, not evidence that a sender is active.

### LinkedIn Timing

- The historical canonical LinkedIn DM sequence was designed around day 0, day 3, day 7, and day 10, with terminal completion at day 14; sender workflows were subsequently deactivated. Do not treat this as a currently running schedule.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.
- If someone responds on LinkedIn, immediately suppress them from all remaining automated LinkedIn DMs and persist that suppression in the shared state.
- State sync must use bounded direct HTTP calls with explicit retry/error reporting; API failures must not be reported as an empty healthy scan.
- Connection dispatch must atomically claim a `ready` row before an invite and perform a live GHL suppression/reply check immediately before sending.
- The state-upsert boundary uses the protected n8n `httpHeaderAuth` credential `LT LinkedIn State Upsert Webhook` and requires `X-LT-LinkedIn-State-Secret`. Callers must send the shared header; do not reuse an unrelated webhook secret. In Community Edition, each relevant workflow stores `stateUpsertSecret` in its single `Config` node and Code nodes read that value instead of embedding the literal. The secret is not stored in the repository.

### Partnership LinkedIn State

- Partnership LinkedIn state is isolated in `partnership_linkedin_connection_state` with `source_key = 'partnership'`; it must not be conflated with the main `linkedin_connection_state` table.
- The partnership dispatcher seeds `ready` rows from GHL contacts tagged `partner_candidate_linkedin` before reading its ready queue. The 2026-07-31 seed produced 127 rows.
- As of the 2026-07-31 checkpoint, the Partnership Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence had been approved with `defaultDryRun=false`; the LinkedIn invite and DM senders were later deactivated (see the 2026-10-21 closeout). Do not infer present activation from this historical statement or manually execute any sender under the production-read-only decision.
- Before changing or republishing a send-capable path, verify GHL suppression/reply checks, state-upsert authentication, idempotent claims, release-log writes, and the exact active version. A successful dry run or readable PIT is not sufficient evidence for safe production sending.

### SMS Campaign Scope

- `outreach_messages.docx` is the source of truth for SMS copy.
- SMS is implemented as a SimpleTexting campaign stack, not as one-off ad hoc messages.
- The campaign uses a controlled pool dispatcher, a sequencer, and a shared send endpoint.
- The SMS workflow needs per-contact send tracking so each message can be marked as sent once and never repeated.
- The SMS workflow also needs response ingestion so replies update the same canonical state used by the send workflow.
- The SMS workflow should preserve unsubscribe handling and should not send to opted-out contacts.
- Replies should trigger a Slack notification in `#lead` so the team can respond without checking n8n first.
- The preferred model is a shared Postgres state table or a tightly controlled send-state plus response-state pair, but the same contact record must be authoritative for both send and reply logic.

### SMS Campaign Build Steps — historical design checkpoint

**Superseded as a statement of current implementation.** Later project records document a live SimpleTexting sender/provider path and campaign workflows; this checklist must not be treated as proof that these components are unbuilt. Consult the [current project status](./Project%20Status%20and%20Next%20Steps.md), the SimpleTexting runbook/evidence, and a fresh authorized read before operating. Keep the following only as a historical design checklist; its smoke-test/deployment steps are not authorization to perform them.

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
- The root `GHL_PIT` was directly verified on 2026-07-31 against the official REST location and contacts endpoints with HTTP 200. PIT access confirms CRM/API access only; it does not authenticate the Firebase/browser session used by the native Custom Report builder.
- Native GHL Custom Report widget layout has no supported public API/SDK mutation surface. Use the authenticated GHL UI or an explicitly approved internal API path; do not infer report-builder access from successful PIT REST calls.
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

## Historical Smoke-Test Outline — Not Authorized for Production Use

The steps below are retained as historical acceptance ideas, not current operating instructions. They call outbound workflows, send messages, or mutate queue/CRM state and therefore must **not** be run as part of documentation review or routine verification. Production execution, provider tests, queue seeding, callback replay, and CRM/state writes require a separately approved, precisely scoped test plan. Prefer offline mocks and read-only artifact/state inspection; confirm current workflow status and safety gates from dated transition evidence before planning any test.

For the Vapi path, a future isolated test plan may verify metadata mapping, callback idempotency, suppression, and warm-transfer handling with mocks or a non-production harness. Do not seed a live queue row, run the live dialer, or replay a callback against production based on this outline.

## Historical Social Outreach Test Outline — Not Authorized for Production Use

These are not current instructions to send or simulate messages. LinkedIn outbound workflows were explicitly left inactive in the 2026-10-21 closeout, and the 2026-10-26 withdrawal-hold update requires held identities to remain out of automated queues. Do not infer that a test send is safe because a workflow or provider endpoint exists. Use read-only graph/state review and offline mocks only unless a new, explicit test authorization names the exact sender, recipient, action, and safeguards.

The historical acceptance goals were to check message-copy provenance, sequence-state transitions, inbound-reply suppression, SMS opt-out handling, and deduplication. Any future validation should avoid real external sends and production state mutations unless separately approved; unsubscribe and reply protections must remain fail-closed.
