# Retention manifest — batch 5: regenerable caches (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§C item 1 ("Regenerable/empty: `.pip-cache/`, ..., misc caches — delete per restricted rules").

| Path | Bytes/files | Classification basis | Dependency check | Sensitivity | Recovery |
|---|---|---|---|---|---|
| `.pip-cache/` (incl. 5 tracked entries) | 17 files / ~55 KB | pip download/selfcheck cache; plan Phase 5 "Safe candidates: regenerated temp files, caches, bytecode" | no doc/script references (rg zero hits); pip re-creates on next run | none (package metadata cache) | automatic — pip re-downloads |
| `.pip-cache/http-v2/*` (tracked: 4 files + selfcheck) | tracked via `git ls-files` | cached HTTP responses from a 2026-04 pip run | none | none | delete from index + disk |
| `.playwright-mcp/` | 1,443 files / 50,041,000+ B | `.gitignore` line 44 classifies it "Browser automation debug artifacts"; advice docs/repository-file-map.md Operating boundaries: "disposable ignored runtime/browser artifacts; safe to recreate" | ignored (0 tracked); no doc references among maintained docs | browser-profile state; may contain discarded session cookies — nothing operational | automatic — recreated by the next Playwright MCP session |

**Action:** delete `.pip-cache/` recursively (with `git rm --cached` for its 5 tracked
entries) and delete `.playwright-mcp/` recursively. Archive-before-delete waived: pure
regenerable cache.
**Post-batch verify:** both dirs absent; `git status` shows only the 5 staged `pip-cache `
index deletions beyond this session's expected surface; withdrawals family + its
`__pycache__` untouched.

## Execution record (filled after execution)

- `.pip-cache/`: **deleted** (5 tracked entries removed from index; dir gone from disk).
- `.playwright-mcp/`: **deleted** (50.04 MB / 1,443 files gone; disk check confirmed).
- `git diff --check`: **PASS**. `git status` surface matches expectations (staged pip-cache
  index removals only, plus the session's other staged batches). Withdrawals family + its
  `__pycache__` untouched.
