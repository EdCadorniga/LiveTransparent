# LiveTransparent Agent Notes

## Project Context
- This project is deployed on a VPS using Coolify.
- There are currently two separate containers managed in Coolify.
- Those containers can reach each other over Coolify's internal/local network.
- `n8n` is publicly routed at `https://automations.livetransparent.com`.
- `bookstack/` assets are prepared in-repo but BookStack is not deployed yet.

## Working Assumptions
- Prefer internal service-to-service communication over the Coolify network where possible.
- Use `automations.livetransparent.com` as the canonical n8n public host for webhook/editor URLs.
- Keep config values centralized in service `.env` files so future domain cutovers are small changes.

## Agent Tooling
- This environment has MCP access to the `n8n` instance via the `n8n-lt` MCP server entry in Codex config.
- When workflow state or runtime behavior is relevant, use the `n8n-lt` MCP tools to verify actual instance state instead of guessing from local files.

## Status Freshness Rule
- Operational status sections in this file are snapshots, not guarantees.
- Treat all `Current` / `Active` status items as "last known state" and re-verify in-system before acting.
- Re-verify workflow activation/state via `n8n-lt` MCP tools before making runtime decisions.

## Paths and Layout
- Keep Docker and service-specific assets under their service folders (for example, `n8n/` and `postgres/`).
- Place service docs close to the service they describe.
- Keep knowledgebase deployment assets under `bookstack/`.

## File Map
- `AGENTS.md`: Agent rules and project operating notes.
- `.env`: Root/shared environment values (non-service-specific).
- `Marketing Docs/Transparent_eCom_Brand_Voice_And_Foundation.docx`: Canonical brand narrative, mission, values, and voice/tone.
- `Marketing Docs/Transparent_eCom_Core_Customer_ICP.docx`: Ideal client profile, decision makers, pain points, and core offer-fit reasons.
- `Marketing Docs/Transparent_eCom_Strategic_Priority_Segments.docx`: Tiered segment priorities and explicit "not for" exclusions.
- `n8n/docker-compose.yml`: n8n service definition, environment wiring, and Traefik labels.
- `n8n/.env`: n8n runtime secrets and host/webhook/editor URL environment values.
- `n8n/nodes/apollo/REFERENCE.md`: Apollo node/API reference map used in this repo.
- `n8n/nodes/ghl/REFERENCE.md`: GHL node/API reference map used in this repo.
- `n8n/nodes/twilio/REFERENCE.md`: Twilio node/API reference map used in this repo.
- `postgres/docker-compose.yml`: Postgres service definition for the stack.
- `bookstack/docker-compose.yml`: BookStack + MariaDB service definition and Traefik labels.
- `bookstack/.env.example`: BookStack environment template for Coolify.
- `bookstack/README.md`: BookStack deployment and hardening notes.
- `EMAIL templates/Cannabis Ads Sequence/`: Source HTML email templates for the cannabis ads sequence.
- `ghl create sequence plan/`: Working folder for sequence build specs, MCP preflight artifacts, and rollout checklists.
- `ghl create sequence plan/ab-sequence-enrollment-checklist.md`: Execution checklist for 50/50 A/B enrollment, stop rules, tracking fields, and sender warm-up ramp.
- `ghl create sequence plan/create_sequence_plan.md`: Prompt-driven sequence planning instructions and MCP execution guidance.
- `ghl create sequence plan/sequence-build-spec.json`: Sequence build specification artifact for deterministic workflow/template creation.
- `ghl create sequence plan/preflight-report.json`: Preflight validation output for sequence creation/update readiness.
- `ghl create sequence plan/ghl-mcp-tool-inventory.json`: MCP capability inventory snapshot used for tool/endpoint validation.
- `ghl create sequence plan/email-templates-cannabis-ads/Order A/`: Ordered HTML package for A path upload/copy.
- `ghl create sequence plan/email-templates-cannabis-ads/Order B/`: Ordered HTML package for B path upload/copy.
- `Email Sequence.docx`: Source sequence copy used to rebuild HTML templates.
- `Backup of all n8n workflows/`: Full-instance n8n workflow JSON backups (one file per workflow) plus export `manifest.json`.

## Reference Docs Convention
- Keep service reference files under `n8n/nodes/<service>/REFERENCE.md`.
- Reference files should map n8n node usage to concrete upstream API actions/endpoints where applicable.
- When native n8n node coverage is partial, document `HTTP Request` fallback endpoints explicitly.

