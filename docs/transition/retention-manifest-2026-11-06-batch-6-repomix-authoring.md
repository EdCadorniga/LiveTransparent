# Retention manifest — batch 6: repomix authoring leftovers (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§C item 2 ("`repomix.config.json`, `.repomixignore` — archive (the bundle stays deleted; the
config files are historical authoring tools)") and §Boundaries: "do NOT confuse this with the
leftover authoring files … which ARE cleanable candidates".

| Path | Bytes | Classification basis | Dependency check | Sensitivity | Recovery |
|---|---|---|---|---|---|
| `repomix.config.json` | 1,301 | Repomix authoring config; the `repomix-output.md` bundle is permanently retired (Ed, 2026-11-04; never recreate) | referenced only by dated 2026-11-05 cleanup EOS/handoff records | legacy config may carry an allow/deny list only | archived copy |
| `.repomixignore` | 70 | same authoring family | none | none | archived copy |

**Destination:** `local-archive/repomix-authoring-2026-11/` (git-ignored), archived with a
short README stating retirement. Tracked files: removed from Git index via `git rm --cached`
after copying (working-copy deletion staged, not committed).

## Execution record (filled after execution)

- Copied/moved both files → `local-archive/repomix-authoring-2026-11/` (2 files + README).
- `git rm --cached repomix.config.json .repomixignore` → done (working-copy deletion staged).
- `git diff --check`: **PASS**.
- Note: archive-before-delete via **Move-Item** (copy + delete compressed to a single move;
  bytes preserved).
