# Vertical LinkedIn Connection + DM Workflow — Design and Build Gate

Date: 2026-10-13

## Request and decisions

Build one LinkedIn outreach system for all eight October vertical cohorts. Ed clarified:

- Round-robin means rotate between vertical queues in this order: Alcohol → Cannabis → Cannabis Dispensaries → Crypto → Gambling → Mushroom → Nicotine → Peptides.
- Use the existing LinkedIn account for connection requests, enforcing the existing account-wide ceiling of 20 requests/day in `America/Los_Angeles` and 5/hour.
- After a verified connection, use each vertical's PDF-specific DM copy through Sales Navigator.
- Create inactive n8n-lt drafts only; do not publish, activate, execute, send, enroll, tag, or alter existing workflows.

## Source copy reviewed

All eight files in `New Campaigns October 2026/` were read. Each has one Day 0 LinkedIn connect note plus LinkedIn DM 1 (Day 9) and DM 2 (Day 17). Notes and DMs are vertical-specific; use the exact strings in each source PDF rather than deriving copy from a common template. Mapping:

| GHL Vertical | Source PDF |
|---|---|
| Alcohol | `Alcohol - Multi Channel Outbound Sequence.pdf` |
| Cannabis | `Cannabis Brands - Multi Channel Outbound Sequence.pdf` |
| Cannabis Dispensaries | `Cannabis Dispenseries - Multi Channel Outbound Sequence.pdf` |
| Crypto | `Crypto - Multi Channel Outbound Sequence.pdf` |
| Gambling | `Gambling - Multi Channel Outbound Sequence.pdf` |
| Mushroom | `Mushroom - Multi Channel Outbound Sequence.pdf` |
| Nicotine | `Nicotine - Multi Channel Outbound Sequence.pdf` |
| Peptides | `Peptides - Multi Channel Outbound Sequence.pdf` |

For the eight verticals, the PDFs place LinkedIn DM 1 on Day 9 and LinkedIn DM 2 on Day 17 (eight PDFs all follow that schedule). Preserve those relative delays from campaign entry, but gate each send on connection state and stop on any reply, suppression, or identity ambiguity.

## Proposed architecture

Create two separate, inactive workflows in **n8n-lt**:

1. **Vertical LinkedIn Connection Dispatcher** — periodic queue scan; eligible contacts are selected from the eight vertical-specific queues, one vertical at a time in persistent round-robin order. Before a Classic connection request, validate the exact LinkedIn identity, skip already connected/requested/suppressed contacts, check provider/account health, and atomically enforce both rolling 60-minute (max 5) and Pacific-day (max 20) limits across all invite sources. Persist request intent/result idempotently; on uncertain provider outcomes, hold for reconciliation and never blindly retry.
2. **Vertical LinkedIn Sales Navigator DM Sequence** — process only verified first-degree connections with a resolved GHL contact and vertical. Send PDF-specific DM 1/2 on their eligibility dates through a Sales Navigator thread, recording message IDs and per-contact step state idempotently. Suppress on inbound reply, stop/DNC, stale identity, failed lookups, or unresolved send outcome. Do not fall back to Classic for DMs.

The existing reply/suppression, LinkedIn connection-state, shared profile index/claim, and Sales Navigator message-event facilities should be reused where their live contracts match. The existing disconnected Classic dispatcher and DM sequence remain untouched during this build.

## Live-state readback

Read-only n8n-lt REST checks (correct instance; no key values printed):

- Readiness endpoint returned `status=ok`.
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is inactive; latest saved version `65a7398b-328c-4f99-b709-ee2da1bc6683`; no active version.
- `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) is inactive; latest saved version `6e301f91-ec2c-4c86-a434-da034c74591e`; no active version.
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) is active and unchanged at `4cf9b218-0edd-41f1-88f3-b5d9a4e7ad94`.
- `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) is active and unchanged at `436a54d0-7bd4-47a5-8bb0-e9b158dab5d0`.
- Existing Sales Navigator gateway and bridge versions are documented in `n8n/sales-navigator/WORKFLOW_BUILD_SPEC.md` and `docs/sessions/2026-10-01-sales-navigator-final-audit.md`.

