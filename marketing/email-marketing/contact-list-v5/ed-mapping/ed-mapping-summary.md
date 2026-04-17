# Ed Mapping Tagging Summary

- Source: `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\Contact List.v5.xlsx`
- Sheet: `Masterlist` (header row `2`)
- Output CSV: `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\contact-list-v5\ed-mapping\ed-mapping-tags.by-email.csv`
- Import CSV (`Email`,`Tags`): `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\contact-list-v5\ed-mapping\ed-mapping-tags.ghl-import.csv`
- Conflict review CSV: `C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\contact-list-v5\ed-mapping\ed-mapping-tags.conflicts.csv`
- Unique emails exported: `16250`
- Emails with mapping conflicts: `50`
- Emails flagged Do Not Contact: `907`

## Unique Mapping Counts (By Email)

- `DO NOT CONTACT`: `907`
- `MSO Executive`: `3928`
- `MSO Finance`: `297`
- `MSO Marketing`: `635`
- `MSO Retail & Sales`: `320`
- `SSO Executive`: `7489`
- `SSO Finance`: `594`
- `SSO Marketing`: `1720`
- `SSO Retail & Sales`: `410`

## Campaign Guard Rule

- Add a first branch/if-condition before every email send.
- Block send if contact has either:
  - `do not contact`
  - `do not nurture`
- For persona-specific sends, require the exact persona tag and exclude other persona tags.

## Import Notes

- Use `Email` + `Tags` from the CSV for bulk tag update.
- In GHL import, choose tag behavior that appends tags (not overwrite), then dedupe tags.
- Contacts with `Has Mapping Conflict = Yes` should be reviewed before persona drip enrollment.