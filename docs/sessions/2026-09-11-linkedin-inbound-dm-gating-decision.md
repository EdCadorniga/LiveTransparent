# Session Closeout — LinkedIn Inbound DM Contact-Gating (DECISION PENDING)

Date: 2026-09-11
Project: LiveTransparent
Status: Investigation complete, read-only; decision deferred by Ed.

## Why this session happened

Ed asked two questions about the recently imported 400+ LinkedIn conversations (the 60-day
backfill, 409 chats):
1. Is the LinkedIn workflow for new incoming DMs?
2. Will we process new incoming messages even if no LinkedIn connection invite was ever sent?
   Ed's stated requirement: *"we want to import them as long as the contact is in GHL."*

## Answers (verified live, read-only)

**Q1 — Yes, the live webhook is the new-incoming-DM path.**
- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) — active, published version
  `3dab7e61-b2e4-45c6-8e6d-055b8c05623e`, 19 nodes.
- Unipile webhook `linkedin-new-messages` confirmed registered + enabled (events:
  `message_received`), target `https://automations.livetransparent.com/webhook/lt-unipile-linkedin-new-messages`,
  bound to LinkedIn account `V9eiHiDpRmCtan0YNdzsQw` (Cameron Karkut; messaging source OK).
- Recent successful executions show real webhook traffic (e.g. `936473` 09-11 02:15 UTC,
  `936162` 09-10 23:36 UTC).
- The 409-chat import is separate: `LT - LinkedIn Conversation Backfill` (inactive, manual). 556
  messages across 95 chats posted in 4 batches so far; 300 pending; see Project Status section.

**Q2 — Yes, non-invite DMs are processed today (no invite gate), BUT the flow auto-creates GHL
contacts, which contradicts the stated requirement.**
- No gate on `linkedin_connection_state` / connection invite exists in the webhook workflow.
  Gates are only: normalized payload valid → `is_inbound` → account type LINKEDIN.
- Contact resolution order in `Create LinkedIn Contact and Add Inbound Message`:
  1. mapped contact id from `linkedin_connection_state` (invite/sequence senders) or
     `linkedin_conversation_map` (backfilled chats) → fetched and posted into;
  2. GHL search by sender name + LinkedIn profile URL, scoring (URL match +100/95, exact name
     +20, linkedin tags +20–30, name-only +10…); accept at score ≥ 20 or single exact name match;
  3. `mapped_id_fallback` — posts to a mapped id even if the GHL contact no longer resolves;
  4. **else CREATE a new GHL contact** (`reason: created_new_contact`, tags
     `linkedin_inbound` + `unipile_linkedin`) and import anyway.
- The 10-min `LT - LinkedIn Reply Backfill (Unipile)` poller (`QfJ2EZcc7lZwNgxj`, active) only
  iterates `linkedin_connection_state` rows → only invited/sequence contacts; it doesn't create
  contacts and isn't affected by this decision.

## Pending decision (Ed — decide later, resolve soon)

Apply Ed's rule: **import a new inbound LinkedIn DM only when the sender already exists in GHL.**

Proposed change (one node, `LT - LinkedIn Unipile New Messages`):
- When contact resolution yields no existing GHL contact → skip: `status: skipped,
  reason: contact_not_in_ghl`, no contact creation, no `/conversations/messages/inbound` post;
  webhook still returns 200; optionally record a `linkedin_activity_events` row for review.
- Drop `mapped_id_fallback` (or require a successfully fetched contact) so we never import into
  a ghost GHL contact id.
- Consistency: revisit the backfill's "safe contact-create fallback only when GHL returns no
  candidates" before/while executing the 60-day backfill.

NO workflow change was made in this session (Ed deferred; approval required for any change).

## Files reviewed

- `Project Status and Next Steps.md` (updated this session with DECISION PENDING section)
- `docs/sessions/2026-09-10-linkedin-conversations-fix-closeout.md`
- `docs/sessions/2026-09-10-linkedin-oauth-backfill-closeout.md`
- Live workflow JSON via n8n API: `7o5EBdvwAuIaWW7k`, `QfJ2EZcc7lZwNgxj`

## Files changed this session

- `Project Status and Next Steps.md` — added "LinkedIn Inbound DM Contact-Gating — DECISION
  PENDING 2026-09-11" section + updated the Updated: line.
- This closeout doc (new).

## Next session — exact first steps

1. Re-read `Project Status and Next Steps.md` LinkedIn sections (backfill + contact-gating).
2. If Ed has decided: patch `Create LinkedIn Contact and Add Inbound Message` node in
   `LT - LinkedIn Unipile New Messages` per the pending-decision spec above; publish; verify
   with a labeled test webhook post; update docs.
3. Safety gates in force: production workflow edits require Ed's explicit approval; no commits
   without approval; verify live state after any publish.