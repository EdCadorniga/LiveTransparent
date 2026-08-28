# August 2026 Partnership Contact Enrollment

## Outcome

On 2026-08-27, the August 26 partnership email and LinkedIn CSV files were reconciled against live GHL and enrolled into the existing Partnership Marketing Pipeline.

- Source rows: 431
- Unique source emails: 429
- New GHL contacts created: 404
- Existing exact-email contacts tagged: 23
- Actionable contacts enrolled in both partnership selectors: 427
- New contacts tagged `august_26_partnership_contact`: 404
- Existing LinkedIn URLs added: 3
- Errors: 0
- Vapi selector tags applied: 0

## Matching Rules

- The email and LinkedIn files were merged by normalized full name.
- Exact email matching was used before contact creation.
- Existing contacts were not overwritten.
- Two shared-email groups were skipped because separate people cannot safely share one email campaign recipient:
  - `chris@medicalmarijuana411.com`
  - `irfan@theflower.agency`

## Applied Tags

The 427 actionable contacts received:

- `partner_candidate_email`
- `partner_candidate_linkedin`

The 404 newly created contacts additionally received:

- `august_26_partnership_contact`

No `vapi_campaign_brand` or `vapi_campaign_dispensary` selector tag was applied. Existing terminal Vapi outcome tags were not modified.

## Routing

- `LT - Partnership Email Dispatcher` (`Xshck23cKo1yXL9D`) is active and published, with a 60/day weekday cap at 11:00 America/New_York.
- `LT - Partnership LinkedIn Dispatcher` (`crKIsaL5k3YBfqDZ`) is active and published, with a 30/day weekday connection-request cap at 15:00 America/Chicago. It seeds partnership state before claiming requests.
- `LT - Partnership LinkedIn DM Sequence` (`nspggypNF245xzeL`) is active and published at 12:00 America/Chicago. It sends DMs only after a LinkedIn connection is accepted.
- No manual live email, connection request, or DM execution was triggered during enrollment.

## Scripts and Verification

- `scripts/reconcile_august_2026_partnership_live.ps1` performed the contact reconciliation and campaign-tag enrollment.
- `scripts/tag_august_26_partnership_contacts.ps1` applied the source tag to the 404 newly created contacts.
- Final dry-run verification found 404/404 new contacts with `august_26_partnership_contact`, with zero missing tags and zero errors.
- The action log is stored beside the source CSVs at `Contacts added August 25 2026/Partnership contacts August 26 2026 1/August_2026_Partnership_Action_Log.json`.

## Follow-Up

- Resolve the two shared-email groups before adding those four rows to email outreach.
- Monitor the next Email Dispatcher and LinkedIn Dispatcher runs for send/state persistence, suppression behavior, and absence of Vapi selector tags.
