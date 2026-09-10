# GHL PIT Rotation Closeout

Updated: 2026-09-10

## Objective

Rotate every LiveTransparent GHL credential to the new full-access PIT supplied by Ed
(2026-09-10), across `.env`, all n8n workflows, and repo export/backup JSONs. Also answer
whether the "API key" and the PIT are the same in form and function.

## Completed

- `.env` (`C:\1_Ed's Active Work\Projects\LiveTransparent\.env`): `GHL_PIT`, `GHL_API_KEY`,
  and `GHL_PIT_LT_HERMES` all now hold the new full-access PIT (`pit-d25ac994-...`).
  Pre-rotation backup: `%LOCALAPPDATA%\Temp\lt_pit_rotation\.env.backup.20260910_100618`.
  `.env` is gitignored/local-only; nothing committed or pushed.
- Live n8n workflows: rotated all 4 old tokens to the new PIT in **70 of 75** workflows via
  the n8n public API (PUT /workflows/{id} with body limited to `name/nodes/connections/
  settings/staticData/pinData` — the API rejects read-only GET fields like `id/active/
  versionId/createdAt`). Every affected workflow's pre-change JSON was backed up to
  `%LOCALAPPDATA%\Temp\lt_pit_rotation\<workflowId>__<name>.pre.json`.
- Re-verified with the repo's own `scripts/inventory_n8n_pits.py` (read-only): the only
  working token now present in live workflows is the new PIT (fingerprint `1f0706f0fc2d`),
  **all HTTP 200**. The previously dead 401 token (`13c5a02e54a2` = `pit-2d2e...`) is gone
  from active workflows.
- Repo exports: refreshed 17 JSON files under `n8n/workflows/`, `n8n/voice-agent/`,
  `n8n/backups/` (36 token replacements total). Verified `grep` across the repo's `*.json`:
  **zero old-token matches remain**.
- API key vs PIT answer (delivered to Ed): in this deployment both old values were
  `pit-<uuid>` format and both authenticated identically as `Authorization: Bearer ...`
  against `services.leadconnectorhq.com` (HTTP 200 on both) — same form, same function.
  GHL's "API Key" vs "PIT" naming is legacy (location-scoped vs scope-controlled v2); the
  meaningful difference is scope, which is why one token could safely replace both.

## Current Live State

- All 70 updated workflows: active/published state unchanged; only node-parameter token
  values changed (no restart needed; tokens read per execution).
- `LT - GHL Daily Leads Ingest` and all other GHL-touching workflows run on the new PIT.
- `AGENCY_TOKEN_PIT` (`.env` line 10) intentionally untouched — agency-scope, referenced by
  no workflow or script (grep across repo = zero hits outside `.env`).
- No executions left `new/running/waiting` by this work.

## Blockers and Risks

- **5 archived workflows could not be rotated via API** (n8n rejects
  "Cannot update an archived workflow"). They do not execute while archived → no production
  impact, but they still embed old tokens:
  - 3 carry `5f92ee655e71` (`pit-b278...`, still-working, SimpleTexting/voice).
  - 2 carry the dead `13c5a02e54a2` (`pit-2d2e...`): the archived duplicate of
    `LT - GHL Daily Leads Ingest` plus its `copy`.
  - Cleanup requires unarchiving in the n8n UI first, then re-running the rotation, or
    deleting them.
- **~19 non-JSON helper scripts** (`_check_ghl_from_n8n.py`, `_query_dispatch.py`,
  `n8n/workflows/*.ts`, `n8n/reporting/*.ts`, `scripts/fix_intake_poller.js`,
  `local-scripts/suppress_linkedin_dms.py`, etc.) still embed old tokens (some dead). Dev helpers,
  not production workflows — left untouched this session; offered to Ed for rotation/trim.
- Nothing committed or pushed (repo currently on branch `codex/social-outreach-sync` with
  many pre-existing modified files from prior sessions). Committing the 17 refreshed JSON
  exports needs Ed's approval.
- Memory write from this session is staged pending approval (`memory.write_approval` on) —
  `/memory pending`.

## Next Steps

1. (Permission needed) Rotate or trim the old tokens in the ~19 non-JSON helper scripts,
   or delete the dead-token ones.
2. (Permission needed) Unarchive + rotate, or delete, the 5 archived workflows so every
   old token is purged server-side.
3. Decide whether to commit the 17 refreshed JSON exports (and any other pending session
   changes) — Ed approval required; `.env` stays local-only regardless.
4. Observe the next scheduled GHL-touching runs (e.g. `LT - GHL Daily Leads Ingest`) to
   confirm clean execution on the new PIT.
5. Approve the staged memory update if desired.
