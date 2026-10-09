# Jason Follow-up Email Links — Closeout (2026-10-08)

## Objective

Correct the booking CTA destinations in the six GHL email templates under **Jason Follow Up Emails** and check whether their remaining GHL trigger-link references resolve.

## Completed live GHL changes

- Folder: `Jason Follow Up Emails`, ID `69e0c9069af5986541802d88`.
- Booking destination set to `https://api.leadconnectorhq.com/widget/booking/WS6lacfQK2XOhqN7mRaF?utm_source=followupemails` in each template:
  - `Jason - 01 - The Real Reason Meta Isn't Working For You` — `69e0d86b9af59801b580f4b5`
  - `Jason - 02 - Most Cannabis Brands Are Locked Out (Including You?)` — `69e0db27d6a707bbf190d022`
  - `Jason - 03 - How Brands Like Mood Are Scaling Ads` — `69e0db9ab02114c1ba3c29d3`
  - `Jason - 04 - Appropriate Marketing Contact` — `69e0dc56d6a707c0ac90e074`
  - `Jason - 05 - Cannabis Ads: Next Steps_EngagedExecutive` — `69e0dcad8ffabf47b4d987c5`
  - `Jason - 06 - Cannabis Ads: Next Steps_EngagedMarketing` — `69e0ddd0b021145bab3c4569`
- Fresh Firebase preview readback verified the new booking URL in all six templates. Booking CTA occurrence counts by template order above: 1, 1, 2, 1, 2, 2. Other destinations, including logo/site links, were preserved.
- Inventory of the saved templates found one remaining unique trigger-link merge token: `{{trigger_link.fRvpZgP1WOghlgY1ARiB}}`, used for the logo/site link in all six. The documented GHL Trigger Links API returned 15 links for the location and confirmed `JohnWebsiteLinkInFollowups` (`fRvpZgP1WOghlgY1ARiB`) exists, redirecting to `https://livetransparent.com/?utm_source=email&utm_medium=outreach&utm_campaign=johnCannabis&utm_content=visit_site_john`. No missing trigger-link references were found.

## Unresolved verification

- Whether `JohnWebsiteLinkInFollowups` is configured as a trigger for any GHL workflow was **not established**. The link exists, but workflow trigger/action details were not available in this session. Next: inspect GHL workflow triggers for the exact trigger-link ID/name and report the matching workflow(s), if any.
- The template-library HTML was updated through the GHL email-builder endpoint. Although Ed said the relevant Send Email action is synced to its template, no action-level template linkage or **Sync Edits to Template** setting was freshly read back. Verify the relevant workflow action(s) in GHL before asserting that the updated CTA has propagated into the action configuration. Do not send a test email or publish/change workflows without separate authorization.

## Repository state and verification

- No application code, tests, or deployments were changed/run in this session.
- `AGENTS.md` was updated with this durable status and handoff.
- At session start the worktree already contained an `AGENTS.md` modification plus untracked Nicotine/Mushroom source, import-preparation, and handoff files. They were not staged, removed, or otherwise modified by this closeout.
- Live verification performed: successful GHL template PATCH responses for all six templates; fresh preview GETs confirmed the new URL in all six; GHL Trigger Links API lookup confirmed the remaining trigger link exists. No email, automation execution, workflow publication, or contact mutation was performed.

## Next session

1. In GHL, search the workflow trigger configuration for `JohnWebsiteLinkInFollowups` / `fRvpZgP1WOghlgY1ARiB`; report the exact automation name and state if found.
2. Inspect Send Email actions that use the six templates; confirm each action is still linked to the intended template and determine whether sync is enabled / reflected.
3. If workflow template linkage is stale, update/reselect only the appropriate template actions, accept any confirmation dialog, save, then freshly read back the action-template linkage and sync setting. Do not send a live test or publish unless separately authorized.
