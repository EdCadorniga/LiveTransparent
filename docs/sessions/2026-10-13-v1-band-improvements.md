# V1 Bands 2–4 improvements — 2026-10-13

## Scope and step status

Ed requested simpler source summaries in Band 2, actual campaign names including October vertical outreach in Band 3, and Booked/SQLs/MQLs in Band 4. Reporting-only changes and V1 deployment are authorized by this request. Preserve the legacy report and dirty worktree; no commit or pack operation.

| Step | Status | Verified result |
|---|---|---|
| Inspect sources/live state | Complete | Facts e8c3dd1a…; Summary 4c5b5611…; Campaign Channels 24492be1… active with matching published versions. |
| Band 2 source summary | Implemented; browser check pending | Group equivalent source labels without changing counts. SQL lead sources are shown separately from the expandable booking-evidence table. Unknown remains explicit. |
| Band 3 campaign evidence | Exact-ID join complete; rendering pending | All 1,501 native queued messages match supported export by message ID, contact ID, outbound sent status and timestamp within 120s. Unique IDs across campaigns; no delivery inference. |
| Band 4 outputs | SQL validation in progress | Use same V1 stage-entry cohorts; current opportunity owner is attribution, not proof of SDR creation. Booked uses Originating SDR or appointment creator who is an SDR; otherwise unattributed. Assigned calendar user is not booker. |
| Deploy/readback | Pending | Desktop, 390px, delayed-source rendering, period switching and legacy bytes required. |

## Email reconciliation

Oct 4–10 Pacific: Alcohol 169, Cannabis Brands 39, Mushroom 117, Dispensaries 116, Crypto 0, Gambling 244, Peptides 128, Nicotine 688 = **1,501 supported outbound sent messages**. Earlier failed get-message probe does not invalidate the exact export-ID join. Delivery/open/click/reply/bounce evidence remains unavailable. Native action exceptions remain 21 errors and 2 skips.

The date-scoped public artifact contains aggregate counts and workflow IDs only; contact/message IDs remain in ignored local audit files. It is a completed historical-window snapshot, not an automatically refreshed feed. Outside its exact window no snapshot counts may be reused. Do not add its counts to legacy release totals without reconciling overlap; present it as a distinct supported source cohort.

## Operational follow-up

SMS boundary repair, 434-timeout provider reconciliation, Crypto 09:00 versus 10:00 timing, booking-click parser repair, and supported GHL clicker filter remain separate open items. This reporting request does not authorize replaying messages or changing campaign schedules.
