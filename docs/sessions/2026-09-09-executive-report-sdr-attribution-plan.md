# Executive Report — SDR Performance & Owner Attribution (Plan 2026-09-09)

**Status:** Planning-only document. **SUPERSEDED for Phases 1–2 by `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md` (implemented + verified 2026-09-09) and for Phase 4 by `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md` (implemented + verified 2026-09-09).** This file remains the reference for the Phase-0 decision list and the Phase 3/5 design.
**Purpose:** Define a strategic, phased implementation for SDR-level performance reporting (booked meetings, showed/no-show, SQLs, MQL→SQL conversion, owner attribution) plus lead-source breakdown for MQL/SQL, so the report is ready for the end-of-month SDR assessment.

## Request

- **Cameron (2026-09-08/09):** "We will be assessing SDR performance at the end of the month. I just need to ensure we are properly tracking booked meetings by SDR. MQL is great, but really want to focus on SQL / booked meetings."
- **Marketing owner:** Add, per SDR: owner attribution field; booked meetings; meetings showed / no-show; SQLs created; MQL→SQL conversion. Clarify the former owner-labelled active deals view. Marketing side: lead source for MQL and SQL (what is working).

## Verified current state (live n8n, 2026-09-09)

| Metric / panel | Current source | Limitation |
|---|---|---|
| `meetingsBooked` (top KPI) | `report_daily_summary.meetings_booked` — Daily Rollups counts opportunities whose stage ∈ (Booked, Discovery Scheduled, Meeting Scheduled, Meeting Requested), attributed to the opportunity **date** | Team-wide only; uses opportunity stage, not calendar events → disagrees with the appointments panel (3 vs 7) |
| Meetings (Cameron's Calendar) panel | `report_raw_ghl_appointments` grouped by status bucket, windowed by `start_at` | Groups only by status — no owner/calendar split. `status` = GHL `appointmentStatus`; **never updated post-meeting → "Showed" stuck at 0** |
| SQL Contacts | `report_raw_ghl_contacts` where the `sql` tag is present, `COUNT(DISTINCT source_key)` | One cumulative number (36–39); no owner or source break-out |
| `mqlSummary` | `report_raw_ghl_opportunities` Warm→`3b3bd98d` (Qualified MQL) joined to Sales Outreach `dhdlf3O4tymxFtHk4aqq` | Team-wide cumulative; no owner dimension |
| Owner data capture | **CONFIRMED in ingests** (see below) | The Exec Summary SQL never projects any owner/assigned field (zero `assigned_to`/`assignedTo`/`owner` matches) |
| "Team Active Deals" | The **same** team-wide opportunity payload relabeled "deal-centred" (reuses `activeOpps`/`workedOpps`/`stageMovers`/`closedWon`/`closedLost`/`winRate`) | Mislabeled — not actually owner-filtered; retain the team-wide label or truly filter |

### Owner data already captured (no ingest change needed)

- **Opportunities** — `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) extracts `assignedTo`/`assigned_to`/`ownerId`/`owner_id` into `dimensions_json->>'assigned_to'` and stores the full object in `payload_json`.
- **Appointments** — `LT - GHL Daily Appointments Ingest` (`yWZVSqEcjTbMT3kG`) stores `assigned_user_id` (from `e.assignedUserId || e.userId`) and the full event in `payload_json`, plus `contact_id`, `calendar_id`, `status`, `start_at`. Note: all bookings are on Cameron's Regulated Ads calendar (`SrtXcFVyea7pFl3nTiIK`), so the appointment's own user is the calendar owner, **not necessarily the SDR**. SDR attribution must join appointment → contact → opportunity `assigned_to`.
- **Contacts** — `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) stores the full GHL contact object in `payload_json` (owner field to confirm per live row) and UTM source/medium/campaign in `dimensions_json`.

## Strategic decisions required before code (Phase 0)

1. **Canonical "Booked Meeting" definition.** Recommend: the appointments table windowed by `start_at` (real calendar events). The top KPI must match this so 3-vs-7 disappears. The opportunity-stage "meeting" count stays available as a separate funnel metric, clearly labeled.
2. **Booked-by-SDR attribution path.** Because all meetings land on Cameron's calendar, attribute to the SDR by joining `appointment.contact_id` → `report_raw_ghl_opportunities` (or contact) `assigned_to`, not the appointment's own user. Decide owner authority:
   - Native opportunity `assigned_to` (the Jason/Marc allocator writes this) — **recommended primary**.
   - Custom opportunity `Owner` (`Wpg7FGrQTgAY1GoKcdEJ`) — cross-check only.
   - Contact `assignedTo` — fallback when no opportunity exists.
