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
- n8n target version: `2.33.3` (native Schedule Trigger is the scheduling standard; do not add OS/Coolify cron jobs for workflows).
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

### Reporting Execution Contract (2026-07-31)

- The spreadsheet at `1AbLdIhQiEoJhdx3l6yeAppNxbYbAIYhcZfoKhy68VZw` is the requirements reference for the MQL, email, LinkedIn, and social report layout.
- Native GHL Custom Report: `6a67dce4a51a4360c60963a3`. Use it for CRM contacts/opportunities, MQL detail, pipeline, email, SMS, calls, appointments, and custom-metric rates.
- Native GHL Social Planner is the source for Facebook, Instagram, and LinkedIn Page post analytics. LinkedIn personal-profile analytics are not supported by the platform API.
- Keep Brands-versus-Dispensaries joins, Unipile LinkedIn DM state, Vapi campaign state, trigger-link detail, and cross-channel comparison in the Executive Report unless the underlying data is intentionally synchronized into GHL objects.
- The Executive Report accepts `range=7d|30d|90d|custom` plus `from=YYYY-MM-DD` and `to=YYYY-MM-DD`. For every selected period it loads the immediately preceding equal-length period and shows current value, prior value, absolute change, and percentage change.
- Reporting weeks use the report API's returned date window and the sub-account reporting timezone. Do not mix widget-level date overrides with the shared selected-period comparison unless the metric definition explicitly requires it.
- Campaign summary workflow: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) is active and published. Its selected-window endpoint is `/webhook/lt-report-campaign-channel-summary`.
- Campaign summary active version `14432194-7f20-47a9-8bcd-6b8ea9f05529` returns named channel/campaign rows plus `linkedin_invites`/`linkedin_accepted` columns. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list` with `campaign_type`/`source_key = 'partnership'` routing, and Vapi uses queue campaign IDs. Catalog rows for `General outbound`, `Partnership emails`, `xyz`, and `abc` remain zero until matching source events exist; `Partnership LinkedIn` is populated from durable `connection_request_sent` ledger events (10 for the verified 2026-07-31 execution `281366`).
- The Executive Report is live at `https://reports.livetransparent.com` as build `2026-08-01-v12-campaign-breakdown`; it includes campaign/channel filters, the campaign table, LinkedIn columns, selected-period controls, prior-period comparison, and social likes/comments/shares/saves/reach/impressions fields when the source supplies them.
- The Executive Report also includes a bottom `Outgoing Call Detail` table. It calls `/api/report/executive/outgoing-calls`, which nginx proxies to `GET /webhook/lt-report-outgoing-calls` from active workflow `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`). The endpoint is fixed to the seven most recent completed `America/Los_Angeles` days, paginates at 100 rows, and reads `voice_call_attempt` joined to `voice_call_queue`.
- The root `GHL_PIT` was directly verified against the official REST location and contacts endpoints on 2026-07-31; both returned HTTP 200 with the required Bearer/Version headers. The native GHL report `6a67dce4a51a4360c60963a3` was also verified in an authenticated GHL UI session: it loads 11 widgets and supports editing. Its `Campaign Opportunities` widget is now filtered to `Partnership Pipeline`, and its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`. The current report date window was 2026-07-19 through 2026-07-25; the widgets showed zero/no data for that window after filtering.
- The official GHL API/SDK does not expose Custom Report widget-layout mutation. Do not guess undocumented report-builder endpoints; native widget changes require authenticated GHL UI access or an explicitly approved internal API path.
- Never commit GHL PITs, Firebase signed URLs, OAuth tokens, or captured response artifacts containing credentials. Use environment placeholders in documentation and leave sensitive captures untracked.

### Ingest and LinkedIn Hardening (2026-07-31)

- `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`. Empty responses finalize as `empty`; malformed data is `partial`; fetch failures finalize run/health state, do not advance the watermark, and then fail the execution. Verification: success `276731`, pinned failure `276747`.
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`. Snapshot/history rows use ingest date, raw rows preserve source timestamps, retries/cursor guards are bounded, finalization errors fail closed, and sales health uses `ghl_opportunities` while raw compatibility remains `source_system = 'ghl'`. Verification: execution `276626` processed 7,683 opportunities and 7,683 history rows.
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) is published on `fa1a5dfe-d00c-47b3-98d3-862ea6f912a7`. It uses direct `this.helpers.httpRequest`, bounded contact/API budgets, retry/timeouts, explicit error reporting, and terminal/reply-state preservation.
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is published on `bd385c89-0678-4301-84e6-abc63fea3c28`. It reads Config explicitly, atomically claims `ready` rows as `requested_pending`, and performs live suppression/reply checks before invites. Do not manually execute it without explicit approval because it can send LinkedIn invites.
- `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on `d9168bbc-9c96-44fd-a356-12e645a2ec3d`; its webhook requires the protected `X-LT-LinkedIn-State-Secret` header. All discovered callers, including the partnership dispatcher/DM path, were updated and published. Unauthorized requests return `403`; malformed authorized requests reach the workflow and fail validation without a state write.
- Community Edition variable convention: each relevant LinkedIn state-upsert workflow has exactly one `Config` node. Workflow-scoped values such as `stateUpsertSecret` live there and Code nodes read them from Config instead of embedding request literals. Config nodes are operational storage, not equivalent to managed credentials; keep access restricted and migrate to credentialed HTTP Request nodes when possible.

## Working Rules

- Check the live state before and after every mutation.
- Fetch first, patch second.
- After every mutation via `update_workflow`, verify the workflow is both **updated AND published**: compare `versionId` vs `activeVersionId` from `get_workflow_details`. If they differ, call `publish_workflow` to activate the draft. The `update_workflow` MCP tool does NOT auto-publish.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Website demo bookings must use the direct GHL Regulated Ads booking widget. Do not route website visitors through the legacy hero form or Calendly embed first.
- Use `Config` nodes only when env or credential access is blocked.
- LinkedIn outbound senders must fail closed on reply/inbound lookup errors. A failed reply check is a skip, not a send.
- For any "stop LinkedIn DMs" request, suppress the contact in both places: add `linkedin_dm_sequence_completed` in GHL and mark the shared `linkedin_connection_state` row terminal (`connection_status = completed`, `sequence_step >= 4`, `dm_sequence_status = completed`/`dm_conversation_status = active` as applicable). The GHL tag alone is not enough because the live LinkedIn send paths select from shared state.
- LinkedIn DM sequences must mark terminal contacts with `linkedin_dm_sequence_completed` and stop reselecting step-4 rows; the queue source is `LT - LinkedIn Connection State Sync (Unipile)` and the GHL connect dispatcher feeds 20 contacts at a time when healthy.

### Follow-up Sender Routing Handoff (2026-07-29)

- User requirement: follow-up email From Name and From Email must follow the opportunity/contact owner; if neither has an owner, default to Jason.
- Affected GHL workflow: `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`), published version 39. Triggers on opportunity stage entry into Sales Outreach: New (`3529dd3d`), Attempting Contact 1st Attempt (`b97e42b1`), 2nd Attempt (`c46c3be3`), 3rd Attempt (`c8b7a450`), Engaged (`9ced8010`).
- Six affected templates are in folder `Jason Follow Up Emails` (`69e0c9069af5986541802d88`) and currently have literal Jason sender defaults. Do not mistake those defaults for the final owner-routing implementation. One template (`69e0dcad8ffabf47b4d987c5`, "Cannabis Ads: Next Steps") is reused by 2 of the 7 email actions. Template signatures use `{{user.email_signature}}` (dynamic).
- The workflow also sends 14 SMS follow-ups via SimpleTexting webhook (`john_sms1` through `john_sms5`), which are not owner-routed.
- Current live artifact check: published version 39 has Jason workflow defaults (`Jason from Transparent eCom`, `jason@livetransparent.com`) confirmed via `senderAddress` in the API response. All 7 Send Email actions retain owner-driven sender fields: `{{opportunity.owner}} from Transparent eCom` and `{{user.email}}`. The three-layer defense is: (1) action-level merge fields resolve to owner, (2) template-level literal Jason values backstop if merge fields fail, (3) workflow-level `senderAddress` defaults backstop if both above fail.
- Remaining GHL work: none for sender routing. Do not send a live test email unless explicitly requested. **Marc routing path is untested in production** — as of 2026-07-30, zero Marc-owned (`sqGx5rp3oAUG610NXyjU`) opportunities exist in any of the 5 trigger stages; all Marc-owned opportunities are in the Qualified stage and have not yet entered a stage that fires this workflow.
- Public GHL APIs cannot write workflow action definitions. The template PATCH API rejects `{{user.email}}` as `fromEmail`; do not attempt to solve owner routing by putting merge fields into template sender metadata.
- Authenticated browser access was used to set and publish the workflow defaults. The published version 39 response confirms `senderAddress` and `status: published`.

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
- n8n Code nodes cannot access managed credentials by design. Do not attempt `$getCredentials()` or `this.getCredentials()` in Code nodes. Credential migration for direct API calls requires credentialed HTTP Request nodes, or an explicitly approved protected runtime-variable path.
- **Historical n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` returned fields that violated the MCP output schema. The deployment target is now n8n `2.33.3`; retain the REST workaround if the MCP schema issue recurs:
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
- **Auth header**: `Authorization: Bearer <GHL_PIT_FROM_ENV>` (PIT token from root `.env`). The `token:` header style does NOT work.
- **Required header**: `Version: 2021-07-28` on every request.
- **Accept/Content-Type**: Always include `Accept: application/json` and `Content-Type: application/json`.

### Email Template Operations

**Listing templates**: Use `ghl_official_emails_fetch-template` MCP tool (OAuth). Pass `query_parentId` for folder-scoped listing, `query_limit` (max 50), `query_offset`.

**Reading template content**: Each template has a `previewUrl` pointing to Firebase Storage. Use `webfetch` with `format: "html"`. No working GET endpoint exists.

**Updating a template** (PATCH):
```bash
curl.exe -s -X PATCH "https://services.leadconnectorhq.com/emails/builder/{templateId}" \
  -H "Authorization: Bearer $env:GHL_PIT" \
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
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Active |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Active |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | **Unpublished** (explicit helper only; not an automatic call-start path) |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Active |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active (hourly, no Slack reporting) |
| LT - Voice Campaign Brand (Alex) | 1d7c5d42-f0a4-4b58-9494-dbda3be3c657 | Active (optimized 2026-07-20) |
| LT - Voice Campaign Dispensary (Jordan) | 056f2e50-8bdf-4257-ac45-4d575600c39d | Active (optimized 2026-07-20) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` is production-active, not manual-only. It runs every 15 minutes and selects up to 10 Brand and 10 Dispensary candidates per execution.
- It reads `emerging_pool_contacts`, performs live GHL contact and suppression checks, and applies campaign tags only after DeepSeek acceptance or a prior qualified-domain match.
- Qualified domains are persisted in `vapi_qualified_domains`. Common free-email domains are excluded, and a domain is written only after a successful GHL tag-add response.
- DeepSeek uses a 600-token output budget with concise English reasoning. The SQL candidate filter accepts a live GHL phone fallback when the imported pool phone is blank.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes. The patch fixed model-output truncation, live-phone eligibility exclusion, and unsafe domain persistence on cleanup/failed writes.

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
- **Native scheduling**: the dialer uses n8n's Schedule Trigger at a two-minute interval. The workflow's timezone-aware business-hours guard remains the authority for whether a call may start; no external cron job is required.
- **Same-run queue advancement (2026-07-25)**: `LT - Voice Agent V1 Outbound Dialer (Vapi)` releases blocked, invalid, and outside-hours contacts and loops back to `Postgres - Fetch Next Queue Item` in the same execution. `Code - Continue Queue Loop` caps each execution at 25 queue checks. The old `End - No Phone` and `End - Outside Contact Hours` nodes are disconnected legacy nodes and are not required for the live path.
- **Dialer credential guard (2026-07-25)**: live GHL contact lookups began returning `401/403`; the dialer now fails closed after an infrastructure lookup failure instead of looping until its one-hour timeout. The `.env` GHL PIT was subsequently rotated, verified against GHL, propagated to active n8n workflows, and smoke-tested with execution `242609`.
- **Gap hardening (2026-07-25)**: silent human answers now produce `interest_unknown` rather than `vapi_qualified`; global dialer hours are 9am-5pm CT; unknown Vapi campaign tags fail closed; source-tag cleanup is dynamic; superseded Apollo Sheet First intake is unpublished; reporting config/publish schedules are connected and tested.
- **Dialer and ingest crash fixes (2026-07-30)**: Three bugs caused every dialer execution to crash. (1) GHL `Version` header `2023-02-21` rejected — corrected to `2021-07-28` on both `HTTP - Get GHL Contact` and `GHL - Create Call Note`. (2) `Code - Continue Queue Loop` read Postgres `RETURNING` columns (`skip_reason`, `loop_attempts`) that n8n's Postgres v2 node never surfaces — rewritten to read from `$('Code - Check Phone').item.json`. Infrastructure errors (`ghl_lookup_failed`, `eligibility_lookup_failed`) now fail closed with `return []`. (3) Empty queue fetches produced phantom `GET /contacts/` → 403 — added `Code - Queue Found Guard` before lookup. Queue reset: 1,051 contacts (1,047 failed + 4 cooling_down) restored to `status='pending'`. Call Outcome Ingest fix: removed `new Date().toISOString().slice(0,10)` from `queryReplacement` (invalid n8n expression). All three workflows published and verified end-to-end.

**Fixes applied 2026-07-16 (anti-spam):**
- **Campaign tag removal**: After enqueueing, the poller now removes the source campaign tag (e.g. `brands_pool`) instead of the hardcoded `vapi_queue` tag. This prevents contacts from being re-found in subsequent rotation cycles.
- **Blocklist expansion**: `Classify Contacts` now checks all 8 `BLOCKLIST_TAGS` via `hasAnyBlocklistTag()` (was only checking `vapi_voicemail` and `vapi_qualified`). Contacts with any terminal outcome tag have their campaign tag removed inline and are skipped.
- `removeTag()` helper now accepts a `tagsToRemove` array parameter for flexible tag removal.

### Voice Assistant Optimizations (2026-07-20)

Live call audit of 4 Vapi calls uncovered 7 issues across the outbound assistants. All fixes applied and published.

**Jordan (Dispensary, `056f2e50`) — 8 prompt fixes + 2 config fixes:**
- `firstMessage` template variables fixed: `{{contact_name}}` → `{{first_name}}` (n8n passes `first_name`, name was never resolving). Removed `{{market}}` (never passed, rendered as blank).
- "with Transparent eCom" → "from Transparent eCom" (Nico TTS inserted "a" → "with-a-transparent").
- Compliance disclosure removed from `firstMessage` — now system-prompt-only for live calls. Voicemail recipients no longer hear the AI/recording disclosure.
- Discovery questions restructured to ONE AT A TIME: numbered Q1-Q4 each with WAIT instructions. Old bullet list caused all 4 questions fired in one turn.
- New `[IVR vs Voicemail Detection - CRITICAL DISAMBIGUATION]` section with keyword-based classification. Voicemail indicators: "record/rerecord your message", "press pound to send". IVR indicators: "press X for sales/operator". Tiebreaker: assume voicemail.
- `[Speech Naturalness]`: "um"/"uh" minimized to once per call max (was explicitly permitted).
- `[Pronunciation]`: "Point of Sale" never "POS" (Nico says "paws"), "from" never "with".
- `[No Stage Directions]` expanded: banned throat-clearing, coughing, sighing, humming, and text like "*clears throat*" that TTS acts out.
- Transcriber: `smartFormat` false → true (Deepgram suppresses non-speech artifacts).
- Model: Llama 3.3 70B tested (cheaper/faster) but reverted to Claude 3 Haiku (better instruction following). System prompt preserved through swap.
- Voice: Nico kept (Emma + Layla as fallbacks).

