# Session Log: Report Correctness + Voice Migration + Backfill

Date: 2026-08-12 (Session 3)
Agent: OpenCode (lt-general model)

## Summary

Fixed 7 report correctness issues, migrated 12 broken Postgres nodes across 2 voice workflows, re-backfilled 12,639 ghl_contact_id values, and completed a full embedded secrets audit across 83 active n8n workflows.

## Fixes Applied

### 1. Executive Summary API — Duplicate JSON Keys (CRITICAL)
- **Workflow**: `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`)
- **Node**: `Build Query` (Code node)
- **Issue**: `vapiWeeklyPerformance` and `vapiWeeklyBreakdown` appeared 5 times each in the `summary_json` CTE's `jsonb_build_object()`. PostgreSQL allows duplicate keys but later values overwrite earlier ones — only the 5th occurrence survived. The CTEs `vapi_weekly` and `vapi_weekly_breakdown` ARE defined in the query (confirmed).
- **Fix**: Removed 4 duplicate pairs, keeping 1 of each.
- **Published**: version `d458117c-63a0-4666-a5dd-1620e9bde4fe` (versionId == activeVersionId)

### 2. Executive Summary API — Timezone Drift (HIGH)
- **Workflow**: `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`)
- **Node**: `Normalize Request` (Code node)
- **Issue**: `startDate` was computed using pure UTC operations (`new Date("${endDate}T00:00:00Z")`, `setUTCDate()`) instead of the configured `America/Los_Angeles` timezone. At timezone boundary hours, the window could drift by ±1 day.
- **Fix**: Replaced UTC date subtraction with `isoDateInTimezone(endDateObj)` for timezone-aware calculation.
- **Published**: Same version as above.

### 3. Executive Summary API — Missing Date Filters (HIGH)
- **Workflow**: `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`)
- **Node**: `Build Query` (Code node)
- **Issue**: `stageVelocity`, `sql_contacts`, and `pool_distribution` (4 sub-queries) had no `WHERE report_date BETWEEN` filter. They returned all-time values regardless of the selected period.
- **Fix**: Added `WHERE report_date BETWEEN $1::date AND $2::date` to all 6 queries. The `$1`/`$2` parameters were already passed by the Postgres node's `queryReplacement`.
- **Published**: Same version as above.

