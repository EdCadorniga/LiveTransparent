# HANDOFF — Integration health check + fixes (Reply Backfill, Instagram, Sales Navigator)

**Copy-ready prompt for the next LLM.**

---

Continue LiveTransparent integration work. Read `docs/sessions/2026-10-12-integration-health-check-and-fixes.md` first — it is the full record of the previous session. All n8n mutations used ONLY the `n8n-lt` REST API (`N8N_LT_API_KEY` from `.env`), never the katwill MCP. No GHL writes, no sends, no commits were made.

**Verdict at session start:** SMS ✅ working (gated by Pacific business-hours, not broken); LinkedIn ✅ working (outbound intentionally paused by Ed) but Reply Backfill was erroring; Instagram ⚠️ pipeline stalled since 2026-08-21 (state full in `n8n` DB but sender claimed=0 daily); Sales Navigator ❌ `sales_navigator=disconnected` on v2 account `acc_01m3sefk22e8jvnmvvfx333pye`.

**Fixes applied (all published, `versionId == activeVersionId`, active):**

1. **Reply Backfill `QfJ2EZcc7lZwNgxj` → `4289ecdb-e36e-4a45-8673-bf1bad99c307`.** (a) Added `normalizeTimestamp()` in `Check Reply Backfill State` + `Build Reply Events SQL` to convert GHL epoch-ms `lastMessageDate` to ISO (fixes `date/time out of range: "1789128603179"`). (b) Added `NOT EXISTS (... linkedin_invitation_withdrawals w WHERE w.dispatcher_hold AND w.ghl_contact_id = <table>.ghl_contact_id)` to BOTH UNION halves of `Select Pending Backfill Rows` (fixes `Invitation cleanup hold blocks automated queue entry` from DB trigger `lt_invitation_withdrawal_hold` on held contacts like France `0tX0UwkOdlsy2rgyvNS1`). Note: the live DB function condition was already correctly scoped `('ready','requested_pending')`; the real fix was excluding held rows from selection.

2. **Instagram sender `IeovbYnhCsetXS89` → `6c30293d-8863-4e0e-a2e3-9c23c4b00fdd`.** Changed `Send Partnership DM Batch` WHERE from `sequence_status IN ('pending','ready')` to `IN ('pending','ready','sent')`. Root cause: Message 1 is sent by the LOCAL script `scripts/instagram/batch_instagram_validate_and_send.py` (sets `sequence_status='sent'` at `message_step=1`), which the old filter never matched → 199 rows invisible → `claimed=0` for 3 weeks. **State tables live in the `n8n` Postgres database, NOT the `postgres` report DB** (earlier "0 rows" readings were the wrong DB; real state = 379 state / 208 send_log / 39 run rows).

3. **Sales Navigator reconnect — link generated, NOT completed (needs Ed/Cameron).** v2 account still `sales_navigator=disconnected`. Hosted Auth reconnect link via `POST https://api.unipile.com/v2/auth/link` with body `{account_id, expires_on, redirect_uri}`, key `UNIPILE_v2_MIGRATION_SERVICE_API_KEY`. (The v1 `/api/v1/hosted/accounts/link` + `{type:"reconnect", reconnect_account}` params are deprecated and return 400.) Link is one-time ~2h expiry — **regenerate a fresh one and hand it to Cameron to authenticate**, then verify `products_connection_status.sales_navigator == running`.

4. **2 held Sales Navigator rows — inspected, left held.** `sales_navigator_v2_message_events` ids 5,6 (`held`, `ghl_conversation_lookup_http_error`, 10-02) have `ghl_contact_id` but NULL `ghl_conversation_id`. Reconciler `sFrvSJIZusAbrsFx` terminalizes at 10 attempts. **Do not blindly replay** — decide reconcile-vs-leave-held explicitly.

**NOT yet verified (post-fix runs had not landed when session ended ~17:47 UTC 2026-10-12):**

1. **Reply Backfill** — confirm the first run after ~17:50 UTC is `success` (no timestamp/hold errors). Last captured was `error 17:40:15` (in-flight during the 17:38:51 patch).
2. **Instagram sender** — confirm the `18:00 UTC` run (cron `0 10-15 * * 1-5` America/Los_Angeles) has `claimed>0` (proves filter fix) and ideally `sent>0`. Check `instagram_company_dm_run` for 2026-10-12 nonzero counts and `instagram_company_dm_send_log` for Message-2 rows. Expect up to 45/day, 10/hr M2 sends to the 199 now-eligible rows (154 dan_brands + 45 partnerships); reply-suppression + 2-business-day gap + identity filters intact. Only 3 of the 175 step-0 Message-1-pending rows are `identity_status='validated'`.
3. **SMS** — watch next Pacific business-hours window (10:00–17:00 `America/Los_Angeles`) for a live send; today's attempts correctly returned `outside_business_hours` (gate working as designed, not broken).

**First actions for you:**
1. Re-read the session doc above.
2. Query Reply Backfill (`QfJ2EZcc7lZwNgxj`) + IG sender (`IeovbYnhCsetXS89`) recent executions via n8n-lt REST (`GET /api/v1/executions?workflowId=...`) to see if post-fix runs succeeded.
3. If Reply Backfill still errors or IG still `claimed=0`, pull failing execution detail (`GET /api/v1/executions/{id}?includeData=true`) and diagnose.

**Safety boundaries to preserve:** n8n-lt only (never katwill/other tenant); no GHL contact/tag/sender writes, no sends, no campaign enrollment, no GHL workflow publishes, no commits; invitation-withdrawal holds (206 rows) still enforced by DB trigger; never print PIT / pg password / n8n API key / Unipile keys.