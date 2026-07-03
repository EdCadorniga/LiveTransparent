This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
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
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
AGENTS.md
classifier-repair-plan.md
classifier-workflow-change-plan.md
classifier-workflow-mcp-update-ops.md
classifier-workflow-patch-snippets.md
Dockerfile
Emerald_Contacts_Data_Audit.md
emerging-pool-post-import-runbook.md
execution-checklist-after-import.md
Executive_Report_Training_Guide.md
fix_intake_poller.js
live-mutation-plan.md
LiveTransparent Report Plan.md
LT_SSO_Executive_Set1_UPDATED.docx
package.json
plan.md
Project Specifications.md
Project Status and Next Steps.md
QWEN.md
rollback-checklist-vapi-emerging-pool.md
Sales and Marketing Roadmap.md
sms_edited_templatekeys.md
Unipile_potential_automations.md
vapi-campaign-prompts-summary.md
```

# Files

## File: AGENTS.md
````markdown
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
- n8n target version: `2.28.6` (upgraded from `2.25.3` on 2026-07-03; originally upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue).
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
- **n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` return fields (`tags`, `scopes`, `canExecute`, `availableInMCP`) that violate the MCP tool's `additionalProperties: false` output schema. **Workaround:** Use direct REST API calls for workflow listing and details:
  ```bash
  # List workflows
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows?active=true&limit=100"
  
  # Get single workflow
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows/{workflowId}"
  ```
  The MCP tools for **workflow execution, editing, and node operations** are unaffected. Only discovery/listing tools are broken. This will be fixed in a future n8n release.

## Code Node HTTP Requests

When making HTTP calls inside n8n Code nodes:
- **Use `this.helpers.httpRequest({...})` directly** — do NOT wrap in an async helper function and call with `.call(this, ...)`. The wrapper pattern (`doHttpRequest.call(this, opts)`) frequently causes HTTP 400 errors because the task runner's `this` context changes in loops.
- **`$httpRequest`** works for simple single calls but may fail in pagination loops.
- **`json: true`** works but must be paired with explicit `'Content-Type': 'application/json'` header.
- For paginated GHL search API calls, use `page` (1-indexed integer) + `pageLimit` (max 100). Do NOT use `startAfter`/`startAfterId`.
- Do NOT include empty `filters: []` array in GHL search body — omit entirely.
- Add `await new Promise(r => setTimeout(r, delayMs))` between pages to avoid rate limiting (GHL PIT token returns 401 after ~5400 requests).

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
| LT - Vapi Campaign Queue Feeder | `RFIZ9Bcfl3Yvms2b` | Manual/scheduled helper (created 2026-07-02, inactive). Patched 2026-07-03 to require both campaign tag + matching imported-pool tag. |
| LT - Emerging Pool Go Live Helper | `OGnADUQKd5z5f905` | Manual helper (created 2026-07-03). Runs imported-pool readiness, backfill, audit, and isolate queries through the live `Postgres account` credential. |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Active 2026-07-02 |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Paused (held for quality gate) |
| LT - Voice Queue Vapi Intake Poller | `bYk1Ai6MJLyhTsDZ` | Paused (held for quality gate) |
| LT - Voice Queue Enqueue | `XzcpOBi9YcIhJPck` | Active 2026-07-02 |
| LT - Voice Dequeue Next | `KsBMFcz1YpBGrjDW` | Active 2026-07-02 |
| LT - Call Outcome Ingest | `PUCfTZBANSPcgS0c` | Active 2026-07-02 |
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
- **Callback trackedAssistants**: Both new campaign assistant IDs added for timer enforcement
- **GHL tags created**: `vapi_campaign_brand`, `vapi_campaign_dispensary`, `vapi_already_called`

### Phase 3 Infrastructure Changes (DONE 2026-07-01)
1. **Dialer campaign mapping**: `Build Vapi Body` Code node now has `CAMPAIGN_ASSISTANTS` map — `'default'`→V1, `'brand'`→Alex, `'dispensary'`→Jordan
2. **Intake poller campaign tags**: `Prepare Search` searches by `vapi_campaign_brand`/`vapi_campaign_dispensary` (OR via separate API calls), `Classify Contacts` maps tag→`campaign_id`
3. **Enqueue dedup gate**: Postgres `WHERE NOT EXISTS` guard prevents duplicate `pending`/`in_progress` rows per `contact_id`
4. **Dequeue pipeline_stage bug**: Removed `AND pipeline_stage = 'queued'` filter (column doesn't exist), added `includeOtherFields: true` to Config, campaign routing via ternary in HTTP node

### Prep Completed (2026-07-01)
- **Queue cleanup**: 1,005 stale V1 `pending` rows → `failed`
- **Pool audit**: 23,726 GHL contacts; 1,045 unique already called; ~16k Emerald pool
- **Classifier workflow**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) created — queries voice_call_attempt + GHL contacts, classifies by Emerald tags (see Phase 2 blocker in section above)
- **Heuristic verified**: Emerald contacts carry tags like `sso_marketing`, `cannabis-retail-sso-marketing-1`, `seq emerald - marketing sso`. No standalone `mso`/`sso` tags. Classifier uses keyword substring matching: `marketing`/`sso`/`brand`/`growth` → Brand campaign; `dispensary`/`retail`/`owner`/`manager`/`executive` → Dispensary campaign.
- **Call history**: 1,711 total attempts across 1,045 contacts (voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18)

### Phase 2 — Classifier Status (imported-pool path live 2026-07-03)
- **Workflow**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)
- **Current structure**: Manual Start → Postgres (`emerging_pool_contacts` joined against `report_raw_ghl_contacts` for `Em_Emerald_Contact_ID` / `Em_Source_File`, then deduped against `voice_call_attempt` and `voice_call_queue` pending/in_progress) → Code classifier (`5` Brand + `5` Dispensary cap) → GHL tag apply → summary
- **Why changed again**: the older `Emerald_Contacts` executive path was not the desired campaign supply. The imported `emerging_pool_contacts` pool is the canonical source for this rollout. The classifier now uses imported pool segmentation directly rather than a keyword heuristic.
- **Current data reality (2026-07-03)**: the GHL Brand + Dispensary import has finished. `report_raw_ghl_contacts` has 30 Brand + 20 Dispensary rows with `Em_Emerald_Contact_ID` and `Em_Source_File` populated. `emerging_pool_contacts.ghl_contact_id` is backfilled for those 50 rows. The remaining 13,818 imported rows are still unmatched to GHL until more reporting ingest lands.
- **Initial tagged seed (10 contacts)**: 5 Brand + 5 Dispensary, all from `emerging_pool_contacts` source list. Tags applied via GHL API in classifier execution `105490` on 2026-07-03.
  - Brand: `KdA7vRKGuVUym1acE0D0`, `3uRbaI3yZOjUCrDZfjiE`, `3vMUseClXnxqZuYSTved`, `FA2Cd923b7YzmJBdfByX`, `2AthxJS3uMoGWxnVU9v7`
  - Dispensary: `DkDogBpdJhH1gX8pauNP`, `bAqpQ2GtnhsoDPcuHGGT`, `wKzcvnuSXMCZdRLJuteo`, `Oxa0BTBbPi6JkPXGQIeT`, `plwkRBIvXuThB54iujAJ`
- **2026-07-03 key bug found and fixed**: SQL readiness + backfill assumed custom fields carry a `name` key. Live GHL contact objects only return `id` + `value` for the imported fields, so the lookup missed everything until we also matched by stable field id `R0wbDRyzZz34PMlQSRWN` (`Em_Emerald_Contact_ID`) and `ILurFacMbAaHz2DdGjPa` (`Em_Source_File`).

### Queue Feeder Status (imported-pool isolation 2026-07-03)
- **Workflow**: `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`)
- **Purpose**: Slowly stage already-approved `vapi_campaign_brand` / `vapi_campaign_dispensary` contacts into `voice_call_queue`
- **Current structure**: Schedule Trigger (30 min) → build per-campaign config → filter enabled campaigns → GHL search by campaign tag → eligible contact filter → guarded Postgres insert → normalized summary
- **Controls**: per-campaign `enabled` flag + `per_run_limit` in the first Code node
- **2026-07-03 patch**: `Filter Eligible Contacts` now also requires the matching imported-pool tag (`brands_pool` or `dispensaries_pool`) so the feed cannot mix legacy campaign-tagged contacts into the imported-pool test cohort.
- **Latest manual run (execution 105492)**: surfaced 4 eligible pool contacts (2 brand, 2 dispensary). 3 were inserted; 1 was skipped because a duplicate queue row already existed from the previous feeder run. No legacy cohort contacts were returned.
- **Insert-path verification**: those 3 candidate IDs from the earlier feeder run were confirmed already-existing `pending` rows in `voice_call_queue`; the duplicate guard is working as designed.
- **2026-07-03 isolation cleanup**: `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) added a step `Isolate Imported Pool Test Queue` that marks any remaining non-imported `pending` campaign rows as `failed` and leaves imported-pool rows untouched. The first run marked 5 legacy rows as failed.
- **Active queue after cleanup**: only imported-pool seed rows remain `pending`:
  - `Oxa0BTBbPi6JkPXGQIeT` — Dispensary — AYR Cannabis Dispensary - Ocala
  - `2AthxJS3uMoGWxnVU9v7` — Brand — Miss Grass
  - `FA2Cd923b7YzmJBdfByX` — Brand — Local Grove
  - `DkDogBpdJhH1gX8pauNP` — Dispensary — Northern Green Canada
- **Dedup status**: the live flow prevents duplicate calls per contact — classifier and feeder both exclude any contact already in `voice_call_attempt` or pending queue, and enqueue blocks duplicate active rows. The voice dialer and dequeue paths are still paused and should be activated only after the manual assistant quality gate.

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

- LinkedIn invite copy is sourced from `docs/outreach/outreach_messages.v2.docx`.
- LinkedIn DM copy is sourced from `docs/outreach/outreach_messages.v2.docx`.
- LinkedIn DM timing is currently 0, 3, 4, 3, 4 days between sends after the first message clock starts.
- Active LinkedIn conversations are marked in `linkedin_connection_state` via `payload_json.dm_conversation_status = 'active'`.
- For LinkedIn supply, prefer seeding `linkedin_connection_state` from the working GHL contacts list and keep `linkedin_connected` rows out of the queue entirely.
- If you restart the session, re-check the live n8n executions for the sync, dispatcher, and DM workflows before saying the pipeline is healthy.
- SimpleTexting SMS campaign work is now staged in repo workflow exports, using `docs/outreach/outreach_messages.docx` as the SMS source of truth.
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
- `n8n/workflows/lt-emerging-pool-import.ts` — SDK workflow for Brands/Dispensaries Postgres import
- `scripts/fix_intake_poller.js` — intake poller fix script
- `scripts/fix_sheets_node.py`, `scripts/fix_brands_code.py`, `scripts/fix_parse_csv.py` — temporary fix scripts (can be cleaned up)
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
- `docs/campaigns/Vapi_Brand_Campaign.docx` — Brand campaign (Alex persona, brand marketing leads)
- `docs/campaigns/Vapi_Dispensary_Campaign.docx` — Dispensary campaign (Jordan persona, dispensary owners)
- `plan.md` — Vapi Campaign Rollout implementation plan (4 phases)

## VPS SSH Access

- Host: `89.117.21.29` (hostname `vmi3077218`), user `root`
- SSH key: `C:\Users\edmon\.ssh\local-upload` (Ed25519, no passphrase, generated via Coolify Keys & Tokens)
- Permission fix on Windows: paramiko works directly (bypasses Win32 OpenSSH permission checks).
  To use `ssh.exe`: run `icacls $keyPath /reset /inheritance:r /grant "$env:USERNAME:(R)"`
  Or use Python paramiko: `paramiko.Ed25519Key.from_private_key(io.StringIO(key_data))`
- SCP via paramiko (sftp):
  ```python
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('89.117.21.29', username='root', pkey=key, timeout=10)
  sftp = ssh.open_sftp()
  sftp.put(local_path, remote_path)
  ```
- Reference keys on server: `vps_caddy_key`, `vps_upload`, `id_ed25519_vps_whitefriar` — all passphrase-encrypted, unknown passwords.
- GHL-ready CSV files live on the n8n server at `/home/node/.n8n-files/GHL_Ready_Brands.csv` and `/home/node/.n8n-files/GHL_Ready_Dispensaries.csv`.
- Local copies (with GHL-mapped column headers, pool tags + `emerald`) at `data/GHL_Ready_Brands.csv` and `data/GHL_Ready_Dispensaries.csv`.
- n8n workflows:
  - `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`) — reads Brands CSV, inserts into `emerging_pool_contacts` with `source_list='brands'`
  - `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`) — reads Dispensaries CSV, inserts with `source_list='dispensaries'`
- Postgres table `emerging_pool_contacts` stores 13,868 contacts (3,668 brands + 10,200 dispensaries) with fields: `emerald_contact_id`, `source_list`, `first_name`, `last_name`, `primary_email`, `primary_phone`, `company_name`, `tags`, `ghl_contact_id`, `ghl_opportunity_id`, `ghl_import_status`, `raw_json` (JSONB with full GHL-mapped row). UNIQUE on (emerald_contact_id, source_list).
- **Imported pool next-session files**:
  - `postgres/emerging-pool-go-live-check.sql` — consolidated landing + coverage + seed cohort preview
  - `postgres/check-emerging-pool-import-readiness.sql` — verify imported contacts landed in `report_raw_ghl_contacts`
  - `postgres/backfill-emerging-pool-ghl-ids.sql` — backfill `emerging_pool_contacts.ghl_contact_id` from `Em_Emerald_Contact_ID`
  - `postgres/audit-emerging-pool-linkage.sql` — duplicate/collision/queue audits after backfill
  - `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql` — optional second-pass opportunity linkage
  - `postgres/select-emerging-pool-vapi-candidates.sql` — eligibility query for rebuilt classifier
  - `postgres/select-vapi-seed-test-batch.sql` — first 5 Brand + 5 Dispensary manual review cohort
   - `docs/classifier/classifier-repair-plan.md` — why the classifier must move to `emerging_pool_contacts`
   - `docs/classifier/classifier-workflow-change-plan.md` — node-by-node classifier rebuild plan
   - `docs/classifier/classifier-workflow-patch-snippets.md` — exact node content replacements
   - `docs/classifier/classifier-workflow-mcp-update-ops.md` — MCP operation objects for `IduCoT5YOs0g2faT`
   - `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json` — machine-ready workflow update payload
   - `docs/classifier/emerging-pool-post-import-runbook.md` — full operator sequence
   - `docs/classifier/live-mutation-plan.md` — mutation order and stop gates
   - `docs/classifier/rollback-checklist-vapi-emerging-pool.md` — surgical rollback plan
   - `docs/classifier/execution-checklist-after-import.md` — concise after-import execution checklist
- **Apollo re-enrichment on bad numbers** (added 2026-07-02): In callback workflow `fx4UvKUWbqJEY3LK`, after `GHL - Apply Tags`, a new `Should Re-enrich Phone` IF node checks disposition. If `wrong_number` or `contact_disconnected`, it fires `HTTP - Set Apollo Enrichment` which sets `Enrich Phone via Apollo = Yes` (custom field `gdJDuZelIxEBE6n9i5Q6`). The existing `LT - Apollo Phone Enrichment Intake V3` then looks up a new number.

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate `repomix-output.md` so next-session context is up to date:

1. `. $PROFILE`  
2. `packlive`

This stages key files into `C:\TempRepomixStaging`, runs `npx repomix --style markdown --compress --remove-comments --remove-empty-lines`, and copies the result back to the project root.
````

## File: classifier-repair-plan.md
````markdown
# Emerald Vapi Classifier Repair Plan

## Why This Needs Repair

- The documented classifier intent says `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) should classify Emerald candidates from Postgres and apply `vapi_campaign_brand` / `vapi_campaign_dispensary`.
- The live workflow no longer matches that description. Its current `Called Contacts` node is hardcoded to 3 specific `voice_call_queue.contact_id` values, so it is not a general classifier anymore.
- Once the imported Brand/Dispensary contacts are linked back into `emerging_pool_contacts`, the classifier should be rebuilt around that imported pool instead of the older executive-heavy `Emerald_Contacts` table.

## Target Data Source

Primary table:
- `emerging_pool_contacts`

Required fields before classification:
- `emerald_contact_id`
- `source_list`
- `primary_phone`
- `primary_email`
- `company_name`
- `tags`
- `ghl_contact_id`

Optional enrichment fields later:
- `ghl_opportunity_id`
- `ghl_import_status`

## Classification Goal

Tag imported pool contacts into one of:
- `vapi_campaign_brand`
- `vapi_campaign_dispensary`

while excluding:
- contacts already called
- contacts already queued
- DNC or already-terminal Vapi outcomes
- contacts without a usable linked `ghl_contact_id`
- contacts without a callable phone path

## Recommended Rule Set

Do not reuse the old broad `sso` substring heuristic.

### Brand campaign candidates
- `source_list = 'brands'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged

### Dispensary campaign candidates
- `source_list = 'dispensaries'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged

This is simpler and safer than role-tag inference, because the new imports are already split into Brand vs Dispensary source pools.

## Recommended Workflow Shape

Manual trigger first, then optionally scheduled later.

1. `Manual Trigger`
2. `Postgres` select eligible rows from `emerging_pool_contacts`
3. `Code` normalize campaign tag payloads
4. `HTTP Request` add GHL tag to matching contacts
5. `Code` summarize counts and sample IDs

## Recommended Eligibility Query Shape

