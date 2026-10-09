# Cannabis SMS 3 correction — EOS 2026-10-09

> **Superseded 2026-10-09 (SMS mode):** every `dryRun=true` reference below is historical. All eight vertical campaign SMS Webhooks are now `dryRun=false` (96/96); Cannabis is Published v73. See the top of `AGENTS.md`.

## New vertical setup priority (2026-10-09)

> **Superseded for campaign setup by the Crypto-first EOS:** [`docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md`](docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md). That handoff records the verified Crypto assets/workflow, confirmed order Crypto → Cannabis Dispensaries → Gambling → Peptides, exact template-spacing checks, and a copy-ready prompt for the next LLM. This file remains the authoritative history for the Cannabis SMS3 correction, active-contact check, and deferred inbound→MQL review.

- Ed wants the remaining vertical automations set up one at a time, starting with email templates, SMS templates/snippets, and tags, then completing the same end-to-end build process used for Alcohol and the other verticals.
- Fresh GHL workflow-list readbacks confirm four pre-created workflows, each Draft with 0 total / 0 active enrollment: Crypto Multi-Channel Outbound - Oct 2026; Cannabis Dispensaries Multi-Channel Outbound - Oct 2026; Gambling Multi-Channel Outbound - Oct 2026; Peptides Multi-Channel Outbound - Oct 2026.
- Matching source PDFs and personal-phone-enriched lead CSVs were found under `New Campaigns October 2026/`. The Cannabis source filenames spell “Dispenseries.”
- At the initial planning checkpoint, Ed's list included Crypto twice; the available separate vertical/files/workflow showed Gambling. The later EOS records the confirmed order as Crypto → Cannabis Dispensaries → Gambling → Peptides and the subsequent Crypto asset setup. Build one vertical fully before moving to the next.
- The user's response requirement is now explicit: inbound response → `mql` tag → ensure opportunity in **Sales Outreach → New**; create no new opportunity if any opportunity already exists. It is intentionally deferred behind the vertical setup. Before its later implementation, reconcile it with the Janvi qualification gate, define covered inbound channels, and decide whether an existing non-Sales Outreach opportunity is preserved or moved.

## Inbound response → MQL and Sales Outreach opportunity review (2026-10-09)

- Ed requested a planned behavior: any inbound response should add the contact's `mql` tag and ensure a Sales Outreach → New opportunity exists, without creating a new opportunity if any opportunity already exists. This is deferred behind the sequential setup of the remaining vertical campaigns.
- Read-only GHL workflow-list check found `WL - Micro - Stage MQL Opportunity Baseline` (`172e98e7-7dde-49fd-b32e-e1d98395484a`) Published, 750 total / 0 active; last updated Aug 31, 2026. Builder confirms trigger `Contact Tag` → `Tag added: mql`; it is not a response trigger and does not apply the tag. `Webhook to process MQL` POSTs contactId/contactName/firstName/lastName/tag to `/webhook/ghl-mql-opportunity-baseline-v2`. A separate `Webhook to send Lead details to Slack` POSTs `New MQL` plus contact/source/UTM fields to `/webhook/wl-slack-channel-update-v2`.
- The existing runbook [`GHL Live Transparent CRM/MQL_Tag_Opportunity_Baseline_Webhook.md`](../../GHL%20Live%20Transparent%20CRM/MQL_Tag_Opportunity_Baseline_Webhook.md) documents the downstream contract as Warm → Qualified (MQL), except when a Sales-pipeline opportunity already exists. It does not document Sales Outreach creation for all inbound replies. The n8n endpoint implementation was not freshly checked through the required `n8n-lt` instance; only the GHL trigger/actions and repository contract were reviewed.
- The separate published all-vertical `Customer replied` workflow only removes contacts from the four outbound vertical workflows in the inspected configuration. It does not add the MQL tag or ensure an opportunity. Call Details and every custom-provider path remain unverified.
- **Policy conflict before implementation:** the request differs from the documented Janvi AI qualification gate, which restricts normal Sales Outreach promotion to explicitly qualified cannabis businesses. Treat any existing opportunity in any pipeline as blocking creation of a new opportunity. Confirm scope of “any response” and whether an existing opportunity outside Sales Outreach should be preserved or moved to Sales Outreach → New. The duplicate-avoidance check should be idempotent across all covered response sources.
- No workflow edits, saves, publishes, executions, webhook calls, tests, contact writes, tags, or opportunity writes were made for this review.
- Next: inspect the live endpoint via `n8n-lt` read-only; reconcile the policy questions above; then plan an authorized implementation and validate its deduplication/response-source coverage. Do not invoke a production webhook as a test.

