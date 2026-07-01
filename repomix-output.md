This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, plan.md, Project Status and Next Steps.md, Project Specifications.md, Vapi_Brand_Campaign.docx, Vapi_Dispensary_Campaign.docx
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
AGENTS.md
plan.md
Project Specifications.md
Project Status and Next Steps.md
Vapi_Brand_Campaign.docx
Vapi_Dispensary_Campaign.docx
```

# Files

## File: AGENTS.md
```markdown
# LiveTransparent Agent Notes

## IMPORTANT — Read This First

Analyze the attached `repomix-output.md` file. It contains the core system architecture, code blueprints, and operational roadmaps for my LiveTransparent automation environment. Review my `AGENTS.md` and custom script setups (like `fix_intake_poller.js`) to understand how my infrastructure is organized. When I ask you to write code modifications, database queries, or new workflow nodes, ensure your suggestions strictly match this architecture and stay within my token budget.

**LLM context-loading order:**
1. `repomix-output.md` — start here for architecture, blueprints, and roadmaps
2. `AGENTS.md` (this file) — short operating guide
3. `Project Status and Next Steps.md` — current priorities and live-state
4. `Project Specifications.md` — system boundaries, guardrails, contracts
5. `plan.md` + sub-plans (`emerald-email-campaign/plan.md`, etc.) — active work plan
6. Custom scripts (`fix_intake_poller.js`, etc.) — infrastructure specifics
7. All other repo files — only when a task requires fine detail

## Canonical Status

- Use [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md) for current priorities and live-state details.
- This file is the short operating guide: keep it current, but avoid duplicating long planning material here.

## Environment

- Deployed via Coolify on a VPS.
- Public hosts: `automations.livetransparent.com` for n8n and `reports.livetransparent.com` for the report host.
- Prefer Coolify internal service-to-service calls when possible.
- n8n target version: `2.25.3` (upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue).
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

## Working Rules

- Check the live state before and after every mutation.
- Fetch first, patch second.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Use `Config` nodes only when env or credential access is blocked.

## Tooling

- Prefer `n8n-lt` MCP or direct API calls before browser workflows.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.
- Codex config: `C:\Users\edmon\.codex\config.toml`.
- **Avoid `n8n-lt` `updateNodeParameters` for Set v3.4 nodes.** It silently corrupts `assignments.assignments` from `[{...}]` to `{item: [{...}]}` and stringifies booleans (`"true"` instead of `true`) and `options: {}` to `""`. The MCP response reports warnings but the corruption persists AND auto-publishes. Use `setNodeParameter` for single-path edits on Set v3.4 nodes instead of `updateNodeParameters`. If `setNodeParameter` also fails, **use direct n8n REST** (`PUT /api/v1/workflows/{id}` with `N8N_API_KEY_LT` from `.env` root) but note that PUT auto-publishes and validates all node credentials, which may fail if credential IDs aren't embedded in node JSON. For Code nodes, `updateNodeParameters` and `setNodeParameter` are both safe. Verify with `GET /api/v1/workflows/{id}` checking both `nodes` (draft) and `activeVersion.nodes` (live). Known-good Config shape: `{"mode": "manual", "assignments": {"assignments": [{id, name, value}, ...]}}` — no `includeOtherFields` or `options` keys required.

## Known Issues & Fixes (2026-07-01)

### LT - LinkedIn Connection State Sync (`ceaKnz6E3onQrZpt`)
- **Issue**: Code node timed out at 300s scanning GHL contacts for LinkedIn profiles. Caused by a config field bug (`cfg.maxPages` used instead of `cfg.maxContacts`) and no HTTP timeout on Unipile API calls.
- **Fix**: Published 2026-07-01. Changed `cfg.maxPages → cfg.maxContacts`, capped `maxPages` at 10, `maxContacts` at 50, added `timeout: 15000` to `apiRequest` HTTP calls.
- **Code node note**: The `maxPages` and `maxContacts` are capped in the Code node itself (not just Config), so adjusting Config values beyond caps has no effect.

### GHL Apollo Phone Enrichment Intake V3 (`WuxgTa0EEL1mb2SA`)
- **Issue**: 3 webhook errors on 2026-06-30 with "Missing contactId in webhook payload". Root cause: the Set v3.4 Config node sometimes drops the webhook payload when `includeOtherFields` is not set, starving the Code node of `contactId`.
- **Fix**: Code node now falls back to reading directly from `$item(0).$node['Webhook']?.json` if the primary input lacks contactId. Fix was already live in the active version as of 2026-07-01 audit.

### LT - GA4 Daily Ingest (`6pCSGzFmrMDFL5Yq`)
- **Issue**: Google Analytics OAuth2 credential expired (`EAUTH`). Caused hourly failures for 24+ hours.
- **Fix**: Re-authorized OAuth2 credential on 2026-07-01. Verified with manual execution (success, ~11s).

