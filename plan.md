# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans voice, reporting, LinkedIn outreach, and the upcoming SimpleTexting SMS campaign.
- For LinkedIn, keep invite copy and DM copy aligned to `outreach_messages.v2.docx`, and keep reply-stop behavior active.
- For SMS, use `outreach_messages.docx` as the campaign source, with batch dispatch, per-send tagging, shared reply-state tracking, and `#lead` notifications on response.
- Keep this file short; the detailed operating status belongs in `Project Status and Next Steps.md`.

## Vapi Campaign Rollout — Implementation Plan (2026-07-01)

### GHL Tag IDs (created 2026-07-01)
| Tag | ID |
|-----|----|
| `vapi_campaign_brand` | `exfU7DXbFF1c314Z1QXQ` |
| `vapi_campaign_dispensary` | `FiYEwJdMSIyKZa059wRY` |
| `vapi_already_called` | `HhkfhzocuEdOFOxeeHu2` |

### Overview
Two new Vapi voice campaigns targeting the Dispensary Attribution Network:
- **Brand Campaign (Alex)** — sell network participation to cannabis brand marketing leads
- **Dispensary Campaign (Jordan)** — recruit dispensaries as network partner locations

### Schema Context
- `voice_call_queue` already has `campaign_id text NOT NULL` — no migration needed
- `voice_call_queue` has **no `pipeline_stage` column** in bootstrap — but dequeue query filters on it (existing bug)
- `voice_call_attempt` has no `campaign_id` — join through `queue_id` for per-campaign reporting
- `report_raw_ghl_contacts` stores contacts as JSONB — but has daily lag, use live GHL API for classifier

### Efficiency Strategy
Multiple phases can run in parallel since they touch independent systems:

| Tracks | Systems Touched | Can parallelize? |
|--------|----------------|------------------|
| Phase 1 (assistants) + Phase 2 (classifier) | Vapi API vs n8n/Postgres | **Yes** |
| Phase 3 individual items | 5+ different workflows | **Yes, all independent** |
| Phase 3 can start before Phase 2 | Infra vs data | **Yes** — only needs assistantIds + tag names |

**Critical tooling note**: `n8n-lt` `updateNodeParameters` **corrupts Set v3.4 Config nodes**. Use direct n8n REST `PUT /api/v1/workflows/{id}` for Config node changes. `setNodeParameter` is safe for Code nodes.

**Rollback**: Each campaign gets an independent toggle — remove its tag from the intake poller filter to stop intake. No shared coupling.

---

### Phase 0 — Prerequisites (done)

0.1 **GHL tags created**: `vapi_campaign_brand`, `vapi_campaign_dispensary`, `vapi_already_called`
0.2 **Schema confirmed**: `campaign_id` column exists in `voice_call_queue`
0.3 `N8N_API_KEY_LT` available from `.env` for direct REST PUTs

### Phase 1 — Vapi Assistants (done 2026-07-01)

**Tool audit**: Vapi org had 16 tools defined. V1 assistant had only 1 attached (`press_dtmf`). Audit revealed:
- 2 deprecated native GHL tools deleted (`old_ok_ghl_calendar_create_event_tool`, `old_ok_check_ghl_calendar_availability`)
- 1 dangling tool ref removed from Inbound assistant (`4b1439f9...` — already deleted from org)
- `ok_transfer_to_john` renamed to `ok_transfer_to_jason` (function name, messages, descriptions)
- 14 tools remain (2 dtmf/transferCall, 5 server/function, 5 code, 1 gohighlevel native, 1 duplicate notify_sales)

All server/function tools already point to the n8n callback webhook — no new tool creation needed.

**John→Jason migration** (2026-07-01):
- `ok_transfer_to_john` tool → `ok_transfer_to_jason`, messages updated, same phone (+15622474600)
- V1 Outbound assistant: system prompt 9 John→Jason refs, voicemail updated, tool ref updated
- Inbound assistant: system prompt 9 John→Jason refs
- n8n callback `Switch - Route Tool`: rule 6 now matches `ok_transfer_to_jason`
- n8n callback `Set - John Callback Slack` → `Set - Jason Callback Slack`, disposition `jason_callback_requested`

1.1 **Brand assistant (Alex) created** via API (`1d7c5d42-f0a4-4b58-9494-dbda3be3c657`):
  - System prompt from `Vapi_Brand_Campaign.docx`: partnerships specialist selling Dispensary Attribution Network
  - **9 tools attached**: `press_dtmf`, `ok_transfer_to_jason`, `ok_get_ghl_contact`, `ok_check_cameron_availability`, `ok_ghl_calendar_book_appointment`, `update_lead_status`, `add_to_dnc`, `log_call_outcome`, `notify_sales`
  - Server messages: `["end-of-call-report", "status-update"]`
  - First message: "Hi, this is Alex calling from Transparent eCom..."
  - Voicemail: directs callbacks to Jason at 562-247-4600

