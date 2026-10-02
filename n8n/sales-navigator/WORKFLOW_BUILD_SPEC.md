# Sales Navigator V2 n8n workflows

**Historical build checkpoint:** This document's version numbers, credential ID, and statements that no live messages were validated predate the 2026-10-01 live verification. Use [`../../docs/sessions/2026-10-01-sales-navigator-final-audit.md`](../../docs/sessions/2026-10-01-sales-navigator-final-audit.md) for current deployed state and the next-session repair plan. Retain the design detail below as implementation history.

**Attachment transport (session 4, 2026-10-01):** one attachment per message, 4 MB cap. Outbound is inline in the gateway (`Fetch GHL Attachment` + `Build V2 Attachment`, GHL host allowlist). Inbound is proxied by `services/sales_navigator_media` (bridge fetches with its Unipile credential, posts bytes to `POST /sales-navigator-attachments/v1/store`, GHL fetches the returned URL). Current node counts: gateway `ZiYEBuP7xdddhnUB` 24 nodes, bridge `CfpedDQWxoJLEMdL` 74 nodes.

**Messaging semantics — follow-ups only, no subject (2026-10-02):** The gateway only sends into an **existing** Sales Nav chat (`POST /v2/{account}/chats/{chatId}/messages/send`, body `{ text, attachments }`, no `subject`) and cannot start a new conversation — `Find V2 Contact Chat` fails closed without a `sales_navigator_v2_conversation_map` row. Per LinkedIn/Unipile docs, a **new** Sales Nav conversation to a **non-connection is an InMail that requires a subject and costs 1 credit**, whereas messaging a **1st-degree connection** in an existing thread needs neither. GHL's Custom (SMS-type) provider payload carries no `subject`, so any future Sales Nav InMail initiation (via `POST /v2/{account}/inboxes/SALES_NAVIGATOR_PRIMARY/chats/send` with `options.linkedin.sales_navigator.subject`) would require a designed subject source. Policy: connection requests stay on Classic; message only 1st-tier; do not start Sales Nav conversations. Detail: [`../../docs/sessions/2026-10-02-sales-navigator-messaging-rules-and-team-note.md`](../../docs/sessions/2026-10-02-sales-navigator-messaging-rules-and-team-note.md).

Current state: both dedicated workflows are wired and active on `n8n-lt`; the shared index and workflow schemas are applied. The user connected the GHL OAuth2 credential in n8n. Unipile V2 endpoint `we_01m3taxyc3e4e8ayvk7aqazvnv` is enabled for `message.new`, scoped only to Sales Navigator account `acc_01m3sefk22e8jvnmvvfx333pye`, and targets the inbound workflow. Its signing secret is configured directly in the inbound Config node. The one-time schema/index migration ran, but no inbound message workflow execution, message send, GHL record write, or controlled validation has occurred.

## Fixed identifiers and credentials

- GHL custom provider: `6abd56db3e5dc9f056868ad2`
- GHL Marketplace client: `6abd41c58a3e9cb4acdbc555-muofh6mn`
- Provider callback and outbound delivery URL: `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`
- Unipile V2 account: `acc_01m3sefk22e8jvnmvvfx333pye`
- Inbound webhook path: `/webhook/lt-unipile-sales-navigator-new-messages`
- GHL OAuth2 credential: `LT Sales Navigator GHL OAuth2` (`zuOARvZFtLm6iIWu`); user reports it is connected.
- Unipile V2 header credential: `LT Sales Navigator Unipile V2 API` (`xfQeYq9i3A0TrEnT`).
- Postgres credential: `Postgres account` (`pgAzUqpwOiGkGXzO`).
- The user explicitly wants project secrets retained in the n8n Config node. Do not print their values in output, logs, or docs.

## Workflow A — provider gateway

`LT - Sales Navigator Provider Gateway (DRAFT)` (`ZiYEBuP7xdddhnUB`) is active at version `f8cb7997-1e74-458a-ba63-7a4c97426419` (15 nodes; `versionId == activeVersionId`). Success/error/manual execution data saving is disabled.

The POST path preserves raw bytes, verifies HighLevel's Ed25519 `X-GHL-Signature`, then parses and validates the documented `locationId`, `contactId`, `messageId`, SMS type, text, and attachment shape. It requires one V2 map row for the contact, optionally narrowing by `replyToAltId` when HighLevel provides it. It claims the GHL message ID in the V2 event ledger before sending through `POST /v2/{account_id}/chats/{chat_id}/messages/send`, using the restricted Unipile credential. It never creates a chat or GHL contact. Duplicate claims return a sanitized acknowledgment.

If the Unipile request times out or the workflow stops after the claim, the event remains `processing`; retries do not send again. Reconcile that row against Unipile before any manual resend. This avoids blind duplicate LinkedIn sends.

