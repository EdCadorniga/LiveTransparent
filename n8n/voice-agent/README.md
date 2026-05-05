# GHL Voice Agent V1 (Outbound Cold Call + Direct Booking)

This package defines the v1 implementation scaffold for a customer-facing outbound voice AI agent.

## Objectives
- Run outbound calls from a controlled queue.
- Answer basic LiveTransparent company FAQs.
- Offer Cameron calendar slots and book directly.
- Persist full transcript and call metadata.
- Sync structured call outcomes into GHL.

## Components
- `Voice_Agent_V1_Implementation_Spec.md` - decision-complete implementation spec.
- `Call_Agent_Prompt_Policy.md` - system prompt and runtime guardrails.
- `postgres/voice_agent_schema.sql` - queue/transcript/attempt schema.
- `n8n-workflow/lt-voice-agent-v1.json` - n8n workflow skeleton (import base).
- `runbooks/Voice_Agent_Operations_Runbook.md` - deployment and operations checks.

## Runtime assumptions
- GHL remains the CRM system of record.
- n8n orchestrates queueing, policy checks, booking, and sync.
- Voice provider and LLM provider are env-driven and swappable.
- Transcript system of record is Postgres; GHL stores summary + link.
