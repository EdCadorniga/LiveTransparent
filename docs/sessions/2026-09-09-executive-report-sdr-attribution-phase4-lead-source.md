# Executive Report — MQL/SQL Lead Source Breakdown (Phase 4 IMPLEMENTED 2026-09-09)

**Status:** Phase 4 implemented and verified against live Coolify/n8n/Postgres. Answers Janvi's marketing-side ask: "lead source for MQL and SQL (what is working)". Phases 1–2 remain documented in `2026-09-09-executive-report-sdr-attribution-phase1-2.md`; Phase 3 (GHL appointment-status update) and Phase 5 (QA/sign-off) remain.

## Definition (consistent with Phase-0 decisions)

- **MQLs Entered** = Warm pipeline opportunities that reached stage `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2` (Qualified MQL) in the selected window (`mql_first.first_mql_date` between `$1` and `$2`) — same basis as `mqlSummary.enteredMqls`.
- **SQLs Created** = Sales Outreach pipeline (`dhdlf3O4tymxFtHk4aqq`) opportunities created in the selected window (same basis as `sdr_sqls` / `sdrPerformance.sqlsCreated`).
- **Lead source resolution** (per opportunity, in order):
  1. Contact's first UTM source/medium/campaign from the latest `report_raw_ghl_contacts` snapshot (`utm_source_first`/`utm_medium_first`/`utm_campaign_first`, with `_last` + `contact.`-nested fallbacks).
  2. `report_bridge_traffic_to_lead` fallback (`traffic_source`/`medium`/`campaign`/`landing_page`), latest snapshot per contact.
  3. GHL contact `source` field.
  - Rows with no resolvable source are labelled **Unknown / Unattributed**. Bridge rows whose landing page matches `(/links/|msgsndr[.]com)` are relabelled **Email/SMS link** (same convention as the existing `contact_sources` CTE).

## Changes made (all verified live)

### Exec Summary `Bukc0mgOD2r7V6ED` — `Build Query` + `Shape Response`
- **New CTEs** (inserted between `sdr_performance` and `summary_json`):
  - `lead_source_contacts` — latest contact snapshot per `contact_id` with UTM source/medium/campaign + GHL `source`.
  - `lead_source_bridge` — latest `report_bridge_traffic_to_lead` row per contact (source/medium/campaign/landing_page).
  - `lead_source_mql` — MQL source_keys entered in the window with their opportunity `contact_id` (lateral latest-opp contact lookup).
  - `lead_source_sql` — Sales Outreach opps created in the window with `contact_id` (reuses `sdr_opp_facts`).
  - `lead_source_breakdown` — `FULL OUTER JOIN` of MQL/SQL on `contact_id`, grouped by source+medium, capped at 20 rows, ordered `sqls DESC, mqls DESC`.
  - `lead_source_coverage` — `mqlsTotal`/`sqlsTotal`/`mqlsAttributed`/`sqlsAttributed` + `basis: contact_utm_first_source_with_bridge_fallback`.
- **Final SELECT** adds `leadSourceBreakdown` + `leadSourceCoverage` keys.
- **`Shape Response`** adds `leadSourceBreakdown: payload.leadSourceBreakdown || []` and `leadSourceCoverage: payload.leadSourceCoverage || {}`.
- **Deployment:** direct n8n REST `PUT /api/v1/workflows/Bukc0mgOD2r7V6ED` via `curl.exe` + JSON file (PowerShell JSON-safe path per AGENTS.md). Active version `162bbba8-0b28-425d-891c-488bd00bc781`; `versionId == activeVersionId` after PUT. Postgres credential `pgAzUqpwOiGkGXzO` retained on `Query Summary` (verified after PUT).

### Performance
- New CTE block measured via `EXPLAIN (ANALYZE, BUFFERS)` on the live DB: **~867 ms standalone** including building all dependency CTEs; in the full query it reuses already-materialized `mql_keys`/`mql_first`/`sdr_opp_facts`, so incremental cost is lower.
- Full live endpoint through the proxy (`range=30d`): **HTTP 200 in ~17.2s** (unchanged vs the 16–19s envelope from Phases 1–2). `SET jit=off` retained.
- `lead_source_contacts`/`lead_source_bridge` scan small tables (`report_raw_ghl_contacts` = 2,654 rows; bridge = 2,613 rows) — no index work needed.