## Latest Alcohol sequence recheck (2026-10-09)

- Fresh authenticated Builder readback of Alcohol workflow `2e8c2d78-aaec-4591-9b53-b0715be8c4ce` is Published version 38.
- Live edge traversal across all four sender branches (`.com`, `.co`, `.agency`, `.org`) now confirms **Day 7 voicemail 1 → 4-day Wait → Day 11 Email 3 → 2-day Wait → Day 13 SMS 2 → 2-day Wait → Day 15 Email 4**. The current branch order is correct and PDF-aligned. This supersedes the earlier version-37 finding that SMS2 remained before Email3.
- No changes, tests, executions, or provider calls were made in this recheck.

## Cannabis early-exit re-entry and inbound-stop follow-up (2026-10-09)

- Ed deferred the shared SMS consent/STOP/DND and idempotency/provider-reconciliation reviews, voicemail-consent review, and three-month newsletter exit work for later.
- Fresh workflow-list readback: `Transparent eCom - Stop Outbound on Inbound Communication (All Verticals)` (`54dc6321-ed85-4eee-870d-0716c73c66fb`) is Published, 8 total / 0 active. Its saved Builder configuration is a `Customer replied` trigger with no filters and a `Remove from Workflow` action targeting Alcohol, Cannabis, Nicotine, and Mushroom. This verifies the published reply-stop path; it does not prove Call Details or every custom provider is covered.
- Fresh Cannabis enrollment history shows the active cohort waiting at Wait with next execution Oct 10. Finished entries show current action `No Action`; sampled execution paths show one contact exited at the qualification-gate default (it had exclusion tags) and another at sender-router None on an earlier enrollment, but that contact now has a later active wait enrollment and a sender assignment.
- No eligible contact was found in the sampled evidence who exited after an outbound action and lacks a current active enrollment. **No contacts were re-entered or retagged.** Do not re-enter records only because they are Finished; the sampled cases are excluded or already active. Preserve active enrollments. If a specific eligible, inactive contact is confirmed to have exited before sequence actions due to an edit, re-enter only that reconciled contact through the authorized entry path.
- No workflow/contact writes, executions, test messages, provider calls, or sends were performed for this follow-up.

## Scope clarification (2026-10-09)

- Ed authorized correcting any incorrect waits and SMS 3 messages across Alcohol, Cannabis, Nicotine, and Mushroom, while preserving enrolled contacts. Do not force contacts forward, remove/re-enroll, retag, or manually compensate them.
- No additional wait should be added before Day 1 Email 1. Email 1 is the first workflow action; check only its downstream wait interval and all later waits against the applicable PDF.
- Preserve current SMS `dryRun` values, canonical SimpleTexting request contracts, and do not execute workflows or invoke/send test messages.

## Latest implementation continuation (2026-10-09)

