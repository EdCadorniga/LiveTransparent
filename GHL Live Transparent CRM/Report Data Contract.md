# Live Transparent Report Data Contract

## Purpose
This document defines the minimum data contract for the executive report.
Use it as the bridge between GHL, GA4, and GSC and the Postgres rollup layer in the current live build.

## Source Systems
- GHL: leads, opportunities, pipeline movement, forms, revenue, and calls
- GA4: traffic and on-site engagement
- GSC: organic search visibility, queries, pages, and site data
- Unipile: LinkedIn connection requests, acceptance, direct messages, replies, and provider failures
- SimpleTexting: SMS delivery and reply events when the provider accepts messages

## Required Identifiers
- GHL location ID: `Zwz4relUXVPxx8uohnjV`
- GA4 property ID: pending from Cameron, only if traffic reporting is reintroduced
- GA4 measurement ID: `G-YYF078K942`
- GA4 stream ID: `7792630179`

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
- source key and campaign key
- owner and assignment source
- event type and event status

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

## UTM Capture Rule
The UTM field names themselves are standard and already part of the contract. The house standard is how we fill them:
- Every ad and tracked link should use the same `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and `utm_term` pattern.
- GHL should preserve the original source in the `First` fields and update the latest observed source in the `Last` fields.
- If a contact arrives without UTMs, the workflow should record the fallback source clearly instead of leaving it implied.

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
- Janvi AI assessment result for cannabis-business qualification (authoritative field/tag to be confirmed before implementation)
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
- AI qualification and SDR boundary:
  - Janvi AI assessment workflow (live workflow and result field/tag to be confirmed)
  - AI-qualified cannabis -> `Sales Outreach -> New` promotion
  - Sales Outreach ownership alignment and Jason/Marc 50/50 fallback
  - Vapi Warm verification queue for AI-pending/unverified contacts
- Reporting support:
  - `LT - Report Config Sync`
  - `LT - GHL Daily Leads Ingest`
  - `LT - GHL Daily Sales Ingest`
  - `LT - Report Attribution Bridge`
  - `LT - Report Daily Rollups`
  - `LT - Report QA and Alerts`
  - `LT - Report Publish Refresh`
  - `LT - GHL Executive Report Menu Sync`

## Raw Tables
- `report_raw_ga4_sessions`
- `report_raw_ga4_pages`
- `report_raw_ga4_events`
- `report_raw_ghl_contacts`
- `report_raw_ghl_opportunities`
- `report_raw_ghl_pipeline_history`
- `report_raw_ghl_forms`
- `report_raw_ghl_calls`
- `report_raw_gsc_queries`
- `report_raw_gsc_pages`
- `report_raw_gsc_site`
- `linkedin_activity_events` or an equivalent partnership UNION source
- `partnership_linkedin_connection_state`
- `partnership_release_log`

## Deferred Later-Phase Tables
## Bridge Tables
- `report_bridge_lead_to_sale`
- `report_bridge_identity_map`
- `report_bridge_traffic_to_lead` (deferred)

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
- Keep GHL pulls isolated so one failure does not block the rest.
- Keep traffic/search sources isolated too, when those later phases return.
- Write raw data first, then bridge rows, then rollups.

## Minimum V1 Output
- GHL contacts created
- GHL form submissions
- GHL opportunities created
- GHL closed won revenue
- GHL pipeline movement and stage drop-off
- One dashboard surface with source labels
- Email campaign metrics (sent, opened, clicked, bounced, unsubscribed, complained) — added 2026-07-21
- Email engagement rates (open rate, click rate, bounce rate) — added 2026-07-21
- LinkedIn outreach funnel (ready → requested → connected → DM active → completed) — added 2026-07-21
- Partnership LinkedIn campaign row with invite, acceptance, DM, reply, completion, suppression, failure, and event-coverage metrics
- Vapi voice campaign breakdown (calls by campaign, queue distribution) — added 2026-07-21
- MQL/SQL contact tracking (opportunities in MQL stage, contacts with SQL tag) — added 2026-07-21
- AI-qualified cannabis contacts promoted to Sales Outreach
- AI-pending/unverified contacts sent to Vapi
- AI-rejected/non-cannabis contacts suppressed from Vapi
- SDR assignment source, owner-alignment result, conflict count, and unassigned Sales Outreach records
- Pool distribution (brands, dispensaries, vapi campaign pools) — added 2026-07-21
