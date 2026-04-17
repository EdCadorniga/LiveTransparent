# Cold Outreach GHL Import Mapping Checklist

## Import File
- Preferred file (full Apollo field coverage): `cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.ui-full-apollo.csv`
- Alternate compact file: `cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.csv`
- Rows: `1413` (email-deduplicated)
- Tags present on all rows: `100M+, cold-outreach` or `10-100M, cold-outreach`

## Required GHL Mapping (UI Import)
- `First Name` -> `First Name` (standard)
- `Last Name` -> `Last Name` (standard)
- `Email` -> `Email` (standard)
- `Phone` -> `Phone` (standard)
- `Company Name` -> `Company Name` (standard)
- `Tags` -> `Tags` (standard, comma-delimited)

## Recommended Standard Mapping
- `Website` -> `Website` (standard)
- `City` -> `City` (standard)
- `State` -> `State` (standard)
- `Country` -> `Country` (standard)

## Recommended Custom Field Mapping
- `Title` -> `Title`
- `Company Address` -> `Apollo Company Address` (or `Company Address` custom field)
- `Company City` -> `Apollo Company City`
- `Company State` -> `Apollo Company State`
- `Company Country` -> `Apollo Company Country`
- `Company Phone` -> `Apollo Company Phone`
- `Person Linkedin Url` -> `Apollo Person LinkedIn URL`
- `Company Linkedin Url` -> `Apollo Company LinkedIn URL`
- `Facebook Url` -> `Apollo Facebook URL`
- `Twitter Url` -> `Apollo Twitter URL`
- `Industry` -> `Apollo Industry` (or `Industry` custom field)
- `# Employees` -> `Apollo Company Employees`
- `Annual Revenue` -> `Apollo Annual Revenue`
- `source_sheet` -> `Source Sheet` (create custom field if not present)
- `source_segment` -> `Source Segment` (create custom field if not present)

## GHL Import Settings
- Use `email` as primary dedupe key.
- If prompted for duplicate handling, select update/merge existing contacts.
- Keep tags enabled as comma-separated values.
- Do not map columns you do not need for this batch.

## Post-Import QA
- Verify at least one imported contact from each segment tag:
  - `100M+, cold-outreach`
  - `10-100M, cold-outreach`
- Filter contacts by `source_sheet` and `source_segment` to confirm both were mapped.
- Spot-check 20 contacts for:
  - email populated
  - expected tags
  - company/title fields
