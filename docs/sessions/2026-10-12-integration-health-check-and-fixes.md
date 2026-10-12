# 2026-10-12/13 — Integration health check + fixes (Reply Backfill, Instagram, Sales Navigator)

## Summary

Ed asked to (1) check whether SMS/SimpleTexting, LinkedIn/Unipile, Instagram/Unipile, and Sales Navigator/Unipile are all working, then (2) "work on fixing them all." This session did a read-only health audit of all four, then applied targeted n8n + Postgres fixes. **All n8n mutations went through the `n8n-lt` REST API (`N8N_LT_API_KEY` from `.env`), never the katwill MCP.** No GHL writes, no contact/tag/sender writes, no sends, no campaign enrollment, no commits.

## Health-check verdict (as of session start)

| Integration | Verdict |
|---|---|
| SMS via SimpleTexting | ✅ Working. API HTTP 200; inbound/unsub recorded through 10/10; send attempts correctly hit the Pacific business-hours gate. |
| LinkedIn via Unipile | ✅ Working (outbound intentionally paused by Ed). Acceptance/State Sync/Relations Backfill success; 12 `connection_accepted` events in 7d. One defect: Reply Backfill intermittently errored. |
| Instagram via Unipile | ⚠️ Transport OK but pipeline stalled. State table (in `n8n` DB) full (379 rows) but sender claimed=0 every day; last real send 2026-08-21. |
| Sales Navigator via Unipile | ❌ Broken. v2 account `status=partial`, `sales_navigator=disconnected` (classic/company still running). Bridge answers `sender_profile_lookup_failed`. |

## Fixes applied this session

### 1. LinkedIn Reply Backfill — two defects fixed (n8n `QfJ2EZcc7lZwNgxj`)

**Defect A — ms-epoch timestamp (root cause of intermittent `date/time field value out of range: "1789128603179"`).** GHL `conversations/search` returns `lastMessageDate` as **epoch milliseconds**, which `Build Reply Events SQL` cast directly to `::timestamptz`. Fixed by adding `normalizeTimestamp()` (converts 12+-digit epoch-ms or 10-digit epoch-s to ISO; garbage→empty→`NOW()` fallback) in both `Check Reply Backfill State` (wraps `conversationTimestamp`) and `Build Reply Events SQL` (normalizes `inbound_at`/`checked_at`).

**Defect B — invitation-withdrawal hold trigger collision.** A DB trigger `lt_invitation_withdrawal_hold()` on `linkedin_connection_state` raises `Invitation cleanup hold blocks automated queue entry` for any held invite contact whose status is `ready`/`requested_pending`. Reply Backfill was selecting held contacts (e.g. France Lescarbeau `0tX0UwkOdlsy2rgyvNS1`, `connection_status='ready'`, `dispatcher_hold=true`) and its `Apply Backfill Update` POST failed the trigger every run → workflow `error` ~every 10 min. This was **pre-existing and correct-by-design** (the hold must block), but Reply Backfill should skip those rows instead of attempting-and-failing.

- I first narrowed the **live DB function** condition (was already `('ready','requested_pending')` — effectively a no-op re-create; the original was already correctly scoped). Blueprint in `scripts/linkedin/plan_john_invite_withdrawals.py` left unchanged.
- **Real fix:** added `NOT EXISTS (... linkedin_invitation_withdrawals w WHERE w.dispatcher_hold AND w.ghl_contact_id = <table>.ghl_contact_id)` to **both halves of the UNION** in the `Select Pending Backfill Rows` query node, so held invite rows are never selected.

**Published versions:** `4174c177…` (Defect A) → `4289ecdb-e36e-4a45-8673-bf1bad99c307` (Defect B), `versionId == activeVersionId`, active. **POST-fix verification run NOT yet observed** — last captured exec was `error 17:40:15` (in-flight when Defect B published at 17:38:51). Next scheduled run ~17:50 UTC.

