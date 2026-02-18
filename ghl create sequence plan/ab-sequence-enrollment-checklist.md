# Cannabis Ads Sequence Enrollment (A/B 50-50) - Implementation Checklist

Last updated: `2026-02-17`

## 1) GHL Contact Fields
- [x] Create `Email Campaign` (Single line text).
- [x] Create `Last Marketing Email` (Single line text).
- [x] Create `Email Variant` (Single line text).
- [x] Create `Last Marketing Email Sent At` (Single line text or date/time, current setup kept as text).
- [x] Move fields into field group `Campaign Details` (completed manually in GHL UI).

## 2) GHL Tags
- [x] `Seq Enrolled - Cannabis Ads`
- [x] `Seq Variant A`
- [x] `Seq Variant B`
- [x] `Meeting Booked`
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
- [x] n8n router workflows retired from active use (kept inactive as rollback only):
- [x] `WL - Seq Enrollment Router - Cannabis Ads (Workflow IDs Live)` (`UJnHFPxSdTcsK9iW`) - inactive
- [x] `WL - Seq Enrollment Router - Cannabis Ads` (`L5Cpe7ZdUgauQcF7`) - inactive
- [ ] Build/verify GHL workflow `WL - Seq Enrollment Router - Cannabis Ads`.
- [ ] Entry filter/guard checks:
- [ ] Has `Enrollment Queue - Cannabis Ads`
- [ ] Does not have `Seq Enrolled - Cannabis Ads`
- [ ] Does not have `Meeting Booked`
- [ ] Does not have `Do Not Nurture`
- [ ] DND Enabled Channels does not include `Email`
- [ ] Randomizer split 50/50 to Variant A and Variant B.
- [ ] In each branch, set:
- [ ] `Email Campaign = Cannabis Ads Sequence`
- [ ] `Email Variant = A` or `B`
- [ ] Add `Seq Variant A` or `Seq Variant B`
- [ ] Add `Seq Enrolled - Cannabis Ads`
- [ ] Remove `Enrollment Queue - Cannabis Ads`
- [ ] Enroll to corresponding sequence workflow (A or B).

## 5) Sequence Workflows (A and B)
- [x] Sequence workflows created in GHL:
- [x] A: `https://app.gohighlevel.com/location/Zwz4relUXVPxx8uohnjV/workflow/716d5fd7-09ef-4535-855b-70a7a73e731b`
- [x] B: `https://app.gohighlevel.com/location/Zwz4relUXVPxx8uohnjV/workflow/1ea5efa6-652b-4213-bf26-f32ff7275d71/advanced-canvas`
- [x] Delay pattern selected: `2d, 2d, 3d, 4d`.
- [ ] Confirm each email step updates:
- [ ] `Last Marketing Email`
- [ ] `Last Marketing Email Sent At`

## 6) Stop/Suppression Automation
- [ ] Build/verify `WL - Seq - Stop on Booked/Reply/Closed`.
- [ ] Trigger paths to include:
- [ ] Appointment booked (demo calendar)
- [ ] Customer replied (email)
- [ ] Opportunity `Closed Won`
- [ ] Opportunity `Closed Lost`
- [ ] Tag added `Do Not Nurture`
- [ ] Actions on all trigger paths:
- [ ] Add `Meeting Booked` where applicable
- [ ] Remove from sequence workflow A
- [ ] Remove from sequence workflow B

## 7) Sender Warm-Up Controls
- [ ] Implement controlled daily enrollment cap for sequence entry.
- [ ] Start with conservative caps and increase only after healthy metrics.
- [ ] Keep sending in business hours.
- [ ] Avoid batch bursts at the same minute (stagger enrollment/actions).

## 8) QA
- [ ] Test with internal contacts first.
- [ ] Verify no dual-enrollment into both A and B.
- [ ] Verify 50/50 distribution is roughly even over time.
- [ ] Verify booking/reply/closed/do-not-nurture exits remove contacts from both sequences.
- [ ] Verify `Email Campaign`, `Email Variant`, `Last Marketing Email`, `Last Marketing Email Sent At` update correctly.

## 9) Backlog (After Core Launch)
- [ ] Review all left-behind workflows for cleanup/activation status.
- [ ] Review and align other intake flows in n8n (funnel, referral, email inbound/outbound, SMS) to sequence enrollment rules.
