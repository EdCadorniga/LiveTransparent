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
- n8n target version: `2.31.5` (native Schedule Trigger is the scheduling standard; do not add OS/Coolify cron jobs for workflows).
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
- Campaign summary version `64641979-71f3-466c-8a09-36013be6bc0e` returns named channel/campaign rows. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list`, and Vapi uses queue campaign IDs. Catalog rows for `General outbound`, `Partnership emails`, `xyz`, and `abc` remain zero until matching source events exist.
- The local Executive Report UI includes the campaign/channel table and LinkedIn columns, but `https://reports.livetransparent.com` still serves the older build `2026-05-11-v9-active-opps`; deploy and verify through Coolify before calling the host current.
- The native GHL report URL must be verified through an authenticated GHL UI session. The last browser check returned 404 plus Firebase token/permission errors, so native widget configuration is not currently confirmed.
- The official GHL API/SDK does not expose Custom Report widget-layout mutation. Do not guess undocumented report-builder endpoints; native widget changes require authenticated GHL UI access or an explicitly approved internal API path.
- Never commit GHL PITs, Firebase signed URLs, OAuth tokens, or captured response artifacts containing credentials. Use environment placeholders in documentation and leave sensitive captures untracked.

### Ingest and LinkedIn Hardening (2026-07-31)

