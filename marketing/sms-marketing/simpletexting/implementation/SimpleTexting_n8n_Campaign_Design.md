# SimpleTexting n8n Campaign Design

## Purpose
- Use `n8n` as the system that enrolls, sequences, waits, checks stop conditions, and delivers all 6 SimpleTexting messages.
- Use GHL as the contact system of record and eligibility source.
- Keep SimpleTexting as the SMS provider.
- Keep Apollo phone enrichment as the fallback when delivery indicates the number is not a valid mobile.

## Locked Decisions
- Do not use GHL SMS actions for this campaign.
- Do not use `SMS Drip - Eligibility + Enrollment` or `SMS Drip - Core 6 Touch`.
- Use the GHL smart list `Simpletexting Pool` as the canonical eligibility pool.
- Keep the existing live tag family unless a deliberate migration is approved:
  - `simpletext_start`
  - `simpletext_ongoing`
  - `simpletext_finished`
  - `simpletext_stop`
- Check for `simpletext_stop` before every message send.
- Trigger Apollo phone enrichment when delivery results imply the current number is invalid, non-mobile, or otherwise unusable for SMS.

## Workflow Set

### 1. LT - SimpleTexting Pool Dispatcher (Staged)
Purpose:
- Run on a schedule.
- Pull eligible contacts from the `Simpletexting Pool` logic.
- Enroll a contact only once into the active campaign.
- Start the sequencer workflow for each enrolled contact.

Recommended trigger:
- `Schedule Trigger`
- Every 1 hour to start

Recommended nodes:
1. `Schedule Trigger`
2. `Config` (`Set`)
3. `Ensure Campaign Tables` (`Postgres`)
4. `Fetch Campaign Enrollment State` (`Postgres`)
5. `Fetch Eligible Contacts` (`Code`)
6. `Only New Enrollments` (`Code`)
7. `Insert Enrollment Rows` (`Postgres`)
8. `Trigger Sequencer` (`Execute Workflow`)
9. `Summary` (`Code` or `Set`)

Core config fields:
- `locationId`
- `ghlApiBaseUrl`
- `ghlApiKey`
- `defaultDryRun`
- `candidateLimit`
- `simpletextingPoolSearchBodyJson`
- `sequencerWorkflowId`
- `campaignKey`
- `tagStart`
- `tagOngoing`
- `tagFinished`
- `tagStop`

Notes:
- `simpletextingPoolSearchBodyJson` should mirror the GHL `Simpletexting Pool` smart list logic.
- The dispatcher should not send SMS directly.
- The dispatcher should only enroll and launch the sequencer.

### 2. LT - SimpleTexting Campaign Sequencer (Staged)
Purpose:
- Run one contact at a time.
- Send up to 6 SMS messages.
- Wait between steps.
- Re-check stop conditions before each send.
- Record campaign progress durably in Postgres.

Recommended trigger:
- `Execute Workflow Trigger`

Recommended nodes:
1. `Execute Workflow Trigger`
2. `Config` (`Set`)
3. `Load Contact Context` (`Code`)
4. `Ensure Contact State Row` (`Postgres`)
5. `Step 1 Precheck` (`Code`)
6. `If Step 1 Allowed`
7. `Send Step 1` (`HTTP Request` to `LT - SimpleTexting SMS Send (Webhook, Staged)`)
8. `Write Step 1 State` (`Postgres`)
9. `Wait Step 2`
10. `Step 2 Precheck`
11. `If Step 2 Allowed`
12. `Send Step 2`
13. `Write Step 2 State`
14. `Wait Step 3`
15. `Step 3 Precheck`
16. `If Step 3 Allowed`
17. `Send Step 3`
18. `Write Step 3 State`
19. `Wait Step 4`
20. `Step 4 Precheck`
21. `If Step 4 Allowed`
22. `Send Step 4`
23. `Write Step 4 State`
24. `Wait Step 5`
25. `Step 5 Precheck`
26. `If Step 5 Allowed`
27. `Send Step 5`
28. `Write Step 5 State`
29. `Wait Step 6`
30. `Step 6 Precheck`
31. `If Step 6 Allowed`
32. `Send Step 6`
33. `Write Step 6 State`
34. `Finalize Campaign` (`Postgres` + optional tag sync)

Implementation note:
- Repeated sections can be built with copyable step blocks.
- Keep the precheck logic centralized and nearly identical per step.

### 3. Keep Existing Published Callback Workflows
- `LT - SimpleTexting Inbound Reply (Webhook, Staged)`
- `LT - SimpleTexting Delivery Events (Webhook, Staged)`
- `LT - SimpleTexting Unsubscribe Events (Webhook, Staged)`

