# Embedded Report Host Spec

## Purpose

Define the external dashboard surface that GHL loads inside an iframe.
The dashboard should be read-only, GHL-first, and backed by Postgres.

## Canonical Host

- `https://reports.livetransparent.com`

## Canonical Embed Route

- `https://reports.livetransparent.com/embed/executive`

## Repo Scaffold

- `reports/README.md`
- `reports/embed/executive/index.html`

## Suggested Query Parameters

- `view=overview|leads|sales|pipeline`
- `range=7d|30d|90d|custom`
- `from=YYYY-MM-DD`
- `to=YYYY-MM-DD`
- `locationId=Zwz4relUXVPxx8uohnjV`
- `embed=1`

## Behavior

- Render a read-only executive report with GHL metrics first.
- Read from Postgres summary tables only.
- Never expose write actions in the iframe surface.
- Keep the URL stable so GHL can embed it without churn.
- Support a consistent default view and a date-range switcher.
- Treat `7d`, `30d`, and `90d` as trailing complete-day presets ending yesterday.
- Surface the metric glossary in the dashboard so visible cards are defined where they are shown.

## Access Model

- Use a short-lived signed embed token or session check on the host side.
- Do not rely on GHL to protect the underlying data.
- Use GHL only as the entry point and the user-facing shell.
- Report-only access should be read-only.

## Response Headers

- Allow framing by the production GHL origin used for the Live Transparent location.
- Do not set `X-Frame-Options: DENY` on the embed route.
- Prefer a CSP `frame-ancestors` policy over ad hoc allowlists.

## Data Contract

- The host reads KPI and detail data from the Postgres reporting tables.
- It should expect the rollup tables to be refreshed by n8n.
- It should not call GA4 or GSC directly in the current phase.

## Outgoing Call Detail

- UI section: `Outgoing Call Detail` at the bottom of the Executive Report.
- Sidebar anchor: `#section-outgoing-calls`.
- Browser API: `GET /api/report/executive/outgoing-calls?range=7d&limit=100&offset=0`.
- Nginx proxy target: `https://automations.livetransparent.com/webhook/lt-report-outgoing-calls`.
- n8n workflow: `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`), active and published.
- Source query: `voice_call_attempt` joined to `voice_call_queue`, with latest `report_raw_ghl_contacts` snapshot enrichment.
- Window rule: exactly the seven most recent completed calendar days in `America/Los_Angeles`; the API returns `total`, `limit`, `offset`, `range`, and `calls`.
- Page rule: maximum 100 rows; the UI uses Previous/Next pagination and does not load all history at once.
- Playback rule: recording elements use `preload="none"`; recording URLs are provider-signed values and must not be committed to the repository.
- Identity rule: if the reporting snapshot has no contact name, display the GHL contact ID rather than `Unknown`.
