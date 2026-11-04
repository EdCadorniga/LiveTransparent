# Retention manifest — batch 2: tmp/ + root tmp* — 2026-11-05

Basis: [cleanup handoff prompt](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md) §C
(YOLO mandate); per-path evidence in
[tmp artifacts classification](tmp-artifacts-classification-2026-11-05.md) (36 paths, bounded
credential-pattern scan: zero hits; scan-bounded only). Nothing is deleted — everything is
moved to git-ignored archive folders, so no sole-copy loss is possible. Recovery = copy back
from the archive folder (plus, for tracked files, `git show HEAD:<path>`).

## Destination `local-archive/campaign-template-captures-2026-11/` (27 tracked files, 5,638,731 bytes)

Classification basis (all rows): plan/handoff §C — "tmp/ Alcohol/cannabis template captures
… move into `local-archive/campaign-template-captures-2026-11/`, since the Alcohol template
work is closed/documented; delete nothing". Screenshot/UI evidence and template YAML of the
October Alcohol vertical template-build session; dependency check: none of the 27 paths is
required by any build/deploy/live process ( captures only). Sensitivity: none of the bounded
patterns hit; PNG/YAML kinds are scan-bounded (kept as archived copies, not redistributed).
Tracked-file handling: `git rm --cached` + physical move → staged deletion in the working
tree, **not committed** (per handoff rule).

| path (was `tmp/…`) | bytes | recovery |
|---|---|---|
| `action-editor.png` | 447,942 | `local-archive/campaign-template-captures-2026-11/action-editor.png` |
| `alcohol-1.png` | 124,756 | same folder |
| `alcohol-2.png` | 151,346 | same folder |
| `alcohol-3.png` | 164,363 | same folder |
| `alcohol-4.png` | 141,547 | same folder |
| `alcohol-5.png` | 119,093 | same folder |
| `alcohol-action-config.yml` | 58,952 | same folder |
| `alcohol-builder.yml` | 48,390 | same folder |
| `alcohol-editor-load.png` | 351,003 | same folder |
| `alcohol-email-template-1-before-cleanup.png` | 1,093,259 | same folder |
| `alcohol-frame-direct.png` | 13,603 | same folder |
| `alcohol-frame-direct2.png` | 13,811 | same folder |
| `alcohol-parent-confirm.png` | 149,405 | same folder |
| `alcohol-template-editor-state.png` | 214,576 | same folder |
| `alcohol-template2-state.png` | 300,526 | same folder |
| `alcohol-template5-verified.png` | 250,625 | same folder |
| `alcohol-workflow-loaded.png` | 149,405 | same folder |
| `alcohol-workflow-tree.yml` | 49,331 | same folder |
| `alcohol-workflow.png` | 11,838 | same folder |
| `cannabis-new-1.png` | 115,980 | same folder |
| `cannabis-new-2.png` | 151,805 | same folder |
| `cannabis-new-3.png` | 158,311 | same folder |
| `cannabis-new-4.png` | 139,380 | same folder |
| `cannabis-new-5.png` | 95,095 | same folder |
| `email1-config.yml` | 58,952 | same folder |
| `email1-focused.yml` | 58,943 | same folder |
| `monaco-select-all.png` | 1,006,494 | same folder |

## Destination `local-archive/report-captures-2026-11/` (9 untracked git-ignored files, 637,939 bytes)

Classification basis: handoff §C — root `tmp*` report captures "review each briefly … rename
to `local-archive/report-captures-2026-11/` … prefer archiving". These are 2026-09-30
report-workflow query/response captures (workflow JSON snapshots, a SQL/JS scratch pair, an
empty headers file, a weekly response). Bounded review: file kinds/first-token checks only
(no values echoed; zero credential-pattern hits from the classification scan). The JSON
snapshot payloads may contain workflow-definition text/report rows — kept in the archive
rather than deleted for that reason. All untracked/ignored (`tmp_` pattern): pure `Move-Item`,
no Git involvement, reversible by moving back.

| path (was root) | bytes | recovery |
|---|---|---|
| `tmp_Bukc0mgOD2r7V6ED.json` | 234,474 | `local-archive/report-captures-2026-11/tmp_Bukc0mgOD2r7V6ED.json` |
| `tmp_campaign_query.sql` | 21,455 | same folder |
| `tmp_knc2wxe4pyYIJ5tw.json` | 25,703 | same folder |
| `tmp_latest_v1_exec.json` | 140,690 | same folder |
| `tmp_MvPLbUAN9IIQikxb.json` | 65,459 | same folder |
| `tmp_summary_query.js` | 98,428 | same folder |
| `tmp_v1_facts_workflow.json` | 40,092 | same folder |
| `tmp_v1_headers.txt` | 0 | same folder |
| `tmp_weekly_response.json` | 11,638 | same folder |

## Result

- 36 files moved (5,638,731 + 637,939 = **6,276,670 bytes** relocated out of the working tree,
  byte-preserved in the archive). `tmp/` directory itself removed once empty. Root working
  copy no longer contains any `tmp*` artifact.
- Nothing was deleted; nothing sensitive printed; no commit.
- Verification: archive dirs contain 27 / 9 files; `git diff --check` passes; `git status`
  shows only the expected 27 staged deletions plus batch-1/batch-0 doc changes.

**Note for docs:** the classification artifact and dated session docs reference the old paths
as captured evidence; that remains historically valid. If a future edit needs these captures,
they are under `local-archive/campaign-template-captures-2026-11/` and
`local-archive/report-captures-2026-11/`.
