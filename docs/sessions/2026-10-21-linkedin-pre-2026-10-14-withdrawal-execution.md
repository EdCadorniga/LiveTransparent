# LinkedIn pre-2026-10-14 withdrawal campaign — EXECUTED (2026-10-21)

Business timezone for all dates below: `America/Los_Angeles`. Campaign ran 2026-10-21
12:07–16:27 PT (2026-10-21 18:45–23:27 UTC / 2026-10-22 02:45–07:27 SGT).

Ed approved the live withdrawal of every LinkedIn connection request made **prior to
2026-10-14**. The scope was computed and snapshotted read-only on 2026-10-21
(`docs/sessions/2026-10-21-linkedin-connection-request-status-and-withdrawal-scope.md`,
scope file `local-scripts/linkedin-withdrawal-scope-pre-2026-10-14.json`).

## Outcome

| Result | Count | Meaning |
|---|---|---|
| **withdrawn** | **1,188** | Provider-confirmed `InvitationCanceled`, all HTTP 200, journal + ledger `withdrawn_at` recorded |
| skipped | 32 | Invitation still pending at LinkedIn, but the identity is **already connected** in our ledger — deliberately not deleted |
| already_gone | 1 | Accepted/declined externally before the DELETE; recorded as `already_gone`, not an error |
| uncertain | 0 | No unknown-outcome deletes |
| failed | 0 | No provider rejections |
| **Total in scope** | **1,221** | Fully accounted for; 0 rows left `pending` |

Provider pending invitations went **1,273 → 88**. The 88 remaining are:

- **32** in-scope invitations that were skipped (below), and
- **56** out-of-scope invitations sent on/after 2026-10-14 (Oct 14 = 3, Oct 20 = 30, Oct 21 = 23) — untouched, as required.

The 206 John/mojibake invitations withdrawn on 2026-10-12 were not touched.

## Timeline

| Time (UTC) | Event |
|---|---|
| 18:32 | Capture completed: 1,221 rows written to `linkedin_invitation_withdrawals` with note text, send timestamp, GHL contact + vertical, 22-day cooldown, `dispatcher_hold=true`, snapshot path + SHA-256. Hold trigger already installed from the Oct-12 campaign and re-verified on both state tables. |
| 18:43–19:08 | First sweep at the documented 30 s spacing. Withdrew **37** (plus 3 skipped) before a transient n8n-lt error on the dispatcher's executions endpoint halted it. The halt message did not distinguish "not inactive" from "executions unreadable", and the worker's status reported a stale pre-batch count, which initially read as "0 withdrawn". |
| 19:12–23:27 | Accelerated sweep at 5 s spacing, 100 per batch, 30 s between batches. Withdrew the remaining **1,151**. Completed 23:27:45 UTC. |

Wall clock: **4 h 20 min** for 1,221 — slower than the "next couple of hours" target. The
bottleneck was **per-invitation safety overhead, not provider pacing**: each invitation
triggered `paused_dispatchers()` (6 n8n-lt API calls) plus 2–3 SSH Postgres round-trips
for the claim and the ledger write, ~12.6 s per invitation against a 5 s delay. 12 batches
× ~21 min. The provider never rate-limited or restricted the account at this pace.

**Fix for any future campaign:** verify the dispatchers once per batch instead of once per
invitation, and batch the ledger writes. That removes ~7 s per invitation and brings
1,221 withdrawals to ~5.5 s each (~2 h).

## Why 32 were skipped

`withdraw()` refuses to delete an invitation whose identity our ledger already records as
`connected`/`completed` — a connection request to an existing connection is a no-op, and
5 of the 32 have two GHL contacts matching one LinkedIn identity, so a delete could hit the
wrong person. Breakdown of how the match was made: 12 by GHL contact id, 13 by contact id
+ public identifier, 6 by public identifier only, 1 by contact id + provider id.

