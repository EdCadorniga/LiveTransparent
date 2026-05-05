# Voice Agent Operations Runbook (V1)

## Purpose
Deploy and operate the outbound voice AI agent safely in the LiveTransparent stack.

## Pre-deploy checks
- Confirm required env vars exist in Coolify for n8n.
- Apply `postgres/voice_agent_schema.sql` to reporting Postgres.
- Confirm Cameron calendar id is correct in `GHL_CALENDAR_ID_CAMERON`.
- Verify DNC source of truth and queue feed workflow are active.

## Deployment sequence
1. Import `n8n-workflow/lt-voice-agent-v1.json` as inactive.
2. Bind Postgres, GHL, and HTTP credentials.
3. Validate test queue record in Postgres.
4. Run one manual execution against a sandbox contact.
5. Confirm:
   - queue item picked,
   - provider call start request sent,
   - GHL note written.
6. Activate workflow with low cadence.

## Callback workflow requirement
Create a separate inbound callback workflow from the voice provider to:
- capture transcript + recording links,
- evaluate qualification/handoff flags,
- fetch free slots from GHL calendar,
- create appointment,
- write final summary note and follow-up task.

## Required observability
- Dashboard query for daily dispositions and booking rate.
- Alert on:
  - repeated provider failures,
  - booking error spikes,
  - transcript write failures,
  - queue backlog growth.

## Safety controls
- Hard stop when call is outside allowed PST window.
- Hard stop on DNC or invalid phone.
- No direct legal/compliance answers.
- Human handoff on complex objection/compliance path.

## Daily QA checklist
- Sample 5 completed call summaries.
- Open 2 full transcripts and verify summary accuracy.
- Verify at least 1 booked call has correct calendar event.
- Verify handoff-required calls created human tasks in GHL.
