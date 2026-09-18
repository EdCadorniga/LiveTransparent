# Versioned automation scripts

The root `scripts/` directory is intentionally organized by operational domain. These files are reusable or retained for rollback/audit and are versioned by Git. Do not put disposable browser captures, caches, or machine-specific probes here.

## Categories

- `apollo/` — Apollo field preparation and cleanup.
- `deploy/` — deployment and runner/report deployment helpers.
- `diagnostics/` — database, PostgreSQL, SSH, and environment diagnostics.
- `email/` — Gmail helper scripts.
- `emerald/` — Emerald campaign/contact maintenance.
- `instagram/` — Instagram/ Facebook company-page and reporting automation.
- `linkedin/` — LinkedIn connection, DM, state, suppression, and backfill tooling.
- `monitoring/` — retained monitor entry points.
- `n8n/` — n8n API, workflow, credential-rotation, and integration helpers.
- `partnerships/` — partnership contact and LinkedIn campaign tooling.
- `social-reporting/` — social and Executive Report fixes/audits.
- `utilities/` — shared or cross-cutting helpers that do not belong to one domain.

The complete file-level inventory and repository boundaries are in [`docs/repository-file-map.md`](../docs/repository-file-map.md).