**Alex (Brand, `1d7c5d42`) — same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Savannah (V1 Outbound, `3f9bbfd2`) — same IVR/voicemail disambiguation, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Outbound Dialer (`r7UjWLndmc6EqEUW`) — stuck queue fix:**
- Contact `AX3wfQNpRwm6DG0HgUE2` (deleted from GHL, 2 entries in voice_call_queue) blocked every dialer run since ~18:38 UTC.
- `HTTP - Get GHL Contact` had `neverError: false` — GHL's 400 crashed the run before lock release. Same contact re-picked every 2 min.
- Fix: `neverError: true` on lookup node (400 passes through to Code - Check Phone which falls back to queue phone). `onError: continueRegularOutput` on `GHL - Create Call Note` (cosmetic note failure won't error the execution).
- Intake poller (`bYk1Ai6MJLyhTsDZ`) was unaffected — continued enqueueing contacts every 10 min throughout.

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

### Regulated-Business Classification and SDR Work Queue Boundary

- Warm is the unassigned intake and verification layer.
- The canonical classifier result is the GHL tag `qualified` for a regulated business (including nicotine, cannabis, CBD, vape, hemp, and related regulated verticals), or `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate; qualified opportunities belong in `Sales Outreach -> Qualified`, not `Sales Outreach -> New`.
- SDR allocation occurs only at Sales Outreach entry:
  - one existing owner: align the other record;
  - matching owners: preserve;
  - conflicting owners: flag for review;
  - neither owner present: deterministic Jason/Marc 50/50 assignment.
- Keep contact `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned.
- Vapi remains in Warm and must exclude contacts tagged `not qualified`; the intake path must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR, who then promotes the record to Sales Outreach.
- Vapi booking remains on Cameron's Regulated Ads calendar; warm transfer uses the shared SDR number and neutral Sales Lead language.
- Vapi transfer tool: `86d380a3-34d2-41f8-96a0-acf5f0124ccb` (`transferCall`); live human-facing wording is neutral Sales Lead language, while compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600` remain unchanged.

### Website Booking Path

- Canonical calendar: `Regulated Ads On Social/Search`.
- Calendar ID: `SrtXcFVyea7pFl3nTiIK`.
- Direct booking URL: `https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK`.
- Website `Book a Demo` CTAs should link directly to this widget or embed it in an iframe. Visitors should enter identity/contact fields once on the booking form.
- The legacy GHL hero form `kxrHpS9bX16nzkIbr2py` must not appear before the booking form for the primary demo CTA; it duplicates name, email, and phone collection.
- The `/apply/` page currently has a legacy Calendly embed and should replace it with:

```html
<div style="width:100%; max-width:1100px; margin:0 auto;">
  <iframe
    src="https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK?utm_source=website&amp;utm_medium=calendar&amp;utm_campaign=regulated_ads_booking&amp;utm_content=apply_page"
    style="width:100%; min-height:900px; border:0;"
    scrolling="no"
    title="Book a Regulated Ads Strategy Call">
  </iframe>
</div>
<script src="https://link.msgsndr.com/js/form_embed.js"></script>
```

- After any website booking change, verify the appointment is created on `SrtXcFVyea7pFl3nTiIK`, not a personal, interview, or Calendly calendar.

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

In callback workflow fx4UvKUWbqJEY3LK, when Vapi returns wrong_number or contact_disconnected, Vapi first tries every available phone number for the contact before requesting Apollo enrichment (2026-08-04).

**Phone candidate sources** (built by the dialer's `Code - Check Phone`, deduped + E.164-normalized): GHL primary `phone`, `Corporate Phone` (`036gD9ds9P5V8VUHnFBP`), `Company Phone` (`YNlWu5FRGk0PhepqD0Zo`), `Em_All_Known_Phones` (`F8iUFGsA8CqdzEzjY3Eh`, may hold multiple), and the queue's `phone_e164` pool fallback.

**How it works:**
- `voice_call_queue` gained `phone_candidates jsonb` and `phone_index integer NOT NULL DEFAULT 0`.
- The dialer (`r7UjWLndmc6EqEUW`) builds the candidate list, picks `phone_candidates[phone_index]`, and passes `phone_candidates` (JSON string) + `phone_index` into the Vapi call metadata/variableValues. `Postgres - Mark Attempted` (updated) also persists `phone_candidates` and `phone_index` to the queue row after the call is submitted.
- The callback's `Code - Normalize End Of Call` extracts `phone_candidates`/`phone_index` from the Vapi metadata (same proven path as `queue_id`).
- `Code - Decide Next Phone` (replaces the old `Should Re-enrich Phone` IF) reads disposition + candidates + index from `Code - Normalize End Of Call`. If `wrong_number`/`contact_disconnected` and `(index + 1) < candidates.length`, it advances: `Postgres - Advance Phone Index` sets `phone_index + 1`, `status='pending'`, `attempt_count=0`, `next_attempt_at=NOW()`, clears the lock, and `HTTP - Remove Bad Call Tag` removes the `vapi_wrong_number`/`vapi_contact_disconnected` tag from GHL so the dialer's blocklist doesn't skip the retry. Only after the last candidate fails does `HTTP - Set Apollo Enrichment` set `Enrich Phone via Apollo = Yes` (custom field gdJDuZelIxEBE6n9i5Q6). The existing LT - Apollo Phone Enrichment Intake V3 then looks up a new number.
- If `queue_id`/`phone_candidates` are absent from the metadata (rare non-dialer call), the decision degrades to the previous behavior (Apollo enrichment immediately).

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

**2026-07-16 Fix (incomplete)**:
- `Classify Contacts` now outputs `source_tag` (the matched campaign tag) with every enqueue result
- `removeTag()` function accepts `tagsToRemove` array argument
- `removeFromQueue` check replaced by `hasAnyBlocklistTag()` checking all 8 outcome tags
- **BUT**: `Transform Postgres Output` couldn't read `source_tag` — Postgres `INSERT...RETURNING` only returns DB columns, not the extra `source_tag` field. `Remove Tag - Enqueued` silently fell back to removing `"vapi_queue"`, which contacts never had. Campaign tag stayed on first enqueue.

**2026-07-22 Fix (this session)**: Rewrote `Transform Postgres Output` to look up `source_tag` from `$("Classify Contacts").all()` by `contact_id` using a pre-built lookup map, instead of expecting Postgres to pass it through. `Remove Tag - Enqueued` now receives the real campaign tag on every run.

**Self-healing behavior**: On the next poller cycle after a contact gets a blocklist outcome tag, `Classify Contacts` matches it in the `skipped` path (not the `enqueue` path). The `skipped` path resolves `matchedCampaignTag` in-scope before any Postgres call and removes the campaign tag inline. So even before this fix, contacts eventually self-cleaned within 1 cycle after getting a terminal tag — but the first enqueue always left the campaign tag intact.

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

### Vapi Call-Path Hardening (2026-07-22 — 2026-07-23)

- n8n target upgraded to `2.33.3`; recurring workflows use native Schedule Trigger nodes, not OS/Coolify cron jobs.
- `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` input because the Config Set node replaces the current item.
- Callback normalization now reads Vapi IDs from `message.assistant.metadata`, `message.assistant.variableValues`, and `artifact.variables`.
- Callback completion-note JSON is built as an object expression, avoiding invalid JSON when summaries contain quotes or newlines.
- GHL note/tag failures continue without blocking Postgres queue completion; queue completion passes query replacements as an array.
- The callback no longer invokes `LT - Voice Dequeue Next`. That helper is unpublished and must remain an explicit/manual helper, not an automatic call-start path.
- The outbound dialer uses a native two-minute Schedule Trigger plus the existing timezone-aware business-hours guard.
- The outbound dialer atomically changes a selected queue row from `pending` to `in_progress` before calling Vapi. Ambiguous Vapi/API failures cannot be retried after the stale-lock window; no-phone and outside-hours release branches explicitly restore `pending`.

### Vapi/n8n Final Hardening (2026-07-23)

- n8n is now documented and operated at target version `2.33.3`; recurring workflows use native Schedule Trigger nodes rather than OS/Coolify cron.
- Callback timer state keeps the 60-second duplicate-start guard and now prunes ended/inactive entries older than 30 minutes.
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) requires `X-LT-Voice-Queue-Secret`; the caller reference is `VOICE_QUEUE_ENQUEUE_SECRET`. Missing authentication fails closed before queue insertion.
- `LT - Apollo Phone Enrichment Polling` reports `apollo_phone_request_failed` when the asynchronous Apollo phone request fails after profile processing.
- `LT - Apollo Queued Timeout Reaper` now connects `Build Slack Summary` to `Post to Slack #leads`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- Final live workflow versions were checked after each mutation; `versionId` matched `activeVersionId` for all changed workflows.
- Safe queue smoke checks passed: unauthenticated requests return `400 unauthorized`; authenticated malformed requests reach validation and do not insert a queue row. Live Vapi control URLs remain untested because exercising them requires an actual call.

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
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Current State

- 4 senders: cameron@livetransparent.{com,co,agency,org}, warmup Week 1 cap 300/day each
- Safety buffer: 5% of cap (15/sender), remaining: 285/sender/day
- Backlog: ~4,918 unreleased after DNC/DND SQL filtering
- Email events flowing to Email_Events table within 3 min

### Sender Capacity (Week 1, per-day)

| Sender | Cap | Safety (5%) | Remaining |
|--------|-----|-------------|-----------|
| cameron@livetransparent.com | 300 | 15 | 285 |
| cameron@livetransparent.co | 300 | 15 | 285 |
| cameron@livetransparent.agency | 300 | 15 | 285 |
| cameron@livetransparent.org | 300 | 15 | 285 |

**Total: ~1,140/day** (4 × 285). Warmup stages: Week 2 = 400/day, Week 3+ = 500/day.

### Fixes Applied (2026-07-21)

- **CRITICAL: In-flight capacity double-counting**: `Estimate InFlight Due Today` queried across 3 days (`CURRENT_DATE, -2d, -4d`), inflating `inFlightDueToday` to 285/sender and blocking all dispatches. Changed to `release_date = CURRENT_DATE` — counts only today's releases.
- **Known unfixed**: Dispatch code uses `doHttpRequest` wrapper (HTTP 400 risk in task-runner loops). Write Release Log uses template-literal SQL injection. These are low-risk for Emerald's current low volume but should be migrated to match DAN's patterns.

### Reply Suppression Repair (2026-07-26)

- `WL - Seq - Stop on Booked/Reply/Closed` (`3dd33ec4-d8c2-40c6-b72f-d1cba57b8c39`) had the correct Email reply trigger, but its removal action only targeted the legacy Variant A/B workflows. It did not remove contacts from the Emerald sequences.
- Added all 12 Emerald sequence workflows, including P2 variants, to the removal action through the GHL UI and published version 17.
- n8n `LT - Email Event Ingest` is reporting-only and does not suppress sequence enrollment.
- For the affected Christy Essex contact, removed `seq enrolled - emerald` and `seq emerald - executives sso` while preserving Warm/MQL state and the opportunity.

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

**Pipeline**: Schedule Trigger -> Config -> Ensure Release Log Table -> Fetch DAN Candidates -> Dispatch + Queue (DryRun Safe) -> Only Queued (filter) -> Write Release Log (with Summary branch)

**Config**: dryRun=false, candidateLimit=85, senders=cameron@livetransparent.{com,co,agency,org} (round-robin), senderFieldName=marketing_sender_email

**Fixes applied 2026-07-14:**
- Schedule changed from hourly to every 30 min (was only hitting 600/day, needed 1200+)
- Added `await new Promise(r => setTimeout(r, 250))` between each contact's GHL API calls to prevent rate limiting (was seeing 20-40% `error_fetch_contact` on early runs)
- candidateLimit increased from 50 to 65 to compensate for ~10 recurring DNC contacts per run (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms — have `do not contact` in GHL but stale data in report_raw_ghl_contacts)

**Fixes applied 2026-07-15 (code/logic audit):**
- **Brand starvation**: Changed `ORDER BY epc.source_list, epc.id ASC` → `ORDER BY RANDOM()` so brands and dispensaries interleave proportionally instead of brands always filling the slot limit first
- **HTTP wrapper**: Removed `doHttpRequest` wrapper function and deprecated `$httpRequest` — all HTTP calls use `this.helpers.httpRequest(options)` directly
- **Sender rotation**: Added 4-sender pool (`cameron@livetransparent.{com,co,agency,org}`) with round-robin via `ci % senders.length`, matching Emerald's warmup pattern
- **Jitter**: Delay randomized to `250 + Math.random() * 250`ms to prevent thundering herd on GHL API recovery

**Fixes applied 2026-07-21 (full audit + hardening):**
- **CRITICAL: Release log crash on skipped_dnc**: `Only Queued` filter passed all non-summary items to `Write Release Log`, but `skipped_dnc` items lacked `enrollment_tag` which is `NOT NULL` in the table. Every daytime run errored on the INSERT. Tags WERE being applied to GHL, so emails were sending, but tracking was broken and the report showed `0 emails sent`.
  - Fix #1: Changed `Only Queued` filter from `status !== "summary"` to `status === "queued"` so only valid items reach the INSERT.
  - Fix #2: Expanded filter to `s !== "summary" && s !== "skipped_incomplete"` — passes `queued`, `skipped_dnc`, and all error items now that they carry `enrollment_tag`.
- **CRITICAL: SQL injection in Write Release Log**: Template-literal `.replace(/'/g, "''")` pattern replaced with parameterized `$1..$10` placeholders and `queryReplacement` array. Same anti-pattern previously fixed in LinkedIn Reply Backfill and Apollo Sheet First.
- **Self-healing pipeline**: `Dispatch + Queue` code now outputs `enrollment_tag`, `first_name`, `last_name`, `company_name` in ALL non-summary items (`skipped_dnc`, `error_fetch_contact`, `error_set_sender`, `error_add_tag`). This means every outcome — success or skip — gets tracked in `DAN_Release_Log`, permanently excluding that contact from future SQL candidate fetches. Pool self-cleans within a few dispatch cycles.
- **Candidate limit**: 65 → 85 to compensate for backfilled/skipped contacts, targeting higher throughput.

**Candidate freshness (3-layer defense):**
1. **SQL dedup**: `NOT EXISTS (SELECT 1 FROM "DAN_Release_Log" r WHERE r.contact_id = epc.ghl_contact_id AND r.campaign = epc.source_list)` — any contact with a release log entry is excluded
2. **SQL tag filter**: `(lt.tags_raw IS NULL OR NOT (lt.tags_raw ILIKE '%seq enrolled - dan%'))` — stale report data catches already-enrolled contacts
3. **Live GHL check**: Per-contact `GET /contacts/{id}` + `isBlocked()` tag check — blocks contacts with `do not contact`, `do not nurture`, `unsubscribed`, `opted out`, `seq enrolled - dan`

All three layers feed into the release log: any contact that passes the SQL but gets live-skipped is recorded with `status: 'skipped_dnc'` (with enrollment_tag) and won't reappear.

**Dispatch performance (2026-07-21):**
- Max theoretical: 85 contacts × 24 runs/day = 2,040/day (Mon-Sat 8 AM ET to 5 PM PT window)
- After fix, first dispatch window will self-clean: previously-tagged contacts get release-logged as `skipped_dnc`, fresh contacts get `queued`
- Email events flow: GHL → n8n Email Event Ingest (`ZrqFN8qLKO8eVHDc`) → Postgres `Email_Events` table → Daily Rollups → Executive Summary
- Report dashboard (`emailsSent`/`emailsOpened`/`emailsClicked`) will populate as the release log backfills and daily rollups ingest

**Enrollment tags applied**:
- Brands: Enrollment Queue - DAN - Brands
- Dispensaries: Enrollment Queue - DAN - Dispensaries

**Deduplication**: Per-contact + per-campaign via DAN_Release_Log table (UNIQUE on contact_id, campaign). Every outcome (queued, skipped_dnc, errors) writes to the release log, permanently excluding the contact from future candidate fetches.

**DNC/unsubscribe protection** (three layers — see "Candidate freshness" above for full details):
1. SQL-level: filters report_raw_ghl_contacts.tags_raw for do not contact, do not nurture, unsubscribed, opted out, seq enrolled - dan
2. Per-contact live GHL check: GET /contacts/{id} before dispatching
3. Release log dedup: any contact with a DAN_Release_Log entry (any status) is excluded from SQL candidates

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

- WL - Micro - DAN Brand Deck Download -- trigger link bNK7txDSQJkvrgmmH9aZ -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- WL - Micro - DAN Dispensary Deck Download -- trigger link DDPOwxFCexuf3cYGOAPt -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- 3x open handling via WL - Micro - Email Open Counter + Assignment to Jason (42aa5940) is an engagement signal only; it must not independently assign an SDR or promote a Warm record

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

### Data Pipeline (4 Layers)

```
Raw Ingest → Attribution Bridge → Daily Rollups → Executive Summary API (GET /lt-report-executive-summary)
```

### Raw Ingest Workflows

| Workflow | ID | Schedule | Target Table |
|----------|----|----------|--------------|
| GHL Daily Leads Ingest | osIJOgBmWITF5Yuv | Every 60 min | `report_raw_ghl_contacts` |
| GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 | Daily | `report_raw_ghl_opportunities` |
| GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq | Daily (24h) | `report_raw_ga4_sessions` |
| GSC Daily Ingest | xHqmCC1vOeZ11gCd | Daily | `report_raw_gsc_queries` |
| GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l | Every 4 hr | `report_raw_ghl_calls` + `outcomes` |
| GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG | Daily | `report_raw_ghl_appointments` |
| GHL Daily Social Ingest | QZoqCaTwDhbym80O | Daily | `report_raw_ghl_social_posts` |

### GHL Leads Ingest Rate-Limit Guard

`LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) uses direct `this.helpers.httpRequest` calls in `Fetch + Normalize Leads`. Do not restore the `doHttpRequest`/`$httpRequest` wrapper pattern. GHL contact pagination retries HTTP 429 responses up to four attempts with `Retry-After` or exponential backoff and waits 500 ms between pages. The live fix was published as version `c740c006-fef5-4873-91b5-d2d4218872de` and validated by execution `241894` with 500 contacts.

### Bridge & Rollup Workflows

| Workflow | ID | Status |
|----------|----|--------|
| GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi | Active |
| GSC Rollup Bridge | fOVBHwti9rC3qrLV | Active |
| Report Attribution Bridge | Y0TU7Il71JswxOBp | Active (daily, 90-day window) |
| Report Daily Rollups | EUeOiRttoVLQ9zF9 | Active (daily, 90-day backfill) |
| Report Pipeline Velocity | iFfwh0jpYUZoDhDR | Active |

### API & Frontend

| Workflow | ID | Status |
|----------|----|--------|
| Report Executive Summary API | Bukc0mgOD2r7V6ED | Active (webhook GET) |
| Report Outgoing Calls Detail | VXFHc8IrF9DDEEdj | Active (webhook GET; published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`) |
| Report QA and Alerts | M5mXcDTFSko6EdHb | Active |
| Report Config Sync | aomO3Z4AXJIgEvvN | Active |
| Report Publish Refresh | 3gXztCnBEN6sGINb | Active |
| Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 | Active |

### MQL / Company Sync

| Workflow | ID | Status |
|----------|----|--------|
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV | Active (daily 6am ET) |

### Executive Report Data Sections (2026-07-21)

The `Report Executive Summary API` (`GET /webhook/lt-report-executive-summary?range=30d`) returns these top-level keys:

| Section | Source | Description |
|---------|--------|-------------|
| `traffic` / `leads` / `sales` | `report_daily_summary` | GA4 sessions, GHL contacts created, closed-won count |
| `summary` | `metric_summary` CTE | Full nested metrics: funnel rates, coverage, revenue, calls, timezone |
| `channelBreakdown` | `report_channel_daily_summary` | Top 8 channels by sessions/leads/opps |
| `utmBreakdown` | `report_utm_daily_summary` | Top 15 UTM source/medium/campaign combos |
| `metaAttribution` | `report_bridge_traffic_to_lead` | Meta (Facebook/Instagram) attribution |
| `pipelineDropoff` | `report_pipeline_daily_summary` | Per-pipeline stage counts + moved-in/moved-out |
| `stageDropoff` | `report_stage_daily_summary` | Top 10 stages by movement |
| `stageVelocity` | `report_stage_velocity_summary` | Avg days per stage |
| `opportunityStageBreakdown` | `report_raw_ghl_opportunities` | Active/worked/stage-mover counts per pipeline+stage |
| `socialPosts` | `report_raw_ghl_social_posts` | Post totals and engagement (likes/comments/shares/saves/reach/impressions; reads plural and singular keys from `insights` and preserved post payloads since 2026-08-04) |
| `health` | `report_source_health` | Source system health statuses |
| `callStatusBreakdown` | `report_raw_ghl_calls` | Top 10 call statuses by direction |
| `callOutcomeBreakdown` | `report_raw_ghl_call_outcomes` | Top 12 dispositions by direction |
| `appointments` | `report_raw_ghl_appointments` | Top 8 appointment statuses |
| **`emailsSent` / `emailsOpened` / `emailsClicked` / `emailsBounced`** | `report_daily_summary` + `Email_Events` + Release Logs | Email campaign metrics (added 2026-07-21) |
| **`emailOpenRate` / `emailClickRate` / `emailBounceRate`** | Computed from above | Email engagement rates (added 2026-07-21) |
| **`linkedinFunnel`** | `linkedin_connection_state` | ready→requested→connected→DM active→completed (added 2026-07-21) |
| **`vapiCampaignBreakdown`** | `voice_call_attempt` JOIN `voice_call_queue` | Per-campaign call totals, answered, qualified, booked (added 2026-07-21) |
| **Outgoing Call Detail** | `voice_call_attempt` JOIN `voice_call_queue` + latest `report_raw_ghl_contacts` snapshot | Seven completed days of paginated Vapi call rows with disposition, duration, contact ID/name fallback, campaign, first-attempt flag, and signed recording URL |
| **`vapiQueueDistribution`** | `voice_call_queue` (status=pending) | Pending queue by campaign (added 2026-07-21) |
| **`mqlSummary`** | `report_raw_ghl_opportunities` (stage IDs) | Active + total MQL opportunities (added 2026-07-21) |
| **`sqlContacts`** | `report_raw_ghl_contacts` (tag search) | Contacts with SQL tag (added 2026-07-21) |
| **`poolDistribution`** | `report_raw_ghl_contacts` (tag counts) | brands_pool, dispensaries_pool, vapi brand/dispensary (added 2026-07-21) |

### Stage Name Resolution (2026-07-21 Fix)

GHL stage names (`pipeline_stage_name`) are NULL in `report_raw_ghl_opportunities`. The report resolves stage names by falling back to `pipeline_stage_id` with a CASE mapping matching the Daily Rollups workflow. Pipeline names use the same ID-based resolution. This fixes `stage_movers` (was 0, now 93), `meetingsBooked`, and `closedWonCount` which previously depended on NULL stage name fields.

### report_daily_summary New Columns (2026-07-21)

| Column | Source |
|--------|--------|
| `emails_sent` | `DAN_Release_Log` + `Emerald_Release_Log` (release_date) |
| `emails_opened` | `Email_Events` (event_type='opened') |
| `emails_clicked` | `Email_Events` (event_type='clicked') |
| `emails_bounced` | `Email_Events` (event_type='bounced') |
| `emails_unsubscribed` | `Email_Events` (event_type='unsubscribed') |
| `emails_complained` | `Email_Events` (event_type='complained') |

### Voice Dialer Fix (2026-07-21)

`LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`): `GHL - Create Call Note` node now has `onError: continueRegularOutput`. Previously the dialer errored on every run because deleted GHL contact `AX3wfQNpRwm6DG0HgUE2` (still in `voice_call_queue`) caused a 400 on the note creation endpoint. Calls go out successfully; note failure is cosmetic.

## Partnership Marketing Pipeline (Infrastructure Live, Outbound Dry-Run 2026-07-31)

131 content partnership contacts imported. Two parallel sequences from Cameron's accounts: a 4-step email sequence and a 4-step LinkedIn DM cadence. All infrastructure isolated from DAN/Emerald (separate Postgres tables, workflows, GHL pipeline).

### Pipeline

- **GHL Pipeline**: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`) — New Partner Lead → Contacted → Proposal Sent → Closed
- **Contacts**: 98 email + 33 LinkedIn-only, all assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- **Tags**: `partner_candidate_email`, `partner_candidate_linkedin`, `partner_email_queued`, `partner_linkedin_requested`, `partner_email_sequence_completed`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact`
- **GHL API key**: configured in the live dispatcher Config nodes and Reply Poller runtime; value intentionally omitted from documentation
- **14 contacts excluded** from original CSVs due to wrong company/email domain mismatches — awaiting corrections

### Email Templates

4 templates in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`):

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The Code node HTML is the canonical message content; templates exist for open tracking and deliverability.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'` |
| `partnership_release_log` | Tracks every sent email. UNIQUE on `(ghl_contact_id, email_step)`. |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active, dry-run | 60/day planning, 11am ET Mon-Fri, 2-weekday intervals |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active, dry-run | 30 connection-request planning, 3pm CT Mon-Fri, state seeding + atomic claim |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active, dry-run | 4-step DM planning, 2-weekday intervals |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | `/webhook/lt-partnership-reply` — tags `partner_replied`, creates opportunity, Slack alert, and writes a `replied` event to `Email_Events` |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Every 5 min — polls GHL for inbound email replies via `GET /conversations/search`, triggers Reply Handler |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | `/webhook/lt-partnership-bulk-import` |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on LinkedIn-only contacts |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows query `partnership_linkedin_connection_state` in addition to main table:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION + `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL + separate Update node |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing + separate update node |

### Remaining

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder. PIT REST access cannot mutate widget layouts; do not guess undocumented report-builder endpoints.
- **Re-import 14 excluded contacts** after corrected company names provided
- **Outbound activation**: Approved and enabled 2026-07-31. Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence now use `defaultDryRun=false`; their published active versions are `6b7490a9-05d8-44e1-8f94-3c4427a7f969`, `29089175-1b37-4271-8b03-d4722b809692`, and `3bd0b759-4740-4e67-85ef-9540bf31c08e`. The dispatcher seeds 127 partnership `ready` state rows before queue fetch.
- **Live workflow verification 2026-07-31**: All 7 partnership workflows are active and published. Fixed the Email Dispatcher schedule to `0 11 * * 1-5` America/New_York, the LinkedIn Dispatcher schedule to `0 15 * * 1-5` America/Chicago, and the LinkedIn DM schedule to `0 12 * * 1-5` America/Chicago; prior interval definitions were firing hourly. Fixed the DM terminal completion scan to include `sequence_step <= 4` and corrected the shared LinkedIn Acceptance Checker state-upsert header. Safe manual smoke executions `281269` (email), `281268` (LinkedIn), and `281270` (DM) succeeded with outbound dry-run enabled.
- **Live outbound activation 2026-07-31**: Explicit user approval changed all three outbound `defaultDryRun` controls to `false`; all three drafts were published and verified with `versionId == activeVersionId`. Do not manually execute these workflows unless intentionally sending an additional live batch; scheduled runs now send real outreach.
- **Credential migration**: Move partnership GHL, Unipile, and state-upsert secrets out of Config/Code literals and rotate them after migration.
- **Reply Poller API gap resolved 2026-08-04**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) uses supported `GET /contacts/` pagination for active contacts and `GET /conversations/search` for inbound email reply lookup. It records lookup failures and fails closed instead of treating an ambiguous lookup as no reply. Smoke execution `522221` returned `checked: 58`, `replied: 0`, and `errors: []`; current published version is `736386a2-a7d2-434d-b9ba-72026e49c98b`.
- **Executive Report response-rate + social fixes (2026-08-04)**: User reported 1 partnership email reply and 1 partnership LinkedIn reply showing as 0 response rate, and incorrect LinkedIn/email data for the 3 campaigns. Four root causes fixed and published:
  1. **Reply Poller used `POST /conversations/search` (404)** — the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522241` returns `errors: []`. Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event** — `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill was one-shot** — `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-checks rows older than 6 hours with `dm_conversation_status <> 'active'`. Published version `0620c314-befb-462e-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch** — the Executive Summary `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but GHL stores `like`/`comment`/`share` (singular). The `Build Query` node now `COALESCE`s both. Verified: `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  - **Historical reply backfill completed 2026-08-04**: the verified Strider Peterson email reply was recorded in `Email_Events` with its actual GHL inbound timestamp (`2026-08-03T15:41:03Z`), and the verified Jaret Christopher LinkedIn reply was recorded in `linkedin_activity_events` at `2026-08-01T03:05:55Z`. The one-time helper workflows were executed successfully and archived. The selected-window Campaign Channel Summary now shows `Partnership emails`: 59 sent, 1 reply, 1.69% response rate; and `Partnership LinkedIn`: 17 invites, 1 reply.
  - **Reach/impressions/saves ingestion remains pending**: the official GHL statistics endpoint returned `152` impressions and `61` reach for its current seven-day OAuth window, proving the source data is available. n8n still has no usable GHL OAuth credential; the PIT returns 401. The Executive Summary query and UI now expose null-safe `totalSaves`, `totalReach`, and `totalImpressions` fields from raw post payloads, but the current PIT-based `posts/list` ingest supplies none of these metrics, so they remain zero until OAuth-backed scheduled ingestion is added.

### Audit (2026-07-31)

Full audit passed:
- All 7 partnership workflows published and active (versionId == activeVersionId for all)
- 3 patched LinkedIn workflows verified: correct SQL UNION/UNION ALL queries, source_table routing, and dedicated partnership update nodes in Reply Backfill and New Messages
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) published with `partnership_release_log` UNION ALL in `email_sent` CTE (version `6641aa9a`). Endpoint confirmed returning "Partnership emails" row.
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped on live VPS; the LinkedIn state table has 127 seeded `ready` rows. The release log was empty during the initial dry-run audit; outbound is now live.
- Partnership candidate lookups use supported `GET /contacts/` pagination with explicit failure handling. LinkedIn state seeding checks existing IDs first; validation execution `278675` found 127 existing rows, seeded 0, and completed the dry-run request plan without outbound sends.
- Post-remediation scheduled executions `278513` (email), `278515` (LinkedIn), `278634` (DM), and `278611` (reply polling) succeeded with no error/crash executions after the fixes.
- Executive Report frontend deployed as build `2026-08-01-v12-campaign-breakdown` to reports.livetransparent.com. It directly fetches campaign channel data, renders LinkedIn Invites/Accepted/Replies, and displays social likes/comments/shares/saves/reach/impressions when supplied.
- GHL contacts verified: 98 `partner_candidate_email`, 127 `partner_candidate_linkedin` (94 overlap + 33 LinkedIn-only), 131 total. All assigned to Janvi.
- 4 email templates confirmed in folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`)
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected — all existing DAN/Emerald/LinkedIn/Vapi workflows unaffected

