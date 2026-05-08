# LiveTransparent Voice Agent V1 (Phase 2 Vapi Production)

This package documents the current production Vapi voice-agent implementation and the historical V1 scaffold that preceded it.

## Objectives
- Run outbound calls from a controlled queue.
- Handle Vapi end-of-call webhooks and live tool calls through a single merged callback workflow.
- Persist call outcomes, DNC updates, and sales alerts into GHL/Postgres/Slack.
- Keep the production workflow pair explicit so older exports are not mistaken for live assets.

## Components
- `Voice_Agent_V1_Implementation_Spec.md` - historical V1 implementation spec retained for reference.
- `Call_Agent_Prompt_Policy.md` - historical V1 prompt policy retained for reference.
- `postgres/voice_agent_schema.sql` - queue/attempt/transcript schema.
- `n8n-workflow/lt-voice-agent-v1.json` - legacy outbound dialer export.
- `n8n-workflow/lt-voice-agent-vapi-callback-v1-merged.json` - canonical merged callback/tool workflow export.
- `runbooks/Voice_Agent_Operations_Runbook.md` - production deployment and operations checks, including the 5-minute call limit.
- `runbooks/Vapi_Outbound_Call_Training.md` - training guide for how the dialer and callback workflows work with Vapi.
- `ARCHIVE.md` - archive index for retired voice workflows and exports.

## Runtime assumptions
- GHL remains the CRM system of record.
- n8n orchestrates queueing, callback/tool routing, and CRM sync.
- Voice provider and LLM provider are env-driven and swappable.
- Transcript system of record is Postgres; GHL stores summary + link.
- Production workflow IDs:
  - `fx4UvKUWbqJEY3LK` - canonical merged callback/tool router on `/webhook/voice-callback`
  - `1ogCy9ScVjtF0Cqf` - canonical outbound dialer
- GHL config:
  - `GHL_PIT` - auth token
  - `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- Archived workflows:
  - `R1gTdLkbjJUPAr6u` - archived validation copy
  - `cd3Gv3llKB8XOUgg`, `pMMPwm2RLjuYqjZ7`, `Qdl2a9KMJnIw745d` - archived tests
