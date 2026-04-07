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
- This environment has MCP access to the live `n8n` instance via the `n8n-lt` MCP server entry in Codex config.
- For this project, use `n8n-lt` as the canonical n8n MCP. Do not assume a generic `n8n` MCP target.
- When workflow state or runtime behavior is relevant, use the `n8n-lt` MCP tools to verify actual instance state instead of guessing from local files.
- This environment also has GHL MCP access.
- Preferred GHL MCP for this location: `ghl_official`. Treat it as the primary MCP that is working against the valid PIT for the `Live Transparent` location.
- Secondary GHL MCP: `ghl_workflows`. It is available and useful, but some endpoints may fail there even when the PIT itself is valid.
- If a GHL MCP call returns scope/auth errors for an endpoint that should be available, verify whether the same endpoint works through direct GHL API before assuming the PIT is bad.

## Codex Skills Available
- This Codex environment includes reusable skills that may be invoked when the task matches them.
- Current installed skills:
- `ai-first-engineering`: engineering operating model and execution guidance for AI-heavy build workflows.
- `browser-qa`: browser-based QA and smoke testing using MCP browser tools.
- `codebase-onboarding`: structured unfamiliar-repo analysis and onboarding.
- `context-budget`: context window and prompt-budget auditing.
- `deep-research`: multi-source research with citations.
- `rules-distill`: extract and consolidate operational rules from existing skills/docs.
- `security-review`: secure implementation checklist for auth, secrets, inputs, APIs, and sensitive flows.
- `verification-loop`: verification-first workflow for implementation/testing loops.
- `openai-docs`: OpenAI docs/product guidance using current official documentation.
- `skill-creator`: create or improve Codex skills.
- `skill-installer`: install additional Codex skills.

## MCP Inventory
- `n8n-lt`: primary MCP for this project; use it for workflow state, execution checks, and runtime verification against `automations.livetransparent.com`.
- `ghl_official`: primary GHL MCP for this location; use it first when interacting with GHL data or configuration backed by the working PIT.
- `ghl_workflows`: secondary GHL MCP; use when it exposes needed actions, but be cautious about false scope/auth failures on some endpoints.
- Direct GHL API fallback remains approved when MCP behavior is inconsistent with known-good PIT access.

## GHL Direct API Fallback
- If `ghl_workflows` fails on a specific endpoint but `ghl_official` or other GHL reads still succeed, treat it as a possible MCP wrapper/auth-scope mismatch rather than an immediate PIT failure.
- For direct GHL API testing, use:
- Base URL: `https://services.leadconnectorhq.com`
- Headers:
- `Authorization: Bearer <PIT>`
- `Version: 2021-07-28`
- `Accept: application/json`
- In this Windows environment, direct HTTPS calls may fail inside the sandbox due local TLS/schannel issues; if the request matters, rerun outside the sandbox before concluding the endpoint is unavailable.
- Proven case (`2026-03-17`):
- `ghl_workflows.GET_all_or_email_sms_templates` returned `401` / `The token is not authorized for this scope.`
- Direct API call with the same PIT succeeded:
- `GET /locations/:locationId/templates?type=sms&limit=20`
- Required documented scope: `locations/templates.readonly`
- Conclusion: direct API fallback can recover access to endpoints that the MCP wrapper cannot currently reach.

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
- `emerald-email-campaign/`: Canonical workspace for the Emerald email campaign snapshot, rollout docs, and artifacts.
- `emerald-email-campaign/Exported Emerald Contacts.csv`: Fixed GHL-exported Emerald cohort snapshot used to seed the campaign dispatch table.
- `emerald-email-campaign/plan.md`: Emerald campaign architecture and locked decisions.
- `emerald-email-campaign/dispatcher-plan.md`: Emerald sender-dispatch and Postgres release rules.
- `emerald-email-campaign/workflow-mapping.md`: Mapping between Emerald queue tags, source tags, and the 4 GHL workflows.
- `Emerald Contacts/build_ghl_import.py`: Canonical Emerald CSV merger and GHL import generator.
- `Emerald Contacts/README.md`: Repeatable Emerald merge, dedupe, and GHL import runbook.
- `Backup of all n8n workflows/`: Full-instance n8n workflow JSON backups (one file per workflow) plus export `manifest.json`.
  - Latest full refresh: `2026-03-31`, `23` workflows exported, `0` failures.
- `Backup of n8n workflows UNTRACKED/`: Gitignored workflow backups for local/development use.
  - Follows naming convention: `{workflowId}__{sanitizedName}.json`
  - Not committed to version control
  - Created: 2026-03-31
- `GHL Live Transparent CRM/RB2B_Website_Visitor_Intake_Workflow.md`: Technical runbook for RB2B webhook intake, GHL reconciliation/tagging, Postgres upsert, and John follow-up task creation.

## Emerald Canonical (Current)
- Treat this section as the compact operational summary for Emerald. Keep deeper design detail in:
  - `emerald-email-campaign/plan.md`
  - `emerald-email-campaign/dispatcher-plan.md`
  - `emerald-email-campaign/workflow-mapping.md`

### Emerald Campaign Architecture
- Canonical source snapshot: `emerald-email-campaign/Exported Emerald Contacts.csv`
- Stable release pool: Postgres table `Emerald_Campaign_Contacts`
- Durable company-research cache: Postgres table `Emerald_Company_Research_Cache`
- Delivery system: GHL workflows
- Release controller: n8n workflow `LT - Emerald Campaign Sender Release Dispatcher (Staged)` (`8UXlpoMJnQ229AuG`)
- Shared campaign value: `Email Campaign = Emerald Cannabis Ads`

### Emerald Buckets and Queue Tags
- Buckets:
  - `executives_mso`
  - `executives_sso`
  - `marketing_mso`
  - `marketing_sso`
- Emerald queue tags:
  - `Enrollment Queue - Emerald - Executives MSO`
  - `Enrollment Queue - Emerald - Executives SSO`
  - `Enrollment Queue - Emerald - Marketing MSO`
  - `Enrollment Queue - Emerald - Marketing SSO`
- Shared enrolled tag:
  - `Seq Enrolled - Emerald`
