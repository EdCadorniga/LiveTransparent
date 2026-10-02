# Sales Navigator messaging rules + team note — 2026-10-02

## Objective

Confirm, from LinkedIn Sales Navigator documentation plus our own tests, the InMail rules that govern our outreach design, and produce an internal (Slack) note for the team. This was a **read-only / knowledge session**: no n8n workflow was changed, published, or activated; no message was sent; no CRM record was written; nothing was committed or pushed. Worktree was clean at session start.

## Verified rules (documentation-backed)

Sources: LinkedIn Help *Understand InMail credits in Sales Navigator* (`help/sales-navigator/answer/a101030`) and *InMail message credits and renewal process* (`help/linkedin/answer/a543695`); Unipile docs *Start a Chat from Inbox* (`developer.unipile.com/v2.0/reference/startchatfrominbox`) and *Send messages with Sales Navigator* (`developer.unipile.com/v2.0/docs/linkedin-send-messages-with-sales-navigator`).

- **InMail to a non-connection:** lets you message anyone you are not connected to; **costs one InMail credit** and **requires a subject line**. Members with an **Open Profile** can be messaged for free (no credit).
- **Credits:** Sales Navigator (Core/Advanced/Advanced Plus) allocates **50/month**, granted on the **1st of the month (UTC)**, with a **maximum accumulated balance of 150**. You **cannot purchase** additional credits. Unused credits roll over month-to-month up to the 150 cap.
- **Refund:** a credit is refunded for any InMail **responded to within 90 days** — accepted, declined, or replied (including auto-replies / Quick Replies). Ignored/pending InMails are not refunded.
- **Decline mechanics:** the recipient taps a one-tap **"Not interested"** quick reply (shown as **"No thanks…"** in some LinkedIn UIs), or sends a negative text reply that LinkedIn's AI classifies as a decline. A decline still refunds the credit. A decline with only the templated quick reply (no text) closes the thread (a new InMail is needed to restart); declining with text, or replying afterward, keeps the conversation open.
- **1st-degree (connected):** messages are regular LinkedIn messages — **no credit and no subject**.
- **Thread separation:** Sales Navigator runs through a separate account from Classic, so a Sales Nav message opens **its own conversation thread** and does not continue/merge the Classic thread.
- **Starting a new Sales Nav conversation to a non-connection requires a subject** (`SALES_NAVIGATOR_PRIMARY` inbox + `options.linkedin.sales_navigator.subject`). This is **documentation-backed and consistent with our tests, but not yet proven by our own end-to-end non-connection test.**

## Evidence from our own bridge and tests

- The gateway sends **follow-ups only**: `POST /v2/{account}/chats/{chatId}/messages/send` with body `{ text, attachments }` — **no subject field** (`scripts/n8n/wire_sales_navigator_v2_workflows.py:385`).
- The gateway **never starts a chat**. `Find V2 Contact Chat` requires an existing `sales_navigator_v2_conversation_map` row; otherwise it fails closed (404/409). So it can only send into an already-mapped Sales Nav chat.
- The repo's gateway test send is text-only: `unipile("/send", {"text": TEXT})` (`scripts/n8n/reconcile_gateway_test_message.py:90`).
- The 2026-10-01 test conversation was with Cameron (a **1st-degree** connection, no "InMail" badge in the inbox list, no subject header in the thread). It confirms regular connected messaging and does **not** exercise the InMail path.

## Decision / operating policy

- **Connection requests go via Classic** (through n8n). Once a person accepts and we are connected, we message them as a **1st-tier connection** (no subject, no credit).
- **Do not start new conversations via Sales Navigator.**
- If we ever want to **initiate contact** via Sales Navigator (to a non-connection), it must run through **n8n**, because a new Sales Nav InMail requires a subject.

## Team note (final Slack text sent for review)

