# LinkedIn DM Pipeline Repair & Audit - 2026-08-18

## Scope

The LinkedIn connection + DM pipeline had stalled: connection invites near-zero and DMs at zero for ~3 weeks. This session diagnosed root causes, fixed them, and ran two audit passes checking for new bugs, logic errors, and duplicate sends. No interest in Instagram DM work here — a separate LLM owns that.

## Root Causes Found

1. **Dispatcher regex corruption** - `identifier()` used `/^https?:\\\\/\\\\//i` (the known SDK-serialization `\\/` corruption). Every `Dispatch LinkedIn Requests` run failed with `SyntaxError: Invalid regular expression flags`, so no invites went out. Artifacts: `requested_pending` pool of ~1,400 that never advanced.
2. **DM send 422** - `Send DM Sequence Messages` always called `POST /chats` (start a new chat). For contacts that already had an outbound chat (e.g. Alison, step 3), Unipile returned 422 ("no_connection_with_recipient" / action already performed). Correct path per Unipile docs is `POST /chats/{chat_id}/messages` for an existing chat.
3. **Reply Backfill over-suppressed** - `Check Reply Backfill State` set `dm_conversation_status='active'` whenever the GHL conversation lookup *errored* (`conversation_check_failed`), not just on real replies. Across the pool this left only ~30 connected contacts DM-eligible.
4. **State Upsert blocked progression** - `Build Upsert SQL` had a CASE clause preserving the existing `connection_status` whenever the row's payload had `dm_conversation_status='active'`. Since the old backfill stamped `active` on the invited rows' payloads, `requested_pending -> requested` never advanced after a real invite. Real invites went out (Unipile + GHL tag) but the state rows stayed `requested_pending`.
5. **Dispatcher daily limit not enforced** - Config declared `dailyLimit: 60` but the code ignored it (would send ~240/day).

## Fixes Applied (all published/active)

| Workflow | ID | Version | Change |
|----------|----|---------|--------|
| LT - GHL LinkedIn Connect Dispatcher | fXxw5lanZcDmUrst | c7291410 -> f2f52041 | Fixed `\\/` regex (`=> /^https?:[/][/]/i`); enforced daily invite limit (60/day) via direct `pg` count of today's `requested` rows |
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | aaf650a9 -> bc79f0d1 | Route send to existing chat (`POST /chats/{chat_id}/messages`) when a `last_chat_id` exists; capture `err.cause` body; durable `dm_sent` event (`ON CONFLICT DO NOTHING`) written after a successful send and BEFORE the state upsert; `Find Contacts Ready for DM` now excludes steps already sent |
| LT - LinkedIn Reply Backfill (Unipile) | QfJ2EZcc7lZwNgxj | b695fc8c -> 9e0131f4 | Stop forcing `active` on check errors; `shouldRemainActive = replyDetected` (self-healing) |
| LT - LinkedIn Connection State Upsert | Old7ZvyVYgFaJgDr | 3cd12fa5 -> 4045c96c | Removed over-broad `active`-preservation clause so `requested_pending -> requested` advances; added guard to prevent `requested -> ready`/`requested_pending` downgrade |

## Data Repairs

- Reset 31 connected non-relation rows wrongly marked `active` -> `idle` (unblocking the queue).
- Repaired 39 invited-but-stuck rows from `requested_pending` (payload `status='sent'`) -> `requested`.
- Healed 918 stale `dm_conversation_status='active'` rows confirmed as `no_inbound_linkedin_conversation` -> `idle`.
- Result: DM-eligible connected (non-relation) contacts went 30 -> 66.

## Verification

- Dispatcher regex fix: 17:15 LA run sent 10 invites, 0 errors; ~30 more across subsequent runs, all distinct contacts.
- State advancement: 18:15 LA run's 10 invites all became `requested` (`stuck_sent_pending=0`).
- Daily limit: 60 distinct contacts invited today, exactly capped (18:45 run sent 1, then stopped).
- No duplicates: `contact_dups=0`, `invite_dups_today=0`; 29 "provider duplicates" are distinct GHL contacts (same profile in multiple pools) - legitimate.
- Reply Backfill: runs every 10 min, all success; new logic produces `idle` for non-replies, not forced `active`.
- State Upsert webhook: healthy across all writes after the change.
- DM Find query (with dedup guard) is valid SQL and returns 66 eligible rows.

## Duplicate-Send Hardening

- Invites: the GHL tag `linkedin_connection_requested` is added after each successful invite and checked before sending; state now also advances to `requested`, so the queue shrinks instead of looping.
- DMs: durable `dm_sent:{contact}:{step}` event (unique `event_key`) is written after a successful Unipile send and before the state upsert; `Find Contacts Ready for DM` excludes any step that already has that event. Even if the state upsert fails after delivery, the same step is not re-sent.
- Reply safety: the DM send performs its own live inbound-conversation check before sending and fails closed on lookup errors; the Dispatcher does the same before inviting.

## Remaining Gap

The DM send path (chat routing + durable event) has not yet been exercised by a real scheduled run. Code is syntax-valid, the Find query runs clean, and the queue is populated (66). DM Sequence schedule is 12-22 UTC (05:00-15:00 LA) Mon-Fri; next scheduled run 05:00 LA the following day. A single manual DM batch can prove it end-to-end if approved.

> **Follow-up 2026-08-19**: the 08-18 REST-PUT repair fixed the dispatcher crash (`\\/` regex) and daily cap but inherited the still-corrupt `sanitize()`/`{first_name}` regexes, so invites sent from 08-18 00:15 onward were garbled. Both were fixed and re-published the next day — see [`2026-08-19-linkedin-double-escape-fix.md`](/docs/sessions/2026-08-19-linkedin-double-escape-fix.md).
