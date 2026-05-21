# LiveTransparent Agent Notes

## Project Context
- This project is deployed on a VPS using Coolify.
- Two containers are managed in Coolify: `n8n` and `reports`.
- Containers can reach each other over Coolify's internal network.
- `n8n` is publicly routed at `https://automations.livetransparent.com`.
- Report host is at `https://reports.livetransparent.com`.
- `bookstack/` and `qdrant/` assets are prepared but not deployed yet (future phases).

## Working Assumptions
- Prefer internal service-to-service communication over the Coolify network where possible.
- Use `automations.livetransparent.com` as the canonical n8n public host for webhook/editor URLs.
- Keep config values centralized in the root `.env` file (n8n/.env has been consolidated into root).
- Environment variables for n8n and Postgres are set in Coolify; the root `.env` is the reference copy.

## Current Progress Snapshot (updated 2026-05-20)
- **n8n-lt MCP is working** — confirmed connected and operational.
  - Uses `mcp-remote` with the remote endpoint `https://automations.livetransparent.com/mcp-server/http`.
  - Token lives in root `.env` as `N8N_MCP_ACCESS_TOKEN`.
- **n8n version**: `2.19.5` target (docker-compose pinned to same; redeploy in Coolify to apply).
- Codebase cleanup completed on 2026-05-05:
  - Deleted `config.toml.bak`, `config.toml.bk` (contained stale multi-project secrets).
  - Consolidated `n8n/.env` into root `.env`, deleted `n8n/.env`.
  - Deleted `package-lock.json`, `WEBSITE_ISSUES_AUDIT_2026-02-16.md`.
  - Cleaned ~60 stray temp files from root.
  - Backup directory deduplicated (45 canonical backups, 1 per live workflow).

### Report Workflow Status (all verified active, updated 2026-05-19)
| Workflow | ID | Status |
|----------|----|--------|
| LT - GHL Daily Leads Ingest | `osIJOgBmWITF5Yuv` | Active (rebuilt replacement) |
| LT - GHL Daily Sales Ingest | `aYT5oHcgmBALzHy5` | Active |
| LT - Report Attribution Bridge | `Y0TU7Il71JswxOBp` | Active |
| LT - Report Daily Rollups | `EUeOiRttoVLQ9zF9` | Active |
| LT - Report Executive Summary API | `Bukc0mgOD2r7V6ED` | Active |
| LT - Report QA and Alerts | `M5mXcDTFSko6EdHb` | Active |
| LT - Report Config Sync | `aomO3Z4AXJIgEvvN` | Active |
| LT - Report Publish Refresh | `3gXztCnBEN6sGINb` | Active |
| LT - Report Postgres Bootstrap Apply | `3XHThUiUSNa4sTb9` | Active |
| LT - Report Pipeline Velocity | `iFfwh0jpYUZoDhDR` | **Active** (computes stage velocity from pipeline history) |
| LT - GHL Daily Calls Ingest | `SqNQ0BYaTdcqyt1l` | **Inactive** (GHL conversations endpoint 404; awaiting API access) |
| LT - GHL Daily Appointments Ingest | `yWZVSqEcjTbMT3kG` | **Active** (GHL calendar events ingestion every 6h; calendarId `SrtXcFVyea7pFl3nTiIK`) |
| LT - GHL Daily Social Ingest | `QZoqCaTwDhbym80O` | **Active** (GHL Social Planner posts every 12h; 138 posts, 5 connected accounts) |
| LT - GA4 Daily Ingest | `6pCSGzFmrMDFL5Yq` | **Active** (GA4 enabled 2026-04-30) |
| LT - GA4 Traffic Rollup Bridge | `0P2AZcQYWYZjXbRi` | **Active** (bridges GA4 raw to rollup tables) |
| LT - GSC Daily Ingest | `xHqmCC1vOeZ11gCd` | **Active** (Search Console API daily ingest; creates raw GSC query/page/site rows) |
| LT - GSC Rollup Bridge | `fOVBHwti9rC3qrLV` | **Active** (daily 04:00 UTC; aggregates raw GSC → report_daily_summary gsc_*) |

