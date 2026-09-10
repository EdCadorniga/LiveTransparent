# Executive Report — Phase 3/5, Owner Seeding, GA4/GSC Diagnosis (2026-09-09)

**Status:** Follow-up session to Phases 1–2 (`2026-09-09-executive-report-sdr-attribution-phase1-2.md`) and Phase 4 (`…-phase4-lead-source.md`). This session: (a) identified + seeded the unknown owners, (b) diagnosed why GA4/GSC are stale, (c) **built + enabled the Phase 3 meeting-outcome helper (operator-approved)**, (d) fixed the Phase 5 sign-off scope + MQL reconciliation. Only GHL-token-free report changes; no credentials rotated.

## 1. Task 2 — Unknown owners identified and seeded (DONE, verified live)

- **`ck6TRlU3wnTmMxuVpn5F` = Janvi Mahajan** (`janvi@livetransparent.com`, GHL role account/admin). Confirmed two ways:
  - Live GHL users list `GET /users/?locationId=Zwz4relUXVPxx8uohnjV` (route is `/users/`, NOT `/users/location/{id}` which 404s for this PIT) returned `{id: ck6TRlU3wnTmMxuVpn5F, name: "Janvi Mahajan", email: "janvi@livetransparent.com"}`.
  - The 5 opps owned by `ck6TRlU3…` include **Strider Peterson – Partnership**, which the 2026-08-08 GHL Native Report audit already recorded as "assigned to Janvi".
- **Full GHL user roster found** (all account admins on the sub-account): Cameron `03p5GatJBH7i9zjMaIzm`, Ed `gePIeuHOEsAiPVA1mfOR`, Janvi `ck6TRlU3wnTmMxuVpn5F`, Jason `yU85G6kfhtW4vUtx3QE6`, Marc `sqGx5rp3oAUG610NXyjU`, Kevin Lagudgud `7s3brzxGF4WSiz95DPkF`, Mike deVries `D8NgkeZYX481rR4J2gOc`, Remus Borela `R5VljBpXah3LaVXFNfCV`.
- **`postgres/reporting-bootstrap.sql`** seed updated (staged/uncommitted): added Janvi (role `marketing`, `is_sdr=false`, note "Partnership + qualification gate owner; formerly 'Unknown SDR'"), plus Kevin/Mike/Remus as informational `staff` non-SDR rows so no future owner renders as "Unknown SDR". Marc's email corrected from NULL → `marc@livetransparent.com`.
- **Applied + verified on live DB** (`postgres-uokgs4c04ko0s4scccg40cgg` / db `postgres`): `INSERT 0 8`; `report_sdr_registry` now has 8 rows (Jason, Marc = SDR; Cameron/Ed/Janvi/Kevin/Mike/Remus = non-SDR).
- **Effect:** the Exec Summary reads `report_sdr_registry` at query time, so the next run renders "Janvi Mahajan" instead of "Unknown SDR ck6TRlU3…". No workflow change required.

## 2. Why GA4 and GSC were stale in the Executive Report (DIAGNOSED + RESOLVED 2026-09-09)

**Root cause: both Google OAuth2 credentials in n8n are expired/revoked.** Both ingests are scheduled and running; both fail at their Google fetch node on every run.

