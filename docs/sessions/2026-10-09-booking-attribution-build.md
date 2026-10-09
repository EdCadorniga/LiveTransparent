# 2026-10-09 — Booking attribution: email Trigger Links + SMS redirect + ledger + views

## Objective
Attribute **bookings** (appointments) to the campaign that drove them — for email and SMS — and only count a booking when the contact actually booked. Email uses GHL **Trigger Links**; SMS uses a first-party **n8n redirect**. Both write one Postgres ledger; bookings are attributed by a report-time join (contact + 30-day window).

## Booking Trigger Links (GHL, location `Zwz4relUXVPxx8uohnjV`)
Created 2026-10-09 via `POST /links/`. `redirectTo` = booking widget + `?utm_source=<slug>&utm_medium=email&utm_campaign=<key>&utm_content=booking`.

| Vertical | Trigger link ID | Calendar | utm_source | utm_campaign |
|---|---|---|---|---|
| Alcohol | `rmFtop1jXctXpz4kJa1l` | WS6 | alcoholsequence | alcohol_brands_oct_2026 |
| Cannabis Brands | `jxGQ0wfSQ3S4UcQsPHCQ` | w6lg (Book 1:1 w/ Cameron) | cannabisbrandemail | cannabis_brands_oct_2026 |
| Nicotine | `FiHvJKjHuxfeg1arFRUj` | WS6 | nicotinesequence | nicotine_brands_oct_2026 |
| Mushroom | `TEkdL5xGyUxXeCmYmAnb` | WS6 | mushroomemailcampaign | mushroom_brands_oct_2026 |
| Crypto | `6fqPSWbqb3HVVZdlzk5N` | WS6 | cryptosequence | crypto_brands_oct_2026 |
| Cannabis Dispensaries | `DUh8OO86BA4xPgub1neh` | WS6 | dispensariesequence | cannabis_dispensaries_oct_2026 |
| Gambling | `ENEHOrItPwan00GnzyZZ` | WS6 | gamblingsequence | gambling_brands_oct_2026 |
| Peptides | `DYoKxOSoet48F4GHzPBE` | WS6 | peptidesequence | peptides_brands_oct_2026 |

WS6 = `WS6lacfQK2XOhqN7mRaF` (Book a demo); w6lg = `w6lgGxG2zOKyw24LTpjD`.

## GHL click workflow
`LT - Booking Link Click → n8n` (`44e3fa9b-e557-4099-bd74-b308d70f39bb`) — **published**. Trigger `Trigger link clicked` (unfiltered). Action = Webhook `POST https://automations.livetransparent.com/webhook/lt-booking-click` with custom data `event=booking_link_click`, `contact_id=Contact.ID`, `link_id=trigger link.id`, `link_name=trigger link.name`, header `Content-Type: application/json`.

## n8n workflows (n8n-lt)
- `LT - Booking Link Click Intake (Webhook)` (`1diZyFmTqWQUEny3`) active — `POST /webhook/lt-booking-click` → map `link_id`→vertical/campaign → insert `lt_booking_link_clicks`.
- `LT - Booking Link SMS Redirect (Webhook)` (`9HT13te9FalOtUZM`) active — `GET /webhook/lt-booking-sms?c=&v=&s=` → bot/prefetch filter → insert (`medium=sms`) → 307 to the calendar + UTMs.

## Postgres (report DB `postgres`)
- Table `lt_booking_link_clicks` (contact_id, link_id, link_name, vertical, utm_source, utm_campaign, medium, clicked_at, source_ip, user_agent).
- View `lt_booking_attribution` — last-touch campaign click within **30 days** before the booking; `attributed` boolean, `booked_via_*`, `days_click_to_book`.
- View `lt_booking_attribution_first` — first-touch within **90 days**; `first_via_*`, `attributed_first`.

## Email templates
32 vertical templates: booking URL → `{{trigger_link.<ID>}}` (7 Email-5 breakups have no booking URL; deck link only).

## SMS payloads
All 8 campaign workflows, 4 SMS-2 nodes each (32): booking URL → `https://automations.livetransparent.com/webhook/lt-booking-sms?c={{contact.id}}&v=<vertical>&s=sms2`.

