# GHL Snapshot Build Spec - LinkedIn Micro Workflows

Location ID: `Zwz4relUXVPxx8uohnjV`  
Scope: LinkedIn-only micro-workflows (phase 1)  
Rule: Tag + metadata only. No pipeline/stage/owner/sequence actions.

## Global Constraints
- Do not modify opportunities.
- Do not assign owners.
- Do not start campaigns/sequences.
- Do not add tasks.
- Do not move pipelines/stages.
- Keep re-entry enabled.
- Master router workflow remains separate: `WL - Master Warm Intake and Routing`.

## Shared Mapping Logic
Last-touch fields (overwrite when value exists):
- `UTM Source Last`
- `UTM Medium Last`
- `UTM Campaign Last`
- `UTM Content Last`
- `UTM Term Last`
- `UTM Landing Page Last`

First-touch fields (write only when empty):
- `UTM Source First`
- `UTM Medium First`
- `UTM Campaign First`
- `UTM Content First`
- `UTM Term First`
- `UTM Landing Page First`

Fallback behavior:
- If trigger value exists, use it.
- If trigger value missing, use workflow defaults below.

---

## Workflow 1
Name: `WL - Micro - LinkedIn Lead Form`

Trigger:
- LinkedIn lead form submission event (your connected LinkedIn lead source)

Actions in order:
1. Add tag: `linkedin lead form` (live; spec originally had `Warm  LinkedIn Lead Form`)
2. Set Last-touch fields from `{{contact.attributionSource.*}}`:
   - `UTM Source Last` = attribution `source` else `linkedin`
   - `UTM Medium Last` = attribution `medium` else `paid`
   - `UTM Campaign Last` = attribution `campaign` else `linkedin_lead_form`
   - `UTM Content Last` = attribution `content` if present
   - `UTM Term Last` = attribution `term` if present
   - `UTM Landing Page Last` = attribution `landingPage` or `page_url` if present
3. If empty, set First-touch fields using same resolved values:
   - `UTM Source First`
   - `UTM Medium First`
   - `UTM Campaign First`
   - `UTM Content First`
   - `UTM Term First`
   - `UTM Landing Page First`

---

## Workflow 2
Name: `WL - Micro - LinkedIn DM`

Trigger:
- LinkedIn DM reply event

Workflow fix applied 2026-07-08: If/Else condition changed from checking message.body CONTAINS placeholder text to checking Contact replied = True (trigger already guarantees LinkedIn DM; the placeholder never matched any real message).

Actions in order:
1. Add tag: `warm linkedin dm` (live; spec originally had `Warm  LinkedIn DM`)
2. Set Last-touch fields:
   - `UTM Source Last` = trigger `utm_source` else `linkedin`
   - `UTM Medium Last` = trigger `utm_medium` else `dm`
   - `UTM Campaign Last` = trigger `utm_campaign` else `linkedin_dm`
   - `UTM Content Last` = trigger `utm_content` if present
   - `UTM Term Last` = trigger `utm_term` if present
   - `UTM Landing Page Last` = trigger `page_url` if present
3. If empty, set First-touch fields using same resolved values:
   - `UTM Source First`
   - `UTM Medium First`
   - `UTM Campaign First`
   - `UTM Content First`
   - `UTM Term First`
   - `UTM Landing Page First`

---

## Workflow 3
Name: `WL - Micro - LinkedIn`

Trigger:
- LinkedIn engagement event (non-DM, non-lead-form)

Actions in order:
1. Add tag: `warm linkedin` (live; spec originally had `Warm  LinkedIn`)
2. Set Last-touch fields:
   - `UTM Source Last` = trigger `utm_source` else `linkedin`
   - `UTM Medium Last` = trigger `utm_medium` else `organic`
   - `UTM Campaign Last` = trigger `utm_campaign` else `linkedin_engagement`
   - `UTM Content Last` = trigger `utm_content` if present
   - `UTM Term Last` = trigger `utm_term` if present
   - `UTM Landing Page Last` = trigger `page_url` if present
3. If empty, set First-touch fields using same resolved values:
   - `UTM Source First`
   - `UTM Medium First`
   - `UTM Campaign First`
   - `UTM Content First`
   - `UTM Term First`
   - `UTM Landing Page First`

---

## QA Checklist (per workflow)
1. Trigger fires once for the event.
2. Correct warm tag is added.
3. Last-touch values update.
4. First-touch values remain unchanged once populated.
5. Contact can enter `WL - Master Warm Intake and Routing`.
6. No stage/pipeline/owner changes occur in micro-workflow.