- Bucket audit tags:
  - `Seq Emerald - Executives MSO`
  - `Seq Emerald - Executives SSO`
  - `Seq Emerald - Marketing MSO`
  - `Seq Emerald - Marketing SSO`

### Emerald GHL Sequence Workflows
- `WL - Seq - Cannabis Ads Emerald - Executives MSO` (`a3f96d18-3cd1-4182-b08d-8e6bde6f77c1`)
- `WL - Seq - Cannabis Ads Emerald - Executives SSO` (`e7a4dd5b-c6da-459c-9c48-2d5ca2bc3421`)
- `WL - Seq - Cannabis Ads Emerald - Marketing MSO` (`141d878e-7a27-43bc-97ab-c67c69b18f14`)
- `WL - Seq - Cannabis Ads Emerald - Marketing SSO` (`18eced4d-958a-49e4-9a23-899eabc94833`)
- Common workflow behavior:
  - remove matching Emerald queue tag on entry
  - add `Seq Enrolled - Emerald`
  - keep `From Email = {{contact.marketing_sender_email}}`
  - v1 keeps only the first 3 emails active unless explicitly changed

### Emerald Dispatcher Rules
- Do not dispatch by straight `ORDER BY id ASC`.
- Use bucket-interleaved candidate ordering so each batch mixes:
  - `executives_mso`
  - `executives_sso`
  - `marketing_mso`
  - `marketing_sso`
- Sender assignment happens in the dispatcher, not at import time.
- Sender warmup caps remain:
  - days 1-7: `300/day` per sender
  - days 8-14: `400/day` per sender
  - day 15 onward: `500/day` per sender
- Exclusion guards include:
  - prior Cannabis Ads enrollment tags/values
  - `Seq Enrolled - Emerald`
  - `Do Not Nurture`
  - blank email
  - email DND

### Emerald Company Sync Workflow
- Live workflow: `LT - Emerald Executive SSO -> Company Sync (Staged)` (`GHVYyYmhfNiZ7bbN`)
- Design intent: company-first research, not contact-first enrichment.
- Grouping key is `company_domain_key`, resolved in this order:
  - non-generic business email domain
  - stronger company/website signals
  - synthetic per-contact fallback key for generic-mailbox cases
- Reusable company findings are cached in Postgres and reused across same-company contacts.
- The workflow should not use the contact's personal city/state as a proxy for company geography.

### Emerald Company Sync Output Contract
- Target company-level fields:
  - `company_name`
  - `company_operating_state`
  - `company_operating_market_note`
  - `company_cannabis_marketing_signal`
  - `company_research_snippet`
  - `company_research_confidence`
  - `company_research_source`
- GHL contact delivery fields currently used for Email #4 support:
  - `Company Name for Emails`
  - `Em_Company_Operating_State`
  - `Em_Company_Research_Snippet`
  - `Em_Company_Market_Note`
  - `Em_Cannabis_Marketing_Signal`
  - `emerald_exec_sso_ai_research`
  - `Em_Email4_Personalization_Ready`
  - `Em_Email4_Personalization_Reason`

### Email #4 Personalization Rules
- Personalized Email #4 is allowed only when the record is actually usable for company/state-specific copy.
- `Em_Email4_Personalization_Ready = Yes` only when all required evidence is present:
  - research source is website-backed (`website+heuristic`)
  - `company_operating_state` is present
  - `company_research_snippet` is present
  - cannabis/marketing context is present enough to justify the copy
- If those conditions are not met, mark:
  - `Em_Email4_Personalization_Ready = No`
  - `Em_Email4_Personalization_Reason = <reason>`
- The fallback/generic Email #4 must be used whenever readiness is `No`.
- Do not send the personalized Email #4 just because research is marked done.

### Company Sync Runtime Rules
- `Needs Research?` should send only true website-research items to `OpenRouter Research`.
- `cache_only`, `deterministic_only`, and institutional skips should bypass `OpenRouter Research`.
- `OpenRouter Research` should stay `continueOnFail=true` with a short timeout, not 5-minute hangs.
- The local validator must preserve one output item per input item.
- Cached `website+heuristic` results must not be downgraded to `no_website_evidence` just because `evidencePages` is empty in a cache-only pass.
- Low-value/non-eligible rows must not broadly propagate the `done` marker across same-company contacts.

### Company Discovery and Skip Rules
- Academic/institutional-looking domains should not be skipped blindly.
- Before skipping an institutional record, check for stronger business/cannabis signals in:
  - `company_non_linkedin_urls`
  - `location_non_linkedin_urls`
  - LinkedIn URL fields
  - company/location naming text
- Social-platform domains should be treated like generic/non-company domains when deriving company keys.
- Discovery/link extraction should favor likely company/about/compliance/cannabis pages and include cannabis-related keyword variants such as:
  - `dispensary`
  - `cannabis`
  - `hemp`
  - `thc`
  - `cbd`
  - `cultivation`
  - `delivery`
  - `adult-use`
  - `medical cannabis`

### Emerald Reset / Backfill Notes
- Use targeted resets for bad cache rows rather than clearing the whole campaign blindly when possible.
- Helper script for temporary reset workflow creation:
  - `scripts/rerun_bad_emerald_sso_companies.py`
- Temporary live reset workflow for full Executive SSO company-sync reruns:
  - `TMP - Reset Emerald Executive SSO Company Sync Queue` (`v2eMeP05wjxqCTFe`)
  - manual trigger only, inactive by default
  - deletes matching `Emerald_Company_Research_Cache` rows and resets `Emerald_Contacts` sync/research fields back to pending for contacts tagged `seq emerald - executives sso`
- n8n execution note:
  - `n8n-lt` is reliable for verification
  - live execution sometimes requires temporarily setting `availableInMCP=true` through direct n8n REST, then reverting it after the run

## Reference Docs Convention
- Keep service reference files under `n8n/nodes/<service>/REFERENCE.md`.
- Reference files should map n8n node usage to concrete upstream API actions/endpoints where applicable.
- When native n8n node coverage is partial, document `HTTP Request` fallback endpoints explicitly.

## n8n Workflow Update Method (Canonical)
- Use `n8n-lt` first for:
  - workflow discovery
  - activation-state verification
  - checking whether a live edit actually persisted