## Other Live Systems

- **SimpleTexting**: Provider bridge, delivery, inbound reply, unsubscribe, and idempotent-send workflows remain available for operator/inbound handling. `LT - SimpleTexting Campaign Step Runner` (`dUyOfxllvkxZavaw`) and `LT - SimpleTexting Campaign Phone Backfill` (`8hQKQi1PooYDFxNR`) remain **unpublished** pending SimpleTexting account re-enablement; do not republish or send live campaign traffic while the provider-side HTTP 409/compliance issue remains unresolved. The pool dispatcher (`usxYXSuc4ahw40V3`) is a separate outbound scheduling path and must be reviewed before campaign resumption. Inbound replies add `simpletext_replied`, remove `simpletext_ongoing`, mark campaign state `replied`, and suppress future campaign/direct sends; `simpletext_stop` remains the opt-out hard stop. `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) posts a Slack alert through node `Post to Slack` with title `Inbound SimpleTexting Reply`, then posts the inbound message to GHL Conversations under `SimpleTexting SMS` via `Post to GHL Conversations` node using `type: "Custom"`, `conversationProviderId: "6a5b91913953360948dd59f1`, and `altId`. On 2026-07-26, the send webhook's live registry updated `sms_1`, `sms_3`, and `sms_5` copy. On 2026-07-29, published `sms_4` was revised to remove `flower`, `pre-roll`, and the Facebook ad preview link while retaining neutral `regulated-industry` positioning; active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- **SimpleTexting GHL Conversations provider**: **LIVE** as of 2026-07-20. Separate GHL private app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`. `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) receives GHL outbound replies, validates provider ID, normalizes phone to E.164, checks `simpletext_stop` tag, and sends via the idempotent send workflow (`gwaEpWDpTIwsafi8`) → SimpleTexting API. Outbound campaign sends mirror into GHL Conversations via `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). `simpletexting_conversation_map` table created in Postgres keyed by `(conversation_provider_id, alt_id)`. GHL Conversations is the primary operator inbox for SimpleTexting SMS; Slack alert for inbound replies is preserved.
- **Unipile/Instagram**: Instagram DM Sequence (`iCnY6ccdHhfJg3sf`) is **unpublished**. It was misconfigured with the LinkedIn Unipile account ID and sent Instagram templates as LinkedIn DMs. Do not republish until it has a real Instagram Unipile account ID and account-type guard.
- **Instagram inbound bridge**: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active at `/webhook/lt-unipile-instagram-new-messages`. It normalizes Unipile Instagram inbound payloads, conservatively resolves an existing GHL contact before creating one, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token via `POST /oauth/locationToken`, and posts inbound messages into GHL Conversations under the `Instagram via Unipile` tab. Post-merge cleanup on 2026-07-16 repointed `instagram_conversation_map.id = 1` for chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`; the temporary duplicate `4V2oTmM7lWya3Nmtmp1Y` created during verification was deleted.
- **Social provider outbound router**: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active at `/webhook/lt-social-provider-outbound`. Fixed 2026-07-16: POST webhook `responseMode` now uses `responseNode`, map tables are created defensively, payload message text is preserved through Postgres lookup, and Unipile send uses the working `api42.unipile.com:17256/api/v1` base. Canonical provider IDs are SMS-type additional custom conversation providers: `Instagram via Unipile` = `6a58a1193cdfc36997580a68` and `LinkedIn via Unipile` = `6a58a14ff3023bea3783c152`. Inbound message API must use `type: "Custom"` with `conversationProviderId` + `altId`; do not include `emailTo`/`emailFrom`/`subject` or dummy contact phone/email data. Deleted Email provider IDs `6a5893d11e9368345005f66e` and `6a5892b9107668309b3f85ac` must not be reused. Verified Instagram and LinkedIn inbound as `TYPE_CUSTOM_PROVIDER_SMS`; Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` both map to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, with LinkedIn conversation `Ze8o3KbsrwuAXQ3KK5ge`. LinkedIn normalizer handles Unipile's form-encoded single-JSON-key webhook shape. Direct outbound router smoke tests after map repair passed: Instagram message `vjdEYSk9XD6R0I46oPWLwA`, LinkedIn message `C7I9944kWsSKutX2XhZEpA`.
- **Social provider bridge handoff**: Full build context, operator inbox runbook, monitoring gaps, and next steps for `LinkedIn via Unipile` + `Instagram via Unipile` GHL bidirectional messaging are in `docs/strategy/unipile-ghl-bidirectional-integration.md`. Read this before changing provider workflows.
- **Unipile/LinkedIn**: Active production path is dispatcher → acceptance/state sync → canonical DM sequence. Follower DM (`pq7XVajNFnnwMUTr`) is **unpublished**. Current published workflow inventory is documented in `Current Published Workflow Inventory` above. Guardrails block John-branded copy.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: Workflow exports are staged in the repo, but campaign execution is paused because SimpleTexting requires account re-enablement. Keep the Step Runner and Phone Backfill unpublished and do not force live sends. The canonical send webhook is `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`; template registry details are in `docs/outreach/sms_edited_templatekeys.md`. Resume only after provider acceptance is verified with a real provider message ID and the bounded-volume safeguards are rechecked.

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
- Partnership Marketing/partnership_master.json
- Partnership Marketing/Content Partnerships - Email - Consolidated List.csv
- Partnership Marketing/Content Partnerships - Linkedln - Consolidated List.csv
- Partnership Marketing/Email Partnership Outreach Sequence.docx
- Partnership Marketing/Linkedln Partnership Outreach Sequence.docx
- scripts/clean_partnership_data.py
- postgres/partnership-bootstrap.sql

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

## Historical Repair Context

The original repair is complete. The old hardcoded `voice_call_queue` selection and executive-focused classifier path are no longer live. This document remains as design history; current production behavior is documented in `classifier-workflow-change-plan.md` and the audit note in `AGENTS.md`.

The current workflow is built around `emerging_pool_contacts`, uses live GHL checks, and runs on a 15-minute native schedule with a 10 + 10 candidate cap.

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
- contacts with an authoritative qualification result that is qualified or rejected/non-cannabis; only explicitly pending/unverified contacts may enter Vapi
- contacts without a usable linked `ghl_contact_id`
- contacts without a callable phone path

## Recommended Rule Set

Do not reuse the old broad `sso` substring heuristic.

### Brand campaign candidates
- `source_list = 'brands'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged
- qualification state is explicitly pending or unverified; qualified/rejected records are excluded

### Dispensary campaign candidates
- `source_list = 'dispensaries'`
- linked `ghl_contact_id` present
- not already called or queued
- not DNC / not terminal Vapi tagged
- qualification state is explicitly pending or unverified; qualified/rejected records are excluded

This is simpler and safer than role-tag inference, because the new imports are already split into Brand vs Dispensary source pools.

## Recommended Workflow Shape

Manual Start is retained for controlled tests; production uses a native 15-minute Schedule Trigger.

1. `Manual Trigger` or `Schedule Trigger 15m`
2. `Postgres` select eligible rows from `emerging_pool_contacts`
3. `Code` normalize campaign tag payloads
4. `AI Gate` and DeepSeek classification when no qualified domain exists
5. `Merge AI and Cleanup Results`
6. `HTTP Request` add/remove GHL campaign tags
7. `Postgres` persist accepted non-free domains after successful tag writes
8. `Code` summarize counts, writes, failures, and qualification sources

## Recommended Eligibility Query Shape

The query below is the historical design skeleton. The live workflow deliberately lets candidates reach the live GHL lookup when imported/report phone fields are blank, then skips rows that remain uncallable.

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

1. Execute the manual or scheduled path and confirm the run completes
2. Confirm failed writes are zero and suppression cleanup is working
3. Spot-check accepted Brand and Dispensary tags in GHL
4. Confirm only successful accepted writes can create/update `vapi_qualified_domains`
5. Let the queue feeder consume newly tagged contacts

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

## Current Production State

The old hardcoded queue-contact selection described below is historical and no longer represents the live graph. The workflow is now a published regulated-business campaign gate.

Live behavior as of 2026-07-29:
- native Schedule Trigger every 15 minutes, plus a Manual Start for controlled tests
- up to 10 Brand and 10 Dispensary candidates per run
- live GHL contact lookup and suppression cleanup
- DeepSeek acceptance for candidates without a qualified domain
- persistent qualified-domain bypass through `vapi_qualified_domains`
- GHL writes only after an accepted classification or domain match

## New Purpose

The workflow now:
- selects eligible imported pool contacts from `emerging_pool_contacts`
- maps `source_list` directly to campaign tag
- applies `vapi_campaign_brand` or `vapi_campaign_dispensary` in GHL
- returns a summary of what was tagged
- records accepted non-free email domains only after a successful tag write

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

## Current Safety Controls

- `Called Contacts` selects up to 250 rows per source pool, while `Classify` caps the live run at 10 Brand and 10 Dispensary rows.
- Candidate ranking prefers imported-pool/report phones, but the live GHL lookup can supply the phone when those fields are blank; candidates still without a live phone are skipped.
- Suppression and terminal Vapi tags are checked in SQL and again against the live GHL contact.
- DeepSeek reasoning is limited to concise English and the model output budget is 600 tokens.
- Malformed model output is ignored by `Normalize AI Classification`; it cannot reach GHL tagging.
- Qualified-domain upsert requires an accepted tag action, a recognized qualification source, and a successful GHL response containing the campaign tag.

## Why This Is Better

- It removes stale dependence on the old executive-focused `Emerald_Contacts` path.
- It aligns the classifier to the imported pool that was already split into Brand vs Dispensary.
- It makes campaign selection deterministic rather than heuristic.
- It keeps the queue feeder as the downstream pacing mechanism.

## Suggested Validation Steps

1. Run `postgres/select-emerging-pool-vapi-candidates.sql`
2. Confirm there are eligible rows in both pools
3. Update workflow `IduCoT5YOs0g2faT`
4. Execute manually or wait for the native schedule
5. Confirm the summary reports zero failed writes
6. Spot-check tags and domain persistence in GHL/Postgres
7. Let `RFIZ9Bcfl3Yvms2b` pick up the newly tagged rows
````

## File: classifier-workflow-mcp-update-ops.md
````markdown
# LT - Campaign Contact Classifier MCP Update Ops

> Historical mutation record. The live workflow is now published and active on a native 15-minute Schedule Trigger. Fetch live state before using any operation in this file. Current behavior is documented in `classifier-workflow-change-plan.md` and `AGENTS.md`.

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
- historical seed example only: verify the current live cap from `get_workflow_details` (currently 10 Brand + 10 Dispensary rows)
- spot-check those contact IDs in GHL before letting the queue feeder continue
````

## File: classifier-workflow-patch-snippets.md
````markdown
# LT - Campaign Contact Classifier Patch Snippets

> Historical patch snippets. They are not the current production contract. The live workflow now runs every 15 minutes, caps selection at 10 Brand + 10 Dispensary candidates, uses DeepSeek plus qualified-domain matching, and requires successful GHL tag writes before domain persistence.

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

Use this to manually inspect a representative Brand and Dispensary sample before relying on the scheduled classifier. Production runs select up to 10 Brand + 10 Dispensary candidates.

### 8. Verify classifier workflow
- Use `classifier-workflow-change-plan.md` for the current production design.
- Use `classifier-repair-plan.md` only for historical repair context.

Target workflow:
- `IduCoT5YOs0g2faT`

### 9. Scheduled tag application / controlled validation
- The published classifier runs every 15 minutes and selects up to 10 Brand + 10 Dispensary candidates per run.
- It applies campaign tags only after DeepSeek acceptance or a prior qualified-domain match, with live GHL suppression checks.
- Let queue feeder workflow `RFIZ9Bcfl3Yvms2b` stage accepted contacts gradually.

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
- inspect a representative Brand and Dispensary sample
- confirm in GHL they are correct and callable
- note that production runs select up to 10 Brand + 10 Dispensary candidates

## Step 5: Verify classifier workflow

Current behavior:
- `docs/classifier/classifier-workflow-change-plan.md`
- historical patch payloads must not be applied without fetching live state first

Target workflow:
- `IduCoT5YOs0g2faT`

## Step 6: Run or observe classifier

Expected:
- up to 10 Brand and 10 Dispensary candidates selected per run
- only accepted AI/domain-list candidates tagged
- suppressed contacts have stale campaign tags cleaned up
- failed write count is zero

## Step 7: Validate tags in GHL

Check newly tagged contacts for:
- correct campaign tag
- correct company / persona fit
- no obvious mis-tagged executive rows

## Step 8: Verify queue feeder

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Expected:
- staged rows only for accepted, tagged contacts
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
Updated: August 6, 2026

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
- Campaign Channels: This table is the cross-channel campaign view. It shows named channel/campaign rows for DAN, Emerald, Partnership, SMS, LinkedIn, and Vapi, with channel-specific sends, engagement, replies, DMs, calls, qualification, and booked metrics where the source data exists. Use the All, Email, LinkedIn, SMS, and VAPI filters to focus on one channel.
- Outgoing Call Detail: This bottom-of-report table shows Vapi outbound call attempts for the seven most recent completed days. It is separate from the aggregate GHL Calls panel and includes contact ID/name fallback, phone, disposition, duration, first-attempt status, campaign, and on-demand recording playback. Use the sidebar Outgoing Calls bookmark to jump to it.
- Sales Detail / SDR Owner View: These cards use the same opportunity payload as the team summary. The owner view should be driven by canonical GHL user ID, not a hardcoded rep name.
- Social and Site: The Social Posts card shows the status of GHL Social Planner posts. Failed means the latest status is failed or error. The Site Traffic card shows GA4 traffic and engagement for the selected window.
- Source Health: This panel tells you whether the integrations are healthy, stale, blocked, or failed. Use it whenever you need to explain why a metric is zero or missing.

# Part 2: Part 2: Technical Deep Dive
This section explains how the report is assembled, what the live API returns, and how to read the payload without inventing new assumptions.

- Architecture: the dashboard is a static HTML and JavaScript SPA at reports.livetransparent.com. It calls the n8n executive summary proxy at `/api/report/executive/summary`, the outgoing-call proxy at `/api/report/executive/outgoing-calls`, and a separate campaign summary webhook at `/webhook/lt-report-campaign-channel-summary`; all render client-side. The public host serves build `2026-08-01-v12-campaign-breakdown` with the current campaign table, channel filters, and outgoing-call detail section.
- Request contract: the report reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query parameters. The current preset ranges are trailing complete days ending yesterday.
- Response shape: the API returns `summary`, `channelBreakdown`, `utmBreakdown`, `metaAttribution`, `contactSources`, `topPages`, `pipelineDropoff`, `stageDropoff`, `stageVelocity`, `appointments`, `health`, `linkedinFunnel`, `vapiCampaignBreakdown`, `vapiQueueDistribution`, `mqlSummary`, `sqlContacts`, `poolDistribution`, `emailsSent`, `emailsOpened`, `emailsClicked`, `emailsBounced`, `emailsUnsubscribed`, `emailsComplained`, `emailOpenRate`, `emailClickRate`, and `emailBounceRate`.
- Response shape: the API also returns the active-opportunity fields used by the report, including `activeOpportunityCount`, `workedOpportunityCount`, `stageMoverCount`, and `opportunityStageBreakdown`.
- Campaign response shape: the campaign summary returns `window` and `campaignChannelBreakdown` rows containing `channel`, `campaign`, SMS metrics, email metrics and rates, LinkedIn DM/reply metrics, and Vapi outcome metrics. DAN attribution uses release logs; Emerald uses bucket/enrollment data; Partnership uses `partnership_release_log`; SMS uses `campaign_key`; LinkedIn uses activity events joined to Brand/Dispensary source pools plus a zero-safe `Partnership LinkedIn` catalog row; and Vapi uses queue campaign IDs. Dynamic source campaigns remain visible as additional rows.
- Outgoing-call response shape: `/api/report/executive/outgoing-calls` returns `{ calls, total, limit, offset, range }`. Each call includes `call_id`, `contact_id`, `contact_name`, `contact_phone`, `number_name`, `started_at`, `ended_at`, `call_status`, `disposition`, `duration_seconds`, `recording_url`, `first_time`, and `marketing_campaign`. The n8n source is `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`), which queries `voice_call_attempt` joined to `voice_call_queue` and latest contact snapshots.
- Funnel basis: the primary funnel rates now use Users as the denominator where possible. This means the dashboard is treating unique visitors as the main traffic audience, not raw GA4 session counts.
- Source status: GSC Daily Ingest is active but currently blocked because its Google OAuth credential requires reconnection. Treat Search Console metrics as unavailable until a successful ingest execution is verified.
- Attribution logic: Acquisition Sources, UTM / Campaign Breakdown, and Attribution Coverage all depend on observed traffic and bridge data. They should be read as live data quality and attribution outputs, not as a perfect campaign registry.
- Operational rule: when a metric looks wrong, check Source Health first. The report separates stale data from business performance so the reader does not draw the wrong conclusion.
- Vapi campaign-gating note: the Executive Report currently shows downstream Vapi campaign outcomes and queue distribution, but not the upstream classifier's AI/domain acceptance counts. For classifier operations, use `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) execution summaries and the Postgres table `vapi_qualified_domains`.

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
| LinkedIn Funnel | Connection state distribution: ready, requested, connected, DM active, completed. | Tracks LinkedIn outreach pipeline health. |
| Vapi Campaigns | Voice AI call outcomes by campaign. | Shows answered rate, qualified calls, and booked meetings per campaign. |
| Vapi Queue | Pending outbound calls grouped by campaign. | Shows how many contacts are queued for each Vapi campaign. |
| Vapi Campaign Eligibility | Upstream Brand/Dispensary campaign-gating workflow. | Not currently returned as a dashboard metric; inspect n8n classifier executions and `vapi_qualified_domains` for selection, acceptance, writes, and domain-match activity. |
| MQL Summary | Active and total opportunities in the Warm pipeline Qualified (MQL) stage. | Tracks marketing-qualified lead volume. |
| AI Qualification | Janvi assessment outcomes for cannabis-business verification. | Distinguishes qualified, pending/unverified, and rejected contacts. Do not confuse this with the separate DeepSeek Vapi campaign-eligibility gate. |
| Sales Outreach Queue | Contacts/opportunities promoted after explicit AI cannabis qualification. | Measures SDR work-queue volume and owner assignment source. |
| SQL Contacts | Contacts with the SQL (Sales Qualified Lead) tag. | Counts contacts promoted to sales-qualified status. |
| Pool Distribution | Contact counts by pool tag (brands, dispensaries, Vapi campaigns). | Shows audience segment sizes. |
| Email Campaigns | Sent, opened, clicked, bounced, unsubscribed, and spam complaint counts. | Tracks email campaign performance across all senders. |
| Campaign Channels | Named campaign rows across email, LinkedIn, SMS, and Vapi. | Use this for cross-channel campaign comparisons; zero or null values can indicate missing source events rather than no business activity. |
| Email Rates | Open rate, click rate, and bounce rate. | Computed from email event metrics. |
| Meetings | Booked appointments or discovery calls in the selected window. | These are GHL appointments when available. |
| Calls | GHL conversation call logs and status breakdown. | Use this for answered, missed, voicemail, inbound, and outbound call activity. |
| Outgoing Call Detail | Vapi outbound call attempts from `voice_call_attempt` for the seven most recent completed days. | Use this for row-level disposition, timing, campaign, first-attempt, and recording review; it is not the aggregate GHL Calls panel. |
| Call Duration | Rounded seconds from `ended_at - started_at`; missing end time uses `started_at`. | A zero value can represent a call attempt with no elapsed provider duration, not necessarily a successful conversation. |
| First Time | True only when no earlier `voice_call_attempt` exists for the contact. | This is a database-history flag, not a selected-window-only flag. |
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
| SDR Owner View | The same opportunity payload shown as a deal-centred view. | Use this when the conversation is about individual owner or deal movement. |
| 7d / 30d / 90d | Trailing complete-day presets ending yesterday. | Example: if you click 7d on Tuesday, you see the previous Tuesday through Monday. |

