This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
AGENTS.md
Dockerfile
fix_intake_poller.js
LiveTransparent Report Plan.md
n8n-home-snapshot.md
n8n-login.md
n8n-signin-snapshot.md
package.json
plan.md
Project Specifications.md
Project Status and Next Steps.md
QWEN.md
Sales and Marketing Roadmap.md
tmp_prepare_phone_live.js
tmp-corrections.ts
tmp-rollup-js.js
tmp-rollup-skel.ts
Unipile_potential_automations.md
```

# Files

## File: AGENTS.md
````markdown
# LiveTransparent Agent Notes

## IMPORTANT — Read This First

Analyze the attached `repomix-output.md` file. It contains the core system architecture, code blueprints, and operational roadmaps for my LiveTransparent automation environment. Review my `AGENTS.md` and custom script setups (like `fix_intake_poller.js`) to understand how my infrastructure is organized. When I ask you to write code modifications, database queries, or new workflow nodes, ensure your suggestions strictly match this architecture and stay within my token budget.

**LLM context-loading order:**
1. `repomix-output.md` — start here for architecture, blueprints, and roadmaps
2. `AGENTS.md` (this file) — short operating guide
3. `Project Status and Next Steps.md` — current priorities and live-state
4. `Project Specifications.md` — system boundaries, guardrails, contracts
5. `plan.md` + sub-plans (`emerald-email-campaign/plan.md`, etc.) — active work plan
6. Custom scripts (`fix_intake_poller.js`, etc.) — infrastructure specifics
7. All other repo files — only when a task requires fine detail

## Canonical Status

- Use [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md) for current priorities and live-state details.
- This file is the short operating guide: keep it current, but avoid duplicating long planning material here.

## Environment

- Deployed via Coolify on a VPS.
- Public hosts: `automations.livetransparent.com` for n8n and `reports.livetransparent.com` for the report host.
- Prefer Coolify internal service-to-service calls when possible.
- n8n target version: `2.19.5`.
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

## Working Rules

- Check the live state before and after every mutation.
- Fetch first, patch second.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Use `Config` nodes only when env or credential access is blocked.

## Tooling

- Prefer `n8n-lt` MCP or direct API calls before browser workflows.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.
- Codex config: `C:\Users\edmon\.codex\config.toml`.

## Live Voice System

| Item | Value |
|------|-------|
| Phone | `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`) |
| Assistant | `3f9bbfd2-efa6-4381-81e6-26f2452d28f1` |
| Callback webhook | `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback` |
| Key env | `VAPI_PHONE_NUMBER_ID`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`, `GHL_API_KEY` / `GHL_PIT` |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Active |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Active |
| LT - Voice Queue Vapi Intake Poller | `bYk1Ai6MJLyhTsDZ` | Active |
| LT - Voice Queue Enqueue | `XzcpOBi9YcIhJPck` | Active |
| LT - Voice Dequeue Next | `KsBMFcz1YpBGrjDW` | Active |
| LT - Call Outcome Ingest | `PUCfTZBANSPcgS0c` | Active |

### Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

## Reporting System

| Workflow | ID | Status |
|----------|----|--------|
| GHL Daily Leads Ingest | `osIJOgBmWITF5Yuv` | Active |
| GHL Daily Sales Ingest | `aYT5oHcgmBALzHy5` | Active |
| GHL Daily Calls Ingest | `SqNQ0BYaTdcqyt1l` | Inactive, GHL 404 |
| GHL Daily Appointments Ingest | `yWZVSqEcjTbMT3kG` | Active |
| GHL Daily Social Ingest | `QZoqCaTwDhbym80O` | Active |
| GA4 Daily Ingest | `6pCSGzFmrMDFL5Yq` | Active |
| GA4 Traffic Rollup Bridge | `0P2AZcQYWYZjXbRi` | Active |
| GSC Daily Ingest | `xHqmCC1vOeZ11gCd` | Active |
| GSC Rollup Bridge | `fOVBHwti9rC3qrLV` | Active |
| Report Attribution Bridge | `Y0TU7Il71JswxOBp` | Active |
| Report Daily Rollups | `EUeOiRttoVLQ9zF9` | Active |
| Report Executive Summary API | `Bukc0mgOD2r7V6ED` | Active |
| Report QA and Alerts | `M5mXcDTFSko6EdHb` | Active |
| Report Config Sync | `aomO3Z4AXJIgEvvN` | Active |
| Report Publish Refresh | `3gXztCnBEN6sGINb` | Active |
| Report Postgres Bootstrap Apply | `3XHThUiUSNa4sTb9` | Active |

### Reporting Notes

- GA4 and GHL ingestion are live.
- GSC still needs workflow verification / cleanup.
- Meta Ads API access is validated against `act_2186975138800404`.
- Keep report validation end-to-end: ingest -> attribution bridge -> daily rollups -> executive summary.

## Other Live Systems

- SimpleTexting: Send, delivery, inbound reply, and unsubscribe webhooks are active.
- Unipile/LinkedIn: All pipeline workflows are active and verified live.
- LinkedIn pipeline status (verified 2026-06-03): Sync seeds state table, Dispatcher sends connection requests, DM Sequence sends follow-ups with auto-connected-sync, daily limit enforcement, and reply detection.
- LinkedIn GHL token: `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28` (from root `.env`). The alternate token `pit-2d2ed8c3-...` is broken (401), do not use.
- LinkedIn Code node regex pattern: always use `[/]` (character class) instead of `\/` in regex literals to avoid SDK JSON serialization corruption.
- GHL warm intake/routing, Apollo enrichment, and Emerald/Cold outreach are active.

## Outreach Notes

- LinkedIn invite copy is sourced from `outreach_messages.v2.docx`.
- LinkedIn DM copy is sourced from `outreach_messages.v2.docx`.
- LinkedIn DM timing is currently 0, 3, 4, 3, 4 days between sends after the first message clock starts.
- Active LinkedIn conversations are marked in `linkedin_connection_state` via `payload_json.dm_conversation_status = 'active'`.
- For LinkedIn supply, prefer seeding `linkedin_connection_state` from the working GHL contacts list and keep `linkedin_connected` rows out of the queue entirely.
- If you restart the session, re-check the live n8n executions for the sync, dispatcher, and DM workflows before saying the pipeline is healthy.
- SimpleTexting SMS campaign work is now staged in repo workflow exports, using `outreach_messages.docx` as the SMS source of truth.
- SMS campaign requirements:
  - tag each SMS send so the same person is not messaged twice
  - keep send state and response state in the same canonical table or a tightly controlled pair of tables
  - make sure inbound replies stop future sends and notify `#lead`
  - preserve opt-out handling and unsubscribe tagging
  - keep batches controlled until the pool filter and reply path are verified in live n8n

