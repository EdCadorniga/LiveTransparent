# Repository organization census & classification — 2026-11-05/06 (late continuation)

**Companion to:** [completeness-audit-2026-11-06.md](completeness-audit-2026-11-06.md) and the
batch manifests 5–11 in this folder. Read-only enumeration documented here; execution happens
only through the per-batch manifests. Sensitive contents were never opened except bounded
first-line probes needed to classify the three root `_*.py` probes.

## Method

Fresh recursive metadata census (files, sizes, tracked/ignored status via `git ls-files` /
`git check-ignore`), bounded content probes only for classification (headers of tiny root
scripts, `README` files). Reference safety: every archived basename was searched across all
Markdown/scripts/JSON/YAML in the repo before its batch; hits outside dated 2026-11-05
handoff/EOS/manifest artifacts are listed explicitly below and pointers were updated where a
maintained control doc referenced a moved file.

## Dispositions executed via batches 5–11

| Batch | Manifest | Class | Content |
|---|---|---|---|
| 5 | [batch-5-regenerable-caches](retention-manifest-2026-11-06-batch-5-regenerable-caches.md) | delete (regenerable) | `.pip-cache/` (5 tracked + dir), `.playwright-mcp/` (1,443 files / 50.04 MB, git-ignored browser-profile debug state) |
| 6 | [batch-6-repomix-authoring](retention-manifest-2026-11-06-batch-6-repomix-authoring.md) | archive | `repomix.config.json`, `.repomixignore` → `local-archive/repomix-authoring-2026-11/` |
| 7 | [batch-7-report-era-captures](retention-manifest-2026-11-06-batch-7-report-era-captures.md) | archive | 16 report-era captures (JSON/PNG/MD/network-response + stale-executions screenshot) → `local-archive/report-captures-2026-11/` |
| 8 | [batch-8-contact-division-working-files](retention-manifest-2026-11-06-batch-8-contact-division-working-files.md) | archive | 12 cohort-division working files (2026-07-29 wave) → `local-archive/contact-division-2026-07/` |
| 9 | [batch-9-contact-cohort-sources](retention-manifest-2026-11-06-batch-9-contact-cohort-sources.md) | archive (PII, never bare-delete) | 3 root `Export_Contacts_*` CSVs + `Contacts added August 25 2026/` (16 files) → `local-archive/ghl-export-csvs-2026-11/`, `local-archive/contacts-import-august-2026/` |
| 10 | [batch-10-root-legacy-scripts-and-docx](retention-manifest-2026-11-06-batch-10-root-legacy-scripts-and-docx.md) | archive | 3 root `_*.py` one-off probes (2026-07-07) → `local-archive/scripts-legacy-2026-07/`; 8 campaign/design `.docx` + `_qa_remove_exec/` legacy QA staging (PDF/PNG) → `local-archive/campaign-design-docx-2026-11/` |
| 11 | [batch-11-marketing-byte-duplicate](retention-manifest-2026-11-06-batch-11-marketing-byte-duplicate.md) | delete (pure duplicate) | `marketing/email-marketing/cold-outreach-prep/reports/live-run-postgres-execution-detail.json` deleted — byte-identical SHA-256 twin `live-run-postgres-full-execution-detail-20260220T094538Z.json` retained |

## Root file map (post-batch)

**Canonical control / maintained docs — keep:** `AGENTS.md`, `plan.md`,
`Project Status and Next Steps.md`, `Project Specifications.md`, `executive_report_v1_plan.md`,
`improvementPlan.md`, `QWEN.md`.

**Config/tooling — keep (tracked):** `.gitignore`, `.env` (ignored, secrets — never copy),
`opencode.json` (OpenCode harness config), `clihub.yaml` + `clihub.lock.json` (CLI-harness
skill/MCP registry: codex/opencode skills, playwright/ref_http/exa/chrome_devtools/ghl/n8n MCP
ids), `package.json` + `package-lock.json` (single `@n8n/workflow-sdk` dep; `npm ci`
regenerates), `Dockerfile` (**load-bearing**: Coolify app `reports.livetransparent_server`
builds from `dockerfile_location: "/Dockerfile"` and copies `reports/nginx.conf` +
`reports/` — do not move; see
[coolify-saved-config-2026-11-05.md](coolify-saved-config-2026-11-05.md)).

**Out of project scope — leave in place unprocessed:** `Billing Report August 10-30 2026.docx`,
`Billing Report August 10-30 2026.md`, `Billing Report July 6-26 2026.md` (personal billing;
do not open/move/describe), `repeated linkedin messages.png` (identifying prospect data;
documented untracked boundary).

**Retired authoring leftovers — archived:** `repomix.config.json`, `.repomixignore` (batch 6;
bundle itself stays deleted, never recreate).

## Directory map (all families; tracked counts from `git ls-files`)