# Part 3: How to Present the Report

- Contacts are not always created by forms. Routing, manual CRM entry, imports, and follow-up can also create contacts, which is why the contact count does not always line up with form submissions.
- The GA4 term `sessions` is not the same phrase everyone uses for website visits, so this report labels the metric `Recorded Visits` to make the meaning clear.
- The UTM breakdown is a view of what the data actually observed, not a master campaign catalog of everything ever created in GHL.
- Acquisition Sources is the contact-level section. It is the right place to go when the question is where contacts came from.
- Sales Team and SDR Owner View use the same opportunity payload. The difference is only the lens: one is the team view and the other is the deal-centred view.
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
| Add an owner filter if `SDR Owner View` is meant to show one rep's pipeline only. | Use the stable GHL user ID and preserve an explicit conflict/unassigned state. | No historical data changes. |
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

### Phase 5: Classifier workflow verification

Target workflow:
- `IduCoT5YOs0g2faT`

The workflow is already published. Do not apply the historical patch payload without first fetching live state.

Confirm the live version has the 15-minute Schedule Trigger, DeepSeek gate, qualified-domain table, live-phone fallback, and successful-write domain guard.

### Phase 6: Classifier execution

Run the classifier manually.

Expected result:
- at most 10 Brand + 10 Dispensary candidates selected per run
- accepted tags and domain persistence only follow successful GHL writes

Manual check:
- confirm new GHL tags were applied correctly

### Phase 7: Queue feeder verification

Workflow:
- `RFIZ9Bcfl3Yvms2b`

Action:
- run manually only when controlled verification is needed; the classifier is already scheduled
- verify queued results match accepted/tagged contacts

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
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), **DAN email campaign** (backfilled ghl_contact_id 2026-07-13, 5,373 eligible for dispatch), **Partnership Marketing pipeline** (activated 2026-07-31, 131 contacts, dual email+LinkedIn sequences, fully audited and deployed), **Apollo phone enrichment** (repaired 2026-07-14, new polling workflow), voice, reporting, LinkedIn outreach (canonical sender path and suppression guardrails hardened), the **LinkedIn/Instagram via Unipile -> GHL bidirectional conversation provider integration**, and the SimpleTexting SMS campaign stack (dispatcher live at low volume as of 2026-07-18).
- Social provider integration handoff: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Reporting implementation handoff: native GHL report `6a67dce4a51a4360c60963a3` plus the read-only Executive Report at `reports/embed/executive/index.html`. The public report host now serves build `2026-07-31-v10-partnership`.
- Reporting contract: use native GHL for CRM/email/SMS/call facts and custom metrics; use Social Planner for native social analytics; use the Executive Report for Brands-versus-Dispensaries joins, Unipile, Vapi, trigger-link detail, and cross-channel reporting.
- **Outgoing call detail (2026-08-06)**: the Executive Report now has a bottom row-level Vapi table backed by `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`). The report-host route `/api/report/executive/outgoing-calls` proxies to `/webhook/lt-report-outgoing-calls`; it is fixed to the seven most recent completed `America/Los_Angeles` days, capped at 100 rows per page, and reads `voice_call_attempt` + `voice_call_queue` with latest contact-snapshot enrichment. Aggregate GHL calls remain a separate status/outcome surface.
- Date contract: selected `from`/`to` windows are supported by the Executive Report and campaign summary endpoint. Every selected period must compare with the immediately preceding equal-length period, including absolute and percentage changes. Default weekly interpretation is Monday-Sunday in the reporting timezone.
- Native GHL limitation: the verified `GHL_PIT` provides valid REST access to the location and contacts endpoints, but the official API/SDK exposes no supported Custom Report widget-layout mutation and cannot replace the Firebase/browser report-builder session. Do not use undocumented endpoints or browser automation as a substitute without explicit approval.
- **Execution order (2026-07-30)**: deploy and verify the Executive Report; complete native GHL report configuration through an approved authenticated path; verify SimpleTexting live delivery; run controlled Brand/Dispensary Vapi checks; implement the deterministic Jason/Marc no-owner allocator; harden public webhook/secret boundaries; then finish the remaining reporting backlog.
- **Current blockers**: native GHL widget configuration still requires an approved working GHL report page/Firebase session or supported internal API path; the GHL PIT itself is valid for REST CRM access, with location and contacts checks returning HTTP 200, but cannot authenticate or mutate the browser report builder. GSC requires OAuth reconnection. SimpleTexting provider remediation is intentionally deferred per user instruction. Credential-bearing response captures must remain untracked. Partnership live outbound remains intentionally blocked by explicit launch approval, not by GHL contact API access.
- **n8n stale execution recovery (2026-08-05)**: the regular-mode n8n instance accumulated 6,946 `new` executions after the PostgreSQL outage/redeploy, including 1,915 SimpleTexting Step Runner, 1,905 SimpleTexting Phone Backfill, 788 Partnership Reply Poller, 396 Vapi Intake Poller, 386 LinkedIn Reply Backfill, 313 Vapi Dialer, and 261 Campaign Contact Classifier records. Follow `docs/n8n-stale-execution-recovery.md`; pause high-volume schedules, preserve recent webhook executions, remove stale scheduled records through n8n UI/API in batches, then add `N8N_CONCURRENCY=10` and re-enable workflows gradually. Do not delete execution rows directly in PostgreSQL.
- **n8n stale execution recovery completed 2026-08-05**: rebuilt the n8n PostgreSQL pool by restarting n8n, unpublished nine high-volume scheduled workflows, and deleted 6,964 stale `new` trigger executions through the supported execution API. No webhook executions were deleted and the current `new` count is zero. `N8N_CONCURRENCY=10` is staged in `n8n/docker-compose.yml` for the next Coolify redeploy. Re-enable schedules gradually; do not reactivate outbound workflows until controlled verification passes.
- **n8n gradual reactivation and optimization**: after redeploy, restore workflows in tiers from allocator/classifier to reply-state pollers, intake/enrichment, and finally outbound senders/dialer. Keep SimpleTexting paused during the provider HTTP 409 remediation. Optimize with bounded batches, no-work exits, atomic claims, watermarks, idempotency, and overlap guards. See `docs/n8n-stale-execution-recovery.md` for the exact sequence and stop conditions.
- **n8n reactivation result**: republished the seven non-SimpleTexting workflows after redeploy and verified matching active versions, HTTP 200 readiness, and zero `new` executions. SimpleTexting Step Runner and Phone Backfill remain unpublished until the account is re-enabled by SimpleTexting. No manual production runs were started.
- **Resolved 2026-07-30**: outbound dialer and Call Outcome Ingest crash fixes. Root causes: (1) GHL `Version` header `2023-02-21` rejected by the API (mandate is `2021-07-28`); (2) dialer loop guard read Postgres `RETURNING` columns that n8n's Postgres v2 node never delivers (only `{"success":true}` is visible); (3) empty-queue fetches produced phantom `GET /contacts/`→403 requests; (4) Call Outcome Ingest used invalid `new Date()` in `queryReplacement`. Fixes applied: Version header corrected on both dialer HTTP nodes, loop guard rewritten to read from Code-node item data, empty-queue guard added before GHL lookup, ingest expression fixed. All three workflows published and verified. Queue reset: 1,051 contacts (1,047 failed + 4 cooling_down) → `status='pending'`. End-to-end verification passed for a real GHL contact lookup.
- SimpleTexting provider handoff is live (2026-07-20). On 2026-07-24, fixed the campaign send boundary: use SimpleTexting `AUTO` mode for multi-segment messages, reclaim provider-failed idempotency claims, and mirror to GHL Conversations only after a real provider message ID. On 2026-07-29/30, published the bounded step runner and phone backfill, verified retry-safe `send_failed` state, captured provider HTTP 409 diagnostics, confirmed the token/sender/contact/opt-in through non-sending API checks, and published E.164 normalization. Live success remains blocked by provider-side message acceptance.
- Vapi Brand prompt/variable hardening completed 2026-07-25: removed the unresolved `{{company_name}}` opener dependency, added GHL `company_name` propagation through the outbound dialer, and tightened live prompt handling for missing variables, IVR/voicemail detection, one-question turn-taking, and stage directions. Brand assistant and dialer are live/published; callback execution `241581` confirmed successful voicemail outcome processing.
- Reporting and LinkedIn hardening completed 2026-07-31: GA4 `6pCSGzFmrMDFL5Yq` is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa` with explicit success/empty/partial/failed finalization, transactional health/run writes, stable named-dimension keys, and no watermark advancement on fetch failure. GA4 success execution `276731` and pinned failure execution `276747` passed. Sales `aYT5oHcgmBALzHy5` is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8` with ingest-date snapshots, cursor/retry guards, fail-closed writes, and `ghl_opportunities` source health; execution `276626` passed with 7,683 opportunities and 7,683 history rows. LinkedIn sync `ceaKnz6E3onQrZpt` and dispatcher `fXxw5lanZcDmUrst` remain published with bounded/atomic behavior and protected state-upsert headers. State upsert `Old7ZvyVYgFaJgDr` is published with terminal promotion, active-reply preservation, protected `httpHeaderAuth`, and a Community Edition `Config` node. All eight relevant workflows now have exactly one `Config` node and callers read `Config.stateUpsertSecret` instead of embedding the literal in request code. Unauthorized verification returned `403`; malformed authorized verification reached validation without writing state. Remaining security work is migrating other embedded GHL/Unipile API secrets to credentialed HTTP Request nodes or approved runtime configuration.

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
- **Outbound Dialer** (r7UjWLndmc6EqEUW): Active, native n8n Schedule Trigger every 2 minutes. Places calls via Vapi using campaign-specific assistants (Alex for brand, Jordan for dispensary). The timezone-aware business-hours guard is authoritative; no external cron is used.
- **Outbound Dialer queue loop**: After releasing a blocked, invalid, or outside-hours contact, the dialer immediately checks the next queue row in the same execution, capped at 25 queue checks. The live workflow is published and verified.

### Remaining Operational Items

- App reinstalled in Live Transparent with canonical SMS-type additional custom providers: LinkedIn `6a58a14ff3023bea3783c152`, Instagram `6a58a1193cdfc36997580a68`.
- Instagram GHL UI outbound reply and direct router smoke test both route to Unipile. Post-merge map repair points Instagram and LinkedIn social chats to canonical contact `XZ4yChllGBdcsVxhFRDe`.
- LinkedIn inbound under provider `6a58a14ff3023bea3783c152` is verified end-to-end; optional next check is a controlled LinkedIn GHL UI outbound reply from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Register/confirm Unipile Instagram inbound webhook points to `https://automations.livetransparent.com/webhook/lt-unipile-instagram-new-messages`.
- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Monitor the next real Instagram inbound after GHL duplicate cleanup; map rows are repaired, but avoid further artificial inbound replays unless needed because they create visible conversation messages.
- ~~Update `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) to apply canonical classification tags: `qualified` on regulated-business acceptance and `not qualified` on rejection, removing the opposite tag when reclassifying.~~ **Done 2026-07-30 — published active version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`.**
- ~~Update Vapi intake so raw pool tags cannot bypass classification; only `qualified` contacts with the required Warm opportunity may enter the Vapi path.~~ **Done 2026-07-30 — published active version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`.**
- ~~Update GHL promotion workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) so the destination is `Sales Outreach -> Qualified`.~~ **Done 2026-07-30 — GHL version 10 published; both opportunity actions target `Sales Outreach -> Qualified`.**
- ~~Implement the Jason/Marc no-owner allocator at Sales Outreach entry.~~ **Live 2026-07-30 — n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) runs every 30 minutes, selects open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, and assigns Jason/Marc by deterministic opportunity-ID hash. It writes only native opportunity ownership; the published GHL alignment workflow handles the contact and custom opportunity owner cascade.**
- Ownership audit result: the allocator assigns only the native opportunity owner, then lets the published GHL `LT - Opportunity Owner Alignment` workflow assign the contact and mirror the custom opportunity `Owner`. The staged n8n owner-sync workflow remains inactive.
- ~~Complete legacy-owner migration for open Sales Outreach opportunities whose custom `Owner` was John or Kevin.~~ **Done 2026-07-30 — authoritative opportunity search returned zero remaining John/Kevin custom-owner records; native ownership cascaded through the published GHL alignment workflow.**
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL. This remains a manual dashboard check because it cannot be safely simulated through n8n.
- Run a controlled live Brand and Dispensary call after the 2026-07-25 prompt/variable patch and verify no unresolved placeholders, no disclosure in voicemail, and one-question turn-taking.
- **SimpleTexting next step**: resolve the provider-side HTTP 409/account re-enablement through SimpleTexting support or an approved provider-console test. Until then, keep `LT - SimpleTexting Campaign Step Runner` (`dUyOfxllvkxZavaw`) and `LT - SimpleTexting Campaign Phone Backfill` (`8hQKQi1PooYDFxNR`) unpublished and do not force live sends. Before resuming, review the pool dispatcher, confirm a real provider message ID, validate `report_sms_sent.provider_response`, and confirm campaign advancement only after provider success.
- SimpleTexting GHL Conversations provider is LIVE: `SimpleTexting SMS` (`6a5b91913953360948dd59f1`) routes GHL outbound replies through the outbound router (`f4VoO1lBWkYRcQai`) → idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Outbound campaign sends mirror into GHL Conversations via `Q3Ivnwe4z2Y3cD7A`. Remaining: full E.164 normalization across delivery/unsubscribe workflows, STOP tag guard in outbound router.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- ~~Investigate Executive Report → Site Traffic → Top Page formatting/aggregation: the displayed page is showing the full email UTM URL instead of the expected normalized top-page label/path.~~ **Fixed locally 2026-07-30 — the Executive Report now strips host, query, fragment, session, and trigger-link parameters; deploy and verify through Coolify remains.**
- Complete the native GHL report configuration through an approved authenticated GHL UI/API path: MQL table, Brands/Dispensaries email widgets, open/click/response custom metrics, pipeline context, and shared date/comparison settings.
- **Add campaign-level reporting to the native GHL report and Executive Report.** The live endpoint now returns named channel/campaign rows, including zero-safe catalog rows for `General outbound`, `Partnership emails`, `xyz`, `abc`, and `Partnership LinkedIn`; the public Executive Report build `2026-07-31-v11-campaign-breakdown` renders All, Email, LinkedIn, SMS, and VAPI filters. Native GHL widget configuration remains a separate operational view; LinkedIn activity-ledger coverage is still pending for nonzero campaign activity. Do not stop at date-level totals. Define a canonical campaign dimension and show each campaign separately for the selected period and immediately preceding equal-length period.
  - Email campaigns: `New attribution model - brands`, `New attribution model - dispensaries`, `General outbound`, `Partnership emails`, and any additional active email campaign discovered from release logs, GHL workflow/sequence metadata, or event attribution.
  - LinkedIn campaigns: `New attribution model - brands`, `New attribution model - dispensaries`, and other named LinkedIn outreach campaigns, using Unipile/state activity where GHL-native data is unavailable.
  - SMS campaigns: each named campaign, including `xyz`, `abc`, and any current SimpleTexting campaign identifiers or template registries.
  - Required campaign metrics: sends, delivered/provider success, opens, clicks, replies, bounces, unsubscribes/complaints, calls or DMs where applicable, booked meetings, qualified outcomes, opportunities, and closed-won revenue.
  - Required dimensions: campaign, channel, audience (`Brands`/`Dispensaries` where applicable), source/medium, workflow or sequence, template/message key, sender/owner, and date window. Preserve unknown/unattributed values instead of silently dropping them.
  - Reconcile campaign totals to the corresponding overall channel totals and surface source-coverage gaps, especially historical email events and LinkedIn activity events.
  - **Tag attribution rules:** use queue/enrollment tags as campaign evidence, source-pool tags as audience evidence, and lifecycle/outcome tags only for status or conversion metrics. Do not treat `seq enrolled - dan`, `seq enrolled - emerald`, `simpletext_ongoing`, `simpletext_finished`, `simpletext_stop`, `linkedin_connected`, or `linkedin_dm_sequence_completed` as campaign names by themselves.
    - DAN: `Enrollment Queue - DAN - Brands` and `Enrollment Queue - DAN - Dispensaries` are definitive campaign triggers; `brands_pool` and `dispensaries_pool` are supporting audience/source tags. The `DAN_Release_Log.campaign` and `enrollment_tag` fields are preferred because queue tags may be removed after enrollment.
    - Emerald: the eight `Enrollment Queue - Emerald - {Executives,Marketing,Finance,Retail and Sales} {MSO,SSO}` tags and matching `Seq Emerald - ...` tags identify the campaign bucket. The source tags `cannabis-retail-{mso,sso}-{executive,marketing,finance}-1/2` are fallback routing evidence; generic `emerald` is insufficient. Prefer `Emerald_Campaign_Contacts.bucket`, `email_campaign`, and `Emerald_Release_Log.bucket` when available.
    - SMS: `sms_drip` identifies the eligibility pool, while `simpletext_start`, `simpletext_ongoing`, `simpletext_finished`, `simpletext_stop`, and `simpletext_sms_1` through `simpletext_sms_6` are lifecycle/template tags. Prefer `SimpleTexting_Campaign_State.campaign_key` and `SimpleTexting_Campaign_Event_Log.campaign_key`; `xyz`/`abc` must be registered campaign keys or explicit campaign tags before they are reported as named campaigns.
    - LinkedIn: current tags (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_queued`, `linkedin_dm_sequence_completed`, and `stop_linkedin_dms`) are lifecycle/suppression tags, not campaign identifiers. Use `emerging_pool_contacts.source_list` or historical `brands_pool`/`dispensaries_pool` observations as an audience fallback, then add a durable LinkedIn campaign key/tag at state enqueue for future exact attribution.
    - General outbound and Partnership emails: no reliable campaign-specific tag was found in the current runbooks/live workflow definitions. Report them as `unattributed` until a sequence/workflow/tag mapping is registered; do not infer them from generic engagement or completion tags.
- Add remaining spreadsheet-only metrics to the Executive Report: per-campaign rates, trigger-link views/clicks, Unipile LinkedIn campaign metrics, and social impressions/reach/clicks/top-post detail where the source API supports the selected period.
- ~~Publish selected-window metadata and derived email rates from `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`).~~ **Done 2026-07-30 — initial version `d9fdec1b-6fcb-4962-8d85-28a94f859370`; expanded named campaign/channel attribution published 2026-07-30 as version `64641979-71f3-466c-8a09-36013be6bc0e`; manual execution `276517` and live 7-day/30-day endpoint checks succeeded.**
- ~~Validate campaign email sent counts against DAN/Emerald release logs and `Email_Events`; zero sent with nonzero opened/clicked is a reporting defect, not a valid result.~~ **Checked 2026-07-30 — the selected 2026-07-20 to 2026-07-26 window has no `LT - Email Event Ingest` executions, so its zero engagement counts reflect missing historical event coverage. Later events are ingesting and aggregate correctly; retain this as a source-coverage limitation rather than altering the query.**
- Deploy the selected-period and campaign-channel Executive Report host change through the normal Coolify path, then verify the live build stamp, campaign table, selected-period controls, prior-period comparison, and both historical/current API windows.
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state sync after the fail-closed patch.
- Monitor the dialer's same-run queue loop and confirm eligible contacts are reached without exceeding the 25-contact safety cap.
~~- Verify one controlled production call using the rotated GHL PIT; manual dialer smoke execution `242609` already succeeded.~~ **Done 2026-07-30 — full audit of all 67 active workflows confirmed old PIT purged. Intake Poller and Dialer Config nodes updated and published.**
- Configure and enforce Vapi callback/server authentication before accepting forged tool or outcome requests.
- Audit and authenticate public Warm intake and SimpleTexting send webhooks whose shared-secret configuration is empty.
- Migrate active n8n Config-node secrets into credentials/protected runtime configuration and rotate exposed values.
- Add provider call ID/idempotency persistence and stale-lock reconciliation to the voice queue.
- Normalize contact owner, opportunity native owner, custom opportunity `Owner`, owner conflict, and canonical SDR identity for reporting.

### Marc Coetzee Sales Rep Onboarding Plan (Planning Only)

The reusable multi-SDR design contract is documented in [docs/strategy/sdr-registry-and-routing-contract.md](./docs/strategy/sdr-registry-and-routing-contract.md). Do not activate a new allocator until the live qualification and Sales Outreach promotion contract is confirmed.

New sales rep:
- Name: Marc Coetzee
- Email: marc@livetransparent.com
- GHL user ID: `sqGx5rp3oAUG610NXyjU`

Required pre-cutover cleanup for any future legacy-owner migration:

- Before enabling any Jason/Marc round-robin, identify any contacts currently owned by former staff using their live GHL user IDs. Do not infer user IDs from display names or historical records.
- Reassign those contacts to Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`) first, with a record-level audit of previous owner, new owner, timestamp, source, and reason.
- Preserve contact tags, custom fields, conversations, notes, tasks, DND/opt-out status, and existing attribution during the owner transfer.
- Inventory opportunities associated with those contacts separately. Do not silently change existing opportunity owners as part of the contact cleanup; apply the documented opportunity ownership and Sales-pipeline handoff rules deliberately.
- Verify the cleanup count before proceeding. No former-staff-owned contact should remain unless it is explicitly excluded and documented.
- This cleanup is separate from the qualification gate. Do not enable a new allocator or make Warm assignments until the Janvi gate and Sales Outreach boundary are implemented.

The 2026-07-30 migration is complete. The initial audit identified 307 open Sales Outreach opportunities with custom owner John or Kevin (305 John, 2 Kevin); the final authoritative search found zero remaining records. The migration changed native opportunity ownership and allowed the published GHL alignment workflow to cascade contact ownership and the custom opportunity `Owner`; no direct duplicate writer was activated.

Allocator rollout note (2026-07-30): the first controlled run assigned 73 previously unowned Qualified opportunities successfully. A live verification confirmed native opportunity owner, contact owner, and custom opportunity `Owner` agree for Jason and Marc. The remaining unowned Qualified backlog is processed in bounded batches by the active allocator; do not manually assign records while the backlog drains.

Before executing any live changes, audit and map every Jason-specific reference across GHL and n8n:

- Workflow names and descriptions that identify Jason, including `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`).
- Contact owner assignment paths and opportunity owner assignment paths; confirm whether each path uses a GHL user ID, a custom field, a round-robin rule, or a hardcoded name.
- GHL email templates, HTML signatures, sender addresses, reply-from values, and any sequence/template folder naming that is Jason-specific.
- Current live Jason-specific GHL templates identified: `Jason - 01` (`69e0d86b9af59801b580f4b5`), `Jason - 02` (`69e0db27d6a707bbf190d022`), `Jason - 03` (`69e0db9ab02114c1ba3c29d3`), `Jason - 04` (`69e0dc56d6a707c0ac90e074`), `Jason - 05` (`69e0dcad8ffabf47b4d987c5`), and `Jason - 06` (`69e0ddd0b021145bab3c4569`). All require backup and a decision between Marc-specific copies versus shared rep-merge templates.
- `Jason - 04 - Appropriate Marketing Contact` currently contains a stale `Best, John` signature and must be corrected during the template audit, regardless of whether it becomes a Marc copy.
- SMS template registries and GHL SMS workflow payloads, including preserved legacy keys such as `john_sms1` through `john_sms5`; do not rename keys without mapping review.
- Vapi assistant `firstMessage`, prompt identity, transfer language, metadata, notes, and any campaign-specific sales-rep references.
- GHL automations and micro-workflows that assign contacts or opportunities after opens, clicks, replies, deck downloads, bookings, or other engagement events.
- Previously documented Jason-specific GHL workflow references: `Jason Followup Emails and SMS` (`f6b44e34`, verified v39, 2026-07-30) and `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`, pending re-fetch and verification).

Required routing change:

- Update `WL - Micro - Email Open Counter + Assignment to Jason` so email opens remain an engagement signal only and do not independently assign an SDR or promote a Warm record.
- Apply Jason/Marc ownership resolution only when Janvi-qualified promotion enters `Sales Outreach -> New`.
- Define the exact balancing rule before implementation, preferably deterministic round-robin or an equivalent 50/50 rule that remains stable across retries and does not repeatedly reassign the same contact.
- Verify the promotion automation's contact-owner and opportunity-owner effects separately; changing one must not be assumed to change the other.
- Preserve existing open-count, tagging, notification, and deduplication behavior.
- For `WL - Micro - Email Open Counter + Assignment to Jason`, preserve the open counter, tagging, notification, and engagement thresholds while removing direct owner/opportunity assignment from the open-event path.

Canonical SDR Routing Contract:

- Create or confirm one authoritative assignment decision for every new qualifying contact. Do not let email opens, SMS sends, Vapi calls, LinkedIn replies, bookings, and opportunity creation independently choose an SDR.
- Use a deterministic 50/50 allocator, preferably a transactional round-robin counter or a contact-ID hash with an explicit tie-break rule. Random assignment is not acceptable because retries can change owners and make the split unverifiable.
- Persist the decision on the contact before any outbound message is sent, and treat the assignment as sticky. Retries, webhook replays, sequence steps, and later engagement events must reuse the existing SDR.
- Store both the GHL user ID and the rep identity needed by outbound channels. At minimum verify fields for `sdr_user_id`, `sdr_name`, `sdr_email`, `sdr_phone`, `sdr_signature`, `sdr_vapi_assistant_id`, and `sdr_calendar_id` or an equivalent canonical mapping.
- Define behavior for contacts that already have an owner, are already assigned to Jason, are assigned to another team member, or have conflicting owner/custom-field values. Do not silently overwrite existing non-SDR ownership.
- Precedence rule: former Kevin/John-owned contacts are migrated to Jason before round-robin assignment. Existing contacts owned by active staff remain unchanged unless separately approved.
- Define the cutover scope: new contacts only, or a controlled rebalance/backfill of existing Jason-owned contacts. If rebalancing existing contacts is requested, preserve active conversations, booked meetings, opt-outs, and opportunity history.
- Make the assignment idempotent using contact ID plus a routing version/cutover marker. A duplicate event must return the prior assignment rather than consume the next round-robin slot.
- Add a routing audit trail containing contact ID, previous owner, assigned SDR, assignment timestamp, trigger/source, routing version, and idempotency key.
- Ownership rule: the canonical assigned SDR must own the contact and every newly created opportunity for that contact while the opportunity is in pre-sales/outreach stages.
- Sales handoff rule: when the opportunity moves into the `Sales` pipeline (`MThKauqlvnEFuFmAkyWX`), transfer the opportunity owner to Cameron. Do not transfer the contact owner unless separately approved; the contact should remain owned by its assigned SDR for relationship continuity.
- Define the exact Sales-pipeline handoff trigger, including whether it fires on pipeline ID change, opportunity creation directly in Sales, or both. The handoff must be idempotent and must not revert the opportunity to the SDR on later contact updates.
- Cameron's live GHL user ID is confirmed as `03p5GatJBH7i9zjMaIzm`; use the user ID rather than a display name in the Sales-pipeline opportunity handoff.

Assignment Surfaces To Audit And Update:

- `WL - Micro - Email Open Counter + Assignment to Jason` (`42aa5940`): email-open threshold, contact owner action, opportunity owner action, assignment state, retry/replay behavior, and notification recipient.
- `Jason Followup Emails and SMS` (`f6b44e34`): all email/SMS actions, owner fields, sender fields, transfer/notification recipients, and legacy John/Jason names. **Completed (2026-07-29), re-audited (2026-07-30)** — all 7 Send Email actions confirmed with `{{opportunity.owner}} from Transparent eCom` + `{{user.email}}`; workflow defaults `Jason from Transparent eCom` / `jason@livetransparent.com` confirmed via `senderAddress` API field; published v39. Six templates (one reused by 2 actions) with literal Jason fallback. 14 SMS follow-ups via `john_sms1`–`john_sms5` (not owner-routed). Marc path (`sqGx5rp3oAUG610NXyjU`) is configured but untested — zero Marc-owned opportunities have entered a trigger stage (New, 1st/2nd/3rd Attempt, Engaged).
- Warm intake workflows for email inbound, email outbound, and SMS: `SmMf8QIfysuxQJbG`, `J4B0n0QeSeOeqAci`, and `5nYzp9DgQUopzWhR`. Confirm they only tag/intake contacts or whether they also assign owners.
- Email enrollment and stop workflows for DAN and Emerald: sender selection, owner persistence, reply/booked stop logic, and any GHL sequence action that assigns or notifies Jason.
- Vapi intake, queue, dialer, callback, and tool paths: `bYk1Ai6MJLyhTsDZ`, `XzcpOBi9YcIhJPck`, `r7UjWLndmc6EqEUW`, and `fx4UvKUWbqJEY3LK`. Carry the canonical SDR identity through queue metadata, Vapi variables, notes, callbacks, Slack alerts, transfers, and bookings.
- SimpleTexting campaign and provider paths: `usxYXSuc4ahw40V3`, `7mSiivR3NhtLIcNz`, `Q3Ivnwe4z2Y3cD7A`, `gwaEpWDpTIwsafi8`, and `f4VoO1lBWkYRcQai`. Confirm campaign template selection, sender identity, conversation mirroring, inbound reply routing, and `externalId`/idempotency keys include the assigned SDR where required.
- LinkedIn/Instagram inbound and outbound provider paths: preserve the assigned SDR on the contact and route replies/notifications to that SDR without changing the shared Unipile transport or conversation-provider IDs.
- Appointment, booking, opportunity, and post-booking workflows: assign the opportunity and appointment owner consistently with the sticky contact SDR, while preserving any separate fulfillment/calendar owner rules.
- Opportunity lifecycle: verify SDR ownership at opportunity creation, retain SDR ownership through pre-sales stages, transfer only the opportunity to Cameron on entry to the Sales pipeline, and preserve the assigned SDR in contact/custom-field/audit metadata.
- Reporting and attribution: include SDR/owner identity in release logs, email events, SMS events, Vapi attempts, opportunities, appointments, and dashboards so the 50/50 result can be measured independently of sender address.

### Revised Qualification and SDR Work Queue Model

- Warm is the unassigned intake and regulated-business classification layer. Contacts receive `qualified` when their business is related to a regulated vertical, or `not qualified` when it is not.
- `qualified` is the regulated-business classification gate and routes the opportunity into `Sales Outreach -> Qualified`.
- SDR allocation occurs at the Sales Outreach promotion boundary, not during Warm intake, email opens, SMS sends, Vapi queueing, or other channel micro-automations.
- When a contact enters Sales Outreach, resolve ownership in this order:
  1. If exactly one of the contact or opportunity has an owner, align the other record to that owner.
  2. If both have the same owner, preserve the assignment.
  3. If both have different owners, flag an ownership conflict for review and do not overwrite automatically.
  4. If neither has an owner, assign Jason or Marc with the deterministic 50/50 allocator.
- Every Sales Outreach assignment must keep contact `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned through the canonical SDR mapping.
- SDRs work from Sales Outreach. Warm contacts are not part of the normal SDR work queue.
- Vapi remains in Warm and must not call contacts tagged `not qualified` or contacts that have bypassed the canonical classification result.
- The existing GHL promotion workflow should use the canonical `qualified` result to route the opportunity to `Sales Outreach -> Qualified`, while `not qualified` blocks promotion.
- A Vapi warm transfer is an exception path: if an SDR answers the shared transfer number, the SDR manually claims the contact and opportunity and promotes the record into `Sales Outreach -> New`.
- Vapi warm transfer uses the shared SDR number through the Vapi `transferCall` tool; it does not select Jason or Marc by phone number.
- Vapi booking remains separate from transfer and uses Cameron's `Regulated Ads On Social/Search` calendar (`SrtXcFVyea7pFl3nTiIK`).
- The authoritative classification contract is now the `qualified` / `not qualified` tag pair. The live classifier currently needs a write-path patch to apply both outcomes; its campaign tags remain downstream campaign labels.

Rep-Specific Message And Channel Configuration:

- Email: decide whether to create Marc copies of the six Jason templates or convert them to shared templates driven by SDR merge fields. Update subject/preheader/body signatures, sender/from/reply-to, meeting links, phone numbers, template names/folders, and any GHL sequence references. Correct the stale `Best, John` in Jason Template 04 before reuse.
- Email: ensure a sequence step cannot send Jason copy from a Marc-owned contact or vice versa. Add a pre-send identity check and fail closed when the SDR mapping is missing or invalid.
- SMS: add Marc message variants or a rep-aware template registry. Preserve `john_sms1` through `john_sms5` only as historical compatibility keys, and define new keys/mappings rather than changing keys referenced by live GHL automations without a migration map.
- SMS: make the selected message, sender label, conversation mirror, reply notification, and idempotency/external ID use the assigned SDR. Confirm STOP, DND, and reply suppression remain global and are not weakened by routing branches.
- Vapi: document the mapping from SDR to assistant identity, first message, system-prompt name, transfer target, calendar, meeting link, phone number, callback metadata, GHL note signature, and Slack notification destination. Do not rely on a generic campaign assistant ID if the spoken rep identity must vary.
- Vapi: pass the SDR identity in `assistantOverrides.variableValues` and metadata, guard against missing/unresolved placeholders, and ensure the callback uses the same owner for notes, outcomes, booking, and follow-up.
- Vapi: keep warm transfer and booking separate. The Vapi `transferCall` tool uses the shared SDR number; the booking tools use Cameron's Regulated Ads calendar. Vapi should refer to the receiving SDR team/Sales Lead without naming Cameron for transfers.
- Vapi: completed 2026-07-25. Updated live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants to neutral Sales Lead wording. Preserved compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- Manual operator sends: update the SimpleTexting/GHL manual-send contract so an operator can send as the assigned SDR without allowing an arbitrary sender override that breaks ownership or auditability.

Equal-Split Validation And Monitoring:

- Build a controlled test matrix covering new contact, email open threshold, SMS send, SMS reply, Vapi call, Vapi callback, inbound email reply, LinkedIn/Instagram reply, deck download, booked appointment, opportunity creation, duplicate webhook, and replayed webhook.
- For every test, verify the same SDR remains on the contact, opportunity, appointment/follow-up task, outbound sender, signature, Vapi variables, CRM note, notification, and report record.
- Add qualification-gate tests for AI-qualified cannabis, AI-rejected/non-cannabis, AI-pending/unverified, duplicate assessment, and Vapi warm-transfer claim.
- Add Sales Outreach ownership tests for contact-only owner, opportunity-only owner, matching owners, conflicting owners, and both records unassigned.
- Include an opportunity lifecycle test: create an opportunity from a Jason-owned contact and a Marc-owned contact, verify the opportunity initially matches the contact owner, move each into the Sales pipeline, verify only the opportunity owner changes to Cameron, and confirm subsequent contact updates do not undo the handoff.
- Verify at least 20 fresh test contacts produce a 10/10 Jason/Marc distribution, or the documented deterministic equivalent, without duplicate assignment on retries.
- Add monitoring for assignment counts, unassigned contacts, invalid SDR mappings, reassignment events, sender/owner mismatches, and failed Vapi/email/SMS identity resolution.
- Add a rollback plan for routing rules, templates, sender mappings, and ownership fields. Backups must be taken before changing GHL workflows or email template HTML.

Implementation order after plan approval:

1. Resolve Kevin's and John's live GHL user IDs and inventory all contacts and associated opportunities they currently own.
2. Back up the affected contact ownership records and transfer former Kevin/John-owned contacts to Jason; verify the complete migration before continuing.
3. Confirm Marc's GHL user record, permissions, email identity, calendar/meeting routing, and any required Vapi or sending-account access.
4. Fetch current live GHL workflow definitions and all referenced n8n workflow versions before editing.
5. Back up every affected GHL email template and record current sender/signature values.
  6. Identify Janvi's authoritative AI assessment field/tag and implement the AI-qualified-cannabis -> Sales Outreach New gate. Apply the canonical ownership alignment/50/50 fallback at that boundary, then update Marc-specific copies/templates and sender identity.
7. Run the controlled routing and channel test matrix before enabling production traffic.
8. Publish changed workflows and verify contact owner, opportunity owner, Sales-pipeline Cameron handoff, sender, signature, SMS, and Vapi behavior with controlled test records.
9. Verify no Jason-only or stale John-branded references remain in active production paths, while preserving intentional legacy template keys and historical reporting identifiers.
10. Monitor the first production assignment batch and confirm the measured Jason/Marc distribution, sticky ownership, and zero sender/owner mismatches.

### Completed

- **2026-07-30**: Repaired outbound dialer and Call Outcome Ingest after prolonged outage. Fixed GHL `Version` header (`2023-02-21`→`2021-07-28`), rewrote loop guard to read from Code-node items (Postgres `RETURNING` invisible to n8n Postgres v2), added empty-queue guard before GHL lookup, and removed invalid `new Date()` from ingest `queryReplacement`. Reset 1,051 contacts to pending. Verified end-to-end GHL lookup succeeds. All three workflows published.

- **2026-07-25**: Gap audit hardened the live voice path: silent human answers no longer receive `qualified_booked`/`vapi_qualified`; the dialer fails closed on GHL `401/403`, uses 9am-5pm CT global hours, and the intake poller rejects unknown campaign tags while cleaning the actual source tag.
- **2026-07-25**: Reconnected the six-hour Schedule Trigger paths for `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) and `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`). Both were published and manual executions `242576` and `242577` succeeded.
- **2026-07-25**: Unpublished superseded Apollo Sheet First webhook `WmKAhG7mIaXonNsh` after confirming zero executions; canonical polling `JH8ShfpglWmLMZ3l` remains active.

- **2026-07-25**: Neutralized live Vapi transfer and voicemail language across the transfer tool and Savannah/Alex/Jordan assistants. Human-facing copy no longer names Jason or John; the compatibility function name and shared destination remain unchanged.
- **2026-07-25**: Disabled the hardcoded Kevin follow-up task in live RB2B workflow `3kjsIUeoEQFx26cC`. Warm intake now persists the contact/lead and returns without creating an SDR task; the legacy task node remains disconnected for future owner-resolved Sales Outreach use.

- **2026-07-24**: Fixed SimpleTexting campaign delivery. `LT - SMS Idempotent Send` now sends multi-segment messages with `AUTO`, records provider errors without crashing, and reclaims failed claims. `LT - SimpleTexting SMS Send (Webhook, Staged)` now gates GHL mirroring on a real provider message ID. Published both workflows and passed safe simulation executions `241272` and `241275`. Live provider confirmation is explicitly queued for the next dispatcher run.
- **2026-07-26**: Refreshed the live SimpleTexting template registry in `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). Updated `sms_1`, `sms_3`, and `sms_5` with clearer copy and selective `https://livetransparent.com/` references; preserved `sms_2`, `sms_4`, and `sms_6`, plus legacy `john_sms*` payload aliases. Republished and verified the workflow's draft and active versions match.

- **2026-07-25**: Audited Vapi callback execution `241579` and its successful end-of-call follow-up `241581`. Fixed the Brand assistant opener and system prompt, added `company_name` extraction/propagation in the outbound dialer, and published/verified dialer version `b3c80814-d7f0-442b-b5d2-f350377a0f2c` as active.
- **2026-07-25**: Recovered n8n from 745 orphaned queued `new` executions that were producing “Starting soon” records and competing recovery messages. Preserved legitimate `waiting` executions, republished the Vapi dialer, and verified the native trigger and manual execution path.
- **2026-07-25**: Updated `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) to continue within the same execution after blocked/invalid/outside-hours contacts are released. Added a 25-contact loop cap, published the workflow, and verified it reaches different queue contacts.

- **2026-07-20**: SimpleTexting GHL Conversations bidirectional provider is LIVE. Separate `LiveTransparent SimpleTexting SMS` GHL app with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Built `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) at `/webhook/lt-simpletexting-provider-outbound` — validates provider, E.164-normalizes phone, routes through idempotent send to SimpleTexting. Patched `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) to post inbound messages to GHL Conversations under `SimpleTexting SMS` with `type: "Custom"` + `conversationProviderId` (Slack alert preserved). Patched `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) to mirror outbound campaign sends into GHL Conversations. Created `simpletexting_conversation_map` table in Postgres. First end-to-end test passed: GHL → outbound router → idempotent send → SimpleTexting (201, message `6a5e46218ebb0860da623b0f`). Remaining: full E.164 normalization across delivery/unsubscribe workflows.
- **2026-07-16**: Verified the GHL Custom Conversation Provider bridge for Instagram and LinkedIn via Unipile using canonical SMS-type custom providers. Inbound uses `type: "Custom"` + `conversationProviderId` + `altId` with no dummy phone/email fields. `LT - Instagram Unipile New Messages` and `LT - LinkedIn Unipile New Messages` are active and published; LinkedIn replay verified `TYPE_CUSTOM_PROVIDER_SMS` on contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`. GHL duplicate cleanup consolidated Edmundo Cadorniga to `XZ4yChllGBdcsVxhFRDe`; Instagram map row `1` and LinkedIn map row `2` were repointed there. Direct outbound router checks passed for Instagram and LinkedIn. Full handoff in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **2026-07-16**: Cleaned up duplicate LinkedIn sender paths. Traced malformed LinkedIn screenshot DMs to misconfigured `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`), which used the LinkedIn Unipile account ID and `instagram_dm_state`; unpublished it. Also unpublished redundant `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`). Production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.
- **2026-07-15**: Built and published automated LinkedIn DM suppression workflow (`LT - LinkedIn DM Suppression from GHL Tag`, IPN8jnR3XSurX0o1). GHL tag `stop_linkedin_dms` triggers a GHL automation → POSTs to `/webhook/lt-linkedin-suppress-dms` → resolves LinkedIn profile via Unipile, tags `linkedin_dm_sequence_completed`, upserts `linkedin_connection_state` to terminal for both real contact and synthetic `linkedin:follower:{providerId}`. Full audit confirmed all 3 send paths (DM Sequence, Follower DM, Dispatcher) correctly block suppressed contacts. Fixed dispatcher Feeder gap: added `linkedin_dm_sequence_completed` to blocking tag list.
- **2026-07-15**: Unicode/mojibake encoding fix expanded across all audited Unipile message sender nodes: LinkedIn DM Sequence (`Sync Connected from Unipile`, `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. Templates are pre-sanitized at runtime and final outbound text is sanitized immediately before Unipile API calls. Handles smart punctuation plus already-garbled forms like `canâ€™t` / `canΓÇÖt`. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.
- **2026-07-14**: Vapi voice system activated. Published Intake Poller + Outbound Dialer. Fixed Trigger Apollo Enrichment auth and Remove Tag - Enriching URL. Added pagination, 30-contact cap, brands_pool/dispensaries_pool tag search, and tag rotation. Added state-to-timezone inference for both poller and dialer. Historical dialer cron was shifted to `*/2 13-22` UTC for 9am ET start; the current implementation uses a native two-minute Schedule Trigger and the timezone-aware business-hours guard remains authoritative.
- **2026-07-14**: Apollo phone enrichment repaired. Created and published LT - Apollo Phone Enrichment Polling (JH8ShfpglWmLMZ3l, every 30 min). Replaces dead webhook-based pipeline. Syncs profile data immediately, requests phone numbers via async callback to V4 handler.
- **2026-07-13**: Backfilled 13,705 ghl_contact_id values into emerging_pool_contacts from GHL export CSVs (email + phone + name/company match). DAN dispatcher now has 5,373 eligible contacts.