## Marketing Docs Map (Canonical)
- Purpose: these are the source-of-truth docs for marketing copy and contact-facing messaging.
- Primary folder: `Marketing Docs/`
- Doc mapping:
- `Marketing Docs/Transparent_eCom_Brand_Voice_And_Foundation.docx`: use for brand story, tone, positioning language, and high-level offer framing.
- `Marketing Docs/Transparent_eCom_Core_Customer_ICP.docx`: use for persona targeting, pain-point framing, objections, and value proposition alignment.
- `Marketing Docs/Transparent_eCom_Strategic_Priority_Segments.docx`: use for segment prioritization, qualification filters, and disqualification language.
- Required usage:
- For funnel page copy (landing, qualification, booking, thank-you), reference these docs before drafting or revising copy.
- For contact communications (email, SMS, DM, nurture/outreach copy, internal message templates), align language and claims to these docs.
- For CTA/qualification logic, ensure segment and ICP alignment with the tier priorities and "Who We're Not For" constraints.
- If requested copy conflicts with these docs, flag the conflict and ask before proceeding.

## Locked GHL Map (Canonical)
- Location: `Live Transparent`
- Locked on: `2026-02-12`
- Security: internal IDs are intentionally omitted from this repo document; resolve live IDs in GHL UI and/or via approved MCP tools before changes.

### Pipelines and Stages
- `Warm` pipeline
- `New`
- `Qualified (MQL)`
- `Routed to Outreach`
- `Nurture Active`
- `Disqualified`

- `Sales Outreach` pipeline
- `New`
- `Attempting Contact`
- `Engaged`
- `Meeting Requested`
- `Booked`
- `Unresponsive`

- `Sales` pipeline
- `Discovery Scheduled`
- `Discovery Completed`
- `Proposal Sent`
- `Negotiation`
- `Closed Won`
- `Closed Lost`

## Current Execution Plan (Active)
1. Keep pipelines/stages as locked above; all automation must reference IDs, not names.
2. Build/maintain channel micro-automations in GHL:
- Trigger per source.
- Only apply warm tag + source metadata.
- Do not move pipeline/stage in micro-automations.
- GHL automations are primarily for routing and tagging.
- Intake tagging is handled through n8n webhook intake workflows so GHL contacts can already have the correct intake tags applied.
3. `WL - Master Warm Intake and Routing` in GHL:
- Trigger set on all warm channel tags.
- Priority branch routing configured.
- Per-branch field updates configured in order: `Warm Source`, `Primary Engagement Channel`, `Warm Trigger Type`.
- Base actions configured: set `Lead Temperature`, set `Warm Date`, add tags `Lead Status: Warm` and `Stage: MQL`.
4. Owner overwrite restrictions are deferred:
- Follow current default owner assignment behavior for now.
5. Run test matrix before broad rollout:
- duplicate events
- multi-channel collisions
- referral precedence
- re-engagement transitions
- outreach booked handoff to sales pipeline
- sequence stop conditions on booked/closed outcomes
6. Build channel micro-automations in GHL UI (in progress):
- One micro-workflow per channel/source trigger.
- Apply exact `Warm ...` tag only.
- Set source metadata fields only.
7. Deploy internal team knowledgebase on Coolify using BookStack:
- Deploy `bookstack/docker-compose.yml`.
- Restrict access to internal team (Cloudflare Access or equivalent).
- Publish internal SOP/process docs there.
8. Optional later phase: connect GHL AI Agent to knowledgebase content after routing tests pass and licensing is approved.