- Treat `n8n-lt` as the read/verification source of truth, not always the most reliable mutation path.
- When workflow edits are small and MCP mutation works cleanly, use `n8n-lt`.
- When `n8n-lt` mutation helpers show transport/schema issues, ignore `active`, or fail to persist large edits, move immediately to the direct n8n REST API instead of repeatedly retrying MCP mutations.
- Direct n8n REST path verified live for this project:
  - base: `https://automations.livetransparent.com/api/v1`
  - auth header: `X-N8N-API-KEY`
  - update route: `PUT /workflows/{id}`
- Live `PUT /workflows/{id}` payload shape is strict:
  - accepted body fields are `name`, `nodes`, `connections`, and `settings`
  - `settings` can be passed as `{}` to preserve the server-side settings block
  - extra top-level fields or read-only fields are rejected
- On Windows, direct `curl.exe` to the n8n host can fail with `schannel` TLS errors; use Python `requests` for direct REST verification and update calls when that happens.
- Least-fragile direct update payload:
  - `name`
  - `nodes`
  - `connections`
  - `settings`
- n8n public API execution caveats verified on `2026-03-31`:
  - `POST /api/v1/workflows/{id}/run` returned `405`
  - `POST /api/v1/workflows/run` returned `405`
  - For one-off execution from Codex, the reliable path was:
    - set workflow `settings.availableInMCP = true`
    - execute through `n8n-lt.execute_workflow`
  - When updating `settings` through direct REST, the accepted minimal body was:
    - `{"callerPolicy":"workflowsFromSameOwner","availableInMCP":<bool>}`
  - Sending back extra settings keys from a read payload can be rejected with `request/body/settings must NOT have additional properties`.
 - Direct workflow update behavior re-verified on `2026-04-05` against n8n `2.14.2`:
   - `PUT /api/v1/workflows/{id}` still rejected the full read-back `settings` block with `request/body/settings must NOT have additional properties`.
   - The working mutation payload again had to reduce `settings` to the minimal accepted subset:
     - `callerPolicy`
     - `availableInMCP`
   - After a successful `PUT`, the API response body can report `active: true` even for a staged workflow that should remain inactive.
   - Do not trust the `PUT` response alone for workflow state.
   - Always follow direct workflow mutation with:
     - `GET /api/v1/workflows/{id}` to verify the saved nodes/code
     - explicit activate/deactivate correction if the workflow must remain staged
     - backup refresh if the local workflow JSON is intended to mirror live
- Avoid full-object writebacks unless required. Large payloads with extra workflow metadata are more likely to fail or drift.
- After every live mutation:
  - re-read the workflow through `n8n-lt`
  - verify `active`
  - verify `defaultDryRun` or equivalent runtime toggles
  - verify the exact changed node parameters/code
- For production webhook workflows:
  - patch code/config first
  - verify state second
  - only then disable dry-run and allow side effects
- For large code-node edits:
  - build the full code string locally
  - push one clean replacement
  - avoid many incremental MCP edits that can leave nodes or connections half-updated
- If a direct patch or workaround is important enough to repeat, save it under `scripts/` and document it in this file or a nearby runbook.

## Emerald SSO Company Sync (Current Learnings)
- Workflow: `LT - Emerald Executive SSO -> Company Sync (Staged)` (`GHVYyYmhfNiZ7bbN`)
- As of `2026-03-31`, important live behavior/rules:
  - `batchLimit` is `10`
  - `researchModel` is `google/gemini-2.5-flash`
  - `validatorModel` remains configured as `qwen/qwen-2.5-7b-instruct`
  - `OpenRouter Validate` is no longer on the runtime path; `Parse Research Response` now flows directly to `Finalize Company Sync`
  - `OpenRouter Research` timeout is `30000`
  - `Needs Research?` must route normalized `researchMode === website` items to `OpenRouter Research`, and all other modes directly to `Parse Research Response`
  - `Parse Research Response` now matches prep data by `company_domain_key` instead of relying on fragile `pairedItem` fallback indexing
  - `Fetch Executive SSO Candidates` should reference `{{$node["Config"].json.batchLimit}}` in the SQL `LIMIT`, not `$item(0)`
  - `defaultDryRun` is now `false` in the live Config node
  - non-research paths (`cache_only`, `deterministic_only`, `skip_institutional`) should bypass the LLM
- Cache quality rule:
  - do not trust `Emerald_Company_Research_Cache` rows with `company_research_source = no_website_evidence` as reusable personalization cache
  - reusable cache should effectively mean `website+heuristic` plus usable state/snippet or signal
- Website fetch implementation note:
  - in n8n Code nodes, use `$httpRequest` / `this.helpers.httpRequest` for site fetches
  - do not rely on global `fetch` for company-site scraping in this workflow
- Email #4 gating rule:
  - personalized Email #4 is only valid when `Em_Email4_Personalization_Ready = Yes`
  - otherwise the fallback generic Email #4 should be used
- Current GHL personalization fields used by this workflow:
  - `Company Name for Emails`
  - `Em_Company_Operating_State`
  - `Em_Company_Research_Snippet`
  - `Em_Company_Market_Note`
  - `Em_Cannabis_Marketing_Signal`
  - `Em_Email4_Personalization_Ready`
  - `Em_Email4_Personalization_Reason`
- Validation bug fixed on `2026-03-31`:
  - cached `website+heuristic` rows must not be downgraded to `no_website_evidence` just because `evidencePages` is empty on the current pass
- Website discovery optimization added on `2026-03-31`:
  - broader cannabis/business keywords are used for:
    - business override detection
    - candidate internal-page discovery
    - cannabis signal extraction
- Temporary targeted cache reset helper exists locally:
  - [scripts/rerun_bad_emerald_sso_companies.py](/C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/scripts/rerun_bad_emerald_sso_companies.py)
  - it was used to delete selected cache rows from `Emerald_Company_Research_Cache` and reset matching `Emerald_Contacts` rows back to `pending`

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

### Active Workflows (23 Total)

