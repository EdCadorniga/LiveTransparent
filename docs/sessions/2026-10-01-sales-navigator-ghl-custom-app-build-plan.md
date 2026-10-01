# Sales Navigator GHL Custom App Build Plan — 2026-10-01

## Goal

Create a separate HighLevel Marketplace app and custom conversation provider for Unipile V2 Sales Navigator account `acc_01m3sefk22e8jvnmvvfx333pye`. Keep the Classic app, account, and history. At cutover, stop Classic-to-GHL inbound and outbound routing so GHL Conversations contains Sales Navigator messages only.

## Verified progress this session

- Created and activated `LT - Sales Navigator Provider Gateway (DRAFT)` (`ZiYEBuP7xdddhnUB`, 5 nodes, active version `196bb492-e9c0-402e-876d-69ea54b70064`) and `LT - Unipile Sales Navigator V2 Inbound (DRAFT)` (`CfpedDQWxoJLEMdL`, 4 nodes, active version `b94e4e4d-ed9f-40ea-84c9-5df9eb84801e`). REST readback confirmed `versionId == activeVersionId` for both. Both use dedicated Set-node `Config` patterns; inbound raw-body capture is enabled and the signing-secret field is blank. Gateway fails closed before OAuth exchange/outbound send; inbound verifies signature/account/direction before failing closed because map/idempotency and GHL posting are not wired. No tests or live requests were run. Read-only Unipile endpoint query returned HTTP 200 and 0 endpoints. Do not install the app or register webhooks against these scaffolds.
- Existing SimpleTexting workflow inspected read-only to confirm the Community Edition Config-node pattern. No existing workflow was modified.

- User created a distinct SMS custom conversation provider. Provider ID: `6abd56db3e5dc9f056868ad2`.
- User supplied Marketplace Client ID `6abd41c58a3e9cb4acdbc555-muofh6mn`; a local, value-redacted check confirmed it matches `.env` variable `CLIENT_ID_SALESNAVIGATOR`.
- User reported completing app Auth details and adding the redirect URI `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`. The provider creation succeeded afterward, but portal settings were not independently inspected.
- Scope screenshot showed `contacts.readonly`, `contacts.write`, `conversations.readonly`, `conversations.write`, `conversations/message.readonly`, and `conversations/message.write` selected. User removed `conversations/reports.readonly`. Reconfirm whether `contacts.write` is needed before install.
- User reported that the formerly exposed GHL Marketplace client key and n8n API key are revoked. The old `.env` key variable `N8N_API_KEY_LT` was removed; replacement `N8N_LT_API_KEY` is present. Old SimpleTexting-named Marketplace variable names were corrected to `CLIENT_ID_SIMPLETEXTING` / `CLIENT_SECRET_SIMPLETEXTING`; Sales Navigator names `CLIENT_ID_SALESNAVIGATOR` / `CLIENT_SECRET_SALESNAVIGATOR` are present. Values were not printed or written to repo docs.
- Read-only direct REST inspection confirmed existing workflow state: `LT - GHL OAuth Callback` (`UnSWPnVoUy3tNJkX`) active/published at `fe7b45cd-6f70-474a-9c62-c1204161150f`; `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) active/published at `4a688b2b-540e-401b-8bdf-8909172c138a`; `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) active/published at `e09111d7-2c63-4925-b335-741c57f5ab5d`.
- Two new Sales Navigator workflow scaffolds were created and activated as explicitly requested later in this session. No existing Classic/Instagram/LinkedIn workflow was changed. No Unipile webhook was registered, no app installation/token exchange occurred, and no GHL/LinkedIn message or contact was written/created. No runtime tests were performed.
- n8n MCP lookup did not resolve the existing production workflow IDs; direct REST reads using the replacement key succeeded. Avoid displaying credentials in future output.

## Target design

