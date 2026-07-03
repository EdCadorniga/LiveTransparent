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
Dockerfile
LiveTransparent Report Plan.md
package.json
plan.md
Project Specifications.md
Project Status and Next Steps.md
QWEN.md
Sales and Marketing Roadmap.md
Unipile_potential_automations.md
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
| LT - Vapi Campaign Queue Feeder | `RFIZ9Bcfl3Yvms2b` | Manual/scheduled helper (created 2026-07-02, inactive) |
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

### Phase 2 — Classifier Status (workflow fixed 2026-07-02, data still blocked)
- **Workflow**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`)
- **Current structure**: Manual Start → Postgres (`Emerald_Contacts` joined against `voice_call_attempt`) → Code classifier → GHL tag apply → summary
- **Why changed**: The old live-GHL pagination path was removed because it hit PIT rate limits and was fragile inside Code-node loops.
- **Current data reality**: `Emerald_Contacts` currently exposes only executive source buckets with both `ghl_contact_id` and `primary_phone`.
  - `Cannabis-Retail-SSO-Executive-2`: 464 rows, 6 with GHL+phone, 4 not previously called
  - `Cannabis-Retail-SSO-Executive-1`: 84 rows, 1 with GHL+phone, 1 not previously called
  - No marketing / brand / dispensary / retail-sales source buckets currently have reachable rows with GHL ID + phone + not-called status
- **Heuristic warning**: Do **not** use raw `sso` substring matching anymore. It incorrectly routes executive rows into Brand. A 5-contact mis-tag test was rolled back immediately on 2026-07-02.
- **Pending**: Phase 2 is now blocked by source data, not code. We need either:
  - refreshed Emerald marketing / dispensary rows synced into `Emerald_Contacts` with GHL IDs and phones, or
  - a manually approved test cohort tagged directly in GHL, or
  - an explicit executive-routing decision if executives are intentionally part of campaign supply
- **2026-07-03 live-state correction**: the imported Brand/Dispensary pool now supersedes the older `Emerald_Contacts` classifier path for this rollout. The live `IduCoT5YOs0g2faT` workflow is currently stale and hardcoded to 3 specific `voice_call_queue.contact_id` values, so do not trust it as a general classifier until it is patched.
- **2026-07-03 prep complete**: all repo-side go-live assets are prepared. The only blocker is external: wait for GHL import processing to finish and for imported contacts to land in `report_raw_ghl_contacts`.

### Queue Feeder Status (created 2026-07-02)
- **Workflow**: `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`)
- **Purpose**: Slowly stage already-approved `vapi_campaign_brand` / `vapi_campaign_dispensary` contacts into `voice_call_queue`
- **Current structure**: Schedule Trigger (30 min) → build per-campaign config → filter enabled campaigns → GHL search by campaign tag → eligible contact filter → guarded Postgres insert → normalized summary
- **Controls**: per-campaign `enabled` flag + `per_run_limit` in the first Code node
- **Verification**: latest manual run succeeded and found 3 candidates (2 brand, 1 dispensary) but returned `total_queued: 0` and no `queue_id`s, so it is safe and non-destructive but not currently inserting rows
- **Insert-path verification**: audited the 3 candidate IDs from the feeder run and confirmed all 3 already exist in `voice_call_queue` with `status = 'pending'`, so the feeder's duplicate guard is behaving as designed
- **Seed cohort status**: those 3 queued campaign contacts are still `pending`, `attempt_count = 0`, and have no `voice_call_attempt` rows yet, so they are safe to keep as the initial controlled batch when voice is resumed

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
- `n8n/workflows/lt-emerging-pool-import.ts` — SDK workflow for Brands/Dispensaries Postgres import
- `fix_intake_poller.js` — intake poller fix script
- `fix_sheets_node.py`, `fix_brands_code.py`, `fix_parse_csv.py` — temporary fix scripts (can be cleaned up)
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
- Local copies (with GHL-mapped column headers, pool tags + `emerald`) at `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv` and `GHL_Ready_Dispensaries.csv`.
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
  - `classifier-repair-plan.md` — why the classifier must move to `emerging_pool_contacts`
  - `classifier-workflow-change-plan.md` — node-by-node classifier rebuild plan
  - `classifier-workflow-patch-snippets.md` — exact node content replacements
  - `classifier-workflow-mcp-update-ops.md` — MCP operation objects for `IduCoT5YOs0g2faT`
  - `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json` — machine-ready workflow update payload
  - `emerging-pool-post-import-runbook.md` — full operator sequence
  - `live-mutation-plan.md` — mutation order and stop gates
  - `rollback-checklist-vapi-emerging-pool.md` — surgical rollback plan
  - `execution-checklist-after-import.md` — concise after-import execution checklist
- **Apollo re-enrichment on bad numbers** (added 2026-07-02): In callback workflow `fx4UvKUWbqJEY3LK`, after `GHL - Apply Tags`, a new `Should Re-enrich Phone` IF node checks disposition. If `wrong_number` or `contact_disconnected`, it fires `HTTP - Set Apollo Enrichment` which sets `Enrich Phone via Apollo = Yes` (custom field `gdJDuZelIxEBE6n9i5Q6`). The existing `LT - Apollo Phone Enrichment Intake V3` then looks up a new number.

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate `repomix-output.md` so next-session context is up to date:

1. `. $PROFILE`  
2. `packlive`

This stages key files into `C:\TempRepomixStaging`, runs `npx repomix --style markdown --compress --remove-comments --remove-empty-lines`, and copies the result back to the project root.
````

## File: Dockerfile
````dockerfile
FROM nginx:1.27-alpine

COPY reports/nginx.conf /etc/nginx/conf.d/default.conf
COPY reports /usr/share/nginx/html
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

### Phase 2 — Contact Classification (code path fixed 2026-07-02, supply BLOCKED)

2.1 **Rewrite done**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) no longer depends on live GHL pagination.
  - Manual Trigger -> Postgres (`Emerald_Contacts` joined against `voice_call_attempt`) -> Code classifier -> GHL tag apply
  - Source rows now come from Postgres `Emerald_Contacts`, using `ghl_contact_id`, `primary_phone`, `source_file`, and `tags`
  - This removes the old `/contacts/search` 238-page scan, the PIT rate-limit failure, and the fragile Code-node HTTP loop
2.2 **Live supply verified**: the remaining Emerald rows with both `ghl_contact_id` and `primary_phone` are executive buckets only.
  - `Cannabis-Retail-SSO-Executive-2`: 464 rows, 6 with GHL+phone, 4 not previously called
  - `Cannabis-Retail-SSO-Executive-1`: 84 rows, 1 with GHL+phone, 1 not previously called
  - Total currently reachable Emerald rows in Postgres: 548 executive rows, 7 with GHL+phone, 5 not previously called
2.3 **Critical finding**: the old `sso`/`marketing` substring heuristic would have mis-tagged executive rows as Brand. That was tested on 5 contacts, then immediately rolled back by removing the accidental `vapi_campaign_brand` tag from those contacts.
2.4 **Current blocker**: no live Emerald rows currently meet all of these conditions at once:
  - campaign-relevant source (`marketing`, `brand`, `dispensary`, or `retail_sales`)
  - mapped `ghl_contact_id`
  - usable `primary_phone`
  - not already called
2.5 **Pending**: Phase 2 is now blocked by data availability, not workflow code. To complete rollout, we need one of:
  - sync/import the missing Emerald marketing and dispensary buckets into `Emerald_Contacts` with GHL contact IDs and phones
  - manually seed a small approved test cohort with `vapi_campaign_brand` / `vapi_campaign_dispensary`
  - define a new, explicit executive-to-campaign routing rule if executive supply is intentionally in scope

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

### Phase 4 status (2026-07-02)

- Not started. Activation remains blocked until a valid Brand/Dispensary test cohort exists.
- **2026-07-03 update**: the next cohort should come from the imported `emerging_pool_contacts` Brand/Dispensary pool, not the old `Emerald_Contacts` heuristic path. The live classifier workflow is stale and needs patching before reuse.

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

### Current live blocker
- Brand and Dispensary CSVs have been imported into GHL, but processing was still running when the session ended.
- Do not run linkage backfills until the imported contacts finish processing and land in `report_raw_ghl_contacts`.

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

Updated: 2026-07-02 (Emerging pool imported to Postgres; Apollo re-enrichment on bad numbers added to callback)

## Source Of Truth

This document is the canonical project status and next-steps reference.
It supersedes the duplicated planning notes in:

- [plan.md](./plan.md)
- [LiveTransparent Report Plan.md](./LiveTransparent%20Report%20Plan.md)

## Current State

- The outbound voice stack is **paused** (since 2026-06-05). Queue cleanup completed 2026-07-01: 1,005 stale `pending` rows marked `failed`. Pool audit complete: 23,726 GHL contacts, 1,045 unique already called via V1, ~16k Emerald pool as primary target for new campaigns.
- **Vapi Campaign Rollout Phase 1 complete (2026-07-01)**: Two Vapi assistants created (Brand/Alex `1d7c5d42`, Dispensary/Jordan `056f2e50`) with full system prompts from campaign docx files, 9 tools each. GHL campaign tags created. Vapi org tools cleaned up (2 deprecated deleted, 1 dangling ref removed). `ok_transfer_to_john` → `ok_transfer_to_jason` migration across all assistants, prompts, and n8n callback. See `plan.md` for next phases.
- **Vapi classifier path fixed (2026-07-02)**: `LT - Campaign Contact Classifier` now runs from Postgres `Emerald_Contacts` plus `voice_call_attempt` exclusion instead of live GHL pagination. The old PIT rate-limit / Code-node-loop failure path is gone.
- **Current rollout blocker (2026-07-02)**: the synced Emerald supply with both GHL IDs and phones is executive-only. We currently have 5 not-called rows available, all from executive source files, and zero reachable marketing / dispensary / retail-sales rows for the two new campaigns.
- **Mis-tag rollback completed (2026-07-02)**: a 5-contact smoke test proved the old `sso` substring heuristic incorrectly routes executive rows into Brand. Those accidental `vapi_campaign_brand` tags were removed immediately.
- **Queue feeder workflow added (2026-07-02)**: `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) now exists to gradually feed already-approved campaign-tagged contacts into `voice_call_queue`. Latest manual test found 3 candidates and queued 0 new rows; follow-up audit confirmed those same 3 contacts were already in `voice_call_queue` as `pending`, so the duplicate guard is working correctly.
- **Activation-readiness audit (2026-07-02)**: the 3 currently staged campaign rows are still `pending` with `attempt_count = 0` and no `voice_call_attempt` rows yet, so they are safe to keep as the seed cohort. The paused Vapi workflows still show the expected campaign-routing updates and no fresh executions since the pause, so the next real gate is controlled reactivation plus manual assistant test calls.
- **Bug discoveries during audit**: `voice_call_queue` has no `pipeline_stage` column — dequeue query filter `AND pipeline_stage = 'queued'` means dequeue webhook has NEVER picked up poller-inserted rows (V1 worked through dialer cron). Callback had hardcoded `trackedAssistants` array — now includes both new campaign assistants.
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
- Target n8n version: `2.25.3` (upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue)
- Canonical MCP: `n8n-lt`