**Warm Intake Workflows (7):**
- n8n workflow `GHL Warm Intake - Add Intake Tag (Webhook)` (`OowP3sAd8c9paSKf`) - active.
- n8n workflow `GHL Warm Intake - Email Inbound Tag (Webhook)` (`SmMf8QIfysuxQJbG`) - active.
- n8n workflow `GHL Warm Intake - Email Outbound Tag (Webhook)` (`J4B0n0QeSeOeqAci`) - active.
- n8n workflow `GHL Warm Intake - SMS Tag (Webhook)` (`5nYzp9DgQUopzWhR`) - active.
- n8n workflow `GHL Warm Intake - Referral Tag (Webhook)` (`6lp8sIS3YMB1t9Ri`) - active.
- n8n workflow `Website Lead Intake from Hero form` (`RTV5jUiTt05lad07`) - active.
- n8n workflow `Website Lead Intake from Footer Form` (`RSfLF7LU0rDC4jAI`) - active.

**Apollo Enrichment Workflows (4):**
- n8n workflow `GHL Apollo Enrichment - Webhook Intake (Sheet First)` (`WmKAhG7mIaXonNsh`) - active.
- n8n workflow `GHL Apollo Enrichment - Phone Webhook Intake (Staged)` (`WuxgTa0EEL1mb2SA`) - active.
- n8n workflow `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`) - active.
- n8n workflow `GHL Apollo Phone Enrichment - Callback Handler` (`YaWizRnw7XmkcvZH`) - active (legacy, superseded by V4).

**Cold Outreach Workflows (3):**
- n8n workflow `LT - Cold Outreach CSV -> Postgres Ingest (Staged)` (`kVCTmy1m8fEyP6Q7`) - active.
- n8n workflow `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)` (`T28iLcm4Hszo19MG`) - active.
- n8n workflow `LT - Cold Outreach Sender Release Dispatcher (Staged)` (`NTpQnMrpjzusPXHX`) - active.

**Emerald Campaign Workflows (4):**
- n8n workflow `LT - Emerald Campaign Sender Release Dispatcher (Staged)` (`8UXlpoMJnQ229AuG`) - active.
- n8n workflow `LT - Emerald CSV -> Postgres Ingest (Staged)` (`mSegmpMUd0DRwFEx`) - inactive.
- n8n workflow `LT - Emerald CSV -> GHL Import (DryRun, Staged)` (`BLr1x1HKdgM1Xfxk`) - inactive.
- n8n workflow `LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged)` (`0jDKgG8VvmfyORQn`) - inactive (seeded 2026-03-27, 20165 rows).

**SimpleTexting Workflows (7):**
- n8n workflow `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) - inactive/staged. Canonical outbound SimpleTexting delivery adapter. Receives webhook payloads, resolves `templateKey`, sends via SimpleTexting, and can sync GHL notes/tags.
- n8n workflow `LT - SimpleTexting Inbound Reply (Webhook, Staged)` (`EhAiGey2o7UJT1cv`) - active, `defaultDryRun=false`. Handles inbound reply callbacks from SimpleTexting and writes back to GHL.
- n8n workflow `LT - SimpleTexting Delivery Events (Webhook, Staged)` (`AEi1VCzkLvaYFr4U`) - active, `defaultDryRun=false`. Handles delivery-status callbacks from SimpleTexting and is the right place to branch invalid-number remediation into Apollo phone enrichment.
- n8n workflow `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)` (`IyBKMkpYQ7pa0C8V`) - active, `defaultDryRun=false`. Handles unsubscribe callbacks and applies the stop-state back to GHL.
- n8n workflow `LT - SimpleTexting Warmup Dispatcher (Staged)` (`dZQLlbTLkpE1843X`) - archived. Legacy/experimental first-touch release dispatcher. Not part of the current planned six-message campaign architecture.
- n8n workflow `LT - SimpleTexting Pool Dispatcher (Staged)` (`usxYXSuc4ahw40V3`) - inactive/staged, `defaultDryRun=true`. Intended enrollment dispatcher for the current design. Pulls eligible contacts from the `Simpletexting Pool` search body, excludes contacts already stopped/in-progress/finished, writes enrollment state, and launches the sequencer.
- n8n workflow `LT - SimpleTexting Campaign Sequencer (Staged)` (`7mSiivR3NhtLIcNz`) - inactive/staged, `defaultDryRun=true`. Six-step n8n-owned drip sequencer. Re-fetches the contact and checks `simpletext_stop` before every send, waits between messages, and records campaign state/events in Postgres.
- Current architecture note:
  - keep `SMS Send`, `Inbound Reply`, `Delivery Events`, `Unsubscribe Events`, `Pool Dispatcher`, and `Campaign Sequencer`
  - keep `Warmup Dispatcher` archived unless the older first-touch warmup experiment is intentionally revived

**Slack Notification Workflows (3):**
- n8n workflow `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) - active.
- n8n workflow `WL - Webhook to Slack Channel - Website Visitor` (`8USvJkRlKzbj6Fu1`) - active.
- n8n workflow `WL - Webhook to Slack Channel - Form Submission` (`FQE90HDUilFVdASY`) - active.

**Other Workflows (2):**
- n8n workflow `rb2b leads` (`3kjsIUeoEQFx26cC`) - active. Webhook: `/webhook/rb2b_leads_v3`.
- n8n workflow `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)` (`MI91SutAbAj3QSXp`) - active.

