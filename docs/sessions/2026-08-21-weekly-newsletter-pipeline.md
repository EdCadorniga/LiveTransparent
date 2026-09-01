# Weekly Newsletter Pipeline — Build & Go-Live Runbook (2026-08-21)

## Operational Update (2026-09-01)

The live dispatcher was retuned for smaller, more frequent executions after the initial large-batch design caused executions to approach the 600-second timeout.

- Dispatcher `vru7OtCkDnPJkWt2` is active and published on version `45bfda66-dcb6-4d1d-914a-05e6f527353e`.
- Prep `vvPdJMzBJMgcf5I9` is active and published on version `981ef005-3ed3-4d12-a6ba-2e80bdaaf81c`.
- Dispatcher schedule: `*/15 7-13 * * 1-5` in `America/Los_Angeles` (28 possible runs/day).
- `maxPerRun=250`; three senders are capped at `2,333` each, for a maximum of `6,999` sends/day.
- The sender cap is database-backed and counts rows already sent during the current Los Angeles calendar day; it no longer resets per execution.
- Stale `claimed` rows older than 20 minutes are recyclable on every dispatcher run, regardless of their weekday bucket. This prevents rows stranded by timed-out executions from waiting until their original bucket day.
- Future prep plans distribute contacts across five weekday buckets (`day_index` 1-5). Thursday and Friday dispatcher runs drain remaining pending/failed rows across all buckets.
- `defaultDryRun=false`. A controlled live test sent one newsletter successfully (execution `838055`); August 31 totaled 695 sent and 39 failed.
- The custom JavaScript runner was rebuilt/configured with a 300-second idle timeout, concurrency 10, isolated `pg`, and `coolify-shared` network access. The full pinned graph test succeeded (execution `837185`).
- The temporary manual trigger used for diagnosis was removed. The native schedule remains the production path.

## Summary

Recurring weekly newsletter sent to all eligible GHL contacts, spread over Monday-Friday
(15-minute dispatcher runs from 07:00-13:00 LA), from 3 sender addresses (`.co`, `.agency`, `.org` — NOT `.com`).
Content is authored in a GHL Email Template named `Newsletter <n> <Monday-date> (<subject>)`
and pulled automatically by the dispatcher at send time. Open/click/unsubscribe tracking
is injected by the dispatcher and recorded in Postgres.

**DNS GATE:** Sending must NOT be enabled until the email-sender domains'
SPF/DMARC records are confirmed fixed (single SPF + single DMARC per domain).
See `docs/dns-email-authentication-fix.md` (sent to domain admin 2026-08-21).

## Source of truth

Live n8n (MCP `n8n-lt`) is authoritative. Workflow IDs below are stable.

## Workflows

| Workflow | ID | Schedule | Role |
|---|---|---|---|
| LT - Newsletter Contact Prep | `vvPdJMzBJMgcf5I9` | Mon 06:30 `America/Los_Angeles` (`30 6 * * 1`) | Paginate all GHL contacts, exclude `do not contact`/`do not nurture` + no-email, dedup by email, assign sender rotation + weekday bucket (1-5), write `newsletter_send_log`. |
| LT - Newsletter Dispatcher | `vru7OtCkDnPJkWt2` | Every 15 minutes, 07:00-13:00 `America/Los_Angeles` (`*/15 7-13 * * 1-5`) | Fetch weekly template by name, claim up to 250 eligible rows, inject tracking, send via `POST /conversations/messages` with rotating senders, enforce the database-backed sender cap, mark sent/failed. |
| LT - Newsletter Open Pixel | `HkTQ9mqwHcpg3AIM` | Webhook `GET /webhook/lt-newsletter-pixel` | **Active.** Verifies HMAC, logs `opened` to `newsletter_events`, returns 1×1 transparent GIF. |
| LT - Newsletter Click Track | `HZ8ndNF4p80PrQjf` | Webhook `GET /webhook/lt-newsletter-click` | **Active.** Verifies HMAC, logs `clicked` + link_url, 307-redirects to original URL. |
| LT - Newsletter Unsubscribe | `RvYusUSGB79K2e2k` | Webhook `GET /webhook/lt-newsletter-unsub` | **Active.** Verifies HMAC, logs `unsubscribed`, marks log row, adds `do not contact` + `do not nurture` tags via GHL, returns confirmation. |

## Postgres (database `postgres` on container `postgres-uokgs4c04ko0s4scccg40cgg`)