### Vapi Workflow Audit & Fixes (2026-07-01)
- **Scope**: All 6 Vapi voice workflows reviewed and patched.
- **LT - Voice Queue Vapi Intake Poller** (`bYk1Ai6MJLyhTsDZ`): Fixed critical bug — `Classify Contacts` Code node called undefined `removeTag()`, would crash on contacts with `vapi_voicemail`/`vapi_qualified` tags. Added real `removeTag()` function that calls GHL `DELETE /contacts/{id}/tags`.
- **LT - Voice Agent V1 Vapi Callback + Tools** (`fx4UvKUWbqJEY3LK`):
  - Converted 4 Postgres nodes from string-interpolated SQL (`'{{ $json.field }}'`) to parameterized queries (`$1`, `$2` with `queryReplacement`).
  - Added Config node (Set v3.4) with all secrets (GHL API key, Vapi API key, Slack webhook, tool secret, dequeue URL). Wired into flow between Webhook and Code - Detect Tool vs Callback.
  - Updated 8 nodes (GHL HTTP calls, Vapi background warning, Slack notification, GHL tool executor, dequeue trigger) to reference `$("Config").item.json.*` instead of hardcoded values.
- **LT - Voice Queue Enqueue** (`XzcpOBi9YcIhJPck`): Converted SQL-building Code node + string-interpolated Postgres node to parameterized query pattern.
- **LT - Voice Dequeue Next** (`KsBMFcz1YpBGrjDW`): Fixed SQL with doubled single quotes (`''pending''`). Added phone validation to Switch so empty/invalid phones don't reach Vapi.
- **LT - Voice Agent V1 Outbound Dialer (Vapi)** (`r7UjWLndmc6EqEUW`): Extended cron from `*/2 14-21` to `*/2 14-22` UTC so CST winter time (UTC-6) doesn't miss the 9am CT hour.
- **Config node warning note**: The `SET_CREDENTIAL_FIELD` warnings on Config nodes are advisory only — n8n lint flags the pattern but does not block execution. Formal n8n credentials are not required.

## Live Voice System

