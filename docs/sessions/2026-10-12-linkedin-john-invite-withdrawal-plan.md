# 2026-10-12 — LinkedIn "John" connection-request withdrawal: recon + data-preservation plan

## Objective
Withdraw every **still-pending** LinkedIn connection request whose invite note contains
"John" (the old internal-test template `Hey {{first}} — quick connect. John here with
Transparent eCom.`), **preserve the contact data durably**, and later re-invite the same
people with the correct per-vertical note. Ed's re-invite rule: use the **Cannabis Brands**
note when `Vertical` is blank.

**Latest continuation (Oct 13 local / Oct 12 UTC): capture completed; 30 withdrawals verified;
paced worker RUNNING for the remaining 176 at the last readback.** See the authorized-run
continuation at the end. Earlier no-write checkpoints below are historical.

## Verified Unipile API capability (official docs + live test)
- **List pending sent invitations** (Classic account, header `X-API-KEY`):
  `GET {UNIPILE_API_BASE_URL}/users/invite/sent?account_id=<acct>&limit=100&cursor=...`
  Returns `InvitationList.items[]`, each with `id`, `invited_user`, `invited_user_id`,
  `invited_user_public_id`, **`invitation_text`** (the connection note), `date`,
  `parsed_datetime`, `inviter`, `specifics.provider=LINKEDIN`. **Returns only PENDING
  invitations**, so accepted invites are excluded automatically.
  - ⚠️ Live limit cap is **100** (the docs say 1–250; `limit=250` returns HTTP 400).
- **Withdraw an invitation:** `DELETE {base}/users/invite/sent/{invitation_id}?account_id=<acct>`
  → `{ "object": "InvitationCanceled" }`.
- v2 equivalent exists (`/v2/{acc_...}/users/me/relation-requests?type=sent` +
  `.../{request_id}/cancel`) but the John invites were sent on the **Classic** account
  (`V9eiHiDpRmCtan0YNdzsQw`), so v1 endpoints are the target.

## Recon findings (read-only)
- **1,444 pending invitations** total on the Classic account.
- **153 match "john here"** → the John withdrawal set. Note text is
  `Hey <First> — quick connect. John here with Transparent eCom.`
- **53 additional pending invites are garbled/mojibake** — `Hi {first_name}, I'm "ameron
  co-fo'nder of Transparent e"om.` (the 2026-08-18 double-escape corruption). Separate defect,
  still pending. Decide whether to include them in the same cleanup.
- 150 of the 153 John invites resolve to a GHL contact; **all 150 have `Vertical = Cannabis`**
  (0 blank, 0 other). 3 do **not** resolve (accented slugs):
  `bethlthomas`, `catherine-ram?rez-foss`, `esteban-gonz?lez-011231119`.
- Confirmed GHL custom field `ODs8fBt5te5HEfSJ91pY` = **"Vertical"** (SINGLE_OPTIONS:
  Alcohol, Cannabis, Cannabis Dispensaries, Crypto, Gambling, Mushroom, Nicotine, Peptides).

### The "correct" per-vertical Day-0 connection notes (source: `New Campaigns October 2026/*.pdf`)
Each vertical PDF has a **Day 0 · LinkedIn Connect** note. These are the corrected messages:

| Vertical | Note |
|---|---|
| Alcohol | `Hi {first_name} - I help alcohol and spirits brands run compliant Meta/Google ads without the disapprovals and account limits. Would love to connect.` |
| Cannabis | `Hi {first_name} - I work with cannabis brands on compliant Meta/Google ads and in-store attribution. Would love to connect.` |
| Cannabis Dispensaries | `Hi {first_name} - I work with dispensaries on bringing in brand-funded ad budgets and verified foot-traffic attribution. Would love to connect.` |
| Crypto | `Hi {first_name} - I help crypto and fintech apps run compliant Meta/Google campaigns that don't get banned mid-scale. Would love to connect.` |
| Gambling | `Hi {first_name} - I help gambling and gaming brands run compliant Meta/Google campaigns that don't get banned mid-scale. Would love to connect.` |
| Mushroom | `Hi {first_name} - I help mushroom and functional-wellness brands run compliant Meta/Google ads without the disapprovals. Would love to connect.` |
| Nicotine | `Hi {first_name} - I help nicotine brands run compliant Meta/Google ads through the right account setup. Would love to connect.` |
| Peptides | `Hi {first_name} - I help peptide brands run compliant ads on Meta/Google without the constant account shutdowns. Would love to connect.` |

