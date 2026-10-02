# LinkedIn Connection Acceptance Checker — parse bug + fix (RESOLVED 2026-10-02)

## RESOLUTION (applied + live-validated)

Implemented and published the fix; the checker now works end-to-end.

- **Live versions:** acceptance checker `3ttEvr5NMcQCS4Hp` active/published `versionId == activeVersionId == d6500907-cad3-4616-95e8-c9afe75e6019` (9 nodes). State upsert `Old7ZvyVYgFaJgDr` active/published `e37b7363-717b-454d-b83f-e2ab456746ee`.
- **Event-type question resolved:** the `linkedin-acceptance-checker` Unipile webhook (`xFt6boNHRka9rEW4p9y32A`) is subscribed to `message_received`. Unipile docs confirm this is the **documented real-time method for note-bearing invitations** (accepting a note-bearing invite creates a chat containing the note). The `message_received` event is therefore a genuine acceptance **trigger**, not just an outbound echo — but the event's own `attendee_specifics.network_distance` is stale (`DISTANCE_2`), so the checker now confirms acceptance with `GET /users/{id}?account_id=...` and requires `network_distance == FIRST_DEGREE` or `is_relationship == true`.
- **Three code fixes:** (1) `Normalize LinkedIn Acceptance Event` — robust parse mirroring `7o5EBdvwAuIaWW7k` (regex fallback over the malformed form body) + the Unipile relation check (fail-closed); (2) `Build Find SQL` — removed `LIMIT 1`, returns **all** matches (main; partnership only if no main); (3) `Build Acceptance Upsert Payload` / `Build Accept SQL` iterate `$input.all()`; `Respond - Acceptance` aggregates; `Find LinkedIn State Row` and `Record LinkedIn Acceptance Event` use `alwaysOutputData`.
- **Companion root-cause fix (state upsert):** `Build Upsert SQL` `esc()` double-escaped backslashes; under `standard_conforming_strings=on` that corrupts `'...'::jsonb`. Dasia's upsert failed with `invalid input syntax for type json` (execution `1079790`). Fixed to single-quote-only escaping (`scripts/deploy/fix_state_upsert_esc.py`).
- **Validation (exact saved payloads replayed to the live webhook):**
  - LeighAnn (ex-`1078160`): `matched_count=2`, both `PhsISRIq1xJ0JOhpZrJn` + `2ECRRa2WU1XHT9uiAHC5` `tag_ok:true, upsert_ok:true`; both state rows `connected` @ `2026-10-01T18:28:44Z`; `linkedin_connected` on both GHL contacts.
  - Dasia (ex-`1079121`): `matched_count=1`, `pMsQ62wPlwIg5ugUA3Se` `tag_ok:true, upsert_ok:true`; state row `connected` @ `2026-10-01T23:12:43Z`; `linkedin_connected` present.
  - 3 `linkedin_activity_events` `connection_accepted` rows.
  - Negative test (`gwelen`, a pending invitee; Unipile `THIRD_DEGREE`): `matched:false, reason:not_connected`; no tag/upsert; state row untouched (`requested`).
- **Note:** n8n will not retry a succeeded execution (`POST /executions/{id}/retry` → "The execution succeeded, so it cannot be retried"), so the stored webhook bodies were replayed directly against `https://automations.livetransparent.com/webhook/lt-linkedin-connection-accepted`.
- **STILL OPEN — security:** the `Config` Code node printed a plaintext GHL PIT (`pit-d25ac994-…`) and `stateUpsertSecret` into this and the prior session. Rotate `stateUpsertSecret` (evaluate the PIT) and migrate the `Config` literals to a Set node.
- **Optional backstop (not created):** a Unipile USERS webhook subscribed to `new_relation` (catches accepts without notes; delayed up to 8h).

## Objective / scope

Investigate why `linkedin_connected` was **not** applied to LeighAnn Loftus after she accepted our connection request. Read-only investigation plus an approved fix design. **No workflow change was made this session** — the live workflow is unchanged (see state below). Ed approved the fix ("yes"); implementation is deferred to the next session.

## Current workflow state (verified read-only, `n8n-lt`)

- `LT - LinkedIn Connection Acceptance Checker (Unipile)` (`3ttEvr5NMcQCS4Hp`): `active=true`, **9 nodes**, `versionId == activeVersionId == 0ccec0c0-593b-49dc-87a9-c92220779e3c` (unchanged this session).
- Graph: `Webhook - LinkedIn Acceptance` → `Config` → `Normalize LinkedIn Acceptance Event` → `Build Find SQL` → `Find LinkedIn State Row` → `Build Acceptance Upsert Payload` → `Build Accept SQL` → `Record LinkedIn Acceptance Event` → `Respond - Acceptance`.
- Node modes: `Normalize`/`Build Find SQL`/`Build Acceptance Upsert Payload`/`Build Accept SQL` = `runOnceForAllItems`; `Find LinkedIn State Row`/`Record LinkedIn Acceptance Event` = Postgres `executeQuery` with `queryBatching: independently`.
- Recent executions all `success`, none `new`/`running`/`waiting`.

