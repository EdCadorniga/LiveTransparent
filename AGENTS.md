# LiveTransparent Agent Notes

## CURRENT 2026-10-09 — Gambling / Cannabis Dispensaries / Peptides email templates + Peptides workflow CONVERTED

- Created **15 GHL email templates** via the `.env` GHL PIT (no browser) in Ed's three folders, populated with `POST /emails/builder` then `PATCH /emails/builder/{id}` with `editorType=html`+`editorContent`+`name`. Create returns HTTP 201 and ignores the supplied name; the PATCH sets the real name/body. Never trust the create response for name/body proof.
  - **Gambling** folder `6ac8e43939edc5e18c159cf8`: `6ac8e8dcf9707340c6901cb1`, `6ac8e9079660fa02e854b290`, `6ac8e90708741365d8940fb7`, `6ac8e90887cdcc5d6eb6b756`, `6ac8e909976a2a32d9f82346` (E1–E5).
  - **Peptides** folder `6ac8e41a39edc5e18c159aa5`: `6ac8e90a87cdcc5d6eb6b776`, `6ac8e90ae6a28b9ad5ef77e7`, `6ac8e90be6a28b9ad5ef77fb`, `6ac8e90c39edc5e18c160657`, `6ac8e90d9660fa02e854b389` (E1–E5).
  - **Cannabis Dispensaries** folder `6ac8e42a1ea8584cd7a514af`: `6ac8e90e4c92b27bd3d9fd53`, `6ac8e90f9660fa02e854b3ed`, `6ac8e90f87cdcc5d6eb6b835`, `6ac8e91039edc5e18c1606dd`, `6ac8e911976a2a32d9f82424` (E1–E5).
- Names follow `<Vertical> Brands - Email N - <Step>` (Cannabis Dispensaries uses the vertical label directly). Copy is from each vertical's source PDF; merge fields normalized to `{{contact.first_name}}`/`{{contact.company_name}}`. Booking `…/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=<slug>` (slug `gamblingsequence`/`peptidesequence`/`dispensariesequence`); checklist resource in Email 1&2 `…/widget/form/5rytqkbske3RlMfYHpMk?utm_source=<slug>`; Email 5 uses the deck trigger link only. Deck trigger links verified live: Gambling `{{trigger_link.QK1BzLSt58DtGPdXci3m}}`, Peptides `{{trigger_link.egfi10VJpDEoSmwcnxQn}}`, Cannabis Dispensaries `{{trigger_link.nPzl7Eh9kT87aPqz8gIt}}`.
- **Format:** Ed explicitly directed all 15 to match the Alcohol Brands Campaign template exactly — `font-family:Arial,sans-serif;color:#111;font-size:14px;line-height:1.5`, no `<head>`/`<main>` wrapper, plain `<hr>`, "you can unsubscribe here" footer. This **supersedes the earlier "Arial 12px" spacing rule for these three verticals** and differs from the Crypto/Mushroom templates (12px/600px). Reconcile whether Crypto/Mushroom/Nicotine should be restyled before launch. Verified 15/15 via saved Firebase previews (style line, greeting blanks, signature, footer, valid `</body></html>`). The Alcohol templates' own preview export is inconsistent (`</body></html>>`/missing `>`); that is a preview artifact, not a builder defect — my 15 export clean closings.
- Local audit copies: `New Campaigns October 2026/Email Templates/<Vertical>/` (+ `_manifest.json`, `_ghl_ids.json`), untracked.
- **Peptides workflow `11a70375-d401-45d1-86c1-13e538528748` "Peptides Multi-Channel Outbound - Oct 2026" — CONVERTED 2026-10-09 (Draft, version 13, 0 enrolled, unpublished).** Driven through the **Playwright** browser, not OpenCLI: OpenCLI cannot reach the cross-origin `workflow-builder` iframe (`frames`=0, `network` sees only the outer frame), while Playwright traverses it. Read the draft graph from `GET backend.leadconnectorhq.com/workflow/Zwz4relUXVPxx8uohnjV/{id}?includeScheduledPauseInfo=true` → `fileUrl` (Firebase Storage). **GHL persists builder edits only on the global Save button** (per-action "Save action" does not persist; the draft `version` increments only on global Save; save is Firestore-backed so not scriptable). The canvas is not fit-to-view on load here — set `.vue-flow__viewport` `transform: translate(10px,60px) scale(0.22)` before node clicks; reload (list → search → open) to re-read the draft for verification.
  - Assets created via PIT: six tags `lt_campaign_peptides_brands_oct_2026_{enroll=uzhO3USGruQrTnLq9noG, active=KM3XnGqRodbedXnuHqlb, replied=DyoXUy55sEFNdixmrUXH, completed=pL9cRYZyboIkTEkgsFTx, suppressed=3bEQJtKUcPpqBin3uEF3, voicemail_consent_verified=kFRHud75y8dzRGPODeAN}`; sender field **LT Campaign Peptides Brands Oct 2026 Sender Email** = `ADJQKqlJzjhnGiCpQQgg` (`contact.lt_campaign_peptides_brands_oct_2026_sender_email`).
  - Trigger `Entry - Peptides Brands Multichannel Oct 2026` (`contact_tag` → `tagsAdded == lt_campaign_peptides_brands_oct_2026_enroll`); gate `Eligibility gate - Peptides` (`Vertical == Peptides`, field `ODs8fBt5te5HEfSJ91pY`); router `Sticky sender route - Peptides campaign field` with 4 branches `Cameron Peptides - .com/.co/.agency/.org` on `ADJQKqlJzjhnGiCpQQgg`; 20 email actions (4 senders × E1–E5) each linked to the corresponding Peptides template with Sync ON, `Cameron Karkut`, correct branch From Email, subjects `Quick question about your ad account` / `Why the account matters more than the creative` / `Third agency in three years` / `30 minutes to keep your ads alive?` / `Should I close this out?`; 12 SimpleTexting Webhook actions with Peptides SMS 1/2/3 and **`dryRun=true`** (were `false` in the copy); 8 voicemail actions retained the shared `V3.mp3`; waits unchanged `2/2/2/4/2/2/4/2/2` per branch. Verified persisted via graph readback (v13): trigger PUT, gate/router/emails/SMS all Peptides.
  - **Initial-wait decision (resolved):** the plan suggested the PDF's "Wait 1 day" before Day 1 Email 1 (Crypto sibling added it), but the standing vertical rule says not to; **Ed answered 2026-10-09 "Do not add the initial wait"** — no structural change.
  - **Remaining (not done):** Peptides SMS snippets folder (snippets are reference-only; delivery uses the SimpleTexting webhook); Peptides cohort reconciliation + balanced sender-assignment (`.com/.co/.agency/.org`); entry-tag application; publication/enrollment. No sends/calls/tests/imports/tag-writes/publish. Email 3 unsupported "40% higher approval rate / 16 months" claim + Florence Kirley testimonial still need substantiation before launch.
  - Sibling drafts: Cannabis Dispensaries `365ecf51-d700-4c2d-8058-df20ad523538` v1, Gambling `4a238825-61d2-49e6-a3d0-4acb3a19c674` v1, Crypto `0a79d683-4374-432d-bc64-6c8272540041` v46.
- Caveats: Email 3 in all three verticals carries the unsubstantiated "40% higher approval rate / 16 months" claims; Peptides Email 3 adds a named testimonial. No emails sent, no workflows changed, no contacts touched, nothing committed. Full detail: [`docs/sessions/2026-10-09-gambling-dispensaries-peptides-email-templates-eos.md`](docs/sessions/2026-10-09-gambling-dispensaries-peptides-email-templates-eos.md).

## CURRENT 2026-10-09 — Executive Report V1 SQL booking attribution handoff

- Executive Report V1 deployed as build `2026-10-09-v1-sql-booking-attribution`; public page and proxied facts endpoint were read back successfully. The 2026-09-09 through 2026-10-09 facts response classifies 582/582 SQLs as SDR or Calendar link. The card shows **Booked via / Who + UTM / SQLs**; missing calendar UTM is shown as a tracking gap rather than an Unknown booking path.
- Current facts expose incomplete capture: 1 SDR SQL (Jason Bornillo), 3 named Regulated Ads calendar SQLs missing UTM, and 578 calendar-link SQLs with no captured calendar/link name or UTM. Do not represent these as verified links. The previous inventory recorded 14 calendars and 18 Trigger Links; the latest documented GHL PIT read returned 14 active calendars and 17 Trigger Links.
- The GHL PIT is read from `.env`; never print or copy its value. Documented v3 API reads confirmed 98 workflow summaries and 27 workflow-email campaigns. Attribution workflows are Alcohol `a707d0b6-0717-4903-8b38-3510504a4136` Published v3, Cannabis `c9bbb696-fe29-44b0-81c7-6feffeaac98f` Published v5, Nicotine `963bf85a-cdff-4eb1-90ea-6a473fb0f32f` Published v4. The generic booking-click and website-click workflows are Published v7 and v4. The production v4 workflow-definition GET still returns 404 even with the PIT; exact workflow triggers/actions and source consumers remain unread. Browser access is unavailable.
- PIT email readback confirmed Alcohol and Cannabis Brands published workflow emails use direct calendar URLs with only `utm_source` and separate deck Trigger Links. The sampled appointment payload distinguished creator from assigned user: four non-null creator records resolved to Jason Bornillo, assigned user to Cameron Karkut, nine records had null creator IDs, and four had `rescheduledAt`. These facts do not justify using assigned owner as booker. Durable inventories and readback results are in [`docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md`](docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md) and its linked CSVs.
- Next: obtain supported production workflow-definition access; confirm active action-to-template/link mappings, click filters, source-field consumers, and redirect propagation; reconcile appointment date bounds and reschedule semantics; then finalize first-touch/latest-touch fields and an idempotent click ledger. Only then update shared templates/links or build click automation; validate with a controlled contact without sending campaign email or publishing a test automation. Preserve original acquisition source and keep clicks separate from bookings/SQLs. Preserve the 578 unnamed calendar-path historical gap unless source records establish more.

## CURRENT 2026-10-09 — inbound response → MQL / Sales Outreach requirement

- Ed requested that any inbound response result in the contact receiving the `mql` tag and having an opportunity in **Sales Outreach → New**, while avoiding a new opportunity when one already exists. Record this requirement for later implementation; current priority is the sequential setup of the remaining vertical campaigns below. No GHL workflow, n8n workflow, contact, or opportunity was changed or executed for it.
- Read-only GHL inspection of `WL - Micro - Stage MQL Opportunity Baseline` (`172e98e7-7dde-49fd-b32e-e1d98395484a`) found it **Published**, 750 total / 0 active at the workflow-list readback. Its trigger is specifically `Contact Tag` → `Tag added: mql`; actions POST contact details to `/webhook/ghl-mql-opportunity-baseline-v2` and send lead details to `/webhook/wl-slack-channel-update-v2`. This is not an inbound-response trigger and does not itself add the `mql` tag.
- The existing baseline runbook documents the n8n endpoint as ensuring an opportunity in `Warm → Qualified (MQL)` unless the contact already has an opportunity in `Sales`. That documented contract does not match the new request for Sales Outreach on any response. The downstream n8n implementation was not freshly read back through the required `n8n-lt` instance in this session; do not claim its current runtime behavior beyond the runbook.
- The published central `Customer replied` workflow is a stop-out path: it removes contacts from the four vertical campaigns. Its observed configuration does not apply `mql` or ensure a Sales Outreach opportunity.
- Before implementation, reconcile the request with the existing Janvi AI qualification gate / Warm-to-Sales Outreach promotion contract. Treat any existing opportunity in any pipeline as suppressing creation of a new one; confirm whether an existing non-Sales Outreach opportunity should be preserved or moved, and specify the destination stage. Keep processing idempotent across response channels.
- Detailed readback and ordered next steps: [`docs/sessions/2026-10-09-cannabis-sms3-correction-eos.md`](docs/sessions/2026-10-09-cannabis-sms3-correction-eos.md), “Inbound response → MQL and Sales Outreach opportunity review.”

## CURRENT 2026-10-09 — sequential setup for remaining vertical campaigns

- Ed wants to finish the remaining vertical automations one at a time, starting with email templates, SMS templates/snippets, and tags, then the same end-to-end setup used for Alcohol and the other verticals. Do not build all vertical workflows in parallel.
- Confirmed build order: **Crypto → Cannabis Dispensaries → Gambling → Peptides**. “Gambling” was the distinct vertical meant by the duplicate Crypto in the original list. Complete one vertical, including non-sending acceptance readback, before beginning the next.
- **Crypto current continuation (2026-10-09):** workflow `0a79d683-4374-432d-bc64-6c8272540041` remains Draft/Saved, 0/0. Its 20 email actions are bound to the five existing Crypto templates with branch-specific From Email, PDF subjects (Email 3 uses the corrected non-quantified subject), Cameron Karkut, and Sync enabled. Crypto Email 3's saved template preview no longer contains the unsupported 40%/16-month claims. All 12 SimpleTexting Webhooks have Crypto copy with `dryRun=true` and canonical endpoint/auth/payload keys. Four initial 1-day waits are connected before Email 1; the other 36 waits read back as `2/2/2/4/2/2/4/2/2` per sender branch. Eight voicemail actions retain the approved shared `V3.mp3`. All 292 source emails and 144 populated personal phone values returned no exact GHL matches; a balanced 73-per-sender assignment CSV is prepared, not applied. Ed approved adding Crypto to the shared published `Customer replied` removal workflow; it now selects Crypto plus the four existing campaigns. Ed chose terminal Email 5 → regular newsletter eligibility, no special three-month wait/re-entry. Remaining: non-sending acceptance, confirm eligibility/exclusion gates and full branch/exits, and reconcile historical imported contacts missing sender assignments (new pending task below). Full readback: [`docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md`](docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md). Do not import, set contact sender fields, apply entry tags, enroll, test, execute, send, call, or publish the Crypto workflow absent separate authorization.
- Crypto assets verified: email folder `Crypto Brands Multichannel - Oct 2026` (`6ac89bf91ea8584cd79f74db`) contains five saved HTML templates (IDs/names in [`docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md`](docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md)); the GHL Snippets UI showed one each of Crypto SMS 1–3 in the Crypto folder; all six campaign tags exist. Two accidental setup artifacts (a stray Vibe `New Template` and unfiled duplicate SMS 3) were deleted and the remaining intended assets were re-read. No contact received the entry tag. Do not recreate assets; first reread their saved preview/content and exact workflow compatibility.
- Mandatory email layout across every vertical: Arial 12px, 1.5 line-height; readable blank lines between paragraphs without repeating spacer blocks between every adjacent paragraph; at least two empty blocks after the greeting and at least two empty blocks between the final paragraph and closing/signature; standard unsubscribe footer. Verify exact PDF wording/subjects, approved claims, merge fields, links, and rendered saved preview. After final HTML edits, reselect/re-add the template in each corresponding Send Email action, accept the confirmation, enable **Sync Edits to Template**, save, and read back template, subject, From Name, literal branch From Email, and Sync for every action.
- Continue Crypto only until its non-sending acceptance is complete. Preserve the existing Crypto templates; do not modify shared Alcohol templates. The current remaining workflow tasks are eligibility/suppression gate readback, full branch/exit acceptance, and final status/history verification. Keep it Draft/unpublished/unenrolled. Do not import contacts, assign contact sender values, apply entry tags, test, execute, send, or call absent the relevant authorization.
- **New follow-up (Ed, 2026-10-09):** audit already-imported contacts with blank/missing campaign-specific sender fields, map each to the correct vertical/workflow, and prepare balanced sender assignments before proper workflow enrollment. This is pending; no historic contacts were searched or changed for this follow-up. Reconcile each campaign-specific sender field against the correct workflow and preserve sticky existing assignments before any separately authorized field/tag writes.
- Detailed Crypto state, exact asset IDs, ordered steps for the other three verticals, and a copy-ready prompt for the next LLM: [`docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md`](docs/sessions/2026-10-09-remaining-vertical-campaigns-crypto-eos.md).
- The response→MQL → Sales Outreach → New requirement above is documented but deferred until the remaining vertical setups are prioritized/completed.

## SUPERSEDED 2026-10-09 — SMS 3 correction continuation (active-contact impact check)

- Resumed from [`docs/sessions/2026-10-09-cannabis-sms3-correction-eos.md`](docs/sessions/2026-10-09-cannabis-sms3-correction-eos.md). Authenticated GHL access was recovered through the Launchpad and Cannabis workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377` was freshly reopened. Workflow list readback showed Published, 88 total / 41 active, last updated Oct 8 1:16 PM (UI local time). The Builder history first page showed nine entries at `Wait` / `Waiting For Time` and one finished entry, but those rows displayed next execution times on Oct 8 (already elapsed at this check). Treat current action/timing as unreconciled; do not infer these are safely waiting or assume their due times recalculate after graph edits.
- No graph edits, saves, publish actions, node payload edits, or webhook executions were made in this continuation. The checked Draft/Publish toggle state in the Builder was not used as a status determination; the workflow-list status is the authoritative UI readback. No exact action-by-action live-mode audit was completed for the 28 SMS actions.
- Ed's expanded authorization below supersedes the hold on correcting wrong waits and SMS3 across all four verticals. Preserve enrolled contacts; do not move them forward, remove/re-enroll, retag, or force actions to compensate.
- **Current remaining work:** reconcile Alcohol's saved graph order (Day13 SMS2 still precedes Day11 Email3) using a Builder edge-reconnection method that does not delete a step, then read back all four branches. Other vertical SMS3 payloads, SMS live modes, and cadence checks are recorded under the expanded authorization below. Preserve existing contacts; no additional initial wait before Day1 Email1.
- No production send, test, provider call, contact write, enrollment change, publish toggle, or workflow save occurred. Repository worktree had the pre-existing modified/untracked artifacts listed in the prior EOS; preserve them.

## CURRENT 2026-10-09 — expanded vertical wait/SMS 3 correction authorization

- Ed authorized correcting any wrong waits and SMS 3 messages across the vertical automations, including Alcohol, Cannabis, Nicotine, and Mushroom. Do not wait for a separate impact-treatment confirmation before correcting the authorized wait intervals; preserve existing enrolled contacts and do not force/remove/re-enroll/retag them.
- Ed clarified that **no additional initial wait is required before Day 1 Email 1**. Do not add one. Treat Email 1 as the first workflow action; verify subsequent intervals against each vertical PDF.
- **Alcohol fresh branch-order recheck (2026-10-09):** current saved workflow `2e8c2d78-aaec-4591-9b53-b0715be8c4ce` is Published version 38. Live edge traversal across `.com`, `.co`, `.agency`, `.org` confirms Day7 voicemail1 → Wait 4d → Day11 Email3 → Wait 2d → Day13 SMS2 → Wait 2d → Day15 Email4. This supersedes the preceding version-37 readback that still showed SMS2 before Email3. The current order is PDF-aligned.
- Nicotine version 40 (Published): all 12 Webhooks have `dryRun=false`; four SMS3 actions have PDF text with First Name/Company; waits are 4/2/2 for Day7→11, Day11→13, Day13→15; saved action order is Email3→SMS2. Cannabis version 73 (Published): all 12 Webhooks have `dryRun=false`; SMS1/SMS2 copy now uses PDF merge fields, SMS3 is exact, and saved cadence/order matches the source. Mushroom version 21 (Published) read back with all 12 Webhooks `dryRun=false` and correct SMS3/cadence.
- No workflow execution, test message, provider call, voicemail, or call was performed. Preserve enrolled contacts; do not force/remove/re-enroll/retag. No additional wait before Day1 Email1.

## CURRENT 2026-10-09 — Vertical SMS mode and campaign status refresh

- Latest authenticated list state: Alcohol Published, 338 total / 169 active; Cannabis Published, 88 / 41; Nicotine Published, 701 / 701; Mushroom Published, 117 / 0. Enrollment counts are not delivery proof.
- Saved in the expanded 2026-10-09 correction: all 12 SMS Webhooks in each of the four workflows are `dryRun=false` (48 total). Cannabis SMS1/SMS2 were aligned to the PDF's company merge-field wording, and all four SMS3 actions across Alcohol/Cannabis/Nicotine/Mushroom contain their vertical's PDF copy with the required merge fields. Readback verified exact Alcohol/Cannabis/Nicotine messages and Mushroom's previously saved copy. Canonical SMS endpoint/source/content-type/auth fields were not intentionally changed. No workflow was executed and no provider/test send, call, or voicemail was made.
- Saved wait fixes: Nicotine's gaps are now 2/2/2/4/2/2/4/2/2 days after the Day1 Email1 action; its Day11 Email3→Day13 SMS2 order is correct. Cannabis's saved branches and waits were verified chronological and PDF-aligned: Day1 Email1→SMS1→Email2→voicemail1→Email3→SMS2→Email4→voicemail2→SMS3→Email5, with two-day intervals except the four-day external LinkedIn gaps before Email3 and voicemail2. Mushroom's previously verified order and waits remain correct.
- Alcohol's four Day21 SMS3 actions remain PDF-correct and all 12 SMS Webhooks remain live-mode. Its newly read branch order and waits are correct as listed above.
- Saved GHL workflow versions were read back as Published: Alcohol version 38, Cannabis version 73, Nicotine version 40, Mushroom version 21. Preserve enrollments; do not add an initial wait before Day1 Email1. No workflow execution or provider invocation for verification.

## CURRENT 2026-10-09 — Cannabis early-exit re-entry request and inbound-stop check

- Ed deferred the shared SMS consent/STOP/DND and idempotency/provider-reconciliation reviews, voicemail-consent review, and three-month newsletter exit work for later. Do not make these launch-readiness items a blocker for the current request.
- Fresh GHL workflow-list readback confirmed `Transparent eCom - Stop Outbound on Inbound Communication (All Verticals)` (`54dc6321-ed85-4eee-870d-0716c73c66fb`) is **Published**, 8 total / 0 active. Builder readback shows a `Customer replied` trigger with no filters and a `Remove from Workflow` action selecting Alcohol, Cannabis, Nicotine, and Mushroom. No contact/enrollment writes were made. This confirms the published customer-reply stop path; the Builder evidence does not establish how Call Details or every custom provider is covered.
- Fresh Cannabis enrollment-history readback showed the current eligible cohort waiting at the sequence Wait (displayed next action Oct 10) and finished entries with current action `No Action`. Execution-path samples showed one finished record taking the qualification-gate default/None branch (it had exclusion tags) and another taking the sender-router None branch on an earlier enrollment; that contact now has a later active wait enrollment and an assigned Cannabis sender. Those examples are not candidates for another enrollment. No evidence so far shows an eligible contact who exited after an outbound action and lacks a current active enrollment; therefore no contacts were re-entered or retagged in this check.
- **Re-entry decision:** do not re-enter the finished/No Action rows merely because they are Finished. The sampled exits are entry qualification/sender routing outcomes, and re-triggering them without checking tags/current sender/active enrollment could re-enroll excluded or already-active contacts. Preserve the 41 active wait enrollments. If a specific remaining contact is identified as eligible, lacks an active entry, and exited before the sequence due to a graph-edit failure, re-enter only that reconciled contact through the authorized entry path.

## CURRENT 2026-10-08 — Vertical outbound automation build pattern and EOS

- **Current campaign workflows (location `Zwz4relUXVPxx8uohnjV`):** Cannabis `5d1236a2-1b98-4b7f-9621-5d4f7749f377`, Mushroom `f1280d4b-ac8f-4353-b3c1-f874f7202bdb`, and Nicotine `e42cee9c-3c0d-474b-8d78-83cd10e9c620`. Cannabis and Nicotine were confirmed Published with last workflow-list counts 41 and 701 active enrollments. Mushroom's latest recorded closeout is Saved/Draft, unpublished, with zero enrollment/log rows in the visible 60-day view. Confirm current state before changes. Enrollment is not delivery proof.
- **Eligibility gates freshly read back and saved/published (2026-10-08):** Mushroom requires `Vertical=Mushroom`, excludes tags `do not contact` and `do not nurture`, and excludes DND channels `Email` and `Call`; Cannabis retains `Vertical=Cannabis` plus its existing separate AND exclusions `dispensaries_pool` and `enrollment queue - dan - dispensaries`, with the same new tag and DND conditions; Nicotine requires `Vertical=Nicotine` plus the same new tag and DND conditions. Ed accepted the GHL multi-select condition behavior; preserve these same selections when matching the gate. No other workflow nodes or contacts were changed in this session.
- **2026-10-08 sequence audit: partial; fixes required next session.** Source PDFs and all three canvases were reviewed, but not every action panel/edge was read in the latest pass. Nicotine's saved-state readback flags Day 13 SMS 2 before Day 11 Email 3, missing Day 21 SMS 3, and final waits of 4 days instead of the specified 2. Cannabis also has a recorded Day 13-before-Day 11 ordering defect; freshly verify all four branches and associated waits. Mushroom's latest saved closeout records corrected chronological paths, including Day 11→13→15 and Day 19 voicemail→Day 21 SMS 3→Day 23 Email 5; verify each branch independently before acceptance. Full ordered fix/verification plan is in `Project Status and Next Steps.md`, “Vertical outbound workflows — sequence audit findings and next-session repair plan.”
- **Next-session rule:** LinkedIn steps are handled by a separate automation and must not be added to these outbound workflows. Inspect/trace all four branch graphs against each vertical's own PDF; exact cadence when LinkedIn is external: Day 1 Email 1 (+1d from entry), Day 3 SMS 1 (+2d), Day 5 Email 2 (+2d), Day 7 voicemail 1 (+2d), Day 11 Email 3 (+4d), Day 13 SMS 2 (+2d), Day 15 Email 4 (+2d), Day 19 voicemail 2 (+4d), Day 21 SMS 3 (+2d), Day 23 Email 5 (+2d), then newsletter nurture for 3 months. Audit email templates/subjects/sender/sync, exact SMS Webhook text and canonical contract (`dryRun=true`), voicemail asset/placement/consent/phone/failure behavior, entry/gate/router/None paths, exits and newsletter handling. Do not infer correct sequence from node labels. No tests, enrollment writes, executions, sends, calls, or live-mode changes during audit/repair planning. Cannabis/Nicotine have active enrollments: account for contacts already waiting and obtain a scoped change plan/explicit authorization before saving or publishing graph changes. Preserve existing campaign state and all SMS dry-run values.
- **Reusable workflow setup:** for later verticals, start from the closest existing multichannel workflow by sequence/channel graph and duplicate that workflow (or ask Ed to duplicate it in GHL if that is the preferred UI path), rather than building from scratch. Before saving/publishing, change and verify the vertical-specific entry tag, `Vertical` gate, campaign exclusion tags, sender custom field and all four exact sender branches, email templates/subjects and node sync, SMS copy while retaining canonical SimpleTexting endpoint/auth/payload and dry-run, and voicemail/consent gates. Preserve existing campaign-specific IDs/tags and active enrollments; never copy a live mode or publish without explicit authorization. GHL Builder uses a cross-origin `workflow-builder` iframe; the outer URL may display HTTP 404 while the authenticated canvas is usable, so inspect/wait for the iframe and verify its Saved/Published UI state.
- Handoff/details: [`docs/sessions/2026-10-08-mushroom-workflow-kickoff.md`](docs/sessions/2026-10-08-mushroom-workflow-kickoff.md) and [`Project Status and Next Steps.md`](Project%20Status%20and%20Next%20Steps.md), section “Vertical outbound workflows — sequence audit findings and next-session repair plan.”

## CURRENT 2026-10-08 — Apollo phone enrichment for all-vertical leads

- **Standing intake rule:** new lead cohorts uploaded for any vertical must be queued for Apollo Phone Enrichment after contact import and identity reconciliation. Before setting `Enrich Phone via Apollo = Yes`, preserve every provided source phone in the GHL `Corporate Phone` custom field (`036gD9ds9P5V8VUHnFBP`). This matters because a successful Apollo callback updates the primary GHL `Phone`; the source number must remain available as the company-line value. Do not clear primary Phone as part of this process unless separately reviewed.
- **Batch method:** import contacts first, then use a separate GHL CSV update keyed by Contact ID to set `Enrich Phone via Apollo = Yes`. The worker schedule is currently paused by an Apollo `insufficient credits` response; target pace is every 5 minutes, maximum 10 contacts/run, with current diagnostic cap 1. Phone results return asynchronously through Callback Handler V4. Verify status/provider outcomes before claiming completion. Avoid re-queuing contacts already enriched or terminal without a deliberate retry decision.
- **Current October all-vertical cohort (source count; import status not reconciled):** source `New Campaigns October 2026/Export_Contacts_All Verticals Oct 2026 Outbound_Oct_2026_8_24_PM.csv` has 914 unique contacts; 135 source Phone values and 779 blank. Courtney McElligott (`FTCWeS26CKKKGDCOTIWS`) was the one-contact live test and is excluded from the batch files. Live GHL readback showed Apollo status `enriched`, `Enrich Phone via Apollo = No`, and the Apollo-provided primary phone populated; her prior source number remains in Corporate Phone. n8n-lt poller `JH8ShfpglWmLMZ3l` was active with matching draft/active version `d3ddd510-1157-42a5-b640-44c058fc7c5b`; successful execution `1109436` processed her contact.
- **Apollo rate-limit follow-up (2026-10-08):** a read-only `n8n-lt` review at 12:54 UTC found a burst of at least 100 poller execution errors and at least 100 queued executions. Sample execution `1110315` failed while fetching a GHL contact with HTTP 429. GHL-originated requests were reaching the active poller webhook at `ghl-apollo-phone-enrichment-intake-v3`; this shows the GHL `WL - Apollo Phone Enrichment Trigger` caller is still invoking the webhook, so do not describe it as unused. A later read at 13:31 UTC found the poller and Callback Handler V4 active with matching versions, no `new`/`running` rows returned for either, poller successes through 13:16 UTC and callback successes through 13:09 UTC; the latest 100 poller errors remained from the 12:55 burst. Treat the immediate burst as recovered but unresolved; inspect all affected contact statuses and identify what initiated the webhook volume before another mass queue. Do not re-import the queue CSV as a retry.
- **Later 2026-10-08 follow-up:** version `22d24fe4-1026-4a7b-a487-99590d10648f` consolidated profile match and phone reveal to one API request/contact. The first scheduled run `1111574` scanned 10, all returned `apollo_error`; fresh GHL reads found trigger flag `Yes`/status `error` on all 10. Schedule was paused to prevent repeat attempts; current workflow version `9c8c63ab-588d-4519-925f-72469781d05c` is active with the Schedule Trigger disabled and webhook ack path retained. Do not reset flags—the worker selects `Yes` regardless of status. Diagnose the request error before resuming. A second Apollo Usage Stats read showed 0 `people/match` consumed; exact rejection cause remains unresolved.
- **Resume diagnostic / re-pause (2026-10-08):** Ed requested resuming; schedule was temporarily enabled at 5 minutes/max 1, and Code began recording only sanitized HTTP status/error code. Natural execution `1111794` at 15:05 UTC scanned one contact and again returned `apollo_error`; no HTTP status/error code was captured. The trigger remains Yes. Schedule was disabled again to prevent repeated failures; current active version is `7cdef5ce-c3be-4cff-95fd-e8b17f594538`, webhook acknowledgement path retained. At 15:08 UTC no `new`/`running`/`waiting` executions were returned. Do not reset/re-import; diagnose the Apollo request before re-enabling.
- **Apollo credit blocker (2026-10-08 16:08 UTC):** a controlled one-contact call using the documented Apollo path returned HTTP 422 `insufficient credits`, no person match, and no phone callback. Current active workflow version is `9c135647-525c-41ed-b809-84cd4a88eea7`, Schedule Trigger disabled, webhook ack-only. Failed contacts remain `Enrich Phone via Apollo=Yes` / status `error`; no reset/re-import is needed. Add credits/adjust the Apollo plan before enabling again; start at maxPerRun=1, verify a successful callback, then scale toward 10.
- **Final diagnostic state (2026-10-08 16:08 UTC):** the Apollo request path now uses the documented `/api/v1/people/match`, with `reveal_phone_number`, `reveal_personal_emails`, and encoded `webhook_url` in the query string. A controlled request returned HTTP 422 `insufficient credits`; this is the actual resume blocker, not a rate-limit response. Poller `JH8ShfpglWmLMZ3l` remains active with schedule disabled at version `9c135647-525c-41ed-b809-84cd4a88eea7`, maxPerRun=1, webhook ack-only. Error-status contacts still have trigger flag Yes, so do not reset/re-import. Add Apollo credits/adjust plan, then resume with one contact and verify its callback before scaling.
- **Security follow-up:** detailed execution diagnostics exposed webhook authentication material in the inspection output, and the poller Code node contains a hard-coded callback key. Treat affected webhook/callback key(s) as exposed; do not copy values into notes. After identifying/reconciling pending Apollo callbacks, rotate the affected key(s), migrate the literal to restricted configuration, and update/verify the callback validator and caller. Do not rotate blindly while callbacks may still be outstanding.
- **Prepared all-vertical files:** `New Campaigns October 2026/GHL Import Prep/All Verticals - Preserve Existing Phones as Corporate Phone.csv` has 134 source-phone values; `All Verticals - Apollo Phone Enrichment Queue.csv` has 913 Contact ID / Yes rows. They were prepared locally; current GHL import completion is **not reconciled** after the webhook burst. Compare Corporate Phone values before overwriting and inspect all cohort statuses before deciding whether to import/retry.
- Session handoff: [`docs/sessions/2026-10-08-all-vertical-apollo-phone-enrichment.md`](docs/sessions/2026-10-08-all-vertical-apollo-phone-enrichment.md). Future all-vertical imports should follow this process; detailed live workflow background remains in the Apollo section below and the Pipeline Process Training Guide.

## CURRENT 2026-10-08 — Mushroom contact cohort and auto-mapped Apollo import prep

- Ed directed reclassification of the seven existing exact-email GHL matches from the Mushroom source. All seven now read back as `Vertical=Mushroom`; only that custom field changed. Jill's two differing source rows resolve to one GHL contact. Existing tags/enrollment state were deliberately preserved; some retain Cannabis-sequence tags and Aaron retains Emerald-sequence tags. They were not enrolled into Mushroom.
- Five of the seven existing contacts have no Apollo status/flag and no primary phone; they are staged in `New Campaigns October 2026/GHL Import Prep/Mushroom Existing Contacts - Vertical and Apollo Phone Enrichment.csv` as Contact ID + Vertical Mushroom + Enrich Phone via Apollo Yes. Jill and Christopher are already Apollo `enriched`; skip them rather than requeue.
- The 111 net-new Mushroom records are staged in `Mushroom New Contacts - Auto-Mapped + Apollo Phone Enrichment.csv`; 94 supplied phone values are mapped to Corporate Phone and all 111 have Apollo flag Yes. This is a new header-normalized copy; the original prep files remain for audit. The GHL import wizard's field-mapping preview has not yet been checked.
- No Mushroom contact import or Apollo queue update has occurred. Reconcile the Apollo 429 burst noted above before importing either Apollo-flagged file. Keep existing contacts out of the create-contact CSV to avoid duplicates. Full handoff: [`docs/sessions/2026-10-08-all-vertical-apollo-phone-enrichment.md`](docs/sessions/2026-10-08-all-vertical-apollo-phone-enrichment.md).

## CURRENT 2026-10-08 — Jason follow-up email booking links and trigger-link audit

- Updated all six GHL email templates in `Jason Follow Up Emails` (`69e0c9069af5986541802d88`) to use Ed's requested booking URL `https://api.leadconnectorhq.com/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=followupemails` for booking CTAs. Template IDs: `69e0d86b9af59801b580f4b5`, `69e0db27d6a707bbf190d022`, `69e0db9ab02114c1ba3c29d3`, `69e0dc56d6a707c0ac90e074`, `69e0dcad8ffabf47b4d987c5`, `69e0ddd0b021145bab3c4569`. Saved Firebase preview readback confirmed the requested URL in all six (1/1/2/1/2/2 booking CTA occurrences respectively). No other links were intentionally changed.
- The only remaining `trigger_link` merge token found across those six saved previews is `{{trigger_link.fRvpZgP1WOghlgY1ARiB}}`, used for the logo/site link in all six. GHL's documented Trigger Links API returned 15 location links; `JohnWebsiteLinkInFollowups` exists and redirects to the LiveTransparent homepage with its existing outreach tracking parameters. No broken/missing trigger-link references were found in these templates.
- Ed asked whether this trigger link has a workflow automation. This remains **unverified**: no workflow trigger/action readback was available during this session, and repository search found no associated automation reference. Do not claim an automation exists or does not exist; inspect GHL Workflow triggers for this exact link ID/name next.
- **Important propagation check:** the template-library HTML was updated directly via the documented GHL template endpoint; no Send Email action was reselected or read back in the associated GHL workflow(s). Although Ed said the workflow action is synced, verify action linkage / Sync Edits to Template in GHL before claiming workflow propagation. Do not send a test email or publish/change a workflow without separate authorization.
- Exact session record: [`docs/sessions/2026-10-08-jason-followup-email-links-closeout.md`](docs/sessions/2026-10-08-jason-followup-email-links-closeout.md). No repo code/tests/deployments changed; the existing worktree had unrelated Nicotine/Mushroom documentation and import-prep artifacts and remains unstaged.

## CURRENT 2026-10-08 — Nicotine enrollment and Mushroom workflow draft handoff

- **EOS status refresh (2026-10-08):** The authoritative Mushroom status and next actions are in [`docs/sessions/2026-10-08-mushroom-workflow-kickoff.md`](docs/sessions/2026-10-08-mushroom-workflow-kickoff.md), section “EOS closeout — current state and remaining plan.” The latest verified campaign workflow has all 20 email actions mapped and synced, chronological cadence through Day 23, and four Day 21 SMS 3 nodes. It remains Saved/Draft and unpublished with no enrollment/execution rows in the visible 60-day window. The earlier bullets in this section about 8/20 mappings, absent SMS 3, and Day 13 preceding Day 11 are historical snapshots superseded by the later verified continuations. Do not treat draft completeness as send readiness: consent/suppression, idempotency/provider reconciliation, voicemail, newsletter re-entry and cross-channel stop gates remain unresolved.
- **Historical cross-vertical live-mode audit (2026-10-08; superseded by the Oct 9 correction above):** the prior snapshot recorded 36 Webhooks at `dryRun=true` and the inbound-stop workflow as Draft. Do not treat those states as current; see the Oct 9 saved-state readback.
- Ed confirmed `Nicotine` and `Mushroom` as GHL `Vertical` options; official contact-field readback verified them. The Nicotine and Mushroom source PDFs and lead CSVs are now present under `New Campaigns October 2026/`.
- **Mushroom workflow / closeout handoff (2026-10-08; latest verified state):** source files are `Mushroom - Multi Channel Outbound Sequence.pdf` and `Mushroom Brands Leads - Leads (1).csv` (119 rows). Mushroom sender field `contact.lt_campaign_mushroom_brands_oct_2026_sender_email` (`IJ1yrUihuKD7DkLgWHYM`), entry tag `lt_campaign_mushroom_brands_oct_2026_enroll`, and Draft workflow `f1280d4b-ac8f-4353-b3c1-f874f7202bdb` are in place. Email folder `6ac68858e6a28b9ad5b636f9` contains Vibe Email 1 `6ac69ed31ea8584cd76f300c`, Email 2 `6ac6a19c1061d40a3a3d781a`, Email 3 `6ac6b8ea1a45a2bc8b2b7bca`, Email 4 `6ac6ba1564b77b4db660c5b5`, and Email 5 `6ac6bb429ed784b5df0ee312`; incomplete Design Editor Email 1 duplicate `6ac688ad64b77b4db65ac1e9` was deleted. Firebase preview verified Emails 3–5; Email 5 generic starter content was replaced in place through the documented template PATCH endpoint and the fresh saved preview now contains only intended Mushroom copy, deck CTA, merge fields, and unsubscribe footer. Email 3 quantified claims remain unapproved and held from launch. Verified Trigger Link `{{trigger_link.7UI7BG20vv4l4VsNpYQj}}` is `Mushroom_Deck_Outbound` and resolves to the Mushroom deck Drive URL. The Conversations Snippets folder `Mushroom Brands Multichannel - Oct 2026` contains three SMS snippets. All eight existing SimpleTexting Webhook actions have Mushroom SMS 1/2 copy; all retain `dryRun=true`, with no provider calls. Four Day 1 Email 1 actions and four Day 5 Email 2 actions are mapped to their Mushroom Vibe templates with PDF subjects, Cameron Karkut, branch sender addresses, and Sync Edits enabled. Workflow remains Saved/Draft; no contacts were imported/updated/sender-assigned/tagged/enrolled, and no email/SMS/voicemail test or send occurred. Outstanding: map the remaining 12 email actions; hold Email 3 claims pending evidence/approval; add Day 21 SMS 3; fix Day 13-before-Day 11 ordering; complete voicemail/SMS/email suppression, consent, idempotency/provider gates; reconcile/import cohort; explicitly authorize live sends before any activation. Keep LinkedIn centralized and `Stop Marketing` future. CSV duplicate `jill@foursigmatic.com` resolves to existing Cannabis contact `rk6jqv9xpKLZSmOYG3Xc`; both source rows held. See [`docs/sessions/2026-10-08-mushroom-workflow-kickoff.md`](docs/sessions/2026-10-08-mushroom-workflow-kickoff.md) for ordered next actions.
- **Mushroom continuation (2026-10-08; historical checkpoint, superseded by EOS status refresh below):** authenticated Builder read at that point confirmed the draft, 12 Email 3–5 actions mapped, eight SMS actions with `dryRun=true`, and the cohort preflight (7 existing Cannabis matches; 111 new contacts prepared; sender balance 28/28/28/27). Its notes that cadence was incorrect and Day 21 SMS 3 absent were subsequently superseded by the later verified continuations. No imports or GHL contact/sender/tag/enrollment changes occurred. Exact current plan and remaining gates: [`docs/sessions/2026-10-08-mushroom-workflow-kickoff.md`](docs/sessions/2026-10-08-mushroom-workflow-kickoff.md).
- **Mushroom cadence correction / latest verification (2026-10-08; supersedes the immediately preceding cadence status):** Ed reordered the graph and manually wired all four Day 13 SMS 2 → Day 15 Wait → Email 4 branch tails. Fresh edge readback confirms the path in `.com/.co/.agency/.org`. The Builder is Saved/Draft, publish toggle off; enrollment history/execution logs show no rows in the last 60 days. Waits are labeled with target day/action: Day 7 Voicemail 1→Day 11 Email 3 = 4 days; Email 3→SMS 2 = 2 days; SMS 2→Email 4 = 2 days; Email 4→Day 19 Voicemail 2 = 4 days. Earlier gaps are 2 days (Day1→3, Day3→5, Day5→7). LinkedIn remains external. No production send or enrollment occurred.
- **Mushroom Day 21 SMS 3 draft (2026-10-08):** four duplicate SMS Webhook actions were repurposed as Day 21 SMS 3 with PDF final-bump text and First Name/Company Name merge chips. All retain canonical SimpleTexting endpoint, `source=sms`, auth header, and `dryRun=true`. Fresh Builder readback confirms each branch is Day 19 Voicemail 2 → Day 21 Wait (2 days) → SMS 3 → Day 23 Wait (2 days) → Email 5. Workflow remains Saved/Draft and unpublished; enrollment/execution history is empty for the last 60 days. Consent/STOP/DND/suppression gates remain prerequisites; no provider calls or contact writes.
- **Historical inbound-stop workflow snapshot (2026-10-08; superseded):** the prior readback called `Transparent eCom - Stop Outbound on Inbound Communication (All Verticals)` (`54dc6321-ed85-4eee-870d-0716c73c66fb`) Draft/unpublished. The Oct 9 fresh workflow-list readback instead showed Published, 8 total / 0 active; its `Customer replied` trigger has no filters and its Remove from Workflow action selects the four vertical campaigns. This verifies the reply-stop path; the Builder does not establish Call Details or every custom-provider path.
- **Historical SMS live-mode/readiness audit (2026-10-08; superseded):** earlier `dryRun=true` and Mushroom Draft observations are replaced by Oct 9 saved-state versions above. Ed later deferred the shared consent/STOP/DND and idempotency reviews; do not treat them as a blocker for the authorized wait/SMS3 correction request.
- **Cross-vertical SMS webhook plan:** every campaign SMS Webhook action intended for live delivery must be updated from dry-run payload mode (`dryRun=true`) to live mode (`dryRun=false`) across **all verticals**, not just Mushroom/Nicotine. Inventory and verify every branch/action by vertical, retain the canonical SimpleTexting endpoint/auth/payload contract, and do not invoke or enable live sends until consent/STOP/DND, suppression, idempotency/provider reconciliation, and explicit live-send authorization are satisfied. The Nicotine/Mushroom campaign notes currently report their SMS nodes as `dryRun=true`; no setting was changed by recording this requirement.
- **Nicotine workflow** `e42cee9c-3c0d-474b-8d78-83cd10e9c620` was published by Ed on 2026-10-08. In the authenticated Playwright Builder, saved the entry trigger `Entry - Nicotine Brands Multichannel Oct 2026` with tag-added filter `lt_campaign_nicotine_brands_oct_2026_enroll`; eligibility requires `Vertical = Nicotine` (`Eligibility gate - Nicotine` / `Eligible - Nicotine`); sender router `Sticky sender route - Nicotine campaign field` uses `contact.lt_campaign_nicotine_brands_oct_2026_sender_email` and exact `.com`, `.co`, `.agency`, `.org` branches renamed Cameron Nicotine. Converted all 20 native Send Email actions to the corresponding Nicotine templates/subjects, preserved Cameron Karkut and the four literal sender addresses, and enabled Sync Edits to Template on all 20. Fresh readback of each action verified template name, exact subject, From Name/Email, and Sync=true. All eight existing Webhook SMS actions are also updated with Nicotine SMS 1 (Day 3) or SMS 2 (Day 13) copy across the four branches; they retain the canonical SimpleTexting endpoint, payload/auth field names, and `dryRun=true`. Day 21 SMS 3 remains absent. The 2026-10-08 EOS readback found 78 nodes, four final waits at 4 days, and the saved sequence order has Day 13 SMS 2 before Day 11 Email 3. An earlier history view showed contacts at the initial Wait (leading to Day 3 SMS 1), but a later fresh last-60-day history view showed “No enrollments found”; reconcile this discrepancy and delivery history rather than inferring enrollment state. Do not reapply the tag or claim delivery. Ed confirmed the shared `V3.mp3` voicemail asset is used across vertical automations and that the SimpleTexting webhook key does not need rotation. Ed clarified that LinkedIn belongs in a later, separate all-vertical workflow. Standard GHL unsubscribe links are present; cross-channel `Stop Marketing` is planned but not implemented. Detailed ordered TODOs: [`docs/sessions/2026-10-07-nicotine-multichannel-build-handoff.md`](docs/sessions/2026-10-07-nicotine-multichannel-build-handoff.md).
- **GHL CSV import attestation — standing operator confirmation (2026-10-08):** Ed confirms that any list he directs us to import, across all verticals, meets the Contacts CSV importer attestation: contacts consented, were contacted within the past year, and the list is not from a third party. Do not ask him to confirm this again for each list. The importer still requires its checkbox; check it when Ed has directed the import, and do not use an alternate route to bypass the UI.
- **Nicotine import (2026-10-08):** read-only reconciliation/preparation found 741 rows, 727 unique nonblank emails, 14 missing emails, and no duplicate source emails. Exact GHL email reconciliation found 3 existing matches, all `Vertical = Cannabis`; these were excluded to preserve Cannabis. Held 24 clear cessation/advocacy/non-brand rows and 13 otherwise-in-scope records missing email. Imported 701 new email-addressable contacts (`Vertical = Nicotine`) via GHL CSV import; import history completed with 701 records found, 0 errors. A second CSV import assigned the Nicotine campaign sender field to all 701, balanced `.com/.co/.agency/.org` = 176/175/175/175; a read-only post-import audit confirmed all 701 Vertical values and sender values. Ed subsequently applied the entry tag and published the workflow; authenticated enrollment-history readback shows contacts enrolled, but full history totals and delivery are not reconciled. Do not repeat tag writes. Phone preflight found 61 shared source Corporate Phone groups across 538 source rows; shared values were kept in the `Corporate Phone` custom field and excluded from primary-phone updates. A separate 110-row unique/no-existing-collision primary-phone update import completed with 1 reported error; **which row failed and exact post-update phone counts are not yet reconciled**. Do not claim the phone update is complete until that single error is investigated and primary phone uniqueness is rechecked. No Apollo Phone Enrichment workflow was run. Prep/audit artifacts are in `New Campaigns October 2026/GHL Import Prep/` and `scripts/audit_nicotine_import.py`.
- Created/read back dedicated Nicotine Email Templates folder `6ac62f057a16a0bf6ec4cf33` containing five saved HTML templates: Email 1 `6ac6356a7a16a0bf6ec53d6e`; Email 2 `6ac63add647447b57a5700cd`; Email 3 `6ac63bde647447b57a57151f`; Email 4 `6ac63ca6f94e3d0736b558fb`; Email 5 `6ac63d811a45a2bc8b1b8e7a`. All 20 action-level links now point to the corresponding Nicotine template with sync enabled. A separate SMS Snippets folder `3Or7iiqyhva4YR703Fdo` contains all **three** Nicotine text snippets. Snippets are copy references; Ed requires actual SMS delivery through the **SimpleTexting webhook**, not GHL's native SMS app. All eight existing SimpleTexting Webhook payloads now use Nicotine SMS 1/2 copy; they remain `dryRun=true`, so these draft changes do not constitute SMS delivery.
- Ed approved retaining the Nicotine PDF claims and supplied `{{trigger_link.wDSwphO1pOZgj8by70bA}}` for the Email 2/5 CTAs; Trigger Links UI readback confirms it is `Nicotine_Deck_Sequence` and resolves to the nicotine deck Drive URL. The source PDF/Doc remains unchanged; the Email 1 company link uses `https://livetransparent.com/`, and checklist links in Email 1/2/3 use `utm_source=nicotineemailcampaign` as Ed directed. Email templates now follow the reference Alcohol HTML layout: Arial 12px, 1.5 line-height, adjacent paragraphs without spacer blocks between each, two empty blocks after greeting and before sign-off, and standard unsubscribe footer. Saved Firebase preview readback confirms no starter content and exact corrected destinations. After any template edit, reselect it in every corresponding Send Email node, accept confirmation, enable **Sync Edits to Template**, save, and read back.
- Created Nicotine trigger-link attribution workflow `Nicotine Trigger Link Source Attribution - Oct 2026` (`963bf85a-cdff-4eb1-90ea-6a473fb0f32f`) by duplicating the Alcohol reference `Alcohol Trigger Link Source Attribution - Oct 2026` (`a707d0b6-0717-4903-8b38-3510504a4136`). Its trigger is `Trigger link clicked` filtered to `Nicotine_Deck_Sequence`; its action updates Contact source to `Nicotine Brands Multi-Channel Outbound - Oct 2026`. Ed explicitly requested publication; published via the GHL Builder and workflow-list readback confirms **Published**, 0 total enrolled / 0 active enrolled. No test or contact update was performed. This is separate from the unpublished Nicotine multichannel campaign workflow.
- **Nicotine EOS readback (2026-10-08):** fresh authenticated Builder read confirmed campaign workflow `e42cee9c-3c0d-474b-8d78-83cd10e9c620` Published/Saved with 78 nodes, no Day 21 SMS 3, and four final pre-Email-5 waits still at 4 days. Saved sequence order currently places Day 13 SMS 2 before Day 11 Email 3. The current last-60-day history and execution-log views both said “No enrollments found” / “No logs found,” conflicting with an earlier Oct 8 history view showing contacts at the first Wait; reconcile before editing or inferring enrollment. Attribution workflow `963bf85a-cdff-4eb1-90ea-6a473fb0f32f` remains Published/Saved; its visible history showed no enrollments. Ed confirmed the shared `V3.mp3` voicemail asset is acceptable and no SimpleTexting webhook key rotation is needed. No saved workflow/contact changes occurred; temporary unsaved Builder edits were discarded and post-reload readback confirmed original values. Detailed ordered TODOs are in [`docs/sessions/2026-10-07-nicotine-multichannel-build-handoff.md`](docs/sessions/2026-10-07-nicotine-multichannel-build-handoff.md). Preserve SimpleTexting `dryRun=true`; LinkedIn remains future centralized workflow work.

## CURRENT 2026-10-07 — Alcohol and Cannabis enrollment closeout; next verticals

- **Sender assignment precedes enrollment:** keep this order for every imported vertical list: reconcile/import and verify `Vertical`; assign and read back the campaign-specific sender field; then apply the campaign entry tag. Do not use the shared `marketing_sender_email` field. Keep existing assignments sticky and balance only new contacts across the four approved addresses.
- **Alcohol + Cannabis cohort tags applied:** after sender-field readback, confirmed 169 unique Alcohol CSV contacts (Vertical Alcohol; sender counts `.com/.co/.agency/.org` = 43/42/42/42) and 44 unique Cannabis CSV contacts (Vertical Cannabis; 11 each). All 213 tag writes returned success: Alcohol `lt_campaign_alcohol_brands_oct_2026_enroll`; Cannabis `lt_campaign_cannabis_brands_oct_2026_enroll`. The entry tags were absent before this action, so no separate removal write was needed. Both workflows are published. `Allow re-entry` is now ON and saved in both; `Allow multiple opportunities` remains OFF; `Stop on response` remains ON.
- **Enrollment-history readback:** both workflows show new campaign entries dated 2026-10-06 around 1:49 p.m. PDT. On the visible first page, Alcohol entries were at `Wait` / `Waiting For Time`, with next execution around 2026-10-08 1:49 p.m. PDT. Cannabis showed 9 visible `Wait` / `Waiting For Time` rows and one `No Action` / `Finished` row; the saved eligibility gate excludes `dispensaries_pool` and `enrollment queue - dan - dispensaries` (3 of this 44-contact cohort were previously identified with the latter tag). Full history-page totals were not reconciled, and no email-delivery confirmation was read. Earlier “No enrollments found” snapshots were from the canvas before its enrollment-history data finished loading; do not rely on those stale empty snapshots.
- **SMS / voicemail failure behavior remains unverified:** inspected standard outbound Webhook and voicemail action panels; neither exposed a continue-on-failure control. HighLevel's standard outbound Webhook docs direct operators to execution logs for errors but do not state whether this configured action advances the workflow after an HTTP failure. The Custom Webhook skip/retry description is for a different action and cannot be assumed here. The voicemail guide likewise does not specify continuation after an invalid/unreachable number. In the next review, inspect GHL execution logs plus the SimpleTexting/provider result for any failures and determine whether later nodes ran. Do not induce a failure on live contacts; use docs or a safely isolated internal test after explicit authorization. Add/verify phone eligibility and consent gates before SMS or voicemail touches.
- **Alcohol SMS state:** all 8 existing SMS webhook nodes (four Day 3, four Day 13) were updated with Alcohol copy and the correct 30-minute booking URL; saved/published. The campaign's planned Day 21 SMS 3 is still absent from the workflow. Do not mistake successful webhook execution for SMS delivery; reconcile provider outcomes. No manual test SMS, voicemail, or email was sent during this closeout.
- **Readiness caveat:** enrollment/tag success does not mean every contact is actively progressing or that delivery occurred. Cannabis exclusion contacts can finish at the gate. The Alcohol plan still flags starter content in email previews and unresolved claims/destinations; both campaigns retain additional suppression, channel-consent, and failure-reconciliation gaps. Inspect the complete enrollment histories and confirm the exact first-email content/schedule before claiming delivery.
- **Email template formatting and node sync:** preserve readable blank lines between paragraphs. Each template must have at least two empty lines after the greeting and two empty lines between the final paragraph and the closing/signature. After editing a template, reselect/re-add the correct template in every corresponding Send Email node, accept GHL's confirmation dialog, then tick **Sync Edits to Template** on every Send Email node and save. Read back the saved node/template linkage and sync setting; do not assume editing a library template updated an already-linked node.
- **Next session:** continue Mushroom per the ordered closeout checklist in [`docs/sessions/2026-10-08-mushroom-workflow-kickoff.md`](docs/sessions/2026-10-08-mushroom-workflow-kickoff.md); the source list has been found. Do not reuse Alcohol/Cannabis tags, sender fields, or workflows.
- Detailed campaign records: [`docs/sessions/2026-10-06-alcohol-brands-multichannel-ghl-campaign-plan.md`](docs/sessions/2026-10-06-alcohol-brands-multichannel-ghl-campaign-plan.md), [`docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md`](docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md), and [`docs/sessions/2026-10-07-alcohol-cannabis-enrollment-eos.md`](docs/sessions/2026-10-07-alcohol-cannabis-enrollment-eos.md).

## SUPERSEDED 2026-10-07 — Multichannel vertical list sender assignment (pre-enrollment reapplication)

- **Required import order for every vertical campaign:** reconcile/import the contacts and confirm `Vertical`; assign each contact the campaign-specific sender field; verify the assigned value; only then apply that workflow's entry tag. Do not add an entry tag before sender assignment, because the published campaign routers branch on the dedicated field and a blank value takes the `None` path.
- **Sticky balanced rotation:** use the four approved email identities `cameron@livetransparent.com`, `.co`, `.agency`, and `.org` in a balanced round-robin. Keep one assigned address on a contact for every email in that campaign. For later lists, retain existing assignments and continue balancing new contacts against cumulative sender counts; never reshuffle prior contacts. If senders or capacity change, check with Ed before changing the rotation.
- **Use campaign-specific fields, not the shared field:** Alcohol uses `contact.lt_campaign_alcohol_brands_oct_2026_sender_email` (`AIzg8FR3PEDr7PSGMuXN`); Cannabis uses `contact.lt_campaign_cannabis_brands_oct_2026_sender_email` (`qoQxuEiX5kwKvvrOvDVm`). Do not substitute shared `contact.marketing_sender_email` (`wjV8dgGMe7tL5Uny4Wgy`); the campaign routers do not read it. Future verticals need their own collision-checked sender field and router.
- **Earlier 2026-10-07 cohort state, superseded by the current block above:** assigned all 169 Alcohol leads (43/42/42/42 across `.com/.co/.agency/.org`) and 44 Cannabis leads (11 each); readback verified all 213 assignments. The entry tags were then removed after the first history view showed `No Action` → `Finished`. A later fully loaded history read showed active waits as well, and Ed explicitly directed reapplication; all 213 tags have since been applied successfully. The Alcohol and Cannabis workflows remain published (`2e8c2d78-aaec-4591-9b53-b0715be8c4ce`; `5d1236a2-1b98-4b7f-9621-5d4f7749f377`). The Cannabis gate still excludes contacts tagged `dispensaries_pool` or `enrollment queue - dan - dispensaries`.
- Detailed campaign notes: [`docs/sessions/2026-10-06-alcohol-brands-multichannel-ghl-campaign-plan.md`](docs/sessions/2026-10-06-alcohol-brands-multichannel-ghl-campaign-plan.md) and [`docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md`](docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md).

## CURRENT 2026-10-06 — Executive Report V1 weekly Band 4 task

- **Weekly runbook saved:** [`docs/runbooks/executive-report-v1-weekly-hermes-refresh.md`](docs/runbooks/executive-report-v1-weekly-hermes-refresh.md) has the exact authenticated GHL/OpenCLI steps, America/Los_Angeles Sunday–Saturday date rule, tooltip/count reconciliation, V1-only update/deploy/readback, and fail-closed criteria. GHL native report counts are authoritative. The completed 2026-09-27–2026-10-03 Band 4 snapshot is in [`docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md`](docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md).
- **Schedule restored and advanced:** previous runbook ID `b231ec42ee37` was absent from Hermes `default` profile. Active job `cd6d1b15f148` (`Executive Report V1 Weekly Band 4`) now runs Mondays at 07:30 machine local time (Singapore Standard Time, UTC+08:00), 90 minutes earlier than its original 09:00. Next run `2026-10-12 07:30 +08:00`. Gateway is live; Windows Scheduled Task install could not proceed without admin approval, so Hermes installed a Startup-folder login item and started the gateway process. The gateway must be running after user login for cron to fire. Telegram delivery is not configured; run output is local.
- **Fail closed:** no numbers are guessed; missing login/MFA, exact tooltip values, correct LA date window, or reconciliation means preserve the last accepted report and record the blocker. The scheduled browser session's unattended authentication/browser availability is not yet proven by an end-to-end scheduled run; validate the first run before treating automation as fully hands-off.

## HISTORICAL 2026-10-06 — Cannabis campaign continuation (superseded 2026-10-07)

- **OpenCLI lesson for GHL workflow canvases:** on the `advanced-canvas` route, the builder is a cross-origin iframe. OpenCLI's outer-page text/AX snapshot can report a stale “Still connecting…” / “Loading fresh data…” banner, and `browser frames` can return an empty list, even while the workflow canvas is fully rendered. Before concluding the editor is stuck, capture and inspect a screenshot of the current tab. Do not treat the outer-page loading text alone as the canvas state.

- **EOS follow-up (2026-10-06):** current authenticated tab was accessed without refresh. Screenshot showed four sender branches and a Wait → Webhook → Wait segment after Email 1, consistent with SMS 1 placement; the later portion was outside the viewport. Ed reports a voicemail action two days after the Day 5 email (planned Day 7), but this was not independently visible in the captured viewport. Save state is uncertain (red indicator beside Save); Draft toggle remained on. Next session: fit-to-screen, inspect full canvas, verify save state and enrollment history, then continue the blockers in the plan's `EOS closeout — SMS and voicemail draft placement review`. No GHL edits, tests, executions, sends, calls, enrollment, or publication occurred in this review. No repeated Cannabis audience check is needed at individual channel nodes; separate contact-level consent and suppression requirements remain.

- **Latest authenticated GHL build readback (2026-10-06):** continued the same workflow ID `5d1236a2-1b98-4b7f-9621-5d4f7749f377` in location `Zwz4relUXVPxx8uohnjV`. Completed and saved the full 20 sender-specific native email actions (five each for `.com`, `.co`, `.agency`, `.org`) with the mapped campaign templates, subjects, Cameron From Name, and exact branch From Email. Email 2 attribution and Email 3 proof remain unsupported; first-party site copy supports the 30-day self-service guarantee, whose eligibility/terms must still match the email. All actions remain Draft assets only. Settings readback: re-entry off, multiple opportunities off, stop-on-response on, Contact timezone, weekday time window, From Name Cameron Karkut, default From Email `cameron@livetransparent.com`. Enrollment history readback: “No enrollments found.” Header is Saved/Draft; no publish, test, enrollment, sends, calls, or contact/tag/sender changes. Cadence waits, sender allocator, global stop/exit logic, attribution/idempotency/reconciliation, and channel consent/routes are still unbuilt or unverified; workflow is NOT complete. See the newest campaign-plan continuation for remaining work.

- **Session 2026-10-06 access check (superseded by OpenCLI continuation):** OpenCLI doctor is green and its authenticated Chrome tab is in Live Transparent location `Zwz4relUXVPxx8uohnjV`. The Automation → Workflows route loads its shell, but the workflow list/editor area is blank after reload and separate-tab attempts; no workflow was edited or freshly verified. The n8n MCP is the unrelated Katwill tenant and must not be used. See the campaign plan's `Continuation — OpenCLI browser recovery attempt (2026-10-06)` section. Continue through OpenCLI after the workflow UI renders; do not guess private endpoints.

- Authenticated GHL access is restored in Chrome. Existing workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377` remains Draft/unpublished. The eligible branch requires Vertical = Cannabis and separately excludes `dispensaries_pool` and `enrollment queue - dan - dispensaries`; re-entry and multiple opportunities are off, stop-on-response is on, with Contact timezone and weekday window. The eligible branch includes an If/Else sender router on `contact.lt_campaign_cannabis_brands_oct_2026_sender_email` with four exact-match branches for Cameron's `.com`, `.co`, `.agency`, and `.org` addresses; None has no actions. The full 20 sender-specific native email actions are now saved, five per branch, with matching templates, subjects, From Name, and literal From Email. Email 2 attribution and Email 3 proof remain unresolved; Email 4 is supported only within the published 30-day self-service offer terms. No action is launch-ready until remaining gates clear. Cadence waits, sender allocation, full stop/exit handling, attribution/idempotency/reconciliation, and channel gates remain unbuilt or unverified. Settings confirm re-entry/multiple opportunities off and stop-on-response on; enrollment history says “No enrollments found.” No tests, enrollment, publication, contact/tag/sender changes, sends, or calls occurred. See the latest campaign-plan continuation for detail.
- **Checklist legal links fixed and verified:** in the supported Forms editor, updated form `5rytqkbske3RlMfYHpMk` so Privacy Policy and Terms of Service both point to `https://livetransparent.com/privacy-policy/`. Saved and opened the public preview; both link destinations read back correctly. The source Google Doc/PDF was not changed.
- **Email claim evidence and channel gates remain:** public-source search found no substantiation for Email 2 store-level/real-time/SKU claims or Email 3 named proof. The public site supports the 30-day self-service guarantee, subject to confirming current offer eligibility/terms. SMS contact-level opt-in/STOP handling, voicemail consent and default route, campaign-scoped LinkedIn paths, V2 map gate, external send idempotency/reconciliation, attribution, and newsletter separation are still unbuilt/unverified. No sender values or lifecycle tags were assigned; no sender allocator/rotation exists. Preserve Draft/unpublished state, leave cohort tags unassigned, and keep all sends, tests, calls, and publication stopped.
- **MUST COMPLETE:** this is an unfinished campaign build, not a handoff to defer indefinitely. Follow the full ordered checklist and definition of done in the campaign plan's `EOS handoff — MUST COMPLETE campaign build (2026-10-06)` section: retain the saved 20-action email matrix and finish the remaining checklist, the complete cadence/waits, fail-closed exits, sender assignment, content evidence, channel consent/routes, attribution, idempotency/reconciliation, and non-sending readbacks. The remaining UI obstacle is reliable insertion and verification of middle-of-sequence Wait actions; recover a reliable authenticated editor surface and continue, rather than treating this as a GHL limitation. Keep Draft/unpublished with zero enrollment; no tests, calls, sends, or publication.
- **EOS resume point (2026-10-06):** the latest earlier authenticated Builder readback had all 20 actions saved and zero enrollments. This EOS run had no browser attached, so it did not freshly re-read GHL. Next session: bind authenticated Chrome; screenshot the existing `advanced-canvas` before interpreting stale loading text; verify the workflow and enrollment history; preserve (do not recreate) the matrix; then resolve Email 2/3 evidence, confirm Email 4 self-service guarantee terms, and continue waits and all remaining gates in the plan's `EOS closeout — campaign resume point`. No tests or external changes occurred during EOS.

## HISTORICAL 2026-10-05 — Cannabis campaign continuation (superseded 2026-10-07)

- Correct canonical source Doc confirmed: `https://docs.google.com/document/d/1rFjPhAcyNL-DMrPMKqcX2yslyDYXF9mKpFG40tL__6M`. Booking and checklist destinations match the five existing GHL templates; the source's footer/homepage URL is malformed (duplicate URL). GHL meeting CTAs remain 30 minutes per Ed's instruction; source is unchanged.
- The authenticated existing workflow canvas visually rendered despite the stale “Still connecting…” banner. It is Saved/Draft and shows the campaign tag trigger → eligibility If/Else (“Vertical is Cannabis” + two segments) → eligible/None branches, with no downstream sequence actions or waits. Cross-origin editor controls/settings and the exact two extra conditions remain unavailable to browser automation. No workflow change, publication, or enrollment occurred.
- Correct GHL location `Zwz4relUXVPxx8uohnjV` confirmed by the official GHL connector. Created isolated contact sender field `contact.lt_campaign_cannabis_brands_oct_2026_sender_email` (`qoQxuEiX5kwKvvrOvDVm`) and lifecycle tags `lt_campaign_cannabis_brands_oct_2026_active` (`uZ8nhAHenOGlWXdED2Yq`), `_replied` (`ABkDGtkRAS6TKrJ3yaZn`), `_completed` (`WNE26HmTjcy9Jb3v00Vv`), and `_suppressed` (`bHKF5O8g1hlDW4wmpxZa`). All were collision-checked/read back. No contact values or tag assignments were made; sticky rotation is not wired.
- Checklist form `5rytqkbske3RlMfYHpMk` still needs its Privacy/Terms `example.com` links changed to `https://livetransparent.com/privacy-policy/`; the embedded form builder has not been editable/readable through the current browser bridge, and public Forms API documentation exposes no form-definition update operation.
- Remaining gates: per-action sender/subject and sticky assignment logic; checklist legal links; evidence/review for Email 2's specific attribution claims; contact-level SMS opt-in and STOP/DND/reply gating; voicemail consent and default-number behavior; campaign-scoped Classic LinkedIn and mapped-chat V2 gates; step-level idempotency/reconciliation and campaign attribution; newsletter interval/re-entry; safe draft actions and non-sending previews. The cohort/tag remains unassigned. Keep all sends and publication stopped.
- **Next session:** start with the authoritative plan's latest `Continuation — source confirmation, GHL canvas read, and campaign metadata` section and execute its numbered **Next-session TODOs** in order. The first task is to regain interactive access to the existing cross-origin builder, then fix the checklist links; no duplicate workflow or additional cohort-selection question is needed. Preserve all existing workflow and contact safety gates.

## 📋 CURRENT 2026-10-05 — Cannabis Brands multichannel GHL campaign (draft implementation; sequence actions held on readiness gates)

- **Entry/eligibility scaffold saved; no send actions or external sender changes made.** Latest PIT-backed workflow-list read confirms the same workflow is Draft version 7; the API omits enrollment count and graph. The last authenticated UI read showed 0 enrollments. Re-entry/multiple-opportunity are disabled and stop-on-response is enabled. Workflow timezone is Contact timezone with a weekday 09:00–17:00 window and location Pacific fallback. GHL Email Services UI shows LeadConnector Email System default and `mg.livetransparent.com` Workflow Domain; From Name default is Cameron, while the full From Email must be set on each email action. No live email test was sent. GHL Send Email templates are selectable but no action-level disable control was found; channel nodes remain omitted. Location-wide Disable Contact Timezone is enabled, as Ed requested. Authoritative plan: [`docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md`](docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md). Source: `New Campaigns October 2026/Cannabis Brands - Multi Channel Outbound Sequence.pdf`.
- Implementation scope includes a dedicated GHL Email Templates folder (`Cannabis Brands Multichannel - Oct 2026`), five email templates, and three SMS template assets if selectable SMS templates are supported for the SimpleTexting path. Otherwise retain canonical SMS copy in named workflow steps and document the platform limitation. Keep assets/workflow unlaunched pending approvals; no enrollment/publication/send without separate authorization.
- **Draft build (2026-10-03):** reused existing GHL workflow `DRAFT - Cannabis Brands Multi-Channel Outbound - Oct 2026`, ID `5d1236a2-1b98-4b7f-9621-5d4f7749f377`. It remains Draft/unpublished with 0 enrolled. It now has a Tag Added trigger for the campaign-specific entry tag and an If/Else gate requiring `Vertical = Cannabis` AND not tagged with either `dispensaries_pool` OR `enrollment queue - dan - dispensaries` (each is a separate AND segment). Ed clarified that either exclusion tag blocks the contact. The new entry tag is `lt_campaign_cannabis_brands_oct_2026_enroll`; it was collision-checked against the existing tag inventory and created. No contacts were assigned it. Reopen/continue this workflow ID; do not duplicate or publish.
- **Campaign assets created and read back:** Email Templates folder `Cannabis Brands Multichannel - Oct 2026` (`6abfeed887cdcc5d6eee904e`) contains five named templates, IDs and details in the plan; GHL now reports HTML mode after linked CTA edits. Conversations > Snippets has a separate campaign-named folder (`4LOuqTbD59U3trQaSJQ7`) containing three SMS snippets. The SMS webhook path uses rendered copy, not snippet IDs. PDF booking/checklist links are applied; Email 5 links to the verified Mood cannabis case study (`https://livetransparent.com/resources/mood-x-transparent-ecom-self-service-case-study/`). Email 2's CTA now accurately links to the site's free cannabis compliance guide rather than calling it an attribution-mechanics deck; the source PDF remains unchanged. The checklist form still needs its `example.com` links edited to the verified combined legal-suite URL (`https://livetransparent.com/privacy-policy/`). SMS 2 snippet has the PDF booking URL. The redundant root SMS 1 duplicate was removed; only the campaign-folder copy remains.
- GHL contact field `Vertical` is single-select (`Cannabis`, `Peptides`, `Gambling`, `Alcohol`); campaign audience gate is `Vertical = Cannabis` AND lacks both user-specified exclusion tags. Operator selects the cohort later; don't auto-enroll everyone.
- The existing GHL draft container is now a saved entry/eligibility scaffold, not a complete sequence. Channel actions and waits remain to be built only in a safely gated/unpublished form after confirming GHL supports disabling/gating those steps; the overall draft remains unpublished.
- Plan uses GHL native Send Email workflow actions (Cameron Karkut, `cameron@livetransparent.com`) for five touches; SimpleTexting boundary for three SMS; Classic Unipile for Day 0 connection request; Sales Navigator V2 only after confirmed acceptance **and** a unique pre-existing V2 chat map; and GHL ringless voicemail drops only after contact-level consent and route gates are verified. Current LinkedIn and automated SimpleTexting send paths are not launch-ready; do not reactivate implicitly.
- ASCII rule for Unipile: normalize and then reject any LinkedIn payload containing non-ASCII bytes/characters before send. U+0027 apostrophe is safe; smart apostrophes/quotes/dashes must be replaced with ASCII. Avoid adding literal backslash escaping to message copy.
- **Confirmed preferences:** missing-company fallback “your team”; retain the source PDF unchanged; campaign meeting copy says 30 minutes to match the booking widget; unready LinkedIn/SMS/voicemail steps must not be saved as send actions unless a fail-closed gate is proven; proposed callback number +1 562-247-4600. On 2026-10-05 Ed set workflow timing to Contact timezone with 09:00–17:00 Monday–Friday and Pacific location fallback when contact timezone is missing. Ed confirmed the three additional sender addresses are set up correctly, chose sticky sender rotation per contact across all five emails, and chose GHL Reply-To/tracking; keep the location Reply Address blank. These choices do not clear remaining channel/readiness gates.
- Outstanding build gates: set full sender From Email on each native Send Email action, implement campaign-isolated sticky assignment after checking shared-field collisions, and validate delivery only with authorization; keep the GHL Reply-To address so responses remain tracked; fix checklist policy/terms `example.com` links; substantiate the remaining attribution mechanics claims in Email 2; voicemail default-number behavior and per-contact consent/eligibility (`lt_campaign_cannabis_brands_oct_2026_voicemail_consent_verified` exists but is unassigned/unwired); campaign-scoped Classic request path; V2 mapped-chat availability; SimpleTexting contact-level opt-in evidence and send readiness; newsletter three-month handling; external campaign attribution and per-step idempotency/reconciliation; and demonstrable fail-closed gates. Ed selected Workflow Campaigns and PDF links/copy, authorized location-wide timezone lock (enabled), and left the cohort unselected.
- Continuation: draft entry trigger and qualification gate were saved; new enrollment tag exists but was not assigned to contacts. No contact changes/enrollment, messages/calls, or live tests; no n8n workflow/sender changed or executed. The last pushed documentation/source commit is `e833b3b`; the later EOS handoff edits are currently uncommitted. Read `docs/sessions/2026-10-03-cannabis-brands-multichannel-ghl-campaign-plan.md` for exact build state, GHL campaign-object distinction, remaining gates, and next steps. Keep the workflow unpublished and all enrollment/sends stopped pending explicit launch authorization.
- **Sender/Reply-To decisions (2026-10-05):** Ed confirms `.co/.agency/.org` From addresses are set up correctly and chose sticky round-robin assignment once per contact across all five email touches. The isolated field `contact.lt_campaign_cannabis_brands_oct_2026_sender_email` now exists; sender assignment/rotation logic is not implemented. Repository review confirms `marketing_sender_email` is used by existing Cannabis Ads and Emerald routing; do not reuse it for this cohort. Ed chose GHL's Reply-To/tracking address; leave the location-wide Reply Address blank because setting it to Cameron would route responses outside Conversations. Forwarding to Cameron could copy replies without changing visible Reply-To, but was not requested or configured. Earlier `.co` DMARC test through `.com` transport is historical; do not represent it as current per-address verification. Email template CTA copy and planned LinkedIn Day 17 now say 30 minutes; source PDF remains unchanged at 15 minutes. Detailed EOS and official docs: campaign plan §§ “sender rotation and Reply-To setup research” and “EOS closeout — sender rotation, Reply-To decision, and booking-copy correction.”

## ✅ CURRENT 2026-10-03 (local; 2026-10-02 UTC) — LinkedIn connection requests CONFIRMED OFF (all senders)

- **Read-only verification session.** No workflow changed/published, no message/invite sent, no CRM or DB write, nothing committed. Worktree clean at start; the only change is this EOS doc update to `AGENTS.md`. Live checks used only the `n8n-lt` REST API (`N8N_LT_API_KEY` from `.env`) — the MCP connector available in-session was the wrong tenant (`katwill`) and was not used, per the standing repo rule.
- **Finding: every LinkedIn outbound sender is `active=false` with empty `activeVersionId` (fully unpublished).** No active workflow will emit connection requests or DMs.

| Workflow | ID | Active | Last run (UTC) | Status |
|---|---|---|---|---|
| LT - GHL LinkedIn Connect Dispatcher | `fXxw5lanZcDmUrst` | false | 2026-10-02 04:45:00Z | success |
| LT - Partnership LinkedIn Dispatcher | `crKIsaL5k3YBfqDZ` | false | 2026-10-01 20:00:00Z | error |
| LT - LinkedIn DM Sequence | `d0tEtijajisIsYcs` | false | 2026-10-01 14:44:00Z | success |
| LT - Partnership LinkedIn DM Sequence | `nspggypNF245xzeL` | false | 2026-09-30 17:00:01Z | success |
| LT - LinkedIn Connection Request (Internal Test) | `Zt8p2aYtIuY0HK18` | false | — | — |
| LT - LinkedIn Follower DM Sequence | `pq7XVajNFnnwMUTr` | false | — | — |

- **When they went off (n8n CE stores no deactivation timestamp; inferred from last execution + schedule):** DM sequences stopped at the documented **2026-10-01 ~14:49Z** pause; the **Partnership dispatcher** last fired **2026-10-01 20:00Z** (daily run) and the **personal Connect dispatcher** last fired **2026-10-02 04:45Z** (was firing every 15 min) then stopped — so the two **invite dispatchers were switched off separately/later than the DM pause** (~2026-10-01 20:00Z and ~2026-10-02 04:45Z respectively), not at the DM pause. All four `updatedAt` values (10-01 14:48–14:49Z and 10-02 03:39Z) reflect last edits, not live state.
- **Supersedes:** the 2026-10-02 session-2 "Live-sending resumed" claim — that was true when written (dispatcher restored and running), but the dispatchers have since been deactivated.
- **Next:** (1) if reactivation of invites/DMs is intended, it is a production send action and requires Ed's explicit approval first; (2) confirm whether the **Partnership dispatcher's last run error** (2026-10-01 20:00Z) was surfaced/handled; (3) still-open security item unchanged (GHL PIT + `stateUpsertSecret` plaintext in `Config` nodes, per the sections below).

## ✅ SUPERSEDED 2026-10-02 (session 3) — LinkedIn `linkedin_connected` backfill DONE + connection-path fixes

- **Backfill COMPLETE.** `linkedin_connected` now on **678 distinct GHL contacts** (read-back `678/678`, 0 untagged), covering every `connected` + `completed` state row that resolves to a real contact. Tool: `scripts/linkedin/backfill_linkedin_connected_tag.py` (`--measure` / `--apply`; idempotent; synthetic ids skipped). State after: `linkedin_connection_state` = 2,196 `connected`, 1,184 `requested`, 58 `requested_pending`, 10,892 `ready`, 100 `follower_messaged`, 5 `completed`; partnership = 127 `ready`.
- **Prior scope was wrong (correction):** only **112** of the 2,041 `connected` rows had real GHL contact ids — **1,929 used a second synthetic prefix `linkedin:relation:<slug>`** (Relations Backfill), which the old measurement missed (it only excluded `linkedin:follower:`). Correct resolution = real rows **plus** synthetic `linkedin:%` rows resolved via `linkedin_contact_profile_index` on `normalized_profile_slug = linkedin_public_identifier` **OR** `linkedin_provider_id = ANY(linkedin_provider_ids)`. 1,514 relation rows resolve to no contact (nothing to tag). Tool bug found+fixed: GHL tag-add returns **201** (not 200).
- **Durable fix — new active workflow `LT - LinkedIn Connected Tag Sync` (`rcvTMprJKga9aEJ6`)** daily `0 4 * * *` `America/Los_Angeles` (after the 03:15 Relations Backfill). Schedule → `Config` (Set) → `Tag Connected Contacts` (Code: `require('pg')` + union resolution + conditional GHL tag) → Result. Live-validated: executions returned `scanned=537, already_tagged=537, failed=0, errors=0`; 429/5xx retried. Builders: `scripts/linkedin/build_connected_tag_sync_workflow.py` + `connected_tag_sync.js`. Published `versionId == activeVersionId == 1394ef0f-7a23-4903-be32-aaded3af2d8c`.
- **`requested` reconciliation DONE:** of 1,396 `requested`/`requested_pending` rows, **155 were genuinely 1st-degree** (cross-checked against all 5,506 Unipile relations via `GET /users/relations`). All 155 marked `connected` via the state-upsert webhook and tagged (`state_ok=155, tag_fail=0`). Tool: `scripts/linkedin/reconcile_requested_connections.py`. The other ~1,184 are correctly still pending (not connected per Unipile).
- **Dispatcher mirror 401 FIXED (was the known defect):** `mirrorLinkedInToGhl` used the stored `ghl_oauth_tokens` **Company/agency** token, which GHL rejects (401 "authClass not allowed"). Verified live: company token → 401; `POST /oauth/locationToken` → **Location** token → auth OK. Patch exchanges to a location token before the mirror. `fXxw5lanZcDmUrst` published `65a7398b-328c-4f99-b709-ee2da1bc6683` (10 nodes). Script: `scripts/linkedin/fix_dispatcher_mirror_location_token.py`. Not yet exercised by a live send.
- **Relations Backfill silent no-op FIXED (found this session):** `VPiHfBwzOHaJnHBY` called `GET /users/connections` which returns the account's **own profile object**, not a list → every daily run was `backfilled:0` (2.4s) and never reconciled requested→connected. Fixed to `GET /users/relations`, provider id fallback `conn.member_id`, URL fallback `conn.public_profile_url`, plus a 240s deadline. Published `0754c540-80a5-4f6f-8b74-7d7ef8f35f9f`. Script: `scripts/linkedin/fix_relations_backfill_endpoint.py`.
- **STILL OPEN — security (unchanged):** GHL PIT (`pit-d25ac994-…`) and `stateUpsertSecret` remain plaintext in many `Config` nodes; **not rotated this session** (rotation touches many live workflows — plan is in the session doc §7).
- Authoritative detail: [`docs/sessions/2026-10-02-linkedin-connected-backfill-and-fixes.md`](docs/sessions/2026-10-02-linkedin-connected-backfill-and-fixes.md).

## ✅ RESOLVED 2026-10-02 — LinkedIn acceptance checker FIXED + live-validated

- **Fix applied + published (n8n-lt):** `LT - LinkedIn Connection Acceptance Checker (Unipile)` (`3ttEvr5NMcQCS4Hp`) now active/published at `versionId == activeVersionId == d6500907-cad3-4616-95e8-c9afe75e6019` (9 nodes). Blueprint: `scripts/deploy/deploy_acceptance_checker.py` + node JS in `scripts/deploy/acceptance_checker/` (`normalize.js`, `build_find_sql.js`, `build_payload.js`, `build_accept_sql.js`).
- **Three root causes fixed.** (1) **Parse:** `message_received` arrives as a form-encoded single-JSON-key body that is frequently malformed (unescaped `":"` in `occupation`); the old `JSON.parse`-only path returned empty identity. New `normalize.js` mirrors the proven `7o5EBdvwAuIaWW7k` fallback (regex extraction from the attendee block before `"sender"`). (2) **Signal:** `message_received` also fires on outbound invite-note/DM echoes (`is_sender:true`, attendee `network_distance:DISTANCE_2`). Per Unipile docs this is the **documented real-time method for note-bearing invitations**; the checker now confirms acceptance with `GET /users/{id}?account_id=...` and requires `network_distance == FIRST_DEGREE` **or** `is_relationship == true` (fail-closed on lookup error). (3) **Duplicates:** `Build Find SQL` returned `LIMIT 1`; it now returns **all** matches (main table; partnership only when no main match) and the payload/accept nodes iterate `$input.all()`, so every duplicate contact is tagged + upserted.
- **Subscription resolved:** the `linkedin-acceptance-checker` Unipile webhook is `message_received` (id `xFt6boNHRka9rEW4p9y32A`), which is correct for our note-bearing invites. Optional backstop (not created): a USERS webhook subscribed to `new_relation` (catches accepts without notes; delayed up to 8h).
- **Live validation (exact saved payloads replayed to the webhook):** LeighAnn `matched_count=2` (`PhsISRIq1xJ0JOhpZrJn`, `2ECRRa2WU1XHT9uiAHC5`) and Dasia (`pMsQ62wPlwIg5ugUA3Se`) all `tag_ok:true, upsert_ok:true`; both LeighAnn state rows and Dasia's row now `connection_status=connected` with the correct `connected_at`; `linkedin_connected` present on all three GHL contacts; 3 `linkedin_activity_events` `connection_accepted` rows. Negative test (pending invitee `gwelen`, Unipile `THIRD_DEGREE`) returned `matched:false, reason:not_connected`, wrote nothing, and left the state row `requested`.
- **Companion root-cause fix:** `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) `Build Upsert SQL` `esc()` double-escaped backslashes, which corrupts `'...'::jsonb` under `standard_conforming_strings=on` and made Dasia's upsert fail with `invalid input syntax for type json` (execution `1079790`). Fixed to single-quote-only escaping; published `versionId == activeVersionId == e37b7363-717b-454d-b83f-e2ab456746ee`. Script: `scripts/deploy/fix_state_upsert_esc.py`.
- **DONE 2026-10-02 (session 3) — backfill `linkedin_connected`:** completed — 678 distinct GHL contacts tagged (read-back `678/678`), plus a durable daily workflow (`rcvTMprJKga9aEJ6`) and 155 `requested`→`connected` reconciliations. See the session-3 section at the top and [`docs/sessions/2026-10-02-linkedin-connected-backfill-and-fixes.md`](docs/sessions/2026-10-02-linkedin-connected-backfill-and-fixes.md). The original scope estimate (2,041 real rows) was wrong; only 112 were real (the rest were `linkedin:relation:` synthetic rows resolved via the profile index).
- **STILL OPEN — security:** the `Config` Code node printed a plaintext GHL PIT (`pit-d25ac994-…`) and `stateUpsertSecret` into this and the prior session. **Rotate `stateUpsertSecret` and evaluate rotating the PIT**, then migrate both literals to the `Config` Set-node pattern. (The acceptance-checker deploy script now sources the PIT from `.env` and the secret from the state-upsert Config, so it no longer depends on the live Config literals.)
- Authoritative detail: [`docs/sessions/2026-10-02-linkedin-acceptance-checker-parse-bug-and-fix-plan.md`](docs/sessions/2026-10-02-linkedin-acceptance-checker-parse-bug-and-fix-plan.md).

## ✅ CURRENT 2026-10-02 (session 2) — "John" LinkedIn invite identified + GHL LinkedIn Connect Dispatcher FIXED

- **The old "John" invite note is explained and stopped.** `Hey {first} — quick connect. John here with Transparent eCom.` was the **default message of n8n workflow `Zt8p2aYtIuY0HK18` ("LT - LinkedIn Connection Request (Unipile) (Internal Test)")**, invoked by the GHL automation **`Send Connection Request through Unipile when MQL Tag is added` (`25cd82a2-8344-4dc5-962f-a2b5e5c5ee88`)** via `https://automations.livetransparent.com/webhook/unipile-linkedin-connect-test`. That GHL action sends **no `message`** (only `linkedin_url`/`contact_id`/`first_name`/`send`), so the text was always `Zt8…`'s own `defaultMessage`. `Zt8…` was **active 2026-04-22 → deactivated 2026-07-11** (now inactive, `activeVersionId` empty) → **no John note has been sent since 2026-07-11**; every GHL call since 404s (last hits 2026-09-28…2026-10-01T12:29Z, tied 1:1 to `mql` tag events). The copy is **not in any current/retained n8n version** (current senders use the Cameron copy). Ed **unpublished the GHL automation**. Notes still appearing are **old Apr–Jul invites accepted now** (LeighAnn Loftus accepted 2026-10-01T18:28:44Z; both `…/in/leighann-loftus` and `…/in/leighann-loftus-2319b011` are the **same** profile `ACoAAAJ1-EUBwEFlr3IYQYUYIjMNzPtY0yB0C58`).
- **`LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) FIXED + republished.** Root cause of the every-run error: the `Config` Set node's **`pgPassword` assignment was missing `"type":"string"`** → Set v3.4 threw `Cannot read properties of undefined (reading 'toLowerCase')` at `Config` on every run (so it had been sending nothing). Added the field, and added the invite business rule to `Fetch Ready Queue`: `AND connected_at IS NULL AND (request_sent_at IS NULL OR request_sent_at < NOW() - INTERVAL '30 days')` (skip if connected or invited <30 days ago; also covered by state + GHL tag blocking). Published `versionId == activeVersionId == 99c1f5ee-d52d-44b4-95ef-b58d122ff2df` (10 nodes). **Verified:** execution `1079371` (2026-10-02 00:45Z) `success`, `sent=10, failed=0`; daily cap 60 intact.
- **Live-sending resumed** (10 invites in the first fixed run; `ready` backlog ≈10,953 ≈ 60/day; snapshot: ready 10,953 / connected 2,038 / requested 1,279 / requested_pending 60).
- **MQL automation not needed** — the dispatcher already invites any LinkedIn-URL contact (MQL included), ≤60/day, with suppression + the 30-day rule. The live MQL pipe is GHL `WL - MQL Tag Ledger` (`203163a4-262a-4195-9a15-b4aa0b712c5a`, published) → n8n `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`, active, logs only).
- **Known defect (not fixed):** the dispatcher's outbound mirror to GHL Conversations returns **401** (`mirrorLinkedInToGhl` uses the PIT against `/conversations/messages`; needs the OAuth location token). Invites send; conversation copy missing.
- **Next:** (1) fix/drop the mirror 401; (2) monitor scheduled runs for success/≤60/day/no dupes and LinkedIn restrictions; (3) optional explicit MQL→enqueue in `U9oc2tZRsr4zq6IM`; (4) rotate Unipile key + Postgres password (plaintext literals); (5) keep GHL `25cd82a2` unpublished/delete it. Detail: [`docs/sessions/2026-10-02-linkedin-john-invite-investigation-and-dispatcher-fix.md`](docs/sessions/2026-10-02-linkedin-john-invite-investigation-and-dispatcher-fix.md).

## ✅ CURRENT 2026-10-02 — Sales Navigator messaging rules clarified (InMail vs 1st-degree) + team note

- Knowledge/read-only session: no workflow changed/published, no message sent, no CRM write, nothing committed; worktree clean at start. Confirmed from LinkedIn + Unipile docs and our own tests: **Sales Nav InMail to a non-connection costs 1 credit and requires a subject**; **1st-degree (connected) messages are regular LinkedIn messages — no subject, no credit**; credits max **150** (50/month on the 1st UTC, **cannot purchase**, unused roll over to the 150 cap, **refunded on any response within 90 days** incl. accept/decline/auto-reply); a decline is a one-tap **"Not interested"** quick reply (still refunds the credit); Sales Nav threads are a **separate conversation from Classic**. Our bridge sends **follow-ups only** (`POST /v2/{account}/chats/{chatId}/messages/send` with `{ text, attachments }`, no subject — `scripts/n8n/wire_sales_navigator_v2_workflows.py:385`; repo test send `scripts/n8n/reconcile_gateway_test_message.py:90`) and **cannot start a chat** (`Find V2 Contact Chat` fails closed without a `sales_navigator_v2_conversation_map` row). GHL's Custom (SMS-type) provider payload carries **no subject**. **Decision:** connection requests stay on **Classic**; once connected, message as **1st-tier**; **do not start new conversations via Sales Nav**; any Sales Nav initiation must run via **n8n** and needs a **subject source** (not built). Docs-backed but **not yet E2E-tested** by us. Authoritative detail + final team Slack note: [`docs/sessions/2026-10-02-sales-navigator-messaging-rules-and-team-note.md`](docs/sessions/2026-10-02-sales-navigator-messaging-rules-and-team-note.md).

## ✅ CURRENT 2026-10-01 (session 4) — n8n-lt stall RESOLVED + Sales Navigator V2 bridge durability + attachments LIVE

- **n8n-lt execution stall RESOLVED.** Symptom: ~148 executions queued `new` (~1h) with one stuck `running` (`1074231`) while `/healthz/readiness` still returned 200. Causes: the external JS runner stopped offering tasks (broker logged `No matching task offer ... Available offer types: [python]` and `Offer expired`) and n8n's own Postgres pool was wedged (`socket hang up`, `Connection terminated due to connection timeout`, continuous `Error while saving insights metadata and raw data`). Fixed by restarting the runner container, then the n8n container; the queue drained, `1074231` was marked `crashed`, and no anomalies appeared after 14:38:27Z.
- **Recurrence cause fixed (stale Postgres password).** `fXxw5lanZcDmUrst` `Dispatch LinkedIn Requests` fell back to a stale hardcoded Postgres password literal because its `Config` node lacked `pgPassword`; the auth failure triggers a `pg`-protocol `TypeError: Cannot assign to read only property 'name'` that exits the whole JS runner. Added `pgPassword` (correct live value; see `.env`/`POSTGRES_PASSWORD`) to the `Config` Set node of the 4 workflows that hold the stale literal: `fXxw5lanZcDmUrst` and `crKIsaL5k3YBfqDZ` (active), `d0tEtijajisIsYcs` and `nspggypNF245xzeL` (inactive). No jsCode edits. Find real matches by searching workflow nodes text with `position(<stale-literal> in nodes::text)`, not `LIKE` (the `%` wildcards match separated tokens). **Security: the live Postgres password is committed in plaintext in several `scripts/` blueprints (e.g. `scripts/linkedin/*.py`, `scripts/diagnostics/*.py`); rotate the DB password and migrate those to Config/placeholders next session.**
- **n8n execution-finalization bug found + fixed.** `saveDataSuccessExecution: none` left executions stuck in `running` on n8n 2.37.10 (gateway/bridge/reconciler accumulated; global `running` exceeded `N8N_CONCURRENCY_PRODUCTION_LIMIT=5`). Setting it to `all` makes them finalize in ~0s. Gateway `ZiYEBuP7xdddhnUB` and bridge `CfpedDQWxoJLEMdL` now use `saveDataSuccessExecution`/`saveDataErrorExecution = all` (Classic `7o5EBdvwAuIaWW7k` deliberately left on `none`); `wire_sales_navigator_v2_workflows.update()` now pins this. Trade-off: message content is stored in n8n execution data (it is already persisted in the V2 ledger); prune via `EXECUTIONS_DATA_PRUNE`.
- **Sales Navigator Step 2 durability DEPLOYED** (Ed authorized "full durability deploy, then validate"). Schema migrated to production Postgres DB `postgres`: 10 new columns (`direction`, `message_text`, `attachment_manifest`, `provider_profile_id`, `provider_timestamp`, `payload_sha256`, `attempt_count`, `last_reconciled_at`, `reconcile_attempts`, `held_reason`), widened status CHECK including `held`, and the reconcile/held/retry/claim indexes. Backup `/tmp/sn_v2_backup_20261001T145248Z.sql`; 4 `posted` rows preserved. Now live: signed-event persistence, `altId = Unipile message id` (was chat id) on inbound and outbound-mirror posts, gateway attachment branch. (Superseded version IDs from that deploy: gateway `496dd095-c1be-412b-9fd4-d834fdaea475` 24 nodes, bridge `323596d5-e350-4733-98ca-685db0c18baa` 58 nodes — see the attachment bullet for the current published versions.)
- **Reconciler `LT - Sales Navigator V2 Uncertain Write Reconciler` (`sFrvSJIZusAbrsFx`, 12 nodes) created + active.** Read-only to GHL/Unipile; updates only the V2 ledger. Hardened this session: `Has Stale Row?` no-op guard (avoids needless external calls), 15s HTTP timeouts, success-data saving so runs finalize. Runs every minute; verified `success` in ~0.1s with zero accumulation. `MAX_RECONCILE_ATTEMPTS=10` → terminal `held` with `held_reason`.
- **Validation:** `py_compile` clean; dry runs 24/74 and 12; gateway negative signature → 401 `invalid_signature`/`signature_missing`; bridge bad signature → 401 `invalid_signature_header`; ledger unchanged (4 `posted`, 0 unresolved/held, 1 map, 0 duplicate maps, 0 pending claims); running=0, queued=0. Media service unit tests 4/4; public unauthenticated store → 401; authenticated store→fetch roundtrip verified. No live message, contact creation, or valid signed webhook was sent.
- **Attachment transport is now LIVE (session 4, 2026-10-01)** — simplified to one attachment per message, 4 MB cap. Outbound (GHL→Unipile) is inline in n8n (host allowlist + binary fetch + base64; no media service). Inbound (Unipile→GHL) uses the deployed slim host `services/sales_navigator_media` (byte store + unguessable URL; bridge fetches with its Unipile credential, service never fetches remote URLs and holds no Unipile key). Media service is `Up` on `coolify-shared`; `GET https://reports.livetransparent.com/sales-navigator-attachments/v1/healthz` → 200; unauth `POST /v1/store` → 401; authenticated store→fetch roundtrip verified. n8n credential `LT Sales Navigator Media Service` = `Sz8fSsdp5mGNIUhB`; repo `.env` has `SN_MEDIA_CREDENTIAL_ID`. Gateway `ZiYEBuP7xdddhnUB` active/published `66019014-f467-4bea-ac1c-d47f6dbfbd07` (24 nodes); bridge `CfpedDQWxoJLEMdL` active/published `dd6b78e3-5bd5-4ce4-90f1-ecb82f2b66ed` (74 nodes); ledger unchanged (4 `posted`, 0 unresolved/held, 1 map, 0 pending claims); running=0, queued=0. Deploy/verify helper: `services/sales_navigator_media/deploy_vps.py`.
- **Still open:** no live attachment end-to-end test yet (no real inbound attachment and no GHL message with an attachment has been sent), so GHL's hosted-URL handling and Unipile's inline attachment acceptance are unverified live; reconciler still sends attachment-bearing uncertain sends to manual `held`. Classic cutover not started (Classic `7o5EBdvwAuIaWW7k` and social router `kqIi8i1RjFAZKrK3` remain active/unchanged). Authoritative detail: [`docs/sessions/2026-10-01-sales-navigator-final-audit.md`](docs/sessions/2026-10-01-sales-navigator-final-audit.md).

## ⏳ SUPERSEDED 2026-10-01 EOS (session 2) — n8n-lt queue/runner incident + Sales Navigator Step 2 durability (local only)

- **⚠️ HISTORICAL INCIDENT (resolved in session 3 above): the n8n-lt execution queue was stalled.** Read-only checks at 2026-10-01T14:25Z: `/healthz/readiness` returned 200 `{"status":"ok"}`, but the newest completed execution `stoppedAt` was `13:26:59Z` (workflow `toUG1yPDmFG48KEP`), execution `1074231` (`QfJ2EZcc7lZwNgxj`) had been `running` since `13:00Z`, and ~140 executions were queued `new` and were not draining. See the session-3 section above for the cause and resolution.
- **Runner Postgres auth error:** resolved in session 3 (stale hardcoded Postgres password literal in `fXxw5lanZcDmUrst` `Dispatch LinkedIn Requests`; fixed by adding `pgPassword` to `Config`).

## ✅ CURRENT 2026-10-01 EOS — LinkedIn DM sequences paused (copy revision)

- Objective: Ed is preparing new LinkedIn messages and asked to pause LinkedIn DMs. Invites were offered as a separate scope and Ed declined ("no"), so only the DM senders were stopped.
- Action taken (live `n8n-lt`, direct REST): deactivated two outbound DM workflows via `POST /api/v1/workflows/{id}/deactivate`:
  - `d0tEtijajisIsYcs` `LT - LinkedIn DM Sequence (Unipile)` — http 200; verified `active=false`, `archived=false`, `activeVersionId=null`, `versionId=96f7cf60-97c2-4f54-ba13-20ebf9d49ef1`, 12 nodes.
  - `nspggypNF245xzeL` `LT - Partnership LinkedIn DM Sequence` — http 200; verified `active=false`, `archived=false`, `activeVersionId=null`, `versionId=9c04b07a-812d-4755-850d-125cadec8c7a`, 6 nodes.
  - Both `versionId`s match the previously published DM versions, so no draft drift; reactivation will restore the same copy unless a new draft is saved first.
- Left ACTIVE intentionally: invite dispatchers `fXxw5lanZcDmUrst` (GHL LinkedIn Connect Dispatcher) and `crKIsaL5k3YBfqDZ` (Partnership LinkedIn Dispatcher); human-reply router `kqIi8i1RjFAZKrK3`; inbound/state-sync workflows (`7o5EBdvwAuIaWW7k`, `ceaKnz6E3onQrZpt`, `QfJ2EZcc7lZwNgxj`, `Old7ZvyVYgFaJgDr`, etc.). Do not pause the human-reply router — it carries manual GHL-originated replies.
- Deactivation stops future scheduled sends only; in-flight `linkedin_connection_state` rows are untouched and will resume automatically on reactivation.
- Access note: the MCP n8n connector available this session was the **Katwill** instance (wrong tenant). Per the standing repo rule it was not used for the mutation. The pause was done with the `.env` `N8N_LT_API_KEY` against `https://automations.livetransparent.com` (the correct `n8n-lt`), after read-only confirmation that the returned workflow IDs match this repo. The variable is `N8N_LT_API_KEY` (not `N8N_API_KEY_LT`).
- No repository files were changed by this session; the worktree remains dirty with preexisting changes and untracked Sales Navigator files. Preserve it.
- Next session (ordered): (1) when new copy is ready, apply it to both DM sequences (edit + save draft), (2) `publish_workflow` / reactivate both `d0tEtijajisIsYcs` and `nspggypNF245xzeL` and confirm `active=true` with a fresh published version, (3) confirm scheduled sends resume (schedule `0 12-22 * * 1-5` main; partnership DM cadence) and no duplicate sends. Reactivation is a production send action — only after Ed approves the new copy.

## ⏳ SUPERSEDED 2026-10-01 EOS (session 2) — Sales Navigator repair paused

- **Superseded by session 3 (Step 2 durability deployed) and session 4 (attachment transport live).** Retained for history. Authoritative handoff: [`docs/sessions/2026-10-01-sales-navigator-final-audit.md`](docs/sessions/2026-10-01-sales-navigator-final-audit.md).
- Historical read-only `n8n-lt` baseline at that time: gateway `ZiYEBuP7xdddhnUB` `853db749-37f5-4e06-9a09-7e481be41738` (16 nodes); V2 bridge `CfpedDQWxoJLEMdL` `8d56bf88-a159-4c5a-a67d-9d74feb228f3` (58 nodes); Classic inbound `7o5EBdvwAuIaWW7k` `8a22c193-3702-4257-bd28-ebd6c6efe720` (27 nodes). Current published versions are in the session-4 section above.
- Ed reported n8n "database not ready" during that session; it later recovered. Start any session with a read-only `n8n-lt` health check and stop if the error returns.
- That session's local-only scaffolds (gateway attachment path, media service, schema metadata, reconciler) are now deployed and published (sessions 3/4). Attachments are live; Classic cutover is still not started.
- Working tree remains dirty with preexisting changes; preserve it. Do not claim Classic cutover completion.

## ⏳ SUPERSEDED 2026-10-01 EOS — Sales Navigator live audit and next-session repair

- Authoritative next-session handoff: [`docs/sessions/2026-10-01-sales-navigator-final-audit.md`](docs/sessions/2026-10-01-sales-navigator-final-audit.md), including an ordered repair plan and acceptance criteria. **Superseded by sessions 3/4:** the ordered repair plan (durable reconciler, `altId` = Unipile message id, attachment transport) is now deployed; see the session-4 section at the top for current versions and state.
- Ed's own GHL outbound `EEXyOBuSaGE2VcikrFzY` reached Cameron's Sales Navigator, and the Sales Navigator inbound is GHL message `W5STWk2Wmb0jrH5Vk7me`. GHL readback showed the former `sent` under Ed's user ID and the latter `delivered` under provider `6abd56db3e5dc9f056868ad2`; production Postgres showed both ledger entries `posted`. Four V2 events total were posted, none unresolved; one V2 contact/chat map and zero pending shared profile claims. No new message was sent in the audit or EOS.
- Live n8n-lt readback: gateway `ZiYEBuP7xdddhnUB` active/published `ef4fa5a1-4d7b-47cb-acae-4bd57a1d2409` (16 nodes); V2 bridge `CfpedDQWxoJLEMdL` active/published `8d56bf88-a159-4c5a-a67d-9d74feb228f3` (58 nodes); Classic inbound `7o5EBdvwAuIaWW7k` active/published `8a22c193-3702-4257-bd28-ebd6c6efe720` (27 nodes). The old social router `kqIi8i1RjFAZKrK3` is also active/published. No workflow was changed during the audit/EOS.
- **Historical unresolved defects (now addressed except Classic cutover):** after a 202 acknowledgement, failed/processing V2-to-GHL events were treated as successful duplicates with no reconciler (now: durable reconciler + `held`); uncertain GHL-to-Unipile sends needed reconciliation (now: reconciler); the bridge was text-only (now: 1x4 MB attachments both directions); GHL `altId` used the chat ID (now: Unipile message id). Still open: Classic LinkedIn routes remain, so Sales Navigator-only GHL cutover is incomplete. Do not blindly replay uncertain events or release pending contact claims.
- The Unipile direct read-only API timed out once during the audit; this is unaccepted as a provider-health check. GHL and n8n-lt Postgres readbacks succeeded. The working tree is dirty with preexisting changes and untracked Sales Navigator build files; preserve it. No tests, sends, workflow publications, CRM mutations, or commits were done in the EOS closeout.

## n8n instance rule — mandatory for this repository

- For every n8n task in this repository, use only the `n8n-lt` instance and its tools/API. Never use `n8n-katwill`, `n8n_whitefriar`, or any other customer/client n8n instance or connector. This is a standing project constraint, not a per-task preference. If `n8n-lt` is unavailable, stop n8n operations and report the access issue; do not fall back to another instance.
- Before any n8n tool call, verify that the selected connection is `n8n-lt`. This applies to reads, writes, credential/workflow operations, and discovery.

## ⏳ SUPERSEDED 2026-10-01 EOS — Sales Navigator GHL app and V2 workflows

- Repository rule: use only `n8n-lt` for all n8n work here. Never use `n8n-katwill`, `n8n_whitefriar`, or another client instance. If `n8n-lt` is unavailable, stop n8n operations; do not fall back.
- User reports the separate Marketplace app OAuth settings are saved and the additional SMS custom conversation provider exists. Client ID `6abd41c58a3e9cb4acdbc555-muofh6mn`; provider ID `6abd56db3e5dc9f056868ad2`; provider callback/delivery URL `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`. Portal settings remain user-reported, not independently inspected. V2 now creates unmatched contacts through the OAuth credential, so its connected grant must include `contacts.write`; no live create has verified that scope yet.
- Dedicated encrypted credentials exist: GHL OAuth2 `zuOARvZFtLm6iIWu` and Unipile V2 API `xfQeYq9i3A0TrEnT`. User reports GHL OAuth2 is now connected. Config also retains GHL client ID/secret and Unipile API key as the user explicitly requested. Do not print credential/config values. Success/error/manual execution data saving is disabled for both workflows.
- V2 SQL map/event schema and shared contact index/claim schema are applied on production Postgres. Existing identity sources were seeded into the shared index; inbound resolution uses the index rather than those sources directly. No Classic outbound router or Classic state rows were changed.
- Both inbound paths use the shared enhanced `linkedin_contact_profile_index` on n8n-lt Postgres. It stores normalized profile slugs, profile URLs, contact names, and provider IDs with B-tree/GIN lookup indexes; the GHL snapshot trigger maintains profile fields. Seeded state includes 30,511 profile/identity rows across 25,878 contacts.
- Legacy `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active at version `8a22c193-3702-4257-bd28-ebd6c6efe720` (`versionId == activeVersionId`). It checks the shared index and acquires a profile-key claim before creating. After GHL contact creation, it persists the contact and resolves the claim before posting the inbound GHL message.
- Sales Navigator V2 bridge `CfpedDQWxoJLEMdL` is active at version `fb85cb53-b266-4d48-9cb8-7895ad93187c` (`versionId == activeVersionId`, 52 nodes). Incoming `message.new` events resolve/create and index the sender contact, map the V2 chat, then idempotently post an inbound Custom message. Sent `message.new` events now mirror to GHL as outbound Custom messages using the same message event ledger. They use the existing chat map or resolve the other participant from chat history and match that LinkedIn profile to the shared index; unknown or ambiguous contacts fail closed.
- `linkedin_contact_profile_claims` serializes messages for the same normalized profile. A waiter checks for the owner's indexed contact for up to 10 seconds, then fails closed. Pending claims never expire or get stolen automatically: if a workflow stops after GHL creation but before the index write, reconcile the GHL contact and claim before any manual release. The one-time database migration ran successfully; no inbound message workflow execution, live message, or GHL contact write was run.
- Gateway `ZiYEBuP7xdddhnUB` is active at version `f8cb7997-1e74-458a-ba63-7a4c97426419` (15 nodes; `versionId == activeVersionId`). It validates raw-body GHL Ed25519 signatures and documented delivery fields, resolves a unique V2 chat (using `replyToAltId` when supplied), claims outbound message IDs, then sends only to the existing mapped V2 chat with the restricted Unipile credential. It never creates a chat/contact.
- V2 workflow `CfpedDQWxoJLEMdL` is active at version `fb85cb53-b266-4d48-9cb8-7895ad93187c` (52 nodes; `versionId == activeVersionId`). It validates Unipile HMAC/account/event and branches on message direction. Incoming events use the shared exact-profile index/claim, create and index a contact when absent, upsert the V2 chat map, claim event/message IDs, acknowledge, then post the Custom inbound message and finalize the ledger. Sent events resolve the existing chat map or match the peer from prior incoming chat history to the shared profile index; a unique match is required before writing a Custom message with `direction: outbound` to GHL. The same event/message ledger deduplicates both directions. Enabled endpoint `we_01m3taxyc3e4e8ayvk7aqazvnv` subscribes to `message.new` for the V2 account; signing secret remains in Config.
- The outbound mirror was published and REST-read back active with matching versions. No event execution, GHL message/contact write, or LinkedIn send was used to validate it. The message Ed sent before this update was not replayed or backfilled. New inbound contact writes remain gated by signature/profile validation and the unique shared profile claim. Pending profile claims require manual reconciliation if a run stops after contact creation. Confirm the custom provider installation and OAuth grant, then validate with a new controlled event. No Classic cutover or historical backfill is in scope.
- Build/update utility: [`scripts/n8n/wire_sales_navigator_v2_workflows.py`](scripts/n8n/wire_sales_navigator_v2_workflows.py). Specs: [`n8n/sales-navigator/WORKFLOW_BUILD_SPEC.md`](n8n/sales-navigator/WORKFLOW_BUILD_SPEC.md) and [`n8n/sales-navigator/sales_navigator_v2_schema.sql`](n8n/sales-navigator/sales_navigator_v2_schema.sql).
- User reports the GHL OAuth credential connection succeeded. The Unipile V2 endpoint and signing-secret configuration are complete. Next confirm the custom provider is installed/available at the intended GHL location and run controlled inbound/outbound validation before broader use. The provider delivery URL remains `https://automations.livetransparent.com/webhook/lt-sales-navigator-provider`.

## ⏳ SUPERSEDED 2026-10-01 EOS — V2 Sales Navigator GHL custom app planning

The historical planning notes in this section below are superseded by the current checkpoint above and the detailed updated handoff. In particular, its initial statements that app/provider setup was unfinished and credentials remained unrevoked are no longer current.

- **Goal:** Create a new HighLevel Marketplace app and custom conversation provider dedicated to Unipile V2 Sales Navigator account `acc_01m3sefk22e8jvnmvvfx333pye`. The existing Classic app is to remain intact. At final cutover, GHL Conversations should contain Sales Navigator messages only; Classic messages must be excluded by disabling/filtering the existing Classic-to-GHL inbound and outbound routes. Do not delete the Classic app, account, or historical GHL messages.
- **User correction:** create a separate new GHL custom app; do not replace the existing app. The apps/accounts may coexist during staging, but the existing Classic message route must be stopped at cutover to meet the Sales Navigator-only GHL requirement.
- **V2 evidence (read-only, 2026-10-01):** `GET /v2/{account_id}/chats/{chat_id}/messages` returned 2 messages in the test Sales Navigator chat; the latest was incoming (`is_sender=false`) from provider user `ACwAACeQjiYBfmQfKakCJqijaX9-LVjeHyQrBw8` at `2026-09-30T16:11:22.738Z`. `GET /v2/webhooks/endpoints` returned HTTP 200 with zero endpoints in the initial check and again during the 2026-10-01 handoff review. This explains why the reply was visible through V2 but was not forwarded to GHL. No webhook was created and no GHL record was changed.
- **Prior GHL app pattern (from project documentation):** Private app, sub-account target, installable by Agency + Sub-Account; the old app was documented with scopes `contacts.readonly`, `contacts.write`, `conversations.readonly`, `conversations.write`, `conversations/message.readonly`, `conversations/message.write`; SMS custom provider with “Is this a Custom Conversation Provider” and “Always show this Conversation Provider” enabled; not selected as the default SMS provider. Existing app multiplexes OAuth GET callback and provider outbound POST on `/webhook/lt-social-provider-outbound`. The separate `/webhook/oauth-callback` workflow was not used by this app. Treat these values as historical reference; for the new app, configure a dedicated route and register its exact OAuth redirect URI. Confirm minimum scopes in the Marketplace UI before installation.
- **Planned architecture:** a new provider ID; a new Unipile V2 webhook endpoint subscribed to `message.new` and restricted to the V2 account; a dedicated outbound callback route that accepts only the new GHL provider ID and sends through the V2 account; an inbound normalizer that checks the exact account, direction, and event/message IDs before posting to GHL as `type: "Custom"` under the new provider; and an identity/chat map that includes V2 account ID, Sales Navigator provider profile ID, Unipile chat ID, and GHL contact/conversation IDs. New Sales Navigator chats use `SALES_NAVIGATOR_PRIMARY`; replies use the existing Sales Navigator chat ID. Do not reuse Classic account identifiers or route Sales Navigator messages through the Classic provider.
- **Conversation semantics:** Classic history is not migrated into Sales Navigator threads. Keep historical messages as-is; do not backfill them as part of this switchover. Do not create a contact for the test unless its GHL contact mapping is confirmed or separately approved.
- **Historical security incident at the time of this checkpoint:** a repository search printed the Katwill n8n API key from `.env`, and reading the legacy social-inbox setup notes printed its GHL Marketplace client secret. The current value is redacted from `docs/strategy/unipile-ghl-bidirectional-integration.md`; old values may remain in Git history. User later confirmed both credentials were revoked on 2026-10-01. Do not reproduce old values in logs, prompts, notes, or workflows.
- **Access/verification limits:** Ed reports he has begun creating the HighLevel Developer Marketplace app; its current configuration was not visible to the assistant. No browser was available for that portal. The available GHL MCP tools do not create Marketplace apps or providers. The n8n credential was not used after exposure; the earlier workflow GET returned 404 and the workflow-list read failed, so no live n8n workflow state was verified in this EOS. No app/provider, OAuth scope, Unipile webhook, or workflow was created/changed by the assistant.
- **Historical next-session checklist:** superseded by the current checkpoint above and the detailed build order in `docs/sessions/2026-10-01-sales-navigator-ghl-custom-app-build-plan.md`.
- **Approval/safety gates:** Do not send a new LinkedIn test message, post a message into GHL, create/update a contact, install the app/grant OAuth scopes, register the V2 webhook, or change/deactivate production workflows without explicit approval at the relevant live action. No message backfill or historical migration is in scope.
- Detailed handoff and build checklist: [`docs/sessions/2026-10-01-sales-navigator-ghl-custom-app-build-plan.md`](docs/sessions/2026-10-01-sales-navigator-ghl-custom-app-build-plan.md).

## ⚠️ CURRENT 2026-09-30 EOS — LinkedIn inbound duplicate-contact race

- `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is active and published at `b9dbffa7-79fc-408d-9d40-7a999a0f2ccc` (`versionId == activeVersionId`). Its lookup now claims a unique LinkedIn provider/profile identity in Postgres before GHL contact resolution; competing events wait/reuse, wait failures stop without creating, failed claims are released, and abandoned pending claims can be reclaimed after five minutes.
- Root cause confirmed from executions `1068352` and `1068355`: two events for Ian Lange's same LinkedIn identity/chat arrived 585 ms apart; both saw no mapped GHL ID and both created a contact. The affected records are `qYSqY56e0UHPTjqUUTiG` and `DcBoUBEiNrC1Zh0sWg0M`, created 418 ms apart. Each has a separate open opportunity (`VrFHG3ljyiLYL3eh0emV` and `ASSrfoX1boNTMnggZySZ`). No CRM record was changed during the fix.
- The patch was published by direct n8n REST update and re-read with matching active/draft version IDs. Node text was checked for the claim, wait-fail-closed branch, and claim resolution SQL. No live event was triggered; no execution has yet demonstrated the new behavior end-to-end. The previous assistant attempted a local syntax check but it was rejected by command policy, so runtime acceptance is unverified.
- **Security follow-up:** during the earlier execution inspection, credential values were present in node execution output, and the live contact node also contains a hardcoded GHL credential. Do not copy these values to notes or logs. Rotate affected GHL credentials and remove hardcoded credentials from the workflow; inspect retention/cleanup options for saved execution data. The previous transcript contained the sensitive output, so treat exposed credentials as compromised.
- **Next session, in order:** (1) rotate/revoke exposed GHL credentials and replace workflow literals using the approved credential mechanism; (2) validate the new SQL and JavaScript offline, then use an isolated, controlled verification that cannot send LinkedIn messages or create extra contacts; (3) inspect identity-claim row behavior for owner, waiter, reuse, failed create, and five-minute recovery; (4) reconcile Ian's two contacts and duplicate opportunities only after reviewing conversation history and choosing a canonical contact. Current evidence shows `DcBo...` holds the full message while `qYSq...` holds the attachment-only event; confirm before cleanup.
- Do not execute a live LinkedIn/CRM test, merge/delete either Ian record, or close/remove either opportunity without explicit approval. Do not claim the race fix is runtime-verified until an isolated verification succeeds.

## ✅ CURRENT 2026-09-30 EOS — reporting-only V1 closeout

- Active V1 Facts API `oxYDg6XnRBKhl1Xd` is published at version `ae414181-adc4-4bbf-8f81-2facef5c3c39`; latest read-only checked execution `1069228` succeeded.
- V1 now returns funnel, closed-source, weekly movement, vertical, retargeting, and contact-acquisition/backfill fields. The deployed V1 page and legacy report both returned HTTP 200; the legacy build marker remains intact.
- No CRM workflow, CRM record, outbound send, Marketplace subscription, or private call-report automation was changed in this closeout.
- Remaining: exact-ID reconciliation of new facts, supported call-reporting parity, manual Sunday-calendar verification, browser/accessibility QA, reporting-only retry/reconciliation, and the read-only LinkedIn candidate report.
- Keep all SLA targets, automatic tasks, CRM notes, outbound follow-up, CRM mutations, sends, Marketplace subscription, and private-route automation approval-gated.

## ✅ CURRENT 2026-09-29 Executive Report V1 Response-SLA Detail Closeout

- Read-only V1 response-SLA detail is deployed. The Facts API returns the exact selected window and event rows with contact name/ID, channel, inbound timestamp, owner name/ID, source event ID, response metadata, and status; aggregate counts and the UI review table use the same rows.
- The UI shows Responded, Internal note done, Unmatched, and Ambiguous. Unmatched rows remain open until a valid same-channel response or separately approved internal review record closes them.
- `lt_exec_v1_response_sla_reviews` supports `internal_note_done`; the approved read-only GHL `InternalComment` reconciler is now wired into the materializer. Verification execution `1064337` processed 100 candidates and found 0 qualifying notes, so no rows were written. CRM note creation remains separate and was not performed.
- Final active versions: Response SLA Materializer `5957bf7b-a52f-4131-97a6-cc07303cb4b7`; V1 Facts API `4039aea2-787a-420b-81ef-829b076d5cef`. Final verification executions: materializer `1064144`/`1064303`, post-approval reconciler `1064337`, Facts API `1064291`–`1064293`, all successful. Earlier failed verification attempts were repaired and are documented in the closeout handoff.
- **Approval boundary:** further Speed-to-lead & follow-up implementation remains unapproved for SLA targets, automatic tasks, CRM note creation, and outbound follow-up. The approved internal-note reconciliation is read-only and may update only the reporting review ledger; do not create CRM notes or alter CRM records.
- The complete original Executive Report V1 feedback-retention ledger is in `executive_report_v1_plan.md` and `reports/embed/executive-v1/DATA-REQUIREMENTS.md`. Do not treat the current wired cards as completion of the still-open Meetings/outcomes merge, weekly movement data, newsletter clicker/audience detail, or LinkedIn-backfill split.
- Detailed handoff: `docs/sessions/2026-09-29-executive-report-v1-response-sla-closeout.md`.

## ⚠️ CURRENT 2026-09-29 Executive Report V1 GHL Call Source Handoff

- The V1 SDR call section now displays an exact GHL native-report snapshot for `2026-09-20`–`2026-09-26` only: Marc 1,006 (802 answered, 105 busy, 59 no-answer, 40 failed); Jason 350 (285 answered, 19 busy, 35 no-answer, 11 failed). The native widgets use `dateAdded`, `direction=outbound`, `userId`, and report timezone `Asia/Manila`; the API snapshot is clearly labeled and must not be treated as a refreshed or historical series.
- The V1-only frontend change is deployed at `/embed/executive-v1/`; the legacy `/embed/executive/` report was not changed. V1 Facts API `oxYDg6XnRBKhl1Xd` serves the dated snapshot for that exact window (version `9a17c3c2-45d2-477e-9c01-3bea0a537ae3`).
- **2026-09-29 source investigation update:** the official `/conversations/messages/export` API is documented and PIT-readable for historical date windows, but its exact-week rows/statuses do not match native widget totals. The authenticated GHL Call Reporting UI's private `POST backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new` did match all outbound per-user/status counts for that week (1,377 total rows including 21 inbound; 1,356 outbound). Calling the same private route with the PIT returned HTTP 401. Do not automate this private route; seek documented GHL API access or supported exports. Keep the V1 exact-week snapshot and do not publish unverified export metrics.
- Published active workflow `LT - GHL Outbound Call Event Ledger (Webhook)` (`SA5SF1cZQcVf3IyB`, version `15b2944f-5b71-40fe-b97a-d87718cd6cdb`, 5 nodes) verifies the official GHL `OutboundMessage` signature and idempotently stores outbound CALL events at `/webhook/lt-ghl-outbound-message-call`. Negative-signature tests returned HTTP 401 `invalid_signature`; executions `1062819` and `1062820` did not run the database write node. This proves rejection-path behavior only, not valid-signature acceptance or event delivery.
- **Not wired yet:** GHL Marketplace app `Transparent eCom Social Inbox` must subscribe to `OutboundMessage` and point to `https://automations.livetransparent.com/webhook/lt-ghl-outbound-message-call`. Subscription settings are in Marketplace app configuration, not available through the API; Marketplace developer login was unavailable in the session. App already has `conversations/message.readonly` scope. No live call was placed and no subscription or CRM/report data was mutated for testing.
- GHL PIT can read supported Conversations APIs but receives HTTP 401 from the private report-widget route. The paginated Conversations backfill is still incomplete and must be reconciled before use for arbitrary ranges. Audit source precedence so polling cannot downgrade webhook event facts.
- **Next session:** follow the latest export investigation addendum in `docs/sessions/2026-09-29-executive-report-v1-ghl-call-source-closeout.md`: ask GHL for supported API access to Call Reporting or obtain report exports spanning selected/prior windows, then validate parity and status semantics. Marketplace subscription is optional and forward-only; do not enable it as a historical-data solution. No outbound call test or production data correction without explicit approval.

## ✅ CURRENT 2026-09-29 LinkedIn Identity and Sales Navigator Handoff

- Alexis Mora's authoritative GHL contact is `RGjMxzMqOR2L14ao8qmg` (`firstName=Alexis`, A.MORA Marketing, LinkedIn `alexistaylormora`). No authoritative source for the historical `Angel` greeting was found.
- Personal LinkedIn dispatcher `fXxw5lanZcDmUrst` and DM sequence `d0tEtijajisIsYcs` now require a non-empty provider first name and use it for outbound copy. Partnership/company paths remain GHL-based.
- Outbound GHL mirrors use `/conversations/messages`; inbound LinkedIn bridge posts use `/conversations/messages/inbound`. Published versions are dispatcher `ca663633-143f-4312-9cc3-d0a4ac262661`, personal DM `96f7cf60-97c2-4f54-ba13-20ebf9d49ef1`, partnership dispatcher `44c4ed5f-d5e3-4c75-94f0-1ac21cd7355e`, and partnership DM `9c04b07a-812d-4755-850d-125cadec8c7a`; all were REST-verified with matching draft/active versions.
- Official Unipile docs state that Sales Navigator is enabled in Hosted Auth with `products: ["classic", "sales_navigator"]`; `ACw...` identifies Sales Navigator provider users, `acc_...` identifies v2 Unipile accounts, and `SALES_NAVIGATOR_PRIMARY` starts new Sales Navigator chats. The current legacy `/api/v1` account has not been migrated or verified for that inbox.
- No live LinkedIn sends, account registration, or historical backfill occurred. Preserve the existing Classic connection until a new Sales Navigator-capable account is read-only verified. Cameron must authenticate directly in Unipile; never request/store `li_at`, `li_a`, cookies, API keys, or session secrets in repository artifacts.
- Next: provision/verify v2 Sales Navigator access, add durable personal/hiring exclusions, then generate a deduplicated historical candidate report limited to canonical DM-sequence messages, connection requests, and connection approvals. Detailed handoff: `docs/sessions/2026-09-29-linkedin-sales-navigator-and-identity-eos-closeout.md`.

## ✅ CURRENT 2026-09-29 SimpleTexting Follow-up SMS Sender Personalization

- `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`) is active/published at `b69a183e-273a-43f9-b06d-b2bd1575543b` (`versionId == activeVersionId`; 7 nodes).
- New `Resolve Sender + SMS Templates` node reads GHL webhook `owner` first, then assignee name, then workflow `user`; recognized owner names Marc/Jason are used, otherwise Jason is the fallback. Owner wins if the owner and workflow user differ.
- Legacy `john_sms1`–`john_sms5` templates are dynamically rendered with that resolved sender name; these remain text-only (`AUTO`), without MMS attachments.
- The effective live business-hours gate is weekdays 10:00–17:00 `America/Los_Angeles`. This overrides the stale Eastern-time Config value for this sender.
- Dry-run manual executions `1062414` and `1062422` passed; one rendered Marc for a Marc owner despite a Jason workflow user, and one rendered Jason for a Jason owner despite a Marc user. No provider send was performed. Prior real invocation `1062395` returned `outside_business_hours` under the old Eastern gate and did not reach SimpleTexting.
- No test executions remain `new`, `running`, or `waiting`. The workflow has no automatic replay guarantee for past business-hours rejections.
- **Next:** observe a natural GHL follow-up invocation during Pacific business hours; confirm SimpleTexting provider message ID and delivery callback before claiming delivery. A controlled send still requires explicit approval.

## ✅ CURRENT 2026-09-26 Executive Report QA and V1 Meeting Window Repair

- `ghl_opp_owner_coverage` remains `attention` because the latest QA probe found 4,614 assigned/fallback owners out of 11,569 opportunities (39.9%), below the intentional 50% threshold. The probe succeeded; the data coverage is below threshold.
- V1 meeting details use appointment `start_at` in `America/Los_Angeles`, meaning scheduled meeting time, not booking/creation time. The frontend sent `range=7d`, but the API previously ignored it and defaulted to 30 days.
- `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) now handles `range=7d|30d|90d`; active/published version `677e728d-8f33-4e78-a406-3a0dca56b19e`. A 7-day endpoint check returned `2026-09-18` through `2026-09-24` with 3 rows.
- Executive report API proxy caching is now 30 minutes for Summary, Campaign Channels, and V1 Facts. Cache keys include only the selected range/from/to values, so retry parameters do not create duplicate cold queries. The V1 Facts endpoint is now cached and uses nginx cache locking/stale-on-upstream-error behavior.
- **Inbound Priority router:** `LT - Inbound Intent Priority Router` (`URpjcm2k5isHUyls`) is active/published at `3a3a6ab2-79a3-4fcc-822f-52677b6ae38c` with `versionId == activeVersionId`. It targets `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `Priority` (`be636da7-3c15-48ab-b589-c75bcd6f9955`) and passed mocked pin-data branch tests only. Its execute-workflow trigger remains `triggerCount=0` by design; it is now called by the persisted LinkedIn, Instagram, and SMS inbound branches below. No live CRM mutation smoke test has been run.
- **LinkedIn Priority source integration:** workflow `7o5EBdvwAuIaWW7k` is active/published at `dd98c27b-0fca-491c-bac1-3ff38b1b147b`. Main and partnership inbound branches route only after conversation-state persistence, using resolved `ghl_contact_id`, stable Unipile `message_id`, normalized `timestamp`, and inbound sender/event payload. The router now fetches the live GHL contact owner before any create, so owner resolution is fail-closed.
- **Instagram/SMS Priority source integration:** Instagram `pISlgYUsyJIrLuJd` is active/published at `e09111d7-2c63-4925-b335-741c57f5ab5d`; SMS `i0pROHpFtN4LYR0Q` is active/published at `599995a9-72ce-467d-9892-c7ddf496c3fa`. Both route only after their existing durable claim/contact-resolution/state paths. SMS STOP/unsubscribe events are explicitly excluded from Priority routing.
- **Call/email Priority source integration:** call workflow `PUCfTZBANSPcgS0c` is active/published at `f9388b9a-ab70-45b2-bc77-4f5c2efef829`; its parallel Priority branch requires inbound direction, resolved contact, original timestamp, and stable call ID/composite, and distinguishes voicemail. DAN/Emerald email poller `hxiiYCpEfMuoSt5H` is active/published at `6e60f832-f175-41a8-a4b7-193f286bef18`; it re-fetches actual messages and rejects automated mail before routing. Partnership handler `mRDw57IHtnQe4wOo` is active/published at `42da3b2e-4b6a-4f2f-9341-880b36292eb4` with the same message-level qualifier. No live CRM mutation smoke test has been run. Router lock expiry still requires a durable retry/reconciler for failures that are not replayed.

## ✅ CURRENT 2026-09-26 Newsletter Fail-Closed Repair

- Live inspection confirmed `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`) already selected the newest pending week dynamically and had no hardcoded historical week keys.
- Its scheduled runs were failing when no GHL template matched active pending week `2026-09-21`. The missing-template path now fails closed with a no-op result instead of an execution error.
- Published active version: `dacd2df9-4647-4910-8ea3-857cf889f9b5`; `versionId == activeVersionId`. No manual execution or email send was performed. A matching current-week GHL template is still required before delivery can resume.

## ✅ CURRENT 2026-09-26 Campaign Classifier Repair

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) remains active on its native 15-minute schedule. The current published version is `07e53f3b-c427-4aea-b286-e1071e2b7839`; `versionId == activeVersionId`.
- The paired-item failure at `Upsert Qualified Domain` was repaired. Unknown Warm MQL contacts now pass through DeepSeek instead of being marked `qualified` by bypass, and MQL-derived rows cannot update `vapi_qualified_domains`.
- Sales Outreach promotion now re-checks open and closed Sales Outreach opportunities before moving a qualified Warm opportunity to Sales Outreach -> Qualified. Existing later-stage opportunities are preserved and closed-only records are not reopened.
- Recent pre-repair executions failed at the paired-item boundary; the first post-repair scheduled success remains unverified. Do not claim the repair is runtime-accepted until a new scheduled execution succeeds.
- This workflow does not classify the entire Warm -> New backlog. Warm -> New promotion remains the separate explicit AI-qualification path and is a TODO below, not a completed classifier capability.

## EOS TODOs — 2026-09-26

1. Verify the first post-repair scheduled execution of `IduCoT5YOs0g2faT`; inspect node-level output for DeepSeek decisions, tag writes, domain-cache writes, and MQL promotions.
2. Define and audit the separate Warm -> New qualification path; do not route Warm -> New records through the campaign/Vapi classifier without confirming the explicit AI qualification contract.
3. Reconcile the report's 22 current MQLs against the 15 currently returned by the live GHL Warm -> Qualified (MQL) search; identify snapshot lag, moved records, bounce records, and `not qualified` conflicts.
4. Diagnose `ghl_opp_owner_coverage` at exact opportunity/contact ID level; 4,614/11,569 = 39.9% remains below the 50% threshold. Do not lower the threshold or assign owners without an approved definition.
5. Repair and verify Attribution Bridge execution `1045692`; accept `bridge: ready` only after a successful execution and public health check.
6. Verify the next GA4/GSC bridge and Report Daily Rollups cycle after ingest executions `1048537` and `1048538`.
7. Build the durable retry/reconciler for inbound Priority events whose claimed router executions fail or expire.
8. Keep all outbound send, CRM mutation smoke-test, campaign activation, and sender changes approval-gated unless separately authorized.

## Executive Report V1 session handoff

- ✅ 2026-10-02: Band 1 funnel bloat fixed (`funnel.opportunities_created` now counts opportunities *created* in-window, not observed; 30d 11,461 → 1,387) and "Pipeline to work" fixed by adding `pipelineToWork` (distinct contacts in Sales Outreach — New + Qualified; live 1,057) to the V1 Facts API; frontend redeployed. V1 Facts API `oxYDg6XnRBKhl1Xd` published `9fff955b-96bf-4951-9c75-0054f9792c8d`. Detail: [`executive_report_v1_plan.md`](executive_report_v1_plan.md).
- Read [`executive_report_v1_plan.md`](executive_report_v1_plan.md) before continuing Executive Report V1 work. It is the authoritative session handoff for the V1 plan, source rules, deployment state, verified progress, known gaps, and next audit steps.
- Preserve the current report at `reports/embed/executive/index.html`; V1 is isolated at `reports/embed/executive-v1/` and is deployed only at `/embed/executive-v1/`.

## ✅ CURRENT 2026-09-25 Executive Report V1 Closeout State

- The authoritative handoff is [`executive_report_v1_plan.md`](executive_report_v1_plan.md), updated for this closeout. Its dated 2026-09-25 section supersedes older V1 version/count references below.
- V1 is active at `https://reports.livetransparent.com/embed/executive-v1/`; the current report at `/embed/executive/` remains preserved and unchanged. The deployed static image remains `v3ud1lum1svamymuor21upog:social-mql-20260817`; current-report build remains `2026-08-17-v27-social-mql`.
- `LT - Executive Report V1 Data Materializer` (`knc2wxe4pyYIJ5tw`) is active/published at `47c5aaf8-047c-4cfe-996f-bdcbb97bb04d`; its appointment/contact join now handles direct IDs, `contact:<id>` keys, and raw contact dimension IDs.
- `LT - Executive Report V1 Facts API` (`oxYDg6XnRBKhl1Xd`) is active/published at `677e728d-8f33-4e78-a406-3a0dca56b19e`; meeting details and unique booking counts are restricted to calendar `SrtXcFVyea7pFl3nTiIK` (Regulated Ads On Social/Search) and count distinct contact IDs.
- The V1 meeting panel is titled `Meetings - Regulated Ads On Social/Search`; redundant Cameron/calendar text was removed. The previously missing six names were verified after materializer execution `988447`.
- Executive Summary (`Bukc0mgOD2r7V6ED`) is active/published at `4c5b5611-841b-48a4-9d78-c0700e599e6a`. Its attribution fallback now checks LinkedIn request/DM/reply ledgers and Apollo/Emerald tag evidence before using Unknown. The next successful execution must verify the exact split of the previously 83 unattributed opportunity rows; do not claim those exact rows are fully classified until that read-only check succeeds.
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) is active/published at `24492be1-3b62-436a-8dbe-7f46c64c314e`; SMS counts use the send ledger plus provider delivery events. Leads Ingest (`osIJOgBmWITF5Yuv`) is active/published at `7057fd10-a7db-4888-98ad-4adb1af1c2cc` with `pageSize=100`, `maxPages=1000`, and normalized contact-owner preservation.
- Reporting health repairs are active/published: Attribution Bridge (`Y0TU7Il71JswxOBp`) at `08d15fa4-e513-4ada-939e-51c3584440a7` deduplicates identity-map keys before upsert; Report QA (`M5mXcDTFSko6EdHb`) at `004f260e-7153-4ab7-9e30-dc066ea2458` measures opportunity owner coverage with contact-owner fallback. Queued bridge executions `989774` and `989781` remain unaccepted until they complete successfully.
- Do not treat HTTP 200 with an empty body, queued `new` execution, stale cache, or unverified attribution fallback as a successful closeout. No live outbound sends were performed for this reporting work.
- EOS boundary 2026-09-25: Executive Summary execution `989640` and V1 Facts execution `989659` were still `new`/queued; last accepted successes were `988482` and `988484`, before the final attribution fallback was verified end-to-end. Recheck these executions before relying on the new Apollo/Emerald/LinkedIn source breakdown.

## ✅ CURRENT 2026-09-19 Executive Report Source Health and Cache State

- The Executive Summary API (`Bukc0mgOD2r7V6ED`) is active/published at `00285be3-e4b5-4741-95a9-474b2c74ce00`. It emits `n8n`, `postgres`, and appointment snapshot health rows; the 7-day endpoint returned HTTP 200 with populated data and all three rows `ready`.
- The Executive Report frontend renders the primary summary before campaign-channel and prior-period requests finish. All three report API caches use a 30-minute successful-response TTL with cache locking and stale-if-error fallback.
- This current state supersedes the older Executive Summary version references below. Treat HTTP 200 with an empty report body as a failure, not valid zero data.

## ⚠️ IN PROGRESS: 2026-09-17 Executive Report Email Attribution Audit

- Read-only audit handoff: [`docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md`](docs/sessions/2026-09-17-executive-report-api-regression-and-email-attribution-audit.md).
- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) is active/published at `da17ea49-6473-4e33-9df5-9d93bf6cf273`. It includes the `s.contact_id` fix, attribution response projection, and the later `s.campaign_key`/`s.campaign_group` qualification required after adding `Email_Events.campaign_key`. The embed-query endpoint returned HTTP 200 with 36,184 bytes and populated metrics. Do not revert this version.
- Newsletter dispatcher `vru7OtCkDnPJkWt2` now derives the newest pending week and matching template dynamically; active version `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff`. It currently fails closed when no builder matches the active pending week; no manual sender execution was run.
- Campaign Channel Summary `MvPLbUAN9IIQikxb` now honors explicit `Email_Events.campaign_key` and maps live Emerald event labels; active version `9bcb5e46-f2a4-484a-ad6e-7761c6538cef`.
- Email Event Ingest `ZrqFN8qLKO8eVHDc` now persists message ID, provider message ID, source event ID, campaign key, and sender email; active version `e57c2664-f0f1-484f-b3a6-32bba41ff125`. DAN event automations remain unwired.
- Do not infer historical campaign attribution where the recipient maps to multiple campaigns. Treat HTTP 200 with an empty report body as a failure, not valid zero data.
- **2026-09-17 follow-up regression and repair:** Adding `Email_Events.campaign_key` exposed a second ambiguity in the Executive Summary attribution CTE (`campaign_key` was unqualified after the new column existed). The report endpoint briefly returned HTTP 200 with an empty body, and the embed's fail-soft loader consequently displayed placeholders/zeros. The attribution CTE now qualifies `s.campaign_key` and `s.campaign_group`; Executive Summary version `da17ea49-6473-4e33-9df5-9d93bf6cf273` is active and published. A fresh endpoint call with the embed query returned HTTP 200 and 36,184 bytes; the latest execution succeeded. Do not treat an HTTP 200 with zero bytes as a valid report response.

## ✅ CLOSED OUT: 2026-09-17 Apollo C-Suite and Marketing September 2026 GHL Batch

- Source `Apollo_VP_Contacts.csv` contained 485 rows; 477 apparent new-contact rows were prepared after 8 exact-email matches. The operator completed the prepared CSV imports, including the 32-row phone-collision retry with original phone values moved to `Em_All_Known_Phones`.
- The expected tag count did not appear after the operator’s email/tag-only update import. The assistant directly reconciled 114 source emails with email-based GHL upserts, omitting phone values to avoid phone collisions; all 114 returned contact IDs and verified the required tag `Apollo_CSuite_and_Marketing_Sep2026`.
- GHL’s aggregate tag search remained incomplete/lagging and returned 395 contacts on the final check. Treat that as a searchable cohort boundary, not proof that the entire source cohort is absent from GHL.
- Opportunities were reconciled for those 395 searchable tagged contacts. The destination is `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`) → `New` (`3529dd3d-cab0-4279-967c-1aea203de4fb`). Final state: 361 in the requested stage; 25 already had opportunities elsewhere and were left unchanged; 9 transient create errors were confirmed afterward to already have the requested opportunity. No duplicate opportunities were created by the final reconciled state.
- Detailed handoff: [`docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md`](docs/sessions/2026-09-17-apollo-csuite-sep2026-ghl-import-closeout.md). Do not create additional opportunities solely from the visible tag count; use exact-email/contact-ID reconciliation for any remaining source-cohort recovery.

## ⚠️ IN PROGRESS: 2026-09-16 GHL-Triggered Mass Email Delivery (active, dry-run protection still enabled)

- The generic email-template mass-delivery pipeline is built end-to-end. The authenticated intake, queue, and dispatcher are now **active/published**; queue and dispatcher `defaultDryRun=true`, so scheduled runs remain non-sending until that guard is deliberately changed. One controlled live send to the owner's address was made earlier (see below); all temporary probe contacts were deleted.
- **Schema APPLIED (non-sending):** `postgres/mass-email-bootstrap.sql` was executed against the `postgres` DB. Live tables `lt_mass_email_campaigns`, `lt_mass_email_deliveries`, `lt_mass_email_events`, 4 indexes, and the `lt_mass_email_campaign_metrics` view exist (all empty). Additive columns for the claim model: `campaigns.subject/queued_at/planned_count`, `deliveries.claimed_at/run_id`. The live intake schema node matches the versioned file byte-for-byte.
- **Intake:** `LT - GHL Email Template Trigger Intake (STAGED)` (`t5frjtbuKzVZI294`, version `9523da34-9306-462b-b24f-72594a62a023`, active/published). Webhook `/webhook/lt-email-template-trigger-stage`. Validates the dedicated `X-LT-Mass-Email-Secret`, ensures schema, idempotently upserts one campaign row (`ON CONFLICT (idempotency_key)`), returns `202` with `campaignId`/`created`; unauthorized → `401`, invalid → `400`, no row.
- **Queue:** `LT - GHL Email Template Campaign Queue (STAGED)` (`vRXRFC6IwIxUME2k`, inactive). Claims `accepted` campaigns, paginates GHL contacts, excludes no-email/duplicate/blocked-tag/`validEmail=false`, assigns senders round-robin, writes idempotent delivery rows. `maxRecipientsPerCampaign` bounds a cohort (0 = unlimited).
- **Dispatcher:** `LT - GHL Email Template Campaign Dispatcher (STAGED)` (`b41Sas8FVVrytZrl`, inactive). Resolves GHL template HTML, atomically claims deliveries, re-fetches each contact and fails closed on suppression/lookup errors, enforces per-sender daily caps (2333), sends via GHL Conversations Email, injects signed open/click tracking, captures provider message IDs, retries 429/5xx, finalizes campaign status.
- **Tracking:** open `J7xZH6BBnoXEQsoB`, click `TbYFpB80xSlRZ6gy`, provider events `f87KRQ1Slhs9VUxJ` — all inactive; `Config` now wired between webhook and record node; open/click stamp delivery timestamps; provider responder returns JSON.
- **Acceptance tests PASSED (non-sending):** duplicate retry returns existing campaign; invalid → 400 no row; queue dry-run = planned counts + zero writes; queue live-planning = 5 deliveries round-robin; dispatcher dry-run = 5 planned / 0 sent; dispatch-time suppression blocked a tagged contact (`suppressed:1`, `sent:0`); signed tokens resolve only to the intended delivery (bad token rejected); provider `delivered` updated the delivery; metrics view reported 2 opens as `total_opens=2`/`unique_opens=1` without inflating planned/sent/delivered. All test rows deleted (0 campaigns/deliveries/events).
- **Recipient allowlist:** queue + dispatcher Config carry `recipientAllowlist` (emails; empty = all) and the queue carries `contactIdAllowlist` (GHL contact IDs; skips pagination). Both are currently set to `edmundocadorniga@gmail.com`, so the pipeline can only plan/send to that address.
- **First controlled live send (2026-09-16):** one campaign (`allowlist-test-2026-09-16`, template `6a87716221922afe5eda9e6f`) sent to exactly one recipient from `cameron@livetransparent.co`; delivery `id=8` = `sent`, provider message `lbOQGrp4bxMvxIBNNFlq`; campaign `completed`. Dispatcher returned to `defaultDryRun=true` immediately after.
- **DELIVERABILITY ROOT CAUSE (2026-09-16, proven with mail-tester):** GHL LC Email for this location sends **all** mail through the `.com` sending subdomain `mg.livetransparent.com` (Mailgun `use4.send.mailgun.net`) regardless of the `emailFrom` domain. A `From:` on `.co`/`.agency`/`.org` therefore does not match the SPF/DKIM domain → **SPF and DKIM do not align → DMARC fails** for the From domain, so Gmail filters/spams it (also a look-alike-domain signal). Gmail later located the original `.co` test in spam; its headers showed `From: cameron@livetransparent.co`, `Reply-To: cameron@mg.livetransparent.com`, `mailed-by: mg.livetransparent.com`, and `signed-by: mg.livetransparent.com`, confirming delivery through the `.com` transport with a different `.co` From identity. Evidence: From `cameron@livetransparent.co` = **5.6/10, "You're not fully authenticated", DMARC fail**; From `cameron@livetransparent.com` = **8.8/10, "You're properly authenticated"**. **Fix applied to the mass-email pipeline:** sender pool is now `cameron@livetransparent.com`. **Confirmed 2026-09-16:** a fresh-subject send from `cameron@livetransparent.com` arrived in the inbox (not spam); Gmail showed `mailed-by: mg.livetransparent.com` and `signed-by: mg.livetransparent.com`, which match the `@livetransparent.com` From. **Still outstanding:** the live newsletter dispatcher (`vru7OtCkDnPJkWt2`) still uses `.co`/`.agency`/`.org` senders and has the same DMARC failure. GHL UI now shows all four dedicated domains present with `SSL Issued`; only `mg.livetransparent.com` is selected, while `.agency`, `.co`, and `.org` are unselected at warmup Stage 1 (0/1000). Select/enable a domain before testing its sender; if only one domain may be selected, keep `.com` selected and use only its sender.
- **Known limitation:** the GHL email-builder API does not expose a template subject; the dispatcher resolves subject as operator `subject` → parenthesized template name → template name. No mass-email unsubscribe webhook (provider-event only). Open/click/provider tracking workflows remain **inactive**, so open/click events are not recorded until activated.
- **Pre-activation hardening applied:** the intake validates `X-LT-Mass-Email-Secret`; the provider-event webhook validates a separate `X-LT-Mass-Email-Provider-Secret`, uses `POST` for body-bearing callbacks, and maps handler status codes to the actual response. Open/click tracking remains `GET`. The intake is active/published; provider events and open/click tracking remain inactive pending caller configuration and approval.
- **Next:** obtain approval for a broader live send naming template, cohort, max recipients, sender boundary, and window; verify SPF/DKIM/DMARC; optionally activate the tracking workflows; then flip the dispatcher `defaultDryRun=false` for that campaign only. Separate approval is required before activation or live sending.
- Detailed handoff: [`docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md`](docs/sessions/2026-09-16-ghl-triggered-newsletter-design.md). Project status: [`Project Status and Next Steps.md`](Project%20Status%20and%20Next%20Steps.md).

**2026-09-17 live-state supersession:** Queue `vRXRFC6IwIxUME2k` and dispatcher `b41Sas8FVVrytZrl` are now active/published at versions `714b2d22-777c-4006-a233-d7e0fa6eb930` and `bf892c33-edca-416d-9b74-cff2ccea9fdf`. Both Config nodes use the sender pool `cameron@livetransparent.co,cameron@livetransparent.org,cameron@livetransparent.agency`; temporary recipient/contact allowlists are empty; the suppression blocklist is preserved. Both still have `defaultDryRun=true`, so scheduled activation has not enabled provider sends. Queue execution `956286` and dispatcher execution `956284` succeeded with zero live sends; execution `956269` also completed. No `new`, `running`, or `waiting` executions remained at final verification. Treat older inactive/.com-only statements in this historical section as superseded. Next step is transport-level SPF/DKIM/DMARC verification per sender, followed by an approved change to `defaultDryRun=false` for the intended campaign.

## ✅ CLOSED OUT: 2026-09-16 LinkedIn Outbound Safety Bug Fixes

- Active LinkedIn dispatcher, DM, Partnership dispatcher/DM, and suppression workflows were updated and published after the confirmed daily-limit, duplicate-send, literal-secret, and outbound-message-validation audit. Fresh GETs verified all five are active with `versionId == activeVersionId`; exact versions and evidence are recorded in [`docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md`](docs/sessions/2026-09-16-linkedin-outbound-safety-bugfix-closeout.md) and `Project Status and Next Steps.md`.
- Actual template literals were parsed from the live registries: zero apostrophes and zero non-ASCII characters. Do not use whole-node character counts as copy proof because sanitizer tables and JavaScript syntax create false positives; use literal-level extraction.
- Remaining approval-gated work: validate `X-LT-LinkedIn-State-Secret` on the receiver, migrate hardcoded credential fallbacks, and implement the durable inbound-reply suppression design. Do not manually execute sender workflows or send tests without explicit approval.

## ⚠️ IN PROGRESS: 2026-09-14 LinkedIn Reply Suppression Review and Handoff

- Read [`docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md`](docs/sessions/2026-09-14-linkedin-reply-suppression-audit-and-plan.md) before changing LinkedIn senders. It records the live workflow IDs/versions, verified gaps, the refined design, test boundaries, and next steps.
- Current decision: do not treat a per-send GHL `lastMessageDirection=inbound` lookup as the primary guarantee. Build a durable LinkedIn-specific reply suppression record from inbound Unipile events before slower CRM writes; gate every automated LinkedIn invite/DM sender on it, with GHL checks as a fail-closed reconciliation fallback.
- Confirm the exact prospect/conversation and originating sender execution before attributing the supplied repeated-message screenshot to a workflow. Its repeated copy matches the connect-invite template; the partnership DM sender has a separate, confirmed cached-state-only gap.
- Preserve normal human replies through the GHL custom-provider outbound router. Scope suppression to automated outreach; do not block all GHL-originated LinkedIn messages.
- No production workflow, CRM record, campaign, sender, or live test was changed during this read-only review. Production workflow changes and live sends require explicit approval. The supplied screenshot is identifying prospect data and remains untracked/local; do not stage it.

## ✅ CLOSED OUT: 2026-09-11 Documentation Staleness Audit

- `AGENTS.md`, `plan.md`, and `Project Status and Next Steps.md` were reconciled against the September 2026 LinkedIn, runner, reporting, and SDR closeouts.
- The detailed handoff is [`docs/sessions/2026-09-11-documentation-staleness-audit-closeout.md`](docs/sessions/2026-09-11-documentation-staleness-audit-closeout.md).
- No production workflow, CRM record, campaign, sender, deployment, or live test was changed during this audit. The worktree remains intentionally dirty; stage reviewed files individually.

## ✅ CLOSED OUT: 2026-09-10 Business Improvement Plan and Shareable Guides

- `improvementPlan.md` is a review-only strategic plan for Transparent eCom. Its opening now contains a plain-language summary, document map, jump links, role-specific reading paths, video-informed positioning, customer FAQ, reusable messaging, a Cameron booking bridge, and Executive Report simplification recommendations.
- The full plan was converted to `Transparent eCom Business Improvement Plan - Full.docx`; it remains untracked and uncommitted. The condensed Google Doc and full converted Google Doc are documented in `Project Status and Next Steps.md` and the detailed closeout under `docs/sessions/`.
- The condensed guide's full-plan link was reinserted after an initial insertion did not persist and was verified in the document contents. Both Google Docs were verified under `ed@livetransparent.com`.
- This strategy/documentation session did not mutate or execute production workflows, GHL records, campaigns, senders, or website deployments. FAQ and claim language requires owner approval and proof references before publication or outbound use.
- The isolated sample landing page was built and deployed for review on 2026-09-10. Deployment details and limitations are documented in `docs/sessions/2026-09-10-sample-landing-page-preview-deployment.md`. The preview remains non-production and requires Cameron approval before any production implementation.

## Sample Landing Page Operating Boundary

- The sample landing page is a review-only prototype in `Sample Landing Page/`; its implementation plan is `Sample Landing Page/PLAN.md`.
- Build it as plain static HTML, CSS, and JavaScript. Keep it isolated from the production website, CRM, GHL workflows, campaigns, senders, and live tracking.
- Use a non-submitting CTA placeholder during early review. The approved GHL booking widget may be added only after page structure and copy are accepted.
- The sample preview may remain deployed as an isolated review service when explicitly requested. Do not add production tracking, connect CRM/GHL/booking functionality, or change the live website without explicit approval.
- Before any preview deployment, test desktop and approximately 390px mobile layout, accessibility basics, horizontal overflow, and unexpected network requests.
- The current preview uses HTTP at the generated `sslip.io` hostname; HTTPS is not yet working. Do not represent it as a production-ready deployment.

## ✅ RESOLVED: 2026-09-10 GHL PIT Rotation (all workflows + .env)

- Full closeout: [`docs/sessions/2026-09-10-ghl-pit-rotation-closeout.md`](docs/sessions/2026-09-10-ghl-pit-rotation-closeout.md).
- `.env` `GHL_PIT`, `GHL_API_KEY`, `GHL_PIT_LT_HERMES` all = the new full-access PIT (`pit-d25ac994-...`, Ed-supplied; verified GET /locations + POST /contacts/search HTTP 200). Both old tokens (`pit-3f4dc6...`, `pit-48a3...`) were also `pit-`-format and functionally identical — one token now covers all GHL slots including embedded workflow tokens.
- Live n8n: 70/75 workflows rotated via API (backs up pre-change JSON per workflow in `%LOCALAPPDATA%\Temp\lt_pit_rotation\`); re-verified by `scripts/n8n/inventory_n8n_pits.py` — only the new PIT remains in active workflows, all HTTP 200. Dead 401 token `13c5a02e54a2` gone from active workflows.
- Repo exports: 17 JSON files refreshed (0 old tokens confirmed remaining in repo `*.json`). Nothing committed/pushed; `.env` local-only.
- Untouched: `AGENCY_TOKEN_PIT` (agency-scope, unreferenced). Residual old tokens: 5 archived workflows (API cannot update archived; need UI unarchive or delete) + ~19 non-JSON helper scripts (offered to Ed, no permission yet).

## ✅ RESOLVED + MONITORED: 2026-09-07 External Runner PostgreSQL Network Path

- Detailed records: [`docs/sessions/2026-09-07-runner-network-path-fix-applied.md`](docs/sessions/2026-09-07-runner-network-path-fix-applied.md), [`docs/sessions/2026-09-07-runner-network-path-verification.md`](docs/sessions/2026-09-07-runner-network-path-verification.md).
- The live Coolify runner had `extra_hosts: postgres:host-gateway` and was NOT on `coolify-shared`, so `postgres` resolved to stale `10.0.0.1` → `ECONNREFUSED 10.0.0.1:5432` every 2 min on pg-using runner workflows.
- **FIX APPLIED and VERIFIED 2026-09-07 UTC**: removed the runner `extra_hosts`, added `coolify-shared` to the runner's networks, recreated the runner (backup + compose validation first). Runner now dual-homed (`10.0.2.5` shared + `10.0.4.4` private); `postgres` → `10.0.2.3`; TCP `postgres:5432` OK; n8n `/healthz` ok; workflow `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`) went from `ECONNREFUSED` errors to continuous `success`.
- **Monitoring live (replaced 2026-09-09)**: Hermes cron job `LT hourly infra+email monitor (Telegram)` (`9622fde81b78`) every 60 min — deterministic gate `C:\1_Ed's Active Work\AI\Hermes\scripts\lt_alert_gate.py` probes n8n `/healthz`, PostgreSQL container health, runner DNS/state, restart counts, and Gmail alert-subject emails (`[LiveTransparent]` `UNHEALTHY|RECOVERED|ALERT`); the agent runs ONLY when the gate line changes, then classifies from full email bodies, applies read-only + safe auto-fix, and escalates to Ed via Telegram (deliver=telegram, ONE message per issue; ids marked processed only on resolution). Old 30-min jobs `33eea46dd9b3` and `b3f164cd1746` PAUSED (folded into the hourly monitor). Full record: [`docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md`](docs/sessions/2026-09-09-workflow-incident-alerts-skill-review-and-hourly-telegram-monitor.md). Email transport: Hermes Google OAuth Gmail (`edmundocadorniga@gmail.com`), tested in prior sessions.
- The n8n internal pool-closure incident remains OPEN and separate (see below). Do not treat the network fix as proof the pool issue is fixed.

## ✅ IN PROGRESS: 2026-09-09 Executive Report — SDR Performance & Owner Attribution (Phases 1–5 LIVE; monitoring/sign-off remains)

- Request (sales leadership/marketing): track booked meetings by SDR for the end-of-month SDR assessment (focus SQL/booked meetings), plus per-SDR owner attribution, showed/no-show, SQLs created, MQL→SQL conversion, lead source for MQL/SQL, and clarification of the former owner-labelled active-deals view.
- **Phases 1–2 IMPLEMENTED and verified 2026-09-09** (operator sign-off on Phase-0 decisions: canonical booked meeting = appointments by `start_at`; owner authority = native opportunity `assigned_to` primary + contact fallback + explicit Unassigned bucket; SDRs = Jason + Marc). Details + verification: `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase1-2.md`.
  - `report_sdr_registry` DDL + seed in `postgres/reporting-bootstrap.sql`, applied live (Jason/Marc SDR; Cameron leadership; Ed exec; Janvi resolved as non-SDR; Kevin/Mike/Remus informational).
  - Daily Rollups `EUeOiRttoVLQ9zF9` active `1af59845…` carries `assigned_to` through `tmp_report_opps`/`tmp_daily_opps_fixed`.
  - Report QA `M5mXcDTFSko6EdHb` active `a21c0f4a…` probes `ghl_opp_owner_coverage` (34.6%) + `ghl_appt_owner_coverage` (11/31) into `report_source_health`.
  - Exec Summary `Bukc0mgOD2r7V6ED` active `90bcc99f…` returns `sdrPerformance` per-owner rows; `meetingsBooked` aligned to appointments (`basis appointments_start_at`, `meetingsBookedStageBasis` kept); query now runs `SET jit=off` (16–19s vs ~71s before). Postgres credential `pgAzUqpwOiGkGXzO` retained on all nodes.
  - Frontend `reports/embed/executive/index.html` deployed as build `2026-09-09-v28-sdr-performance` (backup `index.html.bak-20260909-022102` in the reports container): SDR Performance table + nav item + glossary, former owner-labelled active deals view → "Team Active Deals". Desktop + 390px verified, no overflow, only benign favicon 404.
  - **Phase 4 IMPLEMENTED 2026-09-09**: Lead Source panel (MQLs Entered / SQLs Created by originating source) in Exec Summary `Bukc0mgOD2r7V6ED` (new active version `162bbba8-0b28-425d-891c-488bd00bc781`, `versionId == activeVersionId`, postgres cred `pgAzUqpwOiGkGXzO` retained). New CTEs `lead_source_contacts` / `lead_source_bridge` / `lead_source_mql` / `lead_source_sql` / `lead_source_breakdown` / `lead_source_coverage` resolve each MQL/SQL opportunity's contact → first UTM source (medium/campaign) with `report_bridge_traffic_to_lead` fallback, then GHL contact `source`; breakdown caps at 20 rows, coverage reports attributed/total (30d: 32/164 SQLs, 0/3 MQLs — bounded by the ~500-row Leads snapshot). Query timing unchanged (~17s JIT-off). Frontend build `2026-09-09-v29-lead-source` deployed (backup `index.html.bak-20260908-185312`), Lead Source nav item + panel + glossary card, desktop + 390px verified no overflow, zero console errors. Details: `docs/sessions/2026-09-09-executive-report-sdr-attribution-phase4-lead-source.md`.
- **Phase 3–5 status (2026-09-09 session)**: Unknown owners resolved + seeded — `ck6TRlU3wnTmMxuVpn5F` = **Janvi Mahajan** (`janvi@livetransparent.com`, non-SDR; resolved via live GHL `GET /users/`), Kevin `7s3brzxGF4WSiz95DPkF` / Mike `D8NgkeZYX481rR4J2gOc` / Remus `R5VljBpXah3LaVXFNfCV` added informational; `report_sdr_registry` = 8 rows applied live (bootstrap staged/uncommitted). **GA4+GSC stale was diagnosed + RESOLVED 2026-09-09** — both n8n Google OAuth credentials had re-expired (~09-03/09-04); the operator reconnected them 09-09 and I verified (manual runs GA4 `916807`, GSC `916808`, bridges+rollups `916815-916817`; data current through 09-07; `report_source_health` ga4/gsc `success`). **Phase 3 (Showed/No-show) IMPLEMENTED + LIVE 2026-09-09**: `LT - Meeting Outcome Reminder` (`x5vUQ34IcyKggdqP`, active `cf3c0d72…`, `versionId==activeVersionId`) posts a per-SDR pending-outcome digest to Slack `#sales` Mon–Fri 08:00 LA (smoke `916780`); SDRs mark Showed/No-Show in GHL and the 6-hourly Appointments Ingest (30d look-back) re-syncs status — no report/ingest change. Phase 5 scope confirmed: rank SDRs on **Booked + SQLs + MQL→SQL** (non-SDR/Unassigned rows shown but excluded). Stage-based MQL authoritative (140 total / 3 entered 30d) vs tag ledger 31 (27 in 30d). Details: `docs/sessions/2026-09-09-sdr-attribution-phase3-5-owners-and-ga4-gsc-diagnosis.md`.
- **Post-implementation follow-up**: monitor the daily 08:00 LA meeting-outcome digest runs (Slack `#sales`) and confirm SDRs start marking Showed/No-Show in GHL; get Cameron/Janvi sign-off on the confirmed per-SDR ranking scope wording (Booked + SQLs + MQL→SQL); confirm nightly Rollups/QA health after GA4/GSC reconnection. Janvi and the previously unknown owner IDs are resolved and seeded. Full plan: `docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md`.

## ⚠️ IN PROGRESS: 2026-09-10 SDR attribution for regulated-ads bookings (booking webhook capture deployed)

- **Problem:** An SDR who books a regulated-ads meeting on Cameron's calendar (`SrtXcFVyea7pFl3nTiIK`) gets no credit in `sdr_booked`: at booking, opportunity ownership flips to Cameron and the SDR is recorded NOWHERE that survives (appointments `createdBy.source=booking_widget` userId null; opp created unassigned/Cameron; contact `assignedTo` never an SDR). Confirmed to GHL source of truth; **historical bookings unrecoverable — future-only fix**.
- **Root-cause anchors:** routing stamps `opportunity_owner_sync` → contact field `FQv9wyl2JrMkpf1GPprP`, `opportunity_owner_change` → `IPzJpFLekz9TDi4nWBaV`, written by GHL workflow **`LT - Opportunity Owner Alignment`** (`b26326a5-77af-4df8-8d86-3f636e73afe0`, v7, branches Jason/Marc by `assignedTo`).
- **GHL field DONE:** Contact custom field `Originating SDR` exists as `TEXT`, field id `wBGXjev0rKowcfxTSWNa`. Its value is the assigned user's email in the booking webhook; n8n maps Jason/Marc/Cameron emails to their GHL user IDs.
- **Correct booking boundary identified:** GHL workflow `Appointment with Cameron for Regulated Ads` (`971c3016-946a-4612-ad0a-2afc9a0ee6f0`) is confirmed `published`, version 14, updated 2026-09-09 17:09:26 UTC, and posts to `https://automations.livetransparent.com/webhook/wl-slack-channel-update-v2`. This is separate from `LT - Opportunity Owner Alignment`, which remains owner synchronization only. The public GHL workflow-list API does not expose action bodies, so the `assignedSDR` payload still requires runtime webhook confirmation.
- **n8n implementation LIVE:** `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) active/published at version `1cb05fcd-e0c0-4ae1-9413-637878325e8e`. Its `Build Slack Payload` node reads `assignedSDR`, writes field `wBGXjev0rKowcfxTSWNa` before SQL-tag/opportunity mutation, and skips stamping when the value is missing or unrecognized. The Exec Summary `Bukc0mgOD2r7V6ED` was also activated with field id `wBGXjev0rKowcfxTSWNa` in version `08abd9cb-7100-4e31-88d1-4413aadee625`; both workflows have matching draft/active versions.
- **Verification boundary:** Live workflow reads after deployment passed; no production test execution was run because the webhook performs CRM writes and sends Slack. No executions are currently `new`, `running`, or `waiting`.
- **Next:** observe the next real booking webhook and verify the already-published GHL workflow supplies custom-data key `assignedSDR`, then confirm `sync.originatingSdr = stamped`, the contact field value, and the resulting SDR row in Exec Summary. Historical bookings remain unrecoverable.

## Document precedence (applies to all future work)

1. Live Coolify/n8n state (authoritative: generated `/data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml`, container state, health endpoints)
2. `Project Status and Next Steps.md`
3. Latest dated session handoff under `docs/sessions/`
4. This file's operating rules / safety gates
5. `plan.md` and `repomix-output.md` — historical/archive material; not operational source of truth

## ✅ RESOLVED: 2026-09-02 n8n Compose Database/Runner Hardening

Updated `n8n/docker-compose.yml` after diagnosing transient n8n readiness failures and runner `pg` resolution issues. The changes are committed and pushed in commit `27dea1e`.

### Persistent Compose Changes

- n8n and the inline runner base image were pinned to `2.36.9` at that time; the deployed version is now `2.37.10` (2026-09-07 force redeploy). Concurrency/health settings below remain in effect.
- Production execution concurrency is capped at 5 with `N8N_CONCURRENCY_PRODUCTION_LIMIT=5`; the runner task concurrency remains 10.
- PostgreSQL idle connections are recycled after 30 seconds and pooled connections after 30 minutes.
- n8n database health monitoring pings every 5 seconds and begins recovery after 3 failures, with 1-30 second exponential backoff.
- Runner idle shutdown is set to 300 seconds and runner concurrency is set to 10 in the Compose service environment.
- The Coolify/Compose runner uses the pnpm module path `/opt/pg-node_modules/node_modules` for `pg`. Do not use the standalone runner path `/opt/pg-node_modules` here; that npm-layout path applies only to `scripts/deploy/deploy_runner.py` and `n8n/runners/Dockerfile`.
- Both services use the external `coolify-shared` network, and the n8n service retains the `n8n` network alias required by the runner broker URI `http://n8n:5679`.

### Verification

- `docker compose -f n8n/docker-compose.yml config --quiet` passes with `N8N_RUNNERS_AUTH_TOKEN` supplied by the deployment environment.
- `git diff --check` passes.
- After the deployment restart, `https://automations.livetransparent.com/healthz/readiness`, `/healthz`, and `/` returned HTTP 200. A temporary 404/bad-gateway symptom occurred during container recreation and cleared without a configuration rollback.
- Do not commit the untracked PowerShell investigation scripts from the September 2026 session; several contain embedded GHL bearer tokens. Use environment-based `GHL_PIT` access instead.

## ⚠️ OPEN: 2026-09-07 n8n PostgreSQL Pool Closure Investigation

The later n8n incident is documented in [`docs/sessions/2026-09-07-n8n-pool-closure-investigation.md`](docs/sessions/2026-09-07-n8n-pool-closure-investigation.md). The immediate mechanism is confirmed: n8n remained alive while its internal PostgreSQL pool was already ended, producing `Cannot use a pool after calling end on the pool`, readiness failure, and authenticated API HTTP 503 (`Database is not ready!`). PostgreSQL connectivity, credentials, runner networking, and substantive Compose alignment were not shown to be the primary cause.

The original event that called `pool.end()` remains unresolved. No restart, deployment, workflow operation, configuration write, or database change was performed during the initial investigation. A September 4 kernel soft-lockup involving `postgres` and `soketi-server` is a clue but not proven causal because the first retained pool error was September 7. The live stack was subsequently force-redeployed on n8n `2.37.10` and is monitored, but that does not identify the original caller. If the pool-closure symptom recurs, correlate Docker/Coolify, PostgreSQL, n8n, runner, host, and network events before an approved n8n-only restart. Do not restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` casually.

## ✅ RESOLVED: 2026-08-30 Executive Report Audit & Fixes

Full 7d/30d cross-check of the Executive Report (`https://reports.livetransparent.com/embed/executive/`) against source Postgres tables. The report page was **completely down** — nginx returned 504 because the Executive Summary query took 76.5s (nginx default proxy_read_timeout is 60s). Fixed everything and cut query time to ~15s.

### Changes made (all in `LT - Report Executive Summary API`, active version `11ca17d6-fba7-4fe3-b45c-4c8522ca9e49`)

| Fix | Detail |
|-----|--------|
| **nginx 504** | `reports/nginx.conf` now sets `proxy_read_timeout 300s; proxy_send_timeout 300s; proxy_connect_timeout 10s`. Applied to the running `reports-livetransparent` container + `nginx -s reload`, and committed to the repo. **Permanent via rebuild** — `reports/Dockerfile` copies `reports/nginx.conf`, so the next image build bakes it in; the currently-running container still has the old image until rebuilt. |
| **GHL Calls read wrong table** | The `calls` / `call_status_breakdown` / `call_outcome_breakdown` / `call_outcomes` CTEs read `report_raw_ghl_call_outcomes` (Vapi/GHL outcome table, stale since 08-10) → reported **0 calls**. They now read `report_raw_ghl_calls` (the working GHL Conversations ingest, every 4h). 7d window: 201 calls (115 completed, 51 no-answer, 19 busy, 12 failed, 4 ringing; 4 inbound / 197 outbound; answered 115, missed 82). |
| **Duplicate "Unassigned" channels** | `channels` CTE outer SELECT used `COALESCE(NULLIF(g.channel,''),'Unassigned')` so any row coming only from the rollup side (`r`) was labeled "Unassigned", producing two identical rows. Fixed to `COALESCE(NULLIF(COALESCE(g.channel, r.channel),''),'Unassigned')`. |
| **Vapi timezone buckets** | `vapi_timezone_buckets` counted ALL queue rows ever (2708) and emitted camelCase keys the frontend can't read. Now `WHERE status='pending'` (39) and emits both camelCase AND snake_case keys (`total_queued`/`explicit_count`/`inferred_count`/`none_count`) the deployed frontend expects. |
| **Stage movedIn boundary bug** | `stage_daily` CTE fetched from `$1 - 1 day` for the LAG baseline but did NOT filter the output to the window, so the entire previous day's `stage_count` was counted as "moved in" (Warm New movedIn 5476 vs true 1679). Added `WHERE x.report_date >= $1::date`. |
| **Perf: vapi timezone cross join** | `vapi_timezone_buckets` joined `voice_call_queue` to `vapi_contact_timezone_snapshots` with an `OR` on two normalized IDs → forced a 6.28M-row nested loop (~12s). Replaced with a single equality join on `LOWER(TRIM(REPLACE(q.contact_id,'contact:','')))`. |

Overall Exec Summary query went from **73–77s → ~15–21s** (both 7d and 30d verified through the proxy).

### Pipeline fixes
- **Pipeline Velocity** (`iFfwh0jpYUZoDhDR`): schedule was `hoursInterval:24` and had **0 executions ever** (stale data since 08-24). Changed to daily cron `0 9 * * *` (UTC), published (`09e0f2e7-193b-4102-9008-4ec33bda02d2`), and manually re-ran (execution `832368`) so `report_stage_velocity_summary` is fresh. Health now `ready`.
- **Sender schedules are NOT broken** — the Vapi dialer (`*/2 9-16 * * 1-5`), LinkedIn DM Sequence (`0 12-22 * * 1-5`), IG Company Sender (`0 10-15 * * 1-5`), and LinkedIn Dispatcher (`*/15 15-21 * * 1-5`) are all **weekday-only cron schedules** in America/Chicago or America/Los_Angeles; the apparent "outage" was just the weekend. They will resume Monday. (A harmless deactivate/reactivate cycle was done during diagnosis.)

### Findings needing operator action
- **GA4 resolved 2026-08-31** — the Google OAuth credential was reconnected by the user. `LT - GA4 Daily Ingest` was manually re-run (execution `832654`) and backfilled the entire 08-14…08-29 gap; the GA4 Traffic Rollup Bridge + Daily Rollups were re-run so `report_daily_summary.sessions` is current. The 7d report now shows traffic=174, users=166, real channel breakdown (Direct 43, Email 102, Organic Search 15…), and ga4 health `ready`. **⚠️ Re-broken 2026-09-09 → RESOLVED**: both GA4 (`Google Analytics account`) and GSC (`GSC - Cameron Livetransparent Google account`, id `EKnNrSvlEd0A99AX`) n8n OAuth credentials expired again ~09-03/09-04 (GA4 frozen at 09-02, GSC at 09-03; Exec Report health showed `stale`). **Reconnected by the operator 2026-09-09 and verified**: manual GA4 ingest run `916807` (853 rows, self-backfilled 90d through 09-07), GSC `916808` (13 rows through 09-07), GA4 Bridge `916815` + GSC Bridge `916816` + Daily Rollups `916817` all success; `report_daily_summary.sessions` restored 09-03…09-07 (25/10/5/11/13) and `report_source_health` ga4/gsc = `success`. GA4 data for 09-08 flows on the next scheduled GA4 run (~13:31 UTC) + Rollups.
- **LinkedIn senders: root cause = temporary LinkedIn restriction, now cleared + fixed.** Around 08-28 17:00 UTC the Unipile LinkedIn account hit a temporary LinkedIn sending restriction — every `/users/invite` and `/chats` returned 422. **Verified cleared 2026-08-31**: a live `/users/invite` to a previously-failed ready-pool target returned HTTP 201 (invitation_id `7499980380033150976`). The restriction was likely the weekly invitation limit. Fixes applied:
  - **Dispatcher stuck-claim bug (the real accumulation)**: `Fetch Ready Queue` claimed `ready`→`requested_pending` and when the daily invite limit was reached it returned early WITHOUT releasing the claim — so claimed rows accumulated forever (5,046 stuck rows, all `request_sent_at IS NULL`). Released all 5,046 back to `ready` and added a self-healing `released` CTE to the claim SQL (releases `requested_pending` rows older than 30 min with no confirmed send). Dispatcher published `7b002976-9e3e-450e-9c36-073e13c4e342`.
  - **DM Sequence unreachable recipients**: 5 connected contacts (perrychase, darrylbryanallen, adolfo-araiza, cceciliaw, alison-li-lin) have genuinely unreachable LinkedIn profiles (Unipile `errors/invalid_recipient` on both provider-id and public-identifier lookups) and were clogging the hourly batch. The selection query now excludes `payload_json.dm_unreachable='true'`, the send code marks contacts `dm_unreachable` on invalid_recipient detection, and the 5 current ones are flagged. DM Sequence published `e99b0d0d-b90f-4e41-89bd-164c98e48c7e`.
  - The dispatcher's 08-28 invite failures were the temporary restriction (not a code bug); the DM sequence's 08-28 failures were the 5 unreachable profiles + the restriction. Sender schedules resume Monday.
- **GSC reconnected 2026-08-31** — the user reconnected the Search Console credential; `LT - GSC Daily Ingest` re-ran successfully (execution `832997`) and health is now `success`. It uses a 3-day rolling window (Config computes `end=yesterday, start=end-2`), so the 08-08…08-29 outage gap was NOT backfilled — but GSC volume is negligible (0 clicks, ~30 impressions/month), so the impact is immaterial.
- **Contact acquisition UI cleanup (2026-08-31)** — `contact_sources` CTE now relabels GHL/msgsndr tracking-link landings (`/links/`, `msgsndr.com`) as a single `Email/SMS link` source with a blanked landing page instead of ~17 one-contact rows carrying unreadable `services.leadconnectorhq.com/links/r/2/{JWT}` URLs. 18 link-click contacts now aggregate into one row. Exec Summary version `a66e1914-7ff0-4414-b218-9f688b52803a`.
- **OpenRouter credits restored 2026-08-31** — user added credits; no further `402 Insufficient credits` errors in n8n logs (affects IG/Dispensary/Partnership enrichment + DeepSeek classifier).
- **`sqlContacts`/`poolDistribution` fixed (2026-08-31)** — these read `report_raw_ghl_contacts`, but the pool tags are NOT real GHL tags (`brands_pool`/`dispensaries_pool`/`vapi_campaign_*` return 0 via GHL `/contacts/search`; they are source-list designations in `emerging_pool_contacts`). Exec Summary `pool_distribution` now reads `emerging_pool_contacts` for `brandsPool` (3,668) / `dispensariesPool` (10,200) and `voice_call_queue` for `vapiBrand` (106) / `vapiDispensary` (66 distinct contacts). `sqlContacts` reads the `sql` GHL tag (36 contacts): backfilled once into `report_raw_ghl_contacts` and now re-snapshotted daily by a `sql`-tag fetch added to `LT - GHL Daily Leads Ingest` (idempotent, `report_date` = LA-yesterday so it lands in the current window). Exec Summary version `9c43be7d-7160-448f-82be-00e5f8303b88`.
- **n8n runner `pg` + network fix (2026-08-31 diagnosis, superseded 2026-09-07)** — the Coolify-managed runner initially had an incompatible `NODE_PATH` and stale PostgreSQL host mapping. The repository and live Coolify stack were corrected, the runner was recreated on `coolify-shared`, DNS/TCP resolution was verified, and a pg-using dialer workflow returned continuous success. Treat the network path as resolved and monitored; do not re-apply the old drift diagnosis unless the monitor alerts. See `docs/sessions/2026-09-07-runner-network-path-verification.md`.
- **`report_raw_ghl_call_outcomes`** is now effectively deprecated for the report (reads `report_raw_ghl_calls`). Note: `LT - Call Outcome Ingest` (`PUCfTZBANSPcgS0c`) writes to database **`n8n`** (not `postgres`), so its rows never reach the report DB — a pre-existing misconfiguration worth fixing.
- **Newsletter is live** — `newsletter_send_log` shows 19,739 sent + 101 failed in the 08-23…08-29 window. The DNS-gate note is stale; go-live happened 2026-08-21. The current dispatcher uses 250-row batches every 15 minutes Monday-Friday, with a database-backed cap of 2,333 per sender (6,999/day). Report folds newsletter metrics into email metrics with these definitions:
  - `emailsSent` = **unique sends** (one row per `ghl_contact_id + week_key` in `newsletter_send_log`; UNIQUE constraint ensures no duplicates)
  - `emailsOpened` = **total open events** (counted from `newsletter_events`; a single contact can have multiple open events tracked via HMAC pixel)
  - `emailsClicked` = **total click events** (counted from `newsletter_events`; a single contact can have multiple clicks tracked via HMAC link rewriting)
  - `emailsUnsubscribed` = **unique unsubscribes** (one row per contact who clicked unsubscribe link; logged in `newsletter_events` and `newsletter_send_log`)
  - `newsletterFailed` = **failed send attempts** (rows marked `status='failed'` in `newsletter_send_log`; 101 in last window)
  - Rates (`emailOpenRate`/`emailClickRate`/`emailBounceRate`) are computed from **unique recipients** in the window send cohort
- `sqlContacts`/`poolDistribution` were historically limited by the 500-contact GHL snapshot; the current Executive Summary uses the SQL tag ledger and source tables where available. Treat remaining coverage gaps as data-source limitations, not as evidence that the report logic is still returning zeroes.

## ✅ RESOLVED: 2026-08-12 Postgres Write Blocker

**The n8n Postgres node v2.5+ has a known bug where `queryReplacement` silently fails to persist data.** This affects ~25 Postgres nodes across ~12 workflows. The root cause is that parameterized queries (`$1, $2, ...`) fail to commit in n8n's embedded task runner.

### Current Strategy: External Task Runner

The fix is to switch n8n from embedded task runner mode to **external task runner mode** (`N8N_RUNNERS_MODE=external`). This requires:
1. A custom `n8nio/runners` Docker image with the `pg` module installed
2. The `NODE_FUNCTION_ALLOW_EXTERNAL=*` override in the runner config and runner container
3. Code nodes using `require('pg')` for direct Postgres connections (bypassing the broken Postgres node)

### What's Already Done

| Area | Status |
|------|--------|
| **Frontend fixes** (CSS, mappings, CORS proxy, outgoing calls) | Deployed to live |
| **Database tables** (emerging_pool_contacts, DAN/Emerald release logs, Email_Events) | Created |
| **LinkedIn workflows** (6 workflows, 16 nodes) | Published with fix |
| **Campaign/Email workflows** (4 workflows, 4 nodes) | Published with fix |
| **GHL Leads Ingest** (4 Postgres nodes) | Published with fix |
| **GHL Sales Ingest** (`aYT5oHcgmBALzHy5`) | Published with fix (version `91603d56`, execution `743094`, 7,984 opps) |
| **Call Outcome Ingest auth** (`PUCfTZBANSPcgS0c`) | Published with secret header (version `7af98411`) |
| **Executive Summary query/runtime recovery** (`Bukc0mgOD2r7V6ED`) | Fixed (version `d177a923`, corrected stage-velocity date column and removed redundant campaign lookup) |
| **Report timezone drift** (both report workflows) | Fixed (timezone-aware `isoDateInTimezone()` in both Normalize nodes) |
| **Voice dialer Postgres migration** (`r7UjWLndmc6EqEUW`) | Fixed (version `b8e9c57a`, 4 nodes migrated from broken Postgres v2.6 to direct pg) |
| **Voice callback Postgres migration** (`fx4UvKUWbqJEY3LK`) | Fixed (version `c97480db`, 8 nodes migrated from broken Postgres v2.6 to direct pg) |
| **Voice dialer release-lock verification** (2026-08-14) | Shared scheduled Vapi path verified across 13 consecutive successful executions, including `746845`; no recurrence of `there is no parameter $1`. Not a manual-dialer or Twilio issue. |
| **Voice queue enqueue persistence verification** (2026-08-14) | Found a second active voice path still using Postgres v2.6 `queryReplacement` in `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`). Replaced `Postgres - Insert or Noop` with direct `require('pg')`, published version `42aba803-09b0-4118-a105-9161bebe66e9`, and verified `versionId == activeVersionId`. |
| **Voice intake poller hardening** (2026-08-14) | Published `LT - Voice Queue Vapi Intake Poller` (`bYk1Ai6MJLyhTsDZ`) on `5c464233-c79a-4f49-a809-de303f3b6136`. Aligned terminal blocklist tags with enqueue, routed suppressed contacts through the skip branch, surfaced tag add/remove failures, and made queue insert/no-op outcomes explicit. Smoke execution `747051` succeeded. |
| **Voice intake Apollo tag-context fix** (2026-08-14) | Published `LT - Voice Queue Vapi Intake Poller` on `d852a93d-b468-4b9b-8cc9-d4995131f926`. Preserved the classified campaign tag across the Apollo HTTP response boundary so `Remove Tag - Enriching` removes the actual campaign tag instead of falling back to `vapi_queue`. Verification execution `747053` showed `tagsRemoved: ["vapi_campaign_brand"]` and succeeded. |
| **ghl_contact_id re-backfill** | 12,639/13,868 matched from GHL export CSVs (1,229 not in exports) |
| **Embedded secrets audit** | 12 critical, 5 high, 2 medium findings across 83 active workflows |
| **n8n container** (DB_TYPE=postgresdb, persisted encryption key) | Running |
| **External runner container** (custom image with pg) | Running; `pg.Client` resolves successfully |
| **External runner task timeout propagation** (2026-08-14) | Fixed. `N8N_RUNNERS_TASK_TIMEOUT=300` is now set on the runner container itself, not only the n8n broker. Sales Ingest verification execution `749605` completed in 104.7s and persisted 8,007 opportunities plus 8,007 history rows. |
| **GHL Sales Ingest daily schedule** (2026-08-14) | Fixed. Invalid `minutesInterval: 1440` was firing hourly because minute intervals only support 1-59. Published version `c1b5020c` now runs daily at 1:15 AM `America/Los_Angeles`, after the hourly Leads Ingest. |
| **Social reporting accuracy** (2026-08-17) | Executive Summary version `e4fa3d18` adds account-level reach/impressions/followers from the new daily statistics ingest (`veg9jbN1P67Xmqy8`, PIT-backed) and reworks `mqlSummary` into total MQLs / converted-to-SQL / current MQLs plus windowed movement. Social ingest version `2ed24c59` paginates the 366-day horizon and passed execution `759065`; report build `2026-08-17-v27-social-mql` passed desktop and 390px checks. |
| **Social statistics ingest live** (2026-08-17) | `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`, version `bee234fb`) runs daily 06:00 LA, calls `/social-media-posting/statistics` with the GHL PIT, and stores 7/30/90-day window totals in `report_ghl_social_statistics` in the report database. Execution `760249` stored 12 rows. |
| **LinkedIn DM pipeline repair** (2026-08-18) | Dispatcher `f2f52041`, DM Sequence `bc79f0d1`, Reply Backfill `9e0131f4`, State Upsert `4045c96c`. Fixed dispatcher `\\/` regex + 60/day limit, DM send 422 (existing-chat routing), reply-backfill over-suppression, and the state-updater blocking `requested_pending -> requested`. DM sends now write a durable `dm_sent` event (dedup + reporting metric). 60 distinct invites verified today, zero duplicates; DM queue 66. |
| **LinkedIn send-path double-escape corruption** (2026-08-19) | A 2026-08-11 MCP mutation (version `3b70854e`) double-escaped regex literals in the Code nodes. Two distinct failures resulted. (1) The Dispatcher **crashed at parse time** (`SyntaxError: Invalid regular expression flags` on the `identifier()` `\\/` regex), so it sent **no invites at all** from 08-11 to 08-18. (2) After the 08-18 REST PUT fixed that crash, `sanitize()` char classes matched literal letters `u`/`C`/`D` + digits instead of smart quotes (`u`→`'`, `C`→`"`, producing `"ameron co-fo'nder of Transparent e"om`) and `/\\{first_name\\}/gi` matched only literal `\{first_name\}`, leaving `{first_name}` unreplaced — so **garbled invites were sent only from 08-18 00:15 through 08-19 04:45**, bounded by the 60/day cap, not since 08-11. The 08-18 REST PUT inherited but did not touch these regexes. Fixed via `scripts/linkedin/fix_linkedin_sanitize_double_escape.py`: Dispatcher `fXxw5lanZcDmUrst` (sanitize 8 escapes + `{first_name}` + `[^\\s,]` URL class) → `0a349cdb-295f-45a5-978a-2f3e46022ace`; LinkedIn DM Sequence `d0tEtijajisIsYcs` (`{first_name}` in Sync Connected from Unipile + Send DM Sequence Messages) → `db7dde63-2f6e-42e8-92f0-7f68c66e7445`; both published + active. Full-instance scan of all 164 workflows confirmed no other Code nodes affected. Same failure class as the 2026-07-15 mojibake fix. Full narrative: `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`. |
| **Emerald release-log single-row bug + Apollo August batch enrollment** (2026-08-20) | `LT - Emerald Campaign Sender Release Dispatcher` (`8UXlpoMJnQ229AuG`) `Write Release Log` node used `mode: runOnceForAllItems` with `$json`, so only **1 release-log row persisted per run** even when 60–132 were queued — the other queued contacts stayed pending+unlogged and were re-selected on the next hour (re-tagging risk). Fixed by iterating `$input.all()` in `Build SQL - Write Release Log` and setting `queryBatching: "independently"` on the Postgres node; published version `d6737e68-b2b1-4163-bd99-19d0176640c2`. Separately enrolled 73 clean `apollo_august2026` imports (of 86) into `Emerald_Campaign_Contacts` with `bucket=executives_mso` (dispatcher run `769889`, all queued + GHL enrollment confirmed via `seq emerald - executives mso`/`seq enrolled - emerald`); 12 were already Emerald-enrolled and 1 DAN-only (skipped). Marked the 73 released + release-logged, then backfilled release-log + released status for the 58 prior-run contacts the bug had left unlogged so no re-dispatch occurs. Postgres campaign tables live in the `postgres` default DB (container `postgres-uokgs4c04ko0s4scccg40cgg`), not `n8n`. |
| **Same release-log single-row bug fixed in DAN + Partnership dispatchers** (2026-08-20) | Audit found `LT - DAN Campaign Sender Release Dispatcher` (`toUG1yPDmFG48KEP`) and `LT - Partnership Email Dispatcher` (`Xshck23cKo1yXL9D`) had the identical `mode: runOnceForAllItems` + `$json` bug in their `Build SQL - Write Release Log` nodes. **Partnership was actively manifesting**: run `766371` (2026-08-19) sent 3 step-4 emails but logged only 1 (robert@herb.co), leaving the other 2 contacts unlogged for their step → duplicate re-send risk. DAN was dormant (pool exhausted, no log entries since 07-22). Fixed both with the same `$input.all()` iteration + `queryBatching: "independently"` on the Postgres node. Published: Partnership `2663f32b-4e45-4a5c-9b7f-e9db58ff9bc4`, DAN `f8f29288-45d9-4f35-81a6-a60d2b54ad11` (both `versionId == activeVersionId`). Functional test (`test_workflow` execution `769961`) confirmed 3 sent items → 3 release-log writes; the 3 test rows written to the live `partnership_release_log` were deleted afterward (total restored to 188). |
| **August 2026 Emerald contact enrollment reconciled** (2026-08-26) | Reconciled 2,620 cleaned Brand/Agency/Dispensary rows against live GHL. The bounded reconciliation created 36 genuinely new email-only contacts and completed 319 contact-level repair groups representing 325 tag assignments: 313 Emerald MSO queue enrollments plus six Dispensary pool and six DAN queue assignments. Final dry run returned 0 unmatched rows and 0 pending tag actions. Five AURI emails were identified as additional emails on existing contact `Amy Lund` and intentionally skipped; `scripts/emerald/reconcile_august_2026_emerald_live.ps1` now prevents retrying them. Details: `docs/sessions/2026-08-26-august-emerald-contact-enrollment.md`. |
| **August 2026 partnership contact enrollment** (2026-08-27) | Reconciled the August 26 partnership CSVs as 431 people / 429 unique emails. Created 404 new GHL contacts and enrolled 427 actionable contacts with both `partner_candidate_email` and `partner_candidate_linkedin`; added `august_26_partnership_contact` to the 404 new contacts. Three existing contacts received missing LinkedIn URLs. Four rows across two shared-email groups were skipped for manual resolution. No Vapi selector tags were applied. Details: `docs/sessions/2026-08-27-august-partnership-contact-enrollment.md`. |

### Resolution

The runner now uses an isolated npm-installed `pg@8.21.0` tree at `/opt/pg-node_modules`. `NODE_PATH` is configured in both the container environment and `n8n-task-runners.json`; the runner is rebuilt by `scripts/deploy/deploy_runner.py`. Direct runner verification returns `typeof require('pg').Client === 'function'`. The n8n container must use the persisted Coolify encryption key, not the earlier local/reference key. The live container was recreated with the persisted key and credential decryption errors stopped.

### Executive Report Recovery: 2026-08-12

- The report host and n8n are attached to `coolify-shared`; n8n has the network alias `n8n`.
- `reports/nginx.conf` proxies the Executive Summary, campaign-channel summary, and outgoing-call endpoints directly to `http://n8n:5678`.
- `https://reports.livetransparent.com/api/report/executive/summary?range=30d` now returns HTTP 200 with a real approximately 33 KB JSON payload.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy` resolves raw pipeline/stage IDs, uses exact completed-day ranges, exposes LinkedIn and Instagram ledger metrics, labels Social Planner rows as platform placements, and renders unavailable account statistics as N/A. Desktop and 390px mobile verification found no raw IDs or page-level horizontal overflow.
- The empty-body/zero-metric symptom was caused by the reports proxy reaching n8n while report workflow Postgres credentials failed to decrypt. The running container used `WJR...`; Coolify's persisted service `.env` used `ffff...`. The container was recreated from the persisted value.
- Do not rotate or replace `N8N_ENCRYPTION_KEY` casually. A mismatch makes existing n8n credentials unreadable. Back up the service `.env` before changing it.

### Current Runner Caveat

- Some older n8n logs contain `Module .../pg@8.21.0... is disallowed`. The effective config uses `NODE_FUNCTION_ALLOW_EXTERNAL=*`, and the real affected Code-node path succeeded in GHL Leads Ingest execution `742843`. Treat new warnings as actionable only when tied to a reproducible failing workflow.

### Remaining Follow-up

1. **High**: 1,229 unmatched `ghl_contact_id` rows in `emerging_pool_contacts` — contacts not in GHL export CSVs. Decide: skip, manual GHL lookup, or re-export with broader filter.
2. **High**: migrate embedded secrets to Config nodes (Community Edition cannot use env vars in Code nodes). Priority: GHL PIT (8+ workflows) → Unipile (5+ workflows) → Vapi (2 workflows) → Postgres credentials → webhook secrets. Then rotate exposed values.
3. **High**: recover campaign/reporting state deliberately — `Email_Events`, release logs, LinkedIn state, and SimpleTexting state will populate through live workflow activity. Do NOT fabricate historical data. **Progress 2026-08-20**: Emerald/DAN/Partnership release logs are flowing again after the release-log write fix; 73 `apollo_august2026` contacts were enrolled into Emerald Executives MSO.
4. **Medium**: Warm intake authentication review — `5nYzp9DgQUopzWhR`, `OowP3sAd8c9paSKf`, and `SmMf8QIfysuxQJbG` have empty shared-secret configuration. SimpleTexting send/callback boundaries were hardened on 2026-08-17.
5. **Medium**: add OAuth-backed social statistics for reach/impressions/saves; complete native GHL report UI widgets.
6. **Low**: monitor migrated voice dialer next scheduled execution; clean legacy artifacts after live paths are stable.

### Known Issues Still Unresolved

- **`report_raw_ghl_contacts`** verified (500 rows); **`report_raw_ghl_opportunities`** verified (7,984 rows via execution `743094`)
- **Live post-recovery baseline**: `report_raw_ghl_contacts=500`, `report_raw_ghl_opportunities=7984`, `voice_call_queue=3` pending, `voice_call_attempt=0`, `report_raw_ghl_call_outcomes=0`, `Email_Events=0`, DAN/Emerald/partnership release logs `=0`, main LinkedIn state `=0`, partnership LinkedIn state `=18`, SimpleTexting campaign state/events `=0`. **Updated 2026-08-20**: `Emerald_Release_Log=16,154` (incl. 73 `apollo_august2026` executives_mso + 58 backfilled), `partnership_release_log=188`, `DAN_Release_Log=4,664` (dormant since 07-22)
- **`emerging_pool_contacts.ghl_contact_id`** needs audited backfill (`12,639/13,868` currently populated; 1,229 null — not in GHL exports)
- **Call Outcome Ingest** now requires `X-LT-Call-Outcome-Secret` header (secret in Config node of `PUCfTZBANSPcgS0c`)
- **Call Outcome caller auth fix (2026-08-13)**: GHL automation `LT - Call Outcome to Report` (`2152ba2b-0b9d-4645-aba4-44cc818a1789`) was sending Call Details webhooks to `https://automations.livetransparent.com/webhook/lt-call-outcome-ingest` without the required header. Its Webhook action now includes `X-LT-Call-Outcome-Secret` with the value stored in the n8n Config node, was saved, and was confirmed published in the GHL advanced canvas. Do not weaken the n8n validation or expose the secret in documentation. No live Vapi call was placed during verification.
- **Warm intake boundaries** still need authentication review; SimpleTexting send and provider callback boundaries are protected

### Key Files

- Runner Dockerfile: `n8n/runners/Dockerfile`
- Runner config: `n8n/runners/n8n-task-runners.json`
- n8n docker-compose: `n8n/docker-compose.yml`
- VPS scripts: `scripts/utilities/vapi_audit.py`

## IMPORTANT — Read This First

Analyze the attached `repomix-output.md` file. It contains the core system architecture, code blueprints, and operational roadmaps for my LiveTransparent automation environment. Review custom script setups (like `fix_intake_poller.js`) to understand how my infrastructure is organized.

**LLM context-loading order:**
1. `repomix-output.md` — start here for architecture, blueprints, and roadmaps
2. `AGENTS.md` (this file) — short operating guide
3. `Project Status and Next Steps.md` — current priorities and live-state
4. `Project Specifications.md` — system boundaries, guardrails, contracts
5. `plan.md` + sub-plans — active work plan
6. Custom scripts — infrastructure specifics
7. All other repo files — only when a task requires fine detail

> **Source of Truth**: Live n8n (via `n8n-lt` MCP) is the single source of truth for all workflow state. Repo files (`.ts`, `.json`, `Backup of all n8n workflows/`) may be outdated snapshots. Always `get_workflow_details` or `search_workflows` to read current state before editing.

> **Historical traceability**: Detailed fix narratives, root-cause analyses, and execution histories from 2026-06 onward are preserved in git history. This file contains only the current operating guide and critical patterns.

## Canonical Status

- Use [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md) for current priorities and live-state details.
- For the 2026-08-12 report recovery and session continuation order, read [docs/handoff/2026-08-12-report-recovery.md](./docs/handoff/2026-08-12-report-recovery.md).
- For the 2026-08-14 company Instagram-page DM implementation, read [docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md](./docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md).
- For the 2026-08-19 LinkedIn double-escape corruption fix (timeline, root cause, published versions), read [docs/sessions/2026-08-19-linkedin-double-escape-fix.md](./docs/sessions/2026-08-19-linkedin-double-escape-fix.md).
- This file is the short operating guide: keep it current, but avoid duplicating long planning material here.

### Documentation Review Session (2026-08-12)

Full cross-file review of AGENTS.md, plan.md, Project Status and Next Steps.md, and docs/handoff/2026-08-12-report-recovery.md. Fixed 18 issues across 4 files:

**Security (CRITICAL)**: Redacted 3 exposed secrets — Apollo webhook key, Apollo API key, and Call Outcome secret — from AGENTS.md, Project Status.md, and handoff document. All replaced with `<see .env>` or `stored in Config node` placeholders.

**Stale data (HIGH)**: Updated `ghl_contact_id` from `0/13,868` to `13,755/13,868` across 4 files (AGENTS.md, plan.md, Project Status.md, handoff). Updated plan.md Data Pipeline Status to reflect post-recovery baseline (opportunities=7,984, pipeline_history=7,984, voice_call_queue=3). Marked Sales Ingest repair and Call Outcome auth as DONE in plan.md Follow-up and Next Agent sections. Fixed plan.md Current blockers to remove stale Sales Ingest HTTP 401 reference.

**Contradictions (HIGH)**: Fixed SimpleTexting Step Runner/Phone Backfill/Warmup/Pool Dispatcher status in AGENTS.md from "active and published" to "passed smoke executions but remain unpublished" (matches Project Status.md). Fixed DAN dispatcher candidateLimit from 65 to 85 in Project Status.md (matches AGENTS.md 2026-07-21 change). Fixed Partnership dispatchers from "dry-run" to "Active" in AGENTS.md (outbound activated 2026-07-31). Fixed Partnership header from "Outbound Dry-Run" to "Outbound Live".

**Consistency (MEDIUM)**: Fixed Reply Backfill version ID `462e`→`4620` in AGENTS.md (matching canonical Project Status.md). Fixed plan.md implementation order indentation. Strengthened Emerald HTTP wrapper warning from "should" to "must" migrate.

**Next session**: `repomix-output.md` was regenerated via `packlive` at end of this session. It now reflects all fixes above.

## Environment

- Deployed via Coolify on a VPS.
- Public hosts: `automations.livetransparent.com` for n8n and `reports.livetransparent.com` for the report host.
- Prefer Coolify internal service-to-service calls when possible.
- n8n target version: `2.33.3` (native Schedule Trigger is the scheduling standard; do not add OS/Coolify cron jobs for workflows).
- Canonical MCP: `n8n-lt`.
- Root `.env` is the reference copy; Coolify env vars are the deployed source of truth.

### Business Timezone vs Operator Timezone

- The operator may access GHL from Manila (`Asia/Manila`), but LiveTransparent business operations are pinned to `America/Los_Angeles`.
- Interpret Cameron's calendar availability, GHL appointment dates/times, reminders, campaign schedules, report windows, and business-hours guards in `America/Los_Angeles` unless a task explicitly requests another timezone.
- Never treat a Manila-rendered GHL UI timestamp as the business-local timestamp without converting it to `America/Los_Angeles` and checking the underlying timezone metadata.
- Booking pages and confirmation copy must display or clearly state Pacific Time; a widget defaulting to Manila is a configuration/UX issue, not evidence that the business operates on Manila time.

### n8n Community Edition Constraint

**n8n Community Edition does NOT support environment variables inside Code nodes or workflow expressions.** The `N8N_BLOCK_ENV_ACCESS_IN_NODE` setting blocks `$env.*` access in Code nodes. This is a hard platform limitation, not a configuration choice.

**Canonical pattern for workflow-scoped configuration:**
- Each workflow that needs API keys, secrets, or configuration values uses exactly one **Set node named `Config`** (type `n8n-nodes-base.set`, version 3.4).
- The Config node stores all workflow-scoped values as named assignments (e.g., `ghlApiKey`, `unipileApiKey`, `stateUpsertSecret`, `vapiApiKey`, `pgPassword`).
- Code nodes read these values via `$node['Config'].json.ghlApiKey` (or `$('Config').item.json.ghlApiKey`).
- HTTP Request nodes reference them via `={{ $node['Config'].json.ghlApiKey }}` in header/body expressions.
- Config nodes are **operational storage**, not equivalent to managed n8n credentials. They store secrets in plaintext in the workflow definition. Keep access restricted.

**What Config nodes replace:**
- `$env.GHL_API_KEY` → `Config.ghlApiKey`
- `$env.VAPI_API_KEY` → `Config.vapiApiKey`
- `$env.UNIPILE_API_KEY` → `Config.unipileApiKey`
- `$env.POSTGRES_PASSWORD` → `Config.pgPassword`
- Hardcoded API key literals in Code node jsCode → Config assignment

**What remains as managed credentials (preferred when available):**
- n8n `httpHeaderAuth` credentials for webhook authentication
- n8n `postgres` credentials (when the Postgres v2 node bug is resolved)
- n8n OAuth2 credentials (when implemented)

**Migration priority for embedded secrets:**
1. GHL PIT token → Config node in each of 8+ workflows (already done in some; complete the rest)
2. Vapi API key → Config node in dialer and callback workflows
3. Unipile API key → Config node in all LinkedIn/Instagram workflows
4. Postgres credentials → Config node in direct-`pg` Code nodes (already done in some)
5. Webhook secrets → Config node (already done for state-upsert, call-outcome, voice-queue)
6. GHL OAuth client credentials → migrate to n8n OAuth2 credential when available

### Reporting Execution Contract (2026-07-31)

- The spreadsheet at `1AbLdIhQiEoJhdx3l6yeAppNxbYbAIYhcZfoKhy68VZw` is the requirements reference for the MQL, email, LinkedIn, and social report layout.
- Native GHL Custom Report: `6a67dce4a51a4360c60963a3`. Use it for CRM contacts/opportunities, MQL detail, pipeline, email, SMS, calls, appointments, and custom-metric rates.
- Native GHL Social Planner is the source for Facebook, Instagram, and LinkedIn Page post analytics. LinkedIn personal-profile analytics are not supported by the platform API.
- Keep Brands-versus-Dispensaries joins, Unipile LinkedIn DM state, Vapi campaign state, trigger-link detail, and cross-channel comparison in the Executive Report unless the underlying data is intentionally synchronized into GHL objects.
- The Executive Report accepts `range=7d|30d|90d|custom` plus `from=YYYY-MM-DD` and `to=YYYY-MM-DD`. For every selected period it loads the immediately preceding equal-length period and shows current value, prior value, absolute change, and percentage change.
- Reporting weeks use the report API's returned date window and the sub-account reporting timezone. Do not mix widget-level date overrides with the shared selected-period comparison unless the metric definition explicitly requires it.
- Campaign summary workflow: `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) is active and published. Its selected-window endpoint is `/webhook/lt-report-campaign-channel-summary`.
- Campaign summary active version `d65e2845-660a-40ca-88f4-d39445b87403` returns named channel/campaign rows plus `linkedin_invites`/`linkedin_accepted` columns. DAN uses release-log campaign fields, Emerald uses bucket/enrollment data, SMS uses `SimpleTexting_Campaign_Event_Log.campaign_key`, LinkedIn uses `linkedin_activity_events` joined to `emerging_pool_contacts.source_list` with `campaign_type`/`source_key = 'partnership'` routing, and Vapi uses queue campaign IDs. The response-shaping node now derives separate `DAN`, `Emerald`, `Partnership`, `Vapi Brand`, and `Vapi Dispensary` aggregates from channel rows, so Vapi is no longer incorrectly rolled into DAN.
- The Executive Report is live at `https://reports.livetransparent.com` as build `2026-08-17-v26-social-reporting-accuracy`; it includes campaign/channel filters, separate Vapi filters, campaign drill-downs, comparison view, campaign opportunity counts, LinkedIn and Instagram activity columns, selected-period controls, prior-period comparison, resolved GHL stage names, responsive table containment, and explicit post-ledger versus account-statistics coverage.
- The Executive Report also includes a bottom `Outgoing Call Detail` table. It calls `/api/report/executive/outgoing-calls`, which nginx proxies to `GET /webhook/lt-report-outgoing-calls` from active workflow `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`). The endpoint is fixed to the seven most recent completed `America/Los_Angeles` days, paginates at 100 rows, and reads `voice_call_attempt` joined to `voice_call_queue`.
- Partnership LinkedIn reply recovery (2026-08-12): Campaign Channels now reports 3 verified Partnership replies. Jaret Christopher was already present; David Schachter (`rvWEW2K2WYeQ7v6zypDdZQ`, 2026-08-10) and Gretchen Gailey (`8UF3lxibUmKYaG87h1F5Pg`, 2026-08-06) were recovered from the Unipile API with their original timestamps and inserted idempotently into `linkedin_activity_events`. `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) is published on `f96dafba-9818-4aab-8656-c2e4e2ab8480` with a malformed form-payload fallback so unescaped Unipile JSON no longer loses critical inbound fields. **2026-09-10/11 fixes (E2E verified)**: (1) Endpoint corrected from `/conversations/messages` to `/conversations/messages/inbound` (the `/inbound` suffix is required for posting inbound messages). (2) `resolveWithFullResponse` is silently ignored by `this.helpers.httpRequest` — use `returnFullResponse: true` (returns `{body, headers, statusCode, statusMessage}`); the old option made every successful post read as `inbound_failed: status=undefined body={}`. (3) All `Build * SQL` Code nodes in that workflow must NOT double backslashes inside `'...'::jsonb` literals (`esc()` keeps only `'` → `''`; backslash doubling made any payload containing an embedded quote crash `Upsert LinkedIn Map` with "invalid input syntax for type json" and blocked `linkedin_conversation_map` persistence). **2026-09-25 revert:** The Sales Navigator exclusion (`if (payload.linkedin_feature === 'sales_navigator') return ...sales_navigator_recruiting_exclusion`) was added 2026-09-24 17:01 UTC and reverted 2026-09-25 18:30 UTC. The `normalizedFeature` classification was also removed from `Normalize Unipile Message Event`. All LinkedIn DMs including Sales Navigator are now accepted and contacts are created. Current published version `ec870256-8946-4ff6-be46-e55eab4710b7` (`versionId == activeVersionId`). Correct GHL API flow: POST `/oauth/locationToken` with `{companyId, locationId}` using `Authorization: Bearer <oauth access_token from Postgres ghl_oauth_tokens>` (the PIT returns 401/403 there) to get `access_token`, then use that as Bearer for `POST /conversations/messages/inbound` (inbound) or `POST /conversations/messages` (outbound mirroring) with body `{"type":"Custom","contactId":"<ghl_contact_id>","message":"<text>","conversationProviderId":"6a58a14ff3023bea3783c152","altId":"<chat_id>","date":"<ISO ts>"}`. Gretchen Gailey's two historical outbound messages were backfilled successfully via `/conversations/messages` (the nonexistent `/conversations/messages/outbound` direction path caused the original 422s); the inactive `LT - LinkedIn Conversation Backfill` (`JUvrA7qMa24SwAZG`) now has conversation-message dedup and a Config `only_chat_id` (currently Gretchen's chat `8NOmhtWSUpKbsec3YdsxlA` — clear before broader backfill). Local python scripts calling GHL need a browser `User-Agent` (Cloudflare 1010 blocks python-urllib).
- On 2026-08-08 the live reports container was missing the repository nginx proxy route for `/api/report/executive/outgoing-calls`; the route was copied into `reports-livetransparent`, `nginx -t` passed, nginx was reloaded, and the proxy now returns the healthy n8n endpoint response.
- Campaign summary active version `1cea3b9c-d587-4135-806d-46d301e2c7f4` now counts SimpleTexting `sent_step_1` through `sent_step_4` events and exposes a selected-window `smsSummary` with sent, `delivery_failed`, reply, and normalized failure-reason counts. The Executive Report displays this as the SMS delivery summary; the verified 2026-07-09 through 2026-08-07 window returned 294 sent, 1,095 failed, and 0 replies. Failure reasons were `simpletext_provider_failed` (1,010), `duplicate_send` (63), `unknown` (16), `invalid_phone` (5), and `idempotent_webhook_error` (1).
- **Newsletter reporting (2026-08-24)**: the Campaign Channel Summary (`MvPLbUAN9IIQikxb`, active `2b8608aa-86e3-466f-9347-2ceb6f0b6818`) returns a `Newsletter` campaign channel row (sent/opened/clicked from `newsletter_send_log` + `newsletter_events` mapped into the existing `email_*` columns, grouped as `Newsletter`). The Executive Summary (`Bukc0mgOD2r7V6ED`) folds newsletter sends into `emailsSent` and newsletter opened/clicked/unsubscribed into `emailsOpened`/`emailsClicked`/`emailsUnsubscribed`, and newsletter `failed` rows into a new top-level `newsletterFailed` metric. Because the reports window defaults to ending yesterday, newsletter data only appears when the window includes the send day. The dispatcher sets `sent_at` on `failed` rows too so the failure metric is window-able.
- The same campaign summary response now includes distinct selected-window opportunity counts matched from current contact campaign tags in `report_raw_ghl_opportunities`. The Executive Report displays these in campaign rows, detail cards, and comparison view. The verified window returned Emerald 3,909, Partnership 8, and Vapi Brand 13; DAN and Vapi Dispensary had zero matched opportunities.
- The root `GHL_PIT` was directly verified against the official REST location and contacts endpoints on 2026-07-31; both returned HTTP 200 with the required Bearer/Version headers. The native GHL report `6a67dce4a51a4360c60963a3` was also verified in an authenticated GHL UI session: it supports editing. Its `Campaign Opportunities` widget is filtered to `Partnership Pipeline`, its `Contacts by tag` widget uses `Tags -> Is one of` with `partner_candidate_email` and `partner_candidate_linkedin`, its saved date range is now `Last 30 days`, and the duplicate page-3 outgoing-call widget was removed.
- The official GHL API/SDK does not expose Custom Report widget-layout mutation. Do not guess undocumented report-builder endpoints; native widget changes require authenticated GHL UI access or an explicitly approved internal API path.
- **GHL Native Report Audit (2026-08-08)**: Report `6a67dce4a51a4360c60963a3` ("New LiveTransparent Reporting") was reviewed against live data. The authenticated report editor is now reachable at the documented URL; its saved date range was changed from `Last week` to `Last 30 days` on 2026-08-08. Findings:
  - **1 Partnership Pipeline opportunity exists** (Strider Peterson, created Aug 4, assigned to Janvi, stage "New Partner Lead"). It falls outside the "Last week" window — change to "Last 30 days" to include it.
  - **Duplicate widget**: "Outgoing calls by status" appeared identically on pages 2 and 3 (319 calls, same data). It was deleted from page 3 and saved on 2026-08-08.
  - **Missing pipeline widgets**: Stage Distribution on page 3 only shows Sales pipeline. Add separate Stage Distribution widgets for Sales Outreach (`dhdlf3O4tymxFtHk4aqq`) and Warm (`FRjpDZ1HWj3UPgczsu3t`) pipelines. The Partnership Pipeline widget already exists on page 1.
  - **Missing campaign tag widgets**: Only Partnership tags are widget-tracked. Add "Contacts counts by tags" widgets for DAN (`seq enrolled - dan`, `dan_seq_replied_or_booked`, `dan_seq_completed`), Emerald (`seq emerald`, `seq enrolled - emerald`), and Vapi (`vapi_campaign_brand`, `vapi_campaign_dispensary`) tags.
  - **Missing email widgets**: "Replied emails", "Soft bounced emails", and "Emails by domain" are available in GHL but not used. Add them to page 2.
  - **Pages untitled**: All 3 content pages are "Untitled page". Rename to: Page 1 "Pipeline Overview", Page 2 "Campaigns & Outreach", Page 3 "Communications Detail".
  - **Custom metrics unused**: GHL supports custom metrics (e.g., email open rate, campaign conversion rate). Create at least the open-rate and click-rate custom metrics for cross-filtering.
  - **GHL CANNOT do**: LinkedIn metrics, Vapi campaign outcomes, email attribution by source tag, cross-channel comparison, release-log data. These remain in the Executive Report only.
  - **Available widget counts per category**: Opportunities (17), Emails (11), SMS (5), Calls (13), Contacts (17), Social Planner (18), Appointments (15), Conversations (16), Payments (17), General (15).
- Never commit GHL PITs, Firebase signed URLs, OAuth tokens, or captured response artifacts containing credentials. Use environment placeholders in documentation and leave sensitive captures untracked.

### Ingest and LinkedIn Hardening (2026-07-31)

- `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) is published on `8f4c63ea-dd33-4c7f-93a5-b3cbb5c8e7fa`. Empty responses finalize as `empty`; malformed data is `partial`; fetch failures finalize run/health state, do not advance the watermark, and then fail the execution. Verification: success `276731`, pinned failure `276747`.
- `LT - GHL Daily Sales Ingest` (`aYT5oHcgmBALzHy5`) is published on `4f3e8068-8864-4b4d-9286-ba4d618cc3a8`. Snapshot/history rows use ingest date, raw rows preserve source timestamps, retries/cursor guards are bounded, finalization errors fail closed, and sales health uses `ghl_opportunities` while raw compatibility remains `source_system = 'ghl'`. Verification: execution `276626` processed 7,683 opportunities and 7,683 history rows.
- `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`) is published on `fa1a5dfe-d00c-47b3-98d3-862ea6f912a7`. It uses direct `this.helpers.httpRequest`, bounded contact/API budgets, retry/timeouts, explicit error reporting, and terminal/reply-state preservation.
- `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`) is published on `bd385c89-0678-4301-84e6-abc63fea3c28`. It reads Config explicitly, atomically claims `ready` rows as `requested_pending`, and performs live suppression/reply checks before invites. Do not manually execute it without explicit approval because it can send LinkedIn invites.
- `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`) is published on `d9168bbc-9c96-44fd-a356-12e645a2ec3d`; its webhook requires the protected `X-LT-LinkedIn-State-Secret` header. All discovered callers, including the partnership dispatcher/DM path, were updated and published. Unauthorized requests return `403`; malformed authorized requests reach the workflow and fail validation without a state write.
- Community Edition variable convention: each relevant LinkedIn state-upsert workflow has exactly one `Config` node. Workflow-scoped values such as `stateUpsertSecret` live there and Code nodes read them from Config instead of embedding request literals. Config nodes are operational storage, not equivalent to managed credentials; keep access restricted and migrate to credentialed HTTP Request nodes when possible.

## Working Rules

### Company Instagram Page Outreach (2026-08-18)

The company-page Instagram DM delivery pipeline is LIVE. The sender `LT - Instagram Company Page Partnership Sender` (`IeovbYnhCsetXS89`) is active and published (dryRun=false), Mon-Fri 10:00-15:00 America/Los_Angeles, 45/day cap, 10/hour. It reads `instagram_company_dm_state` and sends via Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`. Do not republish `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`): it used the LinkedIn account and old `instagram_dm_state` model.

**Send priority (2026-08-18):** `campaign_priority` in `instagram_company_dm_state` is `dan_brands`=1, `dan_dispensaries`=2, `partnerships`=3. Brands go first, then Dispensaries, then Partnerships. The 379 state rows are 245 Brands, 58 Dispensaries, 76 Partnerships.

**Message strategy:** Message 2 is now enabled in the live sender (published version `3d721cec-04e6-45cc-9ebb-fb21589b61a6`). It selects `message_step = 1`, waits two business days after Message 1, sends the approved campaign-specific Message 2 copy, and advances state/log idempotently to step 2. Message 3 remains disabled. Do not manually execute the live sender without explicit approval.

**Current state:** 45 Partnerships received Message 1 on 2026-08-17 (before the priority change). The remaining Partnerships and all Brands/Dispensaries are pending Message 1. Unipile key tested OK on 2026-08-18.

**IG/FB enrichment status:** `brand_pool - IG & FB` enrichment is COMPLETE (workflow `BIVAw1AWTTzC0igW` unpublished; last run found 0 unresolved). Dispensary (`Qd7sn9MPq4W24WKi`) and Partnership (`RlogFNDYjtjkuRFJ`) enrichment remain active on a 5-minute schedule; they were temporarily blocked by an OpenRouter weekly key limit that the user fixed on 2026-08-18.

**Contract (from 2026-08-14):** audience selectors `brands_pool`, `dispensaries_pool`, `partner_candidate_email`/`partner_candidate_linkedin`. Existing contact-level Instagram fields are protected; create separate company-level fields (`Company Instagram Username`, `Company Instagram Profile URL`, `Company Instagram Profile Provider ID`, `Company Instagram Chat Attendee ID`, `Company Instagram Chat ID`, `Company Facebook Page URL`, `Company Facebook Page ID`, `Company Facebook Messenger PSID`). Deduplicate by normalized company Instagram handle; retain associated GHL contact IDs plus a primary attribution contact in Postgres. Use direct `require('pg')` transactions for writes. Any prior reply/suppression from any associated contact stops the sequence; identity/reply-check errors fail closed. Cadence: Message 1 first eligible weekday, Messages 2-3 two business days apart, never weekends. No lifecycle tags. Full history in `docs/sessions/2026-08-14-company-instagram-page-dm-handoff.md` and `docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`. Do not manually execute live validation sends without explicit approval.

- Check the live state before and after every mutation.
- Fetch first, patch second.
- After every mutation via `update_workflow`, verify the workflow is both **updated AND published**: compare `versionId` vs `activeVersionId` from `get_workflow_details`. If they differ, call `publish_workflow` to activate the draft. The `update_workflow` MCP tool does NOT auto-publish.
- Preserve n8n graph integrity: keep node IDs and connection maps aligned.
- Use `Switch` over `IF` for voice automations.
- Prefer raw JSON import for dialer patches.
- Use `={{ ... }}` expressions with `$('Node').item.json.field`.
- Prefer runbooks in `GHL Live Transparent CRM/` before changing GHL/n8n workflows.
- Website demo bookings must use the direct GHL Regulated Ads booking widget. Do not route website visitors through the legacy hero form or Calendly embed first.
- Use `Config` nodes only when env or credential access is blocked.
- LinkedIn outbound senders must fail closed on reply/inbound lookup errors. A failed reply check is a skip, not a send.
- For any "stop LinkedIn DMs" request, suppress the contact in both places: add `linkedin_dm_sequence_completed` in GHL and mark the shared `linkedin_connection_state` row terminal (`connection_status = completed`, `sequence_step >= 4`, `dm_sequence_status = completed`/`dm_conversation_status = active` as applicable). The GHL tag alone is not enough because the live LinkedIn send paths select from shared state.
- LinkedIn DM sequences must mark terminal contacts with `linkedin_dm_sequence_completed` and stop reselecting step-4 rows; the queue source is `LT - LinkedIn Connection State Sync (Unipile)` and the GHL connect dispatcher feeds 20 contacts at a time when healthy.

### Follow-up Sender Routing Handoff (2026-07-29)

- User requirement: follow-up email From Name and From Email must follow the opportunity/contact owner; if neither has an owner, default to Jason.
- Affected GHL workflow: `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`), published version 39. Triggers on opportunity stage entry into Sales Outreach: New (`3529dd3d`), Attempting Contact 1st Attempt (`b97e42b1`), 2nd Attempt (`c46c3be3`), 3rd Attempt (`c8b7a450`), Engaged (`9ced8010`).
- Six affected templates are in folder `Jason Follow Up Emails` (`69e0c9069af5986541802d88`) and currently have literal Jason sender defaults. Do not mistake those defaults for the final owner-routing implementation. One template (`69e0dcad8ffabf47b4d987c5`, "Cannabis Ads: Next Steps") is reused by 2 of the 7 email actions. Template signatures use `{{user.email_signature}}` (dynamic).
- The workflow also sends 14 SMS follow-ups via SimpleTexting webhook using legacy compatibility aliases; these messages are not owner-routed.
- Current live artifact check: published version 39 has Jason workflow defaults (`Jason from Transparent eCom`, `jason@livetransparent.com`) confirmed via `senderAddress` in the API response. All 7 Send Email actions retain owner-driven sender fields: `{{opportunity.owner}} from Transparent eCom` and `{{user.email}}`. The three-layer defense is: (1) action-level merge fields resolve to owner, (2) template-level literal Jason values backstop if merge fields fail, (3) workflow-level `senderAddress` defaults backstop if both above fail.
- Remaining GHL work: none for sender routing. Do not send a live test email unless explicitly requested. **Marc routing path is untested in production** — as of 2026-07-30, zero Marc-owned (`sqGx5rp3oAUG610NXyjU`) opportunities exist in any of the 5 trigger stages; all Marc-owned opportunities are in the Qualified stage and have not yet entered a stage that fires this workflow.
- Public GHL APIs cannot write workflow action definitions. The template PATCH API rejects `{{user.email}}` as `fromEmail`; do not attempt to solve owner routing by putting merge fields into template sender metadata.
- Authenticated browser access was used to set and publish the workflow defaults. The published version 39 response confirms `senderAddress` and `status: published`.

### LinkedIn DM Suppression — Production Automation

**Primary path (GHL UI)**: Adding the tag `stop_linkedin_dms` to any contact in GHL triggers the automated suppression pipeline. No code access needed.

```
GHL tag "stop_linkedin_dms" added
  → GHL automation "WL - Stop LinkedIn DMs" fires
    → POST https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms
      → n8n workflow: LT - LinkedIn DM Suppression from GHL Tag (IPN8jnR3XSurX0o1)
        1. Scans webhook body for LinkedIn URL (any key containing "linkedin", nested customData, customFields)
        2. Falls back to GET /contacts/{id} if no URL in webhook
        3. Falls back to Unipile name search as last resort
        4. Adds linkedin_dm_sequence_completed tag via GHL API
        5. Upserts linkedin_connection_state (completed, step=4) for real contact
        6. Upserts linkedin_connection_state (completed, step=4) for synthetic linkedin:follower:{providerId}
```

**GHL automation setup:**
| Setting | Value |
|---------|-------|
| Name | WL - Stop LinkedIn DMs |
| Trigger | Tag Added → `stop_linkedin_dms` |
| Action | Webhook POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` |
| Custom Body | `{"contact_id":"{{contact.id}}","first_name":"{{contact.firstName}}","last_name":"{{contact.lastName}}","linkedin_url":"{{contact.customField.apollo_person_linkedin_url}}"}` |

**Suppression verified across all 3 LinkedIn send paths (2026-07-15 audit):**
| Send Path | How it's blocked |
|-----------|-----------------|
| DM Sequence (d0tEtijajisIsYcs) | SQL `WHERE connection_status = 'connected'` + `dm_conversation_status <> 'active'` |
| Follower DM (pq7XVajNFnnwMUTr) | Code `sequence_step >= 1` + `dm_conversation_status === 'active'` |
| Dispatcher (fXxw5lanZcDmUrst) | SQL `WHERE connection_status = 'ready'` + GHL tag block `linkedin_dm_sequence_completed` |

### LinkedIn DM Suppression Runbook (Manual/CLI)

When the user asks to stop DMs for a contact, preferred path is the GHL tag above. If CLI is needed:

```bash
python local-scripts/suppress_linkedin_dms.py "<name or LinkedIn URL>"
```

This single command handles everything:
1. Resolves the LinkedIn profile via Unipile (by URL or name search)
2. Finds the GHL contact if one exists
3. Adds `linkedin_dm_sequence_completed` tag in GHL (when a GHL contact is found)
4. Upserts `linkedin_connection_state` rows (both real GHL contact ID and synthetic `linkedin:follower:{providerId}`) to terminal:
   - `connection_status` = `completed`
   - `sequence_step` = 4
   - `dm_sequence_status` = `completed`, `dm_conversation_status` = `active`

If the script isn't available, POST directly to the suppression webhook or state upsert webhook:

**Path A — Suppression webhook** (does everything — tag + state table):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-suppress-dms` with `{"contact_id":"...","first_name":"...","last_name":"..."}`

**Path B — State table only** (tag separately via GHL UI):
POST to `https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert`:
```json
{
  "ghl_contact_id": "<contact_id>",
  "location_id": "Zwz4relUXVPxx8uohnjV",
  "unipile_account_id": "V9eiHiDpRmCtan0YNdzsQw",
  "linkedin_profile_url": "https://www.linkedin.com/in/<identifier>/",
  "linkedin_public_identifier": "<identifier>",
  "linkedin_provider_id": "<provider_id>",
  "connection_status": "completed",
  "sequence_step": 4,
  "source_workflow_name": "manual_suppression",
  "source_key": "manual:suppress:<identifier>",
  "payload_json": {
    "dm_sequence_status": "completed",
    "dm_conversation_status": "active"
  },
  "metadata_json": {
    "source": "manual_suppression",
    "reason": "user_requested_stop_DMs"
  }
}
```
4. Also upsert with `ghl_contact_id` = `linkedin:follower:<provider_id>` if the real GHL contact wasn't found (covers the Follower DM path).

## Tooling

- Prefer `n8n-lt` MCP or direct API calls before browser workflows.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.
- Codex config: `C:\Users\edmon\.codex\config.toml`.
- **Avoid `n8n-lt` `updateNodeParameters` for Set v3.4 nodes.** It silently corrupts `assignments.assignments` from `[{...}]` to `{item: [{...}]}` and stringifies booleans / `options`. Use `setNodeParameter` for single-path edits on Set v3.4 nodes. If that also fails, use direct n8n REST `PUT /api/v1/workflows/{id}` with `N8N_API_KEY_LT` from `.env` (note: PUT auto-publishes and validates all node credentials). For Code nodes, both `updateNodeParameters` and `setNodeParameter` are safe. Known-good Config shape: `{"mode": "manual", "assignments": {"assignments": [{id, name, value}, ...]}}` — no `includeOtherFields` or `options` keys required.
- **`setNodeParameter` silent failure (observed 2026-07-06):** On Code nodes and HTTP Request nodes, `setNodeParameter` may report success without modifying parameters. **Use `updateNodeParameters` with `replace: true`** as the primary mutation method for both. Always verify with a fresh `GET` after mutation.
- n8n Code nodes cannot access managed credentials by design. Do not attempt `$getCredentials()` or `this.getCredentials()` in Code nodes. Credential migration for direct API calls requires credentialed HTTP Request nodes, or an explicitly approved protected runtime-variable path.
- **Historical n8n 2.28.6 MCP schema bug (upstream #33056):** `search_workflows`, `search_projects`, and `get_workflow_details` returned fields that violated the MCP output schema. The deployment target is now n8n `2.33.3`; retain the REST workaround if the MCP schema issue recurs:
  ```bash
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows?active=true&limit=100"
  curl.exe -s -H "X-N8N-API-KEY: $env:N8N_API_KEY_LT" "https://automations.livetransparent.com/api/v1/workflows/{workflowId}"
  ```
  MCP tools for **execution, editing, and node operations** are unaffected.

## Code Node HTTP Requests

- **Use `this.helpers.httpRequest({...})` directly** — do NOT wrap in an async helper function called with `.call(this, ...)`. The wrapper pattern causes HTTP 400 errors in task-runner loops.
- **`$httpRequest`** works for single calls but may fail in pagination loops.
- **`json: true`** works but must be paired with explicit `'Content-Type': 'application/json'` header.
- For paginated GHL search API calls, use `page` (1-indexed) + `pageLimit` (max 100). Do NOT use `startAfter`/`startAfterId`.
- Do NOT include empty `filters: []` in GHL search body — omit entirely.
- Add `await new Promise(r => setTimeout(r, delayMs))` between pages to avoid rate limiting.

## GHL REST API

- **Authenticated GHL Builder entry:** begin at `https://app.gohighlevel.com/v2/location/Zwz4relUXVPxx8uohnjV/launchpad` (or switch into the Live Transparent location as the second step from Agency Dashboard) before opening Automation/workflows. Wait for the authenticated location shell and cross-origin workflow iframe to load; the outer route may show HTTP 404 while the shell/sidebar or iframe is usable. Inspect the live UI/iframe before treating the status code as an access failure. Avoid opening a deep workflow URL first in a new browser session.
- **API base URL**: `https://services.leadconnectorhq.com` — NOT `rest.gohighlevel.com`.
- **Auth header**: `Authorization: Bearer <GHL_PIT_FROM_ENV>` (PIT token from root `.env`). The `token:` header style does NOT work.
- **Required header**: `Version: 2021-07-28` on every request.
- **Accept/Content-Type**: Always include `Accept: application/json` and `Content-Type: application/json`.

### Email Template Operations

**Listing templates**: Use `ghl_official_emails_fetch-template` MCP tool (OAuth). Pass `query_parentId` for folder-scoped listing, `query_limit` (max 50), `query_offset`.

**Reading template content**: Each template has a `previewUrl` pointing to Firebase Storage. Use `webfetch` with `format: "html"`. No working GET endpoint exists.

**Updating a template** (PATCH):
```bash
curl.exe -s -X PATCH "https://services.leadconnectorhq.com/emails/builder/{templateId}" \
  -H "Authorization: Bearer $env:GHL_PIT" \
  -H "Version: 2021-07-28" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"locationId":"Zwz4relUXVPxx8uohnjV","editorType":"html","editorContent":"<html>...</html>"}'
```
- Uses `editorType` + `editorContent`, NOT `rawHTML`/`html`/`type` fields.
- `locationId` is required in body.
- On success, verify new `lastUpdated` timestamp and `previewUrl`.
- **Backup before editing**: `webfetch` current HTML first.
- **Watch for `&#8211;` entities**: GHL normalizes en-dashes to `&#8211;`. Preserve exactly.

## n8n REST API Note

When using direct n8n REST `PUT /api/v1/workflows/{id}`:
- Required fields: `name`, `nodes`, `connections`, `settings`
- Settings must NOT include `availableInMCP` (remove before PUT)
- `versionId` and `tags` are read-only — exclude from body
- `Content-Type: application/json` header is required
- If settings get rejected as "additional properties", strip to: `executionOrder`, `timezone`, `saveDataErrorExecution`, `saveDataSuccessExecution`, `saveManualExecutions`, `saveExecutionProgress`, `executionTimeout`, `callerPolicy`
- Use `curl.exe` with JSON file for large payloads (PowerShell `ConvertTo-Json` can corrupt nested objects with `#` chars)

## Live Voice System

| Item | Value |
|------|-------|
| Phone | +1 (562) 534 1977 (bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4) |
| Callback webhook | https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback |
| Key env | VAPI_PHONE_NUMBER_ID, GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV, GHL_API_KEY / GHL_PIT |

### Voice Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Campaign Contact Classifier | IduCoT5YOs0g2faT | Active (native Schedule Trigger every 15 min; 10 Brand + 10 Dispensary candidates/run) |
| LT - Vapi Campaign Queue Feeder | RFIZ9Bcfl3Yvms2b | Inactive helper |
| LT - Emerging Pool Go Live Helper | OGnADUQKd5z5f905 | Manual helper |
| LT - Voice Agent V1 Vapi Callback + Tools | fx4UvKUWbqJEY3LK | Active |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | r7UjWLndmc6EqEUW | Active (native Schedule Trigger every 2 minutes; business-hours guard) |
| LT - Voice Queue Vapi Intake Poller | bYk1Ai6MJLyhTsDZ | Active (polls every 10 min, 30 contacts/cycle, tag rotation) |
| LT - Voice Queue Enqueue | XzcpOBi9YcIhJPck | Active |
| LT - Voice Dequeue Next | KsBMFcz1YpBGrjDW | **Unpublished** (explicit helper only; not an automatic call-start path) |
| LT - Call Outcome Ingest | PUCfTZBANSPcgS0c | Active |
| LT - Apollo Queued Timeout Reaper | RL5ZyUoshSPbmVA1 | Active (hourly, reports to #reaper) |
| LT - Voice Campaign Brand (Alex) | 1d7c5d42-f0a4-4b58-9494-dbda3be3c657 | Active (optimized 2026-07-20) |
| LT - Voice Campaign Dispensary (Jordan) | 056f2e50-8bdf-4257-ac45-4d575600c39d | Active (optimized 2026-07-20) |

### Campaign Contact Classifier Audit (2026-07-29)

- `LT - Campaign Contact Classifier` is production-active, not manual-only. It runs every 15 minutes and selects up to 10 Brand and 10 Dispensary candidates per execution.
- It reads `emerging_pool_contacts`, performs live GHL contact and suppression checks, and applies campaign tags only after DeepSeek acceptance or a prior qualified-domain match.
- Qualified domains are persisted in `vapi_qualified_domains`. Common free-email domains are excluded, and a domain is written only after a successful GHL tag-add response.
- DeepSeek uses a 600-token output budget with concise English reasoning. The SQL candidate filter accepts a live GHL phone fallback when the imported pool phone is blank.
- Manual execution `268658` and scheduled execution `268659` passed after the audit patch with zero failed writes. The patch fixed model-output truncation, live-phone eligibility exclusion, and unsafe domain persistence on cleanup/failed writes.

### Campaign Contact Classifier — fetch diagnostics + 429 retry (2026-08-07)

- `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) `Process Warm MQL Contacts` Code node the per-contact `GET /contacts/{id}` loop failed opaquely. Two changes were made and each was deployed via direct n8n REST `PUT /api/v1/workflows/{id}` (publishing automatically; `versionId === activeVersionId` after each).
- **Fetch diagnostics**: the `fetch_error` catch now emits `error` (message, truncated to 300 chars) and `status_code` alongside `contact_id`/`status`, so every failure is self-diagnosing in execution output.
- **Bounded 429 retry**: a new `fetchContact(contactId)` helper (with a shared `SLEEP(ms)` helper) wraps the contact fetch and retries on `status_code === 429` up to 3 attempts with linear backoff (1s, 2s). Non-429 errors and a persistent 429 after the 3rd attempt rethrow into the catch as `fetch_error`.
- **Deployment**: first change published as version `85bcae4f-ce87-428c-be45-f82450bee12`; second (479) as version `adcc6622-2e7e-4519-8acf-ba6a628dc8d9`. Both active/published with matching `versionId`/`activeVersionId`; the 15-minute schedout Trigger remains intact.
- **Verification run `723561` (00:45)**: the first run on the diagnostics change classified 79 contacts (0 empty), all 12 failures clearly reported `error: "Request failed with status code 429"` and `status_code: 429` — identifying GHL per-window rate limiting as the cause rather than dead contacts or auth. The scheduler is healthy (confirmed by concurrent runs of other scheduled workflows); no runs are missed (local-clock misreading was ruled out).
- Deployment via PUT is made while the workflow is active; any single missed-tick from a publish repo is self-healed by the next 15-minute run.

**Tag rotation** (one tag per 10-min cycle, cycles every 40 min):
1. `vapi_campaign_brand` (926)
2. `vapi_campaign_dispensary` (19)
3. `brands_pool` (3,024)
4. `dispensaries_pool` (7,953)

**Fixes applied 2026-07-14:**
- `Trigger Apollo Enrichment` auth: changed `predefinedCredentialType` → `none` (was crashing because API key is passed in headers)
- `Remove Tag - Enriching` URL: changed `$json.contact_id` → `$json.contact.id` (Apollo response nests ID)
- Added full pagination loop with 250ms delays and 30-contact cap to avoid GHL rate limiting
- Added `brands_pool`/`dispensaries_pool` to search tags (was only searching campaign tags)
- Dedup: SQL `WHERE NOT EXISTS` prevents re-enqueue + `Set` dedup within each run
- **Timezone inference**: added state-to-timezone mapping in both intake poller (`Classify Contacts`) and outbound dialer (`Code - Check Phone`) since most pool contacts lack timezone data. Maps US state/Canadian province codes to IANA timezone names (e.g. `NY`→`America/New_York`, `CA`→`America/Los_Angeles`).
- **Native scheduling**: the dialer uses n8n's Schedule Trigger at a two-minute interval. The workflow's timezone-aware business-hours guard remains the authority for whether a call may start; no external cron job is required.
- **Release-lock resolution (2026-08-14)**: The shared scheduled dialer had an n8n Postgres v2.6 `queryReplacement` binding failure (`there is no parameter $1`) in the queue-release path. The affected node and three related persistence nodes were migrated to direct `require('pg')` Code nodes in published version `b8e9c57a-f81f-49fd-b469-1388320568c5`. Thirteen consecutive scheduled executions, including `746845`, succeeded afterward. The error occurred before Vapi/Twilio call creation and was not a provider outage.
- **Same-run queue advancement (2026-07-25)**: `LT - Voice Agent V1 Outbound Dialer (Vapi)` releases blocked, invalid, and outside-hours contacts and loops back to `Postgres - Fetch Next Queue Item` in the same execution. `Code - Continue Queue Loop` caps each execution at 25 queue checks. The old `End - No Phone` and `End - Outside Contact Hours` nodes are disconnected legacy nodes and are not required for the live path.
- **Dialer credential guard (2026-07-25)**: live GHL contact lookups began returning `401/403`; the dialer now fails closed after an infrastructure lookup failure instead of looping until its one-hour timeout. The `.env` GHL PIT was subsequently rotated, verified against GHL, propagated to active n8n workflows, and smoke-tested with execution `242609`.
- **Gap hardening (2026-07-25)**: silent human answers now produce `interest_unknown` rather than `vapi_qualified`; global dialer hours are 9am-5pm CT; unknown Vapi campaign tags fail closed; source-tag cleanup is dynamic; superseded Apollo Sheet First intake is unpublished; reporting config/publish schedules are connected and tested.
- **Dialer and ingest crash fixes (2026-07-30)**: Three bugs caused every dialer execution to crash. (1) GHL `Version` header `2023-02-21` rejected — corrected to `2021-07-28` on both `HTTP - Get GHL Contact` and `GHL - Create Call Note`. (2) `Code - Continue Queue Loop` read Postgres `RETURNING` columns (`skip_reason`, `loop_attempts`) that n8n's Postgres v2 node never surfaces — rewritten to read from `$('Code - Check Phone').item.json`. Infrastructure errors (`ghl_lookup_failed`, `eligibility_lookup_failed`) now fail closed with `return []`. (3) Empty queue fetches produced phantom `GET /contacts/` → 403 — added `Code - Queue Found Guard` before lookup. Queue reset: 1,051 contacts (1,047 failed + 4 cooling_down) restored to `status='pending'`. Call Outcome Ingest fix: removed `new Date().toISOString().slice(0,10)` from `queryReplacement` (invalid n8n expression). All three workflows published and verified end-to-end.

**Fixes applied 2026-07-16 (anti-spam):**
- **Campaign tag removal**: After enqueueing, the poller now removes the source campaign tag (e.g. `brands_pool`) instead of the hardcoded `vapi_queue` tag. This prevents contacts from being re-found in subsequent rotation cycles.
- **Blocklist expansion**: `Classify Contacts` now checks all 8 `BLOCKLIST_TAGS` via `hasAnyBlocklistTag()` (was only checking `vapi_voicemail` and `vapi_qualified`). Contacts with any terminal outcome tag have their campaign tag removed inline and are skipped.
- `removeTag()` helper now accepts a `tagsToRemove` array parameter for flexible tag removal.

### Voice Assistant Optimizations (2026-07-20)

Live call audit of 4 Vapi calls uncovered 7 issues across the outbound assistants. All fixes applied and published.

**Jordan (Dispensary, `056f2e50`) — 8 prompt fixes + 2 config fixes:**
- `firstMessage` template variables fixed: `{{contact_name}}` → `{{first_name}}` (n8n passes `first_name`, name was never resolving). Removed `{{market}}` (never passed, rendered as blank).
- "with Transparent eCom" → "from Transparent eCom" (Nico TTS inserted "a" → "with-a-transparent").
- Compliance disclosure removed from `firstMessage` — now system-prompt-only for live calls. Voicemail recipients no longer hear the AI/recording disclosure.
- Discovery questions restructured to ONE AT A TIME: numbered Q1-Q4 each with WAIT instructions. Old bullet list caused all 4 questions fired in one turn.
- New `[IVR vs Voicemail Detection - CRITICAL DISAMBIGUATION]` section with keyword-based classification. Voicemail indicators: "record/rerecord your message", "press pound to send". IVR indicators: "press X for sales/operator". Tiebreaker: assume voicemail.
- `[Speech Naturalness]`: "um"/"uh" minimized to once per call max (was explicitly permitted).
- `[Pronunciation]`: "Point of Sale" never "POS" (Nico says "paws"), "from" never "with".
- `[No Stage Directions]` expanded: banned throat-clearing, coughing, sighing, humming, and text like "*clears throat*" that TTS acts out.
- Transcriber: `smartFormat` false → true (Deepgram suppresses non-speech artifacts).
- Model: Llama 3.3 70B tested (cheaper/faster) but reverted to Claude 3 Haiku (better instruction following). System prompt preserved through swap.
- Voice: Nico kept (Emma + Layla as fallbacks).

**Alex (Brand, `1d7c5d42`) — same discovery questions, IVR/voicemail disambiguation, turn-taking, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Savannah (V1 Outbound, `3f9bbfd2`) — same IVR/voicemail disambiguation, stage directions, and `{{contact_name}}`→`{{first_name}}` fixes.**

**Outbound Dialer (`r7UjWLndmc6EqEUW`) — stuck queue fix:**
- Contact `AX3wfQNpRwm6DG0HgUE2` (deleted from GHL, 2 entries in voice_call_queue) blocked every dialer run since ~18:38 UTC.
- `HTTP - Get GHL Contact` had `neverError: false` — GHL's 400 crashed the run before lock release. Same contact re-picked every 2 min.
- Fix: `neverError: true` on lookup node (400 passes through to Code - Check Phone which falls back to queue phone). `onError: continueRegularOutput` on `GHL - Create Call Note` (cosmetic note failure won't error the execution).
- Intake poller (`bYk1Ai6MJLyhTsDZ`) was unaffected — continued enqueueing contacts every 10 min throughout.

### Voice Tags

vapi_call_attempted, vapi_dnc, vapi_human_answered, vapi_interested, vapi_not_interested, vapi_interest_unknown, vapi_voicemail, vapi_voicemail_left, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected

### Vapi Campaign Tags

| Tag | ID |
|-----|-----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Vapi Assistants

| Assistant | ID | LLM | maxTokens | Temp | Speed | Voice |
|-----------|-----|-----|-----------|------|-------|-------|
| V1 Outbound (Savannah) | 3f9bbfd2 | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |
| Brand (Alex) | 1d7c5d42 | claude-3-haiku | 300 | 0.5 | 1.05 | Elliot |
| Dispensary (Jordan) | 056f2e50 | claude-3-haiku | 300 | 0.5 | 0.88 | Nico |
| V1 Inbound (Savannah) | 43f379ff | claude-3-haiku | 300 | 0.5 | 0.95 | Savannah |

### Regulated-Business Classification and SDR Work Queue Boundary

- Warm is the unassigned intake and verification layer.
- The canonical classifier result is the GHL tag `qualified` for a regulated business (including nicotine, cannabis, CBD, vape, hemp, and related regulated verticals), or `not qualified` for a non-regulated business.
- `qualified` is the regulated-business classification gate; qualified opportunities belong in `Sales Outreach -> Qualified`, not `Sales Outreach -> New`.
- SDR allocation occurs only at Sales Outreach entry:
  - one existing owner: align the other record;
  - matching owners: preserve;
  - conflicting owners: flag for review;
  - neither owner present: deterministic Jason/Marc 50/50 assignment.
- Keep contact `assignedTo`, opportunity native `assignedTo`, and custom opportunity `Owner` aligned.
- Vapi remains in Warm and must exclude contacts tagged `not qualified`; the intake path must not bypass the canonical classification result.
- A successful Vapi warm transfer is manually claimed by the answering SDR, who then promotes the record to Sales Outreach.
- Vapi booking remains on Cameron's Regulated Ads calendar; warm transfer uses the shared SDR number and neutral Sales Lead language.
- Vapi transfer tool: `86d380a3-34d2-41f8-96a0-acf5f0124ccb` (`transferCall`); live human-facing wording is neutral Sales Lead language, while compatibility function name `ok_transfer_to_jason` and shared destination `+15622474600` remain unchanged.

### Website Booking Path

- Canonical calendar: `Regulated Ads On Social/Search`.
- Calendar ID: `SrtXcFVyea7pFl3nTiIK`.
- Direct booking URL: `https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK`.
- Website `Book a Demo` CTAs should link directly to this widget or embed it in an iframe. Visitors should enter identity/contact fields once on the booking form.
- The legacy GHL hero form `kxrHpS9bX16nzkIbr2py` must not appear before the booking form for the primary demo CTA; it duplicates name, email, and phone collection.
- The `/apply/` page currently has a legacy Calendly embed and should replace it with:

```html
<div style="width:100%; max-width:1100px; margin:0 auto;">
  <iframe
    src="https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK?utm_source=website&amp;utm_medium=calendar&amp;utm_campaign=regulated_ads_booking&amp;utm_content=apply_page"
    style="width:100%; min-height:900px; border:0;"
    scrolling="no"
    title="Book a Regulated Ads Strategy Call">
  </iframe>
</div>
<script src="https://link.msgsndr.com/js/form_embed.js"></script>
```

- After any website booking change, verify the appointment is created on `SrtXcFVyea7pFl3nTiIK`, not a personal, interview, or Calendly calendar.

### Apollo Phone Enrichment Status (custom field rgYJ7UqoznGoe3WeUAtH)

- enriched -- terminal (good)
- no_match -- terminal (no Apollo hit)
- error -- terminal (API error)
- queued -- transient (awaiting Apollo callback)
- queued_phone -- transient (profile enriched, phone requested via async callback)
- callback_timeout -- terminal (set by reaper when queued > 24h)
- callback_failed -- terminal (Apollo callbacks received but processing failed)

### Apollo Enrichment Pipeline (Fixed 2026-07-14)

The pipeline was completely dead since 2026-05-13. All webhook-based workflows had 0 executions.

**Before fix**: 3 webhook workflows with 0 executions each, 1,279 contacts stuck at callback_timeout.

**After fix**: The poller workflow is the canonical intake; prior separate intake workflows are superseded. It retains the GHL-called compatibility webhook `ghl-apollo-phone-enrichment-intake-v3`, which now only acknowledges flag events. A native Schedule Trigger was added and tuned to every 5 minutes/max 10, but its first single-call run `1111574` errored on all ten contacts; the Schedule Trigger is currently disabled in active version `9c8c63ab-588d-4519-925f-72469781d05c` pending diagnosis. The webhook queue route remains active. Intended processing still performs profile match and async phone reveal with one Apollo request/contact:
1. Sync profile match: calls Apollo `/v1/people/match` (no phone), writes name/email/company/LinkedIn/title/dept/revenue immediately
2. Async phone request: calls Apollo again with `webhook_url` pointing to V4 callback handler

| Workflow | ID | Status |
|----------|-----|--------|
| **LT - Apollo Phone Enrichment Polling** | **JH8ShfpglWmLMZ3l** | **Active; Schedule Trigger paused; webhook ack-only; version `9c8c63ab-588d-4519-925f-72469781d05c`** |
| GHL Apollo Phone Enrichment - Callback Handler V4 | U7c6byTLXAMgcS75 | Active (1,058+ callbacks received by 2026-07-16, working) |
| GHL Apollo Enrichment - Webhook Intake (Sheet First) | WmKAhG7mIaXonNsh | Active (0 executions - superseded by polling) |
| GHL Apollo Enrichment - Phone Webhook Intake (Staged) | WuxgTa0EEL1mb2SA | **Unpublished** (legacy; 1,008 orphaned webhook executions canceled 2026-07-16) |
| GHL Apollo Phone Enrichment - Callback Handler V3 | YaWizRnw7XmkcvZH | **Unpublished** (legacy V3, fully superseded by V4) |

**Pipeline flow:**
1. **Scheduled worker (currently paused)** scans GHL for contacts needing enrichment (3 sources: `Enrich Phone via Apollo = Yes`, empty enrichment status + no phone, orphaned `queued` / `queued_phone` status), capped by `maxPerRun=10` when resumed.
2. **Sync step**: Calls Apollo `/v1/people/match` with name/email/LinkedIn → writes profile data (name, email, company, title, dept, LinkedIn, revenue, funding) to GHL immediately
3. **Async step**: Calls Apollo `/v1/people/match` with `reveal_phone_number: true` + `webhook_url` pointing to V4 callback → Apollo processes and calls back
4. **V4 callback handler** receives the phone number and updates GHL with it, setting status to `enriched`
5. **GHL automation caller** (`WL - Apollo Phone Enrichment Trigger`) watches for `Enrich Phone via Apollo = Yes` and POSTs to `ghl-apollo-phone-enrichment-intake-v3`, a Webhook node on the active poller workflow. This route now acknowledges only; the Schedule Trigger worker handles contact lookup and Apollo requests in paced batches. The pre-change webhook fan-out caused GHL HTTP 429 errors; see the current Apollo follow-up at the top of this document before another mass queue.

**2026-10-08 rate-limit improvement:** the pre-change live graph had only Webhook → Config → Code and no Schedule Trigger, so each GHL flag event immediately fetched a GHL contact and made up to two sequential Apollo calls. The new active graph is Schedule Trigger (30 min) + Webhook → Config → Code. Webhook mode exits without external API calls; scheduled mode scans queued GHL statuses and processes at most five contacts serially. Apollo Usage Stats showed the `people/match` endpoint at 1,000 requests/minute, 0 consumed at the 13:47 UTC read, and no hourly/daily cap returned; this cap is shared by the team and Apollo returns `Retry-After` on its own 429s. The observed 12:55 burst's sampled 429 was instead a GHL contact-fetch error. The first scheduled worker run remains unobserved; do not manually execute it against live contacts.

**Webhook key** for all Apollo callbacks: `<APOLLO_WEBHOOK_KEY — see .env>`

**Apollo API key**: `<APOLLO_API_KEY — see .env>`

### Apollo Pipeline Full Audit + Fixes (2026-07-15)

Full review of 7 Apollo-related workflows found 2 CRITICAL bugs, 2 HIGH issues, and several medium/low cleanups. 10 fixes applied across 6 workflows:

#### 1. `queued_phone` status invisible to Timeout Reaper — CRITICAL (RL5Zy, JH8Sh)

**Bug**: Polling workflow set status to `queued_phone` after async phone request, but Reaper only searched for `queued`. Contacts stuck in async callback phase were never unblocked.

**Fix**: Reaper now searches both `queued` AND `queued_phone`. Polling workflow now writes `Apollo Phone Enrichment Queued At` (NgC3xGTh0laQ9ArTnude) alongside `queued_phone` so aging works.

#### 2. Intake Poller re-triggers enrichment on `queued_phone` — CRITICAL (bYk1)

**Bug**: Classify Contacts code matched `queued` → `waiting` but `queued_phone` fell through to default `enrich` action, triggering duplicate Apollo API calls for already-pending contacts.

**Fix**: Added `queued_phone` to the `waiting` path alongside `queued`.

#### 3. SQL injection in Sheet First intake — CRITICAL (WmKAh)

**Bug**: Build Upsert SQL used template-literal injection with manual `''` escaping — same anti-pattern previously fixed in LinkedIn Reply Backfill.

**Fix**: Switched to parameterized query with `$1..$9` and `queryReplacement` array. Code node now outputs typed JSON fields instead of building SQL strings.

#### 4. `doHttpRequest` wrapper pattern removed from all workflows — HIGH

The wrapper pattern `async function doHttpRequest(options) { ... $httpRequest / this.helpers.httpRequest ... }` called with `.call(this, ...)` causes HTTP 400 errors in task-runner loops. Removed from: V4 callback (U7c6), V3 callback (YaWi), Intake Poller Search GHL Contacts (bYk1), Sheet First main Code node (WmKAh). All replaced with direct `this.helpers.httpRequest(options)` or `this.helpers.httpRequest(opts)`.

#### 5. V3 callback handler had zero error handling — HIGH (YaWi)

**Bug**: No try/catch in main Code node. Any error returned 500 with no status update.

**Fix**: Added try/catch with best-effort `callback_failed` status update on error, matching V4's error handler. Then **unpublished** V3 (fully superseded by V4).

#### 6. GHL error handling in polling workflow — MEDIUM (JH8Sh)

**Bug**: `ghl()` helper swallowed all errors identically (`{ ok: false }`). A 429 rate limit looked the same as a 404.

**Fix**: `ghl()` now returns `{ ok: false, status: ... }`. All 3 search sources retry on 429 with 5s delay before re-scanning the same page.

#### 7. V4 callback `Apollo Contact Id` conditionally set — MEDIUM (U7c6)

**Bug**: `Apollo Contact Id` was only written when `normalizedPhone` was found. If Apollo returned valid profile but phone was blocked (corporate phone match), the contact lost traceability.

**Fix**: `successfulApolloContactId` now always set to `str(person?.contact?.id || person?.id)` regardless of phone status.

#### 8. Reaper Config node corruption — LOW (RL5Zy)

**Bug**: Set v3.4 Config node had nested `parameters.parameters.assignments.assignments` corruption artifact from a prior `setNodeParameter` call.

**Fix**: Removed via REST API PUT. Config node now has clean `{"mode":"manual","assignments":{"assignments":[...]}}` shape.

#### 9. Intake Poller `removeTag` used `$httpRequest` fallback — LOW (bYk1)

**Bug**: Classify Contacts `removeTag()` function checked `typeof $httpRequest === 'function'` as primary with `this.helpers.httpRequest` as fallback.

**Fix**: Replaced with direct `await this.helpers.httpRequest(opts)` call.

#### 10. Status pipeline now consistent end-to-end

| Status | Set by | Read by | Action |
|--------|--------|---------|--------|
| `queued` | Staged Intake (legacy) | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `queued_phone` | Polling workflow | Reaper, Intake Poller | Reaper: unblock after 24h; Poller: waiting |
| `enriched` | V4 callback | Intake Poller | Enqueue to voice_call_queue |
| `no_match` | Polling/V4/Sheet First | Intake Poller | Terminal skip |
| `error` | Polling | Intake Poller | Terminal skip |
| `callback_failed` | V4 callback catch | Intake Poller | Terminal skip |
| `callback_timeout` | Reaper | Intake Poller | Terminal skip |

### Apollo Production Hardening (2026-07-16)

- Audited the live production path end-to-end: Polling (`JH8ShfpglWmLMZ3l`), V4 callback (`U7c6byTLXAMgcS75`), and Reaper (`RL5ZyUoshSPbmVA1`) were all active and published.
- Canceled **1,008** orphaned `running` executions on legacy staged workflow `WuxgTa0EEL1mb2SA`. Sample stuck runs never progressed beyond the `Webhook` node; this was stale execution state, not the active Apollo production path.
- Polling workflow fix: orphan re-discovery now searches both `queued` and `queued_phone` instead of only `queued`.
- Callback V4 fix: Apollo provider-level callback failures (for example `failure_reason: "you ran out of mobile number credits"`) now write `Apollo Phone Enrichment Status = callback_failed` instead of being silently treated as `no_match`.
- Polling workflow write-path fix: hardened GHL contact update fallback after reproducing live GHL behavior on `PUT /contacts/{id}`.
  Accepted shape for this endpoint is `{"customFields":[...]}` without `locationId`; bodies containing `locationId` or `customField` can return `422`.
- Polling workflow now falls back to a minimal write when the full profile update fails, ensuring at least:
  - `Apollo Phone Enrichment Status = queued_phone`
  - `Apollo Phone Enrichment Queued At = <today>`
  - `Enrich Phone via Apollo = No`
  - Apollo IDs where available
- Backfilled 6 previously blank contacts on 2026-07-16 into `queued_phone` so they are now visible to the callback/reaper path immediately:
  `VXwNjbZyBm1DMNljim6g`, `K9otZl89OAFlWmGk8fY7`, `mUgGwrkOB8CW8reYmpMd`, `e7eu0xGixu3ATmA61OqN`, `KA8xGJbf0QZHxXV6HXWF`, `8uobjmgriFLAdtmHfjk7`.

### Custom Field IDs (GHL)

- Apollo Phone Enrichment Status = rgYJ7UqoznGoe3WeUAtH (SINGLE_OPTIONS)
- Apollo Phone Enrichment Queued At = NgC3xGTh0laQ9ArTnude (DATE)
- Enrich Phone via Apollo = gdJDuZelIxEBE6n9i5Q6 (SINGLE_OPTIONS: Yes/No)
- Em_Emerald_Contact_ID = R0wbDRyzZz34PMlQSRWN
- Em_Source_File = ILurFacMbAaHz2DdGjPa

### Pool Tags

- brands_pool -- contacts from Brands.csv import
- dispensaries_pool -- contacts from Dispensaries.csv import

### Apollo Re-enrichment on Bad Numbers

In callback workflow fx4UvKUWbqJEY3LK, when Vapi returns wrong_number or contact_disconnected, Vapi first tries every available phone number for the contact before requesting Apollo enrichment (2026-08-04).

**Phone candidate sources** (built by the dialer's `Code - Check Phone`, deduped + E.164-normalized): GHL primary `phone`, `Corporate Phone` (`036gD9ds9P5V8VUHnFBP`), `Company Phone` (`YNlWu5FRGk0PhepqD0Zo`), `Em_All_Known_Phones` (`F8iUFGsA8CqdzEzjY3Eh`, may hold multiple), and the queue's `phone_e164` pool fallback.

**How it works:**
- `voice_call_queue` gained `phone_candidates jsonb` and `phone_index integer NOT NULL DEFAULT 0`.
- The dialer (`r7UjWLndmc6EqEUW`) builds the candidate list, picks `phone_candidates[phone_index]`, and passes `phone_candidates` (JSON string) + `phone_index` into the Vapi call metadata/variableValues. `Postgres - Mark Attempted` (updated) also persists `phone_candidates` and `phone_index` to the queue row after the call is submitted.
- The callback's `Code - Normalize End Of Call` extracts `phone_candidates`/`phone_index` from the Vapi metadata (same proven path as `queue_id`).
- `Code - Decide Next Phone` (replaces the old `Should Re-enrich Phone` IF) reads disposition + candidates + index from `Code - Normalize End Of Call`. If `wrong_number`/`contact_disconnected` and `(index + 1) < candidates.length`, it advances: `Postgres - Advance Phone Index` sets `phone_index + 1`, `status='pending'`, `attempt_count=0`, `next_attempt_at=NOW()`, clears the lock, and `HTTP - Remove Bad Call Tag` removes the `vapi_wrong_number`/`vapi_contact_disconnected` tag from GHL so the dialer's blocklist doesn't skip the retry. Only after the last candidate fails does `HTTP - Set Apollo Enrichment` set `Enrich Phone via Apollo = Yes` (custom field gdJDuZelIxEBE6n9i5Q6). The existing LT - Apollo Phone Enrichment Intake V3 then looks up a new number.
- If `queue_id`/`phone_candidates` are absent from the metadata (rare non-dialer call), the decision degrades to the previous behavior (Apollo enrichment immediately).

## Vapi Workflow Fixes (2026-07-14)

Full review conducted of all 12 Vapi-related workflows. Five bugs fixed across 3 workflows:

### 1. Race Condition: Dialer Picked Queue Items Without Lock (r7UjWLndmc6EqEUW)
`Postgres - Fetch Next Queue Item` used `SELECT...LIMIT 1` (read-only). Between the read and the write, `LT - Voice Dequeue Next` could `UPDATE...RETURNING` the same item, causing **duplicate outbound calls** to the same contact.
**Fix**: Changed to `UPDATE...FROM...RETURNING` that atomically locks the row (`locked_at = NOW(), lock_owner = 'outbound-dialer'`) at fetch time.

### 2. `report_referral` Tool Was Dead Code (fx4UvKUWbqJEY3LK)
`Switch - Route Tool` output 4 routed `report_referral` to `Code - Normalize End Of Call`, which checks `endedReason`/`analysis.summary` — none of which exist on tool call payloads. Node returned `[]` silently.
**Fix**: Re-routed to `Respond - 200` so Vapi gets a proper acknowledgment.

### 3. Intake Poller Could Create Duplicate Queue Entries (bYk1Ai6MJLyhTsDZ)
`Postgres - Insert Queue` used plain `INSERT INTO...VALUES(...)` with **no dedup check**. The webhook-based enqueue had `WHERE NOT EXISTS` but the poller didn't.
**Fix**: Wrapped INSERT in `SELECT...WHERE NOT EXISTS (SELECT 1 FROM voice_call_queue WHERE contact_id = $1 AND status IN ('pending', 'in_progress'))`. Also updated `Transform Postgres Output` to return `[]` gracefully when dedup blocks insertion (was throwing an error).

### 4. No Error Handling on Tag Removal HTTP Nodes (bYk1Ai6MJLyhTsDZ)
Three HTTP DELETE nodes (`Remove Tag - Enqueued`, `Remove Tag - Enriching`, `Remove Tag - Skipped`) lacked `continueOnFail`. A flaky GHL tag deletion crashed the workflow after the enqueue/enrich/skip already succeeded.
**Fix**: Enabled `continueOnFail: true` on all three.

### 5. Timer System Static Data Race Condition (fx4UvKUWbqJEY3LK)
`$getWorkflowStaticData('global')` not atomic across concurrent executions. Two rapid status-update webhooks could both start a 465-second timer chain — producing duplicate background warnings and force-end commands.
**Fix**: Replaced `state.timersScheduled` boolean with `state.timersScheduledAt` timestamp. Added 60-second dedup window: if a timer was already started within 60s, a duplicate is skipped. Updated `Code - Prepare Background Warning` and `Code - Prepare Hard Stop` to check `timersScheduledAt`.

## Vapi Anti-Spam Fixes (2026-07-16)

Root-cause audit triggered by a contact complaint about repeated Vapi calls after voicemail had already been left. Identified **4 bugs combining into an infinite call loop** across 3 workflows. All published 2026-07-16.

### The Spam Chain (before fixes)

1. Intake Poller finds contacts by campaign tag (e.g. `brands_pool`) → enqueues → **only removed `vapi_queue` tag** (which contacts never had). Campaign tag stayed.
2. Dialer calls → voicemail → Callback applies tags but **never marks queue `completed`** (only the tool-call `update_lead_status` path did that).
3. 3 days later, dialer retries → `Code - Check Phone` sees `vapi_voicemail` tag → blanks phone → release lock → `status = 'completed'`.
4. Next poller cycle finds same contact (campaign tag still present) → old entry is `completed` → dedup only blocks `pending`/`in_progress` → **creates new queue entry**.
5. Dialer picks new entry → calls again → voicemail again → loop forever.

### Fixes Applied

#### 1. Intake Poller removed wrong tag after enqueue (bYk1Ai6MJLyhTsDZ) — CRITICAL

**Bug**: `Remove Tag - Enqueued` always removed `vapi_queue`, but contacts were found by campaign tags like `brands_pool`, `dispensaries_pool`, `vapi_campaign_brand`, `vapi_campaign_dispensary`. The campaign tag never got removed, so contacts were re-found every 40-minute rotation cycle.

**2026-07-16 Fix (incomplete)**:
- `Classify Contacts` now outputs `source_tag` (the matched campaign tag) with every enqueue result
- `removeTag()` function accepts `tagsToRemove` array argument
- `removeFromQueue` check replaced by `hasAnyBlocklistTag()` checking all 8 outcome tags
- **BUT**: `Transform Postgres Output` couldn't read `source_tag` — Postgres `INSERT...RETURNING` only returns DB columns, not the extra `source_tag` field. `Remove Tag - Enqueued` silently fell back to removing `"vapi_queue"`, which contacts never had. Campaign tag stayed on first enqueue.

**2026-07-22 Fix (this session)**: Rewrote `Transform Postgres Output` to look up `source_tag` from `$("Classify Contacts").all()` by `contact_id` using a pre-built lookup map, instead of expecting Postgres to pass it through. `Remove Tag - Enqueued` now receives the real campaign tag on every run.

**Self-healing behavior**: On the next poller cycle after a contact gets a blocklist outcome tag, `Classify Contacts` matches it in the `skipped` path (not the `enqueue` path). The `skipped` path resolves `matchedCampaignTag` in-scope before any Postgres call and removes the campaign tag inline. So even before this fix, contacts eventually self-cleaned within 1 cycle after getting a terminal tag — but the first enqueue always left the campaign tag intact.

#### 2. EOC callback never marked queue completed (fx4UvKUWbqJEY3LK) — CRITICAL

**Bug**: End-of-call path was `Normalize End Of Call → Respond → Insert Attempt → Apply Tags → Should Re-enrich Phone`. It inserted call attempts, applied GHL tags, and triggered re-enrichment — but **never set `voice_call_queue.status = 'completed'`**. Only the tool-call path (`update_lead_status` → Postgres - Update Status) updated the queue.

**Fix**: Added new Postgres node `Postgres - Mark Queue Completed` wired between `GHL - Apply Tags` and `Should Re-enrich Phone`:
```sql
UPDATE voice_call_queue SET status = 'completed', updated_at = NOW() WHERE queue_id = $1;
```
Now every end-of-call callback immediately terminates the queue entry.

#### 3. Only 2 of 10 outcome tags blocked retries (r7UjWLndmc6EqEUW) — HIGH

**Bug**: `Code - Check Phone` blocklist was only `['vapi_voicemail', 'vapi_qualified']`. Contacts with `vapi_no_answer`, `vapi_busy`, `vapi_wrong_number`, `vapi_contact_disconnected`, `vapi_voicemail_left`, `vapi_dnc` were retried indefinitely (up to `max_attempts`).

**Fix**: Expanded `BLOCKLIST_TAGS` to all 8 terminal tags:
```
vapi_voicemail, vapi_voicemail_left, vapi_qualified, vapi_no_answer, vapi_busy, vapi_wrong_number, vapi_contact_disconnected, vapi_dnc
```

#### 4. Intake Poller blocklist only checked 2 tags (bYk1Ai6MJLyhTsDZ) — HIGH

**Bug**: `Classify Contacts` only skipped contacts with `vapi_voicemail` or `vapi_qualified`. Contacts with other outcome tags could be re-enqueued on discovery.

**Fix**: Added `hasAnyBlocklistTag()` using the same 8-tag `BLOCKLIST_TAGS` constant. Also removes the campaign tag inline before skipping.

### Defense Layers (per-contact, now active)

| Layer | What blocks the call |
|--------|---------------------|
| 1 | **Campaign tag removed** after enqueue — poller never re-finds contact |
| 2 | **Queue marked `completed`** by callback — dialer FETCH ignores it (`WHERE status = 'pending'`) |
| 3 | **Dialer live-checks** all 8 outcome tags on GHL contact before every call via `Code - Check Phone` |
| 4 | **Intake Poller rejects** contacts with any of the 8 blocklist tags via `hasAnyBlocklistTag()` |
| 5 | **Queue dedup** `WHERE NOT EXISTS` blocks duplicate `pending`/`in_progress` entries |

### Key Constants (synced across all 3 workflows)

```
BLOCKLIST_TAGS = ['vapi_voicemail', 'vapi_voicemail_left', 'vapi_qualified', 'vapi_no_answer', 'vapi_busy', 'vapi_wrong_number', 'vapi_contact_disconnected', 'vapi_dnc']
```

### New Callback EOC Path

```
Before: Apply Tags → Should Re-enrich Phone
After:  Apply Tags → Postgres - Mark Queue Completed → Should Re-enrich Phone
```

### Vapi Call-Path Hardening (2026-07-22 — 2026-07-23)

- n8n target upgraded to `2.33.3`; recurring workflows use native Schedule Trigger nodes, not OS/Coolify cron jobs.
- `Code - Detect Tool vs Callback` now reads the original `Webhook - Vapi` input because the Config Set node replaces the current item.
- Callback normalization now reads Vapi IDs from `message.assistant.metadata`, `message.assistant.variableValues`, and `artifact.variables`.
- Callback completion-note JSON is built as an object expression, avoiding invalid JSON when summaries contain quotes or newlines.
- GHL note/tag failures continue without blocking Postgres queue completion; queue completion passes query replacements as an array.
- The callback no longer invokes `LT - Voice Dequeue Next`. That helper is unpublished and must remain an explicit/manual helper, not an automatic call-start path.
- The outbound dialer uses a native two-minute Schedule Trigger plus the existing timezone-aware business-hours guard.
- The outbound dialer atomically changes a selected queue row from `pending` to `in_progress` before calling Vapi. Ambiguous Vapi/API failures cannot be retried after the stale-lock window; no-phone and outside-hours release branches explicitly restore `pending`.

### Vapi/n8n Final Hardening (2026-07-23)

- n8n is now documented and operated at target version `2.33.3`; recurring workflows use native Schedule Trigger nodes rather than OS/Coolify cron.
- Callback timer state keeps the 60-second duplicate-start guard and now prunes ended/inactive entries older than 30 minutes.
- `LT - Voice Queue Enqueue` (`XzcpOBi9YcIhJPck`) requires `X-LT-Voice-Queue-Secret`; the caller reference is `VOICE_QUEUE_ENQUEUE_SECRET`. Missing authentication fails closed before queue insertion.
- `LT - Apollo Phone Enrichment Polling` reports `apollo_phone_request_failed` when the asynchronous Apollo phone request fails after profile processing.
- `LT - Apollo Queued Timeout Reaper` now connects `Build Slack Summary` to `Post to Slack #reaper`.
- Removed the stale response-code option from `LT - Call Outcome Ingest`.
- Final live workflow versions were checked after each mutation; `versionId` matched `activeVersionId` for all changed workflows.
- Safe queue smoke checks passed: unauthenticated requests return `400 unauthorized`; authenticated malformed requests reach validation and do not insert a queue row. Live Vapi control URLs remain untested because exercising them requires an actual call.

## LinkedIn Workflow Fixes (2026-07-14 — 2026-07-15)

### Current Published Workflow Inventory (Updated 2026-07-16)

**Canonical LinkedIn path**: Dispatcher sends connection requests -> Acceptance Checker/State Sync marks contacts `connected` -> DM Sequence sends the 4-message cadence -> Unipile New Messages/Reply Backfill marks conversations active -> DM Suppression or sequence completion prevents future sends.

**Published / active LinkedIn workflows left running:**

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Active | Selects `ready` contacts from `linkedin_connection_state`, live-checks GHL tags/conversations, sends LinkedIn connection requests through Unipile, writes `requested` state. |
| LT - LinkedIn Connection Acceptance Checker (Unipile) | 3ttEvr5NMcQCS4Hp | Active webhook | Receives Unipile relation/acceptance events at `/webhook/lt-linkedin-connection-accepted`, finds matching state row, marks contact `connected`, tags GHL with `linkedin_connected`. |
| LT - LinkedIn Connection State Sync (Unipile) | ceaKnz6E3onQrZpt | Active schedule `15 */6 * * *` | Reconciles GHL contacts + LinkedIn profile URLs against Unipile and upserts ready/connection state rows. |
| LT - LinkedIn Connection State Upsert | Old7ZvyVYgFaJgDr | Active webhook | Canonical state-table write endpoint at `/webhook/lt-linkedin-connection-state-upsert`; used by dispatcher, acceptance, sync, suppression, and DM workflows. |
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Active schedule `0 12-22 * * 1-5` | Canonical post-connection DM sequence for contacts with `connection_status = connected`; sends 4 DMs and later marks complete. |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | Active webhook | Receives inbound LinkedIn message events at `/webhook/lt-unipile-linkedin-new-messages`; marks `dm_conversation_status = active` so outbound DM sequences stop. |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | Active schedule `*/10 * * * *` | Backfills/updates reply state from Unipile conversations so contacts with inbound replies are not messaged again. |
| LT - LinkedIn Relations Backfill | VPiHfBwzOHaJnHBY | Active daily 3:15am | Backfills LinkedIn relation/provider state, including synthetic rows where needed. |
| LT - LinkedIn DM Suppression from GHL Tag | IPN8jnR3XSurX0o1 | Active webhook | Receives GHL `stop_linkedin_dms` automation payload at `/webhook/lt-linkedin-suppress-dms`; resolves LinkedIn profile, applies `linkedin_dm_sequence_completed`, and terminal-upserts real + synthetic state IDs. |

**Unpublished / intentionally stopped:**

| Workflow | ID | Status | Why |
|----------|----|--------|-----|
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Unpublished, `active=false` | Redundant one-touch LinkedIn follower DM path. It used separate follower state semantics and could overlap the canonical dispatcher -> connected -> 4-message DM sequence. |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Unpublished, `active=false` | Misconfigured with the LinkedIn Unipile account ID (`V9eiHiDpRmCtan0YNdzsQw`) and no account-type guard. It was sending the short Instagram templates as LinkedIn DMs using `instagram_dm_state`. |
| LT - LinkedIn DM Sequence Test (No Delay) | wnpVYUNFLyNe5cS6 | Manual/test only | Not part of production sending. Use only for controlled testing. |

### Canonical DM Sequence Definition (d0tEtijajisIsYcs)

The production LinkedIn DM sequence sends 4 messages after a contact reaches `connection_status = connected` in `linkedin_connection_state`.

| Step | When Eligible | Behavior |
|------|---------------|----------|
| 1 | `sequence_step = 0` and `dm_sequence_started_at IS NULL` | Sends DM 1 immediately and sets `dm_sequence_started_at`. |
| 2 | Sequence started at least 3 days ago | Sends DM 2. |
| 3 | Sequence started at least 7 days ago | Sends DM 3. |
| 4 | Sequence started at least 10 days ago | Sends DM 4. |
| Complete | Sequence started at least 14 days ago and `sequence_step = 4` | Sends no DM; applies `linkedin_dm_sequence_completed`, sets `connection_status = completed`, and advances terminal state. |

The sequence skips if `payload_json.dm_conversation_status = active`, if GHL conversation lookup finds an inbound message, or if the reply lookup fails. Reply lookup failure is fail-closed.

### Fixes Applied 2026-07-16

- Traced malformed LinkedIn screenshot messages and identified they were sent by `LT - Instagram DM Sequence (Unipile)`, not the canonical LinkedIn DM sequence. The exact templates were `instagram.v1[1]` and `instagram.v1[2]`.
- Unpublished `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`) after confirming it was using the LinkedIn Unipile account ID and separate `instagram_dm_state`, creating an accidental second LinkedIn DM path.
- Unpublished `LT - LinkedIn Follower DM Sequence (Unipile)` (`pq7XVajNFnnwMUTr`) because the canonical 4-message connected-contact sequence supersedes the one-touch follower DM path.
- Expanded sanitizer coverage across all audited Unipile sender template nodes before unpublishing the redundant paths: template registries are pre-sanitized, and final outbound text is sanitized immediately before `POST /chats` or `POST /users/invite`.
- Cleaned stored mojibake/smart punctuation from audited DM template literals and verified no bad literal message text remained in sender nodes.

### Connection Acceptance Checker (3ttEvr5NMcQCS4Hp)
`access to env vars denied` on Postgres queryReplacement using `$env.UNIPILE_ACCOUNT_ID`. Node `N8N_BLOCK_ENV_ACCESS_IN_NODE` blocks env access. **Fix**: Replaced with hardcoded `V9eiHiDpRmCtan0YNdzsQw`.

### Connection State Sync (ceaKnz6E3onQrZpt)
Task runner timed out after 300s. Code node searches GHL + Unipile with 15 pages/200 contacts. **Fix**: Reduced maxPages 15→5, maxContacts 200→50.

### Follower DM Sequence (pq7XVajNFnnwMUTr)
Code node referenced `CFG.ghlApiBaseUrl`/`CFG.ghlApiKey` but both the Config node's outer `assignments` AND the Code node's CFG object lacked those fields. The Config node had a duplicate inner `parameters.assignments` (11 items with GHL creds) that n8n ignored because only the outer `parameters.assignments` (9 items, no GHL) is the live path. **Fix (2026-07-14)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config inner assignments — BUT this didn't fix the Code node CFG which still didn't read them. **Fix (2026-07-15)**: Added `ghlApiBaseUrl`/`ghlApiKey` to Config outer assignments AND to the Code node CFG object AND fixed the synthetic ID inbound check (see below).

### DM Sequence (d0tEtijajisIsYcs)
`Code doesn't return items properly` — **leading** backtick (not trailing) at start of `jsCode` field in node "Send DM Sequence Messages" caused unterminated template literal syntax error. **Fix (2026-07-14)**: Removed orphan backtick — BUT it was never published (draft versionId ≠ activeVersionId). **Fix (2026-07-15)**: Published the corrected draft; confirmed jsCode char[0] is 'c' (ASCII 99).

### Dispatcher Feeder Tag Check (fXxw5lanZcDmUrst)
`Feed Ready Queue` Code node checked `fullContact.tags` but GHL `GET /contacts/{id}` returns tags nested under `fullContact.contact.tags`. So blocking tags (`linkedin_connection_requested`, `linkedin_connected`, `linkedin_state_queued`) were never detected — `skipped` was always 0. This caused every run to re-process already-queued contacts, but the UPSERT CASE in `linkedin_connection_state` prevented downgrading `requested`/`connected` back to `ready`, so `Fetch Ready Queue` always returned empty. **Fix**: Added GHL response unwrap: `var contactData = fullContact.contact ? fullContact.contact : fullContact;`. Tag check now correctly skips already-processed contacts.

**GHL API response gotcha**: `GET /contacts/{id}` returns `{ contact: { tags: [...], ... } }`. Code reading `.tags` directly will always get `undefined`. Always unwrap via `.contact` first.

### Bulk Feed (2026-07-13)
Discovered dispatcher had zero `connection_status = 'ready'` rows because all contacts in the state table were `requested` or `connected` from June 2026. User exported 14,987 contacts from GHL with LinkedIn URLs and no blocking tags. Batch-upserted via state upsert webhook into `linkedin_connection_state` with `connection_status = 'ready'`. ~15,202 total executions recorded. Dispatcher's `Fetch Ready Queue` will now find contacts on its next scheduled run.

### Full 9-Workflow LinkedIn Audit + Fixes (2026-07-15)

Full review of all 9 LinkedIn workflows found 2 critical bugs, 3 high-severity issues, and 3 medium issues. Three fixes applied:

#### 1. Reply Backfill SQL Injection (QfJ2EZcc7lZwNgxj) — CRITICAL

**Bug**: `Apply Backfill Update` Postgres node used n8n template literal injection:
```
query: `={{ \`UPDATE ... SET payload_json = '\${$json.payload_json_sql}'::jsonb WHERE ghl_contact_id = '\${$json.ghl_contact_id}'...\` }}`
```
The Code node manually escaped with `.replace(/'/g, "''")`, but this is not safe against all SQL injection vectors (backslash/Unicode).

**Fix**: Changed Code node output to `JSON.stringify(nextPayload)` (no `''` escaping) and Postgres node to parameterized query:
```sql
UPDATE linkedin_connection_state
SET payload_json = $1::jsonb, metadata_json = $2::jsonb, ...
WHERE ghl_contact_id = $3
```
With `queryReplacement: "={{ [ $json.payload_json_sql, $json.metadata_json_sql, $json.ghl_contact_id ] }}"`.

#### 2. Follower DM Synthetic ID Inbound Check (pq7XVajNFnnwMUTr) — HIGH

**Bug**: `Process LinkedIn Followers` Code node passed `existing?.ghl_contact_id || 'linkedin:follower:' + providerId` to `hasInboundConversation`. For new followers (no Postgres row), `existing` was `undefined`, so the fallback synthetic ID hit GHL's conversation search API. GHL returned an error (no contact with that ID) → catch returned `{ blocked: true }` → **all new follower DMs were skipped**.

**Fix**: Only call `hasInboundConversation` when the Contact ID is a real GHL contact:
```js
var checkContactId = existing?.ghl_contact_id || '';
var inbound = checkContactId
  ? await hasInboundConversation.call(this, checkContactId)
  : { blocked: false, reason: '' };
```
New followers (no existing row) now skip the inbound check and allow the DM send (fail-open).

**Also fixed**: Added `ghlApiBaseUrl` and `ghlApiKey` to both Config node outer assignments AND Code node CFG object. Previously they were only present in a duplicate inner `parameters.parameters` object that n8n ignores.

#### 3. DM Sequence Backtick Published (d0tEtijajisIsYcs) — CRITICAL

**Bug**: Leading backtick had been removed from the draft in a prior fix session but the draft was never published — the active version still had the syntax error.

**Fix**: Published the corrected draft. Verified jsCode char[0] = ASCII 99 ('c').

### Unicode Encoding Fix — LinkedIn + Instagram Send Paths (2026-07-15)

**Bug**: Message templates contained Unicode smart punctuation (curly apostrophes `'`/`'` U+2018—U+2019, smart quotes `"`/`"` U+201C—U+201D, em-dashes `—`, ellipsis `…`, non-breaking spaces). Some already-stored templates also contained mojibake like `canΓÇÖt`. These multi-byte characters could get decoded as Latin-1/CP437 instead of UTF-8 when passing through the `JSON.stringify` → Unipile API chain, producing garbled text (e.g., `can't` → `canâ€™t` / `canΓÇÖt`).

**Fix**: Added/expanded `sanitizeMessage()` and `sanitizeTemplateRegistry()` across all Unipile send-capable message-template nodes. Stored templates are pre-sanitized when the Code node starts, and final outbound text is sanitized again immediately before `POST /chats` or `POST /users/invite`.

```js
function sanitizeMessage(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/\u00A0/g, ' ')
    .replace(/\u0393\u00C7[\u00D6\u00FF]/g, "'")
    .replace(/\u0393\u00C7[\u00A3\u00A5]/g, '"')
    .replace(/\u0393\u00C7[\u00F4\u00F6]/g, '-')
    .replace(/\u0393\u00C7\u00AA/g, '...')
    .replace(/\u00E2\u20AC[\u02DC\u2122]/g, "'")
    .replace(/\u00E2\u20AC[\u0153\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u0094]/g, '-')
    .replace(/\u00E2\u20AC\u00A6/g, '...');
}
```

Applied in the message assembly line of each workflow before the Unipile `POST /chats` or `POST /users/invite` call:
```js
var message = sanitizeMessage(msgTemplate.replace(/\{first_name\}/gi, firstName));
```

| Workflow | ID | Node fixed |
|----------|-----|------------|
| LT - LinkedIn DM Sequence (Unipile) | d0tEtijajisIsYcs | Sync Connected from Unipile; Send DM Sequence Messages |
| LT - LinkedIn Follower DM Sequence (Unipile) | pq7XVajNFnnwMUTr | Process LinkedIn Followers |
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | fXxw5lanZcDmUrst | Dispatch LinkedIn Requests |
| LT - Instagram DM Sequence (Unipile) | iCnY6ccdHhfJg3sf | Process Instagram Outreach |

**Verification 2026-07-15 follow-up**: live versions were active/published after patching. Final audit passed for smart/mojibake sanitizer coverage, template registry pre-sanitization where present, immediate send-time sanitization, and no remaining bad literal message text in the audited sender template nodes.

The local operator helper `local-scripts/suppress_linkedin_dms.py` provides one-command DM suppression (resolves LinkedIn profile via Unipile, finds GHL contact, tags + state-table-terminates in both ID paths).

### LinkedIn Regex Double-Escaping — Root Cause & Prevention (2026-08-19)

The 07-15 sanitizer/mojibake fix **recurred as a different failure** on 08-19. An MCP mutation on 08-11 (`3b70854e`) double-escaped regex literals in Code-node `jsCode`, producing **syntactically valid JavaScript that silently does the wrong thing**. This is distinct from the 07-15 mojibake (Unicode decode at write time): here the source characters were corrupted at edit time.

**Two distinct failures resulted (not one):**
1. `identifier()` `/^https?:\\\\/\\\\//i` → **crashed the Dispatcher at parse time** (`SyntaxError: Invalid regular expression flags`). No invites were sent at all from 08-11 → 08-18.
2. After the 08-18 REST PUT fixed only that crash regex, `sanitize()` `/[\\\\u2018\\\\u2019]/` matched literal `u`/`C`/`D` + digits instead of smart quotes (`u`→`'`, `C`→`"`, producing `"ameron co-fo'nder of Transparent e"om`), and `/\\\\{first_name\\\\}/gi` matched only a literal `\{first_name\}`, leaving `{first_name}` unreplaced. **Garbled invites were sent only from 08-18 00:15 → 08-19 04:45**, bounded by the 60/day cap — not since 08-11.

**Why the 08-18 REST PUT repair missed it:** it fixed the crash-causing `\\/` regex and the daily-cap logic via direct REST `PUT /workflows/{id}`, but the PUT inherited the two offending Code-node `jsCode` bodies unchanged because the corrupt regexes were still valid JS.

**Fix + prevention:** `scripts/linkedin/fix_linkedin_sanitize_double_escape.py` rewrites `\\uXXXX` → `\uXXXX` and `\\{` → `\{` idempotently (dry-run report by default). Re-publish after every run and verify `versionId == activeVersionId`. When editing any Code node with an MCP/API tool path, avoid `\\\\`-style literal escaping in character classes and `\\{` for placeholders; use character-class form `[/][/]` instead of `\/` where possible. Full narrative: `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`.

### Unfixed Issues (acknowledged, not fixed today)

| Severity | Issue | Workflow(s) |
|----------|-------|-------------|
| Medium | Two different PIT tokens in use (`pit-2d2e...` vs `pit-b278...`) | Dispatcher vs others |
| Medium | `payload_json` grows unbounded per row due to `||` merge on every upsert | Connection State Upsert (Old7Z) |
| Low | Reply Backfill runs every 10 min (`*/10 * * * *`) — 144x/day | Reply Backfill (QfJ2) |
| Low | Relations Backfill can produce thousands of synthetic rows | Relations Backfill (VPiHf) |
| Low | `n8n/lt-linkedin-dispatcher.ts` SDK file is stale vs live workflow | Dispatcher (fXxw) |

## Emerald Email Campaign (Activated 2026-07-07)

Dispatches ~14,702 unenrolled Emerald contacts through GHL email sequences using 4 sender addresses with safe warmup pacing.

### Pipeline

```
Snapshot -> Postgres (Emerald_Campaign_Contacts) -> Dispatcher -> GHL tags + sender field
-> GHL "Enrollment Queue Entry" workflow -> Emerald Sequence -> Email
-> GHL Event webhook -> n8n Event Ingest -> Postgres (Email_Events)
```

### n8n Workflows

| Workflow | ID | Status |
|----------|----|--------|
| LT - Emerald Campaign Sender Release Dispatcher (Staged) | 8UXlpoMJnQ229AuG | Active, hourly |
| LT - Email Event Ingest | ZrqFN8qLKO8eVHDc | Active, webhook |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | 0jDKgG8VvmfyORQn | Active, webhook |

### GHL Workflows (all published)

- **5 Event automations**: WL - Event - Emerald Email Event Ingest - {Opened,Clicked,Bounced,Complained,Unsubscribed} -- POST to n8n webhook /lt-email-event-ingest
- **Bridge**: WL - Seq - Enrollment Queue Entry (v13)
- **12 Emerald sequences**: WL - Seq - Cannabis Ads Emerald - {Executives, Marketing, Finance, Retail and Sales} {MSO, SSO}, including the applicable P2 variants
- **Supporting**: WL - Seq - Cannabis Ads - Variant A/B, WL - Seq - Stop on Booked/Reply/Closed (published version 17), WL - Micro - Email Inbound/Outbound/Open Counter

### Current State

- 4 senders: cameron@livetransparent.{com,co,agency,org}, warmup Week 1 cap 300/day each
- Safety buffer: 5% of cap (15/sender), remaining: 285/sender/day
- Backlog: ~16,672 unreleased pending in `Emerald_Campaign_Contacts` (dispatcher candidateLimit=250, runs hourly)
- Email events flowing to Email_Events table within 3 min
- **2026-08-20**: release-log single-row write bug fixed (published `d6737e68`); 73 `apollo_august2026` imports enrolled into Executives MSO (all confirmed in GHL, marked released + release-logged)

### Sender Capacity (Week 1, per-day)

| Sender | Cap | Safety (5%) | Remaining |
|--------|-----|-------------|-----------|
| cameron@livetransparent.com | 300 | 15 | 285 |
| cameron@livetransparent.co | 300 | 15 | 285 |
| cameron@livetransparent.agency | 300 | 15 | 285 |
| cameron@livetransparent.org | 300 | 15 | 285 |

**Total: ~1,140/day** (4 × 285). Warmup stages: Week 2 = 400/day, Week 3+ = 500/day.

### Fixes Applied (2026-07-21)

- **CRITICAL: In-flight capacity double-counting**: `Estimate InFlight Due Today` queried across 3 days (`CURRENT_DATE, -2d, -4d`), inflating `inFlightDueToday` to 285/sender and blocking all dispatches. Changed to `release_date = CURRENT_DATE` — counts only today's releases.
- **Known unfixed**: Dispatch code uses `doHttpRequest` wrapper (HTTP 400 risk in task-runner loops). Write Release Log uses template-literal SQL injection. These are low-risk for Emerald's current low volume but **must** be migrated to match DAN's patterns (`this.helpers.httpRequest` direct calls + parameterized queries) before scaling.

### Reply Suppression Repair (2026-07-26)

- `WL - Seq - Stop on Booked/Reply/Closed` (`3dd33ec4-d8c2-40c6-b72f-d1cba57b8c39`) had the correct Email reply trigger, but its removal action only targeted the legacy Variant A/B workflows. It did not remove contacts from the Emerald sequences.
- Added all 12 Emerald sequence workflows, including P2 variants, to the removal action through the GHL UI and published version 17.
- n8n `LT - Email Event Ingest` is reporting-only and does not suppress sequence enrollment.
- For the affected Christy Essex contact, removed `seq enrolled - emerald` and `seq emerald - executives sso` while preserving Warm/MQL state and the opportunity.

### Postgres Tables

| Table | Rows | Notes |
|-------|------|-------|
| Emerald_Campaign_Contacts | 20,238 | 16,672 pending, 3,566 released (incl. 73 `apollo_august2026` executives_mso released 2026-08-20) |
| Emerald_Release_Log | 16,154 | Dispatched contacts by sender |
| Email_Events | growing | From 5 GHL event automations |

## DAN Email Campaign -- Brands and Dispensaries (LIVE 2026-07-10, Backfilled 2026-07-13)

### Dispatcher

| Workflow | ID | Status |
|----------|----|--------|
| LT - DAN Campaign Sender Release Dispatcher (Staged) | toUG1yPDmFG48KEP | Active (dryRun=false), every 30 min |

**Pipeline**: Schedule Trigger -> Config -> Ensure Release Log Table -> Fetch DAN Candidates -> Dispatch + Queue (DryRun Safe) -> Only Queued (filter) -> Write Release Log (with Summary branch)

**Config**: dryRun=false, candidateLimit=85, senders=cameron@livetransparent.{com,co,agency,org} (round-robin), senderFieldName=marketing_sender_email

**Fixes applied 2026-07-14:**
- Schedule changed from hourly to every 30 min (was only hitting 600/day, needed 1200+)
- Added `await new Promise(r => setTimeout(r, 250))` between each contact's GHL API calls to prevent rate limiting (was seeing 20-40% `error_fetch_contact` on early runs)
- candidateLimit increased from 50 to 65 to compensate for ~10 recurring DNC contacts per run (BRĒZ, Teal Cannabis, AYR Wellness, Nova Farms — have `do not contact` in GHL but stale data in report_raw_ghl_contacts)

**Fixes applied 2026-07-15 (code/logic audit):**
- **Brand starvation**: Changed `ORDER BY epc.source_list, epc.id ASC` → `ORDER BY RANDOM()` so brands and dispensaries interleave proportionally instead of brands always filling the slot limit first
- **HTTP wrapper**: Removed `doHttpRequest` wrapper function and deprecated `$httpRequest` — all HTTP calls use `this.helpers.httpRequest(options)` directly
- **Sender rotation**: Added 4-sender pool (`cameron@livetransparent.{com,co,agency,org}`) with round-robin via `ci % senders.length`, matching Emerald's warmup pattern
- **Jitter**: Delay randomized to `250 + Math.random() * 250`ms to prevent thundering herd on GHL API recovery

**Fixes applied 2026-07-21 (full audit + hardening):**
- **CRITICAL: Release log crash on skipped_dnc**: `Only Queued` filter passed all non-summary items to `Write Release Log`, but `skipped_dnc` items lacked `enrollment_tag` which is `NOT NULL` in the table. Every daytime run errored on the INSERT. Tags WERE being applied to GHL, so emails were sending, but tracking was broken and the report showed `0 emails sent`.
  - Fix #1: Changed `Only Queued` filter from `status !== "summary"` to `status === "queued"` so only valid items reach the INSERT.
  - Fix #2: Expanded filter to `s !== "summary" && s !== "skipped_incomplete"` — passes `queued`, `skipped_dnc`, and all error items now that they carry `enrollment_tag`.
- **CRITICAL: SQL injection in Write Release Log**: Template-literal `.replace(/'/g, "''")` pattern replaced with parameterized `$1..$10` placeholders and `queryReplacement` array. Same anti-pattern previously fixed in LinkedIn Reply Backfill and Apollo Sheet First.
- **Self-healing pipeline**: `Dispatch + Queue` code now outputs `enrollment_tag`, `first_name`, `last_name`, `company_name` in ALL non-summary items (`skipped_dnc`, `error_fetch_contact`, `error_set_sender`, `error_add_tag`). This means every outcome — success or skip — gets tracked in `DAN_Release_Log`, permanently excluding that contact from future SQL candidate fetches. Pool self-cleans within a few dispatch cycles.
- **Candidate limit**: 65 → 85 to compensate for backfilled/skipped contacts, targeting higher throughput.

**Fixes applied 2026-08-20 (release-log single-row bug):**
- **CRITICAL: Only 1 release-log row persisted per run**: `Build SQL - Write Release Log` used `mode: runOnceForAllItems` with `$json` (first item only), so even when multiple contacts were queued/skipped, exactly 1 `DAN_Release_Log` row was inserted. Unlogged contacts were re-selected on the next run. Fixed by iterating `$input.all()` and setting `queryBatching: "independently"` on the Postgres node. Published `f8f29288-45d9-4f35-81a6-a60d2b54ad11` (versionId == activeVersionId). DAN pool is currently exhausted (last log entry 07-22), so the fix is dormant until candidates reappear.

**Candidate freshness (3-layer defense):**
1. **SQL dedup**: `NOT EXISTS (SELECT 1 FROM "DAN_Release_Log" r WHERE r.contact_id = epc.ghl_contact_id AND r.campaign = epc.source_list)` — any contact with a release log entry is excluded
2. **SQL tag filter**: `(lt.tags_raw IS NULL OR NOT (lt.tags_raw ILIKE '%seq enrolled - dan%'))` — stale report data catches already-enrolled contacts
3. **Live GHL check**: Per-contact `GET /contacts/{id}` + `isBlocked()` tag check — blocks contacts with `do not contact`, `do not nurture`, `unsubscribed`, `opted out`, `seq enrolled - dan`

All three layers feed into the release log: any contact that passes the SQL but gets live-skipped is recorded with `status: 'skipped_dnc'` (with enrollment_tag) and won't reappear.

**Dispatch performance (2026-07-21):**
- Max theoretical: 85 contacts × 24 runs/day = 2,040/day (Mon-Sat 8 AM ET to 5 PM PT window)
- After fix, first dispatch window will self-clean: previously-tagged contacts get release-logged as `skipped_dnc`, fresh contacts get `queued`
- Email events flow: GHL → n8n Email Event Ingest (`ZrqFN8qLKO8eVHDc`) → Postgres `Email_Events` table → Daily Rollups → Executive Summary
- Report dashboard (`emailsSent`/`emailsOpened`/`emailsClicked`) will populate as the release log backfills and daily rollups ingest

**Enrollment tags applied**:
- Brands: Enrollment Queue - DAN - Brands
- Dispensaries: Enrollment Queue - DAN - Dispensaries

**Deduplication**: Per-contact + per-campaign via DAN_Release_Log table (UNIQUE on contact_id, campaign). Every outcome (queued, skipped_dnc, errors) writes to the release log, permanently excluding the contact from future candidate fetches.

**DNC/unsubscribe protection** (three layers — see "Candidate freshness" above for full details):
1. SQL-level: filters report_raw_ghl_contacts.tags_raw for do not contact, do not nurture, unsubscribed, opted out, seq enrolled - dan
2. Per-contact live GHL check: GET /contacts/{id} before dispatching
3. Release log dedup: any contact with a DAN_Release_Log entry (any status) is excluded from SQL candidates

### ghl_contact_id Backfill (2026-07-13)

The import workflows (`LT - Brands Pool to Postgres + Sheets`, `LT - Dispensaries Pool to Postgres + Sheets`) set `ghl_contact_id = NULL`. The DAN dispatcher requires a non-null `ghl_contact_id`, so it found zero candidates despite contacts existing in GHL.

**Fix**: Backfilled 13,705 `ghl_contact_id` values from GHL export CSVs using three match passes:
1. Email match (lower+trim): +4,629
2. Phone match (digit-stripped): +5,691
3. Name+company match: +3,385

**Result**: 13,755 with IDs (3,645 brands / 10,110 dispensaries), 113 still missing (not in exports). **5,373 now eligible for DAN dispatch**.

**Export CSVs used** (delete after use):
- `Export_Contacts_brands pool_Jul_2026_5_24_AM.csv`
- `Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv`

### GHL Sequence Tags

| Tag | Purpose |
|-----|---------|
| Enrollment Queue - DAN - Brands | Triggers Brand email sequence |
| Enrollment Queue - DAN - Dispensaries | Triggers Dispensary email sequence |
| dan_seq_completed | Finished all 5 emails |
| dan_seq_no_engagement | No opens on emails 1-3 |
| dan_seq_replied_or_booked | Replied or booked meeting |

### GHL Workflows (all published)

- DAN - Brands Sequence (5d25147c-cd63-4c4f-ba49-a0e62c53ee0c)
- DAN - Dispensaries Sequence (ec24cbb8-bd0b-4e6e-8607-d93886a02034)
- DAN - Stop on Reply or Booked (d7ff2fc2-cdc2-4952-afa7-71cd9edfc490)

### Deck Download Automations

- WL - Micro - DAN Brand Deck Download -- trigger link bNK7txDSQJkvrgmmH9aZ -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- WL - Micro - DAN Dispensary Deck Download -- trigger link DDPOwxFCexuf3cYGOAPt -> tag/source metadata -> Warm; no SDR assignment before the Janvi qualification gate
- 3x open handling via WL - Micro - Email Open Counter + Assignment to Jason (42aa5940) is an engagement signal only; it must not independently assign an SDR or promote a Warm record

### GHL Email Folders

| Folder | ID |
|--------|-----|
| Brands | 6a4f6b06a3e9bfb4f9ebe8ad |
| Dispensaries | 6a4f6b128c6f614ebf8ba9e9 |

### Signature (all templates)

Cameron Karkut
Co-Founder / Head of Sales and Strategy
714-469-6406
LiveTransparent.com

## Reporting System

### Data Pipeline (4 Layers)

```
Raw Ingest → Attribution Bridge → Daily Rollups → Executive Summary API (GET /lt-report-executive-summary)
```

### Raw Ingest Workflows

| Workflow | ID | Schedule | Target Table |
|----------|----|----------|--------------|
| GHL Daily Leads Ingest | osIJOgBmWITF5Yuv | Every 60 min | `report_raw_ghl_contacts` |
| GHL Daily Sales Ingest | aYT5oHcgmBALzHy5 | Daily | `report_raw_ghl_opportunities` |
| GA4 Daily Ingest | 6pCSGzFmrMDFL5Yq | Daily (24h) | `report_raw_ga4_sessions` |
| GSC Daily Ingest | xHqmCC1vOeZ11gCd | Daily | `report_raw_gsc_queries` |
| GHL Daily Calls Ingest | SqNQ0BYaTdcqyt1l | Every 4 hr | `report_raw_ghl_calls` + `outcomes` |
| GHL Daily Appointments Ingest | yWZVSqEcjTbMT3kG | Daily | `report_raw_ghl_appointments` |
| GHL Daily Social Ingest | QZoqCaTwDhbym80O | Daily | `report_raw_ghl_social_posts` |

### GHL Leads Ingest Rate-Limit Guard

`LT - GHL Daily Leads Ingest` (`osIJOgBmWITF5Yuv`) uses direct `this.helpers.httpRequest` calls in `Fetch + Normalize Leads`. Do not restore the `doHttpRequest`/`$httpRequest` wrapper pattern. GHL contact pagination retries HTTP 429 responses up to four attempts, waits 500 ms between pages, and must send both `startAfter` and `startAfterId`. Repeated pages and missing/stalled cursors fail closed. Published version `d29b7af9-0b69-4fc7-a53c-c23dd24b0825` uses an atomic direct-`pg` transaction for contacts plus sync/watermark/health metadata. Controlled execution `742843` persisted 500/500 distinct contacts with healthy metadata.

### Bridge & Rollup Workflows

| Workflow | ID | Status |
|----------|----|--------|
| GA4 Traffic Rollup Bridge | 0P2AZcQYWYZjXbRi | Active |
| GSC Rollup Bridge | fOVBHwti9rC3qrLV | Active |
| Report Attribution Bridge | Y0TU7Il71JswxOBp | Active (daily, 90-day window) |
| Report Daily Rollups | EUeOiRttoVLQ9zF9 | Active (daily, 90-day backfill) |
| Report Pipeline Velocity | iFfwh0jpYUZoDhDR | Active |

### API & Frontend

| Workflow | ID | Status |
|----------|----|--------|
| Report Executive Summary API | Bukc0mgOD2r7V6ED | Active (webhook GET) |
| Report Outgoing Calls Detail | VXFHc8IrF9DDEEdj | Active (webhook GET; published version `d004556d-0b11-4a86-8827-f8f58a1eeee3`) |
| Report QA and Alerts | M5mXcDTFSko6EdHb | Active |
| Report Config Sync | aomO3Z4AXJIgEvvN | Active |
| Report Publish Refresh | 3gXztCnBEN6sGINb | Active |
| Report Postgres Bootstrap Apply | 3XHThUiUSNa4sTb9 | Active |
| LT - MQL Tag Event Ingest | U9oc2tZRsr4zq6IM | Active webhook (`POST /webhook/lt-mql-tag-event`, secret header; logs `mql` tag adds to `mql_tag_events`) |

### Executive Summary Runtime Recovery (2026-08-12)

- The report regressed to zeroes because the Executive Summary webhook returned an empty HTTP 200 after PostgreSQL rejected `v.report_date`; `report_stage_velocity_summary` stores `computed_at`, not `report_date`.
- Corrected the stage-velocity filter to `DATE(v.computed_at) BETWEEN $1::date AND $2::date`.
- The query then completed, but the response still exceeded nginx's 60-second proxy window because `Shape Response` synchronously called the Campaign Channel Summary endpoint even though the frontend already fetches that endpoint in parallel.
- Removed the redundant internal HTTP lookup and projected the existing `email_direct` totals/rates into the summary response. Final active version is `d177a923-da94-43ac-ac97-dbba1a664ab4` with `versionId == activeVersionId`.
- Verification: current 30-day summary returned HTTP 200 with a 33.7 KB body in 19.9 seconds; the prior equal-length period returned HTTP 200 with a 22.1 KB body in 12.3 seconds. Browser verification rendered 1,847 visits, 160 contacts, 4,368 opportunities, 5,743 email opens, and 362 email clicks.

### Executive Report Accuracy Audit (2026-08-25)

Full 30d cross-check of the Executive Summary, Campaign Channel Summary, and Outgoing Calls against source Postgres tables. Most figures were already exact (`emailsSent`/`opened`/`clicked`/`bounced`/`unsubscribed`, Vapi 50 calls by disposition + campaign, LinkedIn 44 invites/26 DMs/4 replies, Instagram 204 DMs, social posts/account stats, appointments 4, calls 828, Meta ads spend/clicks/impressions, MQL summary, SMS). Fixed these reporting bugs:

- **Raw pipeline/stage IDs exposed** — `pipelineDropoff` showed Partnership pipeline as `tQkFYrHjALgoLz6oq0uz`; `stageDropoff`/`stageVelocity`/`opportunityStageBreakdown` showed raw stage IDs (`91517911…`=Sales Outreach Qualified, `16fb26a2…`=Warm vapi_qualified, `67d47ef7…`=Warm New_Not Qualified, etc.). Added the full canonical pipeline/stage name CASE mappings (incl. Partnership Pipeline `tQkFYrHjALgoLz6oq0uz` and its 4 stages, plus `91517911`, `67d47ef7`, `0741e8b5`, `967292f9`, `16fb26a2`, `5112b5c8`, `268ed432`) to: Exec Summary `Build Query` (opportunity_snapshots CTE), Daily Rollups `Build Rollup SQL` (both tmp_report_opps and opp_transitions CASE blocks), and Pipeline Velocity `Build Velocity SQL` (timeline CTE). Re-ran the rollup and velocity workflows; stage tables now fully resolved. Exec Summary `stageVelocity` filter changed from `DATE(computed_at) BETWEEN window` to `computed_at = MAX(computed_at)` so it always shows the latest velocity compute (was going to return empty after a fresh compute lands outside the window).
- **Campaign Channel Partnership email undercount** — `Partnership emails email_sent` showed 59 (COUNT DISTINCT contacts) while the release log has 233 sent emails (59 contacts × 4 steps); Exec Summary correctly counted 233. Changed `email_sent` to `COUNT(*)` for DAN/Emerald/Partnership in the Campaign Channel Query so it matches the Exec Summary definition (release-log rows = emails sent). Now 2692 total on both.
- **Email rates were hardcoded `NULL`** — Exec Summary now computes cohort-based `emailOpenRate`/`emailClickRate`/`emailBounceRate` = unique recipients opened/clicked/bounced among the window send cohort / unique sent recipients (e.g. 44.6% / 11.4% / 4.7% for 30d). The `email_direct` CTE gained `emails_sent_unique`/`emails_opened_unique`/`emails_clicked_unique`/`emails_bounced_unique` (opens/clicks/bounces restricted to the window send cohort to avoid inflation from historical sends opening in-window). `emailRateBasis` = `unique_recipient_rates_over_window_sent_cohort`.
- **`salesQuality.topLossReason` mislabeled** — returned a stage name (e.g. "New") instead of a loss reason; renamed to `topLossStage` (GHL has no structured loss-reason field captured).
- **MQL tag ledger (2026-08-25)**: the business counts MQLs by the `mql` **tag being added** (e.g. past week), not by the Warm Qualified (MQL) stage. GHL does not expose tag-add timestamps and the hourly contact snapshot can't reconstruct them, so we built a forward-looking ledger: `mql_tag_events` table (UNIQUE `(contact_id, tag)`, first-add wins) + active workflow `LT - MQL Tag Event Ingest` (`U9oc2tZRsr4zq6IM`, POST `/webhook/lt-mql-tag-event`, requires `X-LT-MQL-Tag-Secret` from its Config node; 403 on unauthorized/missing contact, `duplicate` on re-add). **Pending operator step**: create the GHL automation `WL - MQL Tag Ledger` (Contact → Tag Added → `mql` → webhook POST with the secret header and `{"contact_id":"{{contact.id}}",...}` body) — runbook: `docs/sessions/2026-08-25-mql-tag-ledger.md`. Exec Summary `mqlSummary` now also returns `taggedMqlsTotal`/`taggedMqlsThisPeriod`/`taggedAsOfDate`/`tagBasis: mql_tag_events_ledger` (0 until events flow; forward-looking only). The 443 current `mql`-tagged contacts are noisy (mailer-daemon bounces, `not qualified`) — the ledger records whatever GHL fires.
- **Workflow version notes**: Exec Summary `Bukc0mgOD2r7V6ED` active `f49277bb-dc64-4855-933e-c38e53991bff`; Daily Rollups `EUeOiRttoVLQ9zF9` active `ddded785-2d31-4818-8ced-8a9c881a689f`; Pipeline Velocity `iFfwh0jpYUZoDhDR` active `43515531-dd9f-4462-bbe6-e58e321ab130`; Campaign Channel Summary `MvPLbUAN9IIQikxb` active `6ec148ff-6f1c-42b5-8b72-157d40d0a74a`; MQL Tag Event Ingest `U9oc2tZRsr4zq6IM` active `298be9d4-692b-4787-9bcb-a7f5de138e8c`. All `versionId == activeVersionId` after the REST PUT (PUT auto-publishes; the Query Summary postgres credential was restored to `pgAzUqpwOiGkGXzO` after the first PUT stripped it).

**Remaining data-source issues (need operator action, not logic fixes):**
- **GA4 credential is expired** — `LT - GA4 Daily Ingest` (`6pCSGzFmrMDFL5Yq`) has errored on every hourly run since 2026-08-14 (`The credential "Google Analytics account" needs to be reconnected`). `report_raw_ga4_sessions`/daily summary sessions freeze at 08-13, so `traffic` is UNDERCOUNTED (the 30d window's last ~13 days are missing). The `health` section already flags GA4 as stale. Reconnect the Google OAuth credential in n8n.
- **Pipeline Velocity schedule stopped firing** — active but 0 executions since ~08-07; data was stale until the manual re-run above. Verify the 24h Schedule Trigger is registering.
- **GSC ingest stale** since 08-07 (low volume: 1 click/41 impressions in window).
- **Sales Ingest snapshot gap 08-12…08-20** — no `report_raw_ghl_opportunities` snapshot rows those days (resumed 08-21), so stage-movement history for that span is absent.
- **`poolDistribution` always 0** — the GHL Leads Ingest snapshots only ~500 contacts, so pool tags (`brands_pool` 3k+, `dispensaries_pool` 7k+) never appear. Not a logic bug; data-coverage limitation.
- **`metaAttribution` empty / Meta leads 0** — no contacts in the 500-row snapshot carry Meta UTM attribution; genuine 0 given current data coverage.

### MQL / Company Sync

| Workflow | ID | Status |
|----------|----|--------|
| LT - Company MQL Google Sheets Sync | 9Y3Kedm768kkwwSV | Active (daily 6am ET) |

### Executive Report Data Sections (2026-07-21)

The `Report Executive Summary API` (`GET /webhook/lt-report-executive-summary?range=30d`) returns these top-level keys:

| Section | Source | Description |
|---------|--------|-------------|
| `traffic` / `leads` / `sales` | `report_daily_summary` | GA4 sessions, GHL contacts created, closed-won count |
| `summary` | `metric_summary` CTE | Full nested metrics: funnel rates, coverage, revenue, calls, timezone |
| `channelBreakdown` | `report_channel_daily_summary` | Top 8 channels by sessions/leads/opps |
| `utmBreakdown` | `report_utm_daily_summary` | Top 15 UTM source/medium/campaign combos |
| `metaAttribution` | `report_bridge_traffic_to_lead` | Meta (Facebook/Instagram) attribution |
| `pipelineDropoff` | `report_pipeline_daily_summary` | Per-pipeline stage counts + moved-in/moved-out |
| `stageDropoff` | `report_stage_daily_summary` | Top 10 stages by movement |
| `stageVelocity` | `report_stage_velocity_summary` | Avg days per stage |
| `opportunityStageBreakdown` | `report_raw_ghl_opportunities` | Active/worked/stage-mover counts per pipeline+stage |
| `socialPosts` | `report_raw_ghl_social_posts` | Post totals and engagement (likes/comments/shares/saves/reach/impressions; reads plural and singular keys from `insights` and preserved post payloads since 2026-08-04) |
| `health` | `report_source_health` | Source system health statuses |
| `callStatusBreakdown` | `report_raw_ghl_calls` | Top 10 call statuses by direction |
| `callOutcomeBreakdown` | `report_raw_ghl_call_outcomes` | Top 12 dispositions by direction |
| `appointments` | `report_raw_ghl_appointments` | Top 8 appointment statuses |
| **`emailsSent` / `emailsOpened` / `emailsClicked` / `emailsBounced`** | `report_daily_summary` + `Email_Events` + Release Logs | Email campaign metrics (added 2026-07-21) |
| **`emailOpenRate` / `emailClickRate` / `emailBounceRate`** | Computed from above | Email engagement rates (added 2026-07-21) |
| **`linkedinFunnel`** | `linkedin_connection_state` | ready→requested→connected→DM active→completed (added 2026-07-21) |
| **`vapiCampaignBreakdown`** | `voice_call_attempt` JOIN `voice_call_queue` | Per-campaign call totals, answered, qualified, booked (added 2026-07-21) |
| **Outgoing Call Detail** | `voice_call_attempt` JOIN `voice_call_queue` + latest `report_raw_ghl_contacts` snapshot | Seven completed days of paginated Vapi call rows with disposition, duration, contact ID/name fallback, campaign, first-attempt flag, and signed recording URL |
| **`vapiQueueDistribution`** | `voice_call_queue` (status=pending) | Pending queue by campaign (added 2026-07-21) |
| **`mqlSummary`** | `report_raw_ghl_opportunities` (stage IDs) + `mql_tag_events` (tag ledger) | Total MQLs (ever in Warm Qualified (MQL)), converted-to-SQL (also in Sales Outreach pipeline), current MQLs awaiting sales, entered/converted in the selected window, plus `taggedMqlsTotal`/`taggedMqlsThisPeriod` from the `mql` tag-add ledger |
| **`sqlContacts`** | `report_raw_ghl_contacts` (tag search) | Contacts with SQL tag (added 2026-07-21) |
| **`poolDistribution`** | `report_raw_ghl_contacts` (tag counts) | brands_pool, dispensaries_pool, vapi brand/dispensary (added 2026-07-21) |

### Stage Name Resolution (2026-07-21 Fix)

GHL stage names (`pipeline_stage_name`) are NULL in `report_raw_ghl_opportunities`. The report resolves stage names by falling back to `pipeline_stage_id` with a CASE mapping matching the Daily Rollups workflow. Pipeline names use the same ID-based resolution. This fixes `stage_movers` (was 0, now 93), `meetingsBooked`, and `closedWonCount` which previously depended on NULL stage name fields.

### report_daily_summary New Columns (2026-07-21)

| Column | Source |
|--------|--------|
| `emails_sent` | `DAN_Release_Log` + `Emerald_Release_Log` (release_date) |
| `emails_opened` | `Email_Events` (event_type='opened') |
| `emails_clicked` | `Email_Events` (event_type='clicked') |
| `emails_bounced` | `Email_Events` (event_type='bounced') |
| `emails_unsubscribed` | `Email_Events` (event_type='unsubscribed') |
| `emails_complained` | `Email_Events` (event_type='complained') |

### Executive Report Campaign Improvement Plan (2026-08-08)

The Executive Report at `https://reports.livetransparent.com` (build `2026-08-17-v26-social-reporting-accuracy`) has campaign/channel filters, separate Vapi filters, LinkedIn and Instagram ledger metrics, campaign drill-downs, comparison view, SMS delivery diagnostics, campaign opportunity counts, resolved GHL stage names, explicit Social Planner placement definitions, and responsive wide-table containment. The following remaining improvements complement the GHL Native Report:

**High Priority — Campaign Detail Page:**
1. **Per-campaign funnel metrics** — Each campaign row (DAN, Emerald, Partnership Emails, Partnership LinkedIn, Vapi Brand, Vapi Dispensary, SMS) should expand to show:
   - **Email campaigns**: Sent, delivered, opened, clicked, replied, bounced, unsubscribed with rates
   - **LinkedIn campaigns**: Invites sent, accepted, connected, DM sent, replied with rates
   - **Vapi campaigns**: Calls attempted, answered, voicemail, qualified, booked with rates
   - **SMS**: Sent, delivered, failed, replied with rates
2. **Campaign comparison table** — Side-by-side view of all active campaigns with key metrics and period-over-period deltas
3. **Partnership cross-channel view** — Combined email + LinkedIn funnel for partnership contacts showing overlap

**Medium Priority — Pipeline Integration:**
4. **Pipeline + Campaign bridge** — Show opportunities created per campaign source, with stage distribution and conversion rates
5. **Vapi-to-pipeline conversion** — Track Vapi qualified → MQL → Sales Outreach conversion rates
6. **LinkedIn-to-meeting rate** — Connected → replied → meeting booked funnel

**Low Priority — Data Quality:**
7. **Source health dashboard** — Per-campaign data freshness indicators (last ingest time, row counts, error rates)
8. **Campaign cohort analysis** — Time-to-first-action metrics per campaign (days to first open, days to first reply)
9. **SMS failure breakdown** — The GHL report shows 33/70 SMS failed (47%). Add a root-cause investigation widget (invalid numbers, rate limits, carrier blocks)

**Data Sources Available:**
| Data | Table/Workflow | Current Status |
|------|---------------|----------------|
| DAN + Emerald email metrics | `Email_Events`, `DAN_Release_Log`, `Emerald_Release_Log` | Already flowing into `report_daily_summary` |
| Partnership email + LinkedIn | `partnership_release_log`, `partnership_linkedin_connection_state`, `linkedin_activity_events` | Already in Campaign Channel Summary |
| Vapi call outcomes | `voice_call_attempt` JOIN `voice_call_queue` | Already in `vapiCampaignBreakdown` |
| SMS delivery | `SimpleTexting_Campaign_Event_Log` | Available via campaign_key routing |
| LinkedIn DM state | `linkedin_connection_state` | Already in `linkedinFunnel` |
| Per-campaign opportunity attribution | All opportunities have pipeline + tag affiliation | Needs bridge CTE added to Executive Summary API |

**Implementation Notes:**
- The `LT - Report Campaign Channel Summary` (`MvPLbUAN9IIQikxb`) endpoint already provides campaign-level aggregates; expand it with the detail fields listed above
- The frontend at `reports/embed/executive/index.html` already supports campaign/channel toggles; add a drill-down panel
- Add a `/webhook/lt-report-campaign-detail?campaign=<key>&range=<period>` endpoint that returns the per-campaign detail view
- For SMS, reconcile `SimpleTexting_Campaign_Event_Log` delivery/failure rates with the GHL-native SMS widget data (33/70 failure rate needs investigation)

### Voice Dialer Fix (2026-07-21)

`LT - Voice Agent V1 Outbound Dialer (Vapi)` (`r7UjWLndmc6EqEUW`): `GHL - Create Call Note` node now has `onError: continueRegularOutput`. Previously the dialer errored on every run because deleted GHL contact `AX3wfQNpRwm6DG0HgUE2` (still in `voice_call_queue`) caused a 400 on the note creation endpoint. Calls go out successfully; note failure is cosmetic.

## Partnership Marketing Pipeline (Infrastructure Live, Outbound Live 2026-07-31)

The original 131 content partnership contacts remain enrolled. A separate August 26 cohort added 404 new contacts and 427 actionable contacts to both partnership selectors. Two parallel sequences from Cameron's accounts: a 4-step email sequence and a 4-step LinkedIn DM cadence. All infrastructure isolated from DAN/Emerald (separate Postgres tables, workflows, GHL pipeline).

### Pipeline

- **GHL Pipeline**: `Partnership Pipeline` (`tQkFYrHjALgoLz6oq0uz`) — New Partner Lead → Contacted → Proposal Sent → Closed
- **Contacts**: original 131 contacts plus 404 new August 26 contacts; the 404 new contacts are identified by `august_26_partnership_contact`
- **Tags**: `partner_candidate_email`, `partner_candidate_linkedin`, `august_26_partnership_contact`, `partner_email_queued`, `partner_linkedin_requested`, `partner_email_sequence_completed`, `partner_replied`, `partner_not_interested`, `partner_do_not_contact`
- **GHL API key**: configured in the live dispatcher Config nodes and Reply Poller runtime; value intentionally omitted from documentation
- **14 contacts excluded** from original CSVs due to wrong company/email domain mismatches — awaiting corrections

### Email Templates

4 templates in GHL folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`):

| # | ID | Name |
|---|----|------|
| 1 | 6a6b8dfba3c113f06dee9e26 | Partnership - Email 1: Initial Outreach |
| 2 | 6a6b8e05264ebab67f776e9c | Partnership - Email 2: Follow Up |
| 3 | 6a6b8e06a3c113f06dee9ee6 | Partnership - Email 3: Value Proposition |
| 4 | 6a6b8e07a4bd9f4493fc536e | Partnership - Email 4: Breakup |

**Important**: The Email Dispatcher sends via `POST /conversations/messages` with inline HTML, not through GHL templates. The Code node HTML is the canonical message content; templates exist for open tracking and deliverability.

### Postgres Tables

| Table | Purpose |
|-------|---------|
| `partnership_linkedin_connection_state` | Mirrors `linkedin_connection_state` with `source_key = 'partnership'` |
| `partnership_release_log` | Tracks every sent email. UNIQUE on `(ghl_contact_id, email_step)`. |

### n8n Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - Partnership Email Dispatcher | Xshck23cKo1yXL9D | Active | 60/day, 11am ET Mon-Fri, 2-weekday intervals |
| LT - Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ | Active | 30 connection-request/day, 3pm CT Mon-Fri, state seeding + atomic claim |
| LT - Partnership LinkedIn DM Sequence | nspggypNF245xzeL | Active | 4-step DM, 2-weekday intervals |
| LT - Partnership Reply Handler | mRDw57IHtnQe4wOo | Active webhook | `/webhook/lt-partnership-reply` — tags `partner_replied`, creates opportunity, Slack alert, and writes a `replied` event to `Email_Events` |
| LT - Partnership Reply Poller | 0SQ7tTk03okegp9V | Active | Every 5 min — polls GHL for inbound email replies via `GET /conversations/search`, triggers Reply Handler |
| LT - Partnership Bulk Import | zmrYrUjVcyXaS7PJ | Active webhook | `/webhook/lt-partnership-bulk-import` |
| LT - Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn | Active webhook | Set LinkedIn URLs on LinkedIn-only contacts |

### LinkedIn Workflow Patches

3 existing LinkedIn workflows query `partnership_linkedin_connection_state` in addition to main table:

| Workflow | ID | Patch |
|----------|----|-------|
| LT - LinkedIn Connection Acceptance Checker | 3ttEvr5NMcQCS4Hp | SQL UNION + `source_table` routing |
| LT - LinkedIn Reply Backfill | QfJ2EZcc7lZwNgxj | UNION ALL + separate Update node |
| LT - LinkedIn Unipile New Messages | 7o5EBdvwAuIaWW7k | UNION ALL + routing + separate update node |

### Remaining

- **August 26 shared-email records**: resolve the two skipped shared-email groups before adding them to email outreach.
- **August 26 campaign monitoring**: monitor the next scheduled email and LinkedIn dispatcher runs; confirm release-log/state writes and verify that no Vapi selector tags appear on the cohort.

- **GHL Custom Report**: Partnership widgets are configured and verified in native report `6a67dce4a51a4360c60963a3`; MQL, owner, and stage-split widgets remain limited by the builder. PIT REST access cannot mutate widget layouts; do not guess undocumented report-builder endpoints.
- **Re-import 14 excluded contacts** after corrected company names provided
- **Outbound activation**: Approved and enabled 2026-07-31. Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence now use `defaultDryRun=false`; their published active versions are `6b7490a9-05d8-44e1-8f94-3c4427a7f969`, `29089175-1b37-4271-8b03-d4722b809692`, and `3bd0b759-4740-4e67-85ef-9540bf31c08e`. The dispatcher seeds 127 partnership `ready` state rows before queue fetch.
- **Live workflow verification 2026-07-31**: All 7 partnership workflows are active and published. Fixed the Email Dispatcher schedule to `0 11 * * 1-5` America/New_York, the LinkedIn Dispatcher schedule to `0 15 * * 1-5` America/Chicago, and the LinkedIn DM schedule to `0 12 * * 1-5` America/Chicago; prior interval definitions were firing hourly. Fixed the DM terminal completion scan to include `sequence_step <= 4` and corrected the shared LinkedIn Acceptance Checker state-upsert header. Safe manual smoke executions `281269` (email), `281268` (LinkedIn), and `281270` (DM) succeeded with outbound dry-run enabled.
- **Live outbound activation 2026-07-31**: Explicit user approval changed all three outbound `defaultDryRun` controls to `false`; all three drafts were published and verified with `versionId == activeVersionId`. Do not manually execute these workflows unless intentionally sending an additional live batch; scheduled runs now send real outreach.
- **Release-log single-row bug fixed 2026-08-20**: `Build SQL - Write Release Log` used `mode: runOnceForAllItems` with `$json` (first item only), so each run persisted exactly 1 `partnership_release_log` row. Actively manifesting: run `766371` (2026-08-19) sent 3 step-4 emails but logged only 1 (robert@herb.co), leaving the other 2 contacts unlogged for their step → duplicate re-send risk. Fixed by iterating `$input.all()` + `queryBatching: "independently"` on the Postgres node; published `2663f32b-4e45-4a5c-9b7f-e9db58ff9bc4` (versionId == activeVersionId). Functional test (`test_workflow` execution `769961`) confirmed 3 sent items → 3 release-log writes; the 3 live test rows were deleted afterward (`partnership_release_log` restored to 188).
- **Credential migration**: Move partnership GHL, Unipile, and state-upsert secrets out of Config/Code literals and rotate them after migration.
- **Reply Poller API gap resolved 2026-08-04**: `LT - Partnership Reply Poller` (`0SQ7tTk03okegp9V`) uses supported `GET /contacts/` pagination for active contacts and `GET /conversations/search` for inbound email reply lookup. It records lookup failures and fails closed instead of treating an ambiguous lookup as no reply. Smoke execution `522221` returned `checked: 58`, `replied: 0`, and `errors: []`; current published version is `736386a2-a7d2-434d-b9ba-72026e49c98b`.
- **Executive Report response-rate + social fixes (2026-08-04)**: User reported 1 partnership email reply and 1 partnership LinkedIn reply showing as 0 response rate, and incorrect LinkedIn/email data for the 3 campaigns. Four root causes fixed and published:
  1. **Reply Poller used `POST /conversations/search` (404)** — the correct endpoint is `GET /conversations/search` (200). Every poll run failed with `email_reply_lookup_failed` on all ~59 contacts, so the email reply was never detected. Fixed to GET with query params; smoke-tested execution `522241` returns `errors: []`. Published version `736386a2-a7d2-434d-b9ba-72026e49c98b`.
  2. **Reply Handler never wrote a reply event** — `LT - Partnership Reply Handler` (`mRDw57IHtnQe4wOo`) only tagged `partner_replied` + created an opportunity + Slack. Added a `Store Reply Event` Postgres node that inserts `event_type='replied'` into `Email_Events` (campaign_id `partnership`, workflow `LT - Partnership Reply Handler`). Published version `ad993fc2-4822-49bb-ad3e-f045a86b465d`.
  3. **Reply Backfill was one-shot** — `LT - LinkedIn Reply Backfill (Unipile)` (`QfJ2EZcc7lZwNgxj`) only selected rows where `dm_backfill_checked_at` was empty, so it ran once on 2026-07-31 (all partnership rows `idle`) and never re-checked. The `Select Pending Backfill Rows` query now also re-checks rows older than 6 hours with `dm_conversation_status <> 'active'`. Published version `0620c314-befb-4620-b23a-ad96b55cf4a0`.
  4. **Social insights key mismatch** — the Executive Summary `social_posts` CTE read `insights->>'likes'/'comments'/'shares'` (plural) but GHL stores `like`/`comment`/`share` (singular). The `Build Query` node now `COALESCE`s both. Verified: `totalLikes: 24, totalShares: 4, totalComments: 3` (was all 0). Published version `ff6fdc52-5eef-44b2-a50a-358cace45228`.
  - **Historical reply backfill completed 2026-08-04**: the verified Strider Peterson email reply was recorded in `Email_Events` with its actual GHL inbound timestamp (`2026-08-03T15:41:03Z`), and the verified Jaret Christopher LinkedIn reply was recorded in `linkedin_activity_events` at `2026-08-01T03:05:55Z`. The one-time helper workflows were executed successfully and archived. At that point, the selected-window Campaign Channel Summary showed `Partnership emails`: 59 sent, 1 reply, 1.69% response rate; and `Partnership LinkedIn`: 17 invites, 1 reply. The 2026-08-12 recovery added verified David Schachter and Gretchen Gailey replies, bringing the current Partnership LinkedIn reply total to 3.
  - **Account-level social statistics live (2026-08-17)**: the GHL PIT now authenticates `/social-media-posting/statistics`, so `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`) stores 7/30/90-day reach/impressions/likes/followers/posts windows daily and the Executive Summary returns them. Saves is not supplied by the statistics source and stays N/A. |

### Audit (2026-07-31)

Full audit passed:
- All 7 partnership workflows published and active (versionId == activeVersionId for all)
- 3 patched LinkedIn workflows verified: correct SQL UNION/UNION ALL queries, source_table routing, and dedicated partnership update nodes in Reply Backfill and New Messages
- Campaign Channel Summary (`MvPLbUAN9IIQikxb`) published with `partnership_release_log` UNION ALL in `email_sent` CTE (version `6641aa9a`). Endpoint confirmed returning "Partnership emails" row.
- Postgres tables `partnership_release_log` and `partnership_linkedin_connection_state` bootstrapped on live VPS; the LinkedIn state table has 127 seeded `ready` rows. The release log was empty during the initial dry-run audit; outbound is now live.
- Partnership candidate lookups use supported `GET /contacts/` pagination with explicit failure handling. LinkedIn state seeding checks existing IDs first; validation execution `278675` found 127 existing rows, seeded 0, and completed the dry-run request plan without outbound sends.
- Post-remediation scheduled executions `278513` (email), `278515` (LinkedIn), `278634` (DM), and `278611` (reply polling) succeeded with no error/crash executions after the fixes.
- Executive Report frontend deployed as build `2026-08-01-v12-campaign-breakdown` to reports.livetransparent.com. It directly fetches campaign channel data, renders LinkedIn Invites/Accepted/Replies, and displays social likes/comments/shares/saves/reach/impressions when supplied.
- GHL contacts verified: 98 `partner_candidate_email`, 127 `partner_candidate_linkedin` (94 overlap + 33 LinkedIn-only), 131 total. All assigned to Janvi.
- 4 email templates confirmed in folder `Partnership Email Campaign` (`6a6b768aa43d24a7ce1514f1`)
- Partnership Pipeline (`tQkFYrHjALgoLz6oq0uz`) with 4 stages confirmed in GHL
- No regressions detected — all existing DAN/Emerald/LinkedIn/Vapi workflows unaffected

## Other Live Systems

- **SimpleTexting**: Automated outbound remains paused. Step Runner (`dUyOfxllvkxZavaw`), Warmup Dispatcher (`dZQLlbTLkpE1843X`), Pool Dispatcher (`usxYXSuc4ahw40V3`), and Campaign Sequencer (`7mSiivR3NhtLIcNz`) are unpublished. Phone Backfill (`8hQKQi1PooYDFxNR`) is active but non-sending. The active send webhook defaults to dry-run; no sender schedule may be published and no live SMS may be sent without explicit approval. Inbound replies add `simpletext_replied`, remove `simpletext_ongoing`, mark campaign state `replied`, and suppress future sends; `simpletext_stop` remains the hard opt-out.
- **SimpleTexting GHL Conversations provider**: **LIVE** as of 2026-07-20. Separate GHL private app `LiveTransparent SimpleTexting SMS` with provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`). Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`. `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`) receives GHL outbound replies, validates provider ID, normalizes phone to E.164, checks `simpletext_stop` tag, reads GHL `attachments[]`, and sends via the idempotent send workflow (`gwaEpWDpTIwsafi8`) → SimpleTexting API. One HTTPS attachment selects `MMS_PREFERRED`; if SimpleTexting rejects it, one URL-bearing SMS fallback is attempted. Outbound campaign sends mirror into GHL Conversations via `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`). `simpletexting_conversation_map` table created in Postgres keyed by `(conversation_provider_id, alt_id)`. GHL Conversations is the primary operator inbox for SimpleTexting SMS; Slack alert for inbound replies is preserved. Multiple attachments are not supported in v1 and fail closed.
  - **2026-10-01 provider auth correction and verification:** Router config `internalSendHeaderValue` was aligned with the canonical send workflow and idempotent sender expectation. Router active version is `287678fd-a9e1-48c9-ab91-587368a3249a` (`versionId == activeVersionId`); read-back confirmed auth values match. The earlier Cameron attempt (`1071419`/`1071420`) was rejected before sending. The user then initiated a test: router `1071447` and idempotent sender `1071448` accepted it and returned provider message ID `6abd4452651df117957b9ee6`; delivery callback `1071449` matched that ID and wrote status `delivered`. No test or replay was initiated by the assistant.
  - **Unipile/Instagram**: Instagram DM Sequence (`iCnY6ccdHhfJg3sf`) remains **unpublished**. The real Instagram account is `F2UprZ8aQc6Qm9CYYWU6cg`, but the old workflow must not be republished because it used the LinkedIn account and old state model. Build the company-page workflow against the approved identity/state plan instead.
- **Instagram inbound bridge**: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) is active at `/webhook/lt-unipile-instagram-new-messages`. It normalizes Unipile Instagram inbound payloads, conservatively resolves an existing GHL contact before creating one, persists `instagram_conversation_map`, converts the stored agency OAuth token to a location token via `POST /oauth/locationToken`, and posts inbound messages into GHL Conversations under the `Instagram via Unipile` tab. Post-merge cleanup on 2026-07-16 repointed `instagram_conversation_map.id = 1` for chat `yx-R-9J6XdWaFpGOQd1JFA` to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`; the temporary duplicate `4V2oTmM7lWya3Nmtmp1Y` created during verification was deleted.
- **Social provider outbound router**: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`) is active at `/webhook/lt-social-provider-outbound`. Fixed 2026-07-16: POST webhook `responseMode` now uses `responseNode`, map tables are created defensively, payload message text is preserved through Postgres lookup, and Unipile send uses the working `api42.unipile.com:17256/api/v1` base. Canonical provider IDs are SMS-type additional custom conversation providers: `Instagram via Unipile` = `6a58a1193cdfc36997580a68` and `LinkedIn via Unipile` = `6a58a14ff3023bea3783c152`. Inbound message API must use `type: "Custom"` with `conversationProviderId` + `altId`; do not include `emailTo`/`emailFrom`/`subject` or dummy contact phone/email data. Deleted Email provider IDs `6a5893d11e9368345005f66e` and `6a5892b9107668309b3f85ac` must not be reused. Verified Instagram and LinkedIn inbound as `TYPE_CUSTOM_PROVIDER_SMS`; Instagram chat `yx-R-9J6XdWaFpGOQd1JFA` and LinkedIn chat `60Ult1SrWhOuvuZp1u7nXw` both map to canonical GHL contact `XZ4yChllGBdcsVxhFRDe`, with LinkedIn conversation `Ze8o3KbsrwuAXQ3KK5ge`. LinkedIn normalizer handles Unipile's form-encoded single-JSON-key webhook shape. Direct outbound router smoke tests after map repair passed: Instagram message `vjdEYSk9XD6R0I46oPWLwA`, LinkedIn message `C7I9944kWsSKutX2XhZEpA`.
- **Social provider bridge handoff**: Full build context, operator inbox runbook, monitoring gaps, and next steps for `LinkedIn via Unipile` + `Instagram via Unipile` GHL bidirectional messaging are in `docs/strategy/unipile-ghl-bidirectional-integration.md`. Read this before changing provider workflows.
- **Unipile/LinkedIn**: Active production path is dispatcher → acceptance/state sync → canonical DM sequence. Follower DM (`pq7XVajNFnnwMUTr`) is **unpublished**. Current published workflow inventory is documented in `Current Published Workflow Inventory` above. Guardrails block former-owner-branded copy.
- **LinkedIn invite copy**: n8n defaults say Transparent eCom. If LiveTransparent appears, check GHL-side body.message overrides first. Use [/] character class instead of \/ in regex literals to avoid SDK serialization corruption.
- **GHL warm intake/routing**, Apollo enrichment, Emerald and DAN email campaigns are active.
- **SMS campaign**: The canonical send webhook is `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`; template registry details are in `docs/outreach/sms_edited_templatekeys.md`. Send, provider-router, idempotency, and callback boundaries were hardened on 2026-08-17, with automatic SMS/MMS routing published on 2026-09-24. Registered provider callbacks use protected secret URLs because SimpleTexting cannot attach custom headers. Historical reconciliation restored 41 confirmed sends, terminalized 202 exhausted provider failures, quarantined 55 `send_unknown` rows, and replayed nothing. Keep sender schedules and legacy diagnostics inactive until an approved live provider test or natural traffic verifies the final boundary.

### Weekly Newsletter Pipeline (Built 2026-08-21 — LIVE; capacity retuned 2026-09-01)

Recurring weekly newsletter to all eligible GHL contacts, spread over Monday-Friday with 15-minute dispatcher runs from 07:00-13:00 LA, from 3 senders (`.co`, `.agency`, `.org` — NOT `.com`). Content lives in a GHL **Email Template** (NOT Campaigns) named `Newsletter <n> <Monday-date> (<subject>)`, pulled automatically at send time. Custom open/click/unsubscribe tracking is injected by the dispatcher into `newsletter_events` (GHL does NOT emit webhooks for `POST /conversations/messages` sends, so native GHL Campaign stats are unavailable on this path).

**DNS gate cleared:** go-live was completed on 2026-08-21. Do not revert the live dispatcher to dry-run or unpublished without explicit approval.

| Workflow | ID | Schedule | Status |
|---|---|---|---|
| LT - Newsletter Contact Prep | vvPdJMzBJMgcf5I9 | Mon 06:30 America/Los_Angeles (`30 6 * * 1`) | Active/published; weekday buckets 1-5 |
| LT - Newsletter Dispatcher | vru7OtCkDnPJkWt2 | Every 15 minutes, 07:00-13:00 LA (`*/15 7-13 * * 1-5`) | Active/published; `maxPerRun=250`, `maxPerSenderPerDay=2333`, live |
| LT - Newsletter Open Pixel | HkTQ9mqwHcpg3AIM | `GET /webhook/lt-newsletter-pixel` | **Active** |
| LT - Newsletter Click Track | HZ8ndNF4p80PrQjf | `GET /webhook/lt-newsletter-click` | **Active** |
| LT - Newsletter Unsubscribe | RvYusUSGB79K2e2k | `GET /webhook/lt-newsletter-unsub` | **Active** |

- **Eligibility (measured 2026-08-21):** 31,800 GHL contacts → 22,169 eligible (excludes no-email + `do not contact`/`do not nurture`, email-deduped). Per sender: ~7,390/week, ~1,478/day across five weekday buckets (under the live `maxPerSenderPerDay=2333` cap).
- **Dispatcher behavior:** `maxPerRun=250`, `maxPerSenderPerDay=2333` enforced from database sent counts in the current LA day, 400–600ms delay, 429/transient retry (4 attempts, 2/4/6s backoff), dry-run emits `planned` and never mutates DB. Template matcher accepts `builder` OR `html` types and fails closed if the week's template is missing.
- **Runner recovery (2026-09-01):** The custom JavaScript runner stays warm for 300 seconds with concurrency 10 and uses isolated `pg` plus `coolify-shared`. Full pinned graph test `837185` passed; controlled live send `838055` succeeded. August 31 sent 695 newsletters and recorded 39 HTTP 400 failures. Do not launch large single executions; use the 250-row cadence.
- **Tracking:** HMAC-signed URLs (`trackSecret` in Config nodes). Pixel `log_id`+`tok`, click `log_id|u`+`tok`, unsub `log_id`+`tok`. Tables `newsletter_send_log` (UNIQUE `(ghl_contact_id, week_key)`) + `newsletter_events` in the `postgres` DB.
- **Template:** ID `6a87716221922afe5eda9e6f` (`Newsletter 1 2026-08-24 (The real reason regulated ads get disapproved)`), proper logo applied 2026-08-21.
- **Deliverability audit + DND suppression (2026-09-09):** the ~2.7% GHL 400 rejection rate is `CONVERSATIONS_MSG_INVALID_EMAILTO` from contacts whose **Email DND suppression is active** (prior bounce/spam/unsubscribe) — not sender-related and not stale email. Dispatcher now retries `invalid_email` rejects once with the contact's current GHL email and marks terminal `invalid_email`, tagging the contact `newsletter_dnd_suppressed`; Prep's `blockedTags` now includes that tag so suppressed contacts are never re-queued. Dispatcher active `9774bd27-0e23-48da-a512-889ac49a6c61`; Prep active `8c3342d0-793d-4c22-9d5b-b8191aeeaea4` (Prep Config edited via direct n8n REST PUT; Set v3.4 node). Full record + remaining DKIM/DMARC/Postmaster steps: `docs/sessions/2026-09-09-newsletter-deliverability-audit-and-dnd-suppression.md`.
- **Full build + Go-Live runbook + verification:** `docs/sessions/2026-08-21-weekly-newsletter-pipeline.md`.

**Go-Live sequence (after DNS confirmed):** (1) re-check SPF/DMARC on `.co`/`.agency`/`.org` (one `v=spf1` and one `v=DMARC1` each; mxtoolbox recommended), (2) confirm this week's `Newsletter 1 <next-Monday> (<subject>)` exists in GHL Templates, (3) `publish_workflow` both prep + dispatcher, (4) flip dispatcher `defaultDryRun=false` via direct n8n REST PUT (Config Set node is unsafe via MCP pointer ops), (5) verify `versionId == activeVersionId` after each mutation, (6) monitor first run.

### SimpleTexting SMS via GHL — Bidirectional Provider (LIVE 2026-07-20)

GHL App: `LiveTransparent SimpleTexting SMS`, provider `SimpleTexting SMS` (`6a5b91913953360948dd59f1`), SMS-type, Custom Conversation Provider, Delivery URL: `https://automations.livetransparent.com/webhook/lt-simpletexting-provider-outbound`.

#### Workflows

| Workflow | ID | Status | Role |
|----------|----|--------|------|
| LT - SimpleTexting Provider Outbound Router | f4VoO1lBWkYRcQai | Active | Receives GHL outbound messages at `/webhook/lt-simpletexting-provider-outbound`, validates provider ID, normalizes phone to E.164, sends via idempotent boundary → SimpleTexting API. Skips business-hours guard for human replies. |
| LT - SimpleTexting Inbound Reply (Webhook) | i0pROHpFtN4LYR0Q | Active | Slack alert preserved. Now also posts inbound messages to GHL Conversations under `SimpleTexting SMS` via `type: "Custom"` + `conversationProviderId`. |
| LT - SimpleTexting SMS Send (Webhook, Staged) | Q3Ivnwe4z2Y3cD7A | Active | Mirrors successful outbound campaign sends into GHL Conversations under `SimpleTexting SMS`. |
| LT - SMS Idempotent Send | gwaEpWDpTIwsafi8 | Active | Canonical deduplicated SMS boundary. Called by outbound router and campaign send paths. |
| LT - SimpleTexting Campaign Phone Backfill | 8hQKQi1PooYDFxNR | Active | Non-sending phone-state repair; supports `awaiting_phone_refresh` and terminal `phone_unavailable`. |
| LT - SimpleTexting Campaign Step Runner | dUyOfxllvkxZavaw | Unpublished | Canonical scheduled sender candidate; dry-run guard enabled. |
| LT - SimpleTexting Warmup Dispatcher (Staged) | dZQLlbTLkpE1843X | Unpublished | Sender-capable; keep paused pending explicit approval. |
| LT - SimpleTexting Pool Dispatcher (Staged) | usxYXSuc4ahw40V3 | Unpublished | `sms_drip`, 10/run; dry-run/small-batch gate required. |
| LT - SimpleTexting Campaign Sequencer (Staged) | 7mSiivR3NhtLIcNz | Unpublished | 6-step flow; keep disabled until the canonical sender path is selected. |
| LT - SimpleTexting Delivery Events (Webhook) | AEi1VCzkLvaYFr4U | Active | Registered protected callback for delivery and non-delivery reports. |
| LT - SimpleTexting Unsubscribe Events (Webhook) | IyBKMkpYQ7pa0C8V | Active | Registered protected callback for unsubscribe reports. |

#### DB Table

`simpletexting_conversation_map` — UNIQUE on `(conversation_provider_id, alt_id)`, with indexes on `ghl_contact_id` and `normalized_phone`. Created on first outbound router execution.

#### Phone Format Contract

- Canonical phone: E.164, e.g. `+17144696406`.
- Conversation `altId`: `simpletexting:+17144696406`.
- `simpletexting_conversation_map.normalized_phone`: E.164 only.
- Outbound router has full E.164 normalization (`normalizePhoneE164`). AltId for inbound/outbound mirroring uses `simpletexting:+1<10-digit>` which works for US numbers. Full E.164 migration across delivery/unsubscribe workflows is deferred.
- `simpletext_replied` blocks automated sends; `simpletext_stop` blocks all sends including human GHL provider replies.

#### Guardrails

- Human replies bypass business-hours limits but still enforce STOP suppression.
- Outbound router validates `conversationProviderId` against `6a5b91913953360948dd59f1`.
- Idempotent send deduplicates on `(contact_id, workflow_id, message_hash)` per day.
- `simpletext_stop` tag check in outbound router blocks provider-originated sends to opted-out contacts.
- SMS Send mirroring runs on `onError: continueRegularOutput` so mirror failures don't block sends.
- Inbound reply still posts to Slack AND GHL Conversations; Slack alert preserved as secondary channel.
- A provider result is accepted only when the idempotent boundary confirms `sent` or `duplicate`; ambiguous responses fail closed.
- Controlled live validation still requires explicit approval. Safe pinned/dry-run tests are not proof of provider acceptance.

## Local Script And Archive Boundaries

- `local-scripts/` is an intentionally Git-ignored workspace for reusable operator-only helpers and machine-specific probes.
- `local-archive/n8n/` is an intentionally Git-ignored workspace for historical n8n exports, backups, and one-off patch inputs. Live n8n remains authoritative; these files are for audit/reference only and must not be redeployed without reconciliation.
- Keep reviewed, versioned automation and migration sources in `scripts/` and the retained `n8n/**/*.ts` blueprints; do not move them into the ignored archive merely because they contain code.
- Retained source blueprints must use environment placeholders and must not contain live PITs, API keys, webhook secrets, or provider tokens.

## Key Files

- repomix-output.md
- .env
- Project Status and Next Steps.md
- Export_Contacts_brands pool_Jul_2026_5_24_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_Dispensaries pool_Jul_2026_5_28_AM.csv (GHL export, used for DAN backfill)
- Export_Contacts_for fresh Linkedin connections_Jul_2026_2_16_AM.csv (GHL export, 14,987 contacts, used for LinkedIn dispatcher bulk feed 2026-07-13)
- GHL Live Transparent CRM/
- postgres/reporting-bootstrap.sql
- n8n/docker-compose.yml
- n8n/voice-agent/
- n8n/lt-linkedin-dispatcher.ts
- local-archive/n8n/workflows/
- local-scripts/suppress_linkedin_dms.py
- local-scripts/_vps_psql.py
- local-archive/n8n/
- scripts/n8n/fix_intake_poller.js
- reports/embed/executive/index.html
- reports/nginx.conf
- Backup of all n8n workflows/
- Project Specifications.md
- docs/campaigns/Vapi_Brand_Campaign.docx
- docs/campaigns/Vapi_Dispensary_Campaign.docx
- docs/strategy/unipile-ghl-bidirectional-integration.md
- docs/sessions/2026-08-21-weekly-newsletter-pipeline.md
- docs/dns-email-authentication-fix.md
- plan.md
- marketing/email-marketing/emerald-email-campaign/plan.md
- marketing/email-marketing/emerald-email-campaign/dispatcher-plan.md
- marketing/email-marketing/emerald-email-campaign/workflow-mapping.md
- Partnership Marketing/partnership_master.json
- Partnership Marketing/Content Partnerships - Email - Consolidated List.csv
- Partnership Marketing/Content Partnerships - Linkedln - Consolidated List.csv
- Partnership Marketing/Email Partnership Outreach Sequence.docx
- Partnership Marketing/Linkedln Partnership Outreach Sequence.docx
- scripts/partnerships/clean_partnership_data.py
- postgres/partnership-bootstrap.sql

## VPS SSH Access

- Host: 89.117.21.29 (hostname vmi3077218), user root
- SSH key: C:\Users\edmon\.ssh\local-upload (Ed25519, no passphrase, generated via Coolify)
- Permission fix: paramiko works directly. To use ssh.exe: icacls $keyPath /reset /inheritance:r /grant "$env:USERNAME:(R)"
- Reference keys on server: vps_caddy_key, vps_upload, id_ed25519_vps_whitefriar -- all passphrase-encrypted
- GHL-ready CSV files on n8n server: /home/node/.n8n-files/GHL_Ready_{Brands,Dispensaries}.csv
- Local copies: data/GHL_Ready_{Brands,Dispensaries}.csv

### Postgres Reference

- emerging_pool_contacts: 13,868 contacts (3,668 brands + 10,200 dispensaries)
  Fields: emerald_contact_id, source_list, first_name, last_name, primary_email, primary_phone, company_name, tags, ghl_contact_id, ghl_opportunity_id, ghl_import_status, raw_json (JSONB). UNIQUE on (emerald_contact_id, source_list).
  ghl_contact_id coverage: 12,639 filled (from GHL export CSVs), 1,229 null (not in exports).

## Former SDR Identity Cleanup (2026-07-07)

### What changed

- Message content and email signatures were changed from the former SDR identity to the active sales-owner identity in the customer-facing templates.
- Sender defaults and transfer wording were changed to the active sales-owner identity.
- All assistant system prompts updated

### What stayed the same (keys NOT changed)

- Legacy SMS payload aliases remain as internal compatibility identifiers because existing GHL automations reference them; they are not customer-facing implementation names.

### User IDs

- Jason Bornillo (jason@livetransparent.com): yU85G6kfhtW4vUtx3QE6
- Cameron Karkut (cameron@livetransparent.com): 03p5GatJBH7i9zjMaIzm
- Ed Cadorniga (ed@livetransparent.com): gePIeuHOEsAiPVA1mfOR

### GHL Status (2026-07-10)

- **Former-owner-branded LinkedIn invite resolved**: Workflow 25cd82a2 repointed from "Create Task" to n8n webhook with Cameron default message + send:true.
- **SMS failed-send workflows verified clean**: 41c6aecd and a99f96d9 -- no former-owner customer-facing messages.
- **GHL Sales Followup Emails and SMS** (f6b44e34): all Send email actions use the active sales-owner routing and sender defaults. The implementation should retain this neutral display name in future documentation.
- **Jason user ID found**: yU85G6kfhtW4vUtx3QE6 -- was agency-level, reassigned to sub-account.

## Tool & CLI Preferences

These CLI tools are installed and available via PATH. Prefer them over slower alternatives:

| Tool | Use instead of | Why |
|------|---------------|-----|
| rg | findstr, Select-String, grep | 10-100x faster text search, .gitignore-aware |
| fd | Get-ChildItem, dir | Blazing fast file finding by name/pattern |
| bat | cat, Get-Content | Syntax-highlighted file viewing with line numbers |
| jq | manual JSON parsing | Process API/LLM JSON responses inline |
| yq | manual YAML parsing | YAML equivalent of jq |
| xsv | CSV processing in Python/JS | Fast CSV search, slice, stats, join |
| delta | default git diff | Syntax-highlighted, side-by-side git diffs |
| fzf | scrolling through lists | Interactive fuzzy finder |
| zoxide | cd | Learns your navigation patterns, z <fragment> jumps anywhere |
| hyperfine | manual timing | Benchmark any command with statistical analysis |
| sd | sed, regex replaces | Simpler find-and-replace syntax |
| ast-grep | regex-only code search | Structural code search that understands syntax trees |
| eza | ls, dir | Modern ls with icons, colors, tree view |

## repomix-output.md Refresh — PAUSED BY ED

Do not run Repomix, `packlive`, or an equivalent pack operation until Ed explicitly reauthorizes it. Preserve the existing `repomix-output.md`. If Ed reauthorizes a refresh later, confirm the active workspace path before selecting the target.

## ✅ CURRENT 2026-10-05 Executive Report V1 weekly accuracy closeout

- V1 for `2026-09-27`–`2026-10-03` is updated and live at `/embed/executive-v1/`; default reporting timezone is `America/Los_Angeles` regardless of browser locale. Ed directed that GHL native data is authoritative.
- Band 4 statuses reconcile by SDR and Team. Current Team: 1,373 attempted, 1,003 answered, 147 busy, 137 no answer, 83 failed, 3 ringing. Prior Team: 1,356 / 1,087 / 124 / 94 / 51 / 0. Busy is corrected from the old double-counted 175. WoW percentages display; prior zero yields `—`.
- KPI methodology subtitles were removed. SQL attribution shows 2 of 4 attributed and 2 Unknown / Unattributed; combined MQL/SQL source coverage is 89%.
- Live browser/API verification passed. The exact-week health badge identifies `GHL native call snapshot: ready`; other ranges retain the general call-feed completeness status. Initial deployment stamp `2026-10-05-v1-band4` was superseded by the Oct 6 rolling-default build below. Legacy `/embed/executive/` preserved (`2026-08-17-v27-social-mql`). Handoff: [`docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md`](docs/sessions/2026-10-05-executive-report-v1-band4-refresh-handoff.md).
- **2026-10-06 rolling default:** when no explicit dates are supplied, V1 now defaults to the last completed Sunday–Saturday window computed in `America/Los_Angeles` (`Intl.DateTimeFormat` timezone override). On Oct 6 Manila it selected Sep 27–Oct 3; next week it will roll to Oct 4–10. User-specified URL dates remain fixed. Deployment `v3ud1lum1svamymuor21upog:executive-v1-20261006`, stamp `2026-10-06-v1-rolling-week`; verified live. Legacy report unchanged.