### Deferred / Inactive
- `LT - GHL Executive Report Menu Sync` (`8YtaPmPnTXUkBDAd`) — one-time provision, inactive
- **Meta Ads API access is now live** — validated on 2026-05-05 with system user app token against active ad account `act_2186975138800404` (`Livetransparent-3`).
  - Root `.env` now holds `META_TOKEN` and `META_AD_ACCOUNT_ID`.
  - Direct Graph API validation succeeded for `/me`, `/act_2186975138800404`, and `/act_2186975138800404/insights`.
  - Insights auth is working; the smoke test returned `data: []`, which indicates no matching default-window rows rather than a permission failure.
  - Historical/non-empty Meta data is currently coming from `act_975543647768982` and `act_24843211111954088` through the staged ingest workflow.
  - The Executive Report should surface Meta through attribution-first reporting: Meta-tagged visits plus downstream lead/opportunity activity from GA4 + GHL bridge data. Spend is intentionally not required in the report yet.

### Known Data Issues
- **`closed_won = 0` is genuine** — verified against current opportunity data; no won deals are present yet.
- **GA4 traffic is now live** — 6 channels flowing through the pipeline (Email, Organic Social, Direct, Organic Search, Unassigned, Referral). Bridge updates `report_daily_summary`, `report_channel_daily_summary`, and `report_landing_page_daily_summary`.
- **GA reporting clobber fix is live** — `LT - Report Daily Rollups` now preserves GA-backed rows in `report_daily_summary`, `report_channel_daily_summary`, `report_utm_daily_summary`, and `report_landing_page_daily_summary` instead of deleting them during CRM rollups.
- **Rollups draft restored** — `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) no longer has the `PLACEHOLDER_SQL_CODE` draft issue. The draft was restored from the active workflow definition on 2026-05-02.
- **Daily-summary corrections are live in Rollups** — `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) now owns the dedupe patch for `opportunitiesCreated`, the stage-aware `closed_won` check, and `meetings_booked` dedupe in production.
- **Funnel-efficiency metrics are live** — `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) now returns `session_to_contact_rate`, `contact_to_opportunity_rate`, `opportunity_to_meeting_rate`, `meeting_to_closed_won_rate`, and `session_to_form_rate`; the embedded report consumes them.
- **Funnel semantics normalized** — `contact_to_opportunity_rate` now uses a contact-safe cohort metric in `LT - Report Executive Summary API` instead of the raw multi-opportunity rollup total.
- **Current cohort result** — the present 30-day new-contact cohort is showing `contact_to_opportunity_rate = 0`, which means no newly created contacts in the window are currently matching through to opportunities under the stricter cohort-safe definition.
- **Attribution coverage is materially improved** — after normalizing raw contact ids, adding GHL attribution fallbacks, and rebuilding the rolling bridge window, the current 30-day cohort is now: `cohortContacts = 97`, `contactsWithSourceFields = 45`, `contactsWithBridgeMatch = 45`, `contactsWithSaleMatch = 22`, `contactBridgeMatchRate = 46.4%`, `opportunityMatchCoverageRate = 100%`.
- **Pipeline velocity is live** — `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`) computes stage-by-stage timing from `report_raw_ghl_pipeline_history` using CTE + LEAD window function, upserts into `report_stage_velocity_summary` (14 stages across 3 pipelines) and `report_opp_stage_timeline` (50,522 rows). Data surfaces in Executive Report via `stageVelocity` field.

### Other Live Systems
- **SimpleTexting**: SMS Send, Delivery Events, Inbound Reply, and Unsubscribe webhooks are active. Pool Dispatcher and Campaign Sequencer are inactive by design.
- **Unipile/LinkedIn**: `LT - GHL LinkedIn Connect Dispatcher` (`S32vc8pjJIBZZHLK`) is active and LIVE (dry-run off). Runs hourly Mon-Fri 10am-4pm EST. Uses `POST /contacts/search` with filter `contact.apollo_person_linkedin_url is_not_empty`, skips contacts tagged `linkedin_connection_requested`, processes 10/run from queue of 50, caps at 50/day via staticData. `LT - UNIPILE LinkedIn Connection Request (Internal Test)` (`Zt8p2aYtIuY0HK18`) was **archived 2026-05-20** (never received any webhook invocations). **2026-05-20 fix**: Config node defaultMessage updated from "John" to "Cameron" (message sends through Cameron's Unipile account).
- **GHL warm intake/routing**, **Apollo enrichment**, **Emerald/Cold outreach** workflows all active.

### Apollo Enrichment Timeout Fix (2026-05-14)
- Identified root cause: staged intake sets `queued` before calling Apollo with `webhook_url`; if callback never arrives, contact stays stuck
- Modified staged intake (`WuxgTa0EEL1mb2SA`): added timeout check — if already `queued` for >24h (via new field `Apollo Phone Enrichment Queued At`), sets `callback_timeout` and skips Apollo
- Modified callback handler V4 (`U7c6byTLXAMgcS75`): wrapped in try-catch; on error sets status to `callback_failed`
- Created GHL custom field `Apollo Phone Enrichment Queued At` (ID: `NgC3xGTh0laQ9ArTnude`, dataType: `DATE`)
- Bulk-updated 21 previously stuck `queued` contacts to `callback_timeout` via direct GHL API (POST `/contacts/search` with filter `{"field":"customFields.rgYJ7UqoznGoe3WeUAtH","operator":"eq","value":"queued"}`)
- Verified: 0 queued, 96 callback_timeout, 560 enriched, 0 failed/processing
### Voice AI (Vapi + n8n) — Phase 2 (2026-05-18)
- **Phone**: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`)
- **All Vapi webhooks** route to: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback` (single merged path)
- **Production workflows**
  - `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — canonical merged callback + tool router; active
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — **clean replacement** queue dialer (created 2026-05-19); active. Raw JSON import is the reliable update path for this workflow because it preserves `Switch` nodes and the exact n8n graph shape. Runs Mon-Fri 9am-5pm CT only. 72h cooldown. All fixes applied: proper cron interval, Postgres credentials, business hours guard, contact-TZ-aware scheduling, GHL call note on dispatch.
  - `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — Active. Polls GHL for `vapi_queue` tagged contacts. Added `hasValidPhone` E.164 bypass: if phone exists, enqueues directly skipping Apollo enrichment.
  - `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — Active. Webhook enqueue (allows NULL phone).
  - `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — Active. Webhook dequeue → Vapi call.
  - `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — Active. GHL call webhooks → Postgres + Slack.
