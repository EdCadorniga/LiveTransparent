# LinkedIn connection-request status + withdrawal scope (2026-10-21)

> **Superseded for execution.** This scope was approved and withdrawn on 2026-10-21 —
> 1,188 invitations withdrawn, 32 skipped as already-connected, 1 already gone, 0 failures.
> See [`docs/sessions/2026-10-21-linkedin-pre-2026-10-14-withdrawal-execution.md`](2026-10-21-linkedin-pre-2026-10-14-withdrawal-execution.md).
> The read-only findings below remain the scope's provenance. Note that the provider's
> send-day values are recomputed at read time and drift daily, so the by-day tables here
> are capture-time snapshots.

Business timezone for all dates below: `America/Los_Angeles`.
Session ran 2026-10-21 10:37 PT (2026-10-21 17:37 UTC / 2026-10-22 01:37 SGT).
**Read-only session.** No workflow activated, no invitation sent or withdrawn, no CRM/contact/tag/state write, no commit.

## Ed's directive recorded in this handoff

> **Withdraw every LinkedIn connection request made prior to October 14, 2026.**

This is a **recorded intent for the next session**, not an authorization executed now.
It requires a separate explicit approval before any live `DELETE /users/invite/sent/{id}` call,
exactly like the 2026-10-12 John/mojibake withdrawal campaign.

## Numbers requested this session

### 1. Connection requests yet to be accepted

**Provider truth: 1,273 pending invitations** (Unipile Classic account `V9eiHiDpRmCtan0YNdzsQw`;
`GET {UNIPILE_API_BASE_URL}/users/invite/sent?account_id=...&limit=100` plus cursor returns pending only).

| Sent (Pacific) | Pending |
|---|---|
| 2026-03-21 | 1 |
| 2026-04-21 | 11 |
| 2026-05-21 | 10 |
| 2026-06-21 | 36 |
| 2026-08-21 | 238 |
| 2026-09-21 | 703 |
| 2026-09-30 | 117 |
| 2026-10-07 | 105 |
| 2026-10-14 | 3 |
| 2026-10-20 | 30 |
| 2026-10-21 | 19 |
| **Total** | **1,273** |

Internal ledger `linkedin_connection_state` (main, Unipile account `V9eiHiDpRmCtan0YNdzsQw`):

| `connection_status` | Rows |
|---|---|
| `ready` (queued, never sent) | 10,837 |
| `connected` | 2,500 |
| `requested` (sent, no acceptance recorded) | 1,244 |
| `follower_messaged` | 82 |
| `requested_pending` (claimed, send never confirmed) | 28 |
| `completed` | 5 |

`partnership_linkedin_connection_state`: 127 rows, all `ready`, never sent.

