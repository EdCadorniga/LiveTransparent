# Live Transparent CRM Operating Snapshot

## Purpose
This is the live-state summary for the Live Transparent GHL sub-account.
Use it for current decisions. Use the deeper runbooks for implementation detail.

## Live Context
- Location: `Live Transparent`
- Location ID: `Zwz4relUXVPxx8uohnjV`
- Timezone: `America/Los_Angeles`
- Public n8n host: `https://automations.livetransparent.com`

## Live Assumptions
- Treat pipeline/stage logic as ID-driven even when docs show human-readable names.
- Prefer internal service-to-service calls over public hops when possible.
- Use `n8n-lt` to verify live workflow state before runtime changes.
- Use `ghl_official` first for supported GHL reads and writes.
- Treat `ghl_workflows` as secondary.
- If an MCP wrapper fails on a valid endpoint, verify through direct GHL API before assuming the PIT is invalid.
- GA4/GSC traffic is not available natively in GHL and must be pulled into the report layer separately.

## Active Pipelines
- `Warm`
  - `New`
  - `Qualified (MQL)`
  - `Routed to Outreach`
  - `Nurture Active`
  - `Disqualified`
- `Sales Outreach`
  - `New`
  - `Attempting Contact 1st Attempt`
  - `2nd attempt`
  - `3rd attempt`
  - `Engaged`
  - `Meeting Requested`
  - `Booked`
  - `Unresponsive`
- `Sales`
  - `Discovery Scheduled`
  - `Discovery Completed`
  - `Proposal Sent`
  - `Negotiation`
  - `Closed Won`
  - `Closed Lost`

## Reporting-Critical Field Families
Keep these aligned with routing and report logic:
- First/last touch UTMs:
  - source, medium, campaign, content, term, landing page
- Warm and routing metadata:
  - `Warm Source`
  - `Warm Trigger Type`
  - `Lead Temperature`
  - `LT Last Routing Channel`
  - `LT Last Routing Reason`
  - `LT Last Routed At`
  - `LT Route Lock Until`
  - `LT Routing Priority`
  - `LT Last Event Fingerprint`
  - `LT Last Event At`
- Exact field IDs live in `Warm_Lead_Conflict_Safe_Implementation_Spec.md`.

## Active Workflow Families
- Warm intake and routing:
  - `GHL Warm Intake - Add Intake Tag (Webhook)`
  - `GHL Warm Intake - Email Inbound Tag (Webhook)`
  - `GHL Warm Intake - SMS Tag (Webhook)`
  - `GHL Warm Intake - Referral Tag (Webhook)`
  - `GHL Warm Intake - Email Outbound Tag (Webhook)`
  - `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)`
  - `WF - Master Warm Intake and Routing`
  - `WF - Warm Channel Micro Entry`
- Apollo enrichment:
  - `GHL Apollo Enrichment - Webhook Intake (Sheet First)`
  - `GHL Apollo Enrichment - Phone Webhook Intake (Staged)`
  - `GHL Apollo Phone Enrichment - Callback Handler`
  - `GHL Apollo Phone Enrichment - Callback Handler V4`
- SimpleTexting:
  - `LT - SimpleTexting SMS Send (Webhook, Staged)`
  - `LT - SimpleTexting Inbound Reply (Webhook, Staged)`
  - `LT - SimpleTexting Delivery Events (Webhook, Staged)`
  - `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)`
  - `LT - SimpleTexting Campaign Sequencer (Staged)`
  - Archived: `LT - SimpleTexting Warmup Dispatcher (Staged)`
  - `LT - SimpleTexting Pool Dispatcher (Staged)`
- Cold outreach:
  - `LT - Cold Outreach CSV -> Postgres Ingest (Staged)`
  - `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)`
  - `LT - Cold Outreach Sender Release Dispatcher (Staged)`
- Emerald:
  - `LT - Emerald CSV -> Postgres Ingest (Staged)`
  - `LT - Emerald CSV -> GHL Import (DryRun, Staged)`
  - `LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged)`
  - `LT - Emerald Campaign Sender Release Dispatcher (Staged)`
  - `LT - Emerald Executive SSO -> Company Sync (Staged)`
  - `LT - Emerald Intro Sent -> P2 Queue Dispatcher (Staged)`
  - `LT - Emerald Intro Backfill Tagger (Staged)`
- Slack / booking handoff:
  - `WL - Webhook to Slack Channel Update`
  - `WL - Webhook to Slack Channel - Website Visitor`
  - `WL - Webhook to Slack Channel - Form Submission`
## Reporting Workflow Status
Active in the current live report chain:
- `LT - GHL Daily Sales Ingest`
- `LT - Report Attribution Bridge`
- `LT - Report Daily Rollups`
- `LT - Report Executive Summary API`

Live but still needing publish / verification follow-up:
- `LT - GHL Daily Leads Ingest`
  - Archived damaged workflow ID: `OtqWjqGXZC3OcrXP`
  - Rebuilt replacement ID: `osIJOgBmWITF5Yuv`
- `LT - Report QA and Alerts`

Deferred by design:
- `LT - Report Config Sync`
- `LT - GA4 Daily Ingest`
- `LT - GSC Daily Ingest`
- `LT - Report Publish Refresh`

## SimpleTexting Runtime Status
- `LT - SimpleTexting SMS Send (Webhook, Staged)` is active and had recent successful webhook executions in the last audit pass.
- `LT - SimpleTexting Delivery Events (Webhook, Staged)` is active and had recent successful webhook executions in the last audit pass.
- `LT - SimpleTexting Inbound Reply (Webhook, Staged)` was failing with a syntax error in `Validate + Normalize Reply` and was patched on `2026-04-26`.
- `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)` is active, but no recent executions were returned in the last audit pass.
- `LT - SimpleTexting Campaign Sequencer (Staged)` and `LT - SimpleTexting Pool Dispatcher (Staged)` are inactive by design.

## Special Live Rules
- The regulated ads booking path is the only booking flow that currently auto-hands off into `Sales -> Discovery Scheduled`.
- The executive report should combine GA4 traffic, GSC visibility, and GHL leads/sales.
- GHL alone is not sufficient for traffic reporting.

## Runtime Update Rule
- Verify before mutating.
- Mutate once.
- Re-read the live workflow or object after the change.
- Do not trust an MCP mutation response alone if it can drift from live state.

## Reference Docs
- `../LiveTransparent Report Plan.md`
- `Report Data Contract.md`
- `GHL_Snapshot_Build_Spec_LinkedIn_Micro_Workflows.md`
- `GHL_Intake_Webhook_Sender_Automations_Checklist.md`
- `Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- `Pipeline_Process_Training_Guide.md`
- `Pipeline_Quick_Reference.md`
- `RB2B_Website_Visitor_Intake_Workflow.md`
