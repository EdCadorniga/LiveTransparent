# Session Handoff: Instagram Company Page DM Priority

Updated: 2026-08-24

Treat live n8n and the deployed Postgres state as authoritative. The company-page Instagram DM sender is now live; this document records the 2026-08-18 priority change and the current delivery strategy.

## Summary of Changes (2026-08-18)

1. **Campaign send priority flipped** in `instagram_company_dm_state.campaign_priority`: `dan_brands` = 1, `dan_dispensaries` = 2, `partnerships` = 3 (379 rows updated). Previously partnerships were 1, brands 2, dispensaries 3.
2. **Message-1-first strategy confirmed**: `firstWeekMessage1Only=true` remains in the live sender. Only Message 1 is sent; Message 2 (then 3) is enabled only after everyone has received Message 1.
3. **Unipile key verified working** on 2026-08-18 — accounts list returned HTTP 200 with Instagram account `F2UprZ8aQc6Qm9CYYWU6cg` status OK. The earlier 401 blocking is resolved.
4. **Brand pool IG/FB enrichment complete**: workflow `LT - IG & FB Company Page Enrichment` (`BIVAw1AWTTzC0igW`) unpublished; last run found zero unresolved companies.
5. **Dispensary and Partnership enrichment active** (`Qd7sn9MPq4W24WKi`, `RlogFNDYjtjkuRFJ`) on a 5-minute schedule; temporarily blocked by an OpenRouter weekly key limit that the user fixed.
6. **Message 2 enabled**: the live sender now selects Message-1-complete rows, waits two business days after `last_sent_at`, sends the approved campaign-specific Message 2 copy, and advances the send log/state to step 2. Published version: `3d721cec-04e6-45cc-9ebb-fb21589b61a6`. Message 3 remains disabled.

## Live Sender

| Item | Value |
|------|-------|
| Workflow | `LT - Instagram Company Page Partnership Sender` (`IeovbYnhCsetXS89`) |
| Status | Active and published (dryRun=false) |
| Schedule | Mon-Fri 10:00-15:00 `America/Los_Angeles` (cron `0 10-15 * * 1-5`) |
| Daily cap | 45, hourly cap 10 |
| Unipile account | `F2UprZ8aQc6Qm9CYYWU6cg` |
| State table | `instagram_company_dm_state` (direct `require('pg')`) |
| Guards | `dryRun !== false` throws; Message 2 requires `firstWeekMessage1Only=false` |

The sender's `msgFor()` function carries approved Message 2 copy for `partnerships`, `dan_brands`, and `dan_dispensaries`. The SQL selects only `message_step = 1` rows with valid provider/attendee IDs, no reply evidence, no suppression, and no existing send log for step 2; a JavaScript business-day gate requires two weekdays after Message 1. Each send is idempotently reserved, sent through Unipile `POST /chats`, then committed with state, send-log, and activity-event writes inside a transaction.

## State Inventory (instagram_company_dm_state, 2026-08-18)

| Campaign | Rows | Priority |
|----------|-----:|----------|
| dan_brands | 245 | 1 |
| dan_dispensaries | 58 | 2 |
| partnerships | 76 | 3 |

## Delivery Plan

1. **Message 1 to everyone** — starting tomorrow (Mon-Fri schedule), brands are processed first, then dispensaries, then the remaining partnerships. 45 partnerships already received Message 1 on 2026-08-17 before the priority change, so their state is at `message_step = 1`.
2. **Message 2** — enabled on 2026-08-24 with the approved copy, step selection, two-business-day gate, and first-week guard disabled.
3. **Message 3** — same gate, two business days after Message 2.

## Enrichment Status

| Sheet | Workflow | Status |
|-------|----------|--------|
| brand_pool - IG & FB | `BIVAw1AWTTzC0igW` | COMPLETE (unpublished) |
| dispensary_pool - IG & FB | `Qd7sn9MPq4W24WKi` | Active, 5-min schedule |
| partnership_candidate - IG and FB | `RlogFNDYjtjkuRFJ` | Active, 5-min schedule |

All enrichment workflows use DeepSeek V4 Flash via OpenRouter with web-search plugin, 5-company batches, one aggregated Sheets write per batch, and research markers `candidate_found_review_required`, `openrouter_no_match_v2`, and `openrouter_web_research_v2`. Missing research headers fall back to columns E/F.

## Contract Reference

- Audience selectors: `brands_pool`, `dispensaries_pool`, `partner_candidate_email` / `partner_candidate_linkedin`.
- Existing contact-level Instagram fields are protected; company-level fields are separate (`Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, `Company Facebook Messenger PSID`).
- Any prior reply/suppression from any associated contact stops the sequence; identity/reply-check errors fail closed.
- Full contract, source audit, and guardrails: `docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md`.

## Non-Negotiable Guardrails

- Do not change the approved message text.
- Do not send to personal Instagram profiles.
- Do not republish `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`).
- Message 2 is enabled; do not enable Message 3 until Message 2 delivery has been reviewed.
- Do not manually execute the live sender without explicit approval.
- Fetch live state before every mutation and verify state after it.
- After workflow mutation, verify `versionId == activeVersionId`; publish if necessary.
- Do not commit secrets, tokens, or captured credential-bearing responses.