- **2026-07-20 - Voice Assistant Optimization (all 3 outbound assistants + dialer)**:
  - **Jordan (Dispensary, 056f2e50)**: 8 system prompt fixes + 2 config fixes from live call audit. Removed compliance disclosure from firstMessage (voicemail fix). Fixed {{contact_name}}->{{first_name}} (n8n passes first_name not contact_name). Removed unmet {{market}} variable. Changed "with"->"from" Transparent eCom (Nico TTS inserted "a"). Discovery questions restructured to one-at-a-time with numbered Q1-Q4 + WAIT instructions. Added [IVR vs Voicemail Detection] disambiguation section. Tightened "um/uh" to once per call max. Added [Pronunciation] rules: "Point of Sale" not "POS", "from" not "with". Expanded [No Stage Directions] to ban throat-clearing/coughing/sighing. [Turn-Taking] strengthened to CRITICAL with self-check. Transcriber smartFormat enabled. Model tested Llama 3.3 70B then reverted to Claude 3 Haiku (system prompt preserved through model swap).
  - **Alex (Brand, 1d7c5d42)**: Same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and {{contact_name}}->{{first_name}} fixes. Brand-specific questions preserved.
  - **Savannah (V1 Outbound, 3f9bbfd2)**: Same IVR/voicemail disambiguation, stage directions, and {{contact_name}}->{{first_name}} fixes. First message already clean.
   - **Outbound Dialer (r7UjWLndmc6EqEUW)**: Stuck contact AX3wfQNpRwm6DG0HgUE2 (deleted from GHL, 2 entries in voice_call_queue) blocked every run since 18:38 UTC. HTTP - Get GHL Contact had neverError: false - 400 crashed run before lock release. Same contact re-picked every 2 min. Fix: neverError: true on lookup node; onError: continueRegularOutput on GHL - Create Call Note. Calls resumed by 18:50 UTC. Intake poller unaffected throughout.

- **2026-07-23 - Vapi and n8n production hardening**:
  - Standardized documentation on n8n `2.33.3` and native Schedule Triggers.
  - Kept the callback-to-dequeue path removed and `LT - Voice Dequeue Next` unpublished.
  - Added callback timer deduplication plus 30-minute static-state pruning.
  - Added queue enqueue authentication with `X-LT-Voice-Queue-Secret` and `VOICE_QUEUE_ENQUEUE_SECRET`.
  - Added Apollo asynchronous phone-request failure telemetry.
  - Reconnected timeout-reaper Slack summaries and removed the stale outcome-webhook response option.
  - Verified changed workflows are published and smoke-tested authenticated and unauthenticated enqueue behavior.

- **2026-07-31 — Partnership Marketing pipeline activated and fully audited**: 131 content partnership contacts imported into GHL (98 email + 33 LinkedIn-only) from two CSV lists, deduplicated/cleaned by `scripts/clean_partnership_data.py`. Built 7 n8n workflows: Email Dispatcher (`Xshck23cKo1yXL9D`, 60/day 11am ET), LinkedIn Dispatcher (`crKIsaL5k3YBfqDZ`, 30/day 3pm CT), LinkedIn DM Sequence (`nspggypNF245xzeL`), Reply Handler (`mRDw57IHtnQe4wOo`, webhook), Reply Poller (`0SQ7tTk03okegp9V`, every 5 min), Bulk Import (`zmrYrUjVcyXaS7PJ`), and LinkedIn URL Update (`ew6uQQnAjgCbjeGn`). Created GHL Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages. Created 4 GHL email templates in folder `6a6b768aa43d24a7ce1514f1` with HTML content via PATCH API. Patched 3 existing LinkedIn workflows (Acceptance Checker `3ttEvr5NMcQCS4Hp`, Reply Backfill `QfJ2EZcc7lZwNgxj`, Unipile New Messages `7o5EBdvwAuIaWW7k`) to also query `partnership_linkedin_connection_state`. All infrastructure isolated from DAN/Emerald pipelines (separate Postgres tables, separate state tracking).
- **2026-07-31 — Partnership reporting integration**: Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL updated with `partnership_release_log` UNION ALL in `email_sent` CTE (published version `6641aa9a`). Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped via `postgres/partnership-bootstrap.sql`. Executive Report frontend deployed as build `2026-07-31-v10-partnership` to reports.livetransparent.com with updated footer note. Full audit completed: 7 partnership workflows confirmed published/active, 3 patched LinkedIn workflows verified with correct queries/routing, all 131 GHL contacts assigned to Janvi, email templates confirmed, pipeline confirmed, Campaign Channel Summary confirmed returning "Partnership emails" row, and the Executive Summary API includes partnership release/state data. Reply Poller version `04cf007e-0ed1-41c7-abf5-4d1174b4bc9f` now uses POST conversation lookup and fails closed; manual execution `277923` passed. Remaining: GHL Custom Report integration (browser-only), provider-side SimpleTexting HTTP 409, and 14 excluded contacts awaiting corrected company names.
- **2026-07-31 — Partnership state and dry-run remediation**: Replaced partnership candidate reads with supported paginated `GET /contacts/` and explicit failure handling. Added LinkedIn `Seed Partnership State`, which populated 127 `ready` rows from GHL LinkedIn-tagged contacts. Current live versions are Email Dispatcher `1b41ce9c-8a89-4e2f-b45c-81bce8bc3484`, LinkedIn Dispatcher `ef3f9aee-88c1-4d02-a40e-b74e8694b6b9`, LinkedIn DM Sequence `798b1c75-cf15-4e4e-9cf4-e3c9fd7b9d7c`, and Reply Poller `42fbe7fc-fffe-4784-a4a4-4187a385bd5b`; relevant outbound configs remain `defaultDryRun=true`. Dispatcher dry run `278203` planned 30 requests with 0 sent; DM dry run `278342` completed with no sends. Direct GHL PIT verification returned HTTP 200 for location and contacts endpoints. Remaining: explicit live launch approval, native GHL report-builder access/configuration, provider-side SimpleTexting HTTP 409, credential migration, and 14 excluded partnership contacts awaiting corrected company names.
- **2026-07-31 — Partnership live-state hardening**: Audited all 7 live workflows and corrected the three outbound schedules from hourly interval definitions to explicit weekday cron schedules: email `0 11 * * 1-5` America/New_York, LinkedIn `0 15 * * 1-5` America/Chicago, and LinkedIn DM `0 12 * * 1-5` America/Chicago. Fixed the DM sequence terminal completion query and the shared LinkedIn Acceptance Checker state-upsert header. Published versions are Email `ca59164e-b3d8-4e84-b8af-c843832d043a`, LinkedIn `31a83f80-6256-4a50-a690-aa666102c1d4`, DM `f37a01e2-5ce6-4ce7-9327-21f3510d99bc`, and Acceptance Checker `0d85599c-fc9a-4391-83b5-725da2d7f451`; smoke executions `281269`, `281268`, and `281270` succeeded. Outbound remains dry-run pending explicit authorization.
- **2026-07-31 — Partnership outbound activated**: After explicit user approval, set Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence `defaultDryRun=false`. Published and verified active versions: Email `6b7490a9-05d8-44e1-8f94-3c4427a7f969`, LinkedIn `29089175-1b37-4271-8b03-d4722b809692`, and DM `3bd0b759-4740-4e67-85ef-9540bf31c08e`. Scheduled production sending is now enabled; no unscheduled manual live execution was run.
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

### Qualification and SDR Boundary

- Warm is the unassigned intake and verification layer.
- The canonical classification tags are `qualified` for a regulated business, including nicotine, cannabis, CBD, vape, hemp, and related verticals, and `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate and routes qualified opportunities to `Sales Outreach -> Qualified`.
- SDR assignment happens only at Sales Outreach entry: align a single existing owner, preserve matching owners, flag conflicting owners, or assign Jason/Marc 50/50 when neither record has an owner.
- Contact native `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` must remain aligned.
- Vapi handles classified regulated-business contacts in Warm and excludes `not qualified` contacts. Raw pool tags must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR and promoted to Sales Outreach. Vapi booking remains on Cameron's Regulated Ads calendar.

### Scheduling Contract

- Recurring n8n workflows must use n8n's native `Schedule Trigger` node.
- Do not create OS, Coolify, or external cron jobs for workflow scheduling.
- The Vapi dialer runs from a two-minute Schedule Trigger and applies its timezone-aware business-hours guard before dispatching a call.
- `LT - Voice Dequeue Next` is an unpublished helper and must not be used as an automatic call-start path. Callback completion must not trigger another dequeue request.
- `LT - Voice Queue Enqueue` is authenticated with `X-LT-Voice-Queue-Secret` using the `VOICE_QUEUE_ENQUEUE_SECRET` deployment/reference value.
- Callback timer state is deduplicated within 60 seconds and pruned after 30 minutes.

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

- The current LinkedIn DM cadence is approximately day 0, day 3, day 7, and day 10, with terminal completion at day 14.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.
- If someone responds on LinkedIn, immediately suppress them from all remaining automated LinkedIn DMs and persist that suppression in the shared state.
- State sync must use bounded direct HTTP calls with explicit retry/error reporting; API failures must not be reported as an empty healthy scan.
- Connection dispatch must atomically claim a `ready` row before an invite and perform a live GHL suppression/reply check immediately before sending.
- The state-upsert boundary uses the protected n8n `httpHeaderAuth` credential `LT LinkedIn State Upsert Webhook` and requires `X-LT-LinkedIn-State-Secret`. Callers must send the shared header; do not reuse an unrelated webhook secret. In Community Edition, each relevant workflow stores `stateUpsertSecret` in its single `Config` node and Code nodes read that value instead of embedding the literal. The secret is not stored in the repository.

### Partnership LinkedIn State

- Partnership LinkedIn state is isolated in `partnership_linkedin_connection_state` with `source_key = 'partnership'`; it must not be conflated with the main `linkedin_connection_state` table.
- The partnership dispatcher seeds `ready` rows from GHL contacts tagged `partner_candidate_linkedin` before reading its ready queue. The 2026-07-31 seed produced 127 rows.
- Partnership Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence remain `defaultDryRun=true` until explicit live-launch approval. A successful dry run is not evidence that an email, invitation, or DM was sent.
- Before activation, verify GHL suppression/reply checks, state-upsert authentication, idempotent claims, release-log writes, and the exact active version. Do not activate a send-capable path merely because the PIT can read contacts.

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

Minimum live `voice_call_queue` fields:

`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

Injected Vapi variables:

`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

Planned qualification extension: add `ai_qualification_state` only after the authoritative qualification workflow and field/tag contract has been identified and migrated through the live queue, dialer, and callback paths.

Normalized callback output:

`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration

- Secrets: `GHL_PIT` aliased as `GHL_API_KEY`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- The root `GHL_PIT` was directly verified on 2026-07-31 against the official REST location and contacts endpoints with HTTP 200. PIT access confirms CRM/API access only; it does not authenticate the Firebase/browser session used by the native Custom Report builder.
- Native GHL Custom Report widget layout has no supported public API/SDK mutation surface. Use the authenticated GHL UI or an explicitly approved internal API path; do not infer report-builder access from successful PIT REST calls.
- Voice write actions: add `vapi_*` tags per outcome, create contact notes for completed calls

## Guardrails

- Do not call `dnc=true` contacts.
- Respect `attempt_count < max_attempts`.
- Enforce 72h cooldown between attempts.
- Call only Mon-Fri 9am-5pm CT.
- The native Schedule Trigger controls polling frequency; the workflow guard controls call eligibility.
- Fall back to GHL contact timezone when queue timezone is missing; use CT 12-2pm safe window if neither is available.
- Keep secrets in env/credentials; do not hardcode them in workflow JSON.
- Do not enqueue AI-qualified or explicitly rejected/non-cannabis contacts for Vapi. Vapi queue eligibility is limited to AI-pending/unverified Warm contacts.
- Keep Vapi warm transfer separate from Cameron calendar booking. Transfer uses the shared SDR number; booking uses Cameron's Regulated Ads calendar.
- Preserve n8n graph integrity when editing workflows.
- For social outreach, never send duplicate messages. Every send workflow must check and update shared state before and after send.
- For social outreach, reply-handling workflows must mark the contact as in conversation so follow-up sequences stop.
- For SMS, keep the batch size controlled until reply capture, opt-out propagation, and Slack alerts have all been verified live.

## Callback Tools

- `update_lead_status`: GHL tag plus Postgres disposition update.
- `add_to_dnc`: set `voice_call_queue.dnc=true` and add the GHL DNC tag.
- `log_call_outcome`: upsert `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales`: post lead name and summary into `#leads`.
- Vapi API-managed `transferCall`: warm-transfer to the shared SDR number using neutral Sales Lead language.

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
7. Confirm AI-qualified contacts are excluded from the Vapi queue and a successful warm transfer remains manually claimable by the answering SDR.

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

Updated: 2026-08-06 (Executive Report outgoing-call detail setup and documentation)

## Source Of Truth

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Executive Report response-rate + social-engagement fixes (2026-08-04)**: User reported that 1 LinkedIn partnership response and 1 email partnership response showed as 0 response rate, and that LinkedIn/email data for the 3 campaigns (New attribution model - brands, New attribution model - dispensaries, Partnerships) looked wrong. Root-cause investigation found 4 bugs, all fixed and published:
  1. **Reply Poller wrong HTTP method (CRITICAL)**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) called `POST /conversations/search` which returns 404; the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522221` now returns `errors: []` (was 59 errors). Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event (CRITICAL)**: `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack alert; it never wrote to `Email_Events`. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). The handler now also passes `email`/`event_ts` through. Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill one-shot (CRITICAL)**: `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows set to `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-selects rows whose last check is older than 6 hours and whose `dm_conversation_status <> 'active'`, so new replies are picked up. Published version `0620c314-befb-4620-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch**: The Executive Summary's `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but the social ingest stores `like`/`comment`/`share` (singular). Fixed the `Build Query` node to `COALESCE` both plural and singular keys. Verified live: `socialPosts` now shows `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  5. **Historical reply backfill completed**: Verified GHL/Unipile records for Strider Peterson's email reply and Jaret Christopher's LinkedIn reply were inserted idempotently. The email event uses the actual GHL inbound timestamp `2026-08-03T15:41:03Z`; the LinkedIn event uses the verified Unipile message timestamp `2026-08-01T03:05:55Z`. The temporary backfill workflows were archived after successful executions `522402` and `522416`.
  6. **Social metric fields expanded**: Executive Summary API version `a3e1660f-7bd3-4157-8e5c-b55e5d2aa923` and the deployed report build `2026-08-01-v12-campaign-breakdown` now expose likes, comments, shares, saves, reach, and impressions when present in the source payload. Current raw post ingest still reports 24 likes, 3 comments, 4 shares, and zero saves/reach/impressions.
  - **Reach/impressions/saves scheduled ingestion remains pending**: The official GHL Social Planner statistics endpoint returned 152 impressions and 61 reach for its current seven-day OAuth window, but n8n has no usable GHL OAuth credential and the PIT returns 401. Add OAuth-backed statistics ingestion before treating the zero fields as source totals.

- **Partnership LinkedIn reporting (2026-07-31)**: The Campaign Channel Summary now returns 10 durable, idempotent `connection_request_sent` events in the `Partnership LinkedIn` row for the verified execution `281366`. The live dispatcher records future successful invites after Unipile success and records provider/state-transition diagnostics without issuing any reporting-time outbound requests.

- **Voice stack**: ACTIVE since 2026-07-14, hardened 2026-07-16, optimized 2026-07-20, and call-path hardened 2026-07-23. All 3 outbound assistants (Jordan/Dispensary, Alex/Brand, Savannah/V1) updated: compliance disclosure removed from voicemail, discovery questions restructured to one-at-a-time with turn-taking enforcement, IVR/voicemail disambiguation added, stage-direction/throat-clearing ban, pronunciation fixes, `{{contact_name}}`→`{{first_name}}` variable corrected. On 2026-07-25, the Brand assistant and dialer were patched to remove the unresolved `{{company_name}}` opener dependency, pass `company_name` from GHL when available, and explicitly guard against missing placeholders. The dialer uses n8n's native Schedule Trigger every 2 minutes plus a timezone-aware business-hours guard; no external cron job is used. The callback webhook no longer automatically invokes the dequeue helper, and `LT - Voice Dequeue Next` is unpublished so it cannot start unscheduled calls. Callback metadata extraction, GHL note JSON handling, queue completion parameters, tag failure handling, and the 8-tag plus DNC suppression blocklist were hardened. The dialer now marks selected rows `in_progress` before the Vapi request, preventing ambiguous request failures from retrying the same contact; no-phone and outside-hours branches restore `pending`. Poller searches 4 tag pools with rotation, 30/cycle, and removes the source campaign tag after enqueueing. On 2026-07-25, the dialer was changed to continue fetching and filtering blocked/invalid contacts within the same execution, up to 25 queue checks, instead of waiting two minutes after every skipped contact. On 2026-07-30, the dialer and Call Outcome Ingest were repaired after a prolonged outage: GHL `Version` header corrected from `2023-02-21`→`2021-07-28`, the same-run loop guard was rewritten to read from Code-node items instead of invisible Postgres `RETURNING` columns, an empty-queue guard was added before GHL contact lookup, and the ingest workflow's `new Date()` expression was removed from the `queryReplacement` path. The 1,047 failed + 4 cooling_down queue rows were reset to `pending`, restoring 1,051 contacts to the active dialing pool.
- **n8n runtime**: upgraded to target `2.33.3`; redeployment of n8n and PostgreSQL is planned after the August 5 database connection-timeout incident. Native Schedule Trigger is the standard for recurring workflows. The Python task-runner warning during deployment is expected for JavaScript-only workflows; the stale queued-execution incident was resolved by deleting 745 orphaned `new` executions after the initial targeted cleanup, leaving legitimate `waiting` executions intact. The dialer was unpublished/republished, manually smoke-tested, and confirmed to select different queue contacts. It is active and published with the same-run queue loop.
- **n8n stale execution cleanup (2026-08-05)**: after the PostgreSQL/n8n redeploy, the database was healthy but `execution_entity` contained 6,946 `new` executions, 102 `crashed`, and 38 `error` records. The oldest `new` execution was from 2026-07-27. The largest backlogs were SimpleTexting Step Runner (1,915), SimpleTexting Phone Backfill (1,905), Partnership Reply Poller (788), Vapi Intake Poller (396), LinkedIn Reply Backfill (386), Vapi Dialer (313), and Campaign Contact Classifier (261). This is regular-mode stale scheduled execution state, not missing Queue Mode workers. Follow [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md): pause high-volume schedules, preserve recent webhook executions, delete stale scheduled `new` records through n8n UI/API in batches, then re-enable workflows gradually. Do not delete directly from PostgreSQL.
- **n8n stale execution cleanup completed (2026-08-05)**: n8n's PostgreSQL pool was rebuilt by restarting the n8n container, then nine high-volume scheduled workflows were unpublished. The supported n8n execution API deleted 6,964 stale `new` trigger executions with zero failures and preserved all webhook executions. The current `new` count is zero; 102 crashed and 38 error records remain as diagnostic history. The schedules remain paused pending controlled reactivation. `N8N_CONCURRENCY=10` is now staged in `n8n/docker-compose.yml` and will take effect on the next Coolify redeploy. See [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **n8n reactivation/optimization plan**: after the redeploy, reactivate the paused workflows in tiers: allocator/classifier, reply-state pollers, intake/enrichment, then outbound senders and dialer last. Keep SimpleTexting workflows paused until the provider HTTP 409 is resolved. Proposed improvements are bounded batches, cheap no-work exits, atomic claims/idempotency, watermarks instead of full scans, and overlap guards. Full gates and cadence proposals are documented in [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md); no workflow will be reactivated or modified until live state is fetched and verified after redeploy.
- **n8n reactivation completed with SimpleTexting excluded**: after redeploy, the seven non-SimpleTexting workflows were republished and verified with matching `versionId`/`activeVersionId`: Partnership Reply Poller, Vapi Intake Poller, LinkedIn Reply Backfill, Vapi Dialer, Campaign Contact Classifier, DAN Dispatcher, and Jason/Marc Allocator. SimpleTexting Step Runner and Phone Backfill remain inactive pending account re-enablement. Readiness is HTTP 200 and the current `new` execution count is zero. No manual production executions were started.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences. Reply suppression was repaired in GHL on 2026-07-26 after an inbound email continued into a later sequence step.
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (65/run every 30 min, 1,560/day capacity). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery.
- **Apollo phone enrichment**: ACTIVE and hardened 2026-07-16. Production path is polling + V4 callback + reaper. Legacy staged webhook orphans were canceled, poller now re-discovers `queued_phone`, callback provider failures map to `callback_failed`, and known blank contacts were backfilled into `queued_phone`.
- **LinkedIn**: Production path is dispatcher -> acceptance/state sync -> canonical 4-message DM sequence. Follower DM and misconfigured Instagram DM sender paths are unpublished. The dispatcher now explicitly reads Config, atomically claims `ready` rows as `requested_pending`, performs immediate GHL tag/reply checks, and fails closed on provider/state errors. State sync uses direct HTTP requests, bounded contact/API budgets, retries/timeouts, explicit error reporting, and preserves terminal/replied state. The shared state-upsert workflow promotes explicit terminal payloads to `completed` and preserves active replies. The state-upsert webhook now requires the protected `X-LT-LinkedIn-State-Secret` header; all discovered callers were updated and published, and unauthorized requests return `403`.
- **Instagram**: old DM Sequence is unpublished after it was found using the LinkedIn Unipile account. New inbound bridge is active and posts messages into GHL Conversations under `Instagram via Unipile`.
- **Social provider bridge**: Instagram and LinkedIn inbound both work through SMS-type custom conversation providers (`LinkedIn: 6a58a14ff3023bea3783c152`, `Instagram: 6a58a1193cdfc36997580a68`). Inbound uses `type: "Custom"`, not `SMS`, and avoids dummy phone/email data. GHL duplicate cleanup consolidated Edmundo Cadorniga to canonical contact `XZ4yChllGBdcsVxhFRDe`; both Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` now map there. GHL Conversations is the operator-facing inbox; no dedicated macro dashboard or alert digest is live yet. Detailed handoff and operator runbook live in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **Reporting**: GA4, GHL, and GSC ingestion are live. **Call reporting fix (2026-08-01)**: the Executive Report's `GHL Calls` panel undercounted calls because the `calls`/`call_status_breakdown` CTEs read `report_raw_ghl_calls`, which `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`) only populates by scanning 2 pages × 25 conversations where the last message is a call (85 calls in 30d). The authoritative `report_raw_ghl_call_outcomes` table is fed by the GHL Call Details webhook (`LT - Call Outcome Ingest`, `PUCfTZBANSPcgS0c`, 348 calls / 333 outbound in 30d). Both CTEs now read the webhook-fed outcomes table; verified live at Total 348 / Answered 261 / Missed 75 / Voicemail 11 / Inbound 14 / Outbound 333. **Channel/UTM attribution fix (2026-08-01)**: `report_channel_daily_summary` and `report_utm_daily_summary` each receive rows from two writers with incompatible keys — the GA4 Traffic Rollup Bridge (`0P2AZcQYWYZjXbRi`, GA4 sessions, `metadata.source='ga4_rollup_bridge'`) and Report Daily Rollups (`EUeOiRttoVLQ9zF9`, GHL contact/opportunity counts, `metadata.source_system='rollups'`). The API's `channels` and `utm_breakdown` CTEs previously grouped all rows by channel/source-medium-campaign and ordered by `sessions DESC`, so GHL-only rows (sessions=0) fell below the LIMIT and the UTM `leads`/`opportunities` columns were always 0. Both CTEs now FULL-JOIN the GA4 rows to the rollups rows on the shared key so each channel/UTM row shows traffic AND CRM outcomes, and channel names are normalized (`unattributed`/`Unassigned`/blank/`(none)`/`not set` → `Unassigned`). Verified live: channel breakdown now clean (Unassigned merges 155 sessions + 4,727 opps; Direct 403 sessions + 229 leads); named UTM campaigns (e.g. `wl_seq_cannabis_ads` 1,159 sessions) correctly show `leads=0` because GHL does not store UTM campaign fields on those contacts (confirmed against raw DB), while the 229 contacts that do carry UTM data land in the unknown bucket. The Executive Report is published on version `b5c67086`. GSC execution `281697` succeeded after OAuth renewal, fetched 10 rows for report date `2026-07-30`, upserted them, and finalized source health as `success`. `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on version `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`; it finalizes success, empty, partial, and failed fetch states, does not advance watermarks on fetch failure, and preserves raw-row idempotency. The reconnected GA4 credential was verified by execution `276731`; pinned failure execution `276747` confirmed health finalization followed by an intentional n8n error. `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`; it uses ingest-date snapshots, bounded cursor/retry guards, fail-closed finalization, and health key `ghl_opportunities` to avoid collision with leads. Execution `276626` processed 7,683 opportunities and 7,683 history rows successfully. The Executive Report is deployed as build `2026-07-31-v11-campaign-breakdown`; its campaign/channel table, selected-period comparison, and LinkedIn Invites/Accepted columns are live. After the live 10-contact Partnership LinkedIn test, the Executive Report shows 10 overall LinkedIn invites and attributes them to a `Partnership LinkedIn` campaign row via durable `connection_request_sent` ledger events. Native GHL report `6a67dce4a51a4360c60963a3` loads 11 widgets in an authenticated UI session. Its `Campaign Opportunities` widget is filtered to `Partnership Pipeline`, and its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`; the current 2026-07-19 through 2026-07-25 window showed zero/no data after filtering. Native GHL does not consume Unipile activity without explicit CRM synchronization. Detailed gaps and required report fields are documented in `docs/reports/Reporting Gaps and Requirements.md`.
- **Outgoing call detail (2026-08-06)**: Added and published `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`, version `d004556d-0b11-4a86-8827-f8f58a1eeee3`). Its GET webhook `/webhook/lt-report-outgoing-calls` returns up to 100 Vapi call rows from the seven most recent completed `America/Los_Angeles` days. The report host exposes this through `/api/report/executive/outgoing-calls` and renders it at the bottom of the Executive Report with pagination, disposition, duration, campaign, contact ID/name fallback, first-attempt state, and lazy signed recording playback. Manual execution `703098` succeeded and the production webhook returned 6 rows. This detail surface is separate from aggregate GHL call-status reporting.
 - **GHL PIT verification**: The root `GHL_PIT` was tested directly against the official REST API on 2026-07-31. `GET /locations/Zwz4relUXVPxx8uohnjV` and `GET /contacts/?locationId=Zwz4relUXVPxx8uohnjV&limit=1` both returned HTTP 200 with `Authorization: Bearer` and `Version: 2021-07-28`. The PIT is valid for CRM/API data access. It does not resolve the native Custom Report builder page's Firebase/browser-session failure, and the supported API/SDK still does not expose widget-layout mutation.
