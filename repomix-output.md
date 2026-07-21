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
unipile-ghl-bidirectional-integration.md
vapi-campaign-prompts-summary.md
```

# Files

## File: AGENTS.md
````markdown
# LiveTransparent Agent Notes

## IMPORTANT — Read This First

Analyze the attached `repomix-output.md` file. It contains the core system architecture, code blueprints, and operational roadmaps for my LiveTransparent automation environment. Review custom script setups (like `fix_intake_poller.js`) to understand how my infrastructure is organized.

**LLM context-loading order:**
1. `repomix-output.md` — start here for architecture, blueprints, and roadmaps
2. `AGENTS.md` (this file) — short operating guide
3. `Project Status and Next Steps.md` — current priorities and live-state
4. `Project Specifications.md` — system boundaries, guardrails, contracts
5. `plan.md` + sub-plans — active work plan
6. Custom scripts — infrastructure specifics
7. All other repo files — only when a task requires fine detail

> **Source of Truth**: Live n8n (via `n8n-lt` MCP) is the single source of truth for all workflow state. Repo files (`.ts`, `.json`, `Backup of all n8n workflows/`) may be outdated snapshots. Always `get_workflow_details` or `search_workflows` to read current state before editing.

> **Historical traceability**: Detailed fix narratives, root-cause analyses, and execution histories from 2026-06 onward are preserved in git history. This file contains only the current operating guide and critical patterns.

## Canonical Status

- Use [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md) for current priorities and live-state details.
- This file is the short operating guide: keep it current, but avoid duplicating long planning material here.

## Environment

- Deployed via Coolify on a VPS.
- Public hosts: `automations.livetransparent.com` for n8n and `reports.livetransparent.com` for the report host.
- Prefer Coolify internal service-to-service calls when possible.
- n8n target version: `2.28.6`.
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

## Working Rules

- Check the live state before and after every mutation.
- Fetch first, patch second.
- After every mutation via `update_workflow`, verify the workflow is both **updated AND published**: compare `versionId` vs `activeVersionId` from `get_workflow_details`. If they differ, call `publish_workflow` to activate the draft. The `update_workflow` MCP tool does NOT auto-publish.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Use `Config` nodes only when env or credential access is blocked.
- LinkedIn outbound senders must fail closed on reply/inbound lookup errors. A failed reply check is a skip, not a send.
- For any "stop LinkedIn DMs" request, suppress the contact in both places: add `linkedin_dm_sequence_completed` in GHL and mark the shared `linkedin_connection_state` row terminal (`connection_status = completed`, `sequence_step >= 4`, `dm_sequence_status = completed`/`dm_conversation_status = active` as applicable). The GHL tag alone is not enough because the live LinkedIn send paths select from shared state.
- LinkedIn DM sequences must mark terminal contacts with `linkedin_dm_sequence_completed` and stop reselecting step-4 rows; the queue source is `LT - LinkedIn Connection State Sync (Unipile)` and the GHL connect dispatcher feeds 20 contacts at a time when healthy.

### LinkedIn DM Suppression — Production Automation

**Primary path (GHL UI)**: Adding the tag `stop_linkedin_dms` to any contact in GHL triggers the automated suppression pipeline. No code access needed.

```
GHL tag "stop_linkedin_dms" added
  → GHL automation "WL - Stop LinkedIn DMs" fires
    → POST https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms
      → n8n workflow: LT - LinkedIn DM Suppression from GHL Tag (IPN8jnR3XSurX0o1)
        1. Scans webhook body for LinkedIn URL (any key containing "linkedin", nested customData, customFields)
        2. Falls back to GET /contacts/{id} if no URL in webhook
        3. Falls back to Unipile name search as last resort
        4. Adds linkedin_dm_sequence_completed tag via GHL API
        5. Upserts linkedin_connection_state (completed, step=4) for real contact
        6. Upserts linkedin_connection_state (completed, step=4) for synthetic linkedin:follower:{providerId}
```

**GHL automation setup:**
| Setting | Value |
|---------|-------|
| Name | WL - Stop LinkedIn DMs |
| Trigger | Tag Added → `stop_linkedin_dms` |
| Action | Webhook POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` |
| Custom Body | `{"contact_id":"{{contact.id}}","first_name":"{{contact.firstName}}","last_name":"{{contact.lastName}}","linkedin_url":"{{contact.customField.apollo_person_linkedin_url}}"}` |

**Suppression verified across all 3 LinkedIn send paths (2026-07-15 audit):**
| Send Path | How it's blocked |
|-----------|-----------------|
| DM Sequence (d0tEtijajisIsYcs) | SQL `WHERE connection_status = 'connected'` + `dm_conversation_status <> 'active'` |
| Follower DM (pq7XVajNFnnwMUTr) | Code `sequence_step >= 1` + `dm_conversation_status === 'active'` |
| Dispatcher (fXxw5lanZcDmUrst) | SQL `WHERE connection_status = 'ready'` + GHL tag block `linkedin_dm_sequence_completed` |

### LinkedIn DM Suppression Runbook (Manual/CLI)

When the user asks to stop DMs for a contact, preferred path is the GHL tag above. If CLI is needed:

```bash
python scripts/suppress_linkedin_dms.py "<name or LinkedIn URL>"
```

This single command handles everything:
1. Resolves the LinkedIn profile via Unipile (by URL or name search)
2. Finds the GHL contact if one exists
3. Adds `linkedin_dm_sequence_completed` tag in GHL (when a GHL contact is found)
4. Upserts `linkedin_connection_state` rows (both real GHL contact ID and synthetic `linkedin:follower:{providerId}`) to terminal:
   - `connection_status` = `completed`
   - `sequence_step` = 4
   - `dm_sequence_status` = `completed`, `dm_conversation_status` = `active`

If the script isn't available, POST directly to the suppression webhook or state upsert webhook:

**Path A — Suppression webhook** (does everything — tag + state table):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` with `{"contact_id":"...","first_name":"...","last_name":"..."}`

**Path B — State table only** (tag separately via GHL UI):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert`:
```json
{
  "ghl_contact_id": "<contact_id>",
  "location_id": "Zwz4relUXVPxx8uohnjV",
  "unipile_account_id": "V9eiHiDpRmCtan0YNdzsQw",
  "linkedin_profile_url": "https://www.linkedin.com/in/<identifier>/",
  "linkedin_public_identifier": "<identifier>",
  "linkedin_provider_id": "<provider_id>",
  "connection_status": "completed",
  "sequence_step": 4,
  "source_workflow_name": "manual_suppression",
  "source_key": "manual:suppress:<identifier>",
  "payload_json": {
    "dm_sequence_status": "completed",
    "dm_conversation_status": "active"
  },
  "metadata_json": {
    "source": "manual_suppression",
    "reason": "user_requested_stop_DMs"
  }
}
```
4. Also upsert with `ghl_contact_id` = `linkedin:follower:<provider_id>` if the real GHL contact wasn't found (covers the Follower DM path).

## Tooling

- Prefer `n8n-lt` MCP or direct API calls before browser workflows.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.
- Codex config: `C:\Users\edmon\.codex\config.toml`.
- **Avoid `n8n-lt` `updateNodeParameters` for Set v3.4 nodes.** It silently corrupts `assignments.assignments` from `[{...}]` to `{item: [{...}]}` and stringifies booleans / `options`. Use `setNodeParameter` for single-path edits on Set v3.4 nodes. If that also fails, use direct n8n REST `PUT /api/v1/workflows/{id}` with `N8N_API_KEY_LT` from `.env` (note: PUT auto-publishes and validates all node credentials). For Code nodes, both `updateNodeParameters` and `setNodeParameter` are safe. Known-good Config shape: `{"mode": "manual", "assignments": {"assignments": [{id, name, value}, ...]}}` — no `includeOtherFields` or `options` keys required.
- **`setNodeParameter` silent failure (observed 2026-07-06):** On Code nodes and HTTP Request nodes, `setNodeParameter` may report success without modifying parameters. **Use `updateNodeParameters` with `replace: true`** as the primary mutation method for both. Always verify with a fresh `GET` after mutation.
- **n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` return fields that violate the MCP output schema. **Workaround:** Use direct REST API calls for workflow listing and details:
  ```bash
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows?active=true&limit=100"
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows/{workflowId}"
  ```
  MCP tools for **execution, editing, and node operations** are unaffected.

## Code Node HTTP Requests

- **Use `this.helpers.httpRequest({...})` directly** — do NOT wrap in an async helper function called with `.call(this, ...)`. The wrapper pattern causes HTTP 400 errors in task-runner loops.
- **`$httpRequest`** works for single calls but may fail in pagination loops.
- **`json: true`** works but must be paired with explicit `'Content-Type': 'application/json'` header.
- For paginated GHL search API calls, use `page` (1-indexed) + `pageLimit` (max 100). Do NOT use `startAfter`/`startAfterId`.
- Do NOT include empty `filters: []` in GHL search body — omit entirely.
- Add `await new Promise(r => setTimeout(r, delayMs))` between pages to avoid rate limiting.

## GHL REST API

- **API base URL**: `https://services.leadconnectorhq.com` — NOT `rest.gohighlevel.com`.
- **Auth header**: `Authorization: Bearer pit-b278b3ad-96bd-41fb-ba03-9f927039eb28` (PIT token from root `.env`). The `token:` header style does NOT work.
- **Required header**: `Version: 2021-07-28` on every request.
- **Accept/Content-Type**: Always include `Accept: application/json` and `Content-Type: application/json`.

### Email Template Operations

**Listing templates**: Use `ghl_official_emails_fetch-template` MCP tool (OAuth). Pass `query_parentId` for folder-scoped listing, `query_limit` (max 50), `query_offset`.

**Reading template content**: Each template has a `previewUrl` pointing to Firebase Storage. Use `webfetch` with `format: "html"`. No working GET endpoint exists.

**Updating a template** (PATCH):
```bash
curl.exe -s -X PATCH "https://services.leadconnectorhq.com/emails/builder/{templateId}" \
  -H "Authorization: Bearer pit-b278b3ad-96bd-41fb-ba03-9f927039eb28" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"locationId":"Zwz4relUXVPxx8uohnjV","editorType":"html","editorContent":"<html>...</html>"}'
```
- Uses `editorType` + `editorContent`, NOT `rawHTML`/`html`/`type` fields.
- `locationId` is required in body.
- On success, verify new `lastUpdated` timestamp and `previewUrl`.
- **Backup before editing**: `webfetch` current HTML first.
- **Watch for `&#8211;` entities**: GHL normalizes en-dashes to `&#8211;`. Preserve exactly.

## n8n REST API Note

When using direct n8n REST `PUT /api/v1/workflows/{id}`:
- Required fields: `name`, `nodes`, `connections`, `settings`
- Settings must NOT include `availableInMCP` (remove before PUT)
- `versionId` and `tags` are read-only — exclude from body
- `Content-Type: application/json` header is required
- If settings get rejected as "additional properties", strip to: `executionOrder`, `timezone`, `saveDataErrorExecution`, `saveDataSuccessExecution`, `saveManualExecutions`, `saveExecutionProgress`, `executionTimeout`, `callerPolicy`
- Use `curl.exe` with JSON file for large payloads (PowerShell `ConvertTo-Json` can corrupt nested objects with `#` chars)

## Live Voice System

| Item | Value |
|------|-------|
| Phone | +1 (562) 534 1977 (bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4) |
| Callback webhook | https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback |
| Key env | VAPI_PHONE_NUMBER_ID, GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV, GHL_API_KEY / GHL_PIT |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Manual |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Active |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (polls `*/2 13-22 UTC Mon-Fri`, ET-forward schedule) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Active |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Active |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Active |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active (hourly, no Slack reporting) |
| LT - Voice Campaign Brand (Alex) | 1d7c5d42-f0a4-4b58-9494-dbda3be3c657 | Created, not active |
| LT - Voice Campaign Dispensary (Jordan) | 056f2e50-8bdf-4257-ac45-4d575600c39d | Created, not active |

### LT - Voice Queue Vapi Intake Poller (bYk1Ai6MJLyhTsDZ) — Details

**Tag rotation** (one tag per 10-min cycle, cycles every 40 min):
1. `vapi_campaign_brand` (926)
2. `vapi_campaign_dispensary` (19)
3. `brands_pool` (3,024)
4. `dispensaries_pool` (7,953)

**Fixes applied 2026-07-14:**
- `Trigger Apollo Enrichment` auth: changed `predefinedCredentialType` → `none` (was crashing because API key is passed in headers)
- `Remove Tag - Enriching` URL: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID)
- Added full pagination loop with 250ms delays and 30-contact cap to avoid GHL rate limiting
- Added `brands_pool`/`dispensaries_pool` to search tags (was only searching campaign tags)
- Dedup: SQL `WHERE NOT EXISTS` prevents re-enqueue + `Set` dedup within each run
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`) since most pool contacts lack timezone data. Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`, `CA`→`America/Los_Angeles`).
- **ET-forward dialer schedule**: cron shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. Initial business hours guard widened from 9-17 to 8-18 CT so it doesn't gate early ET calls.

**Fixes applied 2026-07-16 (anti-spam):**
- **Campaign tag removal**: After enqueueing, the poller now removes the source campaign tag (e.g. `brands_pool`) instead of the hardcoded `vapi_queue` tag. This prevents contacts from being re-found in subsequent rotation cycles.
- **Blocklist expansion**: `Classify Contacts` now checks all 8 `BLOCKLIST_TAGS` via `hasAnyBlocklistTag()` (was only checking `vapi_voicemail` and `vapi_qualified`). Contacts with any terminal outcome tag have their campaign tag removed inline and are skipped.
- `removeTag()` helper now accepts a `tagsToRemove` array parameter for flexible tag removal.

### Voice Tags

vapi_call_attempted, vapi_dnc, vapi_human_answered, vapi_interested, vapi_not_interested, vapi_interest_unknown, vapi_voicemail, vapi_voicemail_left, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected

### Vapi Campaign Tags

| Tag | ID |
|-----|-----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Vapi Assistants

| Assistant | ID | LLM | maxTokens | Temp | Speed | Voice |
|-----------|-----|-----|-----------|------|-------|-------|
| V1 Outbound (Savannah) | 3f9bbfd2 | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |
| Brand (Alex) | 1d7c5d42 | claude-3-haiku | 300 | 0.5 | 1.05 | Elliot |
| Dispensary (Jordan) | 056f2e50 | claude-3-haiku | 300 | 0.5 | 0.88 | Nico |
| V1 Inbound (Savannah) | 43f379ff | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |

### Apollo Phone Enrichment Status (custom field rgYJ7UqoznGoe3WeUAtH)

- enriched -- terminal (good)
- no_match -- terminal (no Apollo hit)
- error -- terminal (API error)
- queued -- transient (awaiting Apollo callback)
- queued_phone -- transient (profile enriched, phone requested via async callback)
- callback_timeout -- terminal (set by reaper when queued > 24h)
- callback_failed -- terminal (Apollo callbacks received but processing failed)