Pull rows from `emerging_pool_contacts` where:
- `ghl_contact_id IS NOT NULL`
- `source_list IN ('brands', 'dispensaries')`
- `primary_phone <> ''` or a later approved fallback exists
- not already present in `voice_call_attempt`
- not already present in `voice_call_queue` with `status IN ('pending', 'in_progress')`

Map tag directly:
- `brands` -> `vapi_campaign_brand`
- `dispensaries` -> `vapi_campaign_dispensary`

## Suggested SQL Skeleton

```sql
SELECT
  epc.id,
  epc.ghl_contact_id AS contact_id,
  epc.source_list,
  epc.first_name,
  epc.primary_phone,
  CASE
    WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'
    WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'
    ELSE NULL
  END AS campaign_tag
FROM emerging_pool_contacts epc
WHERE epc.ghl_contact_id IS NOT NULL
  AND epc.source_list IN ('brands', 'dispensaries')
  AND COALESCE(epc.primary_phone, '') <> ''
  AND NOT EXISTS (
    SELECT 1
    FROM voice_call_attempt a
    WHERE a.contact_id = epc.ghl_contact_id
  )
  AND NOT EXISTS (
    SELECT 1
    FROM voice_call_queue q
    WHERE q.contact_id = epc.ghl_contact_id
      AND q.status IN ('pending', 'in_progress')
  );
```

## Rollout Recommendation

Phase the classifier relaunch:

1. Run once in dry/manual mode and return only a summary
2. Spot-check 10 Brand + 10 Dispensary candidates
3. Enable live tag application for a tiny cohort
4. Let the queue feeder consume those tagged contacts
5. Only then resume dialer/poller activation

## Dependency Order

1. GHL CSV import completes
2. `report_raw_ghl_contacts` lands imported contacts
3. `postgres/backfill-emerging-pool-ghl-ids.sql` runs
4. optional `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql` runs later
5. classifier is rebuilt against `emerging_pool_contacts`
6. queue feeder is rechecked against real imported campaign cohorts

## Notes

- This classifier should become much simpler than the old Emerald heuristic workflow.
- The imported pool split (`brands` vs `dispensaries`) is already the campaign decision, so the main job becomes eligibility filtering, not semantic classification.
````

## File: classifier-workflow-change-plan.md
````markdown
# LT - Campaign Contact Classifier Workflow Change Plan

Target workflow:
- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)

## Current Problem

The live workflow currently does not act as a general Emerald classifier.
Its `Called Contacts` Postgres node is hardcoded to 3 specific `voice_call_queue.contact_id` values.

## New Purpose

Repurpose the workflow into a manual or low-volume helper that:
- selects eligible imported pool contacts from `emerging_pool_contacts`
- maps `source_list` directly to campaign tag
- applies `vapi_campaign_brand` or `vapi_campaign_dispensary` in GHL
- returns a summary of what was tagged

## Recommended Node Changes

### 1. `Manual Start`
- Keep as-is.

### 2. Replace `Called Contacts` query
- Keep the node type as Postgres.
- Replace the current hardcoded queue-contact query with the selection query from:
  - `postgres/select-emerging-pool-vapi-candidates.sql`
- For the workflow version, use only the main candidate-select statement, not the summary block.

Expected output fields:
- `emerging_pool_row_id`
- `emerald_contact_id`
- `source_list`
- `contact_id`
- `campaign_id`
- `campaign_tag`
- `first_name`
- `last_name`
- `primary_email`
- `primary_phone`
- `company_name`

### 3. Replace `Classify` node logic
- Current node just returns `$input.all()`.
- Update it to normalize payloads and optionally cap run size for safety.

Recommended behavior:
- pass through only rows with both `contact_id` and `campaign_tag`
- optionally limit to first N rows per run for controlled activation

Recommended output shape:
- `contact_id`
- `campaign_id`
- `campaign_tag`
- `first_name`
- `company_name`
- `emerging_pool_row_id`

### 4. Keep `Apply Campaign Tag`
- The HTTP node is structurally fine.
- It already posts to:
  - `POST /contacts/{contact_id}/tags`
- Keep batching.

Verify it still uses:
- bearer auth credential
- `Version: 2021-07-28`
- `Content-Type: application/json`
- `jsonBody = { tags: [$json.campaign_tag] }`

### 5. Update `Summarize Tags`
- Keep the node type as Code.
- Make it report:
  - total eligible selected
  - total tagged successfully
  - counts by `campaign_id`
  - sample contact IDs
  - sample company names
  - sample Emerald row IDs

Suggested summary fields:
- `eligible_count`
- `tagged_count`
- `brand_count`
- `dispensary_count`
- `sample_contact_ids`
- `sample_companies`
- `sample_emerging_pool_row_ids`

## Recommended Safe Rollout Mode

For the first live pass, constrain the `Classify` node to:
- max 5 Brand rows
- max 5 Dispensary rows

After spot-checking the actual contacts in GHL, remove or raise the cap.

## Why This Is Better

- It removes stale dependence on the old executive-focused `Emerald_Contacts` path.
- It aligns the classifier to the imported pool that was already split into Brand vs Dispensary.
- It makes campaign selection deterministic rather than heuristic.
- It keeps the queue feeder as the downstream pacing mechanism.

## Suggested Validation Steps

1. Run `postgres/select-emerging-pool-vapi-candidates.sql`
2. Confirm there are eligible rows in both pools
3. Update workflow `IduCoT5YOs0g2faT`
4. Execute manually with a small cap
5. Spot-check tags in GHL
6. Let `RFIZ9Bcfl3Yvms2b` pick up the newly tagged rows
````

## File: classifier-workflow-mcp-update-ops.md
````markdown
# LT - Campaign Contact Classifier MCP Update Ops

Target workflow:
- `IduCoT5YOs0g2faT`

Use these operation payloads with `n8n-lt update_workflow` after imported contacts are landed and `ghl_contact_id` backfill is done.

## Operation 1: Update `Called Contacts`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Called Contacts",
  "replace": false,
  "parameters": {
    "operation": "executeQuery",
    "query": "WITH latest_ghl_contacts AS (\n  SELECT DISTINCT ON (source_key)\n    source_key,\n    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,\n    payload_json,\n    dimensions_json,\n    loaded_at\n  FROM report_raw_ghl_contacts\n  WHERE source_system = 'ghl'\n    AND source_key LIKE 'contact:%'\n  ORDER BY source_key, report_date DESC, loaded_at DESC\n),\neligible_contacts AS (\n  SELECT\n    epc.id AS emerging_pool_row_id,\n    epc.emerald_contact_id,\n    epc.source_list,\n    epc.first_name,\n    epc.last_name,\n    epc.primary_email,\n    epc.primary_phone,\n    epc.company_name,\n    epc.tags AS pool_tags,\n    epc.ghl_contact_id AS contact_id,\n    epc.ghl_opportunity_id,\n    lgc.dimensions_json->>'tags' AS ghl_tags,\n    lgc.dimensions_json->>'phone' AS ghl_phone,\n    lgc.dimensions_json->>'email' AS ghl_email,\n    CASE\n      WHEN epc.source_list = 'brands' THEN 'brand'\n      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'\n      ELSE NULL\n    END AS campaign_id,\n    CASE\n      WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'\n      WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'\n      ELSE NULL\n    END AS campaign_tag\n  FROM emerging_pool_contacts epc\n  LEFT JOIN latest_ghl_contacts lgc\n    ON lgc.ghl_contact_id = epc.ghl_contact_id\n  WHERE epc.ghl_contact_id IS NOT NULL\n    AND epc.source_list IN ('brands', 'dispensaries')\n    AND COALESCE(epc.primary_phone, '') <> ''\n    AND NOT EXISTS (\n      SELECT 1\n      FROM voice_call_attempt a\n      WHERE a.contact_id = epc.ghl_contact_id\n    )\n    AND NOT EXISTS (\n      SELECT 1\n      FROM voice_call_queue q\n      WHERE q.contact_id = epc.ghl_contact_id\n        AND q.status IN ('pending', 'in_progress')\n    )\n    AND NOT EXISTS (\n      SELECT 1\n      WHERE lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_already_called%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_call_attempted%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_dnc%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%do not contact%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_human_answered%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interested%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_not_interested%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interest_unknown%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail_left%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_no_answer%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_busy%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_wrong_number%'\n         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_contact_disconnected%'\n    )\n)\nSELECT\n  emerging_pool_row_id,\n  emerald_contact_id,\n  source_list,\n  contact_id,\n  campaign_id,\n  campaign_tag,\n  first_name,\n  last_name,\n  primary_email,\n  primary_phone,\n  company_name,\n  ghl_phone,\n  ghl_email\nFROM eligible_contacts\nWHERE campaign_tag IS NOT NULL\nORDER BY source_list, emerging_pool_row_id;"
  }
}
```

## Operation 2: Update `Classify`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Classify",
  "replace": false,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const MAX_PER_CAMPAIGN = 5;\nconst rows = $input.all().map((item) => item.json || {});\n\nconst grouped = { brand: [], dispensary: [] };\n\nfor (const row of rows) {\n  const campaignId = String(row.campaign_id || '').trim();\n  const contactId = String(row.contact_id || '').trim();\n  const campaignTag = String(row.campaign_tag || '').trim();\n  if (!campaignId || !contactId || !campaignTag) continue;\n  if (!grouped[campaignId]) continue;\n  if (grouped[campaignId].length >= MAX_PER_CAMPAIGN) continue;\n\n  grouped[campaignId].push({\n    json: {\n      emerging_pool_row_id: row.emerging_pool_row_id || null,\n      emerald_contact_id: row.emerald_contact_id || null,\n      source_list: row.source_list || null,\n      contact_id: contactId,\n      campaign_id: campaignId,\n      campaign_tag: campaignTag,\n      first_name: row.first_name || '',\n      last_name: row.last_name || '',\n      primary_email: row.primary_email || '',\n      primary_phone: row.primary_phone || '',\n      company_name: row.company_name || ''\n    }\n  });\n}\n\nreturn [...grouped.brand, ...grouped.dispensary];"
  }
}
```

## Operation 3: Update `Summarize Tags`

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Summarize Tags",
  "replace": false,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const classified = $items('Classify').map((item) => item.json || {});\nconst applied = $input.all().map((item) => item.json || {});\n\nconst byCampaign = {\n  brand: { eligible: 0, tagged: 0 },\n  dispensary: { eligible: 0, tagged: 0 }\n};\n\nfor (const row of classified) {\n  const key = String(row.campaign_id || '').trim();\n  if (byCampaign[key]) byCampaign[key].eligible += 1;\n}\n\nfor (const row of applied) {\n  const key = String(row.campaign_id || '').trim();\n  if (byCampaign[key]) byCampaign[key].tagged += 1;\n}\n\nreturn [{\n  json: {\n    ok: true,\n    workflow: 'LT - Campaign Contact Classifier',\n    eligible_count: classified.length,\n    tagged_count: applied.length,\n    brand_count: byCampaign.brand.eligible,\n    dispensary_count: byCampaign.dispensary.eligible,\n    brand_tagged_count: byCampaign.brand.tagged,\n    dispensary_tagged_count: byCampaign.dispensary.tagged,\n    sample_contact_ids: classified.slice(0, 10).map((row) => row.contact_id),\n    sample_companies: classified.slice(0, 10).map((row) => row.company_name || row.first_name || row.contact_id),\n    sample_emerging_pool_row_ids: classified.slice(0, 10).map((row) => row.emerging_pool_row_id)\n  }\n}];"
  }
}
```

## Suggested Batch Apply

Pass the three operations in one atomic `update_workflow` call.

## First Manual Validation

After patching:
- execute the workflow manually
- verify it selects only up to 5 Brand + 5 Dispensary rows
- spot-check those contact IDs in GHL before letting the queue feeder continue
````

## File: classifier-workflow-patch-snippets.md
````markdown
# LT - Campaign Contact Classifier Patch Snippets

Target workflow:
- `IduCoT5YOs0g2faT`

Use this after:
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- optional review of `postgres/select-emerging-pool-vapi-candidates.sql`

## Replace `Called Contacts` Query

Node name:
- `Called Contacts`

Replace the current SQL with:

```sql
WITH latest_ghl_contacts AS (
  SELECT DISTINCT ON (source_key)
    source_key,
    regexp_replace(source_key, '^contact:', '') AS ghl_contact_id,
    payload_json,
    dimensions_json,
    loaded_at
  FROM report_raw_ghl_contacts
  WHERE source_system = 'ghl'
    AND source_key LIKE 'contact:%'
  ORDER BY source_key, report_date DESC, loaded_at DESC
),
eligible_contacts AS (
  SELECT
    epc.id AS emerging_pool_row_id,
    epc.emerald_contact_id,
    epc.source_list,
    epc.first_name,
    epc.last_name,
    epc.primary_email,
    epc.primary_phone,
    epc.company_name,
    epc.tags AS pool_tags,
    epc.ghl_contact_id AS contact_id,
    epc.ghl_opportunity_id,
    lgc.dimensions_json->>'tags' AS ghl_tags,
    lgc.dimensions_json->>'phone' AS ghl_phone,
    lgc.dimensions_json->>'email' AS ghl_email,
    CASE
      WHEN epc.source_list = 'brands' THEN 'brand'
      WHEN epc.source_list = 'dispensaries' THEN 'dispensary'
      ELSE NULL
    END AS campaign_id,
    CASE
      WHEN epc.source_list = 'brands' THEN 'vapi_campaign_brand'
      WHEN epc.source_list = 'dispensaries' THEN 'vapi_campaign_dispensary'
      ELSE NULL
    END AS campaign_tag
  FROM emerging_pool_contacts epc
  LEFT JOIN latest_ghl_contacts lgc
    ON lgc.ghl_contact_id = epc.ghl_contact_id
  WHERE epc.ghl_contact_id IS NOT NULL
    AND epc.source_list IN ('brands', 'dispensaries')
    AND COALESCE(epc.primary_phone, '') <> ''
    AND NOT EXISTS (
      SELECT 1
      FROM voice_call_attempt a
      WHERE a.contact_id = epc.ghl_contact_id
    )
    AND NOT EXISTS (
      SELECT 1
      FROM voice_call_queue q
      WHERE q.contact_id = epc.ghl_contact_id
        AND q.status IN ('pending', 'in_progress')
    )
    AND NOT EXISTS (
      SELECT 1
      WHERE lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_already_called%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_call_attempted%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_dnc%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%do not contact%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_human_answered%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_not_interested%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_interest_unknown%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_voicemail_left%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_no_answer%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_busy%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_wrong_number%'
         OR lower(COALESCE(lgc.dimensions_json->>'tags', '')) LIKE '%vapi_contact_disconnected%'
    )
)
SELECT
  emerging_pool_row_id,
  emerald_contact_id,
  source_list,
  contact_id,
  campaign_id,
  campaign_tag,
  first_name,
  last_name,
  primary_email,
  primary_phone,
  company_name,
  ghl_phone,
  ghl_email
FROM eligible_contacts
WHERE campaign_tag IS NOT NULL
ORDER BY source_list, emerging_pool_row_id;
```

## Replace `Classify` Code

Node name:
- `Classify`

Recommended safe first-pass code:

```javascript
const MAX_PER_CAMPAIGN = 5;
const rows = $input.all().map((item) => item.json || {});

const grouped = {
  brand: [],
  dispensary: [],
};

for (const row of rows) {
  const campaignId = String(row.campaign_id || '').trim();
  const contactId = String(row.contact_id || '').trim();
  const campaignTag = String(row.campaign_tag || '').trim();
  if (!campaignId || !contactId || !campaignTag) continue;
  if (!grouped[campaignId]) continue;
  if (grouped[campaignId].length >= MAX_PER_CAMPAIGN) continue;

  grouped[campaignId].push({
    json: {
      emerging_pool_row_id: row.emerging_pool_row_id || null,
      emerald_contact_id: row.emerald_contact_id || null,
      source_list: row.source_list || null,
      contact_id: contactId,
      campaign_id: campaignId,
      campaign_tag: campaignTag,
      first_name: row.first_name || '',
      last_name: row.last_name || '',
      primary_email: row.primary_email || '',
      primary_phone: row.primary_phone || '',
      company_name: row.company_name || '',
    },
  });
}

return [...grouped.brand, ...grouped.dispensary];
```

After validation, raise or remove `MAX_PER_CAMPAIGN`.

## Replace `Summarize Tags` Code

Node name:
- `Summarize Tags`

Use this summary code:

```javascript
const classified = $items('Classify').map((item) => item.json || {});
const applied = $input.all().map((item) => item.json || {});

const byCampaign = {
  brand: { eligible: 0, tagged: 0 },
  dispensary: { eligible: 0, tagged: 0 },
};

for (const row of classified) {
  const key = String(row.campaign_id || '').trim();
  if (byCampaign[key]) byCampaign[key].eligible += 1;
}

for (const row of classified) {
  const key = String(row.campaign_id || '').trim();
  if (byCampaign[key]) byCampaign[key].tagged += 1;
}

