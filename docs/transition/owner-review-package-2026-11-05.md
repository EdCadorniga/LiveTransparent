# Owner review package — developer transition — 2026-11-05

Status: **transition in progress** (not complete). This package consolidates what was
evidenced today, what remains blocked, and the specific decisions/inputs needed from Ed.
Every claim below links to a dated artifact; nothing here authorizes a production or
destructive action.

## 1. What is now evidenced (2026-11-05)

| Area | Evidence |
|---|---|
| n8n exception last-observed outcomes | [exception register 2026-11-05 addendum](n8n-active-name-exceptions-2026-11-04.md) — status-only `/executions` reads; the n8n Schedule `hoursInterval`-omission semantics are corroborated |
| n8n relationship edges | [edges + runs + schedules](n8n-edges-and-exception-runs-2026-11-05.md) — execute-workflow and literal webhook edges; 94 served paths; 81 schedule registry |
| Coolify saved configuration | [coolify-saved-config](coolify-saved-config-2026-11-05.md) — first direct saved-config facts (n8n 2.44.6 / runner / postgres-shared healthy; no `extra_hosts`) |
| Postgres schema/ownership | [postgres schema inventory](postgres-schema-inventory-2026-11-05.md) — databases, tables/columns/views names, approximate row counts (planner estimates), consumers mapped from dated evidence |
| Traefik route map | [coolify route map](coolify-route-map-2026-11-05.md) — labels-derived routes for all 13 running containers, route precedence, and the sample-page duplicate-route observation |
| Scripts classification | [scripts-classification](scripts-classification-2026-11-05.md) — 443 exact paths, sizes, doc-reference counts, 12 sensitive-hit rows |
| Workflow archive classification | [n8n-archive-classification](n8n-archive-classification-2026-11-05.md) — 68 paths; 13 IDs live-version compared (all differ from current published versions → rollback evidence) |
| tmp classification | [tmp-artifacts-classification](tmp-artifacts-classification-2026-11-05.md) — 36 paths, zero bounded credential hits |
| Documentation | [training register](training-doc-register.md), [onboarding draft](developer-onboarding.md), heading/DATED-CURRENT relabels |

## 2. SECURITY — live GHL PIT exposure (owner decision: RESOLVED — retain)

- The **exact live GHL PIT** was found verbatim committed in
  `docs/sessions/2026-09-10-linkedin-conversations-fix-closeout.md` (plus `pit-` prefix
  fragments in three other 2026-09/10 session docs). Working copies are now redacted;
  **Git history still contains the token**.
- The same live value also appears inside **37** workflow exports/blueprints under
  `local-archive/n8n/` and in `local-scripts/build_mass_email_stage.py` (all git-ignored,
  local-only exposure, but files must not be redistributed).
- **RESOLVED 2026-11-05 (later): Ed directed retention of the latest PIT from `.env` — no rotation.**
  (a) ~~rotate the GHL PIT now~~ — declined; the current `.env` `GHL_PIT` stays authoritative.
  (b) Git-history purge of the 4 dated docs — with retention chosen, the token's presence in
  Git history is an **owner-accepted residual risk**; no rewrite is required or scheduled, and
  the working-copy `<redacted-pit>` redactions stay in place.
- Related rotation debt already recorded: Unipile key, Postgres password(s) in historical
  scripts, `stateUpesertSecret`, webhook callback keys — all listed in AGENTS security
  follow-ups.

## 3. Decisions needed (grouped)

> **Update 2026-11-05 (later, cleanup execution):** decision group 1 was **executed** under
> Ed's explicit YOLO mandate ("I approve all archiving and deletions as long as they were
> based on what I asked in the plan"), per batch, with recovery manifests:
> [batch 0](retention-manifest-2026-11-05-batch-0-regenerable-junk.md),
> [batch 1](retention-manifest-2026-11-05-batch-1-credential-hardening.md),
> [batch 2](retention-manifest-2026-11-05-batch-2-tmp-captures.md),
> [batch 3](retention-manifest-2026-11-05-batch-3-archive-dedup.md),
> [batch 4](retention-manifest-2026-11-05-batch-4-node-modules.md). Remaining owner
> decisions are: groups 2–6 below, plus the withdrawal-family disposition
> (which stayed untouched), and the four orphaned pre-2.44.6 VPS backups within group 4.

1. ~~**Repository cleanup** (Phase 6): approve per-path dispositions starting from the
   three exact-path artifacts in §1 — 12 credential-hit scripts (redact→migrate→keep),
   68-file archive (restrict + keep; no movement yet), 36 tmp files (content review first),
   and a `node_modules/` decision. No deletion batch is executable without per-path
   approval + recovery manifest.~~ **Executed 2026-11-05 (batches 0–4; see the update above
   and the cleanup EOS).** The only deliberately-not-executed cleanup plan items are: the
   withdrawal-family disposition (still owner-gated by the 310-invitation boundary) and any
   VPS/host-side disposition (not covered by repository-batch approval).
2. **GHL Developer portal access** — **partially resolved 2026-11-05: Ed confirmed there is no
   fourth app** (see the [evidence register](ghl-marketplace-apps-2026-11-04.md)); the
   "identify the fourth app" acceptance item is closed by owner statement. App-by-app
   enumeration of the three known apps (installs/scopes/callbacks/provider settings) remains
   an optional owner-gated read only if Ed later wants that depth.
3. **Training guides**: name the owner + intended audience + active-use status for the five
   guides; authorize procedure-evidence reads (GHL) only where needed.
4. **Coolify**: confirm backup policy (Ed said "we do not need to retain backups" — what
   then happens to the three root-only pre-`2.44.6` backup files?), and whether a
   **restore test** (isolated container) is authorized to prove recoverability. Confirm the
   reports-app network drift (generated `coolify` vs running `coolify,coolify-shared`)
   should be left as-is or remediated (remediation would be a Coolify state change). Also:
   the sample-page preview currently has **two running containers sharing one host rule** —
   confirm whether both are intended (or one is stale and needs a separately-approved
   remediation).
5. **LinkedIn invitation residue** (310 unledgered + held `ready` row): approve a scoped
   investigation or declare it out-of-transition-scope permanently.
6. **Onboarding facts**: runtime/tool versions, release process, access provisioning path,
   escalation contacts, and recovery procedures — confirm or correct the draft's marked
   gaps.

## 4. Explicitly NOT done (kept honest)

- Phase 1C: the **fourth-app identity question is closed (owner statement 2026-11-05: no
  fourth app)**; app-by-app enumeration of the three known apps remains optional/owner-gated.
- Coolify restore acceptance: **untested** (no authorization).
- GHL/provider external callers for the Emerald intake, SN V2 inbound, and mass-email
  intake: **unknown** (need owner-authenticated reads).
- Postgres-level agent notes and database schema ownership map: **not produced yet** (read
  metadata only via prior session evidence).
- ~~No cleanup batch…was performed today~~ **Cleanup batches 0–4 were executed 2026-11-05
  (later, same day) under Ed's YOLO mandate — see §3 update and the
  [cleanup EOS](../sessions/2026-11-05-developer-transition-cleanup-eos.md). Still not
  done anywhere: any production/live-state action, restore, send, or workflow change.**
