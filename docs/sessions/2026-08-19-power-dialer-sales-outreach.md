# Human Power Dialer — Sales Outreach (Qualified + New)

Date: 2026-08-19

## Status

**Queueing is manual.** The queue is populated by manually applying a queue tag to selected contacts in GHL — there is no automated queue-builder running. This lets the SDRs (Marc/Jason) control exactly who is in the day's calling queue.

Component A (`LT - Power Dialer Queue Builder`, id `J5uwS4Dn83JDpYs5`) was built and dry-run-verified (execution `764964`) but is **parked/unpublished and not the queue trigger**. It remains available as an optional bulk-audit helper if a mass backfill is ever wanted. Components B and C (GHL Manual Call queues and Call Status disposition) are the live path and must be built in the GHL UI (no API/MCP surface for GHL workflow automations).

## Intent

Introduce a **human SDR power dialer** as a new outbound channel, parallel to the existing Vapi AI dialer (unchanged). Used by Marc and Jason to cold-call contacts whose opportunities are in the `Sales Outreach` pipeline, stages `Qualified` and `New`.

This is a **managed task queue** (GHL `Manual Actions`), not the third-party continuous auto-advance dialer described in the source plan. GHL's "Voicemail Drop" is ringless voicemail (two-call carrier trick, ~70% reliable, TCPA prior-consent required). The operator accepted enabling it anyway.

## Locked decisions

| Decision | Value |
|---|---|
| Channel | Human SDR power dialer (new) |
| Users | Marc `sqGx5rp3oAUG610NXyjU`, Jason `yU85G6kfhtW4vUtx3QE6` |
| Pipeline | `Sales Outreach` = `dhdlf3O4tymxFtHk4aqq` |
| Eligible stages | `Qualified` = `91517911-3eee-45a0-b432-e36209495c16`, `New` = `3529dd3d-cab0-4279-967c-1aea203de4fb` |
| Queue trigger | **Manual tag application** (SDR/manager adds the queue tag to chosen contacts in GHL). No automated queue-builder. |
| Queue tags | `powerdialer_SalesOutreach_Qualified`, `powerdialer_SalesOutreach_New` |
| Done tags | `powerdialer_SalesOutreach_Qualified_Done`, `powerdialer_SalesOutreach_New_Done` |
| Ownership | 3-step resolution (below); round-robin only for leftovers; hash allocator `eeksgD0fbGHUqh4r` stays as Qualified-entry authority (option a) |
| Post-call (VM / No Answer / Busy) | remove queue tag → add `_Done` → move opp to `Attempting Contact 1st Attempt` (`b97e42b1-b4c2-4759-8212-33596a085cf2`) |
| Post-call (Completed) | remove queue tag → add `_Done`; SDR moves opp manually |
| Voicemail | Ringless drop enabled (accepted TCPA risk) |
| Phone | Primary `Phone` field only |
| Follow-up | Reuse `Jason Followup Emails and SMS` (`f6b44e34`) |

## Tag registry

| Tag | Meaning |
|---|---|
| `powerdialer_SalesOutreach_Qualified` | In queue, opp in Qualified |
| `powerdialer_SalesOutreach_New` | In queue, opp in New |
| `powerdialer_SalesOutreach_Qualified_Done` | Passed through dialer from Qualified |
| `powerdialer_SalesOutreach_New_Done` | Passed through dialer from New |

These are lifecycle tags, not campaign names. Add them to the reporting "not a campaign name" exclusion list.

## Ownership resolution (3 steps, in order)

Given a contact (C) and its opportunity (O) in Qualified/New:

1. If C has an owner → set O owner = C owner.
2. Else if C owner is not Marc/Jason → read O owner; if O owner is Marc/Jason → set C owner = O owner.
3. If neither C nor O is Marc/Jason → round-robin assign between Jason and Marc (set both).

Final owner must always be Marc or Jason. Owner writes keep native `assignedTo` (contact and opportunity) and the opportunity custom `Owner` field `Wpg7FGrQTgAY1GoKcdEJ` aligned.

## Suppression

Exclude contacts carrying any of: `do not contact`, `do not nurture`, `dnc`, `do not call`, `unsubscribed`, `opted out`. Also exclude contacts already carrying a queue tag or a `_Done` tag (no re-queue).

## Components

### Manual queueing (the live trigger)

To build the day's queue, an SDR or manager adds the queue tag to the contacts they want called:

- Add `powerdialer_SalesOutreach_Qualified` to a contact whose opp is in `Qualified`.
- Add `powerdialer_SalesOutreach_New` to a contact whose opp is in `New`.

The `Tag Added` workflow in component B picks the contact up and drops it into `Conversations → Manual Actions`, assigned to the contact owner. Tags can be applied in bulk from the Contacts list (multi-select → add tag) or per-contact. No automation is required — the SDR controls the day's queue by choosing which contacts to tag.

### A. n8n — `LT - Power Dialer Queue Builder` (PARKED, not the trigger)