### Apollo Enrichment Pipeline (Fixed 2026-07-14)

The pipeline was completely dead since 2026-05-13. All webhook-based workflows had 0 executions.

**Before fix**: 3 webhook workflows with 0 executions each, 1,279 contacts stuck at callback_timeout.

**After fix**: New polling workflow replaces the webhook-based intake. Works in two steps per contact:
1. Sync profile match: calls Apollo `/v1/people/match` (no phone), writes name/email/company/LinkedIn/title/dept/revenue immediately
2. Async phone request: calls Apollo again with `webhook_url` pointing to V4 callback handler

| Workflow | ID | Status |
|----------|-----|--------|
| **LT - Apollo Phone Enrichment Polling** | **JH8ShfpglWmLMZ3l** | **Active, every 30 min, batch 50** |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active (1,058+ callbacks received by 2026-07-16, working) |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active (0 executions - superseded by polling) |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** (legacy; 1,008 orphaned webhook executions canceled 2026-07-16) |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** (legacy V3, fully superseded by V4) |

**Pipeline flow:**
1. **Polling workflow** searches GHL every 30 minutes for contacts needing enrichment (3 sources: `Enrich Phone via Apollo = Yes`, empty enrichment status + no phone, orphaned `queued` / `queued_phone` status)
2. **Sync step**: Calls Apollo `/v1/people/match` with name/email/LinkedIn → writes profile data (name, email, company, title, dept, LinkedIn, revenue, funding) to GHL immediately
3. **Async step**: Calls Apollo `/v1/people/match` with `reveal_phone_number: true` + `webhook_url` pointing to V4 callback → Apollo processes and calls back
4. **V4 callback handler** receives the phone number and updates GHL with it, setting status to `enriched`
5. **GHL automation** (`WL - Apollo Phone Enrichment Trigger`) watches for `Enrich Phone via Apollo = Yes` and POSTs to the (now unpublished) intake webhook — no longer needed since poller handles it

**Webhook key** for all Apollo callbacks: `4ecdfb53615c43fc9541d9a65b758102addf5b4f279c415f88b9d1a89e468d55`

**Apollo API key**: `CIgACIqwFAXuvYUQKHZcLA`

### Apollo Pipeline Full Audit + Fixes (2026-07-15)

Full review of 7 Apollo-related workflows found 2 CRITICAL bugs, 2 HIGH issues, and several medium/low cleanups. 10 fixes applied across 6 workflows:

#### 1. `queued_phone` status invisible to Timeout Reaper — CRITICAL (RL5Zy, JH8Sh)

**Bug**: Polling workflow set status to `queued_phone` after async phone request, but Reaper only searched for `queued`. Contacts stuck in async callback phase were never unblocked.

**Fix**: Reaper now searches both `queued` AND `queued_phone`. Polling workflow now writes `Apollo Phone Enrichment Queued At` (NgC3xGTh0laQ9ArTnude) alongside `queued_phone` so aging works.

#### 2. Intake Poller re-triggers enrichment on `queued_phone` — CRITICAL (bYk1)

**Bug**: Classify Contacts code matched `queued` → `waiting` but `queued_phone` fell through to default `enrich` action, triggering duplicate Apollo API calls for already-pending contacts.

**Fix**: Added `queued_phone` to the `waiting` path alongside `queued`.

#### 3. SQL injection in Sheet First intake — CRITICAL (WmKAh)

**Bug**: Build Upsert SQL used template-literal injection with manual `''` escaping — same anti-pattern previously fixed in LinkedIn Reply Backfill.

**Fix**: Switched to parameterized query with `$1..$9` and `queryReplacement` array. Code node now outputs typed JSON fields instead of building SQL strings.

#### 4. `doHttpRequest` wrapper pattern removed from all workflows — HIGH

The wrapper pattern `async function doHttpRequest(options) { ... $httpRequest / this.helpers.httpRequest ... }` called with `.call(this, ...)` causes HTTP 400 errors in task-runner loops. Removed from: V4 callback (U7c6), V3 callback (YaWi), Intake Poller Search GHL Contacts (bYk1), Sheet First main Code node (WmKAh). All replaced with direct `this.helpers.httpRequest(options)` or `this.helpers.httpRequest(opts)`.

#### 5. V3 callback handler had zero error handling — HIGH (YaWi)

**Bug**: No try/catch in main Code node. Any error returned 500 with no status update.

**Fix**: Added try/catch with best-effort `callback_failed` status update on error, matching V4's error handler. Then **unpublished** V3 (fully superseded by V4).

#### 6. GHL error handling in polling workflow — MEDIUM (JH8Sh)

**Bug**: `ghl()` helper swallowed all errors identically (`{ ok: false }`). A 429 rate limit looked the same as a 404.

**Fix**: `ghl()` now returns `{ ok: false, status: ... }`. All 3 search sources retry on 429 with 5s delay before re-scanning the same page.

#### 7. V4 callback `Apollo Contact Id` conditionally set — MEDIUM (U7c6)

**Bug**: `Apollo Contact Id` was only written when `normalizedPhone` was found. If Apollo returned valid profile but phone was blocked (corporate phone match), the contact lost traceability.

**Fix**: `successfulApolloContactId` now always set to `str(person?.contact?.id || person?.id)` regardless of phone status.

#### 8. Reaper Config node corruption — LOW (RL5Zy)

**Bug**: Set v3.4 Config node had nested `parameters.parameters.assignments.assignments` corruption artifact from a prior `setNodeParameter` call.

**Fix**: Removed via REST API PUT. Config node now has clean `{"mode":"manual","assignments":{"assignments":[...]}}` shape.

#### 9. Intake Poller `removeTag` used `$httpRequest` fallback — LOW (bYk1)

**Bug**: Classify Contacts `removeTag()` function checked `typeof $httpRequest === 'function'` as primary with `this.helpers.httpRequest` as fallback.

**Fix**: Replaced with direct `await this.helpers.httpRequest(opts)` call.

#### 10. Status pipeline now consistent end-to-end

| Status | Set by | Read by | Action |
|--------|--------|---------|--------|
| `queued` | Staged Intake (legacy) | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `queued_phone` | Polling workflow | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `enriched` | V4 callback | Intake Poller | Enqueue to voice_call_queue |
| `no_match` | Polling/V4/Sheet First | Intake Poller | Terminal skip |
| `error` | Polling | Intake Poller | Terminal skip |
| `callback_failed` | V4 callback catch | Intake Poller | Terminal skip |
| `callback_timeout` | Reaper | Intake Poller | Terminal skip |

### Apollo Production Hardening (2026-07-16)

- Audited the live production path end-to-end: Polling (`JH8ShfpglWmLMZ3l`), V4 callback (`U7c6byTLXAMgcS75`), and Reaper (`RL5ZyUoshSPbmVA1`) were all active and published.
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed beyond the `Webhook` node; this was stale execution state, not the active Apollo production path.
- Polling workflow fix: orphan re-discovery now searches both `queued` and `queued_phone` instead of only `queued`.
- Callback V4 fix: Apollo provider-level callback failures (for example `failure_reason: "you ran out of mobile number credits"`) now write `Apollo Phone Enrichment Status = callback_failed` instead of being silently treated as `no_match`.
- Polling workflow write-path fix: hardened GHL contact update fallback after reproducing live GHL behavior on `PUT /contacts/{id}`.
  Accepted shape for this endpoint is `{"customFields":[...]}` without `locationId`; bodies containing `locationId` or `customField` can return `422`.
- Polling workflow now falls back to a minimal write when the full profile update fails, ensuring at least:
  - `Apollo Phone Enrichment Status = queued_phone`
  - `Apollo Phone Enrichment Queued At = <today>`
  - `Enrich Phone via Apollo = No`
  - Apollo IDs where available
- Backfilled 6 previously blank contacts on 2026-07-16 into `queued_phone` so they are now visible to the callback/reaper path immediately:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

### Custom Field IDs (GHL)

- Apollo Phone Enrichment Status = rgYJ7UqoznGoe3WeUAtH (SINGLE_OPTIONS)
- Apollo Phone Enrichment Queued At = NgC3xGTh0laQ9ArTnude (DATE)
- Enrich Phone via Apollo = gdJDuZelIxEBE6n9i5Q6 (SINGLE_OPTIONS: Yes/No)
- Em_Emerald_Contact_ID = R0wbDRyzZz34PMlQSRWN
- Em_Source_File = ILurFacMbAaHz2DdGjPa

### Pool Tags

- brands_pool -- contacts from Brands.csv import
- dispensaries_pool -- contacts from Dispensaries.csv import

### Apollo Re-enrichment on Bad Numbers

In callback workflow fx4UvKUWbqJEY3LK, when Vapi returns wrong_number or contact_disconnected, the Should Re-enrich Phone IF node sets Enrich Phone via Apollo = Yes (custom field gdJDuZelIxEBE6n9i5Q6). The existing LT - Apollo Phone Enrichment Intake V3 then looks up a new number.

## Vapi Workflow Fixes (2026-07-14)

Full review conducted of all 12 Vapi-related workflows. Five bugs fixed across 3 workflows:

### 1. Race Condition: Dialer Picked Queue Items Without Lock (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` used `SELECT...LIMIT 1` (read-only). Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item, causing **duplicate outbound calls** to the same contact.
**Fix**: Changed to `UPDATE...FROM...RETURNING` that atomically locks the row (`locked_at = NOW(), lock_owner = 'outbound-dialer'`) at fetch time.

### 2. `report_referral` Tool Was Dead Code (fx4UvKUWbqJEY3LK)
`Switch - Route Tool` output 4 routed `report_referral` to `Code - Normalize End Of Call`, which checks `endedReason`/`analysis.summary` — none of which exist on tool call payloads. Node returned `[]` silently.
**Fix**: Re-routed to `Respond - 200` so Vapi gets a proper acknowledgment.

### 3. Intake Poller Could Create Duplicate Queue Entries (bYk1Ai6MJLyhTsDZ)
`Postgres - Insert Queue` used plain `INSERT INTO...VALUES(...)` with **no dedup check**. The webhook-based enqueue had `WHERE NOT EXISTS` but the poller didn't.
**Fix**: Wrapped INSERT in `SELECT...WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also updated `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing an error).

### 4. No Error Handling on Tag Removal HTTP Nodes (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes (`Remove Tag - Enqueued`, `Remove Tag - Enriching`, `Remove Tag - Skipped`) lacked `continueOnFail`. A flaky GHL tag deletion crashed the workflow after the enqueue/enrich/skip already succeeded.
**Fix**: Enabled `continueOnFail: true` on all three.

### 5. Timer System Static Data Race Condition (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain — producing duplicate background warnings and force-end commands.
**Fix**: Replaced `state.timersScheduled` boolean with `state.timersScheduledAt` timestamp. Added 60-second dedup window: if a timer was already started within 60s, a duplicate is skipped. Updated `Code - Prepare Background Warning` and `Code - Prepare Hard Stop` to check `timersScheduledAt`.

## Vapi Anti-Spam Fixes (2026-07-16)

Root-cause audit triggered by a contact complaint about repeated Vapi calls after voicemail had already been left. Identified **4 bugs combining into an infinite call loop** across 3 workflows. All published 2026-07-16.

### The Spam Chain (before fixes)

1. Intake Poller finds contacts by campaign tag (e.g. `brands_pool`) → enqueues → **only removed `vapi_queue` tag** (which contacts never had). Campaign tag stayed.
2. Dialer calls → voicemail → Callback applies tags but **never marks queue `completed`** (only the tool-call `update_lead_status` path did that).
3. 3 days later, dialer retries → `Code - Check Phone` sees `vapi_voicemail` tag → blanks phone → release lock → `status = 'completed'`.
4. Next poller cycle finds same contact (campaign tag still present) → old entry is `completed` → dedup only blocks `pending`/`in_progress` → **creates new queue entry**.
5. Dialer picks new entry → calls again → voicemail again → loop forever.

### Fixes Applied

#### 1. Intake Poller removed wrong tag after enqueue (bYk1Ai6MJLyhTsDZ) — CRITICAL

**Bug**: `Remove Tag - Enqueued` always removed `vapi_queue`, but contacts were found by campaign tags like `brands_pool`, `dispensaries_pool`, `vapi_campaign_brand`, `vapi_campaign_dispensary`. The campaign tag never got removed, so contacts were re-found every 40-minute rotation cycle.

**Fix**: 
- `Classify Contacts` now outputs `source_tag` (the matched campaign tag) with every enqueue result
- `Transform Postgres Output` passes `source_tag` through to tag removal
- `Remove Tag - Enqueued` removes `$json.source_tag` (the actual campaign tag) instead of hardcoded `vapi_queue`
- `removeTag()` function accepts `tagsToRemove` array argument
- `removeFromQueue` check (was `hasContactTag('vapi_voicemail') || hasContactTag('vapi_qualified')`) replaced by `hasAnyBlocklistTag()` that checks all 8 outcome tags

#### 2. EOC callback never marked queue completed (fx4UvKUWbqJEY3LK) — CRITICAL

**Bug**: End-of-call path was `Normalize End Of Call → Respond → Insert Attempt → Apply Tags → Should Re-enrich Phone`. It inserted call attempts, applied GHL tags, and triggered re-enrichment — but **never set `voice_call_queue.status = 'completed'`**. Only the tool-call path (`update_lead_status` → Postgres - Update Status) updated the queue.

**Fix**: Added new Postgres node `Postgres - Mark Queue Completed` wired between `GHL - Apply Tags` and `Should Re-enrich Phone`:
```sql
UPDATE voice_call_queue SET status = 'completed', updated_at = NOW() WHERE queue_id = $1;
```
Now every end-of-call callback immediately terminates the queue entry.

#### 3. Only 2 of 10 outcome tags blocked retries (r7UjWLndmc6EqEUW) — HIGH

**Bug**: `Code - Check Phone` blocklist was only `['vapi_voicemail', 'vapi_qualified']`. Contacts with `vapi_no_answer`, `vapi_busy`, `vapi_wrong_number`, `vapi_contact_disconnected`, `vapi_voicemail_left`, `vapi_dnc` were retried indefinitely (up to `max_attempts`).

**Fix**: Expanded `BLOCKLIST_TAGS` to all 8 terminal tags:
```
vapi_voicemail, vapi_voicemail_left, vapi_qualified, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected, vapi_dnc
```

#### 4. Intake Poller blocklist only checked 2 tags (bYk1Ai6MJLyhTsDZ) — HIGH

**Bug**: `Classify Contacts` only skipped contacts with `vapi_voicemail` or `vapi_qualified`. Contacts with other outcome tags could be re-enqueued on discovery.

**Fix**: Added `hasAnyBlocklistTag()` using the same 8-tag `BLOCKLIST_TAGS` constant. Also removes the campaign tag inline before skipping.

### Defense Layers (per-contact, now active)

