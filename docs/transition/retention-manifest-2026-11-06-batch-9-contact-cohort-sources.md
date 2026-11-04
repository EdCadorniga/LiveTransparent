# Retention manifest — batch 9: root GHL export CSVs + August 25 2026 import cohort (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§C item 4 ("Root GHL export CSVs + `Contacts added August 25 2026/` — **archive, do not
delete**, because they contain mass contact PII and remain the only local record of import
source provenance"). AGENTS-era rule also said the export CSVs are "delete after use"; the
backfill-era uses (DAN `ghl_contact_id` backfill 2026-07-13; LinkedIn dispatcher bulk feed
2026-07-13) are recorded as completed, so retention moves to archive. **Nothing here is
deleted.**

| Path | Bytes | Sensitivity | Dependency check |
|---|---|---|---|
| `Export_Contacts_brands pool_Jul_2026_5_24_AM.csv` | 469,908 | bulk contact PII | referenced by `AGENTS.md` Key Files + dated 2026-08-12 session record — pointers updated post-move |
| `Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv` | 1,415,965 | bulk contact PII | same |
| `Export_Contacts_for fresh Linkedin connections_Jul_2026_2_16_AM.csv` | 4,891,839 | bulk contact PII (LinkedIn feed) | same |
| `Contacts added August 25 2026/` (16 files incl. `Agency.csv`, `Brand.csv`, `Dispensaries (1).csv`, `cleaned/*`, `Partnership contacts August 26 2026 1/*`) | 13,914,000+ | bulk contact PII + import logs | referenced by dated 2026-08-26/08-27 session records + transition plan (historical); dir's own summary md moved with it |
| `data/runs/`, `data/*.csv` | — | NOT in this batch — `data/` is documented and `GHL_Ready_*.csv` may still be referenced by n8n docs | excluded |

**Destinations:**
- `local-archive/ghl-export-csvs-2026-11/` (3 root CSVs)
- `local-archive/contacts-import-august-2026/` (directory tree, structure preserved)

Tracked files/files: `git rm --cached` after copying (assures PII leaves the tracked tree while
byte copies remain locally, per the retention decision to keep contact-import provenance).

**Pointer updates recorded post-move:** `AGENTS.md` Key Files (three export CSV rows),
`Project Status and Next Steps.md` (Full.docx/context rows only where they reference moved
paths), transition-plan ledger note.

## Execution record (filled after execution)

- 3 export CSVs moved → `local-archive/ghl-export-csvs-2026-11/` (3 files present).
- `Contacts added August 25 2026/` moved intact → `local-archive/contacts-import-august-2026/`
  (tree preserved; 16 files, 2 subsets `cleaned/` + `Partnership contacts August 26 2026 1/`).
- `git rm -r --cached` on the directory + `git rm --cached` on the 3 CSV names → staged index
  deletions only.
- `git diff --check`: **PASS**.