## Existing Setup Artifacts
- n8n workflow `GHL Warm Intake - Add Intake Tag (Webhook)` (`OowP3sAd8c9paSKf`) - active.
- n8n workflow `GHL Warm Intake - Email Inbound Tag (Webhook)` (`SmMf8QIfysuxQJbG`) - active.
- n8n workflow `GHL Warm Intake - Email Outbound Tag (Webhook)` (`J4B0n0QeSeOeqAci`) - active.
- n8n workflow `GHL Warm Intake - SMS Tag (Webhook)` (`5nYzp9DgQUopzWhR`) - active.
- n8n workflow `GHL Warm Intake - Referral Tag (Webhook)` (`6lp8sIS3YMB1t9Ri`) - active.
- n8n workflow `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`) - active.
- n8n workflow `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`) - active.
- n8n workflow `GHL Apollo Enrichment - Webhook Intake (Sheet First)` (`WmKAhG7mIaXonNsh`) - active.
- n8n workflow `GHL Apollo Enrichment - Phone Webhook Intake (Staged)` (`WuxgTa0EEL1mb2SA`) - active.
- n8n workflow `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`) - active.
- n8n workflow `LT - Cold Outreach CSV -> Postgres Ingest (Staged)` (`kVCTmy1m8fEyP6Q7`) - active.
- n8n workflow `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)` (`T28iLcm4Hszo19MG`) - active.
- n8n workflow `LT - Cold Outreach Sender Release Dispatcher (Staged)` (`NTpQnMrpjzusPXHX`) - active.
- n8n workflow `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) - active.
- n8n workflow `WL - Webhook to Slack Channel - Website Visitor` (`8USvJkRlKzbj6Fu1`) - active.
- n8n workflow `WL - Webhook to Slack Channel - Form Submission` (`FQE90HDUilFVdASY`) - active.
- Plan doc: `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Training guide: `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
- Quick reference: `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
- GHL webhook sender checklist: `GHL Live Transparent CRM/GHL_Intake_Webhook_Sender_Automations_Checklist.md`
- AI agent process: `GHL Live Transparent CRM/AI_Agent_Knowledgebase_Setup_Process.md`
- BookStack deploy guide: `bookstack/README.md`

## Contact Field Status (Current)
- Warm fields: complete.
- UTM first/last-touch fields: complete.
- LT routing metadata fields: complete.
- Apollo enrichment controls/flags:
- `contact.enrich_phone_via_apollo` (`Enrich Phone via Apollo`) is dropdown `Yes/No` trigger control.
- `contact.apollo_phone_enrichment_status` (`Apollo Phone Enrichment Status`) is dropdown status control (`queued`, `enriched`, `no_match`, `error`).
- `contact.apollo_phone_enriched_at` (`Apollo Phone Enriched At`) is currently written as `DATE` (`YYYY-MM-DD`) by workflow logic.
- `contact.apollo_contact_id` (`Apollo Contact Id`) is now only written on successful phone enrichment and prefers Apollo `contact.id` when available.
- `Corporate Phone` and `Company Phone` remain company/trunkline metadata only and are explicitly excluded from direct phone writes.
- Duplicate UTM/LT fields were created during initial run and cleaned up; one canonical field per name now exists.
- `Warm Date` is canonically `DATE` by design (no Date/Time migration planned).

## Workflow Status (Current)
- GHL workflow `WL - Master Warm Intake and Routing`
- Branch routing and branch field updates are configured.
- Channel micro-automations are partially built in GHL UI.
- Completed in GHL UI (as of `2026-02-14`):
- `WL - Micro - LinkedIn` (previously complete)
- `WL - Micro - LinkedIn DM` (previously complete)
- `WL - Micro - LinkedIn Lead Form` (previously complete)
- `WL - Micro - Meta Lead Form` (trigger + tag + warm source metadata + UTM first/last-touch logic)
- `WL - Micro - Email Inbound` (intake-tag pattern)
- `WL - Micro - Email Outbound` (intake-tag pattern)
- `WL - Micro - Instagram` actions are configured but trigger is not connected yet.
- Added intake tag `Referral - Intake` for referral-triggered micro workflow entry.
- Added intake tags for channel-splitting where trigger filtering is unavailable:
- `Warm Intake - Email Inbound`
- `Warm Intake - Email Outbound`
- `Warm Intake - SMS`
- Pending / revisit required:
- `WL - Micro - Instagram`: connect trigger after Instagram pages are selected.
- `WL - Micro - Facebook` (Messenger): deferred until Facebook pages are connected.
- `WL - Micro - Meta Traffic`: build/verify trigger and warm tag flow.
- `WL - Micro - Meta Remarketing`: build/verify trigger and warm tag flow.
- `WL - Micro - Website`: build/verify trigger and warm tag flow.
- Verify `WL - Master Warm Intake and Routing` trigger list includes every warm tag, including `Warm Meta Remarketing`.
- Verify opportunity routing handoff automation for `Sales Outreach: Booked` -> `Sales: Discovery Scheduled`.
- Verify active outreach/nurture sequence stop conditions at booked/closed states.
- Validate/test active n8n warm intake tag webhooks; set `defaultDryRun=false` (or pass `dryRun=false`) only when ready for live intake tag writes.
- Restart Codex/MCP session after updating `N8N_WEBHOOK_USERNAME` and `N8N_WEBHOOK_PASSWORD` in `~/.codex/config.toml` so `run_webhook` can execute authenticated tests.
- End-to-end tests are pending (no production contacts yet).

