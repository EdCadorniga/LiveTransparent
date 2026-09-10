# 2026-09-09 — SDR Attribution Fix: Concrete Design (Option A, Capture-at-booking)

Status: **PART 3 (SQL read change) DEPLOYED 2026-09-09 — live & verified.** Parts 1–2
(manual GHL steps) remain Ed/Cameron's to-dos; Part 3 is inert until the real field id
replaces the placeholder.
Predecessor: `2026-09-09-sdr-attribution-success-booking-gap-diagnosis.md` (root cause,
verified to GHL source of truth: the SDR who books a regulated-ads meeting for Cameron is
recorded NOWHERE that survives the booking handoff).

## Design summary

Three parts. Only Part 3 is a code change (SQL read change in the live Exec Summary
workflow). Parts 1–2 are one-time GHL-builder changes (manual by Ed/Cameron) + zero
ingest changes. The fix is **future-only** — historical bookings are unrecoverable.

### Part 1 — GHL: create a contact custom field "Originating SDR" (manual, GHL builder)

- New **contact** custom field, type text, e.g. name `Originating SDR`.
- The value stored must be the **GHL user id** of the SDR (Jason `yU85G6kfhtW4vUtx3QE6`,
  Marc `sqGx5rp3oAUG610NXyjU`) — matches `report_sdr_registry.user_id` so names resolve.
- Note: this is the field the SQL will read; its **GHL field id** must be captured after
  creation (GET /locations/{locationId}/customFields?model=contact) and baked into the SQL.

### Part 2 — GHL: stamp the SDR at booking time (manual, GHL workflow editor)

- The existing handoff automation(s) — the workflows recorded in contact custom fields as
  `opportunity_owner_sync` (`FQv9wyl2JrMkpf1GPprP`) and `opportunity_owner_change`
  (`IPzJpFLekz9TDi4nWBaV`) — already prove this GHL setup can write contact custom fields.
- Edit the workflow that fires at booking → handoff: **as its first step (before ownership
  flips to Cameron)**, set contact custom field `Originating SDR` =
  `{{opportunity.assignedTo}}` (the pre-flip owner = the SDR).
- This is the capture: at booking the SDR still owns the pre-sales opp; the same workflow
  run stamps the contact, then flips ownership to Cameron. Nothing downstream overwrites it.
- If the workflow trigger cannot read the pre-flip opp owner, fallback mechanism: per-SDR
  booking links carrying `?sdr=<userid>` (GHL stores URL tracking params on the contact;
  contacts feed picks them up). To be decided by Ed after testing the workflow.

### Part 3 — n8n/DB: SQL read change (the only code change) — Exec Summary "Build Query"

No ingest changes at all:
- Contacts feed (`osIJOgBmWITF5Yuv`, every 60 min) already persists contact customFields
  (2,173/2,696 contacts carry them) — the new field flows in automatically.
- Appointments table unchanged (`contact_id` join key already present).

SQL change in the live "Build Query" node of Exec Summary (`Bukc0mgOD2r7V6ED`):

1. **New CTE `originating_sdr`** — extract the latest contact-snapshot value of the
   "Originating SDR" custom field:
   ```sql
   originating_sdr AS (
     SELECT DISTINCT ON (contact_id) contact_id, owner_id
     FROM (
       SELECT NULLIF(dimensions_json->>'contact_id','') AS contact_id,
              cf->>'value' AS owner_id,
              report_date
       FROM report_raw_ghl_contacts,
            jsonb_array_elements(COALESCE(payload_json->'customFields','[]'::jsonb)) AS cf
       WHERE NULLIF(dimensions_json->>'contact_id','') IS NOT NULL
         AND cf->>'id' = '__ORIGINATING_SDR_FIELD_ID__'
         AND NULLIF(cf->>'value','') IS NOT NULL
     ) x
     ORDER BY contact_id, report_date DESC
   )
   ```
   Deployed 2026-09-09 with placeholder `__ORIGINATING_SDR_FIELD_ID__` (matches nothing ⇒
   CTE returns zero rows ⇒ behavior identical to pre-fix). Replace the placeholder with the
   real GHL field id once Ed creates the field; that single edit activates the fix.