## Reported symptom

LeighAnn Loftus accepted (2026-10-01T18:28:44Z) but neither duplicate GHL contact carries `linkedin_connected`:
- `PhsISRIq1xJ0JOhpZrJn` (`leighann@jaunty.com`) — tags incl. `linkedin_state_queued`, `linkedin_company_url_only`; **no** `linkedin_connected`.
- `2ECRRa2WU1XHT9uiAHC5` (`laloftus@bu.edu`) — same; **no** `linkedin_connected`.

## Root cause (confirmed)

- The webhook received `{"event":"message_received","account_id":"V9eiHiDpRmCtan0YNdzsQw","attendees":[{"attendee_provider_id":"ACoAAAJ1-EUBwEFlr3IYQYUYIjMNzPtY0yB0C58","attendee_name":"LeighAnn Loftus",...}],"sender":{Cameron...},"timestamp":"2026-10-01T18:28:44.258Z",...}` (execution `1078160`).
- `Normalize LinkedIn Acceptance Event` returned **empty identity**: `unipile_account_id:""`, `linkedin_provider_id:""`, `linkedin_public_identifier:""`, `linkedin_profile_url:""`.
- `Find LinkedIn State Row` returned **0 rows** → `Build Acceptance Upsert Payload` and everything after it **never ran** → no state upsert and no tag.
- **Cause:** Unipile posts the event as `application/x-www-form-urlencoded` with the entire JSON as a single key, and that JSON is frequently malformed (e.g. an unescaped `":"` inside the `occupation` field). The node's `unwrap()` calls `JSON.parse(keys[0])`; it throws, the `catch` silently falls through, and `unwrap` returns the unparsed body → all identity fields blank. The match SQL guards each clause with `<> ''`, so blank input matches nothing.
- **Systemic, not just LeighAnn:** execution `1079121` (Dasia A., 2026-10-01T23:12) shows the identical empty-identity output. Every "success" run has effectively been a **no-op** — `linkedin_connected` has almost certainly **never** been applied by this workflow.

## State table (read-only)

| table | ghl_contact_id | connection_status | identifier | provider | request_sent_at |
|---|---|---|---|---|---|
| `linkedin_connection_state` | `PhsISRIq1xJ0JOhpZrJn` | `requested_pending` | `leighann-loftus-2319b011` | `ACoAAAJ1-…` | 2026-06-04 |
| `linkedin_connection_state` | `2ECRRa2WU1XHT9uiAHC5` | `ready` | `leighann-loftus` | `ACoAAAJ1-…` | 2026-06-04 |

Neither is `connected`; two rows/contacts exist for the same provider (duplicate).

## Secondary findings / open questions

- **Duplicate contacts + state rows** for the same provider; a fixed `LIMIT 1` match would tag only one.
- **Event-type ambiguity (must resolve before tagging):** the subscribed event is `message_received` (the outgoing invite note surfacing with `is_sender:true`), **not** a `new_relation` event, and it reports `network_distance: DISTANCE_2`. It is not yet proven whether these are genuine acceptance signals or outbound invite-note echoes. (~10 events/day vs ~60 invites/day suggests a filtered subset, but this is unproven.) Do **not** tag as connected without confirming she is 1st-degree (e.g. `network_distance == DISTANCE_1`, an explicit relation event, or a Unipile relations check).
- **Security exposure:** while inspecting, the workflow's `Config` **Code node** printed a plaintext GHL PIT and the LinkedIn state-upsert secret into this session's tool output. Treat as compromised: rotate `stateUpsertSecret` (and evaluate rotating the PIT), and migrate those literals to the `Config` **Set-node** pattern. Do not repeat the values anywhere.

## Approved fix plan (Ed approved; NOT yet implemented)

