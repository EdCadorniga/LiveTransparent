# Retention manifest — batch 1: credential hardening (12 flagged files) — 2026-11-05

Basis: [cleanup handoff prompt](../sessions/2026-11-05-developer-transition-cleanup-handoff-prompt.md) §B
YOLO mandate; classification source
[scripts-classification-2026-11-05.md](scripts-classification-2026-11-05.md) sensitive-hit table (values never emitted).
Secrets moved out of working copies as `.env`-key loaders (plan §3; handoff §B rules).
Values were never printed to the transcript or into any artifact.

| path | tracked? | hits (names) | action basis | dependency result | recovery | disposition |
|---|---|---|---|---|---|---|
| `local-scripts/_state_sync_sql.py` | no | katwill (comment only) | single matching line verified as a doc comment restating the n8n-lt-only rule; no secret present | no references to this file as a live dependency | file unchanged | **no change** (note recorded) |
| `local-scripts/build_mass_email_stage.py` | no | ghl_pit (live PIT), env_constant | handoff §B tracked-script rule (applied to untracked local script equally); live PIT must live in `.env` | referenced in [2026-09-16 newsletter design](../docs/../sessions/2026-09-16-ghl-triggered-newsletter-design.md) (historical) | **process deviation, recorded honestly:** no pre-redaction byte copy was archived for this untracked file. Equivalent values are NOT lost: the PIT remains in `.env` (`GHL_PIT`), and the `trackSecret`/`pgPassword`/`ghlApiKey` values remain stored in the corresponding live n8n Config nodes (owner-accessible; values are kept out of the repository). The redacted literals cannot be byte-reconstructed from the working copy alone. | **redacted in place**: `PIT` → `os.environ.get("GHL_PIT", "")`; `TRACK_SECRET` → `os.environ.get("MASS_EMAIL_TRACK_SECRET", "")`; 2 adjacent plaintext `pgPassword` literals → `os.environ.get("POSTGRES_PASSWORD", "")`. Re-run (if ever re-run) is documented; script itself remains intact |
| `local-scripts/linkedin-invite-withdrawals/capture-20261021T183214Z-45b220e7-431a45d2.withdrawal.jsonl` | no | jwt | hard boundary: `local-scripts/linkedin-invite-withdrawals/` whole family held while the 310-unledgered-invitation investigation is open — disposition requires an owner-scoped decision first | n/a | none — untouched | **no action; remains held** (recorded, not counted as complete) |
| `marketing/automation/scripts/patch_simpletexting_callbacks.py` | yes | jwt (API_KEY block), ghl_pit ×2 in workflow-template assignments | handoff §B: tracked script → redact literal to env loader | docs reference only in dated classification/handoff artifacts | `git show HEAD:<path>` | **redacted in place**: split JWT `API_KEY` block → `os.environ.get("N8N_API_KEY_LT", "")`; 2 `"pit-…"` template values → `os.environ.get("GHL_PIT", "<redacted-pit>")`; `import os` added |
| `marketing/automation/scripts/rerun_bad_emerald_sso_companies.py` | yes | jwt | same | same | `git show HEAD:<path>` | **redacted in place**: split JWT block → env loader; `import os` added |
| `marketing/email-marketing/cold-outreach-prep/reports/retest-api-key-20260220T053242Z.txt` | yes | jwt (API response capture, 2026-02-20 execution retest) | handoff §B: unreferenced JWT-bearing test capture → move to archive with historical header | referenced only in dated [scripts classification](scripts-classification-2026-11-05.md) table (historical evidence reference) | archive copy + `git show HEAD:<path>` (git history) | **archived** → `local-archive/historical-captures-2026-11/retest-api-key-20260220T053242Z.txt` with a short historical/superseded header; tracked deletion staged via `git rm --cached`, not committed |
| `marketing/email-marketing/emerald-email-campaign/artifacts/publish_emerald_executive_sso_workflow.py` | yes | ghl_pit in workflow-template value | handoff §B | n/a | `git show HEAD:<path>` | **redacted in place**: `"pit-…"` → env loader; `import os` added |
| `marketing/email-marketing/emerald-email-campaign/artifacts/update_emerald_exec_workflow.py` | yes | apikey_literal/jwt (X-N8N-API-KEY) | handoff §B | n/a | `git show HEAD:<path>` | **redacted in place** → `os.environ.get("N8N_API_KEY_LT", "")`; `import os` added |
| `scripts/emerald/run_dispensaries.py` | yes | apikey_literal/jwt | handoff §B | n/a | `git show HEAD:<path>` | **redacted in place** → env loader (`os` already imported) |
| `scripts/n8n/fix_sheets_node.py` | yes | apikey_literal/jwt | handoff §B | n/a | `git show HEAD:<path>` | **redacted in place** → env loader (`os` already imported) |
| `scripts/social-reporting/fix_brands_code.py` | yes | apikey_literal/jwt | handoff §B | n/a | `git show HEAD:<path>` | **redacted in place** → env loader; `import os` added |
| `scripts/utilities/fix_parse_csv.py` | yes | apikey_literal/jwt | handoff §B | katwill-era artifact (references cloud-instance-style workflow `q7q…`); already non-runnable under the n8n-lt-only standing rule | `git show HEAD:<path>` | **redacted in place** → env loader (`os` already imported) |

**Verification:** masked re-probe shows **0 remaining sensitive-pattern hits in the 9
redacted files**; `py_compile` passes for all 9; `git status` shows exactly the 8 tracked
edits (no other tracked change from this batch). The env-loader name follows the
repo-wide n8n-lt convention (`N8N_API_KEY_LT` in `.env`); the two pre-migration scripts
remain non-runnable regardless (stale katwill-era IDs) — that limitation predates and is
independent of redaction.

**Notes:** `P@ss…` plaintext Postgres literals inside
`build_mass_email_stage.py` were also redacted (adjacent credential in the same file,
same hygiene rule). Boundary respected: no withdrawal-family file was touched except to
record the hold; no secret value copied or printed anywhere.