| Item | Value |
|------|-------|
| Phone | `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`) |
| Assistant | `3f9bbfd2-efa6-4381-81e6-26f2452d28f1` |
| Callback webhook | `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback` |
| Key env | `VAPI_PHONE_NUMBER_ID`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`, `GHL_API_KEY` / `GHL_PIT` |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Campaign Contact Classifier | `IduCoT5YOs0g2faT` | Manual (created 2026-07-01) |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Paused 2026-06-05 |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Paused 2026-06-05 |
| LT - Voice Queue Vapi Intake Poller | `bYk1Ai6MJLyhTsDZ` | Paused 2026-06-05 |
| LT - Voice Queue Enqueue | `XzcpOBi9YcIhJPck` | Paused 2026-06-05 |
| LT - Voice Dequeue Next | `KsBMFcz1YpBGrjDW` | Paused 2026-06-05 |
| LT - Call Outcome Ingest | `PUCfTZBANSPcgS0c` | Paused 2026-06-05 |
| LT - Apollo Queued Timeout Reaper | `RL5ZyUoshSPbmVA1` | Active (hourly) |

### Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

### Vapi Campaign Tags (to create)

- `vapi_campaign_brand`
- `vapi_campaign_dispensary`
- `vapi_already_called`

## Vapi Campaign Rollout Plan (2026-07-01)

Two new voice campaigns deploying alongside the existing V1 paused infrastructure. See `plan.md` for full step-by-step.

### Campaign Definitions

| Campaign | Persona | Target | Goal | Vapi Assistant ID | Campaign Tag |
|----------|---------|--------|------|-------------------|--------------|
| Brand Outreach | Alex | Brand marketing/growth leads | Book strategy call for Dispensary Attribution Network | TBD (create) | `vapi_campaign_brand` |
| Dispensary Recruitment | Jordan | Dispensary owners/managers | Book call or email partner agreement | TBD (create) | `vapi_campaign_dispensary` |

### Prep Completed (2026-07-01)
- **Queue cleanup**: 1,005 stale V1 `pending` rows → `failed`
- **Pool audit**: 23,726 GHL contacts; 1,045 unique already called; ~16k Emerald pool
- **Classifier workflow**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) created — queries voice_call_attempt + GHL contacts, classifies by Emerald tags
- **Call history**: 1,711 total attempts across 1,045 contacts (voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18)

### Campaign Tags (to create)
- `vapi_campaign_brand`
- `vapi_campaign_dispensary`
- `vapi_already_called`

### Critical Infrastructure Changes Needed
1. Dialer must map `campaign_id → assistantId` (currently hardcoded to V1 assistant)
2. Intake poller must seed from campaign-specific tags (currently only `vapi_queue`)
3. Enqueue must dedup against existing queue rows by `contact_id`
4. Callback + Tools must handle per-campaign structured output schemas

### Apollo Phone Enrichment Status (custom field `rgYJ7UqoznGoe3WeUAtH`)

- `enriched` — terminal (good)
- `no_match` — terminal (no Apollo hit)
- `error` — terminal (API error)
- `queued` — transient (intake sent request to Apollo, awaiting callback)
- `callback_timeout` — terminal (set by `LT - Apollo Queued Timeout Reaper` when `queued` is older than 24h or queued_at is missing). Backstop for the V4 callback URL not delivering; root cause still needs Apollo-side investigation.

### Custom field IDs (GHL)

- `Apollo Phone Enrichment Status` = `rgYJ7UqoznGoe3WeUAtH` (SINGLE_OPTIONS)
- `Apollo Phone Enrichment Queued At` = `NgC3xGTh0laQ9ArTnude` (DATE)
- `Enrich Phone via Apollo` = `gdJDuZelIxEBE6n9i5Q6` (SINGLE_OPTIONS: Yes/No)

## Reporting System

| Workflow | ID | Status |
|----------|----|--------|
| GHL Daily Leads Ingest | `osIJOgBmWITF5Yuv` | Active |
| GHL Daily Sales Ingest | `aYT5oHcgmBALzHy5` | Active |
| GHL Daily Calls Ingest | `SqNQ0BYaTdcqyt1l` | Active (4hr schedule) |
| GHL Daily Appointments Ingest | `yWZVSqEcjTbMT3kG` | Active |
| GHL Daily Social Ingest | `QZoqCaTwDhbym80O` | Active |
| GA4 Daily Ingest | `6pCSGzFmrMDFL5Yq` | Active |
| GA4 Traffic Rollup Bridge | `0P2AZcQYWYZjXbRi` | Active |
| GSC Daily Ingest | `xHqmCC1vOeZ11gCd` | Active |
| GSC Rollup Bridge | `fOVBHwti9rC3qrLV` | Active |
| Report Attribution Bridge | `Y0TU7Il71JswxOBp` | Active |
| Report Daily Rollups | `EUeOiRttoVLQ9zF9` | Active |
| Report Executive Summary API | `Bukc0mgOD2r7V6ED` | Active |
| Report QA and Alerts | `M5mXcDTFSko6EdHb` | Active |
| Report Config Sync | `aomO3Z4AXJIgEvvN` | Active |
| Report Publish Refresh | `3gXztCnBEN6sGINb` | Active |
| Report Postgres Bootstrap Apply | `3XHThUiUSNa4sTb9` | Active |

### Reporting Notes

- GA4, GHL, and GSC ingestion are all live and active.
- GSC ingest and rollup bridge are active daily (verified from execution data).
- Report Pipeline Velocity (`iFfwh0jpYUZoDhDR`) is active.
- Meta Ads API access is validated against `act_2186975138800404` but spend ingest is still deferred.
- Keep report validation end-to-end: ingest -> attribution bridge -> daily rollups -> executive summary.

## Other Live Systems

- SimpleTexting: Send, delivery, inbound reply, and unsubscribe webhooks are active.
- Unipile/LinkedIn: All pipeline workflows are active and verified live.
- LinkedIn pipeline status (verified 2026-07-01): Sync seeds state table, Dispatcher sends connection requests, DM Sequence sends follow-ups with auto-connected-sync, daily limit enforcement, and reply detection. LinkedIn Connection State Sync timeout fix published 2026-07-01.
- LinkedIn GHL token: `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28` (from root `.env`). The alternate token `pit-2d2ed8c3-...` is broken (401), do not use.
- LinkedIn Code node regex pattern: always use `[/]` (character class) instead of `\/` in regex literals to avoid SDK JSON serialization corruption.
- GHL warm intake/routing, Apollo enrichment, and Emerald/Cold outreach are active.

## Outreach Notes

- LinkedIn invite copy is sourced from `outreach_messages.v2.docx`.
- LinkedIn DM copy is sourced from `outreach_messages.v2.docx`.
- LinkedIn DM timing is currently 0, 3, 4, 3, 4 days between sends after the first message clock starts.
- Active LinkedIn conversations are marked in `linkedin_connection_state` via `payload_json.dm_conversation_status = 'active'`.
- For LinkedIn supply, prefer seeding `linkedin_connection_state` from the working GHL contacts list and keep `linkedin_connected` rows out of the queue entirely.
- If you restart the session, re-check the live n8n executions for the sync, dispatcher, and DM workflows before saying the pipeline is healthy.
- SimpleTexting SMS campaign work is now staged in repo workflow exports, using `outreach_messages.docx` as the SMS source of truth.
- SMS campaign requirements:
  - tag each SMS send so the same person is not messaged twice
  - keep send state and response state in the same canonical table or a tightly controlled pair of tables
  - make sure inbound replies stop future sends and notify `#lead`
  - preserve opt-out handling and unsubscribe tagging
  - keep batches controlled until the pool filter and reply path are verified in live n8n

## Key Files