## Artifacts produced this session
- `scripts/linkedin/list_john_pending_invites.py` — paginates `GET /users/invite/sent`,
  filters by note substring (default `"john here"`), writes a review CSV. Read-only.
- `scripts/linkedin/enrich_john_invites_vertical.py` — resolves each `invited_user_public_id`
  → GHL contact + `Vertical`. Read-only. (Committed by another process in HEAD `5613544`;
  this session did not run `git commit`.)
- Untracked (gitignored) snapshots:
  - `local-scripts/john_pending_invites_review.csv` — 153 invitation rows.
  - `local-scripts/john_pending_invites_vertical_review.csv` — 153 rows + resolved
    `ghl_contact_id`, `connection_status`, `vertical`.
- Extraction helper (temp, not committed): vertical-PDF→text extraction used to read the
  Day-0 notes.

## Original recon checkpoint — subsequently updated below
- **`scripts/linkedin/plan_john_invite_withdrawals.py` was never created** (the write was cut
  off). No capture tool, no ledger, no withdrawal.
- No Postgres ledger table exists yet.
- No invitations withdrawn; no one has been re-invited.

## Data-preservation plan (designed, not yet built)
Goal: capture a full snapshot of every flagged invite **before** withdrawing and drive the
later re-invite from a durable ledger, so nothing depends on the Unipile list still containing
the row afterwards.

1. **Postgres ledger** `linkedin_invitation_withdrawals` (VPS `postgres` DB), the source of
   truth + re-invite queue. Columns: `unipile_account_id`, `invitation_id` (UNIQUE together),
   `invited_user`, `invited_user_public_id`, `invited_user_provider_id`, `ghl_contact_id`,
   `first_name`, `vertical`, `linkedin_profile_url`, `old_invitation_text`,
   `old_invitation_sent_at`, `issue` (`john_note`|`mojibake`), `withdraw_status`
   (`pending|withdrawn|already_gone|failed|skipped`), `withdraw_http_status`, `withdrawn_at`,
   `cooldown_until`, `reinvite_status` (`pending|sent|failed|skipped|needs_review`),
   `reinvite_message`, `reinvite_invitation_id`, `reinvited_at`, `last_error`,
   `raw_invitation` jsonb, `raw_ghl_contact` jsonb, `created_at`, `updated_at`.
2. **Immutable local snapshot**: CSV + full raw Unipile/GHL JSON dump in `local-scripts/`.
3. **`linkedin_connection_state`**: set withdrawn contacts' `request_sent_at = now()` (restart
   the existing 30-day rule) and merge `payload_json.invite_withdrawn/reinvite_due`; never
   downgrade `connected` rows.
4. **Flow**: capture (before any DELETE) → withdraw batched (fail-closed on
   `account_restricted`/`too_many_requests`) → set `cooldown_until` → after cooldown re-invite
   from the ledger (re-check not-connected + not-suppressed; record new invitation id).

## Key risks / blockers
- **The live dispatcher is NOT vertical-aware.** `LT - GHL LinkedIn Connect Dispatcher`
  (`fXxw5lanZcDmUrst`) sends a single generic Cameron copy. If withdrawn contacts are left in a
  state the dispatcher selects (`ready`, `request_sent_at > 30d`), it will **re-invite them
  with the wrong copy and risk a double invite**. The re-invite must be ledger-driven (or the
  dispatcher made vertical-aware), and withdrawn contacts must be held out of the dispatcher's
  selection until the correct re-invite runs.
- **Live withdrawal is on Cameron's real LinkedIn account** — batch with delays and stop on any
  restriction error.
- The 3 unmatched contacts and the accented slugs must not be lost (store raw JSON; mark
  `needs_review`).
- 30-day cooldown is the house rule (`request_sent_at < NOW() - INTERVAL '30 days'`), used as
  the default pending Ed's confirmation.

## Open decisions (need Ed)
1. Cooldown length (default **30 days**).
2. Re-invite message: for the 150 `Vertical=Cannabis` use the **Cannabis Brands** note (blank/
   unknown also → Cannabis Brands note). Confirm; define behavior for other verticals.
3. Include the **53 mojibake** invites in the same ledger/withdrawal run?
4. Re-invite owner: ledger-driven script (recommended) vs making the dispatcher vertical-aware.
5. The 3 unmatched contacts: withdraw + hold `needs_review`, or skip.