## Key Files

- `repomix-output.md`
- `.env`
- `Project Status and Next Steps.md`
- `GHL Live Transparent CRM/`
- `postgres/reporting-bootstrap.sql`
- `n8n/docker-compose.yml`
- `n8n/voice-agent/`
- `n8n/workflows/lt-linkedin-dm-sequence.ts`
- `n8n/workflows/lt-linkedin-connection-state-sync.ts`
- `n8n/workflows/lt-linkedin-connection-state-upsert.ts`
- `n8n/workflows/lt-linkedin-unipile-new-messages.ts`
- `n8n/workflows/lt-linkedin-connection-acceptance-checker.ts`
- `n8n/workflows/lt-simpletexting-send-sms.json`
- `n8n/workflows/lt-simpletexting-pool-dispatcher.json`
- `n8n/workflows/lt-simpletexting-campaign-sequencer.json`
- `n8n/workflows/lt-simpletexting-inbound-reply.json`
- `n8n/workflows/lt-simpletexting-delivery-events.json`
- `n8n/workflows/lt-simpletexting-unsubscribe-events.json`
- `reports/embed/executive/index.html`
- `reports/nginx.conf`
- `Backup of all n8n workflows/`
- `Project Specifications.md`

## repomix-output.md Refresh

After any significant work session (workflow fixes, new automations, config changes), regenerate `repomix-output.md` so next-session context is up to date:

1. `. $PROFILE`  
2. `packlive`

This stages key files into `C:\TempRepomixStaging`, runs `npx repomix --style markdown --compress --remove-comments --remove-empty-lines`, and copies the result back to the project root.
````

## File: Dockerfile
````dockerfile
FROM nginx:1.27-alpine

COPY reports/nginx.conf /etc/nginx/conf.d/default.conf
COPY reports /usr/share/nginx/html
````

## File: fix_intake_poller.js
````javascript

````

## File: LiveTransparent Report Plan.md
````markdown
# LiveTransparent Report Plan

This note is now a pointer to the canonical project status document:

- [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

Use that file for the current state and priority order so reporting work stays aligned with the voice plan.
````

## File: n8n-home-snapshot.md
````markdown
- generic [ref=e3]:
  - main [ref=e4]:
    - main [ref=e7]:
      - generic [ref=e10]:
        - generic [ref=e11]:
          - img [ref=e12]
          - img [ref=e14]
        - generic [ref=e18]:
          - generic [ref=e20]: Sign in
          - generic [ref=e23]:
            - generic [ref=e25]:
              - generic [ref=e30]: Email
              - textbox "Email" [active] [ref=e34]:
                - /placeholder: ""
            - generic [ref=e36]:
              - generic [ref=e41]: Password
              - textbox "Password" [ref=e45]:
                - /placeholder: ""
          - button "Sign in" [ref=e47] [cursor=pointer]:
            - generic [ref=e49]: Sign in
          - link "Forgot my password" [ref=e51] [cursor=pointer]:
            - /url: /forgot-password
            - generic [ref=e53]: Forgot my password
  - complementary
````

## File: n8n-login.md
````markdown

````

## File: n8n-signin-snapshot.md
````markdown
- generic [ref=e3]:
  - main [ref=e4]:
    - main [ref=e7]:
      - generic [ref=e10]:
        - generic [ref=e11]:
          - img [ref=e12]
          - img [ref=e14]
        - generic [ref=e18]:
          - generic [ref=e20]: Sign in
          - generic [ref=e23]:
            - generic [ref=e25]:
              - generic [ref=e30]: Email
              - textbox "Email" [active] [ref=e34]:
                - /placeholder: ""
            - generic [ref=e36]:
              - generic [ref=e41]: Password
              - textbox "Password" [ref=e45]:
                - /placeholder: ""
          - button "Sign in" [ref=e47] [cursor=pointer]:
            - generic [ref=e49]: Sign in
          - link "Forgot my password" [ref=e51] [cursor=pointer]:
            - /url: /forgot-password
            - generic [ref=e53]: Forgot my password
  - complementary
````

## File: package.json
````json
{
  "dependencies": {
    "@n8n/workflow-sdk": "^0.13.3"
  }
}
````

## File: plan.md
````markdown
# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans voice, reporting, LinkedIn outreach, and the upcoming SimpleTexting SMS campaign.
- For LinkedIn, keep invite copy and DM copy aligned to `outreach_messages.v2.docx`, and keep reply-stop behavior active.
- For SMS, use `outreach_messages.docx` as the campaign source, with batch dispatch, per-send tagging, shared reply-state tracking, and `#lead` notifications on response.
- Keep this file short; the detailed operating status belongs in `Project Status and Next Steps.md`.
````

## File: Project Specifications.md
````markdown
# Project Specifications: Outbound Voice Agent and Social Outreach

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This file defines boundaries, guardrails, and contracts; it does not repeat the architecture.

## Purpose

Production outbound calling flow for Vapi + n8n + GHL. The agent introduces LiveTransparent, qualifies intent and fit, records call context, and routes outcomes through tool calls.

## Canonical Status

- Current live state and priority order: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)

## System Boundaries

- Vapi: realtime voice runtime.
- n8n: queueing, dispatch, callback routing, persistence, CRM sync.
- GHL: contact, opportunity, note, and tag system of record.
- Postgres: call-attempt and transcript metadata store.

## Live Workflows

| Workflow | ID | Role |
|----------|----|------|
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Queue poller, timezone guard, call dispatch |
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | End-of-call webhook plus 4 tool endpoints |

## Social Outreach Scope

### Current Live LinkedIn State

- `LT - GHL LinkedIn Connect Dispatcher (Unipile)` is active and uses the invite copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn DM Sequence (Unipile)` is active and uses the LinkedIn DM copy from `outreach_messages.v2.docx`.
- `LT - LinkedIn Unipile New Messages` is active and marks active conversations when inbound replies arrive.
- LinkedIn DM sends are blocked when `payload_json.dm_conversation_status = 'active'`.

### LinkedIn Timing

- The current LinkedIn DM cadence is `0, 3, 4, 3, 4` days between sends.
- The first message starts the clock by setting `dm_sequence_started_at`.
- Sequence state is stored in `linkedin_connection_state`.

### LinkedIn State Requirements

- Use one canonical state row per contact.
- Persist `sequence_step`, `dm_sequence_started_at`, and `payload_json`.
- Preserve reply state when a contact enters active conversation.
- Never send duplicate LinkedIn DMs once a reply is detected.

### SMS Campaign Scope

- `outreach_messages.docx` is the source of truth for SMS copy.
- SMS is implemented as a SimpleTexting campaign stack, not as one-off ad hoc messages.
- The campaign uses a controlled pool dispatcher, a sequencer, and a shared send endpoint.
- The SMS workflow needs per-contact send tracking so each message can be marked as sent once and never repeated.
- The SMS workflow also needs response ingestion so replies update the same canonical state used by the send workflow.
- The SMS workflow should preserve unsubscribe handling and should not send to opted-out contacts.
- Replies should trigger a Slack notification in `#lead` so the team can respond without checking n8n first.
- The preferred model is a shared Postgres state table or a tightly controlled send-state plus response-state pair, but the same contact record must be authoritative for both send and reply logic.