- `newsletter_send_log` — one row per contact per week.
  `UNIQUE (ghl_contact_id, week_key)`. Columns: `week_key, day_index (1-5), ghl_contact_id, contact_email, first_name, sender_email, status (pending|sent|failed|skipped|capped|unsubscribed|planned|claimed), ghl_message_id, ghl_conversation_id, error, created_at, sent_at, claimed_at, run_id`.
- `newsletter_events` — tracking. Columns: `log_id, week_key, contact_id, event_type (opened|clicked|unsubscribed), link_url, event_ts, ip, user_agent`.

## Config values (dispatcher `Config` node)

- `locationId` = `Zwz4relUXVPxx8uohnjV`
- `apiBaseUrl` = `https://services.leadconnectorhq.com`
- `apiKey` = GHL PIT (shared with other workflows; value in Config)
- `trackBase` = `https://automations.livetransparent.com`
- `trackSecret` = `bd2141171b2610f3964ab3f83714149c` (HMAC signing for tracking URLs; stored in dispatcher + all 3 handlers' Config)
- `templatePrefix` = `Newsletter`
- `maxPerRun` = 250
- `maxPerSenderPerDay` = 2333 (database-backed daily count, Los Angeles timezone)
- `defaultDryRun` = false (MUST be false after DNS gate passes and Go-Live; was true during dry-run testing phase)

## Template convention

Name = `Newsletter <n> <Monday-date> (<subject>)`, e.g.
`Newsletter 1 2026-08-24 (The real reason regulated ads get disapproved)`.

- `<n>` is an editor label, ignored by matching.
- `<Monday-date>` is the Monday of the current week in `America/Los_Angeles` (computed by the dispatcher).
- `(<subject>)` becomes the email subject line.
- The dispatcher regex matches both `Newsletter <n> <date> (...)​` and `Newsletter <date> (...)​`.
- Template `templateType` may be `builder` OR `html` (a PATCH via API converts it to `html`); the dispatcher accepts both. Fails closed if this week's template is missing.

**Current template ID:** `6a87716221922afe5eda9e6f` (logo fixed 2026-08-21 to the proper Transparent eCom logo `https://storage.googleapis.com/msgsndr/Zwz4relUXVPxx8uohnjV/media/699310eda9efde4e01a14ef1.png`).

## Tracking injection (dispatcher, per recipient)

- **Open pixel:** `<img src=".../lt-newsletter-pixel?log_id=<id>&tok=<hmac>">`
- **Click:** every `href="https://..."` rewritten to `.../lt-newsletter-click?log_id=<id>&u=<urlencoded>&tok=<hmac>` (HMAC over `log_id|url`)
- **Unsubscribe footer:** `.../lt-newsletter-unsub?log_id=<id>&tok=<hmac>`
- HMAC = `hmac-sha256(trackSecret, parts.join('|'))`, hex.

## Rate limiting / send behavior

- 28 possible runs/day at 15-minute intervals from 07:00 through 13:45 PT, `maxPerRun=250` per run.
- `maxPerSenderPerDay=2333` per sender; the dispatcher counts already-sent rows in the current Los Angeles day before sending. Rows over the cap remain eligible for a later day. Claims older than 20 minutes are recycled on every run; normal pending rows remain bucket-gated until late-week catch-up.
- 400–600ms delay between sends; 429/transient errors retried up to 4 attempts with linear backoff (2s/4s/6s). Only persistent failures mark the row `failed`.
- Dry-run mode emits `planned` items and does NOT write/update DB rows (verified).

## Go-live sequence (only after DNS confirmed)

1. Confirm DNS is fixed (see gate above). Re-check: `nslookup -type=TXT livetransparent.co` (exactly one `v=spf1`), `nslookup -type=TXT _dmarc.livetransparent.co` (exactly one `v=DMARC1`). Repeat for `.agency` and `.org`. Recommended: mxtoolbox per domain.
2. Create/rename the weekly template to `Newsletter 1 <next-Monday> (<subject>)` in GHL **Templates** (not Campaigns). Confirm it appears via `GET /emails/builder?locationId=...`.
3. Publish `vvPdJMzBJMgcf5I9` (prep) and `vru7OtCkDnPJkWt2` (dispatcher) via `publish_workflow`.
4. Flip dispatcher `defaultDryRun` = false (REST PUT; `setNodeParameter`/`updateNodeParameters` are unsafe on the Config Set node — use direct n8n REST `PUT /api/v1/workflows/{id}`).
5. Verify after each mutation `versionId == activeVersionId`.
6. First real run: prep Mon 06:30 → dispatcher every 15 minutes from 07:00-13:45, Monday-Friday. Monitor executions + `newsletter_send_log`.

## Validation performed 2026-08-21

- **Eligible count:** 31,800 GHL contacts → 23,168 with email → 999 blocked (`do not contact`/`do not nurture`) → **22,169 eligible** (email-deduped).
- **Per sender per day (3 days):** ~7,390/sender total, ~2,463/sender/day (under 3,000 cap).
- **Prep execution `774082`:** success, wrote 22,169 rows, 0 sends. Test rows cleaned afterward.
- **Dispatcher dry run `773957`:** success, template matched + subject extracted, bucket SQL correct, emitted `planned` (0 sent, 0 DB mutation). Test artifacts cleaned (test row deleted, temp template archived).
- **Tracking E2E (log_id=1):** valid-token pixel logged `opened` (HTTP 200 GIF, 42 bytes); invalid token rejected; click logged `clicked` + redirected 307; unsubscribe logged + tagged GHL + marked row. Tags removed after test.
- **Bugs found & fixed during dry run:** (1) dispatcher template filter only accepted `templateType='builder'` but the PATCH converted the template to `'html'` — fixed to accept both; (2) dry-run items previously used `status:'sent'` which would have updated DB rows — fixed to `status:'planned'`; (3) prep workflow had no timezone (would fire 06:30 UTC) — set to `America/Los_Angeles`.
- **Metric definitions (unique vs total):** `emailsSent` counts unique sends per `ghl_contact_id + week_key` (UNIQUE constraint). `emailsOpened`/`emailsClicked` count total events per contact (a single contact can have multiple opens/clicks). `emailsUnsubscribed` counts unique unsubscribes per contact. Rates (`emailOpenRate`/`emailClickRate`/`emailBounceRate`) are computed from unique recipients in the send cohort.

## Notes / caveats

- GHL does NOT emit open/click/unsubscribe webhooks for `POST /conversations/messages` sends, so tracking is fully custom (tokens + `newsletter_events`). GHL native Campaign statistics are NOT available on this path (Option B decision).
- The template body may still need a visible unsubscribe link; the dispatcher injects one, but adding it to the template design is recommended for Gmail compliance (>5,000/day).
- Sending up to ~2,333/sender/day is ~8× the documented warmup cap (300/day) — deliverability risk accepted per user decision; DNS fix is the primary mitigation.
- **Metric definitions (unique vs total):** The newsletter is wired into reporting (2026-08-24): the **Campaign Channel Summary** (`MvPLbUAN9IIQikxb`) adds a `Newsletter` campaign channel row (**sent/opened/clicked from `newsletter_send_log` + `newsletter_events`, mapped into the existing `email_*` columns and grouped as `Newsletter`**); the **Executive Summary** (`Bukc0mgOD2r7V6ED`) folds newsletter sends into `emailsSent`, newsletter opened/clicked/unsubscribed into `emailsOpened`/`emailsClicked`/`emailsUnsubscribed`, and newsletter `failed` rows into a new top-level `newsletterFailed` metric. Both workflows edited via direct REST PUT and verified. Because the reports window defaults to ending yesterday, newsletter data appears when the window includes the send day. The dispatcher marks `failed` rows with `sent_at` too, so the failure metric is window-able.
  - `emailsSent` = **unique sends** (one row per `ghl_contact_id + week_key` in `newsletter_send_log`; UNIQUE constraint ensures no duplicates)
  - `emailsOpened` = **total open events** (counted from `newsletter_events`; a single contact can have multiple open events tracked via HMAC pixel)
  - `emailsClicked` = **total click events** (counted from `newsletter_events`; a single contact can have multiple clicks tracked via HMAC link rewriting)
  - `emailsUnsubscribed` = **unique unsubscribes** (one row per contact who clicked unsubscribe link; logged in `newsletter_events` and `newsletter_send_log`)
  - `newsletterFailed` = **failed send attempts** (rows marked `status='failed'` in `newsletter_send_log`; 101 in last window)
  - Rates (`emailOpenRate`/`emailClickRate`/`emailBounceRate`) are computed from **unique recipients** in the window send cohort
