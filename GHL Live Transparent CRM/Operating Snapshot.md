# Live Transparent CRM Operating Snapshot

Updated: 2026-07-16

## Purpose
This is the live-state summary for the Live Transparent GHL sub-account.
Use it for current decisions. Use the deeper runbooks for implementation detail.

## Live Context
- Location: `Live Transparent`
- Location ID: `Zwz4relUXVPxx8uohnjV`
- Timezone: `America/Los_Angeles`
- Public n8n host: `https://automations.livetransparent.com`
- n8n version: `2.25.3` (upgraded from `2.19.5` on 2026-06-05 to fix cron scheduler issue)

## Live Assumptions
- Treat pipeline/stage logic as ID-driven even when docs show human-readable names.
- Prefer internal service-to-service calls over public hops when possible.
- Use `n8n-lt` to verify live workflow state before runtime changes.
- Use `ghl_official` first for supported GHL reads and writes.
- Treat `ghl_katwill_*` as secondary.
- Current PIT/auth state:
  - `GHL_PIT` in root `.env` was updated and validated against location-scoped GHL contact/opportunity queries.
  - `GHL_API_KEY` is aliased to `GHL_PIT` in root `.env` for workflow compatibility.
  - Both tokens `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28` (LinkedIn) and the main PIT are valid.
- If an MCP wrapper fails on a valid endpoint, verify through direct GHL API before assuming the PIT is invalid.
- GA4/GSC traffic is not available natively in GHL and must be pulled into the report layer separately.

## Active Pipelines
- `Warm`
  - `New`
  - `Qualified (MQL)`
  - `Routed to Outreach`
  - `Nurture Active`
  - `Disqualified`
- `Sales Outreach`
  - `New`
  - `Attempting Contact 1st Attempt`
  - `2nd attempt`
  - `3rd attempt`
  - `Engaged`
  - `Meeting Requested`
  - `Booked`
  - `Unresponsive`
- `Sales`
  - `Discovery Scheduled`
  - `Discovery Completed`
  - `Proposal Sent`
  - `Negotiation`
  - `Closed Won`
  - `Closed Lost`

## Reporting-Critical Field Families
Keep these aligned with routing and report logic:
- First/last touch UTMs:
  - source, medium, campaign, content, term, landing page
- Warm and routing metadata:
  - `Warm Source`
  - `Warm Trigger Type`
  - `Lead Temperature`
  - `LT Last Routing Channel`
  - `LT Last Routing Reason`
  - `LT Last Routed At`
  - `LT Route Lock Until`
  - `LT Routing Priority`
  - `LT Last Event Fingerprint`
  - `LT Last Event At`
- Apollo enrichment:
  - `Apollo Phone Enrichment Status` (`rgYJ7UqoznGoe3WeUAtH`)
  - `Apollo Phone Enrichment Queued At` (`NgC3xGTh0laQ9ArTnude`)
  - `Enrich Phone via Apollo` (`gdJDuZelIxEBE6n9i5Q6`)
- Exact field IDs live in `Warm_Lead_Conflict_Safe_Implementation_Spec.md`.

## Active Workflow Families

### Warm Intake and Routing
- `GHL Warm Intake - Add Intake Tag (Webhook)` — active
- `GHL Warm Intake - Email Inbound Tag (Webhook)` — inactive (paused)
- `GHL Warm Intake - SMS Tag (Webhook)` — active
- `GHL Warm Intake - Referral Tag (Webhook)` — active
- `GHL Warm Intake - Email Outbound Tag (Webhook)` — inactive (paused)
- `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)` — active
- `WF - Master Warm Intake and Routing` — active (GHL-side)
- `WF - Warm Channel Micro Entry` — active (GHL-side)

### Apollo Enrichment
- `GHL Apollo Enrichment - Webhook Intake (Sheet First)` (`WmKAhG7mIaXonNsh`) — active
- `GHL Apollo Enrichment - Phone Webhook Intake (Staged)` (`WuxgTa0EEL1mb2SA`) — active (API key rotated 2026-06-05)
- `GHL Apollo Phone Enrichment - Callback Handler` (`YaWizRnw7XmkcvZH`) — active
- `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`) — active (zero deliveries since 2026-05-13, root cause unknown)
- `LT - Apollo Queued Timeout Reaper` (`RL5ZyUoshSPbmVA1`) — active, hourly backstop for stuck `queued` contacts