### SMS Missing Steps

1. Normalize SMS copy from `outreach_messages.docx` into a template registry.
2. Define the SMS state schema and idempotency keys.
3. Build the SimpleTexting send workflow with batching controls.
4. Wire inbound reply and delivery webhooks into the same state model.
5. Confirm opt-out / unsubscribe propagation.
6. Run a low-volume smoke test before batch sends.
7. Deploy the staged SMS workflows into live n8n and verify the live webhook routes.

## Queue Contract

Minimum `voice_call_queue` fields:

`queue_id`, `contact_id`, `phone_e164`, `campaign_id`, `status`, `attempt_count`, `max_attempts`, `next_attempt_at`, `dnc`, `first_name`, `lead_timezone`

Injected Vapi variables:

`contact_id`, `queue_id`, `campaign_id`, `lead_timezone`, `first_name`

Normalized callback output:

`call_id`, `contact_id`, `queue_id`, `disposition`, `summary`, `transcript_text`, `recording_url`

## GHL Configuration

- Secrets: `GHL_PIT` aliased as `GHL_API_KEY`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`
- Voice write actions: add `vapi_*` tags per outcome, create contact notes for completed calls

## Guardrails

- Do not call `dnc=true` contacts.
- Respect `attempt_count < max_attempts`.
- Enforce 72h cooldown between attempts.
- Call only Mon-Fri 9am-5pm CT.
- Fall back to GHL contact timezone when queue timezone is missing; use CT 12-2pm safe window if neither is available.
- Keep secrets in env/credentials; do not hardcode them in workflow JSON.
- Preserve n8n graph integrity when editing workflows.
- For social outreach, never send duplicate messages. Every send workflow must check and update shared state before and after send.
- For social outreach, reply-handling workflows must mark the contact as in conversation so follow-up sequences stop.
- For SMS, keep the batch size controlled until reply capture, opt-out propagation, and Slack alerts have all been verified live.

## Callback Tools

- `update_lead_status`: GHL tag plus Postgres disposition update.
- `add_to_dnc`: set `voice_call_queue.dnc=true` and add the GHL DNC tag.
- `log_call_outcome`: upsert `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales`: post lead name and summary into `#leads`.

## Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

## Smoke Test

1. Seed one queue row with a controlled test number.
2. Run the outbound workflow manually.
3. Confirm the Vapi request includes expected metadata.
4. Send a simulated callback payload.
5. Confirm Postgres insert plus GHL note creation.
6. Replay the callback and confirm no duplicate record.

## Social Outreach Smoke Test

1. Verify LinkedIn invite and DM copy are still sourced from `outreach_messages.v2.docx`.
2. Send one LinkedIn test DM and confirm `linkedin_connection_state` advances exactly one step.
3. Simulate an inbound LinkedIn reply and confirm `dm_conversation_status` becomes `active`.
4. Confirm the active conversation is excluded from both LinkedIn DM send paths.
5. Prepare a single SMS test contact and confirm one SMS send is tagged in state.
6. Simulate an inbound SMS reply and confirm the response workflow updates the same canonical state.
7. Confirm unsubscribe handling blocks any future SMS sends for opted-out contacts.
````

## File: Project Status and Next Steps.md
````markdown
# LiveTransparent Project Status and Next Steps

Updated: 2026-06-03

## Source Of Truth

This document is the canonical project status and next-steps reference.
It supersedes the duplicated planning notes in:

- [plan.md](./plan.md)
- [LiveTransparent Report Plan.md](./LiveTransparent%20Report%20Plan.md)

## Current State

- The outbound voice stack is live: queue-driven outbound calls, the merged callback webhook, and all 4 tools are active.
- The reporting stack is live: GA4 and GHL ingestion are in production, data is flowing into Postgres, and the Executive Report is live in GHL.
- Report rollups, attribution bridge, QA/alerts, and the executive summary API are already running.
- Emerald email-marketing ingest workflows are active again in n8n: CSV -> GHL Import, CSV -> Postgres Ingest, and Campaign Snapshot -> Postgres Ingest.
- Emerald intro backfill is staged in live GHL: 500 additional eligible contacts have now been tagged `seq emerald - intro backfill pending`, the live pending queue increased to 3,566, and 1,719 enrolled contacts remain eligible for controlled staging.
- LinkedIn outreach pipeline is fully operational and verified (2026-06-03):
  - `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) seeds `linkedin_connection_state` from GHL contacts with LinkedIn URLs, resolved through Unipile profile lookups. Verified: `scanned: 101, matched: 100, upserted: 100`, schedule `15 */6 * * *`.
  - `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`, replaces archived `S32vc8pjJIBZZHLK`) reads the Postgres queue, sends LinkedIn connection requests via Unipile `POST /users/invite`. Verified: `sent: 10`, schedule `0 15-21 * * 1-5`.
  - `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`) polls connected contacts, includes automatic connection detection from Unipile chats, enforces a daily DM limit of 200 with carry-forward, and sends up to 40 DMs per progression step. Verified: `sent: 2`, schedule `0 12-22 * * 1-5`.
  - `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is the webhook receiver for state table upserts (ON CONFLICT with smart merging).
  - `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) marks active conversations to stop DM sequences on reply.
  - Working GHL token: `pit-b278b3ad-96bd-41fb-ba03-9f927039eb28`. The alternate `pit-2d2ed8c3-...` is broken (401).
  - Code node regex safety: always use `[/]` character class instead of `\/` in regex literals to avoid SDK JSON serialization corruption.
  - State table `linkedin_connection_state`: 171 contacts with `status='ready'`, 34 with `status='connected'`, 10 invites sent, 2 DMs delivered.
- SimpleTexting SMS campaign workflow exports are now staged in repo from `outreach_messages.docx`: sender, pool dispatcher, sequencer, inbound reply, delivery events, and unsubscribe events are all represented as separate workflows.
- The SMS stack still needs live deployment and a final GHL pool filter body for the dispatcher, but the message registry, batching shape, reply-stop handling, and Slack `#lead` notification path are now defined in the repo artifacts.
- GSC still needs workflow verification / cleanup.
- Meta Ads API access is validated, but spend ingest is still deferred.

