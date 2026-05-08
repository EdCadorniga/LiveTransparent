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

## Current Progress Snapshot (updated 2026-05-08)
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

### Report Workflow Status (all verified active, updated 2026-05-05)
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

### Deferred / Inactive
- `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) — **built and tested** but blocked on OAuth2 scope (needs `webmasters.readonly` added to Google OAuth2 credential)
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
- **Unipile/LinkedIn**: `LT - GHL LinkedIn Connect Dispatcher` (`S32vc8pjJIBZZHLK`) is active and LIVE (dry-run off). Runs hourly Mon-Fri 10am-4pm EST. Uses `POST /contacts/search` with filter `contact.apollo_person_linkedin_url is_not_empty`, skips contacts tagged `linkedin_connection_requested`, processes 10/run from queue of 50, caps at 50/day via staticData. `LT - UNIPILE LinkedIn Connection Request` (`Zt8p2aYtIuY0HK18`) is active (internal test webhook).
- **GHL warm intake/routing**, **Apollo enrichment**, **Emerald/Cold outreach** workflows all active.
### Voice AI (Vapi + n8n) — Phase 2 (2026-05-07)
- **Phone**: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`)
- **All Vapi webhooks** route to: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback` (single merged path)
- **Production workflows**
  - `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — canonical merged callback + tool router; published
  - `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`1ogCy9ScVjtF0Cqf`) — canonical queue dialer; published
- **Archived / non-production workflows**
  - `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) — validation copy, archived in n8n
  - `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`) — archived test workflow
  - `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`) — archived test workflow
  - `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`) — archived test workflow
- **4 tools wired into callback workflow** (`fx4UvKUWbqJEY3LK`):
  - `update_lead_status` → GHL tag + Postgres disposition update
  - `add_to_dnc` → set `dnc=true` in `voice_call_queue` + GHL DNC tag
  - `log_call_outcome` → upsert `voice_call_attempt` with disposition/notes/followUpAt
  - `notify_sales` → Slack `#leads` alert (reuses `wl-slack-channel-update-v2` pattern)
- **VAPI_PHONE_NUMBER_ID** now set in `.env`
- **GHL_LOCATION_ID** now set in `.env` as `Zwz4relUXVPxx8uohnjV`
- **GHL_API_KEY** is now an alias of `GHL_PIT` in `.env` so voice workflow HTTP nodes resolve correctly
- Voice GHL smoke test completed on test contact `WWuQ3TgiaxFs97lSHWSn`:
  - tags `AI Call Attempted` and `do_not_call` added successfully
  - contact note write succeeded
  - readback confirmed tags are present
- Outbound Dialer (`1ogCy9ScVjtF0Cqf`) + Callback+Tools (`fx4UvKUWbqJEY3LK`) are the production pair in n8n

### Secret Hygiene (remaining work)
- SimpleTexting API tokens, GHL keys, and webhook secrets are still in workflow `Config` nodes.
- Move these into n8n credentials or env-backed config (per AGENTS.md:128).

## Agent Tooling
- Canonical Codex config lives at `C:\Users\edmon\.codex\config.toml`.
- Use `n8n-lt` as the canonical n8n MCP for this project (confirmed working).
- Prefer `n8n-lt` MCP or direct API calls before browser-based approaches.
- Use `ghl_official` as the primary GHL MCP, `ghl_workflows` as secondary.

## GHL and n8n Rules
- Prefer documented runbooks in `GHL Live Transparent CRM/` before making workflow changes.
- For n8n workflow edits, verify live state after every mutation.
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
   - Keep `fx4UvKUWbqJEY3LK` and `1ogCy9ScVjtF0Cqf` as the only production voice workflows.
   - Finish moving any remaining secrets out of workflow `Config` nodes into credentials or env-backed config.
   - In Vapi dashboard, keep the 4 tools and end-of-call webhook pointed at `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`.
2. Expose a richer contact-capture panel with both counts and conversion rates by channel and landing page.
3. Build matched funnel views by channel, campaign, and landing page.
4. Harden the Meta attribution view in the Executive Report so Meta-tagged visits and downstream calls/opportunities are visible without relying on spend metrics.
5. Build `WL - Nurture - 14 Day` workflow — moving a lead to `Nurture Active` (stage `98775f02-0018-4629-9e69-0b1fcab293eb`) currently has no email automation. Need to: apply `LT Nurture Active` tag, start 14-day nurture sequence, skip if tag already present.
6. Finish SimpleTexting hardening: move secrets out of workflow `Config` nodes into credentials.
7. GSC credential — re-authorize Google OAuth2 credential (`suzEHDZE7MwohGCr`) with `https://www.googleapis.com/auth/webmasters.readonly` scope, then activate GSC workflow.
