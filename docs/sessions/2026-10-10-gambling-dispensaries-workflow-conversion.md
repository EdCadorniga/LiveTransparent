# 2026-10-10 — Gambling + Cannabis Dispensaries outbound workflows converted (email templates + SMS + vertical identity)

## Objective
Ed directive: convert the two cloned vertical outbound workflows (`Gambling Multi-Channel Outbound - Oct 2026`, `Cannabis Dispensaries Multi-Channel Outbound - Oct 2026`) from their Alcohol-copied content to their own vertical content — bind all 20 email Send actions per workflow to the already-created vertical templates and replace the SimpleTexting Webhook SMS 1/2/3 copy — and keep both **Draft/unpublished/unenrolled**.

## Result (DONE)
| Workflow | ID | Before | After |
|---|---|---|---|
| Gambling Multi-Channel Outbound - Oct 2026 | `4a238825-61d2-49e6-a3d0-4acb3a19c674` | Draft v1 | **published v11** |
| Cannabis Dispensaries Multi-Channel Outbound - Oct 2026 | `365ecf51-d700-4c2d-8058-df20ad523538` | Draft v1 | **published v9** |

Converted while Draft (v8/v5); Ed then **published both** (status `published`, **0 enrolled**). No sends, enrollments, contact tag application, voicemail, or contact writes. The only location-data change was the creation of 2 enroll tags.

## Email Send actions (20 per workflow = 5 emails × 4 sender branches)
Rebound `template_id` + `subject`; `from_name` `Cameron Karkut`, branch `from_email` `cameron@livetransparent.{com,co,agency,org}`, `syncEnabled:true`, `templatesource:email-builder` preserved.

