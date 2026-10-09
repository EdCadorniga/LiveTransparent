# 2026-10-09 — Gambling / Cannabis Dispensaries / Peptides email templates + Peptides workflow next

> **Superseded 2026-10-09 (SMS mode):** every `dryRun=true` reference below is historical. All eight vertical campaign SMS Webhooks are now `dryRun=false` (96/96) after Ed's authorization — see the top of `AGENTS.md`. Peptides is Draft v14; Crypto is Published v48.

## Objective
Create the GHL email templates for the next three verticals (Gambling, Cannabis Dispensaries, Peptides) inside the folders Ed created, using the Alcohol Brands Campaign templates as the formatting reference, and without using browser tools. Then record the Peptides workflow as the next task.

## What was done (all via the `.env` GHL PIT; no browser)

### 15 email templates created and populated
Created via `POST /emails/builder` then `PATCH /emails/builder/{id}` with `editorType=html` + `editorContent` + `name`. (Create ignores the supplied name and returns HTTP 201; the PATCH sets the real name and body. Do not trust the create response for body/name proof.)

**Gambling — folder `6ac8e43939edc5e18c159cf8`**
| Template | GHL ID |
|---|---|
| Gambling Brands - Email 1 - The Opener | `6ac8e8dcf9707340c6901cb1` |
| Gambling Brands - Email 2 - How It Works | `6ac8e9079660fa02e854b290` |
| Gambling Brands - Email 3 - The Proof | `6ac8e90708741365d8940fb7` |
| Gambling Brands - Email 4 - The Direct Ask | `6ac8e90887cdcc5d6eb6b756` |
| Gambling Brands - Email 5 - The Breakup | `6ac8e909976a2a32d9f82346` |

**Peptides — folder `6ac8e41a39edc5e18c159aa5`**
| Template | GHL ID |
|---|---|
| Peptides Brands - Email 1 - The Opener | `6ac8e90a87cdcc5d6eb6b776` |
| Peptides Brands - Email 2 - How It Works | `6ac8e90ae6a28b9ad5ef77e7` |
| Peptides Brands - Email 3 - The Proof | `6ac8e90be6a28b9ad5ef77fb` |
| Peptides Brands - Email 4 - The Direct Ask | `6ac8e90c39edc5e18c160657` |
| Peptides Brands - Email 5 - The Breakup | `6ac8e90d9660fa02e854b389` |

**Cannabis Dispensaries — folder `6ac8e42a1ea8584cd7a514af`**
| Template | GHL ID |
|---|---|
| Cannabis Dispensaries - Email 1 - The Opener | `6ac8e90e4c92b27bd3d9fd53` |
| Cannabis Dispensaries - Email 2 - How It Works | `6ac8e90f9660fa02e854b3ed` |
| Cannabis Dispensaries - Email 3 - The Proof | `6ac8e90f87cdcc5d6eb6b835` |
| Cannabis Dispensaries - Email 4 - The Direct Ask | `6ac8e91039edc5e18c1606dd` |
| Cannabis Dispensaries - Email 5 - The Breakup | `6ac8e911976a2a32d9f82424` |

Local source copies (audit/reference, untracked): `New Campaigns October 2026/Email Templates/<Vertical>/<name>.html` plus `_manifest.json` and `_ghl_ids.json`.

### Content source and links
- Copy taken from each vertical's source PDF (`Gambling -`, `Cannabis Dispenseries -`, `Peptides - Multi Channel Outbound Sequence.pdf`), normalized to `{{contact.first_name}}` / `{{contact.company_name}}`.
- Booking: `https://api.leadconnectorhq.com/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=<slug>` with slug `gamblingsequence` / `peptidesequence` / `dispensariesequence`.
- Checklist resource (Email 1 & 2 only): `https://api.leadconnectorhq.com/widget/form/5rytqkbske3RlMfYHpMk?utm_source=<slug>`.
- Deck trigger links (verified live via `GET /links/`): Gambling `{{trigger_link.QK1BzLSt58DtGPdXci3m}}` ("Gambling_Deck_OutboundSequence"), Peptides `{{trigger_link.egfi10VJpDEoSmwcnxQn}}` ("Peptides_Deck_Outboundsequence"), Cannabis Dispensaries `{{trigger_link.nPzl7Eh9kT87aPqz8gIt}}` ("CannabisDispensery_Deck_OutboundSequence"). Email 5 (Breakup) uses only the deck trigger link, by design.

### Formatting decision (important)
Ed first chose the documented 12px / 600px-wrapper format, then explicitly directed a restyle of all 15 to **match the Alcohol Brands Campaign template exactly**. Final style applied and verified:
```
<!doctype html><html><body style="font-family:Arial,sans-serif;color:#111;font-size:14px;line-height:1.5">
  <p>Hi {{contact.first_name}},</p><p>&nbsp;</p><p>&nbsp;</p>
  ... body ...
  <p>&nbsp;</p><p>&nbsp;</p>
  <p>Best,<br>Cameron Karkut<br>Transparent eCom</p>
  <hr><p style="font-size:11px;color:#666">To stop receiving these emails, you can <a href="{{email.unsubscribe_link}}">unsubscribe here</a>.</p>
  </body></html>
```
- No `<head>`/`<title>`, no `<main>`/`max-width` wrapper, `Arial,sans-serif`, `#111`, `14px`, plain `<hr>`, "you can unsubscribe here" wording — matching Alcohol.
- This **supersedes the earlier "Arial 12px" template-spacing acceptance note for these three verticals**. It also differs from the already-built Crypto/Mushroom templates (12px / 600px wrapper). Reconcile whether Crypto/Mushroom/Nicotine should be restyled for consistency before launch.