1.2 **Dispensary assistant (Jordan) created** via API (`056f2e50-8bdf-4257-ac45-4d575600c39d`):
  - System prompt from `Vapi_Dispensary_Campaign.docx`: warm/relational, owner-operator focused
  - Same 9 tools attached
  - First message: "Hi, is this {{contact_name}}? This is Jordan with Transparent eCom..."
  - Voicemail: directs callbacks to Jason

1.3 **Phone number**: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`) for both campaigns.
1.4 **Callback trackedAssistants updated**: both new assistant IDs added to `Code - Detect Tool vs Callback` in n8n callback for timer enforcement.
1.5 **Inbound assistant**: `ok_transfer_to_jason` tool attached (was missing).
1.6 **Quality gate (pending)**: 1 manual test call per assistant. Verify persona, tools fire, end-of-call report delivers, dispositions correct.

### Phase 2 — Contact Classification (imported-pool path live 2026-07-03)

2.1 **Rewritten for imported pool**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) now uses the imported Brand/Dispensary pool as the canonical campaign source.
  - Manual Trigger → Postgres (`emerging_pool_contacts` joined against `report_raw_ghl_contacts` for `Em_Emerald_Contact_ID` / `Em_Source_File`) → Code classifier (5 Brand + 5 Dispensary cap) → GHL tag apply → summary
  - The classifier also dedupes against `voice_call_attempt` and pending/in_progress `voice_call_queue` rows
  - This removes the old `Emerald_Contacts` executive path entirely
2.2 **Live data reality (2026-07-03)**: 30 Brand + 20 Dispensary imported rows now have `Em_Emerald_Contact_ID` and `Em_Source_File` in GHL raw contacts. `emerging_pool_contacts.ghl_contact_id` is backfilled for those 50 rows. The remaining 13,818 imported rows are still unmatched to GHL until more reporting ingest lands.
2.3 **Initial tagged seed (10 contacts)**: 5 Brand + 5 Dispensary, all from `emerging_pool_contacts` source list. Tags applied via GHL API in classifier execution `105490` on 2026-07-03.
  - Brand: `KdA7vRKGuVUym1acE0D0`, `3uRbaI3yZOjUCrDZfjiE`, `3vMUseClXnxqZuYSTved`, `FA2Cd923b7YzmJBdfByX`, `2AthxJS3uMoGWxnVU9v7`
  - Dispensary: `DkDogBpdJhH1gX8pauNP`, `bAqpQ2GtnhsoDPcuHGGT`, `wKzcvnuSXMCZdRLJuteo`, `Oxa0BTBbPi6JkPXGQIeT`, `plwkRBIvXuThB54iujAJ`
2.4 **Bug found and fixed (2026-07-03)**: SQL readiness + backfill assumed custom fields carry a `name` key. Live GHL contact objects only return `id` + `value` for the imported fields, so the lookup missed everything until we also matched by stable field id `R0wbDRyzZz34PMlQSRWN` (`Em_Emerald_Contact_ID`) and `ILurFacMbAaHz2DdGjPa` (`Em_Source_File`).
2.5 **Next**: continue to wait for more reporting ingest to land; classifier will re-eligible new imported rows automatically as they backfill. No code change needed once a `ghl_contact_id` is set.

### Phase 3 — Infrastructure Modifications

#### Bug Fixes Found During Audit (DONE 2026-07-01)

3.0.1 ~~**BUG: Dequeue references non-existent `pipeline_stage` column**~~ — **DONE** via `setNodeParameter` on Postgres node. Removed `AND pipeline_stage = 'queued'` from WHERE clause and `pipeline_stage = 'dialing'` from UPDATE SET.

3.0.2 ~~**BUG: Callback has hardcoded `trackedAssistants` array**~~ — **WORKAROUND DONE**: Both new campaign assistant IDs added to the hardcoded array. Ideally move to Config node in future.

#### Infrastructure Changes (ALL DONE 2026-07-01)

3.1 **Modify dialer** (`LT - Voice Agent V1 Outbound Dialer`, `r7UjWLndmc6EqEUW`):
  - **DONE**: `Build Vapi Body` now has `CAMPAIGN_ASSISTANTS` map: `{ default: V1-ID, brand: Alex-ID, dispensary: Jordan-ID }`. Resolves from `$json.campaign_id`.

3.2 **Update callback + tools** (`LT - Voice Agent V1 Vapi Callback + Tools`, `fx4UvKUWbqJEY3LK`):
  - **DONE**: trackedAssistants array updated with `1d7c5d42` (Alex) and `056f2e50` (Jordan).

3.3 **Update intake poller** (`LT - Voice Queue Vapi Intake Poller`, `bYk1Ai6MJLyhTsDZ`):
  - **DONE**: `Prepare Search` passes `campaignTags: ['vapi_campaign_brand', 'vapi_campaign_dispensary']`.
  - **DONE**: `Search GHL Contacts` loops through each tag, makes separate API calls, dedupes results (GHL /contacts/search does NOT support OR filterType).
  - **DONE**: `Classify Contacts` maps matched tag → `campaignId` via `CAMPAIGN_TAG_MAP`.

3.4 **Add dedup gate to enqueue** (`LT - Voice Queue Enqueue`, `XzcpOBi9YcIhJPck`):
  - **DONE**: INSERT now uses `WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`.

3.5 **Fix dequeue + campaign routing** (`LT - Voice Dequeue Next`, `KsBMFcz1YpBGrjDW`):
  - **DONE**: 3.5.1 pipeline_stage bug fixed.
  - **DONE**: 3.5.2+3 Config node now has `includeOtherFields: true` (passes queue data through).
  - **DONE**: HTTP node uses ternary: `$json.campaign_id === 'brand' ? Alex-ID : ($json.campaign_id === 'dispensary' ? Jordan-ID : V1-ID)`.

### Phase 4 — Activation & Testing

4.1 Seed test queue: 5 Brand + 5 Dispensary contacts manually
4.2 Reactivate workflows in order:
  1. `LT - Call Outcome Ingest` (capture results)
  2. `LT - Voice Queue Enqueue` (accept queue rows)
  3. `LT - Voice Agent V1 Outbound Dialer` (place calls)
  4. `LT - Voice Agent V1 Vapi Callback + Tools` (process results)
  5. `LT - Voice Dequeue Next` (serve next call)
  6. `LT - Voice Queue Vapi Intake Poller` (only after test batch passes)
4.3 Smoke test: 10 test calls, verify dispositions + campaign_id in attempt rows
4.4 Verify Slack `#leads` fires with campaign context
4.5 **Scale**: Activate intake poller for campaign tags. Brand only for 24h, then Dispensary.
4.6 Monitor first 50 calls. Rollback any underperforming campaign by removing its tag from intake filter.
4.7 Update `AGENTS.md` and `Project Status and Next Steps.md` with new assistantIds and campaign status

