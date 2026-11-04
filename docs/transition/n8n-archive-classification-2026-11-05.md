# Phase 4 — workflow export/backup archive classification — 2026-11-05

Read-only: exact paths + sizes; JSON exports parsed for `id`/`name`/`versionId`/node count;
current live version compared via GET (version IDs are non-secret); credential-pattern hit
NAMES + counts only (values never emitted). No archive file was modified; nothing was
deleted, archived, or deployed. Not a deletion manifest.

**Coverage:** 68 files, 1,848,174 bytes under `local-archive/n8n/`; live version comparison performed for 13 workflow ID(s).

| path | kind | bytes | mtime | wf id | name | vs current active version | secret hits | class |
|---|---|---|---|---|---|---|---|---|
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003155.json` | json | 67,275 | 2026-09-10 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence, superseded by date); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003207.json` | json | 67,275 | 2026-09-10 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence, superseded by date); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003224.json` | json | 67,277 | 2026-09-10 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence, superseded by date); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003224_2026-05-26T18-07-02-658Z_5ad87536.ts` | ts | 29,413 | 2026-09-10 | `` | workflow_Q3Ivnwe4z2Y3cD7A_20260527_003224_2026-05-26T18-07-02-658Z_5ad87536.ts | ? | ghl_pit(1) | keep (rollback evidence, superseded by date); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/backups/workflow_Q3Ivnwe4z2Y3cD7A_updated_preview.json` | json | 66,205 | 2026-09-10 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence, superseded by date); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/test-ghl-search.js` | js | 2,520 | 2026-09-10 | `` | test-ghl-search.js | ? | ghl_pit(1) | owner decision; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/update-dispatcher-message.mjs` | mjs | 3,660 | 2026-09-10 | `` | update-dispatcher-message.mjs | ? | ghl_pit(1) | owner decision; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/dialer-update.mjs` | mjs | 138 | 2026-05-19 | `` | dialer-update.mjs | ? |  | keep (voice rollback/source pending mapping) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/dialer-workflow-clean.json` | json | 18,020 | 2026-09-10 | `` | LT - Voice Agent V1 Outbound Dialer (Vapi) | ? | ghl_pit(1) | keep (voice rollback/source pending mapping); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/dialer-workflow-clean.mjs` | mjs | 15,431 | 2026-09-10 | `` | dialer-workflow-clean.mjs | ? | ghl_pit(1) | keep (voice rollback/source pending mapping); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/intake-poller-update.mjs` | mjs | 10,945 | 2026-07-23 | `` | intake-poller-update.mjs | ? |  | keep (voice rollback/source pending mapping) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/n8n-workflow/lt-voice-agent-v1.json` | json | 6,407 | 2026-05-28 | `` | LT - Voice Agent V1 Outbound Dialer (Vapi) | ? |  | keep (voice rollback/source pending mapping) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/n8n-workflow/lt-voice-agent-vapi-callback-v1-backup-2026-05-07.json` | json | 5,365 | 2026-05-07 | `` |  | ? |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/n8n-workflow/lt-voice-agent-vapi-callback-v1-merged.json` | json | 106,326 | 2026-09-10 | `` |  | ? | apikey_literal(2), ghl_pit(10) | keep (voice rollback/source pending mapping); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/n8n-workflow/lt-voice-agent-vapi-callback-v1.json` | json | 4,924 | 2026-05-06 | `` | LT - Voice Agent V1 Vapi Callback Sync | ? |  | keep (voice rollback/source pending mapping) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/voice-agent/workflow-1ogCy-DIALER-EXPORT.json` | json | 19,519 | 2026-09-10 | `1ogCy9ScVjtF0Cqf` | LT - Voice Agent V1 Outbound Dialer (Vapi) | differs-from-active | ghl_pit(2) | keep (voice rollback/source pending mapping); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/MvPLbUAN9IIQikxb.before-email-mapping-20260917.json` | json | 62,070 | 2026-09-18 | `MvPLbUAN9IIQikxb` | LT - Report Campaign Channel Summary | differs-from-active |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/Q3Ivnwe4z2Y3cD7A-before-simpletexting-mms-20260924T111415Z.json` | json | 52,141 | 2026-09-24 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/Q3Ivnwe4z2Y3cD7A-before-simpletexting-mms-20260924T111732Z.json` | json | 57,165 | 2026-09-24 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/Q3Ivnwe4z2Y3cD7A-before-simpletexting-mms-20260924T111845Z.json` | json | 57,629 | 2026-09-24 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/Q3Ivnwe4z2Y3cD7A-before-simpletexting-mms-20260924T112004Z.json` | json | 57,379 | 2026-09-24 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/ZrqFN8qLKO8eVHDc.before-message-enrichment-20260917.json` | json | 23,523 | 2026-09-18 | `ZrqFN8qLKO8eVHDc` | LT - Email Event Ingest | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/company-mql-google-sheets-sync.json` | json | 10,772 | 2026-05-08 | `` | LT - Company MQL Google Sheets Sync | ? |  | archive/keep pending review |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/company_mql_google_sheets_sync.ts` | ts | 27,180 | 2026-05-09 | `` | company_mql_google_sheets_sync.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-mms-20260924T111415Z.json` | json | 21,942 | 2026-09-24 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-mms-20260924T111732Z.json` | json | 25,944 | 2026-09-24 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-mms-20260924T111845Z.json` | json | 26,408 | 2026-09-24 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-mms-20260924T112004Z.json` | json | 26,158 | 2026-09-24 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182410Z.json` | json | 21,656 | 2026-09-22 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182447Z.json` | json | 21,656 | 2026-09-22 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/f4VoO1lBWkYRcQai-before-sms-auth-sync-20261001.json` | json | 26,724 | 2026-10-01 | `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/gwaEpWDpTIwsafi8-before-simpletexting-mms-20260924T111415Z.json` | json | 20,791 | 2026-09-24 | `gwaEpWDpTIwsafi8` | LT - SMS Idempotent Send | differs-from-active |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/gwaEpWDpTIwsafi8-before-simpletexting-mms-20260924T111732Z.json` | json | 27,437 | 2026-09-24 | `gwaEpWDpTIwsafi8` | LT - SMS Idempotent Send | differs-from-active |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/gwaEpWDpTIwsafi8-before-simpletexting-mms-20260924T111845Z.json` | json | 28,555 | 2026-09-24 | `gwaEpWDpTIwsafi8` | LT - SMS Idempotent Send | differs-from-active |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/gwaEpWDpTIwsafi8-before-simpletexting-mms-20260924T112004Z.json` | json | 28,305 | 2026-09-24 | `gwaEpWDpTIwsafi8` | LT - SMS Idempotent Send | current-active |  | keep (rollback evidence) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-apollo-queued-timeout-reaper.ts` | ts | 9,362 | 2026-09-10 | `` | lt-apollo-queued-timeout-reaper.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-dan-campaign-dispatcher.json` | json | 14,600 | 2026-09-10 | `toUG1yPDmFG48KEP` | LT - DAN Campaign Sender Release Dispatcher (Staged) | differs-from-active | ghl_pit(1) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-ghl-call-outcomes-ingest.json` | json | 12,653 | 2026-05-12 | `` | LT - GHL Call Outcomes Ingest | ? |  | archive/keep pending review |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-ghl-oauth-token-refresh.ts` | ts | 4,742 | 2026-08-11 | `` | lt-ghl-oauth-token-refresh.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-company-page-five-send-test.ts` | ts | 16,596 | 2026-08-17 | `` | lt-instagram-company-page-five-send-test.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-company-page-ghl-association.ts` | ts | 5,635 | 2026-08-17 | `` | lt-instagram-company-page-ghl-association.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-company-page-identity-validator.ts` | ts | 7,856 | 2026-08-17 | `` | lt-instagram-company-page-identity-validator.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-company-page-message1-dry-run.ts` | ts | 6,682 | 2026-08-17 | `` | lt-instagram-company-page-message1-dry-run.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-company-page-source-import.ts` | ts | 8,672 | 2026-08-17 | `` | lt-instagram-company-page-source-import.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-dm-sequence.ts` | ts | 21,984 | 2026-07-16 | `` | lt-instagram-dm-sequence.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-dm-state-upsert.ts` | ts | 10,321 | 2026-05-30 | `` | lt-instagram-dm-state-upsert.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-instagram-unipile-new-messages.ts` | ts | 16,730 | 2026-09-10 | `` | lt-instagram-unipile-new-messages.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-connection-acceptance-checker.ts` | ts | 12,160 | 2026-05-30 | `` | lt-linkedin-connection-acceptance-checker.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-connection-state-sync.ts` | ts | 13,779 | 2026-09-10 | `` | lt-linkedin-connection-state-sync.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-connection-state-upsert.ts` | ts | 8,641 | 2026-06-03 | `` | lt-linkedin-connection-state-upsert.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-dm-sequence-update.json` | json | 17,979 | 2026-09-10 | `` |  | ? | ghl_pit(1) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-dm-sequence.json` | json | 17,971 | 2026-09-10 | `` |  | ? | ghl_pit(1) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-dm-sequence.ts` | ts | 24,136 | 2026-09-10 | `` | lt-linkedin-dm-sequence.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-follower-dm-sequence.ts` | ts | 18,623 | 2026-07-16 | `` | lt-linkedin-follower-dm-sequence.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-follower-sync.ts` | ts | 11,985 | 2026-09-10 | `` | lt-linkedin-follower-sync.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-relations-backfill.ts` | ts | 16,595 | 2026-09-10 | `` | lt-linkedin-relations-backfill.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-reply-backfill.ts` | ts | 10,241 | 2026-09-10 | `` | lt-linkedin-reply-backfill.ts | ? | ghl_pit(1) | keep (retained blueprint source); secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-linkedin-unipile-new-messages.ts` | ts | 10,496 | 2026-05-30 | `` | lt-linkedin-unipile-new-messages.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-campaign-sequencer.json` | json | 141,261 | 2026-09-10 | `7mSiivR3NhtLIcNz` | LT - SimpleTexting Campaign Sequencer (Staged) | differs-from-active | ghl_pit(2) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-delivery-events.json` | json | 33,199 | 2026-09-10 | `AEi1VCzkLvaYFr4U` | LT - SimpleTexting Delivery Events (Webhook) | differs-from-active | ghl_pit(2) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-inbound-reply.json` | json | 51,561 | 2026-09-10 | `i0pROHpFtN4LYR0Q` | LT - SimpleTexting Inbound Reply (Webhook) | differs-from-active | ghl_pit(2) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-pool-dispatcher.json` | json | 31,113 | 2026-09-10 | `usxYXSuc4ahw40V3` | LT - SimpleTexting Pool Dispatcher (Staged) | differs-from-active | ghl_pit(2) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-send-sms.json` | json | 63,009 | 2026-09-10 | `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send | differs-from-active | ghl_pit(1) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-simpletexting-unsubscribe-events.json` | json | 35,684 | 2026-09-10 | `IyBKMkpYQ7pa0C8V` | LT - SimpleTexting Unsubscribe Events (Webhook) | differs-from-active | ghl_pit(2) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/lt-sms-idempotent.json` | json | 7,867 | 2026-05-30 | `` | LT - SimpleTexting SMS Send Helper | ? |  | archive/keep pending review |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/social_outreach_templates.ts` | ts | 4,310 | 2026-07-16 | `` | social_outreach_templates.ts | ? |  | keep (retained blueprint source) |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/update-payload.json` | json | 15,744 | 2026-09-10 | `` |  | ? | ghl_pit(1) | archive/keep pending review; secret-hit review required before redistribution |
| `C:/1_Ed's Active Work/Projects/LiveTransparent/local-archive/n8n/workflows/vru7OtCkDnPJkWt2.before-dynamic-week-20260917.json` | json | 51,852 | 2026-09-18 | `vru7OtCkDnPJkWt2` | LT - Newsletter Dispatcher | differs-from-active | ghl_pit(2) | keep (rollback evidence); secret-hit review required before redistribution |