## Ordered next steps
1. Build `scripts/linkedin/plan_john_invite_withdrawals.py` (modes: `report` default read-only,
   `capture` = create table + upsert ledger, `withdraw --yes` = live DELETEs + mark ledger).
2. Run `report`; confirm the 153-row snapshot + the re-invite-message mapping.
3. Run `capture`; back up the ledger + raw JSON locally.
4. Run `withdraw` batched (fail-closed), then set `cooldown_until` and the
   `linkedin_connection_state` anchor.
5. Build the ledger-driven re-invite (per-vertical note) to run after cooldown; keep the
   generic dispatcher from touching these contacts in the meantime.

## Safety gates (in force)
- Live LinkedIn sends/writes are approval-gated. Withdrawal is a live write — dry-run first.
- Use only the Classic Unipile account `V9eiHiDpRmCtan0YNdzsQw`; only `n8n-lt` for n8n.
- Never print/commit the Unipile token, GHL PIT, Postgres password, or n8n key.
- `repomix` refresh remains paused by Ed.

## Worktree state
- Branch `codex/social-outreach-sync`; HEAD `5613544` (already contains the two recon scripts;
  not committed by this session).
- Unrelated pre-existing/concurrent changes present and untouched: modified Executive-V1 SQL +
  `scripts/reconcile_v1_band1_opportunities.py`, plus untracked `scripts/patch_v1_band1_facts.py`
   and two "New Campaigns October 2026/GHL Import Prep" CSVs.

## Continuation — tool built and read-only verification (2026-10-12 15:29 UTC)

### Deliverables and fresh findings
- Added `scripts/linkedin/plan_john_invite_withdrawals.py` and its isolated test suite
  `scripts/linkedin/test_plan_john_invite_withdrawals.py`.
- Fresh live report: **1,444 pending / 153 John-note / 53 mojibake**. Default scope is John only.
- Live resolution now checks both the shared profile index and Classic connection state,
  using **slug OR provider ID**, and refuses to arbitrarily choose among duplicate contacts.
  The three originally unmatched profiles resolve through provider identity. **146 invites
  have a unique Cannabis contact; seven invites each match two GHL contacts** and are held
  `needs_review`. Both candidate GHL JSON records are preserved for each ambiguous profile.
- Ambiguous profile slugs: `cheryl-king-4074949`, `alex-gerard-7a204b174`, `laiah-walsh`,
  `anna-walters-60a339324`, `ginette-masse-489697268`, `atom-taro-85724a6`,
  `manav-singh-toronto`. Do not merge/select a contact without reviewing these identities.
- Immutable local report: `local-scripts/linkedin-invite-withdrawals/report-20261012T152948Z-7827d621.json`
  and sibling `.csv`. JSON contains full Unipile invitations, full matched GHL payloads,
  candidate IDs, and matched original connection-state rows. This is a **report snapshot**,
  not an authorized or committed database capture.
- First report stopped on GHL HTTP 429 without accepting a snapshot. Added bounded read-only
  retries (four attempts, 2/4/6-second backoff) and 250ms contact pacing; second report completed.

### Modes and preservation contract
```powershell
# Fresh remote reads + new local JSON/CSV, no remote writes:
python scripts/linkedin/plan_john_invite_withdrawals.py report

# Offline summary of an existing snapshot:
python scripts/linkedin/plan_john_invite_withdrawals.py report --snapshot "<report.json>"

# After scope/policy approval: fresh preservation snapshot + ledger + database hold:
python scripts/linkedin/plan_john_invite_withdrawals.py capture --cooldown-days 30 --reinvite-owner ledger-script
# Add --include-mojibake ONLY if Ed chooses that scope.

# Read-only withdrawal preview using the ORIGINAL capture JSON:
python scripts/linkedin/plan_john_invite_withdrawals.py withdraw --snapshot "<capture.json>" --limit 10

# Separately authorized live batch; default 2-second inter-DELETE delay:
python scripts/linkedin/plan_john_invite_withdrawals.py withdraw --snapshot "<capture.json>" --yes --limit 10
```
- `capture` creates `linkedin_invitation_withdrawals`, inserts missing records idempotently,
  preserves prior raw snapshots/statuses on conflict, and writes a full local ledger readback
  to `.ledger.json`. It records the original snapshot path and SHA-256. Repeated capture does
  **not** replace an earlier record: use that record's original capture snapshot to withdraw.