### Verification performed
- Each of the 3 folders returns exactly 5 correctly-named templates (no leftover "New Template").
- Saved Firebase previews for all 15 re-fetched: 15/15 PASS on the Alcohol style line, greeting blank-block pattern, signature, footer wording, no wrapper, no 12px/#222, and valid `</body></html>`.
- Closing-tag note: the Alcohol templates' own Firebase **preview export** is inconsistent (`</body></html>>` on E1/E2/E4, `</body></html` on E3, `</body></html>` on E5). This is a preview-export artifact; the builder renders/normalizes proper closings. My 15 templates export a clean, consistent `</body></html>`. Not a defect.

## Peptides workflow — next task
Ed wants to work next on **Peptides Multi-Channel Outbound - Oct 2026** `11a70375-d401-45d1-86c1-13e538528748`.
- Live readback (PIT workflow list): status **draft**, version **1**, created `2026-10-09T07:27:03.389Z`, never updated. Fresh, untouched copy.
- It is a copy of the Alcohol source workflow `Alcohol Brands Multi-Channel Outbound - Oct 2026` `2e8c2d78-aaec-4591-9b53-b0715be8c4ce` (published v38).
- Sibling drafts created the same day: Cannabis Dispensaries `365ecf51-d700-4c2d-8058-df20ad523538` (v1), Gambling `4a238825-61d2-49e6-a3d0-4acb3a19c674` (v1), Crypto `0a79d683-4374-432d-bc64-6c8272540041` (v46).
- The GHL API does **not** expose workflow action bodies; `GET /workflows/{id}` returns 404. Full graph read/edit requires the authenticated GHL Builder (browser). Read-only list state was captured here.

### Ordered next-session work for `11a70375-…`
1. Open via authenticated Launchpad (`…/v2/location/Zwz4relUXVPxx8uohnjV/launchpad` → Automation → this workflow). Inventory the copied graph: entry trigger, gate, four sender branches, email actions, SMS webhooks, voicemail actions, waits/edges/exits. Do not assume counts — read them.
2. Convert gate/trigger/router to Peptides:
   - Entry tag → Peptides enroll tag (verify/create `lt_campaign_peptides_brands_oct_2026_enroll`).
   - Eligibility gate `Vertical = Peptides` (the `Vertical` dropdown already includes `Peptides`).
   - Sender router field → Peptides-specific sender field (verify/create `contact.lt_campaign_peptides_brands_oct_2026_sender_email`), four exact `.com/.co/.agency/.org` branches.
3. Map all email actions to the 5 new Peptides templates (IDs above): reselect the template in each Send Email action, accept GHL's confirmation, enable **Sync Edits to Template**, set the PDF subject, From Name `Cameron Karkut`, and the literal branch From Email. Read back template/subject/sender/sync per action.
4. Replace SMS payload copy with Peptides SMS 1/2/3 from the PDF; keep `dryRun=true` and retain the canonical SimpleTexting endpoint/auth/payload keys. Replace voicemail copy/asset as required.
5. Verify per-PDF cadence/waits: Day1 Email1, Day3 SMS1, Day5 Email2, Day7 VM1, Day11 Email3, Day13 SMS2, Day15 Email4, Day19 VM2, Day21 SMS3, Day23 Email5; include the PDF's 1-day wait before Day 1 Email 1 (the copied graph previously lacked it in the Crypto sibling).
6. Create/verify Peptides SMS snippets folder and campaign tags; reconcile the Peptides cohort and assign the campaign sender field before any entry-tag application.
7. Keep the workflow **Draft/unpublished** and **unenrolled**; no test sends, calls, or publication without explicit authorization.

### Open caveats
- **Claims need approval** before launch: Gambling/Cannabis Dispensaries/Peptides Email 3 carry the "40% higher approval rate / 16 months" claims; Peptides Email 3 adds the Florence Kirley / GuardLab testimonial. Taken verbatim from the source PDFs but not independently substantiated.
- This Peptides task departs from the documented Crypto-first sequence in `Project Status and Next Steps.md`; record accordingly.
- No emails were sent; no workflows were changed; no contacts were touched; nothing was committed.

## Safety gates in force
- Keep all four new vertical workflows Draft/unpublished and unenrolled.
- Keep all SMS Webhook actions at `dryRun=true`; no provider/test sends.
- Do not print or copy the GHL PIT or any secret.
- Do not edit the shared Alcohol/Nicotine/Mushroom/Crypto library templates to change a node's template; reselect templates in the target workflow instead.
- Preserve existing campaign state, enrolled contacts, and unrelated dirty worktree files.

