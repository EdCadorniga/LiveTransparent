# Alcohol Brands Multichannel Campaign - Preparation Plan

**Date:** 2026-10-06
**Status (updated 2026-10-07):** Published workflow `2e8c2d78-aaec-4591-9b53-b0715be8c4ce`; all 169 imported Alcohol contacts have verified sticky sender assignments and the entry tag `lt_campaign_alcohol_brands_oct_2026_enroll` was reapplied successfully. `Allow re-entry` is ON; `Allow multiple opportunities` is OFF; `Stop on response` is ON. Enrollment-history data, once fully loaded, showed current Wait / Waiting For Time entries with a next execution on 2026-10-08 around 1:49 p.m. PDT. The workflow's exact enrollment total and message delivery were not reconciled. The email preview still has reported GHL starter content after the Alcohol copy; remove and verify it before the scheduled sequence step. Destination placeholders, Email 3 numeric claims, other offer/outcome claims, and channel safeguards remain unresolved. See the 2026-10-07 EOS note and do not equate tag writes or workflow enrollment with email delivery.
**Source:** `New Campaigns October 2026/Alcohol - Multi Channel Outbound Sequence.pdf`
**GHL location:** Live Transparent (`Zwz4relUXVPxx8uohnjV`).

**Historical build log:** everything from `Objective and boundary` onward records state as of the dated checkpoint in that entry. Those notes may describe pre-publication or pre-enrollment conditions; they are not current instructions or readbacks. Use the 2026-10-07 status and CURRENT blocks above for the latest verified status.

## CURRENT 2026-10-07 — Imported-list sender assignment and workflow state

- For every Alcohol import, first reconcile/import records and confirm `Vertical = Alcohol`; then populate `contact.lt_campaign_alcohol_brands_oct_2026_sender_email` (`AIzg8FR3PEDr7PSGMuXN`); verify the field; apply `lt_campaign_alcohol_brands_oct_2026_enroll` only after launch checks. The workflow routes on this campaign-specific field. Do not use the shared `contact.marketing_sender_email`; it does not satisfy the router.
- Use balanced round-robin across `cameron@livetransparent.com`, `cameron@livetransparent.co`, `cameron@livetransparent.agency`, and `cameron@livetransparent.org`, keeping each contact's assignment sticky across all five emails. Preserve existing assignments in future imports and give new contacts to the least-used sender based on cumulative counts.
- **Current 169-contact Alcohol cohort:** assignments were read back as 43 `.com`, 42 `.co`, 42 `.agency`, and 42 `.org`. After the earlier entry tag removal, Ed explicitly instructed reapplication. The tag was absent from the cohort and was added to all 169 contacts with successful GHL API responses. History readback showed the first visible 10 contacts at `Wait` / `Waiting For Time`, next execution around 2026-10-08 1:49 p.m. PDT. Inspect remaining history pages and verify which exact action fires next; no delivery confirmation was read. Re-entry was enabled and saved before reapplication.

## CURRENT 2026-10-07 — SMS / voicemail failure-path handoff

- All 8 existing SMS outbound Webhook nodes (four Day 3 and four Day 13 sender branches) now contain Alcohol copy, preserve the first-name merge field, and use the 30-minute Alcohol booking URL. The edited workflow was saved/published. The planned Day 21 SMS 3 node is absent; do not claim all three planned touches are configured.
- The standard outbound Webhook panel and voicemail action panel expose no “continue on failure” control. HighLevel's standard outbound Webhook documentation says to inspect workflow execution logs for errors but does not specify whether this standard action halts or advances after an HTTP failure. The skip/retry statement in Custom Webhook documentation concerns a different action and must not be assumed. The voicemail help material also does not specify whether an invalid/unreachable number causes the workflow to stop or continue.
- **Required next verification:** monitor workflow Execution Logs and SimpleTexting/provider records for SMS action outcomes; for voicemail, inspect workflow logs and the provider/carrier result available. Determine whether later nodes ran after a reported failure. Do not create a deliberate failing send on cohort contacts. Use product documentation or an isolated internal contact only after explicit authorization. Add or verify phone eligibility, SMS opt-in/STOP/DND, voicemail consent, and route gates before relying on either channel. A 2xx webhook or “action executed” record is not proof the recipient received a message.
- **Immediate cadence readback:** the latest visible Alcohol enrollment-history page showed contacts in `Wait`, `Waiting For Time`, with next execution 2026-10-08 around 1:49 p.m. PDT. The next step name and actual email delivery are not established by that row alone. The full history and exact first-email action need inspection before representing messages as sent.

## Objective and boundary

Prepare a separate Alcohol Brands multichannel campaign modeled on the Cannabis Brands campaign while preserving the existing Cannabis assets and workflow. Build Alcohol-specific assets under their own names and folders. The eventual orchestration should be a separate GHL workflow with its own entry tag, lifecycle state, eligibility and suppression checks, attribution key, idempotency keys, and audit trail. Do not reuse Cannabis campaign tags or workflow.

The existing Cannabis build notes in `docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md` provide the execution pattern and known GHL constraints. Revalidate shared settings and provider readiness, but preserve all Alcohol-specific copy, audience rules, and channel steps.

## Source sequence

