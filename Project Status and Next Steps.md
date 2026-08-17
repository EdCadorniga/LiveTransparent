# LiveTransparent Project Status and Next Steps

Updated: 2026-08-17 (SimpleTexting boundary hardening and Executive Report social accuracy)

## Source Of Truth

### Executive Report MQL and Account Statistics (2026-08-17)

- The MQL panel now shows the three requested figures plus period movement. Verified live: Total MQLs 137, MQLs Converted to SQL 48 (opportunities that also entered the Sales Outreach pipeline `dhdlf3O4tymxFtHk4aqq`), Current MQLs awaiting Sales 89. The 30-day window reports 119 entered and 44 converted; the 7-day window reports 0 entered and 0 converted.
- The previous `Active = Total = 137` display was misleading: it counted only the Warm Qualified (MQL) stage snapshot, so 48 MQLs that had already moved to Sales Outreach were still shown as active. The reworked `mqlSummary` CTE (Executive Summary version `e4fa3d18-1a61-47db-b255-d34e20051d7f`) resolves current pipeline per opportunity.
- Reach, impressions, posts, likes, and followers are now live from GHL Social Planner account statistics. The PIT authenticates `/social-media-posting/statistics` (it returned 401 on 2026-08-04, so this unblocked the feature without needing GHL OAuth). 7-day window: 45 reach, 159 impressions, 4 posts; 30-day: 4,018 reach, 1,821 impressions, 10 posts. Saves is not provided by the statistics endpoint and remains N/A.
- `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`, active version `bee234fb-5234-4fb4-88e9-4dd611b937fb`) runs daily 06:00 America/Los_Angeles, calls the statistics endpoint with the GHL PIT from its Config node, and stores per-window `all` plus per-platform rows in `report_ghl_social_statistics` (report `postgres` database). Verification execution `760249` stored 12 rows.
- Executive Report build `2026-08-17-v27-social-mql` is deployed. Desktop (1440px) and 390px mobile verified: all report APIs HTTP 200, no console errors, no page-level horizontal overflow, and the new MQL and account-statistics cards render correct values for 7d and 30d.
- Full audit and implementation notes: [`docs/sessions/2026-08-17-social-and-mql-reporting.md`](docs/sessions/2026-08-17-social-and-mql-reporting.md).

### Executive Report Social Accuracy (2026-08-17)

- The official GHL Social Planner post API and the report ledger both return 8 platform/account placements and 3 likes for the completed `2026-08-10` through `2026-08-16` window: 6 LinkedIn placements and 2 Instagram placements. The report now labels these as placements rather than unique composer posts.
- Executive Summary (`Bukc0mgOD2r7V6ED`) is active and published on version `bc4856aa-e640-4477-a9fc-3ed14ae53707`. Reach, impressions, and saves return `null` and render as `N/A` when the source payload lacks those fields; unavailable account analytics are no longer represented as measured zeroes.
- The LinkedIn snapshot now groups both `requested` and `requested_pending` into Requested. Verified live totals are 10,469 Ready, 1,365 Requested, 2,040 Connected, 100 Follower Messaged, and 13,977 total state rows. The selected-window activity ledger reports 2 requests and 2 replies from 2 responders.
- `LT - GHL Daily Social Ingest` (`QZoqCaTwDhbym80O`) is published on version `2ed24c59-1fc8-40ae-bdb0-aba9744a37a1`. It uses GHL API version `2021-07-28`, paginates the full 366-day report horizon, fails closed on fetch errors, refreshes every mutable post field, and reports the actual upsert count. Read-only verification execution `759065` refreshed 229 posts; the table retains 250 rows and refreshed at `2026-08-17T14:51:02Z`.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` is deployed. Desktop and 390px mobile checks returned all report APIs as HTTP 200, no console errors, and no page-level horizontal overflow.
- Exact-range account statistics remain blocked because the active `ghl_oauth_tokens` row has an empty access token. The experimental workflow was unpublished and archived. Do not cache or fabricate reach/impression totals; reconnect GHL OAuth before adding the official statistics endpoint.
- Full audit and verification notes: [`docs/sessions/2026-08-17-social-reporting-accuracy.md`](docs/sessions/2026-08-17-social-reporting-accuracy.md).

### SimpleTexting Safety Reconciliation (2026-08-17)

- Automated outbound remains paused. Campaign Step Runner (`dUyOfxllvkxZavaw`), Warmup Dispatcher (`dZQLlbTLkpE1843X`), Pool Dispatcher (`usxYXSuc4ahw40V3`), and Campaign Sequencer (`7mSiivR3NhtLIcNz`) are unpublished. Phone Backfill (`8hQKQi1PooYDFxNR`) is active but cannot send SMS.
- The active send webhook (`Q3Ivnwe4z2Y3cD7A`, version `47dd0303-3d36-49e4-9bd9-e34873edbad2`) now defaults to dry-run, validates malformed GHL `customData`, normalizes US/Canada numbers, resolves the Jason/campaign/Emerald template registry, rejects unresolved merge fields, and enforces business hours plus live GHL DND/tag suppression before a real send.
- Provider Router (`f4VoO1lBWkYRcQai`, version `dfbb09db-890c-48ef-83a6-9cf4a64863f4`) and Idempotent Send (`gwaEpWDpTIwsafi8`, version `bcc7d22e-58b8-4419-a56f-753ff80773b8`) fail closed on invalid provider, contact, phone, message, suppression, or non-confirmed provider responses. Safe tests `757212`, `757213`, `757214`, `757227`, and `757239` produced no live SMS.
- SimpleTexting webhooks are registered for inbound messages, delivery/non-delivery reports, and unsubscribe reports. Their active workflows are protected through secret callback URLs: Inbound `i0pROHpFtN4LYR0Q` version `d657c79b-f075-4241-a78d-0be33f67f627`; Delivery `AEi1VCzkLvaYFr4U` version `31e884de-b4fe-4f03-af22-49cb64b766a1`; Unsubscribe `IyBKMkpYQ7pa0C8V` version `c21eb489-9561-4393-8d52-f8a8231fa0a7`. Pinned delivery test `757225` verified protected routing without a state write.
- Database reconciliation restored 41 confirmed `sent_step_*` events from provider IDs, terminalized 202 exhausted historical provider failures as `delivery_failed`, retained 55 unmatched `send_unknown` rows in quarantine, and marked one unsupported/missing number `phone_unavailable`. No uncertain historical send was replayed.
- Remaining production validation requires either natural provider traffic or one explicitly approved controlled live SMS. Do not publish sender schedules or run a live test without approval.

### Executive Report Campaign Accuracy (2026-08-16)

- The 7-day preset now returns exactly seven completed local dates, verified as `2026-08-09` through `2026-08-15`. Executive Summary (`Bukc0mgOD2r7V6ED`) is published on `be29cdcb-efdf-4e43-a17a-cdbd1ef622b7`; Campaign Channel Summary (`MvPLbUAN9IIQikxb`) is published on `12f28e56-dd02-4afd-81cd-e7a2c8fa6086`.
- Vapi `interest_unknown` and `human_answered` outcomes count as answered, not qualified. The verified window has 42 calls and 7 answered: Brand 22/3 and Dispensary 20/4.
- Global email rates now return `null` with basis `event_counts_without_matching_send_denominator` when event counts lack a compatible sent-recipient denominator. Campaign email rates remain based on tracked delivered recipients.
- LinkedIn inbound (`7o5EBdvwAuIaWW7k`) preserves source timestamps and reconstructs malformed form-encoded Unipile payloads. Missed message `4pX8FcptXnSl5aADrrfm8A` was inserted idempotently at its original timestamp: first insert 1, second insert 0. The live 7-day campaign API now reports 2 LinkedIn replies: 1 Partnership and 1 unattributed. Final workflow version `9f61f384-f481-467f-a13e-47bf9a1b6e52` is active with no temporary recovery nodes.
- Instagram inbound (`pISlgYUsyJIrLuJd`) and social outbound routing (`kqIi8i1RjFAZKrK3`) now maintain `instagram_activity_events`. The report exposes explicit ledger coverage and currently reports 0 DMs and 0 replies rather than implying historical completeness.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` supersedes v24 while retaining its Instagram channel/filter support, DM/reply columns, drill-down/comparison metrics, and ledger coverage.
- Full implementation and verification notes: [`docs/sessions/2026-08-16-executive-report-campaign-accuracy.md`](docs/sessions/2026-08-16-executive-report-campaign-accuracy.md).

### Company Instagram Page Delivery Decision (2026-08-14)

The approved Instagram/FB DM copy is unchanged. Phase one targets verified company Instagram pages through Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`, not employee profiles. The unpublished `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) must not be reused because it used the LinkedIn account and old state model. Facebook Messenger is deferred to native GHL Messenger; public Facebook URLs and Page IDs are not Messenger recipient IDs.

Audience selectors: `brands_pool` for Brands, `dispensaries_pool` for Dispensaries, and `partner_candidate_email` or `partner_candidate_linkedin` for Partnerships. Original-source audit: `data/Brands.csv` has 3,668 rows, 3,224 with Instagram URL occurrences, and 2,799 with Facebook URL occurrences; `data/Dispensaries.csv` has 10,200 rows, 6,875 with Instagram URL occurrences, and 6,431 with Facebook URL occurrences. Relevant columns are `Company non-LinkedIn URL(s)`, `Location non-LinkedIn URL(s)`, and `Contact non-LinkedIn URL(s)`. Counts are preliminary and require normalization, deduplication, and company-page validation. Partnership source files lack reliable Instagram/Facebook URL fields and require separate enrichment.