| Directory | Files | Size | Status |
|---|---|---|---|
| `_qa_remove_exec/` | 2 | 268 KB | legacy QA staging for the Executive Report removal request (PNG + PDF); archived with the matching root `.docx` (batch 10) |
| `.gemini/` | 1 | 4 KB | Gemini tool config; **tracked** — keep |
| `.git/` | – | – | repository metadata |
| `.kilo/` | 1 | 107 B | Kilo tool state (`.gitignore` only); keep |
| `.monitor/` | 32 | 90 KB | monitor runtime state; **documented boundary** — keep |
| `.pip-cache/` | 17 | 55 KB | pip download cache (5 odd tracked entries); **regenerable — deleted** (batch 5) |
| `.playwright-mcp/` | 1,443 | 50.04 MB | Playwright MCP browser-profile debug state; git-ignored, disposable by `.gitignore` class; **deleted** (batch 5) |
| `.qwen/` | 2 | 193 B | Qwen tool state incl. `settings.json.orig` backup variant; **tracked** — keep |
| `AppScript for IG and FB enhancement/` | 3 | 17 KB | tracked Apps Script sources (`.clasp.json`, script ID present, `Enrich with FB and IG Links.js`); Google Apps Script source family — keep, documented |
| `bookstack/` | 3 | 3.5 KB | BookStack-on-Coolify compose template (`.env.example`, README, compose); referenced by `QWEN.md`, `GHL Live Transparent CRM/Warm_Lead_Conflict_Safe_Implementation_Spec.md`, `marketing/website/ai-chatbot/plans/AI_Agent_Knowledgebase_Setup_Process.md` — **keep, deployable infra template** |
| `Contacts added August 25 2026/` | 16 | 13.91 MB | Aug 25–26 Emerald/Partnership import cohort source (Agency/Brand/Dispensaries.csv + cleaned/ + partnership sub-folder, contact PII); **archived** (batch 9) |
| `data/` | 33 | 39.82 MB | source contact datasets (`Brands.csv`, `Dispensaries.csv`, `GHL_Ready_*.csv` referenced by n8n docs, `Contact List.v5.xlsx`, `Cold-outreach contacts.xlsx`) + `data/runs/2026-09-16-apollo-vp-ghl/` (documented run bundle) — keep |
| `docs/` | 201 | 2.42 MB | `docs/transition/` 42 files, `docs/sessions/` 115 dated records, plus reports/strategy material — keep (dated records are evidence, not editorial churn) |
| `GHL Live Transparent CRM/` | 22 | 236 KB | training guides/runbooks — keep |
| `images/` | 4 | 296 KB | logo + DPK images — keep |
| `landing/` | 7 | 69 KB | tracked, **NOT DEPLOYED** static landing page build (README-gated on Ed's deploy approval); superseded-shape but real website source — keep until owner decides deploy vs delete |
| `local-archive/` | 165 (post-batches) | 33.8 MB | archived historical captures; 10 dated folders after batches 5–11 |
| `local-scripts/` | 250 | 77.22 MB | operator workspace: withdraw-al family 44.17 MB (held), `apollo_vp_ghl_prep_20260916/` 25.06 MB, vertical-audit JSONs ~6 MB — keep (ignored operator-only) |
| `marketing/` | 501 | 317.53 MB | email-marketing 314.6/automation 0.2/sms-marketing 0.6/strategy 0.1/website 2.1; 442 tracked. Mass = source import CSVs (`cold-outreach-prep` 241.2 MB incl. reports/ ~160 MB of dated Feb-2026 n8n run captures; `emerald-contacts` 64 MB import sources) + dated plans/specs. One byte-duplicate deduped (batch 11); all else retained pending the reduced-toolkit owner review below |
| `n8n/` | 52 | 256 KB | tracked azure/workflow JSON/ts sources + ignored backups/workflows — keep |
| `New Campaigns October 2026/` | 116 | 3.74 MB | Oct 2026 campaign build sources (15 script files + PDFs + prep CSVs) — keep pending campaign-closure evidence |
| `Partnership Marketing/` | 5 | 133 KB | partnership lists + master JSON + sequence docs — keep |
| `postgres/` | 15 | 90 KB | SQL bootstrap/migration sources — keep |
| `qdrant/` | 2 | 618 B | Qdrant compose template; referenced by `marketing/website/ai-chatbot/plans/Website_AI_Chatbot_V1_Implementation_Spec.md` — **keep, deployable infra template** |
| `reports/` | 42 | 1.08 MB | report host source (nginx/executive/executive-v1) — keep |
| `Sample Landing Page/` | 15 | 11.9 MB | review-only prototype; **documented operating boundary** — keep isolated |
| `scripts/` | 259 (242 script-like: 226 .py + 9 .js + 7 .ps1) | 1.21 MB | versioned automation per `scripts/README.md` — keep |
| `services/` | 6 | 20 KB | sales-navigator media service — keep |
| `tools/` | 6 | 40 KB | small utilities — keep |

## Notes & risks

- `marketing/email-marketing/cold-outreach-prep/reports/` contains ~140 tracked dated
  (Feb-2026) n8n request/response/workflow-export captures, including a file literally named
  `workflow-T28iLcm4Hszo19MG.apiKey-env-payload-20260220T094956Z.json`. These were **not**
  opened or dispositioned: their sensitivity (possible embedded credentials in captured
  payloads) requires per-file review before any redistribution. Flagged to the owner review
  package as the one remaining unread-sensitivity family.
- Both copies of the 81.9 MB execution dump were byte-identical (SHA-256 verified before
  deleting one). The retained twin preserves the record.
- Root result: after batches 5–11 the root contains only canonical docs, tracked
  config/tooling, the deploy-critical `Dockerfile`, `.env`, and the two out-of-scope personal
  artifacts — nothing loose or undocumented.
- Personal billing files and `repeated linkedin messages.png` remain untouched, per boundary.
