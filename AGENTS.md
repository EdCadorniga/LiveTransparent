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
- **`setNodeParameter` silent failure (observed 2026-07-06):** On Code nodes and HTTP Request nodes, `setNodeParameter` may report success (4 operations applied, 0 warnings) without actually modifying parameters in draft OR active version. **Use `updateNodeParameters` with `replace: true`** as the primary mutation method for both Code and HTTP Request nodes. Always verify with a fresh `GET` after mutation.
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
- **Issue 2 (2026-07-06)**: Apollo API call had two bugs: (a) path missing `/api/` prefix (`/v1/people/match` → `/api/v1/people/match`), (b) parameters sent as JSON body instead of URL query string. These prevented Apollo from delivering async phone number reveals to the V4 callback webhook (0 executions ever on `U7c6byTLXAMgcS75`).
- **Fix 2**: Changed path to `/api/v1/people/match`, moved all params (match fields + flags + `webhook_url`) from request body to query string with `encodeURIComponent`. Removed `body` from the API call.
- **Fix 3 (2026-07-06)**: V4 Callback Handler (`U7c6byTLXAMgcS75`) had a webhook key validation bug — the first-ever Apollo callback (receiving phone `+12104882613` for a test contact) was rejected with "Webhook key missing or mismatch" despite the key being present in query params. Fixed by adding a fallback check: if the multi-source candidate doesn't match, also checks `query.webhookKey` directly. Apollo callbacks now deliver within ~17 seconds.

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

### LT - Instagram DM Sequence (Unipile) (`iCnY6ccdHhfJg3sf`) — 2026-07-06 Fixes

- **Issue 1**: Cron runs every weekday hour at 12-22 UTC failing with HTTP 400. Root cause: `Config.pageSize` was `200`, but Unipile's Instagram API rejects limits >100 with `400 "Limit too high"`. The `fetchPaged()` calls to `/users/followers` and `/users/following` had no try/catch, so the error killed the entire execution.
- **Issue 2**: Unipile's `/users/following` endpoint returns `501 "feature not implemented"` for Instagram. With no try/catch, this would also crash the workflow even after the limit fix.
- **Issue 3**: Completed contacts (sequence_step >= 4) were still counted as `eligible`, had `persistState` webhooks fired for them wastefully, and inflated the eligibility metric.
- **Fix 1**: Config `pageSize` 200 → 100. Code cap `Math.min(200, ...)` → `Math.min(100, ...)` for defense-in-depth.
- **Fix 2**: Wrapped both `fetchPaged('/users/followers')` and `fetchPaged('/users/following')` in try/catch — on failure, returns empty array and continues. Changed `const` → `let` for these variables.
- **Fix 3**: Added early-exit check after attendeeId resolution but before `eligible++` and `persistState`:
  ```
  if (state.completedAt || state.sequenceStep >= (MESSAGE_TEMPLATES.length - 1)) {
    skipped += 1;
    actions.push({ ... reason: 'already_completed' });
    continue;
  }
  ```
- **Method**: `setNodeParameter` (`/parameters/assignments/assignments/4/value`) for Config + REST `PUT` with JSON file for Code node.
- **Verification**: Direct Unipile API call confirmed `limit=100` OK, `limit=200` returns 400. Both draft and active versions verified.
- **State table**: `instagram_dm_state` (Postgres) with webhook upsert (`lt-instagram-dm-state-upsert`). Dedup works correctly via `sequence_step` tracking. Now also prevents wasteful re-processing of completed contacts.
- **Unipile account**: `V9eiHiDpRmCtan0YNdzsQw` at `api42.unipile.com:17256`. Active and responsive at limit=100.

### LT - Company MQL Google Sheets Sync (`9Y3Kedm768kkwwSV`) — 2026-07-06 Timeout Fix

- **Issue**: `Build Sheet Payload` and `Build All Companies Sheet Payload` Code nodes padded the payload to 5,000 rows (4,999 empty rows when only 2 data rows existed). The bloated payload (~66KB of empty strings) caused the Google Sheets API to exceed the 30s HTTP timeout on `Write Sheet Snapshot` (`ECONNABORTED`). Same bug existed on the Broad/All Companies path.
- **Fix**: Reduced `targetRowCount` from 4,999 to 500 in both Code nodes. Increased HTTP timeout from 30s to 60s on both `Write Sheet Snapshot` and `Write All Companies Snapshot`. Published 2026-07-06.
- **Method**: `updateNodeParameters` with `replace: true` on all 4 nodes (Code + HTTP Request). Initial attempt with `setNodeParameter` silently failed — reported success but did not modify parameters. Also confirmed `updateNodeParameters` with `replace: true` on HTTP Request nodes does NOT corrupt parameters (clean audit on all 14 nodes, no nested `parameters.parameters`).
- **Spreadsheet**: `1h71qBh90rh4hK94qYEBD4MZILDEZKPiocKcajo1-BcY`, sheets `Company MQLs` (col A-K) and `All Companies` (col A-J).
- **Verification**: Both draft and active versions confirmed `targetRowCount=500`, `timeout=60000`, no structural corruption, all 12 connections intact across both MQL and Broad paths.

### Vapi Assistant Optimizations (2026-07-07)