### n8n Intake Runtime Status (Verified `2026-02-26` via `n8n-lt`)
- Website intake webhooks (active):
- `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`) path `lt-form-demo-intake`, `defaultDryRun=false`.
- `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`) path `lt-form-footer-intake`, `defaultDryRun=false`.
- Warm intake tagging webhooks (active, dry-run by default):
- `GHL Warm Intake - Add Intake Tag (Webhook)` (`OowP3sAd8c9paSKf`) path `lt-warm-intake-tag`, `defaultDryRun=true`.
- `GHL Warm Intake - Email Inbound Tag (Webhook)` (`SmMf8QIfysuxQJbG`) path `lt-warm-intake-email-inbound`, `defaultDryRun=true`.
- `GHL Warm Intake - Email Outbound Tag (Webhook)` (`J4B0n0QeSeOeqAci`) path `lt-warm-intake-email-outbound`, `defaultDryRun=true`.
- `GHL Warm Intake - SMS Tag (Webhook)` (`5nYzp9DgQUopzWhR`) path `lt-warm-intake-sms`, `defaultDryRun=true`.
- `GHL Warm Intake - Referral Tag (Webhook)` (`6lp8sIS3YMB1t9Ri`) path `lt-warm-intake-referral`, `defaultDryRun=true`.
- Apollo enrichment intake:
- `GHL Apollo Enrichment - Webhook Intake (Sheet First)` (`WmKAhG7mIaXonNsh`) is active.
- `GHL Apollo Enrichment - Phone Webhook Intake (Staged)` (`WuxgTa0EEL1mb2SA`) is active.
- `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`) is active.
- Legacy callback workflow `YaWizRnw7XmkcvZH` should be treated as superseded by V4 for production callback handling.
- `GHL Apollo Enrichment - Webhook Intake` (`HQaHuLZbtKCSaKqE`) was deleted on `2026-02-26` during archived-workflow cleanup.
- Phone enrichment paths:
- intake path: `ghl-apollo-phone-enrichment-intake-v3`
- callback path: `ghl-apollo-phone-enrichment-callback-v4`
- Sheet-first enrichment path: `ghl-apollo-enrichment-intake-sheet-first-v3`
- Apollo phone workflow is callback-driven:
- intake requests Apollo match + phone reveal and leaves contacts in `queued` with reason `awaiting_callback` when no acceptable direct phone is returned synchronously.
- callback V4 processes Apollo webhook payloads from `body.people[0]`, `body.data.people[0]`, or `body.person`.
- Apollo profile + phone parsing now prioritizes person-level direct phone sources and filters out company/trunkline values from `Corporate Phone` and `Company Phone`.
- `Apollo_Contacts` upsert now includes top-level `phone` plus `ingest_record` payload.
- Intake appends diagnostic columns to the `Enriched Contacts` Google Sheet, including `enrichment_status`, `enrichment_reason`, `apollo_error_status`, `apollo_error`, `duplicate_phone_conflict`, `normalized_phone`, `found_phone`, `update_request_body_used`, and `raw_result`.
- Intake wiring note:
- GHL sender automations are confirmed live for `Email Inbound`, `Email Outbound`, `SMS`, and `Referral`; these intake endpoints are now receiving webhook traffic.
- Keep `dryRun` as boolean `false` in GHL webhook payloads for live writes (not string `"false"`).

## Funnel Workstream Status (Current)
- Workstream started on `2026-02-16`.
- Current direction: manual funnel build in GHL UI using approved page copy/content plan (not "Generate with AI").
- Primary funnel objective: booked demos for compliance ad account offers; secondary objective: qualified lead capture.
- Planned funnel structure:
- Landing Page
- Qualification Page
- Booking Page (calendar)
- Thank You Page

### Funnel Artifacts Added
- Funnel content plan document: `Transparent_eCom_Funnel_Plan.docx`
- Website issues backlog for later fixes: `WEBSITE_ISSUES_AUDIT_2026-02-16.md`

### Funnel Source Attribution Rules (Locked)
- Differentiate funnel-originated leads from website-originated leads using explicit source tags and fields.
- Use source tags:
- `Warm Funnel`
- `Warm Website`
- In funnel form-entry automation set:
- `Warm Source` = `Funnel`
- `Primary Engagement Channel` = `Website Funnel`
- `Warm Trigger Type` = `Form Submitted`
- In website form-entry automation set:
- `Warm Source` = `Website`
- `Primary Engagement Channel` = `Website`
- `Warm Trigger Type` = `Form Submitted`
- Optional hidden field standard for forms:
- `lead_origin` with default `funnel` on funnel forms and `website` on website forms.