Existing contact-level Instagram fields are protected: `Instagram Username` (`8k6vF61VBIysdIXXFQD5`), `Instagram Profile URL` (`beGMXoidqHdYqAQDORWX`), `Instagram Profile Provider ID` (`fYYUrFLABP5l0w7RdK7Y`), `Instagram Chat Attendee ID` (`SQdQw0MNvk8uQbr4yDZU`), and `Instagram Chat ID` (`ab6euY7qo5klhUSe7VWu`). Create separate company-level fields named exactly: `Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, and `Company Facebook Messenger PSID`. Do not repurpose `Apollo Facebook URL`; a Facebook PSID may only be populated from an eligible GHL Messenger event.

The enrichment workflow matches source rows to GHL by Emerald Contact ID, source metadata, exact normalized email, exact normalized phone, then company-plus-contact-name as a review fallback. It extracts and normalizes company/location URLs, resolves Instagram pages through Unipile, rejects personal or ambiguous pages, updates only the new company-level fields, and produces an unresolved/conflict report. One company page may map to multiple GHL contacts; Postgres stores associated IDs and a primary attribution contact. A dedicated company-page identity/state model is authoritative for delivery and lifecycle, with identity uniqueness by campaign/account/profile provider ID and send idempotency by campaign/profile/step. Use direct `require('pg')` transactions for writes.

Any prior reply or suppression from any associated contact stops the full company-page sequence, including relevant GHL/email/LinkedIn reply evidence; email and LinkedIn campaigns may continue independently when no reply exists. Identity/reply-check errors fail closed. Cadence: Message 1 on the first eligible weekday, then Messages 2 and 3 two business days apart; never send on weekends. Lifecycle remains in Postgres; no lifecycle tags are required. All eight company-level fields are `TEXT`; provider/profile fields require validated Unipile resolution, and chat fields require a usable messaging identity. The existing `instagram_conversation_map` remains the contact-level inbound bridge, not campaign state. Next gates: source extraction report; GHL matching/review; create the eight company fields; resolve/write validated Instagram identities; create/import state; five-page dry-run samples for Brands and Dispensaries; one controlled live Instagram test per campaign with explicit approval; verify Unipile IDs, GHL mapping, state persistence, and reply suppression; then publish/activate the weekday dispatcher.

### Session 3 Fixes (2026-08-12)

- **Executive Summary duplicate JSON keys removed**: `vapiWeeklyPerformance` and `vapiWeeklyBreakdown` appeared 5 times each in the `Build Query` node's `summary_json` CTE. Removed 4 duplicate pairs; 1 of each remains. Published version `d458117c-63a0-4666-a5dd-1620e9bde4fe`.
- **Executive Summary timezone drift fixed**: `Normalize Request` node computed `startDate` using pure UTC operations (`new Date().setUTCDate()`) instead of the configured `America/Los_Angeles` timezone. Now uses `isoDateInTimezone()` for timezone-aware date subtraction. Same fix applied.
- **Date filters added to unfiltered CTEs**: `stageVelocity`, `sql_contacts`, and `pool_distribution` (4 sub-queries) in the Executive Summary API now include `WHERE report_date BETWEEN $1::date AND $2::date`, matching the selected period.
- **Executive Summary zero/timeout regression repaired**: The stage-velocity filter referenced nonexistent `v.report_date`, causing PostgreSQL failure and an empty HTTP 200 that the frontend rendered as zeroes. Changed it to `DATE(v.computed_at)`. Removed the redundant Campaign Channel Summary HTTP call from `Shape Response` and projected existing `email_direct` totals/rates instead, reducing current/prior summary requests to 19.9s/12.3s. Final active version `d177a923-da94-43ac-ac97-dbba1a664ab4`; browser verification rendered 1,847 visits, 160 contacts, 4,368 opportunities, 5,743 email opens, and 362 clicks.
- **Partnership LinkedIn replies corrected**: Campaign Channels undercounted replies because malformed form-encoded Unipile webhook payloads lost sender/message fields. Verified David Schachter and Gretchen Gailey directly through Unipile, restored their original message IDs/timestamps to `linkedin_activity_events`, and raised Partnership LinkedIn replies from 1 to 3. Published inbound workflow version `f96dafba-9818-4aab-8656-c2e4e2ab8480` adds a field-level malformed-payload fallback for future events.
- **Campaign Channel Summary timezone drift fixed**: `Normalize Campaign Window` node used `new Date().toISOString()` (UTC) for default end date. Now uses `isoDateInTimezone()` with `America/New_York`. Published version `e3b9f13f-e589-4dd9-bc8d-98801ed8c654`.
- **Voice dialer Postgres migration**: Migrated 4 broken Postgres v2.6 nodes (`Postgres - Release Lock`, `Postgres - Release Lock (Timezone)`, `Postgres - Mark Attempted`, `Postgres - Mark Vapi Start Failed`) to direct `require('pg')` Code nodes. The dialer was crashing on every execution due to the `queryReplacement` parameter bug. Published version `b8e9c57a-f81f-49fd-b469-1388320568c5`.
- **Voice dialer release-lock resolution verified (2026-08-14)**: This was the shared scheduled Vapi outbound dialer path, not a manual dialer and not Twilio. Queue items skipped for phone, suppression/DNC, qualification, or calling-hours reasons could hit `Postgres - Release Lock`; the n8n Postgres v2.6 `$1/$2/$3` binding failure caused `there is no parameter $1`. The published direct-`pg` migration removes that dependency. Thirteen consecutive scheduled executions on 2026-08-13, including execution `746845`, completed successfully with no recurrence.
- **Voice enqueue residual error resolved (2026-08-14)**: The same n8n/Postgres binding defect remained in the active `LT - Voice Queue Enqueue` webhook (`XzcpOBi9YcIhJPck`) at `Postgres - Insert or Noop`, which still used `$1`-`$5` with `queryReplacement`. Replaced it with a direct `require('pg')` Code node using the same advisory-lock and deduplication behavior. Published version `42aba803-09b0-4118-a105-9161bebe66e9`; fresh live details confirm `versionId == activeVersionId`. This was the residual shared voice-queue path, not Twilio.
- **Voice intake poller audit fixes (2026-08-14)**: Published `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) on `5c464233-c79a-4f49-a809-de303f3b6136`. The poller now uses the full terminal voice blocklist, routes suppressed contacts to the skip branch, reports tag mutation failures instead of silently claiming success, and returns explicit inserted/deduplicated queue outcomes. Smoke execution `747051` succeeded.
- **Voice intake Apollo tag-context fix (2026-08-14)**: The Apollo HTTP response replaced the classified item and caused `Remove Tag - Enriching` to fall back to `vapi_queue`, leaving the actual campaign tag behind. Published version `d852a93d-b468-4b9b-8cc9-d4995131f926` now resolves the original campaign tag from `Classify Contacts`; verification execution `747053` removed `vapi_campaign_brand` successfully.
- **Voice callback Postgres migration**: Migrated 8 Postgres v2.5/v2.6 nodes (`Postgres - Update Status`, `Postgres - Set DNC`, `Postgres - Log Outcome`, `Postgres - Insert Attempt`, `Postgres - Mark Queue Completed`, `Postgres - Resolve Queue By Call ID`, `Postgres - Claim Timer State`, `Postgres - Advance Phone Index`) to direct `require('pg')` Code nodes. Published version `c97480db-d741-4c7c-8705-f173296800ac`.
- **ghl_contact_id re-backfill**: All 13,868 rows had NULL `ghl_contact_id` (lost during DB recovery). Re-ran 3-pass matching from GHL export CSVs: email (4,642), phone (5,742), name+company (2,255) = 12,639 matched. 1,229 unmatched (contacts not in exports).
- **Embedded secrets audit**: Scanned all 83 active workflows. Found 12 critical (GHL PIT in 8+ workflows, Vapi key, Unipile key, Postgres creds, GHL OAuth creds), 5 high (webhook secrets, Slack token), 2 medium (OAuth client creds). Full remediation plan documented — requires credential creation and rotation.
- **LinkedIn state backfill**: Executed LinkedIn Reply Backfill (`QfJ2EZcc7lZwNgxj`) successfully (execution `743291`). State Sync (`ceaKnz6E3onQrZpt`) timed out at 60s task runner limit; will populate on normal 6-hour schedule.

### Immediate Runtime Update (2026-08-12)

- The external n8n JavaScript runner blocker is resolved. `n8nio/runners-custom:latest` now contains an isolated npm `pg@8.21.0` tree at `/opt/pg-node_modules`; `NODE_PATH` is configured in the container and task-runner config. VPS verification returns `typeof require('pg').Client === 'function'`, and runner logs show no allowlist/module errors.
- The n8n container was recreated with the persisted Coolify encryption key after a mismatch caused `Credentials could not be decrypted` and empty report responses. The public report endpoint now returns HTTP 200 with a real approximately 33 KB JSON payload.
- The external runner's direct `require('pg')` path is verified by controlled GHL leads ingest execution `742843`; the atomic transaction completed successfully.
- GHL leads ingest is active hourly on published version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825`. Execution `742843` wrote 500 distinct contacts and matching sync-run, watermark, and source-health records.
- **GHL Sales Ingest repaired (2026-08-12)**: Workflow `aYT5oHcgmBALzHy5` published on version `91603d56`. Migrated from broken Postgres v2.6 template-literal injection to atomic direct-`pg` transaction (`require('pg')` BEGIN/COMMIT). Execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows. Sync run completed (15,968 row_count, 0 errors). Watermark `2026-08-12`. Health `ghl_opportunities` status `ready`.
- **GHL Sales Ingest cadence corrected (2026-08-14)**: Invalid `minutesInterval: 1440` caused hourly executions because Schedule Trigger minute intervals support only 1-59. Published version `c1b5020c-757b-4515-8c51-3066a15326aa` runs once daily at 1:15 AM `America/Los_Angeles`, after the hourly Leads Ingest. Post-timeout scheduled executions `749695`, `749902`, and `750085` all succeeded before the cadence correction.
- **Call Outcome Ingest secured (2026-08-12)**: Workflow `PUCfTZBANSPcgS0c` published on version `7af98411`. Now requires `X-LT-Call-Outcome-Secret` header (secret stored in Config node of `PUCfTZBANSPcgS0c`). Unauthorized requests throw before any DB write.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` is deployed. Pipeline/stage charts resolve live GHL IDs; campaign tables include LinkedIn and Instagram ledger metrics; social post/account definitions are explicit; desktop and 390px mobile checks found no raw stage IDs or page-level horizontal overflow.

For the complete recovery narrative and continuation order, read [`docs/handoff/2026-08-12-report-recovery.md`](docs/handoff/2026-08-12-report-recovery.md). For the company Instagram-page DM implementation, read [`docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md`](docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md).

### Documentation Review (2026-08-12)

Full cross-file review of AGENTS.md, plan.md, this document, and docs/handoff/2026-08-12-report-recovery.md. Fixed 18 issues across 4 files:
- **Security**: Redacted 3 exposed secrets (Apollo webhook key, Apollo API key, Call Outcome secret)
- **Stale data**: Updated `ghl_contact_id` from `0/13,868` to `13,755/13,868` across all files; updated plan.md Data Pipeline Status; marked Sales Ingest + Call Outcome auth as DONE in plan.md
- **Contradictions**: Fixed SimpleTexting status (AGENTS.md said "active/published" vs Status.md "unpublished"), DAN candidateLimit (85 vs 65), Partnership dry-run→live, Reply Backfill version ID (`462e`→`4620`), Emerald HTTP wrapper severity
- **Formatting**: Fixed plan.md step 6 indentation
- **Remaining**: `repomix-output.md` was regenerated via `packlive` at end of this session.

### Severity-Ranked Open Work

1. ~~**Critical: repair and prove GHL Sales Ingest**~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities + 7,984 pipeline history rows.
2. **Critical: restore source coverage with provenance**. Opportunities now restored. Voice, email, LinkedIn, SMS still at zero — will populate through live workflow activity. LinkedIn Reply Backfill executed successfully (execution `743291`).
3. ~~**Critical: authenticate public write boundaries**~~ **DONE for Call Outcome Ingest and SimpleTexting send/callback boundaries.** Review the remaining Warm intake webhooks; retain explicit approval gates for manual sends/calls.
4. ~~**High: audit then backfill `ghl_contact_id`~~ **DONE.** Re-backfilled 12,639/13,868 from GHL export CSVs (email/phone/name+company matching). 1,229 unmatched (not in exports).
5. ~~**High: verify voice persistence safely**~~ **DONE.** Migrated dialer (4 nodes) and callback (8 nodes) from broken Postgres v2.6 to direct `require('pg')`. Both published and verified.
6. **High: migrate embedded secrets** to Config nodes (Community Edition cannot use env vars in Code nodes) or n8n managed credentials where available, then rotate exposed values. Full audit completed — 12 critical, 5 high, 2 medium findings documented.
7. ~~**Medium: fix report correctness debt**~~ **DONE.** Removed duplicate Executive Summary JSON keys, fixed timezone drift in both report workflows, added date filters to `stageVelocity`, `sql_contacts`, `pool_distribution`.
8. **High: 1,229 unmatched ghl_contact_id rows** — contacts in `emerging_pool_contacts` not in GHL export CSVs. Decide: skip, manual GHL lookup, or re-export.
9. **Medium: Warm intake authentication** — review webhook auth on `5nYzp9DgQUopzWhR`, `OowP3sAd8c9paSKf`, and `SmMf8QIfysuxQJbG`. SimpleTexting send and provider callback boundaries were hardened on 2026-08-17.
10. **Medium: add OAuth-backed social statistics** ~~for reach, impressions, and saves~~ — reach/impressions/likes/followers now live via PIT-backed `LT - GHL Social Statistics Ingest` (saves stays N/A); complete approved native GHL report widgets/page names through the UI.
11. ~~**Low: monitor migrated voice dialer**~~ **DONE 2026-08-14.** Thirteen consecutive scheduled executions succeeded after the direct-`pg` migration, including execution `746845` through `Postgres - Release Lock`.
12. **Low: clean legacy nodes/scripts and stale historical prose** only after live paths are stable.

The exact restart procedure, evidence, and guardrails are in [`docs/handoff/2026-08-12-report-recovery.md`](docs/handoff/2026-08-12-report-recovery.md), section `Next Agent: Start Here`.

### Post-Recovery Baseline

Measured directly on live Postgres after execution `743094` (Sales Ingest repair):