3. **SDR registry.** Create `report_sdr_registry` (user_id → name → role) so the report renders names, not UUIDs. Known IDs: Jason `yU85G6kfhtW4vUtx3QE6`, Marc `sqGx5rp3oAUG610NXyjU`, Cameron `03p5GatJBH7i9zjMaIzm`, Ed `gePIeuHOEsAiPVA1mfOR`. Verify Janvi's ID and any SDR-only users before building.
4. **SQL definition.** Offer both, primary = **Sales Outreach opportunities created in the window grouped by owner** ("SQLs Created by SDR"); keep the `sql`-tag contact count as the existing cumulative figure.
5. **MQL definition.** Keep the stage-based MQL (Warm Qualified MQL → Sales Outreach) as authoritative; the forward-looking `mql_tag_events` ledger (2026-08-25) stays supplementary and clearly labeled. Reconcile the "3 in last 30 days" number against `enteredMqls` before adding lead-source.

## Phased implementation (strategic order, each phase verifiable)

### Phase 1 — Read-model foundation (no UI change)
- Create `report_sdr_registry` in `postgres/reporting-bootstrap.sql` + bootstrap on live DB.
- Extend Daily Rollups `tmp_report_opps` to carry `assigned_to` so the stage/pipeline summaries and `meetings_booked` rollup become owner-aware.
- Add owner-data coverage to `report_source_health` via `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`): % of opps with `assigned_to`, % of appointments with `contact_id`+owner, so gaps are visible.
- Verify one representative live row per table to confirm owner field shapes before building CTEs.

### Phase 2 — SDR Performance panel (report + API)
- Exec Summary (`Bukc0mgOD2r7V6ED`) new CTEs, all grouped by owner (via `assigned_to` / contact join):
  - Booked meetings by SDR (appointments by `start_at`, owner via contact join)
  - Showed / No-show / Cancelled by SDR (status bucket + owner)
  - SQLs created by SDR (Sales Outreach opps created in window)
  - MQL → SQL conversion by SDR (join `mql_keys` → `mql_conversion` → owner)
  - Won / Lost / Revenue by SDR (closed-won/lost grouped by owner)
- Align the top `meetingsBooked` KPI to the appointments definition (Phase 0 decision) so it matches the panel.
- Frontend `reports/embed/executive/index.html`: new "SDR Performance" panel (per-rep table) + glossary definitions. Deploy as a new build stamp.
- Update `docs/reports/Reporting Gaps and Requirements.md` acceptance checklist.

### Phase 3 — Meetings showed / no-show operational fix (GHL-side)
- The report bucket logic is correct; the gap is that GHL `appointmentStatus` is never flipped after the meeting. Add a GHL automation (or small n8n helper) that updates appointment status to showed/no-show post-meeting, and/or surface a "pending status update" list by SDR in the report so reps know what to close.
- This is an operator/automation change, not a report query change.

### Phase 4 — Marketing lead source for MQL/SQL
- Join MQL/SQL opportunity `contact_id` → `report_raw_ghl_contacts` and project `utm_source_first` / `utm_medium_first` / `utm_campaign_first` (plus `source`/channel), with `report_bridge_traffic_to_lead` fallback when UTM is absent.
- Add a "Lead Source" breakdown panel for entered MQLs and created SQLs (answers "what is working").

### Phase 5 — Cleanup & housekeeping
- Retain "Team Active Deals" as the team-wide label, or implement a real owner filter and document the distinction.
- Reconcile MQL definitions and label both stage-based and tag-ledger figures.
- QA assertions: 3-vs-7 resolved, showed/no-show flow, owner coverage %; verify desktop + 390px, zero console errors.

## Files / workflows touched (each with a gate)

| Artifact | Change | Gate |
|---|---|---|
| `postgres/reporting-bootstrap.sql` | add `report_sdr_registry` | idempotent, apply + verify |
| Daily Rollups `EUeOiRttoVLQ9zF9` | carry `assigned_to` through `tmp_report_opps` | REST PUT → re-attach postgres cred `pgAzUqpwOiGkGXzO`; verify `versionId==activeVersionId`; re-run |
| Exec Summary `Bukc0mgOD2r7V6ED` | owner CTEs + meetings KPI alignment | REST PUT (large Build Query edit); EXPLAIN before/after; verify JSON keys |
| Frontend `reports/embed/executive/index.html` | SDR Performance panel | back up first; deploy build; desktop + 390px |
| Report QA `M5mXcDTFSko6EdHb` | owner coverage probe | publish; verify health rows |
| GHL automation / n8n helper | appointment status update post-meeting | explicit approval before enabling |

## Safety gates (per AGENTS.md)
- Fetch-first, patch-second. `update_workflow` does not auto-publish — verify `versionId == activeVersionId` after every mutation.
- For large `Build Query` / `Build Rollup SQL` edits use direct n8n REST `PUT` via `curl.exe` (PowerShell JSON can corrupt nested objects); PUT auto-publishes and validates credentials — re-attach the Query Summary postgres credential after.
- Do not run live LinkedIn/Instagram/Vapi/newsletter/SMS sends for testing without explicit approval.
- Do not restart PostgreSQL or rotate `N8N_ENCRYPTION_KEY` casually.
- Profile with `EXPLAIN (ANALYZE, BUFFERS)` before heavy SQL changes (Exec Summary is already ~15–59s).

