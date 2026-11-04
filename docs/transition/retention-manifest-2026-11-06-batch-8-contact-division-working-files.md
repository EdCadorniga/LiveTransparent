# Retention manifest — batch 8: contact-division working files (2026-07-29 wave) (2026-11-05/06)

Mandate: [repo-organization handoff prompt](../sessions/2026-11-05-developer-transition-repo-organization-handoff-prompt.md)
§Root loose files ("working cohort files …"). Classification: one-time working outputs of the
2026-07-29 Warm/not-qualified/MQL/SQL division + domain-classification wave; superseded by
completion of that work and by GHL being system of record. **Archived rather than deleted**
because split outputs carry contact data (PII) and remain evidence of the division decisions.

| Path | Bytes | Notes |
|---|---|---|
| `contacts_not_qualified_tag.csv` | 42,077 | contacts joined to `not qualified` tag |
| `to_move_not_qualified.csv` | 53,296 | move list |
| `warm_not_qualified_opps.csv` | 32,649 | Warm not-qualified opportunities |
| `warm_mql_opportunities.txt` | 31,695 | Warm MQL opportunity IDs |
| `warm_new_opportunities.txt` | 1,597,484 | Warm→New opportunity IDs |
| `sales_outreach_qualified_opps.txt` | 87,239 | Sales Outreach Qualified IDs |
| `Test - Leads - Domains classification.csv` | 187,029 | domain-classification test sheet |
| `csv_matched_opps.csv` | 714,815 | CSV→opportunity matched pairs |
| `csv_unmatched_opps.csv` | 106,417 | unmatched remainder |
| `duplicate_opp_contacts.csv` | 178,937 | duplicate opportunity/contact rows |
| `fix_errors.txt` | 49 | error remnant |
| `move_errors.txt` | 320 | error remnant |

Total ≈ 3,031,686 bytes (12 files). **Reference check:** basenames searched across all
Markdown/scripts/JSON/YAML — only the 2026-11-05 handoff prompt references them (historical).
No active doc link breaks.

**Destination:** `local-archive/contact-division-2026-07/` (git-ignored). Tracked files:
`git rm --cached` after copying.

## Execution record (filled after execution)

- Moved 12/12 via `Move-Item` → `local-archive/contact-division-2026-07/` (12 files present).
- `git rm --cached` on all 12 paths → staged index deletions only.
- `git diff --check`: **PASS**.
