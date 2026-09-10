# Executive Report — SDR Attribution Gap for Successful Bookings (2026-09-09, follow-up diagnosis)

**Status:** Conclusive — the SDR who books a regulated-ads meeting for Cameron is *not recorded
anywhere* in either the reporting pipeline OR the source of truth (GHL). This is a data-capture
gap, not a query bug. Fix requires capturing the SDR at booking time + a small SQL read change.

## What we verified (window 2026-08-09 .. 2026-09-09, Cameron's Regulated Ads calendar `SrtXcFVyea7pFl3nTiIK`)

| Source | SDR trace for booked contacts? |
|---|---|
| Appointment `assigned_user_id` / `createdBy` / `assignedResources` | **No** — `booking_widget`, `userId:null`, `[]`, assigned_user_id=Cameron |
| Opportunity `assigned_to` (latest + as-of booking date + earliest snapshot) | **No** — Cameron/unassigned from creation day; never an SDR |
| Opportunity custom "Owner" field `Wpg7FGrQTgAY1GoKcdEJ` | **No** — empty on every booked contact's opp (one Marc opp, already credited) |
| Contact `assignedTo` (earliest, timeline, on booking date, today) | **No** — flips unassigned→Cameron; only Marc-credited contact still assigned to Marc today |
| `dhdlf` Sales Outreach opp (report table + pipeline history + stage timeline) | **No** — 85,817 dhdlf opps system-wide / 3,579 contacts, but ZERO for the 8 booked contacts |
| **GHL live API** (opportunities/search per contact) | **No** — only `MThK` Sales opps, Cameron/unassigned; no dhdlf opp exists in GHL either |
| GHL contact custom fields | **No SDR, but two workflow tags**: `FQv9wyl2JrMkpf1GPprP`="opportunity_owner_sync", `IPzJpFLekz9TDi4nWBaV`="opportunity_owner_change" — confirms a GHL automation transfers ownership at handoff |

## Root cause

1. SDRs (Marc `sqGx5rp3oAUG610NXyjU`, Jason) work regulated-ads leads; success = lead books a
   meeting on Cameron's calendar via the booking widget.
2. The booking-widget appointment carries **no SDR identity** (`createdBy.userId` null,
   `assignedResources` empty).
3. At/after booking, a GHL automation (workflow tags `opportunity_owner_sync` /
   `opportunity_owner_change` on contacts) moves the opp to the Sales pipeline `MThK...`
   and assigns contact+opp to Cameron `03p5GatJBH7i9zjMaIzm`.
4. The Exec Summary `contact_owner` CTE reads the **latest** opp `assigned_to` (all pipelines)
   → credits Cameron. `sdr_booked` then `COALESCE(contact_owner, appointment assigned_user_id)`
   → also Cameron. There is no SDR field anywhere to read.

## Consequences

- Report shows the truth: the SDR is not in the data. Symptom: `sdrPerformance` credits
  "Cameron Karkut" (booked 1, cancelled 1) — Cameron is NOT an SDR.
- For the current window: 7 booked + 1 cancelled → Cameron 2, Marc 1 (his contact still assigned
  to him in GHL today), unassigned 3, NO_OPP 1 (contact has no opp at all).
- **Historical bookings are unrecoverable** — the SDR was never captured anywhere (report DB AND
  GHL). Verified to source of truth.

## Fix options (decision needed from Ed)

- **(A) Capture-at-booking (recommended, future-only):** Extend the existing GHL
  `opportunity_owner_sync` workflow (or the n8n Appointments Ingest) to stamp the originating SDR
  into a contact/appointment custom field ("Originating SDR") at booking time — e.g. record the
  owner before the transfer flips it to Cameron. Exec Summary reads that field.
  Historical: not recoverable.
- **(B) Process change:** Have each SDR book meetings through their own calendar link / GHL
  account so `createdBy.userId` = the SDR; report reads appointment creator. Fixes future;
  changes team process.
- **(C) SQL-only:** not viable for these bookings — nothing exists to read.

## Supporting artifacts

- Probe scripts under `scripts\_tmp_*.sql` / `_tmp_ghl_probe*.py` (throwaway; `_vps_psql.py` reusable).
- Live Exec Summary SQL: `C:\Users\edmon\AppData\Local\Temp\lt_Build_Query.js` (CTEs `contact_owner`,
  `sdr_opp_facts`, `sdr_booked`, `sdr_sqls`, `sdr_performance`, `appointments`).