### Documentation & References
- GHL direct API template retrieval pattern verified for this location:
- `GET https://services.leadconnectorhq.com/locations/Zwz4relUXVPxx8uohnjV/templates?type=sms&limit=20`
- Returned live SMS templates successfully with a valid PIT on `2026-03-17`.
- Plan doc: `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Training guide: `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
- Quick reference: `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
- GHL webhook sender checklist: `GHL Live Transparent CRM/GHL_Intake_Webhook_Sender_Automations_Checklist.md`
- AI agent process: `Website AI Chatbot/plans/AI_Agent_Knowledgebase_Setup_Process.md`
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
- Emerald import metadata:
- GHL source tags created for Emerald:
  - `emerald`
  - `cannabis-retail-mso-executive-1`
  - `cannabis-retail-mso-executive-2`
  - `cannabis-retail-mso-marketing-1`
  - `cannabis-retail-sso-executive-1`
  - `cannabis-retail-sso-executive-2`
  - `cannabis-retail-sso-marketing-1`
- Emerald custom field folder exists in GHL UI and holds the `Em_` preservation fields.
- Emerald-specific contact fields created:
  - `Em_Emerald_Contact_ID`
  - `Em_Roles`
  - `Em_Seniorities`
  - `Em_All_Known_Emails`
  - `Em_All_Known_Phones`
  - `Em_Contact_LinkedIn_URLs`
  - `Em_Contact_Non_LinkedIn_URLs`
  - `Em_Emerald_Location_IDs`
  - `Em_Location_Legal_Names`
  - `Em_Location_Display_Names`
  - `Em_Location_LinkedIn_URLs`
  - `Em_Location_Non_LinkedIn_URLs`
  - `Em_Ultimate_HQ_Names`
  - `Em_HQ_Names`
  - `Em_Company_LinkedIn_URLs`
  - `Em_Company_Non_LinkedIn_URLs`
  - `Em_Source_File`
- `Batch_Upload` is the canonical field for storing the original Emerald source CSV base name without `.csv`.
- Emerald campaign queue tags created:
  - `enrollment queue - emerald - executives mso`
  - `enrollment queue - emerald - executives sso`
  - `enrollment queue - emerald - marketing mso`
  - `enrollment queue - emerald - marketing sso`
- Emerald campaign enrolled/audit tags created:
  - `seq enrolled - emerald`
  - `seq emerald - executives mso`
  - `seq emerald - executives sso`
  - `seq emerald - marketing mso`
  - `seq emerald - marketing sso`

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
- Regulated ads booking handoff is now verified live:
  - source calendar `Regulated Ads On Social/Search`
  - normalized internal key can appear as `regulated-ads` or `regulated-ads-on-social-search`
  - GHL filtered booking automation posts to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`
  - n8n workflow `WL - Webhook to Slack Channel Update` sends Slack, adds `SQL`, and creates or moves the opportunity into `Sales -> Discovery Scheduled`
- `WL - Seq - Stop on Booked/Reply/Closed` was re-verified live on `2026-03-24`:
  - `Customer Booked Appointment` is now filtered to calendar `Regulated Ads On Social/Search`
  - `meeting booked` should only remain on contacts with either:
    - current regulated ads booking calendar `SrtXcFVyea7pFl3nTiIK`
    - legacy Cameron 30-minute booking calendar `a5VRVUAXQQQw5hV3Iqd3`
  - historical cleanup completed on `2026-03-24`: `58` invalid `meeting booked` tags removed; `3` valid contacts retained
- Other booking paths still require separate verification before assuming they should hand off into Sales.
- Verify active outreach/nurture sequence stop conditions at booked/closed states.
- Validate/test active n8n warm intake tag webhooks; set `defaultDryRun=false` (or pass `dryRun=false`) only when ready for live intake tag writes.
- Restart Codex/MCP session after updating `N8N_WEBHOOK_USERNAME` and `N8N_WEBHOOK_PASSWORD` in `~/.codex/config.toml` so `run_webhook` can execute authenticated tests.
- End-to-end booking-path validation is complete for the regulated ads flow; continue to treat unrelated booking paths as unverified until checked live.

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
- `https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK?utm_source=email&utm_medium=outreach&utm_campaign=wl_seq_cannabis_ads&utm_content=book_meeting`
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

## Session Notes (2026-03-08)
- `LT - Cold Outreach Sender Release Dispatcher (Staged)` (`NTpQnMrpjzusPXHX`) was updated and re-verified live.
- Dispatcher now enforces contact-local hour gating using:
  - explicit `contact_timezone` / `timezone` when valid
  - fallback mapping from full US state names and CA province names (plus code-based values)
- `Fetch Cold Candidates` now surfaces timezone candidates via:
  - `row_to_json(a)->>'timezone'`
  - `row_to_json(a)->>'contact_timezone'`
- Added throttling guard for GHL upserts:
  - `200ms` delay before each upsert call (`/contacts/upsert`)
- Retry behavior remains unchanged by design:
  - failed/deferred contacts are not written to `ColdOutreach_Release_Log`
  - they are retried on later dispatcher runs
- Execution validation snapshots:
  - `1371`: timezone resolution fixed (`deferredMissingTimezone=0`), `queued=77`, `error_upsert=11` (`429`)
  - `1415`: `queued=11`, `deferred_no_capacity=425`, `errors=0`, upsert attempts `0`
- n8n backup refresh completed:
  - `Backup of all n8n workflows/manifest.json` now reflects `21` live workflows with `0` failed exports.

## Session Notes (2026-03-10)
- n8n workflow `rb2b leads` (`3kjsIUeoEQFx26cC`) was implemented and stabilized for production.
- Webhook: `/webhook/rb2b_leads_v2`.
- Workflow behavior now includes:
  - GHL contact reconciliation by email first, then exact full-name fallback.
  - Contact update or upsert in GHL.
  - Tag append (non-destructive): `rb2b_website_visitor`, `mql`.
  - Postgres upsert into `RB2B_Leads` keyed by `lead_key`.
  - Follow-up task creation: `New RB2B contact - Call`, assigned to John.
- Runtime fixes applied during stabilization:
  - removed direct `$env` dependency in Code node (moved to Set `Config` node inputs).
  - switched HTTP helper to `$httpRequest`/`this.helpers.httpRequest` fallback pattern.
- corrected task node contact-id reference to avoid empty `/contacts//tasks` path.
- reconnected `Ensure RB2B Leads Table` so it is not orphaned in graph.

