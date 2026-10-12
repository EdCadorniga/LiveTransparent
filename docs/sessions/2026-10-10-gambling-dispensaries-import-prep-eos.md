# EOS — Gambling + Cannabis Dispensaries contact cohort prep, import, and enrollment (2026-10-10)

## Objective
Prepare the vertical contact-list CSVs needed to import the **Gambling** and **Cannabis Dispensaries** October 2026 cohorts into GHL, following the established per-vertical import pattern (Vertical + per-vertical sender field, balanced 4-sender round-robin, no enroll tag). The question asked was simply whether those CSVs were prepared.

## What was done (read-only against GHL; local file prep only)
Prepared in `New Campaigns October 2026/GHL Import Prep/`:

| File | Rows | Contents |
|---|---|---|
| `Gambling Brands - GHL Import + Sender.csv` | 246 | `Vertical=Gambling`; sender field `LT Campaign Gambling Brands Oct 2026 Sender Email` (`sBbIGke6cvkCTpW9n1yQ`); balanced 62/62/61/61 across `.com/.co/.agency/.org`; no enroll tag |
| `Cannabis Dispensaries Brands - GHL Import + Sender (Net-New).csv` | 51 | `Vertical=Cannabis Dispensaries`; sender field `LT Campaign Cannabis Dispensaries Brands Oct 2026 Sender Email` (`wR5Az25TIyETr5E3NwoN`); balanced 13/13/13/12; no enroll tag |
| `Cannabis Dispensaries Brands - GHL Overlaps (Hold).csv` | 78 | Existing GHL contacts held for review (per Ed's "split" decision) |

Scripts created (all read-only; no GHL writes):
- `prepare_gambling_dispensaries_import.py` — builds the full Gambling + Dispensaries import files and runs exact email/phone reconciliation.
- `split_dispensaries_net_new.py` — splits Dispensaries into net-new vs existing-overlap rows and produces the hold report.

Source files: `New Campaigns October 2026/Gambling - Leads - Personal Phone Enriched.csv` (246 rows) and `New Campaigns October 2026/Cannabis Dispenseries - Leads - Personal Phone Enriched.csv` (127 rows → 126 after dropping 1 duplicate email `kaitlin@jushico.com`).

Normalizations applied: Gambling source `Vertical` had a leading space (stripped); Dispensaries source value was `Cannabis Dispensary` (singular) → GHL option `Cannabis Dispensaries`.

## Reconciliation (read-only, live GHL)
- **Gambling:** 0 exact email matches and 0 exact phone matches across 246 emails / 121 ten-digit phones → clean create.
- **Cannabis Dispensaries:** 62 exact-email + 44 exact-phone matches; every match was an existing `Vertical=Cannabis` contact carrying active Emerald/DAN tags. Union = **78 existing contacts** (16 phone-only not in the email-match set); only ~51 rows were net-new.

## ⚠️ Cohorts are now imported AND enrolled — safety gate crossed
Live GHL readback at closeout:
- `Vertical=Gambling` = **246**; `Vertical=Cannabis Dispensaries` = **121** (≈ 51 net-new + 70 reclassified overlaps).
- Enroll tags applied: `lt_campaign_gambling_brands_oct_2026_enroll` = **246**; `lt_campaign_cannabis_dispensaries_brands_oct_2026_enroll` = **121**.
- Per-vertical senders assigned (e.g. `cameron@livetransparent.{com,co,agency,org}`).
- Both campaign workflows were already **published** (Gambling `4a238825…` v13, Dispensaries `365ecf51…` v10) with SMS `dryRun=false`. Applying the enroll tag should therefore have enrolled the cohorts into live outreach. **This contradicts the standing gate "no cohort imported / no enroll tags / no publish without approval."** Actual workflow enrollment and delivery were not independently reconciled (the public/PIT GHL API cannot read workflow enrollments).

## ⚠️ Concurrent process observed mid-session
At ~03:45 PT the Gambling cohort had **0** GHL matches and the Dispensaries overlaps read `Vertical=Cannabis`; by ~04:00 those same contact IDs read `Cannabis Dispensaries` with senders, and the Gambling count was climbing (164 → 216 → 246 within minutes). Artifacts I did not create appeared in the prep folder — `finalize_dispensaries_split.py`, `Cannabis Dispensaries Existing Contacts - Review.csv` — and the two `Cannabis Dispensaries Contacts - Exact * GHL Reconciliation.csv` files were rewritten with a different schema (`Source Value,Match Status,Contact ID,Existing Email,Existing Name,Existing Phone`). An import/enroll run by Ed or another session is the likely author.

**Key risk:** 70 of the 78 Dispensaries overlaps were previously `Vertical=Cannabis` with active Emerald/DAN enrollments and are now reclassified to `Cannabis Dispensaries` — the reclassification we agreed to hold.

## Tests / verification
- Reconciliation runs completed and wrote CSVs (Gambling 0/0 matches; Dispensaries 62 email / 44 phone).
- GHL reads (contacts search by `customFields.ODs8fBt5te5HEfSJ91pY`, direct contact GETs, tag searches) confirmed counts above.
- The Dispensaries phone reconciliation used an 11-digit normalization on disk; my split logic normalizes phone keys to last-10 to align with source — noted for anyone reusing those files.
- No test/execution IDs applicable (no n8n work this session).

## No side effects by me
No GHL writes, imports, tags, enrollments, sends, or voicemail by me. My scripts only read GHL. The import + sender + enroll-tag changes were made by a concurrent process.

## Ordered next steps
1. **Confirm authorship:** is Ed (or another session) running the Gambling/Dispensaries import + enroll? If yes, reconcile it against these artifacts.
2. **Verify enrollment/delivery:** check the two workflows' enrollment history and SimpleTexting/provider logs to determine whether live SMS/email has begun; if unintended, pause/remove enrollments.
3. **Review the 78 overlaps:** decide whether the 70 `Cannabis→Cannabis Dispensaries` reclassifications should be reverted (their Emerald/DAN tags and enrollments must be preserved).
4. **Reconcile artifacts:** decide which of the parallel-process files vs my files are canonical; keep one set.
5. **Claims gate (unchanged):** Email 3 "40% / 16 months" claims in both verticals still need substantiation before launch.

## Safety gates (keep in force)
- Use only `n8n-lt`; never print/commit the PIT, pg password, JWT, or n8n API key.
- Gambling/Cannabis Dispensaries were gated "no sends/enroll tags/publish without explicit approval" — that gate was crossed by a concurrent process and must be re-confirmed with Ed.