## Executive Report V1
Facts API `oxYDg6XnRBKhl1Xd` `Build V1 Facts Query` now joins `lt_booking_attribution` (by `appointment_id`); `sqlBookingBreakdown` rows gain `campaign` and `attribution_model` (`last_touch_30d`). Active version `f69187f3-…`; verified 200 in ~99s.

## Audit (2026-10-09) — verified state
All read-only unless noted.
- **8 booking trigger links**: correct `redirectTo` (Cannabis Brands → `w6lg`, others WS6) and UTMs.
- **GHL `LT - Booking Link Click → n8n`**: published; webhook `POST …/lt-booking-click` with correct custom data + JSON header.
- **n8n `1diZyFmTqWQUEny3`, `9HT13te9FalOtUZM`, `oxYDg6XnRBKhl1Xd`**: all `active` + `published` (versionId == activeVersionId).
- **Email templates**: E1–E4 carry the correct `{{trigger_link.<ID>}}`; E5 carries the deck link; merges intact; no raw booking URLs left (Alcohol E1/E5 spot-checked).
- **Campaign workflow integrity**: 85 nodes each (20 email, 36 wait, 12 webhook, 8 voicemail, 9 if_else); email nodes untouched (subject/templateId/from/sync intact).
- **SMS nodes**: 4/4 tracked per workflow (after the fix below); endpoint/auth/keys/`dryRun=false` intact; only SMS-2 changed.
- **DB views**: 43 = 43 = 43 rows, 0 null `booked_at`, 0 null `contact_id` (1 row per appointment).
- **V1 30d**: `sqlBookingBreakdown` total **572 = funnel.sqls_entered 572** (no duplicate inflation); `campaign`/`attribution_model` present (null until clicks).

## Defect found + fixed (audit)
- **Draft-workflow reversion.** After the first API wiring, the SMS-2 nodes in **Cannabis Dispensaries** (`365ecf51-d700-4c2d-8058-df20ad523538`) and **Gambling** (`4a238825-61d2-49e6-a3d0-4acb3a19c674`) reverted to the raw booking URL. These are the only two **draft** workflows; the six **published** ones held the change. Re-wired both and re-verified `good=4` after a 30s delay (now v6 / v9). **Risk:** API step edits to *draft* GHL workflows may not persist — re-verify before publishing them.

## Notes / residual risks
- Pre-existing source slug inconsistency: Dispensaries email used `dispensariesequence`; the original SMS used `dispensariessequence`. Standardized on `dispensariesequence` (canonical PDF slug) via the redirect's `v=` param.
- Unverified until first send: GHL webhook body format (JSON vs form). The intake handles both.
- Attribution is contact-keyed (a booking on a different contact → untracked).
- Unfiltered trigger fires on every trigger-link click (deck/website/booking); n8n drops non-booking links (`ignored:true`).
- V1 surfaces the attributed campaign via `calendar_link_name`; the literal `campaign` column is not separately rendered in the UI yet.

## Next session (ordered)
1. Trigger one **email** click (controlled or natural) → confirm `lt_booking_link_clicks` gets a row with the right `link_id`/`vertical`/`medium=email` (validates the GHL→n8n payload format).
2. Trigger one **SMS-2** link click → confirm a `medium=sms` ledger row.
3. Re-verify the two **draft** workflows' SMS-2 wiring is still intact before publishing Dispensaries/Gambling.
4. Reconcile a **real booking** → confirm `lt_booking_attribution` attributes it and V1 `campaign` populates.
5. Optional: render the `campaign` column in the V1 UI; add a `first_touch_90d` breakdown using `lt_booking_attribution_first`.

## Safety gates (keep in force)
- Do not publish or enroll Dispensaries/Gambling without explicit approval.
- No sends/tests/calls without explicit approval.
- Never print/commit the GHL JWT, PIT, pg password, or n8n API key.
- Ledger/views are additive; do not modify shared Alcohol/Cannabis/Nicotine/Mushroom email templates except the already-applied booking-CTA token swap.
