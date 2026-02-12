# LiveTransparent Agent Notes

## Project Context
- This project is deployed on a VPS using Coolify.
- There are currently two separate containers managed in Coolify.
- Those containers can reach each other over Coolify's internal/local network.
- `n8n` is publicly routed at `https://automations.livetransparent.com` (Cloudflare proxied to `89.117.21.29`).

## Working Assumptions
- Prefer internal service-to-service communication over the Coolify network where possible.
- Use `automations.livetransparent.com` as the canonical n8n public host for webhook/editor URLs.
- Keep config values centralized in service `.env` files so future domain cutovers are small changes.

## Agent Tooling
- This environment has MCP access to the `n8n` instance via the `n8n-lt` MCP server entry in Codex config.
- When workflow state or runtime behavior is relevant, use the `n8n-lt` MCP tools to verify actual instance state instead of guessing from local files.

## Paths and Layout
- Keep Docker and service-specific assets under their service folders (for example, `n8n/` and `postgres/`).
- Place service docs close to the service they describe.

## File Map
- `AGENTS.md`: Agent rules and project operating notes.
- `.env`: Root/shared environment values (non-service-specific).
- `n8n/docker-compose.yml`: n8n service definition, environment wiring, and Traefik labels.
- `n8n/.env`: n8n runtime secrets and host/webhook/editor URL environment values.
- `n8n/nodes/apollo/REFERENCE.md`: Apollo node/API reference map used in this repo.
- `n8n/nodes/ghl/REFERENCE.md`: GHL node/API reference map used in this repo.
- `n8n/nodes/twilio/REFERENCE.md`: Twilio node/API reference map used in this repo.
- `postgres/docker-compose.yml`: Postgres service definition for the stack.

## Reference Docs Convention
- Keep service reference files under `n8n/nodes/<service>/REFERENCE.md`.
- Reference files should map n8n node usage to concrete upstream API actions/endpoints where applicable.
- When native n8n node coverage is partial, document `HTTP Request` fallback endpoints explicitly.

## Locked GHL Map (Canonical)
- Location: `Live Transparent` (`Zwz4relUXVPxx8uohnjV`)
- Locked on: `2026-02-12`

### Pipelines and Stages
- `Warm` pipeline: `FRjpDZ1HWj3UPgczsu3t`
- `New`: `b961de1f-34fd-4b66-b032-f21225654868`
- `Qualified (MQL)`: `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2`
- `Routed to Outreach`: `477c0b59-4a64-4566-81d6-63e233362520`
- `Nurture Active`: `98775f02-0018-4629-9e69-0b1fcab293eb`
- `Disqualified`: `dae2ddc5-a031-4ffa-bcdb-79d5c9afe91b`

- `Sales Outreach` pipeline: `dhdlf3O4tymxFtHk4aqq`
- `New`: `3529dd3d-cab0-4279-967c-1aea203de4fb`
- `Attempting Contact`: `b97e42b1-b4c2-4759-8212-33596a085cf2`
- `Engaged`: `9ced8010-dfd7-4d5b-aa9c-c2eb58fca94d`
- `Meeting Requested`: `1ab47457-c945-4d16-9dd7-305583823114`
- `Booked`: `1f95dd0a-1cf2-4d31-abad-825d97d3ef69`
- `Unresponsive`: `23276991-fbb3-4b0f-8d65-35c737b62bdd`

- `Sales` pipeline: `MThKauqlvnEFuFmAkyWX`
- `Discovery Scheduled`: `6f5aa304-a190-40da-8556-7c65bbc52733`
- `Discovery Completed`: `facd3d31-c634-40c5-9271-17d608b4379c`
- `Proposal Sent`: `42b12e59-9b51-4c82-b597-4a9c972322c9`
- `Negotiation`: `f9022c83-7791-45c9-903d-381668454b2f`
- `Closed Won`: `f6b65baa-eac8-4f02-b91e-2ab0c8841b2d`
- `Closed Lost`: `d7784617-96f4-4ae4-8b3e-e2088b62627d`

## Current Execution Plan (Active)
1. Keep pipelines/stages as locked above; all automation must reference IDs, not names.
2. Build/maintain channel micro-automations in GHL:
- Trigger per source.
- Only apply warm tag + source metadata.
- Do not move pipeline/stage in micro-automations.
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
6. Build channel micro-automations in GHL UI (next):
- One micro-workflow per channel/source trigger.
- Apply exact `Warm  ...` tag only.
- Set source metadata fields only.
7. Publish knowledge docs to GHL AI Agent chatbot after routing stabilizes.
8. Setup Chatbot with AI Agent to make knowledgebase available to users (deferred until routing tests pass).

## Existing Setup Artifacts
- n8n workflow `GHL Warm Lead Setup - Fields and Tags`: `BYvEuUMUQFlXoxRj`
- n8n workflow `GHL Warm Pipelines - Validate and Map IDs`: `v3oYLcD3pzVr8l2O`
- n8n workflow `GHL Warm Lead Setup - UTM and Routing Fields`: `21yw9WflGkFISbQD`
- n8n workflow `GHL Warm Lead Fields - Duplicate Cleanup`: `6lVyZHKyZRYbVomd`
- n8n workflow `WF - Warm Channel Micro Entry`: `LaXTCx5689lVaFIj` (inactive, dryRun=true)
- n8n workflow `WF - Master Warm Intake and Routing`: `y3O34qp0O6hzD79x` (inactive, dryRun=true)
- Plan doc: `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Training guide: `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
- Quick reference: `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
- AI agent process: `GHL Live Transparent CRM/AI_Agent_Knowledgebase_Setup_Process.md`

## Contact Field Status (Current)
- Warm fields: complete.
- UTM first/last-touch fields: complete.
- LT routing metadata fields: complete.
- Duplicate UTM/LT fields were created during initial run and cleaned up; one canonical field per name now exists.
- `Warm Date` remains `DATE` by design for now (accepted; no Date/Time migration currently planned).

## Workflow Status (Current)
- GHL workflow `WL - Master Warm Intake and Routing`: `970cd6cb-dc37-4a17-8a79-62252623c371`
- Branch routing and branch field updates are configured.
- Channel micro-automations are pending build in GHL UI.
- End-to-end tests are pending (no production contacts yet).

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
- Assume latest stable n8n unless specified.
- Before using any node, operation, or parameter, VERIFY no newer version/schema exists.
  - If verification is not possible, STOP and ask for n8n version and node details.
- Use ONLY current native nodes and parameters.
- Never use deprecated/legacy nodes or invent options.
- Prefer native nodes over Function/Code unless unavoidable.
- Use current expression syntax ($json, $items(), $node[]).

### OUTPUT
- Be concise and task-focused.
- Output code first when requested.
- No explanations unless asked.

Failure to follow these rules is incorrect.
