# Cannabis Brands Multichannel Campaign — GHL Automation Plan

**Date:** 2026-10-03
**Status:** Campaign assets exist; entry trigger and eligibility gate saved in the existing unpublished GHL workflow; remaining channel sequence actions are held on readiness/gating checks.
**Source copy:** `New Campaigns October 2026/Cannabis Brands - Multi Channel Outbound Sequence.pdf`
**GHL location:** Live Transparent (`Zwz4relUXVPxx8uohnjV`), timezone `America/Los_Angeles`.

## Objective and boundary

Build one **GHL Automation workflow** as the authoritative record and orchestration container for the 23-day Cannabis Brands multichannel sequence. Keep the workflow in Draft until content, action mappings, sender readiness, suppression gates, and the operator-selected cohort are validated. The workflow is not to enroll contacts or send during this planning session.

This is a cross-channel automation, not a single GHL Marketing > Emails blast. Native GHL email actions should be used for the five email steps so those messages are sent and attributed through the GHL workflow. Custom channels (Classic LinkedIn requests, SimpleTexting SMS, Sales Navigator messages) must use explicit provider paths; those steps will be visible in GHL workflow history and should be mirrored/recorded in the relevant conversation and campaign state. Before launch, verify in a controlled internal test that GHL reports the five native email actions under this workflow and that the external-channel webhook outcomes can be reconciled to this workflow/contact. If Ed specifically requires the Marketing > Emails campaign report object rather than the GHL workflow execution/history, resolve that product requirement before build; a single Marketing Email Campaign does not represent the full multichannel cadence.

## Verified account facts

- GHL `Vertical` is contact custom field `ODs8fBt5te5HEfSJ91pY`, key `contact.vertical`, type `SINGLE_OPTIONS`; `Cannabis` is an allowed option (alongside Peptides, Gambling, Alcohol).
- GHL location profile sender is Cameron Karkut, `cameron@livetransparent.com`; location timezone is `America/Los_Angeles`.
- GHL's location response reports `defaultEmailService` empty. It does not prove that the requested From address is connected/usable for campaign mail. Verify email service, domain alignment, and From selection in GHL before launch.
- Current project notes say the Classic LinkedIn connection-request and automated LinkedIn DM workflows are unpublished; automated SimpleTexting sequence senders are also unpublished / dry-run guarded. This GHL draft cannot make those senders live by itself.
- Sales Navigator V2 bridge sends replies/follow-ups only on an existing mapped V2 chat. It does not start a conversation. A Classic LinkedIn acceptance is necessary but is not sufficient for a Sales Navigator send: a valid V2 chat/contact map must also exist.
- The existing GHL-to-SimpleTexting send boundary is `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`; `SimpleTexting SMS` is the custom contact field. Campaign automation must preserve its authentication, idempotency, opt-out, DND, response, delivery, and GHL mirror behavior.
- A GHL workflow `DRAFT - Cannabis Brands Multi-Channel Outbound - Oct 2026` (ID `5d1236a2-1b98-4b7f-9621-5d4f7749f377`) is saved, unpublished, and empty. Open it from the authenticated Automation → Workflows list; do not rely on a guessed deep link. Reconfirm empty/Draft before editing and reuse this ID.
- **Campaign assets created 2026-10-03:** GHL Email Templates folder `Cannabis Brands Multichannel - Oct 2026` (`6abfeed887cdcc5d6eee904e`) contains five saved plain-text templates: Email 1 `6abfef1496c6d799dbf5973e`; Email 2 `6abff09b9ed784b5df7a4e23`; Email 3 `6abff0ffc9468540aa8b3dd8`; Email 4 `6abff1710545fe92f6b4a8e0`; Email 5 `6abff1cc75b709136ba1079b`. Names and saved body content were read back; bodies contain explicit `[..._LINK]` placeholders that must be replaced before any send. Email subject lines are not part of these template records and must be configured in the native workflow actions. First-name merge fallback is `there`; company-name fallback still needs a safe value/verification.
- GHL Conversations > Snippets has a separate campaign folder `Cannabis Brands Multichannel - Oct 2026` (`4LOuqTbD59U3trQaSJQ7`) containing three text snippets: `Cannabis Brands - SMS 1 - The Nudge`, `Cannabis Brands - SMS 2 - Follow-up Bump`, and `Cannabis Brands - SMS 3 - Final Bump`. These are reusable copy references; the SimpleTexting webhook sends rendered message text and does not consume a GHL snippet ID. The exact-title/body root-level SMS 1 duplicate was deleted and read-back confirmed only the campaign-folder copy remains.
- Email templates and SMS snippets live in separate GHL libraries and therefore use separate campaign-named folders.

