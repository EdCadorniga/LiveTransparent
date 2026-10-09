# All-Vertical Apollo Phone Enrichment — EOS (2026-10-08)

## Objective and standing decision

For future lead cohorts uploaded across **all verticals**, run Apollo Phone Enrichment after import and identity reconciliation. Preserve any source-provided phone in GHL's `Corporate Phone` field before setting `Enrich Phone via Apollo = Yes`. A successful Apollo callback writes the enriched direct number to primary `Phone`; the source/company line should remain available in its separate custom field. Do not clear primary Phone in the queue import.

Use two ordered GHL CSV updates keyed by Contact ID: (1) source `Phone` → `Corporate Phone`, then (2) `Enrich Phone via Apollo` = `Yes`. Skip contacts already enriched unless a retry is intentionally approved. Read back import outcomes and asynchronous status/provider results before claiming completion.

## Live test and verification

- Test contact: Courtney McElligott, GHL contact `FTCWeS26CKKKGDCOTIWS`.
- Ed set `Enrich Phone via Apollo = Yes`; the existing path completed successfully.
- Live n8n-lt readiness returned HTTP 200. `LT - Apollo Phone Enrichment Polling` (`JH8ShfpglWmLMZ3l`) was active with `versionId == activeVersionId == d3ddd510-1157-42a5-b640-44c058fc7c5b`.
- Successful execution `1109436` (`webhook`, 2026-10-08 12:31:33Z) included Courtney at `Enrich Contacts via Apollo`. GHL contact readback showed Apollo status `enriched`, trigger field reset to `No`, Apollo contact metadata present, and the enriched primary phone populated. Her source phone remained in `Corporate Phone`.
- At the initial test checkpoint, this validated only the one-contact path; no bulk import/enrichment or additional contact change had occurred at that point. A later same-day update below records the webhook burst and Mushroom-only Vertical field changes.

## Current staged all-vertical cohort

Source: `New Campaigns October 2026/Export_Contacts_All Verticals Oct 2026 Outbound_Oct_2026_8_24_PM.csv`.

- 914 rows; 914 unique Contact IDs and emails.
- 135 rows had a source Phone; 779 had no source Phone.
- Courtney, the completed test, is excluded from both prepared files. The source-phone preservation file therefore has 134 rows; the Apollo queue has 913 rows, including remaining contacts both with and without a source phone.
- Prepared local-only files:
  - `New Campaigns October 2026/GHL Import Prep/All Verticals - Preserve Existing Phones as Corporate Phone.csv` — Contact ID + Corporate Phone (134 rows).
  - `New Campaigns October 2026/GHL Import Prep/All Verticals - Apollo Phone Enrichment Queue.csv` — Contact ID + Enrich Phone via Apollo = Yes (913 rows).
- At initial preparation, neither file had been imported. The later 12:54 UTC webhook burst shows that GHL flag-trigger requests were subsequently reaching the poller, but this review did not establish whether either CSV was imported or which cohort produced those requests. Do not describe the 913-contact cohort as unstarted or completed until its GHL flag/status state is reconciled. Before importing the Corporate Phone file, compare against current GHL values so newer/different values are not overwritten; import preservation before queueing.
- The staging helper is `scripts/apollo/prepare_all_verticals_phone_enrichment.py`; it reads the supplied export and writes local CSVs only.

## Ordered next actions

1. Reconcile the 134 staged source-phone values against current GHL `Corporate Phone`; resolve mismatches/existing values before import.
2. Ed imports the phone-preservation CSV through the GHL Contacts CSV UI and verifies successful row count and field mapping.
3. Ed imports the Apollo queue CSV through the same UI and verifies the Contact ID and `Enrich Phone via Apollo` mappings. Do not change any primary Phone value as part of this queue import.
4. Allow the active poller to process the cohort in scheduled batches; current live settings are a native 5-minute Schedule Trigger and maximum 10 contacts per run. Verify the first natural scheduled execution after the latest tuning before treating the changed pace as runtime-proven.
5. Reconcile every Contact ID against GHL status and callback/provider outcomes: enriched, no_match, error, callback_failed, callback_timeout, or still queued. Investigate failures before retrying; do not blindly re-import Yes for already processed contacts.
6. Review primary Phone versus preserved Corporate Phone values and any duplicate/shared-number collisions before subsequent phone cleanup or campaign use.
7. For every later vertical import, repeat the preserve-then-queue sequence automatically as the intake checklist, with a completed-contact skip.

## Scope and verification boundary

