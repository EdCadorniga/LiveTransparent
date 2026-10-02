# LinkedIn `linkedin_connected` backfill + connection-path fixes (2026-10-02, session 3)

Approved YOLO/autonomous session. Scope: complete the pre-approved `linkedin_connected`
backfill and fix every LinkedIn-connection defect found along the way. No LinkedIn
message was sent. All changes are idempotent and read-mostly; every workflow change was
published with `versionId == activeVersionId`.

## Outcome summary

| Item | Result |
|---|---|
| `linkedin_connected` backfill | **678 distinct GHL contacts tagged, 0 untagged** (read-back measured) |
| Durable tag sync | New active daily workflow `LT - LinkedIn Connected Tag Sync` (`rcvTMprJKga9aEJ6`) |
| `requested` reconciliation | **155** `requested`/`requested_pending` rows that were genuinely 1st-degree → marked `connected` + tagged |
| Dispatcher mirror 401 | Root-caused (company token) and fixed (exchange to location token) |
| Relations Backfill silent no-op | Root-caused (`/users/connections` wrong endpoint) and fixed |
| Security literals | **Still open** (documented below) — not rotated this session |

State after: `linkedin_connection_state` = 2,196 `connected`, 1,184 `requested`, 58
`requested_pending`, 10,892 `ready`, 100 `follower_messaged`, 5 `completed`.
`partnership_linkedin_connection_state` = 127 `ready` (no connected rows).

## 1. The prior scope estimate was wrong (important correction)

`AGENTS.md` said all 2,041 `connected` rows had real GHL contact ids and only
`linkedin:follower:` synthetic ids needed skipping. **Only 112 were real.** The other
**1,929** used a second synthetic prefix, `linkedin:relation:<slug>`, created by the
Relations Backfill. The old measurement only excluded `linkedin:follower:`, so it
over-counted the taggable set by ~18x.

Correct resolution (used by both tools):
- state rows with a real GHL contact id → tag directly; and
- synthetic `linkedin:%` rows resolved to a real contact via the shared
  `linkedin_contact_profile_index` on **`normalized_profile_slug = linkedin_public_identifier`
  OR `linkedin_provider_id = ANY(linkedin_provider_ids)`**.

This yields **678 distinct taggable contacts** (was 537 before provider-id resolution was
added). 1,514 relation rows remain unresolvable to any contact (nothing to tag).

## 2. Backfill (done)

Tool: `scripts/linkedin/backfill_linkedin_connected_tag.py` (`--measure` / `--apply`).
- Reads `connected`/`completed` rows from production Postgres over SSH, resolves contacts,
  GETs each, and POSTs `linkedin_connected` only when missing. Synthetic ids are never
  treated as contacts.
- Bug found + fixed in the tool itself: GHL `POST /contacts/{id}/tags` returns **201**
  (not 200); the first apply run mis-read 201 as failure but had in fact written every tag.
- Final read-back: **678/678 tagged, 0 failed, 0 not_found**.
- `completed`/synthetic `linkedin:follower:` DM rows are skipped.
- Partnership connected rows: none, so `partner_linkedin_connected` was not needed.

## 3. Durable fix — `LT - LinkedIn Connected Tag Sync` (`rcvTMprJKga9aEJ6`)

Created and activated on n8n-lt (daily `0 4 * * *` `America/Los_Angeles`, after the 03:15
Relations Backfill). Nodes: Schedule Trigger → `Config` (Set) → `Tag Connected Contacts`
(Code) → `Result`; plus Manual Trigger. Build/deploy:
`scripts/linkedin/build_connected_tag_sync_workflow.py` + `scripts/linkedin/connected_tag_sync.js`.

- Code node uses `require('pg')` + `this.helpers.httpRequest` (the repo's external-runner
  pattern) to run the same union resolution and conditionally tag. Steady state is one GET
  per connected contact per day.
- **Live-validated**: execution `1080021` (and later) returned
  `scanned=531/537, already_tagged=531/537, failed=0, errors=0`. The extended provider-id
  resolution was confirmed live (`scanned=537`).
- 429 hardening: `statusOf()` covers n8n's various error shapes so 429/5xx are retried; a
  transient 429 storm only occurred while the temporary per-minute test cron overlapped
  runs (the daily single run does not).

### Why a separate workflow (not the state-upsert choke point)
`VPiHfBwzOHaJnHBY` and `ceaKnz6E3onQrZpt` call the state-upsert webhook for *every*
connection each run (thousands/day). Tagging inside that shared workflow would add a GHL
write per connected upsert and could not resolve synthetic ids without DB access. The
isolated daily job uses the profile index, is idempotent, and cannot break the send paths.

## 4. `requested` → `connected` reconciliation (155 fixed)

Tool: `scripts/linkedin/reconcile_requested_connections.py` (dry-run by default; `--apply`).
- Fetched all **5,506** Unipile 1st-degree relations (`GET /users/relations`, cursor
  exhausted) and cross-checked against 1,396 `requested`/`requested_pending` rows.