## Audience and enrollment design

Audience gate is an AND of the user-selected cohort and these campaign requirements:

1. Contact custom field `Vertical` equals exactly `Cannabis`.
2. Contact has neither `dispensaries_pool` nor `enrollment queue - dan - dispensaries`. Ed clarified that either tag should disqualify the contact, so both are excluded independently.
3. Contact is manually chosen/assigned by Ed or the campaign operator after the automation is validated. Do not select or enroll the whole audience automatically.
4. A usable email address is required for each email touch, but is not an enrollment requirement. SMS, voicemail, and LinkedIn are independently channel-gated; an ineligible or unavailable channel is recorded as skipped and does not block other eligible touches.

Use the campaign-specific tag `lt_campaign_cannabis_brands_oct_2026_enroll` as the controlled entry point. Ed selected a campaign-specific trigger rather than reusing an existing DAN/general cannabis enrollment tag. The tag is an enrollment control, not the audience qualification: GHL must re-check `Vertical = Cannabis` and absence of both exclusion tags at entry and immediately before each channel send. Prevent duplicate/re-entry for the same contact/campaign. The operator must be able to remove an enrollee before the first touch.

Recommended campaign lifecycle tags (proposed; confirm naming collision-free in GHL before creation):

- `lt_campaign_cannabis_brands_oct_2026_active`
- `lt_campaign_cannabis_brands_oct_2026_replied`
- `lt_campaign_cannabis_brands_oct_2026_completed`
- `lt_campaign_cannabis_brands_oct_2026_suppressed`

Add a campaign identifier to every native and external send record, such as `cannabis_brands_oct_2026`, so campaign attribution is explicit and reports can distinguish this sequence from other Cameron sends.

## Suppression and exit contract

Check gates at entry and immediately before every send. Fail closed on failed/ambiguous contact, reply-state, provider-map, DND, or sendability lookups.

- **Global stop / remove from all remaining campaign touches:** global DNC / `do not contact`, `do not nurture`, `simpletext_stop`, explicit campaign suppression, or any confirmed human inbound reply on any channel. A booked appointment is also a sequence exit. Write the campaign terminal state/tag before later scheduled branches can run.
- **Channel-specific DND:** do not send on a channel that is DND/opted-out. Email unsubscribe suppresses all subsequent campaign emails; SMS STOP / SMS DND suppresses every SMS. Keep other channels stopped when the contact also has global DNC or a human reply. Do not use a failed DND lookup as permission to send.
- **Replies:** wire inbound email, SimpleTexting, Classic LinkedIn, and Sales Navigator messages to a shared campaign reply/exit state. Confirm the exact GHL Customer Replied trigger semantics for custom LinkedIn providers and SimpleTexting before relying on it; keep channel-specific inbound webhook/state as a defense-in-depth signal. Human-initiated replies remain permitted.
- **Meeting booked:** exit immediately, leaving the existing appointment workflow to handle appointment confirmation/routing.
- **Provider/send outcome and cadence:** no blind replay. Record each touch as `sent`, `skipped`, `failed`, or `unknown`, keyed by campaign/contact/step. A confirmed send records provider ID and completes the step. An ineligible/unsupported channel is recorded as skipped and the cadence advances at its next scheduled offset. A definitive failure is terminal for that step unless a separately defined bounded retry is approved. An unknown result is held for reconciliation; do not retry or advance past that touch until reconciled. The later Day 1 email remains scheduled from enrollment regardless of Day 0 invite acceptance unless the operator explicitly chooses otherwise.
- **Campaign completion:** after Email 5 on Day 23, apply completed state and ensure no further campaign touches are queued. Newsletter eligibility is independent; confirm existing weekly newsletter eligibility and exclusions rather than adding a duplicate newsletter sender here. The campaign stops after Day 23 while the separate newsletter system may continue under its own eligibility/suppression rules. The three-month interval begins after Email 5; refreshed campaign re-entry after that interval remains an explicit, operator-reviewed action, not automatic re-enrollment by this workflow.

## Channel and sender design

### Email (Days 1, 5, 11, 15, 23)