- **SMS campaign**: SimpleTexting campaign execution remains paused pending provider account re-enablement. On 2026-07-24, the send boundary was fixed and published: campaign messages use `AUTO` mode, failed provider claims are retryable, and GHL conversation mirroring requires a real provider message ID. The campaign runner (`dUyOfxllvkxZavaw`) and phone backfill (`8hQKQi1PooYDFxNR`) remain unpublished after the n8n stale-execution recovery. SimpleTexting still returns HTTP `409` on sends; diagnostics confirmed the bearer token, provisioned primary number, and target contact/opt-in are valid, leaving provider-side message acceptance/account policy as the blocker. The idempotent boundary (`gwaEpWDpTIwsafi8`) is published as `a56d28c0-11f1-4938-8eea-08c6d665c3d8` with E.164 normalization and safe provider-error capture. Do not resume campaign execution or success-volume testing until SimpleTexting re-enables the account and one controlled send returns a real provider ID.
- **SimpleTexting remediation**: Deferred per user instruction while provider compliance discussions are active. Do not modify or resume provider-success testing until the provider-side issue is resolved.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.
- **Regulated-business classification / SDR boundary (contract clarified 2026-07-30)**: `qualified` means the contact's business is related to a regulated vertical such as nicotine, cannabis, CBD, vape, or hemp; `not qualified` means it is not a regulated business. The live classifier now writes the canonical classification tags and the Vapi intake is published with a `qualified` gate. Qualified opportunities now enter `Sales Outreach -> Qualified` through published GHL workflow version 10. Existing contact/opportunity ownership alignment is handled separately; the live Jason/Marc allocator handles records entering that stage without a native owner.
- **SDR ownership synchronization**: Published GHL workflow `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, version 7) now keeps contact owner, native opportunity owner, custom opportunity `Owner`, and routing audit fields aligned for Jason and Marc when the opportunity owner changes. It does not replace the unresolved Janvi qualification gate or allocate unowned Warm records.
- **Classification and promotion implementation (2026-07-30)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is published on version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`; `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) is published on version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`; and GHL workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) is published as version 10 with both opportunity actions targeting `Sales Outreach -> Qualified`.
- **Ownership double-handling audit (2026-07-30)**: No active duplicate owner writer was found. The classifier writes tags only; Vapi intake writes queue/Apollo state only; the active n8n MQL workflow creates or updates Warm opportunities without owners; and the GHL promotion workflow changes pipeline stage only. The sole active owner-alignment path is GHL `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, published version 7), triggered by an opportunity `assignedTo` change. It assigns the contact and updates the custom opportunity `Owner` plus routing fields, but does not assign the opportunity owner. The staged n8n workflow `VI39o4X954fYDjOQ` is inactive and must not be activated as-is because it would duplicate those contact/custom-field writes.
- **Legacy-owner migration (2026-07-30)**: Migrated the open Sales Outreach opportunities whose custom opportunity `Owner` was John or Kevin. The initial scope was 307 records (305 John, 2 Kevin). The final authoritative opportunity search returned zero remaining John/Kevin custom-owner records; native opportunity owners and the published GHL alignment cascade are now the source of truth. The staged n8n owner-sync workflow remains inactive.
- **Jason/Marc no-owner allocator (2026-07-30)**: Published n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) on a 30-minute native Schedule Trigger. It fetches open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, assigns Jason (`yU85G6kfhtW4vUtx3QE6`) or Marc (`sqGx5rp3oAUG610NXyjU`) using deterministic opportunity-ID hashing, and writes only native opportunity ownership. The first controlled run assigned 73 records successfully; sample verification confirmed contact owner and custom opportunity `Owner` cascaded correctly through GHL workflow version 7. Remaining unowned Qualified records are draining in bounded batches.
- **Follow-up sender routing - COMPLETE (2026-07-29, audited 2026-07-30)**: Workflow `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`) is published as version 39 with Jason workflow defaults (`Jason from Transparent eCom` / `jason@livetransparent.com`). All 7 Send Email actions use `From Name = {{opportunity.owner}} from Transparent eCom` and `From Email = {{user.email}}`. The six templates (one reused by 2 actions) retain literal Jason sender metadata as safe fallback. The workflow triggers on Sales Outreach stages: New, Attempting Contact 1st Attempt, 2nd Attempt, 3rd Attempt, Engaged. Marc routing path (`sqGx5rp3oAUG610NXyjU`) is configured but untested — zero Marc-owned opportunities have entered a trigger stage. Do not send a live test email unless explicitly requested.
- **Vapi transfer hardening**: Live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants now use neutral Sales Lead wording while preserving the compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- **RB2B assignment hardening**: Live workflow `3kjsIUeoEQFx26cC` no longer runs its hardcoded Kevin task during Warm intake. The legacy task node is disconnected/disabled and the workflow is published with contact persistence ending at `Result`.
- **PIT token rotation (2026-07-30)**: Full GHL PIT token rotation completed and verified. The old token was replaced with the rotated PIT across both Config nodes that embedded it (Intake Poller `bYk1Ai6MJLyhTsDZ`, Dialer `r7UjWLndmc6EqEUW`). Full REST API audit of all 67 active n8n workflows confirmed zero occurrences of the old token remain in live production paths. Both modified workflows were published with matching `versionId === activeVersionId`. Documentation (`AGENTS.md`, `repomix-output.md`, `Operating Snapshot.md`) updated. Archive/backup files in `n8n/backups/`, `n8n/voice-agent/`, and `scripts/` retain historical snapshots.

## Prioritized Next Steps

1. ~~**Deploy and verify the Executive Report**~~ **Done 2026-08-04**: the public host serves build `2026-08-01-v12-campaign-breakdown`; campaign/channel rows, selected-period controls, prior-period comparison, LinkedIn Invites/Accepted/Replies columns, social engagement fields, and the HTTP 200 campaign endpoint were verified. The report container was updated on the managed VPS after the live API and UI changes.
2. **Complete native GHL report configuration**: in the now-verified authenticated GHL UI, add Partnership Pipeline and partnership-tag filters to the relevant widgets, then verify the MQL table, Brands/Dispensaries email widgets, custom open/click/response metrics, pipeline context, campaign rows, and shared date behavior. Do not use undocumented API guesses.
3. **Resolve SimpleTexting provider 409**: coordinate with SimpleTexting support/account settings or test the account through an approved provider console/API path. The n8n boundary, token, primary sender number, recipient contact, opt-in status, E.164 normalization, retry state, and GHL mirroring guards are verified. After the provider accepts one controlled message with a real provider ID, resume low-volume production verification and then complete the STOP-tag guard audit.
4. **Run controlled Vapi verification (dialer now operational)**: the 1,051 pending contacts are being processed. Monitor a live Brand call and a live Dispensary call from the next few dialer executions; confirm the Vapi dashboard callback/tools are present, no unresolved placeholders, no voicemail disclosure, correct one-question turn-taking, and correct outcome/queue completion via the repaired Call Outcome Ingest workflow.
5. ~~Implement Jason/Marc no-owner allocation~~ **Done 2026-07-30** — workflow `eeksgD0fbGHUqh4r` is active, 73 records assigned in first run, remaining unowned Qualified records draining in bounded batches.
6. **Harden remaining public boundaries**: authenticate Warm intake and SimpleTexting send webhooks, then migrate active Config-node secrets into protected credentials/runtime configuration. n8n Code nodes cannot access managed credentials, so this migration requires replacing direct Code-node HTTP calls with credentialed HTTP Request nodes or an approved protected runtime-variable path; do not move the same secrets into another Set/Config node.
7. **Finish reporting backlog**: implement `docs/reports/Reporting Gaps and Requirements.md`, including LinkedIn activity-ledger instrumentation and `Partnership LinkedIn` attribution, configure the native GHL Partnership Pipeline/tag widgets through authenticated UI access, add approved Meta Ads spend/click/impression ingest, normalize Top Page formatting, and add remaining trigger-link, Unipile, and social metrics where source data supports the selected period.
8. **Migrate remaining embedded Config secrets**: replace active hardcoded GHL/Unipile values with protected credentials or approved runtime configuration, then rotate values exposed during migration. The LinkedIn state-upsert boundary is already authenticated and verified.
9. **Partnership outbound activation**: approved and enabled 2026-07-31. `LT - Partnership Email Dispatcher` (`Xshck23cKo1yXL9D`), `LT - Partnership LinkedIn Dispatcher` (`crKIsaL5k3YBfqDZ`), and `LT - Partnership LinkedIn DM Sequence` (`nspggypNF245xzeL`) are published with `defaultDryRun=false`, active schedules, and matching `versionId === activeVersionId`. Do not manually execute these workflows unless intentionally sending an additional live batch.
10. **Capture social reach/impressions/saves (2026-08-04)**: Add a GHL OAuth credential to n8n, then build or extend a scheduled social statistics ingest to store platform/day metrics and surface the official statistics response in the Executive Report. The official endpoint currently returns reach/impressions, while the existing PIT-based post ingest does not.
11. ~~**Backfill the known partnership replies**~~ **Done 2026-08-04**: Strider Peterson's email reply and Jaret Christopher's LinkedIn reply were inserted with verified source timestamps; the selected-window campaign summary now reports both.

### Explicit Reporting Notes

- The campaign summary workflow is live and published as `64641979-71f3-466c-8a09-36013be6bc0e`; manual execution `276517` succeeded, and live 7-day/30-day endpoint checks returned named rows.
- The `2026-07-20` through `2026-07-26` email engagement gap is a historical `Email_Events` coverage gap; no event-ingest executions existed in that window. Do not change valid aggregation logic or fabricate rates.
- Four credential-bearing response captures remain intentionally untracked and must not be committed.

## Newly Confirmed Gaps

### Follow-up Sender Routing Handoff

- **User requirement**: follow-up email sender name and email must follow the opportunity/contact owner; if neither record has an owner, use Jason.
- **Workflow**: `Jason Followup Emails and SMS`, ID `f6b44e34-779e-4959-b41d-b05641f134e7`, currently published version `38`.
- **Template folder**: `Jason Follow Up Emails`, ID `69e0c9069af5986541802d88`.
- **Affected template IDs**:
  - `69e0d86b9af59801b580f4b5`
  - `69e0db27d6a707bbf190d022`
  - `69e0db9ab02114c1ba3c29d3`
  - `69e0dc56d6a707c0ac90e074`
  - `69e0dcad8ffabf47b4d987c5`
  - `69e0ddd0b021145bab3c4569`
- **Current template state**: all six have literal `fromName = Jason from Transparent eCom` and `fromEmail = jason@livetransparent.com`. Keep this as a safe fallback; the live workflow actions already override it for owned records.
- **Current workflow state**: all 7 Send Email actions use owner-driven sender fields. Verify or set Jason as the no-owner fallback user in the workflow UI. Do not hard-code Jason as the sender for owned opportunities/contacts.
- **API limitation**: `PATCH /emails/builder/{templateId}` accepts literal sender emails but rejects `{{user.email}}` with HTTP 422 (`fromEmail must be an email`). The public `GET /workflows/` endpoint confirms metadata/status/version only; workflow action definitions are not writable through the public API.
- **Browser status**: authenticated GHL workflow access was used to set and publish the Jason defaults. The published version 39 API response confirms `senderAddress` and `status: published`.
- **No test send**: no live email was sent during this investigation or patch.
- **Next session exact order**:
  1. Open the authenticated GHL workflow URL from the user-provided link.
  2. Monitor the next normal follow-up execution; do not send a live test email solely for sender verification.
  5. Reopen the workflow and verify all 7 Send Email actions and the published version.
  6. Do not change template HTML or send a live test without explicit approval.

- ~~**Dialer credential rotation**: verified against GHL, full audit of 67 active workflows confirmed PIT rotation complete. Both Config nodes updated and published.~~ **Done 2026-07-30**
- **Callback authentication**: Vapi server authentication is configured on all four tracked assistants and enforced at the callback boundary with `X-Vapi-Secret`. Unauthorized callback, status, and tool payloads are rejected before routing.
- **SMS and Warm webhook authentication**: several live intake/send webhooks have empty shared-secret configuration and require an authentication pass before continued public use.
- **Credential storage**: active n8n Config nodes still contain API keys and webhook secrets. Migrate to n8n credentials or protected runtime configuration, then rotate exposed values.
- **LinkedIn state-upsert boundary**: `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on version `d9168bbc-9c96-44fd-a356-12e645a2ec3d` with terminal-state promotion, reply preservation, and protected `httpHeaderAuth`. All discovered callers are published with the shared header; unauthorized verification returned `403` and malformed authorized verification reached validation without writing state.
- **LinkedIn Config convention**: all eight relevant state-upsert workflows now have exactly one `Config` node. Callers read `Config.stateUpsertSecret` instead of embedding the shared header value in request code. This is the Community Edition variable workaround, not a replacement for managed credentials.
- **Ingest hardening (2026-07-31)**: GA4 empty/failure finalization, sales snapshot-date and cursor guards, sales `ghl_opportunities` health isolation, LinkedIn sync budgets/retries, dispatcher pre-invite claims, and terminal-state promotion are live and published. Dispatcher and sync were not live-executed during verification because they can mutate LinkedIn state or send invites.
- **Reporting owner dimensions**: contact owner, opportunity custom `Owner`, owner conflicts, and canonical SDR identity are not normalized into the reporting read model.
- **Campaign-level reporting dimensions**: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) returns named campaign/channel rows. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list`, and Vapi uses queue campaign IDs. The public report build `2026-08-01-v12-campaign-breakdown` has All, Email, LinkedIn, SMS, and VAPI campaign filters, plus LinkedIn Invites/Accepted/Replies columns. Reply instrumentation is live and the two known historical replies are backfilled. The remaining reporting gap is OAuth-backed social statistics ingestion; the Executive Summary's weekly LinkedIn KPI still needs a follow-up query adjustment to count `reply_received` alongside legacy `inbound_reply` events.
- **Partnership state and outbound safety (2026-07-31)**: `partnership_linkedin_connection_state` now contains 127 `ready` rows seeded from GHL contacts with `partner_candidate_linkedin` and LinkedIn URLs. The dispatcher and DM sequence are published in dry-run mode; dispatcher execution `278203` reported 100 candidates, 30 planned, 0 sent, and 0 errors. DM execution `278342` completed successfully with no sends. `partnership_release_log` remains empty because email sending is also dry-run. These rows are state preparation, not evidence of invitations or DMs sent.
- **Tag-based attribution audit (2026-07-30)**: DAN has reliable queue tags (`Enrollment Queue - DAN - Brands/Dispensaries`) plus `DAN_Release_Log.campaign` and `enrollment_tag`; `brands_pool`/`dispensaries_pool` should remain supporting audience evidence. Emerald has eight bucket-specific queue tags and matching `Seq Emerald - ...` tags, with stronger backend fields in `Emerald_Campaign_Contacts.bucket/email_campaign` and `Emerald_Release_Log.bucket`. SMS has lifecycle tags but its durable campaign identifier is `SimpleTexting_Campaign_State/Event_Log.campaign_key`; `sms_drip` is only the eligibility pool. LinkedIn has lifecycle/suppression tags but no durable campaign tag, so current Brand/Dispensary attribution must use `emerging_pool_contacts.source_list` or historical pool-tag observations until a campaign key is added to state.
- **Vapi correlation**: end-of-call callbacks now recover missing `queue_id` values from prior `voice_call_attempt` records when possible. The dialer also reclaims stale `in_progress` locks after 15 minutes, while unresolved provider correlation remains observable through the callback execution path.
- **Gap fixes applied 2026-07-25**: silent human Vapi answers now classify as `interest_unknown`; dialer global hours are 9am-5pm CT; invalid campaign tags fail closed; source-tag cleanup is dynamic; report config/publish schedules are connected and tested; superseded Apollo Sheet First webhook is unpublished.
- **Vapi hardening applied 2026-07-27**: intake, direct enqueue, and dialer paths require the `not qualified` suppression guard plus an open Warm → New opportunity; callback requests require the Vapi server secret; tool outcomes complete queue rows; timer scheduling uses an atomic Postgres claim; stale queue locks are reclaimed; timer and GHL cleanup requests retry transient failures. The intake still needs to require positive `qualified` classification so raw pool tags cannot bypass the classifier.

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
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Reply Suppression Repair (2026-07-26)

- **Incident**: Christy Essex replied on 2026-07-23 that she had left Vangst and referred new/current-project questions to Logan Humiston. An automated Emerald follow-up was still sent on 2026-07-26.
- **Root cause**: `WL - Seq - Stop on Booked/Reply/Closed` had the correct `Customer Replied to Sequence Emails` trigger filtered to Email, but its `Remove from Workflow` action only removed the legacy Variant A/B workflows. It did not include the Emerald sequence workflows.
- **Fix**: Through the GHL UI, added all 12 Emerald sequence workflows, including P2 variants, to the removal action. Published as version 17.
- **Immediate containment**: Removed Christy's `seq enrolled - emerald` and `seq emerald - executives sso` tags. Her Warm/MQL context and opportunity were preserved.
- **Boundary**: n8n `LT - Email Event Ingest` remains reporting-only; it stores events in `Email_Events` and is not the sequence suppression mechanism.

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
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Unpublished helper |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (native Schedule Trigger every 10 min, 30 contacts/cycle, tag rotation) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is active on a native 15-minute Schedule Trigger.
- It selects up to 10 Brand and 10 Dispensary candidates per run, uses live GHL suppression checks, and applies Vapi campaign tags only after DeepSeek acceptance or a qualified-domain match.
- `vapi_qualified_domains` is updated only after a successful campaign-tag write; free-email domains, cleanup rows, failed writes, and rejected model output are excluded.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes.

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **Historical ET-forward timing**: the previous cron-based schedule shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. The current implementation uses a native two-minute Schedule Trigger; the timezone-aware business-hours guard remains authoritative.

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

### Fixes Applied — Call-Path and Callback Hardening (2026-07-22 to 2026-07-23)

- **Unscheduled call path removed**: the callback workflow previously posted to `LT - Voice Dequeue Next` after every end-of-call event. That helper could start another Vapi call without the dialer's Schedule Trigger. The callback trigger was removed and `LT - Voice Dequeue Next` was unpublished; it is now an explicit helper only.
- **Callback payload recovery**: the callback Config Set node replaced the webhook input before detection. `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` item directly.
- **End-of-call metadata coverage**: the normalizer now reads IDs from Vapi `assistant.metadata`, `assistant.variableValues`, and `artifact.variables` paths.
- **GHL note safety**: completion-note JSON now uses an object expression instead of interpolating unescaped summaries into a JSON string. Note and tag writes are non-blocking so a CRM note failure cannot prevent queue completion.
- **Queue completion safety**: `Postgres - Mark Queue Completed` now passes query replacements as an array, preventing the scalar-parameter error that previously stopped completion.
- **Scheduler standardization**: the outbound dialer uses a fresh native Schedule Trigger with a two-minute interval. The business-hours guard remains the call eligibility authority. Resolved 2026-07-30: the dialer was crashing on every execution due to three separate bugs (GHL `Version` header, Postgres `RETURNING` visibility, empty-queue 403) — fixed and verified end-to-end.

### Fixes Applied — Brand Prompt and Variable Context (2026-07-25)

- **Execution audit**: callback execution `241579` received an `in-progress` status update and entered the background timer as designed. The corresponding end-of-call callback `241581` completed successfully for queue `7aed3bdb-fe22-4b98-a4ce-33b9018fe32b`, normalized the outcome as `voicemail`, applied `vapi_voicemail` and `vapi_voicemail_left`, inserted the call attempt, and marked the queue row completed.
- **Brand assistant prompt** (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`): removed `{{company_name}}` from the first-message opener so a missing company value cannot be spoken as an unresolved placeholder. Added explicit runtime-variable handling, IVR-versus-voicemail disambiguation, one-question turn-taking, and no-stage-direction rules. The live-call AI/recording disclosure remains system-prompt-only and is excluded from voicemail.
- **Outbound dialer** (`r7UjWLndmc6EqEUW`): `Code - Check Phone` now extracts `company_name` from the GHL contact; `Build Vapi Body` passes it through `assistantOverrides.variableValues` and metadata. The workflow was republished and verified with matching `versionId` and `activeVersionId`.