- **30 of 32 were connected before the invitation was even sent** (e.g. Blake Patterson connected 2023-05-02, invite sent 2026-09-21; Chris Fontes connected 2023-04-06).
- 2 connected after the invite was sent.
- 1 is Ed himself (`edmundo-c-a06372166`).
- 26 carry a resolved GHL contact id; 6 match only on the LinkedIn public identifier.
- 5 have more than one candidate GHL contact; 1 has none.

These remain pending at LinkedIn and are harmless there. If Ed wants them removed, the
tool needs an explicit override of the connected-state skip, reviewed per row first.

## Ledger state

`linkedin_invitation_withdrawals` now holds **1,427 rows** (206 from Oct-12 + 1,221 new),
**all 1,427 with `dispatcher_hold=true`**.

- 1,188 withdrawn rows carry `withdraw_http_status=200`, `withdrawn_at` between
  2026-10-21T18:45Z and 2026-10-21T23:27Z, and `cooldown_until = 2026-11-12` (22 days).
- Note preservation: 1,172 rows keep the exact original connection note; 49 rows store
  `NULL` (the provider sent no note).
- 1,123 rows carry a resolved GHL contact id, vertical and the per-vertical re-invite template.
- Re-invite state: **1,096 rows `pending`** (cooldown to 2026-11-12) and **125 rows
  `needs_review`** = 98 unmatched (no GHL contact id) + 27 resolved-but-flagged
  (ambiguous dual contact or a connected state). The 32 skipped and the 1 already-gone
  row are all inside the 125. The `needs_review` rows must stay out of any automatic
  re-invite.

## Provider send dates are recomputed at read time (not a stored timestamp)

`GET /users/invite/sent` returns a relative `date` string ("Sent 6 months ago",
"Sent 2 weeks ago") and a `parsed_datetime` that Unipile **recomputes from it on every
read**. The same invitation therefore reports a different absolute day as the clock
moves, and the mapping is lossy: one invitation captured as `2026-09-21T18:18:17Z` read
back as `2026-08-22T03:07:22Z` a few hours later ("Sent 2 months ago" → 30 days
earlier), while "Sent 1 month ago" moved forward one day. Between 2026-10-21 23:28 UTC
and 2026-10-22 00:30 UTC every pending invitation's day label shifted by one, purely
because the UTC date rolled over.

Consequences, all verified:

- The by-day breakdowns in this document and in the 2026-10-21 scope read are **capture-time
  snapshots**, not stable facts. Do not treat them as the send date.
- The scope decision itself is robust: the 32 in-scope invitations are days away from the
  2026-10-14 boundary, and the 56 out-of-scope ones stay on/after it, so the split
  (32 / 56) was identical on every read.
- The `old_invitation_sent_at` value stored in the ledger is the provider's value **as of
  capture**. It is the only send-time record that exists, which is why the ledger, not a
  fresh provider read, is the source of truth for "when was this sent".