## Session Notes (2026-03-17)
- Direct GHL API fallback was verified for endpoints that were not reachable through `ghl_workflows` MCP.
- `ghl_official` MCP calls confirmed the PIT was valid.
- `ghl_workflows.GET_all_or_email_sms_templates` continued to return `401` / `The token is not authorized for this scope.` even with a valid PIT.
- Public docs lookup confirmed:
- endpoint: `GET /locations/:locationId/templates`
- required scope: `locations/templates.readonly`
- Direct API call with PIT succeeded and returned `6` live SMS templates for location `Zwz4relUXVPxx8uohnjV`.
- Current live SMS templates in GHL:
- `SMS 1 – Initial Outreach`
- `SMS 2 – Value + Soft Authority`
- `SMS 3 – Social Proof`
- `SMS 4 – Curiosity Hook`
- `SMS 5 – Dispensary Angle (if applicable)`
- `SMS 6 – Breakup Message`
- Reusable lesson:
- if `ghl_workflows` fails but the endpoint is documented and the PIT works elsewhere, test the endpoint directly against `https://services.leadconnectorhq.com` before assuming the token is invalid.
- PIT rotation / n8n workflow update work completed:
- Latest PIT standardized to `pit-8a0de81d-3555-4909-a8eb-afecd3794828`.
- Verified that several live n8n workflows had older PITs hardcoded in node parameters and code payloads.
- Updated live workflows to the latest PIT, including warm intake tagging, website intake, Apollo enrichment, MQL opportunity creation, and the cold outreach sender dispatcher.
- Repo-side workflow backups and generated artifacts were also bulk-updated so local snapshots match the latest PIT.
- Reliable direct n8n API path from this machine:
- use `X-N8N-API-KEY` header, not Bearer auth
- use `https://automations.livetransparent.com/api/v1`
- a Node `fetch` script with a browser-like `User-Agent` worked reliably when PowerShell `Invoke-RestMethod` / `curl.exe` hit local TLS or transport issues
- SimpleTexting live workflow status:
- Workflow `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) remains inactive/staged.
- It supports `templateKey`-driven sends in addition to raw `message` payloads.
- The send workflow now uses a dedicated shared secret for webhook auth and a separate `simpleTextingApiToken` field for the provider API key.
- `LT - SimpleTexting Inbound Reply (Webhook, Staged)` (`EhAiGey2o7UJT1cv`) path `lt-simpletexting-inbound-reply` is active/published and writes back to GHL.
- `LT - SimpleTexting Delivery Events (Webhook, Staged)` (`AEi1VCzkLvaYFr4U`) path `lt-simpletexting-delivery-events` is active/published and writes back to GHL.
- `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)` (`IyBKMkpYQ7pa0C8V`) path `lt-simpletexting-unsubscribes` is active/published and writes back to GHL.
- `LT - SimpleTexting Warmup Dispatcher (Staged)` (`dZQLlbTLkpE1843X`) is now archived and should be treated as retired legacy logic, not the current campaign path.
- `LT - SimpleTexting Pool Dispatcher (Staged)` (`usxYXSuc4ahw40V3`) and `LT - SimpleTexting Campaign Sequencer (Staged)` (`7mSiivR3NhtLIcNz`) were created on `2026-04-05` for the n8n-owned six-message SimpleTexting drip architecture and remain inactive/dry-run.

## Session Notes (2026-03-19)
- Regulated ads booking flow was validated with a real public booking on `Regulated Ads On Social/Search`.
- Source GHL workflow is a filtered booking automation that sends:
  - `POST https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`
- Runtime worker:
  - n8n workflow `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`)
- Live validation initially exposed a payload-shape bug:
  - GHL sent booking data under nested `calendar` fields
  - the workflow had been checking only flat fields
  - result was a false non-match until the normalization logic was corrected
- Current verified behavior for the regulated ads booking path:
  - Slack alert is sent to `#leads`
  - contact receives tag `SQL`
  - opportunity is moved to `Sales -> Discovery Scheduled`, or created there if missing
- Live validation artifacts:
  - historical test contact kept in GHL: `OMfr5JlM7HqQv1YUq5bn`
  - test opportunity kept in GHL: `6gt9SCmZkmoPPo5bfzlT`
  - test appointment deleted after validation to clear the slot: `xlSmtk8beDM4uUI1e24V`

## Session Notes (2026-03-24)
- Reviewed live GHL workflow `WL - Seq - Stop on Booked/Reply/Closed` in the builder.
- Confirmed `Customer Booked Appointment` is filtered to `Regulated Ads On Social/Search` rather than all calendars.
- Confirmed the workflow still adds tag `meeting booked` and removes contacts from sequence workflows.
- Audited all contacts carrying `meeting booked` against live appointment history.
- Canonical allowed booking calendars for retaining `meeting booked`:
  - current regulated ads calendar `SrtXcFVyea7pFl3nTiIK`
  - legacy Cameron 30-minute calendar `a5VRVUAXQQQw5hV3Iqd3`
- Audit result before cleanup:
  - `61` contacts had `meeting booked`
  - `3` had qualifying appointments
  - `58` were invalid and had the tag removed
- Post-cleanup live state:
  - `meeting booked` remains only on the `3` valid contacts
  - invalid historical tags from `Cameron-1on1-15mins`, `Interview-Presentation`, RB2B, Facebook, and cold outreach records were cleared

## Session Notes (2026-03-25)
- Emerald contact import process is now documented and repeatable:
  - generator: `Emerald Contacts/build_ghl_import.py`
  - runbook: `Emerald Contacts/README.md`
- Current Emerald merge process:
  - reads all source CSVs from `Emerald Contacts/`
  - maps standard GHL fields plus planned `Em_*` preservation fields
  - sets `Batch_Upload` to the original source CSV name without `.csv`
  - dedupes by email first, then name/company, then phone
  - suppresses unsafe shared phones from direct `Phone` import by moving them to `Corporate Phone`
- SimpleTexting callback productionization completed:
  - `LT - SimpleTexting Inbound Reply (Webhook, Staged)` (`EhAiGey2o7UJT1cv`)
  - `LT - SimpleTexting Delivery Events (Webhook, Staged)` (`AEi1VCzkLvaYFr4U`)
  - `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)` (`IyBKMkpYQ7pa0C8V`)
- All three callback workflows were verified active after user-side enablement.
- All three callback workflows were updated so `defaultDryRun=false` and re-verified live.
- Verified efficient live n8n workflow update path for this project:
  - `n8n-lt` is reliable for workflow discovery and readback verification
  - direct n8n REST `PUT /api/v1/workflows/{id}` with `X-N8N-API-KEY` is the reliable fallback when MCP activation/update helpers are inconsistent
- Direct patch payload that worked cleanly in production:
  - `name`
  - `nodes`
  - `connections`
  - `settings: {}`
