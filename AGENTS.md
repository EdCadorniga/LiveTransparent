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
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Paused (quality gate) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Paused (quality gate) |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Active |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Active |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Active |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active (hourly, no Slack reporting) |
| LT - Voice Campaign Brand (Alex) | 1d7c5d42-f0a4-4b58-9494-dbda3be3c657 | Created, not active |
| LT - Voice Campaign Dispensary (Jordan) | 056f2e50-8bdf-4257-ac45-4d575600c39d | Created, not active |

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
- callback_timeout -- terminal (set by reaper when queued > 24h)

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

## DAN Email Campaign -- Brands and Dispensaries (LIVE 2026-07-10)

### Dispatcher

| Workflow | ID | Status |
|----------|----|--------|
| LT - DAN Campaign Sender Release Dispatcher (Staged) | toUG1yPDmFG48KEP | Active (dryRun=false), hourly |

**Pipeline**: Schedule Trigger -> Config -> Ensure Release Log Table -> Fetch DAN Candidates -> Dispatch + Queue -> Write Release Log + Summary

**Config**: dryRun=false, candidateLimit=50, sender=cameron@livetransparent.com, senderFieldName=marketing_sender_email

**Enrollment tags applied**:
- Brands: Enrollment Queue - DAN - Brands
- Dispensaries: Enrollment Queue - DAN - Dispensaries

**Deduplication**: Per-contact + per-campaign via DAN_Release_Log table (UNIQUE on contact_id, campaign).

**DNC/unsubscribe protection** (two layers):
1. SQL-level: filters report_raw_ghl_contacts.tags_raw for do not contact, do not nurture, unsubscribed, opted out, seq enrolled - dan
2. Per-contact live check: GET /contacts/{id} before dispatching

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

- **SimpleTexting**: Send, delivery, inbound reply, and unsubscribe webhooks are active.
- **Unipile/Instagram**: DM Sequence workflow (iCnY6ccdHhfJg3sf) active, cron 0 12-22 * * 1-5, 4-message sequence to mutual followers. State tracked in instagram_dm_state. Unipile account V9eiHiDpRmCtan0YNdzsQw at api42.unipile.com:17256.
- **Unipile/LinkedIn**: 8 workflows active (re-enabled 2026-07-10). DM Sequence (d0tEtijajisIsYcs) + Follower DM (pq7XVajNFnnwMUTr) 0 12-22 * * 1-5. State Sync (ceaKnz6E3onQrZpt) 15 */6 * * *. Dispatcher (fXxw5lanZcDmUrst) */15 15-21 * * 1-5. Guardrails block John-branded copy. Acceptance Checker (3ttEvr5NMcQCS4Hp) at /webhook/lt-linkedin-connection-accepted.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: Workflow exports staged in repo. See docs/outreach/outreach_messages.docx for SMS source copy. Requirements: tag sends, shared reply-state tracking, #lead on response, unsubscribe handling.

## Key Files

- repomix-output.md
- .env
- Project Status and Next Steps.md
- GHL Live Transparent CRM/
- postgres/reporting-bootstrap.sql
- n8n/docker-compose.yml
- n8n/voice-agent/
- n8n/workflows/lt-linkedin-dm-sequence.ts
- n8n/workflows/lt-linkedin-connection-state-sync.ts
- n8n/workflows/lt-linkedin-connection-state-upsert.ts
- n8n/workflows/lt-linkedin-unipile-new-messages.ts
- n8n/workflows/lt-linkedin-connection-acceptance-checker.ts
- n8n/workflows/lt-apollo-queued-timeout-reaper.ts
- n8n/workflows/lt-emerging-pool-import.ts
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
