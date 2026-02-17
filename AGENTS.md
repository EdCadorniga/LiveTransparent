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
- n8n workflow `GHL Warm Lead Setup - Fields and Tags`
- n8n workflow `GHL Warm Pipelines - Validate and Map IDs`
- n8n workflow `GHL Warm Lead Setup - UTM and Routing Fields`
- n8n workflow `GHL Warm Lead Fields - Duplicate Cleanup`
- n8n workflow `WF - Warm Channel Micro Entry` (inactive, dryRun=true)
- n8n workflow `WF - Master Warm Intake and Routing` (inactive, dryRun=true)
- n8n workflow `GHL Apollo Enrichment - Webhook Intake`
- n8n workflow `LT Error Notify - Apollo Enrichment Workflow`
- n8n workflow `GHL Apollo Enrichment - Webhook Intake (Sheet First)`
- n8n workflow `Apollo Contacts -> Postgres Ingest`
- n8n workflow `GHL Ensure Batch_Upload Field`
- n8n workflow `GHL Import - Apollo Sheet Opened Email`
- n8n workflow `GHL Warm Intake - Add Intake Tag (Webhook)` (active as of `2026-02-16`; confirm dryRun/defaultDryRun before live writes)
- n8n workflow `GHL Warm Intake - Email Inbound Tag (Webhook)` (active as of `2026-02-16`; confirm dryRun/defaultDryRun before live writes)
- n8n workflow `GHL Warm Intake - Email Outbound Tag (Webhook)` (active as of `2026-02-16`; confirm dryRun/defaultDryRun before live writes)
- n8n workflow `GHL Warm Intake - SMS Tag (Webhook)` (active as of `2026-02-16`; confirm dryRun/defaultDryRun before live writes)
- n8n workflow `GHL Warm Intake - Referral Tag (Webhook)` (active as of `2026-02-16`; confirm dryRun/defaultDryRun before live writes)
- Plan doc: `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Training guide: `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
- Quick reference: `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
- AI agent process: `GHL Live Transparent CRM/AI_Agent_Knowledgebase_Setup_Process.md`
- BookStack deploy guide: `bookstack/README.md`

## Contact Field Status (Current)
- Warm fields: complete.
- UTM first/last-touch fields: complete.
- LT routing metadata fields: complete.
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
- `WL - Micro - Referral`: finish/verify trigger on tag added `Referral - Intake`, then remove intake tag at workflow end.
- `WL - Micro - Meta Traffic`: build/verify trigger and warm tag flow.
- `WL - Micro - Meta Remarketing`: build/verify trigger and warm tag flow.
- `WL - Micro - SMS`: build/verify trigger and warm tag flow.
- `WL - Micro - Website`: build/verify trigger and warm tag flow.
- Verify `WL - Master Warm Intake and Routing` trigger list includes every warm tag, including `Warm Meta Remarketing`.
- Verify opportunity routing handoff automation for `Sales Outreach: Booked` -> `Sales: Discovery Scheduled`.
- Verify active outreach/nurture sequence stop conditions at booked/closed states.
- Validate/test active n8n warm intake tag webhooks; set `defaultDryRun=false` (or pass `dryRun=false`) only when ready for live intake tag writes.
- Restart Codex/MCP session after updating `N8N_WEBHOOK_USERNAME` and `N8N_WEBHOOK_PASSWORD` in `~/.codex/config.toml` so `run_webhook` can execute authenticated tests.
- End-to-end tests are pending (no production contacts yet).

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
- Funnel content plan document: `Transparent_eCom_Funnel_Plan.doc`
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
- Current dry-run behavior remains in place:
- `defaultDryRun=true` unless request payload passes `dryRun=false`.

## Next Steps (Queued)
- Run a full review pass of all existing n8n workflows that were previously left behind:
- confirm active/inactive state
- confirm dryRun/defaultDryRun behavior
- confirm trigger paths, credentials, and downstream actions
- identify stale/duplicate workflows for archive or cleanup plan
- Review and expand other intake flows in n8n beyond hero/footer website forms:
- funnel intake webhook flow
- referral intake flow
- email inbound/outbound intake tagging flows
- SMS intake tagging flow
- ensure each intake path can reliably add enrollment tag(s) for the sequence router

## LLM Operating Constraints
You are a code-first, automation-focused assistant under strict constraints.

### RULES
- Follow this prompt and AGENTS.md exactly. AGENTS.md is authoritative.
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