## References
- `docs/reports/Reporting Gaps and Requirements.md` — P1 "Reporting Owner Dimensions" and Executive Report requirements.
- `GHL Live Transparent CRM/Report Data Contract.md` — owner/assignment dimension and SDR minimum-V1 output already documented.
- `docs/sessions/2026-08-25-mql-tag-ledger.md` — MQL tag ledger runbook.
- AGENTS.md — Reporting Execution Contract, Working Rules, and severity-ranked open work.

## Session Closeout (2026-09-09)

> **SUPERSEDED by the implementation session** (`docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md`): Phases 1–2 were implemented and verified the same day after operator sign-off on the Phase-0 decisions (booked = appointments by `start_at`; owner authority = native opportunity `assigned_to` + contact fallback + explicit Unassigned bucket; SDRs = Jason + Marc). Live workflow versions after implementation: Daily Rollups `1af59845…`, Report QA `a21c0f4a…`, Exec Summary `90bcc99f…`; frontend build `2026-09-09-v28-sdr-performance`. The exact next actions below now apply to Phases 3–5 only.

- **Objective:** assess the Executive Report against Cameron/Janvi's SDR-performance + lead-source asks and record a strategic, phased implementation plan. **Planning only — no workflow or frontend mutations were made in THIS session; Phases 1–2 were later implemented in the follow-up session above.**
- **Work done this session:** (1) read-only inspection of the live Exec Summary SQL (`Bukc0mgOD2r7V6ED` — `Build Query` CTEs: `appointments`, `summary`/`meetings_booked`, `mql_summary`, `sql_contacts`, `pool_distribution`, plus all `report_raw_ghl_opportunities`/`report_raw_ghl_contacts` jsonb paths); (2) read-only inspection of the ingests (Sales `aYT5oHcgmBALzHy5`, Appointments `yWZVSqEcjTbMT3kG`, Leads `osIJOgBmWITF5Yuv`) confirming owner/assigned data is already captured; (3) wrote this plan doc; (4) updated `AGENTS.md`, `plan.md`, `Project Status and Next Steps.md`, `docs/reports/Reporting Gaps and Requirements.md`, `GHL Live Transparent CRM/Report Data Contract.md`.
- **Live state verified (no changes):** Exec Summary active `92507a83-2a82-4a1d-8fb0-43a86d116a2d` (7 nodes); Daily Rollups active `ddded785-2d31-4818-8ced-8a9c881a689f`; Sales Ingest active `1bdf75f4-ecb1-414b-abfe-e8537c676dda`; Appointments Ingest active `1be41962-048d-43a3-ab92-c901f3491ce5`; Leads Ingest active `65024f80-6cc2-4716-970b-7e73370e098d`. All `versionId == activeVersionId`; no drafts pending.
- **Worktree:** branch `codex/social-outreach-sync`. This session's doc edits are uncommitted (5 files + this plan). Pre-existing unrelated working-tree changes (Hermes monitor work) also present: `scripts/gmail_read.py`, `scripts/monitor.py`, `scripts/watch_fix.py` modified; `docs/sessions/2026-09-07-pool-closure-root-cause-and-permanent-fix.md`, `gm_err.txt`, `gm_list.json` untracked. Do not commit these without reviewing for embedded secrets (`gm_err.txt`/`gm_list.json` may contain Gmail/monitor content).
- **Tests run:** none. No executions started, no workflows published/activated, no live sends. Read-only verification only.
- **Blockers / decisions required before any code:** (1) canonical "booked meeting" definition (recommended: appointments by `start_at`); (2) SDR roster + confirm user IDs (Jason `yU85G6kfhtW4vUtx3QE6`, Marc `sqGx5rp3oAUG610NXyjU`, Cameron `03p5GatJBH7i9zjMaIzm`, Ed `gePIeuHOEsAiPVA1mfOR`; verify Janvi's ID); (3) owner authority (recommended: native opportunity `assigned_to`); (4) SQL definition; (5) MQL definition reconciliation (stage-based vs `mql_tag_events` ledger).
- **Exact next action for the next session:** take the Phase-0 decision list to Cameron/Janvi, get sign-off, then begin Phase 1 (create `report_sdr_registry` in `postgres/reporting-bootstrap.sql` + apply on live DB; extend Daily Rollups `tmp_report_opps` to carry `assigned_to`; add owner-coverage probe to `LT - Report QA and Alerts` `M5mXcDTFSko6EdHb`; verify one live row per owner field shape before building CTEs).
- **Safety gates that remain in force:** fetch-first/patch-second; verify `versionId == activeVersionId` after every mutation (`update_workflow` does not auto-publish); use direct n8n REST `PUT` via `curl.exe` for large Build Query/Rollup SQL edits and re-attach the Query Summary postgres credential `pgAzUqpwOiGkGXzO` after; `EXPLAIN (ANALYZE, BUFFERS)` before heavy SQL; no live LinkedIn/Instagram/Vapi/newsletter/SMS sends without explicit approval; do not restart PostgreSQL or rotate `N8N_ENCRYPTION_KEY` casually.
