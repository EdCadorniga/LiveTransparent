# Vapi + n8n Outbound Voice Agent — Implementation Plan

## Goal
Connect n8n to Vapi with production-ready tool calling: outbound calls via queue, 4 agent tools for disposition/DNC/sales-alert/call-logging, all routing through a single merged webhook.

## Phase 2 Hardening (Remaining)

- [ ] **Move secrets out of Config nodes** — migrate remaining secrets (SimpleTexting API tokens, GHL keys, webhook secrets) from workflow `Config` nodes into n8n credentials or env-backed config. Voice HTTP nodes prefer reading from Config when env access is blocked.
- [ ] **Verify Vapi dashboard config** — confirm 4 tools and end-of-call webhook still point at `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`

## Phase 3 — Vapi Reporting

### 1. Auto-Tagging Pipeline
- Tag GHL contacts by call outcome in callback workflow (`fx4UvKUWbqJEY3LK`) via `update_lead_status` or a dedicated node based on `endedReason` from Vapi end-of-call events
- Tags: `vapi_voicemail`, `vapi_connected`, `vapi_busy`, `vapi_no_answer`, etc. (see tag inventory in AGENTS.md — partially done, refine)

### 2. Vapi Pipeline Stage
- [ ] Add a `Vapi Dialed` pipeline stage between existing stages
- [ ] Auto-move opportunities to Vapi stage on specific dispositions via callback workflow

### 3. Cross-Reporting for Vapi
- [ ] New Postgres reporting table `report_vapi_daily_summary` aggregating call metrics by day:
  - total calls, calls by outcome, contact-to-opportunity conversion, avg duration
- [ ] Cross-reference Vapi call data with `voice_call_attempt` dispositions and GHL opportunity stages
- [ ] Surface Vapi KPI panel in Executive Report alongside other channels

## Acceptance Criteria (remaining)
- [x] Outbound calls start for queue rows with `status=pending`, `dnc=false`, `attempt_count < max_attempts` — Cron polls + fetches + locks + starts Vapi call
- [x] `update_lead_status` called after qualifying/hang-up — wired in callback workflow
- [x] `add_to_dnc` called when prospect opts out — wired in callback workflow
- [x] `log_call_outcome` upserts `voice_call_attempt` — wired in callback workflow
- [x] `notify_sales` sends lead name + summary to `#leads` — wired in callback workflow
- [x] GHL contact note written for every call — dialer writes note on call start
- [x] Voice workflows use shared `GHL_LOCATION_ID`
- [x] GHL tag and note paths smoke-tested against test contact
- [ ] Move secrets to credentials (Phase 2 hardening)
- [ ] Vapi auto-tagging by outcome (Phase 3)
- [ ] Vapi pipeline stage + auto-move (Phase 3)
- [ ] Vapi cross-report + dashboard panel (Phase 3)