| Layer | What blocks the call |
|--------|---------------------|
| 1 | **Campaign tag removed** after enqueue — poller never re-finds contact |
| 2 | **Queue marked `completed`** by callback — dialer FETCH ignores it (`WHERE status = 'pending'`) |
| 3 | **Dialer live-checks** all 8 outcome tags on GHL contact before every call via `Code - Check Phone` |
| 4 | **Intake Poller rejects** contacts with any of the 8 blocklist tags via `hasAnyBlocklistTag()` |
| 5 | **Queue dedup** `WHERE NOT EXISTS` blocks duplicate `pending`/`in_progress` entries |

### Key Constants (synced across all 3 workflows)

```
BLOCKLIST_TAGS = ['vapi_voicemail', 'vapi_voicemail_left', 'vapi_qualified', 'vapi_no_answer', 'vapi_busy', 'vapi_wrong_number', 'vapi_contact_disconnected', 'vapi_dnc']
```

### New Callback EOC Path

```
Before: Apply Tags → Should Re-enrich Phone
After:  Apply Tags → Postgres - Mark Queue Completed → Should Re-enrich Phone
```

## LinkedIn Workflow Fixes (2026-07-14 — 2026-07-15)

### Current Published Workflow Inventory (Updated 2026-07-16)

**Canonical LinkedIn path**: Dispatcher sends connection requests -> Acceptance Checker/State Sync marks contacts `connected` -> DM Sequence sends the 4-message cadence -> Unipile New Messages/Reply Backfill marks conversations active -> DM Suppression or sequence completion prevents future sends.

**Published / active LinkedIn workflows left running:**

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Active | Selects `ready` contacts from `linkedin_connection_state`, live-checks GHL tags/conversations, sends LinkedIn connection requests through Unipile, writes `requested` state. |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Active webhook | Receives Unipile relation/acceptance events at `/webhook/lt-linkedin-connection-accepted`, finds matching state row, marks contact `connected`, tags GHL with `linkedin_connected`. |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | Active schedule `15 */6 * * *` | Reconciles GHL contacts + LinkedIn profile URLs against Unipile and upserts ready/connection state rows. |
| LT - LinkedIn Connection State Upsert | Old7ZvyVYgFaJgDr | Active webhook | Canonical state-table write endpoint at `/webhook/lt-linkedin-connection-state-upsert`; used by dispatcher, acceptance, sync, suppression, and DM workflows. |
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Active schedule `0 12-22 * * 1-5` | Canonical post-connection DM sequence for contacts with `connection_status = connected`; sends 4 DMs and later marks complete. |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | Active webhook | Receives inbound LinkedIn message events at `/webhook/lt-unipile-linkedin-new-messages`; marks `dm_conversation_status = active` so outbound DM sequences stop. |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | Active schedule `*/10 * * * *` | Backfills/updates reply state from Unipile conversations so contacts with inbound replies are not messaged again. |
| LT - LinkedIn Relations Backfill | VPiHfBwzOHaJnHBY | Active daily 3:15am | Backfills LinkedIn relation/provider state, including synthetic rows where needed. |
| LT - LinkedIn DM Suppression from GHL Tag | IPN8jnR3XSurX0o1 | Active webhook | Receives GHL `stop_linkedin_dms` automation payload at `/webhook/lt-linkedin-suppress-dms`; resolves LinkedIn profile, applies `linkedin_dm_sequence_completed`, and terminal-upserts real + synthetic state IDs. |

**Unpublished / intentionally stopped:**

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished, `active=false` | Redundant one-touch LinkedIn follower DM path. It used separate follower state semantics and could overlap the canonical dispatcher -> connected -> 4-message DM sequence. |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished, `active=false` | Misconfigured with the LinkedIn Unipile account ID (`V9eiHiDpRmCtan0YNdzsQw`) and no account-type guard. It was sending the short Instagram templates as LinkedIn DMs using `instagram_dm_state`. |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual/test only | Not part of production sending. Use only for controlled testing. |

### Canonical DM Sequence Definition (d0tEtijajisIsYcs)

The production LinkedIn DM sequence sends 4 messages after a contact reaches `connection_status = connected` in `linkedin_connection_state`.

| Step | When Eligible | Behavior |
|------|---------------|----------|
| 1 | `sequence_step = 0` and `dm_sequence_started_at IS NULL` | Sends DM 1 immediately and sets `dm_sequence_started_at`. |
| 2 | Sequence started at least 3 days ago | Sends DM 2. |
| 3 | Sequence started at least 7 days ago | Sends DM 3. |
| 4 | Sequence started at least 10 days ago | Sends DM 4. |
| Complete | Sequence started at least 14 days ago and `sequence_step = 4` | Sends no DM; applies `linkedin_dm_sequence_completed`, sets `connection_status = completed`, and advances terminal state. |

The sequence skips if `payload_json.dm_conversation_status = active`, if GHL conversation lookup finds an inbound message, or if the reply lookup fails. Reply lookup failure is fail-closed.

### Fixes Applied 2026-07-16

- Traced malformed LinkedIn screenshot messages and identified they were sent by `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM sequence. The exact templates were `instagram.v1[1]` and `instagram.v1[2]`.
- Unpublished `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) after confirming it was using the LinkedIn Unipile account ID and separate `instagram_dm_state`, creating an accidental second LinkedIn DM path.
- Unpublished `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`) because the canonical 4-message connected-contact sequence supersedes the one-touch follower DM path.
- Expanded sanitizer coverage across all audited Unipile sender template nodes before unpublishing the redundant paths: template registries are pre-sanitized, and final outbound text is sanitized immediately before `POST /chats` or `POST /users/invite`.
- Cleaned stored mojibake/smart punctuation from audited DM template literals and verified no bad literal message text remained in sender nodes.

### Connection Acceptance Checker (3ttEvr5NMcQCS4Hp)
`access to env vars denied` on Postgres queryReplacement using `$env.UNIPILE_ACCOUNT_ID`. Node `N8N_BLOCK_ENV_ACCESS_IN_NODE` blocks env access. **Fix**: Replaced with hardcoded `V9eiHiDpRmCtan0YNdzsQw`.

### Connection State Sync (ceaKnz6E3onQrZpt)
Task runner timed out after 300s. Code node searches GHL + Unipile with 15 pages/200 contacts. **Fix**: Reduced maxPages 15→5, maxContacts 200→50.

### Follower DM Sequence (pq7XVajNFnnwMUTr)
Code node referenced `CFG.ghlApiBaseUrl`/`CFG.ghlApiKey` but both the Config node's outer `assignments` AND the Code node's CFG object lacked those fields. The Config node had a duplicate inner `parameters.assignments` (11 items with GHL creds) that n8n ignored because only the outer `parameters.assignments` (9 items, no GHL) is the live path. **Fix (2026-07-14)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config inner assignments — BUT this didn't fix the Code node CFG which still didn't read them. **Fix (2026-07-15)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config outer assignments AND to the Code node CFG object AND fixed the synthetic ID inbound check (see below).

### DM Sequence (d0tEtijajisIsYcs)
`Code doesn't return items properly` — **leading** backtick (not trailing) at start of `jsCode` field in node "Send DM Sequence Messages" caused unterminated template literal syntax error. **Fix (2026-07-14)**: Removed orphan backtick — BUT it was never published (draft versionId ≠ activeVersionId). **Fix (2026-07-15)**: Published the corrected draft; confirmed jsCode char[0] is 'c' (ASCII 99).