- `withdraw()` re-evaluates the cutoff against the live value before every DELETE and
  fails closed when it disagrees with the captured scope ("Live invitation is outside the
  captured defect scope"). No such halt occurred, so all 1,188 deletes were taken in a
  consistent scope state. A campaign that spans a UTC midnight will trip that guard by
  design - re-capture rather than weakening it.


## Tooling changes

`scripts/linkedin/plan_john_invite_withdrawals.py`:

- **`--before-date YYYY-MM-DD`** — calendar scope filter. `issue_of()` now classifies by
  send day when a cutoff is given, keeping the note-based `john_note` / `mojibake` modes
  intact. The cutoff is stored in the snapshot and re-evaluated at withdrawal time, so a
  live invitation outside the captured scope stops the run.
- **Null-safe text capture** — `sql_nullable_text()` stores SQL `NULL` instead of the
  literal string `'None'` for absent provider text. The first capture wrote `'None'` into
  `old_invitation_text` for the 49 note-less invitations; a corrective ledger write reset
  those 49 to `NULL` (nothing else touched).
- **Chunked single-transaction writer** — `execute_statements()` writes a large capture in
  256 KB chunks inside one psql session, so the 21 MB capture script cannot exhaust the
  SSH channel buffer while still committing atomically.
- **Resilient dispatcher check** — `paused_dispatchers()` retries 5× with backoff and
  reports *why* it failed (inactive vs unreadable executions), instead of failing on a
  transient n8n-lt error.
- **Deterministic ordering** — withdrawals are ordered oldest invite first, then
  invitation id, so a resumed run is repeatable.
- **Jitter on the spacing** — `delay + uniform(0, 15 % of delay)`.
- **GHL 404 tolerance** — a deleted GHL contact no longer aborts a capture; the row is
  recorded as unmatched and lands in `needs_review`.

New operational scripts (git-ignored, under `local-scripts/`): `_verify_scope_live.py`,
`_hold_impact.py`, `_state_sync_sql.py`, `_verify_capture.py`, `_check_null_handling.py`,
`_fix_null_notes.py`, `_dispatcher_exec_check.py`, `_verify_progress.py`,
`_final_campaign_state.py`, `_characterize_skipped.py`, and
`linkedin-invite-withdrawals/run_pre_cutoff_withdrawal.py` (the detached worker).

## Open risks carried forward

- **The out-of-band sender is still active.** Out-of-scope pending grew from 52 at scope
  capture to 56 by the end of the campaign; the Oct 21 bucket went 19 -> 17 (external
  acceptances) -> 23, i.e. new sends continued during the sweep window. No n8n-lt workflow
  with `users/invite` capability is active, and the vertical dispatcher recorded 0 sends,
  so the sender remains unidentified. Until it is found, treat vertical LinkedIn state as
  "0 recorded sends, 43+ externally sent invites pending".
- **Provider send dates drift** (section above). Any future date-scoped campaign must
  capture the scope and withdraw from that same capture, and must re-derive the scope
  rather than reuse an old one.
- **Ledger still overstates pending volume.** The 206 stale `requested` rows, the 235 live
  pending invites with no ledger row, and the 28 phantom `requested_pending` rows were not
  reconciled (out of scope for this campaign).
- **Re-invite plan is undecided.** 1,096 rows carry a 22-day cooldown to 2026-11-12 and
  need vertical-specific copy, subject to the account-wide 20/day, 5/hour Pacific cap.
  The 125 `needs_review` rows must stay out of any automatic re-invite.
- **All eight LinkedIn senders remain inactive** and no sender was activated. Verified at
  close: all nine invite/DM-capable workflows (`fXxw5lanZcDmUrst`, `crKIsaL5k3YBfqDZ`,
  `d0tEtijajisYcs`, `nspggypNF245xzeL`, `pq7XVajNFnnwMUTr`, `Zt8p2aYtIuY0HK18`,
  `iCnY6ccdHhfJg3sf`, `KsJ3xkDoIfXzjVDw`, `GQv0yNqDtibOXMB8`) report `active=false` and
  `activeVersionId=null`. The eight inbound/reconciliation workflows remain active as
  expected. One `running` execution remains on n8n-lt: `1177163`, the hourly
  `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) - a pre-existing reporting workflow
  with no LinkedIn side effects, not started by this campaign.

## Safety gates that held

- Only `n8n-lt` was used (direct REST with `N8N_LT_API_KEY`); the katwill MCP connector was
  not used.
- No CRM writes, no contact tags, no sends, no workflow activation, no commit.
- The out-of-scope set (Oct 14 / 20 / 21) was never captured, so it was never selectable;
  the worker additionally asserted each cycle that the out-of-scope pending count fell by
  no more than our own withdrawals.
- Every delete was individually journaled before and after, and the provider list was
  re-read after each batch to confirm no withdrawn invitation was still listed.