1. Dedicated GHL OAuth callback + provider outbound route at `/webhook/lt-sales-navigator-provider`; accept only provider ID `6abd56db3e5dc9f056868ad2`.
2. Separate Unipile V2 inbound route at `/webhook/lt-unipile-sales-navigator-new-messages`; subscribe to `message.new` only, account-scoped to `acc_01m3sefk22e8jvnmvvfx333pye`.
3. Validate Unipile HMAC using the exact raw request body and timestamp; validate event type, exact account, incoming direction, and stable message/event ID before processing.
4. Maintain a V2-only identity/chat map covering V2 account, Sales Navigator provider profile, Unipile chat ID, GHL contact ID, and GHL conversation ID. Enforce uniqueness/idempotency. Never reuse Classic account or map identifiers.
5. Reply to an existing Sales Navigator thread using its Unipile chat ID. Start new Sales Navigator chats through `SALES_NAVIGATOR_PRIMARY` only after profile/chat resolution.
6. Do not migrate Classic history or create a contact during the test unless the mapping is confirmed and separately approved.

## Important implementation constraints

- n8n Community Edition Code nodes cannot read `.env` directly. Use the established SimpleTexting-style `Config` Set node for the dedicated OAuth client secret and Unipile API key; these values are visible in the workflow definition, so restrict workflow access and never print/commit them. The webhook signing secret is unavailable until endpoint registration; leave it blank and fail closed until it is added directly to Config after the separate registration approval.
- The Unipile webhook signing secret is generated/available only after registering the endpoint. Add it to the protected runtime configuration without exposing it.
- The GHL callback URL and OAuth redirect URI must match exactly. Provider callback/redirect settings were not independently verified in the portal this session.
- Current provider should remain additional SMS custom channel (“Custom Conversation Provider” and “Always show” enabled), not the location’s default SMS provider.

## Remaining steps — ordered

1. **Finish the active scaffolds:** implement OAuth state/token exchange and persistence plus outbound V2 map lookup/send in `ZiYEBuP7xdddhnUB`; implement V2 map/idempotency and GHL inbound post in `CfpedDQWxoJLEMdL`. Do not modify Classic/Instagram/LinkedIn workflows.
2. **Implement persistence and validation:** apply the V2 map/idempotency schema; fail closed on missing/ambiguous map, provider mismatch, account mismatch, invalid signature, non-inbound message, or duplicate event. Keep test-contact creation disabled. The inbound Config currently contains only its account/provider/signature-age settings plus a blank signing secret; add any required GHL token/OAuth settings when wiring the post path.
3. **Offline/pinned validation:** validate OAuth callback parsing without exchanging a real code; test correct/incorrect provider IDs, account IDs, direction, stale/bad signatures, duplicate message IDs, malformed payloads, and safe errors. Do not post to GHL or send to LinkedIn.
4. **Portal verification:** confirm the new provider’s exact delivery URL and redirect URI are both `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`; confirm provider flags and review the selected scope set, especially `contacts.write`. Do not install until workflow configuration is ready.
5. **Webhook gate:** after the workflows are complete and validated, register a Unipile V2 webhook for `message.new`, restricted to the Sales Navigator account. Add the endpoint signing secret to Config and verify delivery without replaying historical events. Workflow activation has already been explicitly authorized and completed.
6. **Live smoke test gate:** obtain explicit approval immediately before one inbound and one outbound test on the approved mapped GHL contact/thread. Verify same V2 chat, correct provider tab, persistent map, and idempotency. Do not create contacts or backfill history during this test.
7. **Cutover gate:** only after both directions pass, disable/filter Classic-to-GHL inbound and outbound paths. Retain the Classic app/account/history. Verify Classic events are excluded and V2 messages appear only under the new provider.

## Safety boundaries

- User reports that both exposed old credentials are revoked; do not repeat their values. Inspect Git/execution/log retention for residual exposure as separate credential hygiene work.
- Do not install the app, grant/expand scopes, register the Unipile webhook, write a message to GHL, create/update contacts, send a LinkedIn message, or disable Classic routing without explicit approval at that step. Workflow activation was explicitly approved and completed for the two new fail-closed scaffolds only.
- No historical message backfill or Classic-to-V2 migration is in scope.

## Documentation

- [HighLevel Conversation Providers](https://marketplace.gohighlevel.com/docs/2023-02-21/marketplace-modules/ConversationProviders/)
- [HighLevel Provider Outbound Message](https://marketplace.gohighlevel.com/docs/webhook/ProviderOutboundMessage/)
- [Unipile V2 webhooks](https://developer.unipile.com/v2.0/docs/configure-a-webhook)
- [Unipile V2 migration webhooks](https://developer.unipile.com/v2.0/docs/migration-webhooks)
