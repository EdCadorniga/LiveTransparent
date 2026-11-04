# Developer transition continuation EOS — 2026-11-05 (Phase 1/3/4/5 evidence + PIT exposure)

Continued from [`docs/transition-plan.md`](../transition-plan.md) per the YOLO/high-autonomy
continuation instruction. All work was read-only or documentation-only; no workflow was
executed/toggled, no send/test occurred, no workflow/CRM/ledger/provider state was changed,
no service was restarted, no deploy/restore/credential rotation happened, nothing was staged,
committed, reset, or cleaned.

## What was done

1. **Phase 1A/1B (n8n-lt, read-only).** New generator `docs/transition/read_edges_and_last_runs.py`
   (GET-only, allowlisted fields, UUID-token path redaction, query-strings dropped):
   - all 212 workflow definitions re-read with 0 failures;
   - last retrievable execution **status/timestamps only** for the ten active-name exceptions —
     verified the `/executions?workflowId=` filter is genuine with a second positive query (the
     four webhook-driven exceptions return zero retrievable rows);
     [register addendum](../transition/n8n-active-name-exceptions-2026-11-04.md);
   - the Emerald `interval:[{field:"hours"}]` omission is now **explained** — only such workflow
     among 81 Schedule Triggers, hourly firing corroborated by 2026-11-04 07:00→17:00 UTC
     timestamps; recorded as observed-effective, not changed;
   - full literal same-instance edge scan (7 execute-workflow edges, 2 HTTP webhook edges,
     9 code-literal webhook-path references, 94 served paths, 81 schedule registry):
     [edges artifact](../transition/n8n-edges-and-exception-runs-2026-11-05.md).
2. **Phase 1D (Coolify).** New `docs/transition/read_coolify_readonly.py` reads the panel API
   via SSH channel-forwarded GETs; captured the **first direct saved-configuration state**
   (single project; n8n@2.44.6 + runner + healthy postgres-shared; no `extra_hosts`; env var
   NAMES only): [coolify-saved-config](../transition/coolify-saved-config-2026-11-05.md).
   A first-generation pass briefly wrote a Coolify `sentinel_token` into the local artifact;
   it was caught and overwritten; the final artifact is token-free (note this session's
   transcript incidentally saw the Coolify-encrypted sentinel value once; rotation is at
   owner discretion).
3. **Phase 3 (scripts).** New bounded exact-path census + ripgrep secret-pattern scan +
   md-reference map: [scripts classification](../transition/scripts-classification-2026-11-05.md)
   (443 files / 2,198,072 bytes; 223 referenced in docs; 12 sensitive-hit rows; hit values
   never emitted).
4. **Phase 4 (archive).** Exact-path mapping of `local-archive/n8n/` with live-version
   comparison for 13 workflow IDs: [archive classification](../transition/n8n-archive-classification-2026-11-05.md)
   (68 files; all archived JSON versions differ from the current published version → rollback
   evidence; several historical exports carry `pit-` material).
5. **Phase 5 (tmp).** Exact-path classification of 36 tmp/root-`tmp*` files:
   [tmp classification](../transition/tmp-artifacts-classification-2026-11-05.md) (zero
   bounded credential hits; all keep-pending review).
6. **SECURITY finding (HIGH).** The **exact current live GHL PIT** was found verbatim in four
   committed dated session docs (plus a 13-char prefix in three more); all redacted to
   `<redacted-pit>` in the working copy. Git **history** still contains the live token; the
   same value appears in 37 git-ignored local archive/blueprint files and one
   `local-scripts/` helper. Rotating the PIT (coordinated with callers) and any history
   rewrite are owner decisions; recorded in the ledger, retention proposal, and the
   [owner review package](../transition/owner-review-package-2026-11-05.md).
7. **Phase 6.** Published the [owner review package](../transition/owner-review-package-2026-11-05.md)
   (evidence links, grouped owner decisions, explicitly-not-done list), and captured the
   Postgres schema/ownership inventory via read-only `docker exec psql` catalog queries
   (databases, schema/table/view names, column names+types, approximate row counts, consumers
   mapped from dated evidence):
   [postgres schema inventory](../transition/postgres-schema-inventory-2026-11-05.md). `plan.md`
   gained a dated evidence-continuation banner; `docs/repository-file-map.md` and
   `scripts/README.md` gained pointers to the exact-path classification artifacts.
8. Ledger updated after every discrete check; retention proposal and README now link the new
   artifacts; all relative links in the ten touched transition/control documents re-validated
   (0 missing after path fixes).

## Continuation addendum — Phase 1D/2/4 evidence close (later 2026-11-05)