- No production workflow was edited or published. No enrollment or send action was involved.
- The one-contact Apollo enrichment was an explicitly requested live test and is accepted as successful based on execution `1109436` plus GHL contact readback.
- Bulk work remains an operator-import step. The staging script and generated CSVs are local artifacts, not GHL writes.
- Documentation updated in this closeout and follow-up: `AGENTS.md`, `Project Status and Next Steps.md`, `GHL Live Transparent CRM/Operating Snapshot.md`, `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`, `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`, `GHL Live Transparent CRM/Apollo_CSV_to_GHL_Field_Mapping.md`, and the Mushroom workflow handoff.
- Existing dirty worktree contains unrelated Nicotine/Mushroom campaign prep files and session notes. Preserve them; no staging/commit was performed.

## Later same-day update — webhook rate limit and Mushroom cohort (2026-10-08)

### Apollo live-state readback

- At 12:54 UTC, n8n-lt readiness was HTTP 200. Poller `JH8ShfpglWmLMZ3l` was active/non-archived with `versionId == activeVersionId == d3ddd510-1157-42a5-b640-44c058fc7c5b`; Callback Handler V4 `U7c6byTLXAMgcS75` was active/non-archived with matching version `268bf4d0-8d6d-4caa-81bc-c3e7be7229b3`; Reaper `RL5ZyUoshSPbmVA1` was active with matching version `554fd192-8402-4133-bb65-da240bce3be7`.
- The 12:54 UTC snapshot returned at least 100 poller executions in `error`, at least 100 in `new`, and five `running` globally, all five running rows belonging to the Apollo poller. Sample execution `1110315` failed at contact fetch with HTTP 429. Its webhook body showed `Enrich Phone via Apollo = Yes` and the GHL caller `WL - Apollo Phone Enrichment Trigger`; the live poller itself exposes `ghl-apollo-phone-enrichment-intake-v3`. Do not call that GHL caller unused. The originating bulk action/cohort was not established by this read-only check.
- Fresh read at 13:31 UTC found no `new`/`running` poller or callback executions returned. Poller successes had resumed through 13:16 UTC; Callback V4 had successes through 13:09 UTC. The latest 100 poller errors returned were still from the approximately 12:55 burst. This is evidence of immediate recovery, not proof that every affected contact completed enrichment.
- Final read-only check at 13:35 UTC confirmed poller (3 nodes), Callback V4 (4 nodes), and Reaper (6 nodes) all active/non-archived with matching draft/active versions. No `new`, `running`, or `waiting` executions were returned for any of the three. The poller and callback latest successful executions remained `1111297` (13:16 UTC) and `1111252` (13:09 UTC); this does not reconcile the error cohort.
- **Next:** identify which contacts were affected and what initiated the burst; reconcile status/provider results for all requested records. Do not re-import the 913-row queue CSV or repeat `Yes` writes as a retry. Hold further bulk Apollo queuing until the affected cohort and rate limit are understood.

### Rate-limited worker improvement — 2026-10-08 13:46–13:58 UTC

