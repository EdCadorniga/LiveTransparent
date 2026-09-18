# GHL-Triggered Email Template Broadcast — Staged Design

## Objective

Allow a GHL automation to submit any GHL email template for broadcast delivery. The template may be a newsletter, announcement, follow-up, promotion, or another approved email type. n8n snapshots the current GHL contact population, suppresses ineligible contacts, queues the eligible recipients, and distributes sending through the configured sender identities. The workflow must always receive a GHL email-template reference; it must not depend on the word newsletter.

## Current live state — 2026-09-17

This section supersedes the earlier staged-build and pre-activation snapshots in this document.

- Intake `t5frjtbuKzVZI294` is active/published at version `9523da34-9306-462b-b24f-72594a62a023`.
- Queue `vRXRFC6IwIxUME2k` is active/published at version `714b2d22-777c-4006-a233-d7e0fa6eb930`.
- Dispatcher `b41Sas8FVVrytZrl` is active/published at version `bf892c33-edca-416d-9b74-cff2ccea9fdf`.
- Queue and dispatcher sender pools are `cameron@livetransparent.co`, `cameron@livetransparent.org`, and `cameron@livetransparent.agency`.
- Temporary recipient and contact allowlists are empty; the suppression blocklist remains enabled.
- Queue and dispatcher retain `defaultDryRun=true`; activation did not enable provider sends.
- The GHL caller workflow `fe14c3bf-c1ed-4b91-b0fc-e9b5e55d3e71` remains unpublished, so it is not currently submitting new campaigns to intake.
- Queue execution `956286` and dispatcher execution `956284` succeeded with zero live sends; queue execution `956269` also completed. No `new`, `running`, or `waiting` executions remained at final verification.
- Tracking workflows remain inactive. Next steps are transport-level SPF/DKIM/DMARC verification per sender, followed by an approved change to `defaultDryRun=false` for the intended campaign.

## Current live baseline

- `LT - Newsletter Contact Prep` (`vvPdJMzBJMgcf5I9`) is schedule/manual-triggered and builds the weekly recipient plan.
- `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) is schedule-triggered and sends from the database queue.
- Existing newsletter sender pool: `cameron@livetransparent.co`, `cameron@livetransparent.agency`, `cameron@livetransparent.org`; these are not currently DMARC-aligned with the location's observed `.com` Mailgun transport.
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

## Historical progress update and next steps — 2026-09-16

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

## Implementation record — 2026-09-16 (build + dry-run verification)

The staged design was implemented end-to-end and verified with non-sending acceptance tests. A single controlled live send to the owner's address followed (see the deliverability and EOS sections below).

### Schema (applied)

- `postgres/mass-email-bootstrap.sql` was executed against the `postgres` DB (container `postgres-uokgs4c04ko0s4scccg40cgg`). Live objects: `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, `lt_mass_email_events`, 4 indexes, and the `lt_mass_email_campaign_metrics` view. One test campaign/delivery is intentionally retained; all other test rows were removed.
- Additive columns required by the claim model were added and are safe to re-run: `lt_mass_email_campaigns.subject/queued_at/planned_count`, `lt_mass_email_deliveries.claimed_at/run_id`, plus `lt_mass_email_deliveries_status_idx`.
- The live intake `Ensure Mass Email Tracking Tables` node matches the versioned file byte-for-byte.

### Historical workflow snapshot — superseded 2026-09-17

| Workflow | ID | State |
|---|---|---|
| `LT - GHL Email Template Trigger Intake (STAGED)` | `t5frjtbuKzVZI294` | inactive, version `fb82073e-b595-49fd-8a5b-d35f6c429f22` |
| `LT - GHL Email Template Campaign Queue (STAGED)` | `vRXRFC6IwIxUME2k` | inactive, `defaultDryRun=true` |
| `LT - GHL Email Template Campaign Dispatcher (STAGED)` | `b41Sas8FVVrytZrl` | inactive, `defaultDryRun=true` |
| `LT - Mass Email Open Tracking (STAGED)` | `J7xZH6BBnoXEQsoB` | inactive |
| `LT - Mass Email Click Tracking (STAGED)` | `TbYFpB80xSlRZ6gy` | inactive |
| `LT - Mass Email Provider Event Ingest (STAGED)` | `f87KRQ1Slhs9VUxJ` | inactive, version `296ad86b-0aac-4858-bb3b-998a126bbcbf` |

