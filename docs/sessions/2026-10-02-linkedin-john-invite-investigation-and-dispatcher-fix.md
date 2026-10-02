# 2026-10-02 — "John" LinkedIn invite investigation + dispatcher fix

## Objective
Ed saw a LinkedIn connection-request note `Hey Leigh Ann — quick connect. John here with Transparent eCom.` on a prospect (LeighAnn Loftus) and asked what was sending the old "John" template, then to (a) identify the sender, (b) fix the errored GHL LinkedIn Connect Dispatcher, and (c) define the auto-invite business rule for MQL-tagged contacts.

## What the "John" note is
- It is a **LinkedIn connection-request invite note**, not a DM, sent via the **Classic Unipile account** `V9eiHiDpRmCtan0YNdzsQw` (profile `cameronkarkut`).
- **It is NOT in n8n's current config and NOT in any retained workflow version.** Current senders use the **Cameron** copy (`Hi {first_name}, I am Cameron co-founder of Transparent eCom…`).
- **Root cause:** the note was the **default message of n8n workflow `Zt8p2aYtIuY0HK18` ("LT - LinkedIn Connection Request (Unipile) (Internal Test)")**, which the (now unpublished) GHL automation **`Send Connection Request through Unipile when MQL Tag is added` (`25cd82a2-8344-4dc5-962f-a2b5e5c5ee88`)** POSTs to at `https://automations.livetransparent.com/webhook/unipile-linkedin-connect-test`.
  - The GHL action carries **no `message` field** (only `linkedin_url`, `contact_id`, `first_name`, `send:true`, header `x-lt-unipile-key`), so the text always came from `Zt8…`'s own `defaultMessage`.
  - `Zt8…` **publish history:** active **2026-04-22 → deactivated 2026-07-11 00:47 UTC** (edited 2026-07-15; current config default = Cameron copy). It is **inactive now** (`activeVersionId` empty; 0 retained executions — executions are pruned after ~4 days).
- Therefore the John invites were sent **Apr 22 – Jul 11, 2026**. **Nothing has sent the John note since 2026-07-11**; every GHL call since then 404s (`unknown webhook … not registered`; last log hits 2026-09-28 → 2026-10-01T12:29Z tied one-for-one to `mql` tag events). The notes Ed sees are **old invites being accepted now**.
- Evidence: first message (the invite note) in the chats of control contacts is the John template — christopher-powell, catherine-konidas, alison-li-lin — while the n8n `linkedin_connection_state.request_message` for the same contacts is the **Cameron** pitch (the scheduled dispatcher `fXxw5lanZcDmUrst` is a separate sender).

## LeighAnn Loftus specifics
- Both `linkedin.com/in/leighann-loftus` and `linkedin.com/in/leighann-loftus-2319b011` resolve to the **same Unipile profile** `ACoAAAJ1-EUBwEFlr3IYQYUYIjMNzPtY0yB0C58` / `leighann-loftus`. The two GHL contacts (`PhsISRIq1xJ0JOhpZrJn`, `2ECRRa2WU1XHT9uiAHC5`) are **duplicates of one person**.
- **Connected:** `connected_at = 1790879324000` ms = **2026-10-01 18:28:44 UTC**.
- n8n state `request_sent_at = 2026-06-04 20:32:44Z` is the **dispatcher** path (Cameron copy), a different invite than the accepted John one.

