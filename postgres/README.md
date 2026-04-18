# Postgres Reporting Bootstrap

This folder contains the LiveTransparent reporting schema bootstrap.

## Files

- `reporting-bootstrap.sql`: creates the report config, raw, bridge, rollup, and ops tables.

## Deployment Notes

- On a fresh database volume, `postgres/docker-compose.yml` mounts the bootstrap into `/docker-entrypoint-initdb.d/`.
- On an existing database volume, the bootstrap will not auto-run. Apply it manually with `psql` against the live Postgres instance.

## Intended Result

- The reporting stack can write the GHL reporting data immediately.
- GA4 and Search Console remain available for later expansion if traffic reporting returns to scope.