### Queue State

**1,051 contacts pending** (reset 2026-07-30 from 1,047 failed + 4 cooling_down), 1,615 completed. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer is configured for a native two-minute Schedule Trigger and picks up from queue only during timezone-aware business hours. Blocked/invalid/outside-hours candidates are released and skipped within the same execution, capped at 25 queue checks.

### Final Production Hardening — 2026-07-23

- Callback timer state now has the existing 60-second duplicate-start guard plus 30-minute pruning of ended/inactive records.
- `LT - Voice Queue Enqueue` now requires `X-LT-Voice-Queue-Secret`; callers use `VOICE_QUEUE_ENQUEUE_SECRET` and unauthenticated requests fail closed before queue insertion.
- Apollo phone-request failures are counted as `apollo_phone_request_failed` for monitoring.
- `LT - Apollo Queued Timeout Reaper` now connects its Slack summary builder to `Post to Slack #leads`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- All modified live workflow versions were verified published with matching `versionId` and `activeVersionId`.

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
- SimpleTexting send boundary uses `AUTO` mode so multi-segment campaign messages are accepted; provider errors are persisted for diagnosis and can be reclaimed on retry.
- Campaign mirroring is gated on `action = message_sent` and a non-empty provider message ID. Dry runs, blocked sends, duplicates, and provider errors do not call GHL Conversations.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

### Current Template Registry

- Send webhook: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`.
- Canonical keys: `sms_1` through `sms_6`.
- Updated 2026-07-26: `sms_1`, `sms_3`, and `sms_5`.
- Unchanged 2026-07-26: `sms_2` and `sms_6`.
- Updated 2026-07-29: `sms_4` removed cannabis product terms and the unreliable Facebook ad preview link while retaining `regulated-industry` positioning. The published active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- Existing `john_sms1` through `john_sms5` payload aliases remain in place for compatibility and were not renamed.

### 2026-07-24 Fix And Next-Run Check

- Root cause of the `409` provider errors: `LT - SMS Idempotent Send` hardcoded `SINGLE_SMS_STRICTLY`, while SMS 1 is 320 characters and requires multi-segment delivery.
- Root cause of the GHL `404 Contact id not given`: `LT - SimpleTexting SMS Send` mirrored blocked and dry-run outcomes instead of only successful provider sends.
- Fixed and published workflows: `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`) and `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`).
- Safe checks passed: idempotent `simulate:true` execution `241272`; campaign dry run `241275` stopped before the mirror node.
- **Next scheduled dispatcher check:** confirm at least one `status = sent` result with a real SimpleTexting provider message ID, no HTTP `409`, no GHL `Contact id not given` errors, and a matching `report_sms_sent.provider_response` record. Then confirm the campaign state advances to `sent_step_1` only for an actual provider send.

## Partnership Marketing Pipeline (LIVE 2026-07-31)

131 content partnership contacts imported from two CSV lists ("Email" and "LinkedIn") and merged/deduplicated. Two parallel outbound sequences run from Cameron's accounts: a 4-step email sequence (60/day, 11am ET Mon-Fri) and a 4-step LinkedIn DM cadence dispatched through Unipile (30 connection requests/day, 3pm CT Mon-Fri). Both sequences use 2-weekday intervals between steps. All infrastructure is fully isolated from the main DAN/Emerald pipelines (separate Postgres tables, separate n8n workflows, separate GHL pipeline).

### Import

- 131 unique contacts after dedup/merge (script: `scripts/clean_partnership_data.py`)
- 98 email contacts imported via n8n batch workflow (`zmrYrUjVcyXaS7PJ`, webhook `/webhook/lt-partnership-bulk-import`)
- 33 LinkedIn-only contacts created in GHL via MCP (no email; LinkedIn URLs set via `ew6uQQnAjgCbjeGn` webhook)
- All contacts assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- Tags: `partner_candidate_email` (email contacts), `partner_candidate_linkedin` (LinkedIn contacts), or both
- 14 contacts excluded from original CSV due to wrong company/email domain mismatches — awaiting corrections from user
- Test contact `NVAp2GdpbWXLheyUgVf2` (edmundocadorniga@gmail.com) cleaned — partnership tags removed

### GHL Pipeline

- Pipeline: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`)
- Stages: New Partner Lead (`ccc3d423-ff86-46b4-bd53-064458910eba`) → Contacted → Proposal Sent → Closed
- Opportunities created automatically by Reply Handler when a contact replies (email or LinkedIn)

### Email Templates

4 templates created in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`), populated with HTML via PATCH API and `{{contact.first_name}}` merge fields:

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher currently sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The templates exist for open tracking and deliverability but are not the primary send path. The dispatcher's inline HTML in the Code node is the canonical message content.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'`. Tracks connection status, sequence step, and DM state. |
| `partnership_release_log` | Tracks every sent email (contact, step, status, message ID). UNIQUE on `(ghl_contact_id, email_step)`. |

### GHL API Key

GHL, Unipile, and state-upsert values remain configured in the live workflow runtime; values are intentionally omitted from documentation. Credential migration and rotation remain open.

All 7 partnership workflows are active and published. The dispatcher schedules are now explicit weekday cron schedules: email at 11:00 America/New_York, LinkedIn requests at 15:00 America/Chicago, and LinkedIn DMs at 12:00 America/Chicago. Safe smoke executions `281269`, `281268`, and `281270` succeeded. Outbound email, invitations, and DMs remain `defaultDryRun=true` pending explicit launch approval.

### Tags

| Tag | Purpose |
|-----|---------|
| `partner_candidate_email` | Import tag — marks contact for email sequence |
| `partner_candidate_linkedin` | Import tag — marks contact for LinkedIn sequence |
| `partner_email_queued` | Applied after first email send — marks contact as active in email sequence |
| `partner_linkedin_requested` | Applied after LinkedIn connection request sent |
| `partner_email_sequence_completed` | Terminal — all 4 emails sent |
| `partner_replied` | Terminal — contact replied (stops all sequences, creates opportunity) |
| `partner_not_interested` | Terminal — manual override |
| `partner_do_not_contact` | Terminal — manual override |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | Sends 4-step email sequence via GHL Conversations API. 60/day cap, 11am ET Mon-Fri, 2-weekday intervals. |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | Sends LinkedIn connection requests via Unipile. 30/day cap, 3pm CT Mon-Fri. Atomic ready→requested_pending claim. |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step LinkedIn DM cadence for connected partnership contacts. 2-weekday intervals. |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | POST `/webhook/lt-partnership-reply`. Tags contact `partner_replied`, creates opportunity in Partnership Pipeline → New Partner Lead, posts Slack alert. |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Schedule Trigger every 5 min. Polls GHL for inbound email replies from `partner_email_queued` contacts, triggers Reply Handler on detection. |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | Bulk-imported 98 email contacts into GHL. |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on 33 LinkedIn-only contacts. |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows were patched to also query `partnership_linkedin_connection_state`:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION to include partnership rows; `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL select + separate Update node for partnership table |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing node + separate partnership update |

### Audit (2026-07-31)

Full post-build audit completed:
- All 7 partnership workflows published and active
- 3 patched LinkedIn workflows verified with correct partnership table queries, routing, and update nodes
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL includes `partnership_release_log` via UNION ALL (published version `6641aa9a`)
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped and verified
- Executive Report frontend later updated to build `2026-08-01-v12-campaign-breakdown`; the dated audit below records the original partnership deployment.
- GHL contacts verified: 98 with `partner_candidate_email`, 127 with `partner_candidate_linkedin` (94 overlap), 131 total
- 4 email templates confirmed in folder `Partnership Email Campaign`, all with correct HTML content
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected

### Remaining

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder.
- **Social statistics ingestion**: Add a usable GHL OAuth credential to n8n and ingest daily saves, reach, and impressions; the PIT cannot access the official statistics endpoint.
- **Executive weekly LinkedIn KPI**: Adjust the query to count `reply_received` alongside legacy `inbound_reply` events.
- **Reply Poller API gap resolved 2026-07-31**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) used the wrong `POST /conversations/search` method in the earlier implementation. The current published implementation uses `GET /conversations/search`; see the 2026-08-04 remediation entry above.
- **14 excluded contacts**: User to provide corrected company names; re-import when available
- **Marc-owned follow-up sender routing**: Untested — zero Marc-owned opportunities exist in trigger stages

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

GA4, GHL, and GSC ingestion are all live. GSC execution `281697` confirmed the renewed OAuth credential and successful source-health finalization. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

### 2026-07-25 GHL Leads Ingest Rate-Limit Hardening

- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) failed in `Fetch + Normalize Leads` with GHL HTTP `429 Too Many Requests` during paginated contact retrieval (execution `241845`).
- Replaced the task-runner-incompatible HTTP wrapper with direct `this.helpers.httpRequest` calls.
- Added bounded 429 handling: up to four attempts per page, honoring `Retry-After` when available and otherwise using exponential backoff.
- Added a 500 ms delay between pagination requests to reduce GHL rate-limit pressure.
- Published workflow version `c740c006-fef5-4873-91b5-d2d4218872de` and confirmed it is the active version.
- Manual production-path validation execution `241894` succeeded: 500 contacts fetched, raw lead upserts completed, sync watermark and source health updated, and final status was `success`.
- Updated local reporting SDK snapshots (`leads_ingest_sdk_v2.ts`, `leads_ingest_sdk_v2_clean.ts`, and `leads_ingest_sdk_v3.ts`) with the same HTTP hardening.

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- ~~Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools~~ — Confirmed: poller running successfully every 10 min throughout 2026-07-20 dialer outage
- ~~Monitor Outbound Dialer~~ — Dialer recovered 2026-07-20 after stuck-queue fix (contact `AX3wfQNpRwm6DG0HgUE2` deleted from GHL, `neverError: true` applied to lookup, `onError: continueRegularOutput` on call note)
- Watch for GHL rate limiting on downstream nodes
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Test live calls with both Brand and Dispensary assistants after system prompt updates (discovery questions should flow one-at-a-time, no disclosure on voicemail, no "clears throat", "from Transparent eCom" not "with a transparent")
- Consider switching Jordan's voice from Nico to Emma/Layla (both already fallbacks) to eliminate remaining TTS artifacts
- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback

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

### 8. Partnership Marketing Monitoring

- Monitor first Partnership Email Dispatcher run at 11am ET — confirm emails send, release log writes, and `partner_email_queued` tag applied
- Monitor first Partnership LinkedIn Dispatcher run at 3pm CT — confirm connection requests send, state table updated, `partner_linkedin_requested` applied
- Verify Partnership Reply Poller detects any inbound replies and triggers Reply Handler correctly
- Confirm Partnership LinkedIn DM Sequence picks up connected contacts after Acceptance Checker processes them
- Verify 3 patched LinkedIn workflows (Acceptance Checker, Reply Backfill, Unipile New Messages) handle partnership rows correctly
- Monitor for GHL rate limiting on per-contact API calls (250ms delay between contacts)
- After first email sends complete, verify the campaign summary endpoint reflects non-zero "Partnership emails" catalog row (may lag until reporting rollup runs)

### 9. LinkedIn Dispatcher Monitoring

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

1. **Partnership Marketing** — monitor first email dispatcher at 11am ET, LinkedIn dispatcher at 3pm CT. Verify both sequences fire, release logs write, reply polling works.
2. **LinkedIn dispatcher** — monitor first runs now that 14,987 `ready` contacts are queued. Verify invites send, tags apply, state table updates.
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

Warm is the unassigned intake and AI-verification layer. Only Janvi's explicit `qualified cannabis business` result promotes a record to Sales Outreach. AI-pending/unverified records are eligible for Vapi; explicitly rejected/non-cannabis records are not.

### Sales Outreach Pipeline
`New` → `Attempting Contact` → `Engaged` → `Meeting Requested` → `Booked` → `Unresponsive`

SDR ownership is resolved only on entry to `New`: align a single existing contact/opportunity owner, preserve matching owners, flag conflicts, or assign Jason/Marc 50/50 when neither has an owner. Keep native contact/opportunity owners and custom opportunity `Owner` aligned.

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

1. Disable or unpublish the classifier schedule if the bad cohort is still being selected.
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
- a representative Brand and Dispensary sample is manually approved
- accidental tags are removed
- accidental queue rows are cleared or neutralized
- classifier cap remains at 10 Brand + 10 Dispensary per run for the retry

## Practical Rule

For the first imported-pool rollout, rollback should be surgical:
- remove wrong tags
- neutralize wrong pending queue rows
- fix classifier selection
- remove any incorrectly persisted domain rows before retrying
- retry only after live workflow state and suppression checks are reviewed
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
| GHL Calls | `LT - GHL Daily Calls Ingest` + `LT - Call Outcome Ingest` | Aggregate GHL call status, direction, and outcome facts |
| GHL Appointments | `LT - GHL Daily Appointments Ingest` | Calendar events: booked, showed, no-show |
| GA4 Sessions | `LT - GA4 Daily Ingest` | Sessions, users, engagement by channel/landing page |
| GSC Search | `LT - GSC Daily Ingest` | Clicks, impressions, CTR, average position, queries, pages |
| Attribution Bridge | `LT - Report Attribution Bridge` | Traffic → contact matching |
| Daily Rollups | `LT - Report Daily Rollups` | Aggregated summary, channel, UTM, landing page tables |
| Executive API | `LT - Report Executive Summary API` | JSON served to embed via n8n webhook |
| Email Events | `LT - Email Event Ingest` | Opens, clicks, bounces, unsubscribes, spam complaints |
| LinkedIn State | `linkedin_connection_state` | Connection funnel: ready → requested → connected → DM → completed |
| Vapi Voice | `voice_call_attempt` + `voice_call_queue` | Call outcomes by campaign, pending queue distribution |
| Outgoing Call Detail | `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`) | Seven completed days of row-level Vapi calls, disposition, duration, campaign, contact ID/name fallback, and signed recordings; served through `/api/report/executive/outgoing-calls` |
| MQL/SQL | `report_raw_ghl_opportunities` + `report_raw_ghl_contacts` | MQL (Warm pipeline Qualified stage), AI-qualified cannabis promotion to Sales Outreach, SQL (tagged contacts) |
| AI Qualification / SDR Routing | Janvi assessment + GHL owner fields | Qualified cannabis -> Sales Outreach; owner alignment or Jason/Marc 50/50 fallback; pending/unverified -> Vapi Warm |

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

### Qualification and Work Queue Boundary
- Warm is the unassigned intake and AI-verification layer.
- Only Janvi's explicit `qualified cannabis business` result promotes a contact/opportunity into `Sales Outreach -> New`.
- SDRs work in Sales Outreach; they do not receive ordinary Warm assignments.
- Vapi calls AI-pending/unverified Warm contacts and excludes AI-qualified or explicitly rejected/non-cannabis contacts.
- A Vapi warm transfer is manually claimed by the answering SDR and then promoted into Sales Outreach.
- Cameron's Regulated Ads calendar is used for bookings and does not determine SDR assignment.
- Website demo CTAs and `/apply/` must use the direct GHL Regulated Ads booking widget (`https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK`), not the legacy Calendly embed or duplicate hero form.

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
- [x] Email campaign metrics (sent, opened, clicked, bounced, unsubscribed, complained) — added 2026-07-21
- [x] Email engagement rates (open rate, click rate, bounce rate) — added 2026-07-21
- [x] LinkedIn outreach funnel (ready → requested → connected → DM active → completed) — added 2026-07-21
- [x] Vapi voice campaign breakdown (calls by campaign, answered, qualified, booked) — added 2026-07-21
- [x] Vapi queue distribution (pending calls by campaign) — added 2026-07-21
- [x] MQL summary (active + total opportunities in Warm/Qualified MQL) — added 2026-07-21
- [x] SQL contacts count (contacts with SQL tag) — added 2026-07-21
- [x] Pool distribution (brands, dispensaries, vapi brand/dispensary pool tags) — added 2026-07-21
- [x] Stage mover count (fixed from 0 to 93 via stage ID resolution) — added 2026-07-21
- [ ] Meta raw spend/clicks/impressions (deferred)
- [ ] Matched funnel by landing page (after tracking is tightened)

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
- Total GHL calls by status → Available via `report_raw_ghl_call_outcomes` and the Calls & Conversations panel in the Executive Report
- Row-level outgoing Vapi calls → Available through the bottom Outgoing Call Detail section; this is separate from aggregate GHL call status reporting
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

The keys stay unchanged because live GHL workflow payloads reference them. The canonical registry is maintained by `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) at `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`. Automated campaign execution remains paused: `LT - SimpleTexting Campaign Step Runner` (`dUyOfxllvkxZavaw`) and `LT - SimpleTexting Campaign Phone Backfill` (`8hQKQi1PooYDFxNR`) are unpublished pending provider account re-enablement.

On 2026-07-26, `sms_1`, `sms_3`, and `sms_5` were revised and the workflow was republished. On 2026-07-29, `sms_4` was revised and republished to remove cannabis product terms and the unreliable Facebook ad preview link while retaining neutral `regulated-industry` positioning. `sms_2` and `sms_6` remain unchanged.

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
Hi - thanks for checking out regulated ads on social/search.

I'm Cameron, founder of Transparent eCom. We help regulated brands run ads that most agencies can't, including Mood, Cookies, and Lucy.

You can learn more at https://livetransparent.com/

Are you currently running ads, restricted from advertising, or just exploring options?
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
Quick follow-up -

We've helped brands like Mood, Lucy, and GPen scale ads profitably in regulated spaces.

Would it be helpful if I showed you what has worked for them?
```

### `sms_4`

```text
Fun fact:
We can run product ads with regulated-industry mentions directly in the ad.
Would you like me to send a short overview?
```

### `sms_5`

```text
If you're a dispensary, this might be interesting:

We help dispensaries connect digital ad activity to in-store purchases, so they can measure actual ROI from social and search campaigns.

More details are available at https://livetransparent.com/

Should I send over a quick example?
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
- Social replies remain unassigned in Warm until Janvi's AI assessment verifies a qualified cannabis business. Promotion into `Sales Outreach -> New` applies the documented owner-alignment rule; the social transport itself must not assign an SDR.
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
