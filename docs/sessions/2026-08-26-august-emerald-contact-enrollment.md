# August 2026 Emerald Contact Enrollment

Date: 2026-08-26

## Objective

Reconcile the cleaned August 2026 Brand, Agency, and Dispensary source files against the live GHL location, create only genuinely new contacts, and apply the approved campaign queue tags without overwriting existing contacts.

## Source Scope

The cleaned source set contained 2,620 precedence-resolved rows:

- Brand: 514
- Agency: 2,100
- Dispensaries: 6

Precedence was Brand, then Agency, then Dispensaries. The source-cleaning rules and exclusions are documented in `Contacts added August 25 2026/cleaned/August_2026_Emerald_Cleanup_Summary.md`.

## Live Actions

- The existing enrollment script was not used as the final execution manifest because its full 35k-contact scan was too slow and its generated action CSV became stale after partial runs.
- `scripts/reconcile_august_2026_emerald_live.ps1` was added for bounded reconciliation over contacts carrying `august_2026_emerald_contact`.
- The script was hardened to retry transient GHL/Cloudflare `429`, `502`, `503`, and `504` responses.
- Tag updates are grouped per contact and logged in `Contacts added August 25 2026/cleaned/August_2026_Emerald_Tag_Success.log`.
- Existing contacts are not overwritten.

## Final Verification

The final read-only dry run returned:

| Check | Result |
|---|---:|
| Source rows | 2,620 |
| Live August-tagged contacts | 3,769 |
| Unmatched source rows | 0 |
| Pending tag actions | 0 |
| Blocked/already-enrolled rows | 2,609 |

The bounded reconciliation created 36 additional email-only contacts. It completed 319 contact-level repair groups, representing 325 tag assignments: 313 Emerald MSO queue enrollments plus six Dispensary pool and six DAN queue assignments. The queue tags trigger the existing GHL enrollment automations; this work did not manually send email.

## Duplicate-Email Resolution

Five AURI source addresses returned GHL's duplicate-contact response. GHL identified all five as additional emails on existing contact `Amy Lund` (`ZtDaBakEXm0yPi2jW8mi`). They were intentionally skipped and will not be created or updated:

- `hstanislawski@auri.org`
- `adoering@auri.org`
- `aostlund@auri.org`
- `aowens@auri.org`
- `aharguth@auri.org`

## Follow-Up

- Do not execute the stale `August_2026_Emerald_Enrollment_Actions.csv` as a manifest.
- Use the reconciliation script for any future audit or rerun; it is idempotent and recognizes the five known additional-email duplicates.
- Monitor the normal GHL sequence and release-log workflows for downstream enrollment and delivery events.
