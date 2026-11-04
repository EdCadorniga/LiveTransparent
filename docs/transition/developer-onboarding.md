# LiveTransparent developer onboarding

**Draft status: corrected 2026-11-06.** This is a safe repository orientation, not a credential-transfer or production authorization. This checkout has **both** a root `package.json` and `package-lock.json`; batch 4 verified `npm ci --dry-run` and removed regenerable `node_modules/`. This does not establish a supported Node runtime version, project-wide test command, or root Python dependency manifest. Confirm the intended per-subsystem runtime and owner before running deployment tools.

## Start here

1. Read [`AGENTS.md`](../../AGENTS.md) for project safety boundaries and tool rules.
2. While the developer transition is active, read the [transition README](README.md) and [progress ledger](../transition-plan.md). Update the ledger after each completed acceptance check.
3. Read [Project Status and Next Steps](../../Project%20Status%20and%20Next%20Steps.md), then the relevant [specification](../../Project%20Specifications.md), runbook, and latest dated session handoff.
4. Treat dated inventories as point-in-time evidence. Refresh live state before operational decisions. Do not recreate the retired root Repomix bundle.

## Repository and local setup

- Repository root is the project workspace. Preserve existing user changes; inspect `git status --short --branch` and relevant diffs before editing. Do not stage, reset, clean, or commit unless explicitly asked.
- At the earlier full-plan audit baseline, `codex/social-outreach-sync` was at `f5b8eb9` with staged deletions. Subsequent owner-requested commits pushed those reviewed changes; **this is historical, not the present checkout state**. Check `git status --short --branch` and `git log -1` before making or transferring a developer copy.
- Use the supported tools noted in `AGENTS.md` where installed. The project includes Python helpers, JavaScript/TypeScript n8n workflow sources, reports, and service-specific components; there is no single root build/test command.
- Root `package.json` and `package-lock.json` are present. Batch 4 confirmed `npm ci --dry-run` succeeds and documented `npm ci` as the regeneration path for removed root `node_modules/`; that check did **not** verify a full install, SDK build, Node version, or project-wide tests. Before installing for a subsystem, read its manifest and README/runbook. No root Python requirements/pyproject manifest was established by the earlier review.
- **Local workstation probe (2026-11-06, not a production runtime claim):** `node --version` = `v24.19.0`, `npm --version` = `11.18.0`, `python --version` = `3.13.15`, local Docker server = `29.8.1`. These are observed versions on this machine, not pinned/project-supported versions. `git ls-files` finds root `package.json`, `package-lock.json`, `Dockerfile` and no tracked root `requirements*.txt`, `pyproject.toml`, `.gitlab-ci.yml`, `azure-pipelines.yml` or `.github/` CI files. The root `package.json` declares only `@n8n/workflow-sdk` and has no scripts; therefore there is **no supported root build/test/lint command to run**. Subsystems need their own commands verified from their runbooks; do not substitute `npm test` at root.
- **Handoff medium (Ed, 2026-11-06):** the incoming developer will own a **copy of the local repository**. Do not assume a remote push or this worktree's unstaged/untracked files are included in that copy; verify the actual copy contents, Git status, excluded sensitive local files, and custody of restricted backups during handoff. Ed has not supplied the access/escalation roster or release/branch/approval process.
- There is no verified project-wide CI/release or pull-request convention documented in the available root files. Confirm with the repository owner. Do not invent a release workflow.
- For a Python helper, inspect its header/README and side effects first. Use a temporary environment only when the required dependency set is documented. For syntax-only checks, `python -m py_compile <specific-file.py>` is appropriate when the project/runtime supports it; it does not prove API behavior or safety.
- For n8n workflow SDK work, read the relevant MCP SDK reference and node definitions before writing code. Runtime/credential-dependent tests need owner-approved access and may have side effects.

## Access and tenant boundaries

- **n8n:** use only the LiveTransparent `n8n-lt` instance at `automations.livetransparent.com`. The available Katwill/other customer connectors are not substitutes. If n8n-lt is unavailable, stop n8n operations.
- **GHL:** use the LiveTransparent sub-account and supported authenticated surfaces. A later authenticated read-only Developer/Marketplace session on 2026-11-05 confirmed exactly three apps and selected settings ([evidence register](ghl-marketplace-apps-2026-11-04.md)); install/location assignments, grants, callback behavior, and some workflow-builder state remain unverified. Do not search for a fourth app.
- **Coolify/VPS:** saved-configuration structural facts plus Postgres schema and route-map evidence are now captured (2026-11-05, see README). Ed confirmed on 2026-11-06 that existing sensitive backups and the local n8n archive remain in place under his ownership and authorized an isolated **non-production** restore test, not yet performed. Scheduled-backup coverage and any remediation decision (e.g., reports-app saved/generated network drift) remain open. Production stays read-only; no restore into a production service or service change is authorized by this guide.
- **Restore-target update (2026-11-06):** the dedicated non-production host is **not provisioned**. No restricted backup has been copied to a workstation, extracted, or restored; recoverability remains untested until the host, isolation, storage, and access method are provided.
- Obtain credentials from the owner through an approved secure channel. Never put `.env`, PITs, API keys, signing secrets, OAuth tokens, token-bearing URLs, production contact exports, or raw execution payloads in Git or transition docs. Config nodes in n8n may contain plaintext secrets; restrict access and do not copy values into local artifacts.
- Owner and escalation contacts for access provisioning, billing, domains, GHL apps, credentials, Coolify/VPS, and incidents have not been confirmed. Ask the project owner before operational work.
- **Interim route:** Ed is the owner-controlled escalation and restricted-backup custodian until he supplies a named delegated roster; see [closeout decisions](closeout-decisions-2026-11-05.md). This is not a claim that access has been provisioned or that the incoming developer has accepted the handoff.