### Funnel Automation Trigger Pattern (Locked)
- Use micro-workflow entry via `Form Submitted` trigger filtered to exact:
- Funnel
- Funnel Step
- Form
- Micro-workflow should only:
- apply source tag
- set source metadata fields
- do not move pipeline/stage
- Master routing remains in `WL - Master Warm Intake and Routing` and must be tag/field driven.

### GHL Tracking/SEO Settings Notes
- Funnel-level `Head Tracking Code` and `Body Tracking Code` are manual script injection fields, not auto-generated by GHL.
- Prefer one tracking method (recommended: GTM) to avoid duplicate events.
- SEO title/meta description and social preview settings should be configured per funnel step/page in the page builder SEO panel.

## Session Notes (2026-02-17)
- Objective for today: set up Sales Outreach email sequence assets and prepare direct workflow build capability.
- Source content reviewed: `Email Sequence.docx`.
- Local template assets created and organized under:
- `EMAIL templates/Cannabis Ads Sequence/`
- `01-cannabis-ads-1-v5.html`
- `02-cannabis-ads-3-v5.html`
- `03-cannabis-ads-1-v1.html`
- `04-cannabis-ads-5-v1.html`
- `05-cannabis-ads-4-v1.html`
- A/B testing delivery folders prepared under:
- `ghl create sequence plan/email-templates-cannabis-ads/Order A/`
- `01-cannabis-ads-1-v5.html`
- `02-cannabis-ads-1-v1.html`
- `03-cannabis-ads-3-v5.html`
- `04-cannabis-ads-4-v1.html`
- `05-cannabis-ads-5-v1.html`
- `ghl create sequence plan/email-templates-cannabis-ads/Order B/`
- `01-cannabis-ads-1-v5.html`
- `02-cannabis-ads-3-v5.html`
- `03-cannabis-ads-1-v1.html`
- `04-cannabis-ads-5-v1.html`
- `05-cannabis-ads-4-v1.html`
- GHL template folder created for production use:
- `WL - Sequences - Cannabis Ads (Ready)`
- GHL templates created in send order:
- `01 - Cannabis Ads-1-V5 - Say Goodbye To Censored Cannabis Ads On Meta`
- `02 - Cannabis Ads-3-V5 - Why Do Ad Agencies Suck`
- `03 - Cannabis Ads-1-V1 - Breakthrough Alert`
- `04 - Cannabis Ads-5-V1 - Let's Talk About Failure`
- `05 - Cannabis Ads-4-V1 - Save $200k On EBITA`
- CTA link standardized from apply-page Calendly flow:
- `https://calendly.com/transparentecom/how-to-run-cannabis-ads-on-meta`
- Template formatting applied:
- Inline CTA hyperlinks for action phrases (e.g., `book a meeting`)
- CTA button above signature (`Book a Meeting`)
- Logo footer using `livetransparent_logo.png` equivalent hosted logo URL
- Royal Blue CTA button style applied (`#4169E1`)
- Black footer background enforced for logo visibility
- Greeting merge field standardized to `{{contact.first_name}}`
- Calendly link normalized to base URL above for both body hyperlink text and button (no `?month=...` query)
- Greeting/body line-break spacing fixed in:
- `ghl create sequence plan/email-templates-cannabis-ads/Order A/04-cannabis-ads-4-v1.html`
- `ghl create sequence plan/email-templates-cannabis-ads/Order B/05-cannabis-ads-4-v1.html`
- n8n full workflow backup exported to:
- `Backup of all n8n workflows/`
- Export scope and format:
- `24` workflows exported from live n8n.
- `manifest.json` included with export timestamp, workflow IDs, names, and file mapping.
- MCP prep for direct workflow creation:
- Added MCP server `ghl_workflows` in Codex global config using `@drausal/gohighlevel-mcp`.
- Restart required before this session can use newly added `ghl_workflows` tools.
- Immediate next action after restart:
- Build `WL - Seq - Sales Outreach` workflow directly in GHL with exit checks between each send (reply/booked/closed states).
- n8n website intake workflows updated live (MCP verified):
- `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`)
- `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`)
- Both workflows now add tags after successful upsert/update:
- `Warm Website`
- `Enrollment Queue - Cannabis Ads`
- Webhook paths remain unchanged:
- `lt-form-demo-intake`
- `lt-form-footer-intake`
- Both workflows remain active.
- Current dry-run behavior (verified `2026-02-24`):
- Website intake workflows use `defaultDryRun=false` (live by default).
- Warm intake tag webhooks remain `defaultDryRun=true` unless request payload passes `dryRun=false`.
- A/B enrollment routing decision finalized:
- Canonical splitter is now **GHL Randomizer** inside GHL workflow `WL - Seq Enrollment Router - Cannabis Ads`.
- n8n router rollback workflows were deleted on `2026-02-26` after hold window completion:
- `WL - Seq Enrollment Router - Cannabis Ads (Workflow IDs Live)` (`UJnHFPxSdTcsK9iW`) - deleted
- `WL - Seq Enrollment Router - Cannabis Ads` (`L5Cpe7ZdUgauQcF7`) - deleted