## Archived JSON workflow IDs vs current live version

| id | live name | active | current live versionId | archived row versionId |
|---|---|---|---|---|
| `1ogCy9ScVjtF0Cqf` | LT - Voice Agent V1 Outbound Dialer (Vapi) | False | `4a8dc48a-bfa5-4bd2-b963-5a1924f3ba17` | `774a3b2b-efed-405c-a1d2-18deacce1cb9` |
| `7mSiivR3NhtLIcNz` | LT - SimpleTexting Campaign Sequencer (Staged) | False | `57564fc0-d04e-4f18-9eac-ee42a86bfb39` | `c19542ec-7f4a-4c3d-be65-05686714aa64` |
| `AEi1VCzkLvaYFr4U` | LT - SimpleTexting Delivery Events (Webhook) | True | `91c05570-37bb-4ce5-be69-da790037ebd4` | `92d9f6a9-7cfe-48a3-be22-5086d1979df3` |
| `IyBKMkpYQ7pa0C8V` | LT - SimpleTexting Unsubscribe Events (Webhook) | True | `9331c7d3-ac50-4f17-9a9a-fe15642e2d74` | `8fe8da50-5afa-499a-ad3a-cbd9b8f4fe87` |
| `MvPLbUAN9IIQikxb` | LT - Report Campaign Channel Summary | True | `c2336fc3-6a58-4a55-a9a9-9010579348df` | `36c871e0-c4c0-47b1-8b10-f5944a2bad2d` |
| `Q3Ivnwe4z2Y3cD7A` | LT - SimpleTexting SMS Send (Webhook, Staged) | True | `b69a183e-273a-43f9-b06d-b2bd1575543b` | `f0be787e-e229-4d25-9ea6-4a2dea2f6015` |
| `ZrqFN8qLKO8eVHDc` | LT - Email Event Ingest | True | `e57c2664-f0f1-484f-b3a6-32bba41ff125` | `40c61586-e462-43dd-bddd-004d4b0b796d` |
| `f4VoO1lBWkYRcQai` | LT - SimpleTexting Provider Outbound Router | True | `287678fd-a9e1-48c9-ab91-587368a3249a` | `8aa3dc21-2178-4d45-85d1-7081f35164e9` |
| `gwaEpWDpTIwsafi8` | LT - SMS Idempotent Send | True | `52eefd2a-70be-41c9-a60a-2fce0f037929` | `9d587b17-fa9a-409c-90ac-0cc8a68c2fba` |
| `i0pROHpFtN4LYR0Q` | LT - SimpleTexting Inbound Reply (Webhook) | True | `599995a9-72ce-467d-9892-c7ddf496c3fa` | `08dbd2c2-56c1-48e6-b242-06b391b13a30` |
| `toUG1yPDmFG48KEP` | LT - DAN Campaign Sender Release Dispatcher (Staged) | True | `3f5b124b-595e-4573-b75e-a6d7ba93cc70` | `99a06725-1f4d-46b8-86cc-d1dd2a3258f0` |
| `usxYXSuc4ahw40V3` | LT - SimpleTexting Pool Dispatcher (Staged) | False | `706ec3d2-91c5-49d4-ac84-af0544209e54` | `26e538c0-ee4b-42df-8b90-f1e2708c7030` |
| `vru7OtCkDnPJkWt2` | LT - Newsletter Dispatcher | True | `dacd2df9-4647-4910-8ea3-857cf889f9b5` | `056472a2-f172-4a9b-beac-6d27d4628212` |

