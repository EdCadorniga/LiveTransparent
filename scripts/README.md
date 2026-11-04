# Versioned automation scripts

The root `scripts/` directory is intentionally organized by operational domain. These files are reusable or retained for rollback/audit and are versioned by Git. Do not put disposable browser captures, caches, or machine-specific probes here.

> **Exact-path classification notice (2026-11-05):** the developer-transition review produced a per-path classification with sizes, doc-reference counts, and sensitive-hit flags: `docs/transition/scripts-classification-2026-11-05.md`. It is a review-only proposal; the nine files flagged there with hardcoded credential literals were redacted to `os.environ` loaders on 2026-11-05 (batch-1 manifest). No other file was moved or deleted from `scripts/`.
>
> **Reduced-toolkit note (2026-11-05/06):** per the organization census (`docs/transition/repository-organization-2026-11-06.md`), the one-off legacy probes that lived at the repo root (2026-07-07 wave) are archived at `local-archive/scripts-legacy-2026-07/`; `scripts/` itself is unchanged pending the owner's reduced-toolkit decisions in the owner review package.

> **Owner disposition (2026-11-06):** Ed chose conservative retention of all 242 script-like files under `scripts/` as versioned source/history. **Retention is not an operational-toolkit endorsement.** Do not run a script merely because it is tracked or listed below; inspect its effects, target tenant, credentials and current callers before use. The smaller maintained developer toolkit is not selected until Ed supplies/reviews exact paths. `landing/` is retained as source, not deployed or deleted.

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

The dated exact-path classification is [`docs/transition/scripts-classification-2026-11-05.md`](../docs/transition/scripts-classification-2026-11-05.md). [`docs/repository-file-map.md`](../docs/repository-file-map.md) is a navigation index with **incomplete 2026-09-17 filename lists**, not a complete current inventory.

## Inventory freshness

The detailed filename lists in `docs/repository-file-map.md` were last updated 2026-09-17 and are not a current census. A metadata-only enumeration on 2026-11-05 found 242 script-like files (1,256,534 bytes) under `scripts/`; the current per-directory counts are: root 55, `apollo/` 15, `deploy/` 13, `diagnostics/` 39, `email/` 2, `emerald/` 5, `instagram/` 8, `linkedin/` 43, `monitoring/` 1, `n8n/` 37, `partnerships/` 6, `social-reporting/` 10, and `utilities/` 8. This is a path/size count only: it does not establish maintenance, safety, secret-free status, or permission to run/remove any file. The older file map remains useful for navigation but must not be treated as a complete current script list until its exact paths are reviewed and reconciled.