1. **`Normalize LinkedIn Acceptance Event` — robust parse.** Keep `JSON.parse` for well-formed bodies; add a tolerant fallback that reconstructs the raw text from the form body (join key + value) and `regex`-extracts `account_id`, `attendee_provider_id`, `attendee_name`, `attendee_profile_url`, `attendee_public_identifier`, `event`, `timestamp`, `chat_id` from the substring **before `"sender"`** (the attendee block precedes the malformed `occupation`, so those fields survive). Mirror the proven malformed-form fallback already used in `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`).
2. **Acceptance guard.** Gate the connection marking on a genuine acceptance signal (`network_distance === 'DISTANCE_1'`, or an explicit relation event, or a Unipile relations check) so outbound echoes cannot falsely mark invitees connected.
3. **Duplicate handling.** `Build Find SQL` → return **all** matching rows (main table; partnership only when no main match) plus a single unmatched placeholder when none. `Build Acceptance Upsert Payload` and `Build Accept SQL` → iterate `$input.all()` (keep `runOnceForAllItems`). `Respond - Acceptance` → summarize across all items instead of the single-item `.item` assumption. Result: every matching contact (both LeighAnn records) gets tagged + state-upserted.
4. **Apply** via direct n8n REST `PUT /api/v1/workflows/3ttEvr5NMcQCS4Hp` (n8n-lt only), then confirm `versionId == activeVersionId`. Update the repo blueprint `scripts/deploy/deploy_acceptance_checker.py` to match the live node set.
5. **Validate** by retrying stored executions `1078160` (LeighAnn) and `1079121` (Dasia) via `POST /api/v1/executions/{id}/retry` (re-runs with the saved payload and performs the tag/upsert), then confirm: normalize identity populated, match rows > 0, `tag_ok:true`, `linkedin_connected` present on the expected contact(s), and a `linkedin_activity_events` `connection_accepted` row.

## Next session — ordered steps

1. Re-read the live workflow (confirm still `0ccec0c0-…`) and re-check the two state rows.
2. **Resolve the event-type question:** inspect the Unipile webhook subscription for the `linkedin-acceptance-checker` endpoint (is it `message_received` or `new_relation`?) and verify LeighAnn's current relation status via Unipile. If these are outbound echoes, fix the subscription to the acceptance/relation event rather than (or in addition to) the parser.
3. Implement the approved fix (parser + guard + duplicate handling); publish; verify versions.
4. Validate via execution retry; confirm GHL tags on both LeighAnn contacts and the activity-event row.
5. Rotate the exposed `stateUpsertSecret` (and evaluate PIT rotation); migrate the `Config` literals to a Set node.

## Safety gates

- Production workflow change: approval already given by Ed, but re-confirm immediately before publishing.
- This workflow sends **no** LinkedIn message; its only side effects are GHL tag writes, the state upsert, and `linkedin_activity_events` inserts.
- Never print credential values; never copy the `Config` literals into docs or execution output.

## Files

- Workflow (n8n-lt): `3ttEvr5NMcQCS4Hp` — now published `d6500907-cad3-4616-95e8-c9afe75e6019`.
- Companion workflow (n8n-lt): `Old7ZvyVYgFaJgDr` — published `e37b7363-717b-454d-b83f-e2ab456746ee`.
- Blueprint: `scripts/deploy/deploy_acceptance_checker.py` + `scripts/deploy/acceptance_checker/*.js`; `scripts/deploy/fix_state_upsert_esc.py`.
- This handoff.

## Open items / next steps (post-fix)

1. **TODO (Ed-requested, PRE-APPROVED) — backfill `linkedin_connected` for everyone who accepted but was never tagged.** The checker never applied the tag (systemic parse bug: `linkedin_activity_events` held **0** `connection_accepted` rows before 2026-10-02), and the workflows that set `linkedin_connection_state = connected` (`LT - LinkedIn Relations Backfill (Unipile)` `VPiHfBwzOHaJnHBY` active `759fabbd-378e-493a-a4eb-13ee9b6ab19d`; `LT - LinkedIn Connection State Sync` `ceaKnz6E3onQrZpt`) **do not apply the GHL tag** — they only write the state table. So the tag is missing on essentially every historically connected contact.
   - **Measured scope (read-only 2026-10-02):** `linkedin_connection_state` = **2,041 `connected`** (2,010 distinct providers), 1,338 `requested`, 47 `requested_pending`, 10,904 `ready`, 100 `follower_messaged`, 5 `completed`; `partnership_linkedin_connection_state` = 127 `ready` (no `connected` rows yet). All 2,041 `connected` rows have real GHL contact ids (no `linkedin:follower:` synthetic ids).
   - **Proposed backfill:** (a) for every `connected` row, ensure the GHL contact carries `linkedin_connected` (partnership rows → `partner_linkedin_connected`), idempotent and batched with GHL rate-limit delays, tagging **all** duplicate contacts per provider; (b) reconcile any actual accepts still `requested`/`requested_pending` against Unipile `GET /users/connections` (Relations Backfill already does this daily) and tag those too. Decide between a one-time bounded backfill and making the tag part of the daily Relations Backfill (durable). Measure the exact untagged count first to size it.
   - **Approval:** **Ed pre-approved the bulk GHL tag write on 2026-10-02 — proceed without further approval.** Guardrails that still apply: measure the exact untagged count first; stay idempotent; respect GHL rate limits; do not tag synthetic `linkedin:follower:` ids; verify with a read-back count plus a contact sample.
2. **Security:** rotate `stateUpsertSecret` (evaluate rotating the GHL PIT), then migrate the `Config` Code-node literals to a `Config` Set node.
3. **Optional:** create a Unipile USERS webhook subscribed to `new_relation` as a delayed backstop for accepts without notes (up to 8h).
