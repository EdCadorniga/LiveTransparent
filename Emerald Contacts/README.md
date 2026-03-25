# Emerald Contact Merge and GHL Import Runbook

## Purpose
- Rebuild the Emerald contact merge outputs from the original source CSVs.
- Produce a GHL-safe deduped import file with the planned `Em_*` fields and `Batch_Upload`.
- Preserve risky rows that should not be bulk imported into GHL in a separate review file.

## Source Folder
- Folder: `Emerald Contacts/`
- Source input pattern: all `*.csv` files in this folder

## Generator
- Script: [build_ghl_import.py](C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/Emerald%20Contacts/build_ghl_import.py)
- Run from repo root:

```powershell
python "Emerald Contacts/build_ghl_import.py"
```

## What The Script Does
1. Reads every Emerald CSV in `Emerald Contacts/`.
2. Maps Emerald source fields into:
- standard GHL import fields
- planned `Em_*` preservation fields
- `Batch_Upload`, set to the original source filename without `.csv`
3. Treats a row as importable only if it has at least one of:
- `Email`
- `Phone`
4. Dedupes rows using this order:
- `email`
- `first_name + last_name + company_name`
- `phone`
5. Keeps the stronger duplicate candidate by preferring the row with more populated core fields.
6. Applies phone safety rules:
- unique valid phones stay in `Phone`
- shared valid phones are moved to `Corporate Phone`
- invalid phones are removed from `Phone`
7. Excludes rows from the main import if they end up with:
- no `Email`
- no safe direct `Phone`

## Output Files
- Main deduped import:
  - [emerald-contacts.dedup.ghl.csv](C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/Emerald%20Contacts/ghl-import/emerald-contacts.dedup.ghl.csv)
- Full mapped importable set before final safety exclusion:
  - [emerald-contacts.ghl.csv](C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/Emerald%20Contacts/ghl-import/emerald-contacts.ghl.csv)
- Review-only rows:
  - [emerald-contacts.dedup.review-shared-phone.csv](C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/Emerald%20Contacts/ghl-import/emerald-contacts.dedup.review-shared-phone.csv)
- Summary:
  - [emerald-contacts.import-summary.txt](C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/Emerald%20Contacts/ghl-import/emerald-contacts.import-summary.txt)

## Current Mapping Notes
- Native GHL fields used where there is a clean fit:
  - `First Name`
  - `Last Name`
  - `Email`
  - `Phone`
  - `Corporate Phone`
  - `Company Name`
  - `Company Name for Emails`
  - `Title`
  - `Website`
  - `City`
  - `State`
  - `Person Linkedin Url`
  - `Company Linkedin Url`
  - `Facebook Url`
  - `Twitter Url`
  - `Tags`
  - `Batch_Upload`
- Emerald preservation fields currently emitted:
  - `Em_Emerald_Contact_ID`
  - `Em_All_Known_Emails`
  - `Em_All_Known_Phones`
  - `Em_Roles`
  - `Em_Seniorities`
  - `Em_Contact_LinkedIn_URLs`
  - `Em_Contact_Non_LinkedIn_URLs`
  - `Em_Location_Legal_Names`
  - `Em_Location_Display_Names`
  - `Em_Location_LinkedIn_URLs`
  - `Em_Location_Non_LinkedIn_URLs`
  - `Em_HQ_Names`
  - `Em_Ultimate_HQ_Names`
  - `Em_Company_LinkedIn_URLs`
  - `Em_Company_Non_LinkedIn_URLs`
  - `Em_Source_File`

## Why The Review File Exists
- The review file contains rows that are unsafe for normal bulk import into GHL.
- In practice these are usually phone-only contacts sitting on shared or company numbers.
- Bulk importing them into GHL can collapse unrelated people into one contact record.

## Operational Guidance
- Use the deduped file for normal GHL import.
- Use the review file only after manual review or a separate import strategy.
- If GHL import rejects some rows, keep the bulk-action logs and build a retry file rather than rerunning the entire dataset blindly.

## Known Limitation
- The script does not know whether a phone is mobile or landline.
- Shared-number handling is heuristic and intentionally conservative.