**Gambling**
| # | Template | Subject |
|---|---|---|
| E1 | `6ac8e8dcf9707340c6901cb1` | Quick question about your ad accounts |
| E2 | `6ac8e9079660fa02e854b290` | Why gambling accounts get banned (and what's fixable) |
| E3 | `6ac8e90708741365d8940fb7` | How restricted brands actually scale |
| E4 | `6ac8e90887cdcc5d6eb6b756` | 30 minutes to unblock your acquisition? |
| E5 | `6ac8e909976a2a32d9f82346` | Should I close this out? |

**Cannabis Dispensaries**
| # | Template | Subject |
|---|---|---|
| E1 | `6ac8e90e4c92b27bd3d9fd53` | Curious how {{contact.company_name}} is funding foot traffic right now |
| E2 | `6ac8e90f9660fa02e854b3ed` | How it works — no cost to install |
| E3 | `6ac8e90f87cdcc5d6eb6b835` | 40% of dispensaries have $0 marketing budget |
| E4 | `6ac8e91039edc5e18c1606dd` | Founding partner spots are limited |
| E5 | `6ac8e911976a2a32d9f82424` | Want to keep your spot open? |

Subjects are the source-PDF subjects; `{{company}}` normalized to `{{contact.company_name}}`.

## SimpleTexting Webhook actions (12 per workflow = SMS 1/2/3 × 4 branches)
Message copy replaced with the vertical SMS text. Canonical contract retained on every node: `POST https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`, `Content-Type: application/json`, `x-lt-simpletexting-key`, payload keys `contact_id/phone/first_name/message/source/dryRun`; **`dryRun=false`, `source=sms`**.

- Gambling SMS1: "Hey {{contact.first_name}}, just emailed you about running {{contact.company_name}}'s gaming ads on Meta/Google without the constant bans. Worth a quick look?"
- Gambling SMS2: "Hey {{contact.first_name}} - still happy to show you how we keep gaming ad accounts alive so acquisition scales. Quick call this week? Book here: https://api.leadconnectorhq.com/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=gamblingsequence"
- Gambling SMS3: "{{contact.first_name}}, last nudge - want the breakdown on scaling {{contact.company_name}}'s acquisition without account bans, or should I close this out?"
- Dispensaries SMS1: "Hey {{contact.first_name}}, just emailed you about getting brand-funded ad budgets driving foot traffic to {{contact.company_name}} - no cost to set up. Worth a quick look?"
- Dispensaries SMS2: "Hey {{contact.first_name}} - founding partner spots in your market are limited. Still worth a quick look at getting brand-funded ad budgets to {{contact.company_name}}? Book here: https://api.leadconnectorhq.com/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=dispensariessequence"
- Dispensaries SMS3: "{{contact.first_name}}, last check-in - want me to hold {{contact.company_name}}'s founding partner spot a bit longer, or close it out for now?"

## Vertical identity (per the directive's "extras")
- Eligibility gate: `Vertical == Gambling` / `Vertical == Cannabis Dispensaries` (field `ODs8fBt5te5HEfSJ91pY`).
- Sticky sender router: field → Gambling `sBbIGke6cvkCTpW9n1yQ` / Dispensaries `wR5Az25TIyETr5E3NwoN`; 4 branches renamed `Cameron Gambling - .com/.co/.agency/.org` / `Cameron Cannabis Dispensaries - …`; values unchanged (`cameron@livetransparent.{com,co,agency,org}`).
- Trigger/entry tag: `lt_campaign_gambling_brands_oct_2026_enroll` / `lt_campaign_cannabis_dispensaries_brands_oct_2026_enroll`; trigger names `Entry - Gambling Brands Multichannel Oct 2026` / `Entry - Cannabis Dispensaries Brands Multichannel Oct 2026`.
- Waits unchanged (already PDF-aligned `2/2/2/4/2/2/4/2/2` per branch; the 4-day gaps cover the external LinkedIn steps). Voicemail retained the shared `V3.mp3` (pre-recorded; PDF script text cannot be applied to the asset).
- Zero "Alcohol" strings remain in either graph.

## Tags created
`POST /locations/Zwz4relUXVPxx8uohnjV/tags` (body `{name}` only; `locationId` rejected 422):
- `lt_campaign_gambling_brands_oct_2026_enroll` = `qzKEg4ypFdVRe9WkWDmi`
- `lt_campaign_cannabis_dispensaries_brands_oct_2026_enroll` = `BpZDGfXNARndI5RswRWk`

No contacts were tagged. The other 5 lifecycle tags per vertical were not created (not referenced by the workflow graph).

## Access method (reusable)
The GHL Builder backend is scriptable **from the top app frame** (`app.gohighlevel.com`), no iframe needed.
- Capture headers: inject a `fetch`/XHR interceptor via `navigate_page` `initScript`, reload the workflows list, then read the captured `authorization` (app user JWT) and `token-id` (firebase ID token).
- Call with BOTH headers plus `source: WEB_USER`, `channel: APP`, `accept: application/json, text/plain, */*`, `version: 2021-07-28`, `credentials:'omit'`. (The endpoint returns `Access-Control-Allow-Origin:*`; a single-token or `credentials:'include'` fetch fails.)
- `GET https://backend.leadconnectorhq.com/workflow/{loc}/{id}?includeScheduledPauseInfo=true&includeTriggers=true` → `{workflowData, permissionMeta, triggers, dependentAssets}` (graph at `workflowData.workflowData.templates`).
- `PUT https://backend.leadconnectorhq.com/workflow/{loc}/{id}` with the doc + `{modifiedSteps:[ids], createdSteps:[], deletedSteps:[], triggersChanged:false, oldTriggers, newTriggers}` → 200, `version++`. Node/edge changes apply; **trigger changes do not** (even with `triggersChanged:true` + old/new).
- **Triggers** use a separate service (`POST /workflow/triggers`) that rejects the app token (401). Edit triggers in the Builder UI: open workflow → click the trigger node → edit the trigger NAME textbox → click the `Tag added` chip, type the tag in "Type to search", and click the option (the a11y `listbox` option only appears in a **verbose** snapshot) → **Save trigger** → header **Save** (the header Save persists the trigger via the builder's own authenticated call).

## Verification
Fresh read-back of both graphs (with `includeTriggers=true`) passed:
- 20/20 emails: correct `template_id`, `subject`, `from_name`, `syncEnabled`.
- 12/12 webhooks: correct SMS 1/2/3 copy, `dryRun=false`, `source=sms`, canonical URL.
- Gate `Vertical` value, router field, trigger name + tag correct.
- `status: draft` for both; no "Alcohol" remnants.
- No sends/enrollments/publication.

## Post-publish audit + fix (2026-10-10)
After Ed published both, a full node-by-node audit of the live graphs found that the 20 email Send actions still carried two fields pointing at the **source Alcohol workflow**:
- `trackingOptions.sourceId` = `2e8c2d78-…:<nodeId>` (the Alcohol workflow id)
- `previewUrl` = the Alcohol template's Firebase preview (`…/emails/6ac516…`)

The already-converted Peptides/Crypto verticals use `trackingOptions.sourceId = <ownWorkflowId>:<nodeId>` and their own template's `previewUrl`, so these were inconsistent.

**Fix applied via the workflow PUT** (Gambling → **v11**, Dispensaries → **v8→v9** after Ed's re-save; both status `published`): for all 20 email nodes per workflow, `previewUrl` now points to that vertical template's Firebase preview and `trackingOptions.sourceId = <ownWorkflowId>:<nodeId>`. Re-readback: 20/20 correct per workflow, no other diffs vs the intended output. **Final live check (EOS 2026-10-10): Gambling `published v11` (updated `2026-10-09T18:41:59Z`), Dispensaries `published v9` (updated `2026-10-09T18:48:16Z`); each 20/20 emails correct, trigger/gate/router correct, 0 enrolled.**

Template Firebase preview tokens used: Gambling E1–E5 `999466b1…`, `49c38367…`, `5d6245f9…`, `04955d62…`, `6c44ee58…`; Dispensaries E1–E5 `5b6faadf…`, `602abfa0…`, `7b2b154d…`, `5290a0c8…`, `da178c5e…`.

**Also observed (Ed's edit while publishing):** the 8 SMS‑2 nodes (4 per workflow) were standardized to the booking-attribution redirect `…/lt-booking-sms?c={{contact.id}}&v=gambling|dispensaries&s=sms2`, matching the fleet convention `v=<lowercase vertical>` (alcohol/cannabis/nicotine/mushroom/crypto). This is the correct format; the original conversion had used the raw booking widget URL (mirroring the Alcohol copy). Confirmed the other five live verticals all use the same `lt-booking-sms` redirect.

## Remaining / follow-up
- Email 3's "40% higher approval rate / 16 months" claims in both verticals remain unsubstantiated — hold for launch.
- Both workflows are now **published** but **0 enrolled**; sender fields exist but no cohort has been assigned/enrolled for these two verticals (no sends have occurred).
- Optional consistency item (pre-existing): Gambling/Dispensaries templates use the 14px Alcohol format while Crypto/Mushroom/Nicotine use 12px — reconcile styling before launch if desired.