- **155** were genuinely 1st-degree now. For each: POST to the canonical state-upsert
  webhook (`connection_status='connected'`, `connected_at` = Unipile relation `created_at`,
  `event_type='connection_accepted'`) and add `linkedin_connected` in GHL.
- Result: `state_ok=155, state_fail=0, tagged=155, tag_fail=0`; `connected` 2,041 → 2,196,
  `requested` 1,338 → 1,184.
- The remaining ~1,184 `requested` are genuinely not connected per Unipile (correctly
  pending).

## 5. Dispatcher mirror 401 (fixed, previously-known defect)

Workflow `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`), function
`mirrorLinkedInToGhl`. Root cause proven at the API:
- stored `ghl_oauth_tokens` row is `user_type = Company` (agency token);
- `POST /conversations/messages` with the company token → **401** "This authClass type is
  not allowed to access this scope";
- `POST /oauth/locationToken` (`companyId`,`locationId`) → a **Location** token, and
  `POST /conversations/messages` with it → non-401 (auth OK).

Patch (`scripts/linkedin/fix_dispatcher_mirror_location_token.py`) exchanges the company
token for a location token before posting the mirror. Published
`versionId == activeVersionId == 65a7398b-328c-4f99-b709-ee2da1bc6683` (10 nodes).
Not exercised by a live send (that run had `sent=0`); verified at the endpoint level.

## 6. Relations Backfill silent no-op (fixed, found this session)

`LT - LinkedIn Relations Backfill (Unipile)` (`VPiHfBwzOHaJnHBY`) called
`GET /users/connections?account_id=...`, which returns the **account's own profile
object**, not a list. `res.data.items` was always `undefined`, so every daily run
short-circuited with `backfilled: 0` (2.4 s) and **never** reconciled requested → connected.

Fix (`scripts/linkedin/fix_relations_backfill_endpoint.py`):
- endpoint → `GET /users/relations` (`UserRelationsList`, `items`/`cursor`);
- provider id fallback → `conn.member_id`; URL fallback → `conn.public_profile_url`;
- added a 240 s deadline so the now-real loop cannot exceed the runner task timeout.
Published `versionId == activeVersionId == 0754c540-80a5-4f6f-8b74-7d7ef8f35f9f`.
Next scheduled run 03:15 `America/Los_Angeles`; not live-verified this session (logic is
proven at the API: `/users/relations` returns 5,506 items).

## 7. STILL OPEN — security

The GHL PIT (`pit-d25ac994-…`) and `stateUpsertSecret` remain committed in plaintext in
many workflow `Config` nodes and were printed into earlier sessions. **Not rotated this
session** — rotation touches many live workflows and risks breaking state writes at
session end. Plan (next session):
1. Rotate `stateUpsertSecret`: generate a new value, update the state-upsert validator
   (`Old7ZvyVYgFaJgDr` Config) and every caller (`fXxw5lanZcDmUrst`, `VPiHfBwzOHaJnHBY`,
   `ceaKnz6E3onQrZpt`, `3ttEvr5NMcQCS4Hp`, `IPN8jnR3XSurX0o1`, DM/partnership paths), then
   verify a signed upsert returns 200.
2. Evaluate GHL PIT rotation (large multi-workflow operation; coordinate with Ed).
3. Migrate the leaked `Config` Code-node literals to `Config` Set nodes and stop saving
   Config output into execution data where practical.

## 8. Deployed version IDs

| Workflow | ID | Version |
|---|---|---|
| LinkedIn Connected Tag Sync (NEW) | `rcvTMprJKga9aEJ6` | `1394ef0f-7a23-4903-be32-aaded3af2d8c` |
| GHL LinkedIn Connect Dispatcher | `fXxw5lanZcDmUrst` | `65a7398b-328c-4f99-b709-ee2da1bc6683` |
| LinkedIn Relations Backfill | `VPiHfBwzOHaJnHBY` | `0754c540-80a5-4f6f-8b74-7d7ef8f35f9f` |

## 9. Tools / files

- `scripts/linkedin/backfill_linkedin_connected_tag.py`
- `scripts/linkedin/reconcile_requested_connections.py`
- `scripts/linkedin/build_connected_tag_sync_workflow.py` + `connected_tag_sync.js`
- `scripts/linkedin/fix_dispatcher_mirror_location_token.py`
- `scripts/linkedin/fix_relations_backfill_endpoint.py`

## 10. Open items / next steps

1. Confirm the next daily `rcvTMprJKga9aEJ6` run (~04:00 LA) and the next
   `VPiHfBwzOHaJnHBY` run (~03:15 LA) succeed with real reconciliation.
2. Observe a dispatcher run that actually sends (`sent>0`) to confirm the conversation
   mirror now lands under `LinkedIn via Unipile` (no 401).
3. Security rotation (section 7).
4. Optional: a Unipile USERS webhook on `new_relation` as a real-time backstop for
   no-note accepts (currently detected only by the daily reconcile/Relations Backfill).