return [{
  json: {
    ok: true,
    workflow: 'LT - Campaign Contact Classifier',
    eligible_count: classified.length,
    tagged_count: applied.length,
    brand_count: byCampaign.brand.eligible,
    dispensary_count: byCampaign.dispensary.eligible,
    sample_contact_ids: classified.slice(0, 10).map((row) => row.contact_id),
    sample_companies: classified.slice(0, 10).map((row) => row.company_name || row.first_name || row.contact_id),
    sample_emerging_pool_row_ids: classified.slice(0, 10).map((row) => row.emerging_pool_row_id),
  },
}];
```

## Suggested MCP Update Sequence

When you're ready to patch the workflow, use targeted updates only:

1. `updateNodeParameters` for `Called Contacts` (safe for Postgres node)
2. `updateNodeParameters` for `Classify` (safe for Code node)
3. `updateNodeParameters` for `Summarize Tags` (safe for Code node)

Avoid editing unrelated nodes.

## Validation Checklist

After patching the workflow:

1. Execute manually
2. Confirm returned candidates are only from `brands` / `dispensaries`
3. Confirm no already-called or already-queued contacts are included
4. Confirm only 5 Brand + 5 Dispensary contacts are tagged on the first pass
5. Spot-check those contacts in GHL before letting the queue feeder consume them
````

## File: Dockerfile
````dockerfile
FROM nginx:1.27-alpine

COPY reports/nginx.conf /etc/nginx/conf.d/default.conf
COPY reports /usr/share/nginx/html
````

## File: Emerald_Contacts_Data_Audit.md
````markdown
# Emerald Contacts Data Audit

**Date:** 2026-05-14

## Executive Summary

| Issue | Count |
|-------|-------|
| Cross-bucket duplicates (same email in multiple role buckets) | **50** contacts |
| DNC + active bucket conflicts | **9** contacts (marked Do Not Contact but also in mso_executive or sso_executive) |
| Shared phone numbers (2+ contacts share same number) | **2,247** numbers affecting **~16k** contacts |
| Contacts moved to review file (phone-only shared/invalid) | **4,705** rows |
| Contacts without any phone number (deduped file) | **7,085** / 19,649 (36%) |
| Contacts without usable phone (no-phone + review file) | **11,790** / 24,354 (**48%**) |
| Bucket tag counts: sso_executive 7,603 / mso_executive 4,027 / marketing 2,363 / finance 892 / retail_sales 730 / DNC 909 | **16,524** total in v5 tagging file |

**Data sources:**
- `ghl_v5_tagging_import_email_only.csv` — 16,524 rows, email+tag buckets for GHL tagging
- `emerald-contacts.ghl.csv` — 27,320 rows, full source data (pre-dedup)
- `emerald-contacts.dedup.ghl.csv` — 19,649 rows, deduped GHL-safe import
- `emerald-contacts.dedup.review-shared-phone.csv` — 4,705 rows, phone-only shared/invalid flagged

---

## 1. Cross-Bucket Duplicates (Same Email in Multiple Buckets)

**50 unique emails** appear in 2+ different role buckets. These are contacts assigned to multiple categories (MSO executive, SSO executive, marketing, finance, retail sales, or Do Not Contact).

| Email | Name | Buckets | Rows |
|-------|------|---------|------|
| bj@cookiesre.com | | Do Not Contact, mso_executive | 5 |
| phvesq@gmail.com | | mso_executive, sso_executive | 5 |
| queen@soldistro.com | | mso_executive, sso_executive | 3 |
| gdinla@proton.me | | sso_executive, sso_finance | 3 |
| thebabyloncompany@gmail.com | | mso_executive, sso_executive | 3 |
| altaherbllc@gmail.com | | mso_executive, sso_executive | 3 |
| sveta@citrushill.org | | mso_executive, sso_executive | 3 |
| mike@arcadewellness.org | | mso_executive, mso_finance | 3 |
| nick@highlinedistro.com | | mso_executive, sso_executive | 3 |
| jmendonca@tokenfarmsinc.com | | mso_executive, mso_marketing | 2 |
| joey@theflowery.co | | Do Not Contact, mso_executive | 2 |
| john@novafarms.com | | Do Not Contact, mso_executive | 2 |
| karen.duval@crescolabs.com | | mso_executive, mso_retail_sales | 2 |
| kelsey@thefirestation.com | | mso_executive, mso_marketing | 2 |
| michael.bang@calyxpeak.com | | mso_executive, mso_finance | 2 |
| 17325muskratinc@gmail.com | | sso_executive, sso_finance | 2 |
| jeff@simplysolventless.ca | | mso_executive, mso_marketing | 2 |
| richard@710labs.com | | Do Not Contact, mso_executive | 2 |
| samiy1827@gmail.com | | mso_executive, mso_finance | 2 |
| shivvers@shivvers.com | | sso_executive, sso_marketing | 2 |
| smithunlimited@gmail.com | | mso_retail_sales, sso_finance | 2 |
| soufyan@edenenterprises.com | | Do Not Contact, mso_executive | 2 |
| theloadedbowl420@gmail.com | | sso_executive, sso_finance | 2 |
| tony@sensibrands.ca | | mso_executive, mso_marketing | 2 |
| nate@jettyextracts.com | | Do Not Contact, mso_executive | 2 |
| home4u4life@gmail.com | | mso_executive, sso_finance | 2 |
| greenlifealaska@gmail.com | | mso_executive, sso_executive | 2 |
| triphoffman@bodyandmind.com | | mso_executive, mso_retail_sales | 2 |
| adam@hgremedies.com | | Do Not Contact, sso_executive | 2 |
| akoudijs@hennep.com | | sso_executive, sso_retail_sales | 2 |
| allyfeiler@gmail.com | | mso_executive, sso_executive | 2 |
| andrew@missiondispensaries.com | | mso_executive, mso_marketing | 2 |
| andrew@mockingbird-holdings.com | | sso_executive, sso_finance | 2 |
| bradpalmer@cannacruz.com | | sso_executive, sso_finance | 2 |
| brandon@goldenbarn.com | | sso_executive, sso_marketing | 2 |
| cantodiemllc@gmail.com | | mso_executive, mso_marketing | 2 |
| caren.woodson@kivaconfections.com | | Do Not Contact, mso_executive | 2 |
| hciventures@gmail.com | | sso_executive, sso_finance | 2 |
| chris@levelblends.com | | Do Not Contact, mso_executive | 2 |
| complianceleadership@ethoscannabis.com | | Do Not Contact, mso_executive | 2 |
| cristyearanguiz@gmail.com | | mso_executive, sso_executive | 2 |
| dan@riversidecompany.com | | sso_executive, sso_marketing | 2 |
| daniel@capeanncannabis.com | | sso_executive, sso_retail_sales | 2 |
| daniel@greenwayvegas.com | | mso_executive, sso_executive | 2 |
| dankulchin@yahoo.com | | sso_executive, sso_finance | 2 |
| david@luckyleaf.co | | mso_executive, mso_retail_sales | 2 |
| dcarr@blossommj.com | | mso_executive, sso_executive | 2 |
| exhalence@yahoo.com | | sso_executive, sso_finance | 2 |
| collectivemindsca@gmail.com | | mso_executive, sso_executive | 2 |
| william@bloomnetwork.io | | Do Not Contact, sso_executive | 2 |

**Notable cross-bucket patterns:**
- `mso_executive + sso_executive` — most common (same person in both MSO and SSO executive lists)
- `mso_executive + mso_finance` or `mso_executive + mso_marketing` — person wears multiple hats at same company
- `Do Not Contact + mso_executive` — 9 contacts flagged both as DNC and active (needs resolution)

---

## 2. Shared Phone Numbers

**2,247 unique phone numbers** are shared by 2+ contacts. Most are corporate switchboards where many employees share the same main line.

### Top shared numbers (company main lines)

| Phone | Contacts | Example Companies |
|-------|----------|-------------------|
| +1 877 303 0741 | 114 | Data enrichment source tag (peopledatalabs — flagged as non-phone in source data) |
| +1 781 451 0117 | 70 | Likely corporate switchboard |
| +1 319 355 8843 | 56 | Likely corporate switchboard |
| +1 312 338 7860 | 56 | Likely corporate switchboard |
| +1 614 407 3111 | 41 | Cresco Labs main line |
| +1 415 672 4450 | 40 | Caliva main line |
| +1 800 332 8383 | 38 | General corporate line |
| +1 212 697 1000 | 36 | NYC-area company line |
| +1 860 999 3470 | 36 | Likely corporate switchboard |
| +1 312 929 0993 | 36 | Likely corporate switchboard |
| +1 855 790 8169 | 35 | Cresco Labs related |
| +1 707 599 0610 | 33 | Cresco Labs / Sunnyside related |
| +1 800 432 2558 | 33 | Caliva related |
| +1 212 460 1900 | 32 | Columbia Care main line |
| +1 800 484 0303 | 32 | Cresco Labs related |
| +1 860 717 9333 | 31 | General corporate line |
| +1 800 268 4623 | 31 | Dispensary chain line |
| +1 860 246 4673 | 28 | General corporate line |
| +1 740 672 3706 | 27 | Likely corporate switchboard |
| +1 514 843 3632 | 27 | Canadian company line |

**16,139 distinct contacts** have a phone number that's also associated with another contact. The build script already flagged 4,705 rows into `emerald-contacts.dedup.review-shared-phone.csv` as `phone_only_shared_or_invalid`.

---

## 3. Contacts Without Phone Numbers

### In deduped file (`emerald-contacts.dedup.ghl.csv` — 19,649 rows)

| Source File | Total | No Phone | % |
|-------------|-------|----------|---|
| Cannabis-Retail-MSO-Executive-1 | 3,564 | 1,870 | 52.5% |
| Cannabis-Retail-MSO-Executive-2 | 4,202 | 2,663 | **63.4%** |
| Cannabis-Retail-MSO-Marketing-1 | 717 | 321 | 44.8% |
| Cannabis-Retail-SSO-Executive-1 | 7,154 | 2,606 | 36.4% |
| Cannabis-Retail-SSO-Executive-2 | 9,255 | 3,731 | 40.3% |
| Cannabis-Retail-SSO-Marketing-1 | 2,428 | 1,098 | 45.2% |
| **Total** | **27,320** | **12,289** | **45.0%** |

### Field coverage in deduped file

| Coverage | Count |
|----------|-------|
| Has phone (Phone or Corporate_Phone) | 12,564 |
| Has email | 16,250 |
| Has both phone and email | 9,165 |
| No phone at all (deduped file only) | 7,085 |
| Review file (phone-only shared/invalid) | 4,705 |
| **Total without usable phone** | **11,790 / 24,354 (48.4%)** |

---

## 4. Tag Bucket Distribution (v5 tagging file — 16,524 rows)

| Bucket | Count |
|--------|-------|
| sso_executive | 7,603 |
| mso_executive | 4,027 |
| sso_marketing | 1,723 |
| Do Not Contact | 909 |
| mso_marketing | 640 |
| sso_finance | 595 |
| sso_retail_sales | 410 |
| mso_retail_sales | 320 |
| mso_finance | 297 |
| **Total** | **16,524** |

---

## 5. Original Source File Summary

| Metric | Value |
|--------|-------|
| Source rows (6 files) | 33,561 |
| Importable rows | 27,320 |
| Skipped (missing email + phone) | 6,241 |
| Deduped before phone safety filter | 24,354 |
| Deduped GHL-safe import | 19,649 |
| Moved to review (shared/invalid phone) | 4,705 |
| Deduplication collisions resolved | 2,966 |

---

## Key Takeaways

1. **50 cross-bucket dupes** need dedup resolution — decide which bucket takes priority for each
2. **9 DNC + active bucket conflicts** need resolution (contacts marked Do Not Contact but also in an active bucket)
3. **48% lack usable phone numbers** — MSO-Executive-2 is worst at 63.4% no-phone; enrichment needed if SMS outreach required
4. **~16k contacts share phones** with others — largely corporate switchboards, flagged appropriately in the review file
````

## File: emerging-pool-post-import-runbook.md
````markdown
# Emerging Pool Post-Import Runbook

## Purpose

Operational sequence for taking newly imported `GHL_Ready_Brands.csv` and `GHL_Ready_Dispensaries.csv` contacts from GHL import completion to Vapi-ready campaign cohorts.

## Order Of Operations

### 1. Confirm GHL import completed
- Wait until both GHL CSV imports finish processing in the GHL UI.
- Do not backfill early while contacts are still being created.

### 2. Confirm imported contacts landed in reporting raw contacts
- Run:
  - `postgres/check-emerging-pool-import-readiness.sql`

What to look for:
- both `brands` and `dispensaries` show landed contacts
- `with_emerald_contact_id` is close to landed contacts
- `landed_in_report_raw_contacts` is moving toward imported row counts

### 3. Backfill `ghl_contact_id`
- Run:
  - `postgres/backfill-emerging-pool-ghl-ids.sql`

Expected result:
- `emerging_pool_contacts.ghl_contact_id` fills for imported rows that landed in `report_raw_ghl_contacts`

### 4. Audit linkage quality
- Run:
  - `postgres/audit-emerging-pool-linkage.sql`

Pay attention to:
- duplicate Emerald IDs
- multiple Emerald rows mapping to one GHL contact
- imported pool contacts missing `Em_Emerald_Contact_ID`
- queue-linked rows and orphaned queued contacts

### 5. Optional second pass: backfill `ghl_opportunity_id`
- Run only after contact linkage looks clean:
  - `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`

### 6. Select eligible campaign candidates
- Run:
  - `postgres/select-emerging-pool-vapi-candidates.sql`

This becomes the basis for the rebuilt classifier workflow.

### 7. Select a tiny manual seed batch
- Run:
  - `postgres/select-vapi-seed-test-batch.sql`

Use this to manually inspect the first 5 Brand and 5 Dispensary contacts before tagging or queueing.

### 8. Repair classifier workflow
- Follow:
  - `classifier-workflow-change-plan.md`
  - `classifier-repair-plan.md`

Target workflow:
- `IduCoT5YOs0g2faT`

### 9. Manual tag application / tiny cohort validation
- Apply `vapi_campaign_brand` / `vapi_campaign_dispensary` only to a tiny reviewed cohort first.
- Let queue feeder workflow `RFIZ9Bcfl3Yvms2b` stage them gradually.

### 10. Controlled Vapi resume
- Manual assistant test calls first
- Then recheck queue rows
- Then resume paused dialer / poller in controlled order

## Recommended Safety Gates

Do not proceed to the next phase unless:
- readiness query shows contacts really landed
- `ghl_contact_id` backfill produced healthy coverage
- audit query does not show widespread duplicate collisions
- the seed batch looks correct in GHL by manual inspection

## Files In This Sequence

- `postgres/check-emerging-pool-import-readiness.sql`
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- `postgres/audit-emerging-pool-linkage.sql`
- `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`
- `postgres/select-emerging-pool-vapi-candidates.sql`
- `postgres/select-vapi-seed-test-batch.sql`
- `classifier-repair-plan.md`
- `classifier-workflow-change-plan.md`
````

## File: execution-checklist-after-import.md
````markdown
# Execution Checklist After Import

## Goal

Concrete operator checklist for the moment the GHL Brand / Dispensary imports are fully processed.

## Step 1: Run go-live check

Run:
- `postgres/emerging-pool-go-live-check.sql`

Record:
- landed Brand count
- landed Dispensary count
- seed cohort preview rows

## Step 2: If landing looks healthy, backfill contact IDs

Run:
- `postgres/backfill-emerging-pool-ghl-ids.sql`

Record:
- updated Brand rows
- updated Dispensary rows

## Step 3: Audit linkage

Run:
- `postgres/audit-emerging-pool-linkage.sql`

Check:
- duplicate Emerald IDs
- duplicate `ghl_contact_id` mappings
- missing `Em_Emerald_Contact_ID` on landed pool contacts
- queued contacts not linked back to pool rows

## Step 4: Preview seed cohort

Run:
- `postgres/select-vapi-seed-test-batch.sql`

Manual review:
- 5 Brand rows
- 5 Dispensary rows
- confirm in GHL they are correct and callable

## Step 5: Patch classifier workflow

Patch source:
- `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`

Target workflow:
- `IduCoT5YOs0g2faT`

## Step 6: Run classifier manually

Expected:
- up to 5 Brand contacts tagged
- up to 5 Dispensary contacts tagged

## Step 7: Validate tags in GHL

Check newly tagged contacts for:
- correct campaign tag
- correct company / persona fit
- no obvious mis-tagged executive rows

## Step 8: Run queue feeder manually

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Expected:
- staged rows only for the reviewed cohort
- no unexpected candidates

## Step 9: Decide on voice activation

Only proceed if all prior checks look correct.

Then:
- do manual assistant test calls
- verify queue rows
- resume paused Vapi components in controlled order

## Abort Conditions

Stop if:
- low landing coverage
- weak contact ID backfill rate
- duplicate collision pattern looks unsafe
- wrong contacts appear in seed cohort
- classifier tags wrong contacts
- feeder stages unexpected rows
````

## File: Executive_Report_Training_Guide.md
````markdown
# LiveTransparent Executive Report
## Training Document and Quick Reference Guide
Updated: May 12, 2026

This guide explains what each visible card in the Executive Report means, how to present it, and where the common interpretation risks are. It matches the live dashboard glossary, the users-based funnel cards, and the trailing-day range presets.

# Part I: Report Sections -- Quick Explanations
Use this section when reviewing the report with someone who needs the fastest possible explanation.

- KPI Row: The six cards at the top summarize the selected date window: Recorded Visits, Contacts, Opportunities, Meetings, Closed Won, and Revenue. Recorded visits are the visits GA4 captured in the selected window. Contacts is CRM volume. It is normal for these to differ because a contact is not always created by a form.
- Traffic and Channels: This panel shows where website traffic came from and how much volume each channel produced. Channel Breakdown is a GA4 traffic summary, not a contact summary. Channel Detail connects traffic to contact generation when the data exists.
- Meta Ads: This panel is attribution-first. It shows Meta-tagged visits and downstream contacts, opportunities, and booked meetings. It does not depend on spend to be useful. Treat it as a performance and attribution view, not a ROAS view.
- Acquisition Sources: This is the contact-level source view. It shows where contacts originated from the CRM bridge and source fields. If someone asks where the acquisition source view is, this is the section to open.
- Top Pages: This is a short website page summary based on the landing-page rollup we already capture. It shows the pages that received the most recorded visits, plus form and opportunity activity when available.
- Funnel and Attribution: This panel now uses Users as the primary denominator for the conversion cards. User -> Form and User -> Contact are the main funnel rates. The attribution coverage card next to it is a separate diagnostic panel that tells you whether contacts can be matched back to traffic and sales.
- Capture Gaps: This is an absolute-volume panel. It shows Recorded Visits, Forms, Contacts, Opportunities, Meetings, and Closed Won side by side. Do not read it as a perfectly linear funnel because contacts can arrive from routing, manual CRM entry, imports, and follow-up as well as forms.
- Sales and Pipeline: This section provides the company-wide pipeline summary and active-opportunity view. It covers open deals, worked deals, stage movement, velocity, and sales quality. Use it when discussing pipeline health, not acquisition quality.
- UTM / Campaign Breakdown: This panel shows observed traffic rows by source, medium, campaign, content, term, and landing page. It is not a master list of every UTM ever created in GHL. A campaign will only appear here once the traffic or bridge data actually sees it.
- Sales Detail / John's Deals: These cards use the same opportunity payload as the team summary. The difference is presentation: one is a team-wide view and the other is a deal-centred view. If a stakeholder asks what the difference is, the safe answer is that the source data is the same.
- Social and Site: The Social Posts card shows the status of GHL Social Planner posts. Failed means the latest status is failed or error. The Site Traffic card shows GA4 traffic and engagement for the selected window.
- Source Health: This panel tells you whether the integrations are healthy, stale, blocked, or failed. Use it whenever you need to explain why a metric is zero or missing.

# Part 2: Part 2: Technical Deep Dive
This section explains how the report is assembled, what the live API returns, and how to read the payload without inventing new assumptions.

- Architecture: the dashboard is a static HTML and JavaScript SPA at reports.livetransparent.com. It calls a single n8n webhook at `/api/report/executive/summary` and renders the response client-side.
- Request contract: the report reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query parameters. The current preset ranges are trailing complete days ending yesterday.
- Response shape: the API returns `summary`, `channelBreakdown`, `utmBreakdown`, `metaAttribution`, `contactSources`, `topPages`, `pipelineDropoff`, `stageDropoff`, `stageVelocity`, `appointments`, and `health`.
- Response shape: the API also returns the active-opportunity fields used by the report, including `activeOpportunityCount`, `workedOpportunityCount`, `stageMoverCount`, and `opportunityStageBreakdown`.
- Funnel basis: the primary funnel rates now use Users as the denominator where possible. This means the dashboard is treating unique visitors as the main traffic audience, not raw GA4 session counts.
- Source status: GSC Daily Ingest is now live and verified in n8n. Older notes that describe Search Console as blocked are stale and should be treated as historical.
- Attribution logic: Acquisition Sources, UTM / Campaign Breakdown, and Attribution Coverage all depend on observed traffic and bridge data. They should be read as live data quality and attribution outputs, not as a perfect campaign registry.
- Operational rule: when a metric looks wrong, check Source Health first. The report separates stale data from business performance so the reader does not draw the wrong conclusion.

## Metric Definitions
Use these definitions when presenting the dashboard. If a visible metric is not defined here, it should be treated as incomplete until the definition is added.

| Metric | Definition | Presenter note |
|---|---|---|
| Recorded Visits | GA4 recorded visits in the selected window. | Traffic volume only. One person can generate multiple recorded visits. |
| Users | Unique visitors in the selected window. | This is the primary denominator for the funnel cards. |
| Contacts | New CRM contacts created in the selected window. | Contacts are not 1:1 with forms. |
| Forms | Tracked form submissions in the selected window. | This is the submission count, not total contacts. |
| Opportunities | New deals or sales opportunities created in the selected window. | Use this as pipeline creation, not acquisition volume. |
| Active Opportunities | Open opportunities in the latest snapshot. | This is the current open-deal count, not the number of new deals created in the window. |
| Worked Opportunities | Open opportunities updated or moved stage during the selected window. | This is the best current proxy for deals that were actively worked. |
| Stage Movers | Open opportunities that changed stage at least once during the selected window. | Use this to see which deals progressed, even if no new deal was created. |
| Meetings | Booked appointments or discovery calls in the selected window. | These are GHL appointments when available. |
| Calls | GHL conversation call logs and status breakdown. | Use this for answered, missed, voicemail, inbound, and outbound call activity. |
| Closed Won | Deals marked as won. | Use this for outcome reporting, not top-of-funnel conversion. |
| Revenue | Total dollar value of closed-won deals. | This is reported revenue, not spend or profit. |
| User -> Form | Unique users divided by form submissions in the selected window. | Primary traffic-to-lead capture rate. |
| User -> Contact | Unique users divided by CRM contacts created in the selected window. | Primary traffic-to-contact conversion rate. |
| Contact -> Opportunity | Contacts that became opportunities in the selected window. | Contact-safe and not inflated by multiple opportunities per contact. |
| Opportunity -> Meeting | Opportunities that resulted in a booked meeting. | Use this to understand sales handoff quality. |
| Meeting -> Won | Meetings that closed as won. | Use this as a late-stage close measure. |
| Attribution Coverage | A diagnostic view of whether contacts have usable source fields, bridge matches, and sale matches. | This measures data completeness, not business performance. |
| Contacts Created in Window | New contacts created in the selected window. | This is the denominator for attribution coverage. |
| Source Coverage | Contacts with usable source fields. | This tells you whether attribution can be read from the CRM record. |
| Bridge Matched | Contacts linked to a GA4 session. | This tells you whether traffic can be tied back to the CRM contact. |
| Sale Matched | Contacts linked to an opportunity. | This tells you whether the contact carries through to sales. |
| Acquisition Sources | The visible contact-level source / medium / campaign section. | Use this when someone wants to know where contacts came from. |
| Top Pages | The short website page summary based on the landing-page rollup. | Use this when someone wants to know which pages are getting the most recorded visits. |
| Channel Breakdown | GA4 traffic volume by channel. | This is traffic reporting, not lead reporting. |
| UTM / Campaign Breakdown | Observed traffic rows by UTM fields. | This is not a registry of every UTM ever created in GHL. |
| Social Posts Failed | Posts whose latest status is failed or error in the selected window. | This is status-based, not a hidden count of all broken posts. |
| Sales Team Summary | The company-wide opportunity summary. | Use this for the broad sales picture. |
| John's Deals | The same opportunity payload shown as a deal-centred view. | Use this when the conversation is about individual deal movement. |
| 7d / 30d / 90d | Trailing complete-day presets ending yesterday. | Example: if you click 7d on Tuesday, you see the previous Tuesday through Monday. |

# Part 3: How to Present the Report

- Contacts are not always created by forms. Routing, manual CRM entry, imports, and follow-up can also create contacts, which is why the contact count does not always line up with form submissions.
- The GA4 term `sessions` is not the same phrase everyone uses for website visits, so this report labels the metric `Recorded Visits` to make the meaning clear.
- The UTM breakdown is a view of what the data actually observed, not a master campaign catalog of everything ever created in GHL.
- Acquisition Sources is the contact-level section. It is the right place to go when the question is where contacts came from.
- Sales Team and John's Deals use the same opportunity payload. The difference is only the lens: one is the team view and the other is the deal-centred view.
- Calls and Conversations show GHL call records grouped by status. That is the place to explain call activity without mixing it up with SMS or appointments.
- A social post marked Failed means the latest recorded status is failed or error. It is a status value from the ingest, not a subjective review of the post.
- The date range is a trailing complete-day window ending yesterday. That means the selected range always points to finished days, not a click-day-dependent calendar block.
- Active opportunities are the open deals in the latest snapshot. Worked opportunities are the open deals that were updated or moved stage inside the selected window, and stage movers are the ones that actually changed stage.

# Part 4: Naming Standards for Measured Variables
Naming standards matter because the report can only group what is named consistently. This section should be read as part of the measurement contract, not as optional marketing style guidance.

The UTM fields themselves are standard. The exact naming pattern we use for campaigns, ad sets, ads, and landing pages is our internal house standard so the data stays readable and groupable.

That means the tracking fields are not the problem. The important part is making sure every ad link, landing page, and contact intake path writes into those fields the same way every time.

- Use one naming pattern across campaigns, ad sets, ads, UTMs, and landing pages so the report can group traffic without manual cleanup.
- For campaigns, use a stable pattern such as `{brand}-{channel}-{objective}-{audience}-{geo}-{date}`.
- For ad sets, use `{brand}-{campaign}-{audience}-{geo}-{date}` so the ad set always inherits the campaign context.
- For ads, use `{brand}-{campaign}-{adset}-{creative}-{format}-{date}` so the creative, placement format, and launch date are readable without opening the platform.
- For UTMs, keep source, medium, campaign, content, and term consistent with the paid naming system. Do not let ad names and UTM values drift apart.
- For landing pages, use a slug that reflects the offer or funnel step, then keep the UTM fields as the variable layer instead of encoding everything into the URL path.
- For measured variables, prefer a short controlled vocabulary for audience, geo, objective, and creative format. Avoid free-form phrasing that will fragment reporting.
- If a naming field is used in reporting, treat it as a data contract. Changing it should be a conscious decision, not an individual preference.

# Part 5: Improvement Suggestions
These are split into two groups:

- `Safe now` means we can add it to the report or guide without deleting or rewriting the current records.
- `Needs more setup` means it still should not destroy data, but it may need extra coordination or a small amount of historical cleanup.

None of the `Safe now` items require us to erase or rewrite existing records. They either change the wording, add a clearer explanation, or show information we already have.

## Safe now

The report already has UTM capture fields in GHL. The practical improvement is to make sure every ad, page, and contact path writes into those fields the same way every time.

| Suggestion | Why we need it | Data impact |
|---|---|---|
| Show the exact date window at the top of the report. | People should not have to guess whether a range means a calendar week or a trailing window. | No historical data changes. |
| Keep the metric definitions inside the report and the guide. | Everyone should read the same meaning for each card, not a different guess. | No historical data changes. |
| Show a short summary of the most visited pages. | Leadership can quickly see which pages are drawing the most attention without opening a separate analytics tool. | Uses the landing-page rollup we already have. |
| Show user-based conversion rates directly in the report. | This makes the funnel easier to understand because the rate is shown instead of calculated in someone's head. | Uses the numbers already collected. |
| Define active deals, worked deals, and stage movers in plain language. | This removes confusion about whether the report is counting new deals, open deals, or deals that were actually touched. | Uses current opportunity records. |
| Add a simple drilldown for failed social posts. | Management can see which posts failed and why instead of only seeing a total. | No historical data changes. |
| Show search performance in the report when the team wants to review organic search. | It gives leadership one place to see search demand, clicks, and impressions. | No historical data changes. |
| Show a short summary of the most visited pages. | Leadership can quickly see which pages are drawing the most attention without opening a separate analytics tool. | Uses the landing-page rollup we already have. |
| Add an owner filter if `John's Deals` is meant to show John's own pipeline only. | It makes the owner view match the person's actual book of business. | No historical data changes. |
| Standardize names for campaigns, ad sets, ads, UTMs, and landing pages going forward. | Clean names make the report group results correctly and reduce manual cleanup. The existing `UTM Source First/Last`, `UTM Medium First/Last`, `UTM Campaign First/Last`, `UTM Content First/Last`, `UTM Term First/Last`, and landing page fields are already there to hold this data. The pattern itself is our house standard, built on common UTM fields. | Past records stay as-is; future records improve. |
| Keep a master list of the campaigns and UTMs we intentionally launched. | This helps the team tell the difference between something we launched on purpose and something the report never saw, and it makes it easier to check whether the existing UTM fields were filled correctly. | No historical data changes. |
| Add a note about how contacts can be created. | It explains why contacts may come from forms, routing, manual entry, imports, or follow-up. | No historical data changes. |

