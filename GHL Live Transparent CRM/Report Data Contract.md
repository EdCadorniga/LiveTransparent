# Live Transparent Report Data Contract

## Purpose
This document defines the minimum data contract for the executive report.
Use it as the bridge between GA4, GSC, GHL, and the Postgres rollup layer.

## Source Systems
- GA4: traffic and on-site engagement
- GSC: organic search visibility
- GHL: leads, opportunities, pipeline movement, and revenue

## Required Identifiers
- GA4 property ID: pending from Cameron
- GA4 measurement ID: `G-YYF078K942`
- GA4 stream ID: `7792630179`
- GHL location ID: `Zwz4relUXVPxx8uohnjV`

## Reporting Dimensions
- report date
- source system
- channel
- source
- medium
- campaign
- landing page
- pipeline
- stage
- lead temperature
- identity / matching confidence

## GHL Fields Consumed by the Report
Use the live custom fields from the operating snapshot and warm-routing spec:
- `UTM Source First`
- `UTM Medium First`
- `UTM Campaign First`
- `UTM Content First`
- `UTM Term First`
- `UTM Source Last`
- `UTM Medium Last`
- `UTM Campaign Last`
- `UTM Content Last`
- `UTM Term Last`
- `UTM Landing Page First`
- `UTM Landing Page Last`
- `Warm Source`
- `Warm Trigger Type`
- `Lead Temperature`
- `LT Last Routing Channel`
- `LT Last Routing Reason`
- `LT Last Routed At`
- `LT Route Lock Until`
- `LT Routing Priority`
- `LT Last Event Fingerprint`
- `LT Last Event At`

### Canonical Field Keys
These are the exact keys the ingest and attribution layer should consume:
- `contact.utm_source_first`
- `contact.utm_medium_first`
- `contact.utm_campaign_first`
- `contact.utm_content_first`
- `contact.utm_term_first`
- `contact.utm_landing_page_first`
- `contact.utm_source_last`
- `contact.utm_medium_last`
- `contact.utm_campaign_last`
- `contact.utm_content_last`
- `contact.utm_term_last`
- `contact.utm_landing_page_last`
- `contact.warm_source`
- `contact.warm_trigger_type`
- `contact.lead_temperature`
- `contact.lt_last_routing_channel`
- `contact.lt_last_routing_reason`
- `contact.lt_last_routed_at`
- `contact.lt_route_lock_until`
- `contact.lt_routing_priority`
- `contact.lt_last_event_fingerprint`
- `contact.lt_last_event_at`
- `contact.company_name_for_emails`
- `contact.em_company_operating_state`
- `contact.em_company_research_snippet`
- `contact.em_cannabis_marketing_signal`
- `contact.em_email4_personalization_ready`
- `contact.em_email4_personalization_reason`

## GHL Pipeline / Stage Contract
### Warm
- `New`
- `Qualified (MQL)`
- `Routed to Outreach`
- `Nurture Active`
- `Disqualified`

### Sales Outreach
- `New`
- `Attempting Contact 1st Attempt`
- `2nd attempt`
- `3rd attempt`
- `Engaged`
- `Meeting Requested`
- `Booked`
- `Unresponsive`

### Sales
- `Discovery Scheduled`
- `Discovery Completed`
- `Proposal Sent`
- `Negotiation`
- `Closed Won`
- `Closed Lost`

## GHL Workflow Inputs
These live workflow families create or mutate the records the report reads:
- Warm intake and routing:
  - `GHL Warm Intake - Add Intake Tag (Webhook)`
  - `GHL Warm Intake - Email Inbound Tag (Webhook)`
  - `GHL Warm Intake - SMS Tag (Webhook)`
  - `GHL Warm Intake - Referral Tag (Webhook)`
  - `GHL Warm Intake - Email Outbound Tag (Webhook)`
  - `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)`
  - `WF - Master Warm Intake and Routing`
  - `WF - Warm Channel Micro Entry`
- Website lead capture:
  - `Website Lead Intake from Hero form`
  - `Website Lead Intake from Footer Form`
  - `Form Submissions from Website with no downloads`
- Regulated-booking handoff:
  - `WL - Webhook to Slack Channel Update`
  - regulated ads booking automation for `Regulated Ads On Social/Search`
- Reporting support:
  - `LT - Report Config Sync`
  - `LT - GA4 Daily Ingest`
  - `LT - GSC Daily Ingest`
  - `LT - GHL Daily Leads Ingest`
  - `LT - GHL Daily Sales Ingest`
  - `LT - Report Attribution Bridge`
  - `LT - Report Daily Rollups`
  - `LT - Report QA and Alerts`
  - `LT - Report Publish Refresh`

## Raw Tables
- `report_raw_ga4_sessions`
- `report_raw_ga4_pages`
- `report_raw_ga4_events`
- `report_raw_gsc_queries`
- `report_raw_gsc_pages`
- `report_raw_gsc_site`
- `report_raw_ghl_contacts`
- `report_raw_ghl_opportunities`
- `report_raw_ghl_pipeline_history`
- `report_raw_ghl_forms`

## Bridge Tables
- `report_bridge_traffic_to_lead`
- `report_bridge_lead_to_sale`
- `report_bridge_identity_map`

## Rollup Tables
- `report_daily_summary`
- `report_channel_daily_summary`
- `report_funnel_daily_summary`
- `report_pipeline_daily_summary`
- `report_stage_daily_summary`
- `report_utm_daily_summary`
- `report_landing_page_daily_summary`

## Operational Tables
- `report_sync_runs`
- `report_sync_errors`
- `report_sync_watermarks`
- `report_source_health`

## Core Rules
- Keep raw pulls append-only.
- Do not invent joins when attribution is ambiguous.
- Preserve unmatched rows in explicit unmatched buckets.
- Keep traffic, search, and CRM pulls isolated so one failure does not block the rest.
- Write raw data first, then bridge rows, then rollups.

## Minimum V1 Output
- GA4 sessions by channel
- GA4 landing pages
- GSC clicks and impressions
- GHL contacts created
- GHL opportunities created
- GHL closed won revenue
- One dashboard surface with source labels
