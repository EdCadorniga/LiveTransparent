# Project Specifications: Outbound Voice Agent (Vapi + n8n + GHL)

## Objective
Implement a production-ready outbound AI call agent that can:
- Introduce itself as a LiveTransparent representative.
- Answer basic approved company questions.
- Qualify on intent + fit.
- Capture full call outcome/transcript context.
- Support downstream booking and CRM routing workflows.

## System Boundaries
- `Vapi`: realtime call runtime (voice, ASR/TTS, model execution).
- `n8n`: queue orchestration, call launch, callback processing, persistence, CRM sync.
- `GHL`: contact/opportunity/task/note system of record.
- `Postgres`: durable call-attempt event log and transcript metadata.

## Live Workflows (n8n)
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`orJrDqR6hQjgPLpg`) - inactive.
- `LT - Voice Agent V1 Vapi Callback Sync` (`fx4UvKUWbqJEY3LK`) - inactive.

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
