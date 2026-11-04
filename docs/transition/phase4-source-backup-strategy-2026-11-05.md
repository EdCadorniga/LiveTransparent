# Phase 4 — critical workflow source and rollback strategy — 2026-11-05

Read-only: each critical workflow ID was searched across tracked `scripts/`, `n8n/`,
`postgres/`, `services/`, `tools/` to find which repo artifacts reference it
(the only reproducible builders/repairers). File paths only; no live or archive
workflow data was re-read (see the archive classification for rollback snapshots).
Not a cleanup authorization; nothing was changed.

**Scope correction (2026-11-06):** an ID occurrence in a file is a *reference*, not proof that the file is a reproducible builder/source or a last-known-good backup. The table's GHL automation `WL - Micro - Set Vertical Sender (Webhook)` was mistakenly assigned the n8n ID `z0Sq4AE3Xdbgw2Yh`; its GHL ID is `52f6a14a-927c-433b-82c3-9503feb14110` per `AGENTS.md`. That row is not an additional n8n workflow. No production read or archive restore test was performed by this correction.

**Source strategy (documented from this pass, not recovery-tested):** the live n8n-lt instance is the system
of record; n8n API `GET /workflows/{id}` provides an authoritative live export for any
workflow before/after a change. Some referenced files may be builders/repair scripts,
but this ID search did not verify that they reproduce the current live graph. Where a
workflow has **no** tracked ID reference, its current graph still depends on the live
instance (plus any dated local snapshot listed in the archive classification). A GET
export opportunity is not itself a retained or restore-tested backup.

