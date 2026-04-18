# Postgres Reference

## Purpose
Reference for Postgres usage in the LiveTransparent n8n pipelines.

Use this alongside the GA4, Search Console, and GHL node references when building the reporting stack.

## Current Stack Pattern

- n8n runs on the shared Coolify network.
- Postgres is the durable reporting store.
- Existing ingest workflows already use `n8n-nodes-base.postgres` with `executeQuery`.
- The repo already contains several Postgres ingest examples in the n8n workflow backups.

## Recommended Node Pattern

Use the built-in Postgres node:

- `n8n-nodes-base.postgres`
- operation: `executeQuery`

Recommended usage:

- `queryBatching: independently` for per-row upserts
- `CREATE TABLE IF NOT EXISTS` for bootstrap
- `ALTER TABLE ADD COLUMN IF NOT EXISTS` for schema extension
- `INSERT ... ON CONFLICT ... DO UPDATE` for idempotent writes

## Write Modes

### Raw Ingest Tables

Use deterministic source keys and a stable unique index.

Recommended behavior:

- keep source snapshots logically append-only
- rerun safely for the same date window
- do not delete prior rows during normal runs

Suggested unique keys:

- `source_system + source_key + source_date`
- or a hash-based derivative of the source row identity

### Bridge Tables

Use explicit confidence and reason fields.

Recommended columns:

- `match_rule`
- `match_confidence`
- `match_reason`
- `created_at`
- `updated_at`

### Rollup Tables

Use daily primary keys and idempotent upserts.

Recommended primary key shape:

- `report_date`
- dimension columns such as `channel`, `source`, `campaign`, `pipeline`, `stage`

## Bootstrap Pattern

When a workflow creates a new table, follow this order:

1. Create the table if it does not exist.
2. Add missing columns if needed.
3. Create the unique indexes.
4. Write or upsert the data rows.
5. Record the run in ops tables.

## Failure Handling

- Keep schema bootstrap separate from data writes when possible.
- If a raw ingest slice fails, do not rollback successful slices from another source.
- Persist the failure in `report_sync_errors`.
- Persist source freshness in `report_source_health`.

## Practical Notes

- Use explicit JSONB columns for raw payload capture.
- Keep human-readable dimension columns alongside JSON payloads.
- Prefer small, repeatable upserts over one huge transaction for cross-source ingest.
- For large backfills, batch by date window.

## Examples in This Repo

- `Backup of all n8n workflows/0jDKgG8VvmfyORQn__LT - Emerald Campaign Snapshot -_ Postgres Ingest _Staged_.json`
- `Backup of all n8n workflows/kVCTmy1m8fEyP6Q7__LT - Cold Outreach CSV -_ Postgres Ingest _Staged_.json`
- `Backup of all n8n workflows/mSegmpMUd0DRwFEx__LT - Emerald CSV -_ Postgres Ingest _Staged_.json`
