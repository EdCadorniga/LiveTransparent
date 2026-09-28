# V1 mockup comparison and data-completeness audit

Updated: 2026-09-24

## Result

The V1 page now follows the mockup's six-band flow. It is not yet complete-data ready: voicemail facts, the formal action queue, and some attribution/statistics coverage still do not exist in the current source layer. The page marks those details unavailable instead of displaying guessed or implicit zero values.

## Field-by-field status

| Mockup detail | V1 presentation | Data status | Required before calling complete |
|---|---|---|---|
| New MQLs | Headline card | Available through `mqlSummary` | Reconcile period definition with MQL source totals |
| New SQLs | Headline card | Available through SQL/coverage payload | Reconcile to SQL source rows |
| MQL→SQL | Headline card | Available when `mqlSummary` returns conversion | Confirm period basis and denominator |
| Meetings booked | Headline card | V1 now counts unique Cameron contact IDs | Cancellation/reschedule rows for the same contact count once; raw appointment rows remain available for audit |
| New contacts | Headline card | Available from summary | Add mechanism classification for the source-story card |
| Opportunities created | Headline card | Available from summary | Reconcile to source breakdown |
| Opportunities by source | Story card | Partially available via contact-source opportunity counts | Add a canonical source/opportunity fact table and Unknown bucket |
| MQL sources | Story card | Partially available via `leadSourceBreakdown` | Coverage must equal headline denominator |
| SQL sources | Story card | Partially available via `leadSourceBreakdown` | Coverage must equal headline denominator |
| New contacts — LinkedIn backfill / Apollo / form | Story card | Available through V1 contact provenance facts | Reconcile mechanism rows to the headline contact denominator and retain Unknown |
| Meetings — contact, SDR, link | Story card | Available through V1 appointment-detail facts | Contact names remain unavailable when the source snapshot has no name; preserve the contact ID and attribution confidence; headline uses distinct Cameron contacts |
| Showed / no-show / cancelled / rescheduled | Story card | Aggregate statuses may be available; missing statuses are now not shown as zero | Update appointment status after the meeting and expose all four status buckets |
| Pipeline to work | Story card | Current stage payload is not sufficient to guarantee the mockup definition | Define “qualified remaining” and return a dedicated count |
| Lead-source coverage | Story card | Available through `leadSourceCoverage` | Reconcile all denominators and show Unknown/Unattributed explicitly |
| Speed-to-lead | Story card | Collected in V1 response facts | Match inbound LinkedIn DM, inbound call, or marketing-email reply to the first later outbound event on the same channel; show average/median with denominator |
| Follow-up status | Story card | Unmatched inbound count collected; target not configured | Show inbound events without a matched same-channel reply; do not label them overdue until an approved response-time target exists |
| Email campaigns | Table | Available through Campaign Channel Summary | Verify delivered/open/click/reply/bounce event coverage and unique-recipient rate semantics |
| LinkedIn campaigns | Table | Available for ledger-backed activity | Add accepted/opened/delivered definitions where provider data exists; otherwise show unavailable |
| SMS | Table | Sent/failed/replies available; delivered may be source-dependent | Verify provider delivery event contract and campaign-level rows |
| Voicemail | Table | Drops/left and callback counts now available from latest custom disposition per unique contact | The approved rule treats selecting the voicemail disposition as voicemail left; drops and delivered intentionally use the same unique-contact count |
| Calls attempted / connected / no answer | SDR strip | Available through V1 canonical call facts | Uses `report_raw_ghl_calls` plus Vapi attempts and includes an explicit Unknown/Other bucket so totals reconcile |
| Calls by SDR | SDR table | Available through V1 call facts | Preserve Unassigned when the source has no owner; reconcile team and owner totals |
| Booked / SQLs / MQL→SQL by SDR | SDR table | Available through `sdrPerformance` | Reconcile owner coverage and Unassigned totals |
| Social posts | Social strip/table | Post placements available | Reconcile channel rows to total placements |
| Impressions / reach / followers | Social strip/table | May be unavailable without authenticated statistics | Ingest account statistics by platform/day or explicitly label unavailable |
| Action queue | Final band | MQL awaiting Sales is available; contract/follow-up are not | Define queue rules and return durable actionable records/counts |

## Accuracy rules now enforced in V1

- Missing values do not silently become zero in tables, cards, or outcome buckets.
- Source-health state is visible at the top of the page.
- An empty API response is treated as an error.
- Campaign tables preserve the API's campaign rows; the page does not invent attribution.
- Unavailable provider metrics are labelled `N/A` or `Unavailable`.

## Completion gate

The report should not be described as complete until every row marked “Required before calling complete” has a populated source, a documented definition, and a reconciliation test against the headline totals. The next implementation step is the reporting API/data-model work for those missing facts, followed by live-period QA and desktop/mobile visual QA.
