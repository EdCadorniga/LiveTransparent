# CSV Mapping Validation: postgres_ingestion

- CSV: `cold-outreach-prep/postgres/cold-outreach-all.dedup-email.workflow-input.csv`
- Workflow: `LT - Cold Outreach CSV -> Postgres Ingest (Staged) :: Build SQL (DryRun Safe)` (`kVCTmy1m8fEyP6Q7`)
- Headers: `72`
- Mapped fields: `72`
- Missing mapped fields: `0`
- Record rule pass (at least one id channel): `True`

## Field Matrix

| Target | Destination | Transform | Matched Header | Status |
|---|---|---|---|---|
| apollo_contact_id | postgres_column |  | Apollo Contact Id | matched |
| apollo_account_id | postgres_column |  | Apollo Account Id | matched |
| first_name | postgres_column |  | First Name | matched |
| last_name | postgres_column |  | Last Name | matched |
| title | postgres_column |  | Title | matched |
| company_name | postgres_column |  | Company Name | matched |
| company_name_for_emails | postgres_column |  | Company Name for Emails | matched |
| email | postgres_column |  | Email | matched |
| email_status | postgres_column |  | Email Status | matched |
| primary_email_source | postgres_column |  | Primary Email Source | matched |
| primary_email_verification_source | postgres_column |  | Primary Email Verification Source | matched |
| email_confidence | postgres_column | toNum | Email Confidence | matched |
| primary_email_catch_all_status | postgres_column |  | Primary Email Catch-all Status | matched |
| primary_email_last_verified_at | postgres_column | toTs | Primary Email Last Verified At | matched |
| seniority | postgres_column |  | Seniority | matched |
| departments | postgres_column |  | Departments | matched |
| sub_departments | postgres_column |  | Sub Departments | matched |
| contact_owner | postgres_column |  | Contact Owner | matched |
| work_direct_phone | postgres_column |  | Work Direct Phone | matched |
| home_phone | postgres_column |  | Home Phone | matched |
| mobile_phone | postgres_column |  | Mobile Phone | matched |
| corporate_phone | postgres_column |  | Corporate Phone | matched |
| other_phone | postgres_column |  | Other Phone | matched |
| stage | postgres_column |  | Stage | matched |
| lists | postgres_column |  | Lists | matched |
| last_contacted | postgres_column | toTs | Last Contacted | matched |
| account_owner | postgres_column |  | Account Owner | matched |
| employees_count | postgres_column | toInt | # Employees | matched |
| industry | postgres_column |  | Industry | matched |
| keywords | postgres_column |  | Keywords | matched |
| person_linkedin_url | postgres_column |  | Person Linkedin Url | matched |
| website | postgres_column |  | Website | matched |
| company_linkedin_url | postgres_column |  | Company Linkedin Url | matched |
| facebook_url | postgres_column |  | Facebook Url | matched |
| twitter_url | postgres_column |  | Twitter Url | matched |
| city | postgres_column |  | City | matched |
| state | postgres_column |  | State | matched |
| country | postgres_column |  | Country | matched |
| company_address | postgres_column |  | Company Address | matched |
| company_city | postgres_column |  | Company City | matched |
| company_state | postgres_column |  | Company State | matched |
| company_country | postgres_column |  | Company Country | matched |
| company_phone | postgres_column |  | Company Phone | matched |
| technologies | postgres_column |  | Technologies | matched |
| annual_revenue | postgres_column | toNum | Annual Revenue | matched |
| total_funding | postgres_column | toNum | Total Funding | matched |
| latest_funding | postgres_column |  | Latest Funding | matched |
| latest_funding_amount | postgres_column | toNum | Latest Funding Amount | matched |
| last_raised_at | postgres_column | toTs | Last Raised At | matched |
| subsidiary_of | postgres_column |  | Subsidiary of | matched |
| email_sent | postgres_column | toBool | Email Sent | matched |
| email_open | postgres_column | toBool | Email Open | matched |
| email_bounced | postgres_column | toBool | Email Bounced | matched |
| replied | postgres_column | toBool | Replied | matched |
| demoed | postgres_column | toBool | Demoed | matched |
| number_of_retail_locations | postgres_column | toInt | Number of Retail Locations | matched |
| secondary_email | postgres_column |  | Secondary Email | matched |
| secondary_email_source | postgres_column |  | Secondary Email Source | matched |
| secondary_email_status | postgres_column |  | Secondary Email Status | matched |
| secondary_email_verification_source | postgres_column |  | Secondary Email Verification Source | matched |
| tertiary_email | postgres_column |  | Tertiary Email | matched |
| tertiary_email_source | postgres_column |  | Tertiary Email Source | matched |
| tertiary_email_status | postgres_column |  | Tertiary Email Status | matched |
| tertiary_email_verification_source | postgres_column |  | Tertiary Email Verification Source | matched |
| primary_intent_topic | postgres_column |  | Primary Intent Topic | matched |
| primary_intent_score | postgres_column | toNum | Primary Intent Score | matched |
| secondary_intent_topic | postgres_column |  | Secondary Intent Topic | matched |
| secondary_intent_score | postgres_column | toNum | Secondary Intent Score | matched |
| qualify_contact | postgres_column |  | Qualify Contact | matched |
| tags | postgres_column |  | Tags | matched |
| source_sheet | postgres_column |  | source_sheet | matched |
| source_segment | postgres_column |  | source_segment | matched |

## Unmatched CSV Headers

- none