| Source | Current Rows |
|--------|-------------:|
| `report_raw_ghl_contacts` | 500 |
| `report_raw_ghl_opportunities` | 7,984 |
| `report_raw_ghl_pipeline_history` | 7,984 |
| `voice_call_queue` | 3 pending |
| `voice_call_attempt` | 0 |
| `report_raw_ghl_call_outcomes` | 0 |
| `Email_Events` | 0 |
| DAN / Emerald / Partnership release logs | 0 / 0 / 0 |
| Main / Partnership LinkedIn state | 0 / 18 |
| SimpleTexting campaign state / events | 0 / 0 |
| `emerging_pool_contacts` / with GHL ID | 13,868 / 12,639 |

Pre-recovery throughput and row-count claims are historical until each source is re-ingested or restored.

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Executive Report response-rate + social-engagement fixes (2026-08-04)**: User reported that 1 LinkedIn partnership response and 1 email partnership response showed as 0 response rate, and that LinkedIn/email data for the 3 campaigns (New attribution model - brands, New attribution model - dispensaries, Partnerships) looked wrong. Root-cause investigation found 4 bugs, all fixed and published:
  1. **Reply Poller wrong HTTP method (CRITICAL)**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) called `POST /conversations/search` which returns 404; the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522221` now returns `errors: []` (was 59 errors). Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event (CRITICAL)**: `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack alert; it never wrote to `Email_Events`. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). The handler now also passes `email`/`event_ts` through. Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill one-shot (CRITICAL)**: `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows set to `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-selects rows whose last check is older than 6 hours and whose `dm_conversation_status <> 'active'`, so new replies are picked up. Published version `0620c314-befb-4620-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch**: The Executive Summary's `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but the social ingest stores `like`/`comment`/`share` (singular). Fixed the `Build Query` node to `COALESCE` both plural and singular keys. Verified live: `socialPosts` now shows `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  5. **Historical reply recovery completed**: Verified GHL/Unipile records for Strider Peterson's email reply and Jaret Christopher's LinkedIn reply were inserted idempotently on 2026-08-04. On 2026-08-12, verified Unipile records for David Schachter (`rvWEW2K2WYeQ7v6zypDdZQ`, `2026-08-10T15:09:07.711Z`) and Gretchen Gailey (`8UF3lxibUmKYaG87h1F5Pg`, `2026-08-06T16:20:35.281Z`) were also inserted idempotently. Partnership LinkedIn now reports 3 replies. The temporary 2026-08-04 backfill workflows were archived after successful executions `522402` and `522416`.
  6. **Social metric availability corrected**: Executive Summary exposes post-ledger likes/comments/shares and returns `null` for saves/reach/impressions when those fields are absent. Build `2026-08-17-v26-social-reporting-accuracy` renders unavailable statistics as `N/A`, not zero. OAuth-backed statistics ingestion remains pending because the active stored OAuth token is empty and PIT access returns 401.

- **Partnership LinkedIn reporting (2026-07-31)**: The Campaign Channel Summary now returns 10 durable, idempotent `connection_request_sent` events in the `Partnership LinkedIn` row for the verified execution `281366`. The live dispatcher records future successful invites after Unipile success and records provider/state-transition diagnostics without issuing any reporting-time outbound requests.

- **Campaign reporting optimization (2026-08-08)**: Campaign summary workflow `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) is active and published on version `1cea3b9c-d587-4135-806d-46d301e2c7f4`. The response-shaping layer keeps `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary` separate. The selected-window response now includes SMS sent/failed/reply totals, normalized failure reasons, and distinct campaign-attributed opportunity counts. The verified 2026-07-09 through 2026-08-07 window returned 294 SMS sent, 1,095 failed, 0 replies, Emerald 3,909 opportunities, Partnership 8, and Vapi Brand 13.

- **Executive Report optimization (2026-08-08)**: Public build `2026-08-08-v18-opportunity-attribution` is deployed. Campaign filters, Vapi filters, campaign drill-downs, comparison view, SMS delivery diagnostics, campaign opportunity counts, LinkedIn metrics, and outgoing-call detail are live. The reports container nginx route for `/api/report/executive/outgoing-calls` was restored and verified HTTP 200.

- **Native GHL report cleanup (2026-08-08)**: Report `6a67dce4a51a4360c60963a3` is saved with the `Last 30 days` date range. The duplicate page-3 `Outgoing calls by status` widget was removed. The report still has three pages. Additional stage, campaign-tag, email, page-name, and custom-metric widgets remain open.

- **Voice stack**: ACTIVE since 2026-07-14, hardened 2026-07-16, optimized 2026-07-20, and call-path hardened 2026-07-23. All 3 outbound assistants (Jordan/Dispensary, Alex/Brand, Savannah/V1) updated: compliance disclosure removed from voicemail, discovery questions restructured to one-at-a-time with turn-taking enforcement, IVR/voicemail disambiguation added, stage-direction/throat-clearing ban, pronunciation fixes, `{{contact_name}}`→`{{first_name}}` variable corrected. On 2026-07-25, the Brand assistant and dialer were patched to remove the unresolved `{{company_name}}` opener dependency, pass `company_name` from GHL when available, and explicitly guard against missing placeholders. The dialer uses n8n's native Schedule Trigger every 2 minutes plus a timezone-aware business-hours guard; no external cron job is used. The callback webhook no longer automatically invokes the dequeue helper, and `LT - Voice Dequeue Next` is unpublished so it cannot start unscheduled calls. Callback metadata extraction, GHL note JSON handling, queue completion parameters, tag failure handling, and the 8-tag plus DNC suppression blocklist were hardened. The dialer now marks selected rows `in_progress` before the Vapi request, preventing ambiguous request failures from retrying the same contact; no-phone and outside-hours branches restore `pending`. Poller searches 4 tag pools with rotation, 30/cycle, and removes the source campaign tag after enqueueing. On 2026-07-25, the dialer was changed to continue fetching and filtering blocked/invalid contacts within the same execution, up to 25 queue checks, instead of waiting two minutes after every skipped contact. On 2026-07-30, the dialer and Call Outcome Ingest were repaired after a prolonged outage: GHL `Version` header corrected from `2023-02-21`→`2021-07-28`, the same-run loop guard was rewritten to read from Code-node items instead of invisible Postgres `RETURNING` columns, an empty-queue guard was added before GHL contact lookup, and the ingest workflow's `new Date()` expression was removed from the `queryReplacement` path. The 1,047 failed + 4 cooling_down queue rows were reset to `pending`, restoring 1,051 contacts to the active dialing pool.
- **n8n runtime**: upgraded to target `2.33.3`; redeployment of n8n and PostgreSQL is planned after the August 5 database connection-timeout incident. Native Schedule Trigger is the standard for recurring workflows. The Python task-runner warning during deployment is expected for JavaScript-only workflows; the stale queued-execution incident was resolved by deleting 745 orphaned `new` executions after the initial targeted cleanup, leaving legitimate `waiting` executions intact. The dialer was unpublished/republished, manually smoke-tested, and confirmed to select different queue contacts. It is active and published with the same-run queue loop.
- **n8n stale execution cleanup (2026-08-05)**: after the PostgreSQL/n8n redeploy, the database was healthy but `execution_entity` contained 6,946 `new` executions, 102 `crashed`, and 38 `error` records. The oldest `new` execution was from 2026-07-27. The largest backlogs were SimpleTexting Step Runner (1,915), SimpleTexting Phone Backfill (1,905), Partnership Reply Poller (788), Vapi Intake Poller (396), LinkedIn Reply Backfill (386), Vapi Dialer (313), and Campaign Contact Classifier (261). This is regular-mode stale scheduled execution state, not missing Queue Mode workers. Follow [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md): pause high-volume schedules, preserve recent webhook executions, delete stale scheduled `new` records through n8n UI/API in batches, then re-enable workflows gradually. Do not delete directly from PostgreSQL.
- **n8n stale execution cleanup completed (2026-08-05)**: n8n's PostgreSQL pool was rebuilt by restarting the n8n container, then nine high-volume scheduled workflows were unpublished. The supported n8n execution API deleted 6,964 stale `new` trigger executions with zero failures and preserved all webhook executions. The current `new` count is zero; 102 crashed and 38 error records remain as diagnostic history. The schedules remain paused pending controlled reactivation. `N8N_CONCURRENCY=10` is now staged in `n8n/docker-compose.yml` and will take effect on the next Coolify redeploy. See [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **n8n reactivation/optimization plan**: after the redeploy, reactivate paused workflows in tiers: allocator/classifier, reply-state pollers, intake/enrichment, then outbound senders and dialer last. SimpleTexting now has its own one-by-one re-enable sequence because both dispatcher recovery and provider acceptance require controlled verification. Proposed improvements are bounded batches, cheap no-work exits, atomic claims/idempotency, watermarks instead of full scans, and overlap guards. Full gates and cadence proposals are documented in [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **n8n reactivation and recovery**: after redeploy, the seven non-SimpleTexting workflows were republished and verified with matching `versionId`/`activeVersionId`. SimpleTexting production workflows were then temporarily paused after the execution-dispatcher incident recurred. The stale scheduled queue was cleared through the n8n API; nine webhook `new` executions were preserved and one webhook execution remained running. Timeout and pool settings are staged in `n8n/docker-compose.yml` for the next Coolify redeploy.
- **SimpleTexting workflow hardening (2026-08-06 through 2026-08-17)**: bootstrapped campaign state/event tables and indexes, removed runtime DDL, split Warmup preparation from sending, removed unsafe HTTP wrappers, added overlap/claim guards, hardened send/provider/callback boundaries, and reconciled historical state without replaying uncertain sends. Step Runner, Warmup, Pool, and Campaign Sequencer are unpublished; Phone Backfill is active and non-sending. See [docs/n8n-stale-execution-recovery.md](docs/n8n-stale-execution-recovery.md).
- **SimpleTexting audit/authentication pass (2026-08-06)**: live definitions and recent executions were rechecked. Step Runner and Phone Backfill exited cleanly with no work; provider health returned HTTP 200. Fixed provider-ID validation, active-event runtime DDL, webhook payload preservation, the stale nested Set assignment, the GHL intake HTTP wrapper, unresolved-contact handling, duplicate-event claims, and internal webhook authentication. Unauthorized requests now short-circuit without provider/state side effects; authorized dry-run sending succeeds. The authenticated GHL manual-send caller was updated in the UI to send `x-lt-simpletexting-key` and is published. SimpleTexting provider event headers are only required for inbound reply, delivery, and unsubscribe tracking; they do not block outbound API sending.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences. Reply suppression was repaired in GHL on 2026-07-26 after an inbound email continued into a later sequence step.
- **DAN email campaign**: FULLY LIVE AND SENDING since 2026-07-14. 10 templates, 3 GHL workflows, n8n dispatcher active (65/run every 30 min, 1,560/day capacity). ghl_contact_id backfilled 2026-07-13 (13,705 IDs). 181+ contacts queued first day with verified email delivery.
- **Apollo phone enrichment**: ACTIVE and hardened 2026-07-16. Production path is polling + V4 callback + reaper. Legacy staged webhook orphans were canceled, poller now re-discovers `queued_phone`, callback provider failures map to `callback_failed`, and known blank contacts were backfilled into `queued_phone`.
- **LinkedIn**: Production path is dispatcher -> acceptance/state sync -> canonical 4-message DM sequence. Follower DM and misconfigured Instagram DM sender paths are unpublished. The dispatcher now explicitly reads Config, atomically claims `ready` rows as `requested_pending`, performs immediate GHL tag/reply checks, and fails closed on provider/state errors. State sync uses direct HTTP requests, bounded contact/API budgets, retries/timeouts, explicit error reporting, and preserves terminal/replied state. The shared state-upsert workflow promotes explicit terminal payloads to `completed` and preserves active replies. The state-upsert webhook now requires the protected `X-LT-LinkedIn-State-Secret` header; all discovered callers were updated and published, and unauthorized requests return `403`.
- **Instagram**: old DM Sequence is unpublished after it was found using the LinkedIn Unipile account. New inbound bridge is active and posts messages into GHL Conversations under `Instagram via Unipile`.
- **Social provider bridge**: Instagram and LinkedIn inbound both work through SMS-type custom conversation providers (`LinkedIn: 6a58a14ff3023bea3783c152`, `Instagram: 6a58a1193cdfc36997580a68`). Inbound uses `type: "Custom"`, not `SMS`, and avoids dummy phone/email data. GHL duplicate cleanup consolidated Edmundo Cadorniga to canonical contact `XZ4yChllGBdcsVxhFRDe`; both Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` now map there. GHL Conversations is the operator-facing inbox; no dedicated macro dashboard or alert digest is live yet. Detailed handoff and operator runbook live in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **Reporting**: GA4, GHL, and GSC ingestion are live. **Call reporting fix (2026-08-01)**: the Executive Report's `GHL Calls` panel undercounted calls because the `calls`/`call_status_breakdown` CTEs read `report_raw_ghl_calls`, which `LT - GHL Daily Calls Ingest` (`SqNQ0BYaTdcqyt1l`) only populates by scanning 2 pages × 25 conversations where the last message is a call (85 calls in 30d). The authoritative `report_raw_ghl_call_outcomes` table is fed by the GHL Call Details webhook (`LT - Call Outcome Ingest`, `PUCfTZBANSPcgS0c`, 348 calls / 333 outbound in 30d). Both CTEs now read the webhook-fed outcomes table; verified live at Total 348 / Answered 261 / Missed 75 / Voicemail 11 / Inbound 14 / Outbound 333. **Channel/UTM attribution fix (2026-08-01)**: `report_channel_daily_summary` and `report_utm_daily_summary` each receive rows from two writers with incompatible keys — the GA4 Traffic Rollup Bridge (`0P2AZcQYWYZjXbRi`, GA4 sessions, `metadata.source='ga4_rollup_bridge'`) and Report Daily Rollups (`EUeOiRttoVLQ9zF9`, GHL contact/opportunity counts, `metadata.source_system='rollups'`). The API's `channels` and `utm_breakdown` CTEs previously grouped all rows by channel/source-medium-campaign and ordered by `sessions DESC`, so GHL-only rows (sessions=0) fell below the LIMIT and the UTM `leads`/`opportunities` columns were always 0. Both CTEs now FULL-JOIN the GA4 rows to the rollups rows on the shared key so each channel/UTM row shows traffic AND CRM outcomes, and channel names are normalized (`unattributed`/`Unassigned`/blank/`(none)`/`not set` → `Unassigned`). Verified live: channel breakdown now clean (Unassigned merges 155 sessions + 4,727 opps; Direct 403 sessions + 229 leads); named UTM campaigns (e.g. `wl_seq_cannabis_ads` 1,159 sessions) correctly show `leads=0` because GHL does not store UTM campaign fields on those contacts (confirmed against raw DB), while the 229 contacts that do carry UTM data land in the unknown bucket. The Executive Report is published on version `b5c67086`. GSC execution `281697` succeeded after OAuth renewal, fetched 10 rows for report date `2026-07-30`, upserted them, and finalized source health as `success`. `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on version `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`; it finalizes success, empty, partial, and failed fetch states, does not advance watermarks on fetch failure, and preserves raw-row idempotency. The reconnected GA4 credential was verified by execution `276731`; pinned failure execution `276747` confirmed health finalization followed by an intentional n8n error. `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on version `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`; it uses ingest-date snapshots, bounded cursor/retry guards, fail-closed finalization, and health key `ghl_opportunities` to avoid collision with leads. Execution `276626` processed 7,683 opportunities and 7,683 history rows successfully. The Executive Report is deployed as build `2026-07-31-v11-campaign-breakdown`; its campaign/channel table, selected-period comparison, and LinkedIn Invites/Accepted columns are live. After the live 10-contact Partnership LinkedIn test, the Executive Report shows 10 overall LinkedIn invites and attributes them to a `Partnership LinkedIn` campaign row via durable `connection_request_sent` ledger events. Native GHL report `6a67dce4a51a4360c60963a3` loads 11 widgets in an authenticated UI session. Its `Campaign Opportunities` widget is filtered to `Partnership Pipeline`, and its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`; the current 2026-07-19 through 2026-07-25 window showed zero/no data after filtering. Native GHL does not consume Unipile activity without explicit CRM synchronization. Detailed gaps and required report fields are documented in `docs/reports/Reporting Gaps and Requirements.md`.
- **Outgoing call detail (2026-08-06)**: Added and published `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`, version `d004556d-0b11-4a86-8827-f8f58a1eeee3`). Its GET webhook `/webhook/lt-report-outgoing-calls` returns up to 100 Vapi call rows from the seven most recent completed `America/Los_Angeles` days. The report host exposes this through `/api/report/executive/outgoing-calls` and renders it at the bottom of the Executive Report with pagination, disposition, duration, campaign, contact ID/name fallback, first-attempt state, and lazy signed recording playback. Manual execution `703098` succeeded and the production webhook returned 6 rows. This detail surface is separate from aggregate GHL call-status reporting.
 - **GHL PIT verification**: The root `GHL_PIT` was tested directly against the official REST API on 2026-07-31. `GET /locations/Zwz4relUXVPxx8uohnjV` and `GET /contacts/?locationId=Zwz4relUXVPxx8uohnjV&limit=1` both returned HTTP 200 with `Authorization: Bearer` and `Version: 2021-07-28`. The PIT is valid for CRM/API data access. It does not resolve the native Custom Report builder page's Firebase/browser-session failure, and the supported API/SDK still does not expose widget-layout mutation.