- Operational lesson:
  - if MCP mutation calls ignore `active`, fail schema validation on large payloads, or do not persist edits, stop retrying them and switch to the direct REST update path, then verify through `n8n-lt`
- Additional Emerald setup completed:
  - reviewed all six source CSVs under `Emerald Contacts/`
  - created the Emerald source tags in GHL:
    - `emerald`
    - `cannabis-retail-mso-executive-1`
    - `cannabis-retail-mso-executive-2`
    - `cannabis-retail-mso-marketing-1`
    - `cannabis-retail-sso-executive-1`
    - `cannabis-retail-sso-executive-2`
    - `cannabis-retail-sso-marketing-1`
  - created Emerald-specific GHL custom fields prefixed `Em_` and placed them in the `Emerald` contact field folder
- Emerald workflow decision:
  - direct merged-CSV import into GHL is currently the preferred path for Emerald contacts
  - keep the Emerald staged n8n ingestion workflows available for Postgres use and as fallback import tooling
- Emerald staged n8n workflows created and verified saved inactive:
  - `LT - Emerald CSV -> Postgres Ingest (Staged)` (`mSegmpMUd0DRwFEx`)
    - webhook path: `/webhook/lt-emerald-postgres-intake`
    - target table: `Emerald_Contacts`
    - default behavior: `defaultDryRun=true`
  - `LT - Emerald CSV -> GHL Import (DryRun, Staged)` (`BLr1x1HKdgM1Xfxk`)
    - webhook path: `/webhook/lt-emerald-ghl-import`
    - default behavior: `defaultDryRun=true`
    - maps standard GHL fields plus the `Em_` fields and `Batch_Upload`
  - `LT - Emerald Campaign Sender Release Dispatcher (Staged)` (`8UXlpoMJnQ229AuG`)
    - default behavior: `defaultDryRun=true`
    - release log table: `Emerald_Release_Log`
    - queue routing now targets the 4 Emerald queue tags by bucket
    - sender cap ramp now `300/day` in week 1, `400/day` in week 2, `500/day` in week 3 and beyond
    - warmup start date set to `2026-03-27`

## Session Notes (2026-03-27)
- Emerald campaign workspace created:
  - `emerald-email-campaign/`
  - `emerald-email-campaign/Exported Emerald Contacts.csv`
  - `emerald-email-campaign/plan.md`
  - `emerald-email-campaign/dispatcher-plan.md`
  - `emerald-email-campaign/workflow-mapping.md`
- n8n access status:
  - `n8n-lt` is reachable at `https://automations.livetransparent.com/mcp-server/http`
  - working MCP flow: `POST initialize` followed by `tools/list` over streamable HTTP
  - the server accepts the bearer token from `N8N_MCP_ACCESS_TOKEN`
  - `GET /mcp-server/http` is not a valid health check and returns `404 Cannot GET /mcp-server/http`
  - Codex resource probes (`resources/list`, `resources/templates/list`) return `Method not found` because this server exposes tools, not generic MCP resources
  - direct n8n REST API with `X-N8N-API-KEY` is also working
  - local Windows `curl.exe` can fail here with `schannel` TLS errors; use Node fetch or another client for endpoint verification
  - manual launch of `@leonardsellem/n8n-mcp-server` succeeds when `npm_config_cache` points to repo-local `.npm-cache`
  - no `config.toml` change was required; the earlier failure mode was probe mismatch, not bad credentials
- Emerald dispatcher live-state check:
  - `LT - Emerald Campaign Sender Release Dispatcher (Staged)` (`8UXlpoMJnQ229AuG`) is published, active, and MCP-exposed
  - `execute_workflow` succeeded in dry-run mode with execution id `2843`
  - dry-run summary:
    - `windowOpen: true`
    - `windowLabel: Mon-Sat, 8:00 AM ET to 5:00 PM PT`
    - `sundayBlocked: false`
    - `currentEtHour: 17`
    - `currentPtHour: 14`
    - `candidates: 500`
    - `totalUnreleased: 16081`
    - `backlogBeyondBatch: 15581`
    - `planned: 500`
    - `queued: 0`
    - `deferred: 0`
    - `errors: 0`
  - warnings returned by the workflow:
    - `DRY_RUN_ACTIVE: no GHL writes or release log inserts are executed.`
    - `GHL_WORKFLOWS_STILL_REQUIRE_QUEUE_TAG_TRIGGER_WIRING.`
  - live dispatcher query was updated to interleave buckets instead of scanning `id ASC`, which prevented MSO starvation in the first 500-row batches
  - sender cap visibility is now explicit in `Config.sendersJson` and the live execution summary
  - with `candidateLimit` increased to `500` and later `1200`, the live `Only Queued` output showed all 4 buckets in rotation:
    - `executives_mso`
    - `executives_sso`
    - `marketing_mso`
    - `marketing_sso`
  - sample rows showed balanced sender rotation across the 4 configured aliases
  - no further workflow edits were required after the live validation
- Emerald GHL sequence workflow publication check:
  - `GET /workflows/?locationId=Zwz4relUXVPxx8uohnjV` returned the 4 Emerald workflows as `published`
  - live workflow IDs:
    - `a3f96d18-3cd1-4182-b08d-8e6bde6f77c1` - `WL - Seq - Cannabis Ads Emerald - Executives MSO`
    - `e7a4dd5b-c6da-459c-9c48-2d5ca2bc3421` - `WL - Seq - Cannabis Ads Emerald - Executives SSO`
    - `141d878e-7a27-43bc-97ab-c67c69b18f14` - `WL - Seq - Cannabis Ads Emerald - Marketing MSO`
    - `18eced4d-958a-49e4-9a23-899eabc94833` - `WL - Seq - Cannabis Ads Emerald - Marketing SSO`
  - direct `GET /workflow/:id` returned `401 Unauthorized` with the current PIT, so the direct API can confirm publish/state but not read the inner step graph
  - user-verified follow-up: all 4 automations are published, but enrollments remain at `0`, so the queue-tag trigger path still needs validation