2. **Modify `sdr_booked`** — prefer the stamped SDR, then fall back to the existing chain
   (so nothing regresses for unstamped/legacy rows):
   ```sql
   SELECT COALESCE(os.owner_id,
            co.owner_id,
            COALESCE(NULLIF(a.assigned_user_id,''), 'unassigned')) AS owner_id, ...
   FROM report_raw_ghl_appointments a
   LEFT JOIN contact_owner co ON co.contact_id = a.contact_id
   LEFT JOIN originating_sdr os ON os.contact_id = a.contact_id
   ```
   (`contact_owner` and `sdr_performance` downstream aggregate by `owner_id` unchanged;
   `sdr_owner_names` resolves the id via `report_sdr_registry`.)

## Execution status (2026-09-09)

1. **DONE (2026-09-09)**: Part 3 (SQL read change) deployed to live Exec Summary
   `Bukc0mgOD2r7V6ED` via n8n REST PUT (auto-published; version
   `1fb05ab2-3c6c-4f62-a46a-4d2607a9bbef` == activeVersionId, verified by re-fetch).
   Inert placeholder `__ORIGINATING_SDR_FIELD_ID__` — zero behavior change until replaced.
   Validated standalone against live Postgres first (same window → identical rows; `os_rows = 0`).
2. Ed/Cameron: create GHL field (Part 1); Ed: edit GHL workflow (Part 2).
3. Ed records the new field's GHL id → I replace the placeholder in the Build Query SQL and redeploy.

## Next steps (next session / Ed) — in order

1. **(Ed/Cameron)** GHL UI: create *contact* custom field `Originating SDR` (text). Store the SDR's GHL user id.
2. **(Ed)** GHL workflow editor: in `LT - Opportunity Owner Alignment` (`b26326a5-77af-4df8-8d86-3f636e73afe0`, v7 — the workflow that branches "Owner is Jason"/"Owner is Marc" on `assignedTo` and writes the routing stamps `opportunity_owner_sync`/`opportunity_owner_change`), add a first step BEFORE the owner flip: set `Originating SDR` = `{{opportunity.assignedTo}}` (pre-flip owner = the SDR). If the trigger can't expose the pre-flip owner, use the per-SDR booking-link fallback (`?sdr=<userid>`).
3. **(Ed → assistant)** send the new field's GHL id. Assistant then: replace `__ORIGINATING_SDR_FIELD_ID__` in the Build Query SQL of Exec Summary `Bukc0mgOD2r7V6ED`, PUT/deploy, re-fetch to verify, and confirm real SDR attribution (dry-run on Postgres first).
4. **(assistant)** cleanup: remove remaining `_tmp_*` files/logs from the diagnosis phase (26 files), keep `local-scripts/_vps_psql.py` (reusable read-only psql-over-SSH runner).
5. **(Ed)** approve the staged durable memory entry (pending_id `75849f49`) about this fix (see Memory pending).

## Out of scope / known limits

- Historical bookings: unrecoverable (no SDR data anywhere, incl. GHL live) — fix is
  future-only.
- If the booking handoff workflow cannot expose the pre-flip owner, the tracking-param
  fallback (per-SDR links) becomes the capture mechanism — decisions needed from Ed.
- No changes to the Appointments Ingest (`yWZVSqEcjTbMT3kG`), Contacts Ingest, or the
  GHL API key/token pool.

## Live anchors (verified 2026-09-09)

- Regulated Ads calendar: `SrtXcFVyea7pFl3nTiIK` (Cameron's).
- SDRs: Jason `yU85G6kfhtW4vUtx3QE6`, Marc `sqGx5rp3oAUG610NXyjU`; Cameron
  `03p5GatJBH7i9zjMaIzm`; Janvi `ck6TRlU3wnTmMxuVpn5F` (marketing, non-SDR).
- Exec Summary workflow: `Bukc0mgOD2r7V6ED` (Build Query node holds the SQL).
- Contacts Ingest: `osIJOgBmWITF5Yuv` (hourly). Appointments Ingest: `yWZVSqEcjTbMT3kG`.
- Live CTE bodies captured verbatim in temp: `lt_Build_Query.js`.
# Superseded by 2026-09-10 Booking Webhook Implementation

This document records the original Option A design and is retained for historical traceability. The deployed implementation does **not** stamp the field from `LT - Opportunity Owner Alignment` and does **not** use the placeholder below. The live path is documented in `docs/sessions/2026-09-10-sdr-attribution-booking-webhook-closeout.md`:

- GHL workflow `Appointment with Cameron for Regulated Ads` sends `assignedSDR` to the booking webhook.
- n8n workflow `WL - Webhook to Slack Channel Update` (`lQTW0QPwBcf3o7j8`) stamps field `wBGXjev0rKowcfxTSWNa`.
- Exec Summary `Bukc0mgOD2r7V6ED` reads the live field id.