## Needs More Setup

| Suggestion | Why we need it | Data impact |
|---|---|---|
| Count a deal as worked when notes or updates are added, even if the stage does not change. | Right now, some active work may not show up unless the deal itself changed stage or was updated in a way the report can see. | Still additive, but it needs a clearer rule for what counts as work. |
| Add a cleaner match between contacts and sales when the contact record is incomplete. | This helps reduce the `Unknown` bucket and makes attribution easier to trust. | Still additive, but it may need extra matching rules. |
| Keep the report and the guide using the same definitions. | That prevents the dashboard and the training guide from drifting apart over time. | No historical data changes, but it needs a small maintenance process. |

# Part 6: Current Guardrails

- Treat the glossary in the dashboard as the immediate source of truth for visible cards.
- Use Users-based funnel rates for primary interpretation, and use Recorded Visits only as traffic context.
- Use the attribution coverage card to diagnose data quality separately from business performance.
- Use Source Health whenever a metric unexpectedly drops to zero or looks stale.

# Appendix A: Naming Templates
These examples are intentionally simple and machine-readable. The main goal is to keep campaign, ad set, ad, and UTM values aligned so reporting can aggregate them without manual cleanup.

| Layer | Example pattern | Example |
|---|---|---|
| Meta campaign | `{brand}-{channel}-{objective}-{audience}-{geo}-{date}` | `lt-meta-leads-intake-broad-us-2026-05` |
| Meta ad set | `{brand}-{campaign}-{audience}-{geo}-{date}` | `lt-meta-intake-broad-us-2026-05` |
| Meta ad | `{brand}-{campaign}-{adset}-{creative}-{format}-{date}` | `lt-meta-intake-broad-carousel-01-2026-05` |
| Google Ads campaign | `{brand}-{channel}-{objective}-{geo}-{date}` | `lt-google-search-book-demo-us-2026-05` |
| Google Ads ad group | `{brand}-{campaign}-{keyword-theme}-{geo}-{date}` | `lt-google-search-book-demo-high-intent-us-2026-05` |
| Google Ads ad | `{brand}-{campaign}-{adgroup}-{creative}-{format}-{date}` | `lt-google-search-book-demo-rsa-01-2026-05` |
| UTM source / medium / campaign | `utm_source=...&utm_medium=...&utm_campaign=...` | `utm_source=facebook&utm_medium=paid_social&utm_campaign=lt-meta-leads-intake-broad-us-2026-05` |
| UTM content | `{creative or placement identifier}` | `carousel-01` |
| Landing page slug | `/{offer-or-step}` | `/book-demo` |
````

## File: fix_intake_poller.js
````javascript

````

## File: live-mutation-plan.md
````markdown
# Live Mutation Plan For Emerging Pool -> Vapi Resume

## Goal

Safe execution sequence once GHL import processing has completed and the imported contacts are available in reporting data.

## Preconditions

- GHL imports for `GHL_Ready_Brands.csv` and `GHL_Ready_Dispensaries.csv` are finished
- reporting ingest has landed the imported contacts into `report_raw_ghl_contacts`
- no one else is actively editing the same Vapi classifier workflow at the same time

## Execution Sequence

### Phase 1: Read-only validation

Run in this order:

1. `postgres/check-emerging-pool-import-readiness.sql`
2. `postgres/emerging-pool-go-live-check.sql`

Decision gate:
- proceed only if both `brands` and `dispensaries` show landed contacts and `Em_Emerald_Contact_ID` coverage looks healthy

### Phase 2: Contact linkage mutation

Run:

1. `postgres/backfill-emerging-pool-ghl-ids.sql`
2. `postgres/audit-emerging-pool-linkage.sql`

Decision gate:
- proceed only if contact linkage looks healthy and duplicate collisions are limited / explainable

### Phase 3: Optional opportunity linkage

Run only if needed for downstream reporting or manual review:

1. `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`

This is optional for initial Vapi seeding.

### Phase 4: Seed cohort preview

Run:

1. `postgres/select-vapi-seed-test-batch.sql`

Manual review:
- inspect the returned Brand and Dispensary contacts in GHL
- confirm they look correct for the campaign persona and are callable

### Phase 5: Classifier workflow mutation

Target workflow:
- `IduCoT5YOs0g2faT`

Patch source:
- `classifier-workflow-mcp-update-ops.md`

Apply in one atomic workflow update call.

### Phase 6: Manual classifier execution

Run the classifier manually.

Expected result:
- at most 5 Brand + 5 Dispensary contacts tagged on first pass

Manual check:
- confirm new GHL tags were applied correctly

### Phase 7: Queue feeder verification

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Action:
- run manually after the classifier tags are applied
- verify queued results match expectation

### Phase 8: Controlled voice resume

Only after the seed cohort is confirmed:

1. manual assistant test call for Alex
2. manual assistant test call for Jordan
3. re-check `voice_call_queue` rows for the seed cohort
4. resume paused dialer / poller sequence in the documented order

## Mutation Safety Notes

- Prefer minimal changes to the existing workflow graph.
- Do not touch unrelated nodes in `IduCoT5YOs0g2faT`.
- Keep the first-pass per-campaign cap in place until the first cohort is reviewed.
- Leave `RFIZ9Bcfl3Yvms2b` as the pacing mechanism; do not bypass it for broad rollout.

## Stop Conditions

Pause and reassess if:
- readiness checks show poor landing coverage
- linkage audit shows many-to-one contact collisions at scale
- the classifier returns unexpected executive-style contacts
- the queue feeder inserts rows for contacts that clearly should have been excluded
````

## File: LiveTransparent Report Plan.md
````markdown
# LiveTransparent Report Plan

This note is now a pointer to the canonical project status document:

- [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

Use that file for the current state and priority order so reporting work stays aligned with the voice plan.
````

## File: package.json
````json
{
  "dependencies": {
    "@n8n/workflow-sdk": "^0.13.3"
  }
}
````

## File: plan.md
````markdown
# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans voice, reporting, LinkedIn outreach, and the upcoming SimpleTexting SMS campaign.
- For LinkedIn, keep invite copy and DM copy aligned to `outreach_messages.v2.docx`, and keep reply-stop behavior active.
- For SMS, use `outreach_messages.docx` as the campaign source, with batch dispatch, per-send tagging, shared reply-state tracking, and `#lead` notifications on response.
- Keep this file short; the detailed operating status belongs in `Project Status and Next Steps.md`.

## Vapi Campaign Rollout — Implementation Plan (2026-07-01)

### GHL Tag IDs (created 2026-07-01)
| Tag | ID |
|-----|----|
| `vapi_campaign_brand` | `exfU7DXbFF1c314Z1QXQ` |
| `vapi_campaign_dispensary` | `FiYEwJdMSIyKZa059wRY` |
| `vapi_already_called` | `HhkfhzocuEdOFOxeeHu2` |

### Overview
Two new Vapi voice campaigns targeting the Dispensary Attribution Network:
- **Brand Campaign (Alex)** — sell network participation to cannabis brand marketing leads
- **Dispensary Campaign (Jordan)** — recruit dispensaries as network partner locations

### Schema Context
- `voice_call_queue` already has `campaign_id text NOT NULL` — no migration needed
- `voice_call_queue` has **no `pipeline_stage` column** in bootstrap — but dequeue query filters on it (existing bug)
- `voice_call_attempt` has no `campaign_id` — join through `queue_id` for per-campaign reporting
- `report_raw_ghl_contacts` stores contacts as JSONB — but has daily lag, use live GHL API for classifier

### Efficiency Strategy
Multiple phases can run in parallel since they touch independent systems:

| Tracks | Systems Touched | Can parallelize? |
|--------|----------------|------------------|
| Phase 1 (assistants) + Phase 2 (classifier) | Vapi API vs n8n/Postgres | **Yes** |
| Phase 3 individual items | 5+ different workflows | **Yes, all independent** |
| Phase 3 can start before Phase 2 | Infra vs data | **Yes** — only needs assistantIds + tag names |

**Critical tooling note**: `n8n-lt` `updateNodeParameters` **corrupts Set v3.4 Config nodes**. Use direct n8n REST `PUT /api/v1/workflows/{id}` for Config node changes. `setNodeParameter` is safe for Code nodes.

**Rollback**: Each campaign gets an independent toggle — remove its tag from the intake poller filter to stop intake. No shared coupling.

---

### Phase 0 — Prerequisites (done)

0.1 **GHL tags created**: `vapi_campaign_brand`, `vapi_campaign_dispensary`, `vapi_already_called`
0.2 **Schema confirmed**: `campaign_id` column exists in `voice_call_queue`
0.3 `N8N_API_KEY_LT` available from `.env` for direct REST PUTs

### Phase 1 — Vapi Assistants (done 2026-07-01)

**Tool audit**: Vapi org had 16 tools defined. V1 assistant had only 1 attached (`press_dtmf`). Audit revealed:
- 2 deprecated native GHL tools deleted (`old_ok_ghl_calendar_create_event_tool`, `old_ok_check_ghl_calendar_availability`)
- 1 dangling tool ref removed from Inbound assistant (`4b1439f9...` — already deleted from org)
- `ok_transfer_to_john` renamed to `ok_transfer_to_jason` (function name, messages, descriptions)
- 14 tools remain (2 dtmf/transferCall, 5 server/function, 5 code, 1 gohighlevel native, 1 duplicate notify_sales)

All server/function tools already point to the n8n callback webhook — no new tool creation needed.

**John→Jason migration** (2026-07-01):
- `ok_transfer_to_john` tool → `ok_transfer_to_jason`, messages updated, same phone (+15622474600)
- V1 Outbound assistant: system prompt 9 John→Jason refs, voicemail updated, tool ref updated
- Inbound assistant: system prompt 9 John→Jason refs
- n8n callback `Switch - Route Tool`: rule 6 now matches `ok_transfer_to_jason`
- n8n callback `Set - John Callback Slack` → `Set - Jason Callback Slack`, disposition `jason_callback_requested`

1.1 **Brand assistant (Alex) created** via API (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`):
  - System prompt from `Vapi_Brand_Campaign.docx`: partnerships specialist selling Dispensary Attribution Network
  - **9 tools attached**: `press_dtmf`, `ok_transfer_to_jason`, `ok_get_ghl_contact`, `ok_check_cameron_availability`, `ok_ghl_calendar_book_appointment`, `update_lead_status`, `add_to_dnc`, `log_call_outcome`, `notify_sales`
  - Server messages: `["end-of-call-report", "status-update"]`
  - First message: "Hi, this is Alex calling from Transparent eCom..."
  - Voicemail: directs callbacks to Jason at 562-247-4600

1.2 **Dispensary assistant (Jordan) created** via API (`056f2e50-8bdf-4257-ac45-4d575600c39d`):
  - System prompt from `Vapi_Dispensary_Campaign.docx`: warm/relational, owner-operator focused
  - Same 9 tools attached
  - First message: "Hi, is this {{contact_name}}? This is Jordan with Transparent eCom..."
  - Voicemail: directs callbacks to Jason

1.3 **Phone number**: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`) for both campaigns.
1.4 **Callback trackedAssistants updated**: both new assistant IDs added to `Code - Detect Tool vs Callback` in n8n callback for timer enforcement.
1.5 **Inbound assistant**: `ok_transfer_to_jason` tool attached (was missing).
1.6 **Quality gate (pending)**: 1 manual test call per assistant. Verify persona, tools fire, end-of-call report delivers, dispositions correct.

### Phase 2 — Contact Classification (imported-pool path live 2026-07-03)

2.1 **Rewritten for imported pool**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) now uses the imported Brand/Dispensary pool as the canonical campaign source.
  - Manual Trigger → Postgres (`emerging_pool_contacts` joined against `report_raw_ghl_contacts` for `Em_Emerald_Contact_ID` / `Em_Source_File`) → Code classifier (5 Brand + 5 Dispensary cap) → GHL tag apply → summary
  - The classifier also dedupes against `voice_call_attempt` and pending/in_progress `voice_call_queue` rows
  - This removes the old `Emerald_Contacts` executive path entirely
2.2 **Live data reality (2026-07-03)**: 30 Brand + 20 Dispensary imported rows now have `Em_Emerald_Contact_ID` and `Em_Source_File` in GHL raw contacts. `emerging_pool_contacts.ghl_contact_id` is backfilled for those 50 rows. The remaining 13,818 imported rows are still unmatched to GHL until more reporting ingest lands.
2.3 **Initial tagged seed (10 contacts)**: 5 Brand + 5 Dispensary, all from `emerging_pool_contacts` source list. Tags applied via GHL API in classifier execution `105490` on 2026-07-03.
  - Brand: `KdA7vRKGuVUym1acE0D0`, `3uRbaI3yZOjUCrDZfjiE`, `3vMUseClXnxqZuYSTved`, `FA2Cd923b7YzmJBdfByX`, `2AthxJS3uMoGWxnVU9v7`
  - Dispensary: `DkDogBpdJhH1gX8pauNP`, `bAqpQ2GtnhsoDPcuHGGT`, `wKzcvnuSXMCZdRLJuteo`, `Oxa0BTBbPi6JkPXGQIeT`, `plwkRBIvXuThB54iujAJ`
2.4 **Bug found and fixed (2026-07-03)**: SQL readiness + backfill assumed custom fields carry a `name` key. Live GHL contact objects only return `id` + `value` for the imported fields, so the lookup missed everything until we also matched by stable field id `R0wbDRyzZz34PMlQSRWN` (`Em_Emerald_Contact_ID`) and `ILurFacMbAaHz2DdGjPa` (`Em_Source_File`).
2.5 **Next**: continue to wait for more reporting ingest to land; classifier will re-eligible new imported rows automatically as they backfill. No code change needed once a `ghl_contact_id` is set.

### Phase 3 — Infrastructure Modifications

#### Bug Fixes Found During Audit (DONE 2026-07-01)

3.0.1 ~~**BUG: Dequeue references non-existent `pipeline_stage` column**~~ — **DONE** via `setNodeParameter` on Postgres node. Removed `AND pipeline_stage = 'queued'` from WHERE clause and `pipeline_stage = 'dialing'` from UPDATE SET.

3.0.2 ~~**BUG: Callback has hardcoded `trackedAssistants` array**~~ — **WORKAROUND DONE**: Both new campaign assistant IDs added to the hardcoded array. Ideally move to Config node in future.

#### Infrastructure Changes (ALL DONE 2026-07-01)

3.1 **Modify dialer** (`LT - Voice Agent V1 Outbound Dialer`, `r7UjWLndmc6EqEUW`):
  - **DONE**: `Build Vapi Body` now has `CAMPAIGN_ASSISTANTS` map: `{ default: V1-ID, brand: Alex-ID, dispensary: Jordan-ID }`. Resolves from `$json.campaign_id`.

3.2 **Update callback + tools** (`LT - Voice Agent V1 Vapi Callback + Tools`, `fx4UvKUWbqJEY3LK`):
  - **DONE**: trackedAssistants array updated with `1d7c5d42` (Alex) and `056f2e50` (Jordan).

3.3 **Update intake poller** (`LT - Voice Queue Vapi Intake Poller`, `bYk1Ai6MJLyhTsDZ`):
  - **DONE**: `Prepare Search` passes `campaignTags: ['vapi_campaign_brand', 'vapi_campaign_dispensary']`.
  - **DONE**: `Search GHL Contacts` loops through each tag, makes separate API calls, dedupes results (GHL /contacts/search does NOT support OR filterType).
  - **DONE**: `Classify Contacts` maps matched tag → `campaignId` via `CAMPAIGN_TAG_MAP`.

3.4 **Add dedup gate to enqueue** (`LT - Voice Queue Enqueue`, `XzcpOBi9YcIhJPck`):
  - **DONE**: INSERT now uses `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`.

3.5 **Fix dequeue + campaign routing** (`LT - Voice Dequeue Next`, `KsBMFcz1YpBGrjDW`):
  - **DONE**: 3.5.1 pipeline_stage bug fixed.
  - **DONE**: 3.5.2+3 Config node now has `includeOtherFields: true` (passes queue data through).
  - **DONE**: HTTP node uses ternary: `$json.campaign_id === 'brand' ? Alex-ID : ($json.campaign_id === 'dispensary' ? Jordan-ID : V1-ID)`.

### Phase 4 — Activation & Testing

4.1 Seed test queue: 5 Brand + 5 Dispensary contacts manually
4.2 Reactivate workflows in order:
  1. `LT - Call Outcome Ingest` (capture results)
  2. `LT - Voice Queue Enqueue` (accept queue rows)
  3. `LT - Voice Agent V1 Outbound Dialer` (place calls)
  4. `LT - Voice Agent V1 Vapi Callback + Tools` (process results)
  5. `LT - Voice Dequeue Next` (serve next call)
  6. `LT - Voice Queue Vapi Intake Poller` (only after test batch passes)
4.3 Smoke test: 10 test calls, verify dispositions + campaign_id in attempt rows
4.4 Verify Slack `#leads` fires with campaign context
4.5 **Scale**: Activate intake poller for campaign tags. Brand only for 24h, then Dispensary.
4.6 Monitor first 50 calls. Rollback any underperforming campaign by removing its tag from intake filter.
4.7 Update `AGENTS.md` and `Project Status and Next Steps.md` with new assistantIds and campaign status

### Phase 4 status (2026-07-03)

- **Quality gate pending**: 1 manual test call per assistant (Alex + Jordan) via Vapi dashboard. Verify persona, tools fire, end-of-call report delivers, dispositions correct.
- **Active queue after cleanup (imported-pool only)**:
  - `Oxa0BTBbPi6JkPXGQIeT` — Dispensary — AYR Cannabis Dispensary - Ocala
  - `2AthxJS3uMoGWxnVU9v7` — Brand — Miss Grass
  - `FA2Cd923b7YzmJBdfByX` — Brand — Local Grove
  - `DkDogBpdJhH1gX8pauNP` — Dispensary — Northern Green Canada
- **Dedup confirmed**: classifier, feeder, enqueue, and dequeue all block duplicate calls per contact. Voice dialer and intake poller remain paused.
- **Safest next step**: manual assistant quality gate first, then controlled queue-driven call test. Do not enable intake poller or V1 dialer yet.

## Emerging Pool Import (2026-07-02)

### Source Data
- Two Emerald-sourced CSVs (identical schema, column 1 = `Emerald Contact ID`):
  - `Brands.csv`: 3,668 rows (45% with email, 50% with phone, 29% both)
  - `Dispensaries.csv`: 10,200 rows (37% with email, 72% with phone, 30% both)
- Transformed into GHL-ready CSVs with column headers matching existing GHL custom fields (`Em_*` fields)
- Tags column includes pool tag (`brands_pool` / `dispensaries_pool`) + `emerald`

### Postgres Table
- Created `emerging_pool_contacts` with fields: `emerald_contact_id`, `source_list`, `first_name`, `last_name`, `primary_email`, `primary_phone`, `company_name`, `tags`, `ghl_contact_id`, `ghl_opportunity_id`, `ghl_import_status`, `raw_json` (JSONB), timestamps
- UNIQUE constraint on (emerald_contact_id, source_list)
- 13,868 total contacts inserted (3,668 brands, 10,200 dispensaries)

### Workflows Created
- `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`): reads `/home/node/.n8n-files/GHL_Ready_Brands.csv` → parses → inserts into `emerging_pool_contacts` with `source_list='brands'`
- `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`): reads `/home/node/.n8n-files/GHL_Ready_Dispensaries.csv` → parses → inserts with `source_list='dispensaries'`

### Apollo Re-enrichment on Bad Numbers (callback workflow change)
- Added `Should Re-enrich Phone` IF node + `HTTP - Set Apollo Enrichment` to `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)
- Flow: `GHL - Apply Tags` → IF (disposition == `wrong_number` OR `contact_disconnected`) → HTTP PUT to set `Enrich Phone via Apollo = Yes` → continue to dequeue
- Existing `LT - Apollo Phone Enrichment Intake V3` workflow handles the actual lookup

### Key Files on VPS (inside n8n container at `/home/node/.n8n-files/`)
- `GHL_Ready_Brands.csv` (1.4 MB, 3,668 rows)
- `GHL_Ready_Dispensaries.csv` (3.6 MB, 10,200 rows)

### Supporting workflow added (2026-07-02)

- `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) created to drip-feed already-tagged campaign contacts into `voice_call_queue`.
- Current behavior:
  - runs every 30 minutes
  - searches GHL separately for `vapi_campaign_brand` and `vapi_campaign_dispensary`
  - supports per-campaign `enabled` flags and per-run caps in the config Code node
  - filters out DNC / already-called / already-queued / invalid-phone contacts before queue insert
  - attempts Postgres insert with duplicate guards against `voice_call_queue` and `voice_call_attempt`
- Current verification note:
  - workflow executes successfully end-to-end
  - latest manual verification showed `total_candidates: 3`, `total_queued: 0`, and `skipped_contact_ids` for all 3 candidates
  - Postgres audit confirmed those same 3 contacts already exist in `voice_call_queue` with `status = 'pending'`, so the no-op behavior is currently expected and the duplicate guard is working
  - those 3 queue rows remain `pending` with `attempt_count = 0` and no `voice_call_attempt` history, so they are valid to keep as the seed test batch for controlled activation

## Imported Pool Go-Live Prep (2026-07-03)

### Live state (2026-07-03)
- Brand + Dispensary CSVs imported into GHL. Processing finished.
- 30 Brand + 20 Dispensary rows already in `report_raw_ghl_contacts` with `Em_Emerald_Contact_ID` and `Em_Source_File` populated.
- `emerging_pool_contacts.ghl_contact_id` backfilled for those 50 rows.
- Classifier rebuilt around `emerging_pool_contacts` only; first 5 Brand + 5 Dispensary contacts already tagged in GHL via execution `105490`.
- Queue feeder hardened to require both campaign tag + matching imported-pool tag, and 3 imported-pool rows are now in the active queue (1 still missing because it was already in `voice_call_queue` from a prior run).
- Legacy non-imported campaign rows have been moved to `failed` to keep the first call batch isolated.
- New helper `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) added for the readiness, backfill, audit, and isolation steps.

### Prepared files for the next session
- `postgres/emerging-pool-go-live-check.sql`
- `postgres/check-emerging-pool-import-readiness.sql`
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- `postgres/audit-emerging-pool-linkage.sql`
- `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`
- `postgres/select-emerging-pool-vapi-candidates.sql`
- `postgres/select-vapi-seed-test-batch.sql`
- `classifier-repair-plan.md`
- `classifier-workflow-change-plan.md`
- `classifier-workflow-patch-snippets.md`
- `classifier-workflow-mcp-update-ops.md`
- `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
- `emerging-pool-post-import-runbook.md`
- `live-mutation-plan.md`
- `rollback-checklist-vapi-emerging-pool.md`
- `execution-checklist-after-import.md`

### Exact next-session execution order
1. Run `postgres/emerging-pool-go-live-check.sql`
2. If landing counts look healthy, run `postgres/backfill-emerging-pool-ghl-ids.sql`
3. Run `postgres/audit-emerging-pool-linkage.sql`
4. Patch workflow `IduCoT5YOs0g2faT` using `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
5. Manually execute the classifier with 5 Brand + 5 Dispensary cap
6. Verify the newly tagged contacts in GHL
7. Manually execute queue feeder `RFIZ9Bcfl3Yvms2b`
8. Only then consider controlled Vapi resume

### Classifier note
- The live `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is currently stale and hardcoded to 3 queue contact IDs.
- The rebuilt classifier should use `emerging_pool_contacts` and map campaign directly from `source_list`:
  - `brands` -> `vapi_campaign_brand`
  - `dispensaries` -> `vapi_campaign_dispensary`