### 4. Campaign Channel Summary — Timezone Drift (HIGH)
- **Workflow**: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`)
- **Node**: `Normalize Campaign Window` (Code node)
- **Issue**: Default `end` date used `new Date().toISOString().slice(0, 10)` (UTC). Between 8 PM ET and midnight ET, the date would be one day ahead of the user's local date.
- **Fix**: Added `isoDateInTimezone()` function with `America/New_York` timezone. Start date also uses timezone-aware subtraction.
- **Published**: version `e3b9f13f-e589-4dd9-bc8d-98801ed8c654`

### 5. Voice Dialer — Postgres v2.6 Migration (CRITICAL)
- **Workflow**: `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`)
- **Issue**: 4 Postgres v2.6 nodes used `queryReplacement` parameterized queries, which silently fail in n8n's embedded task runner. The dialer was crashing on every execution (153 error runs) — it acquired a queue lock but couldn't release it.
- **Migrated nodes**:
  - `Postgres - Release Lock` — releases queue lock for no-phone/DNC contacts
  - `Postgres - Release Lock (Timezone)` — releases lock for outside-hours contacts
  - `Postgres - Mark Attempted` — increments attempt counter after call
  - `Postgres - Mark Vapi Start Failed` — marks queue entry failed
- **Pattern**: Each node converted from `n8n-nodes-base.postgres` v2.6 to `n8n-nodes-base.code` v2 with `require('pg')` direct connection. Uses the same Postgres credentials as the working Intake Poller and Call Outcome Ingest.
- **Published**: version `b8e9c57a-f81f-49fd-b469-1388320568c5`

### 5A. Voice Dialer Resolution Verification (2026-08-14)
- **Scope**: Shared scheduled Vapi outbound dialer issue, not a manual-dialer template/card issue. Any queue item entering the common release/skip path could be affected, regardless of campaign or job type.
- **Provider determination**: Failure occurred in n8n's `Postgres - Release Lock` node before a Vapi call was started. It was not a Twilio or Vapi provider error.
- **Verification**: Thirteen consecutive scheduled executions on 2026-08-13 succeeded after the direct-`pg` migration. Execution `746845` completed successfully through `Postgres - Release Lock`; `there is no parameter $1` did not recur.
- **Status**: Resolved and published in version `b8e9c57a-f81f-49fd-b469-1388320568c5`.

### 5B. Residual Voice Queue Enqueue Path (2026-08-14)
- **Finding**: The original dialer migration did not cover the separately active `LT - Voice Queue Enqueue` webhook (`XzcpOBi9YcIhJPck`). Its `Postgres - Insert or Noop` node still used Postgres v2.6 `$1`-`$5` placeholders with `queryReplacement`, so the same error could continue to appear when a contact entered through the enqueue webhook.
- **Fix**: Replaced that node with a direct `require('pg')` Code node, preserving the transaction, advisory contact lock, pending/in-progress deduplication, and queue insertion behavior.
- **Published**: version `42aba803-09b0-4118-a105-9161bebe66e9`; fresh live details confirm `versionId == activeVersionId`.
- **Provider determination**: This was also an n8n/Postgres persistence issue before any Vapi/Twilio call creation, not a Twilio outage.

### 5C. Voice Intake Poller Audit Fixes (2026-08-14)
- **Workflow**: `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`)
- **Fixes**: aligned the poller's terminal blocklist with the enqueue guard; changed suppressed outcomes from `skipped` to the connected `skip` route; surfaced GHL tag add/remove failures; and made direct-`pg` insert/no-op results explicit per contact.
- **Published**: version `5c464233-c79a-4f49-a809-de303f3b6136`.
- **Verification**: smoke execution `747051` completed successfully through contact search, classification, Apollo enrichment, and skipped-contact tag-removal branches.
- **Follow-up fix**: Apollo's HTTP response replaced the original classified item, so enrichment cleanup could remove only the fallback `vapi_queue` tag. Published version `d852a93d-b468-4b9b-8cc9-d4995131f926` resolves the source tag from `Classify Contacts`; execution `747053` verified `tagsRemoved: ["vapi_campaign_brand"]` with no workflow error.

### 6. Voice Callback — Postgres v2.5/v2.6 Migration (HIGH)
- **Workflow**: `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)
- **Issue**: 8 Postgres nodes (mix of v2.5 and v2.6) used parameterized queries vulnerable to the same `queryReplacement` bug. No errors observed yet (callbacks may work differently), but the dependency was fragile.
- **Migrated nodes**:
  - `Postgres - Update Status` — tool-call status update
  - `Postgres - Set DNC` — tool-call DNC marking
  - `Postgres - Log Outcome` — end-of-call outcome logging (generic pg wrapper)
  - `Postgres - Insert Attempt` — call attempt recording
  - `Postgres - Mark Queue Completed` — marks queue entry completed after EOC
  - `Postgres - Resolve Queue By Call ID` — correlates queue from Vapi call ID
  - `Postgres - Claim Timer State` — timer scheduling claim (generic pg wrapper)
  - `Postgres - Advance Phone Index` — rotates phone candidate on wrong number
- **Published**: version `c97480db-d741-4c7c-8705-f173296800ac`

### 7. ghl_contact_id Re-backfill (HIGH)
- **Table**: `emerging_pool_contacts`
- **Issue**: All 13,868 rows had NULL `ghl_contact_id` — the original backfill (13,755/13,868) was lost when the database was recreated during the encryption-key recovery.
- **Method**: 3-pass matching from GHL export CSVs:
  - Pass 1 (email): 4,642 matches
  - Pass 2 (phone): 5,742 matches
  - Pass 3 (name+company): 2,255 matches
  - Total: 12,639 matched / 1,229 unmatched
- **Unmatched**: Contacts not present in the GHL export CSVs (same category as the original 113 nulls)
- **CSVs used**: `Export_Contacts_brands pool_Jul_2026_5_24_AM.csv` (3,024 contacts), `Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv` (7,953 contacts)

### 8. Embedded Secrets Audit (HIGH)
- **Scope**: All 83 active/published n8n workflows
- **Findings**:
  - 12 CRITICAL: GHL PIT token in 8+ Config nodes, Vapi API key in dialer, Unipile API key in 2+ workflows, Postgres credentials in Code nodes, GHL OAuth client credentials in HTTP Request node
  - 5 HIGH: LinkedIn state-upsert secret, voice queue enqueue secret, call outcome ingest secret, Slack webhook URL
  - 2 MEDIUM: Unipile account IDs (identifiers, not secrets), Warm intake webhook auth
- **Remediation plan**: Migrate to Config nodes (Community Edition cannot use env vars in Code nodes) or n8n managed credentials where available. Priority: GHL PIT → Unipile → Vapi → Postgres → webhook secrets → OAuth.

