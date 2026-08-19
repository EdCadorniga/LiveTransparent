# LinkedIn Send-Path Double-Escape Corruption Fix - 2026-08-19

## Outcome

Fixed the second, silent layer of the LinkedIn text-corruption bug that produced garbled invites/DMs (e.g. `"ameron co-fo'nder of Transparent e"om` instead of `Cameron co-founder of Transparent eCom`). The 2026-08-18 REST-PUT repair had fixed the dispatcher **crash** layer (`identifier()` `\\/` regex SyntaxError) and the daily limit, but it inherited the still-broken `sanitize()` and `{first_name}` regexes. This session fixed the remaining corrupt regexes in the Dispatcher and DM Sequence, re-published both, and scanned the whole instance for other Code-node double escapes.

## Timeline correction (important)

- **2026-08-11** MCP mutation (`3b70854e-c70a-4c9f-808e-f39df5afc8b6`, "Escaped inline SQL") double-escaped regex literals in the Code nodes. This produced TWO distinct failures over time.
- **2026-08-11 -> 2026-08-18**: the Dispatcher **crashed at parse time** on `identifier()`'s `/^https?:\\/\\//i` (double-escaped `//`), so it sent **nothing** (execution `760794`, 08-17 23:45, `SyntaxError: Invalid regular expression flags`). No garbled invites were sent during this window.
- **2026-08-18 00:15** (`760849`): the 08-18 REST PUT fixed `identifier` to `/^https?:[/][/]/i` and enforced the 60/day cap, so the Dispatcher **started succeeding and sending** — but with `sanitize()` and `{first_name}` still double-escaped. **Garbled invites were sent starting here**, not from 08-11.
- **2026-08-19 ~13:13 UTC**: this session's fix published as `0a349cdb`; the corrupted regexes were fully replaced. Latest scheduled run `765214` (08-19 04:45) hit the cap (60/60) and sent 0, confirming no sends occur once the daily cap is met.

So the "we sent garbage" window is **~08-18 00:15 through 08-19 04:45** (bounded by the 60/day cap), not since 08-11.

## Root cause

Single-backslash `\uXXXX` and `\{` regex literals in the code nodes were left with **two backslashes** (`\\u2018`, `\\{first_name\\}`) after the 08-11 MCP edit. Because these are still syntactically valid JS, n8n saved/published each mutated node without a parse error. At runtime:

1. `sanitize()` char class `/[\\u2018\\u2019]/` no longer matches the Unicode smart-quote range; instead the class matches the literal characters `u`, `C`, `D` and digits `2/0/1/8/9`, so `C`→`"`, `u`→`'` (and `D`/digits) mangled every message that passed through `sanitize()`.
2. `/\\{first_name\\}/gi` matched only a literal `\{first_name\}`, so `{first_name}` was **sent unreplaced**.

The 08-18 REST PUT inherited these bodies without touching them (it only replaced the crash-causing `\\/` and added the cap). Same failure class as the 2026-07-15 mojibake fix — see `AGENTS.md > Unicode Encoding Fix`.

## Fixes applied

Automated with `scripts/fix_linkedin_sanitize_double_escape.py` (idempotent jsCode transform; dry-run report mode), then re-published via the n8n API so each workflow is **updated AND published**.

| Workflow | ID | Change | Published active version |
|---|---|---|---|
| LT - GHL LinkedIn Connect Dispatcher (Unipile) | `fXxw5lanZcDmUrst` | `sanitize()` 8 double-escapes -> single; `{first_name}` regex; `[^\\s,]` URL class | `0a349cdb-295f-45a5-978a-2f3e46022ace` |
| LT - LinkedIn DM Sequence (Unipile) | `d0tEtijajisIsYcs` | `{first_name}` regex in `Sync Connected from Unipile` and `Send DM Sequence Messages` | `db7dde63-2f6e-42e8-92f0-7f68c66e7445` |

Both verified `versionId == activeVersionId`, `active: true`.

### Full-instance scan

Scanned all 164 non-archived workflows for any remaining `\\u2018`/`\\u2019`/`\\u201C`/`\\u201D`/`\\u2013`/`\\u2014`/`\\u2026`/`\\u00A0`/`\\{first_name\\}`/`[^\\s,]` double-escaped regex literals. Only the two workflows above were affected; no other Code nodes require changes.

## Verification

- Live `jsCode` confirmed fixed on both published versions: `identifier` uses `/^https?:[/][/]/i`, `sanitize` uses single `\u` escapes, and the invite build is `sanitize(CFG.defaultMessage.replace(/\{first_name\}/gi, firstName))`.
- Test invite sent to a real profile via Unipile: rendered clean. Because the test profile (Cameron) was already 1st-degree, the invite landed in the existing chat thread rather than surfacing as a new connection request, so a test DM was also sent and delivered clean.
- Scheduled dispatcher runs are `success` with cap behavior (`sent:10` when under cap, `Daily invite limit reached (60/60)` at cap, e.g. `765214`). No duplicate/corrupt sends.
- Next step: capture the first post-fix run that dispatches a new (non-capped) invite as final long-run confirmation.

## Files

- Fix script: `scripts/fix_linkedin_sanitize_double_escape.py`
- Session notes (this file): `docs/sessions/2026-08-19-linkedin-double-escape-fix.md`