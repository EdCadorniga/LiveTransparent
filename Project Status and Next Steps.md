# LiveTransparent Project Status and Next Steps

Updated: 2026-07-10

## Source Of Truth

This document is the canonical project status and next-steps reference. It supersedes duplicated planning notes in plan.md and other plan documents.

> **Historical traceability**: Fix narratives, root-cause analyses, and execution histories are preserved in git history. This file contains only current live state and actionable next steps.

## Current State Summary

- **Voice stack**: Paused since 2026-06-05. Vapi assistants, dialer, and intake poller held for quality gate. Vapi Campaign Rollout Phase 1-3 complete (assistants created, classifier live, infrastructure modified). See plan.md for quality gate status and activation order.
- **Emerald email campaign**: ACTIVE since 2026-07-07. Dispatches ~14,702 unenrolled contacts through GHL email sequences.
- **DAN email campaign**: FULLY LIVE since 2026-07-10. 10 templates, 3 GHL workflows, n8n dispatcher active.
- **LinkedIn**: 8 workflows re-enabled 2026-07-10. All pipeline fixes verified intact.
- **Instagram**: DM Sequence active, cron 0 12-22 * * 1-5.
- **Reporting**: GA4, GHL, GSC ingestion live. Executive report live in GHL.
- **SMS campaign**: Workflow exports staged in repo. Not yet deployed.
- **John->Jason migration**: Complete on n8n side. GHL workflows updated. Template keys preserved.

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
- **8 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Bucket} + P2 per bucket
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed, WL - Micro - Email Inbound/Outbound/Open Counter

### Dispatch State

- 250 contacts dispatched first batch, 0 errors
- 4 senders: cameron@livetransparent.{com,co,agency,org}, 300/day each Week 1
- Backlog: ~10,618 unreleased after DNC/DND SQL filtering
- Email events flowing within 3 min of dispatch

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,165 | ~14,702 pending, ~5,463 released |
| Emerald_Release_Log | 250+ | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## Email Campaign — DAN Brands & Dispensaries (LIVE 2026-07-10)

### Status

- Templates: CREATED (10/10 -- 5 Brand + 5 Dispensary)
- Tags: CREATED (5/5 -- deployed via GHL API)
- Dispatcher: LIVE (toUG1yPDmFG48KEP, active with defaultDryRun=false, hourly)
- GHL Workflows: ALL PUBLISHED (3/3)
- Deck Download automations: CREATED in GHL
- Dry run: 13 candidates found (10 brand + 3 dispensary)

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

**Duplicate to delete**: 6a4f6fcdf74b73e4b5b9ac0b (renamed "DUPLICATE - DELETE ME" in Brands folder)

## Voice Workflows

Phone: +1 (562) 534 1977
Callback webhook: https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback

### Active

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Webhook |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Webhook |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | Webhook |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Webhook |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Hourly |
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Manual |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |

### Paused (Quality Gate)

| Workflow | ID |
|----------|-----|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ |

### Queue State

4 imported-pool seed rows pending: Oxa0BTBbPi6JkPXGQIeT (Dispensary), 2AthxJS3uMoGWxnVU9v7 (Brand), FA2Cd923b7YzmJBdfByX (Brand), DkDogBpdJhH1gX8pauNP (Dispensary). 5 legacy rows moved to failed. Dedup confirmed across all paths.

### Call History Summary (voice_call_attempt)

1,711 total attempts across 1,045 unique contacts. Dispositions: voicemail=782, qualified/booked=305, connected=288, no_answer=212, busy=106, failed=18.

## LinkedIn Workflows (All Active, Re-enabled 2026-07-10)

| Workflow | ID | Schedule |
|----------|----|----------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | 0 12-22 * * 1-5 |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | 0 12-22 * * 1-5 |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | 15 */6 * * * |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | */15 15-21 * * 1-5 |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Webhook |
| LT - LinkedIn Connection State Upsert (Unipile) | Old7ZvyVYgFaJgDr | Webhook |
| LT - LinkedIn Unipile New Messages (Unipile) | 7o5EBdvwAuIaWW7k | Webhook |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual only |

Guardrails: John-branded copy blocked before Unipile send. Invite defaults say Transparent eCom (not LiveTransparent).

## Instagram

LT - Instagram DM Sequence (Unipile) (iCnY6ccdHhfJg3sf) -- active, cron 0 12-22 * * 1-5. Sends 4-message sequence to mutual followers. State tracked in instagram_dm_state (Postgres). Unipile account V9eiHiDpRmCtan0YNdzsQw at api42.unipile.com:17256.

## SMS Campaign (Staged)

Workflow exports staged in repo from docs/outreach/outreach_messages.docx. Not yet live deployed. Requires final GHL pool filter body for dispatcher.

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

GA4, GHL, and GSC ingestion are all live. Executive report live in GHL. Report rollups, attribution bridge, QA/alerts, and executive summary API all running.

## Next Steps -- By Priority

### 1. Vapi Campaign Rollout -- Quality Gate (BLOCKER)

Manual test call per assistant (Alex + Jordan) via Vapi dashboard before enabling dialer or intake poller. Active queue has 4 imported-pool seed rows ready. See plan.md for activation order.

### 2. Emerald Email Campaign Ramp

Monitor first week of dispatcher runs. Verify Email_Events data quality. Increase warmup caps as sender reputation builds. Currently ~250/hr, ~1,200/day capacity with 4 senders.

### 3. Voice Hardening

- Move remaining secrets out of Config nodes into n8n credentials or env-backed config
- Verify Vapi dashboard tool webhook URLs point to canonical callback
- Run adversarial test calls against both campaign assistants before dialer enable

### 4. Reporting Depth

- Expand contact-capture panel by channel and landing page
- Build matched funnel views by channel, campaign, and landing page

### 5. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics

### 6. Cleanup and Adjacent Automation

- Diagnose Apollo phone-enrichment callback URL zero deliveries since 2026-05-13
- Deploy staged SimpleTexting SMS workflows with live GHL pool query
- Confirm SimpleTexting reply handler posts to #lead and suppresses future sends
- Retry and enable blocked GSC ingest workflow
- Configure Unipile webhook for LinkedIn acceptance events
- Clean up temporary fix scripts (scripts/fix_*.py, fix_*.js)
- Delete duplicate DAN template 6a4f6fcdf74b73e4b5b9ac0b in Brands folder

## Working Order

1. **Quality gate** -- manual Vapi assistant test calls (BLOCKER)
2. **Emerald ramp** -- monitor dispatcher, verify data quality
3. Voice hardening
4. Reporting depth
5. Meta attribution
6. Cleanup and adjacent automation
