# Retention manifest — batch 3: local-archive/n8n SHA-256 dedup — 2026-11-05

Basis: [cleanup handoff prompt](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md) §D
(YOLO mandate) — "Delete exact **duplicate files with identical hashes** … (keep 1 of any
fully duplicated set)". Evidence: SHA-256 over all **68 files (1,848,174 bytes)** under
`local-archive/n8n/` → **66 unique hashes, 2 duplicate groups** (computed read-only; values
never printed). Category basis: plan §5 Phase 4 "retaining only useful historical records"/
"duplicates". Hard gate honored: **TS blueprints are not deleted in any case** (blueprint
source-of-record per path) and the 15 live-only critical workflows' snapshots are untouched.

| path (deleted) | bytes | sha-256 prefix | retained twin (kept) | basis quote | sensitivity | recovery |
|---|---|---|---|---|---|---|
| `local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182447Z.json` | 21,656 | `0043e598b880…` | `local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182410Z.json` (identical bytes, 21,656) | handoff §D.1 duplicate-hash rule; the two 2026-09-21 captures recorded the same pre-change state seconds apart | ghl_pit material (owner-accepted residual risk) | the retained twin in the same archive folder; also `git`-independent (archive is the sole copy of either, twins identical) |
| `local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003155.json` | 67,275 | `8d180094eeb7…` | `local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003207.json` (identical bytes, 67,275) | handoff §D.2: five May-2026 Q3Ivn snapshots → keep newest as last-known-good; older delete **only if** hash-duplicate. Retained set after batch: `_003207.json`, `_003224.json` (newest), `_003224_…5ad87536.ts` (blueprint-companion, TS not deletable), `workflow_Q3Ivnwe4z2Y3cD7A_updated_preview.json` | ghl_pit material (owner-accepted residual risk) | the retained twin `_003207.json` in the same folder |

**Not deleted (explicit):** all 22 TS blueprints; the non-duplicate members of both duplicate
groups; every other file in the archive (66 unique-hash files retained);
`workflows/Q3Ivnwe4z2Y3cD7A-before-simpletexting-mms-*` September snapshots (distinct hashes,
keep); anything inside `local-scripts/linkedin-invite-withdrawals/` (none here, boundary
checked); nothing on the VPS/host (this is a repository-local batch).

**Result:** 68 → 66 files; **88,931 bytes freed** (21,656 + 67,275). Deletion is pure
duplicate collapse — no unique content lost. Verification performed post-batch: re-hash
confirms 66 files, 66 unique hashes, 0 remaining duplicate groups; the deleted paths are
absent; retained twins present with identical byte counts.
