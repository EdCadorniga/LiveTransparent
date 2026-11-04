# Phase 3 exact-path script/artifact classification — 2026-11-05

Read-only enumeration + secret-pattern scan (ripgrep, count-only; matched VALUES never
emitted — only variable/hit NAMES) + markdown reference map. No classified script was
executed. No artifact was moved, changed, or deleted. Not a deletion manifest; no cleanup
is authorized by this document.

**Scope/sizes:** 443 script-like files across `scripts/`, `local-scripts/`, `tools/`,
`marketing/`, `New Campaigns October 2026/` (invoice/invoicing directory-segments excluded,
`__pycache__`/`node_modules` excluded): **2,198,072 bytes** total.
**Doc references:** 223 of 443 files are mentioned somewhere in Markdown
(docs/sessions, runbooks, AGENTS, plans) — that is provenance support, not a safety
verdict.

## Sensitive-pattern hit table (names only)

Any file with a long literal assignment (`API_KEY = '<literal>'`, `TRACK_SECRET = '<literal>'`,
JWT-like strings, `pit-` prefixes, or katwill references) is listed. Values are NOT printed;
owners must review the exact file before reuse. Test-capture files with embedded JWTs are
**keep pending sensitivity review** (do not publish/redistribute).

| path | hits (names) | provisional action |
|---|---|---|
| `local-scripts/_state_sync_sql.py` | katwill | review-before-reuse / harden (owner decision) |
| `local-scripts/build_mass_email_stage.py` | env_constant_with_long_literal, ghl_pit | review-before-reuse / harden (owner decision) |
| `local-scripts/linkedin-invite-withdrawals/capture-20261021T183214Z-45b220e7-431a45d2.withdrawal.jsonl` | jwt | review-before-reuse / harden (owner decision) |
| `marketing/automation/scripts/patch_simpletexting_callbacks.py` | ghl_pit, jwt | review-before-reuse / harden (owner decision) |
| `marketing/automation/scripts/rerun_bad_emerald_sso_companies.py` | jwt | review-before-reuse / harden (owner decision) |
| `marketing/email-marketing/cold-outreach-prep/reports/retest-api-key-20260220T053242Z.txt` | jwt | review-before-reuse / harden (owner decision) |
| `marketing/email-marketing/emerald-email-campaign/artifacts/publish_emerald_executive_sso_workflow.py` | ghl_pit | review-before-reuse / harden (owner decision) |
| `marketing/email-marketing/emerald-email-campaign/artifacts/update_emerald_exec_workflow.py` | apikey_literal, env_constant_with_long_literal, jwt | review-before-reuse / harden (owner decision) |
| `scripts/emerald/run_dispensaries.py` | apikey_literal, jwt | review-before-reuse / harden (owner decision) |
| `scripts/n8n/fix_sheets_node.py` | apikey_literal, env_constant_with_long_literal, jwt | review-before-reuse / harden (owner decision) |
| `scripts/social-reporting/fix_brands_code.py` | apikey_literal, env_constant_with_long_literal, jwt | review-before-reuse / harden (owner decision) |
| `scripts/utilities/fix_parse_csv.py` | apikey_literal, env_constant_with_long_literal, jwt | review-before-reuse / harden (owner decision) |

Note: the katwill hit in `local-scripts/_state_sync_sql.py` is a doc comment restating the
n8n-lt-only rule (verified by reading the single matching comment line; no katwill call
exists in the scanned trees). `pit-`/JWT-style hits may be test or stale artifacts; each
file is listed so an owner may review the exact literal before any reuse, rotation decision,or archive move.