## Production safety and change control

- Read-only inventory does not authorize workflow runs, activation changes, CRM writes, outbound sends/calls, provider tests, schema/data changes, deployments, restarts, credential rotation, or artifact deletion.
- Emerald and DAN release dispatchers are live-send-capable. Never run or toggle them for inventory or testing.
- LinkedIn sender state and invitation-withdrawal artifacts have unresolved reconciliation; do not infer provider send dates from relative labels and do not mutate provider, ledger, or queue state without a scoped approval.
- Before any approved change: freshly read the exact live artifact; identify its caller, side effects, guard, rollback source, and affected users; make the smallest scoped change; read back the saved state; verify with a non-side-effecting check where possible; document evidence and remaining acceptance gaps.
- Workflow or service execution can send messages or change CRM/data. A successful dry run, HTTP 200, or saved draft is not proof of production acceptance.
- Never use generic deployment commands. Follow the specific subsystem deployment runbook, confirm exact target and rollback, and obtain separate approval for production mutation.

## Time and reporting

- Business operations, schedules, report windows, and campaign guards default to `America/Los_Angeles` unless the source contract explicitly specifies otherwise.
- Do not interpret a GHL UI timestamp from an operator-local timezone as Pacific time without checking the source timezone.
- Executive Report V1 lives separately at `/embed/executive-v1/`; do not assume the legacy `/embed/executive/` has the same data or build. Current report facts need a fresh check against the [operational status](../../Project%20Status%20and%20Next%20Steps.md) and relevant report handoff.

## Dated evidence updates (2026-11-05 — bounded facts now evidenced)

- Coolify panel API access is possible via the SSH host + a COOLIFY API key stored in `.env` (read-only GETs only; structural facts captured in [coolify-saved-config](coolify-saved-config-2026-11-05.md); `docker exec psql` inside the shared `postgres-uokgs4c04ko0s4scccg40cgg` container gives catalog metadata without a DB password).
- Host rule/route map: [coolify-route-map](coolify-route-map-2026-11-05.md) (Traefik label discovery; `/sales-navigator-attachments` prioritizes over the reports app's `/` catch; sample-page preview currently has two containers sharing one host rule — owner decision).
- Database boundaries: exactly two user databases exist (`postgres` — project data — and `n8n` — n8n CE runtime); see [postgres schema inventory](postgres-schema-inventory-2026-11-05.md) for the table/column name inventory and consumers map. Confirm consumers against fresh evidence before operational decisions.
- Workflow/relationship state: see the [n8n edges + exception runs artifact](n8n-edges-and-exception-runs-2026-11-05.md) and the [2026-11-05 addendum](n8n-active-name-exceptions-2026-11-04.md).

## Recovery, deployment, and escalation gaps

- The only bounded VPS backup evidence currently documented is a root-only, one-time n8n upgrade set. Ed owns existing restricted local/VPS backups and chose to retain them in place; his earlier “future backups need not be retained” statement did not establish restore readiness. An isolated non-production test is approved in principle, but remains **untested** until a safe target and credential/PII containment are established; do not alter production or existing backup files.
- Coolify's generated reports Compose and running network metadata differ (`coolify` vs `coolify-shared`); do not reconcile by editing either without owner approval and fresh evidence.
- If a change needs inaccessible GHL Builder/Developer access, Coolify saved configuration, or a live credential, record it as **blocked** and request the authorized owner session. Do not work around missing access by guessing private APIs or using another tenant.
- For an incident, preserve evidence, avoid repeated retries or manual replays, and escalate to the confirmed system owner. Owner/escalation roster is an open transition item.

## Handoff checklist

- [ ] Confirm account access, tenant, role, and secure credential provisioning with the owner.
- [ ] Confirm current branch/worktree status and subsystem-specific runtime/manifests.
- [ ] Identify canonical runbook, live workflow/service owner, caller, and rollback for the requested task.
- [ ] Confirm whether the proposed operation is read-only or has send/write/deployment effects; obtain exact approval for the latter.
- [ ] Record verification date, source, result, limits, and next dependency in the appropriate canonical document and transition ledger.
- [ ] Leave unresolved facts explicitly unknown or blocked; do not claim backup/restore readiness, caller completeness, or live acceptance without evidence.
