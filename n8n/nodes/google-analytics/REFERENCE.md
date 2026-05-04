# Google Analytics Reference

## Purpose
Reference for the GA4 portion of the LiveTransparent reporting pipeline.

## What We Need
- Google Analytics 4 property ID
- Measurement ID for the web data stream
- Stream ID for the web data stream

## Live Setup Notes
- Measurement ID: `G-YYF078K942`
- Stream ID: `7792630179`
- Property ID: `434472183` (confirmed 2026-04-29)

## Official Source
- GA4 Data API property ID guidance: https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id
- GA4 Data API report entrypoint: `properties.runReport`
  - https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties#runreport
- GA4 Data API quickstart: https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart

## Implementation Notes
- Use the GA4 Data API against `properties/<property_id>`.
- Do not substitute the measurement ID or stream ID for the property ID.
- Keep traffic pulls separate from GHL pulls.
- Store raw response payloads before rolling up metrics.
- A property ID is required for Data API reporting. A measurement ID alone is not enough.

## Suggested Pull Targets
- Sessions
- Users
- New users
- Engagement rate
- Landing pages
- Channel grouping
- Source / medium / campaign
