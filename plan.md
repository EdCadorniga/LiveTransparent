# Vapi + n8n Outbound Voice Agent Plan — Phase 2 (2026-05-14)

## Goal
Connect n8n to Vapi with production-ready tool calling:
- Vapi can call out to contacts via n8n queue.
- 4 agent tools close the loop: disposition, DNC, sales alert, call logging.
- All routing through single merged webhook.

## Canonical Production State
- Production workflow pair:
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`1ogCy9ScVjtF0Cqf`)
  - `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)
- Archived / non-production workflows:
  - `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) — archived in n8n after validation
  - `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`) — archived in n8n
  - `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`) — archived in n8n
  - `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`) — archived in n8n

## What's Already Done
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`1ogCy9ScVjtF0Cqf`) — production dialer, polls queue, starts Vapi call, logs GHL note
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — production merged callback/tool router, receives end-of-call webhook + all 4 tool calls, routes by `tool.name`
- `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) — archived validation copy, not used in production
- Phone number: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`)
- Assistant ID: `3f9bbfd2-efa6-4381-81e6-26f2452d28f1`
- Postgres schema: `voice_call_queue`, `voice_call_attempt`, `voice_call_transcript_turn`
- GHL location ID: `Zwz4relUXVPxx8uohnjV`

## Phase 2 Work

### 1. Set VAPI_PHONE_NUMBER_ID in .env ✅
`VAPI_PHONE_NUMBER_ID=bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`

### 2. Merged callback workflow ✅ (2026-05-07)
Single workflow at path `/webhook/lt-voice-agent-vapi-callback` handles:
- `POST` — Vapi end-of-call events
- `POST` — Vapi tool calls during live call (routed by `tool.name`)

Tool routing:
- `update_lead_status` → Postgres UPDATE queue status + GHL tags (`AI Call Attempted`)
- `add_to_dnc` → Postgres UPDATE dnc=true + GHL DNC tag (`do_not_call`)
- `log_call_outcome` → Postgres INSERT/UPDATE `voice_call_attempt`
- `notify_sales` → HTTP POST to Slack `#leads`

Webhook URL for all Vapi callbacks + tools:
```
https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback
```

### 3. Outbound dialer — first_name fix ✅
Queue query now fetches `first_name` (was missing, causing Vapi variable to always be empty)

### 4. voice_call_queue schema — first_name column ✅
```sql
ALTER TABLE voice_call_queue ADD COLUMN first_name text;
```

### 5. GHL config — location ID ✅
`GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`

### 6. GHL auth alias — workflow compatibility ✅
`GHL_API_KEY` now aliases `GHL_PIT` in root `.env` so the voice workflow nodes that still reference `GHL_API_KEY` continue to work.

### 7. Voice GHL smoke test ✅
Using test contact `WWuQ3TgiaxFs97lSHWSn`:
- `AI Call Attempted` tag added
- `do_not_call` tag added
- contact note write succeeded
- tag readback confirmed

## Vapi Dashboard Tool Config (manual step)
Register 4 tools in Vapi dashboard, each pointing to:
```
https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback
```
| Tool Name | Parameters |
|-----------|------------|
| `update_lead_status` | `ghl_contact_id`, `disposition`, `notes`, `followUpAt` |
| `add_to_dnc` | `ghl_contact_id`, `reason` |
| `log_call_outcome` | `call_id`, `disposition`, `notes`, `followUpAt`, `handoff_required` |
| `notify_sales` | `lead_name`, `company`, `disposition`, `notes`, `contact_id` |

Also set end-of-call webhook → same URL.

## Activation Status
| Workflow | Status | Notes |
|----------|--------|-------|
| `fx4UvKUWbqJEY3LK` — Callback + Tools | Published in production | Canonical merged callback/tool router |
| `1ogCy9ScVjtF0Cqf` — Outbound Dialer | Published in production | Canonical queue dialer; last updated 2026-05-13 (newest-first dequeue, pipeline_stage tracking) |
| `R1gTdLkbjJUPAr6u` — Callback + Tools Copy | Archived in n8n | Validation copy only; do not use in production |
| `cd3Gv3llKB8XOUgg` — IF Test | Archived in n8n | Archived test workflow |
| `pMMPwm2RLjuYqjZ7` — Switch Test | Archived in n8n | Archived test workflow |
| `Qdl2a9KMJnIw745d` — Switch Branch Test | Archived in n8n | Archived test workflow |

## Acceptance Criteria
- [x] Outbound calls start for queue rows with `status=pending`, `dnc=false`, `attempt_count < max_attempts` — Cron polls every 5min, fetches & locks next candidate, starts Vapi call via HTTP POST
- [x] Vapi calls `update_lead_status` after qualifying/hanging up — tool wired in callback workflow, published
- [x] Vapi calls `add_to_dnc` when prospect opts out — tool wired in callback workflow, published
- [x] Vapi calls `log_call_outcome` with disposition + notes + follow-up — tool upserts `voice_call_attempt` row, published
- [x] Vapi calls `notify_sales` with lead name + summary to `#leads` — tool wired in callback workflow, published
- [x] Each completed call has a row in `voice_call_attempt` — via `log_call_outcome` tool
- [x] GHL contact note written for every call — dialer writes note on call start
- [x] Voice workflows use the shared `GHL_LOCATION_ID` where location-scoped reads are needed
- [x] GHL tag and note paths smoke-tested against a test contact `WWuQ3TgiaxFs97lSHWSn`
- [x] Archived workflows remain inactive — all 4 non-production workflows archived in n8n

## Remaining Work (Phase 2 Hardening)
- [ ] Move remaining secrets out of workflow `Config` nodes into n8n credentials or env-backed config
- [ ] In Vapi dashboard, verify 4 tools and end-of-call webhook still pointed at `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`

## Vapi Reporting (Phase 3)

### 1. Vapi Tagging
- Auto-tag GHL contacts based on Vapi call outcomes (e.g., `AI Call - Voicemail`, `AI Call - Connected`, `AI Call - DNC`, `AI Call - Busy`, `AI Call - No Answer`)
- Apply tags in the callback workflow (`fx4UvKUWbqJEY3LK`) via the `update_lead_status` tool or a new dedicated tag node based on `endedReason` from Vapi end-of-call events
- Enable segmenting contacts by call outcome for reporting and follow-up campaigns

### 2. Vapi Stage in Pipeline
- Add a Vapi-specific pipeline stage (e.g., `AI Outbound` or `Vapi Dialed`) between existing stages in the sales pipeline
- When a Vapi call reaches specific dispositions (e.g., interested, follow-up needed), move the contact's opportunity to the Vapi stage automatically via the callback workflow
- Enables visual tracking of Vapi-sourced leads through the pipeline

### 3. Cross-Reporting for Vapi and Call Outcomes
- New Postgres reporting table (e.g., `report_vapi_daily_summary`) aggregating Vapi call metrics by day:
  - Total calls, calls by outcome (voicemail, connected, busy, no-answer, silence, failed)
  - Contact-to-opportunity conversion rate for Vapi-sourced leads
  - Average call duration by outcome
- Cross-reference Vapi call data with `voice_call_attempt` dispositions and downstream GHL opportunity stages
- Surface KPI panel in the Executive Report showing Vapi performance alongside other channels