- **Archived / non-production workflows** (all archived in n8n)
  - `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) — validation copy
  - `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`) — archived test
  - `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`) — archived test
  - `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`) — archived test
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`orJrDqR6hQjgPLpg`) — original draft (6 nodes, no cooldown, no phone check)
  - `LT - Voice Agent V1 Outbound Dialer (Vapi) v2` (`UUTjW9GZX2lJ6zpt`) — ghost workflow (0 nodes, created accidentally)
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`1ogCy9ScVjtF0Cqf`) — original broken dialer (missing cron interval, empty PG credentials, stub business hours code; archived 2026-05-19)
- **4 tools wired into callback workflow** (`fx4UvKUWbqJEY3LK`):
  - `update_lead_status` → GHL tag + Postgres disposition update
  - `add_to_dnc` → set `dnc=true` in `voice_call_queue` + GHL DNC tag
  - `log_call_outcome` → upsert `voice_call_attempt` with disposition/notes/followUpAt
  - `notify_sales` → Slack `#leads` alert (reuses `wl-slack-channel-update-v2` pattern)
- **VAPI_PHONE_NUMBER_ID** now set in `.env`
- **GHL_LOCATION_ID** now set in `.env` as `Zwz4relUXVPxx8uohnjV`
- **GHL_API_KEY** is now an alias of `GHL_PIT` in `.env` so voice workflow HTTP nodes resolve correctly
- **Voice GHL smoke test** completed on test contact `WWuQ3TgiaxFs97lSHWSn`
- **Dialer pipeline** (2026-05-18 update): Cron → business hours guard (Mon-Fri 9am-5pm CT) → fetch+lock → guard → if empty→end | else → HTTP GET GHL contact → Code check phone → if phone missing→release lock→end | else → HTTP POST Vapi call → Postgres Mark Attempted (attempt_count+1, next_attempt_at=NOW+72h) → GHL note. 72h cooldown prevents redial loop.
- **Intake pipeline** (2026-05-18 update): Cron 10min → search GHL for `vapi_queue` tag → for each contact: if phone matches `/^\+\d{7,15}$/` → enqueue immediately (bypass enrichment); terminal enrichment statuses → remove tag + skip; enriched → remove tag + enqueue; queued → skip; empty → set enrichment flag + enqueue immediately → remove tag.