### Dispatcher Feeder Tag Check (fXxw5lanZcDmUrst)
`Feed Ready Queue` Code node checked `fullContact.tags` but GHL `GET /contacts/{id}` returns tags nested under `fullContact.contact.tags`. So blocking tags (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_queued`) were never detected — `skipped` was always 0. This caused every run to re-process already-queued contacts, but the UPSERT CASE in `linkedin_connection_state` prevented downgrading `requested`/`connected` back to `ready`, so `Fetch Ready Queue` always returned empty. **Fix**: Added GHL response unwrap: `var contactData = fullContact.contact ? fullContact.contact : fullContact;`. Tag check now correctly skips already-processed contacts.

**GHL API response gotcha**: `GET /contacts/{id}` returns `{ contact: { tags: [...], ... } }`. Code reading `.tags` directly will always get `undefined`. Always unwrap via `.contact` first.

### Bulk Feed (2026-07-13)
Discovered dispatcher had zero `connection_status = 'ready'` rows because all contacts in the state table were `requested` or `connected` from June 2026. User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook into `linkedin_connection_state` with `connection_status = 'ready'`. ~15,202 total executions recorded. Dispatcher's `Fetch Ready Queue` will now find contacts on its next scheduled run.

### Full 9-Workflow LinkedIn Audit + Fixes (2026-07-15)

Full review of all 9 LinkedIn workflows found 2 critical bugs, 3 high-severity issues, and 3 medium issues. Three fixes applied:

#### 1. Reply Backfill SQL Injection (QfJ2EZcc7lZwNgxj) — CRITICAL

**Bug**: `Apply Backfill Update` Postgres node used n8n template literal injection:
```
query: `={{ \`UPDATE ... SET payload_json = '\${$json.payload_json_sql}'::jsonb WHERE ghl_contact_id = '\${$json.ghl_contact_id}'...\` }}`
```
The Code node manually escaped with `.replace(/'/g, "''")`, but this is not safe against all SQL injection vectors (backslash/Unicode).

**Fix**: Changed Code node output to `JSON.stringify(nextPayload)` (no `''` escaping) and Postgres node to parameterized query:
```sql
UPDATE linkedin_connection_state
SET payload_json = $1::jsonb, metadata_json = $2::jsonb, ...
WHERE ghl_contact_id = $3
```
With `queryReplacement: "={{ [ $json.payload_json_sql, $json.metadata_json_sql, $json.ghl_contact_id ] }}"`.

#### 2. Follower DM Synthetic ID Inbound Check (pq7XVajNFnnwMUTr) — HIGH

**Bug**: `Process LinkedIn Followers` Code node passed `existing?.ghl_contact_id || 'linkedin:follower:' + providerId` to `hasInboundConversation`. For new followers (no Postgres row), `existing` was `undefined`, so the fallback synthetic ID hit GHL's conversation search API. GHL returned an error (no contact with that ID) → catch returned `{ blocked: true }` → **all new follower DMs were skipped**.

**Fix**: Only call `hasInboundConversation` when the Contact ID is a real GHL contact:
```js
var checkContactId = existing?.ghl_contact_id || '';
var inbound = checkContactId
  ? await hasInboundConversation.call(this, checkContactId)
  : { blocked: false, reason: '' };
```
New followers (no existing row) now skip the inbound check and allow the DM send (fail-open).

**Also fixed**: Added `ghlApiBaseUrl` and `ghlApiKey` to both Config node outer assignments AND Code node CFG object. Previously they were only present in a duplicate inner `parameters.parameters` object that n8n ignores.

#### 3. DM Sequence Backtick Published (d0tEtijajisIsYcs) — CRITICAL

**Bug**: Leading backtick had been removed from the draft in a prior fix session but the draft was never published — the active version still had the syntax error.

**Fix**: Published the corrected draft. Verified jsCode char[0] = ASCII 99 ('c').

### Unicode Encoding Fix — LinkedIn + Instagram Send Paths (2026-07-15)

**Bug**: Message templates contained Unicode smart punctuation (curly apostrophes `'`/`'` U+2018—U+2019, smart quotes `"`/`"` U+201C—U+201D, em-dashes `—`, ellipsis `…`, non-breaking spaces). Some already-stored templates also contained mojibake like `canΓÇÖt`. These multi-byte characters could get decoded as Latin-1/CP437 instead of UTF-8 when passing through the `JSON.stringify` → Unipile API chain, producing garbled text (e.g., `can't` → `canâ€™t` / `canΓÇÖt`).

**Fix**: Added/expanded `sanitizeMessage()` and `sanitizeTemplateRegistry()` across all Unipile send-capable message-template nodes. Stored templates are pre-sanitized when the Code node starts, and final outbound text is sanitized again immediately before `POST /chats` or `POST /users/invite`.

```js
function sanitizeMessage(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/\u00A0/g, ' ')
    .replace(/\u0393\u00C7[\u00D6\u00FF]/g, "'")
    .replace(/\u0393\u00C7[\u00A3\u00A5]/g, '"')
    .replace(/\u0393\u00C7[\u00F4\u00F6]/g, '-')
    .replace(/\u0393\u00C7\u00AA/g, '...')
    .replace(/\u00E2\u20AC[\u02DC\u2122]/g, "'")
    .replace(/\u00E2\u20AC[\u0153\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u0094]/g, '-')
    .replace(/\u00E2\u20AC\u00A6/g, '...');
}
```

Applied in the message assembly line of each workflow before the Unipile `POST /chats` or `POST /users/invite` call:
```js
var message = sanitizeMessage(msgTemplate.replace(/\{first_name\}/gi, firstName));
```

| Workflow | ID | Node fixed |
|----------|-----|------------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Sync Connected from Unipile; Send DM Sequence Messages |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Process LinkedIn Followers |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Dispatch LinkedIn Requests |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Process Instagram Outreach |

**Verification 2026-07-15 follow-up**: live versions were active/published after patching. Final audit passed for smart/mojibake sanitizer coverage, template registry pre-sanitization where present, immediate send-time sanitization, and no remaining bad literal message text in the audited sender template nodes.

Also created `scripts/suppress_linkedin_dms.py` for one-command DM suppression (resolves LinkedIn profile via Unipile, finds GHL contact, tags + state-table-terminates in both ID paths).

### Unfixed Issues (acknowledged, not fixed today)

| Severity | Issue | Workflow(s) |
|----------|-------|-------------|
| Medium | Two different PIT tokens in use (`pit-2d2e...` vs `pit-b278...`) | Dispatcher vs others |
| Medium | `payload_json` grows unbounded per row due to `||` merge on every upsert | Connection State Upsert (Old7Z) |
| Low | Reply Backfill runs every 10 min (`*/10 * * * *`) — 144x/day | Reply Backfill (QfJ2) |
| Low | Relations Backfill can produce thousands of synthetic rows | Relations Backfill (VPiHf) |
| Low | `n8n/lt-linkedin-dispatcher.ts` SDK file is stale vs live workflow | Dispatcher (fXxw) |

## Emerald Email Campaign (Activated 2026-07-07)

Dispatches ~14,702 unenrolled Emerald contacts through GHL email sequences using 4 sender addresses with safe warmup pacing.

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (all published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed} -- POST to n8n webhook /lt-email-event-ingest
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **8 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Bucket} + P2 per bucket
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed, WL - Micro - Email Inbound/Outbound/Open Counter

### Current State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing to Email_Events table within 3 min

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,165 | ~14,702 pending, ~5,463 released |
| Emerald_Release_Log | 250+ | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## DAN Email Campaign -- Brands and Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Dispatcher

| Workflow | ID | Status |
|----------|----|--------|
| LT - DAN Campaign Sender Release Dispatcher (Staged) | toUG1yPDmFG48KEP | Active (dryRun=false), every 30 min |

**Pipeline**: Schedule Trigger -> Config -> Ensure Release Log Table -> Fetch DAN Candidates -> Dispatch + Queue -> Write Release Log + Summary

**Config**: dryRun=false, candidateLimit=65, sender=cameron@livetransparent.com, senderFieldName=marketing_sender_email

**Fixes applied 2026-07-14:**
- Schedule changed from hourly to every 30 min (was only hitting 600/day, needed 1200+)
- Added `await new Promise(r => setTimeout(r, 250))` between each contact's GHL API calls to prevent rate limiting (was seeing 20-40% `error_fetch_contact` on early runs)
- candidateLimit increased from 50 to 65 to compensate for ~10 recurring DNC contacts per run (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms — have `do not contact` in GHL but stale data in report_raw_ghl_contacts)

**Fixes applied 2026-07-15 (code/logic audit):**
- **Brand starvation**: Changed `ORDER BY epc.source_list, epc.id ASC` → `ORDER BY RANDOM()` so brands and dispensaries interleave proportionally instead of brands always filling the 65-slot limit first
- **HTTP wrapper**: Removed `doHttpRequest` wrapper function and deprecated `$httpRequest` — all HTTP calls use `this.helpers.httpRequest(options)` directly
- **Sender rotation**: Added 4-sender pool (`cameron@livetransparent.{com,co,agency,org}`) with round-robin via `ci % senders.length`, matching Emerald's warmup pattern
- **Error logging**: `Only Queued` filter now passes all non-summary statuses to `DAN_Release_Log`; INSERT uses dynamic `$json.status` instead of hardcoded `'queued'`; error objects include `sender_email` and `run_id` for traceability
- **Jitter**: Delay randomized to `250 + Math.random() * 250`ms to prevent thundering herd on GHL API recovery

**Dispatch performance (2026-07-14):**
- First window run (12:00 UTC): 25 queued, 5 DNC, 20 errors (rate limited)
- After 250ms delay fix (12:30+): 40-44 queued, 6-10 DNC, **0 errors** consistently
- DNC contacts not written to DAN_Release_Log, recur each run until SQL tags catch up
- Emails confirmed sending: GHL conversation shows TYPE_EMAIL outbound automated

**Enrollment tags applied**:
- Brands: Enrollment Queue - DAN - Brands
- Dispensaries: Enrollment Queue - DAN - Dispensaries

**Deduplication**: Per-contact + per-campaign via DAN_Release_Log table (UNIQUE on contact_id, campaign).

**DNC/unsubscribe protection** (two layers):
1. SQL-level: filters report_raw_ghl_contacts.tags_raw for do not contact, do not nurture, unsubscribed, opted out, seq enrolled - dan
2. Per-contact live check: GET /contacts/{id} before dispatching

### ghl_contact_id Backfill (2026-07-13)

The import workflows (`LT - Brands Pool to Postgres + Sheets`, `LT - Dispensaries Pool to Postgres + Sheets`) set `ghl_contact_id = NULL`. The DAN dispatcher requires a non-null `ghl_contact_id`, so it found zero candidates despite contacts existing in GHL.

**Fix**: Backfilled 13,705 `ghl_contact_id` values from GHL export CSVs using three match passes:
1. Email match (lower+trim): +4,629
2. Phone match (digit-stripped): +5,691
3. Name+company match: +3,385

**Result**: 13,755 with IDs (3,645 brands / 10,110 dispensaries), 113 still missing (not in exports). **5,373 now eligible for DAN dispatch**.

**Export CSVs used** (delete after use):
- `Export_Contacts_brands pool_Jul_2026_5_24_AM.csv`
- `Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv`

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Workflows (all published)

- DAN - Brands Sequence (5d25147c-cd63-4c4f-ba49-a0e62c53ee0c)
- DAN - Dispensaries Sequence (ec24cbb8-bd0b-4e6e-8607-d93886a02034)
- DAN - Stop on Reply or Booked (d7ff2fc2-cdc2-4952-afa7-71cd9edfc490)

### Deck Download Automations

- WL - Micro - DAN Brand Deck Download -- trigger link bNK7txDSQJkvrgmmH9aZ -> tag -> Warm -> New + assign Jason
- WL - Micro - DAN Dispensary Deck Download -- trigger link DDPOwxFCexuf3cYGOAPt -> tag -> Warm -> New + assign Jason
- 3x open handling via WL - Micro - Email Open Counter + Assignment to Jason (42aa5940)

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Signature (all templates)

Cameron Karkut
Co-Founder / Head of Sales and Strategy
714-469-6406
LiveTransparent.com

## Reporting System

| Workflow | ID | Status |
|----------|----|--------|
| GHL Daily Leads Ingest | osIJOgBmWITF5Yuv | Active |
| GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 | Active |
| GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l | Active (4hr schedule) |
| GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG | Active |
| GHL Daily Social Ingest | QZoqCaTwDhbym80O | Active |
| GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq | Active |
| GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi | Active |
| GSC Daily Ingest | xHqmCC1vOeZ11gCd | Active |
| GSC Rollup Bridge | fOVBHwti9rC3qrLV | Active |
| Report Attribution Bridge | Y0TU7Il71JswxOBp | Active |
| Report Daily Rollups | EUeOiRttoVLQ9zF9 | Active |
| Report Executive Summary API | Bukc0mgOD2r7V6ED | Active |
| Report QA and Alerts | M5mXcDTFSko6EdHb | Active |
| Report Config Sync | aomO3Z4AXJIgEvvN | Active |
| Report Publish Refresh | 3gXztCnBEN6sGINb | Active |
| Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 | Active |
| Report Pipeline Velocity | iFfwh0jpYUZoDhDR | Active |
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV | Active (daily 6am ET) |
## Other Live Systems

- **SimpleTexting**: Send, sequencer, delivery, inbound reply, unsubscribe, and idempotent-send workflows are live/available in n8n. The scheduled pool dispatcher is active as of 2026-07-18, targets GHL tag `sms_drip`, runs weekdays at `10:15am` and `3:00pm` ET, uses `candidateLimit=10`, and has `defaultDryRun=false` for live sends. Sequencer waits 2 days between SMS steps. Inbound replies add `simpletext_replied`, remove `simpletext_ongoing`, mark campaign state `replied`, and suppress future campaign/direct sends; `simpletext_stop` remains the opt-out hard stop. `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) posts a Slack alert through node `Post to Slack` with title `Inbound SimpleTexting Reply`, then posts the inbound message to GHL Conversations under `SimpleTexting SMS` via `Post to GHL Conversations` node using `type: "Custom"`, `conversationProviderId: "6a5b91913953360948dd59f1"`, and `altId`. Monitor first Monday executions and first real reply/unsubscribe closely before raising volume.
- **SimpleTexting GHL Conversations provider**: **LIVE** as of 2026-07-20. Separate GHL private app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`. `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) receives GHL outbound replies, validates provider ID, normalizes phone to E.164, checks `simpletext_stop` tag, and sends via the idempotent send workflow (`gwaEpWDpTIwsafi8`) → SimpleTexting API. Outbound campaign sends mirror into GHL Conversations via `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). `simpletexting_conversation_map` table created in Postgres keyed by `(conversation_provider_id, alt_id)`. GHL Conversations is the primary operator inbox for SimpleTexting SMS; Slack alert for inbound replies is preserved.
- **Unipile/Instagram**: Instagram DM Sequence (`iCnY6ccdHhfJg3sf`) is **unpublished**. It was misconfigured with the LinkedIn Unipile account ID and sent Instagram templates as LinkedIn DMs. Do not republish until it has a real Instagram Unipile account ID and account-type guard.
- **Instagram inbound bridge**: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active at `/webhook/lt-unipile-instagram-new-messages`. It normalizes Unipile Instagram inbound payloads, conservatively resolves an existing GHL contact before creating one, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token via `POST /oauth/locationToken`, and posts inbound messages into GHL Conversations under the `Instagram via Unipile` tab. Post-merge cleanup on 2026-07-16 repointed `instagram_conversation_map.id = 1` for chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`; the temporary duplicate `4V2oTmM7lWya3Nmtmp1Y` created during verification was deleted.
- **Social provider outbound router**: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active at `/webhook/lt-social-provider-outbound`. Fixed 2026-07-16: POST webhook `responseMode` now uses `responseNode`, map tables are created defensively, payload message text is preserved through Postgres lookup, and Unipile send uses the working `api42.unipile.com:17256/api/v1` base. Canonical provider IDs are SMS-type additional custom conversation providers: `Instagram via Unipile` = `6a58a1193cdfc36997580a68` and `LinkedIn via Unipile` = `6a58a14ff3023bea3783c152`. Inbound message API must use `type: "Custom"` with `conversationProviderId` + `altId`; do not include `emailTo`/`emailFrom`/`subject` or dummy contact phone/email data. Deleted Email provider IDs `6a5893d11e9368345005f66e` and `6a5892b9107668309b3f85ac` must not be reused. Verified Instagram and LinkedIn inbound as `TYPE_CUSTOM_PROVIDER_SMS`; Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` both map to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, with LinkedIn conversation `Ze8o3KbsrwuAXQ3KK5ge`. LinkedIn normalizer handles Unipile's form-encoded single-JSON-key webhook shape. Direct outbound router smoke tests after map repair passed: Instagram message `vjdEYSk9XD6R0I46oPWLwA`, LinkedIn message `C7I9944kWsSKutX2XhZEpA`.
- **Social provider bridge handoff**: Full build context, operator inbox runbook, monitoring gaps, and next steps for `LinkedIn via Unipile` + `Instagram via Unipile` GHL bidirectional messaging are in `docs/strategy/unipile-ghl-bidirectional-integration.md`. Read this before changing provider workflows.
- **Unipile/LinkedIn**: Active production path is dispatcher → acceptance/state sync → canonical DM sequence. Follower DM (`pq7XVajNFnnwMUTr`) is **unpublished**. Current published workflow inventory is documented in `Current Published Workflow Inventory` above. Guardrails block John-branded copy.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: Workflow exports staged in repo and corresponding SimpleTexting workflows are live in n8n. See docs/outreach/outreach_messages.docx for SMS source copy. Current launch settings: `sms_drip`, 10 contacts/run, weekdays 10:15am and 3:00pm ET, 2-day inter-step delay, reply/STOP suppression.

### SimpleTexting SMS via GHL — Bidirectional Provider (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

#### Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Receives GHL outbound messages at `/webhook/lt-simpletexting-provider-outbound`, validates provider ID, normalizes phone to E.164, sends via idempotent boundary → SimpleTexting API. Skips business-hours guard for human replies. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Slack alert preserved. Now also posts inbound messages to GHL Conversations under `SimpleTexting SMS` via `type: "Custom"` + `conversationProviderId`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Mirrors successful outbound campaign sends into GHL Conversations under `SimpleTexting SMS`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated SMS boundary. Called by outbound router and campaign send paths. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Active | `sms_drip`, 10/run, weekdays 10:15am + 3:00pm ET, `defaultDryRun=false`. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Active | 6-step flow, 2-day inter-step delay. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | No changes needed. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | No changes needed. |

#### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

#### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

#### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

## Key Files

- repomix-output.md
- .env
- Project Status and Next Steps.md
- Export_Contacts_brands pool_Jul_2026_5_24_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_for fresh Linkedin connections_Jul_2026_2_16_AM.csv (GHL export, 14,987 contacts, used for LinkedIn dispatcher bulk feed 2026-07-13)
- GHL Live Transparent CRM/
- postgres/reporting-bootstrap.sql
- n8n/docker-compose.yml
- n8n/voice-agent/
- n8n/lt-linkedin-dispatcher.ts
- n8n/workflows/lt-linkedin-dm-sequence.ts
- n8n/workflows/lt-apollo-queued-timeout-reaper.ts
- n8n/workflows/lt-emerging-pool-import.ts
- scripts/suppress_linkedin_dms.py
- scripts/fix_intake_poller.js
- n8n/workflows/lt-simpletexting-send-sms.json
- n8n/workflows/lt-simpletexting-pool-dispatcher.json
- n8n/workflows/lt-simpletexting-campaign-sequencer.json
- n8n/workflows/lt-simpletexting-inbound-reply.json
- n8n/workflows/lt-simpletexting-delivery-events.json
- n8n/workflows/lt-simpletexting-unsubscribe-events.json
- reports/embed/executive/index.html
- reports/nginx.conf
- Backup of all n8n workflows/
- Project Specifications.md
- docs/campaigns/Vapi_Brand_Campaign.docx
- docs/campaigns/Vapi_Dispensary_Campaign.docx
- docs/strategy/unipile-ghl-bidirectional-integration.md
- plan.md
- marketing/email-marketing/emerald-email-campaign/plan.md
- marketing/email-marketing/emerald-email-campaign/dispatcher-plan.md
- marketing/email-marketing/emerald-email-campaign/workflow-mapping.md

## VPS SSH Access

- Host: 89.117.21.29 (hostname vmi3077218), user root
- SSH key: C:\Users\edmon\.ssh\local-upload (Ed25519, no passphrase, generated via Coolify)
- Permission fix: paramiko works directly. To use ssh.exe: icacls $keyPath /reset /inheritance:r /grant "$env:USERNAME:(R)"
- Reference keys on server: vps_caddy_key, vps_upload, id_ed25519_vps_whitefriar -- all passphrase-encrypted
- GHL-ready CSV files on n8n server: /home/node/.n8n-files/GHL_Ready_{Brands,Dispensaries}.csv
- Local copies: data/GHL_Ready_{Brands,Dispensaries}.csv

### Postgres Reference

- emerging_pool_contacts: 13,868 contacts (3,668 brands + 10,200 dispensaries)
  Fields: emerald_contact_id, source_list, first_name, last_name, primary_email, primary_phone, company_name, tags, ghl_contact_id, ghl_opportunity_id, ghl_import_status, raw_json (JSONB). UNIQUE on (emerald_contact_id, source_list).
  ghl_contact_id coverage: 13,755 filled (3,645 brands / 10,110 dispensaries), 113 null (not in exports).

## John -> Jason Migration (2026-07-07)

### What changed

- Message content: "John from Transparent eCom" -> "Jason from Transparent eCom" in all SMS templates
- Email signatures: "Best, John" -> "Best, Jason" in all HTML templates
- Sender info: john@livetransparent.com -> jason@livetransparent.com
- Transfer tool: ok_transfer_to_john -> ok_transfer_to_jason (same phone +15622474600)
- All assistant system prompts updated

### What stayed the same (keys NOT changed)

- Template keys: john_sms1 through john_sms5 -- kept as-is because GHL automations reference these keys
- Display names: "John SMS 1 - Initial Outreach" etc. -- kept for consistency with keys
- GHL payloads still use "templateKey": "john_sms4" -- n8n resolves to updated message text

### User IDs

- Jason Bornillo (jason@livetransparent.com): yU85G6kfhtW4vUtx3QE6
- Cameron Karkut (cameron@livetransparent.com): 03p5GatJBH7i9zjMaIzm
- Ed Cadorniga (ed@livetransparent.com): gePIeuHOEsAiPVA1mfOR

### GHL Status (2026-07-10)