- **Voice settings applied** (all 4 assistants): `onNoPunctuationSeconds: 0.7` (was 1.5s default), `backgroundSound: "office"`, `backchannelingEnabled: true`. `startSpeakingPlan` with `smartEndpointingEnabled: true`, `smartEndpointingPlan: { provider: "vapi" }`, `waitSeconds: 0.4`.
- **Async tools**: All 13 tools across all 4 assistants set to `async: true`. Vapi fires tool calls without blocking — assistant acknowledges immediately while n8n processes in background.
- **maxTokens reduced**: All assistants 1000/250 → 300 for faster response generation.
- **Transcriber upgraded**: `deepgram/nova-2` → `deepgram/flux-general-en` on all 4 assistants. `eotTimeoutMs` reduced from 5s default to 700ms for native end-of-turn detection. `smartFormat: false`. `endpointing: 10`.
- **Temperature unified**: All 4 assistants set to `temperature: 0.5` (was 0.4 outbound, 0.7 inbound).
- **V1 Outbound tool fix (CRITICAL)**: Was missing 6 tools (`ok_transfer_to_jason`, `ok_get_ghl_contact`, `update_lead_status`, `add_to_dnc`, `log_call_outcome`, `notify_sales`) due to earlier Phase 1 cleanup — only `press_dtmf` was attached. All 7 tools now attached.
- **serverMessages fix**: Brand, Dispensary, and V1 Inbound were missing `tool-calls` in `serverMessages`. Added to all 3.
- **V1 Inbound gap fixes**: Added missing `endCallMessage: "Goodbye."`, `voicemailMessage`, and `voicemailDetection: { type: "audio", provider: "vapi" }`. Enabled `backgroundDenoisingEnabled: true`.

### Vapi Assistants — Current Configs

| Assistant | ID | LLM | maxTokens | Temp | Transcriber | Tools | serverMessages |
|-----------|-----|-----|-----------|------|-------------|-------|----------------|
| V1 Outbound (Savannah) | `3f9bbfd2` | openrouter/anthropic/claude-3-haiku | 300 | 0.5 | deepgram/flux-general-en | 7 | end-of-call-report, tool-calls, status-update |
| Brand (Alex) | `1d7c5d42` | openrouter/anthropic/claude-3-haiku | 300 | 0.5 | deepgram/flux-general-en | 9 | end-of-call-report, tool-calls, status-update |
| Dispensary (Jordan) | `056f2e50` | openrouter/anthropic/claude-3-haiku | 300 | 0.5 | deepgram/flux-general-en | 9 | end-of-call-report, tool-calls, status-update |
| V1 Inbound (Savannah) | `43f379ff` | openrouter/anthropic/claude-3-haiku | 300 | 0.5 | deepgram/flux-general-en | 8 | end-of-call-report, tool-calls, status-update |

All: `backgroundSound: office`, `backchannelingEnabled: true`, `backgroundDenoisingEnabled: true`, `firstMessageMode: assistant-speaks-first`, `endCallMessage: "Goodbye."`, `maxDurationSeconds: 480`, `voicemailDetection: audio`.

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
| LT - Company MQL Google Sheets Sync | `9Y3Kedm768kkwwSV` | Active (daily 6am ET) |

### Reporting Notes

- GA4, GHL, and GSC ingestion are all live and active.
- GSC ingest and rollup bridge are active daily (verified from execution data).
- Report Pipeline Velocity (`iFfwh0jpYUZoDhDR`) is active.
- Meta Ads API access is validated against `act_2186975138800404` but spend ingest is still deferred.
- Keep report validation end-to-end: ingest -> attribution bridge -> daily rollups -> executive summary.

## Other Live Systems

- SimpleTexting: Send, delivery, inbound reply, and unsubscribe webhooks are active.
- Unipile/Instagram: DM Sequence workflow active, cron `0 12-22 * * 1-5`, sends 4-message sequence to mutual followers. State tracked in `instagram_dm_state`.
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

## Tool & CLI Preferences

These CLI tools are installed and available via PATH on this system. Prefer them over slower alternatives when running bash commands:

| Tool | Use instead of | Why |
|------|---------------|-----|
| `rg` | `findstr`, `Select-String`, `grep` | 10-100x faster text search, .gitignore-aware |
| `fd` | `Get-ChildItem`, `dir` | Blazing fast file finding by name/pattern |
| `bat` | `cat`, `Get-Content` | Syntax-highlighted file viewing with line numbers |
| `jq` | manual JSON parsing | Process API/LLM JSON responses inline |
| `yq` | manual YAML parsing | YAML equivalent of jq |
| `xsv` | CSV processing in Python/JS | Fast CSV search, slice, stats, join (better for large datasets) |
| `delta` | default git diff | Syntax-highlighted, side-by-side git diffs |
| `fzf` | scrolling through lists | Interactive fuzzy finder (pipe any list into it) |
| `zoxide` | `cd` | Learns your navigation patterns, `z <fragment>` jumps anywhere |
| `hyperfine` | manual timing | Benchmark any command with statistical analysis |
| `sd` | `sed`, regex replaces | Simpler find-and-replace syntax |
| `ast-grep` | regex-only code search | Structural code search that understands syntax trees |
| `eza` | `ls`, `dir` | Modern ls with icons, colors, tree view |

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate `repomix-output.md` so next-session context is up to date:

1. `. $PROFILE`  
2. `packlive`

This stages key files into `C:\TempRepomixStaging`, runs `npx repomix --style markdown --compress --remove-comments --remove-empty-lines`, and copies the result back to the project root.
