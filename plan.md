# Vapi + n8n Outbound Voice Agent Plan (LiveTransparent)

## Goal
Launch a production-safe outbound AI call agent where:
- Vapi handles realtime voice/audio + model runtime.
- n8n handles queue orchestration, CRM sync, booking policy, and persistence.
- GHL remains CRM source of truth for contact/opportunity state.

## Current State (2026-05-06)
- Live workflow created: `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`orJrDqR6hQjgPLpg`) - inactive.
- Live workflow created: `LT - Voice Agent V1 Vapi Callback Sync` (`fx4UvKUWbqJEY3LK`) - inactive.
- Repo workflow specs live under `n8n/voice-agent/n8n-workflow/`.

## Architecture
1. `Outbound Dialer (n8n)`
- Poll `voice_call_queue` for callable leads.
- Enforce DNC + max attempts + next_attempt gating.
- Start Vapi call with assistant variables (`contact_id`, `queue_id`, `campaign_id`, context fields).
- Log call-start note in GHL.

2. `Call Runtime (Vapi)`
- Twilio/telephony + speech + OpenRouter model inference.
- Assistant prompt handles intro, FAQ scope, intent+fit qualification, and booking dialogue.

3. `Callback Sync (n8n)`
- Accept end-of-call webhook from Vapi.
- Normalize disposition + summary + transcript/recording metadata.
- Persist attempt in Postgres.
- Write call summary note to GHL.

## Required Configuration
- In Vapi:
  - `VAPI_API_KEY`
  - Assistant configured with OpenRouter model.
  - Phone number + telephony routing configured.
  - End-of-call webhook pointed to n8n callback URL.
- In n8n env/Coolify:
  - `VAPI_API_KEY`
  - `VAPI_PHONE_NUMBER_ID`
  - `VAPI_ASSISTANT_ID`
  - `VAPI_BASE_URL` (optional; defaults to `https://api.vapi.ai/call`)
  - `GHL_API_KEY`
- In Postgres:
  - Apply `n8n/voice-agent/postgres/voice_agent_schema.sql`.

## Next Steps (Execution Order)
1. Configure OpenRouter model + assistant behavior in Vapi.
2. Set n8n env vars for Vapi IDs/keys in Coolify.
3. Apply Postgres schema and confirm tables/indexes exist.
4. Wire Vapi end-of-call webhook to `LT - Voice Agent V1 Vapi Callback Sync`.
5. Run one test contact through queue and verify:
   - Vapi call starts,
   - callback hits n8n,
   - Postgres attempt row is inserted,
   - GHL note is created.
6. Add stage/tag outcome mapping in callback workflow:
   - `AI-Call-Successful`, `AI-Call-No-Answer`, `AI-Handoff-Required`.
7. Add booking-sync branch in callback workflow:
   - when booked, write appointment metadata to GHL contact/opportunity.
8. Activate workflows at low volume and monitor for 48 hours.

## Acceptance Criteria
- Calls only start for eligible queue rows.
- Every completed call has a recorded disposition in Postgres.
- Every completed call writes a summary note in GHL.
- No duplicate bookings or duplicate attempts for same idempotency key.
- Manual QA of 5 transcripts matches summary quality expectations.
