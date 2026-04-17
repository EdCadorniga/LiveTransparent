# Emerald Finance Dispatch Enable Checklist

Last updated: `2026-04-14`

## Current Status
- Finance source tags and queue/sequence tags already exist in GHL:
  - `cannabis-retail-mso-finance-1`
  - `cannabis-retail-sso-finance-1`
  - `enrollment queue - emerald - finance mso`
  - `enrollment queue - emerald - finance sso`
  - `seq emerald - finance mso`
  - `seq emerald - finance sso`
- Finance intro templates are already uploaded in folder `Emerald targeted by profile`:
  - `MSO Finance - Open a More Reliable Revenue Channel` (`69d8cca8f4385cf6dceabf4e`)
  - `SSO Finance - Reduce Dependence on Too Few Revenue Channels` (`69d8ccaea4e06acf3c2484cf`)
- Live n8n ingest currently buckets only executive/marketing tags, so finance contacts are not classified unless this is patched.

## Required Changes
1. Update Emerald ingest bucket classifier to include finance tags:
   - `cannabis-retail-mso-finance-1` -> `finance_mso` + `Enrollment Queue - Emerald - Finance MSO`
   - `cannabis-retail-sso-finance-1` -> `finance_sso` + `Enrollment Queue - Emerald - Finance SSO`
2. Update Emerald dispatcher ordering/map to include finance buckets:
   - ordering: `executives_mso`, `executives_sso`, `marketing_mso`, `marketing_sso`, `finance_mso`, `finance_sso`
   - queue map: add `finance_mso` and `finance_sso`
3. In GHL, create/publish 2 finance sequence workflows (or duplicate executive flows):
   - `WL - Seq - Cannabis Ads Emerald - Finance MSO`
   - `WL - Seq - Cannabis Ads Emerald - Finance SSO`
4. For each finance workflow, keep same first-3-email pattern as executive:
   - Email #1: finance template (MSO/SSO finance template ID above)
   - Email #2: same as corresponding executive workflow Email #2
   - Email #3: same as corresponding executive workflow Email #3
   - Keep `From Email = {{contact.marketing_sender_email}}`
   - Remove matching finance queue tag on entry, then add `Seq Enrolled - Emerald` and finance sequence tag

## Local Artifact Updates Included
- Finance bucket/map support added in:
  - [publish_emerald_campaign_workflows.py](/C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/emerald-email-campaign/artifacts/publish_emerald_campaign_workflows.py)
- Finance intro copy added in:
  - [emerald-sequence-copy-extract.txt](/C:/Users/edmon/OneDrive/Documents/Projects/LiveTransparent/emerald-email-campaign/emerald-sequence-copy-extract.txt)

## Important Data Note
- Current local snapshot file `Exported Emerald Contacts.csv` contains `0` finance-tagged rows.
- If finance contacts were added after that snapshot, re-export/re-ingest from GHL so `Emerald_Campaign_Contacts` gets finance rows.

## Validation Before Go-Live
1. Confirm `Emerald_Campaign_Contacts` has rows where `bucket IN ('finance_mso','finance_sso')`.
2. Dry-run dispatcher and confirm planned records include finance buckets.
3. Test one MSO finance and one SSO finance contact:
   - queue tag added by dispatcher
   - correct finance workflow triggers
   - first 3 emails execute (finance intro + executive email #2/#3 pattern)
4. Confirm no cross-enrollment with executive/marketing queue tags.
