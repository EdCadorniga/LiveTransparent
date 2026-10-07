# Alcohol and Cannabis Enrollment — EOS Handoff

**Date:** 2026-10-07 (Asia/Manila; GHL UI timestamps below are America/Los_Angeles / PDT)
**Project:** LiveTransparent, GHL location `Zwz4relUXVPxx8uohnjV`
**Worktree:** `codex/social-outreach-sync`; latest HEAD observed `c004a57`. The worktree was already dirty at closeout start, with modified campaign notes and untracked source PDFs/CSVs, import-prep files, and `tmp/`. This closeout's documentation edits are uncommitted; do not attribute all existing untracked files to this closeout.

## Verified work

- This EOS pass reviewed repository state and campaign notes only; it did not freshly inspect GHL. The workflow/contact/enrollment statements below refer to the latest live readbacks already recorded in this handoff and AGENTS.md. Re-read GHL before acting on a scheduled step or asserting current enrollment/delivery.

- Confirmed the imported cohorts from the GHL Import Prep CSVs: 169 unique Alcohol contacts and 44 unique Cannabis contacts. Readback matched the expected `Vertical` for each contact, and campaign-specific sender values were present. Alcohol distribution was `.com/.co/.agency/.org` = `43/42/42/42`; Cannabis = `11/11/11/11`.
- Both entry tags were absent from their cohorts before the reapplication, so no removal write was necessary. After Ed's explicit request, all 213 contact tag-add calls returned success: `lt_campaign_alcohol_brands_oct_2026_enroll` on the Alcohol cohort and `lt_campaign_cannabis_brands_oct_2026_enroll` on the Cannabis cohort.
- Both published workflows have `Allow re-entry` ON (saved and visually read back), `Allow multiple opportunities` OFF, and `Stop on response` ON:
  - Alcohol: `2e8c2d78-aaec-4591-9b53-b0715be8c4ce`
  - Cannabis: `5d1236a2-1b98-4b7f-9621-5d4f7749f377`
- Once the GHL history finished loading, it showed entries dated 2026-10-06 around 1:49 p.m. PDT. The visible Alcohol page showed 10 contacts at `Wait` / `Waiting For Time`, next execution around October 8 at 1:49 p.m. PDT. The visible Cannabis page showed 9 at `Wait` / `Waiting For Time` and one `No Action` / `Finished`. The full pagination/active totals were not reconciled. The Cannabis workflow gate excludes `dispensaries_pool` and `enrollment queue - dan - dispensaries`; three contacts in this cohort were earlier identified with the latter tag.
- **Correction to the prior empty-history read:** the initial `No enrollments found` snapshot was captured before the workflow's cross-origin history view had loaded. Later live readback did show active waits and finished entries. Do not cite that early blank snapshot as the final status.
- No manual email, SMS, voicemail, call, test, or send was run by the agent in this EOS. Enrollment may cause scheduled workflow actions; the history's `Wait` status is not proof that an email or other message was delivered.

## SMS and voicemail failure behavior

- The Alcohol workflow has eight existing standard outbound Webhook nodes for SMS: four Day 3 and four Day 13, across four sender branches. Their copy was changed to Alcohol content with the 30-minute Alcohol booking URL and saved/published. The planned Day 21 SMS 3 node is absent. Cannabis SMS nodes were not changed in this session.
- Inspected the standard outbound Webhook and voicemail action panels. Neither showed a `continue on failure` / error-routing control.
- HighLevel's [standard outbound Webhook guide](https://help.gohighlevel.com/support/solutions/articles/155000003299) directs operators to workflow execution logs for errors but does not define whether this configured action stops or advances the workflow after an HTTP failure. The separate [Custom Webhook guide](https://help.gohighlevel.com/support/solutions/articles/48001238167-guide-to-custom-webhook-workflow-action) describes skip/retry behavior for a different action; do not assume those semantics apply here. The [Voicemail action guide](https://help.gohighlevel.com/support/solutions/articles/155000003275) likewise does not say whether an invalid/unreachable number stops or advances the workflow.
- **Required follow-up:** inspect GHL Execution Logs after any SMS/voicemail failure and compare with the SimpleTexting/provider or carrier record. Inspect the contact's later workflow action to establish whether the workflow continued. Do not inject a deliberate failure into the live cohort. Prefer documentation or an isolated internal contact, and get explicit authorization before any test that can call/send. Treat an executed webhook / HTTP 2xx as transport acknowledgement, not proof of recipient delivery.
- Verify phone eligibility, contact SMS opt-in, STOP/DND/reply handling, voicemail consent, and route gates before relying on those phone steps. These campaign-level gates remain incomplete/unverified.

## Remaining campaign risks

- Alcohol plan still records starter content after the intended copy in email previews, unresolved destination placeholders, and unsubstantiated numeric/offer claims. Confirm the exact first email and next scheduled action before representing delivery as correct.
- Full enrollment-history pagination was not reviewed; current active, finished, and excluded totals are unknown. The history page's displayed next execution date was October 8 around 1:49 p.m. PDT, but the exact action name and delivery confirmation were not read.
- Cannabis exclusion and channel-safety gates remain as documented in its campaign plan. Tag success does not mean every contact passed eligibility.
- **Template maintenance rule for future edits and verticals:** maintain blank lines between paragraphs, at least two empty lines after the greeting, and at least two empty lines between the final paragraph and closing/signature. Re-add/reselect the correct template in each corresponding Send Email node, accept the confirmation dialog, enable **Sync Edits to Template** on every Send Email node, save, and read back the template linkage and sync setting.

## Next session — Nicotine and Mushroom

1. **Before the next scheduled Alcohol/Cannabis email action, inspect both workflow histories and exact next Send Email nodes.** Verify the linked template is the correct campaign template, the template has blank lines between paragraphs plus at least two empty lines after the greeting and before the closing/signature, and **Sync Edits to Template** is enabled on every Send Email node. If correcting a node, reselect the template, accept the confirmation dialog, enable sync, save, and read back. Do not assume a library-template edit propagated to the node.
2. Read all Alcohol and Cannabis enrollment-history pages and scheduled actions. When SMS or voicemail attempts occur, compare GHL execution logs with provider/carrier outcomes and determine if later steps continued. Do not report a channel as delivered from node execution alone.
3. Start separate campaign prep for Nicotine and Mushroom; do not reuse Alcohol/Cannabis workflow IDs, entry tags, or sender fields.
4. Inventory the supplied files. The workspace currently contains `New Campaigns October 2026/Mushroom - Multi Channel Outbound Sequence.pdf` and `New Campaigns October 2026/Nicotine Leads (1).csv`. No Nicotine sequence PDF or Mushroom lead list was found in the current file inventory; locate the missing source(s) before finalizing campaign copy or selecting a contact cohort.
5. Review each source sequence and lead list. Reconcile imported/existing contacts and verify each `Vertical`; collision-check a campaign-specific sender field and workflow router; allocate sticky balanced sender values and read them back; only then apply that campaign's entry tag after readiness checks.

## Documentation updated

- `AGENTS.md` now has the current enrollment state and failure-monitoring instruction; the earlier pre-reapplication note is marked superseded.
- Alcohol and Cannabis campaign plans have updated current-state blocks and SMS/voicemail failure-path handoffs.
- No workflow definition, contact field, sender assignment, tag, or message content was changed during EOS beyond the previously authorized tag reapplication and re-entry setting changes documented above.