- Capture policy defaults: 30-day cooldown, John only, future ledger-script re-invite.
  These remain **proposed defaults pending Ed**, not settled decisions.
- `reinvite_message` is the per-vertical **template** with `{first_name}` retained. Blank
  vertical uses Cannabis; unsupported vertical/absent first name/ambiguous identity is review-only.
  A future sender must refresh the authoritative provider first name, recheck vertical,
  suppression and connection status, render and validate ASCII before sending.
- No re-invite sender is built or activated by this tool. The owner field records the planned
  owner; choosing `vertical-dispatcher` does not implement vertical-aware dispatch.

### Durable dispatcher hold and withdrawal behavior
- Capture installs a `lt_invitation_withdrawal_hold` database trigger on **both**
  `linkedin_connection_state` and `partnership_linkedin_connection_state`. An attempted
  `ready`/`requested_pending` INSERT/UPDATE matching a held account+contact/candidate-contact/
  slug/provider identity raises an error, preventing automated queue entry/claim.
- The hold remains true indefinitely, independent of `cooldown_until`. It is intentionally
  **not** an automatic 30-day release. If an operator later enables an old dispatcher and
  selects a held identity, the queue operation may fail for the whole batch. This is the
  deliberate fail-closed tradeoff; integrate a ledger exclusion before resuming that dispatcher.
- Capture/live batches verify the three known invite senders are unpublished on **n8n-lt**
  and their recent execution lists show no queued/running/waiting/unknown run. No n8n workflow
  mutation is performed. Already-running senders must be reconciled before capture.
- Withdrawal preview/live requires captured rows, the original snapshot checksum/path,
  enabled guards on both queues, and a fresh complete pending list. Each live invite's ID,
  note and target identity must still match; connected/terminal state is skipped for review.
- Every DELETE has a local fsynced intent journal and atomic ledger `pending → withdrawing`
  claim first. Confirmed `InvitationCanceled` records `withdrawn`, timestamps/cooldown, and
  resets matching nonterminal state `request_sent_at=now()` plus payload hold/due markers.
  Existing `connected`/`completed` rows are preserved.
- Any nonconfirmation—including restriction, 429, 404, timeout or malformed success—halts
  the batch with the hold retained. No DELETE retry occurs. Uncertain results are stored
  `uncertain`/`needs_review`; a crash after claim can leave `withdrawing`. Neither status is
  automatically selected again: reconcile provider state and the journal before manual recovery.
- Already absent invites are `already_gone`/`needs_review`, without inventing a withdrawal
  timestamp or treating disappearance as proof of withdrawal. Confirmed cancellations receive
  final provider-list readback. If database finalization fails after a confirmed cancellation,
  the local journal is recovery evidence and the claim remains non-replayable.

### Verification and remaining approval boundary
- `python -m unittest discover -s scripts/linkedin -p test_plan_john_invite_withdrawals.py -v`:
  **17/17 PASS**. Tests cover dry-run no-write behavior, pagination refusal, identity ambiguity,
  raw preservation/idempotent capture SQL, checksum and missing-hold refusal, successful
  cancellation, restriction/network uncertainty without replay, and terminal-state preservation.
- These use mocked remote/database calls: **live ledger DDL, trigger runtime, capture and
  DELETE behavior are not yet integration-accepted**. First authorized capture needs fresh
  schema/guard/ledger readback and the withdrawal preview before any live batch.
- No capture, database hold installation, state write, GHL write, live DELETE, re-invite,
  n8n mutation, commit, or push occurred in this continuation. Secrets remain runtime-only;
  snapshots/journals are Git-ignored under `local-scripts/`.
- Next decisions for Ed: cooldown; include 53 mojibake or John-only; ledger-script vs
  vertical-aware dispatcher ownership. Keep the seven ambiguous records review-only for
  re-invites. Scope/policy confirmation and live-withdrawal approval are distinct.

## Handoff prompt for the next LLM (copy-ready)

**Use the latest policy update below rather than the original prompt's 30-day/John-only defaults.**

