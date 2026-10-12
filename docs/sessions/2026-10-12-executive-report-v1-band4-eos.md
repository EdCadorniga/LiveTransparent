# EOS — Executive Report V1 Band 4 partial refresh

Date: 2026-10-12
Project: `C:\1_Ed's Active Work\Projects\LiveTransparent`
Scope: local Band 4 report edit and handoff only. No deployment, publish, CRM write, or external action.

## Completed

- Updated `reports/embed/executive-v1/index.html` Band 4 for `2026-10-04`–`2026-10-10` (`America/Los_Angeles`) using Ed's supplied GHL tooltip counts. The code labels these figures as user-provided; this session did not independently recapture the GHL tooltip values.
- The immediately preceding accepted snapshot (`2026-09-27`–`2026-10-03`) is used for call-status WoW comparisons. Counts reconcile per SDR and Team; calculated changes are displayed by the renderer.
- Booked, SQLs, and MQL→SQL for Oct 4–10 remain blank/pending; SQL/MQL review is assigned to Ed's other LLM agent. No new output counts were assumed.
- The report note explicitly states data provenance and pending outputs. For other date ranges it states that this call snapshot is available for Oct 4–10 only; do not mistake this fixed snapshot for an automatically refreshed historical feed.

## Call snapshot recorded in the report

| Owner | Attempted | Answered | Busy | No answer | Failed | Ringing |
|---|---:|---:|---:|---:|---:|---:|
| Marc | 1,027 | 841 | 65 | 90 | 31 | 0 |
| Jason Bornillo | 778 | 536 | 78 | 133 | 30 | 1 |
| Team | 1,805 | 1,377 | 143 | 223 | 61 | 1 |

Source: user-provided GHL tooltip values (not independently reverified). Comparison source: accepted Sep 27–Oct 3 snapshot in the weekly refresh runbook. Formula: `(current - previous) / previous * 100`, rounded to one decimal. These WoW percentages are arithmetic against that accepted snapshot, not independent verification of either source.

## Verification and state

- Deterministic renderer test exercised the actual `sdr()` function: passed assertions for Marc, Jason, Team figures, call WoW percentages, and pending output values.
- Report inline JavaScript syntax check: `node --check` passed.
- `git diff --check`: passed.
- Current repository change: only `reports/embed/executive-v1/index.html` was modified at review time; this is a shared worktree. Do not overwrite unrelated changes.
- Not deployed or live-readback verified. Live build marker and published state are therefore unknown; do not claim the change is live.

## Missing data and remaining TODOs

1. Re-open the authenticated GHL native report and independently verify the selected LA date window and exact per-SDR status tooltip values, attempted totals, and Team sums. Preserve evidence. If any count differs, correct the local snapshot and rerun reconciliation/tests.
2. Obtain the Oct 4–10 Booked, SQL, and MQL→SQL values from the separate LLM review/authoritative GHL Executive Summary. Reconcile owner-level values and totals; keep unknowns blank until evidenced.
3. Review the preceding-period output values if WoW comparisons for Booked/SQL/MQL are to be shown; none are encoded as verified for this refresh.
4. Update the runbook's current accepted snapshot and comparison baseline only after source verification and output review. The runbook still identifies Sep 27–Oct 3 as accepted; this local partial edit does not make Oct 4–10 an accepted/full snapshot.
5. Confirm default URL period and report health/source labels behave as intended. Current renderer has date-specific logic and other dates do not have a complete call snapshot.
6. Run full acceptance checks and browser-read the local/staged report (date label, values, percentages, source note, no JS errors). Then request explicit approval before any deploy/publish; if approved, deploy V1 only and verify the exact live build marker/readback. No deployment approval was given in this session.
7. Revisit the scheduled weekly OpenCLI/GHL run separately: first unattended browser access is unproven in the runbook. Verify authenticated profile, exact LA window, tooltip extraction and output rows before treating a scheduled run as successful.

## Next session — ordered actions

1. Read this handoff, the weekly refresh runbook, current report diff, and project instructions; preserve the shared worktree.
2. Have Ed's other LLM agent complete SQL/MQL review; record evidence and decisions without accepting model output as source-of-truth by itself.
3. Independently verify all required GHL native values/date windows. Update local Band 4 and run deterministic tests only when values reconcile.
4. Revise the runbook snapshot and this handoff to mark exact acceptance state and provenance.
5. Obtain explicit current-session approval before deployment. Without approval, leave the verified report change local and report that it is not live.