## Voice Workflows

### Live Voice System

- Phone: `+1 (562) 534 1977`
- Vapi Assistant ID: `3f9bbfd2-efa6-4381-81e6-26f2452d28f1`
- Canonical webhook: `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`
- Target n8n version: `2.19.5`
- Canonical MCP: `n8n-lt`

### Active Workflows

- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`) — active, merged callback plus 4 tools
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) — active, queue dialer, contact-TZ-aware, 72h cooldown
- `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) — active, polls `vapi_queue`, E.164 bypass
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) — active, webhook enqueue, allows NULL phone
- `LT - Voice Dequeue Next` (`KsBMFcz1YpBGrjDW`) — active, webhook dequeue then Vapi call
- `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) — active, GHL call webhooks to Postgres and Slack

### Dialer Pipeline

- Cron runs Monday through Friday, 9am to 5pm CT.
- The dialer fetches and locks queue rows, checks the contact, applies a timezone-safe calling window, and places the Vapi call.
- The pipeline then increments attempt counts, sets `next_attempt_at` to `NOW + 72h`, and writes the GHL note.
- The dialer prefers internal Coolify service-to-service communication where possible.

### Intake Pipeline

- Cron runs every 10 minutes.
- The intake poller searches GHL for `vapi_queue` contacts.
- Valid E.164 numbers are enqueued.
- Invalid or missing phone numbers are skipped when enrichment is not sufficient.

### Callback Tools

- `update_lead_status` updates the GHL tag and the Postgres disposition.
- `add_to_dnc` sets `voice_call_queue.dnc=true` and adds the GHL DNC tag.
- `log_call_outcome` upserts `voice_call_attempt` with disposition, notes, and follow-up time.
- `notify_sales` posts lead name and summary into `#leads`.

### Voice Tags

- `vapi_call_attempted`
- `vapi_dnc`
- `vapi_human_answered`
- `vapi_interested`
- `vapi_not_interested`
- `vapi_interest_unknown`
- `vapi_voicemail`
- `vapi_voicemail_left`
- `vapi_no_answer`
- `vapi_busy`
- `vapi_wrong_number`
- `vapi_contact_disconnected`

### Voice Hardening Remaining

- Move remaining secrets out of workflow `Config` nodes into credentials or env-backed config.
- Verify the dashboard still points all tools and the end-of-call webhook to the canonical callback URL.

## Next Steps

### 1. Voice Hardening

- Move remaining secrets out of workflow `Config` nodes into n8n credentials or env-backed config.
- Verify the Vapi dashboard still points all tools and the end-of-call webhook at the current callback URL.

### 2. Reporting Depth

- Expand the contact-capture panel by channel and landing page.
- Build matched funnel views by channel, campaign, and landing page.

### 3. Attribution Expansion

- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Keep the user-facing emphasis on attribution first, then cost reporting.

### 4. Cleanup And Adjacent Automation

- Finish SimpleTexting secret hardening.
- Deploy the staged SMS workflows and verify the live GHL pool query.
- Fix the GHL-to-LinkedIn supply path so `linkedin_connection_state` is seeded from a working GHL contacts list and the dispatcher can send invites from that queue. [DONE 2026-06-03]
- Verify LinkedIn connection requests and DM sends from execution history. [DONE 2026-06-03]
- Retry and enable the blocked GSC ingest workflow.
- Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.

## Reporting Workflows

### Workflow List

- `LT - Report Config Sync` (`aomO3Z4AXJIgEvvN`) — active, seeds report settings and runtime flags
- `LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) — active, rebuilt replacement for archived `OtqWjqGXZC3OcrXP`
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) — active
- `LT - Report Attribution Bridge` (`Y0TU7Il71JswxOBp`) — active
- `LT - Report Daily Rollups` (`EUeOiRttoVLQ9zF9`) — active
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) — active
- `LT - Report QA and Alerts` (`M5mXcDTFSko6EdHb`) — active
- `LT - Report Publish Refresh` (`3gXztCnBEN6sGINb`) — active
- `LT - Report Postgres Bootstrap Apply` (`3XHThUiUSNa4sTb9`) — active

### Live Reporting State

- GA4 ingestion is live and feeding the executive report.
- GHL leads and sales ingestion is live and flowing into Postgres.
- The report host is live and secure.
- The GHL `Executive Report` custom menu entry points at the report host.
- The executive summary webhook is live and returns GHL-first report JSON from Postgres.
- `LT - Report Daily Rollups` preserves GA-backed channel, UTM, landing-page, and daily traffic rows.
- Funnel-efficiency metrics are live in the executive summary API and embedded report.

### Current Cohort Notes

- `contactToOpportunityRate` uses a contact-safe cohort metric instead of a raw multi-opportunity total.
- The current 30-day new-contact cohort is still returning `0` matched contact-to-opportunity progression.
- The current attribution coverage result for that same cohort is `97` contacts, `45` with usable source fields, `45` attributed bridge matches, and `22` lead-to-sale matches after normalized raw contact IDs and stored-field fallbacks.

### Report Model

- Raw tables cover GA4 sessions, GA4 pages, GA4 events, GSC queries, GSC pages, GSC site, GHL contacts, GHL opportunities, GHL pipeline history, and GHL forms.
- Bridge tables cover traffic-to-lead, lead-to-sale, and identity mapping.
- Rollup tables cover daily summary, channel summary, funnel summary, pipeline summary, stage summary, UTM summary, and landing page summary.

### Report Next Work

1. Expand the contact-capture panel by channel and landing page.
2. Build matched funnel views by channel, campaign, and landing page.
3. Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
4. Finish SimpleTexting secret hardening.
5. Deploy the staged SMS workflows and verify the live GHL pool query.
6. Confirm the SimpleTexting reply handler posts into `#lead` and suppresses future sends after a reply.
7. Fix the GHL-to-LinkedIn supply path so queue rows are created from the working GHL contacts list, then verify connection requests and DM sends from execution history.
8. Retry and enable the blocked GSC ingest workflow.

### Report Dependencies

- GA4 property ID is still the external dependency for any remaining GA4 API wiring work.
- Meta Ads API access is validated on `2026-05-05` against `act_2186975138800404`.
- For GA4 service account wiring, use a secret-backed JSON file in Coolify and keep the credentials out of source control.

## Operating Notes