- **SMS campaign**: Automated sending is paused. Step Runner, Warmup, Pool, and Campaign Sequencer are unpublished behind dry-run/approval gates. Phone Backfill is active and only repairs campaign phone state. The send webhook, provider router, idempotent sender, inbound, delivery, and unsubscribe workflows are active with fail-closed validation.
- **SimpleTexting remediation**: Boundary hardening, callback registration, and database reconciliation are complete. The next gate is one approved live provider send or natural callback traffic; do not activate schedules solely to perform validation.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.
- **Regulated-business classification / SDR boundary (contract clarified 2026-07-30)**: `qualified` means the contact's business is related to a regulated vertical such as nicotine, cannabis, CBD, vape, or hemp; `not qualified` means it is not a regulated business. The live classifier now writes the canonical classification tags and the Vapi intake is published with a `qualified` gate. Qualified opportunities now enter `Sales Outreach -> Qualified` through published GHL workflow version 10. Existing contact/opportunity ownership alignment is handled separately; the live Jason/Marc allocator handles records entering that stage without a native owner.
- **SDR ownership synchronization**: Published GHL workflow `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, version 7) now keeps contact owner, native opportunity owner, custom opportunity `Owner`, and routing audit fields aligned for Jason and Marc when the opportunity owner changes. It does not replace the unresolved Janvi qualification gate or allocate unowned Warm records.
- **Classification and promotion implementation (2026-07-30)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is published on version `9eae8a33-319a-4c8a-9ee7-2b3b3d5fb45f`; `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) is published on version `99244f60-3c68-4c08-9bcb-1cf5d8bf20d1`; and GHL workflow `Move Contact's Opportunity to Sales Outreach New` (`cd29d8e6-5e0f-45f8-ba4f-c30804ad9b49`) is published as version 10 with both opportunity actions targeting `Sales Outreach -> Qualified`.
- **Ownership double-handling audit (2026-07-30)**: No active duplicate owner writer was found. The classifier writes tags only; Vapi intake writes queue/Apollo state only; the active n8n MQL workflow creates or updates Warm opportunities without owners; and the GHL promotion workflow changes pipeline stage only. The sole active owner-alignment path is GHL `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, published version 7), triggered by an opportunity `assignedTo` change. It assigns the contact and updates the custom opportunity `Owner` plus routing fields, but does not assign the opportunity owner. The staged n8n workflow `VI39o4X954fYDjOQ` is inactive and must not be activated as-is because it would duplicate those contact/custom-field writes.
- **Legacy-owner migration (2026-07-30)**: Migrated the open Sales Outreach opportunities whose custom opportunity `Owner` was John or Kevin. The initial scope was 307 records (305 John, 2 Kevin). The final authoritative opportunity search returned zero remaining John/Kevin custom-owner records; native opportunity owners and the published GHL alignment cascade are now the source of truth. The staged n8n owner-sync workflow remains inactive.
- **Jason/Marc no-owner allocator (2026-07-30)**: Published n8n workflow `LT - Sales Outreach Jason Marc No-Owner Allocator` (`eeksgD0fbGHUqh4r`) on a 30-minute native Schedule Trigger. It fetches open `Sales Outreach -> Qualified` opportunities, filters blank native owners in code, assigns Jason (`yU85G6kfhtW4vUtx3QE6`) or Marc (`sqGx5rp3oAUG610NXyjU`) using deterministic opportunity-ID hashing, and writes only native opportunity ownership. The first controlled run assigned 73 records successfully; sample verification confirmed contact owner and custom opportunity `Owner` cascaded correctly through GHL workflow version 7. Remaining unowned Qualified records are draining in bounded batches.
- **Follow-up sender routing - COMPLETE (2026-07-29, audited 2026-07-30)**: Workflow `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`) is published as version 39 with Jason workflow defaults (`Jason from Transparent eCom` / `jason@livetransparent.com`). All 7 Send Email actions use `From Name = {{opportunity.owner}} from Transparent eCom` and `From Email = {{user.email}}`. The six templates (one reused by 2 actions) retain literal Jason sender metadata as safe fallback. The workflow triggers on Sales Outreach stages: New, Attempting Contact 1st Attempt, 2nd Attempt, 3rd Attempt, Engaged. Marc routing path (`sqGx5rp3oAUG610NXyjU`) is configured but untested — zero Marc-owned opportunities have entered a trigger stage. Do not send a live test email unless explicitly requested.
- **Vapi transfer hardening**: Live transfer tool `86d380a3-34d2-41f8-96a0-acf5f0124ccb` and all four assistants now use neutral Sales Lead wording while preserving the compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600`.
- **RB2B assignment hardening**: Live workflow `3kjsIUeoEQFx26cC` no longer runs its hardcoded Kevin task during Warm intake. The legacy task node is disconnected/disabled and the workflow is published with contact persistence ending at `Result`.
- **Classifier per-contact fetch hardening (2026-08-07)**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) `Process Warm MQL Contacts` now emits self-diagnosing `fetch_error` records (`error` message + `status_code`) and retries GHL HTTP 429 rate-limit responses up to 3 attempts with linear backoff (1s, 2s) before failing. Root cause was a GHL per-window rate limit on the contact-lookup burst, confirmed by run `723561` (all 12 failures reported `status_code: 429`). Published active version `adcc6622-2e7e-4519-8acf-ba6a628dc8d9` (15-min schedule intact).
- **PIT token rotation (2026-07-30)**: Full GHL PIT token rotation completed and verified. The old token was replaced with the rotated PIT across both Config nodes that embedded it (Intake Poller `bYk1Ai6MJLyhTsDZ`, Dialer `r7UjWLndmc6EqEUW`). Full REST API audit of all 67 active n8n workflows confirmed zero occurrences of the old token remain in live production paths. Both modified workflows were published with matching `versionId === activeVersionId`. Documentation (`AGENTS.md`, `repomix-output.md`, `Operating Snapshot.md`) updated. Archive/backup files in `n8n/backups/`, `n8n/voice-agent/`, and `scripts/` retain historical snapshots.

## Prioritized Next Steps