These remain responsible for:
- adding `simpletext_stop` when appropriate
- writing GHL notes
- stopping future sends indirectly via the sequencer precheck
- kicking off remediation when a number is unusable

## Postgres Schema

### Table: SimpleTexting_Campaign_State
Purpose:
- One row per contact per campaign
- Durable step state for resume, stop, and audit

Recommended columns:
- `id BIGSERIAL PRIMARY KEY`
- `ghl_contact_id TEXT NOT NULL`
- `campaign_key TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'enrolled'`
- `current_step INT NOT NULL DEFAULT 0`
- `last_template_key TEXT`
- `last_sent_at TIMESTAMPTZ`
- `provider_message_id TEXT`
- `phone_at_send TEXT`
- `stop_reason TEXT`
- `run_id TEXT`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

Recommended unique key:
- `(ghl_contact_id, campaign_key)`

Recommended statuses:
- `enrolled`
- `sent_step_1`
- `sent_step_2`
- `sent_step_3`
- `sent_step_4`
- `sent_step_5`
- `sent_step_6`
- `stopped`
- `finished`
- `delivery_failed`
- `awaiting_phone_refresh`

### Table: SimpleTexting_Campaign_Event_Log
Purpose:
- Append-only audit log

Recommended columns:
- `id BIGSERIAL PRIMARY KEY`
- `ghl_contact_id TEXT NOT NULL`
- `campaign_key TEXT NOT NULL`
- `event_type TEXT NOT NULL`
- `step_number INT`
- `template_key TEXT`
- `provider_message_id TEXT`
- `details JSONB`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

Example `event_type` values:
- `enrolled`
- `precheck_blocked`
- `sent`
- `delivery_failed`
- `stopped`
- `finished`
- `apollo_phone_enrichment_triggered`

## Dispatcher Logic
1. Load the GHL search body that represents the `Simpletexting Pool`.
2. Search GHL contacts.
3. Exclude contacts with:
- no phone
- `simpletext_ongoing`
- `simpletext_finished`
- `simpletext_stop`
4. Exclude contacts already enrolled in `SimpleTexting_Campaign_State` for the active `campaign_key`.
5. Insert new `enrolled` rows.
6. Call the sequencer with:
- `contactId`
- `campaignKey`
- `startingStep = 1`
- `dryRun`

## Sequencer Precheck Logic
Run this before every send.

Inputs:
- `contactId`
- `campaignKey`
- `stepNumber`

Checks:
1. Re-fetch contact from GHL by `contactId`.
2. Stop if the contact has:
- `simpletext_stop`
- `simpletext_finished`
3. Stop if the contact is SMS DND, if available from the contact payload.
4. Stop if the campaign row is already `finished` or `stopped`.
5. Stop if the contact has no phone.
6. Optional stop if the contact has entered a booked / closed state.

If blocked:
- update campaign state to `stopped`
- write event log row with reason
- exit cleanly

## Send Contract
Each send step should call the existing send workflow webhook:
- `https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms`

Header:
- `x-lt-webhook-key: <shared secret>`

Payload shape:
```json
{
  "dryRun": true,
  "contactId": "<GHL_CONTACT_ID>",
  "contactPhone": "<PHONE>",
  "templateKey": "sms_1",
  "campaignKey": "simpletexting_campaign_v1",
  "addTags": ["simpletext_start", "simpletext_ongoing"],
  "removeTags": [],
  "contact": {
    "first_name": "<FIRST_NAME>",
    "last_name": "<LAST_NAME>",
    "email": "<EMAIL>"
  }
}
```

Tag behavior by step:
- Step 1:
  - add `simpletext_start`
  - add `simpletext_ongoing`
- Steps 2-5:
  - no tag changes unless needed
- Step 6:
  - remove `simpletext_ongoing`
  - add `simpletext_finished`

Do not remove `simpletext_start`.

## Wait Schedule
Use placeholders now. Final delays can be updated later.

Recommended config fields:
- `delayAfterSms1`
- `delayAfterSms2`
- `delayAfterSms3`
- `delayAfterSms4`
- `delayAfterSms5`

Placeholder values:
- `delayAfterSms1 = <TBD>`
- `delayAfterSms2 = <TBD>`
- `delayAfterSms3 = <TBD>`
- `delayAfterSms4 = <TBD>`
- `delayAfterSms5 = <TBD>`

## Message Placeholders
Keep message text centralized in `LT - SimpleTexting SMS Send (Webhook, Staged)` using template keys.

The live registry currently uses these six slots:

```text
sms_1 = Hi - thanks for checking out regulated ads on social/search. I'm Cameron, founder of Transparent eCom. We help regulated brands run ads that most agencies can't, including Mood, Cookies, and Lucy. You can learn more at https://livetransparent.com/ Are you currently running ads, restricted from advertising, or just exploring options?
sms_2 = Hey, Cameron again. If you're curious, our site has free walkthroughs on how brands run ads in regulated industries on platforms like Meta and Google. Some companies do it themselves - totally fine. But we also have a few capabilities most brands and agencies don't that allow actual product advertising at scale. Want me to send it over?
sms_3 = Quick follow-up - We've helped brands like Mood, Lucy, and GPen scale ads profitably in regulated spaces. Would it be helpful if I showed you what has worked for them?
sms_4 = Fun fact: We can run actual flower and pre-roll ads with regulated-industry mentions directly in the ad. Here's an example (you'll need to be logged into Facebook to preview): https://fb.me/adspreview/facebook/1SsU73bjDHg0XY1
sms_5 = If you're a dispensary, this might be interesting: We help dispensaries connect digital ad activity to in-store purchases, so they can measure actual ROI from social and search campaigns. More details are available at https://livetransparent.com/ Should I send over a quick example?
sms_6 = Hey - Cameron again. I don't want to keep bothering you, so this will be my last message. If you ever want to learn how brands are running regulated ads on social/search, just reply here and I'm happy to help.
```

On 2026-07-26, `sms_1`, `sms_3`, and `sms_5` were updated in the live registry. The legacy GHL payload aliases `john_sms1` through `john_sms5` remain compatibility keys and were not renamed.

Recommended campaign key:
```text
simpletexting_campaign_v1
```

## Bounce and Apollo Enrichment Logic
The sequencer should not try to guess whether a number is mobile.
The source of truth should be delivery outcomes from SimpleTexting.

Recommended behavior:
1. `Delivery Events` receives a failed delivery / invalid number / non-mobile result.
2. That workflow updates `SimpleTexting_Campaign_State`:
- `status = delivery_failed` or `awaiting_phone_refresh`
3. It writes a campaign event log row.
4. It triggers or tags for `WL - Apollo Phone Enrichment Trigger`.
5. The sequencer will not continue while the state is `awaiting_phone_refresh`.
6. After enrichment, one of two policies can be applied:
- resume at failed step
- restart from step 1

Recommended initial policy:
- restart from step 1 only after a valid mobile is found

That is operationally simpler and less brittle.

## Smart List Usage
The dispatcher should treat `Simpletexting Pool` as the canonical eligibility definition.

Important:
- the smart list is the pool
- Postgres campaign state is the durable runtime state

Do not rely on smart list membership alone to know whether a contact is already in-progress.

## Recommended Config Block
Use one config node per workflow with explicit fields.

Dispatcher config:
- `locationId`
- `ghlApiBaseUrl`
- `ghlApiKey`
- `defaultDryRun`
- `candidateLimit`
- `simpletextingPoolSearchBodyJson`
- `sequencerWorkflowId`
- `campaignKey`
- `tagStart`
- `tagOngoing`
- `tagFinished`
- `tagStop`

Sequencer config:
- `locationId`
- `ghlApiBaseUrl`
- `ghlApiKey`
- `defaultDryRun`
- `campaignKey`
- `sendWebhookUrl`
- `sendAuthHeaderName`
- `sendAuthHeaderValue`
- `delayAfterSms1`
- `delayAfterSms2`
- `delayAfterSms3`
- `delayAfterSms4`
- `delayAfterSms5`
- `tagStart`
- `tagOngoing`
- `tagFinished`
- `tagStop`

## Dry Run Rules
- Keep both new workflows `inactive` while building.
- Keep `defaultDryRun = true` until one internal end-to-end test succeeds.
- First live test should use a single internal contact.

## Build Order
1. Create `SimpleTexting_Campaign_State`.
2. Create `SimpleTexting_Campaign_Event_Log`.
3. Clone and refactor the current warmup dispatcher into `LT - SimpleTexting Pool Dispatcher (Staged)`.
4. Build `LT - SimpleTexting Campaign Sequencer (Staged)`.
5. Add the 6 blank template keys to the send workflow.
6. Add delivery-failure -> Apollo enrichment state handling.
7. Test one internal contact in dry run.
8. Test one internal contact live.
9. Activate dispatcher only after the live sequencer path is verified.

## Open Inputs Still Needed
- Exact `Simpletexting Pool` filter body
- Final message copy for:
  - `sms_1`
  - `sms_2`
  - `sms_3`
  - `sms_4`
  - `sms_5`
  - `sms_6`
- Final delays between each message
- Exact delivery failure states that should trigger Apollo phone enrichment
- Whether booked/disqualified contacts should stop immediately