> **How our LinkedIn messaging works across Classic and Sales Navigator**
>
> Hi team,
>
> I want to lay out how our LinkedIn outreach is set up right now and the rules that apply, so we're all working from the same picture. Right now, **both channels are live**: Classic (LinkedIn via Unipile) and LinkedIn Sales Navigator.
>
> **Our rule: only message people once we're connected (1st-degree).** Please **don't start new conversations through Sales Navigator.** We only message people once they're a 1st-degree connection. For 1st-degree connections, messages are regular LinkedIn messages — they use no InMail credits, have no credit cap or refund window, and need no subject line. Connection requests go out via Classic; once the person accepts and we're connected, we message them as a 1st-tier connection.
>
> **What Sales Navigator InMail is (context only).** Sales Navigator can message people we're **not** connected to. Those are InMails, and per LinkedIn's and Unipile's documentation, each one costs an InMail credit and **requires a subject line**. Members with an Open Profile enabled can be messaged free. We are not initiating these from our bridge today.
>
> **InMail credits and their limits.** We can hold a maximum of 150 credits. We can't buy more — the balance is topped up automatically with 50 credits on the first of each month, and any unused credits roll over month to month up to that 150 cap. The credit is refunded if the recipient responds within 90 days, whether they accept, decline, or simply reply. If they ignore the message, it stays pending and we don't get the credit back.
>
> **How a recipient declines.** There's no formal decline like a rejected connection request — it happens inside the InMail thread. The recipient taps a one-tap "Not interested" quick reply (shown as "No thanks…" in some LinkedIn interfaces), or types a negative reply that LinkedIn's AI classifies as a decline. A decline still counts as a response, so we get the credit back. If they decline using only the no-text quick reply, we can't reply in that same thread and would need a new InMail to restart; if they add text or reply afterward, we can continue the conversation.
>
> **Sales Navigator is a separate thread from Classic.** Sales Navigator runs through a separate account from Classic, so a Sales Navigator message opens its own conversation thread and does not continue or merge into the thread from messages we previously sent from Classic. The recipient sees a fresh thread rather than a reply on top of our existing Classic exchange.
>
> **Connection requests.** Connection requests are sent via Classic, through n8n. Classic will eventually be switched off, but connection requests may still be sent via Classic (through n8n) even after that point. Don't assume Sales Navigator has fully replaced Classic yet.
>
> @cameron.transparentdi — if we want to initiate contact via Sales Navigator, we need to do that via n8n, because a new Sales Navigator InMail requires a subject line.

## Bridge gap (recorded, not fixed)

- There is **no start-chat path and no subject plumbing** in the Sales Navigator bridge. GHL's outbound reaches the gateway through a **Custom (SMS-type) conversation provider**, whose payload carries `message` text + attachments only — it has **no `subject` field** (GHL only carries a subject on Email-type providers).
- To add Sales Nav InMail initiation later, we would need: (a) a `POST /v2/{account}/inboxes/SALES_NAVIGATOR_PRIMARY/chats/send` call with `users_ids` (`ACw…` provider IDs) and `options.linkedin.sales_navigator.subject`; and (b) a designed **subject source** (gateway Config/template, contact custom field, parsed message convention, or a dedicated intake).
- Because the gateway only sends into an already-mapped chat, **even messaging a 1st-degree connection requires that a Sales Nav thread already exists** for that contact.

## Next steps (ordered)

1. (Optional, approval-gated) Run one controlled test originating a Sales Nav conversation to a **non-connection** to confirm the subject requirement empirically — costs 1 credit and sends a real message.
2. If Sales Nav initiation is wanted: design the subject source and add a start-chat path; keep connection requests on Classic.
3. Confirm team-note wording/audience (Slack `@cameron.transparentdi` mention retained).

## Safety gates

- No live LinkedIn message, contact creation, workflow publish/activate, app installation, or webhook registration without explicit approval.
- Keep the Classic connection-request path intact; do not change Classic or Sales Navigator workflows from this session's findings.
