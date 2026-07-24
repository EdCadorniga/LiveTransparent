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
- `dialer-workflow-clean.mjs` - current outbound dialer source of truth.
- `dialer-workflow-clean.json` - current inspectable JSON export for the dialer.
- `workflow-1ogCy-DIALER-EXPORT.json` - legacy outbound dialer export retained for archive/reference.
- `n8n-workflow/lt-voice-agent-vapi-callback-v1-merged.json` - canonical merged callback/tool workflow export.
- `runbooks/Voice_Agent_Operations_Runbook.md` - production deployment and operations checks, including the 8-minute call limit.
- `runbooks/Vapi_Outbound_Call_Training.md` - training guide for how the dialer and callback workflows work with Vapi.
- `ARCHIVE.md` - archive index for retired voice workflows and exports.

## Runtime assumptions
- GHL remains the CRM system of record.
- n8n orchestrates queueing, callback/tool routing, and CRM sync.
- n8n `2.31.5` is the target runtime. Recurring workflows use native `Schedule Trigger` nodes; external cron jobs are not part of the production design.
- The 2026-07-23 hardening pass added callback timer pruning, authenticated queue enqueue requests, Apollo phone-request failure metrics, and repaired timeout-reaper Slack-summary wiring.
- Voice provider and LLM provider are env-driven and swappable.
- Transcript system of record is Postgres; GHL stores summary + link.
- Production workflow IDs:
  - `fx4UvKUWbqJEY3LK` - canonical merged callback/tool router on `/webhook/lt-voice-agent-vapi-callback`
  - `r7UjWLndmc6EqEUW` - canonical outbound dialer
  - `bYk1Ai6MJLyhTsDZ` - canonical intake poller
  - `KsBMFcz1YpBGrjDW` - unpublished dequeue helper; not an automatic call-start path
  - `XzcpOBi9YcIhJPck` - authenticated queue enqueue webhook at `/webhook/voice-queue-enqueue`
- GHL config:
  - `GHL_PIT` - auth token
  - `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- Queue enqueue callers must send `X-LT-Voice-Queue-Secret` from `VOICE_QUEUE_ENQUEUE_SECRET`.
- Archived workflows:
  - `R1gTdLkbjJUPAr6u` - archived validation copy
  - `cd3Gv3llKB8XOUgg`, `pMMPwm2RLjuYqjZ7`, `Qdl2a9KMJnIw745d` - archived tests
