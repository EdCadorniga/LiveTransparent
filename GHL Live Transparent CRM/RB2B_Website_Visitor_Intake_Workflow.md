# RB2B Website Visitor Intake Workflow

## Purpose
Capture RB2B webhook leads, reconcile/update contact data in GHL, apply qualification tags, store/update lead data in Postgres, and create a call task for Kevin.

## Live Workflow
- n8n workflow: `rb2b leads`
- Workflow ID: `3kjsIUeoEQFx26cC`
- Webhook path: `/webhook/rb2b_leads_v2`
- Test webhook path: `/webhook-test/rb2b_leads_v2`

## Input Payload (RB2B)
- `LinkedIn URL`
- `First Name`
- `Last Name`
- `Title`
- `Company Name`
- `Business Email`
- `Website`
- `Industry`
- `Employee Count`
- `Estimate Revenue`
- `City`
- `State`
- `Zipcode`
- `Seen At`
- `Referrer`
- `Captured URL`
- `Tags`

## Processing Logic
1. Normalize inbound fields and build `lead_key`.
- `lead_key = email:<business_email>` when email is present.
- Fallback key: `name:<full_name>|company:<company_name>`.

2. Find existing GHL contact.
- First attempt: duplicate search by email.
- Fallback: contacts query by full name and exact normalized full-name match.

3. Upsert/update GHL contact.
- If match exists: update existing contact record.
- If no match: create/upsert contact record.

4. Apply tags in GHL (append only).
- `rb2b_website_visitor`
- `mql`
- Tag action uses add-tags behavior, so existing tags are preserved.

5. Ensure Postgres table and upsert RB2B lead row.
- Table: `RB2B_Leads`
- Unique key: `lead_key`
- Existing rows are updated on conflict.

6. Create follow-up task in GHL.
- Title: `New RB2B contact - Call`
- Assigned to: Kevin (`7s3brzxGF4WSiz95DPkF`)
- Task is created against resolved `ghl_contact_id`.

## Data Stores
- GHL contact record:
  - core contact fields updated from RB2B payload
  - tags appended (`rb2b_website_visitor`, `mql`)
  - task created for Kevin

- Postgres table:
  - `RB2B_Leads`
  - fields include contact/profile/source attributes plus:
    - `ghl_contact_id`
    - `ghl_match_method`
    - `updated_at`

## Node Flow (Current)
- `Webhook` -> `Config` -> `Prepare + Upsert GHL Contact` -> `Upsert RB2B Lead Row` -> `Create Task - Kevin Call` -> `Result`
- `Config` also triggers `Ensure RB2B Leads Table` in a parallel branch.

## Known Guardrails
- Do not replace tags with `contacts_update-contact.body_tags`; use add-tags endpoint behavior only.
- Keep task URL bound to `ghl_contact_id` from `Prepare + Upsert GHL Contact` output to avoid empty `/contacts//tasks` calls.
- Keep `lead_key` non-null and stable; Postgres upsert depends on it.