- **Intake:** webhook → `Config` → `Validate Request` → `Ensure Mass Email Tracking Tables` → `Upsert Campaign` → `Respond`. The upsert uses `ON CONFLICT (idempotency_key) DO UPDATE ... RETURNING (xmax = 0) AS created`; a duplicate `campaign_key` with a different idempotency key is caught (`23505`) and returns the existing campaign. The responder sets the HTTP status dynamically from `statusCode`.
- **Queue:** schedule/manual → `Config` → `Ensure Campaign Tables` → `Claim + Build Deliveries` → `Queue Summary`. Claims `accepted` campaigns (`FOR UPDATE SKIP LOCKED`), paginates `/contacts/`, suppresses no-email/duplicate/blocked-tag/`validEmail=false`, assigns senders round-robin, and inserts deliveries in 500-row chunks with `ON CONFLICT (campaign_id, contact_id) DO NOTHING`. `defaultDryRun=true` skips inserts and resets the campaign to `accepted`; `maxRecipientsPerCampaign` bounds a cohort and stops pagination early.
- **Dispatcher:** schedule/manual → `Config` → `Ensure Tables` → `Resolve Templates` → `Fetch Bucket` → `Dispatch Emails` → `Dispatch Summary`. Resolves each campaign's template HTML from `/emails/builder` + `previewUrl`; claims planned deliveries; re-fetches each contact and fails closed (404 → `skipped`, other lookup errors → release claim and retry); enforces per-sender daily caps; sends via `POST /conversations/messages` (`type: Email`); injects HMAC-signed open/click URLs; captures provider message IDs; retries 429/5xx; finalizes campaign status only when not dry-run.
- **Tracking:** the `Config` node is now wired between the webhook and the record node (it was previously unreferenced, which would have failed). Open/click also stamp `first_/last_opened_at` and `first_/last_clicked_at`. The provider-event responder returns JSON instead of an empty binary payload.

### Acceptance results (all non-sending)

- Duplicate webhook retry returned the existing campaign (`created:false`, same `campaignId`).
- Invalid request returned `400` with `missing` fields and created no row.
- Queue dry-run: `totalFetched=100, planned=5, inserted=0, skipped=91`, campaign reset to `accepted`, zero deliveries.
- Queue live-planning: 5 deliveries created with round-robin senders (`.co`, `.agency`, `.org`, `.co`, `.agency`), campaign `queued`, `planned_count=5`.
- Dispatcher dry-run: `total=5, sent=0`, all claims released back to `planned`, campaign stayed `queued`.
- Dispatch-time suppression: with only one delivery claimable and its contact tagged `mql` (added to `blockedTags`), the run returned `suppressed:1, sent:0`.
- Tracking: valid open token recorded one `opened` event and stamped the delivery; a bad token was rejected with no event; click recorded `clicked` + redirect; provider `delivered` set `delivered_at` and status `delivered`.
- Metrics view: after a second open event, `total_opens=2` / `unique_opens=1` while `planned=5`, `sent=1`, `delivered=1` were not inflated.
- All test rows were deleted afterward: 0 campaigns, 0 deliveries, 0 events.

### Notes / limitations

