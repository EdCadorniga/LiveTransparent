# AI Agent Knowledgebase Setup Process

## Objective
Make the CRM process documentation available to users through a GHL Chat Widget + AI Agent knowledgebase.

## Scope
- In scope: knowledge article preparation, AI Agent knowledge source setup, widget/channel binding, validation tests.
- Out of scope: pipeline/stage changes, workflow logic changes, owner overwrite restrictions.

## Prerequisites
- GHL sub-account: `Live Transparent` (`Zwz4relUXVPxx8uohnjV`).
- Existing source documents:
  - `GHL Live Transparent CRM/Pipeline_Process_Training_Guide.md`
  - `GHL Live Transparent CRM/Pipeline_Quick_Reference.md`
  - `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`
- Admin access in GHL for:
  - Sites/Knowledge Base (or equivalent article area)
  - Conversations AI / AI Agent configuration
  - Chat Widget placement/channel settings
- Public-facing page(s) where widget will be available.

## Knowledgebase Content Pack
Create these article titles in GHL knowledge articles:
1. `LiveTransparent CRM Pipeline Process and Stage Definitions`
2. `Warm Lead Routing Quick Reference`
3. `Warm Lead Conflict-Safe Rules`
4. `Warm Lead Tags and Custom Fields Dictionary`
5. `Escalation Rules: When AI Should Hand Off to Human`

## AI Agent Configuration
1. Create or select AI Agent profile for support users.
2. Add only the 5 knowledge articles above as approved sources.
3. Set response style:
   - Operational, concise, process-first.
   - No speculative answers outside listed sources.
4. Add guardrail prompt:
   - If confidence is low or request is account-specific, handoff to human.
   - Never change pipeline/stage records directly.

## Channel and Widget Setup
1. Enable the AI Agent on website chat widget.
2. Enable fallback handoff route to human inbox/team.
3. Set business hours behavior:
   - In-hours: AI first, then handoff option.
   - After-hours: AI with handoff ticket capture.

## Validation Checklist
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

## Go-Live Criteria
- All validation checks pass.
- Handoff path confirmed in inbox.
- Knowledge articles published and linked to AI Agent.

## Post-Go-Live Maintenance
- Weekly: review AI chat transcripts for missing answers.
- Weekly: update one article for top recurring unanswered question.
- Monthly: re-validate against current pipeline/stage map and custom field set.
