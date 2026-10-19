# Verified n8n SQL writer correction — 2026-10-13

## Supersedes earlier SQL-cleanup and booking-tag instructions

**A booking-link click is not a booking.** The earlier decision to add `meeting booked` from click intake was incorrect. Do not gate SQL on this tag alone, because it may already have been populated by clicks. Do not run `local-scripts/_build_cleanup_workflow.py`: its proposed opportunity deletion and full-tag replacement are not an approved or valid correction.

## Confirmed live n8n-lt source and fix

A read-only scan of accessible n8n-lt workflow definitions identified the explicit SQL-tag POST in:

- Workflow **WL - Webhook to Slack Channel Update**, `lQTW0QPwBcf3o7j8`.
- Node **Build Slack Payload**.
- Original code: `POST /contacts/{contactId}/tags`, body `tags: ['SQL']`.
- Existing eligibility relied on incoming calendar ID/name metadata, including a third calendar. It did not independently verify an appointment.

Published version **`15ef9b89-fbad-4467-a858-2bb2b83c7d7f`**, active with matching draft/published versions:

1. Before CRM writes, read documented `GET /contacts/{contactId}/appointments`.
2. Require one matching appointment, using incoming appointment ID or exact booking start (less than one minute difference).
3. Require calendar `SrtXcFVyea7pFl3nTiIK` or `WS6lacfQK2XOhqN7mRaF`.
4. Reject canceled/invalid/deleted appointments, unknown response shape, duplicate matches, and lookup failure.
5. Only after verification, retain the existing booking mutation path; tag POST now adds SQL and `meeting booked` together.

This identifies an actual writer and fixes its eligibility gap. It **does not prove** this writer caused the seven example opportunity creations. Their latest contact snapshots lacked SQL tags. The MQL ledger's `source=ghl_automation` only identifies the MQL-tag event origin; it does not establish the SQL writer.

## Click intake corrected

`1diZyFmTqWQUEny3` published at **`97f9d873-cdf5-41ce-a0dc-fe386f909f5e`**, active with matching published version:

- Apply MQL Tag now applies `mql` only; no SQL or `meeting booked` write.
- Correct n8n URL/auth expression prefixes.
- Serialize known-click path: UTM update → MQL tag → one Respond node. Preserve Process Click contact ID across the HTTP response.
- Unknown-link branch continues to Respond without tagging.

No historical tags were removed; any prior false `meeting booked` tags require appointment-based review before cleanup.

## Verification

- Full modified writer JavaScript parses with Node AsyncFunction.
- Eight mocked verification checks passed: click cannot qualify, matching ID, matching start, wrong calendar, canceled appointment, lookup failure, duplicate match, and Book a demo.
- Fresh REST readback verified exact saved node definitions and active/published version equality for both workflows.
- No workflow executed, no provider send, no contact cleanup, no opportunity deletion.
- Helpers: `scripts/audit_sql_tag_writers.py`, `scripts/inspect_sql_writer.py`, `scripts/fix_verified_booking_gate.py` (default validation only; explicit `--apply` for scoped publication).

## Reporting issues still open

- V1 `feedback_sql` counts **first Sales Outreach pipeline entry**, not an SQL tag, SQL stage, or verified booking. Therefore 27 is a pipeline-entry cohort; removing SQL tags cannot change this historical count. Correct headline/SDR/vertical/conversion definitions together; preserve historical pipeline entries separately.
- MQL-tag ledger count 36 and MQL-opportunity-stage entries 22 are different units/cohorts. Existing `ghl_automation` events must not be labeled form fills without evidence. Use canonical distinct MQL tag events for the requested MQL metric; retain stage movement as a separate metric.
- Lifetime email statistics must not sit beside weekly sent counts as one funnel. The documented stats endpoint works but weekly filtering needs documented or observed native date-bounded evidence. No proof was established that switching to Mailgun is necessary, or that `OutboundMessage` alone supplies open/click events. Polling starts a forward baseline and cannot reconstruct last week.
- Live Facts cache version `f3d5b042-0241-4fb4-bafc-e60c7fc69c68` parses (read-only EXPLAIN passed). Cache has only `7d|2026-10-07|2026-10-13`, while its lookup expects `{from}|{to}`; it is not an accepted working cache. No refresh schedule was installed in this continuation. Fix keys, Pacific completed-week coverage/current+prior windows, refresh, and measured HIT/MISS behavior before claiming latency resolved.

These outstanding changes remain part of the user's broader request. Preserve dirty worktree and legacy report; no commit or pack operation.