## Peptides workflow `11a70375` — CONVERTED (2026-10-09, done)

- **Access method:** OpenCLI cannot reach or capture network from the cross-origin `workflow-builder` iframe (`opencli browser frames` = 0; `network` sees only the outer frame). Playwright **does** traverse the iframe, so the build was driven with the Playwright browser. The working graph is served in `workflowData.templates` of `GET backend.leadconnectorhq.com/workflow/Zwz4relUXVPxx8uohnjV/{workflowId}?includeScheduledPauseInfo=true` (the older `fileUrl` Firebase-Storage route is a fallback). **The Builder's global Save button issues a scriptable `PUT backend.leadconnectorhq.com/workflow/{loc}/{id}`** (per-action "Save action" alone only updates the local model; `version` increments on the PUT). The canvas also is not fit-to-view on load in this environment; node clicks required setting `.vue-flow__viewport` `transform: translate(10px,60px) scale(0.22)`.
- **Assets created via PIT** (location `Zwz4relUXVPxx8uohnjV`):
  - Tags (6): `lt_campaign_peptides_brands_oct_2026_enroll` `uzhO3USGruQrTnLq9noG`, `_active` `KM3XnGqRodbedXnuHqlb`, `_replied` `DyoXUy55sEFNdixmrUXH`, `_completed` `pL9cRYZyboIkTEkgsFTx`, `_suppressed` `3bEQJtKUcPpqBin3uEF3`, `_voicemail_consent_verified` `kFRHud75y8dzRGPODeAN`.
  - Sender field: **LT Campaign Peptides Brands Oct 2026 Sender Email** = `ADJQKqlJzjhnGiCpQQgg` (`contact.lt_campaign_peptides_brands_oct_2026_sender_email`).
- **Workflow `11a70375-d401-45d1-86c1-13e538528748` "Peptides Multi-Channel Outbound - Oct 2026" — Draft, version 13, 0 enrolled, unpublished.**
  - Trigger: `Entry - Peptides Brands Multichannel Oct 2026`, `contact_tag` → `tagsAdded == lt_campaign_peptides_brands_oct_2026_enroll` (trigger PUT verified).
  - Gate: `Eligibility gate - Peptides` / branch `Eligible - Peptides`, `Vertical == Peptides` (field `ODs8fBt5te5HEfSJ91pY`).
  - Router: `Sticky sender route - Peptides campaign field`, 4 branches `Cameron Peptides - .com/.co/.agency/.org` on field `ADJQKqlJzjhnGiCpQQgg` (values `cameron@livetransparent.{com,co,agency,org}`), None branch.
  - 20 email actions (4 senders × E1–E5), all with **Sync Edits to Template ON**, From Name `Cameron Karkut`, correct literal branch From Email, and Peptides subjects:
    - E1 `Quick question about your ad account` → `6ac8e90a87cdcc5d6eb6b776`
    - E2 `Why the account matters more than the creative` → `6ac8e90ae6a28b9ad5ef77e7`
    - E3 `Third agency in three years` → `6ac8e90be6a28b9ad5ef77fb`
    - E4 `30 minutes to keep your ads alive?` → `6ac8e90c39edc5e18c160657`
    - E5 `Should I close this out?` → `6ac8e90d9660fa02e854b389`
  - 12 SimpleTexting **Webhook** actions: canonical endpoint/`x-lt-simpletexting-key`/`Content-Type`/`source=sms` retained; message = Peptides **SMS 1/2/3** (SMS2 includes the `...utm_source=peptidesequence` booking URL); **`dryRun=true` on all 12** (were `false` in the Alcohol copy). No webhook invoked.
  - 8 ringless-voicemail actions: retained the shared `V3.mp3` asset (a pre-recorded file; the PDF script text cannot be applied to it). Consistent with the other verticals.
  - Waits: 28 × 2-day + 8 × 4-day (per branch `2/2/2/4/2/2/4/2/2`), unchanged from the Alcohol copy.
- **Initial-wait decision (resolved):** the ordered plan suggested adding the PDF's "Wait 1 day" before Day 1 Email 1 (as the Crypto sibling did), but the standing AGENTS.md vertical rule says not to. **Ed answered 2026-10-09: "Do not add the initial wait."** Day 1 Email 1 remains the first action; no structural change made.
- **Content caveat (unchanged):** Peptides Email 3 still carries the unsubstantiated "40% higher approval rate / 16 months" claim and the Florence Kirley / GuardLab testimonial. Hold for launch until substantiated or replaced.
- **Remaining (not done here):** Peptides **SMS snippets folder** (snippets are reference-only; delivery uses the SimpleTexting webhook, not native GHL SMS); Peptides **cohort reconciliation** (292-style source CSV → GHL exact-email/phone match) and **balanced sender-assignment** across `.com/.co/.agency/.org`; applying the **entry tag** to an eligible cohort; **publication/enrollment**. No sends, calls, tests, imports, tag writes, or publish occurred.
- **Access note for the next session:** prefer Playwright (not OpenCLI) for GHL Builder work; apply the fit transform before node clicks; global-Save after each batch; reload (list → search → open) to re-fetch the draft graph for verification.
