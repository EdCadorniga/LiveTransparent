# Project Specifications: Outbound Voice Agent (Vapi + n8n + GHL)

## Objective
Production-ready outbound AI call agent that introduces itself as a LiveTransparent representative, answers approved company questions, qualifies on intent + fit, captures call outcome context, and supports downstream CRM routing via tool calling.

## Status
Describes the current Vapi Phase 2 production implementation. Older split-callback / direct-booking artifacts are archived.

## System Boundaries
- **Vapi**: realtime call runtime (voice, ASR/TTS, model execution).
- **n8n**: queue orchestration, call launch, callback processing, persistence, CRM sync.
- **GHL**: contact/opportunity/task/note system of record.
- **Postgres**: durable call-attempt event log and transcript metadata.

## Live Production Workflows
| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Cron dialer — queue poller, timezone-aware scheduling, Vapi call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Merged callback/tool router — end-of-call webhook + 4 tool endpoints |

## Data Contracts

### Queue Row Minimum (`voice_call_queue`)
`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

### Vapi Variable Injection
`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

### Callback Normalized Output
`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration
- **Secrets**: `GHL_PIT` (aliased as `GHL_API_KEY` in `.env`), `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- **Voice write actions**: add `vapi_*` tags per outcome (see tag inventory in AGENTS.md), create contact notes for completed calls

## Required Environment Variables
- **Vapi**: `VAPI_API_KEY`, `VAPI_PHONE_NUMBER_ID`, `VAPI_ASSISTANT_ID`
- **GHL**: `GHL_API_KEY` (alias for `GHL_PIT`)
- **Postgres**: standard n8n credential (db host, port, user, password, database)

## Operational Guardrails
- Do not call `dnc = true` contacts.
- Respect `attempt_count < max_attempts` and `next_attempt_at` scheduling.
- 72h cooldown between dial attempts.
- Business hours guard: Mon-Fri 9am-5pm CT only.
- Fall back to GHL contact timezone if queue `lead_timezone` is empty; use CT 12-2pm safe window if neither available.
- Keep secrets in env/credentials only; never hardcode in workflow JSON.

## Integration Test (minimum)
1. Seed one queue row with a controlled test number.
2. Execute outbound workflow manually.
3. Confirm Vapi request includes expected metadata variables.
4. Send simulated/real callback payload.
5. Confirm Postgres insert + GHL note creation.
6. Confirm no duplicate record on callback replay.