1. ~~**Repair GHL Daily Sales Ingest first**~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities.
2. **Restore source coverage one system at a time** with supported ingest/replay and provenance. Opportunities now restored; voice, email, LinkedIn, SMS still at zero.
3. ~~**Authenticate public write boundaries**~~ **DONE for Call Outcome Ingest and SimpleTexting.** Review the remaining Warm intake boundaries; retain explicit approval gates for manual sends/calls.
4. **Audit and backfill `emerging_pool_contacts.ghl_contact_id`** — Sales Ingest is now healthy, audit can proceed.
5. **Verify voice persistence safely**, then recover campaign/email/LinkedIn/SMS reporting state.
6. **Migrate and rotate embedded secrets** using protected credential/runtime paths.
7. **Fix Executive Summary/date correctness debt** after source recovery.
8. **Add OAuth social statistics and finish native GHL report UI configuration**.
9. **Clean legacy artifacts and reconcile historical prose last**.
10. **Build company-page Instagram enrichment and delivery**: create the eight company-level fields, produce source/match/review reports, resolve Brands and Dispensaries company pages through Unipile, create authoritative Postgres state, run dry-run and controlled live gates, then activate the weekday dispatcher. Partnerships remain blocked on separate Instagram URL enrichment; Facebook Messenger remains deferred to native GHL Messenger and cannot use public Page URLs/Page IDs as recipient IDs.

### Explicit Reporting Notes

- The campaign summary workflow is live and published as `1cea3b9c-d587-4135-806d-46d301e2c7f4`; live 7-day/30-day endpoint checks return named rows, SMS diagnostics, and campaign opportunity counts.
- The `2026-07-20` through `2026-07-26` email engagement gap is a historical `Email_Events` coverage gap; no event-ingest executions existed in that window. Do not change valid aggregation logic or fabricate rates.
- Four credential-bearing response captures remain intentionally untracked and must not be committed.

## Newly Confirmed Gaps

### Follow-up Sender Routing Handoff

- **User requirement**: follow-up email sender name and email must follow the opportunity/contact owner; if neither record has an owner, use Jason.
- **Workflow**: `Jason Followup Emails and SMS`, ID `f6b44e34-779e-4959-b41d-b05641f134e7`, currently published version `39`.
- **Template folder**: `Jason Follow Up Emails`, ID `69e0c9069af5986541802d88`.
- **Affected template IDs**:
  - `69e0d86b9af59801b580f4b5`
  - `69e0db27d6a707bbf190d022`
  - `69e0db9ab02114c1ba3c29d3`
  - `69e0dc56d6a707c0ac90e074`
  - `69e0dcad8ffabf47b4d987c5`
  - `69e0ddd0b021145bab3c4569`
- **Current template state**: all six have literal `fromName = Jason from Transparent eCom` and `fromEmail = jason@livetransparent.com`. Keep this as a safe fallback; the live workflow actions already override it for owned records.
- **Current workflow state**: all 7 Send Email actions use owner-driven sender fields. Verify or set Jason as the no-owner fallback user in the workflow UI. Do not hard-code Jason as the sender for owned opportunities/contacts.
- **API limitation**: `PATCH /emails/builder/{templateId}` accepts literal sender emails but rejects `{{user.email}}` with HTTP 422 (`fromEmail must be an email`). The public `GET /workflows/` endpoint confirms metadata/status/version only; workflow action definitions are not writable through the public API.
- **Browser status**: authenticated GHL workflow access was used to set and publish the Jason defaults. The published version 39 API response confirms `senderAddress` and `status: published`.
- **No test send**: no live email was sent during this investigation or patch.
- **Next session exact order**:
  1. Open the authenticated GHL workflow URL from the user-provided link.
  2. Monitor the next normal follow-up execution; do not send a live test email solely for sender verification.
  5. Reopen the workflow and verify all 7 Send Email actions and the published version.
  6. Do not change template HTML or send a live test without explicit approval.

- ~~**Dialer credential rotation**: verified against GHL, full audit of 67 active workflows confirmed PIT rotation complete. Both Config nodes updated and published.~~ **Done 2026-07-30**
- **Callback authentication**: Vapi server authentication is configured on all four tracked assistants and enforced at the callback boundary with `X-Vapi-Secret`. Unauthorized callback, status, and tool payloads are rejected before routing.
- **SMS and Warm webhook authentication**: SimpleTexting send and provider callback boundaries are hardened. Several Warm intake webhooks still have empty shared-secret configuration and require an authentication pass before continued public use.
- **Credential storage**: active n8n Config nodes still contain API keys and webhook secrets. Migrate to n8n credentials or protected runtime configuration, then rotate exposed values.
- **LinkedIn state-upsert boundary**: `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on version `d9168bbc-9c96-44fd-a356-12e645a2ec3d` with terminal-state promotion, reply preservation, and protected `httpHeaderAuth`. All discovered callers are published with the shared header; unauthorized verification returned `403` and malformed authorized verification reached validation without writing state.
- **LinkedIn Config convention**: all eight relevant state-upsert workflows now have exactly one `Config` node. Callers read `Config.stateUpsertSecret` instead of embedding the shared header value in request code. This is the Community Edition variable workaround, not a replacement for managed credentials.
- **Ingest hardening (2026-07-31)**: GA4 empty/failure finalization, sales snapshot-date and cursor guards, sales `ghl_opportunities` health isolation, LinkedIn sync budgets/retries, dispatcher pre-invite claims, and terminal-state promotion are live and published. Dispatcher and sync were not live-executed during verification because they can mutate LinkedIn state or send invites.
- **Reporting owner dimensions**: contact owner, opportunity custom `Owner`, owner conflicts, and canonical SDR identity are not normalized into the reporting read model.
- **Campaign-level reporting dimensions**: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) returns canonical DAN, Emerald, Partnership, Instagram, Vapi Brand, Vapi Dispensary, and SMS rows. Public report build `2026-08-17-v27-social-mql` has campaign/channel filters, drill-downs, comparison view, opportunity counts, SMS diagnostics, LinkedIn and Instagram activity columns, resolved GHL stage labels, explicit Social Planner placement/account-statistics definitions, MQL conversion metrics, and responsive table containment. Native GHL campaign-tag and email-detail widgets remain open.
- **Partnership state and outbound safety (2026-07-31)**: The email, LinkedIn dispatcher, and LinkedIn DM workflows were activated after explicit approval and use `defaultDryRun=false`. Their live schedules and suppression/idempotency guards remain authoritative; do not manually execute them unless an additional live batch is intentional. `partnership_linkedin_connection_state` remains the isolated Partnership state store.
- **Tag-based attribution audit (2026-07-30)**: DAN has reliable queue tags (`Enrollment Queue - DAN - Brands/Dispensaries`) plus `DAN_Release_Log.campaign` and `enrollment_tag`; `brands_pool`/`dispensaries_pool` should remain supporting audience evidence. Emerald has eight bucket-specific queue tags and matching `Seq Emerald - ...` tags, with stronger backend fields in `Emerald_Campaign_Contacts.bucket/email_campaign` and `Emerald_Release_Log.bucket`. SMS has lifecycle tags but its durable campaign identifier is `SimpleTexting_Campaign_State/Event_Log.campaign_key`; `sms_drip` is only the eligibility pool. LinkedIn has lifecycle/suppression tags but no durable campaign tag, so current Brand/Dispensary attribution must use `emerging_pool_contacts.source_list` or historical pool-tag observations until a campaign key is added to state.
- **Vapi correlation**: end-of-call callbacks now recover missing `queue_id` values from prior `voice_call_attempt` records when possible. The dialer also reclaims stale `in_progress` locks after 15 minutes, while unresolved provider correlation remains observable through the callback execution path.
- **Gap fixes applied 2026-07-25**: silent human Vapi answers now classify as `interest_unknown`; dialer global hours are 9am-5pm CT; invalid campaign tags fail closed; source-tag cleanup is dynamic; report config/publish schedules are connected and tested; superseded Apollo Sheet First webhook is unpublished.
- **Vapi hardening applied 2026-07-27**: intake, direct enqueue, and dialer paths require the `not qualified` suppression guard plus an open Warm → New opportunity; callback requests require the Vapi server secret; tool outcomes complete queue rows; timer scheduling uses an atomic Postgres claim; stale queue locks are reclaimed; timer and GHL cleanup requests retry transient failures. The intake still needs to require positive `qualified` classification so raw pool tags cannot bypass the classifier.

## Email Campaign — Emerald (Active 2026-07-07)

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (All Published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed}
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Reply Suppression Repair (2026-07-26)

- **Incident**: Christy Essex replied on 2026-07-23 that she had left Vangst and referred new/current-project questions to Logan Humiston. An automated Emerald follow-up was still sent on 2026-07-26.
- **Root cause**: `WL - Seq - Stop on Booked/Reply/Closed` had the correct `Customer Replied to Sequence Emails` trigger filtered to Email, but its `Remove from Workflow` action only removed the legacy Variant A/B workflows. It did not include the Emerald sequence workflows.
- **Fix**: Through the GHL UI, added all 12 Emerald sequence workflows, including P2 variants, to the removal action. Published as version 17.
- **Immediate containment**: Removed Christy's `seq enrolled - emerald` and `seq emerald - executives sso` tags. Her Warm/MQL context and opportunity were preserved.
- **Boundary**: n8n `LT - Email Event Ingest` remains reporting-only; it stores events in `Email_Events` and is not the sequence suppression mechanism.

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,165 | ~14,702 pending, ~5,463 released |
| Emerald_Release_Log | 250+ | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## Email Campaign — DAN Brands & Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Status

- Templates: CREATED (10/10 -- 5 Brand + 5 Dispensary)
- Tags: CREATED (5/5 -- deployed via GHL API)
- Dispatcher: LIVE (toUG1yPDmFG48KEP, active with defaultDryRun=false, every 30 min, candidateLimit=85)
- GHL Workflows: ALL PUBLISHED (3/3)
- Deck Download automations: CREATED in GHL
- ghl_contact_id backfill: COMPLETED 2026-07-13 (13,705 IDs backfilled via email/phone/name matching)
- **5,373 contacts now eligible for DAN dispatch (up from 13 before backfill)**
- **First dispatches confirmed**: Emails sending via GHL (TYPE_EMAIL outbound automated verified)
- **Rate limiting fix**: 250ms delay added between GHL API calls — errors dropped from 40% to 0%
- **2026-07-15 audit**: 5 fixes applied (brand starvation, HTTP wrapper, sender rotation, error logging, jitter)
- **GHL templates verified**: All 10 DAN templates in GHL match repo HTML files exactly

### GHL Workflows

| Workflow | ID |
|----------|-----|
| DAN - Brands Sequence | 5d25147c-cd63-4c4f-ba49-a0e62c53ee0c |
| DAN - Dispensaries Sequence | ec24cbb8-bd0b-4e6e-8607-d93886a02034 |
| DAN - Stop on Reply or Booked | d7ff2fc2-cdc2-4952-afa7-71cd9edfc490 |

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Template IDs (Brands, folder 6a4f6b06a3e9bfb4f9ebe8ad)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fdf525ebffbb911d88c | DAN - Brand 1 - Quick Question |
| 2 | 6a4f6fe0f34b953ec0cfcf5d | DAN - Brand 2 - How It Works |
| 3 | 6a4f6fe15e7d25184dafed44 | DAN - Brand 3 - Housing Works |
| 4 | 6a4f6fe2525ebffbb911d899 | DAN - Brand 4 - Short Version |
| 5 | 6a4f6fe3890f1fb4ac750664 | DAN - Brand 5 - Closing |

### Template IDs (Dispensaries, folder 6a4f6b128c6f614ebf8ba9e9)

| # | ID | Name |
|---|----|------|
| 1 | 6a4f6fe4890f1fb4ac750680 | DAN - Dispensary 1 - Foot Traffic |
| 2 | 6a4f6fe41ad559bda229477d | DAN - Dispensary 2 - How It Works |
| 3 | 6a4f6fe55e7d25184dafed8a | DAN - Dispensary 3 - Housing Works |
| 4 | 6a4f6fe6f74b73e4b5b9ad8d | DAN - Dispensary 4 - Founding Partner |
| 5 | 6a4f6fe71ad559bda2294793 | DAN - Dispensary 5 - Closing |

**Duplicate**: 6a4f6fcdf74b73e4b5b9ac0b — already removed from GHL (verified 2026-07-15)

## Voice Workflows

Phone: +1 (562) 534 1977
Callback webhook: https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback

### Active

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Webhook |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Webhook |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Unpublished helper |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly (monitors queued + queued_phone) |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (native Schedule Trigger every 10 min, 30 contacts/cycle, tag rotation) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is active on a native 15-minute Schedule Trigger.
- It selects up to 10 Brand and 10 Dispensary candidates per run, uses live GHL suppression checks, and applies Vapi campaign tags only after DeepSeek acceptance or a qualified-domain match.
- `vapi_qualified_domains` is updated only after a successful campaign-tag write; free-email domains, cleanup rows, failed writes, and rejected model output are excluded.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes.

### Fixes Applied — Original (2026-07-14)

- **Published** both Intake Poller and Outbound Dialer (were paused for quality gate)
- **Trigger Apollo Enrichment auth**: changed `predefinedCredentialType` → `none` (was crashing because GHL API key is already in headers)
- **Remove Tag - Enriching URL**: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID under `contact`)
- **Full pagination**: GHL contact search was limited to first 20 contacts per tag. Added pagination loop with 250ms delays.
- **30-contact batch cap**: prevents GHL rate limiting on downstream API calls
- **Pool tag search**: added `brands_pool` (3,024) and `dispensaries_pool` (7,953) to search tags alongside `vapi_campaign_brand` (926) and `vapi_campaign_dispensary` (19)
- **Tag rotation**: cycles through one tag per 10-min run to ensure all pools are scanned evenly
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`). Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`). Most pool contacts lack timezone data, so this ensures ET contacts get called at 9am ET.
- **Historical ET-forward timing**: the previous cron-based schedule shifted from `*/2 14-22` to `*/2 13-22` UTC to start calling at 9am ET instead of 10am ET. The current implementation uses a native two-minute Schedule Trigger; the timezone-aware business-hours guard remains authoritative.

### Fixes Applied — Round 2 (2026-07-14, Full Vapi Audit)

A comprehensive logic/code/optimization audit of all 12 Vapi workflows found 5 bugs across 3 active workflows, all fixed and published:

**1. Race condition: Dialer could send duplicate calls** (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` was a read-only `SELECT...LIMIT 1`. Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item. Fixed: changed to `UPDATE...FROM...RETURNING` that atomically locks the row at fetch time.

