# Power Dialer SDR Training Guide

## Purpose

The GHL Power Dialer is the human calling queue for SDRs working the `Sales Outreach` pipeline. It helps Marc and Jason make organized outbound calls, record the correct call outcome, and move each opportunity into the next appropriate step.

This guide covers:

- How to prepare and work a Power Dialer queue
- What each Call Outcome means
- What GHL automates after each outcome
- What the SDR must do manually
- Required notes and escalation rules

## Important Boundaries

- The Power Dialer is a **managed GHL Manual Actions queue**, not an automatic AI dialer.
- The queue contains only contacts intentionally tagged for that day's work.
- The queue is limited to the `Sales Outreach` pipeline stages `Qualified` and `New`.
- The existing Vapi AI dialer is separate and is not changed by this process.
- Do not manually add queue tags to suppressed contacts or contacts already marked done.
- Use the approved voicemail recording configured in GHL. Do not upload a different recording or change the voicemail action without manager approval.

## Before You Start

1. Confirm your browser microphone and speaker permissions are enabled for GHL.
2. Use a stable headset or microphone in a quiet environment.
3. Confirm your caller ID is the approved Live Transparent number.
4. Review the contact and opportunity before dialing:
   - Company name and contact name
   - Current opportunity stage
   - Owner
   - Previous notes and outreach history
   - Phone number
5. Do not call contacts with any of these suppression indicators:
   - `do not contact`
   - `do not nurture`
   - `dnc`
   - `do not call`
   - `unsubscribed`
   - `opted out`

## Build Your Queue

Queueing is intentional and manual. Add the correct queue tag to the contacts you want to call.

| Opportunity stage | Queue tag | Queue name |
|---|---|---|
| `Qualified` | `powerdialer_salesoutreach_qualified` | `Power Dialer - Qualified` |
| `New` | `powerdialer_salesoutreach_new` | `Power Dialer - New` |

From **Contacts**:

1. Filter to contacts you own.
2. Confirm the contact has an open opportunity in `Sales Outreach`.
3. Confirm the opportunity is in `Qualified` or `New`.
4. Confirm no suppression or done tag is present.
5. Select the contact or contacts.
6. Add the matching queue tag.
7. Open **Conversations → Manual Actions** and confirm the task appears in your queue.

Do not use the `Qualified` tag for a `New` opportunity or vice versa. The tags determine which Manual Action queue receives the contact and which stage the post-call automation searches.

## Start Calling

1. Open **Conversations → Manual Actions**.
2. Select `Power Dialer - Qualified` or `Power Dialer - New`.
3. Review the contact card before starting.
4. Click **Let's Start**.
5. When the call connects, follow the approved SDR talk track.
6. Keep the contact record open so you can write the note immediately.
7. Select the most accurate Call Outcome when the call ends.

Do not select `Completed` just because the phone connected. `Completed` means the live conversation was handled and requires the SDR to decide the next opportunity stage.

## Call Outcomes

### Completed

Use when the call connected and the live conversation was completed, including when the prospect answered but the conversation ended quickly.

The automation will:

- Remove the active Power Dialer queue tag
- Add the matching `_done` tag
- Leave the opportunity stage unchanged

The SDR must:

- Write a clear call note
- Record the prospect's interest, objection, timing, and next step
- Move the opportunity manually to the correct stage
- Create or confirm the next task when a follow-up is needed

Examples:

- Interested and meeting requested: move to `Meeting Requested`.
- Meeting booked: move to `Booked` and confirm the appointment.
- Not a fit: follow the manager-approved disqualification process.
- Asked for a later call: keep the opportunity in the appropriate outreach stage and create a dated follow-up task.

### Voicemail

Use when the call reaches voicemail and no live conversation occurs.

The automation will:

- Remove the active queue tag
- Add the matching `_done` tag
- Play the approved ringless voicemail drop
- Find the matching `Sales Outreach` opportunity
- Move it to `Attempting Contact 1st Attempt`
- Start the configured follow-up automation for that stage, when its conditions are met

The SDR must:

- Confirm the outcome is actually voicemail, not an IVR menu or a live person
- Write a brief note with the date and result
- Avoid manually sending a second voicemail or duplicate follow-up immediately

### Not Answered

Use when the call rings but is not answered and does not reach voicemail.

The automation will remove the queue tag, add the matching `_done` tag, and move the opportunity to `Attempting Contact 1st Attempt`.

The SDR must write a note and review the follow-up automation or task created by the stage change.

