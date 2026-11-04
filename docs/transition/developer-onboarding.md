# LiveTransparent developer onboarding

**Draft status: 2026-11-05.** This is a safe repository orientation, not a credential-transfer or production authorization. Repository setup is only partially reproducible: this checkout has a root `package-lock.json` but no root `package.json`, and no root Python dependency manifest was found. Confirm the intended per-subsystem runtime and owner before installing dependencies or running deployment tools.

## Start here

1. Read [`AGENTS.md`](../../AGENTS.md) for project safety boundaries and tool rules.
2. While the developer transition is active, read the [transition README](README.md) and [progress ledger](../transition-plan.md). Update the ledger after each completed acceptance check.
3. Read [Project Status and Next Steps](../../Project%20Status%20and%20Next%20Steps.md), then the relevant [specification](../../Project%20Specifications.md), runbook, and latest dated session handoff.
4. Treat dated inventories as point-in-time evidence. Refresh live state before operational decisions. Do not recreate the retired root Repomix bundle.

## Repository and local setup

- Repository root is the project workspace. Preserve existing user changes; inspect `git status --short --branch` and relevant diffs before editing. Do not stage, reset, clean, or commit unless explicitly asked.
- Current transition checkout was `codex/social-outreach-sync`, ahead of origin by two commits when checked on 2026-11-05. This is a snapshot, not a permanent branch instruction.
- Use the supported tools noted in `AGENTS.md` where installed. The project includes Python helpers, JavaScript/TypeScript n8n workflow sources, reports, and service-specific components; there is no single root build/test command.
- No root `package.json` or Python requirements/pyproject manifest was found at onboarding review. The root lockfile alone does not establish a supported Node version or install procedure. Before installing, locate the nearest subsystem manifest and read its README/runbook. Do not run `npm install` at the root based only on `package-lock.json`.
- There is no verified project-wide CI/release or pull-request convention documented in the available root files. Confirm with the repository owner. Do not invent a release workflow.
- For a Python helper, inspect its header/README and side effects first. Use a temporary environment only when the required dependency set is documented. For syntax-only checks, `python -m py_compile <specific-file.py>` is appropriate when the project/runtime supports it; it does not prove API behavior or safety.
- For n8n workflow SDK work, read the relevant MCP SDK reference and node definitions before writing code. Runtime/credential-dependent tests need owner-approved access and may have side effects.

## Access and tenant boundaries

- **n8n:** use only the LiveTransparent `n8n-lt` instance at `automations.livetransparent.com`. The available Katwill/other customer connectors are not substitutes. If n8n-lt is unavailable, stop n8n operations.
- **GHL:** use the LiveTransparent sub-account and supported authenticated surfaces. The Developer/Marketplace portal was not authenticated in the 2026-11-05 review; app inventory and some workflow-builder state remain blocked.
- **Coolify/VPS:** saved-configuration structural facts plus Postgres schema and route-map evidence are now captured (2026-11-05, see README). Still unverified/unapproved: scheduled-backup coverage, restore test, and any remediation decision (e.g., reports-app saved/generated network drift). No restore or service change is authorized by this guide.
- Obtain credentials from the owner through an approved secure channel. Never put `.env`, PITs, API keys, signing secrets, OAuth tokens, token-bearing URLs, production contact exports, or raw execution payloads in Git or transition docs. Config nodes in n8n may contain plaintext secrets; restrict access and do not copy values into local artifacts.
- Owner and escalation contacts for access provisioning, billing, domains, GHL apps, credentials, Coolify/VPS, and incidents have not been confirmed. Ask the project owner before operational work.

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

- The only bounded backup evidence currently documented is a root-only, one-time n8n upgrade set. Ed said backups need not be retained, but that does not establish restore readiness or authorize altering existing files. Restore remains untested.
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
