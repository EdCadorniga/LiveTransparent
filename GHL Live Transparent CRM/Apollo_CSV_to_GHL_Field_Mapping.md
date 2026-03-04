# Apollo CSV -> GHL Field Mapping (Live Transparent)

## Scope
This document defines the canonical mapping from Apollo CSV export headers to GHL contact fields/custom fields for the Live Transparent sub-account.

- Location ID: `Zwz4relUXVPxx8uohnjV`
- Updated: `2026-03-04`
- Source CSV: `Exported Apollo Contacts who have opened an email at least once - Contacts who have opened an email (2).csv`
- Related workflows:
  - `zsaUaazamrkg1M47` (`GHL Import - Apollo Sheet Opened Email`) - deleted on `2026-02-26` during archived-workflow cleanup
  - `WmKAhG7mIaXonNsh` (`GHL Apollo Enrichment - Webhook Intake (Sheet First)`)
  - `WuxgTa0EEL1mb2SA` (`GHL Apollo Enrichment - Phone Webhook Intake (Staged)`)
  - `U7c6byTLXAMgcS75` (`GHL Apollo Phone Enrichment - Callback Handler V4`)
  - `T28iLcm4Hszo19MG` (`LT - Cold Outreach CSV -> GHL Import (DryRun, Staged)`)

## Recent Update (`2026-02-20`)
- Applied live workflow update to `T28iLcm4Hszo19MG` to align `Import Contacts + Tags` with the canonical field mapping in this document.
- Removed `$env` dependency used in workflow field mapping logic (source of prior dry-run failure).
- Added company address mapping to standard GHL `address1` using CSV aliases:
  - `Address`
  - `address1`
  - `Company Address`
  - `company_address`
- Added city/state/country fallback aliases to ensure canonical GHL standard fields always populate when company-prefixed columns are present:
  - `city`: includes `Company City` / `company_city`
  - `state`: includes `Company State` / `company_state`
  - `country`: includes `Company Country` / `company_country`
- Canonical reusable mapping spec updated at `cold-outreach-prep/mapping/apollo_csv_mappings.json`.
- Canonical validator updated at `cold-outreach-prep/scripts/validate_apollo_csv_mapping.py`:
  - alias-covered headers now count as matched coverage to avoid false unmatched header reporting when synonym columns are used.

## Canonical Header Standard
Use the renamed `Apollo ...` headers in CSV/Sheet for stable matching.

## Core Contact Field Mapping
| CSV Header | GHL Target | Target Type | Notes |
|---|---|---|---|
| `First Name` | `firstName` | Standard Contact Field | Direct map |
| `Last Name` | `lastName` | Standard Contact Field | Direct map |
| `Email` | `email` | Standard Contact Field | Primary dedupe key |
| `Phone` | `phone` | Standard Contact Field | Use as main phone |
| `Company Name` | `companyName` | Standard Contact Field | Company label on contact |
| `Address` | `address1` | Standard Contact Field | Company address currently stored on contact |
| `City` | `city` | Standard Contact Field | Company city currently stored on contact |
| `State` | `state` | Standard Contact Field | Company state currently stored on contact |
| `Country` | `country` | Standard Contact Field | Company country currently stored on contact |

## Extra Contact Custom Fields (Non-Apollo)
| CSV Header | GHL Target Field Name | Data Type |
|---|---|---|
| `Title` | `Title` | `TEXT` |
| `Company Name for Emails` | `Company Name for Emails` | `TEXT` |
| `Corporate Phone` | `Corporate Phone` | `TEXT` |
| `Company Phone` | `Company Phone` | `TEXT` |
| `Lists` | `Lists` | `TEXT` |
| `Batch_Upload` | `Batch_Upload` | `TEXT` |