- **Postgres schema/ownership inventory** captured via read-only `docker exec psql` catalog
  queries inside the shared `postgres-uokgs4c04ko0s4scccg40cgg` container (container-local
  trust, NO database password transmitted): two user databases (`postgres` project data,
  `n8n` runtime), tables/views/column names, approximate `pg_stat_user_tables` row counts
  (planner estimates; most `never`/outdated ANALYZE — not report facts), and a consumers map
  from dated evidence: [postgres schema inventory](../transition/postgres-schema-inventory-2026-11-05.md).
- **Traefik route map** captured from running-container Docker labels only, all 13 containers:
  [coolify route map](../transition/coolify-route-map-2026-11-05.md). Findings: priority-100
  `/sales-navigator-attachments` route precedes the reports app's `/`; the sample-page preview
  has **two running containers sharing one host rule** (owner decision item); internal
  Coolify components/`postgres-shared` expose nothing through the proxy. Proxy dynamic dir has
  only the 503 catch-all + an unused Caddyfile stub. Nothing changed on the host.
- **Phase 4 source/rollback matrix**: 46 critical workflows mapped against tracked repo
  references; **15 rely solely on the live n8n-lt instance** (sender/dispatcher/ledger
  families); no scheduled n8n backup exists and documented rollback = fresh API export:
  [phase4-source-backup-strategy](../transition/phase4-source-backup-strategy-2026-11-05.md).
- `plan.md` gained a 2026-11-05 evidence-continuation banner; `developer-onboarding.md`,
  the owner review package, `docs/repository-file-map.md`, and `scripts/README.md` gained
  pointers. Transition README links all new artifacts.
- Validation: relative-link checks across the touched docs (0 missing), `git diff --check`
  passes (existing LF/CRLF notices only), worktree preserved (`codex/social-outreach-sync`
  ahead by 2; modifications/untracked intact; the authorized Repomix deletion is the only
  removal; no staging/commit).

## Owner decisions applied at session close — 2026-11-05

1. **No fourth GHL app (Ed).** Closes the "identify the fourth app" acceptance item by owner
   statement; the three identified Marketplace apps are the complete list, the screenshot
   dashboard's "4 total live apps" aggregate is informational only, and the "do not guess a
   fourth app" instruction is superseded everywhere
   ([app evidence register](../transition/ghl-marketplace-apps-2026-11-04.md), ledger 1C,
   owner review package, next-session prompt). App-by-app enumeration of the three known
   apps remains optional/owner-gated.
2. **Retain the latest PIT from `.env` (Ed).** No rotation now. Resolves the HIGH-severity
   exposure decision: the working-copy `<redacted-pit>` redactions stay in force, but the
   token's presence in Git history (4 dated docs) and in 37 local git-ignored files plus one
   `local-scripts/` helper is now an **owner-accepted residual risk**. Distribution
   precautions on those files are unchanged; no further action is scheduled for the PIT.
   Other credential-rotation debts (Unipile/Postgres literals/stateSecret/callback keys) are
   separate and still open.

## Open / blocked (unchanged or newly noted)

- ~~GHL fourth-app identity~~ — **closed by owner statement 2026-11-05 (no fourth app).**
- ~~GHL PIT exposure decision~~ — **closed by owner statement 2026-11-05 (retain latest PIT; no rotation).**

- GHL Developer portal app-by-app verification and 4th-app identity: **blocked** on
  authenticated read-only access.
- Training guide owners/audience/active use: **blocked** on Ed's confirmations.
- Coolify backup schedule/coverage (`/backups` endpoints Not found in this panel's API),
  reports-app network drift, restore acceptance: **open**; restore untested.
- LinkedIn residue (310 unledgered invitations + held `ready` row): **held** pending owner scope.
- PIT exposure resolution (rotation/history purge): **owner decision**.
- Phase 6 cleanup batches: **pending** owner per-path approvals.

## Next session

1. Start at the [transition plan ledger](../transition-plan.md) and continue from the
   [owner review package](../transition/owner-review-package-2026-11-05.md) decision list
   once Ed responds; keep advancing remaining unblocked Phase 2 reconciliation in the
   meantime.
2. When Ed provides the six decision inputs (clean-up batch scope, portal access, training
   owners, Coolify backup/restore gate, LinkedIn residue scope, onboarding facts), execute
   the corresponding unblocked items and update the ledger immediately.

## Verification

- `git diff --check` passes (existing LF→CRLF notices only).
- `git status --short --branch`: `codex/social-outreach-sync` ahead of origin by 2; existing
  modifications/untracked preserved; the 4 redacted docs now modified; 12+ new transition
  artifacts/doc generators untracked; nothing staged/committed.