- Prefer Coolify internal service-to-service communication where possible.
- Verify live state after every mutation: fetch first, patch second, audit live workflow plus recent execution before declaring a fix.
- Preserve graph integrity when editing n8n workflows: keep existing node IDs and keep the connections map aligned.
- For voice automations, prefer `Switch` over `IF`, and use raw JSON import for dialer patches.
- Report end-to-end validation should still span leads ingest, attribution bridge, daily rollups, and executive summary output.
- If LinkedIn troubleshooting is resumed in a fresh session, start by reading this file, `AGENTS.md`, `repomix-output.md`, and the latest executions for `LT - LinkedIn Connection State Sync (Unipile)`, `LT - GHL LinkedIn Connect Dispatcher (Unipile)`, and `LT - LinkedIn DM Sequence (Unipile)`.
- Do not declare LinkedIn fixed until execution history shows nonzero `matched`, `upserted`, and `sent` values on the relevant workflows.

## Working Order

1. Voice hardening.
2. Reporting depth.
3. Meta attribution.
4. Cleanup and adjacent automation.
````

## File: QWEN.md
````markdown
# LiveTransparent Project

## Project Overview

LiveTransparent is a marketing automation and CRM operations platform for a B2B compliance advertising agency focused on regulated cannabis marketing. The project orchestrates lead intake, warm lead routing, cold outreach, and email sequence campaigns using a combination of:

- **n8n** - Workflow automation engine (public URL: `https://automations.livetransparent.com`)
- **GoHighLevel (GHL)** - CRM and sequence delivery platform
- **PostgreSQL** - Contact storage, release logs, and company research cache
- **BookStack** - Internal knowledgebase (prepared, not yet deployed)

The system is deployed on a VPS using **Coolify** with Docker Compose services connected over a shared internal network (`coolify-shared`).

### Core Capabilities

1. **Warm Lead Intake** - Multi-channel webhook intake (LinkedIn, Meta, Email, SMS, Referral, Website forms) with automatic tagging and routing into CRM pipelines
2. **Cold Outreach** - Apollo-enriched contact ingestion with sender-capped dispatch and timezone-aware delivery
3. **Email Sequence Campaigns** - A/B tested sequences (e.g., Cannabis Ads, Emerald campaign) with GHL workflow delivery
4. **Company Research** - AI-powered company enrichment cached in Postgres for personalized email content
5. **RB2B Integration** - Website visitor identification with GHL reconciliation and follow-up task creation

## Directory Structure

```
LiveTransparent/
├── n8n/                              # n8n service Docker Compose and config
│   ├── docker-compose.yml
│   └── nodes/                        # Service reference docs (Apollo, GHL, Twilio)
├── postgres/                         # PostgreSQL service definition
│   └── docker-compose.yml
├── bookstack/                        # Internal knowledgebase (staged for deployment)
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
├── scripts/                          # Operational scripts and helpers
│   ├── rerun_bad_emerald_sso_companies.py
│   └── patch_simpletexting_callbacks.py
├── emerald-email-campaign/           # Emerald campaign workspace
│   ├── plan.md
│   ├── dispatcher-plan.md
│   ├── workflow-mapping.md
│   └── Exported Emerald Contacts.csv
├── Emerald Contacts/                 # Emerald source CSV merger and import generator
│   ├── build_ghl_import.py
│   └── README.md
├── cold-outreach-prep/               # Cold outreach workbook processing
│   ├── prepare_cold_outreach.ps1
│   ├── ghl/                          # GHL import CSVs
│   ├── postgres/                     # Postgres ingest CSVs
│   └── reports/                      # Validation and duplicate reports
├── GHL Live Transparent CRM/         # GHL process docs and runbooks
│   ├── Pipeline_Quick_Reference.md
│   ├── Cannabis_Ads_Sender_Routing_Runbook.md
│   └── RB2B_Website_Visitor_Intake_Workflow.md
├── Marketing Docs/                   # Brand voice, ICP, and segment strategy
│   ├── Transparent_eCom_Brand_Voice_And_Foundation.docx
│   ├── Transparent_eCom_Core_Customer_ICP.docx
│   └── Transparent_eCom_Strategic_Priority_Segments.docx
├── EMAIL templates/                  # Email sequence HTML templates
├── ghl create sequence plan/         # Sequence build specs and A/B rollout artifacts
├── Backup of all n8n workflows/      # Full n8n workflow JSON backups
├── AGENTS.md                         # Agent rules and operational notes (source of truth)
└── QWEN.md                           # This file
```

## Building and Running

### Docker Services (Coolify Deployment)

All services are deployed via Coolify using Docker Compose. Local development is not the primary workflow; changes are pushed to the repo and deployed through Coolify.

**n8n Service** (`n8n/docker-compose.yml`):
```bash
# Deployed via Coolify with:
# - Image: n8nio/n8n:2.9.4
# - Public host: automations.livetransparent.com
# - Internal network: coolify-shared
# - Postgres backend
```

**PostgreSQL Service** (`postgres/docker-compose.yml`):
```bash
# Deployed via Coolify with:
# - Image: postgres:17.7
# - Internal network: coolify-shared
# - Persistent volume: postgres_data
```

**BookStack Service** (`bookstack/docker-compose.yml`):
```bash
# Staged for deployment (not yet live)
# - Internal knowledgebase restricted to team access
# - MariaDB backend
# - Traefik routing via Coolify
```

### Operational Scripts

**PowerShell - Cold Outreach Prep**:
```powershell
# Process Cold-outreach contacts.xlsx into GHL/Postgres import CSVs
.\cold-outreach-prep\prepare_cold_outreach.ps1
```

**Python - Emerald Cache Reset**:
```powershell
# Create temporary reset workflow for bad cache rows
python scripts/rerun_bad_emerald_sso_companies.py create [company_keys...]

# Delete temporary workflow after execution
python scripts/rerun_bad_emerald_sso_companies.py delete <workflow_id>
```

### n8n Workflow Management

**Direct REST API** (verified working from Windows):
```bash
# Get workflow
curl -H "X-N8N-API-KEY: <key>" "https://automations.livetransparent.com/api/v1/workflows/<id>"

# Update workflow (minimal payload)
curl -X PUT -H "X-N8N-API-KEY: <key>" -H "Content-Type: application/json" \
  -d '{"name":"...","nodes":[...],"connections":{...},"settings":{}}' \
  "https://automations.livetransparent.com/api/v1/workflows/<id>"
```

**MCP Tools** (via Codex):
- Use `n8n-lt` MCP for workflow discovery, activation checks, and execution
- Use `ghl_official` MCP for GHL data reads
- Use `ghl_workflows` MCP with caution (some endpoints may fail with scope errors)

## Key Configuration Files

### Environment Variables

- **Root `.env`** - Shared credentials (not tracked in git)
- **`n8n/.env`** - n8n-specific secrets (encryption key, DB password)
- **`bookstack/.env.example`** - BookStack environment template

### Service References

- **`n8n/nodes/apollo/REFERENCE.md`** - Apollo API endpoint mapping
- **`n8n/nodes/ghl/REFERENCE.md`** - GHL API endpoint mapping
- **`n8n/nodes/twilio/REFERENCE.md`** - Twilio API endpoint mapping

