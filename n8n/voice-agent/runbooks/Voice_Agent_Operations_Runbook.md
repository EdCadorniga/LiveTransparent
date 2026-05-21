# Voice Agent Operations Runbook (Phase 2 Vapi Production)

## Purpose
Deploy and operate the production Vapi voice agent safely in the LiveTransparent stack.

## Scope
- Production workflow pair:
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`)
  - `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)
- Archived / non-production workflows:
  - `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`)
  - `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`)
  - `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`)
  - `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`)

## Pre-deploy checks
- Confirm required env vars exist in Coolify for n8n.
- Apply `postgres/voice_agent_schema.sql` to reporting Postgres.
- Confirm `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV` is present in root `.env`.
- Confirm `GHL_API_KEY` aliases `GHL_PIT` in root `.env` and that the Codex session has been restarted after any PIT rotation.
- Verify the canonical merged callback URL is still `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`.
- Verify DNC source of truth and queue feed workflow are active.
- Confirm archived workflows are not active in n8n.

## Deployment sequence
1. Restore or update `n8n-workflow/lt-voice-agent-vapi-callback-v1-merged.json` for the canonical callback/tool router if a rebuild is required.
2. Restore or update `n8n-workflow/lt-voice-agent-v1.json` for the canonical outbound dialer if a rebuild is required.
3. Bind Postgres, GHL, Slack, and HTTP credentials.
4. Validate test queue record in Postgres.
5. Run one manual execution against a sandbox contact.
6. Confirm:
   - queue item picked,
   - queue item locked and claimed atomically,
   - provider call start request sent,
   - GHL note written.
7. Activate workflows with low cadence.
8. Enforce the hard 8-minute limit on the two active assistants with a 7:45 background warning and an 8:00 force-end.

## Callback workflow requirement
The production callback workflow is merged:
- captures end-of-call events and live tool calls on the same webhook,
- routes by `tool.name`,
- writes dispositions, DNC updates, and sales alerts,
- logs attempts and contact notes.

Do not reintroduce the older split callback workflow into production.

## Required observability
- Dashboard query for daily dispositions, tool usage, and call logging completeness.
- Alert on:
  - repeated provider failures,
  - callback parse or routing failures,
  - tool execution failures,
  - queue backlog growth.

## Safety controls
- Hard stop when call is outside allowed PST window.
- Hard stop on DNC or invalid phone.
- No direct legal/compliance answers.
- Human handoff on complex objection/compliance path if that behavior is enabled later.

## Daily QA checklist
- Sample 5 completed call summaries.
- Verify tool-call payloads are routed to the correct branch.
- Verify completed calls create one `voice_call_attempt` row each.
- Verify queue rows are locked on claim and are only eligible again after the stale lock window.
- Verify archived workflows remain archived and are not active.
- Verify the vapi\_\* tags are applied correctly on a sample of completed calls.
- Spot-check that failed/null disposition calls did not receive auto tags (expected).