Unpublished. Dry-run-verified (execution `764964`: 1,486 eligible, all already SDR-owned, 0 writes). Kept as an optional bulk-audit/backfill helper only; it is **not** how the queue is populated day-to-day. Do not publish or run it unless a mass backfill is explicitly requested.

- Round-robin counter: **in-memory per run** (resets each execution). Durable Postgres counter (`powerdialer_rr_counter`) documented as a follow-up if round-robin ever becomes non-trivial; currently latent because all eligible records are already SDR-owned.

### B. GHL — Manual Call queues (build in GHL UI)

Two workflows, one per stage:

- Trigger: `Tag Added` = `powerdialer_SalesOutreach_Qualified` → action `Manual Action to Call`.
- Trigger: `Tag Added` = `powerdialer_SalesOutreach_New` → action `Manual Action to Call`.

Settings for each Manual Call action:
- Assignment: **default (contact owner)** — do not set a specific user or round-robin. The SDR tags contacts they own, so the task lands on their queue.
- Name the action clearly (e.g. `Power Dialer - Qualified`).
- Add a call script / notes in the action so reps see the angle on the task card.

### C. GHL — Post-call disposition (build in GHL UI)

Workflow trigger: `Call Status` with filters `direction = Outbound` AND `status ∈ {Voicemail, No Answer, Busy}` (and contact still has a `powerdialer_*` queue tag).

Actions (Voicemail / No Answer / Busy branch):
1. Add `_Done` tag (matching stage).
2. Remove the queue tag.
3. Move the matching opportunity to `Attempting Contact 1st Attempt`.
4. On `Voicemail` only: add the GHL `Voicemail` (ringless) action with the pre-recorded 64 kbps mp3.

Separate path for `status = Completed`: add `_Done`, remove queue tag, no stage change.

### D. Reuse — `f6b44e34` follow-up

No new build. Verify during implementation:
- The SimpleTexting SMS leg of `f6b44e34` is actually live (n8n-side SimpleTexting is paused; this is a separate GHL automation).
- Marc-owned sender routing resolves (documented "configured but untested in production").

### E. n8n — daily reconciliation (not yet built)

- Remove stale queue tags where opp left Qualified/New or suppression tag appeared.
- Flag `_Done`-tagged contacts that re-entered Qualified/New for deliberate re-queue.

## Rollout

1. Confirm LC Phone + caller ID; verify `f6b44e34` SMS leg + Marc routing.
2. Build B and C in GHL; record ringless mp3.
3. Smoke test 3 contacts: manually add the queue tag to each, confirm the task appears in the correct owner's Manual Actions, then run the dispositions end-to-end.
4. Go live — SDRs manually tag the day's queue each morning.

### Component A (parked) — optional bulk backfill

If a mass backfill is ever wanted (e.g. tag every currently-open Qualified/New contact at once), run the parked `LT - Power Dialer Queue Builder` dry-run first to review the report, then flip `dryRun` off and re-run. This is not part of normal operation.

## Agent SOP (distribute)

**Before calling** — build your day's queue: in GHL Contacts, select the contacts you own whose opportunity is in `Qualified` or `New`, and add the tag `powerdialer_SalesOutreach_Qualified` or `powerdialer_SalesOutreach_New` accordingly.

1. Log into GHL → **Conversations → Manual Actions**.
2. Your queue shows only the contacts you tagged (assigned to you as owner); Qualified and New are separate lists.
3. Click **Let's Start** → softphone dials via browser mic/speakers.
4. **Connected** → pitch live, log notes, select **Completed**, then move the opportunity to the correct stage yourself.
5. **Voicemail / No Answer / Busy** → select the disposition; the system moves the opp to *Attempting Contact 1st Attempt* and fires the follow-up email + SMS.
6. Ringless voicemail drop fires automatically on the Voicemail disposition (consent risk already accepted by leadership).

## Key IDs

| Item | ID |
|---|---|
| Sales Outreach pipeline | `dhdlf3O4tymxFtHk4aqq` |
| Qualified stage | `91517911-3eee-45a0-b432-e36209495c16` |
| New stage | `3529dd3d-cab0-4279-967c-1aea203de4fb` |
| Attempting Contact 1st Attempt | `b97e42b1-b4c2-4759-8212-33596a085cf2` |
| Jason | `yU85G6kfhtW4vUtx3QE6` |
| Marc | `sqGx5rp3oAUG610NXyjU` |
| Opportunity `Owner` custom field | `Wpg7FGrQTgAY1GoKcdEJ` |
| GHL location | `Zwz4relUXVPxx8uohnjV` |
| GHL bearer credential (n8n) | `LIgX7IrOQoG1BusR` (`GHL API - Intake Poller`) |
| Allocator (hash, Qualified entry) | `eeksgD0fbGHUqh4r` |
| Owner alignment (GHL) | `b26326a5` |
| Follow-up (email + SMS) | `f6b44e34` |