- **John-branded LinkedIn invite resolved**: Workflow 25cd82a2 repointed from "Create Task" to n8n webhook with Cameron default message + send:true.
- **SMS failed-send workflows verified clean**: 41c6aecd and a99f96d9 -- no hardcoded John messages.
- **GHL JohnFollowup Emails and SMS** (f6b44e34): Owner manually updated all Send email actions to Jason.
- **Jason user ID found**: yU85G6kfhtW4vUtx3QE6 -- was agency-level, reassigned to sub-account.

## Tool & CLI Preferences

These CLI tools are installed and available via PATH. Prefer them over slower alternatives:

| Tool | Use instead of | Why |
|------|---------------|-----|
| rg | findstr, Select-String, grep | 10-100x faster text search, .gitignore-aware |
| fd | Get-ChildItem, dir | Blazing fast file finding by name/pattern |
| bat | cat, Get-Content | Syntax-highlighted file viewing with line numbers |
| jq | manual JSON parsing | Process API/LLM JSON responses inline |
| yq | manual YAML parsing | YAML equivalent of jq |
| xsv | CSV processing in Python/JS | Fast CSV search, slice, stats, join |
| delta | default git diff | Syntax-highlighted, side-by-side git diffs |
| fzf | scrolling through lists | Interactive fuzzy finder |
| zoxide | cd | Learns your navigation patterns, z <fragment> jumps anywhere |
| hyperfine | manual timing | Benchmark any command with statistical analysis |
| sd | sed, regex replaces | Simpler find-and-replace syntax |
| ast-grep | regex-only code search | Structural code search that understands syntax trees |
| eza | ls, dir | Modern ls with icons, colors, tree view |

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate repomix-output.md so next-session context is up to date:

1. . $PROFILE
2. packlive

This stages key files into C:\TempRepomixStaging, runs npx repomix --style markdown --compress --remove-comments --remove-empty-lines, and copies the result back to the project root.
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
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), **DAN email campaign** (backfilled ghl_contact_id 2026-07-13, 5,373 eligible for dispatch), **Apollo phone enrichment** (repaired 2026-07-14, new polling workflow), voice, reporting, LinkedIn outreach (canonical sender path and suppression guardrails hardened), the **LinkedIn/Instagram via Unipile -> GHL bidirectional conversation provider integration**, and the SimpleTexting SMS campaign stack (dispatcher live at low volume as of 2026-07-18).
- Social provider integration handoff: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- SimpleTexting provider handoff is now LIVE (2026-07-20). GHL app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). `/webhook/lt-simpletexting-provider-outbound` routes GHL outbound replies through idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Outbound campaign sends mirror into GHL Conversations. `simpletexting_conversation_map` table live. Full E.164 migration across delivery/unsubscribe workflows and STOP tag guard in outbound router are deferred.

## Vapi Campaign Rollout

### GHL Tag IDs

| Tag | ID |
|-----|----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Active 2026-07-14

Both workflows published and running:
- **Intake Poller** (bYk1Ai6MJLyhTsDZ): Active, every 10 min, 30 contacts/cycle, tag rotation across all 4 pools (vapi_campaign_brand, vapi_campaign_dispensary, brands_pool, dispensaries_pool).
- **Outbound Dialer** (r7UjWLndmc6EqEUW): Active, `*/2 13-22 UTC Mon-Fri`. Places calls via Vapi using campaign-specific assistants (Alex for brand, Jordan for dispensary). ET-forward schedule: starts 9am ET.

### Remaining Operational Items

- App reinstalled in Live Transparent with canonical SMS-type additional custom providers: LinkedIn `6a58a14ff3023bea3783c152`, Instagram `6a58a1193cdfc36997580a68`.
- Instagram GHL UI outbound reply and direct router smoke test both route to Unipile. Post-merge map repair points Instagram and LinkedIn social chats to canonical contact `XZ4yChllGBdcsVxhFRDe`.
- LinkedIn inbound under provider `6a58a14ff3023bea3783c152` is verified end-to-end; optional next check is a controlled LinkedIn GHL UI outbound reply from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Register/confirm Unipile Instagram inbound webhook points to `https://automations.livetransparent.com/webhook/lt-unipile-instagram-new-messages`.
- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Monitor the next real Instagram inbound after GHL duplicate cleanup; map rows are repaired, but avoid further artificial inbound replays unless needed because they create visible conversation messages.
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL.
- Monitor the live SimpleTexting SMS dispatcher after launch: `sms_drip`, `candidateLimit=10`, `defaultDryRun=false`, weekdays `10:15am` and `3:00pm` ET, 2-day inter-step delay, reply/STOP suppression.
- SimpleTexting GHL Conversations provider is LIVE: `SimpleTexting SMS` (`6a5b91913953360948dd59f1`) routes GHL outbound replies through the outbound router (`f4VoO1lBWkYRcQai`) → idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Outbound campaign sends mirror into GHL Conversations via `Q3Ivnwe4z2Y3cD7A`. Remaining: full E.164 normalization across delivery/unsubscribe workflows, STOP tag guard in outbound router.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state sync after the fail-closed patch.

### Completed

- **2026-07-20**: SimpleTexting GHL Conversations bidirectional provider is LIVE. Separate `LiveTransparent SimpleTexting SMS` GHL app with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Built `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) at `/webhook/lt-simpletexting-provider-outbound` — validates provider, E.164-normalizes phone, routes through idempotent send to SimpleTexting. Patched `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) to post inbound messages to GHL Conversations under `SimpleTexting SMS` with `type: "Custom"` + `conversationProviderId` (Slack alert preserved). Patched `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) to mirror outbound campaign sends into GHL Conversations. Created `simpletexting_conversation_map` table in Postgres. First end-to-end test passed: GHL → outbound router → idempotent send → SimpleTexting (201, message `6a5e46218ebb0860da623b0f`). Remaining: full E.164 normalization across delivery/unsubscribe workflows.
- **2026-07-16**: Verified the GHL Custom Conversation Provider bridge for Instagram and LinkedIn via Unipile using canonical SMS-type custom providers. Inbound uses `type: "Custom"` + `conversationProviderId` + `altId` with no dummy phone/email fields. `LT - Instagram Unipile New Messages` and `LT - LinkedIn Unipile New Messages` are active and published; LinkedIn replay verified `TYPE_CUSTOM_PROVIDER_SMS` on contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`. GHL duplicate cleanup consolidated Edmundo Cadorniga to `XZ4yChllGBdcsVxhFRDe`; Instagram map row `1` and LinkedIn map row `2` were repointed there. Direct outbound router checks passed for Instagram and LinkedIn. Full handoff in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **2026-07-16**: Cleaned up duplicate LinkedIn sender paths. Traced malformed LinkedIn screenshot DMs to misconfigured `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`), which used the LinkedIn Unipile account ID and `instagram_dm_state`; unpublished it. Also unpublished redundant `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`). Production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.
- **2026-07-15**: Built and published automated LinkedIn DM suppression workflow (`LT - LinkedIn DM Suppression from GHL Tag`, IPN8jnR3XSurX0o1). GHL tag `stop_linkedin_dms` triggers a GHL automation → POSTs to `/webhook/lt-linkedin-suppress-dms` → resolves LinkedIn profile via Unipile, tags `linkedin_dm_sequence_completed`, upserts `linkedin_connection_state` to terminal for both real contact and synthetic `linkedin:follower:{providerId}`. Full audit confirmed all 3 send paths (DM Sequence, Follower DM, Dispatcher) correctly block suppressed contacts. Fixed dispatcher Feeder gap: added `linkedin_dm_sequence_completed` to blocking tag list.
- **2026-07-15**: Unicode/mojibake encoding fix expanded across all audited Unipile message sender nodes: LinkedIn DM Sequence (`Sync Connected from Unipile`, `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. Templates are pre-sanitized at runtime and final outbound text is sanitized immediately before Unipile API calls. Handles smart punctuation plus already-garbled forms like `canâ€™t` / `canΓÇÖt`. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.
- **2026-07-14**: Vapi voice system activated. Published Intake Poller + Outbound Dialer. Fixed Trigger Apollo Enrichment auth and Remove Tag - Enriching URL. Added pagination, 30-contact cap, brands_pool/dispensaries_pool tag search, and tag rotation. Added state-to-timezone inference for both poller and dialer. Shifted dialer cron to `*/2 13-22` UTC for 9am ET start; widened business hours guard to 8-18 CT.
- **2026-07-14**: Apollo phone enrichment repaired. Created and published LT - Apollo Phone Enrichment Polling (JH8ShfpglWmLMZ3l, every 30 min). Replaces dead webhook-based pipeline. Syncs profile data immediately, requests phone numbers via async callback to V4 handler.
- **2026-07-13**: Backfilled 13,705 ghl_contact_id values into emerging_pool_contacts from GHL export CSVs (email + phone + name/company match). DAN dispatcher now has 5,373 eligible contacts.
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
- If someone responds on LinkedIn, immediately suppress them from all remaining automated LinkedIn DMs and persist that suppression in the shared state.

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
5. Confirm a replied LinkedIn contact stays excluded from all later automated DM steps, not just the next scheduled run.
6. Prepare a single SMS test contact and confirm one SMS send is tagged in state.
7. Simulate an inbound SMS reply and confirm the response workflow updates the same canonical state.
8. Confirm unsubscribe handling blocks any future SMS sends for opted-out contacts.
````

## File: Project Status and Next Steps.md
````markdown
# LiveTransparent Project Status and Next Steps

Updated: 2026-07-20 (SimpleTexting GHL Conversations provider LIVE)

## Source Of Truth

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Voice stack**: ACTIVE since 2026-07-14, hardened 2026-07-16. Intake Poller + Outbound Dialer + Callback published. Poller searches 4 tag pools with rotation, 30/cycle, now removes the source campaign tag after enqueueing to prevent re-discovery. Dialer fires `*/2 13-22 UTC Mon-Fri` (9am ET start). Callback now marks queue `completed` after every end-of-call event. 8-tag blocklist (`vapi_voicemail`, `vapi_voicemail_left`, `vapi_qualified`, `vapi_no_answer`, `vapi_busy`, `vapi_wrong_number`, `vapi_contact_disconnected`, `vapi_dnc`) synced across all 3 workflows with 5-layer defense against spam.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences.
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (65/run every 30 min, 1,560/day capacity). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery.
- **Apollo phone enrichment**: ACTIVE and hardened 2026-07-16. Production path is polling + V4 callback + reaper. Legacy staged webhook orphans were canceled, poller now re-discovers `queued_phone`, callback provider failures map to `callback_failed`, and known blank contacts were backfilled into `queued_phone`.
- **LinkedIn**: Production path is dispatcher -> acceptance/state sync -> canonical 4-message DM sequence. Follower DM and misconfigured Instagram DM sender paths are unpublished. Guardrails include fail-closed reply checks, inbound/reply state sync, terminal DM completion tagging, and GHL `stop_linkedin_dms` suppression.
- **Instagram**: old DM Sequence is unpublished after it was found using the LinkedIn Unipile account. New inbound bridge is active and posts messages into GHL Conversations under `Instagram via Unipile`.
- **Social provider bridge**: Instagram and LinkedIn inbound both work through SMS-type custom conversation providers (`LinkedIn: 6a58a14ff3023bea3783c152`, `Instagram: 6a58a1193cdfc36997580a68`). Inbound uses `type: "Custom"`, not `SMS`, and avoids dummy phone/email data. GHL duplicate cleanup consolidated Edmundo Cadorniga to canonical contact `XZ4yChllGBdcsVxhFRDe`; both Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` now map there. GHL Conversations is the operator-facing inbox; no dedicated macro dashboard or alert digest is live yet. Detailed handoff and operator runbook live in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **Reporting**: GA4, GHL, GSC ingestion live. Executive report live in GHL.
- **SMS campaign**: SimpleTexting dispatcher is live as of 2026-07-18. SimpleTexting GHL Conversations bidirectional provider is **LIVE** as of 2026-07-20 — separate `SimpleTexting SMS` provider (`6a5b91913953360948dd59f1`), outbound router routes GHL replies through idempotent send to SimpleTexting, inbound posts to both Slack and GHL Conversations, outbound campaign sends mirror into GHL Conversations.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.

## Email Campaign — Emerald (Active 2026-07-07)

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (All Published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed}
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **8 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Bucket} + P2 per bucket
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed, WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,165 | ~14,702 pending, ~5,463 released |
| Emerald_Release_Log | 250+ | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## Email Campaign — DAN Brands & Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Status

- Templates: CREATED (10/10 -- 5 Brand + 5 Dispensary)
- Tags: CREATED (5/5 -- deployed via GHL API)
- Dispatcher: LIVE (toUG1yPDmFG48KEP, active with defaultDryRun=false, every 30 min, candidateLimit=65)
- GHL Workflows: ALL PUBLISHED (3/3)
- Deck Download automations: CREATED in GHL
- ghl_contact_id backfill: COMPLETED 2026-07-13 (13,705 IDs backfilled via email/phone/name matching)
- **5,373 contacts now eligible for DAN dispatch (up from 13 before backfill)**
- **First dispatches confirmed**: Emails sending via GHL (TYPE_EMAIL outbound automated verified)
- **Rate limiting fix**: 250ms delay added between GHL API calls — errors dropped from 40% to 0%
- **2026-07-15 audit**: 5 fixes applied (brand starvation, HTTP wrapper, sender rotation, error logging, jitter)
- **GHL templates verified**: All 10 DAN templates in GHL match repo HTML files exactly

### GHL Workflows

| Workflow | ID |
|----------|-----|
| DAN - Brands Sequence | 5d25147c-cd63-4c4f-ba49-a0e62c53ee0c |
| DAN - Dispensaries Sequence | ec24cbb8-bd0b-4e6e-8607-d93886a02034 |
| DAN - Stop on Reply or Booked | d7ff2fc2-cdc2-4952-afa7-71cd9edfc490 |

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Template IDs (Brands, folder 6a4f6b06a3e9bfb4f9ebe8ad)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fdf525ebffbb911d88c | DAN - Brand 1 - Quick Question |
| 2 | 6a4f6fe0f34b953ec0cfcf5d | DAN - Brand 2 - How It Works |
| 3 | 6a4f6fe15e7d25184dafed44 | DAN - Brand 3 - Housing Works |
| 4 | 6a4f6fe2525ebffbb911d899 | DAN - Brand 4 - Short Version |
| 5 | 6a4f6fe3890f1fb4ac750664 | DAN - Brand 5 - Closing |

### Template IDs (Dispensaries, folder 6a4f6b128c6f614ebf8ba9e9)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fe4890f1fb4ac750680 | DAN - Dispensary 1 - Foot Traffic |
| 2 | 6a4f6fe41ad559bda229477d | DAN - Dispensary 2 - How It Works |
| 3 | 6a4f6fe55e7d25184dafed8a | DAN - Dispensary 3 - Housing Works |
| 4 | 6a4f6fe6f74b73e4b5b9ad8d | DAN - Dispensary 4 - Founding Partner |
| 5 | 6a4f6fe71ad559bda2294793 | DAN - Dispensary 5 - Closing |

