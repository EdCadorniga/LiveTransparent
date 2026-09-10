# Executive Report — SDR Performance & Owner Attribution (Phases 1–2 IMPLEMENTED 2026-09-09)

**Status:** Phases 1–2 implemented and verified against live Coolify/n8n/Postgres. **Phase 4 (MQL/SQL lead source) was also implemented + verified in a follow-up session** — see `2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md`. Phase 3 (GHL appointment-status update) and Phase 5 (QA/sign-off) remain; see the plan (`2026-09-09-executive-report-sdr-attribution-plan.md`) for the full phased design and the Phase-0 decision list.

## Phase-0 decisions (operator sign-off this session)

1. **Canonical "Booked Meeting"** = appointments by `start_at` on the Regulated Ads calendar (`SrtXcFVyea7pFl3nTiIK`). The opportunity-stage meeting count stays available as `meetingsBookedStageBasis`.
2. **Owner authority** = native opportunity `assigned_to` primary; contact-owner fallback; custom `Owner` cross-check only. Unassigned records roll into an explicit **Unassigned** bucket, and owner-coverage % is surfaced in `report_source_health`.
3. **SDR roster** = Jason Bornillo (`yU85G6kfhtW4vUtx3QE6`) and Marc (`sqGx5rp3oAUG610NXyjU`). Cameron/Ed/Janvi are non-SDR. Unknown IDs pending: `ck6TRlU3wnTmMxuVpn5F` (appears on 4–5 opps), Janvi (no opp ownership in current data).
4. **SQL definition** = Sales Outreach opportunities created in the window grouped by owner (primary); the cumulative `sql`-tag contact count stays secondary.
5. **MQL definition** = stage-based (Warm Qualified → Sales Outreach) authoritative; `mql_tag_events` ledger stays supplementary/labeled.

## Changes made (all verified live)

### Phase 1 — read-model foundation
- **`postgres/reporting-bootstrap.sql`** — added `report_sdr_registry` (user_id PK, user_name, role, is_sdr, email, is_active, notes, updated_at) + idempotent seed (Jason/Marc SDR; Cameron leadership; Ed exec).
- **Applied + verified on live DB** (`postgres-uokgs4c04ko0s4scccg40cgg`, database `postgres`, user `postgres`): 4 rows, `to_regclass` OK.
- **Daily Rollups `EUeOiRttoVLQ9zF9`** — `Build Rollup SQL` now carries `assigned_to` (`COALESCE(dimensions_json->>'assigned_to', payload_json->>'assignedTo')`) through `tmp_report_opps` and `MAX(assigned_to)` through `tmp_daily_opps_fixed`. REST PUT → active `1af59845-fd7c-48d0-86c7-362c698cdd98` (versionId == activeVersionId), postgres credential `pgAzUqpwOiGkGXzO` retained, execution `914946` success.
- **Report QA `M5mXcDTFSko6EdHb`** — `Probe Coverage Health` now upserts two owner-coverage health rows:
  - `ghl_opp_owner_coverage` → 34.6% assigned on latest snapshot (3,618 / 10,466).
  - `ghl_appt_owner_coverage` → 11/31 appointments attributable to an SDR via contact→opp owner (35.5%).
  - Active `a21c0f4a-1b0d-4b9c-937a-f4a4184f3732` (versionId == activeVersionId), execution `914957` success.

### Phase 2 — SDR Performance panel + meetings KPI alignment
- **Exec Summary `Bukc0mgOD2r7V6ED`** (`Build Query`) — new CTEs: `sdr_owner_names` (from `report_sdr_registry`), `contact_owner` (latest `assigned_to` per appointment-contact), `sdr_opp_facts` (latest per opp created in window), `sdr_booked`, `sdr_sqls`, `sdr_closed`, `sdr_mql_conv`, `sdr_all_owners`, `sdr_performance`. Final SELECT adds `'sdrPerformance', COALESCE((SELECT items FROM sdr_performance), '[]'::json)`.
  - Top KPI `meetingsBooked` now = `COUNT(*) FROM report_raw_ghl_appointments WHERE start_at IN window AND status NOT IN ('cancelled','canceled')`; adds `meetingsBookedStageBasis` (old value) + `meetingsBookedBasis` = `'appointments_start_at'`.
  - Query now prepends `SET jit=off;` (JIT-on was 70–90s; JIT-off 15.5s).
  - **`Shape Response`** adds `sdrPerformance: payload.sdrPerformance || []`.
  - Active `90bcc99f-cc05-492f-90a5-db8e5961a11c` (versionId == activeVersionId), Query Summary credential `pgAzUqpwOiGkGXzO` retained.