- `repomix-output.md`
- `.env`
- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/`
- `postgres/reporting-bootstrap.sql`
- `n8n/docker-compose.yml`
- `n8n/voice-agent/`
- `n8n/workflows/lt-linkedin-dm-sequence.ts`
- `n8n/workflows/lt-linkedin-connection-state-sync.ts`
- `n8n/workflows/lt-linkedin-connection-state-upsert.ts`
- `n8n/workflows/lt-linkedin-unipile-new-messages.ts`
- `n8n/workflows/lt-linkedin-connection-acceptance-checker.ts`
- `n8n/workflows/lt-apollo-queued-timeout-reaper.ts` — flips GHL contacts stuck in `Apollo Phone Enrichment Status = queued` past 24h to `callback_timeout` so the Vapi poller unblocks them (workflow ID `RL5ZyUoshSPbmVA1`, hourly)
- `n8n/workflows/lt-simpletexting-send-sms.json`
- `n8n/workflows/lt-simpletexting-pool-dispatcher.json`
- `n8n/workflows/lt-simpletexting-campaign-sequencer.json`
- `n8n/workflows/lt-simpletexting-inbound-reply.json`
- `n8n/workflows/lt-simpletexting-delivery-events.json`
- `n8n/workflows/lt-simpletexting-unsubscribe-events.json`
- `reports/embed/executive/index.html`
- `reports/nginx.conf`
- `Backup of all n8n workflows/`
- `Project Specifications.md`
- `Vapi_Brand_Campaign.docx` — Brand campaign (Alex persona, brand marketing leads)
- `Vapi_Dispensary_Campaign.docx` — Dispensary campaign (Jordan persona, dispensary owners)
- `plan.md` — Vapi Campaign Rollout implementation plan (4 phases)

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate `repomix-output.md` so next-session context is up to date:

1. `. $PROFILE`  
2. `packlive`

This stages key files into `C:\TempRepomixStaging`, runs `npx repomix --style markdown --compress --remove-comments --remove-empty-lines`, and copies the result back to the project root.
```

## File: plan.md
```markdown
# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans voice, reporting, LinkedIn outreach, and the upcoming SimpleTexting SMS campaign.
- For LinkedIn, keep invite copy and DM copy aligned to `outreach_messages.v2.docx`, and keep reply-stop behavior active.
- For SMS, use `outreach_messages.docx` as the campaign source, with batch dispatch, per-send tagging, shared reply-state tracking, and `#lead` notifications on response.
- Keep this file short; the detailed operating status belongs in `Project Status and Next Steps.md`.

## Vapi Campaign Rollout — Implementation Plan (2026-07-01)

### Overview
Two new Vapi voice campaigns targeting the Dispensary Attribution Network:
- **Brand Campaign (Alex)** — sell network participation to cannabis brand marketing leads
- **Dispensary Campaign (Jordan)** — recruit dispensaries as network partner locations

### Completed Prep Work
1. **Queue cleanup**: 1,005 stale V1 pending rows marked `failed`
2. **Contact pool audit**: 23,726 GHL contacts; 1,045 already called via V1; ~16k Emerald contacts are primary pool
3. **Classification signals mapped**: Apollo enrichment fields, Emerald MSO/SSO tags, role tags
4. **`LT - Campaign Contact Classifier`** (`IduCoT5YOs0g2faT`) created with cross-ref + heuristic logic

### Phase 1 — Vapi Assistants
1. Create Brand assistant (Alex persona) with brand-specific system prompt, tools, structured output
2. Create Dispensary assistant (Jordan persona) with dispensary-specific system prompt, tools, structured output
3. Add campaign tags `vapi_campaign_brand` and `vapi_campaign_dispensary` to GHL tag registry
4. Decide: same phone number or second number for separate caller IDs

### Phase 2 — Contact Classification
5. Fix classifier workflow to paginate through all GHL contacts (237 pages at 100/page)
6. Cross-reference each against `voice_call_attempt` (1,045 excluded)
7. Apply `vapi_campaign_brand` or `vapi_campaign_dispensary` GHL tag per classification
8. Tag already-called contacts with `vapi_already_called` for exclusion

### Phase 3 — Infrastructure Modifications
9. Modify outbound dialer: add `campaign_id -> assistantId` mapping in Vapi HTTP body builder
10. Update callback + tools workflow: handle per-campaign structured output schemas
11. Update intake poller: seed from campaign-specific tags instead of single `vapi_queue`
12. Add dedup gate to enqueue: `SELECT contact_id FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending','in_progress')`

### Phase 4 — Reactivation & Testing
13. Seed test queue: 5 Brand + 5 Dispensary contacts manually
14. Reactivate dialer, callback, outcome ingest workflows
15. Run smoke test batch, verify dispositions logged correctly
16. Scale: activate intake poller for campaign tags, roll out in controlled batches
```

## File: Project Specifications.md
```markdown
# Project Specifications: Outbound Voice Agent and Social Outreach

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This file defines boundaries, guardrails, and contracts; it does not repeat the architecture.

## Purpose

Production outbound calling flow for Vapi + n8n + GHL. The agent introduces LiveTransparent, qualifies intent and fit, records call context, and routes outcomes through tool calls.