**Live-credential containment (2026-11-05):** an exact-value containment check found the
*current live GHL PIT* present verbatim in **1** classified script-like file(s): `local-scripts/build_mass_email_stage.py`. The value was never emitted into this artifact. Rotation/remediation is the owner's
call and must be coordinated with all workflow callers (see the plan's owner-decision §6.6).
**Owner resolution 2026-11-05 (later): Ed directed retention of the latest PIT from `.env` —
no rotation now; the token's presence in Git history and the local archive files is an
owner-accepted residual risk, with redistribution precautions unchanged.**

## Family summary and provisional classification rules

| family | files | bytes | provisional class |
|---|---|---|---|
| `New Campaigns October 2026/` | 15 | 56,717 | **Keep pending campaign-closure evidence review** (auditable evidence: import-prep, audit and reconciliation scripts matching the October vertical campaigns). |
| `local-scripts/` | 153 | 577,556 | **Owner decision** (operator-only helpers, diagnostics, captures). `local-scripts/linkedin-invite-withdrawals/` remains explicitly **held** — worker/ledger/provider artifacts with the standing 310-unledgered-invitation scope. Credential-bearing files marked 'review-before-reuse'. |
| `marketing/` | 28 | 265,875 | **Owner decision** (historical marketing/automation artifacts). Credential-bearing files: redact/migrate then archive. |
| `scripts/` | 242 | 1,256,534 | **Keep — maintained operational source** pending owner review. Repairs/deploy/migration helpers may be the sole reproducible source for live state; do not remove without per-file dependency comparison. Files with credential hits: keep but harden before reuse. |
| `tools/` | 5 | 41,390 | **Keep — source pending owner review** (small set). |

## `New Campaigns October 2026/` exact paths (15)

| path | bytes | mtime | doc refs | hits |
|---|---|---|---|---|
| `New Campaigns October 2026/GHL Import Prep/audit_all_vertical_senders.py` | 3,803 | 2026-10-09 | 1 |  |
| `New Campaigns October 2026/GHL Import Prep/audit_crypto_phone_matches.py` | 4,020 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/audit_mushroom_vertical_scan.py` | 2,771 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/audit_vertical_sender_fields.py` | 4,569 | 2026-10-09 | 1 |  |
| `New Campaigns October 2026/GHL Import Prep/build_dispensaries_existing_update.py` | 2,031 | 2026-10-12 | 1 |  |
| `New Campaigns October 2026/GHL Import Prep/finalize_dispensaries_split.py` | 3,830 | 2026-10-10 | 4 |  |
| `New Campaigns October 2026/GHL Import Prep/find_mushroom_missing.py` | 2,977 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/prepare_crypto_import.py` | 2,045 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/prepare_crypto_sender_assignment.py` | 1,258 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/prepare_gambling_dispensaries_import.py` | 7,146 | 2026-10-10 | 4 |  |
| `New Campaigns October 2026/GHL Import Prep/prepare_import_with_sender.py` | 3,322 | 2026-10-10 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/prepare_mushroom_sender_and_tag.py` | 1,094 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/reconcile_crypto_cohort.py` | 5,947 | 2026-10-09 | 0 |  |
| `New Campaigns October 2026/GHL Import Prep/reconcile_peptides_cohort.py` | 4,305 | 2026-10-10 | 1 |  |
| `New Campaigns October 2026/GHL Import Prep/split_dispensaries_net_new.py` | 7,599 | 2026-10-10 | 3 |  |

## `local-scripts/` exact paths (153)

| path | bytes | mtime | doc refs | hits |
|---|---|---|---|---|
| `local-scripts/_accounts_pending.py` | 2,714 | 2026-10-22 | 0 |  |
| `local-scripts/_add_meeting_booked_tag.py` | 1,890 | 2026-10-13 | 0 |  |
| `local-scripts/_analyze_pending_invites.py` | 2,281 | 2026-10-22 | 1 |  |
| `local-scripts/_append_agents.py` | 5,906 | 2026-10-13 | 0 |  |
| `local-scripts/_append_agents2.py` | 2,498 | 2026-10-13 | 0 |  |
| `local-scripts/_append_agents3.py` | 3,166 | 2026-10-13 | 0 |  |
| `local-scripts/_append_test.py` | 4,022 | 2026-10-13 | 0 |  |
| `local-scripts/_append_test2.py` | 4,404 | 2026-10-13 | 0 |  |
| `local-scripts/_append_test3.py` | 5,922 | 2026-10-13 | 0 |  |
| `local-scripts/_append_test5.py` | 3,780 | 2026-10-13 | 0 |  |
| `local-scripts/_append_test6.py` | 6,633 | 2026-10-13 | 0 |  |
| `local-scripts/_apply_cache_to_v1.py` | 3,908 | 2026-10-13 | 0 |  |
| `local-scripts/_apply_click_fix.py` | 7,354 | 2026-10-13 | 0 |  |
| `local-scripts/_apply_utm_medium_ddl.py` | 597 | 2026-10-13 | 0 |  |
| `local-scripts/_build_cleanup_workflow.py` | 13,111 | 2026-10-13 | 1 |  |
| `local-scripts/_build_mql_ingest.py` | 9,185 | 2026-10-13 | 0 |  |
| `local-scripts/_build_v1_cache.py` | 3,475 | 2026-10-13 | 0 |  |
| `local-scripts/_build_v1_mql_cards.py` | 4,941 | 2026-10-13 | 0 |  |
| `local-scripts/_char_unmatched.py` | 2,948 | 2026-10-22 | 1 |  |
| `local-scripts/_characterize_skipped.py` | 3,555 | 2026-10-22 | 1 |  |
| `local-scripts/_check_cache.py` | 154 | 2026-10-13 | 0 |  |
| `local-scripts/_check_count.py` | 231 | 2026-10-13 | 0 |  |
| `local-scripts/_check_emerald_opens.py` | 1,531 | 2026-10-13 | 0 |  |
| `local-scripts/_check_export.py` | 1,466 | 2026-10-13 | 0 |  |
| `local-scripts/_check_feedback.py` | 323 | 2026-10-13 | 0 |  |
| `local-scripts/_check_ghl_stats.py` | 1,720 | 2026-10-13 | 0 |  |
| `local-scripts/_check_key.py` | 813 | 2026-10-13 | 0 |  |
| `local-scripts/_check_keys.py` | 405 | 2026-10-13 | 0 |  |
| `local-scripts/_check_mql_events.py` | 406 | 2026-10-13 | 0 |  |
| `local-scripts/_check_null_handling.py` | 2,259 | 2026-10-22 | 1 |  |
| `local-scripts/_check_pipeline.py` | 952 | 2026-10-13 | 0 |  |
| `local-scripts/_check_pipeline2.py` | 767 | 2026-10-13 | 0 |  |
| `local-scripts/_check_pit.py` | 1,245 | 2026-10-13 | 0 |  |
| `local-scripts/_check_queue.py` | 517 | 2026-10-13 | 0 |  |
| `local-scripts/_check_recent.py` | 345 | 2026-10-13 | 0 |  |
| `local-scripts/_check_sms_auth.py` | 2,917 | 2026-10-13 | 0 |  |
| `local-scripts/_check_token.py` | 570 | 2026-10-13 | 0 |  |
| `local-scripts/_check_trigger_links.py` | 1,225 | 2026-10-13 | 0 |  |
| `local-scripts/_check_v2_email.py` | 1,611 | 2026-10-13 | 0 |  |
| `local-scripts/_check_workflow_api.py` | 1,206 | 2026-10-13 | 0 |  |
| `local-scripts/_count_pending_invites.py` | 2,357 | 2026-10-22 | 1 |  |
| `local-scripts/_crosscheck_withdrawals.py` | 1,415 | 2026-10-22 | 1 |  |
| `local-scripts/_diag_appts.py` | 1,141 | 2026-10-13 | 0 |  |
| `local-scripts/_dispatcher_code.js` | 14,598 | 2026-10-02 | 0 |  |
| `local-scripts/_dispatcher_exec_check.py` | 2,907 | 2026-10-22 | 1 |  |
| `local-scripts/_dump_pending_ids.py` | 1,660 | 2026-10-22 | 0 |  |
| `local-scripts/_eos_check.py` | 954 | 2026-10-02 | 0 |  |
| `local-scripts/_eos_verify.py` | 4,385 | 2026-10-22 | 0 |  |
| `local-scripts/_exec_window.py` | 2,448 | 2026-10-22 | 1 |  |
| `local-scripts/_fetch_v2_email.py` | 2,333 | 2026-10-13 | 1 |  |
| `local-scripts/_final_campaign_state.py` | 3,656 | 2026-10-22 | 1 |  |
| `local-scripts/_final_check.py` | 1,191 | 2026-10-02 | 0 |  |
| `local-scripts/_find_dan_workflow.py` | 2,993 | 2026-10-13 | 0 |  |
| `local-scripts/_find_invite_senders.py` | 2,442 | 2026-10-22 | 1 |  |
| `local-scripts/_find_unattributed.py` | 2,185 | 2026-10-13 | 0 |  |
| `local-scripts/_fix_null_notes.py` | 2,455 | 2026-10-22 | 1 |  |
| `local-scripts/_ghl_invite_targets.py` | 3,328 | 2026-10-22 | 1 |  |
| `local-scripts/_ghl_tag_check.py` | 3,149 | 2026-10-22 | 1 |  |
| `local-scripts/_hold_impact.py` | 2,995 | 2026-10-22 | 1 |  |
| `local-scripts/_inspect_ba.py` | 258 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_booking.py` | 758 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_click_intake.py` | 969 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_downstream.py` | 1,623 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_meetings.py` | 8,129 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_origin.py` | 6,597 | 2026-10-13 | 1 |  |
| `local-scripts/_inspect_schema.py` | 464 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_sms_auth.py` | 1,396 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_sms_backfill.py` | 1,570 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_sms_code.py` | 400 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_sources.py` | 1,572 | 2026-10-13 | 0 |  |
| `local-scripts/_inspect_vertical_emails.py` | 1,022 | 2026-10-13 | 1 |  |
| `local-scripts/_inspect_vertical_wf.py` | 2,593 | 2026-10-22 | 1 |  |
| `local-scripts/_linkedin_state_check.py` | 3,004 | 2026-10-22 | 1 |  |
| `local-scripts/_list_pipelines.py` | 1,489 | 2026-10-13 | 0 |  |
| `local-scripts/_mass_email_set_config.py` | 2,298 | 2026-09-16 | 1 |  |
| `local-scripts/_mql_vs_sql.py` | 2,136 | 2026-10-13 | 0 |  |
| `local-scripts/_peek.py` | 346 | 2026-10-13 | 0 |  |
| `local-scripts/_per_vertical_status.py` | 4,321 | 2026-10-22 | 1 |  |
| `local-scripts/_poll_email_stats.py` | 4,553 | 2026-10-13 | 1 |  |
| `local-scripts/_print_click_code.py` | 243 | 2026-10-13 | 0 |  |
| `local-scripts/_profile_invites.py` | 2,129 | 2026-10-22 | 1 |  |
| `local-scripts/_recent_batches.py` | 3,395 | 2026-10-22 | 1 |  |
| `local-scripts/_reconcile_pending.py` | 4,201 | 2026-10-22 | 1 |  |
| `local-scripts/_relations_backfill_code.js` | 5,330 | 2026-10-02 | 0 |  |
| `local-scripts/_rewire_click.py` | 2,273 | 2026-10-13 | 0 |  |
| `local-scripts/_scope_withdrawal.py` | 5,862 | 2026-10-22 | 1 |  |
| `local-scripts/_state_sync_code.js` | 6,098 | 2026-10-02 | 0 |  |
| `local-scripts/_state_sync_sql.py` | 2,262 | 2026-10-22 | 1 | katwill |
| `local-scripts/_test_patch_sql.py` | 1,553 | 2026-10-13 | 0 |  |
| `local-scripts/_test_sms_auth.py` | 3,386 | 2026-10-13 | 0 |  |
| `local-scripts/_trace_sql_tag.py` | 2,002 | 2026-10-13 | 0 |  |
| `local-scripts/_trace_sqls.py` | 982 | 2026-10-13 | 0 |  |
| `local-scripts/_update_evidence.py` | 3,077 | 2026-10-13 | 0 |  |
| `local-scripts/_verify_capture.py` | 3,976 | 2026-10-22 | 1 |  |
| `local-scripts/_verify_progress.py` | 2,836 | 2026-10-22 | 1 |  |
| `local-scripts/_verify_scope_live.py` | 4,128 | 2026-10-22 | 1 |  |
| `local-scripts/_vert-GQv0yNqDtibOXMB8.js` | 31,411 | 2026-10-22 | 0 |  |
| `local-scripts/_vert-KsJ3xkDoIfXzjVDw.js` | 31,415 | 2026-10-22 | 0 |  |
| `local-scripts/_vert_code.py` | 2,745 | 2026-10-22 | 1 |  |
| `local-scripts/_vps_exec.py` | 1,454 | 2026-09-16 | 1 |  |
| `local-scripts/_vps_psql.py` | 2,685 | 2026-09-10 | 5 |  |
| `local-scripts/audit_apollo_tag_opportunities.ps1` | 2,118 | 2026-09-16 | 0 |  |
| `local-scripts/build_mass_email_stage.py` | 42,957 | 2026-09-16 | 1 | env_constant_with_long_literal, ghl_pit |
| `local-scripts/check_utm_booking_clicks.py` | 2,528 | 2026-10-15 | 0 |  |
| `local-scripts/create_apollo_tag_opportunities.ps1` | 4,509 | 2026-09-16 | 1 |  |
| `local-scripts/enrich_linkedin_backfill_worklist.py` | 3,635 | 2026-09-11 | 0 |  |
| `local-scripts/fix_mass_email_tracking.py` | 6,538 | 2026-09-16 | 1 |  |
| `local-scripts/linkedin-invite-withdrawals/run_authorized_cleanup.py` | 4,336 | 2026-10-13 | 2 |  |
| `local-scripts/linkedin-invite-withdrawals/run_pre_cutoff_withdrawal.py` | 6,636 | 2026-10-22 | 1 |  |
| `local-scripts/linkedin-invite-withdrawals/verify_capture.py` | 1,901 | 2026-10-13 | 1 |  |
| `local-scripts/live_import_apollo_62.ps1` | 3,111 | 2026-09-16 | 0 |  |
| `local-scripts/lt_apply_report_fix.py` | 2,684 | 2026-09-15 | 0 |  |
| `local-scripts/lt_build_report_fix.py` | 8,575 | 2026-09-15 | 0 |  |
| `local-scripts/lt_check_dispatcher_execs.py` | 1,636 | 2026-09-15 | 0 |  |
| `local-scripts/lt_dispatcher_timeline.py` | 1,755 | 2026-09-15 | 0 |  |
| `local-scripts/lt_dump_campaign_nodes_full.py` | 1,062 | 2026-09-15 | 0 |  |
| `local-scripts/lt_dump_campaign_summary.py` | 1,628 | 2026-09-15 | 0 |  |
| `local-scripts/lt_dump_campaign_summary_full.py` | 2,006 | 2026-09-15 | 0 |  |
| `local-scripts/lt_dump_dispatcher_nodes.py` | 1,628 | 2026-09-15 | 0 |  |
| `local-scripts/lt_exec_email_ctes.py` | 1,878 | 2026-09-15 | 0 |  |
| `local-scripts/lt_exec_email_metric.py` | 2,071 | 2026-09-15 | 0 |  |
| `local-scripts/lt_find_report_workflows.py` | 1,207 | 2026-09-15 | 0 |  |
| `local-scripts/lt_inspect_dispatcher.py` | 2,740 | 2026-09-15 | 0 |  |
| `local-scripts/prepare_apollo_vp_ghl_import.ps1` | 10,375 | 2026-09-16 | 0 |  |
| `local-scripts/query_apollo_source_emails.ps1` | 1,214 | 2026-09-16 | 0 |  |
| `local-scripts/reconcile_apollo_114_tags.ps1` | 5,003 | 2026-09-16 | 0 |  |
| `local-scripts/repair_apollo_122_tags.ps1` | 2,385 | 2026-09-16 | 0 |  |
| `local-scripts/suppress_linkedin_dms.py` | 10,555 | 2026-09-10 | 5 |  |
| `local-scripts/update_mass_email_schema_node.py` | 2,056 | 2026-09-16 | 0 |  |
| `local-scripts/upsert_apollo_missing_114.ps1` | 3,896 | 2026-09-16 | 0 |  |
| `local-scripts/verify_mass_email_schema_node.py` | 1,470 | 2026-09-16 | 0 |  |
| `local-scripts/vertical-inspect-3ttEvr5NMcQCS4Hp-19d48bc3-0657-4c98-a4b4-8cc3bf89cf69.js` | 1,980 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-3ttEvr5NMcQCS4Hp-a90e0a4b-031f-43de-9ddc-bd2b824e7f36.js` | 4,832 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-3ttEvr5NMcQCS4Hp-b68c21da-0c79-4fa2-a238-f667aa1f097b.js` | 2,024 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-3ttEvr5NMcQCS4Hp-df32f8ba-f260-4aba-ac67-49e7df2e83db.js` | 8,142 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-267e8329-3d88-4028-b075-3793a69499c7.js` | 44 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-2ecf8a2b-492f-4942-a000-be99ee16ffe8.js` | 682 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-3b9e6f8e-6464-46ba-a1a4-2d4a8df9be64.js` | 151 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-494c99c8-ffd6-4aa3-aef2-567a39539462.js` | 421 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-4f1c3bf5-df3e-49d2-aae2-a5f8be57f6a3.js` | 2,631 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-564a9e26-67b9-4e74-b97b-e57d0f3b17ad.js` | 221 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-68d6340d-5537-4090-86fb-d09d42fb72a2.js` | 228 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-97b29cda-f5cf-4c6e-b4c9-f1b027354f6e.js` | 83 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-ZiYEBuP7xdddhnUB-ab8c121c-317e-45ed-9101-e52e0339bbd8.js` | 630 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-d0tEtijajisIsYcs-323e1071-3efa-4461-8e7c-7ab13a083b72.js` | 1,287 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-d0tEtijajisIsYcs-85954f39-ba9d-4b64-9447-a306811f09c4.js` | 18,576 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-d0tEtijajisIsYcs-bad0143c-cccc-493b-b2fe-f35f8300b9c8.js` | 26,352 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-d0tEtijajisIsYcs-ccc21698-51e6-482d-937f-f224f4cbfc57.js` | 1,302 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-d0tEtijajisIsYcs-fe3c2162-fb53-410b-ab9d-cae4991cdee9.js` | 530 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-fXxw5lanZcDmUrst-0b6ddd52-8ea8-483c-bc36-2815793f45b8.js` | 5,022 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-fXxw5lanZcDmUrst-172a778e-5e21-43c3-a600-0e042c5490b5.js` | 1,325 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-fXxw5lanZcDmUrst-7aa7e85d-6743-46e8-bf19-f213632e248b.js` | 15,766 | 2026-10-15 | 0 |  |
| `local-scripts/vertical-inspect-fXxw5lanZcDmUrst-bdb25d41-02a0-4d9d-ab5b-273591aac361.js` | 748 | 2026-10-15 | 0 |  |

## `marketing/` exact paths (28)

| path | bytes | mtime | doc refs | hits |
|---|---|---|---|---|
| `marketing/automation/scripts/add_cameron_sms.ps1` | 5,459 | 2026-07-07 | 0 |  |
| `marketing/automation/scripts/build_v5_tagging_import.py` | 1,966 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/check_ghl_get.ps1` | 1,102 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/emerald_intro_backfill_sender.py` | 11,903 | 2026-04-11 | 0 |  |
| `marketing/automation/scripts/emerald_tag_finance_contacts.py` | 7,192 | 2026-04-12 | 0 |  |
| `marketing/automation/scripts/fix_config.py` | 366 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/generate_ed_mapping_tags.py` | 5,862 | 2026-04-14 | 0 |  |
| `marketing/automation/scripts/get_ghl_workflow.ps1` | 1,957 | 2026-04-17 | 0 |  |
| `marketing/automation/scripts/get_n8n_workflow.ps1` | 1,292 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/get_template.ps1` | 1,164 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/patch_ghl_template.ps1` | 1,850 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/patch_ghl_template_raw.ps1` | 1,455 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/patch_simpletexting_callbacks.py` | 31,516 | 2026-03-25 | 1 | ghl_pit, jwt |
| `marketing/automation/scripts/rerun_bad_emerald_sso_companies.py` | 4,581 | 2026-03-31 | 1 | jwt |
| `marketing/automation/scripts/send_ghl_simpletexting_test.ps1` | 1,983 | 2026-05-25 | 0 |  |
| `marketing/automation/scripts/send_live_sms_test.ps1` | 1,488 | 2026-07-07 | 0 |  |
| `marketing/automation/scripts/update_n8n_template_registry.ps1` | 6,797 | 2026-07-08 | 0 |  |
| `marketing/automation/scripts/upload_ghl_builder.ps1` | 2,541 | 2026-04-16 | 0 |  |
| `marketing/automation/scripts/upload_ghl_templates.ps1` | 2,481 | 2026-04-16 | 0 |  |
| `marketing/email-marketing/cold-outreach-prep/prepare_cold_outreach.ps1` | 10,437 | 2026-02-25 | 1 |  |
| `marketing/email-marketing/cold-outreach-prep/scripts/validate_apollo_csv_mapping.py` | 4,731 | 2026-02-25 | 1 |  |
| `marketing/email-marketing/emerald-contacts/build_ghl_import.py` | 10,481 | 2026-03-24 | 2 |  |
| `marketing/email-marketing/emerald-email-campaign/artifacts/emerald_exec_company_sync_finalize.js` | 29,018 | 2026-03-31 | 0 |  |
| `marketing/email-marketing/emerald-email-campaign/artifacts/emerald_exec_company_sync_prepare.js` | 16,621 | 2026-03-31 | 0 |  |
| `marketing/email-marketing/emerald-email-campaign/artifacts/emerald_exec_company_sync_process.js` | 28,765 | 2026-03-31 | 0 |  |
| `marketing/email-marketing/emerald-email-campaign/artifacts/publish_emerald_campaign_workflows.py` | 31,934 | 2026-04-14 | 1 |  |
| `marketing/email-marketing/emerald-email-campaign/artifacts/publish_emerald_executive_sso_workflow.py` | 12,211 | 2026-03-31 | 0 | ghl_pit |
| `marketing/email-marketing/emerald-email-campaign/artifacts/update_emerald_exec_workflow.py` | 28,722 | 2026-03-31 | 0 | apikey_literal, env_constant_with_long_literal, jwt |

## `scripts/` exact paths (242)

| path | bytes | mtime | doc refs | hits |
|---|---|---|---|---|
| `scripts/align_booking_notification.py` | 1,172 | 2026-10-14 | 0 |  |
| `scripts/apollo/add_apollo_fields.py` | 1,528 | 2026-07-03 | 1 |  |
| `scripts/apollo/capture_apollo_rejection_details.py` | 5,496 | 2026-10-08 | 0 |  |
| `scripts/apollo/consolidate_apollo_phone_reveal.py` | 6,860 | 2026-10-08 | 1 |  |
| `scripts/apollo/fix_apollo_people_match_path.py` | 4,438 | 2026-10-09 | 0 |  |
| `scripts/apollo/fix_apollo_phone_reveal_query.py` | 5,790 | 2026-10-08 | 0 |  |
| `scripts/apollo/pause_apollo_worker_schedule.py` | 3,973 | 2026-10-09 | 0 |  |
| `scripts/apollo/prepare_all_verticals_phone_enrichment.py` | 3,138 | 2026-10-08 | 1 |  |
| `scripts/apollo/prepare_mushroom_automapped_import.py` | 4,073 | 2026-10-08 | 1 |  |
| `scripts/apollo/prepare_mushroom_create_with_apollo.py` | 2,349 | 2026-10-08 | 0 |  |
| `scripts/apollo/prepare_mushroom_existing_contact_queue.py` | 2,371 | 2026-10-08 | 0 |  |
| `scripts/apollo/remove_apollo.py` | 831 | 2026-07-03 | 1 |  |
| `scripts/apollo/resume_apollo_worker_single_contact.py` | 7,188 | 2026-10-08 | 0 |  |
| `scripts/apollo/resume_apollo_worker_with_sanitized_diagnostics.py` | 6,149 | 2026-10-08 | 0 |  |
| `scripts/apollo/serialize_apollo_webhook_intake.py` | 6,967 | 2026-10-08 | 1 |  |
| `scripts/apollo/tune_apollo_worker_rate.py` | 6,802 | 2026-10-08 | 1 |  |
| `scripts/audit_mushroom_import.py` | 10,011 | 2026-10-08 | 1 |  |
| `scripts/audit_nicotine_import.py` | 14,090 | 2026-10-08 | 2 |  |
| `scripts/audit_retained_click_events.py` | 1,075 | 2026-10-14 | 0 |  |
| `scripts/audit_sql_tag_writers.py` | 1,769 | 2026-10-13 | 1 |  |
| `scripts/audit_v1_accuracy.py` | 3,187 | 2026-10-19 | 3 |  |
| `scripts/audit_vertical_campaign_contacts.py` | 5,395 | 2026-10-13 | 1 |  |
| `scripts/audit_vertical_campaign_messages.py` | 2,409 | 2026-10-13 | 1 |  |
| `scripts/build_last_touch_owner_workflow.py` | 16,384 | 2026-10-12 | 2 |  |
| `scripts/build_v1_band_improvements.py` | 5,426 | 2026-10-13 | 0 |  |
| `scripts/cache_report_sources.py` | 8,285 | 2026-10-14 | 0 |  |
| `scripts/capture_opportunity_creators.py` | 3,314 | 2026-10-14 | 0 |  |
| `scripts/capture_v1_public_qa.py` | 973 | 2026-10-13 | 0 |  |
| `scripts/check_booking_time_evidence.py` | 316 | 2026-10-14 | 0 |  |
| `scripts/check_click_original_time.py` | 199 | 2026-10-14 | 0 |  |
| `scripts/check_click_registry_utm.py` | 333 | 2026-10-14 | 0 |  |
| `scripts/check_creator_snapshot.py` | 182 | 2026-10-14 | 0 |  |
| `scripts/check_mql_recovery_executions.py` | 637 | 2026-10-14 | 0 |  |
| `scripts/check_recovered_mql_clicks.py` | 1,209 | 2026-10-14 | 0 |  |
| `scripts/check_v1_cache_query.py` | 676 | 2026-10-13 | 0 |  |
| `scripts/check_weekly_email_pit_access.py` | 1,156 | 2026-10-14 | 0 |  |
| `scripts/continue_v1_reporting.py` | 6,381 | 2026-10-13 | 2 |  |
| `scripts/count_new_bookings.py` | 972 | 2026-10-14 | 0 |  |
| `scripts/count_recoverable_click_receipts.py` | 253 | 2026-10-14 | 0 |  |
| `scripts/deploy/acceptance_checker/build_accept_sql.js` | 1,993 | 2026-10-02 | 1 |  |
| `scripts/deploy/acceptance_checker/build_find_sql.js` | 1,952 | 2026-10-02 | 1 |  |
| `scripts/deploy/acceptance_checker/build_payload.js` | 4,706 | 2026-10-02 | 1 |  |
| `scripts/deploy/acceptance_checker/normalize.js` | 7,974 | 2026-10-02 | 1 |  |
| `scripts/deploy/deploy_acceptance_checker.py` | 6,924 | 2026-10-02 | 4 |  |
| `scripts/deploy/deploy_report_proxy.py` | 1,069 | 2026-08-12 | 2 |  |
| `scripts/deploy/deploy_report_vps.py` | 1,738 | 2026-07-31 | 1 |  |
| `scripts/deploy/deploy_report_vps_local.py` | 3,046 | 2026-10-19 | 13 |  |
| `scripts/deploy/deploy_runner.py` | 3,742 | 2026-09-01 | 4 |  |
| `scripts/deploy/fix_runner_pg.py` | 753 | 2026-08-18 | 1 |  |
| `scripts/deploy/fix_state_upsert_esc.py` | 3,564 | 2026-10-02 | 3 |  |
| `scripts/deploy/patch_runner_pg.py` | 1,263 | 2026-08-18 | 1 |  |
| `scripts/deploy/restart_n8n.py` | 1,190 | 2026-07-08 | 1 |  |
| `scripts/diagnostics/_check_npm.py` | 893 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/_check_npm_shim.py` | 1,118 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/_check_pg_v2.py` | 836 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/_check_pg_version.py` | 1,022 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/_check_runner.py` | 995 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/_find_pg.py` | 1,045 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/check_db.py` | 1,057 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/check_db2.py` | 1,507 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/check_dms.py` | 896 | 2026-07-08 | 1 |  |
| `scripts/diagnostics/check_partnership_db.py` | 2,304 | 2026-07-31 | 1 |  |
| `scripts/diagnostics/check_runner_paths.py` | 1,107 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/check_send_status.py` | 1,294 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/db_check.py` | 809 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check2.py` | 1,130 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check3.py` | 1,488 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check4.py` | 1,490 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check5.py` | 2,172 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check6.py` | 1,533 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check7.py` | 1,949 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check8.py` | 1,773 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_check9.py` | 1,634 | 2026-07-07 | 1 |  |
| `scripts/diagnostics/db_query.py` | 1,539 | 2026-07-08 | 1 |  |
| `scripts/diagnostics/find_anywhere.py` | 1,653 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/find_pg.py` | 1,079 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/find_pg_protocol.py` | 1,192 | 2026-08-18 | 1 |  |
| `scripts/diagnostics/find_table.py` | 1,002 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/find_table2.py` | 1,170 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/query_pg.py` | 1,769 | 2026-07-03 | 1 |  |
| `scripts/diagnostics/ssh_baseline.py` | 2,973 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_fix1_edit.py` | 4,883 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_fix2_apply.py` | 1,804 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_health2.py` | 2,087 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_inv_tcp.py` | 2,737 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_pgrecheck.py` | 2,840 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_probe2.py` | 3,355 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_probe3.py` | 2,097 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_probe4.py` | 1,925 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_probe5.py` | 3,035 | 2026-09-07 | 1 |  |
| `scripts/diagnostics/ssh_verify_fix.py` | 2,577 | 2026-09-07 | 1 |  |
| `scripts/email/gmail_read.py` | 3,935 | 2026-09-08 | 3 |  |
| `scripts/email/gmail_send.py` | 2,860 | 2026-09-07 | 1 |  |
| `scripts/emerald/check_emerald.py` | 1,538 | 2026-07-08 | 1 |  |
| `scripts/emerald/clean_august_2026_emerald_contacts.ps1` | 9,828 | 2026-08-26 | 1 |  |
| `scripts/emerald/enroll_august_2026_emerald.ps1` | 10,305 | 2026-08-26 | 1 |  |
| `scripts/emerald/reconcile_august_2026_emerald_live.ps1` | 5,505 | 2026-08-26 | 4 |  |
| `scripts/emerald/run_dispensaries.py` | 1,621 | 2026-07-03 | 1 | apikey_literal, jwt |
| `scripts/enrich_v1_booking_sources.py` | 6,409 | 2026-10-19 | 0 |  |
| `scripts/enrich_v1_opportunity_actions.py` | 6,560 | 2026-10-19 | 0 |  |
| `scripts/finish_cache_stale_policy.py` | 707 | 2026-10-14 | 0 |  |
| `scripts/fix_click_payload_identity.py` | 4,548 | 2026-10-14 | 0 |  |
| `scripts/fix_form_mql_ingest.py` | 4,828 | 2026-10-13 | 0 |  |
| `scripts/fix_v1_accuracy.py` | 7,913 | 2026-10-15 | 1 |  |
| `scripts/fix_verified_booking_gate.py` | 7,842 | 2026-10-14 | 1 |  |
| `scripts/implement_v1_canonical_cache.py` | 8,350 | 2026-10-13 | 0 |  |
| `scripts/inspect_click_http_contract.py` | 636 | 2026-10-14 | 0 |  |
| `scripts/inspect_click_payload_shape.py` | 750 | 2026-10-14 | 0 |  |
| `scripts/inspect_mql_ledger.py` | 534 | 2026-10-13 | 0 |  |
| `scripts/inspect_opportunity_creator.py` | 762 | 2026-10-14 | 0 |  |
| `scripts/inspect_report_cache_paths.py` | 678 | 2026-10-14 | 0 |  |
| `scripts/inspect_sql_writer.py` | 717 | 2026-10-13 | 1 |  |
| `scripts/inspect_v1_band_improvements.py` | 1,787 | 2026-10-13 | 0 |  |
| `scripts/inspect_v1_query_plan.py` | 1,177 | 2026-10-15 | 1 |  |
| `scripts/inspect_v1_runtime.py` | 485 | 2026-10-13 | 0 |  |
| `scripts/instagram/apply_instagram_company_dm_bootstrap.py` | 6,515 | 2026-08-18 | 2 |  |
| `scripts/instagram/backfill_instagram_reporting_events.py` | 4,096 | 2026-08-22 | 1 |  |
| `scripts/instagram/batch_instagram_validate_and_send.py` | 14,309 | 2026-08-18 | 6 |  |
| `scripts/instagram/fix_instagram_reporting_db.py` | 7,883 | 2026-08-22 | 1 |  |
| `scripts/instagram/match_instagram_company_dm_contacts.py` | 6,538 | 2026-08-17 | 1 |  |
| `scripts/instagram/process_ig_fb_local.js` | 11,512 | 2026-08-15 | 1 |  |
| `scripts/instagram/reset_instagram_test_401_failures.py` | 2,229 | 2026-08-17 | 1 |  |
| `scripts/instagram/review_company_instagram_sources.py` | 16,663 | 2026-08-15 | 1 |  |
| `scripts/linkedin/audit_live_linkedin_send_nodes.py` | 2,654 | 2026-09-29 | 1 |  |
| `scripts/linkedin/audit_vertical_outreach.py` | 3,653 | 2026-10-15 | 0 |  |
| `scripts/linkedin/backfill_linkedin_connected_tag.py` | 11,770 | 2026-10-02 | 2 |  |
| `scripts/linkedin/build_connected_tag_sync_workflow.py` | 6,607 | 2026-10-02 | 3 |  |
| `scripts/linkedin/build_vertical_outreach.py` | 9,453 | 2026-10-15 | 0 |  |
| `scripts/linkedin/connected_tag_sync.js` | 5,712 | 2026-10-02 | 3 |  |
| `scripts/linkedin/enforce_linkedin_daily_limit.py` | 4,948 | 2026-08-18 | 1 |  |
| `scripts/linkedin/enrich_john_invites_vertical.py` | 5,173 | 2026-10-12 | 2 |  |
| `scripts/linkedin/fix_connection_state_sync_withdrawal_holds.py` | 7,021 | 2026-10-26 | 2 |  |
| `scripts/linkedin/fix_dispatcher_mirror_location_token.py` | 4,815 | 2026-10-02 | 2 |  |
| `scripts/linkedin/fix_linkedin_backfill_outbound_direction.py` | 9,672 | 2026-09-17 | 2 |  |
| `scripts/linkedin/fix_linkedin_dm_pipeline.py` | 6,958 | 2026-08-18 | 1 |  |
| `scripts/linkedin/fix_linkedin_inbound_response_and_jsonb.py` | 8,646 | 2026-09-17 | 3 |  |
| `scripts/linkedin/fix_linkedin_sanitize_double_escape.py` | 8,125 | 2026-09-17 | 5 |  |
| `scripts/linkedin/fix_linkedin_state_upsert.py` | 4,058 | 2026-08-18 | 1 |  |
| `scripts/linkedin/fix_relations_backfill_endpoint.py` | 4,564 | 2026-10-02 | 2 |  |
| `scripts/linkedin/guard_linkedin_requested_state.py` | 3,817 | 2026-08-18 | 1 |  |
| `scripts/linkedin/harden_linkedin_dm_dedup.py` | 8,058 | 2026-08-18 | 1 |  |
| `scripts/linkedin/implement_linkedin_inbound_oauth_retry.py` | 11,022 | 2026-09-26 | 0 |  |
| `scripts/linkedin/list_john_pending_invites.py` | 4,641 | 2026-10-12 | 2 |  |
| `scripts/linkedin/load_linkedin_backfill_worklist.py` | 4,938 | 2026-09-11 | 1 |  |
| `scripts/linkedin/patch_inbound_map_state_fallback.py` | 7,573 | 2026-09-24 | 0 |  |
| `scripts/linkedin/patch_linkedin_backfill_workflow.py` | 10,874 | 2026-09-11 | 1 |  |
| `scripts/linkedin/patch_linkedin_inbound_oauth_fallback.py` | 2,882 | 2026-09-24 | 0 |  |
| `scripts/linkedin/patch_linkedin_inbound_queue_on_401.py` | 3,508 | 2026-09-24 | 0 |  |
| `scripts/linkedin/patch_live_linkedin_identity_conversations.py` | 22,739 | 2026-09-29 | 1 |  |
| `scripts/linkedin/plan_john_invite_withdrawals.py` | 34,232 | 2026-10-22 | 6 |  |
| `scripts/linkedin/prefer_personal_linkedin_first_name.py` | 5,780 | 2026-09-29 | 1 |  |
| `scripts/linkedin/reconcile_requested_connections.py` | 9,503 | 2026-10-02 | 3 |  |
| `scripts/linkedin/recover_missed_linkedin_reply.py` | 4,965 | 2026-08-17 | 2 |  |
| `scripts/linkedin/repair_linkedin_inbound_retry_sql.py` | 3,310 | 2026-09-26 | 0 |  |
| `scripts/linkedin/repair_live_linkedin_mirror_endpoint.py` | 2,609 | 2026-09-29 | 1 |  |
| `scripts/linkedin/repair_live_linkedin_mirror_scope.py` | 3,270 | 2026-09-29 | 1 |  |
| `scripts/linkedin/repair_outbound_mirror_endpoint.py` | 2,482 | 2026-09-29 | 1 |  |
| `scripts/linkedin/replace_linkedin_retry_no_code.py` | 10,060 | 2026-09-24 | 0 |  |
| `scripts/linkedin/run_linkedin_backfill_batch.py` | 9,866 | 2026-09-11 | 2 |  |
| `scripts/linkedin/test_plan_john_invite_withdrawals.py` | 9,805 | 2026-10-12 | 1 |  |
| `scripts/linkedin/update_follower_dm.py` | 1,678 | 2026-07-08 | 1 |  |
| `scripts/linkedin/verify_vertical_outreach.py` | 4,022 | 2026-10-15 | 0 |  |
| `scripts/linkedin/vertical_outreach_ops.py` | 3,842 | 2026-10-15 | 0 |  |
| `scripts/linkedin/vertical_runtime.js` | 25,333 | 2026-10-15 | 0 |  |
| `scripts/linkedin/vertical_runtime.test.js` | 13,339 | 2026-10-15 | 0 |  |
| `scripts/linkedin/watch_fix.py` | 18,414 | 2026-09-18 | 3 |  |
| `scripts/list_form_workflows.py` | 807 | 2026-10-13 | 0 |  |
| `scripts/monitoring/monitor.py` | 9,514 | 2026-09-08 | 2 |  |
| `scripts/n8n/align_n8n_encryption_key.py` | 876 | 2026-08-12 | 3 |  |
| `scripts/n8n/apply_linkedin_profile_index.py` | 3,281 | 2026-10-01 | 1 |  |
| `scripts/n8n/apply_sales_navigator_schema.py` | 3,838 | 2026-10-01 | 0 |  |
| `scripts/n8n/audit_sales_navigator_live.py` | 3,404 | 2026-10-01 | 1 |  |
| `scripts/n8n/build_sales_navigator_reconciler.py` | 10,944 | 2026-10-01 | 1 |  |
| `scripts/n8n/check_n8n.py` | 2,204 | 2026-07-03 | 1 |  |
| `scripts/n8n/check_n8n_db.py` | 1,355 | 2026-07-03 | 1 |  |
| `scripts/n8n/copy_to_n8n.py` | 1,641 | 2026-07-03 | 1 |  |
| `scripts/n8n/copy_to_n8n_files.py` | 1,407 | 2026-07-03 | 1 |  |
| `scripts/n8n/fix_intake_poller.js` | 14,167 | 2026-09-10 | 5 |  |
| `scripts/n8n/fix_sheets_node.py` | 3,289 | 2026-07-03 | 1 | apikey_literal, env_constant_with_long_literal, jwt |
| `scripts/n8n/fix_workflow.py` | 2,792 | 2026-08-12 | 1 |  |
| `scripts/n8n/inspect_sales_navigator_account_owners.py` | 2,587 | 2026-10-01 | 0 |  |
| `scripts/n8n/inspect_sales_navigator_chats.py` | 2,246 | 2026-10-01 | 0 |  |
| `scripts/n8n/inspect_sales_navigator_contact_map.py` | 6,867 | 2026-10-01 | 0 |  |
| `scripts/n8n/inspect_sales_navigator_runtime.py` | 2,431 | 2026-10-01 | 0 |  |
| `scripts/n8n/inventory_n8n_pits.py` | 2,434 | 2026-08-15 | 3 |  |
| `scripts/n8n/n8n_api_probe.py` | 1,741 | 2026-09-07 | 1 |  |
| `scripts/n8n/n8n_exec_check.py` | 2,132 | 2026-09-07 | 1 |  |
| `scripts/n8n/n8n_find_pgerr.py` | 1,937 | 2026-09-07 | 1 |  |
| `scripts/n8n/n8n_ga4_err.py` | 2,075 | 2026-09-07 | 1 |  |
| `scripts/n8n/n8n_vapi_check.py` | 2,092 | 2026-09-07 | 1 |  |
| `scripts/n8n/patch_linkedin_profile_field_resolver.py` | 28,770 | 2026-10-01 | 1 |  |
| `scripts/n8n/patch_simpletexting_auth.ps1` | 13,662 | 2026-08-06 | 1 |  |
| `scripts/n8n/patch_simpletexting_event_safety.ps1` | 12,266 | 2026-08-06 | 1 |  |
| `scripts/n8n/probe_sales_navigator_hmac_rejection.py` | 1,747 | 2026-10-01 | 0 |  |
| `scripts/n8n/probe_sales_navigator_raw_body.py` | 1,505 | 2026-10-01 | 0 |  |
| `scripts/n8n/probe_verified_unipile_credential.py` | 3,567 | 2026-10-01 | 0 |  |
| `scripts/n8n/reconcile_gateway_test_message.py` | 3,919 | 2026-10-01 | 2 |  |
| `scripts/n8n/reconcile_sales_navigator_test_chat.py` | 4,501 | 2026-10-01 | 0 |  |
| `scripts/n8n/refresh_ghl_oauth_token.py` | 4,895 | 2026-09-19 | 2 |  |
| `scripts/n8n/repair_failed_ghl_pits.py` | 3,338 | 2026-08-15 | 1 |  |
| `scripts/n8n/repair_linkedin_profile_index_live.py` | 1,597 | 2026-10-01 | 0 |  |
| `scripts/n8n/repair_sales_navigator_raw_body.py` | 2,823 | 2026-10-01 | 0 |  |
| `scripts/n8n/replace_sales_navigator_unipile_credential.py` | 1,132 | 2026-10-01 | 0 |  |
| `scripts/n8n/wire_sales_navigator_v2_workflows.py` | 66,358 | 2026-10-02 | 5 |  |
| `scripts/n8n/wire_verified_sales_navigator_credential.py` | 2,493 | 2026-10-01 | 0 |  |
| `scripts/partnerships/clean_partnership_data.py` | 11,453 | 2026-09-17 | 4 |  |
| `scripts/partnerships/import_partnership_candidates.py` | 7,743 | 2026-07-31 | 1 |  |
| `scripts/partnerships/reconcile_august_2026_partnership_live.ps1` | 7,069 | 2026-08-27 | 3 |  |
| `scripts/partnerships/repair_partnership_owners.py` | 4,457 | 2026-07-31 | 1 |  |
| `scripts/partnerships/seed_partnership_linkedin_state.py` | 5,883 | 2026-07-31 | 1 |  |
| `scripts/partnerships/tag_august_26_partnership_contacts.ps1` | 2,456 | 2026-08-27 | 3 |  |
| `scripts/patch_booking_link_click_intake.py` | 8,779 | 2026-10-12 | 1 |  |
| `scripts/patch_v1_band1_facts.py` | 13,133 | 2026-10-12 | 3 |  |
| `scripts/preserve_pipeline_on_mql.py` | 878 | 2026-10-14 | 0 |  |
| `scripts/reconcile_v1_band1_opportunities.py` | 21,298 | 2026-10-12 | 2 |  |
| `scripts/record_click_mql_provenance.py` | 2,727 | 2026-10-14 | 0 |  |
| `scripts/record_mql_provenance.py` | 1,408 | 2026-10-14 | 0 |  |
| `scripts/recover_booking_clicks.py` | 7,073 | 2026-10-14 | 0 |  |
| `scripts/refine_booking_period_metrics.py` | 2,199 | 2026-10-14 | 0 |  |
| `scripts/repair_v1_facts_sql.py` | 8,330 | 2026-10-14 | 2 |  |
| `scripts/social-reporting/audit_social_reporting.py` | 2,414 | 2026-08-17 | 1 |  |
| `scripts/social-reporting/fix_brands_code.py` | 3,708 | 2026-07-03 | 3 | apikey_literal, env_constant_with_long_literal, jwt |
| `scripts/social-reporting/fix_executive_report_metrics.py` | 28,468 | 2026-08-17 | 2 |  |
| `scripts/social-reporting/fix_social_mql_reporting.py` | 8,579 | 2026-08-18 | 1 |  |
| `scripts/social-reporting/fix_social_reporting_accuracy.py` | 5,592 | 2026-08-17 | 1 |  |
| `scripts/social-reporting/implement_email_attribution.py` | 8,940 | 2026-09-17 | 0 |  |
| `scripts/social-reporting/patch_v1_funnel_and_pipeline_to_work.py` | 8,440 | 2026-10-02 | 2 |  |
| `scripts/social-reporting/patch_v1_safe_feedback_api.py` | 9,089 | 2026-09-30 | 0 |  |
| `scripts/social-reporting/repair_source_health.py` | 4,325 | 2026-09-19 | 1 |  |
| `scripts/social-reporting/report_runtime_audit.py` | 2,480 | 2026-08-12 | 4 |  |
| `scripts/utilities/_run_commands.py` | 1,618 | 2026-08-18 | 1 |  |
| `scripts/utilities/decrypt_credential.py` | 1,096 | 2026-08-12 | 1 |  |
| `scripts/utilities/fix_parse_csv.py` | 3,414 | 2026-07-03 | 1 | apikey_literal, env_constant_with_long_literal, jwt |
| `scripts/utilities/fix_simpletexting_boundaries.py` | 43,397 | 2026-09-24 | 3 |  |
| `scripts/utilities/upload_updated.py` | 1,942 | 2026-07-03 | 1 |  |
| `scripts/utilities/vapi_audit.py` | 2,928 | 2026-08-12 | 3 |  |
| `scripts/utilities/verify_tags.py` | 578 | 2026-07-03 | 1 |  |
| `scripts/utilities/x.py` | 1,362 | 2026-07-03 | 5 |  |
| `scripts/validate_click_route_offline.py` | 2,271 | 2026-10-14 | 0 |  |
| `scripts/verify_cache_refresh.py` | 2,576 | 2026-10-14 | 0 |  |
| `scripts/verify_deploy_v1.py` | 1,228 | 2026-10-13 | 5 |  |
| `scripts/verify_reporting_sources_cache.py` | 718 | 2026-10-14 | 0 |  |

## `tools/` exact paths (5)

| path | bytes | mtime | doc refs | hits |
|---|---|---|---|---|
| `tools/add-vapi-weekly-report.ps1` | 6,304 | 2026-05-26 | 0 |  |
| `tools/ga4_ingest_workflow.js` | 11,895 | 2026-04-30 | 0 |  |
| `tools/patch-gsc-workflow.ps1` | 7,593 | 2026-05-09 | 0 |  |
| `tools/patch-linkedin-dispatcher-postgres.ps1` | 9,717 | 2026-06-03 | 0 |  |
| `tools/patch-simpletexting-workflows.ps1` | 5,881 | 2026-04-22 | 0 |  |