## Live-credential containment check (2026-11-05)

A follow-up containment check searched for the *exact* current live GHL PIT value
(read from `.env` locally; the value itself was never printed into this artifact).
Result: the exact live PIT text appears in **41 archived
exports/blueprints in this tree plus one `local-scripts/` file — the same
payload values were baked into historical exports while the token is still in use.
This is **not** committed-to-Git material (the archive is git-ignored), but any
redistribution/migration of these files must handle it.
**Owner resolution 2026-11-05 (later): Ed directed retention of the latest PIT from
`.env` — no rotation now; the token's presence here and in Git history is an owner-accepted
residual risk, with redistribution precautions unchanged.**

**Recovery note:** no archive row is the live system of record; restoring any workflow
requires the documented deploy path plus explicit owner approval. The five May-2026
`workflow_Q3Ivnwe4z2Y3cD7A_*` backups are superseded-by-date history for the current
SimpleTexting send workflow. Sensitive hits must be reviewed before any redistribution.
**Not approved** for movement or deletion.

## Disposition execution — batches 1–4 (2026-11-05, later same day)

Executed under the [YOLO cleanup mandate](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md)
with manifests [batch 2](retention-manifest-2026-11-05-batch-2-tmp-captures.md) /
[batch 3](retention-manifest-2026-11-05-batch-3-archive-dedup.md) /
[batch 4](retention-manifest-2026-11-05-batch-4-node-modules.md):