## Canonical Status

- Current live state and priority order: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

## System Boundaries

- Vapi: realtime voice runtime.
- n8n: queueing, dispatch, callback routing, persistence, CRM sync.
- GHL: contact, opportunity, note, and tag system of record.
- Postgres: call-attempt and transcript metadata store.

## Live Workflows

| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Queue poller, timezone guard, call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | End-of-call webhook plus 4 tool endpoints |

## Social Outreach Scope

### Current Live LinkedIn State

- `LT - GHL LinkedIn Connect Dispatcher (Unipile)` is active and uses the invite copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn DM Sequence (Unipile)` is active and uses the LinkedIn DM copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn Unipile New Messages` is active and marks active conversations when inbound replies arrive.
- LinkedIn DM sends are blocked when `payload_json.dm_conversation_status = 'active'`.

### LinkedIn Timing

- The current LinkedIn DM cadence is `0, 3, 4, 3, 4` days between sends.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.

### SMS Campaign Scope

- `outreach_messages.docx` is the source of truth for SMS copy.
- SMS is implemented as a SimpleTexting campaign stack, not as one-off ad hoc messages.
- The campaign uses a controlled pool dispatcher, a sequencer, and a shared send endpoint.
- The SMS workflow needs per-contact send tracking so each message can be marked as sent once and never repeated.
- The SMS workflow also needs response ingestion so replies update the same canonical state used by the send workflow.
- The SMS workflow should preserve unsubscribe handling and should not send to opted-out contacts.
- Replies should trigger a Slack notification in `#lead` so the team can respond without checking n8n first.
- The preferred model is a shared Postgres state table or a tightly controlled send-state plus response-state pair, but the same contact record must be authoritative for both send and reply logic.

### SMS Missing Steps

1. Normalize SMS copy from `outreach_messages.docx` into a template registry.
2. Define the SMS state schema and idempotency keys.
3. Build the SimpleTexting send workflow with batching controls.
4. Wire inbound reply and delivery webhooks into the same state model.
5. Confirm opt-out / unsubscribe propagation.
6. Run a low-volume smoke test before batch sends.
7. Deploy the staged SMS workflows into live n8n and verify the live webhook routes.

## Queue Contract

Minimum `voice_call_queue` fields:

`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

Injected Vapi variables:

`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

Normalized callback output:

`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration

- Secrets: `GHL_PIT` aliased as `GHL_API_KEY`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- Voice write actions: add `vapi_*` tags per outcome, create contact notes for completed calls

## Guardrails

- Do not call `dnc=true` contacts.
- Respect `attempt_count < max_attempts`.
- Enforce 72h cooldown between attempts.
- Call only Mon-Fri 9am-5pm CT.
- Fall back to GHL contact timezone when queue timezone is missing; use CT 12-2pm safe window if neither is available.
- Keep secrets in env/credentials; do not hardcode them in workflow JSON.
- Preserve n8n graph integrity when editing workflows.
- For social outreach, never send duplicate messages. Every send workflow must check and update shared state before and after send.
- For social outreach, reply-handling workflows must mark the contact as in conversation so follow-up sequences stop.
- For SMS, keep the batch size controlled until reply capture, opt-out propagation, and Slack alerts have all been verified live.

## Callback Tools

- `update_lead_status`: GHL tag plus Postgres disposition update.
- `add_to_dnc`: set `voice_call_queue.dnc=true` and add the GHL DNC tag.
- `log_call_outcome`: upsert `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales`: post lead name and summary into `#leads`.

## Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

## Smoke Test

1. Seed one queue row with a controlled test number.
2. Run the outbound workflow manually.
3. Confirm the Vapi request includes expected metadata.
4. Send a simulated callback payload.
5. Confirm Postgres insert plus GHL note creation.
6. Replay the callback and confirm no duplicate record.

## Social Outreach Smoke Test

1. Verify LinkedIn invite and DM copy are still sourced from `outreach_messages.v2.docx`.
2. Send one LinkedIn test DM and confirm `linkedin_connection_state` advances exactly one step.
3. Simulate an inbound LinkedIn reply and confirm `dm_conversation_status` becomes `active`.
4. Confirm the active conversation is excluded from both LinkedIn DM send paths.
5. Prepare a single SMS test contact and confirm one SMS send is tagged in state.
6. Simulate an inbound SMS reply and confirm the response workflow updates the same canonical state.
7. Confirm unsubscribe handling blocks any future SMS sends for opted-out contacts.
```

## File: Project Status and Next Steps.md
```markdown
# LiveTransparent Project Status and Next Steps

Updated: 2026-07-01 (Vapi Campaign Rollout Prep + Queue Cleanup)

## Source Of Truth

This document is the canonical project status and next-steps reference.
It supersedes the duplicated planning notes in:

- [plan.md](./plan.md)
- [LiveTransparent Report Plan.md](./LiveTransparent%20Report%20Plan.md)

## Current State

