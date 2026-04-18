# Search Console Reference

## Purpose
Reference for the GSC portion of the LiveTransparent reporting pipeline.

## Official Source
- Search Console API overview: https://developers.google.com/webmaster-tools/about
- Search Analytics query endpoint: `POST /sites/siteUrl/searchAnalytics/query`
  - https://developers.google.com/webmaster-tools/v1/api_reference_index

## What We Need
- Verified Search Console property for `livetransparent.com`
- Access with owner, full, or read permissions

## Implementation Notes
- Use the Search Console API to query search analytics for the managed property.
- Keep Search Console pulls separate from GA4 pulls.
- Store raw rows before rollup.
- Make sure the Search Console property is verified and accessible with at least read access.

## Suggested Pull Targets
- Clicks
- Impressions
- CTR
- Average position
- Page-level performance
- Query-level performance
