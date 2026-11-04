# Retention manifest — batch 10: root legacy scripts, QA staging, campaign/design docx (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§Root loose files ("working remnants …", "The historical campaign/design working `.docx` set at
root … archive candidates after doc-reference check") and §C item 5. All moves, nothing
deleted.

**A. Root one-off probes (2026-07-07, Emerald-era) → `local-archive/scripts-legacy-2026-07/`**

| Path | Bytes | Basis | Dependency/sensitivity |
|---|---|---|---|
| `_check_config.py` | 1,393 | one-off probe reading a hardcoded OneDrive `.env` path; July-era | no references outside handoff; reads key from local `.env` (no embedded secret literal) |
| `_kill_and_fix.py` | 1,807 | July paramiko one-off; hardcoded SSH key path + DB IDs | no references; contains no secret literal (uses local key file) |
| `_mark_enrolled.py` | 2,033 | same wave (marks enrolled IDs via SSH psql) | no references; same profile |

**B. QA staging for the Executive-Report removal request → archived with its doc**

| Path | Bytes | Basis |
|---|---|---|
| `_qa_remove_exec/` (2 files: `page-1.png`, `Remove from Executive Report - v1.pdf`) | ~268 KB dir total | name says `remove-exec` QA staging; git-ignored single copies of the removal-request evidence — archived (not deleted) to preserve the sole readable copy alongside the source docx |

**C. Campaign/design history `.docx` set → `local-archive/campaign-design-docx-2026-11/`**

| Path | Bytes | Reference check result |
|---|---|---|
| `Email Content - Dispensary Attribution Network_ Brands.docx` | 9,144 | no repo references |
| `Email Content - Dispensary Attribution Network_ Dispensaries.docx` | 9,001 | no repo references |
| `Instagram and FB DM - Dispensary Attribution Network (Brands).docx` | 7,213 | referenced by dated 2026-08-14 handoff (historical) |
| `INSTAGRAM and FB DM - Dispensary Attribution Network (Dispensaries).docx` | 7,137 | same |
| `INSTAGRAM and FB DM - Partnerships Campaign.docx` | 7,126 | same |
| `Executive Summary Edits .docx` | 9,226 | referenced by `executive_report_v1_plan.md` — pointer note added post-move |
| `Remove from Executive Report - v1.docx` | 7,853 | pairs with `_qa_remove_exec` PDF (archived together) |
| `Transparent eCom Business Improvement Plan - Full.docx` | 78,396 | referenced by `AGENTS.md` + `Project Status and Next Steps.md` + dated session record — pointers updated post-move |

**Out of scope, not touched:** the three root `Billing Report …` files; `repeated linkedin
messages.png`.

## Execution record (filled after execution)

- A moved 3/3 → `local-archive/scripts-legacy-2026-07/` (tracked removals staged).
- B `_qa_remove_exec/` moved intact (2 files) with the matching docx under
  `local-archive/campaign-design-docx-2026-11/` (9 root entries: 8 docx + staging dir) — byte
  preserved, nothing deleted.
- C moved 8/8 docx; tracked removals staged via `git rm --cached`.
- `git diff --check`: **PASS**.