> Continue the LiveTransparent LinkedIn "John" invite cleanup. Context: the old internal-test
> template `Hey {{first}} — quick connect. John here with Transparent eCom.` was sent via
> Unipile Classic account `V9eiHiDpRmCtan0YNdzsQw`; read
> `docs/sessions/2026-10-12-linkedin-john-invite-withdrawal-plan.md` first.
> Recon is done (read-only): `GET {UNIPILE_API_BASE_URL}/users/invite/sent?account_id=...&limit=100`
> returns **pending** invites with `invitation_text`; **153** match "john here" (plus **53**
> mojibake `"ameron co-fo'nder"` pending invites). `DELETE /users/invite/sent/{id}?account_id=...`
> withdraws. 150/153 resolve to GHL contacts, **all `Vertical=Cannabis`**; 3 accented slugs do not
> resolve. Scripts already exist and work: `scripts/linkedin/list_john_pending_invites.py`,
> `scripts/linkedin/enrich_john_invites_vertical.py`; snapshots in `local-scripts/`.
> TODO: build `scripts/linkedin/plan_john_invite_withdrawals.py` (default read-only `report`;
> `capture` = create Postgres ledger `linkedin_invitation_withdrawals` + upsert + local raw-JSON
> backup; `withdraw --yes` = batched live DELETEs, fail-closed on account restriction, then set
> `cooldown_until` and `linkedin_connection_state.request_sent_at = now()`). Preserve every
> contact (raw Unipile + GHL JSON); 3 unmatched → `needs_review`. Re-invite later with the correct
> per-vertical note (Cannabis Brands note for `Vertical=Cannabis`/blank); the current dispatcher
> `fXxw5lanZcDmUrst` is NOT vertical-aware and must not re-invite these people in the meantime.
> Confirm with Ed: cooldown (default 30d), include the 53 mojibake invites?, re-invite owner.
> Safety: dry-run first; live withdrawal is approval-gated; never print/commit secrets; use only
> the Classic account and only `n8n-lt`.

## Policy update and combined read-only report — 2026-10-12 15:53 UTC