The separate GET route is still not an OAuth code-exchange endpoint. OAuth tokens are managed by the encrypted n8n OAuth2 credential.

## Workflow B — Unipile message bridge (inbound and outbound)

`LT - Unipile Sales Navigator V2 Inbound (DRAFT)` (`CfpedDQWxoJLEMdL`) is active at version `fb85cb53-b266-4d48-9cb8-7895ad93187c` (52 nodes; `versionId == activeVersionId`). Success/error/manual execution data saving is disabled. Its webhook signing secret is configured in Config. Endpoint `we_01m3taxyc3e4e8ayvk7aqazvnv` is enabled for `message.new`, scoped to account `acc_01m3sefk22e8jvnmvvfx333pye` only.

The handler verifies `unipile-signature` HMAC over `${timestamp}.${rawBody}`, freshness (300 seconds), event type `message.new`, and exact account, then branches on `is_sender`. For inbound messages it fetches the sender's Sales Navigator profile, then uses the shared `linkedin_contact_profile_index` and `linkedin_contact_profile_claims`. A unique match reuses the GHL contact; duplicate profile matches fail closed; when no match exists, only the claim owner creates the contact. The new contact's profile URL, name, and provider ID are written to the shared index before conversation/message writes. The V2 map is then upserted, event/message IDs claimed, the webhook acknowledged, and `type: Custom`, `direction: inbound` posted through the dedicated OAuth credential.

For messages sent from Sales Navigator (`is_sender=true`), the workflow first resolves the existing V2 chat map. If no map exists, it reads recent chat messages, identifies the other participant from a received message, fetches that Sales Navigator profile, and matches its normalized profile/provider ID against the shared index. It creates a map only when exactly one GHL contact matches; unknown and ambiguous contacts fail closed without creating a contact. The event/message IDs are claimed in the same ledger used for inbound messages, then the external message is posted to GHL through the [custom-provider inbound-message endpoint](https://marketplace.gohighlevel.com/docs/2021-07-28/ghl/conversations/add-an-inbound-message/index.html) with `direction: outbound` and the V2 chat ID as `altId`. HighLevel documents that endpoint supports an explicit message direction, including outbound; [Unipile documents](https://developer.unipile.com/v2.0/reference/event-types-1) `message.new` for messages both received and sent. The sent message that prompted this update was not replayed or backfilled.

Both Classic LinkedIn and Sales Navigator workflows use the same profile-key claim. A second message for the same profile waits up to 10 seconds for the claim owner's index update and reuses that contact; it never enters contact creation while a claim is pending. Pending claims have no automatic expiry: if processing stops after GHL contact creation but before index persistence, check GHL and the claim row before manual recovery. This intentionally favors duplicate prevention over automatic claim stealing.

Duplicate events do not post again. If a request times out or the workflow stops after acknowledgment, reconcile the ledger and GHL conversation before any retry. Unknown or ambiguous identities fail closed. The existing Classic map is only used to verify LinkedIn profile-to-contact identity; its account rows and workflows are not altered.

## Legacy LinkedIn inbound contact matching

The separate legacy workflow `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) uses this same indexed table and claim mechanism. At claim ownership it preserves the existing contact-create fallback and immediately writes the created contact's profile details before posting the inbound message. Current active version: `8a22c193-3702-4257-bd28-ebd6c6efe720`.

## Database

`sales_navigator_v2_conversation_map` and `sales_navigator_v2_message_events` from [`sales_navigator_v2_schema.sql`](sales_navigator_v2_schema.sql), plus the shared indexed contact profile and claim tables from [`../../postgres/linkedin-contact-profile-index.sql`](../../postgres/linkedin-contact-profile-index.sql), are applied to production Postgres. OAuth tokens are held by the encrypted n8n credential, not in these tables. No historical message backfill is included.

Read-only inspection found 61 existing Classic-account LinkedIn profile/contact mappings, with each profile and contact unique. Their provider IDs are now seeded into the shared contact index. The inbound V2 workflow creates a GHL contact only when the shared index has no exact match and the profile claim is acquired.

## Remaining steps

Next: verify the connected OAuth grant targets the intended GHL location and includes `contacts.write`, and confirm the custom provider is installed/available there. Then perform controlled inbound and outbound validation before broader use. New unmatched inbound senders can create contacts, so live validation depends on that write scope; manually sent outbound messages require a unique mapped/indexed contact and fail closed otherwise. No workflow event or GHL write was run during this update. Do not put the webhook secret in chat, repository files, or execution data. No Classic cutover or historical backfill is included.

## Build/update script

[`scripts/n8n/wire_sales_navigator_v2_workflows.py`](../../scripts/n8n/wire_sales_navigator_v2_workflows.py) updates only these workflows through `n8n-lt`. It does not install the Marketplace app, register a webhook, or send messages.
