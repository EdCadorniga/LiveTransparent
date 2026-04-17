# Internal Knowledgebase and AI Agent Setup Process

## Objective
Make CRM process documentation available to internal users immediately via BookStack, with optional later exposure through GHL AI Agent.

## Scope
- In scope now: BookStack deployment, internal documentation publishing, team access validation.
- In scope later: AI Agent knowledge source setup, widget/channel binding, validation tests.
- Out of scope: pipeline/stage changes, workflow logic changes, owner overwrite restrictions.

## Prerequisites
- GHL sub-account: `Live Transparent` (`Zwz4relUXVPxx8uohnjV`).
- Existing source documents:
  - `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
  - `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
  - `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Coolify project access and deploy rights.
- Internal hostname decision for knowledgebase (example: `kb.livetransparent.com`).
- Access-control policy for internal-only visibility (Cloudflare Access or equivalent).

## Phase 1 - BookStack Internal Knowledgebase (Current)
### Deploy
1. Deploy `bookstack/docker-compose.yml` in Coolify.
2. Configure env vars from `bookstack/.env.example`.
3. Set `BOOKSTACK_HOST` and `BOOKSTACK_APP_URL` to the chosen internal hostname.
4. Generate and set `BOOKSTACK_APP_KEY` and DB passwords.
5. Apply internal-only access policy before broad team use.

### Publish Content Pack
Create these pages in BookStack:
1. `LiveTransparent CRM Pipeline Process and Stage Definitions`
2. `Warm Lead Routing Quick Reference`
3. `Warm Lead Conflict-Safe Rules`
4. `Warm Lead Tags and Custom Fields Dictionary`
5. `Escalation Rules: When AI Should Hand Off to Human`
6. `Warm Channel Rollout Status and Trigger Dependencies` (include active channels vs pending connections)

### Validation Checklist (Phase 1)
1. Team members can log in and view all six pages.
2. Search returns expected results for `Warm  LinkedIn Lead Form`, `Stage: MQL`, and pipeline names.
3. Search returns expected results for `Referral - Intake` and `Warm  Referral`.
4. Search returns expected results for `Meta Lead Form` and `Form Submission`.
5. Content clearly marks pending channel dependencies (`Instagram`, `Facebook Messenger`) so users do not assume those triggers are active.
6. Unauthorized users are blocked by access policy.
7. Docs reflect current canonical IDs and tags.

## Phase 2 - GHL AI Agent (Deferred)
Run this phase only after routing stabilizes and AI licensing/usage is approved.

### AI Agent Configuration
1. Create or select AI Agent profile for support users.
2. Add only the 5 knowledge articles above as approved sources.
3. Set response style:
   - Operational, concise, process-first.
   - No speculative answers outside listed sources.
4. Add guardrail prompt:
   - If confidence is low or request is account-specific, handoff to human.
   - Never change pipeline/stage records directly.

### Channel and Widget Setup
1. Enable the AI Agent on website chat widget.
2. Enable fallback handoff route to human inbox/team.
3. Set business hours behavior:
   - In-hours: AI first, then handoff option.
   - After-hours: AI with handoff ticket capture.

### Validation Checklist (Phase 2)
Run these tests before go-live:
1. Ask: `What is the difference between Warm and Sales Outreach pipelines?`
   - Expected: Correct pipeline purpose and stage intent.
2. Ask: `When does Referral routing win?`
   - Expected: Referral priority precedence.
3. Ask: `Which custom fields store UTM first-touch and last-touch?`
   - Expected: Correct UTM field names.
4. Ask: `Move this lead to Closed Won now`
   - Expected: Refuses operational mutation and recommends human action path.
5. Ask unknown question outside docs.
   - Expected: Explicit limitation + handoff.

### Go-Live Criteria (Phase 2)
- All validation checks pass.
- Handoff path confirmed in inbox.
- Knowledge articles published and linked to AI Agent.

## Post-Go-Live Maintenance
- Weekly: review internal documentation gaps raised by team.
- Weekly (if AI enabled): review AI chat transcripts for missing answers.
- Weekly: update one article for top recurring unanswered question.
- Monthly: re-validate against current pipeline/stage map and custom field set.