- Re-entered GHL from the authenticated Live Transparent Launchpad and reopened Cannabis workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377`.
- Fresh workflow-list readback: Published, 88 total / 41 active; last updated Oct 8 1:16 PM in the UI. The enrollment-history first page showed nine entries at `Wait` / `Waiting For Time` and one finished contact, but their displayed next execution times were Oct 8 (already elapsed at this check). Treat the active-action/timing state as unreconciled; neither safe waiting nor the effect of graph edits on deadlines is established.
- At this initial read-only checkpoint, no graph edit, node payload change, workflow save/publish, test, webhook invocation, provider call, or contact/enrollment write occurred. The Builder Draft/Publish toggle was not used to determine status. The workflow-list status was authoritative.
- The initial checkpoint did **not** reconcile all active entries or the Nicotine history, and did not read back all SMS `dryRun` values. The subsequent saved implementation state is recorded below.
- **Superseded:** Ed has now authorized correcting any wrong waits and SMS 3 messages across Alcohol, Cannabis, Nicotine, and Mushroom. Proceed with the graph/copy corrections without another active-contact impact confirmation, while preserving existing enrolled contacts. Do not force contacts forward, remove/re-enroll, retag, or compensate manually.
- Do not add an initial wait before Day 1 Email 1; treat Email 1 as the first workflow action. Preserve existing SMS `dryRun` values; no tests, executions, provider calls, or test messages. Correct waits/copy based on each source PDF and read back all changes.
- **Saved GHL actions:** Alcohol workflow `2e8c2d78-aaec-4591-9b53-b0715be8c4ce` is Published version 37. Its four Day 21 SMS3 actions contain the Alcohol PDF text with First Name/Company merge fields; all 12 Webhooks are `dryRun=false`. Its wait settings were changed to 4/2/2 days for the Day7→11/Day11→13/Day13→15 intervals, and to two days after each later action except the four-day Day15→Day19 external LinkedIn gap. However, saved graph order still routes Day7 voicemail1→SMS2→Email3→Email4: SMS2 remains before Email3. A selected-edge Delete key attempt opened “Are you sure you want to delete this step?”; no edge/action was removed. Do not claim Alcohol topology fixed.
- **Nicotine:** workflow `e42cee9c-3c0d-474b-8d78-83cd10e9c620` is Published version 40. Four Day21 SMS3 actions have the PDF final-bump text with First Name/Company merge fields; all 12 Webhooks are `dryRun=false`. Saved graph order is Email3→SMS2. Waits read back after save: 2/2/2/4/2/2/4/2/2 days after Email1, covering Day1→3 through Day21→23.
- **Cannabis:** workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377` is Published version 73. Corrected SMS1/SMS2 company merge-field copy across all branches; all 12 Webhooks are `dryRun=false`. Saved SMS3 remains PDF-correct. Saved waits/order match the intended chronology: 2/2/2/4/2/2/4/2/2 days after Email1, with Email3 before SMS2.
- **Mushroom:** workflow `f1280d4b-ac8f-4353-b3c1-f874f7202bdb` is Published version 21; latest payload readback shows all 12 SMS Webhooks `dryRun=false`, with correct SMS3/cadence already in place.
- Across the four workflows, 48 SMS Webhook actions are now saved with `dryRun=false`; SMS3 copy has been corrected in all four sender branches for each vertical. Canonical endpoint/auth/source/content-type payload fields were not intentionally changed. No workflow execution, provider call, test SMS, voicemail, or call was performed. No extra wait was added before Day1 Email1.
- **Remaining:** no Alcohol branch-order fix is outstanding after the version-38 recheck above. Keep LinkedIn external. Do not run tests or provider calls.

## Completed

- Opened GHL from the authenticated Live Transparent location Launchpad, then navigated through Automation → Workflows to Cannabis workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377`.
- Updated the Day 21 SMS 3 `message` value in all four sender branches (`.com`, `.co`, `.agency`, `.org`) to the Cannabis PDF copy: `{{first_name}}, last nudge from me - want me to send the dispensary attribution breakdown over, or should I close this out?`
- Saved and read back every SMS 3 action. GHL renders the First Name merge field as `Contact.First Name`; the remaining message text is exact in all four branches.
- Verified that the canonical SimpleTexting webhook URL, `source=sms`, `Content-Type: application/json`, and `dryRun=false` remained in each action. The workflow list shows Published, 88 total enrolled / 41 active enrolled, with a newer update timestamp.
- No workflow execution, webhook invocation, provider call, test SMS, or contact write was performed.

## Current blockers / next actions

1. Preserve enrolled contacts; do not force contacts forward, remove/re-enroll, retag, or compensate manually. No initial wait before Day 1 Email 1.
2. Correct Alcohol's four branch edges so Day11 Email3 precedes Day13 SMS2. The saved wait values are ready for that path: voicemail1→Email3=4d, Email3→SMS2=2d, SMS2→Email4=2d; preserve Email4→voicemail2=4d, voicemail2→SMS3=2d, SMS3→Email5=2d. Verify all four actual edges after reconnection.
3. Read back Published state and all four SMS3 payloads for each vertical, plus all 48 `dryRun=false` fields. The full save/readback now proves the action-copy/live-mode work; no tests, executions, or provider invocations are needed.
4. Keep LinkedIn in the separate automation. Continue using a Builder edge-reconnection method that does not delete any action node.

## Verification and repository state

- `git diff --check` passed; only the existing LF/CRLF normalization warnings were emitted.
- Updated `AGENTS.md` and `Project Status and Next Steps.md` with current workflow state, SMS copy correction, live-mode scope, and ordered follow-up.
- The worktree contained other pre-existing modified and untracked project files. No files were staged or committed.
- The later authorized implementation continuation updated GHL workflow actions/waits as summarized at the top of this file. Handoff/status documentation was refreshed to match; no workflow execution or provider send was used.