**2. `report_referral` tool was dead code** (fx4UvKUWbqJEY3LK)
Routed to end-of-call handler that checked `endedReason`/`analysis.summary` — absent on tool call payloads. Node returned `[]` silently. Fixed: re-routed to `Respond - 200`.

**3. Intake Poller could create duplicate queue entries** (bYk1Ai6MJLyhTsDZ)
INSERT lacked `WHERE NOT EXISTS` dedup check. Fixed: wrapped INSERT with `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also fixed `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing).

**4. Workflow-crashing tag removals** (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes lacked `continueOnFail`. A flaky GHL API call crashed the workflow after enqueue/enrich/skip already succeeded. Fixed: enabled `continueOnFail: true` on all three.

**5. Timer race condition** (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain. Fixed: replaced `timersScheduled` boolean with `timersScheduledAt` timestamp and 60-second dedup window.

### Fixes Applied — Call-Path and Callback Hardening (2026-07-22 to 2026-07-23)

- **Unscheduled call path removed**: the callback workflow previously posted to `LT - Voice Dequeue Next` after every end-of-call event. That helper could start another Vapi call without the dialer's Schedule Trigger. The callback trigger was removed and `LT - Voice Dequeue Next` was unpublished; it is now an explicit helper only.
- **Callback payload recovery**: the callback Config Set node replaced the webhook input before detection. `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` item directly.
- **End-of-call metadata coverage**: the normalizer now reads IDs from Vapi `assistant.metadata`, `assistant.variableValues`, and `artifact.variables` paths.
- **GHL note safety**: completion-note JSON now uses an object expression instead of interpolating unescaped summaries into a JSON string. Note and tag writes are non-blocking so a CRM note failure cannot prevent queue completion.
- **Queue completion safety**: `Postgres - Mark Queue Completed` now passes query replacements as an array, preventing the scalar-parameter error that previously stopped completion.
- **Scheduler standardization**: the outbound dialer uses a fresh native Schedule Trigger with a two-minute interval. The business-hours guard remains the call eligibility authority. Resolved 2026-07-30: the dialer was crashing on every execution due to three separate bugs (GHL `Version` header, Postgres `RETURNING` visibility, empty-queue 403) — fixed and verified end-to-end.

### Fixes Applied — Brand Prompt and Variable Context (2026-07-25)

- **Execution audit**: callback execution `241579` received an `in-progress` status update and entered the background timer as designed. The corresponding end-of-call callback `241581` completed successfully for queue `7aed3bdb-fe22-4b98-a4ce-33b9018fe32b`, normalized the outcome as `voicemail`, applied `vapi_voicemail` and `vapi_voicemail_left`, inserted the call attempt, and marked the queue row completed.
- **Brand assistant prompt** (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`): removed `{{company_name}}` from the first-message opener so a missing company value cannot be spoken as an unresolved placeholder. Added explicit runtime-variable handling, IVR-versus-voicemail disambiguation, one-question turn-taking, and no-stage-direction rules. The live-call AI/recording disclosure remains system-prompt-only and is excluded from voicemail.
- **Outbound dialer** (`r7UjWLndmc6EqEUW`): `Code - Check Phone` now extracts `company_name` from the GHL contact; `Build Vapi Body` passes it through `assistantOverrides.variableValues` and metadata. The workflow was republished and verified with matching `versionId` and `activeVersionId`.

### Queue State

**1,051 contacts pending** (reset 2026-07-30 from 1,047 failed + 4 cooling_down), 1,615 completed. New pool contacts fed in at 30/cycle via tag rotation. SQL `WHERE NOT EXISTS` prevents duplicate enqueue. Outbound dialer is configured for a native two-minute Schedule Trigger and picks up from queue only during timezone-aware business hours. Blocked/invalid/outside-hours candidates are released and skipped within the same execution, capped at 25 queue checks.

### Final Production Hardening — 2026-07-23

- Callback timer state now has the existing 60-second duplicate-start guard plus 30-minute pruning of ended/inactive records.
- `LT - Voice Queue Enqueue` now requires `X-LT-Voice-Queue-Secret`; callers use `VOICE_QUEUE_ENQUEUE_SECRET` and unauthenticated requests fail closed before queue insertion.
- Apollo phone-request failures are counted as `apollo_phone_request_failed` for monitoring.
- `LT - Apollo Queued Timeout Reaper` now connects its Slack summary builder to `Post to Slack #reaper`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- All modified live workflow versions were verified published with matching `versionId` and `activeVersionId`.

### LinkedIn Queue State

Legacy step-4 LinkedIn DM rows are now marked with `linkedin_dm_sequence_completed` and excluded from future DM selection. The GHL connect dispatcher was stuck with 0 `ready` contacts because its feeder tag check was broken (never detected blocking tags). Fixed 2026-07-14 by unwrapping GHL's nested `contact.tags` response. 14,987 contacts from CSV bulk-upserted as `connection_status = 'ready'` on 2026-07-13. Dispatcher should now find contacts on its next scheduled run.

### Call History Summary (voice_call_attempt)

1,711 total attempts across 1,045 unique contacts. Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18.

## LinkedIn Workflows (Production Active + Duplicate Send Paths Stopped)

| Workflow | ID | Schedule | Notes |
|----------|----|----------|-------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | 0 12-22 * * 1-5 | Fixed trailing backtick in jsCode; added template pre-sanitize + send-time sanitize in both DM sender nodes |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished | Redundant one-touch follower DM path; stopped 2026-07-16 after canonical connected-contact DM sequence was confirmed as the only production DM path |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | */15 15-21 * * 1-5 | Fixed GHL response unwrap in tag check; added send-time sanitize for invites; added linkedin_dm_sequence_completed to Feeder tag block |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | 15 */6 * * * | Reduced maxPages 15→5, maxContacts 200→50 |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Webhook | Replaced $env.UNIPILE_ACCOUNT_ID with hardcoded value |
| LT - LinkedIn Connection State Upsert (Unipile) | Old7ZvyVYgFaJgDr | Webhook | No changes |
| LT - LinkedIn Unipile New Messages (Unipile) | 7o5EBdvwAuIaWW7k | Webhook | Active on `f96dafba-9818-4aab-8656-c2e4e2ab8480`; malformed form-payload field recovery preserves inbound reply data |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual only | No changes |
| **LT - LinkedIn DM Suppression from GHL Tag** | **IPN8jnR3XSurX0o1** | **Webhook** | **NEW 2026-07-15. GHL tag stop_linkedin_dms → webhook → Unipile lookup → GHL tag + state table terminal** |

Intentionally stopped non-canonical sender: `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) is unpublished. It was using the LinkedIn Unipile account ID and sending Instagram templates as LinkedIn DMs via `instagram_dm_state`.

Guardrails: John-branded copy blocked before Unipile send. Invite defaults say Transparent eCom (not LiveTransparent).

Outbound guardrails: DM sends now fail closed if the reply lookup fails, and both DM / request paths skip when an inbound conversation is already present.

### 2026-07-15 Unicode Encoding Fix
All audited Unipile message sender nodes now sanitize message text before API calls, and template registries are pre-sanitized where present. Coverage includes LinkedIn DM Sequence (`Sync Connected from Unipile` and `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. `sanitizeMessage()` handles smart punctuation plus mojibake forms like `canâ€™t` / `canΓÇÖt`. Final live audit passed: active versions published, send-time sanitization present, registry pre-sanitization present where applicable, and no remaining bad literal template text in audited sender nodes. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.

### 2026-07-16 Sender Path Cleanup
Malformed LinkedIn screenshot messages were traced to `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM Sequence. Unpublished both `iCnY6ccdHhfJg3sf` and redundant `pq7XVajNFnnwMUTr`; production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.

### 2026-07-14 Fixes Summary
- **Connection Acceptance Checker**: `$env.UNIPILE_ACCOUNT_ID` blocked by N8N_BLOCK_ENV_ACCESS_IN_NODE → hardcoded
- **Connection State Sync**: Code node timed out at 300s → reduced batch sizes
- **Follower DM Sequence**: Code referenced missing Config fields → added them
- **DM Sequence**: Trailing backtick in `jsCode` caused syntax error → removed
- **Dispatcher feeder tag check**: `GET /contacts/{id}` returns tags at `contact.tags`, not flat `tags`. Whole pipeline was stuck because blocking tags were never detected. Fixed by unwrapping through `.contact` first.

### Dispatcher Queue State
The `linkedin_connection_state` table was exhausted (all contacts at `requested`/`connected` from June). User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook as `connection_status = 'ready'`. Dispatcher's Fetch Ready Queue should now find contacts on next run.

## Instagram

### Active

| Workflow | ID | Status | Notes |
|----------|----|--------|-------|
| LT - Instagram Unipile New Messages | pISlgYUsyJIrLuJd | Active webhook | Receives Unipile Instagram inbound payloads at `/webhook/lt-unipile-instagram-new-messages`, normalizes identity, creates/updates GHL contacts, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token, and posts inbound messages into GHL Conversations under `Instagram via Unipile`. |

### Stopped

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished | It used LinkedIn account `V9eiHiDpRmCtan0YNdzsQw` and the old `instagram_dm_state` model. Do not republish as-is; rebuild the company-page workflow using Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, company identity fields, reply suppression, and safe cadence. |

### 2026-07-16 Inbound Mapping Status

- Detailed build context, endpoint contracts, known test payload, and next steps: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- Confirmed real Instagram Unipile account: `F2UprZ8aQc6Qm9CYYWU6cg` (`Transparent eCom`).
- Confirmed test inbound identity: `edmundocadorniga`, profile provider ID `6361495593`, messaging/provider ID `109928757071246`, chat ID `yx-R-9J6XdWaFpGOQd1JFA`.
- Created GHL custom fields for Instagram username/profile URL/profile provider ID/chat attendee ID/chat ID.
- Post-merge cleanup: GHL duplicate contacts for `Edmundo Cadorniga` were consolidated to canonical contact `XZ4yChllGBdcsVxhFRDe`; `instagram_conversation_map.id = 1` now maps chat `yx-R-9J6XdWaFpGOQd1JFA` to that canonical contact.
- Inbound OAuth fix: the workflow converts the stored agency token to a location token inline before calling GHL inbound APIs.
- Direct outbound router test: POST to `/webhook/lt-social-provider-outbound` routed the known Instagram contact/chat to Unipile successfully with message id `DOfjxs8_Xm26V5Ee1IO7PQ`.
- Map repair verification: temporary maintenance workflow `nuuB3qCKxr7J6iPw` repointed Instagram map row `1` and LinkedIn map row `2` to `XZ4yChllGBdcsVxhFRDe`, then was archived. Direct outbound router checks succeeded for Instagram (`vjdEYSk9XD6R0I46oPWLwA`) and LinkedIn (`C7I9944kWsSKutX2XhZEpA`).
- GHL UI outbound verification: message `this is a test reply from GHL to Instagram` routed through `LT - Social Provider Outbound Router` to Unipile message `iEJO1vnvWVGwbk7ril1__A`.

### Social Provider Next Steps

- Monitor the next real Instagram inbound after duplicate cleanup; avoid artificial replays unless needed because they create visible conversation messages.
- Confirm Unipile Instagram webhook delivery to `/webhook/lt-unipile-instagram-new-messages` in production.
- `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) direct webhook path is fixed and routes canonical contact `XZ4yChllGBdcsVxhFRDe` to Instagram and LinkedIn via Unipile successfully using canonical provider IDs.
- Optionally run a controlled LinkedIn GHL UI outbound reply test from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Build and verify a lightweight macro alert/digest path for inbound LinkedIn/Instagram messages after they are successfully posted to GHL Conversations.
- Rebuild Instagram outbound/follower DM only after the bidirectional inbox path is stable and guarded.

## Apollo Phone Enrichment (Repaired 2026-07-14, Audited + Hardened 2026-07-15)

### Before Fix (2026-07-14)

All 3 webhook-based workflows had 0 executions since 2026-05-13. 1,279 contacts collected `callback_timeout`. Entire pipeline was dead.

### After Fix (2026-07-14)

New **LT - Apollo Phone Enrichment Polling** (JH8ShfpglWmLMZ3l) replaces the webhook-based intake:

1. **Sync profile match**: Calls Apollo `/v1/people/match`, writes name/email/company/LinkedIn/title/dept/revenue to GHL immediately
2. **Async phone request**: Calls Apollo with `webhook_url` pointing to existing V4 callback handler
3. **V4 callback** receives phone data and updates GHL

State as of activation (first hour): 60 contacts enriched, 30/run at 30-min cadence.

### 2026-07-15 Full Audit (7 workflows)

Full review found 2 CRITICAL bugs (`queued_phone` invisible to reaper, Intake Poller re-trigger), 2 HIGH issues (HTTP wrapper, V3 no error handling), and several medium/low cleanups. **10 fixes applied across 6 workflows**:

| # | Severity | Fix |
|---|----------|-----|
| 1 | CRITICAL | Reaper now monitors both `queued` + `queued_phone`; polling writes `Queued At` date |
| 2 | CRITICAL | Intake Poller routes `queued_phone` to `waiting` (was defaulting to `enrich`) |
| 3 | CRITICAL | Sheet First SQL injection fixed — parameterized query replacing template literal |
| 4 | HIGH | `doHttpRequest` wrapper removed from all 4 active workflows (V4, V3, Intake Poller, Sheet First) |
| 5 | HIGH | V3 callback: added error handling catch block with `callback_failed`, then **unpublished** V3 |
| 6 | MEDIUM | Polling `ghl()` now returns status codes; 429 triggers 5s retry on all 3 search sources |
| 7 | MEDIUM | V4 `Apollo Contact Id` now always set (was phone-gated) |
| 8 | LOW | Reaper Config node corruption cleaned (nested `parameters.parameters` removed) |
| 9 | LOW | Intake Poller `removeTag()` — removed `$httpRequest` fallback, now direct `this.helpers.httpRequest` |
| 10 | N/A | `$httpRequest` reference eliminated from all Apollo workflows |

### Pipeline Status (end-to-end)

| Step | Workflow | Handles |
|------|----------|---------|
| Discovery | Intake Poller (bYk1) | Tags contacts, sets `Enrich Phone via Apollo = Yes` |
| Sync match | Polling (JH8Sh) | Apollo `/v1/people/match` → writes profile, sets `queued_phone` + date |
| Async phone | Polling (JH8Sh) | Apollo with webhook → V4 callback |
| Phone callback | V4 Callback (U7c6) | Writes phone to GHL + `enriched` status |
| Re-enqueue | Intake Poller (bYk1) | Finds `enriched` contacts → inserts to voice_call_queue |
| Timeout | Reaper (RL5Zy) | Hourly scan for `queued` + `queued_phone` → `callback_timeout` after 24h |

### Workflow Summary

| Workflow | ID | Status | Purpose |
|----------|-----|--------|---------|
| LT - Apollo Phone Enrichment Polling | JH8ShfpglWmLMZ3l | Active, every 30 min | Polls GHL, calls Apollo sync+async, writes profile + triggers phone callback |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active, webhook | Receives Apollo async phone callbacks, writes phone to GHL |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** | Legacy V3, fully superseded by V4 |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active, webhook | 0 executions — superseded by polling, SQL injection fixed |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** | Legacy path. 1,008 orphaned webhook executions canceled on 2026-07-16; not part of production enrichment |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active, hourly | Flips stale `queued` + `queued_phone` to `callback_timeout` |

### 2026-07-16 Production Hardening

- Verified live production workflows are active and published:
  - Polling `JH8ShfpglWmLMZ3l`
  - Callback V4 `U7c6byTLXAMgcS75`
  - Reaper `RL5ZyUoshSPbmVA1`
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed past the `Webhook` node.
- Polling workflow fix: orphan status rediscovery now includes both `queued` and `queued_phone`.
- Callback V4 fix: Apollo provider-level callback failures now map to `callback_failed` rather than silently landing as `no_match`.
- Polling write-path fix: hardened GHL `PUT /contacts/{id}` fallback after reproducing live API behavior.
  Working update shape is `customFields` without `locationId`; payloads containing `locationId` or `customField` can return `422`.
- Polling now has a minimal fallback write so contacts are not left blank when the full Apollo profile write fails.
- Backfilled 6 previously blank contacts into `queued_phone` on 2026-07-16:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

## SMS Campaign — SimpleTexting via GHL (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

### Live n8n Workflow State

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Fail-closed provider validation, E.164 normalization, GHL suppression check, and confirmed-result enforcement; version `dfbb09db-890c-48ef-83a6-9cf4a64863f4`. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Registered protected callback; Slack alert and GHL Conversations mirroring preserved; version `d657c79b-f075-4241-a78d-0be33f67f627`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Defaults to dry-run; validates auth, templates, business hours, suppression, and provider result; version `47dd0303-3d36-49e4-9bd9-e34873edbad2`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated boundary with strict input and boolean validation; version `bcc7d22e-58b8-4419-a56f-753ff80773b8`. |
| LT - SimpleTexting Warmup Dispatcher (Staged) | dZQLlbTLkpE1843X | Unpublished | Sender-capable; keep paused pending explicit approval. |
| LT - SimpleTexting Campaign Step Runner | dUyOfxllvkxZavaw | Unpublished | Dry-run guard enabled; smoke `757254` stopped before claims. |
| LT - SimpleTexting Campaign Phone Backfill | 8hQKQi1PooYDFxNR | Active | Non-sending phone-state repair; supports `awaiting_phone_refresh` and `phone_unavailable`; version `83202303-bca2-4786-9bce-eed8147307c3`. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Unpublished | `sms_drip`, 10/run, weekdays 10:15am + 3:00pm ET; dry-run/small-batch gate required. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Unpublished | 6-step flow; do not run concurrently with Step Runner until canonical path is decided. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | Registered protected callback for delivery/non-delivery; version `31e884de-b4fe-4f03-af22-49cb64b766a1`. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | Registered protected callback for unsubscribe reports; version `c21eb489-9561-4393-8d52-f8a8231fa0a7`. |

### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- SimpleTexting send boundary uses `AUTO` mode so multi-segment campaign messages are accepted; provider errors are persisted for diagnosis and can be reclaimed on retry.
- Campaign mirroring is gated on `action = message_sent` and a non-empty provider message ID. Dry runs, blocked sends, duplicates, and provider errors do not call GHL Conversations.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.

### Current Template Registry

- Send webhook: `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`.
- Canonical keys: `sms_1` through `sms_6`.
- Updated 2026-07-26: `sms_1`, `sms_3`, and `sms_5`.
- Unchanged 2026-07-26: `sms_2` and `sms_6`.
- Updated 2026-07-29: `sms_4` removed cannabis product terms and the unreliable Facebook ad preview link while retaining `regulated-industry` positioning. The published active version is `506303a9-8c6f-466d-9cb6-3e1f68cfc40c`.
- Existing `john_sms1` through `john_sms5` payload aliases remain in place for compatibility and were not renamed.

### 2026-07-24 Fix And Next-Run Check

- Root cause of the `409` provider errors: `LT - SMS Idempotent Send` hardcoded `SINGLE_SMS_STRICTLY`, while SMS 1 is 320 characters and requires multi-segment delivery.
- Root cause of the GHL `404 Contact id not given`: `LT - SimpleTexting SMS Send` mirrored blocked and dry-run outcomes instead of only successful provider sends.
- Fixed and published workflows: `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`) and `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`).
- Safe checks passed: idempotent `simulate:true` execution `241272`; campaign dry run `241275` stopped before the mirror node.
- **Next scheduled dispatcher check:** confirm at least one `status = sent` result with a real SimpleTexting provider message ID, no HTTP `409`, no GHL `Contact id not given` errors, and a matching `report_sms_sent.provider_response` record. Then confirm the campaign state advances to `sent_step_1` only for an actual provider send.

