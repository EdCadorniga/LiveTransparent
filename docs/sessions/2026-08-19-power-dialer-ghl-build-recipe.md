# GHL Build Recipe — Power Dialer Workflows (B + C)

Date: 2026-08-19
Build these workflows in the GHL UI: **Automations → Workflows**. There is no JSON import for GHL workflows; this recipe is copy-paste/click-along.

Workflows to build: **B1** (`LT - Power Dialer Qualified Queue`), **B2** (`LT - Power Dialer New Queue`), and **C** (`LT - Power Dialer Disposition` — a single workflow covering both stages, no C-Qualified / C-New split).

Tags are already created (via API). GHL stores them lowercase (case-insensitive):
- `powerdialer_salesoutreach_qualified`
- `powerdialer_salesoutreach_new`
- `powerdialer_salesoutreach_qualified_done`
- `powerdialer_salesoutreach_new_done`

---

## Pre-flight (one time)

1. Confirm **LC Phone** is enabled (Settings → Phone Numbers) and pick the outbound caller ID for human dialing.
2. Record the ringless voicemail mp3/wav at **64 kbps** (15–20s, no names). Keep it handy for workflow C.
3. Confirm the follow-up automation `Jason Followup Emails and SMS` (`f6b44e34`) is published and its SimpleTexting SMS leg is live.

---

## Workflow B1 — Power Dialer · Qualified queue

> The tag trigger is labeled **`Tag Added`** in most builds, but some GHL versions call it **`Contact Tag`**. Both are the same trigger — if you see "Contact Tag", select that and set its filter to the tag below.

| Step | Field | Value |
|---|---|---|
| 1. Trigger | Type = **`Tag Added`** | |
| | Tag | `powerdialer_salesoutreach_qualified` |
| 2. Action | **`Manual Action`** (Manual Call / "Manual Action to Call") | |
| | Name | `Power Dialer - Qualified` |
| | Assignment | **Leave default = contact owner** (do NOT pick a specific user or round-robin) |

Publish → name the workflow `LT - Power Dialer Qualified Queue`.

**Owner scoping:** because assignment defaults to the contact owner, each SDR sees only the contacts they own. Marc's queue shows Marc-owned contacts; Jason's shows Jason-owned. When an SDR adds the tag to a contact they own (or to one whose opportunity they own and that ownership is aligned), the Manual Action lands in their own queue. Contacts tagged by someone else land in that contact's owner's queue — not the tagger's.

## Workflow B2 — Power Dialer · New queue

Same as B1, but:
- Trigger tag = `powerdialer_salesoutreach_new`
- Manual Action name = `Power Dialer - New`
- Assignment = **default (contact owner)**

Publish → name the workflow `LT - Power Dialer New Queue`.

> Note: If GHL's workflow builder won't let two workflows use the same `Manual Action` name, keep names distinct (`Power Dialer - Qualified` vs `Power Dialer - New`). The two workflows must remain separate so Qualified and New surface as two queues in `Conversations → Manual Actions`.

---

## Workflow C — Power Dialer post-call disposition

GHL's call trigger is **`Call Status`** (may appear as "Call Details" in some builds). Its statuses are: `Not Answered`, `Busy`, `Voicemail`, `Completed`, `Canceled`.

Single workflow: **`LT - Power Dialer Disposition`**. One `Call Status` trigger per outcome (C1–C5); each branch first splits on which queue tag is present, then swaps the matching tag and moves the matching stage's opportunity.

> **Important:** `Update Opportunity` only targets the opportunity that *triggered the workflow*, or one found by a `Find Opportunity` step. A `Call Status` trigger fires on a *call*, not an opportunity — so each branch below includes a **`Find Opportunity`** step before the stage move.

### Shared per-branch pattern

Every branch (C1–C5) uses the same structure. The **Qualified vs New** split is repeated inside each branch:

```
Call Status branch
  └─ split: has `powerdialer_salesoutreach_qualified`?
       ├─ YES (Qualified path)
       │    Remove Tag powerdialer_salesoutreach_qualified
       │    Add Tag    powerdialer_salesoutreach_qualified_done
       │    Find Opportunity  (Sales Outreach / stage Qualified / Latest)
       │    [C1 only] Voicemail  (64 kbps mp3 drop)
       │    Update Opportunity → Attempting Contact 1st Attempt   [skip in C5]
       └─ NO → has `powerdialer_salesoutreach_new`?  (the else / second path)
            Remove Tag powerdialer_salesoutreach_new
            Add Tag    powerdialer_salesoutreach_new_done
            Find Opportunity  (Sales Outreach / stage New / Latest)
            [C1 only] Voicemail  (64 kbps mp3 drop)
            Update Opportunity → Attempting Contact 1st Attempt   [skip in C5]
```

### C1 — Voicemail branch

| Step | Field | Value |
|---|---|---|
| 1. Trigger | **`Call Status`** | |
| | Filter: Call Direction | `Outgoing` |
| | Filter: Call Status | `Voicemail` |
| 2. Split | tag present = `powerdialer_salesoutreach_qualified` | |
| 3. Action | **`Remove Tag`** | `powerdialer_salesoutreach_qualified` (or `_new`) |
| 4. Action | **`Add Tag`** | `powerdialer_salesoutreach_qualified_done` (or `_new_done`) |
| 5. Action | **`Voicemail`** (ringless drop) | upload the 64 kbps mp3 |
| 6. Action | **`Find Opportunity`** | pipeline = `Sales Outreach`, stage = `Qualified` (or `New`), `Latest` |
| 7. Action | **`Update Opportunity`** → move to stage | `Attempting Contact 1st Attempt` (`b97e42b1-b4c2-4759-8212-33596a085cf2`) |

### C2 — Not Answered branch

Same as C1 **minus the `Voicemail` drop**: trigger `Call Status` = `Not Answered` → split Qualified/New → Remove queue tag → Add done tag → Find Opportunity (Qualified/New) → Update Opportunity → `Attempting Contact 1st Attempt`.

### C3 — Busy branch

Same as C2, but `Call Status` = `Busy`.

### C4 — Canceled branch

Same as C2, but `Call Status` = `Canceled`. (Treat a canceled dial the same as a no-answer: tag as done, remove queue tag, advance to 1st Attempt.)

### C5 — Completed branch

| Step | Field | Value |
|---|---|---|
| 1. Trigger | **`Call Status`** | |
| | Filter: Call Direction | `Outgoing` |
| | Filter: Call Status | `Completed` |
| 2. Split | tag present = `powerdialer_salesoutreach_qualified` | |
| 3. Action | **`Remove Tag`** | `powerdialer_salesoutreach_qualified` (or `_new`) |
| 4. Action | **`Add Tag`** | `powerdialer_salesoutreach_qualified_done` (or `_new_done`) |

(No stage change — the SDR moves the opportunity manually.)

This is **5 trigger-branches total**, each split into a Qualified and a New path — **no separate C-Qualified / C-New workflows**.

---

## Post-build smoke test

1. Pick a test contact (real number you control), ensure its opp is in `Qualified` (or `New`).
2. Manually add the queue tag → confirm the task appears under **Conversations → Manual Actions** for the correct owner.
3. Click **Let's Start** → confirm the softphone dials.
4. Trigger each disposition (Voicemail / Not Answered / Busy / Canceled / Completed) and, for each, confirm that a Qualified-contact and a New-contact both get the tag swap + stage move (and, for Voicemail, the ringless drop).
5. Confirm `f6b44e34` fires on the stage move into `Attempting Contact 1st Attempt`.

---

## Key IDs

| Item | ID |
|---|---|
| Sales Outreach pipeline | `dhdlf3O4tymxFtHk4aqq` |
| Qualified stage | `91517911-3eee-45a0-b432-e36209495c16` |
| New stage | `3529dd3d-cab0-4279-967c-1aea203de4fb` |
| Attempting Contact 1st Attempt | `b97e42b1-b4c2-4759-8212-33596a085cf2` |
| Follow-up automation | `f6b44e34` |