### Busy

Use when the carrier or phone system reports a busy signal.

The automation treats this as an unsuccessful first attempt:

- Queue tag is removed
- Matching `_done` tag is added
- Opportunity moves to `Attempting Contact 1st Attempt`

Do not mark `Busy` as `Completed` unless you had a real conversation.

### Canceled

Use when the call was canceled before a meaningful conversation occurred.

The automation treats this like an unsuccessful attempt:

- Queue tag is removed
- Matching `_done` tag is added
- Opportunity moves to `Attempting Contact 1st Attempt`

If the cancellation was caused by a technical problem, note that explicitly and notify the manager rather than silently retrying the contact.

## Outcome Decision Tree

```text
Did a real person have a meaningful conversation?
  Yes -> Completed
  No -> Did the call reach voicemail?
          Yes -> Voicemail
          No -> Did the carrier report busy?
                  Yes -> Busy
                  No -> Was the call canceled before connection?
                          Yes -> Canceled
                          No -> Not Answered
```

## Required Call Note

Every call must have a note. Use this format:

```text
Power Dialer | [Outcome] | [YYYY-MM-DD]
Contact: [name]
Summary: [what happened]
Interest/objection: [detail or None stated]
Next step: [specific action and date, or None]
```

Example:

```text
Power Dialer | Completed | 2026-08-25
Contact: Alex Rivera
Summary: Reached Alex; they handle paid acquisition for the dispensary group.
Interest/objection: Interested but wants pricing before booking.
Next step: Send pricing overview today and follow up Thursday, 2026-08-27.
```

For a voicemail, keep it short:

```text
Power Dialer | Voicemail | 2026-08-25
Reached voicemail. Approved voicemail drop completed. Follow-up automation should proceed from Attempting Contact 1st Attempt.
```

## What Not To Do

- Do not add both Qualified and New queue tags to the same contact.
- Do not re-add a queue tag immediately after a call; the automation removes it and marks the contact done.
- Do not move a `Voicemail`, `Not Answered`, `Busy`, or `Canceled` opportunity back to `New` manually unless a manager approves a correction.
- Do not use `Completed` to avoid the automated first-attempt follow-up.
- Do not send duplicate email, SMS, or voicemail messages outside the configured follow-up process.
- Do not call a suppressed contact, even if the contact appears in a stale queue.
- Do not change tags, stages, ownership, or workflow settings to work around a failed call.

## Troubleshooting

### The contact is not in Manual Actions

- Confirm the correct queue tag was added.
- Confirm the contact is owned by you or the intended SDR.
- Confirm the tag was not immediately removed by another workflow.
- Refresh Manual Actions and check the other queue only if the stage was recently changed.

### The wrong queue is shown

- Check the opportunity stage.
- Remove the incorrect queue tag only after confirming no call is in progress.
- Add the matching Qualified or New queue tag.

### The voicemail did not play

- Do not retry the voicemail manually.
- Record the call outcome and note the issue.
- Capture the contact name, call time, and any GHL error message.
- Escalate to the manager or automation owner.

### The opportunity did not move after an unsuccessful call

- Confirm the call was logged as `Voicemail`, `Not Answered`, `Busy`, or `Canceled`.
- Confirm the contact still had the matching queue tag at the time of the call.
- Check whether the opportunity is in `Sales Outreach` and in the expected Qualified/New stage.
- Do not force a stage change without documenting the reason.

### The contact cannot be called

- Verify the phone number and caller ID.
- Check browser microphone permissions.
- Check whether the contact is suppressed or already marked done.
- Escalate technical failures instead of repeatedly dialing.

## Daily Closeout

Before ending the calling block:

1. Complete or disposition every Manual Action.
2. Confirm every call has a note.
3. Review `Completed` calls and manually move opportunities where needed.
4. Confirm scheduled follow-ups have a clear date and owner.
5. Report technical failures, incorrect routing, duplicate tasks, or voicemail issues to the manager.

## Manager Training Checklist

An SDR is ready to use the Power Dialer when they can:

- Find both Manual Action queues.
- Add the correct queue tag for Qualified versus New.
- Explain all five Call Outcomes.
- Select `Completed` only after a meaningful live conversation.
- Write a complete call note.
- Explain which outcomes move the opportunity to `Attempting Contact 1st Attempt`.
- Explain that Voicemail also triggers the approved ringless voicemail drop.
- Move a Completed opportunity manually to its next stage.
- Recognize suppression tags and stop instead of calling.