## Partnership Marketing Pipeline (LIVE 2026-07-31)

131 content partnership contacts imported from two CSV lists ("Email" and "LinkedIn") and merged/deduplicated. Two parallel outbound sequences run from Cameron's accounts: a 4-step email sequence (60/day, 11am ET Mon-Fri) and a 4-step LinkedIn DM cadence dispatched through Unipile (30 connection requests/day, 3pm CT Mon-Fri). Both sequences use 2-weekday intervals between steps. All infrastructure is fully isolated from the main DAN/Emerald pipelines (separate Postgres tables, separate n8n workflows, separate GHL pipeline).

### Import

- 131 unique contacts after dedup/merge (script: `scripts/clean_partnership_data.py`)
- 98 email contacts imported via n8n batch workflow (`zmrYrUjVcyXaS7PJ`, webhook `/webhook/lt-partnership-bulk-import`)
- 33 LinkedIn-only contacts created in GHL via MCP (no email; LinkedIn URLs set via `ew6uQQnAjgCbjeGn` webhook)
- All contacts assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`)
- Tags: `partner_candidate_email` (email contacts), `partner_candidate_linkedin` (LinkedIn contacts), or both
- 14 contacts excluded from original CSV due to wrong company/email domain mismatches — awaiting corrections from user
- Test contact `NVAp2GdpbWXLheyUgVf2` (edmundocadorniga@gmail.com) cleaned — partnership tags removed

### GHL Pipeline

- Pipeline: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`)
- Stages: New Partner Lead (`ccc3d423-ff86-46b4-bd53-064458910eba`) → Contacted → Proposal Sent → Closed
- Opportunities created automatically by Reply Handler when a contact replies (email or LinkedIn)

### Email Templates

4 templates created in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`), populated with HTML via PATCH API and `{{contact.first_name}}` merge fields:

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher currently sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The templates exist for open tracking and deliverability but are not the primary send path. The dispatcher's inline HTML in the Code node is the canonical message content.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'`. Tracks connection status, sequence step, and DM state. |
| `partnership_release_log` | Tracks every sent email (contact, step, status, message ID). UNIQUE on `(ghl_contact_id, email_step)`. |