- The outbound voice stack is **paused** (since 2026-06-05). Queue cleanup completed 2026-07-01: 1,005 stale `pending` rows marked `failed`. Pool audit complete: 23,726 GHL contacts, 1,045 unique already called via V1, ~16k Emerald pool as primary target for new campaigns.
- **Vapi Campaign Rollout prep completed 2026-07-01**: Two new campaigns documented (Brand/Alex + Dispensary/Jordan), `LT - Campaign Contact Classifier` workflow created (`IduCoT5YOs0g2faT`), classification signals mapped, dedup and cross-reference logic designed. See `plan.md` for full implementation plan.
- The reporting stack is live: GA4 and GHL ingestion are in production, data is flowing into Postgres, and the Executive Report is live in GHL.
- Report rollups, attribution bridge, QA/alerts, and the executive summary API are already running.
- Emerald email-marketing ingest workflows are **PAUSED 2026-06-05** (9 workflows unpublished). See [Plan - VAPI Pause & Queued Goals.md](./Plan%20-%20VAPI%20Pause%20%26%20Queued%20Goals.md) for the full list and resumption playbook. **GHL email sequences still need to be paused manually in the GHL UI** for already-enrolled contacts.
- Emerald intro backfill is staged in live GHL: 500 additional eligible contacts have now been tagged `seq emerald - intro backfill pending`, the live pending queue increased to 3,566, and 1,719 enrolled contacts remain eligible for controlled staging.
- LinkedIn outreach pipeline is fully operational and verified (2026-06-03):
  - `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) seeds `linkedin_connection_state` from GHL contacts with LinkedIn URLs, resolved through Unipile profile lookups. Verified: `scanned: 101, matched: 100, upserted: 100`, schedule `15 */6 * * *`.
  - `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`, replaces archived `S32vc8pjJIBZZHLK`) reads the Postgres queue, sends LinkedIn connection requests via Unipile `POST /users/invite`. Verified: `sent: 10`, schedule `0 15-21 * * 1-5`.
  - `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) polls connected contacts, includes automatic connection detection from Unipile chats, enforces a daily DM limit of 200 with carry-forward, and sends up to 40 DMs per progression step. Verified: `sent: 2`, schedule `0 12-22 * * 1-5`.
  - `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is the webhook receiver for state table upserts (ON CONFLICT with smart merging).
  - `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) marks active conversations to stop DM sequences on reply.
  - Working GHL token: `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28`. The alternate `pit-2d2ed8c3-...` is broken (401).
  - Code node regex safety: always use `[/]` character class instead of `\/` in regex literals to avoid SDK JSON serialization corruption.
  - State table `linkedin_connection_state`: 171 contacts with `status='ready'`, 34 with `status='connected'`, 10 invites sent, 2 DMs delivered.
- SimpleTexting SMS campaign workflow exports are now staged in repo from `outreach_messages.docx`: sender, pool dispatcher, sequencer, inbound reply, delivery events, and unsubscribe events are all represented as separate workflows.
- The SMS stack still needs live deployment and a final GHL pool filter body for the dispatcher, but the message registry, batching shape, reply-stop handling, and Slack `#lead` notification path are now defined in the repo artifacts.
- GSC still needs workflow verification / cleanup.
- Meta Ads API access is validated, but spend ingest is still deferred.

## Voice Workflows

### Live Voice System

- Phone: `+1 (562) 534 1977`
- Vapi Assistant ID: `3f9bbfd2-efa6-4381-81e6-26f2452d28f1`
- Canonical webhook: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`
- Target n8n version: `2.25.3` (upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue)
- Canonical MCP: `n8n-lt`

### Active Workflows

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) — **Manual, created 2026-07-01**, classifies GHL contacts by Brand/Dispensary using Emerald tags, cross-references voice_call_attempt to exclude called contacts
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — **PAUSED 2026-06-05**, was active, merged callback plus 4 tools
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — **PAUSED 2026-06-05**, was active, queue dialer, contact-TZ-aware, 72h cooldown
- `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — **PAUSED 2026-06-05**, was active, polls `vapi_queue`, E.164 bypass
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — **PAUSED 2026-06-05**, was active, webhook enqueue, allows NULL phone
- `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — **PAUSED 2026-06-05**, was active, webhook dequeue then Vapi call
- `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — **PAUSED 2026-06-05**, was active, GHL call webhooks to Postgres and Slack
- **All 6 VAPI workflows are paused.** GHL-side infrastructure (reaper, Apollo V3/V4 callbacks, intake) remains active. Resumption playbook and queued goals documented in [Plan - VAPI Pause & Queued Goals.md](./Plan%20-%20VAPI%20Pause%20%26%20Queued%20Goals.md).
- **Voice queue cleanup (2026-07-01)**: 1,005 stale `pending` queue rows from the V1 pause marked `failed`. Post-cleanup queue: 86 completed, 1,005 failed, 0 pending. The 86 completed represent calls with callback dispositions; the remaining V1 contacts with `attempt_count > 0` but no completion are safe to re-enqueue into new campaigns.
- `LT - Apollo Queued Timeout Reaper` (`RL5ZyUoshSPbmVA1`) — active, hourly, flips GHL contacts stuck with `Apollo Phone Enrichment Status = queued` AND `Apollo Phone Enrichment Queued At < NOW - 24h` (or missing queued_at) to `callback_timeout` so the Vapi poller unblocks them. Verified first run (execution `75153`): scanned 500, stuck 500, updated 499, 1 contact (Joey Evans `nayDFnGCCcrVO9oTg4ls`) hit a transient 400 in the reaper log but the status field was actually written to `callback_timeout` (GHL dateUpdated confirms) and the Vapi poller will pick him up on a later batch. Source: `n8n/workflows/lt-apollo-queued-timeout-reaper.ts`.