### Active Workflows

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) — **Manual**, now reads from `Emerald_Contacts` + `voice_call_attempt`; code path is working, but current campaign-relevant source supply is empty
- `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) — **Inactive helper**, runs every 30 minutes when enabled and stages approved `vapi_campaign_*` contacts into the queue with pacing + duplicate guards
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

### 0. Emerging Pool Import (DONE 2026-07-02)
- **13,868 Emerald contacts** imported into Postgres `emerging_pool_contacts` (3,668 brands + 10,200 dispensaries)
- **GHL-ready CSVs** created at `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_{Brands,Dispensaries}.csv` with columns matching existing GHL `Em_*` custom fields
- Tags: `brands_pool,emerald` / `dispensaries_pool,emerald`
- Two n8n workflows created: `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`) and `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`)
- **2026-07-03 update**: Brand and Dispensary CSVs have now been imported into GHL, but GHL-side processing was still running at the end of session. Do not run the backfill yet until imported contacts finish processing and land in `report_raw_ghl_contacts`.
- **Next live sequence when processing finishes**:
  1. `postgres/emerging-pool-go-live-check.sql`
  2. `postgres/backfill-emerging-pool-ghl-ids.sql`
  3. `postgres/audit-emerging-pool-linkage.sql`
  4. patch `IduCoT5YOs0g2faT` using `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
  5. manually run classifier with 5 Brand + 5 Dispensary cap
  6. verify queue feeder `RFIZ9Bcfl3Yvms2b`

