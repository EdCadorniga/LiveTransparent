# Retention manifest — batch 7: root report-era captures (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§C item 3 ("Report-era captures / working files at root — archive …; check Markdown references
before any deletion"). Classification basis: plan §3 Deletion/retention ("Prefer moving approved
historical material into one clearly named archive"). These are dated evidence of the Executive
Report / owner-alignment debug era (2026-07-25 → 2026-09-29), PII/credential-safety unknown
(dashes/network captures were verified credential-pattern-free by the tmp classification method
for the root `tmp*` subset only, so this batch **archives instead of deleting** everything).

| Path | Bytes | Notes |
|---|---|---|
| `campaign-channels-7d.json` | 7,272 | Campaign Channel Summary snapshot (8/17) |
| `corrected-7d-audit.json` | 12,967 | post-correction audit capture (8/17) |
| `summary-7d.json` | 21,857 | Executive Summary 7d capture (8/17) |
| `summary-prior-7d.json` | 26,872 | prior-period capture (8/17) |
| `outgoing-calls-7d.json` | 23,565 | outgoing-calls detail capture (8/17) |
| `executive-7d-snapshot.md` | 66,130 | report readback narrative (9/10) |
| `exec_report_mockup_v3 (1).png` | 153,379 | V1 report mockup (9/24) |
| `report-ui.png` | 64,337 | report UI screenshot (8/5) |
| `Jason's Call Report.png` | 61,672 | SDR native-report capture (9/29) |
| `Marc's Call Report.png` | 68,436 | SDR native-report capture (9/29) |
| `followup-workflow-canvas.png` | 147,027 | GHL workflow canvas capture (7/29) |
| `ghl-followup-workflow.network-response` | 180,425 | GHL workflow GET response capture (7/30) |
| `ghl-followup-workflow-v39.network-response` | 1,733 | v39 readback capture (7/30) |
| `ghl-owner-alignment-response.json` | 18,058 | owner-alignment workflow GET capture (7/30) |
| `ghl-owner-alignment-trigger.json` | 918 | trigger readback capture (7/30) |
| `screenshot_stale_executions.jpg` | 68,778 | stale-executions debug screenshot (7/25); git-ignored single copy — archived to keep evidence |

Total ≈ 1,031,514 bytes (16 files). **Reference check:** every basename above was searched
across all repo Markdown/scripts/JSON/YAML — only hit is the 2026-11-05 handoff prompt list
(excluded as historical). No active doc link breaks.

**Destination:** `local-archive/report-captures-2026-11/` (already holds the 9 root `tmp*`
captures from batch 2). Tracked files: `git rm --cached` after copying.

## Execution record (filled after execution)

- Moved 16/16 via `Move-Item` (15 tracked + 1 ignored screenshot) to
  `local-archive/report-captures-2026-11/` — folder now 25 files (9 prior + 16 new).
- `git rm --cached` on the 15 tracked paths → staged index deletions only.
- `git diff --check`: **PASS**.