### Dialer Pipeline

- Cron runs Monday through Friday, 9am to 5pm CT.
- The dialer fetches and locks queue rows, checks the contact, applies a timezone-safe calling window, and places the Vapi call.
- The pipeline then increments attempt counts, sets `next_attempt_at` to `NOW + 72h`, and writes the GHL note.
- The dialer prefers internal Coolify service-to-service communication where possible.

### Intake Pipeline

- Cron runs every 10 minutes.
- The intake poller searches GHL for `vapi_queue` contacts.
- Valid E.164 numbers are enqueued.
- Invalid or missing phone numbers are skipped when enrichment is not sufficient.

### Callback Tools

- `update_lead_status` updates the GHL tag and the Postgres disposition.
- `add_to_dnc` sets `voice_call_queue.dnc=true` and adds the GHL DNC tag.
- `log_call_outcome` upserts `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales` posts lead name and summary into `#leads`.

### Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

### Vapi Campaign Tags (to create)

- `vapi_campaign_brand`
- `vapi_campaign_dispensary`
- `vapi_already_called`

### Call History Summary (voice_call_attempt)

- **1,711** total attempts across **1,045** unique contacts
- Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18
- All V1 calls were against the Emerald MSO/SSO contact pool

### Voice Hardening Remaining

- Move remaining secrets out of workflow `Config` nodes into credentials or env-backed config.
- Verify the dashboard still points all tools and the end-of-call webhook to the canonical callback URL.
- Diagnose why the Apollo phone-enrichment callback URL (`/webhook/ghl-apollo-phone-enrichment-callback-v4`) has had zero deliveries since 2026-05-13 even though the intake workflow still flips contacts to `queued` (synthetic POST to that webhook should be tested, and the Apollo dashboard webhook delivery log should be inspected). Reaper exists as a backstop but the root cause needs fixing.
- ~~The reaper's first run identified contact `nayDFnGCCcrVO9oTg4ls` (Joey Evans) as a 400 on the GHL update; investigate why the standard `PUT /v1/contacts/{id}` payload failed for that one contact and decide whether the reaper needs a defensive retry path.~~ **Resolved 2026-06-05**: GHL dateUpdated confirms the reaper did write `callback_timeout` despite the 400 in the log (transient blip on the 500th sequential PUT). Vapi poller will pick him up on a later batch since his dateAdded is older than the first 40 already processed.

### Apollo API Key Rotation (Done 2026-06-05)

- Old key `W7j2vbChZDN8bfoS-wVJ2Q` replaced in all live n8n workflows with new key `CIgACIqwFAXuvYUQKHZcLA` from `.env` line 39.
- Live workflows touched: `WuxgTa0EEL1mb2SA` (Apollo Phone Enrichment intake V3) and `WmKAhG7mIaXonNsh` (Sheet First).
- Smoke test on V3 webhook `https://automations.livetransparent.com/webhook/ghl-apollo-phone-enrichment-intake-v3` (execution `75289`) confirmed the new apolloApiKey loads at runtime; downstream code errored on test payload (unrelated to key).
- **Critical**: MCP `n8n-lt` `updateNodeParameters` silently corrupts Set v3.4 Config nodes (wraps `assignments.assignments` in `{item: [...]}`, stringifies booleans and `options`). Recovery was via direct n8n REST `PUT /api/v1/workflows/{id}` using the reaper's known-good Config as a reference. Documented in `AGENTS.md` Tooling section.

### Marketing Email Pause (Done 2026-06-05)

- 9 marketing email workflows unpublished in n8n. See [Plan - VAPI Pause & Queued Goals.md](./Plan%20-%20VAPI%20Pause%20%26%20Queued%20Goals.md) for the full list, resumption playbook, and a list of channels (LinkedIn, Instagram, SimpleTexting SMS) that are still active.
- **Required owner action (outside n8n)**: open GHL location `Zwz4relUXVPxx8uohnjV` and manually pause any active marketing email sequences. Pausing the n8n workflows stops CSV imports and intake routing, but the GHL sequences themselves keep running for already-enrolled contacts.

## Next Steps

### 1. Vapi Campaign Rollout (NEW — 2026-07-01)

