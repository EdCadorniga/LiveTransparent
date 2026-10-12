# EOS — All-vertical email template spacing review

Date: 2026-10-12
Project: `C:\1_Ed's Active Work\Projects\LiveTransparent`
Scope: GHL email template formatting and readback; no workflow edits or sends.

## What was done

- Reviewed Cannabis Brands reference template `6abff1710545fe92f6b4a8e0` (“Email 4 - The Direct Ask”). Its saved HTML uses Arial 14px, 1.25 line-height, zero paragraph margins, and explicit empty paragraph blocks at selected points.
- Updated 35 templates through the GHL location PIT: Alcohol, Nicotine, Mushroom, Crypto, Peptides, Cannabis Dispensaries, and Gambling (five templates per vertical). Cannabis Brands’ five templates already used the reference typography and were not changed.
- Read back all 40 saved previews. All use the 14px / 1.25 / zero-margin style. The copy and links were checked after the update and preserved. No email or SMS was sent.

## Spacing defect found after the update

The typography matches, but paragraph spacing is incomplete. With `margin:0`, adjacent `<p>` elements have no vertical gap unless an empty `<p>&nbsp;</p>` is inserted between them. The sample Alcohol template `6ac516ec0baff29423fe92fe` has four empty paragraphs total: two after the greeting and two before the sign-off, with none between most body paragraphs. The other seven vertical folders follow the same four-spacer pattern. Cannabis Brands has six to nine spacer paragraphs depending on the template, so its body spacing varies by template too.

This explains the issue Ed noticed: the CSS removed the default paragraph margins, while the templates did not add a spacer between each body paragraph. The earlier “all templates follow the same spacing” completion claim was too broad. The updated typography is verified; consistent blank visual separation between body paragraphs is still open. This EOS records the defect; no further template edit was made after Ed asked why the paragraphs run together.

## Current external state

- Official GHL template listing returned 40 campaign templates across eight vertical folders. Fresh preview readback confirmed the typography and spacer counts above.
- No workflow Send actions, preview URLs, or sync settings were refreshed or re-read in this continuation. No workflow sends, executions, enrollment changes, or publication changes were performed.
- The last pushed repository commit is `cba931b` on `codex/social-outreach-sync` (`origin` points to the same commit). It includes five files from the preceding shared-worktree task and is not limited to email formatting.

## Next session

1. Settle one consistent visual rule for ordinary body paragraphs, including whether to use paragraph bottom margins or explicit spacer elements. Preserve the intended two-line separation after the greeting and before the sign-off without creating oversized gaps.
2. Apply the selected rule to all 40 templates, retaining each template’s copy, links, merge fields, and unsubscribe footer.
3. Read back every saved preview and verify actual rendered paragraph spacing, not only CSS. Recheck template copy and link destinations.
4. Review the campaign Send actions’ template sync/preview state if needed. Do not send test emails or alter workflow enrollment/publication as part of formatting work.

## Shared worktree

During EOS review, additional shared-worktree edits appeared after commit `cba931b`. They were left untouched: `AGENTS.md`, `docs/sessions/2026-10-10-gambling-dispensaries-12px-restyle.md`, `reports/embed/executive-v1/index.html`, `scripts/build_last_touch_owner_workflow.py`, `scripts/deploy/deploy_report_vps_local.py`, two Cannabis Dispensaries prep files, and two LinkedIn scripts. The worktree therefore is not clean. No commit or push was made during this EOS.