````

## File: Project Specifications.md
````markdown
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
````

## File: Project Status and Next Steps.md
````markdown
# LiveTransparent Project Status and Next Steps

Updated: 2026-07-03 (n8n upgraded to 2.28.6, imported Brand/Dispensary pool live in classifier + feeder, queue isolated to imported-pool seed)

## Source Of Truth

This document is the canonical project status and next-steps reference.
It supersedes the duplicated planning notes in:

- [plan.md](./plan.md)
- [LiveTransparent Report Plan.md](./LiveTransparent%20Report%20Plan.md)

## Current State

- The outbound voice stack is **paused** (since 2026-06-05). Vapi assistants, dialer, and intake poller remain intentionally held for the quality gate.
- **Vapi Campaign Rollout Phase 1 complete (2026-07-01)**: Two Vapi assistants created (Brand/Alex `1d7c5d42`, Dispensary/Jordan `056f2e50`) with full system prompts from campaign docx files, 9 tools each. GHL campaign tags created. Vapi org tools cleaned up (2 deprecated deleted, 1 dangling ref removed). `ok_transfer_to_john` → `ok_transfer_to_jason` migration across all assistants, prompts, and n8n callback.
- **Vapi Campaign Rollout Phase 2 live (2026-07-03)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) rebuilt around the imported `emerging_pool_contacts` Brand/Dispensary pool. First seed run tagged 5 Brand + 5 Dispensary contacts in GHL via execution `105490`. The old `Emerald_Contacts` executive heuristic path is no longer used.
- **Imported-pool link fixed (2026-07-03)**: live GHL contacts expose custom fields as `id` + `value` only, not `name`. The readiness, backfill, and audit SQL now match by stable field IDs `R0wbDRyzZz34PMlQSRWN` (`Em_Emerald_Contact_ID`) and `ILurFacMbAaHz2DdGjPa` (`Em_Source_File`), which is what unlocked the first real cohort.
- **Queue feeder isolated (2026-07-03)**: `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) now requires both the campaign tag and the matching imported-pool tag (`brands_pool` or `dispensaries_pool`) before staging a queue row.
- **Active queue after cleanup (2026-07-03)**: only imported-pool seed rows remain `pending`. 4 rows from the first cohort are staged: `Oxa0BTBbPi6JkPXGQIeT` (Dispensary / AYR Cannabis Dispensary - Ocala), `2AthxJS3uMoGWxnVU9v7` (Brand / Miss Grass), `FA2Cd923b7YzmJBdfByX` (Brand / Local Grove), `DkDogBpdJhH1gX8pauNP` (Dispensary / Northern Green Canada). 5 legacy non-imported campaign rows were moved to `failed` to keep the first batch isolated.
- **Dedup confirmed**: classifier, feeder, enqueue, and dequeue all block duplicate calls per contact. The Vapi dialer and intake poller remain paused and should only be enabled after the manual assistant quality gate.
- **New helper workflow (2026-07-03)**: `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) runs imported-pool readiness, backfill, audit, queue audit, and isolation SQL through the live `Postgres account` credential.
- **Bug discoveries (2026-07-03)**: `voice_call_queue` has no `pipeline_stage` column (dequeue filter fixed earlier). Callback `trackedAssistants` array now includes both new campaign assistants.
- **Emerging Pool import (2026-07-02)**: Two brand/dispensary Emerald CSV files imported into Postgres `emerging_pool_contacts` (13,868 total). GHL-ready CSVs prepared with correct column mapping. Two n8n workflows created. Apollo re-enrichment on bad numbers added to callback workflow.
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
- Vapi Assistant IDs: V1 Outbound `3f9bbfd2...`, V1 Inbound `43f379ff...`, Brand (Alex) `1d7c5d42...`, Dispensary (Jordan) `056f2e50...`
- Canonical webhook: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`
- Target n8n version: `2.28.6` (upgraded from `2.25.3` on 2026-07-03; originally upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue)
- Canonical MCP: `n8n-lt`

### Active Workflows

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) — **Manual**, reads from `emerging_pool_contacts` joined against `report_raw_ghl_contacts` and deduped against `voice_call_attempt` / pending queue. Tags 5 Brand + 5 Dispensary per run.
- `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) — **Inactive helper**, runs every 30 minutes when enabled and stages approved `vapi_campaign_*` contacts into the queue with pacing + duplicate guards. Patched 2026-07-03 to require both campaign tag and matching imported-pool tag.
- `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) — **Manual helper** (created 2026-07-03). Runs imported-pool readiness, backfill, audit, queue audit, and isolation SQL through the live `Postgres account` credential.
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — **ACTIVE 2026-07-02**, merged callback plus 4 tools, all 4 campaign assistants tracked
- `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — **ACTIVE 2026-07-02**, receives GHL call webhooks, upserts Postgres, Slack alerts for missed inbound
- `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — **ACTIVE 2026-07-02**, webhook-triggered dequeue, campaign-aware assistant routing
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — **ACTIVE 2026-07-02**, webhook enqueue with dedup guard
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — **PAUSED** (intentionally held for quality gate), queue dialer, contact-TZ-aware, campaign routing
- `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — **PAUSED** (intentionally held for quality gate), polls campaign tags, Apollo enrichment
- **4 of 6 VAPI workflows are now active.** Dialer and intake poller remain paused pending quality gate test calls. GHL-side infrastructure (reaper, Apollo callbacks) remains independent.
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

### Callback Changes (2026-07-02)
- Added `Should Re-enrich Phone` IF node + `HTTP - Set Apollo Enrichment` to the end-of-call flow
- When Vapi returns `wrong_number` or `contact_disconnected` disposition, the callback sets `Enrich Phone via Apollo = Yes` so Apollo can find a new number
- Only those 2 dispositions trigger re-enrichment — all others skip this step
- Uses existing `LT - Apollo Phone Enrichment Intake V3` for the actual lookup

### Callback Tools

- `update_lead_status` updates the GHL tag and the Postgres disposition.
- `add_to_dnc` sets `voice_call_queue.dnc=true` and adds the GHL DNC tag.
- `log_call_outcome` upserts `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales` posts lead name and summary into `#leads`.

### Pool Tags (created 2026-07-02)
- `brands_pool` — contacts from Brands.csv
- `dispensaries_pool` — contacts from Dispensaries.csv

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

### 0. Emerging Pool Import (DONE 2026-07-02, LINKED 2026-07-03)
- **13,868 Emerald contacts** imported into Postgres `emerging_pool_contacts` (3,668 brands + 10,200 dispensaries)
- **GHL-ready CSVs** created at `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_{Brands,Dispensaries}.csv` with columns matching existing GHL `Em_*` custom fields
- Tags: `brands_pool,emerald` / `dispensaries_pool,emerald`
- Two n8n workflows created: `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`) and `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`)
- **2026-07-03 update**: GHL import finished. 30 Brand + 20 Dispensary rows now have `Em_Emerald_Contact_ID` and `Em_Source_File` in `report_raw_ghl_contacts`. `emerging_pool_contacts.ghl_contact_id` backfilled for those 50 rows. First classifier seed run tagged 5 Brand + 5 Dispensary via execution `105490`.

### 1. Vapi Campaign Rollout (Phases 1–3 DONE, Phase 4 READY FOR QUALITY GATE — 2026-07-03)

See `plan.md` for full details. Progress:
- **Phase 1**: **DONE** — 2 assistants created, tools cleanup, John→Jason migration, GHL tags created
- **Quality gate (PENDING)**: Manual test call per assistant (Alex + Jordan) via Vapi dashboard
- **Phase 2**: **DONE** — `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) rebuilt around `emerging_pool_contacts`. First seed run tagged 5 Brand + 5 Dispensary. Old `Emerald_Contacts` executive heuristic is no longer used. GHL field-ID matching fix is live.
- **Phase 3**: **DONE** — All 6 infra changes deployed (dialer mapping, intake poller campaign tags, enqueue dedup, dequeue bugfix + routing, callback trackedAssistants, Config includeOtherFields)
- **Phase 4**: **READY FOR QUALITY GATE** — Active queue is now imported-pool-only. Dialer and intake poller remain paused. 4 imported-pool seed rows are pending (`Oxa0BTBbPi6JkPXGQIeT`, `2AthxJS3uMoGWxnVU9v7`, `FA2Cd923b7YzmJBdfByX`, `DkDogBpdJhH1gX8pauNP`). 5 legacy non-imported campaign rows were moved to `failed` to keep the first batch isolated.
- **Supporting helper**: Queue feeder workflow hardened to require both campaign tag and matching imported-pool tag. `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) added for the readiness, backfill, audit, queue audit, and isolation SQL.
- **Dedup confirmed**: classifier, feeder, enqueue, and dequeue all block duplicate calls per contact. Do not enable intake poller or V1 dialer until after the manual assistant quality gate.

### 1A. Imported Pool Go-Live Prep (DONE 2026-07-03)

- Repo-side prep is complete for the imported Brand/Dispensary pool go-live.
- Prepared assets:
  - `postgres/emerging-pool-go-live-check.sql`
  - `postgres/check-emerging-pool-import-readiness.sql`
  - `postgres/backfill-emerging-pool-ghl-ids.sql`
  - `postgres/audit-emerging-pool-linkage.sql`
  - `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`
  - `postgres/select-emerging-pool-vapi-candidates.sql`
  - `postgres/select-vapi-seed-test-batch.sql`
  - `classifier-repair-plan.md`
  - `classifier-workflow-change-plan.md`
  - `classifier-workflow-patch-snippets.md`
  - `classifier-workflow-mcp-update-ops.md`
  - `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
  - `emerging-pool-post-import-runbook.md`
  - `live-mutation-plan.md`
  - `rollback-checklist-vapi-emerging-pool.md`
  - `execution-checklist-after-import.md`
- **All SQL assets updated to match custom fields by stable field id (`R0wbDRyzZz34PMlQSRWN` / `ILurFacMbAaHz2DdGjPa`) in addition to name, so the imported-pool linkage survives the GHL custom-field shape change.**
- **Next move is operational, not data-side**: manual assistant quality gate, then controlled queue-driven call test. Do not enable intake poller or V1 dialer yet.

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
````

## File: QWEN.md
````markdown
# LiveTransparent Project

## Project Overview

LiveTransparent is a marketing automation and CRM operations platform for a B2B compliance advertising agency focused on regulated cannabis marketing. The project orchestrates lead intake, warm lead routing, cold outreach, and email sequence campaigns using a combination of:

- **n8n** - Workflow automation engine (public URL: `https://automations.livetransparent.com`)
- **GoHighLevel (GHL)** - CRM and sequence delivery platform
- **PostgreSQL** - Contact storage, release logs, and company research cache
- **BookStack** - Internal knowledgebase (prepared, not yet deployed)

The system is deployed on a VPS using **Coolify** with Docker Compose services connected over a shared internal network (`coolify-shared`).

### Core Capabilities

1. **Warm Lead Intake** - Multi-channel webhook intake (LinkedIn, Meta, Email, SMS, Referral, Website forms) with automatic tagging and routing into CRM pipelines
2. **Cold Outreach** - Apollo-enriched contact ingestion with sender-capped dispatch and timezone-aware delivery
3. **Email Sequence Campaigns** - A/B tested sequences (e.g., Cannabis Ads, Emerald campaign) with GHL workflow delivery
4. **Company Research** - AI-powered company enrichment cached in Postgres for personalized email content
5. **RB2B Integration** - Website visitor identification with GHL reconciliation and follow-up task creation

## Directory Structure

```
LiveTransparent/
├── n8n/                              # n8n service Docker Compose and config
│   ├── docker-compose.yml
│   └── nodes/                        # Service reference docs (Apollo, GHL, Twilio)
├── postgres/                         # PostgreSQL service definition
│   └── docker-compose.yml
├── bookstack/                        # Internal knowledgebase (staged for deployment)
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
├── scripts/                          # Operational scripts and helpers
│   ├── rerun_bad_emerald_sso_companies.py
│   └── patch_simpletexting_callbacks.py
├── emerald-email-campaign/           # Emerald campaign workspace
│   ├── plan.md
│   ├── dispatcher-plan.md
│   ├── workflow-mapping.md
│   └── Exported Emerald Contacts.csv
├── Emerald Contacts/                 # Emerald source CSV merger and import generator
│   ├── build_ghl_import.py
│   └── README.md
├── cold-outreach-prep/               # Cold outreach workbook processing
│   ├── prepare_cold_outreach.ps1
│   ├── ghl/                          # GHL import CSVs
│   ├── postgres/                     # Postgres ingest CSVs
│   └── reports/                      # Validation and duplicate reports
├── GHL Live Transparent CRM/         # GHL process docs and runbooks
│   ├── Pipeline_Quick_Reference.md
│   ├── Cannabis_Ads_Sender_Routing_Runbook.md
│   └── RB2B_Website_Visitor_Intake_Workflow.md
├── Marketing Docs/                   # Brand voice, ICP, and segment strategy
│   ├── Transparent_eCom_Brand_Voice_And_Foundation.docx
│   ├── Transparent_eCom_Core_Customer_ICP.docx
│   └── Transparent_eCom_Strategic_Priority_Segments.docx
├── EMAIL templates/                  # Email sequence HTML templates
├── ghl create sequence plan/         # Sequence build specs and A/B rollout artifacts
├── Backup of all n8n workflows/      # Full n8n workflow JSON backups
├── AGENTS.md                         # Agent rules and operational notes (source of truth)
└── QWEN.md                           # This file
```

## Building and Running

### Docker Services (Coolify Deployment)

All services are deployed via Coolify using Docker Compose. Local development is not the primary workflow; changes are pushed to the repo and deployed through Coolify.

**n8n Service** (`n8n/docker-compose.yml`):
```bash
# Deployed via Coolify with:
# - Image: n8nio/n8n:2.9.4
# - Public host: automations.livetransparent.com
# - Internal network: coolify-shared
# - Postgres backend
```

**PostgreSQL Service** (`postgres/docker-compose.yml`):
```bash
# Deployed via Coolify with:
# - Image: postgres:17.7
# - Internal network: coolify-shared
# - Persistent volume: postgres_data
```

**BookStack Service** (`bookstack/docker-compose.yml`):
```bash
# Staged for deployment (not yet live)
# - Internal knowledgebase restricted to team access
# - MariaDB backend
# - Traefik routing via Coolify
```

### Operational Scripts

**PowerShell - Cold Outreach Prep**:
```powershell
# Process Cold-outreach contacts.xlsx into GHL/Postgres import CSVs
.\cold-outreach-prep\prepare_cold_outreach.ps1
```

**Python - Emerald Cache Reset**:
```powershell
# Create temporary reset workflow for bad cache rows
python scripts/rerun_bad_emerald_sso_companies.py create [company_keys...]

# Delete temporary workflow after execution
python scripts/rerun_bad_emerald_sso_companies.py delete <workflow_id>
```

### n8n Workflow Management

**Direct REST API** (verified working from Windows):
```bash
# Get workflow
curl -H "X-N8N-API-KEY: <key>" "https://automations.livetransparent.com/api/v1/workflows/<id>"

# Update workflow (minimal payload)
curl -X PUT -H "X-N8N-API-KEY: <key>" -H "Content-Type: application/json" \
  -d '{"name":"...","nodes":[...],"connections":{...},"settings":{}}' \
  "https://automations.livetransparent.com/api/v1/workflows/<id>"
```

**MCP Tools** (via Codex):
- Use `n8n-lt` MCP for workflow discovery, activation checks, and execution
- Use `ghl_official` MCP for GHL data reads
- Use `ghl_workflows` MCP with caution (some endpoints may fail with scope errors)

## Key Configuration Files

### Environment Variables

- **Root `.env`** - Shared credentials (not tracked in git)
- **`n8n/.env`** - n8n-specific secrets (encryption key, DB password)
- **`bookstack/.env.example`** - BookStack environment template

### Service References

- **`n8n/nodes/apollo/REFERENCE.md`** - Apollo API endpoint mapping
- **`n8n/nodes/ghl/REFERENCE.md`** - GHL API endpoint mapping
- **`n8n/nodes/twilio/REFERENCE.md`** - Twilio API endpoint mapping

## Development Conventions

### Workflow Update Pattern

1. **Verify first** - Use `n8n-lt` MCP to read current workflow state
2. **Build locally** - Construct full `nodes` and `connections` arrays locally
3. **Direct REST for large changes** - Use `PUT /workflows/{id}` with minimal payload (`name`, `nodes`, `connections`, `settings`)
4. **Verify after** - Re-read workflow and confirm `active`, `defaultDryRun`, and changed parameters

### GHL Integration Rules

- **Field naming** - Use exact GHL custom field names (e.g., `marketing_sender_email`, `Apollo Phone Enrichment Status`)
- **Tag hygiene** - Tags are appended non-destructively; removal requires explicit action
- **Pipeline stages** - Reference by ID, not name (see `AGENTS.md` for locked pipeline map)
- **Direct API fallback** - If MCP fails with scope errors, test endpoint directly against `https://services.leadconnectorhq.com`
- **LinkedIn supply path** - For the LinkedIn connection-request queue, use the working GHL `contacts/` list endpoint and filter locally by LinkedIn URL custom fields and tags. Treat `contacts/search` failures against private-integration tokens as a live blocker, not a harmless empty result.

### Data Processing

- **CSV imports** - Dedupe by email first, then name/company, then phone
- **Snake case conversion** - Postgres columns use snake_case (handled by `prepare_cold_outreach.ps1`)
- **Timezone handling** - Contact-local dispatch with explicit timezone resolution order
- **Dry-run discipline** - Keep `defaultDryRun=true` for staged workflows until ready for production

### Marketing Copy Alignment

