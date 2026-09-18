# GHL OAuth Renewal Hardening — 2026-09-19

## Outcome

The GHL OAuth connection was reauthorized and token renewal was verified end to end. Nine identifiable inbound LinkedIn messages from the last seven days were recovered into GHL Conversations and the Executive Report. No LinkedIn outreach was sent.

## Live changes

- `LT - GHL OAuth Token Refresh` (`Mf4wdFNurt5vyQu4`) is active and published at version `3ee6b021-c45b-47cc-a428-d1b7f8fb9e15`.
- The schedule now runs every six hours (`0 */6 * * *`).
- The workflow validates the source refresh token, HTTP status, response body, access token, and minimum expiry before database rotation.
- Invalid or missing renewal responses now resolve `edmundocadorniga@gmail.com` as a GHL contact, send a failure email from the authenticated `.com` sender transport, and then fail the execution instead of being reported as a successful n8n run. The email includes the sanitized failure details, the uninstall/reinstall recommendation, and the GHL app renewal link. The former Slack alert node was removed.
- Token storage only deactivates the prior active token after a validated replacement is available. Rotated refresh tokens are persisted.
- A direct refresh test returned HTTP 200, stored a new active token, and the resulting GHL location-token exchange returned HTTP 201 with an access token.

## LinkedIn inbound/reporting repair

- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active and published at version `49defb77-336f-43c5-92dc-71d87c3810de`.
- `Build Find State SQL` now obtains inbound/account context from the normalized Unipile event when the upstream map-upsert output does not carry those fields. This removes the erroneous `WHERE false` branch that suppressed conversation-state updates and `reply_received` reporting events.
- The same state lookup now falls back to a real `linkedin_conversation_map` contact when no non-synthetic state row exists. This preserves fail-closed behavior for an unidentified profile while allowing mapped contacts to produce report events.
- Both live workflows passed JavaScript syntax checks after publication.

## Seven-day message recovery

- Unipile inventory found 10 inbound messages from 2026-09-12T00:00Z through the recovery run.
- Nine were matched to existing GHL contacts and recovered: AL CARON (1), Dan Tramontozzi (1), Arafat Hossain (1), Eric Caron (4), Drew Barrett (1), and Matias Plager (1).
- GHL content verification found each recoverable message exactly once; the nine corresponding `reply_received` rows now exist for the real GHL contacts.
- Replies recovered through a conversation-map-only match are recorded as `linkedin_unattributed`; no historical campaign was inferred from a weak or synthetic state row.
- Executive Summary smoke test returned HTTP 200 with a populated 35,976-byte response. Its default 30-day window currently ends on 2026-09-17, so the 2026-09-18 AL event is outside that default window until the report rolls forward or a custom end date includes it.
- A custom Executive Summary request for 2026-09-12 through 2026-09-18 returned HTTP 200 with 28,338 bytes and reported `inboundReplies=9` and `uniqueResponders=6`.
- One `no thanks` message remains unrecovered because Unipile returned an unidentified/locked LinkedIn profile and there was no unambiguous GHL contact match. It was not guessed or assigned.
- A temporary duplicate created during recovery for Eric and Matias was removed by deleting only their newly-created empty custom-provider conversations, then recreating the messages once. No other contact/channel conversations were deleted.

## Local maintenance

- Corrected `scripts/n8n/refresh_ghl_oauth_token.py` so it resolves the project-level `.env` from `scripts/n8n` correctly. The corrected helper completed a refresh successfully.

## Remaining follow-up

- The latest scheduled execution `964056` at `2026-09-18T19:00:00Z` failed at `Check Refresh Token Source` with `Could not get parameter "jsCode"`. A current read-only workflow GET shows non-empty `jsCode` on every Code node, so this is recorded as an unresolved runtime/cache discrepancy rather than a confirmed logic defect. No manual OAuth-failure replay was run during EOS.
- Next session: inspect the next scheduled run and node-level data. If the same error recurs, investigate/reload the active workflow under explicit approval before changing renewal logic; if it succeeds, verify token storage and the fail-closed email route.
- Resolve the unidentified `no thanks` sender only if a reliable LinkedIn-to-GHL identity match becomes available; do not infer it from the first name in the preceding outbound message.