### Phase 4 status (2026-07-03)

- **Quality gate pending**: 1 manual test call per assistant (Alex + Jordan) via Vapi dashboard. Verify persona, tools fire, end-of-call report delivers, dispositions correct.
- **Active queue after cleanup (imported-pool only)**:
  - `Oxa0BTBbPi6JkPXGQIeT` — Dispensary — AYR Cannabis Dispensary - Ocala
  - `2AthxJS3uMoGWxnVU9v7` — Brand — Miss Grass
  - `FA2Cd923b7YzmJBdfByX` — Brand — Local Grove
  - `DkDogBpdJhH1gX8pauNP` — Dispensary — Northern Green Canada
- **Dedup confirmed**: classifier, feeder, enqueue, and dequeue all block duplicate calls per contact. Voice dialer and intake poller remain paused.
- **Safest next step**: manual assistant quality gate first, then controlled queue-driven call test. Do not enable intake poller or V1 dialer yet.

## Emerging Pool Import (2026-07-02)

### Source Data
- Two Emerald-sourced CSVs (identical schema, column 1 = `Emerald Contact ID`):
  - `Brands.csv`: 3,668 rows (45% with email, 50% with phone, 29% both)
  - `Dispensaries.csv`: 10,200 rows (37% with email, 72% with phone, 30% both)
- Transformed into GHL-ready CSVs with column headers matching existing GHL custom fields (`Em_*` fields)
- Tags column includes pool tag (`brands_pool` / `dispensaries_pool`) + `emerald`

### Postgres Table
- Created `emerging_pool_contacts` with fields: `emerald_contact_id`, `source_list`, `first_name`, `last_name`, `primary_email`, `primary_phone`, `company_name`, `tags`, `ghl_contact_id`, `ghl_opportunity_id`, `ghl_import_status`, `raw_json` (JSONB), timestamps
- UNIQUE constraint on (emerald_contact_id, source_list)
- 13,868 total contacts inserted (3,668 brands, 10,200 dispensaries)

### Workflows Created
- `LT - Brands Pool to Postgres + Sheets` (`fg06Ip8wT3EapfdD`): reads `/home/node/.n8n-files/GHL_Ready_Brands.csv` → parses → inserts into `emerging_pool_contacts` with `source_list='brands'`
- `LT - Dispensaries Pool to Postgres + Sheets` (`q7qbjjm6185WeukV`): reads `/home/node/.n8n-files/GHL_Ready_Dispensaries.csv` → parses → inserts with `source_list='dispensaries'`