- Emerald campaign tags created in GHL:
  - queue tags:
    - `enrollment queue - emerald - executives mso`
    - `enrollment queue - emerald - executives sso`
    - `enrollment queue - emerald - marketing mso`
    - `enrollment queue - emerald - marketing sso`
  - enrolled/audit tags:
    - `seq enrolled - emerald`
    - `seq emerald - executives mso`
    - `seq emerald - executives sso`
    - `seq emerald - marketing mso`
    - `seq emerald - marketing sso`
- Emerald campaign n8n implementation:
  - created `LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged)` (`0jDKgG8VvmfyORQn`)
    - webhook path: `/webhook/lt-emerald-campaign-postgres-intake`
    - target table: `Emerald_Campaign_Contacts`
    - default behavior: `defaultDryRun=true`
  - updated `LT - Emerald Sender Release Dispatcher (Staged)` (`8UXlpoMJnQ229AuG`) to `LT - Emerald Campaign Sender Release Dispatcher (Staged)`
    - active and MCP-exposed
    - source table now `Emerald_Campaign_Contacts`
    - queue routing now targets the 4 Emerald queue tags by bucket
    - sender cap ramp now `300/day` in week 1, `400/day` in week 2, `500/day` in week 3 and beyond
    - warmup start date set to `2026-03-27`
- Emerald campaign snapshot seeded into Postgres:
  - source file: `emerald-email-campaign/Exported Emerald Contacts.csv`
  - result: `20165` rows written into `Emerald_Campaign_Contacts`
  - snapshot ingest workflow was deactivated again after the seed run

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
- `300/day` per sender.
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

## Current Workflow Inventory (2026-03-31)

**Total Active Workflows:** 23

### Warm Intake Workflows (7)
- `OowP3sAd8c9paSKf` - GHL Warm Intake - Add Intake Tag (Webhook)
- `SmMf8QIfysuxQJbG` - GHL Warm Intake - Email Inbound Tag (Webhook)
- `J4B0n0QeSeOeqAci` - GHL Warm Intake - Email Outbound Tag (Webhook)
- `5nYzp9DgQUopzWhR` - GHL Warm Intake - SMS Tag (Webhook)
- `6lp8sIS3YMB1t9Ri` - GHL Warm Intake - Referral Tag (Webhook)
- `RTV5jUiTt05lad07` - Website Lead Intake from Hero form
- `RSfLF7LU0rDC4jAI` - Website Lead Intake from Footer Form

### Apollo Enrichment Workflows (4)
- `WmKAhG7mIaXonNsh` - GHL Apollo Enrichment - Webhook Intake (Sheet First)
- `WuxgTa0EEL1mb2SA` - GHL Apollo Enrichment - Phone Webhook Intake (Staged)
- `U7c6byTLXAMgcS75` - GHL Apollo Phone Enrichment - Callback Handler V4
- `YaWizRnw7XmkcvZH` - GHL Apollo Phone Enrichment - Callback Handler (legacy)

### Cold Outreach Workflows (3)
- `kVCTmy1m8fEyP6Q7` - LT - Cold Outreach CSV -> Postgres Ingest (Staged)
- `T28iLcm4Hszo19MG` - LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)
- `NTpQnMrpjzusPXHX` - LT - Cold Outreach Sender Release Dispatcher (Staged)

### Emerald Campaign Workflows (4)
- `8UXlpoMJnQ229AuG` - LT - Emerald Campaign Sender Release Dispatcher (Staged) - **ACTIVE**
- `mSegmpMUd0DRwFEx` - LT - Emerald CSV -> Postgres Ingest (Staged) - inactive
- `BLr1x1HKdgM1Xfxk` - LT - Emerald CSV -> GHL Import (DryRun, Staged) - inactive
- `0jDKgG8VvmfyORQn` - LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) - inactive (seeded)

### SimpleTexting Workflows (7)
- `Q3Ivnwe4z2Y3cD7A` - LT - SimpleTexting SMS Send (Webhook, Staged) - outbound delivery adapter; keep inactive until message copy and campaign wiring are final
- `EhAiGey2o7UJT1cv` - LT - SimpleTexting Inbound Reply (Webhook, Staged) - published callback handler for inbound replies
- `AEi1VCzkLvaYFr4U` - LT - SimpleTexting Delivery Events (Webhook, Staged) - published callback handler for delivery events and delivery-failure branching
- `IyBKMkpYQ7pa0C8V` - LT - SimpleTexting Unsubscribe Events (Webhook, Staged) - published callback handler for unsubscribes
- `dZQLlbTLkpE1843X` - LT - SimpleTexting Warmup Dispatcher (Staged) - archived legacy/experimental first-touch dispatcher; not part of the current six-step campaign design
- `usxYXSuc4ahw40V3` - LT - SimpleTexting Pool Dispatcher (Staged) - staged enrollment dispatcher for the current n8n-owned campaign design
- `7mSiivR3NhtLIcNz` - LT - SimpleTexting Campaign Sequencer (Staged) - staged six-message sequencer with stop check before every send

### Slack Notification Workflows (3)
- `lQTW0QPwBcf3o7j8` - WL - Webhook to Slack Channel Update
- `8USvJkRlKzbj6Fu1` - WL - Webhook to Slack Channel - Website Visitor
- `FQE90HDUilFVdASY` - WL - Webhook to Slack Channel - Form Submission

### Other Workflows (2)
- `3kjsIUeoEQFx26cC` - rb2b leads
- `MI91SutAbAj3QSXp` - GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)

### Inactive/Staged Workflows
- `Q3Ivnwe4z2Y3cD7A` - LT - SimpleTexting SMS Send (Webhook, Staged) - inactive/staged
- `usxYXSuc4ahw40V3` - LT - SimpleTexting Pool Dispatcher (Staged) - inactive/staged
- `7mSiivR3NhtLIcNz` - LT - SimpleTexting Campaign Sequencer (Staged) - inactive/staged

### Archived Workflows
- `dZQLlbTLkpE1843X` - LT - SimpleTexting Warmup Dispatcher (Staged) - archived legacy workflow

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
- Current production target/version: `2.14.2`.
- Repo deploy definition currently pins [`n8n/docker-compose.yml`](/C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/n8n/docker-compose.yml) to `n8nio/n8n:2.14.2`.
- Previous deployed version before this upgrade: `2.9.4`.
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