**Duplicate**: 6a4f6fcdf74b73e4b5b9ac0b — already removed from GHL (verified 2026-07-15)

## Voice Workflows

Phone: +1 (562) 534 1977
Callback webhook: https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback

### Active

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Webhook |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Webhook |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Webhook |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Manual |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (polls `*/2 13-22 UTC Mon-Fri`, ET-forward schedule) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **ET-forward dialer schedule**: cron shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. Initial business hours guard widened from 9-17 to 8-18 CT so it doesn't gate early ET calls.

### Fixes Applied — Round 2 (2026-07-14, Full Vapi Audit)

A comprehensive logic/code/optimization audit of all 12 Vapi workflows found 5 bugs across 3 active workflows, all fixed and published:

**1. Race condition: Dialer could send duplicate calls** (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` was a read-only `SELECT...LIMIT 1`. Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item. Fixed: changed to `UPDATE...FROM...RETURNING` that atomically locks the row at fetch time.

**2. `report_referral` tool was dead code** (fx4UvKUWbqJEY3LK)
Routed to end-of-call handler that checked `endedReason`/`analysis.summary` — absent on tool call payloads. Node returned `[]` silently. Fixed: re-routed to `Respond - 200`.

**3. Intake Poller could create duplicate queue entries** (bYk1Ai6MJLyhTsDZ)
INSERT lacked `WHERE NOT EXISTS` dedup check. Fixed: wrapped INSERT with `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also fixed `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing).

**4. Workflow-crashing tag removals** (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes lacked `continueOnFail`. A flaky GHL API call crashed the workflow after enqueue/enrich/skip already succeeded. Fixed: enabled `continueOnFail: true` on all three.

**5. Timer race condition** (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain. Fixed: replaced `timersScheduled` boolean with `timersScheduledAt` timestamp and 60-second dedup window.

### Queue State

~28 contacts initially enqueued from enriched vapi_campaign_brand/dispensary pools. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer picks up from queue during business hours (13-22 UTC Mon-Fri, ET-forward).

### LinkedIn Queue State

Legacy step-4 LinkedIn DM rows are now marked with `linkedin_dm_sequence_completed` and excluded from future DM selection. The GHL connect dispatcher was stuck with 0 `ready` contacts because its feeder tag check was broken (never detected blocking tags). Fixed 2026-07-14 by unwrapping GHL's nested `contact.tags` response. 14,987 contacts from CSV bulk-upserted as `connection_status = 'ready'` on 2026-07-13. Dispatcher should now find contacts on its next scheduled run.

### Call History Summary (voice_call_attempt)

1,711 total attempts across 1,045 unique contacts. Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18.

## LinkedIn Workflows (Production Active + Duplicate Send Paths Stopped)

| Workflow | ID | Schedule | Notes |
|----------|----|----------|-------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | 0 12-22 * * 1-5 | Fixed trailing backtick in jsCode; added template pre-sanitize + send-time sanitize in both DM sender nodes |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished | Redundant one-touch follower DM path; stopped 2026-07-16 after canonical connected-contact DM sequence was confirmed as the only production DM path |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | */15 15-21 * * 1-5 | Fixed GHL response unwrap in tag check; added send-time sanitize for invites; added linkedin_dm_sequence_completed to Feeder tag block |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | 15 */6 * * * | Reduced maxPages 15→5, maxContacts 200→50 |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Webhook | Replaced $env.UNIPILE_ACCOUNT_ID with hardcoded value |
| LT - LinkedIn Connection State Upsert (Unipile) | Old7ZvyVYgFaJgDr | Webhook | No changes |
| LT - LinkedIn Unipile New Messages (Unipile) | 7o5EBdvwAuIaWW7k | Webhook | No changes |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual only | No changes |
| **LT - LinkedIn DM Suppression from GHL Tag** | **IPN8jnR3XSurX0o1** | **Webhook** | **NEW 2026-07-15. GHL tag stop_linkedin_dms → webhook → Unipile lookup → GHL tag + state table terminal** |

Intentionally stopped non-canonical sender: `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) is unpublished. It was using the LinkedIn Unipile account ID and sending Instagram templates as LinkedIn DMs via `instagram_dm_state`.

Guardrails: John-branded copy blocked before Unipile send. Invite defaults say Transparent eCom (not LiveTransparent).

Outbound guardrails: DM sends now fail closed if the reply lookup fails, and both DM / request paths skip when an inbound conversation is already present.