### Apollo Re-enrichment on Bad Numbers (callback workflow change)
- Added `Should Re-enrich Phone` IF node + `HTTP - Set Apollo Enrichment` to `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)
- Flow: `GHL - Apply Tags` → IF (disposition == `wrong_number` OR `contact_disconnected`) → HTTP PUT to set `Enrich Phone via Apollo = Yes` → continue to dequeue
- Existing `LT - Apollo Phone Enrichment Intake V3` workflow handles the actual lookup

### Key Files on VPS (inside n8n container at `/home/node/.n8n-files/`)
- `GHL_Ready_Brands.csv` (1.4 MB, 3,668 rows)
- `GHL_Ready_Dispensaries.csv` (3.6 MB, 10,200 rows)

### Supporting workflow added (2026-07-02)

- `LT - Vapi Campaign Queue Feeder` (`RFIZ9Bcfl3Yvms2b`) created to drip-feed already-tagged campaign contacts into `voice_call_queue`.
- Current behavior:
  - runs every 30 minutes
  - searches GHL separately for `vapi_campaign_brand` and `vapi_campaign_dispensary`
  - supports per-campaign `enabled` flags and per-run caps in the config Code node
  - filters out DNC / already-called / already-queued / invalid-phone contacts before queue insert
  - attempts Postgres insert with duplicate guards against `voice_call_queue` and `voice_call_attempt`
- Current verification note:
  - workflow executes successfully end-to-end
  - latest manual verification showed `total_candidates: 3`, `total_queued: 0`, and `skipped_contact_ids` for all 3 candidates
  - Postgres audit confirmed those same 3 contacts already exist in `voice_call_queue` with `status = 'pending'`, so the no-op behavior is currently expected and the duplicate guard is working
  - those 3 queue rows remain `pending` with `attempt_count = 0` and no `voice_call_attempt` history, so they are valid to keep as the seed test batch for controlled activation

## Imported Pool Go-Live Prep (2026-07-03)

### Live state (2026-07-03)
- Brand + Dispensary CSVs imported into GHL. Processing finished.
- 30 Brand + 20 Dispensary rows already in `report_raw_ghl_contacts` with `Em_Emerald_Contact_ID` and `Em_Source_File` populated.
- `emerging_pool_contacts.ghl_contact_id` backfilled for those 50 rows.
- Classifier rebuilt around `emerging_pool_contacts` only; first 5 Brand + 5 Dispensary contacts already tagged in GHL via execution `105490`.
- Queue feeder hardened to require both campaign tag + matching imported-pool tag, and 3 imported-pool rows are now in the active queue (1 still missing because it was already in `voice_call_queue` from a prior run).
- Legacy non-imported campaign rows have been moved to `failed` to keep the first call batch isolated.
- New helper `LT - Emerging Pool Go Live Helper` (`OGnADUQKd5z5f905`) added for the readiness, backfill, audit, and isolation steps.

### Prepared files for the next session
- `postgres/emerging-pool-go-live-check.sql`
- `postgres/check-emerging-pool-import-readiness.sql`
- `postgres/backfill-emerging-pool-ghl-ids.sql`
- `postgres/audit-emerging-pool-linkage.sql`
- `postgres/backfill-emerging-pool-ghl-opportunity-ids.sql`
- `postgres/select-emerging-pool-vapi-candidates.sql`
- `postgres/select-vapi-seed-test-batch.sql`
- `classifier-repair-plan.md`
- `classifier-workflow-change-plan.md`
- `classifier-workflow-patch-snippets.md`
- `classifier-workflow-mcp-update-ops.md`
- `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
- `emerging-pool-post-import-runbook.md`
- `live-mutation-plan.md`
- `rollback-checklist-vapi-emerging-pool.md`
- `execution-checklist-after-import.md`

### Exact next-session execution order
1. Run `postgres/emerging-pool-go-live-check.sql`
2. If landing counts look healthy, run `postgres/backfill-emerging-pool-ghl-ids.sql`
3. Run `postgres/audit-emerging-pool-linkage.sql`
4. Patch workflow `IduCoT5YOs0g2faT` using `n8n/workflow-update-payloads/lt-campaign-contact-classifier-update-ops.json`
5. Manually execute the classifier with 5 Brand + 5 Dispensary cap
6. Verify the newly tagged contacts in GHL
7. Manually execute queue feeder `RFIZ9Bcfl3Yvms2b`
8. Only then consider controlled Vapi resume

### Classifier note
- The live `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) is currently stale and hardcoded to 3 queue contact IDs.
- The rebuilt classifier should use `emerging_pool_contacts` and map campaign directly from `source_list`:
  - `brands` -> `vapi_campaign_brand`
  - `dispensaries` -> `vapi_campaign_dispensary`
