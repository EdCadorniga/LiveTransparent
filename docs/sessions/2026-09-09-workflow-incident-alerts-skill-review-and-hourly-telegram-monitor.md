# Session Closeout — Workflow Incident Alerts Skill Review + Hourly Telegram Monitor

Date: 2026-09-09 03:20 MPST (session started 2026-09-08)

Scope: review of the reusable global OpenCode skill `workflow-incident-alerts`, learning it in
Hermes, and replacing the two 30-minute LiveTransparent monitor cron jobs with one hourly
infra+email monitor that reads Gmail alert emails, does read-only + safe auto-fix triage, and
escalates to Ed via Telegram.

## What changed (all verified this session)

1. Global skill reviewed and updated
   - File: `C:\Users\edmon\.config\opencode\skills\workflow-incident-alerts\SKILL.md`
   - Review verdict delivered: "good but not done" — 5 strengths + 5 gaps.
   - Applied ALL five suggested improvements (dedup by fingerprint, failed-closed detection,
     retiring old alert workflows, classify-from-full-body, attachment scrubbing) plus the
     resolve-only processed-ids rule discovered during implementation.
2. Hermes-side skill created
   - Name `workflow-incident-alerts`, category `devops`, description "Use when triaging n8n
     workflow failure alerts." (60-char budget enforced). Loaded by the hourly cron agent.
3. New hourly monitor gate script
   - `C:\1_Ed's Active Work\AI\Hermes\scripts\lt_alert_gate.py` (145 lines)
   - Deterministic one-line output: `READY=<http>|ssh=ok|<container>=<state>/<health>|restarts=..|pool=N|new=N:<ids>`
   - Cron engine skips the agent run when output is byte-identical to previous run (dedup loop).
   - Current healthy output: `READY=200|ssh=ok|n8n=running/none|pg=running/healthy|runner=running/none|restarts=0,0,0|pool=0|new=0:`
4. Cron job wiring (via `hermes cron edit`, not direct file edit)
   - Job `9622fde81b78` — "LT hourly infra+email monitor (Telegram)"
   - Every 60m, deliver=`telegram`, continuity on, workdir LiveTransparent
   - Model `deepseek-v4-flash` / provider `opencode-go` PINNED (fixes the old `drift_skip`
     failure: provider 'openai-codex' -> 'opencode-go'; model 'gpt-5.6-luna' -> 'deepseek-v4-flash')
   - Monitor-script gate `lt_alert_gate.py`, 5 skills attached, RESUME/D enabled
5. Old jobs paused (user chose "Replace" — fold email triage into one hourly monitor)
   - `33eea46dd9b3` (LT n8n-postgres-runner monitor) — PAUSED
   - `b3f164cd1746` (LT watch-email auto-fix) — PAUSED
6. Old drift incident acknowledged
   - `hermes cron incidents ack 9622fd_a969f3866045` (historical pre-fix drift_skip, 2026-09-07)

## Verification (exact outcomes)

- Manual run `hermes cron run 9622fde81b78 --accept-hooks` at 13:47 → run completed cleanly,
  NO incident. Output: `cron/output/9622fde81b78/2026-09-08_13-47-54.md` (67KB).
- Agent in the run loaded all 5 skills, probed infrastructure + Gmail, classified `new=0`
  (no alert emails), responded: `ALL CLEAR - no issues need your attention.`
- TELEGRAM DELIVERY CONFIRMED from agent log:
  `13:47:55 Job '9622fde81b78': delivered to telegram:8712052921 via live adapter thread=- message_id=416`
- Gate baseline recorded in `monitor_last_output.txt`; subsequent runs skip the agent until
  the gate line changes (byte-identical hash comparison).
- Persisted cron state: `enabled=True`, `deliver=telegram`, monitor gate hash stored,
  `last_status=ok`, `last_delivery_error=None`, next_run_at ~14:47.

## Deduplication semantics (critical, do not revert)

- Gate re-fires the agent ONLY when its one-line output changes: new UI alert email id
  (`UNHEALTHY|RECOVERED|ALERT` subjects from LiveTransparent), container state flip, restart
  count bump, or pool/signature count change.
- Agent appends an alert id to `triage_state.json` `processed_ids` ONLY when its incident is
  RESOLVED (recovery email or verified healthy). Open-incident ids stay unprocessed so the
  gate's `new=` set stays stable — otherwise the 1→0 flip one hour later fires the agent and
  sends a misleading ALL CLEAR while the incident is still open.
- Final response rules: `ALL CLEAR - no issues need your attention.` only when no open
  incidents AND no new alert emails; `STILL OPEN - <incident>: no change, awaiting RECOVERED
  or manual fix.` when an open incident is unchanged and already reported (<24h).
  At most ONE Telegram message per real issue (+1 resolution note on recovery).

## Known caveats / not changed

- AGENTS.md (182KB) is auto-injected into cron runs truncated at ~20KB (engine logs the
  truncation warning; tail is cut). Job prompt now instructs the agent to read the full file
  from disk when it needs sections beyond the head. AGENTS.md was NOT restructured — Ed's
  operational runbook; offered to split into lean runbook + archive if desired.
- The n8n internal pool-closure incident investigation is SEPARATE and untouched by this
  session (see AGENTS.md OPEN section + docs/sessions/2026-09-07-n8n-pool-closure-investigation.md).
  Monitoring now covers it via the hourly gate/email triage instead of the old 30m jobs.
- AGENTS.md in the repo has pre-existing uncommitted local edits (incl. n8n version note) —
  left untouched.

## Safety gates in force (unchanged)

- Credential protection: no secrets in any alert/sample-email body, attachments scrubbed.
- Autonomy level (user-selected): read-only + safe auto-fix — auto-apply only reversible,
  non-destructive, retry-safe, idempotent, credential-safe fixes; escalate restarts,
  credential rotation, destructive cleanup to Ed via Telegram.
- Approval required before: commits/pushes, service restarts (n8n/runner/postgres),
  credential rotation, deleting temporary workflows, production workflow execution.
- Do not restart PostgreSQL/Redis or rotate `N8N_ENCRYPTION_KEY` without evidence + approval.

## Next session (precise order)

1. Verify the first naturally-scheduled hourly cycle (~14:47 and beyond): `hermes cron runs
   9622fde81b78` and `hermes cron incidents list` — expect NO agent run and NO telegram
   message while gate output is unchanged (dedup working).
2. When a real alert arrives: confirm ONE telegram message per issue, confirm `triage_state.json`
   keeps open-incident ids unprocessed, confirm resolution note on RECOVERED.
3. If desired: split AGENTS.md into lean runbook + archive to remove the 20KB truncation caveat.
4. Separate track (unrelated to this session): SDR attribution report Phases 3–5 — see
   docs/sessions/2026-09-09-executive-report-sdr-attribution-plan.md; pool-closure root cause —
   see AGENTS.md OPEN section.