# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), **DAN email campaign** (backfilled ghl_contact_id 2026-07-13, 5,373 eligible for dispatch), **Apollo phone enrichment** (repaired 2026-07-14, new polling workflow), voice, reporting, LinkedIn outreach (canonical sender path and suppression guardrails hardened), the **LinkedIn/Instagram via Unipile -> GHL bidirectional conversation provider integration**, and the SimpleTexting SMS campaign stack (dispatcher live at low volume as of 2026-07-18).
- Social provider integration handoff: [docs/strategy/unipile-ghl-bidirectional-integration.md](./docs/strategy/unipile-ghl-bidirectional-integration.md)
- SimpleTexting provider handoff is now LIVE (2026-07-20). GHL app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). `/webhook/lt-simpletexting-provider-outbound` routes GHL outbound replies through idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Outbound campaign sends mirror into GHL Conversations. `simpletexting_conversation_map` table live. Full E.164 migration across delivery/unsubscribe workflows and STOP tag guard in outbound router are deferred.

## Vapi Campaign Rollout

### GHL Tag IDs

| Tag | ID |
|-----|----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Active 2026-07-14

Both workflows published and running:
- **Intake Poller** (bYk1Ai6MJLyhTsDZ): Active, every 10 min, 30 contacts/cycle, tag rotation across all 4 pools (vapi_campaign_brand, vapi_campaign_dispensary, brands_pool, dispensaries_pool).
- **Outbound Dialer** (r7UjWLndmc6EqEUW): Active, `*/2 13-22 UTC Mon-Fri`. Places calls via Vapi using campaign-specific assistants (Alex for brand, Jordan for dispensary). ET-forward schedule: starts 9am ET.

### Remaining Operational Items

- App reinstalled in Live Transparent with canonical SMS-type additional custom providers: LinkedIn `6a58a14ff3023bea3783c152`, Instagram `6a58a1193cdfc36997580a68`.
- Instagram GHL UI outbound reply and direct router smoke test both route to Unipile. Post-merge map repair points Instagram and LinkedIn social chats to canonical contact `XZ4yChllGBdcsVxhFRDe`.
- LinkedIn inbound under provider `6a58a14ff3023bea3783c152` is verified end-to-end; optional next check is a controlled LinkedIn GHL UI outbound reply from conversation `Ze8o3KbsrwuAXQ3KK5ge`.
- Register/confirm Unipile Instagram inbound webhook points to `https://automations.livetransparent.com/webhook/lt-unipile-instagram-new-messages`.
- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Monitor the next real Instagram inbound after GHL duplicate cleanup; map rows are repaired, but avoid further artificial inbound replays unless needed because they create visible conversation messages.
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL.
- Monitor the live SimpleTexting SMS dispatcher after launch: `sms_drip`, `candidateLimit=10`, `defaultDryRun=false`, weekdays `10:15am` and `3:00pm` ET, 2-day inter-step delay, reply/STOP suppression.
- SimpleTexting GHL Conversations provider is LIVE: `SimpleTexting SMS` (`6a5b91913953360948dd59f1`) routes GHL outbound replies through the outbound router (`f4VoO1lBWkYRcQai`) → idempotent send → SimpleTexting. Inbound posts to both Slack and GHL Conversations. Outbound campaign sends mirror into GHL Conversations via `Q3Ivnwe4z2Y3cD7A`. Remaining: full E.164 normalization across delivery/unsubscribe workflows, STOP tag guard in outbound router.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state sync after the fail-closed patch.

### Completed