- Use GHL native **Send Email** workflow actions for all five email touches. From name: Cameron Karkut; From email: `cameron@livetransparent.com` (configured identity; active email service/usable From remains unverified).
- The dedicated GHL Email Templates folder `Cannabis Brands Multichannel - Oct 2026` and five named plain-text email templates already exist (IDs above). The workflow actions should reference these templates, not duplicate unmanaged HTML inline. Keep them non-sending; unresolved URL placeholders, merge-field behavior, From identity, and claims remain blocked pending verification/approval.
- Before build acceptance, verify the connected email service supports this From identity and that each actual test send appears in the GHL workflow/contact activity with the expected campaign and From address. Do not route these five emails through an n8n HTTP send if native GHL campaign/workflow attribution is the requirement.
- Replace PDF link placeholders with verified HTTPS URLs: call booking, short deck, compliance checklist, Housing Works case study/read, and any link to the “2026 Meta & Google Ad Compliance Checklist.” Preserve source copy; do not invent or substitute assets.
- Use contact merge fields for first name/company; define a safe fallback for missing first name/company before launch. Encode HTML links and content safely.

### Classic LinkedIn connection request (Day 0)

- Send via the approved Classic Unipile account only. The copy in the PDF must be normalized to ASCII-only before the final API request, then runtime-validated byte-by-byte/codepoint-by-codepoint (`0x20`–`0x7E`, except intentional line breaks if supported). Normalize curly apostrophes/quotes/dashes to ASCII apostrophe/quote/hyphen; reject or strip all other non-ASCII characters. An apostrophe U+0027 is valid ASCII; never add backslashes to the final natural-language text to “escape” it.
- Plain ASCII-safe note:
  `Hi {{first_name}} - I work with cannabis brands on compliant Meta/Google ads and in-store attribution. Would love to connect.`
- Skip if no LinkedIn URL/provider identity, existing connection/request, prior reply, DNC, or a live suppression signal. Use a campaign-specific request/idempotency key so GHL retries cannot duplicate an invite.
- Current sender is unpublished. Build/reuse a campaign-specific request path that invokes an approved `n8n-lt` sender only after its request handler, identity matching, idempotency, suppression gate, and GHL audit/mirror behavior are reviewed. Do not reactivate the generic dispatcher as an implicit side effect.

### SMS via SimpleTexting (Days 3, 13, 21)

- Use existing canonical GHL → SimpleTexting webhook boundary, with campaign key `cannabis_brands_oct_2026`, step id, stable external ID, contact ID/phone, and Cameron-rendered text. Preserve the internal auth header; never place its value in the plan or UI copy.
- Three campaign-specific GHL Conversations snippets already exist in their own campaign-named Snippets folder (not the Email Templates folder). The SimpleTexting webhook does not consume snippet IDs; if these assets cannot be selected by the workflow send path, use canonical rendered copy in named workflow steps and document that limitation. Only send with valid phone, verified eligibility/consent, no SMS DND, no `simpletext_stop`, and no global DNC/reply/meeting/completed state. Confirm webhook response semantics and write back confirmed message ID/state; do not count a 202/ambiguous response as delivered.
- Plain-text copy comes from the PDF. The apostrophe in `{{company}}'s` is ASCII. Normalize to ASCII before dispatch; SMS can also be plain ASCII for predictable segment accounting. Count final rendered GSM-7/Unicode segments after personalization and link insertion.
- Automated SimpleTexting sequence sending is currently not launch-ready (scheduled senders unpublished/dry-run); build and validate this campaign path separately without enabling it during planning.

### GHL ringless voicemail drops (Days 7 and 19)

- User intends GHL to drop voicemails using its default Twilio number. The action must be a verified **ringless voicemail drop**, not a normal call, power dialer call, or voicemail-leave-on-no-answer action.
- Before building either step, inspect the GHL action catalog/account configuration and prove what the exact action does, the caller-ID/default number, the required recording/audio format, and how delivery/failure is exposed to the workflow. If true ringless drop is unavailable, leave both steps disabled and ask Ed before substituting another route.
- Require a valid/eligible phone, documented permission/eligibility for the ringless-voicemail method and jurisdiction, and no phone/channel DND; do not treat a call attempt as a voicemail drop. Replace each “number” placeholder with a verified Cameron callback number. Do not invoke actual call/drop actions in tests.

### Sales Navigator follow-ups (Days 9 and 17)

