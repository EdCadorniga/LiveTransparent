# Newsletter Deliverability Audit + DND Suppression Fixes

Date: 2026-09-09

## Objective

Audit email deliverability for the weekly newsletter path and fix the two structural weaknesses found: stale-email re-attempts and repeated sends to GHL-suppressed (DND) recipients.

## Findings

- **Blocklists clean**: livetransparent.com/.co/.agency/.org plus the VPS IP are clean on Spamhaus ZEN, SpamCop, Barracuda, SORBS, SURBL.
- **SPF correct**: all sending domains include `include:spf.leadconnectorhq.com` (verified GHL sender IPs 134.199.x/216.163.x/209.162.x) plus Google + Mailgun.
- **DMARC gap**: `.co/.agency/.org` (the newsletter From domains) run `p=none`. Only `google._domainkey` exists (Workspace signing); **no GHL custom-domain DKIM selector exists**, so DKIM does not align to the From domains. `.com` is already `p=reject`.
- **Engagement**: week of 08-31 ≈ 21% unique open / 22% unique click; unsub rate 0.3–1.0%/day.
- **Failure cause identified**: the ~2.7% GHL 400 rejections (`CONVERSATIONS_MSG_INVALID_EMAILTO`) are **not** sender-related and **not** stale-email — the recipient's email matches GHL exactly, but the contact has **Email DND suppression active** (prior bounce/spam-complaint/unsubscribe, e.g. `dndSettings.Email.status=active`). Verified live on 5 sampled contacts. GHL correctly refuses sends to suppressed addresses; the senders are irrelevant.
- **Recurring waste**: 1,589 unique emails have failed at least once; 191 fail every single week because Prep re-queues all eligible GHL contacts without checking DND status, then the dispatcher re-rejects them.
- **No bounce/complaint feedback loop**: GHL emits no webhooks for `POST /conversations/messages`, so `status='sent'` only means "GHL accepted it".

## Changes Applied (all live n8n, published + verified)

### 1. `LT - Newsletter Dispatcher` (`vru7OtCkDnPJkWt2`, active `9774bd27-0e23-48da-a512-889ac49a6c61`)

`Dispatch Emails` Code node now:
- Detects `CONVERSATIONS_MSG_INVALID_EMAILTO` 400s, fetches the contact's current GHL email (`contact.email` + `additionalEmails`), and retries once with a corrected address.
- Marks the row terminal `invalid_email` (instead of `failed`) when no usable current email exists or the retry also fails.
- Adds GHL tag **`newsletter_dnd_suppressed`** on every `invalid_email` outcome (best-effort, non-blocking).
- `Dispatcher Summary` now reports `invalid_email` and `recovered` counts.

### 2. `LT - Newsletter Contact Prep` (`vvPdJMzBJMgcf5I9`, active `8c3342d0-793d-4c22-9d5b-b8191aeeaea4`)

- `Build SQL - Insert Plan`: changed `ON CONFLICT (ghl_contact_id, week_key) DO NOTHING` → `DO UPDATE SET contact_email/first_name/sender_email = EXCLUDED.*` so a changed email is refreshed on later prep runs of the same week.
- `Config` `blockedTags` is now `do not contact,do not nurture,newsletter_dnd_suppressed`, so contacts tagged by the dispatcher are excluded from future queueing. Edited via direct n8n REST PUT (Set v3.4 node — `setNodeParameter` array-path failed).

## Verification

- Dispatcher: active, 8 nodes, `versionId == activeVersionId == 9774bd27`.
- Prep: active, 8 nodes, `versionId == activeVersionId == 8c3342d0`.
- No uncontrolled send performed. The dispatcher's live schedule (`*/12 7-19 * * 1-5`) will exercise the new recovery path on its next run.

## Remaining / Recommended Next Steps

1. **DKIM alignment (highest impact, operator action)**: add GHL's custom-domain DKIM records to `.co/.agency/.org` (selector per GHL Email/Domain settings). Currently only `google._domainkey` exists.
2. **DMARC enforcement**: after DKIM aligns, move the 3 sending domains from `p=none` → `p=quarantine` → `p=reject`.
3. **Delivery visibility**: set up Google Postmaster Tools on the 3 domains and run a seed-list/placement test (GlockApps/250ok) on Gmail/Outlook/Yahoo — there is currently zero bounce/complaint data on this path.
4. **Watch burst behavior**: the 09-03 spike (1,275 failures in ~4h, self-recovered) was GHL-side and is mitigated by the retry logic; confirm cap math holds as volume grows.
5. **Optional one-time sweep** (not required): retroactively fetch previously-`failed` contacts and tag DND ones with `newsletter_dnd_suppressed`. They are already excluded from fetching (`status='pending'` only), so this is hygiene-only.

## Repository State

The worktree already contained unrelated user/agent changes (SDR attribution phase docs, incident-alerts review, SimpleTexting route fix) before this closeout. This session added only this session record and the corresponding AGENTS.md / Project Status entries; no unrelated files were reverted or modified.