### 2. Instagram Company Page sender — eligibility filter fixed (n8n `IeovbYnhCsetXS89`)

**Root cause of 3-week stall:** the sender's candidate SELECT only accepted `sequence_status IN ('pending','ready')`, but Message 1 (sent by the **local batch script** `scripts/instagram/batch_instagram_validate_and_send.py`, NOT n8n) sets `sequence_status='sent'` at `message_step=1`. So all 199 step-1 rows (`'sent'`) were invisible → `claimed=0` daily forever.

- Fixed `Send Partnership DM Batch` WHERE to `sequence_status IN ('pending','ready','sent')` (safe: after Message 2 success the row moves to `message_step=2`, so step-1 `'sent'` = M1 delivered / M2 pending).
- **Published:** `6c30293d-8863-4e0e-a2e3-9c23c4b00fdd`, `versionId == activeVersionId`, active. **Post-fix run NOT yet observed** — last run was `17:00:00` (before the 17:32 patch), `claimed=0/sent=0`. Next slot `0 10-15 * * 1-5` America/Los_Angeles → **18:00 UTC**.
- **Impact once it runs:** 199 rows become eligible for Message 2 (154 dan_brands + 45 partnerships). Cap `dailyCap=45`, `maxPerHour=10`. Reply-suppression + 2-business-day wait + identity filters all still apply.

**Data note (NOT a defect, reporting only):** the `instagram_company_dm_state` / `_send_log` / `_run` / `instagram_activity_events` tables live in the **`n8n` Postgres database**, not the `postgres` report DB. Earlier health-check "0 rows" readings were from the wrong DB — the real state is in `n8n` (379 state, 208 send_log, 39 run rows). Only `Message 1` is pending for 175 step-0 rows (but only 3 are `identity_status='validated'` — the rest need identity validation first).

### 3. Sales Navigator reconnect — link generated, NOT completed (needs Ed)

v2 account `acc_01m3sefk22e8jvnmvvfx333pye` (Cameron Karkut) has `sales_navigator=disconnected`. Reconnect requires Cameron to re-authenticate LinkedIn via Unipile Hosted Auth (no credentials pass through us). Generated a reconnect link:

- **Endpoint:** `POST https://api.unipile.com/v2/auth/link` (v2) with body `{account_id, expires_on, redirect_uri}` — note: the older `POST /api/v1/hosted/accounts/link` and `{type:"reconnect", reconnect_account}` params are **v1/deprecated and return 400**; v2 uses `account_id` + `expires_on` + `redirect_uri`.
- **Key:** `UNIPILE_v2_MIGRATION_SERVICE_API_KEY` (`.env`).
- Returned `HostedAuthLink.url` (one-time, ~2h expiry, regenerable). Redirect URI used `https://livetransparent.com/`.
- **NOT completed** — Cameron must open the link and authenticate. After reconnect, verify `products_connection_status.sales_navigator == running`.

### 4. 2 held Sales Navigator message rows — inspected, left held

`sales_navigator_v2_message_events` ids 5 & 6 (`held`, `failure_code=ghl_conversation_lookup_http_error`, from 10/02) both have valid `ghl_contact_id` but NULL `ghl_conversation_id`. The reconciler `sFrvSJIZusAbrsFx` runs every min, max 10 attempts, then terminal `held`. AGENTS rule: **do not blindly replay uncertain events or release pending contact claims.** Left as-is pending a deliberate decision; they are inbound messages that failed GHL conversation lookup, not SN-auth failures.

## Not done / next steps (ordered)