## Next Steps (Queued)
- Run a full review pass of all existing n8n workflows that were previously left behind:
- confirm active/inactive state
- confirm dryRun/defaultDryRun behavior
- confirm trigger paths, credentials, and downstream actions
- identify stale/duplicate workflows for archive or cleanup plan
- Review and expand other intake flows in n8n beyond hero/footer website forms:
- funnel intake webhook flow
- ensure each intake path can reliably add enrollment tag(s) for the sequence router
- Sequence router rollback cleanup completed on `2026-02-26` (obsolete router workflows deleted).

## Session Notes (2026-02-26)
- Archived/inactive n8n workflow cleanup completed via `n8n-lt`.
- Deleted `21` inactive workflows from the live instance.
- Post-cleanup n8n runtime state: `14` workflows total, all active.
- Deleted router rollback workflows:
- `WL - Seq Enrollment Router - Cannabis Ads (Workflow IDs Live)` (`UJnHFPxSdTcsK9iW`)
- `WL - Seq Enrollment Router - Cannabis Ads` (`L5Cpe7ZdUgauQcF7`)
- Apollo phone enrichment implementation completed and verified live:
- Activated `GHL Apollo Enrichment - Phone Webhook Intake (Staged)` (`WuxgTa0EEL1mb2SA`) and initial callback handler `YaWizRnw7XmkcvZH`.
- Updated `GHL Apollo Enrichment - Webhook Intake (Sheet First)` (`WmKAhG7mIaXonNsh`) with matching phone parsing/update behavior.
- Added guarded webhook key validation in intake/callback handling.
- Added GHL custom field writes for:
- `Apollo Phone Enrichment Status` (`queued`/`enriched`/`no_match`/`error`)
- `Apollo Phone Enriched At` (`YYYY-MM-DD`)
- `Contact already Enriched` -> `Yes`
- `Enrich via Apollo` -> `No`
- `Enrich Phone via Apollo` -> `No`
- Added `Title` mapping from Apollo into GHL `Title` custom field.
- Added GHL custom field value normalization:
- `TEXT` fields trimmed to avoid 422 payload-length failures
- `DATE` fields normalized to `YYYY-MM-DD`
- Added Postgres `Apollo_Contacts.phone` support in both intake workflows:
- table DDL `ADD COLUMN IF NOT EXISTS phone TEXT`
- upsert writes `phone = normalizedPhone`
- Added sheet row output fields for callback/debug visibility including callback URL used.

## Session Notes (2026-03-04)
- Apollo phone enrichment callback registration issue was resolved by creating a fresh production callback workflow with a registered webhook node:
- `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`)
- Production callback path is now `ghl-apollo-phone-enrichment-callback-v4`.
- Production intake path remains `ghl-apollo-phone-enrichment-intake-v3`.
- Intake workflow now:
- leaves matched contacts in `queued` with reason `awaiting_callback` when Apollo does not return an acceptable direct phone synchronously
- ignores Apollo phone candidates that match existing `Corporate Phone` or `Company Phone`
- does not write `Apollo Contact Id` until a successful phone enrichment occurs
- appends detailed diagnostics to the `Enriched Contacts` sheet for each run
- Callback V4 now:
- parses Apollo native webhook payload shapes from `people[]` and `person`
- writes `Apollo Contact Id` using Apollo `contact.id` when available, falling back to `person.id`
- only finalizes `enriched` when a real direct phone is written
- Live rerun results after callback fix:
- previously stale `queued` contacts were largely resolved through reruns once callback V4 was active
- current queued contacts should be treated as active Apollo callback waits rather than stale webhook-registration failures unless age indicates otherwise