## Development Conventions

### Workflow Update Pattern

1. **Verify first** - Use `n8n-lt` MCP to read current workflow state
2. **Build locally** - Construct full `nodes` and `connections` arrays locally
3. **Direct REST for large changes** - Use `PUT /workflows/{id}` with minimal payload (`name`, `nodes`, `connections`, `settings`)
4. **Verify after** - Re-read workflow and confirm `active`, `defaultDryRun`, and changed parameters

### GHL Integration Rules

- **Field naming** - Use exact GHL custom field names (e.g., `marketing_sender_email`, `Apollo Phone Enrichment Status`)
- **Tag hygiene** - Tags are appended non-destructively; removal requires explicit action
- **Pipeline stages** - Reference by ID, not name (see `AGENTS.md` for locked pipeline map)
- **Direct API fallback** - If MCP fails with scope errors, test endpoint directly against `https://services.leadconnectorhq.com`
- **LinkedIn supply path** - For the LinkedIn connection-request queue, use the working GHL `contacts/` list endpoint and filter locally by LinkedIn URL custom fields and tags. Treat `contacts/search` failures against private-integration tokens as a live blocker, not a harmless empty result.

### Data Processing

- **CSV imports** - Dedupe by email first, then name/company, then phone
- **Snake case conversion** - Postgres columns use snake_case (handled by `prepare_cold_outreach.ps1`)
- **Timezone handling** - Contact-local dispatch with explicit timezone resolution order
- **Dry-run discipline** - Keep `defaultDryRun=true` for staged workflows until ready for production

### Marketing Copy Alignment

Before drafting or revising contact-facing copy, reference:
- **Brand voice** - `Marketing Docs/Transparent_eCom_Brand_Voice_And_Foundation.docx`
- **ICP** - `Marketing Docs/Transparent_eCom_Core_Customer_ICP.docx`
- **Segments** - `Marketing Docs/Transparent_eCom_Strategic_Priority_Segments.docx`

Flag conflicts with these docs before proceeding.

## Active Workflows (Snapshot)

See `AGENTS.md` for the authoritative, up-to-date workflow inventory. Key production workflows include:

| Workflow | ID | Status |
|----------|-----|--------|
| Website Lead Intake (Hero) | `RTV5jUiTt05lad07` | Active |
| Website Lead Intake (Footer) | `RSfLF7LU0rDC4jAI` | Active |
| GHL Apollo Phone Enrichment - Callback Handler V4 | `U7c6byTLXAMgcS75` | Active |
| LT - Cold Outreach Sender Release Dispatcher | `NTpQnMrpjzusPXHX` | Active |
| LT - Emerald Campaign Sender Release Dispatcher | `8UXlpoMJnQ229AuG` | Active |
| rb2b leads | `3kjsIUeoEQFx26cC` | Active |
| WL - Webhook to Slack Channel Update | `lQTW0QPwBcf3o7j8` | Active |

## GHL Pipelines (Locked Map)

### Warm Pipeline
`New` → `Qualified (MQL)` → `Routed to Outreach` → `Nurture Active` → `Disqualified`

### Sales Outreach Pipeline
`New` → `Attempting Contact` → `Engaged` → `Meeting Requested` → `Booked` → `Unresponsive`

### Sales Pipeline
`Discovery Scheduled` → `Discovery Completed` → `Proposal Sent` → `Negotiation` → `Closed Won` → `Closed Lost`

## Important Operational Notes

1. **Status freshness** - Treat all "Current" / "Active" status items in `AGENTS.md` as "last known state" and re-verify in-system before acting
2. **TLS/schannel on Windows** - Direct `curl.exe` to HTTPS endpoints may fail; use Python `requests` or Node `fetch` for API verification
3. **MCP mutation limits** - If `n8n-lt` mutation helpers fail or ignore `active`, switch to direct REST API
4. **Emerald campaign** - Use Postgres table `Emerald_Campaign_Contacts` as dispatch source, not live GHL smart lists
5. **Sender caps** - Week 1: 300/day, Week 2: 400/day, Week 3+: 500/day (total outbound per sender, including in-flight sequence sends)

## Related Documentation

- **`AGENTS.md`** - Comprehensive agent rules, workflow status, and operational notes (source of truth)
- **`GHL Live Transparent CRM/Pipeline_Quick_Reference.md`** - Pipeline stage definitions and movement rules
- **`emerald-email-campaign/plan.md`** - Emerald campaign architecture and locked decisions
- **`bookstack/README.md`** - BookStack deployment instructions
- **`Project Status and Next Steps.md`** - Canonical live state plus the current LinkedIn troubleshooting handoff
````

## File: Sales and Marketing Roadmap.md
````markdown
# Sales and Marketing Roadmap

## KPI Framework

### Lead Generation
- Qualified outbound leads per week
- Open / response rates in sequences
- Appointment show rate

### Next Week Report Plan
- Add sequence-event ingest so we can show real sequence performance instead of only enrollments.
- Tighten landing-page and form tracking so we can trust the matched funnel by landing page.
- [x] Show a short summary of the most visited pages on the website using the landing-page rollup we already have.

### Conversion
- Lead → MQL → SQL conversion rate
- SQL → Proposal → Close rate
- Pipeline velocity (days between stages)
- Stage-by-stage opportunity movement (moved-in / moved-out per stage)
- Opportunity cycle length (days from first stage to close)

### Operational Efficiency
- % of outbound automated vs manual
- Lead scoring accuracy (hit rate among top scores)
- Sales cycle length changes

### Revenue Impact
- Pipeline contribution per month
- ROI of tools + sequences

---

## Current State

| System | Status |
|--------|--------|
| GoHighLevel (GHL) | Production — CRM, pipeline, routing, reporting |
| Apollo.io | Production — enrichment, outbound sequences |
| Meta Ads API | Validated — attribution-first reporting live |
| GA4 | Live — sessions, channels, engagement |
| GSC | Live — Search Console clicks, impressions, CTR, position |
| Clay | Planned — Phase 2 |
| n8n Orchestration | Production — all report workflows active |

---

## Executive Report Data Sources

The executive report (`reports/embed/executive/index.html`) surfaces data from:

| Source | Workflow | Data |
|--------|----------|------|
| GHL Contacts | `LT - GHL Daily Leads Ingest` | Contacts, UTM fields, warm source, routing metadata |
| GHL Opportunities | `LT - GHL Daily Sales Ingest` | Pipeline stages, closed-won revenue |
| GHL Calls | `LT - GHL Daily Calls Ingest` | Voice call logs: status, direction, duration |
| GHL Appointments | `LT - GHL Daily Appointments Ingest` | Calendar events: booked, showed, no-show |
| GA4 Sessions | `LT - GA4 Daily Ingest` | Sessions, users, engagement by channel/landing page |
| GSC Search | `LT - GSC Daily Ingest` | Clicks, impressions, CTR, average position, queries, pages |
| Attribution Bridge | `LT - Report Attribution Bridge` | Traffic → contact matching |
| Daily Rollups | `LT - Report Daily Rollups` | Aggregated summary, channel, UTM, landing page tables |
| Executive API | `LT - Report Executive Summary API` | JSON served to embed via n8n webhook |

### GHL Custom Fields Captured for Reporting
- `UTM Source First/Last`, `UTM Medium First/Last`, `UTM Campaign First/Last`, `UTM Content First/Last`, `UTM Term First/Last`, `UTM Landing Page First/Last`
- `Warm Source`, `Warm Trigger Type`, `Lead Temperature`
- `LT Last Routing Channel`, `LT Last Routing Reason`, `LT Last Routed At`
- `LT Route Lock Until`, `LT Routing Priority`, `LT Last Event Fingerprint`, `LT Last Event At`

---

## Active Pipelines

| Pipeline | Stages |
|----------|--------|
| Warm | New → Qualified (MQL) → Routed to Outreach → Nurture Active → Disqualified |
| Sales Outreach | New → Attempting Contact → 2nd attempt → 3rd attempt → Engaged → Meeting Requested → Booked → Unresponsive |
| Sales | Discovery Scheduled → Discovery Completed → Proposal Sent → Negotiation → Closed Won / Closed Lost |

---

## Phase 1 — Live (Now → +90 days)

### Stack
- **GHL** — CRM, pipeline, routing, warm lead management
- **Apollo.io** — Enrichment, outbound sequences, SDR motion
- **Meta Ads** — Attribution-first reporting via GA4 UTM + GHL bridge
- **n8n** — All ingestion, bridge, rollup, and alerting orchestration

### Why GHL + Apollo
- Faster hiring (reps can operate in one tool)
- Faster pipeline (built-in routing eliminates manual handoffs)
- Lower cognitive load (scoring + routing automated)
- Gets reps + ops aligned quickly

### What to Test
- Messaging variants per vertical
- Offer framing by company size / industry
- Channel routing (which warm sources convert best)

### Key Constraints
- Enforce quality filters: titles, industries, revenue bands
- Don't let Apollo become spammy — enforce cadence limits
- Use GHL scoring + routing immediately — don't manual-tag

---

## Phase 2 — Planned (Once outbound proves ROI)

### Add Clay — precision layer on top of Apollo

Clay handles:
- Enterprise / strategic accounts
- Founder-led brands
- Platforms, MSOs, aggregators
- High-intent, high-context outreach

Apollo continues doing:
- Broad outbound
- SDR motion
- Volume coverage

### Clay Use Cases
- "Top 500 cannabis brands" — targeted account list
- "Brands spending on Meta but blocked" — retargeting pool
- "Recently funded alternative wellness brands" — funded signal

---

## Deferred / Blocked

| Item | Status | Notes |
|------|--------|-------|
| GSC Daily Ingest | Active | Search Console access granted; workflow healthy |
| Meta Ads raw spend ingest | Deferred | Attribution-first path live; spend reporting deferred |
| Clay integration | Planned Phase 2 | Not started |
| Matched funnel by landing page | Planned | Needs tighter landing-page and form tracking first |
| Sequence event performance | Planned next week | Need open, reply, click, bounce, and unsubscribe events from Apollo sequences |
| GHL → LinkedIn automation | Planned | LinkedIn connect dispatcher active; full workflow deferred |
| GHL Calls & Appointments Ingest | Active | Appointments ingest live (`yWZVSqEcjTbMT3kG`, calendar `SrtXcFVyea7pFl3nTiIK`); Calls ingest live from GHL Conversations |
| Pipeline stage velocity (days per stage) | Active | `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`) calculates this by combining pipeline history events with the previous stage record for each opportunity |

---

## Report Data Contract

Minimum v1 output from the executive report:
- [x] GA4 sessions by channel
- [x] GA4 landing pages
- [x] GHL contacts created
- [x] GHL opportunities created
- [x] GHL closed-won revenue
- [x] Funnel efficiency rates (session→contact, contact→opp, opp→meeting, meeting→won)
- [x] Attribution coverage rates (source fields, bridge match, sale match)
- [x] Meta attribution panel (GA4 UTM + GHL bridge)
- [x] Pipeline stage velocity (avg days per stage, per-opp timeline)
- [x] Sales Detail panel (win rate, deals by stage, pipeline value)
- [x] GSC clicks and impressions
- [ ] Meta raw spend/clicks/impressions (deferred)
- [ ] Matched funnel by landing page (after tracking is tightened)
- [ ] Sequence event performance (opens, replies, clicks, bounces, unsubscribes)

### Pipeline Movement Tracking

| Metric | Status | Notes |
|--------|--------|-------|
| Stage counts by day | Working | `report_stage_daily_summary.stage_count` |
| Moved-in count | Working | Computed via LAG window comparing previous day's stage count |
| Moved-out count | Working | Computed via LAG window comparing previous day's stage count |
| Won/lost counts | Working | From opportunity status mapping |
| Pipeline history raw events | Captured | `report_raw_ghl_pipeline_history` table populated by GHL Daily Sales Ingest |
| Stage-by-stage velocity | Live | Computed by `LT - Report Pipeline Velocity` using pipeline history events plus the previous stage for each opportunity; writes to `report_stage_velocity_summary` and `report_opp_stage_timeline` |
| Opportunity cycle length | Live | Now computed from actual event timestamps via `report_opp_stage_timeline.days_in_stage` |
| True stage transition timestamps | Live | `report_opp_stage_timeline` has `entered_at` / `exited_at` per opportunity per stage |

**Resolved**: Pipeline velocity (avg days between stages) is now computed from actual pipeline history event timestamps by `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`). The workflow uses a query that compares each stage event to the previous stage event for the same opportunity, then writes to `report_stage_velocity_summary` (14 stages across 3 pipelines) and `report_opp_stage_timeline` (50,522 rows). Runs daily at 24h interval.

Additional reporting requests that would be sub sections under the main section and can be covered in calls more in depth by team leads
Sales (john)
- Total calls by status → Available via `report_raw_ghl_calls` and the Calls & Conversations panel in the Executive Report
- Total meetings and if they showed → Available via `report_raw_ghl_appointments` (ingested by `LT - GHL Daily Appointments Ingest`, calendar `SrtXcFVyea7pFl3nTiIK`)
- Contract closed and pending → Available via Sales Detail panel and Deal Stage Pipeline in executive report
- Win rate (closed won / closed total) → Available in Sales Quality panel