## Fixes applied (live n8n-lt, this session)
Workflow **`LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`)**, published via direct REST PUT:
1. **Root cause of the every-run error:** the `Config` Set node's **`pgPassword` assignment was missing `"type":"string"`**, so Set v3.4 threw `Cannot read properties of undefined (reading 'toLowerCase')` at `Config` and every scheduled run failed. Added the field.
2. **Business rule added** to `Fetch Ready Queue` claim query:
   ```sql
   AND connected_at IS NULL
   AND (request_sent_at IS NULL OR request_sent_at < NOW() - INTERVAL '30 days')
   ```
   → skip if already connected, or if invited within the last 30 days. Duplicate prevention is also covered by state (`requested`/`connected` rows are not `ready`) and GHL tag blocking (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_done`, `stop_linkedin_dms`).
- **Live state:** `active=true`, `versionId == activeVersionId == 99c1f5ee-d52d-44b4-95ef-b58d122ff2df`, 10 nodes, `versionCounter=86`.
- **Verified:** execution **`1079371`** (2026-10-02 00:45 UTC) `success` — `queue_found=15, batch_size=10, sent=10, failed=0`. Daily cap intact (`min(batchSize, dailyLimit − sentToday)`, `dailyLimit=60`). 60 stale `requested_pending` rows self-release to `ready` after 30 min.

## Current data/backlog snapshot (~2026-10-02T00:35Z)
`linkedin_connection_state`: `ready` 10,953 · `connected` 2,038 · `requested` 1,279 · `requested_pending` 60 · `follower_messaged` 100 · `completed` 5. Of the `ready` rows: 10,866 never requested, 87 requested >30 days ago, 0 requested <30 days, 0 connected.

## MQL automation — decision
- The separate GHL `Send Connection Request through Unipile when MQL Tag is added` automation is **not needed**; Ed has **unpublished** it. The dispatcher already invites any contact that has a LinkedIn URL (MQL contacts included), 10 per 15-min run, ≤60/day, with suppression + the 30-day rule.
- A live "mql tag added → n8n" pipe already exists if we want explicit/immediate MQL enqueue: GHL **`WL - MQL Tag Ledger` (`203163a4-262a-4195-9a15-b4aa0b712c5a`, published)** → n8n **`LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`, active)**, which currently only logs to `mql_tag_events`.
- GHL **`LT - UNIPILE LinkedIn Connection Request (Internal Test)` (`ac5c28b7-746a-48b9-a780-2595e53bb114`)** is `draft` (not running).

## Known defects / risks (not fixed this session)
- **Dispatcher outbound mirror to GHL Conversations fails `401`** (`mirror_status: mirror_failed`, "Request failed with status code 401" per sent invite). The `mirrorLinkedInToGhl` step uses the **PIT** against `/conversations/messages`, which needs the **OAuth location token** (via `/oauth/locationToken`). Invites still send on LinkedIn; only the GHL conversation copy is missing.
- **Live sending resumed**: the fixed dispatcher now sends real invites (10 in the first run). ~10,953 `ready` backlog ≈ 60/day.
- **Secret exposure (pre-existing):** the Unipile API key and the Postgres password are stored/captured in plaintext in workflow Config/Code and some `scripts/`; the Postgres password was also read this session. Rotate + migrate to Config/placeholders as previously flagged.

## Next steps (ordered)
1. **Fix or drop the GHL mirror 401** in `fXxw5lanZcDmUrst` `Dispatch LinkedIn Requests` (`mirrorLinkedInToGhl`): use the OAuth location token (`POST /oauth/locationToken` with the agency access token from Postgres `ghl_oauth_tokens`) instead of the PIT — or intentionally stop mirroring.
2. **Monitor** the next scheduled dispatcher runs (15-min, `*/15 15-21 * * 1-5` America/Los_Angeles): confirm `success`, ≤60/day, no duplicate invites, and watch for LinkedIn invite restrictions.
3. Optional: **decide on explicit MQL enqueue** — extend `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`) to upsert MQL-tagged contacts as `ready` in `linkedin_connection_state` (reuses dispatcher suppression/rate-limit). Not required while the dispatcher feeds all LinkedIn-URL contacts.
4. **Security:** rotate the Unipile API key and Postgres password; migrate plaintext literals to Config/placeholders.
5. Confirm the unpublished GHL `25cd82a2` stays unpublished/disabled, or delete it to remove the dead `unipile-linkedin-connect-test` pointer.

## Safety gates
- Live LinkedIn sends are approval-gated except the dispatcher's intended scheduled operation. Do not manually execute sender workflows without explicit approval.
- Use only `n8n-lt`; never use another n8n instance. Never commit/echo secrets.