- `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`. Empty responses finalize as `empty`; malformed data is `partial`; fetch failures finalize run/health state, do not advance the watermark, and then fail the execution. Verification: success `276731`, pinned failure `276747`.
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`. Snapshot/history rows use ingest date, raw rows preserve source timestamps, retries/cursor guards are bounded, finalization errors fail closed, and sales health uses `ghl_opportunities` while raw compatibility remains `source_system = 'ghl'`. Verification: execution `276626` processed 7,683 opportunities and 7,683 history rows.
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) is published on `fa1a5dfe-d00c-47b3-98d3-862ea6f912a7`. It uses direct `this.helpers.httpRequest`, bounded contact/API budgets, retry/timeouts, explicit error reporting, and terminal/reply-state preservation.
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is published on `bd385c89-0678-4301-84e6-abc63fea3c28`. It reads Config explicitly, atomically claims `ready` rows as `requested_pending`, and performs live suppression/reply checks before invites. Do not manually execute it without explicit approval because it can send LinkedIn invites.
- `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on `bf814307-a235-4416-abaa-9c8329f76130`; terminal payloads promote state to `completed` and active replies remain preserved. Its webhook still has no protected credential because none is currently available; provision one before adding caller authentication.

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
- **Historical n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` returned fields that violated the MCP output schema. The deployment target is now n8n `2.31.5`; retain the REST workaround if the MCP schema issue recurs:
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

- n8n target upgraded to `2.31.5`; recurring workflows use native Schedule Trigger nodes, not OS/Coolify cron jobs.
- `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` input because the Config Set node replaces the current item.
- Callback normalization now reads Vapi IDs from `message.assistant.metadata`, `message.assistant.variableValues`, and `artifact.variables`.
- Callback completion-note JSON is built as an object expression, avoiding invalid JSON when summaries contain quotes or newlines.
- GHL note/tag failures continue without blocking Postgres queue completion; queue completion passes query replacements as an array.
- The callback no longer invokes `LT - Voice Dequeue Next`. That helper is unpublished and must remain an explicit/manual helper, not an automatic call-start path.
- The outbound dialer uses a native two-minute Schedule Trigger plus the existing timezone-aware business-hours guard.
- The outbound dialer atomically changes a selected queue row from `pending` to `in_progress` before calling Vapi. Ambiguous Vapi/API failures cannot be retried after the stale-lock window; no-phone and outside-hours release branches explicitly restore `pending`.

### Vapi/n8n Final Hardening (2026-07-23)

- n8n is now documented and operated at target version `2.31.5`; recurring workflows use native Schedule Trigger nodes rather than OS/Coolify cron.
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
| `socialPosts` | `report_raw_ghl_social_posts` | Post totals, engagement |
| `health` | `report_source_health` | Source system health statuses |
| `callStatusBreakdown` | `report_raw_ghl_calls` | Top 10 call statuses by direction |
| `callOutcomeBreakdown` | `report_raw_ghl_call_outcomes` | Top 12 dispositions by direction |
| `appointments` | `report_raw_ghl_appointments` | Top 8 appointment statuses |
| **`emailsSent` / `emailsOpened` / `emailsClicked` / `emailsBounced`** | `report_daily_summary` + `Email_Events` + Release Logs | Email campaign metrics (added 2026-07-21) |
| **`emailOpenRate` / `emailClickRate` / `emailBounceRate`** | Computed from above | Email engagement rates (added 2026-07-21) |
| **`linkedinFunnel`** | `linkedin_connection_state` | ready→requested→connected→DM active→completed (added 2026-07-21) |
| **`vapiCampaignBreakdown`** | `voice_call_attempt` JOIN `voice_call_queue` | Per-campaign call totals, answered, qualified, booked (added 2026-07-21) |
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

## Partnership Marketing Pipeline (LIVE 2026-07-31)

131 content partnership contacts imported. Two parallel sequences from Cameron's accounts: a 4-step email sequence and a 4-step LinkedIn DM cadence. All infrastructure isolated from DAN/Emerald (separate Postgres tables, workflows, GHL pipeline).

### Pipeline

- **GHL Pipeline**: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`) — New Partner Lead → Contacted → Proposal Sent → Closed
- **Contacts**: 98 email + 33 LinkedIn-only, all assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- **Tags**: `partner_candidate_email`, `partner_candidate_linkedin`, `partner_email_queued`, `partner_linkedin_requested`, `partner_email_sequence_completed`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact`
- **GHL API key**: `pit-48a3b580-6906-418b-8215-3257599fd551` (embedded in dispatcher Config nodes + Reply Poller via `$env.GHL_PIT`)
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
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | 60/day, 11am ET Mon-Fri, 2-weekday intervals |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | 30 connection requests/day, 3pm CT Mon-Fri, atomic claim |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step DM cadence, 2-weekday intervals |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | `/webhook/lt-partnership-reply` — tags `partner_replied`, creates opportunity, Slack alert |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Every 5 min — polls GHL for inbound email replies, triggers Reply Handler |
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

- **GHL Custom Report**: Add partnership metrics to native report `6a67dce4a51a4360c60963a3` — requires authenticated browser session
- **Re-import 14 excluded contacts** after corrected company names provided

## Other Live Systems

- **SimpleTexting**: Send, sequencer, delivery, inbound reply, unsubscribe, and idempotent-send workflows are live/available in n8n. The scheduled pool dispatcher is active as of 2026-07-18, targets GHL tag `sms_drip`, runs weekdays at `10:15am` and `3:00pm` ET, uses `candidateLimit=10`, and has `defaultDryRun=false` for live sends. Sequencer waits 2 days between SMS steps. Inbound replies add `simpletext_replied`, remove `simpletext_ongoing`, mark campaign state `replied`, and suppress future campaign/direct sends; `simpletext_stop` remains the opt-out hard stop. `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) posts a Slack alert through node `Post to Slack` with title `Inbound SimpleTexting Reply`, then posts the inbound message to GHL Conversations under `SimpleTexting SMS` via `Post to GHL Conversations` node using `type: "Custom"`, `conversationProviderId: "6a5b91913953360948dd59f1`, and `altId`. Monitor first Monday executions and first real reply/unsubscribe closely before raising volume. On 2026-07-26, the send webhook's live registry updated `sms_1`, `sms_3`, and `sms_5` copy. On 2026-07-29, published `sms_4` was revised to remove `flower`, `pre-roll`, and the Facebook ad preview link while retaining neutral `regulated-industry` positioning; active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- **SimpleTexting GHL Conversations provider**: **LIVE** as of 2026-07-20. Separate GHL private app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`. `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) receives GHL outbound replies, validates provider ID, normalizes phone to E.164, checks `simpletext_stop` tag, and sends via the idempotent send workflow (`gwaEpWDpTIwsafi8`) → SimpleTexting API. Outbound campaign sends mirror into GHL Conversations via `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). `simpletexting_conversation_map` table created in Postgres keyed by `(conversation_provider_id, alt_id)`. GHL Conversations is the primary operator inbox for SimpleTexting SMS; Slack alert for inbound replies is preserved.
- **Unipile/Instagram**: Instagram DM Sequence (`iCnY6ccdHhfJg3sf`) is **unpublished**. It was misconfigured with the LinkedIn Unipile account ID and sent Instagram templates as LinkedIn DMs. Do not republish until it has a real Instagram Unipile account ID and account-type guard.
- **Instagram inbound bridge**: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active at `/webhook/lt-unipile-instagram-new-messages`. It normalizes Unipile Instagram inbound payloads, conservatively resolves an existing GHL contact before creating one, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token via `POST /oauth/locationToken`, and posts inbound messages into GHL Conversations under the `Instagram via Unipile` tab. Post-merge cleanup on 2026-07-16 repointed `instagram_conversation_map.id = 1` for chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`; the temporary duplicate `4V2oTmM7lWya3Nmtmp1Y` created during verification was deleted.
- **Social provider outbound router**: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active at `/webhook/lt-social-provider-outbound`. Fixed 2026-07-16: POST webhook `responseMode` now uses `responseNode`, map tables are created defensively, payload message text is preserved through Postgres lookup, and Unipile send uses the working `api42.unipile.com:17256/api/v1` base. Canonical provider IDs are SMS-type additional custom conversation providers: `Instagram via Unipile` = `6a58a1193cdfc36997580a68` and `LinkedIn via Unipile` = `6a58a14ff3023bea3783c152`. Inbound message API must use `type: "Custom"` with `conversationProviderId` + `altId`; do not include `emailTo`/`emailFrom`/`subject` or dummy contact phone/email data. Deleted Email provider IDs `6a5893d11e9368345005f66e` and `6a5892b9107668309b3f85ac` must not be reused. Verified Instagram and LinkedIn inbound as `TYPE_CUSTOM_PROVIDER_SMS`; Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` both map to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, with LinkedIn conversation `Ze8o3KbsrwuAXQ3KK5ge`. LinkedIn normalizer handles Unipile's form-encoded single-JSON-key webhook shape. Direct outbound router smoke tests after map repair passed: Instagram message `vjdEYSk9XD6R0I46oPWLwA`, LinkedIn message `C7I9944kWsSKutX2XhZEpA`.
- **Social provider bridge handoff**: Full build context, operator inbox runbook, monitoring gaps, and next steps for `LinkedIn via Unipile` + `Instagram via Unipile` GHL bidirectional messaging are in `docs/strategy/unipile-ghl-bidirectional-integration.md`. Read this before changing provider workflows.
- **Unipile/LinkedIn**: Active production path is dispatcher → acceptance/state sync → canonical DM sequence. Follower DM (`pq7XVajNFnnwMUTr`) is **unpublished**. Current published workflow inventory is documented in `Current Published Workflow Inventory` above. Guardrails block John-branded copy.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: Workflow exports staged in repo and corresponding SimpleTexting workflows are live in n8n. The canonical send webhook is `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`; template registry details are in `docs/outreach/sms_edited_templatekeys.md`. Current launch settings: `sms_drip`, 10 contacts/run, weekdays 10:15am and 3:00pm ET, 2-day inter-step delay, reply/STOP suppression.

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