### 2026-07-15 Unicode Encoding Fix
All audited Unipile message sender nodes now sanitize message text before API calls, and template registries are pre-sanitized where present. Coverage includes LinkedIn DM Sequence (`Sync Connected from Unipile` and `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. `sanitizeMessage()` handles smart punctuation plus mojibake forms like `canâ€™t` / `canΓÇÖt`. Final live audit passed: active versions published, send-time sanitization present, registry pre-sanitization present where applicable, and no remaining bad literal template text in audited sender nodes. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.

### 2026-07-16 Sender Path Cleanup
Malformed LinkedIn screenshot messages were traced to `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM Sequence. Unpublished both `iCnY6ccdHhfJg3sf` and redundant `pq7XVajNFnnwMUTr`; production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.

### 2026-07-14 Fixes Summary
- **Connection Acceptance Checker**: `$env.UNIPILE_ACCOUNT_ID` blocked by N8N_BLOCK_ENV_ACCESS_IN_NODE → hardcoded
- **Connection State Sync**: Code node timed out at 300s → reduced batch sizes
- **Follower DM Sequence**: Code referenced missing Config fields → added them
- **DM Sequence**: Trailing backtick in `jsCode` caused syntax error → removed
- **Dispatcher feeder tag check**: `GET /contacts/{id}` returns tags at `contact.tags`, not flat `tags`. Whole pipeline was stuck because blocking tags were never detected. Fixed by unwrapping through `.contact` first.

### Dispatcher Queue State
The `linkedin_connection_state` table was exhausted (all contacts at `requested`/`connected` from June). User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook as `connection_status = 'ready'`. Dispatcher's Fetch Ready Queue should now find contacts on next run.

## Instagram

### Active

| Workflow | ID | Status | Notes |
|----------|----|--------|-------|
| LT - Instagram Unipile New Messages | pISlgYUsyJIrLuJd | Active webhook | Receives Unipile Instagram inbound payloads at `/webhook/lt-unipile-instagram-new-messages`, normalizes identity, creates/updates GHL contacts, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token, and posts inbound messages into GHL Conversations under `Instagram via Unipile`. |

### Stopped

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished | It was using LinkedIn Unipile account `V9eiHiDpRmCtan0YNdzsQw` and could send Instagram templates as LinkedIn DMs through `instagram_dm_state`. Do not republish until rebuilt with Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, account-type guard, reply suppression, and safe cadence. |

### 2026-07-16 Inbound Mapping Status

- Detailed build context, endpoint contracts, known test payload, and next steps: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Confirmed real Instagram Unipile account: `F2UprZ8aQc6Qm9CYYWU6cg` (`Transparent eCom`).
- Confirmed test inbound identity: `edmundocadorniga`, profile provider ID `6361495593`, messaging/provider ID `109928757071246`, chat ID `yx-R-9J6XdWaFpGOQd1JFA`.
- Created GHL custom fields for Instagram username/profile URL/profile provider ID/chat attendee ID/chat ID.
- Post-merge cleanup: GHL duplicate contacts for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; `instagram_conversation_map.id = 1` now maps chat `yx-R-9J6XdWaFpGOQd1JFA` to that canonical contact.
- Inbound OAuth fix: the workflow converts the stored agency token to a location token inline before calling GHL inbound APIs.
- Direct outbound router test: POST to `/webhook/lt-social-provider-outbound` routed the known Instagram contact/chat to Unipile successfully with message id `DOfjxs8_Xm26V5Ee1IO7PQ`.
- Map repair verification: temporary maintenance workflow `nuuB3qCKxr7J6iPw` repointed Instagram map row `1` and LinkedIn map row `2` to `XZ4yChllGBdcsVxhFRDe`, then was archived. Direct outbound router checks succeeded for Instagram (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn (`C7I9944kWsSKutX2XhZEpA`).
- GHL UI outbound verification: message `this is a test reply from GHL to Instagram` routed through `LT - Social Provider Outbound Router` to Unipile message `iEJO1vnvWVGwbk7ril1__A`.

### Social Provider Next Steps

- Monitor the next real Instagram inbound after duplicate cleanup; avoid artificial replays unless needed because they create visible conversation messages.
- Confirm Unipile Instagram webhook delivery to `/webhook/lt-unipile-instagram-new-messages` in production.
- `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) direct webhook path is fixed and routes canonical contact `XZ4yChllGBdcsVxhFRDe` to Instagram and LinkedIn via Unipile successfully using canonical provider IDs.
- Optionally run a controlled LinkedIn GHL UI outbound reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Build and verify a lightweight macro alert/digest path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.
- Rebuild Instagram outbound/follower DM only after the bidirectional inbox path is stable and guarded.

## Apollo Phone Enrichment (Repaired 2026-07-14, Audited + Hardened 2026-07-15)

### Before Fix (2026-07-14)

All 3 webhook-based workflows had 0 executions since 2026-05-13. 1,279 contacts collected `callback_timeout`. Entire pipeline was dead.

### After Fix (2026-07-14)

New **LT - Apollo Phone Enrichment Polling** (JH8ShfpglWmLMZ3l) replaces the webhook-based intake:

1. **Sync profile match**: Calls Apollo `/v1/people/match`, writes name/email/company/LinkedIn/title/dept/revenue to GHL immediately
2. **Async phone request**: Calls Apollo with `webhook_url` pointing to existing V4 callback handler
3. **V4 callback** receives phone data and updates GHL

State as of activation (first hour): 60 contacts enriched, 30/run at 30-min cadence.

### 2026-07-15 Full Audit (7 workflows)

Full review found 2 CRITICAL bugs (`queued_phone` invisible to reaper, Intake Poller re-trigger), 2 HIGH issues (HTTP wrapper, V3 no error handling), and several medium/low cleanups. **10 fixes applied across 6 workflows**:

| # | Severity | Fix |
|---|----------|-----|
| 1 | CRITICAL | Reaper now monitors both `queued` + `queued_phone`; polling writes `Queued At` date |
| 2 | CRITICAL | Intake Poller routes `queued_phone` to `waiting` (was defaulting to `enrich`) |
| 3 | CRITICAL | Sheet First SQL injection fixed — parameterized query replacing template literal |
| 4 | HIGH | `doHttpRequest` wrapper removed from all 4 active workflows (V4, V3, Intake Poller, Sheet First) |
| 5 | HIGH | V3 callback: added error handling catch block with `callback_failed`, then **unpublished** V3 |
| 6 | MEDIUM | Polling `ghl()` now returns status codes; 429 triggers 5s retry on all 3 search sources |
| 7 | MEDIUM | V4 `Apollo Contact Id` now always set (was phone-gated) |
| 8 | LOW | Reaper Config node corruption cleaned (nested `parameters.parameters` removed) |
| 9 | LOW | Intake Poller `removeTag()` — removed `$httpRequest` fallback, now direct `this.helpers.httpRequest` |
| 10 | N/A | `$httpRequest` reference eliminated from all Apollo workflows |

### Pipeline Status (end-to-end)

| Step | Workflow | Handles |
|------|----------|---------|
| Discovery | Intake Poller (bYk1) | Tags contacts, sets `Enrich Phone via Apollo = Yes` |
| Sync match | Polling (JH8Sh) | Apollo `/v1/people/match` → writes profile, sets `queued_phone` + date |
| Async phone | Polling (JH8Sh) | Apollo with webhook → V4 callback |
| Phone callback | V4 Callback (U7c6) | Writes phone to GHL + `enriched` status |
| Re-enqueue | Intake Poller (bYk1) | Finds `enriched` contacts → inserts to voice_call_queue |
| Timeout | Reaper (RL5Zy) | Hourly scan for `queued` + `queued_phone` → `callback_timeout` after 24h |

### Workflow Summary

| Workflow | ID | Status | Purpose |
|----------|-----|--------|---------|
| LT - Apollo Phone Enrichment Polling | JH8ShfpglWmLMZ3l | Active, every 30 min | Polls GHL, calls Apollo sync+async, writes profile + triggers phone callback |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active, webhook | Receives Apollo async phone callbacks, writes phone to GHL |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** | Legacy V3, fully superseded by V4 |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active, webhook | 0 executions — superseded by polling, SQL injection fixed |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** | Legacy path. 1,008 orphaned webhook executions canceled on 2026-07-16; not part of production enrichment |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active, hourly | Flips stale `queued` + `queued_phone` to `callback_timeout` |

### 2026-07-16 Production Hardening

- Verified live production workflows are active and published:
  - Polling `JH8ShfpglWmLMZ3l`
  - Callback V4 `U7c6byTLXAMgcS75`
  - Reaper `RL5ZyUoshSPbmVA1`
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed past the `Webhook` node.
- Polling workflow fix: orphan status rediscovery now includes both `queued` and `queued_phone`.
- Callback V4 fix: Apollo provider-level callback failures now map to `callback_failed` rather than silently landing as `no_match`.
- Polling write-path fix: hardened GHL `PUT /contacts/{id}` fallback after reproducing live API behavior.
  Working update shape is `customFields` without `locationId`; payloads containing `locationId` or `customField` can return `422`.
- Polling now has a minimal fallback write so contacts are not left blank when the full Apollo profile write fails.
- Backfilled 6 previously blank contacts into `queued_phone` on 2026-07-16:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

## SMS Campaign — SimpleTexting via GHL (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

### Live n8n Workflow State

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Receives GHL outbound messages at `/webhook/lt-simpletexting-provider-outbound`, validates provider ID, normalizes phone to E.164, sends via idempotent boundary → SimpleTexting API. Skips business-hours guard for human replies. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Slack alert preserved. Now also posts inbound messages to GHL Conversations under `SimpleTexting SMS` via `type: "Custom"` + `conversationProviderId`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Mirrors successful outbound campaign sends into GHL Conversations under `SimpleTexting SMS`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated SMS boundary. Called by outbound router and campaign send paths. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Active | `sms_drip`, 10/run, weekdays 10:15am + 3:00pm ET, `defaultDryRun=false`. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Active | 6-step flow, 2-day inter-step delay. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | No changes needed. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | No changes needed. |

### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

## Reporting

### Active Workflows

| Workflow | ID |
|----------|-----|
| LT - GHL Daily Leads Ingest | osIJOgBmWITF5Yuv |
| LT - GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 |
| LT - GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l |
| LT - GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG |
| LT - GHL Daily Social Ingest | QZoqCaTwDhbym80O |
| LT - GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq |
| LT - GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi |
| LT - GSC Daily Ingest | xHqmCC1vOeZ11gCd |
| LT - GSC Rollup Bridge | fOVBHwti9rC3qrLV |
| LT - Report Attribution Bridge | Y0TU7Il71JswxOBp |
| LT - Report Daily Rollups | EUeOiRttoVLQ9zF9 |
| LT - Report Executive Summary API | Bukc0mgOD2r7V6ED |
| LT - Report QA and Alerts | M5mXcDTFSko6EdHb |
| LT - Report Config Sync | aomO3Z4AXJIgEvvN |
| LT - Report Publish Refresh | 3gXztCnBEN6sGINb |
| LT - Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 |
| LT - Report Pipeline Velocity | iFfwh0jpYUZoDhDR |
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV |

### State

GA4, GHL, and GSC ingestion are all live. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools — verify dedup (Fix #3) prevents double-enqueue
- Monitor Outbound Dialer when it activates at 14:00 UTC today — verify atomic lock (Fix #1) prevents duplicate calls
- Watch for GHL rate limiting on downstream nodes (Trigger Apollo Enrichment, Remove Tag nodes) — continueOnFail (Fix #4) prevents workflow crashes from flaky deletions
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback
- Run adversarial test calls against both campaign assistants
- Monitor timer system for duplicate warning/end-call events — 60s dedup window (Fix #5) should prevent this

### 3. Emerald Email Campaign Ramp

Monitor first week of dispatcher runs. Verify Email_Events data quality. Increase warmup caps as sender reputation builds. Currently ~250/hr, ~1,200/day capacity with 4 senders.

### 4. Reporting Depth

- Expand contact-capture panel by channel and landing page
- Build matched funnel views by channel, campaign, and landing page

### 5. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics

### 6. DAN Email Campaign Ramp

- Monitor dispatcher runs at 65/cycle every 30 min — verify consistent deliverability (5 fixes applied 2026-07-15)
- Track Email_Events for DAN campaign data quality (opens, clicks, bounces)
- Monitor DAN_Release_Log growth — ~1,200/day target should exhaust eligible pool in ~4 days
- Recurring DNC contacts (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms) are not written to release log but reappear each run — address stale tags in report_raw_ghl_contacts to reduce waste
- Verify sender rotation (4 senders) doesn't trigger GHL domain limits

### 7. Apollo Enrichment — MONITORING (audited + hardened 2026-07-15)

- ~~Watch polling workflow runs to confirm steady 30/cycle consumption~~ — Confirmed: batch size 50, steady 30-min runs, all successful
- ~~Verify V4 callback handler starts receiving Apollo async phone responses~~ — Confirmed: 1,058+ callbacks received by 2026-07-16, working
- ~~Confirm `queued_phone` contacts transition to `enriched` as callbacks arrive~~ — Pipeline confirmed end-to-end. Reaper now monitors both statuses.
- ~~Retune maxPerRun and schedule if Apollo rate limits appear~~ — 429 retry with 5s delay added to all 3 search sources
- ~~Ensure legacy blank contacts are not left invisible after poller write failures~~ — Fixed 2026-07-16 with hardened poller fallback + 6-contact backfill to `queued_phone`
- **ACTIVE MONITORING**: Watch Reaper Slack reports for `queued_phone` reaping counts
- **ACTIVE MONITORING**: Confirm polling `Queued At` dates flow correctly so Reaper aging works
- **ACTIVE MONITORING**: Watch for Apollo API rate limits / Apollo credit exhaustion on async phone callback requests; V4 now maps provider failures to `callback_failed`

### 8. LinkedIn Dispatcher Monitoring

- Monitor first dispatcher runs to confirm Fetch Ready Queue picks up the 14,987 `ready` contacts
- Verify dispatcher sends invites (successTag: `linkedin_connection_requested`) and updates state table correctly
- Watch for GHL rate limiting on dispatcher's per-contact API calls (tag check + LinkedIn URL extraction)
- Confirm Acceptance Checker correctly processes new connections and applies `linkedin_connected` tag

### 9. Cleanup and Adjacent Automation

- ~~Build automated LinkedIn DM suppression workflow~~ — DONE 2026-07-15. GHL tag `stop_linkedin_dms` → webhook → state table terminal. Full audit confirms all 3 send paths blocked.
- Build the separate `SimpleTexting SMS` GHL Custom Conversation Provider bridge after the user provides `conversationProviderId`; keep the existing SimpleTexting dispatcher live at low volume.
- Confirm first real SimpleTexting inbound reply posts to the existing Slack alert and suppresses future automated sends; then add GHL Conversations posting as the primary operator inbox.
- Retry and enable blocked GSC ingest workflow
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state lag after the fail-closed patch
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- ~~Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder~~ (verified already removed 2026-07-15)
- Delete GHL export CSVs after DAN backfill confirmed healthy

## Working Order

1. **LinkedIn dispatcher** — monitor first runs now that 14,987 `ready` contacts are queued. Verify invites send, tags apply, state table updates.
2. **DAN ramp** — active dispatching (5 fixes applied 2026-07-15), monitor deliverability, track pool exhaustion (~4 days at 1,200/day)
3. **Vapi monitoring** — verify dialer fires, calls route to correct assistants
4. **Apollo enrichment** — monitor polling runs, verify V4 callback receiving phones
5. **Voice hardening** — secret management, webhook verification, adversarial testing
6. **Emerald ramp** — monitor dispatcher, verify data quality
7. Reporting depth
8. Meta attribution
9. SimpleTexting GHL Conversations provider bridge
10. Cleanup and adjacent automation
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

## Jason SMS

### `john_sms1`

```text
Hi, Jason from Transparent eCom, just gave you a call. Saw you were interested in learning about ads for regulated industries on social/search.

We run ads for Mood, Cookies, and more! Interested in learning how?
```

### `john_sms2`

```text
Hey {{first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

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
Hey {{contact.first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

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
Hey {{contact.first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

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
Hey {{contact.first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

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
Hey {{first_name}}! Jason from Transparent eCom here. Are you locked out of ads, or just avoiding them because of the horror stories?

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
- The Jason and Cameron message sets are the only ones that were edited for wording.
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

1. **Priority 1:** Finish the GHL Custom Conversation Provider bridge for LinkedIn/Instagram via Unipile. Current handoff: `docs/strategy/unipile-ghl-bidirectional-integration.md`.
2. **Priority 2:** Resolve GHL marketplace/custom-provider OAuth `401` on `/conversations/messages/inbound`, then verify inbound Instagram messages appear in GHL Conversations.
3. **Priority 3:** Build real outbound routing in `LT - Social Provider Outbound Router` so GHL replies send through the correct Unipile chat/account.
4. **Priority 4:** Upgrade LinkedIn inbound messages to also post into GHL Conversations, while preserving existing reply-state suppression.
5. **Priority 5:** Only after bidirectional inbox routing is stable, rebuild Instagram outbound/follower DM with the real Instagram Unipile account, account-type guard, and reply suppression.

Each automation can be implemented incrementally, starting with the webhook infrastructure already in place.

## Implementation Order

1. Complete inbound-to-GHL for Instagram and LinkedIn custom providers.
2. Complete GHL outbound-provider reply routing back to Unipile.
3. Keep LinkedIn automated outreach on the canonical dispatcher -> acceptance/state sync -> 4-message DM sequence path.
4. Rebuild Instagram outbound only after inbox routing and reply suppression are verified.
5. Extract shared template/copy utilities only after both channels have stable, separate state models.
````

## File: unipile-ghl-bidirectional-integration.md
````markdown
# LinkedIn and Instagram via Unipile -> GHL Bidirectional Integration

Updated: 2026-07-16 (Session 6: Instagram dedup verified; Instagram and LinkedIn inbound/outbound paths working through canonical SMS custom providers)

Next-session handoff for the bidirectional GHL Custom Conversation Provider integration using Unipile for LinkedIn and Instagram.

## Goal

Make GHL Conversations the operator-facing inbox for LinkedIn and Instagram conversations while Unipile remains the transport layer.

1. Inbound LinkedIn/Instagram message arrives in Unipile.
2. n8n receives the Unipile webhook, resolves or creates the matching GHL contact, and adds the message into GHL Conversations under the correct custom provider tab.
3. GHL user replies from the LinkedIn via Unipile or Instagram via Unipile custom provider tab.
4. GHL posts the outbound provider webhook to n8n.
5. n8n resolves the mapped Unipile chat/profile and sends the reply through the correct Unipile account.
6. Reply/inbound state feeds back into the outbound automation guardrails so automated DMs stop.

## What's Working

### Instagram Inbound Bridge (WORKING)

Messages flow end-to-end from Unipile webhook -> GHL contact create/update -> GHL Conversation under "Instagram via Unipile" tab.

**Key innovation**: The stored OAuth token is agency-scoped and can't access conversation providers. The fix: each inbound call first converts the agency token to a location token via `POST /oauth/locationToken`, then uses that for the inbound message API. This avoids needing a location-scoped token at install time.

**Flow**:
- Webhook `/webhook/lt-unipile-instagram-new-messages`
- Normalize Instagram Message (Code) -> parses Unipile payload
- Lookup Mapping and OAuth Token (Postgres) -> finds/creates `instagram_conversation_map`, reads active OAuth token
- Create Contact and Add Inbound Message (Code) -> conservatively resolves an existing GHL contact, calls `/oauth/locationToken` to convert agency->location token, posts inbound with `type: "Custom"`
- Upsert Instagram Mapping (Postgres) -> persists chat mapping

**Inbound message type**: `type: "Custom"` works. `type: "SMS"` returns `CONVERSATIONS_MSG_CONVERSATION_PROVIDER_MISMATCH` for our SMS-type custom providers.

**Dedup / merge status 2026-07-16:** Initial Instagram replay reused pre-merge contact `sZjiGh8zJbG2DFhDCFBD`; that contact was later merged into canonical GHL contact `XZ4yChllGBdcsVxhFRDe`. After a stale-map replay created temporary duplicate `4V2oTmM7lWya3Nmtmp1Y`, map row `1` was repaired to `XZ4yChllGBdcsVxhFRDe` and the duplicate was deleted. Avoid artificial inbound replays unless needed because they create visible conversation messages.

**Location token API**: `POST https://services.leadconnectorhq.com/oauth/locationToken` with `companyId: "7vMmm4at5OrjQplRN3EO"` and `locationId: "Zwz4relUXVPxx8uohnjV"`.

### LinkedIn Inbound Bridge (WORKING)

Same architecture as Instagram but with `linkedin_conversation_map` table and canonical provider `6a58a14ff3023bea3783c152`. Contact create/update + map + inbound posting + existing DM suppression preservation are active.

**Verified 2026-07-16:** LinkedIn replay for chat `60Ult1SrWhOuvuZp1u7nXw` posted to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`, message `XubHwhlqdFAMQnZ4DAsm`. GHL conversation search showed `lastMessageType = TYPE_CUSTOM_PROVIDER_SMS`, `lastMessageDirection = inbound`, and `lastMessageConversationProviderId = 6a58a14ff3023bea3783c152`.

**Live webhook verification:** A real LinkedIn message, `Sending another test message`, arrived from Unipile as an `application/x-www-form-urlencoded` object whose single key contained the JSON payload. `Normalize Unipile Message Event` now parses that shape. Replay posted the message to GHL conversation `Ze8o3KbsrwuAXQ3KK5ge` as `TYPE_CUSTOM_PROVIDER_SMS` with provider `6a58a14ff3023bea3783c152`.

**Fixes applied:** `Upsert LinkedIn Map` now creates missing columns, avoids `ON CONFLICT` because the live table has no unique constraint, accepts blank LinkedIn profile URLs, and maps chat `60Ult1SrWhOuvuZp1u7nXw` to the real GHL contact. Lookup now prefers real `linkedin_connection_state` contacts over provisional map rows, and the final state lookup prefers real GHL contact IDs over synthetic `linkedin:follower:*` rows.

### Outbound Router (WORKING for direct webhook tests)

POST path of `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`):
- Lookup Outbound Chat ID (Postgres) -> queries `instagram_conversation_map` and `linkedin_conversation_map`
- Route Outbound to Unipile (Code) -> maps conversationProviderId to Unipile account, sends via `POST /chats/{id}/messages`

**Fixed 2026-07-16 Session 3:**
- POST webhook now uses `responseMode: responseNode`; prior `onReceived` + connected Respond node caused `Unused Respond to Webhook node found in the workflow` and immediate 40ms failures.
- Lookup node now creates missing map tables defensively before selecting. The missing `linkedin_conversation_map` table was crashing Instagram-only lookups.
- Lookup node preserves `message_text`/`alt_id` for the Code node; the previous query discarded the original webhook body before routing.
- Code node no longer uses `process.env` (task-runner sandbox returned `process is not defined`) and uses the working Unipile base URL `https://api42.unipile.com:17256/api/v1`.
- Direct smoke test to `/webhook/lt-social-provider-outbound` for canonical contact `XZ4yChllGBdcsVxhFRDe` routed successfully to Instagram with Unipile message id `vjdEYSk9XD6R0I46oPWLwA`.
- Direct smoke test through the canonical Instagram SMS custom provider `6a58a1193cdfc36997580a68` routed successfully with Unipile message id `sQJlo6mxUUO2dEMWzdi1OA`.
- Live GHL UI reply from the Instagram provider tab routed through n8n to Unipile successfully with Unipile message id `iEJO1vnvWVGwbk7ril1__A`.

### Contact Data Rule

Do not add dummy phone or email data for LinkedIn/Instagram provider routing. The working inbound payload uses `type: "Custom"` with `conversationProviderId` and `altId`, so provider routing does not require contact phone/email shims.

## What's Blocked

### Canonical SMS Custom Providers (Fixed 2026-07-16)

Email-type providers were deleted because they forced GHL to render LinkedIn/Instagram replies as email compose boxes with From/To/Subject fields. The working setup is **SMS-type additional custom conversation providers** paired with inbound message `type: "Custom"`.

Canonical provider IDs:
1. `Instagram via Unipile` -> `6a58a1193cdfc36997580a68`
2. `LinkedIn via Unipile` -> `6a58a14ff3023bea3783c152`

Provider setup requirements:
1. Type: `SMS`
2. Check `Is this a Custom Conversation Provider`
3. Check `Always show this Conversation Provider`
4. Do not select these providers under `Settings > Phone Numbers > Advanced Settings > SMS Provider`
5. Delivery URL: `https://automations.livetransparent.com/webhook/lt-social-provider-outbound`

Inbound message API payload must use `type: "Custom"` with `conversationProviderId` and `altId`. Do not use `type: "SMS"` for these providers; GHL returned `CONVERSATIONS_MSG_CONVERSATION_PROVIDER_MISMATCH`. Do not include `emailTo`, `emailFrom`, `subject`, or any dummy phone/email fields.

Verified 2026-07-16:
- Instagram inbound replay succeeded with provider `6a58a1193cdfc36997580a68` and returned message `er8mbcB9Lj8ao6Y0H2nJ` in conversation `yPLDgs90sEU5dbedA1gW`.
- GHL conversation search showed `lastMessageType = TYPE_CUSTOM_PROVIDER_SMS`, `lastMessageBody = Patched Instagram custom-provider inbound test`, and `lastMessageConversationProviderId = 6a58a1193cdfc36997580a68`.
- Canonical merged contact `XZ4yChllGBdcsVxhFRDe` retained real email/phone plus Instagram and LinkedIn routing fields; no dummy provider phone/email shims were added.
- Direct outbound router smoke test through new Instagram provider routed to Unipile message `sQJlo6mxUUO2dEMWzdi1OA`.
- LinkedIn inbound replay succeeded with provider `6a58a14ff3023bea3783c152`, canonical contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`, and GHL message `XubHwhlqdFAMQnZ4DAsm`.

### Outbound Router Webhook (FIXED 2026-07-16 Session 3)

The POST webhook at `/webhook/lt-social-provider-outbound` was erroring immediately (40ms execution). Root cause found in n8n container logs:

```text
Unused Respond to Webhook node found in the workflow
Error in handling webhook request POST /webhook/lt-social-provider-outbound: Unused Respond to Webhook node found in the workflow
```

Fixes applied:
- Removed `rawBody: true` (conflicting with `responseMode: responseNode`)
- Changed GET webhook to different path to avoid sharing `/webhook/lt-social-provider-outbound`
- Set Postgres credential on Lookup Outbound Chat ID node
- Final clean PUT via REST API with full JSON
- Changed POST webhook from `responseMode: onReceived` to `responseMode: responseNode`
- Added defensive table creation for `instagram_conversation_map` and `linkedin_conversation_map`
- Preserved outbound payload fields through the lookup
- Removed sandbox-blocked `process.env` access in Route Outbound to Unipile

Current direct test result with the canonical Instagram SMS custom provider:

```json
{
  "ok": true,
  "accepted": true,
  "service": "lt-social-provider-outbound",
  "routing": {
    "routed": true,
    "provider_id": "6a58a1193cdfc36997580a68",
    "contact_id": "XZ4yChllGBdcsVxhFRDe",
    "provider_type": "INSTAGRAM",
    "provider_name": "Instagram via Unipile",
    "chat_id": "yx-R-9J6XdWaFpGOQd1JFA",
    "unipile_message_id": "vjdEYSk9XD6R0I46oPWLwA"
  }
}
```

A quick diagnostic: test the POST path directly with curl and check n8n container logs:
```bash
curl -X POST https://automations.livetransparent.com/webhook/lt-social-provider-outbound \
  -H "Content-Type: application/json" \
  -d '{"conversationProviderId":"6a58a1193cdfc36997580a68","contactId":"XZ4yChllGBdcsVxhFRDe","message":"test","type":"Custom","altId":"yx-R-9J6XdWaFpGOQd1JFA"}'
```

## GHL Setup Reference

### Marketplace App

| Field | Value |
|-------|-------|
| App ID | `6a57dec68099a1e7cf68a266` |
| Client ID | `6a57dec68099a1e7cf68a266-mrmh8fl9` |
| Client Secret | `56f564ab-9eed-4797-9d4e-0df367e1acd4` |
| App Name | Transparent eCom Social Inbox |
| Developer | Transparent eCom |
| Target User | Sub-account |
| Who can install | Agency + Sub-Account |
| App Type | Private |

### Scopes (all correct)
`contacts.readonly`, `contacts.write`, `conversations.readonly`, `conversations.write`, `conversations/message.readonly`, `conversations/message.write`

### Conversation Providers

| Provider | Type | Alias | ID |
|----------|------|-------|-----|
| LinkedIn via Unipile | SMS custom provider | LinkedIn via Unipile | `6a58a14ff3023bea3783c152` |
| Instagram via Unipile | SMS custom provider | Instagram via Unipile | `6a58a1193cdfc36997580a68` |

Deleted Email provider IDs, do not use:
- LinkedIn via Unipile Email: `6a5892b9107668309b3f85ac`
- Instagram via Unipile Email: `6a5893d11e9368345005f66e`

Legacy SMS provider IDs retained only for transition/reference:
- LinkedIn via Unipile SMS: `6a5853a51e93687696053bf8`
- Instagram via Unipile SMS: `6a5853d33cdfc31a8c572766`

### Delivery URL (for both providers)
```
https://automations.livetransparent.com/webhook/lt-social-provider-outbound
```

### GHL Locations

| Field | Value |
|-------|-------|
| Location ID | `Zwz4relUXVPxx8uohnjV` |
| Location Name | Live Transparent |
| Company ID | `7vMmm4at5OrjQplRN3EO` |

### Unipile Accounts

| Platform | Account Name | Account ID |
|----------|--------------|------------|
| LinkedIn | Cameron Karkut | `V9eiHiDpRmCtan0YNdzsQw` |
| Instagram | Transparent eCom | `F2UprZ8aQc6Qm9CYYWU6cg` |

### OAuth Install URL (full scopes)
```
https://marketplace.gohighlevel.com/v2/oauth/chooselocation?response_type=code&redirect_uri=https%3A%2F%2Fautomations.livetransparent.com%2Fwebhook%2Flt-social-provider-outbound&client_id=6a57dec68099a1e7cf68a266-mrmh8fl9&scope=contacts.readonly+contacts.write+conversations.readonly+conversations.write+conversations%2Fmessage.readonly+conversations%2Fmessage.write&version_id=6a57dec68099a1e7cf68a266
```

Note: marketplace.gohighlevel.com has session issues. Use app.gohighlevel.com integration pages to uninstall/reinstall instead.

## n8n Workflows

### Active / Published

| Workflow | ID | Status |
|----------|----|--------|
| LT - Social Provider Outbound Router | `kqIi8i1RjFAZKrK3` | Active (outbound working for direct tests and Instagram GHL UI reply) |
| LT - Instagram Unipile New Messages | `pISlgYUsyJIrLuJd` | Active (inbound working; dedup verified) |
| LT - LinkedIn Unipile New Messages | `7o5EBdvwAuIaWW7k` | Active (inbound working) |
| LT - GHL OAuth Callback | `UnSWPnVoUy3tNJkX` | Active |

### Stopped

| Workflow | ID | Status |
|----------|----|--------|
| LT - Instagram DM Sequence (Unipile) | `iCnY6ccdHhfJg3sf` | Unpublished |
| LT - LinkedIn Follower DM Sequence (Unipile) | `pq7XVajNFnnwMUTr` | Unpublished |

## Data Tables

### `instagram_conversation_map`
Created by `pISlgYUsyJIrLuJd`. Maps `ghl_contact_id` <-> `instagram_chat_id` (UNIQUE).

### `linkedin_conversation_map`
Created by `7o5EBdvwAuIaWW7k`. Maps `ghl_contact_id` <-> `linkedin_chat_id` (UNIQUE).

### `ghl_oauth_tokens`
Stores OAuth tokens from marketplace app installs. Queried by inbound workflows with `WHERE active IS TRUE`.

### `ghl_oauth_install_events`
Logs OAuth install events (codes, exchanges).

## Known Test Identity (Instagram)

| Field | Value |
|-------|-------|
| Contact name | Edmundo Cadorniga |
| GHL Contact ID | `XZ4yChllGBdcsVxhFRDe` |
| Instagram username | `edmundocadorniga` |
| Chat ID | `yx-R-9J6XdWaFpGOQd1JFA` |
| Profile provider ID | `6361495593` |
| Messaging provider ID | `109928757071246` |
| Map row ID | `1` |
| Email | `ed@livetransparent.com` |
| Phone | `+63471666523` |

### 2026-07-16 Merge Cleanup

- Historical GHL duplicates for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; GHL search now returns one matching contact.
- Temporary verification duplicate `4V2oTmM7lWya3Nmtmp1Y` was deleted after map repair.
- Temporary workflow `LT - Temp Social Map Maintenance 2026-07-16` (`nuuB3qCKxr7J6iPw`) repointed `instagram_conversation_map.id = 1` and `linkedin_conversation_map.id = 2` to `XZ4yChllGBdcsVxhFRDe`, then was archived.
- Post-repair outbound router verification succeeded for Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` (`C7I9944kWsSKutX2XhZEpA`).

### Test Payload
```json
{"account_id":"F2UprZ8aQc6Qm9CYYWU6cg","account_type":"INSTAGRAM","id":"yx-R-9J6XdWaFpGOQd1JFA","chat_id":"yx-R-9J6XdWaFpGOQd1JFA","lastMessage":{"id":"test-msg","chat_id":"yx-R-9J6XdWaFpGOQd1JFA","text":"test message","is_sender":0,"sender_id":"109928757071246","timestamp":"2026-07-17T00:00:00.000Z","account_id":"F2UprZ8aQc6Qm9CYYWU6cg"},"profile":{"provider_id":"6361495593","public_identifier":"edmundocadorniga","full_name":"Edmundo Cadorniga"}}
```

## Operator Inbox and Monitoring Runbook

### Current Operator Inbox

GHL Conversations is the canonical operator-facing inbox for LinkedIn and Instagram messages. Inbound Unipile messages are written into GHL as custom-provider messages, and GHL replies are routed back through `LT - Social Provider Outbound Router` to Unipile.

Operators should monitor GHL Conversations at the conversation level, not by opening each contact record manually. Use the provider tabs named `LinkedIn via Unipile` and `Instagram via Unipile` when replying so outbound messages route through the correct custom conversation provider.

### Response Rules

- Reply from the correct GHL custom provider tab: `LinkedIn via Unipile` for LinkedIn, `Instagram via Unipile` for Instagram.
- Do not reply through normal SMS, email, or manually typed phone/email fields for social messages.
- Do not add dummy phone or email values to make social replies work; routing depends on `conversationProviderId` and `altId`.
- If a person replies on LinkedIn, confirm the automated LinkedIn sequence is suppressed by `dm_conversation_status = active` or the `linkedin_dm_sequence_completed` tag/state.
- If a contact asks to stop LinkedIn DMs, use the suppression runbook in `AGENTS.md` or add the GHL tag `stop_linkedin_dms`.

### Macro-Level Visibility

The system currently supports macro review through GHL Conversations, but there is no dedicated social inbox dashboard or alert digest documented as live. Any macro alerting or dashboard should be treated as a new enhancement unless a live workflow is added and verified.

Recommended macro views:

- GHL Conversations filtered to recent inbound messages from `LinkedIn via Unipile` and `Instagram via Unipile`.
- GHL Conversations filtered to unread or unreplied conversations when available in the GHL UI.
- A future n8n digest that lists new inbound LinkedIn/Instagram messages across all contacts.
- A future dashboard backed by GHL Conversations plus `instagram_conversation_map` and `linkedin_conversation_map`.

### Recommended Alert Workflow

Not currently documented as live. If alerting is needed, build a workflow or extend the inbound bridges after the GHL message write succeeds.

Recommended flow:

```text
Unipile inbound webhook
-> Normalize platform/message/contact
-> Post inbound message to GHL Conversations
-> Upsert social conversation map
-> Send Slack/email alert or write digest row
```

Recommended alert fields:

- Platform: LinkedIn or Instagram
- Sender name and profile identifier
- Message text
- GHL contact ID and contact link
- GHL conversation ID when available
- Unipile chat ID / `altId`
- Automation suppression status
- Workflow execution ID

Recommended alert cadence:

- Real-time alert for every inbound message until operator confidence is high.
- Hourly digest for unread or unreplied social conversations.
- Daily QA summary showing inbound count, outbound reply count, routing failures, and unmapped chats.

### Health Checks

Run these checks after any workflow/provider change and at least weekly while the bridge is in active use.

- Confirm `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active and published.
- Confirm `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active and published.
- Confirm `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active and published.
- Confirm `LT - GHL OAuth Callback` (`UnSWPnVoUy3tNJkX`) is active.
- Confirm GHL provider IDs are still canonical: Instagram `6a58a1193cdfc36997580a68`, LinkedIn `6a58a14ff3023bea3783c152`.
- Confirm the provider delivery URL for both providers is `https://automations.livetransparent.com/webhook/lt-social-provider-outbound`.
- Confirm Unipile Instagram webhook points to `/webhook/lt-unipile-instagram-new-messages`.
- Confirm Unipile LinkedIn webhook points to `/webhook/lt-unipile-linkedin-new-messages`.
- Confirm `ghl_oauth_tokens` has an active token row for the Live Transparent location.
- Confirm `instagram_conversation_map` and `linkedin_conversation_map` contain rows for active social chats.

### Troubleshooting

If an inbound social message does not appear in GHL:

- Check the relevant inbound workflow execution first.
- Confirm the Unipile webhook is firing and the account ID matches the expected platform account.
- Check OAuth conversion to a location token via `POST /oauth/locationToken`.
- Check that the inbound GHL message payload uses `type: "Custom"`, `conversationProviderId`, and `altId`.
- Check for duplicate or stale map rows pointing to a merged/deleted GHL contact.

If a GHL reply does not send through Unipile:

- Check `LT - Social Provider Outbound Router` executions.
- Confirm the webhook body includes `conversationProviderId`, `contactId`, `message`, and `altId`.
- Confirm the matching row exists in `instagram_conversation_map` or `linkedin_conversation_map`.
- Confirm the router uses the working Unipile base URL `https://api42.unipile.com:17256/api/v1`.
- Confirm the reply was sent from the correct provider tab, not normal SMS/email.

If automated LinkedIn DMs continue after a reply:

- Check `linkedin_connection_state.payload_json.dm_conversation_status` for `active`.
- Check whether `linkedin_dm_sequence_completed` is present on the GHL contact when the conversation should be terminal.
- Run the LinkedIn DM suppression path from `AGENTS.md` if the contact needs to be manually suppressed.

### Open Gaps

- No dedicated macro social inbox dashboard exists in this repo.
- No live Slack/email alert workflow is documented for every LinkedIn/Instagram inbound message.
- No SLA/owner assignment rule is documented for social replies.
- No automated stale-unreplied social conversation report is documented.
- No daily reconciliation job is documented to compare Unipile chats against GHL conversations.

## Next Steps (Priority Order)

1. **Monitor post-merge social inbound**: Map rows now point to canonical contact `XZ4yChllGBdcsVxhFRDe`. Watch the next real Instagram inbound to confirm it lands on the canonical contact without creating a new duplicate.

2. **Optional LinkedIn UI outbound test**: LinkedIn inbound and direct outbound router checks are verified; run a controlled GHL UI reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge` if operator-side confirmation is needed.

3. **Register/confirm Unipile Instagram webhook**: Ensure the production Instagram Unipile webhook points to `/webhook/lt-unipile-instagram-new-messages`.

4. **Add macro alerting/digest**: Build and verify a lightweight n8n notification path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.

5. **Rebuild Instagram outbound DM**: Only after the bidirectional inbox remains stable, with Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, account-type guard, reply suppression, and safe cadence.

6. Do NOT republish Instagram DM Sequence or LinkedIn Follower DM Sequence unless explicitly requested.

## Guardrails (Preserved)

- LinkedIn automated sends fail closed if reply lookup errors
- DM suppression blocks all 3 send paths (DM Sequence, Follower DM, Dispatcher)
- `dm_conversation_status = active` set after LinkedIn inbound bridge
- Contact creation conservative (matched by provider IDs, not name)
- `altId` preserved as Unipile chat ID for outbound reply routing
- Live n8n state is source of truth over repo files
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
