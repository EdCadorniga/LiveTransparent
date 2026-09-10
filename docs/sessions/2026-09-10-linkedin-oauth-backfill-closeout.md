# LinkedIn OAuth and Message Backfill Closeout

Updated: 2026-09-10

## Objective

Restore the GHL OAuth installation path used by the social inbox and backfill the prepared historical LinkedIn conversations into GHL Conversations without sending outbound LinkedIn messages.

## Completed

- Reinstalled `Transparent eCom Social Inbox` for the Live Transparent location.
- Verified OAuth authorization and token exchange through the existing social-provider route in execution `930484`; the exchange returned HTTP 200 and a fresh token was stored in `ghl_oauth_tokens`.
- Confirmed the canonical social route is intentionally multiplexed:
  - `GET /webhook/lt-social-provider-outbound`: OAuth installation callback.
  - `POST /webhook/lt-social-provider-outbound`: LinkedIn/Instagram provider delivery.
- Updated the inactive `LT - LinkedIn Conversation Backfill` workflow (`JUvrA7qMa24SwAZG`) to read the current OAuth token from `ghl_oauth_tokens` using the `Postgres account` credential instead of its embedded stale token.
- Removed the stale token assignment from its `Config` node.
- Fixed the backfill `Summarize` Set-node expressions after the first run exposed an invalid-expression error.
- Ran the prepared five-chat backfill manually as execution `930588`.

## Backfill Result

- David Schachter: 1 message posted.
- Julia Granowicz-Johnson: 1 message posted.
- Azeez Agunbiade: 1 message posted.
- Morgan Ruzowitzky: 3 messages posted.
- Gretchen Gailey: 0 messages posted; 2 outbound historical messages returned HTTP 422 from GHL.
- Total posted: 6 messages.

The execution is marked `error` only because the final summary node failed before its expression fix. The `Backfill Conversations` node itself completed successfully and reported the six posted messages. The workflow was not rerun because it is not idempotent and a rerun could duplicate the six successful messages.

## Current Live State

- Social Provider Outbound Router (`kqIi8i1RjFAZKrK3`) remains active.
- GHL OAuth Callback (`UnSWPnVoUy3tNJkX`) remains active on `/webhook/oauth-callback`, but this app does not use it for installation callbacks.
- LinkedIn Conversation Backfill (`JUvrA7qMa24SwAZG`) remains inactive and is not scheduled.
- No production outbound LinkedIn sender was executed.
- No executions were left in `new`, `running`, or `waiting` at closeout.

## Blockers and Risks

- Gretchen's two HTTP 422 failures need targeted request/body diagnosis before retrying. Do not rerun the full five-chat workflow.
- The historical backfill workflow still has hardcoded chat IDs and uses a non-idempotent message-posting path. It should not be broadened or rerun without adding message-level deduplication.
- Backfilled messages are expected to be reply-capable because they use the canonical `LinkedIn via Unipile` provider ID and original Unipile chat IDs. A controlled reply test remains outstanding.

## Next Steps

1. Inspect the two Gretchen 422 responses and determine whether they are unsupported historical outbound messages, payload-shape errors, or existing-message conflicts.
2. If needed, add idempotency checks before retrying only the failed messages.
3. Perform one approved, controlled reply from the GHL Conversations screen against a successfully backfilled chat and verify the provider outbound router receives and delivers it.
4. Only after that verification consider any broader historical backfill scope.