## Session Notes (2026-02-24)
- Intake webhook sender wiring completed and validated:
- `WL - Micro - Email Inbound` -> `lt-warm-intake-email-inbound`
- `WL - Micro - Email Outbound` -> `lt-warm-intake-email-outbound`
- `WL - Micro - SMS` -> `lt-warm-intake-sms`
- `WL - Micro - Referral` -> `lt-warm-intake-referral`
- Production confirmation: inbound, outbound, sms, and referral intake flows are working.

## Session Notes (2026-02-20)
- Cold outreach workbook prep completed from `Cold-outreach contacts.xlsx`.
- Generated import artifacts and reports under:
- `cold-outreach-prep/ghl/`
- `cold-outreach-prep/postgres/`
- `cold-outreach-prep/reports/`
- Primary import files:
- `cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.csv`
- `cold-outreach-prep/postgres/cold-outreach-all.dedup-email.workflow-input.csv`
- Generated runbook/checklist:
- `cold-outreach-prep/reports/GHL-import-mapping-checklist.md`
- `cold-outreach-prep/reports/n8n-staged-workflows-runbook.md`
- Staged n8n workflows created:
- `LT - Cold Outreach CSV -> Postgres Ingest (Staged)` (`kVCTmy1m8fEyP6Q7`)
- `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)` (`T28iLcm4Hszo19MG`)
- Webhook paths:
- `/webhook/lt-cold-outreach-postgres-intake`
- `/webhook/lt-cold-outreach-ghl-import`
- Current workflow state:
- Both workflows are currently published/active (re-verify before next run).
- Dry-run execution attempt from this Windows shell failed at transport layer:
- `Invoke-RestMethod`: connection closed on receive
- `curl.exe` (schannel): `SEC_E_NO_CREDENTIALS`
- Conclusion:
- Webhook triggering from this Windows shell is currently unreliable due local TLS/schannel constraints.
- Switching execution to WSL Ubuntu is recommended for webhook-trigger testing and run control.
- Follow-up mapping/workflow updates completed (same day):
- Updated live staged GHL import workflow `T28iLcm4Hszo19MG` (`LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)`):
- `Import Contacts + Tags` now maps canonical contact fields + Apollo custom fields + mapped extras from the mapping spec.
- Removed `$env` dependency in mapping logic that caused prior dry-run failure.
- Added `Company Address` -> `address1` mapping.
- Added fallback aliases for `Company City`/`Company State`/`Company Country` -> `city`/`state`/`country`.
- Updated reusable mapping spec:
- `cold-outreach-prep/mapping/apollo_csv_mappings.json`
- Updated reusable validator behavior:
- `cold-outreach-prep/scripts/validate_apollo_csv_mapping.py`
- Validator now treats alias-covered headers as matched coverage (prevents false unmatched-header reporting for synonym columns).
- Regenerated validation reports after mapping/validator updates.
- n8n API access retest (same day):
- Verified that API access works when key is sent via header `X-N8N-API-KEY` (not Bearer auth).
- Current working key fingerprint for this session: ends with `a5ho` (store/use full key only in secure local config, not repo files).
- Verified endpoints with `X-N8N-API-KEY`:
- `GET /api/v1/workflows/kVCTmy1m8fEyP6Q7` -> `200`
- `GET /api/v1/executions?includeData=false&workflowId=kVCTmy1m8fEyP6Q7&limit=2` -> `200`
- `GET /api/v1/workflows/T28iLcm4Hszo19MG` -> `200`
- `GET /api/v1/executions?includeData=false&workflowId=T28iLcm4Hszo19MG&limit=2` -> `200`
- Bearer mode (`Authorization: Bearer <key>`) returns `401` with message `'X-N8N-API-KEY' header required`.
- Reusable test command pattern:
- `curl -sS -H "X-N8N-API-KEY: <N8N_API_KEY>" "https://automations.livetransparent.com/api/v1/workflows/<WORKFLOW_ID>"`
- Cannabis Ads sender-routing implementation decisions (same day):
- Canonical sender release control moved to n8n dispatcher workflow (not manual GHL-only release).
- New GHL field created for sender lock/routing: `marketing_sender_email`.
- Email actions in Cannabis Ads workflow are being configured to use dynamic sender:
- `From Email = {{contact.marketing_sender_email}}`
- Sender warm-up policy locked:
- Week 1 `50/day` per sender, Week 2 `75/day` per sender, Week 3+ `100/day` per sender.
- Quota interpretation locked:
- per-sender cap is total outbound emails/day (includes in-flight sequence sends + new enrollments), not just new contacts added that day.
- Current sender pool: one active sender; add additional senders later after domain + sender verification.
- Sender assignment timing locked:
- do not set `marketing_sender_email` at import time for backlog contacts.
- set `marketing_sender_email` immediately before enrollment/queue release so distribution reflects currently active verified senders.
- Current verified sender status (as of `2026-02-20`):
- `cameron@livetransparent.com` verified in GHL.
- Added implementation runbook:
- `GHL Live Transparent CRM/Cannabis_Ads_Sender_Routing_Runbook.md`
- Updated checklist artifact:
- `ghl create sequence plan/ab-sequence-enrollment-checklist.md`
- New n8n staged automation created for sender-capped release:
- `LT - Cold Outreach Sender Release Dispatcher (Staged)` (`NTpQnMrpjzusPXHX`)
- Purpose:
- assign `marketing_sender_email` at release time (not import time), apply `Enrollment Queue - Cannabis Ads`, and log releases in Postgres table `ColdOutreach_Release_Log`.
- Current live status update (`2026-02-21`):
- `NTpQnMrpjzusPXHX` is active/live, `defaultDryRun=false`, hourly trigger.
- Dispatch window gate: `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`.
- Sunday behavior: summary-only execution; no contact dispatch.
- Per-contact gate: dispatch only during contact local `8:00 AM-4:59 PM`.
- Timezone resolution order:
- use contact timezone when available
- fallback from `state/country` (`Apollo_Contacts` fields including company fallback columns)
- If contact missing/unknown timezone, contact is deferred and retried later (not logged as released).
- Candidate scope:
- source table `Apollo_Contacts`
- requires email + `cold-outreach` tag
- excludes contacts already present in `ColdOutreach_Release_Log`
- Verified live release test (`2026-02-21`):
- controlled live run with 10 contacts completed successfully (`queued=10`, `errors=0`)
- sender field set successfully using GHL `customFields` update payload
- queue routing validated downstream in GHL sequence workflows
- Live GHL import test completed (`2026-02-20`):
- Triggered `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)` (`T28iLcm4Hszo19MG`) with `dryRun=false` using 10-row batch from:
- `cold-outreach-prep/ghl/cold-outreach-10_100m.ghl.csv`
- Result:
- `sourceRecords=10`, `imported=10`, `errors=0`, `missingCustomFields=[]`.
- Artifacts:
- `cold-outreach-prep/reports/live-run-ghl-10-request-20260220T095512Z.json`
- `cold-outreach-prep/reports/live-run-ghl-10-response-20260220T095512Z.json`
- `cold-outreach-prep/reports/live-run-ghl-10-response-raw-20260220T095512Z.txt`