| Day | Channel | Source step |
|---:|---|---|
| 0 | LinkedIn | Connect |
| 1 | Email | Email 1 - The Opener |
| 3 | SMS | SMS 1 - The Nudge |
| 5 | Email | Email 2 - How It Works |
| 7 | Voicemail | Voicemail 1 |
| 9 | LinkedIn | DM 1 |
| 11 | Email | Email 3 - The Proof |
| 13 | SMS | SMS 2 - Follow-up Bump |
| 15 | Email | Email 4 - The Direct Ask |
| 17 | LinkedIn | DM 2 |
| 19 | Voicemail | Voicemail 2 |
| 21 | SMS | SMS 3 - Final Bump |
| 23 | Email | Email 5 - The Breakup |
| 23+ | Exit | Newsletter nurture, 3 months |

## GHL email assets - initial attempt and current state

Created dedicated Email Templates folder `Alcohol Brands Multichannel - Oct 2026` (`6ac516def94e3d07369a811b`) and five template records in it:

| Touch | Subject | Record ID |
|---|---|---|
| Email 1 | Quick question about your ad approvals | `6ac516e9f94e3d07369a8226` |
| Email 2 | Why the account matters more than the creative | `6ac516e9de5506b64c8f56b2` |
| Email 3 | How we keep restricted brands live | `6ac516ea81f928bb68926184` |
| Email 4 | 30 minutes to address the disapprovals? | `6ac516eb87cdcc5d6e585f89` |
| Email 5 | Should I close this out? | `6ac516ec0baff29423fe92fe` |

**Initial API behavior:** official GHL template creation returned success, but the API ignored the supplied HTML body. The five shells were then edited through the authenticated Email Templates UI on 2026-10-07; no replacement records were created. Read-back confirmed revisions for all five original IDs. Each body has two blank paragraphs after the greeting, two blank paragraphs before `Best,`, and includes the unsubscribe link. **Preview issue:** each template still renders GHL's default starter content after the Alcohol copy. A node-level experiment confirmed Email 1 would include that unrelated starter content, so its unsaved change was canceled. Do not link any of these templates to the workflow until the starter content is removed and all five previews are clean. Bracketed destinations and content-review gates also remain unresolved.

The source PDF contains the copy and subjects. Keep claims and links as review gates. Apply the already-confirmed campaign-wide 30-minute meeting duration preference where source copy says 15 minutes. Do not change the PDF.

## Content and destination gates

1. Email 3 includes quantified claims: 40% higher approval rate and 16-month average retention. Verify the comparison, measurement period, sample, and evidence before launch; if unsupported, obtain approved replacement copy.
2. The source refers to the short deck, booking page, Compliance Ad Account Setup Checklist, and a quick read without actual destinations in the PDF. Do not invent links. Resolve and read back each first-party URL before adding hyperlinks.
3. Use safe fallbacks for missing first name and company, and verify exact GHL merge syntax in a saved preview. Do not assume `{{contact.first_name}}` / `{{contact.company_name}}` work or render safely.
4. Source makes claims about compliance-built accounts, campaigns staying live, approvals, no minimum spend, free account review, and outcomes. Confirm each claim and the applicable offer terms before launch.
5. Use the campaign's confirmed 30-minute meeting duration across emails and LinkedIn copy where a call length appears.

## Build checklist after email content is corrected

1. Finish and read back all five native GHL Send Email template bodies and subjects; keep templates in the dedicated folder.
2. Create a separate Alcohol SMS snippets folder and three campaign-specific snippets using source copy. Confirm snippet storage is reference-only if the SimpleTexting path uses rendered message text.
3. Resolve a campaign-specific Day 0 Classic LinkedIn request path, ASCII validation, request idempotency, suppression check, and activity mirror. Current LinkedIn senders are unpublished; do not reactivate generic senders.
4. Build LinkedIn DM paths only where connection state and any required Sales Navigator V2 chat mapping are confirmed.
5. Verify contact-level SMS opt-in, STOP/DND and inbound reply handling; use existing SimpleTexting boundary only after campaign attribution, idempotency, and reconciliation are verified.
6. Verify voicemail consent/eligibility, provider/action semantics, callback route and default-number behavior before representing voicemail as a send action.
7. Establish exact Alcohol audience eligibility and exclusions from current GHL fields/tags. Do not infer enrollment or exclusion tags from Cannabis values. Manually selected cohort only.
8. Create Alcohol-specific entry and lifecycle tags only after exact names are collision-checked. Keep them unassigned.
9. Build a separate Draft GHL workflow with entry qualification, global stop/reply/appointment exits, per-channel consent gates, waits, and fail-closed handling. Recheck eligibility immediately before each send.
10. Record every step outcome (`sent`, `skipped`, `failed`, `unknown`) with campaign/contact/step idempotency and provider IDs. Hold unknown results for reconciliation; never blind-retry.
11. Preserve the separate newsletter system; confirm the 3-month exclusion interval and operator-reviewed re-entry after Email 5.
12. Perform non-sending readbacks of workflow settings, graph, templates/snippets, zero enrollment, and unpublished status. No tests, calls, sends, enrollment, or publication without separate authorization.

## Current session boundary

No Alcohol workflow, tags, contacts, snippets, channel providers, or newsletter settings were changed. No enrollment, test, send, voicemail, call, LinkedIn action, publication, or commit occurred. The only GHL changes were creation of the named Email Templates folder and five empty/default-layout template records noted above. The Alcohol campaign is not ready for sending.
