# EOS Closeout — LinkedIn Inbound DMs and GHL OAuth Renewal

Date: 2026-09-24
Status: Closed out; live fixes verified.

## Objective

Recover the missing LinkedIn inbound messages for Andrew Timmons and Anthony Riley, identify why they did not appear in GHL Conversations, and restore reliable GHL OAuth renewal for the inbound bridge.

## Root causes

1. `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) stopped at `Find LinkedIn State Row By Provider` because its fallback SQL referenced `linkedin_conversation_map.payload_json`, which is absent from the live table. The live column is `raw_payload`.
2. After that SQL issue was fixed, the inbound bridge reached the GHL exchange but the stored OAuth access token returned HTTP 401 from `/oauth/locationToken`.
3. The scheduled OAuth renewal workflow (`Mf4wdFNurt5vyQu4`) was scheduled every six hours but failed at `Check Refresh Token Source` with `Could not get parameter "jsCode"`. The runtime was not executing the Code-node definition shown by the workflow API.

## Live changes

- Published the LinkedIn map fallback fix, using `COALESCE(m.raw_payload, '{}'::jsonb)`.
- Refreshed the GHL OAuth token and stored a validated replacement.
- Changed the LinkedIn inbound bridge to queue OAuth 401s for replay after renewal instead of bypassing the queue with the location PIT.
- Replaced the OAuth renewal workflow's two successful-path Code nodes with native Set nodes and expressions, preserving source-token validation, HTTP/expiry validation, and fail-closed failure handling.
- Added `LT - LinkedIn Inbound OAuth Retry` (`4Qww6KyTxnoRAs9m`) on `10 */6 * * *` so it runs ten minutes after renewal, exchanges the renewed agency token, replays queued GHL inbound messages, and bounds each row to five attempts. Its active path contains no Code node.
- Republished and reactivated the OAuth renewal workflow. Temporary verification webhook triggers were removed after each test.

## Verification

- Andrew Timmons replay: contact `nZMeEnELiwPeVVz73LVD`; GHL conversation `XuidkqTq5Mk6eZqSmDxo`; GHL message `c9vhcydCCtoSV3hs6wQZ`.
- Anthony Riley replay: contact `iTH9FZpgiqZgrLRUACvW`; GHL conversation `NVqlWtYpYDCrUZNVg0Vb`; GHL message `J1UZapNyJEHEEwus4k0V`.
- LinkedIn inbound executions `986969` and `986971` completed successfully with `status=processed`.
- OAuth renewal verification execution `986997` completed successfully: GHL HTTP 200, `expires_in=86399`, new active token row `42`, expiry `2026-09-25T11:36:12.632Z`.
- Empty-queue retry verification execution `987023` completed successfully through claim, token context, no-token branch, and finalization; no outbound GHL message was sent.
- Scheduled renewal verification execution `987233` ran at `2026-09-24T13:00:00Z` and completed successfully; the refreshed active token was stored with expiry `2026-09-25T13:00:00Z`. No token value is recorded.
- Current live state: inbound, OAuth renewal, and retry workflows are active and `versionId == activeVersionId`. OAuth schedule remains `0 */6 * * *`; retry schedule is `10 */6 * * *`.

## Next session

1. Confirm the next scheduled OAuth renewal execution succeeds at the next six-hour boundary.
2. If it fails, inspect the node-level execution before changing the workflow again.
3. Keep the OAuth refresh-token alert path in place and monitor the first natural 401 queue/replay cycle.

No secrets or token values are recorded here. Do not stage unrelated worktree changes.
