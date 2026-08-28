# August 2026 Emerald Contact Cleanup and Enrollment

The source files were compared against 31,804 contacts fetched from the live GHL location. Existing contacts were excluded rather than updated.

## Final Import Counts

| Category | Count | Tags |
|---|---:|---|
| Brand | 514 | `brands_pool`, `emerald`, `august_2026_emerald_contact` |
| Agency | 2,100 | `agency_pool`, `emerald`, `august_2026_emerald_contact` |
| Dispensaries | 6 | `dispensaries_pool`, `emerald`, `august_2026_emerald_contact` |
| **Total** | **2,620** | |

## Exclusion Breakdown

| Reason | Rows | Meaning |
|---|---:|---|
| Existing phone | 5,049 | The normalized phone already belongs to a GHL contact. This is the largest group because GHL rejects duplicate phone numbers. |
| Duplicate source Emerald ID | 2,612 | The same Emerald Contact ID appeared more than once across the three source files. The first winning category by precedence was retained. |
| Duplicate source phone | 1,891 | The phone appeared more than once among otherwise new source rows. The first winning category by precedence was retained. |
| Missing email and phone | 574 | No safe GHL deduplication key or usable contact channel was available. |
| Existing email | 217 | The normalized email already belongs to a GHL contact. |
| Existing Emerald ID | 79 | The Emerald Contact ID was already stored on a GHL contact. |
| Duplicate source email | 18 | The email appeared more than once among otherwise new source rows. |
| **Total excluded** | **10,440** | |

## Precedence Effects

The source files overlap heavily. Category precedence was applied in this order:

1. Brand
2. Agency
3. Dispensaries

The Agency and Dispensaries files share approximately 5,695 Emerald Contact IDs, so most overlapping records correctly resolved to Agency. This explains why only six Dispensaries records survived after deduplication and GHL collision checks. No contact receives more than one pool tag.

## Identifier Rules

- Emerald Contact ID was checked first for existing and source duplicates.
- Email was normalized by trimming whitespace and lowercasing.
- Phone was normalized to E.164-style format where possible.
- Phone values longer than 15 digits were rejected as invalid rather than imported.
- Source rows may contain an email-only contact or phone-only contact, but never a row with neither.
- Existing GHL contacts were checked using primary and additional email values, primary phone, and the Emerald Contact ID custom field.

## Validation

- Output email duplicates: 0
- Output phone duplicates: 0
- Output invalid phone lengths: 0
- Output rows missing both email and phone: 0
- The initial import pass created email-only contacts where the source email was new and GHL had rejected the source phone as a duplicate. Existing contacts were not overwritten.

## Final Live Reconciliation (2026-08-26)

- Source rows reconciled: `2,620`
- Live August-tagged contacts observed: `3,769`
- Additional email-only contacts created during the bounded reconciliation: `36`
- Successful campaign/pool tag updates: `319` contact-level repair groups and `325` tag assignments, including `313` Emerald MSO queue enrollments and `6` Dispensary pool plus DAN queue enrollments
- Final dry-run unmatched records: `0`
- Final dry-run pending tag actions: `0`
- Records skipped because they were already enrolled, suppressed, or otherwise blocked: `2,609`

### Intentional Existing-Contact Skips

The following five source emails were rejected by GHL because they already exist as additional emails on contact `Amy Lund` (`ZtDaBakEXm0yPi2jW8mi`). No duplicate contacts or updates were made for them:

- `hstanislawski@auri.org`
- `adoering@auri.org`
- `aostlund@auri.org`
- `aowens@auri.org`
- `aharguth@auri.org`

The reconciliation script records these as known duplicate additional-email skips and will not retry creation.

## Operational Artifacts

- Reconciliation script: `scripts/reconcile_august_2026_emerald_live.ps1`
- Tag success log: `Contacts added August 25 2026/cleaned/August_2026_Emerald_Tag_Success.log`
- The generated `August_2026_Emerald_Enrollment_Actions.csv` predates the final bounded reconciliation and should not be used as an execution manifest.
