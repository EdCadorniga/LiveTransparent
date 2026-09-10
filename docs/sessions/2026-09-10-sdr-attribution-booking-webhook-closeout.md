# 2026-09-10 — SDR Booking Attribution Webhook Closeout

## Objective

Capture the SDR assigned when a regulated-ads appointment is booked on Cameron's calendar, before downstream SQL-tag and opportunity mutations overwrite or obscure ownership.

## Completed

- Confirmed the correct GHL booking workflow is `Appointment with Cameron for Regulated Ads` (`971c3016-946a-4612-ad0a-2afc9a0ee6f0`), not `LT - Opportunity Owner Alignment`.
- Read-only GHL API verification confirms the workflow is `published`, version 14, updated `2026-09-09T17:09:26Z`.
- Confirmed the GHL action posts to `/webhook/wl-slack-channel-update-v2`.
- Confirmed contact custom field `Originating SDR` exists as `TEXT`, field id `wBGXjev0rKowcfxTSWNa`.
- The deployed n8n handler expects GHL booking custom data key `assignedSDR` containing the assigned user's email; the public GHL API does not expose the saved action body for independent inspection.
- Updated n8n workflow `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`):
  - reads `assignedSDR`;
  - maps Jason, Marc, and Cameron email values to GHL user IDs;
  - stamps `Originating SDR` before SQL tag/opportunity writes;
  - skips safely when the value is missing or unrecognized.
- Published active version: `1cb05fcd-e0c0-4ae1-9413-637878325e8e`.
- Activated Exec Summary field lookup in `Bukc0mgOD2r7V6ED`, version `08abd9cb-7100-4e31-88d1-4413aadee625`, using `wBGXjev0rKowcfxTSWNa`.

## Verification

- Re-read both live workflows after mutation; `versionId == activeVersionId` and both are active.
- The public GHL workflow-list API confirms publication/version metadata, but does not expose action definitions. Therefore `assignedSDR` being present in the saved GHL action body remains unverified until a real webhook execution is observed.
- Confirmed no n8n executions are currently `new`, `running`, or `waiting` for the booking webhook.
- Did not run a production test event because the handler writes GHL contact/opportunity data and posts to Slack.

## Next Session

1. Observe the next real regulated-ads booking webhook and confirm the payload includes `assignedSDR`.
2. Verify n8n reports `sync.originatingSdr = stamped` and the contact field contains Jason/Marc's GHL user ID.
3. Verify the Exec Summary `sdrPerformance` booked count reflects the originating SDR.
4. If the value is missing or resolves to an unexpected user, inspect the GHL merge-field output before changing n8n logic.

Historical bookings remain unrecoverable. Do not manually execute the production webhook or create a test booking without explicit approval.