- **2026-07-20**: SimpleTexting GHL Conversations bidirectional provider is LIVE. Separate `LiveTransparent SimpleTexting SMS` GHL app with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Built `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) at `/webhook/lt-simpletexting-provider-outbound` — validates provider, E.164-normalizes phone, routes through idempotent send to SimpleTexting. Patched `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`) to post inbound messages to GHL Conversations under `SimpleTexting SMS` with `type: "Custom"` + `conversationProviderId` (Slack alert preserved). Patched `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) to mirror outbound campaign sends into GHL Conversations. Created `simpletexting_conversation_map` table in Postgres. First end-to-end test passed: GHL → outbound router → idempotent send → SimpleTexting (201, message `6a5e46218ebb0860da623b0f`). Remaining: full E.164 normalization across delivery/unsubscribe workflows.
- **2026-07-16**: Verified the GHL Custom Conversation Provider bridge for Instagram and LinkedIn via Unipile using canonical SMS-type custom providers. Inbound uses `type: "Custom"` + `conversationProviderId` + `altId` with no dummy phone/email fields. `LT - Instagram Unipile New Messages` and `LT - LinkedIn Unipile New Messages` are active and published; LinkedIn replay verified `TYPE_CUSTOM_PROVIDER_SMS` on contact `XZ4yChllGBdcsVxhFRDe`, conversation `Ze8o3KbsrwuAXQ3KK5ge`. GHL duplicate cleanup consolidated Edmundo Cadorniga to `XZ4yChllGBdcsVxhFRDe`; Instagram map row `1` and LinkedIn map row `2` were repointed there. Direct outbound router checks passed for Instagram and LinkedIn. Full handoff in `docs/strategy/unipile-ghl-bidirectional-integration.md`.
- **2026-07-16**: Cleaned up duplicate LinkedIn sender paths. Traced malformed LinkedIn screenshot DMs to misconfigured `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`), which used the LinkedIn Unipile account ID and `instagram_dm_state`; unpublished it. Also unpublished redundant `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`). Production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.
- **2026-07-15**: Built and published automated LinkedIn DM suppression workflow (`LT - LinkedIn DM Suppression from GHL Tag`, IPN8jnR3XSurX0o1). GHL tag `stop_linkedin_dms` triggers a GHL automation → POSTs to `/webhook/lt-linkedin-suppress-dms` → resolves LinkedIn profile via Unipile, tags `linkedin_dm_sequence_completed`, upserts `linkedin_connection_state` to terminal for both real contact and synthetic `linkedin:follower:{providerId}`. Full audit confirmed all 3 send paths (DM Sequence, Follower DM, Dispatcher) correctly block suppressed contacts. Fixed dispatcher Feeder gap: added `linkedin_dm_sequence_completed` to blocking tag list.
- **2026-07-15**: Unicode/mojibake encoding fix expanded across all audited Unipile message sender nodes: LinkedIn DM Sequence (`Sync Connected from Unipile`, `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. Templates are pre-sanitized at runtime and final outbound text is sanitized immediately before Unipile API calls. Handles smart punctuation plus already-garbled forms like `canâ€™t` / `canΓÇÖt`. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.
- **2026-07-14**: Vapi voice system activated. Published Intake Poller + Outbound Dialer. Fixed Trigger Apollo Enrichment auth and Remove Tag - Enriching URL. Added pagination, 30-contact cap, brands_pool/dispensaries_pool tag search, and tag rotation. Added state-to-timezone inference for both poller and dialer. Shifted dialer cron to `*/2 13-22` UTC for 9am ET start; widened business hours guard to 8-18 CT.
- **2026-07-14**: Apollo phone enrichment repaired. Created and published LT - Apollo Phone Enrichment Polling (JH8ShfpglWmLMZ3l, every 30 min). Replaces dead webhook-based pipeline. Syncs profile data immediately, requests phone numbers via async callback to V4 handler.
- **2026-07-13**: Backfilled 13,705 ghl_contact_id values into emerging_pool_contacts from GHL export CSVs (email + phone + name/company match). DAN dispatcher now has 5,373 eligible contacts.

- **2026-07-20 - Voice Assistant Optimization (all 3 outbound assistants + dialer)**:
  - **Jordan (Dispensary, 056f2e50)**: 8 system prompt fixes + 2 config fixes from live call audit. Removed compliance disclosure from firstMessage (voicemail fix). Fixed {{contact_name}}->{{first_name}} (n8n passes first_name not contact_name). Removed unmet {{market}} variable. Changed "with"->"from" Transparent eCom (Nico TTS inserted "a"). Discovery questions restructured to one-at-a-time with numbered Q1-Q4 + WAIT instructions. Added [IVR vs Voicemail Detection] disambiguation section. Tightened "um/uh" to once per call max. Added [Pronunciation] rules: "Point of Sale" not "POS", "from" not "with". Expanded [No Stage Directions] to ban throat-clearing/coughing/sighing. [Turn-Taking] strengthened to CRITICAL with self-check. Transcriber smartFormat enabled. Model tested Llama 3.3 70B then reverted to Claude 3 Haiku (system prompt preserved through model swap).
  - **Alex (Brand, 1d7c5d42)**: Same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and {{contact_name}}->{{first_name}} fixes. Brand-specific questions preserved.
  - **Savannah (V1 Outbound, 3f9bbfd2)**: Same IVR/voicemail disambiguation, stage directions, and {{contact_name}}->{{first_name}} fixes. First message already clean.
  - **Outbound Dialer (r7UjWLndmc6EqEUW)**: Stuck contact AX3wfQNpRwm6DG0HgUE2 (deleted from GHL, 2 entries in voice_call_queue) blocked every run since 18:38 UTC. HTTP - Get GHL Contact had neverError: false - 400 crashed run before lock release. Same contact re-picked every 2 min. Fix: neverError: true on lookup node; onError: continueRegularOutput on GHL - Create Call Note. Calls resumed by 18:50 UTC. Intake poller unaffected throughout.