### 1. Vapi Campaign Rollout (Phases 1+3 DONE, Phase 2 DATA-BLOCKED — 2026-07-02)

See `plan.md` for full details. Progress:
- **Phase 1**: **DONE** — 2 assistants created, tools cleanup, John→Jason migration, GHL tags created
- **Quality gate (PENDING)**: Manual test call per assistant (Alex + Jordan) via Vapi dashboard
- **Phase 2**: **DATA-BLOCKED** — The classifier workflow is fixed, but the current data supply is not.
  - `Cannabis-Retail-SSO-Executive-2`: 464 rows, 6 with GHL+phone, 4 not previously called
  - `Cannabis-Retail-SSO-Executive-1`: 84 rows, 1 with GHL+phone, 1 not previously called
  - No current marketing / dispensary / retail-sales source rows have the required combination of `ghl_contact_id`, usable phone, and not-called status
  - Old `sso` matching is no longer safe because it routes executives into Brand
  - To unblock: sync refreshed marketing / dispensary rows into `Emerald_Contacts`, manually approve a GHL test cohort, or define executive routing intentionally
- **2026-07-03 strategy shift**: the imported `emerging_pool_contacts` Brand/Dispensary split is now the preferred campaign source for this rollout. The classifier should become a simple eligibility filter over `emerging_pool_contacts`, not a heuristic role classifier over `Emerald_Contacts`.
- **2026-07-03 workflow note**: the live `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is stale and currently hardcoded to 3 queue contact IDs. It must be patched before reuse. Patch assets are prepared in repo.
- **Phase 3**: **DONE** — All 6 infra changes deployed (dialer mapping, intake poller campaign tags, enqueue dedup, dequeue bugfix + routing, callback trackedAssistants, Config includeOtherFields)
- **Phase 4**: **BLOCKED** — Needs quality gate plus an approved Brand/Dispensary cohort first
- **Supporting helper**: Queue feeder workflow exists and its no-op behavior has been verified as expected when candidates are already pending in `voice_call_queue`

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
- **Remaining blocker**: external only. Wait for GHL import completion + reporting ingest landing imported contacts in `report_raw_ghl_contacts`.

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