- Only attempt after the Classic LinkedIn acceptance checker has confirmed a first-degree relationship (`connected`) and before any reply/suppression/terminal state.
- Also require an existing Sales Navigator V2 chat/contact mapping to the exact GHL contact and a unique peer identity. No V2 chat creation, InMail, or unverified identity resolution in this sequence. If acceptance is missing or the V2 map is absent/ambiguous, skip that message; continue non-LinkedIn touches only if the contact has not replied or otherwise been suppressed.
- Send through the V2 chat bridge only; do not route these texts via the Classic DM sequence or the generic social-provider router. Never send until GHL-to-V2 bridge sending is specifically ready and published with approval.
- ASCII-only final payload, same strict validation as the connection note. Plain ASCII-normalized copy:
  - Day 9: `Hi {{first_name}} - reached out by email but figured LinkedIn might be easier. We help cannabis brands prove which dispensaries their ad spend actually drives sales in. Put together a short case study on it - happy to send if useful. Worth a quick chat?`
  - Day 17: `Hi {{first_name}} - circling back. If proving retail ROI is on {{company}}'s radar this quarter, I'd love 15 min to show you how we track ad spend to in-store sales. Book here - or reply and I'll work around you.`
- In addition to static verification, log the exact final rendered bytes and a checksum in the campaign event/audit record without logging secrets. Runtime should reject any character outside the allowed ASCII range before the Unipile HTTP call.

## Full timing and workflow sequence

Timing uses elapsed calendar-day offsets from successful campaign enrollment, measured in `America/Los_Angeles`; execute messages inside the next permitted Pacific weekday/business window. If a due time lands outside the window, queue for the next allowed window without compressing later steps. Skipped channel touches do not shift later offsets; an unresolved `unknown` touch pauses that contact's remaining cadence until reconciled.

| Day | Step | GHL/workflow action | Eligibility / exit behavior |
|---:|---|---|---|
| 0 | Classic LinkedIn connection request | Campaign request webhook to approved Unipile Classic sender | Contact/identity/reply/suppression/idempotency checks; record accepted provider result |
| 1 | Email 1 — The Opener | Native GHL Send Email | Email eligible; send from Cameron `.com`; stop on reply/DND/booked |
| 3 | SMS 1 — The Nudge | GHL webhook to SimpleTexting boundary | SMS eligible; status captured; STOP/DND blocks |
| 5 | Email 2 — How It Works | Native GHL Send Email | Same email gates; verified short-deck/checklist links |
| 7 | Voicemail 1 | Verified GHL ringless voicemail drop action | Disabled until ringless semantics/callback number/eligible phone verified |
| 9 | LinkedIn DM 1 | Sales Navigator V2 mapped-chat send | Require confirmed Classic acceptance **and** unique existing V2 chat map; otherwise skip |
| 11 | Email 3 — The Proof | Native GHL Send Email | Same gates; verify named proof/quote and links against approved source |
| 13 | SMS 2 — Follow-up Bump | GHL webhook to SimpleTexting boundary | SMS eligible and not suppressed |
| 15 | Email 4 — The Direct Ask | Native GHL Send Email | Same gates; verify booking link and guarantee claim before send |
| 17 | LinkedIn DM 2 | Sales Navigator V2 mapped-chat send | Acceptance + mapped chat + no reply; otherwise skip |
| 19 | Voicemail 2 | Verified GHL ringless voicemail drop action | Same voicemail gates; disabled if action/provider remains unverified |
| 21 | SMS 3 — Final Bump | GHL webhook to SimpleTexting boundary | Same SMS gates |
| 23 | Email 5 — The Breakup | Native GHL Send Email | Same email gates; then mark campaign completed and stop |
| 23+ | Exit / newsletter interval | End campaign workflow; newsletter remains its separate existing system | No campaign sends for 3 months; reviewed re-entry with refreshed copy only |

## Campaign record, audit trail, and workflow implementation shape

1. Retain the named GHL workflow as the authoritative multichannel orchestration record. GHL classifies workflow email sends under Marketing → Emails → Workflow Campaigns; this is not the standalone Email Campaign object. The workflow's entry trigger and audience gate are saved. It must show each remaining step and configured wait/action in the graph once safely built. The five email templates and three SMS snippets already exist in their respective campaign-named folders; the SimpleTexting path uses rendered copy, not snippet IDs.
2. The campaign-specific entry tag `lt_campaign_cannabis_brands_oct_2026_enroll` is created and assigned to no contacts; the workflow's Tag Added trigger uses it. Disable re-entry/duplicate enrollment. The saved entry gate checks `Vertical = Cannabis` and separately excludes `dispensaries_pool` and `enrollment queue - dan - dispensaries`. No other proposed lifecycle tags/custom fields have been created; do not tag/enroll a cohort during setup.
3. Use immediate stop/removal triggers or a paired GHL stop workflow for inbound reply, appointment booked, DND/global stop, unsubscribe/STOP, and manual campaign removal. If GHL cannot immediately remove a contact from a running workflow based on these events, implement a campaign-level stop-state check before every send; don't rely only on start-of-workflow filters.
4. Give every step a stable step key (`connect_0`, `email_1`, `sms_1`, etc.) and every send an idempotency key derived from campaign ID, GHL contact ID, and step key. Record result/status, channel, sender, provider message ID, timestamp, and skip/failure reason in GHL contact/workflow history and any existing external ledger. Do not store message secrets.
5. Native GHL emails must be sent by GHL actions and reference the campaign-specific email templates. Non-native sender actions must return structured sent/skipped/failed/unknown outcomes. Persist an atomic per-contact/per-step claim before attempting a send and reconcile unknown outcomes before another attempt. GHL native email actions have no idempotency guarantee established by this plan; prove a reliable pre-send claim/reconciliation boundary or explicitly accept and document residual duplicate-send risk before build acceptance.
6. Any further campaign custom fields or lifecycle tags remain uncreated. Check existing names and collisions before adding them; do not apply the enrollment tag to a live cohort during setup.

