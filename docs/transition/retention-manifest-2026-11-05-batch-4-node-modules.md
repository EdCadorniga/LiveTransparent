# Retention manifest — batch 4: node_modules/ — 2026-11-05

Basis: [cleanup handoff prompt](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md) §E
(YOLO mandate) + plan §6.4: remove `node_modules/` **only after** verifying a package
manifest/lockfile exists and regeneration is provable; record size freed.

## Verification performed (2026-11-05)

| check | result |
|---|---|
| root package manifest | `package.json` present — single dependency `@n8n/workflow-sdk": "^0.13.3"` |
| lockfile | `package-lock.json` present, `lockfileVersion 3`, 96 package entries (pinned) |
| installed tree | `node_modules/` = 91 package directories, **48,387,637 bytes** |
| regeneration proof | `npm ci --dry-run` exited 0 (`up to date in 744ms`) — the lockfile alone fully resolves the tree; a later `npm ci` / `npm install` restores it byte-exact from the registry |
| dependents | the SDK is the build dependency for the retained `n8n/**/*.ts` workflow-blueprint sources (Phase 4 matrix builder family); no live service/production process reads this local tree — all production code is deployed on the VPS |

| path | bytes | disposition | recovery |
|---|---|---|---|
| `node_modules/` (whole tree, untracked, not git-ignored) | 48,387,637 | **delete** | `npm ci` (or `npm install`) at repo root regenerates from the retained `package-lock.json` |

**Not touched:** `package.json` and `package-lock.json` remain (they are the manifest the
recovery depends on). Nothing else was deleted in this batch.

**Result:** 48,387,637 bytes (~48.4 MB) freed; regeneration verified provable; no secret or
data value involved (dependency tree only).