- **Performance (EXPLAIN ANALYZE, 30d window 2026-08-10…2026-09-08):** pre-change JIT-on ≈ 70.8s; new JIT-on ≈ 86–90s; **new JIT-off ≈ 15.5s** (full script end-to-end 16.8s). Live endpoint after deploy: **16–19s** (was ~70.8s before).
- **Live verification (30d through the proxy):** HTTP 200 in ~16–19s; `meetingsBooked=5` (basis `appointments_start_at`), `meetingsBookedStageBasis=3`; `sdrPerformance` rows: Unassigned (booked 3), Marc (booked 1, SQLs 156, MQL→SQL 49, lost 10), Cameron Karkut (booked 1, cancelled 1), Jason Bornillo (SQLs 8, MQL→SQL 7), Unknown SDR `ck6TRlU3…`. Sum of per-owner booked = 5 = `meetingsBooked`. (Note: the "3 vs 7" disagreement is resolved by construction; the panel shows 7 = 5 booked + 1 cancelled + … statuses within the panel buckets.)

### Frontend — build `2026-09-09-v28-sdr-performance`
- `reports/embed/executive/index.html` (repo == live before edit, sha verified identical):
  - New **SDR Performance** panel (`section-sdr` + nav item) with `.campaign-table` (SDR, Booked, Showed, No-show, Cancelled, SQLs Created, MQL→SQL, Won, Lost, Revenue) + `renderSdrPerformance()` wired into `render(data)`.
  - Glossary: added **SDR Performance** definition card; updated Sales Panels card.
  - **Former owner-labelled active deals view → "Team Active Deals"** (heading + glossary).
  - `BUILD_STAMP` → `2026-09-09-v28-sdr-performance`.
- **Deployed** to `reports-livetransparent` at `/usr/share/nginx/html/embed/executive/index.html`; backup `index.html.bak-20260909-022102`. Sha verified on-disk.
- **Browser verified** (Playwright): desktop and 390px — SDR table populated, no horizontal overflow (scrollWidth == clientWidth == 375), zero console errors (only benign `favicon.ico` 404), build badge shows the new stamp.

## Verification gate results
- `versionId == activeVersionId` for all three mutated workflows (Rollups, QA, Exec Summary); no drafts pending.
- Postgres credentials retained after every REST PUT (no re-attach needed this session).
- `report_source_health` shows both owner-coverage probes (status `attention`).
- EXPLAIN (ANALYZE, BUFFERS) executed on the live DB before/after; full modified script runs end-to-end RC=0 in ~16.8s and returns `sdrPerformance`.

## Remaining work (next sessions)
- **Phase 3 — GHL appointment-status update** post-meeting so Showed/No-show flows (report logic is correct; `appointmentStatus` is never flipped). Requires a GHL automation or small n8n helper + explicit operator approval before enabling.
- **Phase 4 — MQL/SQL lead-source breakdown**: join MQL/SQL opportunity `contact_id` → `report_raw_ghl_contacts` UTM first fields, `report_bridge_traffic_to_lead` fallback; add a Lead Source panel.
- **Identify + seed unknown owners**: `ck6TRlU3wnTmMxuVpn5F` (4–5 opps) and Janvi's user ID.
- **Phase 5 — QA + sign-off**: confirm the per-SDR ranking scope with Cameron/Janvi; reconcile MQL definitions (stage-based vs `mql_tag_events`); monitor the nightly Rollups/QA runs.

## Safety gates honoured
- Fetch-first/patch-second; REST PUT via `curl.exe` + JSON files for large Code-node edits (no PowerShell JSON corruption).
- `EXPLAIN (ANALYZE, BUFFERS)` before/after heavy SQL; `SET jit=off` added to Exec Summary query.
- No live LinkedIn/Instagram/Vapi/newsletter/SMS sends; no PostgreSQL restart; no `N8N_ENCRYPTION_KEY` rotation.
- Backups: frontend `index.html.bak-20260909-022102`; workflow changes are versioned in n8n history (PUT auto-publishes new versions `1af59845…`, `a21c0f4a…`, `90bcc99f…`).