- The GHL email-builder API does not expose a template subject. The dispatcher resolves the subject as: operator-supplied `subject` → parenthesized text in the template name → template name.
- A raw `pg` error inside a Code node crashes the external task runner (a `pg-protocol`/n8n interaction where the error object's read-only `name` is reassigned). SQL in these Code nodes must be validated before deployment; the delivery INSERT column/placeholder mismatch that triggered this was fixed and all statements were validated directly in psql.
- There is no mass-email unsubscribe webhook; unsubscribe is handled via provider events only.
- Helper scripts (machine-local, git-ignored): `local-scripts/build_mass_email_stage.py`, `local-scripts/fix_mass_email_tracking.py`, `local-scripts/_mass_email_set_config.py`, `local-scripts/_vps_exec.py`.

### Recipient allowlist + first controlled live send (2026-09-16)

- **Allowlist added:** the queue and dispatcher Config nodes now carry `recipientAllowlist` (comma-separated emails; empty = no restriction). The queue additionally carries `contactIdAllowlist` (comma-separated GHL contact IDs; when set, the queue skips pagination and fetches only those contacts, which makes a controlled test fast). Both allowlists are enforced in the queue (planning) and the dispatcher (sending), so a non-allowlisted recipient is never planned and never sent.
- **Current values:** `recipientAllowlist = edmundocadorniga@gmail.com` on both workflows; `contactIdAllowlist` cleared; queue and dispatcher `defaultDryRun=true`.
- **First controlled live send:** campaign `allowlist-test-2026-09-16` (template `6a87716221922afe5eda9e6f`, subject "The real reason regulated ads get disapproved") was planned to exactly one recipient (`edmundocadorniga@gmail.com`, GHL contact `NVAp2GdpbWXLheyUgVf2`) and sent from `cameron@livetransparent.co`. Delivery `id=8` reached `status='sent'` with a provider message ID and conversation ID; the campaign finalized as `completed`. The dispatcher was returned to `defaultDryRun=true` immediately after. A later resend from the aligned `.com` sender is the inbox-delivery evidence described below.
- **Tracking caveat:** the open/click/provider tracking workflows are still inactive, so the tracking pixel and rewritten links in the sent email will not record events until those workflows are activated.

### Remaining before a broader live send

1. Confirm the GHL automation uses `X-LT-Mass-Email-Secret` with the configured intake secret, and configure any provider-event caller with `X-LT-Mass-Email-Provider-Secret`.
2. Obtain approval naming the template, cohort, maximum recipient count, sender boundary, and send window.
3. Verify SPF/DKIM/DMARC and confirm the requested template is the approved GHL template.
4. Optionally activate the open/click/provider tracking workflows so engagement is recorded.
5. Flip the dispatcher `defaultDryRun=false` for that campaign only, run the send, and verify provider message IDs, delivery/event correlation, and metrics read-back.
6. Remove or widen the `recipientAllowlist` only when a broader cohort is explicitly approved.

## Deliverability root cause and fix — 2026-09-16

### Symptom

The first controlled live send (`delivery id=8`, from `cameron@livetransparent.co`) was recorded by GHL as `sent` with a provider message ID, but the recipient did not receive it, and a test to a disposable inbox (Guerrilla Mail) also initially appeared not to arrive.

### Diagnosis

- Gmail later located the original `.co` test in spam. Its headers show `From: cameron@livetransparent.co`, `Reply-To: cameron@mg.livetransparent.com`, `mailed-by: mg.livetransparent.com`, and `signed-by: mg.livetransparent.com`. This confirms the message was delivered through the `.com` Mailgun transport but presented a different `.co` From identity to Gmail.
- A delivery probe to a Guerrilla Mail inbox **did** arrive (`from=cameron@livetransparent.co`), proving GHL LC Email dispatching works.
- A mail-tester.com analysis of the exact `emailFrom: cameron@livetransparent.co` send returned **5.6/10** with **"You're not fully authenticated"** and **DMARC failed**.
- mail-tester showed the envelope/sending domain was **`mg.livetransparent.com`** (server `a28.a926d550.use4.send.mailgun.net`), i.e. the **`.com`** Mailgun subdomain — even though the `From:` header was `cameron@livetransparent.co`.
- **Root cause:** GHL LC Email for this location sends **all** mail through the `.com` sending subdomain `mg.livetransparent.com` regardless of the `emailFrom` domain. `.co`, `.agency` and `.org` are separate registered domains (not subdomains of `.com`), so a `From:` on those domains does not align with the SPF/DKIM domain → **SPF and DKIM do not align → DMARC fails** for the From domain. Gmail then filters/spams the message (compounded by a look-alike-domain signal).
- Note: the root `mailo._domainkey` DKIM records exist for `.agency`/`.org`, and `.co` has its own DKIM on the `mg` subdomain (`k1._domainkey.mg.livetransparent.co`) — the domains are configured; the problem is that GHL is not sending *from* them.

### Fix (proven)

- Re-sending the same content with `emailFrom: cameron@livetransparent.com` (which matches the actual sending domain) returned **8.8/10** with **"You're properly authenticated"** — DMARC now passes.
- **Applied:** the mass-email queue and dispatcher sender pool is now `cameron@livetransparent.com`. The allowlisted test to `edmundocadorniga@gmail.com` re-sent successfully (delivery `id=8`, provider message `SmRfu9z9g9CsRwrmsVfM`).
- **Still outstanding:** the live newsletter dispatcher (`vru7OtCkDnPJkWt2`) still uses `.co`, `.agency`, `.org` senders and therefore has the same DMARC failure on every weekly send. The GHL UI shows all four dedicated domains present with `SSL Issued`; only `mg.livetransparent.com` is selected. The `.agency`, `.co`, and `.org` cards are unselected and each shows warmup Stage 1 at 0/1000. Select/enable a domain before testing its sender; if the sub-account permits only one selected domain, keep `.com` selected and use only its sender.

### Diagnostic tooling

- Disposable inboxes used: Guerrilla Mail (`https://api.guerrillamail.com/ajax.php`) and mail.tm (`https://api.mail.tm`). mail-tester.com was driven with a real browser (Playwright) to obtain the address and read the score.
- Temporary GHL test contacts created for probes were deleted after the test.

## Historical pre-activation audit and hardening — 2026-09-16

- The staged intake webhook now validates `X-LT-Mass-Email-Secret` against a dedicated workflow secret and returns `401` for missing or incorrect credentials. The GHL caller must be configured with that header before activation.
- The staged provider-event webhook now validates a separate `X-LT-Mass-Email-Provider-Secret`, uses `POST` for body-bearing callbacks, and maps handler status codes to the actual webhook response. The provider caller must be configured with that header before activation.
- The open and click tracking endpoints remain `GET` because email clients request those URLs. Their HMAC tokens remain the access control for event recording.
- Negative manual tests returned `401` for both unauthenticated intake and provider-event requests; no campaign or delivery rows were created or changed. All six mass-email/tracking workflows remain inactive and the queue/dispatcher remain dry-run guarded.

## Historical EOS closeout — 2026-09-16 (superseded by current live state above)

### Live state (fresh API read-back)

| Workflow | ID | State |
|---|---|---|
| `LT - GHL Email Template Trigger Intake (STAGED)` | `t5frjtbuKzVZI294` (ver `fb82073e-b595-49fd-8a5b-d35f6c429f22`) | inactive, 6 nodes |
| `LT - GHL Email Template Campaign Queue (STAGED)` | `vRXRFC6IwIxUME2k` (ver `0d292f47-2a43-4d01-9d20-07ef5366c506`) | inactive, 6 nodes, `defaultDryRun=true` |
| `LT - GHL Email Template Campaign Dispatcher (STAGED)` | `b41Sas8FVVrytZrl` (ver `a005c68a-944c-41de-bbf1-a65ca2711f68`) | inactive, 8 nodes, `defaultDryRun=true` |
| `LT - Mass Email Open Tracking (STAGED)` | `J7xZH6BBnoXEQsoB` | inactive, 4 nodes |
| `LT - Mass Email Click Tracking (STAGED)` | `TbYFpB80xSlRZ6gy` | inactive, 4 nodes |
| `LT - Mass Email Provider Event Ingest (STAGED)` | `f87KRQ1Slhs9VUxJ` (ver `58f3ef73-ef74-4d44-a4d9-e9a8e888f6a9`) | inactive, 4 nodes |
| `LT - Newsletter Contact Prep` | `vvPdJMzBJMgcf5I9` | active (unchanged) |
| `LT - Newsletter Dispatcher` | `vru7OtCkDnPJkWt2` | active (unchanged) |

- No executions in `new` / `running` / `waiting`.
- Queue + dispatcher: `senders = cameron@livetransparent.com`, `recipientAllowlist = edmundocadorniga@gmail.com`, `defaultDryRun = true`.
- DB: 1 campaign (`allowlist-test-2026-09-16`, `completed`) + 1 delivery (`id=8`, `sent`, `cameron@livetransparent.com`, provider `ShpyiNhtPKv5C8WHtByl`); 0 events.

### Worktree

- Modified (intentionally uncommitted): `AGENTS.md`, `Project Status and Next Steps.md`, `docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md`, `postgres/mass-email-bootstrap.sql`.
- `git diff --check` passes (LF→CRLF warnings only). Many unrelated untracked Apollo CSV/import artifacts exist — do not stage them.
- Git-ignored helper scripts: `local-scripts/build_mass_email_stage.py`, `local-scripts/fix_mass_email_tracking.py`, `local-scripts/_mass_email_set_config.py`, `local-scripts/_vps_psql.py`, `local-scripts/_vps_exec.py`.

### Next session — ordered actions

1. **[USER, GHL UI]** In the Live Transparent sub-account, use GHL → Settings → Email Services → Dedicated Sending Domains. The screenshot shows `mg.livetransparent.com`, `mg.livetransparent.agency`, `mg.livetransparent.co`, and `mg.livetransparent.org` already present with `SSL Issued`; `.com` is selected, while `.agency`, `.co`, and `.org` are unselected and at warmup Stage 1 (0/1000). Select/enable the additional domain(s) only if GHL permits them for this sub-account. If only one domain can be selected, keep `.com` selected and use only its sender.
2. **[ASSISTANT]** After each domain is selected, run a mail-tester test from its sender and confirm the envelope/signature domain matches the `From` domain and authentication passes. Do not retain a multi-domain newsletter pool based on DNS records alone; each domain needs transport-level proof.
3. Obtain approval for a broader mass-email live send (template, cohort, max recipients, sender boundary, window) and flip the dispatcher `defaultDryRun=false` for that campaign only.
4. Decide on: mass-email unsubscribe webhook, activating the tracking workflows, and the per-sender cap if `.com` is used for bulk (single sender ≈2,333/day will not cover ~22k/week).
5. Re-verify intake `Validate`/`Upsert` idempotency and the metrics view before any broader send.

### Safety gates

- All six mass-email/tracking workflows stay inactive; queue + dispatcher stay `defaultDryRun=true`.
- `recipientAllowlist` stays `edmundocadorniga@gmail.com` until a broader cohort is explicitly approved.
- Do not change the live newsletter sender pool until steps 1–2 are complete.
- Do not publish/activate or run an uncontrolled production event without explicit approval.
