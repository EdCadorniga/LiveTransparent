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

## n8n REST API Note

When using direct n8n REST `PUT /api/v1/workflows/{id}`:
- Required fields: `name`, `nodes`, `connections`, `settings`
- Settings must NOT include `availableInMCP` (remove before PUT)
- `versionId` and `tags` are read-only — exclude from body
- `Content-Type: application/json` header is required
- If settings get rejected as "additional properties", strip down to: `executionOrder`, `timezone`, `saveDataErrorExecution`, `saveDataSuccessExecution`, `saveManualExecutions`, `saveExecutionProgress`, `executionTimeout`, `callerPolicy`
- Use `curl.exe` with JSON file for large payloads (PowerShell `ConvertTo-Json` can corrupt deep nested objects with `#` chars in API keys)

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

### LT - Voice Dequeue Next (`KsBMFcz1YpBGrjDW`) — pipeline_stage Bug
- **Issue**: Dequeue query filters `AND pipeline_stage = 'queued'`, but `voice_call_queue` schema has **no `pipeline_stage` column** (confirmed in bootstrap SQL). This means the dequeue webhook has NEVER returned rows from the intake poller. V1 pipeline worked through the dialer cron path instead.
- **Fix**: Remove `AND pipeline_stage = 'queued'` from dequeue query.
- **Method**: `setNodeParameter` on Postgres node (safe).

### LT - Voice Agent V1 Vapi Callback + Tools (`fx4UvKUWbqJEY3LK`) — trackedAssistants
- **Issue**: `trackedAssistants` array in `Code - Detect Tool vs Callback` was hardcoded with only V1 Outbound + Inbound IDs. Campaign assistants would not be tracked for timer enforcement.
- **Fix**: Added both campaign assistant IDs (`1d7c5d42...`, `056f2e50...`) to the array. Ideally move to Config node.

### Vapi Campaign Rollout Phase 1 (2026-07-01)
- **Phase 1 complete**: 2 new Vapi assistants created (Brand/Alex + Dispensary/Jordan) via Vapi API, 9 tools each, full system prompts from campaign docx files.
- **Vapi tools cleanup**: 2 deprecated (`old_ok_ghl_calendar_*`) deleted, 1 dangling ref removed from Inbound assistant.
- **John→Jason migration**: Transfer tool renamed (`ok_transfer_to_john` → `ok_transfer_to_jason`), all assistant prompts updated, n8n callback Switch + Set node updated. Keep phone same (+15622474600).
- **Quality gate (pending)**: Manual test call per assistant before Phase 2.

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
| Callback webhook | `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback` |
| Key env | `VAPI_PHONE_NUMBER_ID`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`, `GHL_API_KEY` / `GHL_PIT` |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Voice Campaign Brand (Alex) | `1d7c5d42-f0a4-4b58-9494-dbda3be3c657` | Created 2026-07-01 (not active) |
| LT - Voice Campaign Dispensary (Jordan) | `056f2e50-8bdf-4257-ac45-4d575600c39d` | Created 2026-07-01 (not active) |
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

### Vapi Campaign Tags (created 2026-07-01)

- `vapi_campaign_brand` (`exfU7DXbFF1c314Z1QXQ`)
- `vapi_campaign_dispensary` (`FiYEwJdMSIyKZa059wRY`)
- `vapi_already_called` (`HhkfhzocuEdOFOxeeHu2`)

## Vapi Campaign Rollout Plan (2026-07-01)

Two new voice campaigns deploying alongside the existing V1 paused infrastructure. See `plan.md` for full step-by-step.

### Campaign Definitions

| Campaign | Persona | Target | Goal | Vapi Assistant ID | Campaign Tag |
|----------|---------|--------|------|-------------------|--------------|
| Brand Outreach | Alex | Brand marketing/growth leads | Book strategy call for Dispensary Attribution Network | `1d7c5d42-f0a4-4b58-9494-dbda3be3c657` | `vapi_campaign_brand` |
| Dispensary Recruitment | Jordan | Dispensary owners/managers | Book call or email partner agreement | `056f2e50-8bdf-4257-ac45-4d575600c39d` | `vapi_campaign_dispensary` |

### Phase 1 Complete (2026-07-01)
- **Assistants created**: Brand/Alex + Dispensary/Jordan via Vapi API, 9 tools each, campaign doc prompts
- **Vapi tools cleanup**: 2 deprecated tools deleted, 1 dangling ref removed, 14 remain
- **John → Jason migration**: Transfer tool renamed, all assistant prompts updated, n8n switch + Set node updated
- **Inbound assistant**: Added missing `ok_transfer_to_jason` tool
- **Callback trackedAssistants**: Both new assistant IDs added for timer enforcement
- **GHL tags created**: `vapi_campaign_brand`, `vapi_campaign_dispensary`, `vapi_already_called`

### Prep Completed (2026-07-01)
- **Queue cleanup**: 1,005 stale V1 `pending` rows → `failed`
- **Pool audit**: 23,726 GHL contacts; 1,045 unique already called; ~16k Emerald pool
- **Classifier workflow**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) created — queries voice_call_attempt + GHL contacts, classifies by Emerald tags
- **Call history**: 1,711 total attempts across 1,045 contacts (voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18)

### Bugs Discovered During Audit
1. **Dequeue pipeline_stage bug**: `voice_call_queue` schema has no `pipeline_stage` column, but dequeue query filters `AND pipeline_stage = 'queued'`. Dequeue has NEVER returned rows from intake poller. V1 worked through dialer cron. Fix: remove the filter.
2. **Callback trackedAssistants hardcoded**: Was a static array `['43f379ff...', '3f9bbfd2...']`. Now includes both campaign assistants. Ideally move to Config node.

### Critical Infrastructure Changes Needed (Phase 3)
1. Dialer must map `campaign_id → assistantId` (currently hardcoded to V1 assistant)
2. Intake poller must seed from campaign-specific tags (currently only `vapi_queue`)
3. Enqueue must dedup against existing queue rows by `contact_id`
4. Fix dequeue `pipeline_stage` bug

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