## WSL Transition Plan (Historical - Completed)
This block is preserved as execution history. Current operational state is now live and verified:
- `kVCTmy1m8fEyP6Q7` active (Postgres ingest webhook)
- `T28iLcm4Hszo19MG` active (GHL import webhook)
- `NTpQnMrpjzusPXHX` active/live (sender release dispatcher)

## LLM Operating Constraints
You are a code-first, automation-focused assistant under strict constraints.

### RULES
- Follow AGENTS.md for repo-specific rules. If AGENTS.md conflicts with higher-priority runtime/system instructions, follow the higher-priority instructions and flag the conflict.
- If instructions conflict or context is missing, STOP and ask.
- Do NOT guess, invent, or assume.
- Preserve existing behavior, schemas, payloads, and signatures unless explicitly told otherwise.
- Prefer correctness and maintainability over cleverness.
- Do NOT refactor, add files, or change architecture unless asked.
- Never silently change logic; fail loud with clear errors.

### RUNTIME
- Use ONLY the stated or clearly implied language/runtime.
- Do NOT mix ecosystems.
- If runtime support is uncertain, STOP and ask.

### GOOGLE APPS SCRIPT
- Assume V8 runtime.
- No Node.js APIs or packages.
- Prefer batch operations; respect quotas and limits.

### N8N (MANDATORY)
- n8n policy: keep production n8n updated to the latest stable version.
- Current observed live version (verified `2026-02-16`): `2.7.4`.
- Before using any node, operation, or parameter, verify against the currently running instance/schema when version-sensitive behavior matters.
  - If you cannot verify the running version/schema for a version-sensitive change, STOP and ask.
- Use ONLY current native nodes and parameters.
- Never use deprecated/legacy nodes or invent options.
- Prefer native nodes over Function/Code unless unavoidable.
- Use current expression syntax ($json, $items(), $node[]).

### OUTPUT
- Be concise and task-focused.
- Output code first when requested.
- No explanations unless asked.

Failure to follow these rules is incorrect.

