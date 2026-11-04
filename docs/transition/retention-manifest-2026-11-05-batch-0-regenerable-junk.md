# Retention manifest — batch 0: regenerable bytecode only — 2026-11-05

Mandatory per-batch manifest per [cleanup handoff prompt](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md)
(YOLO mandate) and plan §3 "Deletion and retention". Nothing outside this manifest is deleted.

| path | bytes | classification basis | dependency result | sensitivity | recovery | disposition |
|---|---|---|---|---|---|---|
| `docs/transition/__pycache__/` | 51,762 (dir) | plan §5 Phase 5 "regenerated temp/caches/bytecode" delete-freely category; git-ignored via `.gitignore:21 **/__pycache__/` | none — bytecode regenerated automatically by running the read-only generators | none (compiled from already-local sources) | regenerate on next script run | **delete** |
| `local-scripts/__pycache__/` | 9,514 | same | none | none | regenerate | **delete** |
| `marketing/automation/scripts/__pycache__/` | 17,807 | same | none | none | regenerate | **delete** |
| `marketing/email-marketing/emerald-email-campaign/artifacts/__pycache__/` | 58,854 | same | none | none | regenerate | **delete** |
| `scripts/__pycache__/` | 202,836 | same | none | none | regenerate | **delete** |
| `scripts/deploy/__pycache__/` | 4,752 | same | none | none | regenerate | **delete** |
| `scripts/linkedin/__pycache__/` | 219,526 | same | none | none | regenerate | **delete** |
| `scripts/n8n/__pycache__/` | 91,328 | same | none | none | regenerate | **delete** |
| `scripts/utilities/__pycache__/` | 49,346 | same | none | none | regenerate | **delete** |
| `services/sales_navigator_media/__pycache__/` | 36,540 | same | none | none | regenerate | **delete** |

**Total freed:** ≈ 741,465 bytes across 10 directories (source-tree bytecode only; `.pyc`
occurs only inside `__pycache__` here, so no separate file rows are needed).

**Exclusions / boundaries:** `local-scripts/linkedin-invite-withdrawals/__pycache__/`
(9,363 bytes) is **NOT touched** — the whole `linkedin-invite-withdrawals/` family is held
while the 310-unledgered-invitation investigation is open. `node_modules/` (untracked,
not *regenerable-trivially*) is a separate batch E decision. No Git staging is involved:
all `__pycache__` paths are git-ignored, so deletion does not touch the index.
