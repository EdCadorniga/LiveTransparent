# CSV Mapping Validation: ghl_ingestion

- CSV: `cold-outreach-prep/ghl/cold-outreach-all.dedup-email.ghl.csv`
- Workflow: `LT - Cold Outreach CSV -> GHL Import (DryRun, Staged) :: Import Contacts + Tags` (`T28iLcm4Hszo19MG`)
- Headers: `25`
- Mapped fields: `22`
- Missing mapped fields: `0`
- Record rule pass (at least one id channel): `True`

## Field Matrix

| Target | Destination | Transform | Matched Header | Status |
|---|---|---|---|---|
| firstName | ghl_standard |  | First Name | matched |
| lastName | ghl_standard |  | Last Name | matched |
| email | ghl_standard |  | Email | matched |
| phone | ghl_standard |  | Phone | matched |
| companyName | ghl_standard |  | Company Name | matched |
| address1 | ghl_standard |  | Company Address | matched |
| website | ghl_standard |  | Website | matched |
| city | ghl_standard |  | City | matched |
| state | ghl_standard |  | State | matched |
| country | ghl_standard |  | Country | matched |
| tags | ghl_tags |  | Tags | matched |
| Title | ghl_custom |  | Title | matched |
| Company Phone | ghl_custom |  | Company Phone | matched |
| Apollo Person LinkedIn URL | ghl_custom |  | Person Linkedin Url | matched |
| Apollo Company LinkedIn URL | ghl_custom |  | Company Linkedin Url | matched |
| Apollo Facebook URL | ghl_custom |  | Facebook Url | matched |
| Apollo Twitter URL | ghl_custom |  | Twitter Url | matched |
| Apollo Industry | ghl_custom |  | Industry | matched |
| Apollo Company Employees | ghl_custom | toNum | # Employees | matched |
| Apollo Annual Revenue | ghl_custom | toNum | Annual Revenue | matched |
| source_sheet | workflow_meta_only |  | source_sheet | matched |
| source_segment | workflow_meta_only |  | source_segment | matched |

## Unmatched CSV Headers

- none