Reconciliation gaps (defects, not rounding):
- Only **1,038** of the 1,244 `requested` rows still exist as live pending invites. **206 ledger rows are stale** — the invite is no longer pending at LinkedIn (accepted, declined, or expired) but the ledger never reconciled it.
- **235 live pending invites have no `requested` ledger row** (identifier drift between `linkedin_provider_id` / `linkedin_public_identifier` and the provider's `invited_user_id` / `invited_user_public_id`).
- The 28 `requested_pending` rows never produced a live invite.
- The 206 John/mojibake invitations withdrawn on 2026-10-12 are **confirmed gone** from the provider (0 of them appear in the 1,273). No overlap between the already-withdrawn set and the new scope.

### 2. Vertical connection-request status

**Our vertical LinkedIn machinery has sent zero connection requests.**

| Vertical | Queued (`lt_li_vertical_queue`) | Live pending invites | Queue-recorded sends | Accepted | DMs sent |
|---|---|---|---|---|---|
| Alcohol | 167 | 6 | 0 | 0 | 0 |
| Cannabis | 29 | 0 | 0 | 0 | 0 |
| Cannabis Dispensaries | 90 | 2 | 0 | 0 | 0 |
| Crypto | 292 | 0 | 0 | 0 | 0 |
| Gambling | 246 | 0 | 0 | 0 | 0 |
| Mushroom | 115 | 1 | 0 | 0 | 0 |
| Nicotine | 700 | 14 | 0 | 0 | 0 |
| Peptides | 129 | 20 | 0 | 0 | 0 |
| **Total** | **1,768** | **43** | **0** | **0** | **0** |

Evidence that zero vertical sends occurred:
- `LT - Vertical LinkedIn Connection Dispatcher` (`KsJ3xkDoIfXzjVDw`): `active=false`, `activeVersionId=null`, 0 executions, updated 2026-10-15T15:42:19Z.
- `LT - Vertical LinkedIn Sales Navigator DM Sequence` (`GQv0yNqDtibOXMB8`): `active=false`, `activeVersionId=null`, 0 executions, updated 2026-10-15T15:42:21Z.
- `lt_li_vertical_queue`: all 1,768 rows `status='ready'`, `invite_sent_at` NULL, `accepted_at` NULL, `dm_step` NULL, `reason` NULL, `provider_id` empty.
- `lt_li_outbound_attempts`: 0 rows. `lt_li_vertical_control`: `sent=0`, `failed=false`, `paused=false` (single row, 2026-10-15 15:42:07 UTC).
- `linkedin_activity_events`: 156 `connection_request_sent`, 70 `dm_sent`, 36 `connection_accepted`, 27 `reply_received` — **0** of them belong to a vertical-queue contact.

### 3. All LinkedIn senders are currently OFF

| Workflow | ID | Active | Last updated |
|---|---|---|---|
| LT - GHL LinkedIn Connect Dispatcher | `fXxw5lanZcDmUrst` | false | 2026-10-02T03:39:25Z |
| LT - Partnership LinkedIn Dispatcher | `crKIsaL5k3YBfqDZ` | false | 2026-10-01T14:48:59Z |
| LT - LinkedIn DM Sequence (Unipile) | `d0tEtijajisIsYcs` | false | 2026-10-01T14:49:36Z |
| LT - Partnership LinkedIn DM Sequence | `nspggypNF245xzeL` | false | 2026-10-01T14:49:39Z |
| LT - LinkedIn Follower DM Sequence | `pq7XVajNFnnwMUTr` | false | 2026-09-10T02:03:15Z |
| LT - LinkedIn Connection Request (Internal Test) | `Zt8p2aYtIuY0HK18` | false | 2026-07-15T18:13:28Z |
| LT - Instagram DM Sequence (Unipile) | `iCnY6ccdHhfJg3sf` | false | 2026-07-15T16:52:17Z |

These are the only n8n-lt workflows whose nodes can call `users/invite` (scan across all 212 workflows):
`fXxw5lanZcDmUrst`, `crKIsaL5k3YBfqDZ`, `Zt8p2aYtIuY0HK18`, `KsJ3xkDoIfXzjVDw`, `GQv0yNqDtibOXMB8`.
The other three in the table above (`d0tEtijajisIsYcs`, `nspggypNF245xzeL`, `pq7XVajNFnnwMUTr`) plus
`iCnY6ccdHhfJg3sf` send DMs only, and are listed because they are also LinkedIn senders that must stay off.
Only inbound/reconciliation workflows remain active: Acceptance Checker `3ttEvr5NMcQCS4Hp`, State Sync
`ceaKnz6E3onQrZpt`, Reply Backfill `QfJ2EZcc7lZwNgxj`, Connected Tag Sync `rcvTMprJKga9aEJ6`, Relations Backfill
`VPiHfBwzOHaJnHBY`, New Messages `7o5EBdvwAuIaWW7k`, State Upsert `Old7ZvyVYgFaJgDr`, DM Suppression
`IPN8jnR3XSurX0o1`. None of these send invitations.

## Open risk discovered this session (source not yet identified)

**52 connection requests went out on 2026-10-14, 2026-10-20 and 2026-10-21 that our ledger did not record.**

- Batch sizes: Oct 14 = 3, Oct 20 = 30, Oct 21 = 19, all at roughly 17:25-17:27 UTC (10:25-10:27 PT).
- All 52 carried **no connection note** (`invitation_text` null).
- 43 of them target contacts that are in the vertical queue (Alcohol 6, Cannabis Dispensaries 2, Mushroom 1, Nicotine 14, Peptides 20).
- None of the 43 has a `linkedin_connection_state` row, and none of the sampled GHL contacts carries the `linkedin_connection_requested` tag (only the vertical `lt_campaign_*_enroll` tag).
- `lt_li_outbound_attempts` is empty and `lt_li_vertical_control` shows 0 sent, so the vertical dispatcher did **not** send them.
- No n8n-lt workflow capable of calling `users/invite` is active.

Conclusion: these were sent **out-of-band**, outside the tracked n8n-lt workflows and outside the GHL-tagged
dispatcher path. The source is unidentified. Do not assume our own automation sent them. The next session should
identify the sender before drawing conclusions about vertical outreach state.

Mitigation already built in: the vertical dispatcher reads the provider's full pending list before every send and
marks such rows `reason='provider_pending'`, and folds any external invite younger than 48 hours into
`lt_li_outbound_attempts` (`source='provider_readback'`) so it consumes the 20/day, 5/hour Pacific budget.
Enabling it later therefore will not double-invite those 43 contacts.

## Withdrawal scope (computed, not executed)

Snapshot captured at `local-scripts/linkedin-withdrawal-scope-pre-2026-10-14.json` (git-ignored).

- **In scope (sent strictly before 2026-10-14): 1,221 pending invitations.**
  - 1,172 carry the Cameron connection note; 49 carry no note.
  - By send day: Mar 21 = 1, Apr 21 = 11, May 21 = 10, Jun 21 = 36, Aug 21 = 238, Sep 21 = 703, Sep 30 = 117, Oct 7 = 105.
  - 2 of the 1,221 are vertical contacts: David Spreckman (Cannabis Dispensaries, sent 2026-10-07) and Lauren Fontein (Cannabis Dispensaries, sent 2026-09-30).
  - 0 of the 1,221 appear in `linkedin_invitation_withdrawals` — no overlap with the 206 already withdrawn.
- **Out of scope (sent on or after 2026-10-14): 52** — Oct 14 = 3, Oct 20 = 30, Oct 21 = 19. These are the live activity and must not be withdrawn.

## Ordered next steps for the next session

1. **Get explicit written approval for the withdrawal** of the 1,221 pre-2026-10-14 invitations. The directive in this document is an intent, not an approval to execute DELETEs.
2. **Extend `scripts/linkedin/plan_john_invite_withdrawals.py` with a date scope filter.** As written, `issue_of()` only flags `john_note` and `mojibake`, so the tool cannot select the current scope. Add an explicit `--before-date` / `--scope-before` option (default off) that selects by `parsed_datetime`, keeping the existing note-based modes intact. Alternative: drive the withdrawal from the scope snapshot — but the durable ledger must still be the source of truth.
3. **Capture into the durable ledger before withdrawing.** Use `capture` mode so every target lands in `linkedin_invitation_withdrawals` with `unipile_account_id`, `invitation_id`, `invited_user_public_id`, `ghl_contact_id`, `old_invitation_text`, `old_invitation_sent_at`, `issue`, `cooldown_until` (22 days), `reinvite_status`, `dispatcher_hold=true`, plus a raw snapshot path and SHA. The existing `lt_invitation_withdrawal_hold` trigger then blocks `ready` / `requested_pending` queue entries for held contacts. Re-read the ledger afterwards to confirm every scoped invitation is present.
4. **Withdraw with Ed's recorded pacing.** `DELETE {UNIPILE_API_BASE_URL}/users/invite/sent/{invitation_id}?account_id=...`, `--delay 30` seconds between individual withdrawals, `--limit` batch cap, 10-minute pause between batches. 1,221 invitations at 30-second spacing is roughly 10.2 hours of provider calls — this needs a resumable, durable-ledger-driven worker, not a single foreground run. Keep the machine awake.
5. **Fail closed on uncertainty.** On `account_restricted` / `too_many_requests` / timeout, stop the batch and record the outcome; never blind-retry a DELETE whose result is unknown. A provider-side withdrawal caused by acceptance is an `already_gone` outcome, not an error.
6. **Do not disturb the 52 post-2026-10-14 invitations.** Verify the scope filter by re-reading the provider pending list before and after each batch, confirming the remaining count moves from 1,273 down by exactly the number withdrawn and that the 52 stay pending.
7. **Reconcile the 206 stale `requested` rows** after the withdrawal sweep: for each row whose invitation is no longer pending at the provider, move it out of `requested` (to `connected` where an acceptance was recorded, otherwise a terminal closed state) so the ledger stops overstating pending volume.
8. **Reconcile the 235 live pending invites with no ledger row**, and the 28 `requested_pending` rows that never produced an invite, using the same provider readback.
9. **Decide the re-invite plan for the full withdrawn population.** The existing 191 `pending` + 15 `needs_review` rows carry `cooldown_until = 2026-11-03`. The new 1,221 will carry their own 22-day cooldown from their withdrawal date. Re-invite copy must be vertical-specific (existing rule: Cannabis Brands note when `Vertical` is blank) and must respect the account-wide **20/day, 5/hour Pacific** caps, which include re-invites.
10. **Keep every LinkedIn sender inactive.** `fXxw5lanZcDmUrst`, `crKIsaL5k3YBfqDZ`, `d0tEtijajisIsYcs`, `nspggypNF245xzeL`, `pq7XVajNFnnwMUTr`, `Zt8p2aYtIuY0HK18`, `KsJ3xkDoIfXzjVDw`, `GQv0yNqDtibOXMB8` stay `active=false` until separately authorized.
11. **Identify the out-of-band sender** of the 52 note-less Oct 14/20/21 invites before treating the vertical LinkedIn program as having a clean zero-send baseline.
12. **The 2 withdrawn vertical contacts** (David Spreckman, Lauren Fontein) become eligible again once withdrawn, because the vertical dispatcher skips only on `provider_pending`. Keep the vertical dispatcher inactive until the withdrawal sweep completes and Ed decides the re-invite order.
13. **Do not run the report-side backlog from the 2026-10-19 EOS handoff** unless Ed reprioritises it; the LinkedIn withdrawal directive is the current priority.

## Known defects and risks carried forward

- **Ledger overstates pending volume.** 206 stale `requested` rows plus 28 `requested_pending` rows with no live invite; 235 live pending invites with no ledger row. The provider count (1,273) is authoritative; the ledger (1,272) currently matches it only by coincidence.
- **Out-of-band invites are untracked.** 52 note-less invites (Oct 14/20/21) bypassed our ledgers and GHL tags. Until the sender is identified, treat vertical outbound state as "0 recorded sends, 43 externally sent invites pending", not a clean zero.
- **Provider account-restriction history.** A LinkedIn sending restriction was observed in late August 2026 (cleared 2026-08-31). A 1,221-invitation DELETE campaign is a large volume of account-level provider calls and must be paced, resumable, and stop on restriction.
- **Withdrawal destroys the only copy of the connection note for 1,172 invitations.** The note text and the invite snapshot must be captured into the ledger *before* any DELETE, with the local snapshot and SHA kept.
- **Identity ambiguity.** The 2026-10-12 campaign left 15 contacts in `reinvite_status='needs_review'` because two GHL contacts matched the same LinkedIn identity. The new 1,221 are not identity-resolved yet; expect a similar `needs_review` bucket and keep it out of any automatic re-invite.

## Safety gates

- Use only `n8n-lt`; never another n8n tenant.
- **No live invitation withdrawal until Ed gives explicit approval for this specific campaign.** This document records intent only.
- **No LinkedIn sender activation.** All eight send-capable workflows stay `active=false`.
- No CRM writes, sends, enrollments, contact tagging, or state mutations without explicit approval.
- Never print or commit PITs, API keys, webhook secrets, JWTs, Unipile keys, or database passwords.
- Fail closed on provider uncertainty; never blind-retry a DELETE.

## Audit artifacts

Read-only scripts written this session under git-ignored `local-scripts/`:

| File | Purpose |
|---|---|
| `_count_pending_invites.py` | Provider pending-invite count |
| `_analyze_pending_invites.py` | Note/day breakdown of provider pending invites |
| `_profile_invites.py` | Relative `date` vs `parsed_datetime` semantics check |
| `_reconcile_pending.py` | Provider pending vs ledger reconciliation |
| `_char_unmatched.py` | Characterization of unmatched provider invites |
| `_recent_batches.py` | Recent (post-2026-10-14) batch profile and vertical overlap |
| `_crosscheck_withdrawals.py` | Pending invites vs the 206 already-withdrawn ledger rows |
| `_per_vertical_status.py` | Per-vertical pending / sent / accepted / DM table |
| `_linkedin_state_check.py` | n8n-lt activation state for every LinkedIn workflow |
| `_inspect_vertical_wf.py` | Vertical workflow node/schedule/execution inspection |
| `_vert_code.py` | Vertical dispatcher persistence + invite logic extraction |
| `_find_invite_senders.py` | Scan all 212 n8n-lt workflows for `users/invite` capability |
| `_exec_window.py` | n8n-lt execution window scan around the invite batch times |
| `_ghl_invite_targets.py` | GHL readback of recent invite targets |
| `_ghl_tag_check.py` | GHL tag readback for vertical contacts with pending invites |
| `_scope_withdrawal.py` | Computes and snapshots the pre-2026-10-14 withdrawal scope |

Scope snapshot: `local-scripts/linkedin-withdrawal-scope-pre-2026-10-14.json`
(`cutoff`, `captured_at_utc`, `account_id`, `in_scope_count`, `out_of_scope_count`, and per-invitation rows).