- **Dedup (batch 3):** SHA-256 over the 68 files found 2 duplicate groups; only the 2
  byte-exact duplicates were deleted (kept the identical twins):
  `workflows/f4VoO1lBWkYRcQai-before-simpletexting-response-fix-20260921T182447Z.json`
  (twin `-182410Z.json` kept) and
  `backups/workflow_Q3Ivnwe4z2Y3cD7A_20260527_003155.json` (twin `_003207.json` kept;
  newest `_003224.json` + its TS companion + `_updated_preview.json` retained). Archive
  is now **66 files / 1,759,243 bytes / 66 unique hashes / 0 duplicate groups** (88,931
  bytes freed). All TS blueprints kept; no live-only workflow snapshot touched.
- **Archive paths in general:** the archive family itself was retained as-is (it is the
  archive destination for other batches); no file was moved out of it except the two
  duplicate deletions above.
- The table above is historical for the two deleted rows; all other rows remain accurate.


## Disposition addendum - late continuation 2026-11-05

Executed under manifests `retention-manifest-2026-11-06-batch-5..11` (see `repository-organization-2026-11-06.md`): regenerable caches deleted (`.pip-cache/`, `.playwright-mcp/`); one byte-identical duplicate deduped inside `marketing/`; root residue (report-era captures, contact-division working files, `Export_Contacts_*` CSVs, `Contacts added August 25 2026/`, root `_check_config.py`/`_kill_and_fix.py`/`_mark_enrolled.py`, campaign/design `.docx` set, `_qa_remove_exec/`, `repomix.config.json`/`.repomixignore`) archived to dated `local-archive/` folders (PII kept locally, staged out of the Git index, not deleted). Nothing referenced by a maintained doc moved without a pointer update. This artifact's per-path tables remain historical evidence of the pre-batch state.

No file inside local-archive/n8n/ was changed this continuation (still 66 files / 66 unique SHA-256 hashes, re-verified). The PIT-in-archives note above stands as recorded (owner-accepted residual risk).