See `plan.md` for full step-by-step. High-level phases:
- **Phase 1**: Create 2 new Vapi assistants (Alex/Brand, Jordan/Dispensary) with prompts, tools, structured output
- **Phase 2**: Fix classifier workflow to paginate all contacts, apply campaign GHL tags, exclude already-called
- **Phase 3**: Modify dialer (`campaign_id -> assistantId`), callback (per-campaign structured output), intake poller (campaign tags), add dedup gate
- **Phase 4**: Smoke test each campaign, scale rollout

### 2. Voice Hardening

- Move remaining secrets out of workflow `Config` nodes into n8n credentials or env-backed config.
- Verify the Vapi dashboard still points all tools and the end-of-call webhook at the current callback URL.

### 3. Reporting Depth

- Expand the contact-capture panel by channel and landing page.
- Build matched funnel views by channel, campaign, and landing page.

### 4. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Keep the user-facing emphasis on attribution first, then cost reporting.

### 5. Cleanup And Adjacent Automation

- Finish SimpleTexting secret hardening.
- Deploy the staged SMS workflows and verify the live GHL pool query.
- Fix the GHL-to-LinkedIn supply path so `linkedin_connection_state` is seeded from a working GHL contacts list and the dispatcher can send invites from that queue. [DONE 2026-06-03]
- Verify LinkedIn connection requests and DM sends from execution history. [DONE 2026-06-03]
- Retry and enable the blocked GSC ingest workflow.
- Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.

## Reporting Workflows

### Workflow List

- `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) — active, seeds report settings and runtime flags
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — active, rebuilt replacement for archived `OtqWjqGXZC3OcrXP`
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) — active
- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) — active
- `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) — active
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) — active
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) — active
- `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`) — active
- `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`) — active

### Live Reporting State

- GA4 ingestion is live and feeding the executive report.
- GHL leads and sales ingestion is live and flowing into Postgres.
- The report host is live and secure.
- The GHL `Executive Report` custom menu entry points at the report host.
- The executive summary webhook is live and returns GHL-first report JSON from Postgres.
- `LT - Report Daily Rollups` preserves GA-backed channel, UTM, landing-page, and daily traffic rows.
- Funnel-efficiency metrics are live in the executive summary API and embedded report.

### Current Cohort Notes

- `contactToOpportunityRate` uses a contact-safe cohort metric instead of a raw multi-opportunity total.
- The current 30-day new-contact cohort is still returning `0` matched contact-to-opportunity progression.
- The current attribution coverage result for that same cohort is `97` contacts, `45` with usable source fields, `45` attributed bridge matches, and `22` lead-to-sale matches after normalized raw contact IDs and stored-field fallbacks.

### Report Model

- Raw tables cover GA4 sessions, GA4 pages, GA4 events, GSC queries, GSC pages, GSC site, GHL contacts, GHL opportunities, GHL pipeline history, and GHL forms.
- Bridge tables cover traffic-to-lead, lead-to-sale, and identity mapping.
- Rollup tables cover daily summary, channel summary, funnel summary, pipeline summary, stage summary, UTM summary, and landing page summary.

### Report Next Work

1. Expand the contact-capture panel by channel and landing page.
2. Build matched funnel views by channel, campaign, and landing page.
3. Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
4. Finish SimpleTexting secret hardening.
5. Deploy the staged SMS workflows and verify the live GHL pool query.
6. Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.
7. Fix the GHL-to-LinkedIn supply path so queue rows are created from the working GHL contacts list, then verify connection requests and DM sends from execution history.
8. Retry and enable the blocked GSC ingest workflow.

### Report Dependencies

- GA4 property ID is still the external dependency for any remaining GA4 API wiring work.
- Meta Ads API access is validated on `2026-05-05` against `act_2186975138800404`.
- For GA4 service account wiring, use a secret-backed JSON file in Coolify and keep the credentials out of source control.

## Operating Notes

- Prefer Coolify internal service-to-service communication where possible.
- Verify live state after every mutation: fetch first, patch second, audit live workflow plus recent execution before declaring a fix.
- Preserve graph integrity when editing n8n workflows: keep existing node IDs and keep the connections map aligned.
- For voice automations, prefer `Switch` over `IF`, and use raw JSON import for dialer patches.
- Report end-to-end validation should still span leads ingest, attribution bridge, daily rollups, and executive summary output.
- If LinkedIn troubleshooting is resumed in a fresh session, start by reading this file, `AGENTS.md`, `repomix-output.md`, and the latest executions for `LT - LinkedIn Connection State Sync (Unipile)`, `LT - GHL LinkedIn Connect Dispatcher (Unipile)`, and `LT - LinkedIn DM Sequence (Unipile)`.
- Do not declare LinkedIn fixed until execution history shows nonzero `matched`, `upserted`, and `sent` values on the relevant workflows.

## Working Order

1. Vapi Campaign Rollout (new campaigns, 4 phases — see `plan.md`).
2. Voice hardening.
3. Reporting depth.
4. Meta attribution.
5. Cleanup and adjacent automation.
```
