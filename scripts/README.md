# Versioned automation scripts

The root `scripts/` directory is intentionally organized by operational domain. These files are reusable or retained for rollback/audit and are versioned by Git. Do not put disposable browser captures, caches, or machine-specific probes here.

> **Exact-path classification notice (2026-11-05):** the developer-transition review produced a per-path classification with sizes, doc-reference counts, and sensitive-hit flags: `docs/transition/scripts-classification-2026-11-05.md`. It is a review-only proposal; no file was moved or deleted. Files flagged there with hardcoded credential literals are pending owner-approved hardening.

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

## Inventory freshness

The detailed filename lists in `docs/repository-file-map.md` were last updated 2026-09-17 and are not a current census. A metadata-only enumeration on 2026-11-05 found 242 script-like files (1,256,534 bytes) under `scripts/`; the current per-directory counts are: root 55, `apollo/` 15, `deploy/` 13, `diagnostics/` 39, `email/` 2, `emerald/` 5, `instagram/` 8, `linkedin/` 43, `monitoring/` 1, `n8n/` 37, `partnerships/` 6, `social-reporting/` 10, and `utilities/` 8. This is a path/size count only: it does not establish maintenance, safety, secret-free status, or permission to run/remove any file. The older file map remains useful for navigation but must not be treated as a complete current script list until its exact paths are reviewed and reconciled.