## Apollo Custom Field Mapping
| Apollo CSV Header | GHL Custom Field Name | Data Type |
|---|---|---|
| `Apollo Contact Id` | `Apollo Contact Id` | `TEXT` |
| `Apollo Account Id` | `Apollo Account Id` | `TEXT` |
| `Apollo Email Status` | `Apollo Email Status` | `TEXT` |
| `Apollo Primary Email Source` | `Apollo Primary Email Source` | `TEXT` |
| `Apollo Primary Email Verification Source` | `Apollo Primary Email Verification Source` | `TEXT` |
| `Apollo Email Confidence` | `Apollo Email Confidence` | `NUMERICAL` |
| `Apollo Primary Email Catch-all Status` | `Apollo Primary Email Catch-all Status` | `TEXT` |
| `Apollo Primary Email Last Verified At` | `Apollo Primary Email Last Verified At` | `DATE` |
| `Apollo Seniority` | `Apollo Seniority` | `TEXT` |
| `Apollo Departments` | `Apollo Departments` | `TEXT` |
| `Apollo Sub Departments` | `Apollo Sub Departments` | `TEXT` |
| `Apollo Company Employees` | `Apollo Company Employees` | `NUMERICAL` |
| `Apollo Industry` | `Apollo Industry` | `TEXT` |
| `Apollo Keywords` | `Apollo Keywords` | `TEXT` |
| `Apollo Person LinkedIn URL` | `Apollo Person LinkedIn URL` | `TEXT` |
| `Apollo Company LinkedIn URL` | `Apollo Company LinkedIn URL` | `TEXT` |
| `Apollo Facebook URL` | `Apollo Facebook URL` | `TEXT` |
| `Apollo Twitter URL` | `Apollo Twitter URL` | `TEXT` |
| `Apollo Technologies` | `Apollo Technologies` | `TEXT` |
| `Apollo Annual Revenue` | `Apollo Annual Revenue` | `NUMERICAL` |
| `Apollo Total Funding` | `Apollo Total Funding` | `NUMERICAL` |
| `Apollo Latest Funding` | `Apollo Latest Funding` | `TEXT` |
| `Apollo Latest Funding Amount` | `Apollo Latest Funding Amount` | `NUMERICAL` |
| `Apollo Last Raised At` | `Apollo Last Raised At` | `DATE` |
| `Apollo Subsidiary Of` | `Apollo Subsidiary Of` | `TEXT` |
| `Apollo Secondary Email` | `Apollo Secondary Email` | `TEXT` |
| `Apollo Secondary Email Source` | `Apollo Secondary Email Source` | `TEXT` |
| `Apollo Secondary Email Status` | `Apollo Secondary Email Status` | `TEXT` |
| `Apollo Secondary Email Verification Source` | `Apollo Secondary Email Verification Source` | `TEXT` |
| `Apollo Tertiary Email` | `Apollo Tertiary Email` | `TEXT` |
| `Apollo Tertiary Email Source` | `Apollo Tertiary Email Source` | `TEXT` |
| `Apollo Tertiary Email Status` | `Apollo Tertiary Email Status` | `TEXT` |
| `Apollo Tertiary Email Verification Source` | `Apollo Tertiary Email Verification Source` | `TEXT` |
| `Apollo Primary Intent Topic` | `Apollo Primary Intent Topic` | `TEXT` |
| `Apollo Primary Intent Score` | `Apollo Primary Intent Score` | `NUMERICAL` |
| `Apollo Secondary Intent Topic` | `Apollo Secondary Intent Topic` | `TEXT` |
| `Apollo Secondary Intent Score` | `Apollo Secondary Intent Score` | `NUMERICAL` |
| `Apollo Qualify Contact` | `Apollo Qualify Contact` | `TEXT` |

## Notes
- Keep header names exact to avoid mapping drift.
- `WmKAhG7mIaXonNsh` now supports both old and new header naming, but this document is the canonical standard.
- Company-level normalization (single company record for many contacts) is deferred to a later company import phase.

## Live Enrichment Runtime Notes (`2026-03-04`)
These are non-CSV runtime mapping rules used by the Apollo enrichment workflows.

- GHL phone updates:
- Standard field `phone` is updated when a normalized candidate is found.
- Phone enrichment intake is callback-driven for direct phone reveal:
- intake path `ghl-apollo-phone-enrichment-intake-v3`
- callback path `ghl-apollo-phone-enrichment-callback-v4`
- intake leaves contacts in `queued` with reason `awaiting_callback` when Apollo returns a matched person but no acceptable direct phone synchronously.

- Candidate source priority:
- intake prioritizes person-level direct phone sources and nested `person.contact.phone_numbers` / `person.phone_numbers`.
- callback V4 parses Apollo webhook payloads from `body.people[0]`, `body.data.people[0]`, or `body.person`.
- organization/company phone sources are stored as company metadata but are not used as direct phone candidates in the callback-driven phone workflow.
- any candidate matching existing GHL `Corporate Phone` or `Company Phone` is discarded before phone write/update.

- Phone enrichment status fields:
- `Apollo Phone Enrichment Status` (`contact.apollo_phone_enrichment_status`) -> `queued` / `enriched` / `no_match` / `error`
- `Apollo Phone Enriched At` (`contact.apollo_phone_enriched_at`) -> `YYYY-MM-DD`

- Guardrail field updates on successful enrichment:
- `Contact already Enriched` -> `Yes`
- `Enrich via Apollo` -> `No`
- `Enrich Phone via Apollo` -> `No`
- `Apollo Contact Id` is written only on successful phone enrichment and prefers Apollo `contact.id` when available, otherwise falls back to `person.id`.

- Additional runtime mappings:
- `Title` custom field is populated from Apollo person title when present.
- TEXT custom fields are trimmed and DATE fields normalized to reduce GHL update failures.
- intake appends debugging output to the `Enriched Contacts` Google Sheet, including `enrichment_status`, `enrichment_reason`, `apollo_error_status`, `apollo_error`, `duplicate_phone_conflict`, `normalized_phone`, `found_phone`, `update_request_body_used`, and `raw_result`.

- Postgres upsert behavior:
- `Apollo_Contacts` now includes top-level `phone` in addition to `ingest_record`.