1. **Verify Reply Backfill post-fix** — confirm the run after ~17:50 UTC is `success` (no more `date/time out of range`, no more `hold blocks`). If still erroring, inspect the failing contact.
2. **Verify Instagram sender post-fix** — confirm the 18:00 UTC run `claimed>0` and `sent>0` (or at least `claimed>0` proving the filter works); check `instagram_company_dm_run` for 2026-10-12 nonzero counts and `instagram_company_dm_send_log` Message-2 rows.
3. **Sales Navigator reconnect** — hand Ed the regenerated Hosted Auth link; Cameron authenticates; verify `sales_navigator=running`.
4. **SN held rows (2)** — decide: reconcile or leave held (requires reading GHL conversations for those contacts; do not auto-replay).
5. **SMS** — watch next Pacific business-hours window (10:00–17:00 `America/Los_Angeles`) to confirm a live send goes out (last actual send 10/09–10/10; today's attempts correctly gated `outside_business_hours`).

## EOS continuation (2026-10-12 18:06–18:18 UTC) — verification + clean-up

### Reply Backfill — secondary fix landed

The Reply Backfill post-fix runs from 17:50–18:00 UTC all errored with a NEW bug: `ReferenceError: clean is not defined [line 7]` in `Build Reply Events SQL`. The Oct-12 patch (Defect A — epoch-ms normalization) copied `normalizeTimestamp()` into this Code node but did NOT copy its `clean()` helper (which is defined in `Check Reply Backfill State`'s scope but not here). Patch `4289ecdb…` was deployed but the JS crashed before SQL was built.

**Fix published (n8n-lt only, no GHL touch):**
- Added `clean(v)` helper to `Build Reply Events SQL` jsCode (defined once, before `normalizeTimestamp`).
- New `versionId == activeVersionId = 436a54d0-7bd4-47a5-8bb0-e9b158dab5d0`, updatedAt 10/12 18:06:05 UTC.

**Verified post-fix run 1133169 (18:10 UTC, `status=success`):**
- 25 rows selected, all `reply_detected=false` (no new LinkedIn replies; expected)
- `Build Reply Events SQL` produced 25 valid SQL payloads (`SELECT '<contact_id>'::text AS contact_id`)
- `Record Reply Events` succeeded (`executionStatus:"success"`)
- `Summarize Backfill Run`: `{ok:true,total:25,active:0,idle:25,error:0}`
- No `date/time out of range` errors, no `Invitation cleanup hold blocks automated queue entry` triggers
- Next scheduled run 18:20 UTC → expected success

### Instagram sender — verified live

Run 1133105 (10/12 18:00 UTC, `status=success`):
- `mode: live`, `cap: 45`, `sent_today: 9`, `batch: 10`, `sent: 9`, `failed: 1`, `claimed: 10`, `reportingBackfillRows: 204`
- 9 successful sends: SACRED (`sacredfarmswa`), Auxly, Surly Brewing, Higher Realm, Redemption Cannabis, Portland Heights, Lehua Brands, Shatterizer, CannaPrints
- 1 failure: Jushi Holdings (`Request failed with status code 422` — likely already-DM'd previously or duplicate contact_id)
- Sender reads `sent` rows again now (the post-fix filter change), so 199 M2 rows are visible. Cap 45/day, 10/hr will pace future sends.

### Sales Navigator — Hosted Auth link regenerated, Cameron still needs to authenticate

- Endpoint is **v2** (`POST https://api.unipile.com/v2/auth/link` with `X-API-KEY` and body `{providers:["LINKEDIN"], account_id, expires_on (ISO string), redirect_uri}`). The prior session's note about `{account_id, expires_on, redirect_uri}` was incomplete — `providers` is required.
- Account `acc_01m3sefk22e8jvnmvvfx333pye` still: `status=partial`, `metadata.products_connection_status={classic:running, company:running, sales_navigator:disconnected}`.
- New link (valid ~2h from 18:15 UTC): `https://auth.unipile.com/?token=5H%2Bzujd2.sVWx%2FldT3OcVqFR4kRy1SNrb%2BHexhS1e1DzK0jbTb60%3D`
- Cameron must open the link in a browser, authenticate LinkedIn, then verify `sales_navigator=running` (and the bridge stops returning `sender_profile_lookup_failed`).

### SN held rows (2) — left held, no blind replay

Reconciler `sFrvSJIZusAbrsFx` runs every minute; latest execution 1133177 (18:11:25 UTC, `status=success`) returned `success:true` from `Claim Stale V2 Row` with no stale rows (because `posted` rows older than 10 min without a `delivered` callback don't exist right now — only the 2 terminal `held` rows from 10/02 remain). Per the AGENTS rule, no blind replay. Decision still requires Ed's read of the 2 GHL conversations for those contacts.

### SMS — partial live-send verified, but a different bug found

Pacific business hours are open (current UTC 18:18 = LA 11:18). Found a **real live SMS run** today:

- Execution 1128168 (10/11 20:25 UTC = LA 13:25, business hours) — Gambling campaign → Irena Shershunovich (`csK1DO3o5P1K3la6nkQ1`), Product Madness. `customData.message="Hey Irena, just emailed you about running Product Madness's gaming ads on Meta/Google without the constant bans. Worth a quick look?"`, `dryRun=false`, `templateKey=...` — but `Validate + Send SMS` returned `{ok:false, error:"unauthorized"}`.
- Root cause: the auth check in `Validate + Send SMS` requires the supplied key to match either `cfg.authHeaderValue` (in header `x-lt-simpletexting-key`) OR `cfg.legacyAuthHeaderValue` (in header `x-lt-webhook-key`). The GHL campaign workflows send the **legacy secret** `Lt9Qv2Xm` but in the `x-lt-simpletexting-key` header — not in `x-lt-webhook-key`. So both checks fail and the send is blocked.
  - Expected: `x-lt-simpletexting-key = aetFwFcEojH1QQ9fWSHskDIQs6nV8gKfJsvrjBw8J6Y` (canonical post-Oct-1 value) OR `x-lt-webhook-key = Lt9Qv2Xm` (legacy alias)
  - Received: `x-lt-simpletexting-key = Lt9Qv2Xm` (legacy secret in canonical header — mismatch)
- This is the SMS live-send blocker. **Fix scope:** (a) update the `Validate + Send SMS` auth check to also accept `Lt9Qv2Xm` in `x-lt-simpletexting-key` (legacy alias under canonical header), OR (b) update each of the 8 vertical campaign workflows' webhook action to use `x-lt-webhook-key` instead of `x-lt-simpletexting-key`. The (a) fix is one node; (b) is 8+ workflow edits. Requires Ed's approval — touches live send auth.
- Business-hours gate is **correct** in Resolver (overrides Config's stale `America/New_York` with `America/Los_Angeles`). Executions at LA 6:49 AM correctly returned `outside_business_hours` and didn't send. Executions at LA 13:25 (during hours) tried but got `unauthorized` — the auth bug.

### Updated next steps (replacing the earlier list)

1. **Decision on SMS live-send auth fix** (Ed pick): (a) one-node update to `Validate + Send SMS` auth check, OR (b) GHL-campaign workflow header rename × 8. Either way the next live SMS during LA business hours must be a controlled test, not a fleet blast.
2. **SN Hosted Auth link handoff** — Ed, send Cameron the link above; he authenticates; verify `sales_navigator=running`.
3. **SN held rows (2)** — Ed reads GHL conversations for those 2 contacts; decision: reconcile (re-fetch `ghl_conversation_id`) or leave terminal `held`.
4. **Reply Backfill + IG sender** — now self-healing; next scheduled runs (18:20 UTC Reply Backfill; IG 19:00 UTC slot) should both be `success`.

### Safety boundaries preserved
- n8n-lt only; no katwill/other tenant.
- No GHL contact/tag/sender writes, no sends, no campaign enrollment, no publish of GHL workflows, no commits.
- PIT / pg password / n8n API key / Unipile keys never printed.
- Invitation-withdrawal holds (206 rows) untouched and still enforced by the DB trigger.
- SN held rows (2) untouched.
- SMS live-send auth fix not applied (requires Ed's approval per safety gate above).
- Instagram M2 pacing (45/day, 10/hr, 2-business-day gap, reply suppression) left intact.