### 9. LinkedIn State Backfill (MEDIUM)
- **Executed**: LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`) — succeeded (execution `743291`)
- **Executed**: LinkedIn Connection State Sync (`ceaKnz6E3onQrZpt`) — timed out at 60s task runner limit; will populate on normal 6-hour schedule
- **Result**: `linkedin_activity_events` has 28 rows; `linkedin_connection_state` will populate gradually

## Community Edition Architecture Constraint

**n8n Community Edition does NOT support environment variables inside Code nodes.** The `N8N_BLOCK_ENV_ACCESS_IN_NODE` setting blocks `$env.*` access. This is documented in the n8n configuration and confirmed by runtime errors (`access to env vars denied`).

**Canonical pattern**: Each workflow that needs secrets uses exactly one **Set node named `Config`** (type `n8n-nodes-base.set`, version 3.4). Code nodes read values via `$node['Config'].json.keyName`. This is the established convention across all LiveTransparent workflows.

**What this means for secret migration**:
- Do NOT attempt to use `$env.GHL_API_KEY` in Code nodes — it will fail
- Do NOT attempt to use `process.env.GHL_API_KEY` in Code nodes — it will fail
- Use Config nodes to store workflow-scoped secrets
- Use n8n managed credentials (httpHeaderAuth, postgres, oauth2) when the platform supports them
- The external task runner's `require('pg')` Code nodes CAN access `process.env` for Postgres connection (this is a runner-level exception, not a Code node feature)

## Post-Session Database State

| Table | Rows |
|-------|-----:|
| `report_raw_ghl_contacts` | 500 |
| `report_raw_ghl_opportunities` | 7,984 |
| `report_raw_ghl_pipeline_history` | 7,984 |
| `emerging_pool_contacts` (with ghl_contact_id) | 13,868 (12,639 matched) |
| `voice_call_queue` | 3 pending |
| `voice_call_attempt` | 0 |
| `report_raw_ghl_call_outcomes` | 0 |
| `Email_Events` | 0 |
| `DAN_Release_Log` | 0 |
| `Emerald_Release_Log` | 0 |
| `linkedin_connection_state` | 0 (State Sync pending) |
| `partnership_linkedin_connection_state` | 18 |
| `linkedin_activity_events` | 28 |

## Workflow Versions Published This Session

| Workflow | ID | Version | Changes |
|----------|-----|---------|---------|
| Executive Summary API | `Bukc0mgOD2r7V6ED` | `d458117c` | Duplicate keys, timezone drift, date filters |
| Campaign Channel Summary | `MvPLbUAN9IIQikxb` | `e3b9f13f` | Timezone drift |
| Outbound Dialer | `r7UjWLndmc6EqEUW` | `b8e9c57a` | 4 Postgres nodes → direct pg |
| Vapi Callback | `fx4UvKUWbqJEY3LK` | `c97480db` | 8 Postgres nodes → direct pg |

## Remaining Work (Ranked by Severity)

1. **HIGH — Secret migration**: Create Config nodes for GHL PIT (8+ workflows), Vapi API key (dialer/callback), Unipile API key (5+ workflows), Postgres credentials (Code nodes). Community Edition cannot use env vars in Code nodes — Config nodes are the canonical pattern. Then rotate exposed values.
2. **HIGH — Source coverage gaps**: `voice_call_attempt` (0), `Email_Events` (0), `DAN_Release_Log` (0), `Emerald_Release_Log` (0), `partnership_release_log` (0), `linkedin_connection_state` (0), SimpleTexting state/events (0). These will populate through live workflow activity — do NOT fabricate historical data.
3. **HIGH — 1,229 unmatched ghl_contact_id rows**: Contacts in `emerging_pool_contacts` not present in GHL export CSVs. Decide: skip (low-value contacts), manual GHL lookup, or re-export from GHL with broader filter.
4. **MEDIUM — Warm intake and SimpleTexting send authentication**: Review webhook authentication on `5nYzp9DgQUopzWhR` (SMS Tag), `OowP3sAd8c9paSKf` (Add Intake Tag), `SmMf8QIfysuxQJbG` (Email Inbound Tag). Several have empty shared-secret configuration.
5. **MEDIUM — OAuth social statistics**: GHL Social Planner statistics endpoint requires OAuth (PIT returns 401). Add OAuth-backed ingestion for reach/impressions/saves.
6. **MEDIUM — Native GHL report UI**: Add Sales Outreach/Warm stage widgets, DAN/Emerald/Vapi tag widgets, email widgets, page names, custom metrics through authenticated UI.
7. **LOW — Voice dialer verification**: Next scheduled execution of the migrated dialer should be monitored to confirm the direct `pg` nodes work in production.
8. **LOW — Legacy cleanup**: Remove disconnected legacy nodes, stale historical prose, temporary scripts, old export CSVs after live paths are stable.
5. **1,229 unmatched contacts**: Decide skip or manual match for contacts not in GHL exports
