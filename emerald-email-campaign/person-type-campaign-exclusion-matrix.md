# Emerald Person-Type Campaign Exclusion Matrix

Last updated: `2026-04-11`

## Purpose
- Prevent duplicate sends across Emerald person-type campaigns.
- Separate execution paths for:
  - backfill contacts that already received original emails 1-3
  - new contacts that should receive Intro first

## Backfill vs New Contacts
- Backfill path:
  - target tag: `seq emerald - intro backfill pending`
  - send one profile Intro only
  - then mark completion with:
    - `seq emerald - intro sent`
    - `seq emerald - intro backfill done`
- New-contact path:
  - Intro must send first
  - only after Intro sent, enroll into the original 3-email sequence

## Campaign Include/Exclude Rules

### Executive Campaigns
- Executives MSO
  - include: `cannabis-retail-mso-executive-1` OR `cannabis-retail-mso-executive-2`
  - exclude:
    - `cannabis-retail-mso-marketing-1`
    - `cannabis-retail-sso-marketing-1`
    - `cannabis-retail-mso-finance-1`
    - `cannabis-retail-sso-finance-1`
- Executives SSO
  - include: `cannabis-retail-sso-executive-1` OR `cannabis-retail-sso-executive-2`
  - exclude:
    - `cannabis-retail-mso-marketing-1`
    - `cannabis-retail-sso-marketing-1`
    - `cannabis-retail-mso-finance-1`
    - `cannabis-retail-sso-finance-1`

### Marketing Campaigns
- Marketing MSO
  - include: `cannabis-retail-mso-marketing-1`
  - exclude:
    - `cannabis-retail-mso-executive-1`
    - `cannabis-retail-mso-executive-2`
    - `cannabis-retail-sso-executive-1`
    - `cannabis-retail-sso-executive-2`
    - `cannabis-retail-mso-finance-1`
    - `cannabis-retail-sso-finance-1`
- Marketing SSO
  - include: `cannabis-retail-sso-marketing-1`
  - exclude:
    - `cannabis-retail-mso-executive-1`
    - `cannabis-retail-mso-executive-2`
    - `cannabis-retail-sso-executive-1`
    - `cannabis-retail-sso-executive-2`
    - `cannabis-retail-mso-finance-1`
    - `cannabis-retail-sso-finance-1`

### Finance Campaigns (New)
- Finance MSO
  - include: `cannabis-retail-mso-finance-1`
  - exclude:
    - `cannabis-retail-mso-executive-1`
    - `cannabis-retail-mso-executive-2`
    - `cannabis-retail-sso-executive-1`
    - `cannabis-retail-sso-executive-2`
    - `cannabis-retail-mso-marketing-1`
    - `cannabis-retail-sso-marketing-1`
- Finance SSO
  - include: `cannabis-retail-sso-finance-1`
  - exclude:
    - `cannabis-retail-mso-executive-1`
    - `cannabis-retail-mso-executive-2`
    - `cannabis-retail-sso-executive-1`
    - `cannabis-retail-sso-executive-2`
    - `cannabis-retail-mso-marketing-1`
    - `cannabis-retail-sso-marketing-1`

## Queue and Sequence Tags (Finance Added)
- Queue tags:
  - `enrollment queue - emerald - finance mso`
  - `enrollment queue - emerald - finance sso`
- Sequence progress tags:
  - `seq emerald - finance mso`
  - `seq emerald - finance sso`

## One-Time Dedupe Safety Rule
- Before adding a queue tag for any person-type campaign, remove any conflicting queue tags for other person types in the same operation.
- Never allow a contact to hold more than one Emerald enrollment queue tag at a time.
