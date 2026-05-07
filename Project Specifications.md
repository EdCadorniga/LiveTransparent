# Project Specifications: Outbound Voice Agent (Vapi + n8n + GHL)

## Objective
Implement a production-ready outbound AI call agent that can:
- Introduce itself as a LiveTransparent representative.
- Answer basic approved company questions.
- Qualify on intent + fit.
- Capture full call outcome/transcript context.
- Support downstream CRM routing workflows and tool calling.

## Status
This specification describes the current production Vapi Phase 2 implementation. The older split callback / direct-booking voice-agent artifacts are archived and should not be treated as live sources of truth.

## System Boundaries
- `Vapi`: realtime call runtime (voice, ASR/TTS, model execution).
- `n8n`: queue orchestration, call launch, callback processing, persistence, CRM sync.
- `GHL`: contact/opportunity/task/note system of record.
- `Postgres`: durable call-attempt event log and transcript metadata.

## Live Workflows (n8n)
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`orJrDqR6hQjgPLpg`) - production dialer.
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) - production merged callback/tool router.

## Archived Voice Workflows
- `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) - archived validation copy.
- `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`) - archived test workflow.
- `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`) - archived test workflow.
- `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`) - archived test workflow.

## Data Contracts
- Queue row minimum fields:
  - `queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`.
- Vapi variable injection fields:
  - `contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, optional `first_name`.
- Callback normalized output:
  - `call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`.

## Disposition Rules (v1)
- `no_answer`: no pickup/no-answer provider outcome.
- `voicemail`: voicemail endpoint reached.
- `connected`: connected call without qualification success signal.
- `qualified_booked`: success-evaluated booked/qualified flow.
- `failed`: webhook/infrastructure/provider failure cases.

## Required Environment Variables
- Vapi:
  - `VAPI_API_KEY`
  - `VAPI_PHONE_NUMBER_ID`
  - `VAPI_ASSISTANT_ID`
  - `VAPI_BASE_URL` (optional)
- GHL:
  - `GHL_API_KEY`
- Existing database credentials for Postgres node in n8n.

## Operational Guardrails
- Do not call `dnc = true` contacts.
- Respect `attempt_count < max_attempts`.
- Respect `next_attempt_at` scheduling.
- Keep workflows inactive until integration test passes.
- Keep secrets in env/credentials only; never hardcode in workflow JSON.

## Integration Test (minimum)
1. Seed one queue row with a controlled test number.
2. Execute outbound workflow manually.
3. Confirm Vapi request includes expected metadata variables.
4. Send simulated/real callback payload.
5. Confirm Postgres insert + GHL note creation.
6. Confirm no duplicate record on callback replay.
