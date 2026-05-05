# Voice Agent V1 Implementation Spec

## Objective
Implement an outbound cold-call AI agent that introduces itself as a LiveTransparent representative, answers basic company questions, and books qualified prospects directly with Cameron.

## Locked Decisions
- Channel: Voice calls only.
- Runtime: External AI runtime orchestrated by n8n.
- Queue model: Task Queue Dial.
- Booking mode: Offer slots and book directly.
- Qualification gate: Intent + fit.
- Handoff: Compliance/complexity or explicit human request.
- Transcript sink: Postgres full transcript + GHL summary note.
- Call window: Mon-Fri business hours in PST.

## Core Flow
1. Pull next callable item from queue (`pending`, within policy window, not DNC, attempts remaining).
2. Place voice call through provider.
3. Run policy-constrained AI conversation.
4. If qualified, fetch available slots and offer options.
5. On prospect confirmation, create appointment.
6. Persist transcript, call metadata, and disposition.
7. Upsert GHL note/task/opportunity updates.
8. Mark queue item outcome and schedule retry/follow-up if needed.

## Public Contracts

### Queue payload
- `queue_id` (uuid)
- `contact_id` (ghl contact id)
- `phone_e164`
- `lead_timezone` (optional)
- `campaign_id`
- `max_attempts`
- `attempt_count`
- `last_attempt_at`
- `next_attempt_at`
- `dnc` (bool)
- `status` (`pending|in_progress|completed|failed`)

### Call outcome
- `call_id`
- `contact_id`
- `disposition` (`no_answer|voicemail|connected|qualified_booked|qualified_not_booked|not_qualified|handoff_required|failed`)
- `qualified_intent_fit` (bool)
- `booking_attempted` (bool)
- `booking_result` (`success|slot_conflict|declined|error|not_attempted`)
- `handoff_required` (bool)
- `handoff_reason`

### Transcript record
- `call_id`
- `turn_index`
- `speaker` (`agent|prospect|system`)
- `utterance`
- `timestamp_utc`

## GHL integration actions
- Read contact and existing opportunity context.
- Create contact note with summary, disposition, next step, transcript link.
- Create follow-up task when not booked or when handoff required.
- Update tags for call outcomes:
  - `AI Call Attempted`
  - `AI Qualified`
  - `AI Booked`
  - `AI Human Handoff`

## Safety and guardrails
- Do not provide legal/regulatory advice.
- Do not claim guaranteed outcomes or pricing commitments.
- On complex objections or compliance topics, escalate to human.
- Respect DNC flags and calling window policy.
- Enforce idempotency key per attempt to avoid duplicate booking.

## Required environment values
- `VOICE_PROVIDER_BASE_URL`
- `VOICE_PROVIDER_API_KEY`
- `VOICE_FROM_NUMBER`
- `OPENAI_API_KEY` (or alternate LLM key)
- `GHL_API_KEY`
- `GHL_LOCATION_ID`
- `GHL_CALENDAR_ID_CAMERON`
- `VOICE_CALL_WINDOW_PST_START` (e.g. `09:00`)
- `VOICE_CALL_WINDOW_PST_END` (e.g. `17:00`)