- Ed chose **John plus mojibake** and requested checking LinkedIn's documented wait, then
  using **three weeks plus one day**. Official LinkedIn Help says: “You won’t be able to send
  a new invitation to the same member for up to three weeks.” Source:
  [Withdraw an invitation](https://www.linkedin.com/help/linkedin/answer/a568295/withdraw-an-invitation?lang=en).
  Retrieved directly after an official-source search. The tool default is now **22 days**.
- Ed reiterated: check each contact's `Vertical`; a blank field uses the **Cannabis Brands**
  connection note. This confirms the copy rule, not whether a ledger script or vertical-aware
  dispatcher will own the later send. CLI re-invite owner now defaults to `undecided`.
- Ran `python scripts/linkedin/plan_john_invite_withdrawals.py report --include-mojibake --cooldown-days 22`.
  **1,444 pending; 206 selected = 153 John + 53 mojibake.** **191 unique Cannabis matches**;
  **15 profiles match two GHL records each**, both `Vertical=Cannabis` on every ambiguous
  profile. All matched records have Cannabis; no unmatched profile or uniquely blank/other
  vertical was found. The 15 ambiguous identities stay `needs_review` for re-invites, even
  though their two candidate records agree on copy.
- The eight additional mojibake ambiguities are `steven-leung-90708521`,
  `jed-mcwhorter-b4ba13a8`, `nikhitanair6`, `eilishboydmkt`, `domalley`,
  `brian-jones-643964171`, `dereck-reyes-b1183a149`, `gregorycookgalexan`.
- Latest full report JSON/CSV:
  `local-scripts/linkedin-invite-withdrawals/report-20261012T155354Z-9ac1b368.json`
  and sibling `.csv`. The JSON now also records `candidate_verticals` explicitly.
- Next authorized capture command must include `--include-mojibake --cooldown-days 22`.
  Add `--reinvite-owner ledger-script|vertical-dispatcher` only after that implementation owner
  is chosen; leaving it `undecided` does not prevent preserving/withdrawing invitations.
- **Policy choices did not authorize remote writes:** no capture, guard installation,
  withdrawal, re-invite, CRM write, or n8n mutation was performed. Ask Ed to authorize the
  capture and first bounded withdrawal batch before those operations. Re-invites remain a
   future separately authorized implementation, with live vertical/identity/suppression checks.

## Authorized capture and paced withdrawal — 2026-10-13 local / 2026-10-12 UTC

- Ed authorized capture and first 10, then before the first live batch completed expanded
  authorization to **30 per 10 minutes until all captured defective invitations are handled**.
  Official LinkedIn withdrawal Help does not publish a numeric daily withdrawal cap. Absence
  of a published cap does not establish unlimited allowance. Stop-on-restriction remains active.
- Capture succeeded for **206 (153 John / 53 mojibake)**, with **191 unique Cannabis matches
  and 15 duplicate-contact ambiguities**. Both candidate records remain preserved; ambiguous
  identities remain `needs_review` for future re-invites.
- Original capture (required for every subsequent withdrawal):
  `local-scripts/linkedin-invite-withdrawals/capture-20261012T160619Z-72182cff.json`.
  Sibling `.csv` and `.ledger.json` preserve full captured/ledger records.
- Live ledger readback verified all 206 held, cooldown policy 22 days. Enabled triggers on
  both main/partnership tables were runtime-tested with nested exception rollback probes:
  each rejected `ready` writes for held identities with the expected error; no probe persisted.
- First capture attempt exceeded terminal wait before producing a snapshot; retry succeeded.
  The first 30-row withdrawal command exceeded terminal wait after **18 confirmed withdrawals**.
  Process absence and ledger status were checked before continuation; no uncertain/withdrawing
  rows remained. A provider readback verified those 18 absent before another DELETE.
- Detached worker `local-scripts/linkedin-invite-withdrawals/run_authorized_cleanup.py`
  completed the remaining 12 in that first allowance. **At 16:18 UTC: 30 withdrawn, 176 pending**;
  provider readback passed and ledger contains no failed/uncertain/withdrawing rows. Holds remain
  enabled on all 206. Earliest withdrawal 16:09:37 UTC; latest current cooldown Nov 3 16:17:42 UTC.
- Worker launch PID **42448**, still running at the last process check. It limits each batch to
  30, checks withdrawals in the rolling previous 600 seconds, waits **602 seconds after each
  completed batch**, verifies previous withdrawals absent and known senders paused/quiescent,
  and stops on any batch error or unresolved ledger status. Each child has a 900-second timeout;
  timeout halts the driver and requires journal/ledger reconciliation before any restart.
  Loop bounded at 20 iterations. No automatic replays of uncertain/claimed rows.
- Local status: `local-scripts/linkedin-invite-withdrawals/authorized-cleanup-status.json`.
  Output log: sibling `authorized-cleanup.log`. Last status `waiting`, next batch
  **2026-10-12T16:28:27Z**, remaining 176. This is an ongoing run, **not complete**.
  Machine/process must remain running. Before any restart, check process, status file, journals,
  ledger statuses and provider pending list. Never launch concurrent workers.
- No re-invites, contact writes, workflow mutations or commits. Re-invite owner undecided;
  holds remain indefinite and require deliberate later integration/release.
- Next: inspect completion or halt status, reconcile exact ledger totals with provider list,
  and update this handoff only after final readback. Remaining expected total pending after
  successful cleanup is 1,238 absent unrelated acceptance/new-invite activity.

### Pacing update — Oct 12 17:11 UTC / Oct 13 local

- Ed requested **30-second delay per withdrawal**; keep up to 30 per batch with a
  602-second pause after each completed batch. The slower delay means a full batch takes
  at least 15 minutes plus API/readback overhead, followed by the existing pause.
- Stopped PID 42448 while status was `waiting`; process inspection confirmed no withdrawal
  child running. Fresh ledger read: **120 withdrawn / 86 pending**, all held, 22-day policy,
  no failed/uncertain/withdrawing rows. Both hold rollback probes passed again.
- Changed CLI delay default to 30 seconds and worker child argument to `--delay 30`;
  child timeout now **1800 seconds**, replacing 900 seconds, to accommodate the full batch.
  Worker restart preserves the saved `next_batch_at` rather than starting immediately.
- Restarted worker **PID 14076**; status readback confirms `contact_delay_seconds=30`,
  `waiting`, remaining 86, next batch **2026-10-12T17:19:43Z**. Earlier PID/time/counts above
  are historical checkpoints. This update did not itself execute a withdrawal batch.
- Existing 17 isolated cleanup tests passed after the default change. No new sends,
  re-invites, CRM writes, n8n mutations, or commits.
- **New-request cap (Ed): 20 per Pacific day, maximum 5 per hour**, account-wide across
  senders and future re-invites. Treat as shared limits, not separate allowances per workflow.
  Existing sender workflows remain paused; actual live enforcement has not been changed in
  this pacing update and must be reconciled/implemented before any approved resumption.
