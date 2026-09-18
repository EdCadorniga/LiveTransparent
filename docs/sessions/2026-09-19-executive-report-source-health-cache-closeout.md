# Executive Report Source Health and Cache Closeout — 2026-09-19

## Objective

Repair misleading Source Health placeholders, expose appointment snapshot freshness, make the Executive Report render its primary data before slower secondary requests, and extend the report API cache lifetime.

## Implemented

- `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`) now emits synthetic request-path health rows for `n8n` and `postgres` when the report query succeeds.
- The API now emits an `appointments` health row from `report_raw_ghl_appointments`, including latest `loaded_at`, snapshot row count, and a 48-hour stale threshold.
- The Executive Report maps `n8n` and `postgres` health rows to their tiles and labels Source Health as runtime, pipeline, and snapshot freshness.
- The frontend renders the primary summary immediately; campaign channels and prior-period comparison load afterward.
- `reports/nginx.conf` caches successful Executive Summary and Campaign Channel responses for **20 minutes**. Cache locking, stale-if-error fallback, and the 10-minute inactive cache window remain enabled.

## Live state

- Executive Summary workflow active/published version: `00285be3-e4b5-4741-95a9-474b2c74ce00`.
- Live report image: `v3ud1lum1svamymuor21upog:progressive-health-20260919`.
- Nginx active configuration reports `proxy_cache_valid 200 20m` for both report API locations.
- 7-day endpoint verification: HTTP 200, 29,909 bytes, `X-Report-Cache: HIT`; health rows `appointments=ready`, `n8n=ready`, `postgres=ready`.
- Current 7-day appointment data contains 2 booked appointments.

## Repository state

Changed or added during this work:

- `reports/embed/executive/index.html`
- `reports/nginx.conf`
- `scripts/social-reporting/repair_source_health.py`
- This closeout document.

The worktree remains uncommitted. `git diff --check` passes with only existing LF/CRLF normalization warnings.

## Follow-up

- Commit the reviewed report frontend, nginx configuration, repair helper, and closeout documentation when ready.
- The existing `scripts/deploy/deploy_report_proxy.py` has a repository-root path bug (`scripts/reports/nginx.conf`); use the corrected path or repair the helper before relying on it for future nginx-only deployments.
- Treat an HTTP 200 response with an empty body as a report failure, not valid zero data.