| workflow (role) | id | repo artifacts referencing the ID |
|---|---|---|
| LT - GHL Daily Sales Ingest — Opportunities snapshot ingest (daily) | `aYT5oHcgmBALzHy5` | `n8n/reporting/Workflow_Shell_Index.md`, `scripts/n8n/n8n_exec_check.py` |
| LT - GHL Daily Leads Ingest — Contacts snapshot ingest (hourly) | `osIJOgBmWITF5Yuv` | `n8n/reporting/Workflow_Shell_Index.md`, `scripts/n8n/fix_workflow.py`, `scripts/utilities/vapi_audit.py` |
| LT - Report Executive Summary API — Legacy Executive Report facts API | `Bukc0mgOD2r7V6ED` | `n8n/reporting/Workflow_Shell_Index.md`, `scripts/cache_report_sources.py`, `scripts/continue_v1_reporting.py`, `scripts/inspect_report_cache_paths.py`, `scripts/inspect_v1_band_improvements.py`, `scripts/social-reporting/fix_executive_report_metrics.py` |
| LT - Report Campaign Channel Summary — Campaign channel facts API | `MvPLbUAN9IIQikxb` | `n8n/REPORTING_IMPLEMENTATION.md`, `n8n/reporting/README.md`, `scripts/cache_report_sources.py`, `scripts/inspect_report_cache_paths.py`, `scripts/inspect_v1_band_improvements.py`, `scripts/social-reporting/fix_executive_report_metrics.py` |
| LT - Executive Report V1 Facts API — Executive Report V1 facts API | `oxYDg6XnRBKhl1Xd` | `scripts/audit_sql_tag_writers.py`, `scripts/audit_v1_accuracy.py`, `scripts/build_v1_band_improvements.py`, `scripts/check_recovered_mql_clicks.py`, `scripts/check_v1_cache_query.py`, `scripts/continue_v1_reporting.py` |
| LT - Executive Report V1 Data Materializer — V1 facts materializer | `knc2wxe4pyYIJ5tw` | `scripts/continue_v1_reporting.py`, `scripts/patch_v1_band1_facts.py` |
| LT - Report Daily Rollups — Daily rollups bridge | `EUeOiRttoVLQ9zF9` | `n8n/reporting/Workflow_Shell_Index.md` |
| LT - Report Pipeline Velocity — Stage velocity | `iFfwh0jpYUZoDhDR` | —none— |
| Report Attribution Bridge — Traffic-to-lead attribution | `Y0TU7Il71JswxOBp` | `n8n/reporting/Workflow_Shell_Index.md` |
| LT - GHL LinkedIn Connect Dispatcher — Connection invite sender | `fXxw5lanZcDmUrst` | `scripts/linkedin/audit_live_linkedin_send_nodes.py`, `scripts/linkedin/build_vertical_outreach.py`, `scripts/linkedin/enforce_linkedin_daily_limit.py`, `scripts/linkedin/fix_dispatcher_mirror_location_token.py`, `scripts/linkedin/fix_linkedin_dm_pipeline.py`, `scripts/linkedin/fix_linkedin_sanitize_double_escape.py` |
| LT - LinkedIn DM Sequence (Unipile) — 4-step DM sender | `d0tEtijajisIsYcs` | `scripts/linkedin/audit_live_linkedin_send_nodes.py`, `scripts/linkedin/build_vertical_outreach.py`, `scripts/linkedin/fix_linkedin_dm_pipeline.py`, `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`, `scripts/linkedin/harden_linkedin_dm_dedup.py`, `scripts/linkedin/patch_live_linkedin_identity_conversations.py` |
| LT - LinkedIn Connection State Sync — Ready/connected state reconciliation | `ceaKnz6E3onQrZpt` | `scripts/linkedin/backfill_linkedin_connected_tag.py`, `scripts/linkedin/fix_connection_state_sync_withdrawal_holds.py`, `scripts/linkedin/reconcile_requested_connections.py` |
| LT - LinkedIn Connection State Upsert — Canonical state write webhook | `Old7ZvyVYgFaJgDr` | `scripts/deploy/deploy_acceptance_checker.py`, `scripts/deploy/fix_state_upsert_esc.py`, `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`, `scripts/linkedin/fix_linkedin_state_upsert.py`, `scripts/linkedin/guard_linkedin_requested_state.py` |
| LT - LinkedIn Connection Acceptance Checker — Acceptance detection webhook | `3ttEvr5NMcQCS4Hp` | `scripts/deploy/acceptance_checker/build_accept_sql.js`, `scripts/deploy/deploy_acceptance_checker.py`, `scripts/linkedin/backfill_linkedin_connected_tag.py`, `scripts/linkedin/vertical_outreach_ops.py` |
| LT - LinkedIn Reply Backfill — Reply divergence reconciliation | `QfJ2EZcc7lZwNgxj` | `scripts/linkedin/fix_linkedin_dm_pipeline.py` |
| LT - LinkedIn Relations Backfill — Provider relations daily backfill | `VPiHfBwzOHaJnHBY` | `scripts/linkedin/backfill_linkedin_connected_tag.py`, `scripts/linkedin/fix_relations_backfill_endpoint.py` |
| LT - LinkedIn DM Suppression from GHL Tag — Suppression webhook | `IPN8jnR3XSurX0o1` | —none— |
| LT - LinkedIn Connected Tag Sync — Daily connected-tag sync | `rcvTMprJKga9aEJ6` | —none— |
| LT - Sales Navigator Provider Gateway — GHL provider outbound/inbound gateway (V2) | `ZiYEBuP7xdddhnUB` | `n8n/sales-navigator/WORKFLOW_BUILD_SPEC.md`, `scripts/linkedin/vertical_outreach_ops.py`, `scripts/n8n/audit_sales_navigator_live.py`, `scripts/n8n/repair_sales_navigator_raw_body.py`, `scripts/n8n/wire_sales_navigator_v2_workflows.py`, `scripts/n8n/wire_verified_sales_navigator_credential.py` |
| LT - Unipile Sales Navigator V2 Inbound — V2 event bridge + GHL inbound mirror | `CfpedDQWxoJLEMdL` | `n8n/sales-navigator/WORKFLOW_BUILD_SPEC.md`, `scripts/n8n/audit_sales_navigator_live.py`, `scripts/n8n/probe_sales_navigator_hmac_rejection.py`, `scripts/n8n/repair_sales_navigator_raw_body.py`, `scripts/n8n/wire_sales_navigator_v2_workflows.py`, `scripts/n8n/wire_verified_sales_navigator_credential.py` |
| LT - Sales Navigator V2 Uncertain Write Reconciler — Uncertain-event reconciler | `sFrvSJIZusAbrsFx` | —none— |
| LT - SimpleTexting SMS Send (Webhook, Staged) — SMS send boundary | `Q3Ivnwe4z2Y3cD7A` | `scripts/n8n/patch_simpletexting_auth.ps1`, `scripts/utilities/fix_simpletexting_boundaries.py`, `tools/patch-simpletexting-workflows.ps1` |
| LT - SMS Idempotent Send — Idempotent SMS boundary | `gwaEpWDpTIwsafi8` | `scripts/n8n/patch_simpletexting_auth.ps1`, `scripts/utilities/fix_simpletexting_boundaries.py` |
| LT - SimpleTexting Provider Outbound Router — GHL->SimpleTexting outbound router | `f4VoO1lBWkYRcQai` | `scripts/n8n/patch_simpletexting_auth.ps1`, `scripts/utilities/fix_simpletexting_boundaries.py` |
| LT - SimpleTexting Inbound Reply (Webhook) — Inbound SMS reply handler | `i0pROHpFtN4LYR0Q` | `scripts/n8n/patch_simpletexting_auth.ps1`, `scripts/n8n/patch_simpletexting_event_safety.ps1`, `scripts/utilities/fix_simpletexting_boundaries.py` |
| LT - Voice Agent V1 Outbound Dialer (Vapi) — Vapi dialer | `r7UjWLndmc6EqEUW` | `n8n/voice-agent/README.md`, `n8n/voice-agent/Voice_Agent_V1_Implementation_Spec.md`, `n8n/voice-agent/runbooks/Vapi_Outbound_Call_Training.md`, `n8n/voice-agent/runbooks/Voice_Agent_Operations_Runbook.md`, `scripts/n8n/n8n_vapi_check.py`, `scripts/utilities/vapi_audit.py` |
| LT - Voice Agent V1 Vapi Callback + Tools — Vapi end-of-call ingestion | `fx4UvKUWbqJEY3LK` | `n8n/voice-agent/ARCHIVE.md`, `n8n/voice-agent/README.md`, `n8n/voice-agent/Voice_Agent_V1_Implementation_Spec.md`, `n8n/voice-agent/n8n-workflow/lt-voice-agent-vapi-callback-v1-timeout.ts`, `n8n/voice-agent/runbooks/Vapi_Outbound_Call_Training.md`, `n8n/voice-agent/runbooks/Voice_Agent_Operations_Runbook.md` |
| LT - Voice Queue Vapi Intake Poller — Queue poller | `bYk1Ai6MJLyhTsDZ` | `n8n/voice-agent/README.md`, `scripts/n8n/fix_intake_poller.js` |
| LT - Voice Queue Enqueue — Queue enqueue webhook | `XzcpOBi9YcIhJPck` | `n8n/voice-agent/README.md` |
| LT - Emerald Campaign Sender Release Dispatcher — Emerald live-send dispatcher | `8UXlpoMJnQ229AuG` | —none— |
| LT - DAN Campaign Sender Release Dispatcher — DAN live-send dispatcher | `toUG1yPDmFG48KEP` | —none— |
| LT - Partnership Email Dispatcher — Partnership email sender | `Xshck23cKo1yXL9D` | —none— |
| LT - Newsletter Dispatcher — Weekly newsletter sender | `vru7OtCkDnPJkWt2` | —none— |
| LT - Newsletter Contact Prep — Newsletter eligible cohorts | `vvPdJMzBJMgcf5I9` | —none— |
| LT - Email Event Ingest — Provider email event webhook | `ZrqFN8qLKO8eVHDc` | `n8n/REPORTING_IMPLEMENTATION.md` |
| LT - Apollo Phone Enrichment Polling — Apollo worker | `JH8ShfpglWmLMZ3l` | `scripts/apollo/capture_apollo_rejection_details.py`, `scripts/apollo/consolidate_apollo_phone_reveal.py`, `scripts/apollo/fix_apollo_people_match_path.py`, `scripts/apollo/fix_apollo_phone_reveal_query.py`, `scripts/apollo/pause_apollo_worker_schedule.py`, `scripts/apollo/resume_apollo_worker_single_contact.py` |
| GHL Apollo Phone Enrichment - Callback Handler V4 — Apollo callback | `U7c6byTLXAMgcS75` | —none— |
| LT - Apollo Queued Timeout Reaper — Apollo timeout reaper | `RL5ZyUoshSPbmVA1` | —none— |
| LT - Call Outcome Ingest — Vapi/GHL call outcome webhook | `PUCfTZBANSPcgS0c` | `scripts/utilities/vapi_audit.py` |
| LT - MQL Tag Event Ingest — MQL tag ledger webhook | `U9oc2tZRsr4zq6IM` | `scripts/check_recovered_mql_clicks.py`, `scripts/inspect_mql_ledger.py`, `scripts/record_mql_provenance.py` |
| LT - Booking Link Click Intake (Webhook) — Booking attribution intake | `1diZyFmTqWQUEny3` | `scripts/audit_retained_click_events.py`, `scripts/audit_sql_tag_writers.py`, `scripts/check_click_registry_utm.py`, `scripts/check_recovered_mql_clicks.py`, `scripts/continue_v1_reporting.py`, `scripts/count_recoverable_click_receipts.py` |
| LT - Booking Link SMS Redirect (Webhook) — Booking attribution SMS redirect | `9HT13te9FalOtUZM` | —none— |
| LT - Vertical Sender Assign (Webhook) — Per-vertical sender round-robin | `z0Sq4AE3Xdbgw2Yh` | —none— |
| LT - Last-Touch Owner Resolver + 14-Day Backfill — Owner attribution resolver | `KQjosWjChMYbhZkF` | `scripts/build_last_touch_owner_workflow.py` |
| WL - Micro - Set Vertical Sender (Webhook) — GHL caller, **not an n8n workflow** | GHL `52f6a14a-927c-433b-82c3-9503feb14110` | —not part of n8n source count— |
| LT - Inbound Intent Priority Router — Priority router (execute-workflow target) | `URpjcm2k5isHUyls` | —none— |

**Workflows with no tracked repo ID reference (15)** rely solely on the live
n8n-lt instance and any dated archive/local snapshots; treat their repo replications
as future work if/when they are edited by an approved change.

## Rollback strategy (documented, not newly-built)
- Live n8n-lt API export (GET) is the authoritative pre-change snapshot mechanism and
  can be taken fresh at any time; no scheduled n8n backup exists.
- The `local-archive/n8n/` dated snapshots for **13 workflow IDs** are all older than
  the currently published versions — useful as history/rollback only after per-file
  review (see archive classification).
- There is **no verified automated n8n workflow backup/restore pipeline**; the
  documented practice is to export before every future change. Any new automated
  backup design is an owner-decision item, not an authorized build.
- Critical workflows that will not run without live Postgres tables (LinkedIn/voice
  queue/report state) also require the DB schema inventory + database availability;
  see [postgres schema inventory](postgres-schema-inventory-2026-11-05.md).
