# Phase 5 — temporary/build/data artifact classification — 2026-11-05

Read-only path/size/mtime enumeration + credential-pattern scan (hit NAMES + counts only).
No file was read for classification beyond pattern counts; no file was changed, moved, or
deleted. NOT a deletion manifest; nothing is approved for cleanup.

| path | kind (by extension/provenance) | bytes | mtime | credential-pattern hits | provisional class |
|---|---|---|---|---|---|
| `action-editor.png` | screenshot capture | 447,942 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-1.png` | screenshot capture | 124,756 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-2.png` | screenshot capture | 151,346 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-3.png` | screenshot capture | 164,363 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-4.png` | screenshot capture | 141,547 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-5.png` | screenshot capture | 119,093 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-action-config.yml` | config/template capture | 58,952 | 2026-10-07 |  | keep pending review (may hold template HTML/credentials) |
| `alcohol-builder.yml` | config/template capture | 48,390 | 2026-10-07 |  | keep pending review (may hold template HTML/credentials) |
| `alcohol-editor-load.png` | screenshot capture | 351,003 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-email-template-1-before-cleanup.png` | screenshot capture | 1,093,259 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-frame-direct.png` | screenshot capture | 13,603 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-frame-direct2.png` | screenshot capture | 13,811 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-parent-confirm.png` | screenshot capture | 149,405 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-template-editor-state.png` | screenshot capture | 214,576 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-template2-state.png` | screenshot capture | 300,526 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-template5-verified.png` | screenshot capture | 250,625 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-workflow-loaded.png` | screenshot capture | 149,405 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `alcohol-workflow-tree.yml` | config/template capture | 49,331 | 2026-10-07 |  | keep pending review (may hold template HTML/credentials) |
| `alcohol-workflow.png` | screenshot capture | 11,838 | 2026-10-06 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `cannabis-new-1.png` | screenshot capture | 115,980 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `cannabis-new-2.png` | screenshot capture | 151,805 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `cannabis-new-3.png` | screenshot capture | 158,311 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `cannabis-new-4.png` | screenshot capture | 139,380 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `cannabis-new-5.png` | screenshot capture | 95,095 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `email1-config.yml` | config/template capture | 58,952 | 2026-10-07 |  | keep pending review (may hold template HTML/credentials) |
| `email1-focused.yml` | config/template capture | 58,943 | 2026-10-07 |  | keep pending review (may hold template HTML/credentials) |
| `monaco-select-all.png` | screenshot capture | 1,006,494 | 2026-10-07 |  | keep pending content/sensitivity review (campaign-build UI evidence) |
| `tmp_Bukc0mgOD2r7V6ED.json` | workflow/execution response snapshot | 234,474 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |
| `tmp_MvPLbUAN9IIQikxb.json` | workflow/execution response snapshot | 65,459 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |
| `tmp_campaign_query.sql` | query/hasource scratch | 21,455 | 2026-09-30 |  | keep pending review |
| `tmp_knc2wxe4pyYIJ5tw.json` | workflow/execution response snapshot | 25,703 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |
| `tmp_latest_v1_exec.json` | workflow/execution response snapshot | 140,690 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |
| `tmp_summary_query.js` | query/hasource scratch | 98,428 | 2026-09-30 |  | keep pending review |
| `tmp_v1_facts_workflow.json` | workflow/execution response snapshot | 40,092 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |
| `tmp_v1_headers.txt` | capture/log | 0 | 2026-09-30 |  | keep pending review (may hold credentials) |
| `tmp_weekly_response.json` | workflow/execution response snapshot | 11,638 | 2026-09-30 |  | keep pending review (may hold PII/credentials) |

**Notes:** `tmp/` files map to the October Alcohol vertical template-build session (UI state
captures and template YAML). Root `tmp*` files are October report-workflow query/response
captures (bucketed JSON responses and SQL/JS scratch) — they may contain contact rows or
workflow definition text and require content review before any disposition. The bounded
pattern scan does not rule out secrets for the PNG/YAML/SQL/JS kinds whose formats the
pattern list doesn't cover; treat 'no hits' as scan-bounded, not cleared.

## Disposition execution — batch 2 (2026-11-05, later same day)

Executed under the [YOLO cleanup mandate](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md)
with manifest [retention-manifest-2026-11-05-batch-2-tmp-captures.md](retention-manifest-2026-11-05-batch-2-tmp-captures.md):
all 27 `tmp/` files moved to `local-archive/campaign-template-captures-2026-11/` and all 9
root `tmp*` files moved to `local-archive/report-captures-2026-11/` (byte-preserved,
**nothing deleted**; `tmp/` dir removed once empty). Tracked `tmp/` removals are staged-git
deletions (uncommitted). Bounded review was kind/first-token only — no values echoed. The
table above records the pre-move state; recovery = copy back from the two archive folders.

## Disposition addendum - late continuation 2026-11-05

Executed under manifests `retention-manifest-2026-11-06-batch-5..11` (see `repository-organization-2026-11-06.md`): regenerable caches deleted (`.pip-cache/`, `.playwright-mcp/`); one byte-identical duplicate deduped inside `marketing/`; root residue (report-era captures, contact-division working files, `Export_Contacts_*` CSVs, `Contacts added August 25 2026/`, root `_check_config.py`/`_kill_and_fix.py`/`_mark_enrolled.py`, campaign/design `.docx` set, `_qa_remove_exec/`, `repomix.config.json`/`.repomixignore`) archived to dated `local-archive/` folders (PII kept locally, staged out of the Git index, not deleted). Nothing referenced by a maintained doc moved without a pointer update. This artifact's per-path tables remain historical evidence of the pre-batch state.
