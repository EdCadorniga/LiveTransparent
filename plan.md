# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), **DAN email campaign** (backfilled ghl_contact_id 2026-07-13, 5,373 eligible for dispatch), **Apollo phone enrichment** (repaired 2026-07-14, new polling workflow), voice, reporting, LinkedIn outreach (guardrails hardened; completion tagging added; monitoring), Instagram outreach, and the upcoming SimpleTexting SMS campaign.

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

- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL.
- Deploy staged SimpleTexting SMS workflows.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
- Monitor LinkedIn outbound guardrails, completion tagging, and reply-state sync after the fail-closed patch.

### Completed

- **2026-07-16**: Cleaned up duplicate LinkedIn sender paths. Traced malformed LinkedIn screenshot DMs to misconfigured `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`), which used the LinkedIn Unipile account ID and `instagram_dm_state`; unpublished it. Also unpublished redundant `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`). Production LinkedIn outreach is now dispatcher → acceptance/state sync → canonical 4-message DM sequence only.
- **2026-07-15**: Built and published automated LinkedIn DM suppression workflow (`LT - LinkedIn DM Suppression from GHL Tag`, IPN8jnR3XSurX0o1). GHL tag `stop_linkedin_dms` triggers a GHL automation → POSTs to `/webhook/lt-linkedin-suppress-dms` → resolves LinkedIn profile via Unipile, tags `linkedin_dm_sequence_completed`, upserts `linkedin_connection_state` to terminal for both real contact and synthetic `linkedin:follower:{providerId}`. Full audit confirmed all 3 send paths (DM Sequence, Follower DM, Dispatcher) correctly block suppressed contacts. Fixed dispatcher Feeder gap: added `linkedin_dm_sequence_completed` to blocking tag list.
- **2026-07-15**: Unicode/mojibake encoding fix expanded across all audited Unipile message sender nodes: LinkedIn DM Sequence (`Sync Connected from Unipile`, `Send DM Sequence Messages`), LinkedIn Follower DM, LinkedIn Dispatcher invites, and Instagram DM Sequence. Templates are pre-sanitized at runtime and final outbound text is sanitized immediately before Unipile API calls. Handles smart punctuation plus already-garbled forms like `canâ€™t` / `canΓÇÖt`. Created `scripts/suppress_linkedin_dms.py` for one-command DM suppression.
- **2026-07-14**: Vapi voice system activated. Published Intake Poller + Outbound Dialer. Fixed Trigger Apollo Enrichment auth and Remove Tag - Enriching URL. Added pagination, 30-contact cap, brands_pool/dispensaries_pool tag search, and tag rotation. Added state-to-timezone inference for both poller and dialer. Shifted dialer cron to `*/2 13-22` UTC for 9am ET start; widened business hours guard to 8-18 CT.
- **2026-07-14**: Apollo phone enrichment repaired. Created and published LT - Apollo Phone Enrichment Polling (JH8ShfpglWmLMZ3l, every 30 min). Replaces dead webhook-based pipeline. Syncs profile data immediately, requests phone numbers via async callback to V4 handler.
- **2026-07-13**: Backfilled 13,705 ghl_contact_id values into emerging_pool_contacts from GHL export CSVs (email + phone + name/company match). DAN dispatcher now has 5,373 eligible contacts.
