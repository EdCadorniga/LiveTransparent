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

### Phase 2 — Contact Classification (attempted 2026-07-01, BLOCKED)

2.1 **Rewrite done**: `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) restructured:
  - Manual Trigger -> Postgres (`SELECT DISTINCT contact_id FROM voice_call_attempt`, 1,045 IDs found) -> Classify (single Code node with full pagination loop)
  - GHL POST `/contacts/search` uses `page` + `pageLimit` (100/page) — NOT `startAfter`/`startAfterId`
  - Valid body shape: `{ locationId, pageLimit, page }` — do NOT include `filters: []` (causes 422)
  - Heuristic: `emerald` tag + keyword match → `vapi_campaign_brand` or `vapi_campaign_dispensary`
  - Collects arrays of contact IDs per campaign (no per-contact tag API calls to avoid slow loop)
2.2 **Pagination learned**: `page` (1-indexed, integer) + `pageLimit` (max 100). 23,726 total = 238 pages.
2.3 **Code node HTTP approach learned**: Use `this.helpers.httpRequest({...})` directly. **Do NOT wrap** in an async helper function — `doHttpRequest.call(this, ...)` breaks HTTP context and causes 400 errors.
2.4 **Rate limit discovered**: GHL PIT token returns 401 after ~54 pages (~5400 contacts). Add `await new Promise(r=>setTimeout(r, 300))` between pages. Even with delay, the `for` loop inside a Code node with `this.helpers.httpRequest` is still fragile.
2.5 **Pending**: Classify-only pass (no tag API calls) runs in ~27s for partial scan. Full 238-page run hasn't completed due to `this` context issues in loops or rate limiting. Potential fix: batch via external script or use `$httpRequest` global directly outside loop context. See `AGENTS.md` Phase 2 section.

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
