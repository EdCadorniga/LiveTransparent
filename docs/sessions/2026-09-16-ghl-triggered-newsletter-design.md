# GHL-Triggered Email Template Broadcast — Staged Design

## Objective

Allow a GHL automation to submit any GHL email template for broadcast delivery. The template may be a newsletter, announcement, follow-up, promotion, or another approved email type. n8n snapshots the current GHL contact population, suppresses ineligible contacts, queues the eligible recipients, and distributes sending through the existing three verified sender identities. The workflow must always receive a GHL email-template reference; it must not depend on the word newsletter.

## Current live baseline

- `LT - Newsletter Contact Prep` (`vvPdJMzBJMgcf5I9`) is schedule/manual-triggered and builds the weekly recipient plan.
- `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) is schedule-triggered and sends from the database queue.
- Existing sender pool: `cameron@livetransparent.co`, `cameron@livetransparent.agency`, `cameron@livetransparent.org`.
- Existing controls to preserve: sender daily cap, bounded concurrency, retry/backoff, HMAC open/click/unsubscribe tracking, `newsletter_send_log`, and reporting.
- Existing live prep currently blocks no-email contacts, duplicate email addresses, `do not contact`, `do not nurture`, and `newsletter_dnd_suppressed`; the triggered path must additionally check GHL's live Email-DND/bounce/unsubscribe state before queueing and immediately before each send.

## Proposed workflow graph

1. **`LT - GHL Email Template Trigger Intake (STAGED)`**
   - Protected POST webhook.
   - Validate authentication, schema, idempotency key, template selector, and explicit dry-run state.
   - Create one campaign request row; reject duplicate idempotency keys without creating another campaign.
   - Snapshot `templateId` and the submitted template name.
   - Build an immutable reporting label from the template name and campaign key, for example `Template Name — ghl-automation-2026-09-16-example`.
   - Return `202 Accepted` with campaign ID and status URL/lookup key.

2. **`LT - GHL Email Template Campaign Queue (STAGED)`**
   - Scheduled worker drains accepted requests.
   - Fetches all GHL contacts with bounded pagination.
   - Excludes no-email, duplicate normalized emails, `do not contact`, `do not nurture`, `newsletter_dnd_suppressed`, and live Email-DND/bounce/unsubscribe suppression.
   - Assigns senders round-robin across the existing three-sender pool.
   - Writes idempotent campaign recipient rows; no recipient is inserted twice for the same campaign.

3. **`LT - GHL Email Template Campaign Dispatcher (STAGED)`**
   - Scheduled bounded worker drains only the requested campaign's recipient rows.
   - Re-fetches the contact immediately before send and fails closed on current suppression/DND state.
   - Uses the existing GHL Conversations Email send boundary, daily sender caps, retry policy, tracking injection, unsubscribe tagging, and reporting ledger.
   - Staged mode defaults to `dryRun=true`; it must not send or mutate recipient status beyond safe planning until separately approved.

## GHL automation webhook contract

```json
{
  "event": "email_template.requested",
  "idempotencyKey": "{{workflow.id}}:{{workflow.execution.id}}",
  "campaignKey": "ghl-automation-2026-09-16-example",
  "templateId": "<GHL email template id>",
  "templateName": "Optional human-readable template name",
  "label": "Optional operator label",
  "dryRun": true
}
```

`templateId` is required. The template may be a newsletter, announcement, follow-up, promotion, or another approved email type. n8n will resolve the GHL template and use its subject/body for each recipient. The live-send version must reject `dryRun:false` unless the workflow is explicitly enabled and the request is within the approved operating boundary. GHL automations should call the webhook only once at their terminal step and should use a stable idempotency key.

## Tracking and attribution

Every campaign stores both stable identity and human-readable attribution:

- `campaign_key`: idempotent campaign identity from GHL.
- `template_id`: immutable GHL template identifier.
- `template_name_snapshot`: name captured at intake, so later template renames do not rewrite history.
- `campaign_name`: readable label such as `Template Name — campaign-key`.
- `recipient_id`, `provider_message_id`, and `sender_email` on each delivery.

The staged implementation adds an idempotent `Ensure Mass Email Tracking Tables` PostgreSQL node to the intake path. It creates `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, `lt_mass_email_events`, indexes, and the `lt_mass_email_campaign_metrics` view. The view calculates planned, sent, delivered, bounced, total opens, unique opens, total clicks, unique clicks, and unsubscribes.

The staged tracking workflows are:

- `LT - Mass Email Open Tracking (STAGED)` (`J7xZH6BBnoXEQsoB`) — `/webhook/lt-mass-email-open`.
- `LT - Mass Email Click Tracking (STAGED)` (`TbYFpB80xSlRZ6gy`) — `/webhook/lt-mass-email-click`.
- `LT - Mass Email Provider Event Ingest (STAGED)` (`f87KRQ1Slhs9VUxJ`) — `/webhook/lt-mass-email-event` for delivered, bounced, unsubscribed, complained, replied, failed, retrying, and sent events.

All three are inactive. The future dispatcher will inject signed open/click URLs containing the delivery ID and will pass provider message IDs to the event ingest workflow. Unique opens and unique clicks are calculated by counting distinct deliveries with at least one corresponding event; repeated events remain available for total-open and total-click reporting. Open metrics are directional because image blocking and privacy features can distort them.

## Safety gates

- Staged workflows remain inactive or dry-run-only.
- No manual execution, provider send, GHL CRM mutation, campaign activation, or sender change is part of the staged build.
- Do not add a sender to bypass caps or deliverability controls.
- A live send requires a separate approval naming the campaign, template, cohort, and maximum recipient count.
- Before activation, verify SPF/DKIM/DMARC and confirm that the requested template is the approved GHL template.

## Implementation record — 2026-09-16

- The staged intake workflow was renamed from newsletter-specific wording to `LT - GHL Email Template Trigger Intake (STAGED)` and uses `/webhook/lt-email-template-trigger-stage`.
- The staged intake now requires `templateId`, accepts any approved GHL email-template type, and derives `campaignName` from the template name plus `campaignKey`.
- The PostgreSQL schema node is connected after validation and before the staged response. The schema is also retained as `postgres/mass-email-bootstrap.sql`; its campaign metrics view uses a correlated event aggregate so repeated open/click events cannot inflate planned, sent, delivered, or bounced delivery counts. It has not run because the workflow is inactive; no `lt_mass_email_*` tables have been created yet.
- The live schema node was corrected and published as version `b785df4c-2188-4697-ad0c-24dff29abdf0`; the workflow remains inactive with 4 nodes and 3 connection groups. A local pre-change backup is retained under `%LOCALAPPDATA%\\Temp\\lt_mass_email_workflow\\`.
- Local operator scripts used to create/update the staged definitions are in `C:/Users/edmon/`: `rename_stage_intake.py`, `build_mass_tracking_stage.py`, and `create_provider_event_stage.py`. They are machine-local helpers, not production source-of-truth artifacts.

## Progress update and next steps — 2026-09-16

**Completed:** the staged generic intake contract and tracking workflow definitions are in place; the schema is versioned locally; the intake workflow's PostgreSQL node is synchronized with that source; and the campaign metrics aggregation defect was corrected so repeated event rows cannot inflate delivery totals. Live read-back confirms the intake remains inactive at version `b785df4c-2188-4697-ad0c-24dff29abdf0`.

**Not yet executed:** the PostgreSQL schema has not been run, and no campaign request, contact snapshot, delivery row, provider message, or email send has been created. The supporting open, click, and provider-event workflows remain inactive.

**Next, in order:**

1. Obtain approval for and execute the versioned schema as a non-sending migration; read back the created tables, indexes, and metrics view.
2. Implement campaign-request persistence with idempotency-key deduplication and immutable template attribution.
3. Implement bounded GHL contact pagination and fail-closed suppression checks at snapshot and dispatch time.
4. Implement delivery-row creation, sender round-robin assignment, and per-sender caps.
5. Implement the approved template-resolution/send boundary, provider message-ID capture, signed tracking URLs, retry/backoff, and final suppression re-check.
6. Connect provider events and activate tracking only after correlation and metrics tests pass.
7. Run inactive/dry-run acceptance tests; obtain separate campaign/cohort/recipient-limit/send-window approval before activation or live sending.

## Acceptance checks before activation

- Duplicate webhook retries return the existing campaign instead of creating a second campaign.
- A suppression fixture is excluded at intake and again at dispatch.
- Sender assignment counts reconcile exactly to queued recipients.
- `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, and `lt_mass_email_events` are idempotent and correlate by campaign/contact/delivery/provider message ID.
- A dry-run execution produces planned counts and zero provider calls.
- Signed open/click tokens resolve only to the intended delivery row.
- Provider delivery events update the intended delivery and event rows.
- The metrics view returns correct total-versus-unique open/click counts for repeated events.
- An approved small-cohort send produces provider message IDs and read-back evidence without exceeding per-sender caps.