- **Root cause in graph:** the live 3-node poller contained Webhook → Config → Code only; no native Schedule Trigger existed. Its code had `maxPerRun=5` and a scan/batch branch, but the live GHL path was webhook mode and bypassed that cap. Each flag change fetched a GHL contact and made up to two serial Apollo `POST /v1/people/match` calls inside a separate execution. A bulk GHL field update could therefore fan out concurrent webhook executions.
- **Change applied to n8n-lt only:** added a native Schedule Trigger → existing Config → worker connection. Webhook mode now acknowledges and returns before GHL contact lookup/Apollo calls; `Enrich Phone via Apollo=Yes` remains the durable queue. Initial deployed pace was 30 minutes/max 5 (`cb8e76e4-a190-43b4-97fc-05ca971cfaf8`); Ed then selected the faster 5-minute/max-10 setting, now active at `d1b08e39-6152-427d-b409-a7429647b290` (4 nodes). Helpers: `scripts/apollo/serialize_apollo_webhook_intake.py` and `scripts/apollo/tune_apollo_worker_rate.py` (both dry-run by default; `--apply` performs the n8n-lt update).
- **Apollo capacity check:** official [Apollo rate-limit docs](https://docs.apollo.io/reference/rate-limits) say limits are plan- and endpoint-specific, shared across the Apollo team, and 429 responses include `Retry-After`. Read-only Usage Stats API check at 13:47 UTC reported `api/v1/people:match` limit 1,000/minute, 0 consumed, and no hourly/daily limits returned. At the new cap, up to 10 contacts × two `people/match` calls is 20 calls every 5 minutes (4/minute average, 240/hour), excluding other team usage. Apollo's [bulk people enrichment API](https://docs.apollo.io/reference/bulk-people-enrichment) supports up to 10 records/request and async phone callbacks, but was not adopted because current callback correlation embeds one GHL contact ID per webhook URL; batching needs a durable Apollo-ID↔GHL-contact mapping and callback redesign.
- **Post-tune verification:** poller active/non-archived, `versionId == activeVersionId == d1b08e39-6152-427d-b409-a7429647b290`, 4 nodes, schedule 5 minutes and `maxPerRun=10`; Callback V4 remains active version `268bf4d0-8d6d-4caa-81bc-c3e7be7229b3` (4 nodes); Reaper remains active version `554fd192-8402-4133-bb65-da240bce3be7` (6 nodes). At 13:58 UTC, no `new`/`running`/`waiting` poller executions were returned. Code syntax parsed successfully with Node. **The first scheduled worker run has not been observed; no manual worker run or bulk enrichment was performed.**
- **Next steps:** wait for the first natural scheduled execution; verify scheduled mode, `scanned <= 10`, contact status transitions, and later callbacks. Then reconcile the 12:55 GHL-429 contact cohort and identify the burst source before importing Apollo-flagged cohorts. Do not increase the cap until GHL stability and Apollo usage headers are reviewed.
- **Security follow-up:** detailed execution diagnostics exposed webhook authentication material in the inspection output, and the poller Code node contains a hard-coded callback key. Treat affected key(s) as exposed; no values are recorded here. After identifying/reconciling pending callbacks, rotate the key(s), migrate the literal to restricted workflow configuration, and verify the callback handler/caller. Do not rotate while valid Apollo callbacks may still be outstanding.

## Later update — single-call credit optimization and error pause (2026-10-08)

- Apollo's official pricing guide says people enrichment costs 1–9 credits/person when qualifying data is returned: typically 1 for demographics/email and +8 when a mobile number is returned. Apollo warns repeated enrichment calls can increase total credit use; its docs do not promise that two calls for the same person are deduplicated.
- Consolidated match and phone reveal into the same `people/match` call/contact, preserving asynchronous phone delivery through the same webhook URL with GHL Contact ID correlation. Live workflow version `22d24fe4-1026-4a7b-a487-99590d10648f`, active, four nodes; pacing was 5 minutes/max 10. Script `scripts/apollo/consolidate_apollo_phone_reveal.py`.
- First scheduled execution after this update, `1111574` (2026-10-08 14:30:22 UTC), scanned 10 and returned `apollo_error` for all 10. Read-only GHL checks confirmed all ten still have `Enrich Phone via Apollo=Yes` and status `error`. Apollo Usage Stats after the run still reported 0 `people/match` consumed; the exact API rejection reason was not present in the workflow output and remains undiagnosed.
- **Safety action:** disabled only the Schedule Trigger; webhook acknowledgement remains enabled. Current workflow version is `9c8c63ab-588d-4519-925f-72469781d05c`, active, 4 nodes. No new/running/waiting executions returned after the pause. This stops automatic retries while preserving the durable `Yes` flags.
- **Retry behavior:** no field reset is needed. The scheduled worker selects `Enrich Phone via Apollo=Yes` regardless of Apollo status, so contacts whose status is `error` remain eligible. Do not re-import/reapply Yes; doing so can create another webhook burst. Keep the schedule paused until the Apollo request error is diagnosed and a safe one-contact retry is explicitly chosen, then re-enable and verify.
- Apollo docs: [API pricing and credits](https://docs.apollo.io/docs/api-pricing), [People Enrichment](https://docs.apollo.io/reference/people-enrichment). The current single-request method should avoid the redundant second match; actual credit savings still need confirmation in Apollo Credit Usage after a successful request. No controlled test or manual batch was run.

## Resume request and one-contact diagnostic — 2026-10-08 15:08 UTC

- Ed requested resuming. The workflow was briefly enabled at 5 minutes/max 1 and the Apollo error result was extended to record only sanitized HTTP status/error code (no response body or credentials).
- Natural execution `1111794` at 15:05:22 UTC scanned one contact and returned `apollo_error`. Neither HTTP status nor error code was captured. The contact remains `Enrich Phone via Apollo=Yes`; readback confirmed the queue flag survives the failure.
- The Schedule Trigger was disabled again to avoid retrying that same error every five minutes. Current active workflow version `7cdef5ce-c3be-4cff-95fd-e8b17f594538`, four nodes; webhook ack-only path remains available. At 15:08 UTC no `new`/`running`/`waiting` executions were returned.
- **Reset guidance:** do not reset status or re-import/reapply `Yes`. The scheduled worker selects by the trigger flag regardless of `Apollo Phone Enrichment Status=error`; the ten failed contacts remain eligible when the schedule is restored. The current blocker is the undiagnosed Apollo request error, not queue membership.
- Apollo Usage Stats still showed `people/match` consumed 0 at the read after the failed attempts. This does not explain the request rejection. Next: diagnose the request/route with sanitized status detail or a separately authorized single-contact test; then restore the five-minute schedule at a small cap and inspect a successful run before increasing throughput.

## Credit blocker confirmed and current pause — 2026-10-08 16:08 UTC

- Corrected the Apollo API URL to the documented `https://api.apollo.io/api/v1/people/match` and passed phone-reveal settings plus encoded `webhook_url` in the query string. The one-contact scheduled attempt still returned HTTP 422; execution `1111965` only retained the generic status, so a single controlled request was made for one queued contact to inspect Apollo's response.
- Apollo returned HTTP 422 `insufficient credits`, with no person match, no request ID, and no phone callback. Apollo Usage Stats still showed zero consumed `people/match` requests. The blocker is credits/plan eligibility, not the schedule cadence or rate limit.
- Schedule is disabled in active version `9c135647-525c-41ed-b809-84cd4a88eea7` (4 nodes, maxPerRun=1). Webhook acknowledgement remains active. The error-status contacts still have `Enrich Phone via Apollo=Yes`; no reset/re-import is required. Do not re-enable the worker or retry until credits are added/plan adjusted. Then start at one contact, verify a successful callback and credit consumption, and scale toward 10/run.
- No successful Apollo match or phone reveal resulted from the diagnostic request; no contact phone was written by that request. It used one contact only.

### Mushroom cohort/import preparation and live contact updates

- The 119-row Mushroom source reconciled to 111 net-new contacts plus seven unique exact-email GHL matches; Jill's address occurs on two different source rows. All seven matched records were initially `Vertical = Cannabis` and held to avoid changing an existing record or creating an email duplicate.
- At Ed's direction, the seven existing GHL contacts were reclassified to `Vertical = Mushroom`: Kylee Hoynacki (`4nosJTSPqasgf8hWTXTR`), Cheyne Nadeau (`UqcKoEkyKsDbGQb7q1HO`), Jill Wilson (`rk6jqv9xpKLZSmOYG3Xc`), Christopher Shields (`yCZSVldehjWCYtO57Vht`), Madison Christie-Hamre (`gDEeKCPhfaMXcNQDrUOv`), Matthew Snyman (`s0K1jYuXlL2R8IBoBbkw`), and Aaron Nosbisch (`qE3Xx8kZIdOLrLcioOwz`). Fresh GHL readbacks confirmed all seven. Only `Vertical` was changed; pre-existing tags/enrollment markers were preserved. In particular, Kylee/Cheyne retain Cannabis sequence tags and Aaron retains Emerald enrollment tags; they were not enrolled in the Mushroom sequence.
- Read-only Apollo-field check after reclassification found Jill and Christopher already `enriched` (skip them); the other five have no Apollo status/flag and no primary phone, while each has a source Corporate Phone value. Prepared `Mushroom Existing Contacts - Vertical and Apollo Phone Enrichment.csv` with Contact ID, Vertical=Mushroom, and Enrich Phone via Apollo=Yes for those five only. This is a staged update file, not imported.
- The 111 new-contact creation file has `Enrich Phone via Apollo=Yes` on all rows and retains 94 source numbers in `Corporate Phone`. A second, auto-mapping-friendly version was prepared at `New Campaigns October 2026/GHL Import Prep/Mushroom New Contacts - Auto-Mapped + Apollo Phone Enrichment.csv`. It uses standard/exact GHL labels (`Company Name`, `Apollo Person LinkedIn URL`, `Apollo Company LinkedIn URL`, `Apollo Facebook URL`, `Apollo Twitter URL`, `Corporate Phone`, `Vertical`, `Enrich Phone via Apollo`); the old ambiguous and blank columns are omitted. Script: `scripts/apollo/prepare_mushroom_automapped_import.py`.
- Structural validation passed: 111 rows, 111 unique emails, all `Vertical=Mushroom`, all Apollo flags `Yes`, 94 Corporate Phone values preserved, no primary `Phone` column, and every non-dropped source value matched the previous staged file. The GHL import wizard auto-mapping preview has not been checked; the user must verify it before confirming the import.
- No Mushroom contact import or Apollo queue update was performed. Given the preceding GHL 429 burst, do not import the Apollo-flagged files until the Apollo webhook incident has been reconciled/cleared. Keep the existing GHL contacts out of the new-contact create CSV to avoid duplicates.