| Source | Workflow | Last success | Data frozen | Latest failure (evidence) |
|---|---|---|---|---|
| GA4 | `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) | 2026-09-03 16:12 (exec success, 851 rows, data through 09-02) | `report_daily_summary.sessions` = 0 since 09-03; `report_raw_ga4_sessions` max 09-02 | exec `911460` (09-08 13:31): `The credential "Google Analytics account" needs to be reconnected.` |
| GSC | `LT - GSC Daily Ingest` (`xHqmCC1vOeZ11gCd`) | 2026-09-04 02:00 (10 rows, window 09-03) | gsc data last 09-03 | exec `909421` (09-08 02:00): credential `GSC - Cameron Livetransparent Google account` (id `EKnNrSvlEd0A99AX`) — "Access could not be refreshed because the connected account has revoked access, the refresh token expired, or the account password/permissions changed." |

- **Live 30d Exec Summary health already flags both correctly:** `ga4 → stale`, `gsc → stale` (the health CTE derives staleness from `last_success_at` + `stale_after_hours=48`). Note: `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) overwrites the raw `report_source_health` rows to optimistic `ready`/`success` (observed 09-08 18:01:48), but this does **not** mask the report because the Exec Summary recomputes staleness.
- **This is a recurrence** of the 2026-08-14 GA4 credential expiry that was fixed 08-31; the credentials broke again ~09-03/09-04.
- **Resolution (2026-09-09):** the operator reconnected both n8n Google OAuth credentials (`Google Analytics account` for GA4; `GSC - Cameron Livetransparent Google account`, id `EKnNrSvlEd0A99AX`, for GSC). Verified with manual runs:
  - GA4 ingest exec `916807` → **success**, 853 rows, `report_raw_ga4_sessions` now through 09-07 (90-day window self-backfilled).
  - GSC ingest exec `916808` → **success**, 13 rows, `report_raw_gsc_queries` now through 09-07.
  - GA4 Traffic Rollup Bridge `916815`, GSC Rollup Bridge `916816`, Daily Rollups `916817` → all **success**.
  - `report_daily_summary.sessions` restored for 09-03…09-07 (25/10/5/11/13; GSC impressions 09-07 = 22, clicks 1); `report_source_health` ga4/gsc = `success`.
- **Remaining freshness note:** GA4 data for 09-08 lands on the next scheduled GA4 run (~13:31 UTC) + next Daily Rollups (~17:41 UTC). GSC's 3-day rolling window does not backfill the 09-04…09-07 gap beyond the 3-day window it re-fetched (volume immaterial, ~1 click/22 impressions).

## 3. Phase 3 — Meetings Showed/No-show (DESIGN COMPLETE, awaiting operator approval)

### Verified facts
- `report_raw_ghl_appointments.status` only ever contains `confirmed` (24) and `cancelled` (7); **no `showed`/`no-show` rows ever** → Showed/No-show stuck at 0. Report bucket logic is already correct (`showed` := showed/shown/show/attended/completed; `no-show` := no-show/no_show/noshow/missed; `booked` := booked/scheduled/confirmed; `cancelled` := cancelled/canceled).
- All appointments are on Cameron's Regulated Ads calendar (`SrtXcFVyea7pFl3nTiIK`); `assigned_user_id` = Cameron (calendar owner), NOT the SDR — SDR attribution is via contact→opportunity `assigned_to` (already implemented).
- Appointments Ingest (`yWZVSqEcjTbMT3kG`) runs **every 6h with a 30-day look-back** and upserts `status` — so a GHL-side status flip on any past appointment within 30 days is re-captured within ≤6h. **No ingest or report change needed.**
- GHL supports appointment statuses `Showed/Completed` and `No-Show`, a `PUT /calendars/events/appointments/{eventId}` API, and an **Appointment Status workflow trigger** (fires on booked/confirmed/showed/completed/no-show/canceled).

### Proposed design (nothing enabled)
**A small n8n helper (unpublished until approved), daily ~08:00 America/Los_Angeles:**
1. Select "actionable" appointments from `report_raw_ghl_appointments`: `start_at` in the past ≤30 days, `status = 'confirmed'`, calendar `SrtXcFVyea7pFl3nTiIK`, not already showed/no-show/cancelled.
2. Resolve each appointment's SDR via contact→opportunity `assigned_to` (same logic as `sdr_booked`).
3. Emit a **per-SDR pending-outcome digest** → Slack (recommended) and/or create GHL tasks assigned to each SDR naming the appointment + contact.
4. SDR (or Cameron) marks **Showed / No-Show** in GHL; the 6-hourly ingest picks it up; the SDR Performance panel + `meetingsBooked` become accurate.

This matches the Phase 3 plan ("surface a 'pending status update' list by SDR so reps know what to close"). The alternative "auto-mark no-show after N hours" is NOT recommended (cannot distinguish genuinely-no-show from rescheduled/late without human input). GHL-only automation is not practical for the time-based "meeting passed → remind SDR" case.

### Decisions (operator answered 2026-09-09)
- Mechanism: **Slack digest, then enable** (not GHL tasks).
- Who marks outcome: **owning SDR (Jason/Marc)**.
- Phase 5 scope: **Booked + SQLs + MQL→SQL**, non-SDR/Unassigned rows shown but excluded from ranking.

