# LiveTransparent Report Host

This folder holds the external dashboard surface that GHL will load inside an iframe.

## Canonical Route

- `https://reports.livetransparent.com/embed/executive`

## Current Status

- The host shell is prepared in repo.
- The report host is now deployment-ready with `docker-compose.yml`, `Dockerfile`, `nginx.conf`, and `index.html`.
- The preferred GHL entry point is a Custom Menu Link that opens this page in an embedded iframe.
- The report data store remains Postgres.
- n8n writes the raw data, bridge rows, rollups, QA rows, and publish markers.
- GA4 ingest still waits for the Property ID from Cameron.
- The GHL sidebar menu record is already live in GHL.

## Expected Runtime Flow

1. GHL sidebar item opens the embedded report URL.
2. The host page reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query params.
3. The host fetches executive report data from a Postgres-backed API.
4. The page renders KPI cards, funnel panels, and drilldowns in read-only mode.

## GHL Fit

- This host is designed to stay external while being embedded inside GHL.
- That keeps the dashboard flexible while leaving CRM, navigation, and user access inside HighLevel.
- If the team later wants a dashboard-page view instead, the same host can also be embedded through a GHL dashboard widget.

## Planned API Contract

- `GET /api/report/executive/summary`
- `GET /api/report/executive/channel-breakdown`
- `GET /api/report/executive/pipeline-dropoff`
- `GET /api/report/executive/health`

Those endpoints are not implemented in this repo yet. The HTML shell is written so it can consume them later without changing the GHL embed URL.

## Files

- `Dockerfile`: container build for Coolify or other static hosting.
- `docker-compose.yml`: Coolify-ready service definition for the report host.
- `nginx.conf`: static web server config.
- `index.html`: root redirect into the executive report.
- `embed/executive/index.html`: interactive embedded dashboard shell
