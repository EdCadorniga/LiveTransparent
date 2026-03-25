# Cannabis Ads Sequence Enrollment (A/B 50-50) - Implementation Checklist

Last updated: `2026-03-24`

## 1) GHL Contact Fields
- [x] Create `Email Campaign` (Single line text).
- [x] Create `Last Marketing Email` (Single line text).
- [x] Create `Email Variant` (Single line text).
- [x] Create `Last Marketing Email Sent At` (Single line text or date/time, current setup kept as text).
- [x] Move fields into field group `Campaign Details` (completed manually in GHL UI).
- [x] Create `marketing_sender_email` (contact custom field).
- [ ] Optional but recommended: create `Sender Locked At` (Date/Time).

## 2) GHL Tags
- [x] `Seq Enrolled - Cannabis Ads`
- [x] `Seq Variant A`
- [x] `Seq Variant B`
- [x] `meeting booked`
- [x] `Enrollment Queue - Cannabis Ads`
- [x] `Do Not Nurture`

## 3) n8n Intake Flows (Website)
- [x] Hero intake workflow updated: `Website Lead Intake from Hero form`.
- [x] Footer intake workflow updated: `Website Lead Intake from Footer Form`.
- [x] Both now add tags after successful upsert/update:
- [x] `Warm Website`
- [x] `Enrollment Queue - Cannabis Ads`
- [x] Webhook paths verified unchanged:
- [x] `lt-form-demo-intake`
- [x] `lt-form-footer-intake`
- [ ] Set `defaultDryRun=false` in live workflows when ready for production writes without passing `dryRun=false` manually.

## 4) Enrollment Routing (A/B Split)
- [x] Decision locked: use **GHL Randomizer** for 50/50 split (not n8n hash router).
- [x] n8n router workflows retired from active use (deleted after rollback hold window on `2026-02-26`):
- [x] `WL - Seq Enrollment Router - Cannabis Ads (Workflow IDs Live)` (`UJnHFPxSdTcsK9iW`) - deleted
- [x] `WL - Seq Enrollment Router - Cannabis Ads` (`L5Cpe7ZdUgauQcF7`) - deleted
- [ ] Build/verify GHL workflow `WL - Seq Enrollment Router - Cannabis Ads`.
- [ ] Entry filter/guard checks:
- [ ] Has `Enrollment Queue - Cannabis Ads`
- [ ] Does not have `Seq Enrolled - Cannabis Ads`
- [ ] Does not have `meeting booked`
- [ ] Does not have `Do Not Nurture`
- [ ] DND Enabled Channels does not include `Email`
- [ ] Has non-empty `marketing_sender_email`
- [ ] Randomizer split 50/50 to Variant A and Variant B.
- [ ] In each branch, set:
- [ ] `Email Campaign = Cannabis Ads Sequence`
- [ ] `Email Variant = A` or `B`
- [ ] Add `Seq Variant A` or `Seq Variant B`
- [ ] Add `Seq Enrolled - Cannabis Ads`
- [ ] Add sender audit tag from `marketing_sender_email` (or sender-specific static tag if dynamic tag formatting is unavailable).
- [ ] Remove `Enrollment Queue - Cannabis Ads`
- [ ] Enroll to corresponding sequence workflow (A or B).

## 5) Sequence Workflows (A and B)
- [x] Sequence workflows created in GHL:
- [x] A: `https://app.gohighlevel.com/location/Zwz4relUXVPxx8uohnjV/workflow/716d5fd7-09ef-4535-855b-70a7a73e731b`
- [x] B: `https://app.gohighlevel.com/location/Zwz4relUXVPxx8uohnjV/workflow/1ea5efa6-652b-4213-bf26-f32ff7275d71/advanced-canvas`
- [x] Delay pattern selected: `2d, 2d, 3d, 4d`.
- [x] `From Email` now configured as `{{contact.marketing_sender_email}}` in workflow email actions (verify every send step in both A and B).
- [ ] Confirm each email step updates:
- [ ] `Last Marketing Email`
- [ ] `Last Marketing Email Sent At`
- [ ] Dynamic sender validation pass:
- [ ] Test contact with `marketing_sender_email=<verified_sender_1>`
- [ ] Confirm all sent steps use that sender
- [ ] Test contact with `marketing_sender_email=<verified_sender_2>` once second sender is added
- [ ] Confirm no fallback to personal sender

## 6) Stop/Suppression Automation
- [x] Build/verify `WL - Seq - Stop on Booked/Reply/Closed`.
- [ ] Trigger paths to include:
- [x] Appointment booked (`Regulated Ads On Social/Search` only)
- [ ] Customer replied (email)
- [ ] Opportunity `Closed Won`
- [ ] Opportunity `Closed Lost`
- [ ] Tag added `Do Not Nurture`
- [ ] Actions on all trigger paths:
- [x] Add `meeting booked` only on the qualifying regulated ads booking path
- [ ] Remove from sequence workflow A
- [ ] Remove from sequence workflow B
- [x] Historical cleanup completed on `2026-03-24`: invalid `meeting booked` tags were removed from non-qualifying bookings and unrelated contacts

## 7) Sender Warm-Up Controls
- [x] Implement controlled daily enrollment cap using n8n dispatcher `NTpQnMrpjzusPXHX` (automated release model).
- [x] Week 1 cap locked: `50/day` per sender.
- [x] Ramp locked: Week 2 `75/day` per sender, Week 3+ `100/day` per sender.
- [x] Cap interpretation locked: cap is total outbound emails/day per sender (not just new enrollments).
- [x] Global dispatch window: `Mon-Sat`, `8:00 AM ET` to `5:00 PM PT`.
- [x] Sunday policy: summary-only execution, no dispatch.
- [x] Per-contact local-hour gate enabled (`8:00 AM-4:59 PM`, timezone then state/country fallback).
- [x] Timezone fallback mapping now supports full US state names and full CA province names (in addition to code-based values).
- [x] Upsert throttling enabled: `200ms` delay before each `/contacts/upsert` call.
- [x] Retry model confirmed: deferred/failed contacts are retried next dispatcher runs because only `queued` rows are logged to `ColdOutreach_Release_Log`.
- [x] Per-sender allowance formula in automation:
- [x] `remaining = cap - in_flight_sends_today - safety_buffer`
- [x] Safety buffer applied: `max(10% of cap, 5)`.
- [x] Current sender pool (equal distribution):
- [x] `cameron@livetransparent.com`
- [x] `cameron@livetransparent.co`
- [x] `cameron@livetransparent.agency`
- [x] `cameron@livetransparent.org`

## 8) QA
- [ ] Test with internal contacts first.
- [ ] Verify no dual-enrollment into both A and B.
- [ ] Verify 50/50 distribution is roughly even over time.
- [ ] Verify booking/reply/closed/do-not-nurture exits remove contacts from both sequences.
- [ ] Verify `Email Campaign`, `Email Variant`, `Last Marketing Email`, `Last Marketing Email Sent At` update correctly.
- [ ] Verify sender stickiness:
- [ ] Contact remains on same `marketing_sender_email` across entire sequence.
- [ ] Mid-sequence field edits do not unintentionally switch sender.
- [ ] Verify queue release math:
- [ ] Released count per sender does not exceed daily cap.

## 9) Backlog (After Core Launch)
- [ ] Review all left-behind workflows for cleanup/activation status.
- [ ] Review and align other intake flows in n8n (funnel, referral, email inbound/outbound, SMS) to sequence enrollment rules.