Social and site (chella)
- Social engagement: comments, reactions etc. → Needs Meta/Facebook Graph API (not in GHL)
- Website visits and traffic source → Already available via GA4 + channel breakdown
- Interactions on website: page visited, form fills etc. → Already available via GA4 landing pages + GHL forms

Next-week follow-up
- Sequence reporting → add event-level ingest for opens, replies, clicks, bounces, and unsubscribes so the report shows sequence performance, not just enrollments.
- Landing pages → preserve page URL and UTM fields consistently on every link and form so a matched funnel by landing page becomes reliable.
- Website pages → show the most visited pages as a short summary using the landing-page rollup while the deeper funnel tracking is being tightened.
````

## File: tmp_prepare_phone_live.js
````javascript
function str(v)
function lower(v)
function normalizePhone(raw)
function uniquePhones(values)
function getCustomFieldValue(contact, fieldId)
async function doHttpRequest(options)
async function apiRequest(
````

## File: tmp-corrections.ts
````typescript

````

## File: tmp-rollup-js.js
````javascript

````

## File: tmp-rollup-skel.ts
````typescript

````

## File: Unipile_potential_automations.md
````markdown
# Unipile Potential Automations

These are potential automations we want to do using Unipile for our regulated-industry advertising business.

---

## 1. InMail Campaigns

**Purpose:** Send sponsored LinkedIn messages directly to prospects who aren't connected.

**Use Case:** Great for reaching decision-makers who don't accept connection requests.

**Implementation:**
- Build a GHL automation that triggers when a new lead enters the system
- Send an InMail campaign with a personalized message
- Track responses and tag leads based on engagement

---

## 2. List Building & Enrichment

**Purpose:** Search LinkedIn for ideal prospects and enrich them with contact info.

**Use Case:** Find marketing directors at cannabis brands, CBD companies, or other regulated industries.

**Implementation:**
- Create a scheduled workflow that searches for targets by title/industry
- Enrich profiles with email, phone, company size
- Auto-create/update GHL contacts with enriched data
- Tag by campaign stage and priority score

---

## 3. Competitor Audience Targeting

**Purpose:** Find people who follow or engage with competitor pages.

**Use Case:** Target prospects who are already interested in regulated-industry advertising solutions.

**Implementation:**
- Monitor competitor LinkedIn pages for followers
- Build targeted outreach lists from engaged users
- Send personalized messages highlighting our unique capabilities
- Track conversion rates vs. cold outreach

---

## 4. Event-Based Outreach

**Purpose:** Trigger outreach when prospects post about challenges or attend events.

**Use Case:** Reach out when someone posts about "getting banned from Meta ads" or industry events.

**Implementation:**
- Monitor LinkedIn for keywords like "restricted", "banned", "compliance"
- Trigger automated outreach within 24 hours
- Personalize message based on their specific pain point
- Schedule follow-up tasks in GHL

---

## 5. Multi-Step Sequences

**Purpose:** Automate a 3-5 step sequence with timed follow-ups.

**Use Case:** Connection → follow-up message → InMail → break-up message.

**Implementation:**
- Day 0: Send connection request
- Day 3: If accepted, send follow-up message
- Day 7: If no response, send InMail
- Day 14: If still no response, send break-up message
- Track acceptance/response rates at each stage

---

## 6. Lead Scoring & Prioritization

**Purpose:** Score prospects based on profile signals.

**Use Case:** Prioritize hot leads for manual follow-up.

**Implementation:**
- Score based on job seniority (executive = high score)
- Score based on company size (larger = higher score)
- Score based on engagement rate (active poster = higher score)
- Auto-route high-score leads to sales team in GHL
- Low-score leads go into nurture sequence

---

## 7. CRM Sync & Tagging

**Purpose:** Auto-create/update GHL contacts and track engagement history.

**Use Case:** Keep GHL in sync with LinkedIn outreach activities.

**Implementation:**
- Webhook listener for Unipile events (connection accepted, message replied)
- Auto-create GHL contact if not exists
- Tag by campaign stage (connected, replied, scheduled, etc.)
- Log all outreach history in GHL notes
- Trigger GHL automations based on engagement

---

## 8. A/B Testing Message Variations

**Purpose:** Test different hooks and automatically route better performers.

**Use Case:** Test "Mood case study" vs. "compliance guarantee" messaging.

**Implementation:**
- Create multiple message variants in template registry
- Split outreach 50/50 to test groups
- Track acceptance/response rates per variant
- Auto-switch to winner after statistical significance
- Log results in GHL for future reference

---

## 9. Analytics & Attribution Dashboard

**Purpose:** Track connection acceptance rates, response rates, and downstream conversions.

**Use Case:** Measure ROI of LinkedIn outreach campaigns.

**Implementation:**
- Export Unipile metrics to Postgres or BigQuery
- Build dashboard showing:
  - Connections sent / accepted rate
  - Response rate by message variant
  - Meetings booked from LinkedIn
  - Leads created from LinkedIn
  - Revenue attributed to LinkedIn
- Sync metrics to GHL reports

---

## 10. Team Account Management

**Purpose:** Manage multiple LinkedIn accounts with centralized reporting.

**Use Case:** One account for John, one for Cameron, one for sales team.

**Implementation:**
- Use Unipile's team features for multiple accounts
- Centralized reporting dashboard
- Permission-based access (sales vs. marketing)
- Auto-rotate accounts to avoid rate limits
- Track performance per account/rep

---

## Bonus: GHL Automation Integration

**Purpose:** Trigger GHL automations based on Unipile events.

**Use Case:** Automatically move leads through sales pipeline.

**Implementation:**
- Webhook endpoint in GHL for Unipile events
- On connection accepted: Add to "Hot Lead" campaign
- On message replied: Schedule follow-up call task
- On meeting booked: Create calendar event + send prep email
- On no response after X days: Add to nurture sequence

---

## Next Steps

1. **Priority 1:** Implement CRM Sync & Tagging (already partially done via webhook)
2. **Priority 2:** Build Multi-Step Sequences for John's outreach
3. **Priority 3:** Set up Lead Scoring & Prioritization
4. **Priority 4:** Create Analytics Dashboard for ROI tracking

Each automation can be implemented incrementally, starting with the webhook infrastructure already in place.

## Implementation Order

1. Ship the Instagram DM workflow first so the team has a dedicated Unipile-backed sequence for mutual followers and follow-backs.
2. Reuse the same message registry concept for LinkedIn, but keep LinkedIn as a separate variant layer so step timing and audience rules stay isolated by channel.
3. After the Instagram flow is stable, extract the shared copy registry so LinkedIn and Instagram can read from the same template source without sharing state.
````