### Dialer Clean Replacement (2026-05-19)
- **Problem**: `1ogCy9ScVjtF0Cqf` had 3 configuration bugs making it inaccessible in UI: missing `minutesInterval` on cron trigger, empty credential names on all 4 Postgres nodes (type `postgres` referenced with blank name), and stub `return [{ json: {} }]` business hours code node
- **Fix**: Created clean replacement `r7UjWLndmc6EqEUW` via n8n SDK with all fixes — proper `minutesInterval: 1`, `newCredential('Postgres account')` on all 4 PG nodes, real CT business hours code with contact-TZ-aware scheduling, GHL call note on dispatch, 72h cooldown
- **Old workflow** `1ogCy9ScVjtF0Cqf` archived after replacement validated
- **Activation**: Still requires UI toggle — API activation endpoint remains broken (500 "object is not iterable") on this instance
- **Source code**: `n8n/voice-agent/dialer-workflow-clean.mjs`

### VAPI Webhook 404 Fix (2026-05-18)
- **Root cause**: Workflow `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) webhook node was listening at `/webhook/voice-callback`, but VAPI dashboard was configured to POST to `/webhook/lt-voice-agent-vapi-callback`
- **Fix**: Updated webhook path via `PATCH /rest/workflows/fx4UvKUWbqJEY3LK` (REST API) — `PUT` returned 404 on n8n 2.19.5; `PATCH` succeeded
- **Key discovery**: n8n REST login requires `emailOrLdapLoginId` field (not `email`) in the JSON body due to LDAP/SSO setup
- **Verification**: Test webhook execution `29344` completed with `status: success`; no deactivation/reactivation needed — n8n auto-re-registered the trigger
- **Now matches**: Canonical path from `AGENTS.md` line 84 and VAPI dashboard configuration

### Voice Agent `vapi_*` Tag Inventory (documented 2026-05-20)
All tags live-applied by callback workflow `fx4UvKUWbqJEY3LK`:

| Tag | When | Applied By |
|-----|------|------------|
| `vapi_call_attempted` | Assistant calls `update_lead_status` during call | `GHL - Update Tags` node |
| `vapi_no_answer` | Customer did not answer | End-of-call event `GHL - Apply Tags` |
| `vapi_voicemail` | Voicemail left (paired with `vapi_voicemail_left`) | End-of-call event |
| `vapi_voicemail_left` | Voicemail left (paired with `vapi_voicemail`) | End-of-call event |
| `vapi_busy` | Customer was busy | End-of-call event |
| `vapi_wrong_number` | Wrong number reached | End-of-call event |
| `vapi_contact_disconnected` | Customer dropped during call | End-of-call event |
| `vapi_qualified` | Human answered, high-value disposition | End-of-call event (unchanged) |
| `vapi_nurture` | *(legacy)* No longer emitted — replaced by `vapi_interest_*` | — |
| `vapi_human_answered` | Vapi detected a human answered (base enrichment tag) | End-of-call event (added 2026-05-20) |
| `vapi_interested` | Human answered + `successEvaluation=true` + meaningful call | End-of-call event (added 2026-05-20) |
| `vapi_not_interested` | Human answered + `successEvaluation=false` + meaningful call | End-of-call event (added 2026-05-20) |
| `vapi_interest_unknown` | Human answered but couldn't gauge interest (silence/short call) | End-of-call event (added 2026-05-20) |
| `vapi_dnc` | Assistant calls `add_to_dnc` tool | `GHL - DNC Tag` node |

Cross-reference: GHL custom field `Bad Data Reasons` (`contact.bad_data_reasons`, ID `QKbRQD4mekBtHQsqx24O`, type `MULTIPLE_OPTIONS`) — options: "Invalid number", "Number does not belong to contact", "Company not related to business", "Competitor". Future report should intersect Bad Data Reasons with `vapi_*` tags.

### Voice Agent Documentation Cleanup (2026-05-20)
- **4 stale docs fixed** after verifying live workflow IDs via n8n SDK:
  - `runbooks/Vapi_Outbound_Call_Training.md`: Updated dialer WF ID `1ogCy9ScVjtF0Cqf`→`r7UjWLndmc6EqEUW`, replaced old tags `AI Call Attempted`/`do_not_call` with `vapi_*` references, expanded disposition table with all outcomes, added dequeue trigger info
  - `runbooks/Voice_Agent_Operations_Runbook.md`: Fixed WF ID and webhook URL `/webhook/voice-callback`→`/webhook/lt-voice-agent-vapi-callback`, added tag verification items to QA checklist
  - `README.md`: Fixed dialer WF ID
  - `Voice_Agent_V1_Implementation_Spec.md`: Stripped old `AI Call Attempted`/`do_not_call` tag references, cross-referenced to current `vapi_*` tag system
- **Verification**: Confirmed `r7UjWLndmc6EqEUW` is active (created 2026-05-18), `fx4UvKUWbqJEY3LK` is active with webhook path `/webhook/lt-voice-agent-vapi-callback`

### Voice Agent `successEvaluation` Fix (2026-05-20)
- **Root cause**: Vapi assistant `LT Voice Agent V1 Outbound` (`3f9bbfd2`) had `analysisPlan.successEvaluationPlan.enabled = false`, so `analysis.successEvaluation` was never populated on any call. The callback workflow's code node correctly checks `successEvaluation` but it was always `{}`/falsy, causing all "human answered" paths to emit `vapi_nurture` instead of `vapi_qualified`.
- **Fix**: PATCHed the Vapi assistant to set `successEvaluationPlan.enabled = true` (rubric type: `PassFail` — Vapi AI evaluates pass/fail based on conversation). Verified via API.
- **Effect**: Future calls will populate `analysis.successEvaluation` as a boolean. The callback workflow `fx4UvKUWbqJEY3LK` already handles this correctly — calls where the prospect is interested will now fire `vapi_qualified` instead of `vapi_nurture`.
- **Retroactive tag**: 8 failed-connection contacts (twilio-failed-to-connect-call / call.start.error-get-transport) that had no vapi tag applied were backfilled with `vapi_call_attempted` via GHL API (2026-05-20).
- **Caution**: `vapi_qualified` will only fire for calls placed AFTER this config change. Past calls remain with their existing tags.

### VAPI Friday Performance (2026-05-15)
- **Total calls**: 181 (queried by full CT business day, not UTC day)
- **Per outcome**:
  | Outcome | Count |
  |---------|-------|
  | Voicemail | 71 |
  | Customer busy | 50 |
  | Silence timed out | 46 |
  | Customer ended call | 7 |
  | Assistant forwarded call | 6 |
  | Customer did not answer | 1 |
- **Dialer hours**: 10am-5pm CT Mon-Fri (business hours guard); calls spanned 13:55–23:55 UTC (8:55am–6:55pm CT)
- **Call volume by day**: Wed 14 → Thu 44 → Fri 181 (ramping up through first full week)
- ⚠ Query must use midnight-CT to midnight-CT range (`T05:00Z` to `T+1T05:00Z`) — UTC-midnight filter clips early/late calls
- **Source**: VAPI REST API `GET /call` with `createdAtGt`/`createdAtLt` filters

### Secret Hygiene (remaining work)
- SimpleTexting API tokens, GHL keys, and webhook secrets are still in workflow `Config` nodes.
- Move these into n8n credentials or env-backed config (per AGENTS.md:128).
- For voice workflow HTTP nodes, prefer reading secrets from the workflow `Config` node rather than `$env`; node runtime env access can be denied in n8n.

## Agent Tooling
- Canonical Codex config lives at `C:\Users\edmon\.codex\config.toml`.
- Use `n8n-lt` as the canonical n8n MCP for this project (confirmed working).
- Prefer `n8n-lt` MCP or direct API calls before browser-based approaches.
- Use `ghl_official` as the primary GHL MCP, `ghl_workflows` as secondary.

## GHL and n8n Rules
- Prefer documented runbooks in `GHL Live Transparent CRM/` before making workflow changes.
- For n8n workflow edits, verify live state after every mutation.
- Before declaring a workflow fixed, audit the live workflow and at least one recent execution if the issue was runtime-related.
- Fetch first, patch second: always read the live workflow before editing, then modify only the necessary nodes and connections.
- Preserve graph integrity: keep existing node IDs for unchanged nodes and keep the connections map aligned with every referenced node.
- Use `Config` nodes when workflow nodes need secrets or constants and n8n runtime env access is blocked or unreliable.
- Prefer `Switch` nodes over `IF` nodes when branching workflow paths in voice automations unless there is a strong reason not to.
- Keep voice-workflow expressions in the exact form the field expects, typically `={{ ... }}` with node references like `$('Node Name').item.json.field`.
- When preserving exact node types matters, use raw n8n workflow JSON import/update instead of the SDK builder path; the builder path can flatten or lose `Switch` nodes in voice workflows.
- If a workflow relies on raw `Switch` nodes, keep them in the n8n schema form (`n8n-nodes-base.switch`, `typeVersion: 3.4`, `parameters.rules.values`, `conditions.options.version: 3`).
- When the report data needs to be validated end to end, rerun: leads ingest → attribution bridge → daily rollups → executive summary.

## Paths and Layout
- Keep Docker and service-specific assets under their service folders (`n8n/`, `postgres/`, `reports/`).
- Place service docs close to the service they describe.
- Keep marketing assets under `marketing/`.
- BookStack and Qdrant are future-phase; keep assets under `bookstack/` and `qdrant/` respectively.

## Key File Map
- `.env` — Root secrets reference (n8n, GHL, SimpleTexting, Unipile, GA4)
- `LiveTransparent Report Plan.md` — Step-by-step report build plan
- `GHL Live Transparent CRM/Operating Snapshot.md` — Live GHL/n8n operating summary
- `GHL Live Transparent CRM/Report Data Contract.md` — GHL-first report data contract
- `postgres/reporting-bootstrap.sql` — Postgres reporting schema
- `n8n/docker-compose.yml` — n8n service definition
- `n8n/REPORTING_IMPLEMENTATION.md` — Report pipeline build scaffold
- `plan.md` — Active implementation plan for Vapi+n8n outbound voice agent
- `n8n/voice-agent/` — Voice agent specs, prompt policy, schema, workflow JSON, runbooks
- `reports/embed/executive/index.html` — Embedded executive report SPA
- `reports/nginx.conf` — Nginx config (proxies /api/report/ to n8n webhook)
- `Backup of all n8n workflows/` — Canonical workflow backups (45 files, 1 per live workflow)

## Immediate Next Steps (priority order)
1. **Voice Agent Phase 2 hardening**:
     - Keep `fx4UvKUWbqJEY3LK` and `r7UjWLndmc6EqEUW` as the only production voice workflows.
     - Finish moving any remaining secrets out of workflow `Config` nodes into credentials or env-backed config.
     - In Vapi dashboard, keep the 4 tools and end-of-call webhook pointed at `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`.
     - Use raw JSON import/update for dialer patches so the live UI preserves `Switch` nodes and `Config`-backed HTTP auth.
2. Expose a richer contact-capture panel with both counts and conversion rates by channel and landing page.
3. Build matched funnel views by channel, campaign, and landing page.
4. Harden the Meta attribution view in the Executive Report so Meta-tagged visits and downstream calls/opportunities are visible without relying on spend metrics.
5. Build `WL - Nurture - 14 Day` workflow — moving a lead to `Nurture Active` (stage `98775f02-0018-4629-9e69-0b1fcab293eb`) currently has no email automation. Need to: apply `LT Nurture Active` tag, start 14-day nurture sequence, skip if tag already present.
6. Finish SimpleTexting hardening: move secrets out of workflow `Config` nodes into credentials.
7. **GSC pipeline is fully live** — `LT - GSC Daily Ingest` writes raw queries to `report_raw_gsc_queries`; `LT - GSC Rollup Bridge` aggregates into `report_daily_summary.gsc_*` daily at 04:00 UTC; Executive Summary API reads both sources; frontend renders clicks, impressions, unique visitors, CTR, and avg position. Keep the Search Console credential valid.
8. Build a cross-report intersecting GHL `Bad Data Reasons` custom field with `vapi_*` tags to identify contacts misclassified for Voice AI cadence.