### Voice System (All Paused 2026-06-05)
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — paused
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — paused
- `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — paused
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — paused
- `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — paused
- `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — paused

### SimpleTexting
- `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) — active
- `LT - SimpleTexting Pool Dispatcher (Staged)` (`usxYXSuc4ahw40V3`) — active
- `LT - SimpleTexting Campaign Sequencer (Staged)` (`7mSiivR3NhtLIcNz`) — active (triggerCount=0)
- `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) — active
- `LT - SimpleTexting Delivery Events (Webhook)` (`AEi1VCzkLvaYFr4U`) — active
- `LT - SimpleTexting Unsubscribe Events (Webhook)` (`IyBKMkpYQ7pa0C8V`) — active

### LinkedIn/Unipile Pipeline
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) — active, `15 */6 * * *`
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) — active, `0 15-21 * * 1-5`
- `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) — active, `0 12-22 * * 1-5`
- `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) — active (webhook receiver)
- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) — active; posts inbound LinkedIn messages into GHL Conversations under `LinkedIn via Unipile` using canonical provider `6a58a14ff3023bea3783c152`.
- `LT - LinkedIn Connection Request (Unipile) (Internal Test)` (`Zt8p2aYtIuY0HK18`) — active (test)
- Verified 2026-06-03: sync scans 101/matches 100, dispatcher sent 10, DM sent 2

### Social Provider Bridge (GHL Custom Providers + Unipile)
- Full handoff: `../docs/strategy/unipile-ghl-bidirectional-integration.md`
- GHL provider `LinkedIn via Unipile` (`6a58a14ff3023bea3783c152`) — canonical SMS-type additional custom conversation provider for LinkedIn via Unipile.
- GHL provider `Instagram via Unipile` (`6a58a1193cdfc36997580a68`) — canonical SMS-type additional custom conversation provider for Instagram via Unipile; inbound, direct router smoke tests, GHL UI outbound reply, and dedup replay succeeded.
- Deleted Email providers must not be reused: LinkedIn `6a5892b9107668309b3f85ac`, Instagram `6a5893d11e9368345005f66e`. Legacy SMS providers remain reference/transition only: LinkedIn `6a5853a51e93687696053bf8`, Instagram `6a5853d33cdfc31a8c572766`.
- `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) — active; receives GHL provider outbound replies at `/webhook/lt-social-provider-outbound` and routes to Unipile via conversation map tables.
- `LT - GHL OAuth Callback` (`UnSWPnVoUy3tNJkX`) — active; captures marketplace app OAuth callbacks at `/webhook/ghl-oauth-callback`.
- `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) — active; receives Instagram inbound payloads at `/webhook/lt-unipile-instagram-new-messages`, conservatively resolves existing GHL contacts before creating, posts messages into GHL Conversations, and persists `instagram_conversation_map`. Post-merge map repair verified row `1` points chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`.
- `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) — unpublished; was misconfigured with the LinkedIn Unipile account ID.
- `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`) — unpublished; redundant with canonical LinkedIn DM sequence.

### Emerald (Staged — Marketing Email Paused 2026-06-05)
- All 7 Emerald workflows are inactive (staged by design since pause):
  - `LT - Emerald CSV -> Postgres Ingest (Staged)` — inactive
  - `LT - Emerald CSV -> GHL Import (DryRun, Staged)` — inactive
  - `LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged)` — inactive
  - `LT - Emerald Campaign Sender Release Dispatcher (Staged)` — inactive
  - `LT - Emerald Intro Sent -> P2 Queue Dispatcher (Staged)` — inactive
  - `LT - Emerald Executive SSO -> Company Sync (Staged)` — inactive
  - `LT - Emerald Intro Backfill Tagger (Staged)` — inactive
- Backfill tagger staged 3,566 pending contacts in `seq emerald - intro backfill pending`

### Cold Outreach (Staged)
- All 3 workflows inactive by design:
  - `LT - Cold Outreach CSV -> Postgres Ingest (Staged)` — inactive
  - `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)` — inactive
  - `LT - Cold Outreach Sender Release Dispatcher (Staged)` — inactive

### Reporting Workflows (All Active)
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — active (every 60 min)
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) — active
- `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`) — active (4hr schedule)
- `LT - GHL Daily Appointments Ingest` (`yWZVSqEcjTbMT3kG`) — active
- `LT - GHL Daily Social Ingest` (`QZoqCaTwDhbym80O`) — active
- `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) — active
- `LT - GA4 Traffic Rollup Bridge` (`0P2AZcQYWYZjXbRi`) — active
- `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) — active
- `LT - GSC Rollup Bridge` (`fOVBHwti9rC3qrLV`) — active
- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) — active
- `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) — active (90-day backfill, +email columns 2026-07-21)
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) — active (+MQL/SQL/LinkedIn/Vapi/Pool/Email sections 2026-07-21)
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) — active
- `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) — active
- `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`) — active
- `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`) — active
- `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`) — active
- `LT - Email Event Ingest` (`ZrqFN8qLKO8eVHDc`) — active
- `LT - Company MQL Google Sheets Sync` (`9Y3Kedm768kkwwSV`) — active (daily 6am ET)

Deferred by design:
- `LT - GHL Executive Report Menu Sync` (`8YtaPmPnTXUkBDAd`) — inactive (one-time provision)

Known issues (resolved 2026-07-21):
- ~~`opportunitiesCreated` inflation — suspect rollup/SQL counting bug~~ → Resolved
- ~~`closed_won = 0` — needs verification whether genuine or mapping gap~~ → Stage names NULL in raw data; resolved via stage ID fallback in Executive Summary SQL
- ~~`stage_movers = 0`~~ → Fixed (was 0, now 93): removed date filter from `opportunity_traces` CTE, added stage ID resolution

## Special Live Rules
- The regulated ads booking path is the only booking flow that currently auto-hands off into `Sales -> Discovery Scheduled`.
- The executive report should combine GA4 traffic, GSC visibility, and GHL leads/sales.
- GHL alone is not sufficient for traffic reporting.

## Runtime Update Rule
- Verify before mutating.
- Mutate once.
- Re-read the live workflow or object after the change.
- Do not trust an MCP mutation response alone if it can drift from live state.

## Reference Docs
- `../Project Status and Next Steps.md`
- `../AGENTS.md`
- `Report Data Contract.md`
- `GHL_Snapshot_Build_Spec_LinkedIn_Micro_Workflows.md`
- `GHL_SimpleTexting_Access_Workflow.md`
- `GHL_Intake_Webhook_Sender_Automations_Checklist.md`
- `Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- `Pipeline_Process_Training_Guide.md`
- `Pipeline_Quick_Reference.md`
- `RB2B_Website_Visitor_Intake_Workflow.md`
