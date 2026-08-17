# Executive Report Campaign Accuracy - 2026-08-16

## Outcome

The Executive Report 7-day campaign view now uses exactly seven completed local dates, handles Vapi answered outcomes consistently, avoids invalid global email rates, recovers malformed LinkedIn inbound events with source timestamps, and exposes Instagram DM/reply ledger coverage.

## Live Versions

| Workflow | ID | Active version |
|---|---|---|
| Report Executive Summary API | `Bukc0mgOD2r7V6ED` | `be29cdcb-efdf-4e43-a17a-cdbd1ef622b7` |
| Report Campaign Channel Summary | `MvPLbUAN9IIQikxb` | `12f28e56-dd02-4afd-81cd-e7a2c8fa6086` |
| LinkedIn Unipile New Messages | `7o5EBdvwAuIaWW7k` | `9f61f384-f481-467f-a13e-47bf9a1b6e52` |
| Instagram Unipile New Messages | `pISlgYUsyJIrLuJd` | `ad44d943-a788-4b08-af2d-fa8ab4adbc92` |
| Social Provider Outbound Router | `kqIi8i1RjFAZKrK3` | `4a688b2b-540e-401b-8bdf-8909172c138a` |

All listed workflows were verified active with `versionId == activeVersionId`.

## Corrections

- Preset ranges end yesterday and contain exactly N completed local dates. The verified 7-day window is `2026-08-09` through `2026-08-15`; the comparison window is `2026-08-02` through `2026-08-08`.
- Vapi dispositions `connected`, `human_answered`, `interest_unknown`, `qualified`, `qualified_booked`, and `booked` count as answered. Only qualified/booked outcomes count as qualified.
- Global email rates are null when only unmatched event counts exist. The response identifies the basis as `event_counts_without_matching_send_denominator`.
- The campaign response always includes canonical rows, including Emerald, and exposes `attributionAsOf`.
- `instagram_activity_events` records successful Instagram outbound routing and inbound replies. Current historical coverage is explicitly `ledger`; existing activity before instrumentation is not fabricated.
- LinkedIn malformed form payload reconstruction now handles split form keys. Reply ledger writes use the provider timestamp rather than ingestion time.

## LinkedIn Recovery

The failed Unipile event from execution `747521` was recovered using its original message ID and timestamp:

- Message ID: `4pX8FcptXnSl5aADrrfm8A`
- Event time: `2026-08-13T20:10:07.142Z`
- First authoritative insert: `1`
- Second authoritative insert: `0`
- Live selected-window result: 1 Partnership reply plus 1 unattributed reply

The recovery utility temporarily adds an isolated webhook/Postgres branch using the workflow's existing managed Postgres credential, executes the idempotent insert twice, and removes the branch in a `finally` block. Final live verification found zero recovery nodes.

## Frontend

Build `2026-08-16-v24-campaign-accuracy` is deployed from image `v3ud1lum1svamymuor21upog:campaign-accuracy-20260816`.

- Added Instagram channel and campaign filters.
- Added Instagram DM/reply columns to channel and campaign tables.
- Added Instagram drill-down and comparison metrics.
- Added explicit Instagram ledger coverage summary.
- Retained table-level horizontal scrolling without page-level overflow.

Browser verification passed on desktop and a 390px viewport. Executive Summary, prior-period Summary, Campaign Channels, and Outgoing Calls all returned HTTP 200. The only browser console issue was the pre-existing missing `favicon.ico` request.

## Files

- `scripts/fix_executive_report_metrics.py`
- `scripts/recover_missed_linkedin_reply.py`
- `reports/embed/executive/index.html`
- `scripts/deploy_report_vps_local.py`