## Copy/asset review before build

Use the PDF as canonical text. Preserve non-LinkedIn copy unless owner review changes it. Required content replacements / checks:

- `{{first_name}}` and `{{company}}`: select the canonical GHL merge fields and safe fallbacks; test capitalization/HTML escaping and apostrophes in company names.
- “Book here/call here/Grab 15 min”: resolve to the approved Regulated Ads calendar URL (known calendar `SrtXcFVyea7pFl3nTiIK`) and verify Pacific Time display.
- “short deck,” “checklist,” and “quick read”: resolve to current approved public assets; never send literal placeholder text.
- Housing Works testimonial and statement, “2026 Meta & Google Ad Compliance Checklist,” no-minimum/no-cost review, and 30-day guarantee: owner must verify exact claim, attribution, and published supporting asset before the email is activated.
- Both voicemail scripts say “number” / “again, number”; replace with a verified Cameron callback number and calculate spoken duration. Do not create test calls.
- Verify email headers/sender address on an internal-only test before any audience send. The current `.com` sending identity is consistent with the documented LC Email auth result, but the location API has no default email service configured; recheck current GHL provider UI/verification at implementation time.

## Acceptance and rollout gates

### Non-sending validation

- Confirm GHL draft has one intended entry trigger, explicit enrollment filters, re-entry disabled, ordered waits/steps, and immediate exits.
- Preview an internal test contact with Vertical Cannabis and without the Dispensaries tag; confirm all required gates pass. Preview negative cases: non-Cannabis, missing Vertical, Dispensaries-tagged, each DND/opt-out, STOP, replied, booked, missing channel identity, missing V2 chat map, ambiguous send result. Do not issue outbound calls or messages as part of a preview.
- Test final rendered LinkedIn message text through an offline checker. Assert every outbound text byte is safe ASCII; assert any unsupported character rejects before provider call; verify apostrophe, em dash, curly quote, emoji, company apostrophe, and non-Latin first-name cases. For real send path, log sanitized final content + checksum; do not capture tokens or session data.
- Verify exact GHL step-to-campaign attribution for the five native email actions and verify each external webhook records the workflow/campaign/step/contact IDs with no send. Check that there is no parallel native SMS send when SimpleTexting is intended.
- Verify requested Cameron From identity, company default Twilio voice number, ringless semantics, and route behavior in account UI before those steps can be enabled.

### Launch / live test authorization

No user has authorized publication, cohort enrollment, sender activation, test email/SMS/LinkedIn message, or voicemail drop. Each is a separate production action. After Ed explicitly approves a narrowly scoped internal live test, use one internal recipient per channel (never a prospect) and validate GHL activity attribution and provider receipt. Keep the workflow unpublished until all per-channel gates are accepted and Ed separately authorizes publication and selected cohort enrollment.

## Open decisions / implementation blockers