### Implementation (built + enabled 2026-09-09 — operator-approved)
- **New workflow `LT - Meeting Outcome Reminder` (id `x5vUQ34IcyKggdqP`)** — active/published `cf3c0d72-76fd-4b32-be96-820b49964dc7` (`versionId == activeVersionId`), schedule `0 8 * * 1-5` America/Los_Angeles, `dryRun=false`.
- Nodes: Schedule + Manual Trigger → `Config` (pg connection via direct `pg` pattern; `calendarId SrtXcFVyea7pFl3nTiIK`, `lookbackDays 30`, `dryRun`, `slackChannel #sales`, `slackWebhookUrl` copied from the reaper Config) → `Fetch Pending Appointments` (direct `require('pg')` SELECT: past `confirmed` appointments ≤30d, owner via contact→opp `assigned_to` + `report_sdr_registry`) → `Build Slack Digest` (per-SDR pending list; `post = !dryRun`) → `If - Should Post` (boolean true) → `Post to Slack` (HTTP Request, same incoming-webhook pattern as reaper, body `{channel, text}`).
- **Smoke execution `916780` (dryRun)**: success; 6 pending appointments resolved (Cameron 2 / Unassigned 3 / Marc 1), digest built, `post=false` → Slack NOT hit. Live run posts to `#sales`.
- **Behavior:** SDRs mark Showed/No-Show in GHL; the 6-hourly Appointments Ingest (30d look-back) re-syncs `status`; the SDR Performance panel + `meetingsBooked` then flow. No report-query or ingest change required.
- **Note:** channel is `#sales` (Config `slackChannel`) — change there if the workspace channel differs.

## 4. Phase 5 — QA/sign-off numbers + MQL reconciliation

### Per-SDR scope (30d window 2026-08-10…09-08, live endpoint)
`sdrPerformance` rows: **Unassigned** (booked 3), **Marc** (booked 1, SQLs created 156, MQL→SQL 49, lost 10), **Cameron Karkut** (booked 1, cancelled 1), **Jason Bornillo** (SQLs 8, MQL→SQL 7), **Janvi Mahajan** (was "Unknown SDR"; 0 in window). Booked sum = 5 = `meetingsBooked` (top KPI, appointments basis). Panel `appointments` shows booked 7 + cancelled 1 → the 2-appointment delta is attribution coverage (appointments whose contact has no opp owner are excluded from `sdr_booked`) — flagged for QA.

### MQL reconciliation (stage-based authoritative per Phase-0 decision #5)
| Metric | Stage-based (`mql_keys`) | Tag ledger (`mql_tag_events`) |
|---|---|---|
| Total | 140 ever (104 converted→SQL, 36 current) | 31 total events |
| In 30d window | enteredMqls **3** | convertedThisPeriod **56** | taggedMqlsThisPeriod **27** |

The two definitions disagree sharply and are expected to: the ledger records `mql` **tag-adds** fired by GHL (noisy — includes bounces / `not qualified` per the 08-25 runbook), while stage-based counts opps that reached Warm **Qualified (MQL)** stage. **Keep stage-based authoritative for the SDR assessment; keep the ledger labeled separately** (the API already returns `tagBasis: mql_tag_events_ledger`).

### Sign-off scope to confirm with Cameron/Janvi
Rank SDRs (Jason + Marc) on: **booked meetings** (appointments by start_at, primary) + **SQLs created** + **MQL→SQL conversion**; secondary: showed/no-show (once Phase 3 flows), won/lost/revenue. Decide whether non-SDR rows (Cameron, Janvi, Unassigned) should be shown-but-excluded or hidden from the ranking.

### Nightly monitoring
- 09-08 observed healthy: Rollups `completed` 17:41 UTC, Report QA probes 20:01 UTC (owner-coverage rows present: opp 34.6% / appt 35.5%), Bridge 00:02, Velocity 09:02, Leads hourly success. **Exception:** GA4/GSC ingests failing on expired credentials (above). Monitor after reconnect + next QA/Rollups.

## 5. Safety gates honoured
- Read-only investigation + one idempotent registry `INSERT…ON CONFLICT` applied to the report DB (no other DB writes). No workflow mutations, no publishes, no live sends, no credential rotation, no PostgreSQL restart.
- GA4/GSC reconnection is left to the operator (OAuth requires interactive Google login).