Before drafting or revising contact-facing copy, reference:
- **Brand voice** - `Marketing Docs/Transparent_eCom_Brand_Voice_And_Foundation.docx`
- **ICP** - `Marketing Docs/Transparent_eCom_Core_Customer_ICP.docx`
- **Segments** - `Marketing Docs/Transparent_eCom_Strategic_Priority_Segments.docx`

Flag conflicts with these docs before proceeding.

## Active Workflows (Snapshot)

See `AGENTS.md` for the authoritative, up-to-date workflow inventory. Key production workflows include:

| Workflow | ID | Status |
|----------|-----|--------|
| Website Lead Intake (Hero) | `RTV5jUiTt05lad07` | Active |
| Website Lead Intake (Footer) | `RSfLF7LU0rDC4jAI` | Active |
| GHL Apollo Phone Enrichment - Callback Handler V4 | `U7c6byTLXAMgcS75` | Active |
| LT - Cold Outreach Sender Release Dispatcher | `NTpQnMrpjzusPXHX` | Active |
| LT - Emerald Campaign Sender Release Dispatcher | `8UXlpoMJnQ229AuG` | Active |
| rb2b leads | `3kjsIUeoEQFx26cC` | Active |
| WL - Webhook to Slack Channel Update | `lQTW0QPwBcf3o7j8` | Active |

## GHL Pipelines (Locked Map)

### Warm Pipeline
`New` → `Qualified (MQL)` → `Routed to Outreach` → `Nurture Active` → `Disqualified`

### Sales Outreach Pipeline
`New` → `Attempting Contact` → `Engaged` → `Meeting Requested` → `Booked` → `Unresponsive`

### Sales Pipeline
`Discovery Scheduled` → `Discovery Completed` → `Proposal Sent` → `Negotiation` → `Closed Won` → `Closed Lost`

## Important Operational Notes

1. **Status freshness** - Treat all "Current" / "Active" status items in `AGENTS.md` as "last known state" and re-verify in-system before acting
2. **TLS/schannel on Windows** - Direct `curl.exe` to HTTPS endpoints may fail; use Python `requests` or Node `fetch` for API verification
3. **MCP mutation limits** - If `n8n-lt` mutation helpers fail or ignore `active`, switch to direct REST API
4. **Emerald campaign** - Use Postgres table `Emerald_Campaign_Contacts` as dispatch source, not live GHL smart lists
5. **Sender caps** - Week 1: 300/day, Week 2: 400/day, Week 3+: 500/day (total outbound per sender, including in-flight sequence sends)

## Related Documentation

- **`AGENTS.md`** - Comprehensive agent rules, workflow status, and operational notes (source of truth)
- **`GHL Live Transparent CRM/Pipeline_Quick_Reference.md`** - Pipeline stage definitions and movement rules
- **`emerald-email-campaign/plan.md`** - Emerald campaign architecture and locked decisions
- **`bookstack/README.md`** - BookStack deployment instructions
- **`Project Status and Next Steps.md`** - Canonical live state plus the current LinkedIn troubleshooting handoff
````

## File: rollback-checklist-vapi-emerging-pool.md
````markdown
# Rollback Checklist: Emerging Pool Classifier And Queue Feeder

## Use When

Use this if the first imported Brand / Dispensary cohort behaves incorrectly after classifier tagging or queue staging.

## Common Rollback Triggers

- wrong contacts received `vapi_campaign_brand` or `vapi_campaign_dispensary`
- executive or unrelated contacts appear in the cohort
- queue feeder stages contacts that should have been excluded
- too many contacts were tagged in the first pass
- queue rows appear for contacts outside the intended seed batch

## Immediate Containment

1. Do not activate the paused dialer or intake poller.
2. If classifier tags were just applied, stop before re-running `RFIZ9Bcfl3Yvms2b`.
3. If the feeder already ran, do not activate downstream calling.

## Rollback Actions

### 1. Remove accidental campaign tags from GHL contacts

Remove:
- `vapi_campaign_brand`
- `vapi_campaign_dispensary`

Only from the accidentally tagged cohort.

### 2. Clean staged queue rows for that cohort

For seed-batch rollback, target only:
- `campaign_id IN ('brand', 'dispensary')`
- rows created from the bad cohort
- `status = 'pending'`

Do not mass-delete or change historical completed rows.

### 3. Re-check `voice_call_attempt`

Verify no live calls were placed.

If no attempts exist, rollback remains low-risk.

### 4. Disable classifier rerun path

Until fixed:
- do not manually rerun `IduCoT5YOs0g2faT`
- do not let the feeder re-stage the same contacts blindly

## Root Cause Review

Check these in order:

1. `postgres/select-emerging-pool-vapi-candidates.sql`
2. `postgres/select-vapi-seed-test-batch.sql`
3. `IduCoT5YOs0g2faT` live SQL and Code nodes
4. `RFIZ9Bcfl3Yvms2b` manual execution output
5. actual GHL tags on affected contacts

## Safe Resume Criteria

Do not resume until all are true:
- the candidate query returns only expected Brand / Dispensary rows
- the first 5+5 seed batch is manually approved
- accidental tags are removed
- accidental queue rows are cleared or neutralized
- classifier cap remains in place for the retry

## Practical Rule

For the first imported-pool rollout, rollback should be surgical:
- remove wrong tags
- neutralize wrong pending queue rows
- fix classifier selection
- retry only with a tiny reviewed cohort
````

## File: Sales and Marketing Roadmap.md
````markdown
# Sales and Marketing Roadmap

## KPI Framework

### Lead Generation
- Qualified outbound leads per week
- Open / response rates in sequences
- Appointment show rate

### Next Week Report Plan
- Add sequence-event ingest so we can show real sequence performance instead of only enrollments.
- Tighten landing-page and form tracking so we can trust the matched funnel by landing page.
- [x] Show a short summary of the most visited pages on the website using the landing-page rollup we already have.

### Conversion
- Lead → MQL → SQL conversion rate
- SQL → Proposal → Close rate
- Pipeline velocity (days between stages)
- Stage-by-stage opportunity movement (moved-in / moved-out per stage)
- Opportunity cycle length (days from first stage to close)

### Operational Efficiency
- % of outbound automated vs manual
- Lead scoring accuracy (hit rate among top scores)
- Sales cycle length changes

### Revenue Impact
- Pipeline contribution per month
- ROI of tools + sequences

---

## Current State

| System | Status |
|--------|--------|
| GoHighLevel (GHL) | Production — CRM, pipeline, routing, reporting |
| Apollo.io | Production — enrichment, outbound sequences |
| Meta Ads API | Validated — attribution-first reporting live |
| GA4 | Live — sessions, channels, engagement |
| GSC | Live — Search Console clicks, impressions, CTR, position |
| Clay | Planned — Phase 2 |
| n8n Orchestration | Production — all report workflows active |

---

## Executive Report Data Sources

The executive report (`reports/embed/executive/index.html`) surfaces data from:

| Source | Workflow | Data |
|--------|----------|------|
| GHL Contacts | `LT - GHL Daily Leads Ingest` | Contacts, UTM fields, warm source, routing metadata |
| GHL Opportunities | `LT - GHL Daily Sales Ingest` | Pipeline stages, closed-won revenue |
| GHL Calls | `LT - GHL Daily Calls Ingest` | Voice call logs: status, direction, duration |
| GHL Appointments | `LT - GHL Daily Appointments Ingest` | Calendar events: booked, showed, no-show |
| GA4 Sessions | `LT - GA4 Daily Ingest` | Sessions, users, engagement by channel/landing page |
| GSC Search | `LT - GSC Daily Ingest` | Clicks, impressions, CTR, average position, queries, pages |
| Attribution Bridge | `LT - Report Attribution Bridge` | Traffic → contact matching |
| Daily Rollups | `LT - Report Daily Rollups` | Aggregated summary, channel, UTM, landing page tables |
| Executive API | `LT - Report Executive Summary API` | JSON served to embed via n8n webhook |

### GHL Custom Fields Captured for Reporting
- `UTM Source First/Last`, `UTM Medium First/Last`, `UTM Campaign First/Last`, `UTM Content First/Last`, `UTM Term First/Last`, `UTM Landing Page First/Last`
- `Warm Source`, `Warm Trigger Type`, `Lead Temperature`
- `LT Last Routing Channel`, `LT Last Routing Reason`, `LT Last Routed At`
- `LT Route Lock Until`, `LT Routing Priority`, `LT Last Event Fingerprint`, `LT Last Event At`

---

## Active Pipelines

| Pipeline | Stages |
|----------|--------|
| Warm | New → Qualified (MQL) → Routed to Outreach → Nurture Active → Disqualified |
| Sales Outreach | New → Attempting Contact → 2nd attempt → 3rd attempt → Engaged → Meeting Requested → Booked → Unresponsive |
| Sales | Discovery Scheduled → Discovery Completed → Proposal Sent → Negotiation → Closed Won / Closed Lost |

---

## Phase 1 — Live (Now → +90 days)

### Stack
- **GHL** — CRM, pipeline, routing, warm lead management
- **Apollo.io** — Enrichment, outbound sequences, SDR motion
- **Meta Ads** — Attribution-first reporting via GA4 UTM + GHL bridge
- **n8n** — All ingestion, bridge, rollup, and alerting orchestration

### Why GHL + Apollo
- Faster hiring (reps can operate in one tool)
- Faster pipeline (built-in routing eliminates manual handoffs)
- Lower cognitive load (scoring + routing automated)
- Gets reps + ops aligned quickly

### What to Test
- Messaging variants per vertical
- Offer framing by company size / industry
- Channel routing (which warm sources convert best)

### Key Constraints
- Enforce quality filters: titles, industries, revenue bands
- Don't let Apollo become spammy — enforce cadence limits
- Use GHL scoring + routing immediately — don't manual-tag

---

## Phase 2 — Planned (Once outbound proves ROI)

### Add Clay — precision layer on top of Apollo

Clay handles:
- Enterprise / strategic accounts
- Founder-led brands
- Platforms, MSOs, aggregators
- High-intent, high-context outreach

Apollo continues doing:
- Broad outbound
- SDR motion
- Volume coverage

### Clay Use Cases
- "Top 500 cannabis brands" — targeted account list
- "Brands spending on Meta but blocked" — retargeting pool
- "Recently funded alternative wellness brands" — funded signal

---

## Deferred / Blocked

| Item | Status | Notes |
|------|--------|-------|
| GSC Daily Ingest | Active | Search Console access granted; workflow healthy |
| Meta Ads raw spend ingest | Deferred | Attribution-first path live; spend reporting deferred |
| Clay integration | Planned Phase 2 | Not started |
| Matched funnel by landing page | Planned | Needs tighter landing-page and form tracking first |
| Sequence event performance | Planned next week | Need open, reply, click, bounce, and unsubscribe events from Apollo sequences |
| GHL → LinkedIn automation | Planned | LinkedIn connect dispatcher active; full workflow deferred |
| GHL Calls & Appointments Ingest | Active | Appointments ingest live (`yWZVSqEcjTbMT3kG`, calendar `SrtXcFVyea7pFl3nTiIK`); Calls ingest live from GHL Conversations |
| Pipeline stage velocity (days per stage) | Active | `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`) calculates this by combining pipeline history events with the previous stage record for each opportunity |

---

## Report Data Contract

Minimum v1 output from the executive report:
- [x] GA4 sessions by channel
- [x] GA4 landing pages
- [x] GHL contacts created
- [x] GHL opportunities created
- [x] GHL closed-won revenue
- [x] Funnel efficiency rates (session→contact, contact→opp, opp→meeting, meeting→won)
- [x] Attribution coverage rates (source fields, bridge match, sale match)
- [x] Meta attribution panel (GA4 UTM + GHL bridge)
- [x] Pipeline stage velocity (avg days per stage, per-opp timeline)
- [x] Sales Detail panel (win rate, deals by stage, pipeline value)
- [x] GSC clicks and impressions
- [ ] Meta raw spend/clicks/impressions (deferred)
- [ ] Matched funnel by landing page (after tracking is tightened)
- [ ] Sequence event performance (opens, replies, clicks, bounces, unsubscribes)

### Pipeline Movement Tracking

| Metric | Status | Notes |
|--------|--------|-------|
| Stage counts by day | Working | `report_stage_daily_summary.stage_count` |
| Moved-in count | Working | Computed via LAG window comparing previous day's stage count |
| Moved-out count | Working | Computed via LAG window comparing previous day's stage count |
| Won/lost counts | Working | From opportunity status mapping |
| Pipeline history raw events | Captured | `report_raw_ghl_pipeline_history` table populated by GHL Daily Sales Ingest |
| Stage-by-stage velocity | Live | Computed by `LT - Report Pipeline Velocity` using pipeline history events plus the previous stage for each opportunity; writes to `report_stage_velocity_summary` and `report_opp_stage_timeline` |
| Opportunity cycle length | Live | Now computed from actual event timestamps via `report_opp_stage_timeline.days_in_stage` |
| True stage transition timestamps | Live | `report_opp_stage_timeline` has `entered_at` / `exited_at` per opportunity per stage |

**Resolved**: Pipeline velocity (avg days between stages) is now computed from actual pipeline history event timestamps by `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`). The workflow uses a query that compares each stage event to the previous stage event for the same opportunity, then writes to `report_stage_velocity_summary` (14 stages across 3 pipelines) and `report_opp_stage_timeline` (50,522 rows). Runs daily at 24h interval.

Additional reporting requests that would be sub sections under the main section and can be covered in calls more in depth by team leads
Sales (john)
- Total calls by status → Available via `report_raw_ghl_calls` and the Calls & Conversations panel in the Executive Report
- Total meetings and if they showed → Available via `report_raw_ghl_appointments` (ingested by `LT - GHL Daily Appointments Ingest`, calendar `SrtXcFVyea7pFl3nTiIK`)
- Contract closed and pending → Available via Sales Detail panel and Deal Stage Pipeline in executive report
- Win rate (closed won / closed total) → Available in Sales Quality panel

Social and site (chella)
- Social engagement: comments, reactions etc. → Needs Meta/Facebook Graph API (not in GHL)
- Website visits and traffic source → Already available via GA4 + channel breakdown
- Interactions on website: page visited, form fills etc. → Already available via GA4 landing pages + GHL forms

Next-week follow-up
- Sequence reporting → add event-level ingest for opens, replies, clicks, bounces, and unsubscribes so the report shows sequence performance, not just enrollments.
- Landing pages → preserve page URL and UTM fields consistently on every link and form so a matched funnel by landing page becomes reliable.
- Website pages → show the most visited pages as a short summary using the landing-page rollup while the deeper funnel tracking is being tightened.
````

## File: sms_edited_templatekeys.md
````markdown
# SMS Edited Template Keys

This document lists the current SMS template keys and the full message bodies currently used in the workflow.

The keys stay unchanged. Only the message text was updated to remove literal `cannabis` wording and shift the copy toward `regulated industries`.

## John SMS

### `john_sms1`

```text
Hi, John from Transparent eCom, just gave you a call. Saw you were interested in learning about ads for regulated industries on social/search.

We run ads for Mood, Cookies, and more! Interested in learning how?
```

### `john_sms2`

```text
Hey {{first_name}}! John from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

I can show you how top regulated-industry brands are doing it in 10 mins.
```

### `john_sms3`

```text
Hi {{first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?
```

### `john_sms4`