1. **Resolved:** Ed confirmed both `dispensaries_pool` and `enrollment queue - dan - dispensaries` exclude the contact; the gate uses separate `Tags Does not include` segments.
2. **Resolved:** campaign-specific entry tag `lt_campaign_cannabis_brands_oct_2026_enroll` was collision-checked, created, and assigned to no contacts. The actual cohort remains manually selected later.
3. Timing decision is resolved: elapsed calendar-day offsets, with each due touch deferred to the next permitted Pacific weekday/business window.
4. Verify live native GHL email service/From config and email workflow activity attribution; location API showed `defaultEmailService` empty.
5. Verify the precise GHL ringless voicemail action and outbound Twilio default-number configuration; otherwise keep Day 7/19 disabled.
6. Resolve all PDF asset URLs and Cameron callback number; approve the Housing Works/guarantee claims.
7. Design/validate a campaign-scoped Classic invite dispatch call path while current LinkedIn outbound senders remain unpublished; do not re-enable the general dispatcher implicitly.
8. Resolve the V2 availability constraint: Sales Navigator messages require both accepted Classic connection state and a pre-existing unique V2 Sales Navigator chat map. Confirm whether the planned skip-on-missing-map behavior is approved.
9. Decide how a newsletter-exit cohort is kept untouched by this sequence for three months and who authorizes its refreshed re-entry. Existing newsletter automation is separate; do not clone or duplicate it.
10. Confirm workflow history/metrics satisfy the meaning of “recorded as a campaign in GHL.” If Marketing > Emails campaign reporting is explicitly required, design/test that separately without replacing the cross-channel GHL automation record.
11. Confirm documented recipient eligibility/consent requirements for SMS and ringless voicemail in each applicable jurisdiction and how the workflow will verify them before sending.

## Ordered next-session build checklist (initial version; superseded below)

1. Continue only in workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377`; its campaign tag trigger and Cannabis/dual-exclusion gate are saved.
2. Before adding channel actions, confirm GHL can keep each not-ready action reliably disabled or gated (email pending provider/From, unresolved claims/URLs, Classic LinkedIn, SimpleTexting, mapped-chat Sales Navigator, and voicemail). If the builder cannot represent an enforceable non-send gate, leave that channel action out and record the limitation.
3. Resolve email From/provider configuration, approved URLs/claim substantiation, voicemail semantics/route/eligibility, Classic campaign-scoped LinkedIn route, SimpleTexting readiness, V2 chat-map behavior, newsletter three-month handling, campaign attribution acceptance, and per-step idempotency/reconciliation design.
4. Add remaining waits/actions only with tested non-send gates and canonical assets; verify no action can transmit while blocked. Add audit state and error/unknown handling.
5. Validate in non-sending draft mode and offline LinkedIn ASCII tests. Confirm trigger/filter/action order and saved-state readback. Do not publish, enroll contacts, or send live tests without separate authorization.

## Initial session outcome (superseded in part by the dated continuation sections below)

- Review follow-up clarified channel gating, skipped/failed/unknown cadence behavior, newsletter separation and three-month clock, native-email idempotency acceptance, and SMS/voicemail eligibility checks.
- Created and verified the campaign-specific Email Templates folder plus all five named plain-text email templates, and the separate campaign-specific SMS snippets folder plus all three SMS snippets. Link placeholders remain intentionally unresolved; campaign claims and sender settings remain owner/implementation gates.
- During template creation, GHL initially persisted four email template names concatenated with their body text and did not save those body edits. They were repaired by editing the email-builder contenteditable within the builder frame, setting the title separately, and saving again. Final template inventory confirms all five names are now correct; spot checks confirm the repaired body content. The separate root-level SMS 1 duplicate was subsequently deleted after exact title/body and blank-folder confirmation (see continuation below).
- At the initial session checkpoint, the existing GHL workflow was Draft/empty and no trigger/action was saved. This was later superseded: the campaign-specific tag, trigger, and eligibility gate were saved in the continuation below. The workflow remains Draft/unpublished and 0 enrolled.
- Initial boundary: no contacts were enrolled, no messages/voicemails sent, no n8n workflow/sender changed/executed, no live test, and no commit. The later checkpoint adds one non-contact campaign tag and the draft trigger/gate; the no-enrollment/no-send boundary still holds.
- Worktree: modified `AGENTS.md` and `Project Status and Next Steps.md`, untracked October campaign input directory, and untracked plan are present. Preserve pre-existing changes and PDF. `git diff --check` passed; it reports only expected LF→CRLF working-copy warnings for the two modified Markdown handoff files.

## Ordered next-session build checklist

1. Read this plan and verify the live campaign folders/templates by name and parent ID; root-level duplicate SMS 1 snippet cleanup is complete.
2. Re-open the existing GHL draft from Automation → Workflows search/list, verify Draft/empty/0 enrollment, and continue in that exact workflow ID; direct deep links may 404 outside the authenticated SPA.
3. Resolve the exact `Dispensaries` tag, campaign enrollment/lifecycle naming collision checks, elapsed-calendar vs business-day wait convention, consent/eligibility verification, sender/email service, callback number, asset URLs, claims, and workflow attribution requirements.
4. Inspect whether the current five email templates can be selected as native GHL workflow Send Email assets; configure each PDF subject on its action and settle company-name fallback.
5. Build the entry, disqualification/suppression, and exit logic first; then add the guarded ordered channel steps and audit state. Keep all send-capable steps unavailable/disabled until the relevant implementation and launch gates are accepted.
6. Validate the draft with non-sending preview and read-only identity checks. Do not publish, enroll contacts, send tests, or reactivate paused senders without separate explicit approval.

## Historical continuation — readiness recheck and draft hold (2026-10-03; superseded by the later build continuation)

- Re-read this plan, `AGENTS.md`, and `Project Status and Next Steps.md`; reviewed the source PDF and verified the five email templates remain under folder `6abfeed887cdcc5d6eee904e`.
- Authenticated Automation → Workflows list/editor was opened through the location UI. The existing workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377` remains Draft, empty, 0 total/active enrolled; it is the correct workflow to reuse.
- Live read-only account checks reconfirmed location timezone `America/Los_Angeles`, Cameron Karkut / `cameron@livetransparent.com`, profile phone `+1 562-247-4600`, and `defaultEmailService` still empty. The configured sender identity is known, but an active/usable native workflow email provider and actual From selection are **not confirmed**.
- The `Vertical` custom field remains a single-select with `Cannabis`, `Peptides`, `Gambling`, and `Alcohol`. A broad contact query containing “dispensaries” returns records by contact text and does not prove which exclusion tag is canonical. Ed asked to specify exact tags; the exact exclusion and enrollment tag names are still pending.
- User selected elapsed calendar-day offsets (Day 0–23) with sends deferred to the next allowed Pacific weekday/business window; selected “your team” as the fallback personalization for missing company name; and allowed PDF claim/case-study text to remain only as blocked draft copy with unresolved links. The user requested unready LinkedIn, SMS, and voicemail steps be represented as clearly disabled/gated. Proposed voicemail callback number is the location profile number, but true ringless action semantics/default Twilio routing and phone eligibility are still unverified.
- No confirmed public URLs or substantiation/approval for the Housing Works testimonial, compliance/guarantee claims, deck, checklist, or quick-read assets were provided. The placeholders must remain blocked. No active Classic LinkedIn campaign-scoped request route; SimpleTexting campaign sender remains not launch-ready; Sales Navigator V2 requires an existing unique chat map and has no initiation capability; ringless-drop action and consent/eligibility remain unverified. Newsletter separation/three-month rule and campaign history attribution acceptance remain open.
- Attempted exact tag resolution from a generic GHL contact search is inconclusive. Ed is to provide the precise tag strings; do not encode a guess in workflow entry/exclusion logic or create campaign tags without collision checks and authorization.
- Located the duplicate in authenticated Conversations → Snippets: exact title/body match to SMS 1, but its Folder cell was blank (root-level); the canonical copy remains in `Cannabis Brands Multichannel - Oct 2026`. Deleted only the root-level duplicate through its row menu and confirmed the sole remaining match is in the campaign folder.
- **Build hold:** no trigger/action was saved to the campaign workflow. The exact exclusion and enrollment tags are required to configure a safe entry contract. Continue only after Ed supplies both exact values; then build the gated draft, not publish/activate it. No contact changes/enrollment, send, n8n work, or commit occurred.

