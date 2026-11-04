# Retention manifest — batch 11: marketing byte-identical duplicate dedup (2026-11-05/06)

Mandate boundary quoted: "You may execute archive/delete batches yourself for anything
matching the plan's own removal categories — **duplicates whose byte-identical/set content is
retained elsewhere**, regenerable caches/temp/bytecode…".

| Path | Bytes | Basis | Recovery |
|---|---|---|---|
| `marketing/email-marketing/cold-outreach-prep/reports/live-run-postgres-execution-detail.json` | 85,869,804 (81.9 MB) | SHA-256 hash == `live-run-postgres-full-execution-detail-20260220T094538Z.json` (verified via `Get-FileHash` before deletion); identical twin retained in the same directory | copy the twin back |

No tracked copy remains necessary: the file was tracked, so `git rm --cached` + disk delete;
the retained twin stays tracked in Git history providing recovery anyway.

**Explicitly NOT touched in this batch:** the remaining ~140 dated run captures and
workflow-export JSONs in the same `reports/` folder (per-file sensitivity review pending —
one filename suggests an embedded-key payload; flagged to the owner review package), and all
retained import source CSVs.

## Execution record (filled after execution)

- Hash verified identical pre-delete (`85869804` bytes each; SHA-256 match confirmed twice:
  pre-manifest and immediately pre-delete) → **deleted**.
- Retained twin `live-run-postgres-full-execution-detail-20260220T094538Z.json` read back
  intact at 85,869,804 bytes.
- `git rm --cached` → staged index deletion; `git diff --check`: **PASS**.