```text
Hi {{first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We're onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

### `john_sms4`

```text
Hi {{first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We're onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

### `john_sms2`

```text
Hey {{contact.first_name}}! John from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

I can show you how top regulated-industry brands are doing it in 10 mins.
```

### `john_sms3`

```text
Hi {{contact.first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?
```

### `john_sms4`

```text
Hi {{contact.first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We're onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

### `john_sms2`

```text
Hey {{contact.first_name}}! John from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

I can show you how top regulated-industry brands are doing it in 10 mins.
```

### `john_sms3`

```text
Hi {{contact.first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?
```

### `john_sms4`

```text
Hi {{contact.first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We're onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

### `john_sms2`

```text
Hey {{contact.first_name}}! John from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

I can show you how top regulated-industry brands are doing it in 10 mins.
```

### `john_sms3`

```text
Hi {{contact.first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?
```

### `john_sms4`

```text
Hi {{contact.first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We're onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

### `john_sms2`

```text
Hey {{first_name}}! John from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

I can show you how top regulated-industry brands are doing it in 10 mins.
```

### `john_sms3`

```text
Hi {{contact.first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?
```

### `john_sms4`

```text
Hi {{contact.first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?
```

### `john_sms5`

```text
Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.

We’re onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}
```

## Cameron / Regulated Industry SMS

### `sms_1`

```text
Hi - thanks for checking out ads for regulated industries on social/search.
I'm Cameron, founder of Transparent eCom. We help regulated industries run ads that most agencies can't, including Mood, Cookies, and Lucy.

Quick question - are you currently running ads, restricted from advertising, or just exploring options?
```

### `sms_2`

```text
Hey, Cameron again.
If you're curious, our site has free walkthroughs on how brands run ads in regulated industries on platforms like Meta and Google.

Some companies do it themselves - totally fine. But we also have a few capabilities most brands and agencies don't that allow actual product advertising at scale.
Want me to send it over?
```

### `sms_3`

```text
Quick follow up -
We've helped brands like Mood, Lucy, and GPen scale ads profitably in regulated spaces.
Happy to show you how they're doing it if that would be helpful.
```

### `sms_4`

```text
Fun fact:
We can run actual flower and pre-roll ads with regulated-industry mentions directly in the ad.
Here's an example (you'll need to be logged into Facebook to preview):
https://fb.me/adspreview/facebook/1SsU73bjDHg0XY1
```

### `sms_5`

```text
If you're a dispensary, this might be interesting:
We can track when someone clicks or views a social/search ad and then purchases in-store.
That's been a game changer for dispensaries measuring real ROI from digital ads.
```

### `sms_6`

```text
Hey - Cameron again.
I don't want to keep bothering you, so this will be my last message.
If you ever want to learn how brands are running regulated ads on social/search, just reply here and I'm happy to help.
```

## Emerald Intro Templates

### `emerald_mso_executive_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Most regulated-industry brands still cannot properly run Meta ads - we help teams get live through compliant accounts and keep them running without constant restrictions. Let me know if this is relevant.
```

### `emerald_mso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Most teams still cannot fully run paid social - we help marketing teams get live and keep campaigns running without disruption. Let me know if this is relevant.
```

### `emerald_mso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Many still cannot fully use paid social as a revenue channel - we help teams unlock and maintain it reliably. Let me know if this is relevant.
```

### `emerald_mso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. When Meta ads go down, traffic and sales usually drop too - we help teams get live and keep things running without constant restrictions. Let me know if this is relevant.
```

### `emerald_sso_executive_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where teams have to reset more often than they should when ads get interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where campaigns get interrupted mid-execution, causing teams to lose momentum. Let me know if this sounds familiar.
```

### `emerald_sso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where revenue becomes uneven when advertising gets interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where interruptions in advertising quietly create gaps in traffic and conversions. Let me know if this is something you have noticed.
```

### `emerald_mso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Most teams still cannot fully run paid social - we help marketing teams get live and keep campaigns running without disruption. Let me know if this is relevant.
```

### `emerald_mso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Many still cannot fully use paid social as a revenue channel - we help teams unlock and maintain it reliably. Let me know if this is relevant.
```

### `emerald_mso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. When Meta ads go down, traffic and sales usually drop too - we help teams get live and keep things running without constant restrictions. Let me know if this is relevant.
```

### `emerald_sso_executive_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where teams have to reset more often than they should when ads get interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where campaigns get interrupted mid-execution, causing teams to lose momentum. Let me know if this sounds familiar.
```

### `emerald_sso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where revenue becomes uneven when advertising gets interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where interruptions in advertising quietly create gaps in traffic and conversions. Let me know if this is something you have noticed.
```

### `emerald_mso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Most teams still cannot fully run paid social - we help marketing teams get live and keep campaigns running without disruption. Let me know if this is relevant.
```

### `emerald_mso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. Many still cannot fully use paid social as a revenue channel - we help teams unlock and maintain it reliably. Let me know if this is relevant.
```

### `emerald_mso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. When Meta ads go down, traffic and sales usually drop too - we help teams get live and keep things running without constant restrictions. Let me know if this is relevant.
```

### `emerald_sso_executive_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where teams have to reset more often than they should when ads get interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_marketing_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where campaigns get interrupted mid-execution, causing teams to lose momentum. Let me know if this sounds familiar.
```

### `emerald_sso_finance_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where revenue becomes uneven when advertising gets interrupted. Let me know if this sounds familiar.
```

### `emerald_sso_retail_sales_intro`

```text
Hi {{first_name}}, Cameron from Transparent eCom. We have seen cases where interruptions in advertising quietly create gaps in traffic and conversions. Let me know if this is something you have noticed.
```

## Notes

- The template keys were left unchanged on purpose.
- Any future copy update should change the message text only, unless the n8n workflow mappings are also updated.
- The John and Cameron message sets are the only ones that were edited for wording.
````

## File: Unipile_potential_automations.md
````markdown
# Unipile Potential Automations

These are potential automations we want to do using Unipile for our regulated-industry advertising business.

---

## 1. InMail Campaigns

**Purpose:** Send sponsored LinkedIn messages directly to prospects who aren't connected.

**Use Case:** Great for reaching decision-makers who don't accept connection requests.

**Implementation:**
- Build a GHL automation that triggers when a new lead enters the system
- Send an InMail campaign with a personalized message
- Track responses and tag leads based on engagement

---

## 2. List Building & Enrichment

**Purpose:** Search LinkedIn for ideal prospects and enrich them with contact info.

**Use Case:** Find marketing directors at cannabis brands, CBD companies, or other regulated industries.

**Implementation:**
- Create a scheduled workflow that searches for targets by title/industry
- Enrich profiles with email, phone, company size
- Auto-create/update GHL contacts with enriched data
- Tag by campaign stage and priority score

---

## 3. Competitor Audience Targeting

**Purpose:** Find people who follow or engage with competitor pages.

**Use Case:** Target prospects who are already interested in regulated-industry advertising solutions.

**Implementation:**
- Monitor competitor LinkedIn pages for followers
- Build targeted outreach lists from engaged users
- Send personalized messages highlighting our unique capabilities
- Track conversion rates vs. cold outreach

---

## 4. Event-Based Outreach

**Purpose:** Trigger outreach when prospects post about challenges or attend events.

**Use Case:** Reach out when someone posts about "getting banned from Meta ads" or industry events.

**Implementation:**
- Monitor LinkedIn for keywords like "restricted", "banned", "compliance"
- Trigger automated outreach within 24 hours
- Personalize message based on their specific pain point
- Schedule follow-up tasks in GHL

---

## 5. Multi-Step Sequences

**Purpose:** Automate a 3-5 step sequence with timed follow-ups.

**Use Case:** Connection → follow-up message → InMail → break-up message.

**Implementation:**
- Day 0: Send connection request
- Day 3: If accepted, send follow-up message
- Day 7: If no response, send InMail
- Day 14: If still no response, send break-up message
- Track acceptance/response rates at each stage

---

## 6. Lead Scoring & Prioritization

**Purpose:** Score prospects based on profile signals.

**Use Case:** Prioritize hot leads for manual follow-up.

**Implementation:**
- Score based on job seniority (executive = high score)
- Score based on company size (larger = higher score)
- Score based on engagement rate (active poster = higher score)
- Auto-route high-score leads to sales team in GHL
- Low-score leads go into nurture sequence

---

## 7. CRM Sync & Tagging

**Purpose:** Auto-create/update GHL contacts and track engagement history.

**Use Case:** Keep GHL in sync with LinkedIn outreach activities.

**Implementation:**
- Webhook listener for Unipile events (connection accepted, message replied)
- Auto-create GHL contact if not exists
- Tag by campaign stage (connected, replied, scheduled, etc.)
- Log all outreach history in GHL notes
- Trigger GHL automations based on engagement

---

## 8. A/B Testing Message Variations

**Purpose:** Test different hooks and automatically route better performers.

**Use Case:** Test "Mood case study" vs. "compliance guarantee" messaging.

**Implementation:**
- Create multiple message variants in template registry
- Split outreach 50/50 to test groups
- Track acceptance/response rates per variant
- Auto-switch to winner after statistical significance
- Log results in GHL for future reference

---

## 9. Analytics & Attribution Dashboard

**Purpose:** Track connection acceptance rates, response rates, and downstream conversions.

**Use Case:** Measure ROI of LinkedIn outreach campaigns.

**Implementation:**
- Export Unipile metrics to Postgres or BigQuery
- Build dashboard showing:
  - Connections sent / accepted rate
  - Response rate by message variant
  - Meetings booked from LinkedIn
  - Leads created from LinkedIn
  - Revenue attributed to LinkedIn
- Sync metrics to GHL reports

---

## 10. Team Account Management

**Purpose:** Manage multiple LinkedIn accounts with centralized reporting.

**Use Case:** One account for John, one for Cameron, one for sales team.

**Implementation:**
- Use Unipile's team features for multiple accounts
- Centralized reporting dashboard
- Permission-based access (sales vs. marketing)
- Auto-rotate accounts to avoid rate limits
- Track performance per account/rep

---

## Bonus: GHL Automation Integration

**Purpose:** Trigger GHL automations based on Unipile events.

**Use Case:** Automatically move leads through sales pipeline.

**Implementation:**
- Webhook endpoint in GHL for Unipile events
- On connection accepted: Add to "Hot Lead" campaign
- On message replied: Schedule follow-up call task
- On meeting booked: Create calendar event + send prep email
- On no response after X days: Add to nurture sequence

---

## Next Steps

1. **Priority 1:** Implement CRM Sync & Tagging (already partially done via webhook)
2. **Priority 2:** Build Multi-Step Sequences for John's outreach
3. **Priority 3:** Set up Lead Scoring & Prioritization
4. **Priority 4:** Create Analytics Dashboard for ROI tracking

Each automation can be implemented incrementally, starting with the webhook infrastructure already in place.

## Implementation Order

1. Ship the Instagram DM workflow first so the team has a dedicated Unipile-backed sequence for mutual followers and follow-backs.
2. Reuse the same message registry concept for LinkedIn, but keep LinkedIn as a separate variant layer so step timing and audience rules stay isolated by channel.
3. After the Instagram flow is stable, extract the shared copy registry so LinkedIn and Instagram can read from the same template source without sharing state.
````

## File: vapi-campaign-prompts-summary.md
````markdown
# Brand Campaign (Alex)
Vapi.ai Configuration — Brand Outreach Campaign
Dispensary Attribution Network — selling cannabis brands into the network

Identity
You are Alex, a partnerships specialist at Transparent eCom, calling on behalf of
the new Dispensary Attribution Network. You are NOT a generic sales bot — you
speak like someone who understands cannabis marketing specifically (CPMs, ROAS,
shelf placement, the attribution gap between digital ad spend and retail sales).
Voice / Persona
Confident, consultative, peer-to-peer (talking to a brand's marketing/growth lead, not a consumer)
Pace: moderate, comfortable with brief silence while prospect thinks
Recommend an ElevenLabs voice in the "professional, warm, mid-30s" range — avoid anything that sounds like a call center
First Message
Hey, this is Alex calling from Transparent eCom — is this {{contact_name}}?
... Got a quick 90 seconds? We just launched something that closes the loop
between your Meta and Google ad spend and actual in-store dispensary sales —
wanted to see if it's relevant to {{company_name}}.
System Prompt — Six-Section Structure
1. Role & Objective
Qualify the brand and book a strategy call. You are not closing the deal on this call — you are pre-qualifying and getting a calendar booking. Do not over-promise specific ROI numbers; the deck's stats (40% ad approval increase, 16mo retention) are about Transparent's agency track record, not a guarantee for this specific brand.
2. Discovery Questions (ask before pitching)
What's your current ad spend split across Meta/Google?
Are you running into ad account suspensions or compliance blocks right now?
Do you know which dispensaries actually move your product, or is that a black box?
What markets matter most to you right now? (maps to "Your Markets First" in the deck)
3. Pitch Structure (only after discovery — don't lead with this)
Problem: ad spend ≠ sales proof, dispensaries don't share data, can't justify budget upward
Solution: geo-targeted Meta/Google ads around partner dispensaries + real-time in-store purchase attribution via compliance ad accounts
Proof point: 16-month average client retention, 40% higher ad approval rate vs standard accounts
Important: this is currently launching in test markets only — be honest about that, don't oversell national availability
4. Objection Handling
"We already run ads" → "This isn't replacing your media buy, it's closing the loop on attribution you don't have today."
"Is this compliant?" → "Yes — we run through exclusive compliance ad accounts, no blurring or workarounds, which is the whole reason brands work with us."
"What's it cost?" → Do not quote pricing on the call. Say: "Pricing depends on markets and spend level — that's exactly what the strategy call covers."
"Not interested" → Thank them, do not push twice, log as not-interested in structured output.
5. Call-to-Action
Book a strategy call. If a calendar tool is connected, offer 2-3 specific times. If not, confirm best email/number for a follow-up booking link.
6. Guardrails
Never make specific ROI or revenue guarantees
Never discuss specific pricing — defer to strategy call
Never give legal/compliance advice about the prospect's own ad accounts — that's a human conversation
If asked "are you an AI?" — answer honestly, immediately. Do not deny it.
If prospect asks to be removed from the call list — confirm immediately, do not re-pitch, log it.
Keep total call under 4 minutes unless prospect is actively engaged
Structured Output Schema
{
  "company_name": "string",
  "contact_name": "string",
  "current_ad_platforms": "string",
  "current_monthly_ad_spend_range": "string",
  "has_compliance_issues": "boolean",
  "target_markets_mentioned": "array",
  "interest_level": "enum: hot | warm | not_interested | callback_requested",
  "objections_raised": "array",
  "booked_strategy_call": "boolean",
  "do_not_call": "boolean",
  "call_summary": "string"
}
Dynamic Variables
Pass via assistantOverrides.variableValues on each call: contact_name, company_name, lead_source (helps track which list converted)

Shared Setup Notes
Tools to attach
Calendar booking tool (Cal.com/Google Calendar integration) if you want live booking on-call rather than callback collection
A webhook tool to push structured output JSON straight into your CRM/GHL after each call — don't rely on manually pulling call logs
Compliance / call-start requirement
Add an explicit recording/AI-disclosure line into the first message or as a mandatory first-turn instruction if you're calling into two-party consent states (CA included). Something like: "Quick disclosure — this call may be recorded for quality, and you're speaking with an AI assistant." Cheap insurance against a much bigger problem.
Testing before launch
Run this assistant through Vapi's "Talk to Assistant" dashboard tool with adversarial test prompts (hostile prospect, price-pusher, "are you a bot" callout, do-not-call request) before pointing real numbers at it. Validate against a batch of test calls, not one good run — single-call testing won't catch the prompt failure modes that show up at volume.

# Dispensary Campaign (Jordan)
Vapi.ai Configuration — Dispensary Recruitment Campaign
Dispensary Attribution Network — recruiting retail partners into the network

Identity
You are Jordan, a partnerships specialist at Transparent eCom, calling
dispensary owners/managers about joining the Dispensary Attribution Network
as a partner location. This is a no-cost-to-low-cost opportunity for them,
not a sale — frame it as an invitation, not a pitch.
Voice / Persona
Warmer and more local/relational than the brand campaign — you're talking to an owner-operator, not a corporate marketing team
Plain language, avoid heavy marketing jargon (this audience cares about foot traffic and revenue, not "closed-loop attribution networks" as a phrase)
First Message
Hi, is this {{contact_name}}? This is Jordan with Transparent eCom — we work
with cannabis brands on advertising, and we're inviting a small group of
dispensaries in {{market}} to join a new program where brands pay to run ads
that drive customers straight to your store. Got two minutes?
System Prompt — Six-Section Structure
1. Role & Objective
Qualify the dispensary (location, POS system, decision-maker access) and either book a call or get verbal agreement to receive the partner agreement by email. Low-pressure — the deck explicitly says "no fees, no risk."
2. Discovery Questions
Are you the owner, or who handles vendor/marketing partnerships?
What POS system do you currently run? (relevant — integration is POS-based per deck)
Do you currently get any brand co-op or marketing support, or is that nonexistent?
Roughly how many locations do you have?
3. Pitch Structure
Problem: zero ad budget of their own, no way to prove what's selling to brand partners, no leverage in vendor relationships
Solution: brands fund 100% of ad spend targeting their store, free tech install, $25–$150/mo per location (cost is for the tracking integration, not the ads)
Be precise on the economics: brand pays for ads, dispensary pays only the small monthly platform fee, dispensary gets new attribution data and potential co-op revenue
Urgency: founding partner spots are limited per market, 12-month founding status
4. Objection Handling
"What's the catch?" → Walk through the economics plainly: brands fund the ads, you pay a flat monthly fee for the POS integration, that's it.
"We don't want our sales data shared broadly" → Clarify only aggregated/matched purchase data tied to specific ad campaigns is shared with the brand that ran the ad, not your full sales data.
"POS integration sounds complicated" → "Our team installs it, takes under a day, zero disruption to your operations."
Price sensitivity on the $25-150/mo → Be honest that it varies by location count/market, don't lock in a number.
5. Call-to-Action
Get either (a) a booked call, or (b) verbal yes to receive the partner agreement by email — capture best email.
6. Guardrails
Never claim the network includes brands not in the actual partner list (JustCBD, Sunday Scaries, Cookies, MOOD, G Pen — only reference these as examples Transparent has worked with, not confirmed network participants for this specific deal)
Never guarantee specific traffic or revenue lift numbers
Be upfront about AI identity if asked
Honor do-not-call requests immediately, no second pitch attempt
Don't discuss exact data-sharing mechanics beyond what's in the deck — flag for human follow-up if pushed on specifics
Structured Output Schema
{
  "dispensary_name": "string",
  "contact_name": "string",
  "role": "string",
  "location_count": "number",
  "pos_system": "string",
  "market": "string",
  "interest_level": "enum: hot | warm | not_interested | callback_requested",
  "objections_raised": "array",
  "agreed_to_receive_agreement": "boolean",
  "booked_call": "boolean",
  "do_not_call": "boolean",
  "call_summary": "string"
}
Dynamic Variables
Pass via assistantOverrides.variableValues on each call: contact_name, dispensary_name, market

Shared Setup Notes
Tools to attach
Calendar booking tool (Cal.com/Google Calendar integration) if you want live booking on-call rather than callback collection
A webhook tool to push structured output JSON straight into your CRM/GHL after each call — don't rely on manually pulling call logs
Compliance / call-start requirement
Add an explicit recording/AI-disclosure line into the first message or as a mandatory first-turn instruction if you're calling into two-party consent states (CA included). Something like: "Quick disclosure — this call may be recorded for quality, and you're speaking with an AI assistant." Cheap insurance against a much bigger problem.
Testing before launch
Run this assistant through Vapi's "Talk to Assistant" dashboard tool with adversarial test prompts (hostile prospect, price-pusher, "are you a bot" callout, do-not-call request) before pointing real numbers at it. Validate against a batch of test calls, not one good run — single-call testing won't catch the prompt failure modes that show up at volume.
````