## Historical continuation — handoff reconciliation before tag clarification (2026-10-03; superseded below)

- Re-read `AGENTS.md`, `Project Status and Next Steps.md`, this plan, and the source PDF. The PDF confirms the Day 0–23 cadence and the three-month newsletter interval; user-confirmed timing remains elapsed calendar days with the next permitted Pacific weekday/business window.
- Reconciled stale plan statements: the SMS 1 root duplicate was already deleted; the email and SMS assets already exist in separate libraries/folders; company fallback is “your team”; timing is settled; and the existing draft must be opened through the authenticated workflow list rather than a guessed deep link.
- Current repository state at review: `AGENTS.md` and `Project Status and Next Steps.md` are modified; the October source directory and this campaign plan are untracked. These are existing user/session changes and must be preserved. No commit was made.
- Correction after locating the persistent Playwright browser: authenticated GHL was available. Opened Automation → Workflows, searched the list for the exact campaign workflow name, and entered the matching row (no guessed deep link). The page title and URL identify workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377`; the editor shows Draft, Saved, and the empty-canvas prompt “Add first step,” with 0 enrolled/active shown in the list. This fresh read confirms the prior reported empty/Draft state. The connected n8n MCP advertised in this session is still `katwill`, not permitted `n8n-lt`, so no n8n call was made.
- The exact existing Dispensaries exclusion tag string and exact existing campaign enrollment tag string remain blocking inputs. Do not guess between similar tags, create tags, or write workflow entry logic before both are supplied and live-verified.
- No workflow/contact/tag/provider changes, enrollment, sends, live tests, n8n operations, or commit occurred during this documentation review. The draft remains unpublished; after Ed supplies both exact tag strings, verify their exact names/existence read-only, then save the gated draft only.

## Campaign audit continuation (2026-10-03)

- Fresh read-only asset audit: official GHL template listing returned the five expected plain-text templates under folder `6abfeed887cdcc5d6eee904e`, with matching names and IDs. The authenticated Snippets list shows the three expected campaign SMS snippets under folder `4LOuqTbD59U3trQaSJQ7`; no root-level SMS 1 duplicate remains.
- The live GHL location tag inventory reports 187 tags. Exact existing candidates observed include `dispensaries_pool`, `enrollment queue - dan - dispensaries`, `enrollment queue - cannabis ads`, and `seq enrolled - cannabis ads`. The inventory does not establish which Ed intends for this campaign's exclusion or enrollment trigger. There is no cannabis-brands-Oct-2026-specific enrollment tag in the inventory.
- Do not select/repurpose one of these possibly unrelated tags by inference. Since both tag semantics and exact strings remain unconfirmed, do not add a trigger or entry/filter actions; that would be unsafe and would violate the previously stated hold. Workflow remains Draft, Saved, and empty (`Add first step`); 0 total/active enrolled.
- No workflow, contact, tag, or provider changes; no enrollment or sends; no live test; no n8n operation; no commit.

## Campaign draft build continuation (2026-10-03)

- Ed clarified that either `dispensaries_pool` or `enrollment queue - dan - dispensaries` excludes a contact, and requested a campaign-specific enrollment trigger. The 187-tag inventory had no collision for `lt_campaign_cannabis_brands_oct_2026_enroll`.
- Created GHL tag `lt_campaign_cannabis_brands_oct_2026_enroll` in Settings → Tags with an operator-selected-cohort description; searched/read it back successfully. No contacts were assigned this tag.
- Reopened existing workflow `5d1236a2-1b98-4b7f-9621-5d4f7749f377` from Automation → Workflows. Added a Contact Tag → Tag added trigger for `lt_campaign_cannabis_brands_oct_2026_enroll`, named `Entry - Cannabis Brands Multichannel Oct 2026`.
- Added and saved an If/Else eligibility gate named `Eligibility gate - Cannabis; exclude dispensary cohorts`. Branch `Eligible - Cannabis, no dispensary exclusion tags` requires `Vertical is Cannabis` AND two distinct `Tags Does not include` conditions (one for each exclusion tag). The no-condition branch has no actions. Distinct AND segments are intentional: GHL's tag operator describes the condition as true if any selected tag is absent, so combining both tag names in one multi-select would not implement the requested “either tag excludes” rule.
- Workflow remains Draft/unpublished; no execution/test, contact enrollment, sends, or channel actions were added. The email provider/From, claim/link approvals, and unready channel implementations remain blocked. This is the saved entry/qualification scaffold, not the complete Day 0–23 sequence.
- Validation readback shows the workflow header `Saved` / `Draft`, trigger and eligibility gate on the canvas; list previously showed 0 enrolled/active. Recheck the workflow list once more before continuing with any additional changes. No n8n calls or commit.

## GHL campaign-object clarification (2026-10-03)

- Inspected Marketing → Emails → Campaigns in the authenticated GHL account. The page separates `Email Campaigns`, `Workflow Campaigns`, `Bulk Action Campaigns`, and `Email Sequences`.
- The artifact we have saved is an **Automation workflow**. GHL classifies email sends made by published workflow actions under **Workflow Campaigns**, not as a standalone **Email Campaign** object. The current draft has no email actions and is unpublished; searching the Workflow Campaigns list for “Cannabis Brands” returned no campaign, as expected.
- Thus the current artifact is a multichannel workflow/campaign scaffold, not currently a visible Campaign entry or native Email Campaign. If the requirement is specifically to have an item in the `Email Campaigns` category, that requires a distinct GHL Email Campaign artifact; it cannot represent the whole multichannel branching/wait sequence by itself and should not duplicate emails from the workflow.
- No Email Campaign object was created and no workflow publication/send was performed. Keep the workflow as the multichannel orchestration record unless Ed explicitly changes the requirement to add a separately coordinated Email Campaign component.