### Frontend — build `2026-09-09-v29-lead-source`
- `reports/embed/executive/index.html`:
  - New **Lead Source — MQL & SQL** panel (`section-lead-source` + nav item) with `.campaign-table` (Lead Source, Medium, MQLs Entered, SQLs Created) + `renderLeadSource(rows, coverage)` wired into `render(data)`.
  - Footer note includes live attribution coverage (`Attributed in this window: N of N SQLs, N of N MQLs`).
  - Glossary card **Lead Source — MQL & SQL** added; existing **SDR Performance** + **Sales Panels** cards untouched.
  - `BUILD_STAMP` → `2026-09-09-v29-lead-source`.
- **Deployed** to `reports-livetransparent` at `/usr/share/nginx/html/embed/executive/index.html` via SFTP + `docker cp`; backup `index.html.bak-20260908-185312` (v28) + `index.html.bak-20260909-022102`. Deployed sha == repo sha (`6ecd3e22405d60d2f392a24600f897b455edc63be86990ff2d4a09f567648bea`), `v29-lead-source` stamp present, 5 "Lead Source" occurrences on-disk.
- **Browser verified** (Chrome DevTools): desktop + 390px — Lead Source table populated (8 rows), coverage note correct, SDR Performance panel intact (5 rows), `scrollWidth == clientWidth` at both 375px and 1285px (no horizontal overflow), zero console errors (only benign favicon 404).

## Live verification (30d through the proxy)

`leadSourceCoverage` → `{"basis":"contact_utm_first_source_with_bridge_fallback","mqlsTotal":3,"sqlsTotal":164,"mqlsAttributed":0,"sqlsAttributed":32}`.

`leadSourceBreakdown` (8 rows, 30d window):

| Lead Source | Medium | MQLs | SQLs |
|---|---|---|---|
| Unknown / Unattributed | — | 3 | 132 |
| CRM UI | csv_import | 0 | 21 |
| Other | other | 0 | 3 |
| Email/SMS link | — | 0 | 3 |
| LinkedIn via Unipile | — | 0 | 2 |
| Book a demo | — | 0 | 1 |
| partnership_outreach | — | 0 | 1 |
| external_form | External Form | 0 | 1 |

## Data-coverage note (known limitation, not a logic bug)

Coverage is bounded by the GHL Leads Ingest snapshot (`report_raw_ghl_contacts` holds ~2,650 rows / ~2,360 distinct contacts of the full CRM). Most MQL/SQL contacts are not in the snapshot, so the majority of SQLs land in **Unknown / Unattributed** (132/164) and all 3 entered MQLs are unattributed. The bridge fallback (`report_bridge_traffic_to_lead`, ~2,600 rows) adds 32 attributed SQLs. As the snapshots accumulate, attribution will improve; the coverage note surfaces the exact attributed/total each window so the numbers are read honestly.

## Verification gate results
- `versionId == activeVersionId` for the Exec Summary (`162bbba8…`) after the REST PUT; no drafts pending.
- Postgres credential `pgAzUqpwOiGkGXzO` retained on `Query Summary` after PUT (verified via GET).
- EXPLAIN (ANALYZE, BUFFERS) on live DB before/after; new CTE block ~867ms standalone; full endpoint ~17s.
- Frontend deployed sha matches repo; desktop + 390px verified; zero console errors.

## Safety gates honoured
- Fetch-first/patch-second. REST PUT via `curl.exe` + JSON file for large Code-node edits (no PowerShell JSON corruption).
- Verified `versionId == activeVersionId` and postgres credential retention after the PUT.
- EXPLAIN (ANALYZE, BUFFERS) before heavy SQL; `SET jit=off` retained.
- No live LinkedIn/Instagram/Vapi/newsletter/SMS sends; no PostgreSQL restart; no `N8N_ENCRYPTION_KEY` rotation.
- Backups: frontend `index.html.bak-20260908-185312` (pre-v29) + `index.html.bak-20260909-022102`; workflow changes versioned in n8n history (PUT auto-published `162bbba8…`).

## Remaining work (next sessions)
- **Phase 3** — GHL appointment-status update post-meeting so Showed/No-show flows (report logic correct; `appointmentStatus` never flipped). Requires a GHL automation or small n8n helper + explicit operator approval before enabling.
- **Phase 5** — QA + sign-off: confirm per-SDR ranking scope with Cameron/Janvi; reconcile MQL definitions (stage-based vs `mql_tag_events`); monitor nightly Rollups/QA runs.
- **Identify + seed unknown owners**: `ck6TRlU3wnTmMxuVpn5F` (4–5 opps) and Janvi's user ID into `report_sdr_registry`.