The current handoff at the top of `AGENTS.md` reports the V2 account's Sales Navigator product disconnected and the n8n execution queue stalled at 250 `new` executions. Re-check both before any workflow validation or activation.

## Why no n8n draft was created in this session

The existing Sales Navigator outbound gateway only sends follow-ups to a previously mapped chat (`POST /v2/{account}/chats/{chatId}/messages/send`). It does not start a chat. The documented start-chat endpoint is available in the design notes, but the *connected first-degree recipient* path and payload have not been verified end-to-end on this account. The account's Sales Navigator feature is currently reported disconnected. A saved-but-inactive workflow could be authored with an unverified external API operation, but would not be a validated, usable draft. No workflow was created, updated, executed, published, or activated.

## Required before build validation

1. Reconnect Sales Navigator for the existing V2 account; confirm status `running` and read-only resolve a known first-degree recipient in `SALES_NAVIGATOR_PRIMARY`.
2. Verify Unipile's connected-first-degree start-chat request shape (no InMail subject/credit) against current official API docs and an isolated, non-sending contract check. Any actual message test is a production send and needs separate approval.
3. Inspect all vertical contacts' LinkedIn identity and current connection state read-only; define exact eligible counts by vertical. A contact lacking a valid, unique LinkedIn profile/provider ID cannot receive a request.
4. Implement shared atomic pacing across the existing and new send paths. The previous 20/day, 5/hour rule is explicitly account-wide; per-workflow counters are insufficient. Keep all LinkedIn senders inactive while this enforcement is developed and verified.
5. Confirm identity/source mapping for vertical labels, handling existing duplicate contacts, and DM schedule anchor (campaign-entry date vs connection-accepted date). The PDFs specify sequence Day 9/17 from entry, but a late accept must not cause an immediate catch-up burst; use next eligible scheduled step after acceptance unless Ed directs otherwise.
6. Build two inactive workflows, validate graph/config offline, inspect saved node definitions, and verify both remain `active=false`. Only after that should any future user request authorize execution/publication.

## Safety boundary

No messages/invites, contact changes, state writes, tags, enrollment, account reconnect, workflow mutation, or publication occurred in this session. Use only `n8n-lt`; never use the Katwill n8n connector. Do not modify the active connection-state sync or reply suppression workflows as a side effect of this work.

## Addendum — GHL Marketplace Sales Navigator app redirect diagnosis (2026-10-13)

- Ed supplied the GHL Standard install URL for app `6abd41c58a3e9cb4acdbc555-muofh6mn`; it uses redirect URI `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`. The GHL developer page shows that URI selected, plus `https://automations.livetransparent.com/rest/oauth2-credential/callback` as another registered redirect.
- Fresh `n8n-lt` readback of active gateway `ZiYEBuP7xdddhnUB`: GET `/lt-sales-navigator-provider` enters `Validate Callback or Provider`, but that Code node has no `/oauth/token` exchange and no token persistence. POST on the same path is the signed provider delivery handler. Recent execution listing was empty; the workflow saves execution data, so no callback run was evidenced in that listing.
- This confirms the selected `webhook/lt-sales-navigator-provider` URL is **not currently a complete Marketplace OAuth redirect handler**. Changing the URL to n8n's native OAuth credential callback without initiating the matching n8n credential OAuth state is not verified either.
- `Config` on the gateway includes GHL app client ID/secret, redirect URI, and location ID; the existing Postgres `ghl_oauth_tokens` table stores access/refresh tokens and has a global `active` flag. Do not insert a Marketplace token into that table or change its active row without tracing consumers and deciding how this app's token should be isolated; doing so could change the token used by other workflows.
- No GHL app configuration, workflow, credential, OAuth grant, or token table was changed. Browser access to GHL Developer Marketplace was unavailable. Next: implement a dedicated, state-validated OAuth callback with an isolated token-storage/credential contract; add that exact redirect URI to the Marketplace app; then reinstall and verify the callback/token and location install. Keep the provider POST endpoint separate. No OAuth authorization code, access token, refresh token, or client secret was logged.
