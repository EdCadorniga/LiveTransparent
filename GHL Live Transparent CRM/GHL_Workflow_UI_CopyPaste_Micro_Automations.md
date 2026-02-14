# GHL Workflow UI Copy/Paste - Warm Channel Micro-Automations

Use one workflow per channel.  
Each workflow does only:
1. Trigger on source event
2. Add exact `Warm  ...` tag
3. Update UTM/source metadata fields
4. End

Do NOT add any pipeline/stage/owner/sequence actions here.

---

## Current Build Status (2026-02-14)
- Completed: `WL - Micro - LinkedIn`, `WL - Micro - LinkedIn DM`, `WL - Micro - LinkedIn Lead Form`, `WL - Micro - Meta Lead Form`
- Built but trigger pending channel connection: `WL - Micro - Instagram`
- Deferred pending page connection: `WL - Micro - Facebook` (Messenger)
- Referral intake pattern now standardized on tag trigger `Referral - Intake`
- Build/verification pending: `WL - Micro - Meta Traffic`, `WL - Micro - Meta Remarketing`, `WL - Micro - Email Outbound`, `WL - Micro - Email Inbound`, `WL - Micro - SMS`, `WL - Micro - Website`

## Global Field Update Rules (apply in every micro-workflow)

### Last-touch writes (always update when value exists)
- `UTM Source Last`
- `UTM Medium Last`
- `UTM Campaign Last`
- `UTM Content Last`
- `UTM Term Last`
- `UTM Landing Page Last`

### First-touch writes (only if empty)
- `UTM Source First`
- `UTM Medium First`
- `UTM Campaign First`
- `UTM Content First`
- `UTM Term First`
- `UTM Landing Page First`

---

## 1) WL - Micro - Referral

### Trigger
`Contact Tag Added` where tag = `Referral - Intake`.

### Tag Action
`Warm  Referral`

### Source/UTM Defaults (if trigger does not pass UTM)
- Source: `referral`
- Medium: `referral`
- Campaign: `referral`

### End Action
Remove tag `Referral - Intake` at workflow end to prevent accidental re-entry from the same intake tag state.

---

## 2) WL - Micro - LinkedIn Lead Form

### Trigger
LinkedIn lead form submission.

### Tag Action
`Warm  LinkedIn Lead Form`

### Source/UTM Defaults
- Source: `linkedin`
- Medium: `paid`
- Campaign: `linkedin_lead_form`

---

## 3) WL - Micro - Meta Lead Form

### Trigger
Meta/Facebook lead form submission.

### Tag Action
`Warm  Meta Lead Form`

### Source/UTM Defaults
- Source: `meta`
- Medium: `paid`
- Campaign: `meta_lead_form`

### Warm Metadata Values
- `Warm Source` = `Meta Lead Form`
- `Primary Engagement Channel` = `Social`
- `Warm Trigger Type` = `Form Submission`

---

## 4) WL - Micro - Meta Traffic

### Trigger
Meta paid traffic visit/engagement event.

### Tag Action
`Warm  Meta Traffic`

### Source/UTM Defaults
- Source: `meta`
- Medium: `paid`
- Campaign: `meta_traffic`

---

## 5) WL - Micro - Meta Remarketing

### Trigger
Meta remarketing revisit/engagement event.

### Tag Action
`Warm  Meta Remarketing`

### Source/UTM Defaults
- Source: `meta`
- Medium: `paid`
- Campaign: `meta_remarketing`

---

## 6) WL - Micro - LinkedIn DM

### Trigger
LinkedIn DM reply event.

### Tag Action
`Warm  LinkedIn DM`

### Source/UTM Defaults
- Source: `linkedin`
- Medium: `dm`
- Campaign: `linkedin_dm`

---

## 7) WL - Micro - Instagram

### Trigger
Instagram DM reply event.

### Tag Action
`Warm  Instagram`

### Source/UTM Defaults
- Source: `instagram`
- Medium: `dm`
- Campaign: `instagram_dm`

---

## 8) WL - Micro - Facebook

### Trigger
Facebook Messenger reply event.

### Tag Action
`Warm  Facebook`

### Source/UTM Defaults
- Source: `facebook`
- Medium: `dm`
- Campaign: `facebook_messenger`

---

## 9) WL - Micro - LinkedIn

### Trigger
LinkedIn engagement event (non-DM, non-lead-form).

### Tag Action
`Warm  LinkedIn`

### Source/UTM Defaults
- Source: `linkedin`
- Medium: `organic`
- Campaign: `linkedin_engagement`

---

## 10) WL - Micro - Email Inbound

### Trigger
Inbound email reply.

### Tag Action
`Warm  Email Inbound`

### Source/UTM Defaults
- Source: `email`
- Medium: `inbound`
- Campaign: `email_inbound`

---

## 11) WL - Micro - Email Outbound

### Trigger
Outbound email engagement (click/open rule per your policy).

### Tag Action
`Warm  Email Outbound`

### Source/UTM Defaults
- Source: `email`
- Medium: `outbound`
- Campaign: `email_outbound`

---

## 12) WL - Micro - SMS

### Trigger
Inbound SMS reply.

### Tag Action
`Warm  SMS`

### Source/UTM Defaults
- Source: `sms`
- Medium: `inbound`
- Campaign: `sms_reply`

---

## 13) WL - Micro - Website

### Trigger
Website engagement rule (visit depth/time threshold).

### Tag Action
`Warm  Website`

### Source/UTM Defaults
- Source: `website`
- Medium: `organic`
- Campaign: `website_engagement`

---

## QA Quick Check (per workflow)
1. Trigger fires.
2. Correct `Warm  ...` tag is added.
3. `Last` fields update when values are present.
4. `First` fields are not overwritten once populated.
5. No pipeline/stage movement occurs in this micro-workflow.
6. For referral micro, `Referral - Intake` is removed at end.