### GHL API Key

GHL, Unipile, and state-upsert values remain configured in the live workflow runtime; values are intentionally omitted from documentation. Credential migration and rotation remain open.

All 7 partnership workflows are active and published. The dispatcher schedules are explicit weekday cron schedules: email at 11:00 America/New_York, LinkedIn requests at 15:00 America/Chicago, and LinkedIn DMs at 12:00 America/Chicago. Outbound was explicitly activated on 2026-07-31 with `defaultDryRun=false`; do not manually execute these workflows unless intentionally sending an additional batch. The post-recovery database currently has 0 partnership release rows and 18 partnership LinkedIn state rows, so persistence/source restoration must be verified before trusting campaign totals.

### Tags

| Tag | Purpose |
|-----|---------|
| `partner_candidate_email` | Import tag — marks contact for email sequence |
| `partner_candidate_linkedin` | Import tag — marks contact for LinkedIn sequence |
| `partner_email_queued` | Applied after first email send — marks contact as active in email sequence |
| `partner_linkedin_requested` | Applied after LinkedIn connection request sent |
| `partner_email_sequence_completed` | Terminal — all 4 emails sent |
| `partner_replied` | Terminal — contact replied (stops all sequences, creates opportunity) |
| `partner_not_interested` | Terminal — manual override |
| `partner_do_not_contact` | Terminal — manual override |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | Sends 4-step email sequence via GHL Conversations API. 60/day cap, 11am ET Mon-Fri, 2-weekday intervals. |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | Sends LinkedIn connection requests via Unipile. 30/day cap, 3pm CT Mon-Fri. Atomic ready→requested_pending claim. |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step LinkedIn DM cadence for connected partnership contacts. 2-weekday intervals. |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | POST `/webhook/lt-partnership-reply`. Tags contact `partner_replied`, creates opportunity in Partnership Pipeline → New Partner Lead, posts Slack alert. |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Schedule Trigger every 5 min. Polls GHL for inbound email replies from `partner_email_queued` contacts, triggers Reply Handler on detection. |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | Bulk-imported 98 email contacts into GHL. |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on 33 LinkedIn-only contacts. |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows were patched to also query `partnership_linkedin_connection_state`:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION to include partnership rows; `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL select + separate Update node for partnership table |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing node + separate partnership update |

### Audit (2026-07-31)

Full post-build audit completed:
- All 7 partnership workflows published and active
- 3 patched LinkedIn workflows verified with correct partnership table queries, routing, and update nodes
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) SQL includes `partnership_release_log` via UNION ALL (published version `6641aa9a`)
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped and verified
- Executive Report frontend later updated to build `2026-08-01-v12-campaign-breakdown`; the dated audit below records the original partnership deployment.
- GHL contacts verified: 98 with `partner_candidate_email`, 127 with `partner_candidate_linkedin` (94 overlap), 131 total
- 4 email templates confirmed in folder `Partnership Email Campaign`, all with correct HTML content
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected

### Remaining

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder.
- **Social statistics ingestion**: Add a usable GHL OAuth credential to n8n and ingest daily saves, reach, and impressions; the PIT cannot access the official statistics endpoint.
- **Executive weekly LinkedIn KPI**: Adjust the query to count `reply_received` alongside legacy `inbound_reply` events.
- **Reply Poller API gap resolved 2026-07-31**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) used the wrong `POST /conversations/search` method in the earlier implementation. The current published implementation uses `GET /conversations/search`; see the 2026-08-04 remediation entry above.
- **14 excluded contacts**: User to provide corrected company names; re-import when available
- **Marc-owned follow-up sender routing**: Untested — zero Marc-owned opportunities exist in trigger stages

## Reporting

### Active Workflows

| Workflow | ID |
|----------|-----|
| LT - GHL Daily Leads Ingest | osIJOgBmWITF5Yuv |
| LT - GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 |
| LT - GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l |
| LT - GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG |
| LT - GHL Daily Social Ingest | QZoqCaTwDhbym80O |
| LT - GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq |
| LT - GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi |
| LT - GSC Daily Ingest | xHqmCC1vOeZ11gCd |
| LT - GSC Rollup Bridge | fOVBHwti9rC3qrLV |
| LT - Report Attribution Bridge | Y0TU7Il71JswxOBp |
| LT - Report Daily Rollups | EUeOiRttoVLQ9zF9 |
| LT - Report Executive Summary API | Bukc0mgOD2r7V6ED |
| LT - Report QA and Alerts | M5mXcDTFSko6EdHb |
| LT - Report Config Sync | aomO3Z4AXJIgEvvN |
| LT - Report Publish Refresh | 3gXztCnBEN6sGINb |
| LT - Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 |
| LT - Report Pipeline Velocity | iFfwh0jpYUZoDhDR |
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV |

### State

GA4, GHL, and GSC ingestion are all live. GSC execution `281697` confirmed the renewed OAuth credential and successful source-health finalization. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

### 2026-07-25 GHL Leads Ingest Rate-Limit Hardening

- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) failed in `Fetch + Normalize Leads` with GHL HTTP `429 Too Many Requests` during paginated contact retrieval (execution `241845`).
- Replaced the task-runner-incompatible HTTP wrapper with direct `this.helpers.httpRequest` calls.
- Added bounded 429 handling: up to four attempts per page, honoring `Retry-After` when available and otherwise using exponential backoff.
- Added a 500 ms delay between pagination requests to reduce GHL rate-limit pressure.
- Published workflow version `c740c006-fef5-4873-91b5-d2d4218872de` and confirmed it is the active version.
- Manual production-path validation execution `241894` succeeded: 500 contacts fetched, raw lead upserts completed, sync watermark and source health updated, and final status was `success`.
- Updated local reporting SDK snapshots (`leads_ingest_sdk_v2.ts`, `leads_ingest_sdk_v2_clean.ts`, and `leads_ingest_sdk_v3.ts`) with the same HTTP hardening.

## Next Steps -- By Priority

### 1. Vapi Campaign Monitoring

- ~~Monitor Intake Poller executions to confirm steady 30/cycle churn through all 4 pools~~ — Confirmed: poller running successfully every 10 min throughout 2026-07-20 dialer outage
- ~~Monitor Outbound Dialer~~ — Dialer recovered 2026-07-20 after stuck-queue fix (contact `AX3wfQNpRwm6DG0HgUE2` deleted from GHL, `neverError: true` applied to lookup, `onError: continueRegularOutput` on call note)
- Watch for GHL rate limiting on downstream nodes
- Verify `report_referral` tool calls now get proper ack in Vapi logs (Fix #2)

### 2. Voice Hardening

- Test live calls with both Brand and Dispensary assistants after system prompt updates (discovery questions should flow one-at-a-time, no disclosure on voicemail, no "clears throat", "from Transparent eCom" not "with a transparent")
- Consider switching Jordan's voice from Nico to Emma/Layla (both already fallbacks) to eliminate remaining TTS artifacts
- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback

### 3. Emerald Email Campaign Ramp

Monitor first week of dispatcher runs. Verify Email_Events data quality. Increase warmup caps as sender reputation builds. Currently ~250/hr, ~1,200/day capacity with 4 senders.

### 4. Reporting Depth

- Expand contact-capture panel by channel and landing page
- Build matched funnel views by channel, campaign, and landing page

### 5. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics

### 6. DAN Email Campaign Ramp

- Monitor dispatcher runs at 65/cycle every 30 min — verify consistent deliverability (5 fixes applied 2026-07-15)
- Track Email_Events for DAN campaign data quality (opens, clicks, bounces)
- Monitor DAN_Release_Log growth — ~1,200/day target should exhaust eligible pool in ~4 days
- Recurring DNC contacts (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms) are not written to release log but reappear each run — address stale tags in report_raw_ghl_contacts to reduce waste
- Verify sender rotation (4 senders) doesn't trigger GHL domain limits

### 7. Apollo Enrichment — MONITORING (audited + hardened 2026-07-15)

- ~~Watch polling workflow runs to confirm steady 30/cycle consumption~~ — Confirmed: batch size 50, steady 30-min runs, all successful
- ~~Verify V4 callback handler starts receiving Apollo async phone responses~~ — Confirmed: 1,058+ callbacks received by 2026-07-16, working
- ~~Confirm `queued_phone` contacts transition to `enriched` as callbacks arrive~~ — Pipeline confirmed end-to-end. Reaper now monitors both statuses.
- ~~Retune maxPerRun and schedule if Apollo rate limits appear~~ — 429 retry with 5s delay added to all 3 search sources
- ~~Ensure legacy blank contacts are not left invisible after poller write failures~~ — Fixed 2026-07-16 with hardened poller fallback + 6-contact backfill to `queued_phone`
- **ACTIVE MONITORING**: Watch Reaper Slack reports for `queued_phone` reaping counts
- **ACTIVE MONITORING**: Confirm polling `Queued At` dates flow correctly so Reaper aging works
- **ACTIVE MONITORING**: Watch for Apollo API rate limits / Apollo credit exhaustion on async phone callback requests; V4 now maps provider failures to `callback_failed`

### 8. Partnership Marketing Monitoring

- Monitor first Partnership Email Dispatcher run at 11am ET — confirm emails send, release log writes, and `partner_email_queued` tag applied
- Monitor first Partnership LinkedIn Dispatcher run at 3pm CT — confirm connection requests send, state table updated, `partner_linkedin_requested` applied
- Verify Partnership Reply Poller detects any inbound replies and triggers Reply Handler correctly
- Confirm Partnership LinkedIn DM Sequence picks up connected contacts after Acceptance Checker processes them
- Verify 3 patched LinkedIn workflows (Acceptance Checker, Reply Backfill, Unipile New Messages) handle partnership rows correctly
- Monitor for GHL rate limiting on per-contact API calls (250ms delay between contacts)
- After first email sends complete, verify the campaign summary endpoint reflects non-zero "Partnership emails" catalog row (may lag until reporting rollup runs)

### Historical LinkedIn Dispatcher Monitoring

- Historical checklist only: the post-recovery main LinkedIn state table currently has 0 rows, so the old 14,987-ready count is not current.
- Verify restored state and current queue counts before expecting dispatcher work.
- Verify dispatcher sends invites (successTag: `linkedin_connection_requested`) and updates state table correctly
- Watch for GHL rate limiting on dispatcher's per-contact API calls (tag check + LinkedIn URL extraction)
- Confirm Acceptance Checker correctly processes new connections and applies `linkedin_connected` tag

### 9. Cleanup and Adjacent Automation

- ~~Build automated LinkedIn DM suppression workflow~~ — DONE 2026-07-15. GHL tag `stop_linkedin_dms` → webhook → state table terminal. Full audit confirms all 3 send paths blocked.
- Build the separate `SimpleTexting SMS` GHL Custom Conversation Provider bridge after the user provides `conversationProviderId`; keep the existing SimpleTexting dispatcher live at low volume.
- Confirm first real SimpleTexting inbound reply posts to the existing Slack alert and suppresses future automated sends; then add GHL Conversations posting as the primary operator inbox.
- Retry and enable blocked GSC ingest workflow
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state lag after the fail-closed patch
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- ~~Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder~~ (verified already removed 2026-07-15)
- Delete GHL export CSVs after DAN backfill confirmed healthy

## Next Session Start

1. Read `docs/handoff/2026-08-12-report-recovery.md` and re-run `scripts/report_runtime_audit.py`.
2. Re-query the post-recovery baseline because schedules may change counts.
3. ~~Repair GHL Sales Ingest (`aYT5oHcgmBALzHy5`) from failure `742754` before any backfill or report interpretation.~~ **DONE.** Published version `91603d56`; execution `743094` wrote 7,984 opportunities.
4. ~~Verify the repaired workflow's published version and database writes.~~ **DONE.** Sync run completed (15,968 row_count, 0 errors).
5. Restore source coverage one system at a time: voice attempts/outcomes, email/release logs, main LinkedIn state, and SimpleTexting state. Audit `ghl_contact_id` candidate matches before mutation.
6. Ask for explicit approval before any live outbound test.
