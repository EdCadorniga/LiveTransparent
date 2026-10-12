# 2026-10-10 — Gambling + Cannabis Dispensaries 12px template restyle (+ workflow previewUrl refresh)

## Objective
Ed directive: fix the styling inconsistency — the two verticals' email templates used the **14px Alcohol format** while Crypto/Mushroom/Nicotine use **12px**. Reconcile before launching/importing contacts.

## Result
- **10 email templates restyled** (Gambling E1–E5, Cannabis Dispensaries E1–E5) to the Crypto/Mushroom 12px format.
- Both workflows' 20 email Send-action node `previewUrl`s refreshed to the updated template previews.
- Both workflows remain **published**, 0 enrolled.

## Target format applied (Crypto/Mushroom 12px)
```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{subject}</title><!-- outlook-fixes-applied --></head>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:#222;background:#fff;">
  <main style="max-width:600px;margin:0 auto;padding:24px;">
    … paragraphs (copy/links/merge fields preserved verbatim) …
    <hr style="border:0;border-top:1px solid #ddd;margin:24px 0 12px;">
    <p style="font-size:11px;color:#666;">To stop receiving these emails, <a href="{{email.unsubscribe_link}}">unsubscribe here</a>.</p>
  </main>
</body>
</html>
```
- Source (old) format was: `<html><body style="…font-size:14px;line-height:1.5">`, no `<head>`/`<main>` wrapper, bare `<hr>`, footer "you can unsubscribe here".
- Reference formats confirmed: **Crypto/Mushroom = head + `<main>` 600px + styled `<hr>` + 12px**; **Nicotine = 12px but no wrapper** (pre-existing difference; not changed). Chose the fuller Crypto/Mushroom format.
- E3 (both verticals) correctly keep **no** "Free Resource" line; E1/E2 carry it.

### Templates (Gambling folder `6ac8e43939edc5e18c159cf8`)
| # | Template ID | Subject/title |
|---|---|---|
| E1 | `6ac8e8dcf9707340c6901cb1` | Quick question about your ad accounts |
| E2 | `6ac8e9079660fa02e854b290` | Why gambling accounts get banned (and what's fixable) |
| E3 | `6ac8e90708741365d8940fb7` | How restricted brands actually scale |
| E4 | `6ac8e90887cdcc5d6eb6b756` | 30 minutes to unblock your acquisition? |
| E5 | `6ac8e909976a2a32d9f82346` | Should I close this out? |

### Templates (Cannabis Dispensaries folder `6ac8e42a1ea8584cd7a514af`)
| # | Template ID | Subject/title |
|---|---|---|
| E1 | `6ac8e90e4c92b27bd3d9fd53` | Curious how {{contact.company_name}} is funding foot traffic right now |
| E2 | `6ac8e90f9660fa02e854b3ed` | How it works — no cost to install |
| E3 | `6ac8e90f87cdcc5d6eb6b835` | 40% of dispensaries have $0 marketing budget |
| E4 | `6ac8e91039edc5e18c1606dd` | Founding partner spots are limited |
| E5 | `6ac8e911976a2a32d9f82424` | Want to keep your spot open? |

## Method
- **Template content**: `PATCH https://services.leadconnectorhq.com/emails/builder/{id}` with `{locationId, editorType:'html', editorContent:'<full html>'}` using the `.env` GHL PIT. **Cloudflare 1010 blocks python-urllib** — send a browser `User-Agent`. All 10 returned HTTP 200.
- **Read-back**: fresh `fetch-template` `previewUrl` per template, read via webfetch. 10/10 confirmed.
- **Workflow node `previewUrl` refresh**: driven from the authenticated GHL Builder (Playwright). Captured the app `authorization` + `token-id` headers reliably via **Playwright `page.on('request')`** (server-side), filtering `backend.leadconnectorhq.com` — this is more robust than the in-page initScript interceptor, which was flaky (tokens reset between calls; non-backend requests overwrote captured values).

## ⚠️ Incident + corrected PUT recipe (IMPORTANT for future sessions)
The first `previewUrl` PUT used the **GET-response wrapper** as the body → **422 `Version is required`**. Adding a top-level `version` then saved a **malformed doc that emptied the Gambling graph** (read back v12, `templates: undefined`; Builder showed only the trigger → END). Dispensaries was untouched.

**Fix / correct recipe:**
- The workflow PUT body must be the **`workflowData` object** (from `GET …/workflow/{loc}/{id}` → `resp.workflowData`), which carries `version` at its top level and nests the graph at `.workflowData.templates`.
- Body = `Object.assign({}, resp.workflowData, { modifiedSteps:[nodeIds], createdSteps:[], deletedSteps:[], triggersChanged:false, oldTriggers: resp.triggers, newTriggers: resp.triggers })`.
- `PUT https://backend.leadconnectorhq.com/workflow/{loc}/{id}` → 200, `version++`, status preserved (`published`).
- **Always back up the full GET response before PUT** (this backup is what made the restore trivial).

**Restore:** re-PUT the backup `workflowData` (with the current `version`) → Gambling back to **85 nodes / 20 emails**, then applied the `previewUrl` updates in the same write. Dispensaries was then refreshed cleanly the same way.

## Final verified state
| Workflow | ID | Version | Status | Nodes | Emails | Templates | Trigger |
|---|---|---|---|---|---|---|---|
| Gambling Multi-Channel Outbound - Oct 2026 | `4a238825-61d2-49e6-a3d0-4acb3a19c674` | **v13** | published | 85 | 20 | 5 | Entry - Gambling Brands Multichannel Oct 2026 |
| Cannabis Dispensaries Multi-Channel Outbound - Oct 2026 | `365ecf51-d700-4c2d-8058-df20ad523538` | **v10** | published | 85 | 20 | 5 | Entry - Cannabis Dispensaries Brands Multichannel Oct 2026 |

Node mix (both): `if_else 9, email 20, wait 36, webhook 12, voicemail 8`. Email nodes: `template_id` + `syncEnabled:true`, **no inline body** → send renders from the template. `previewUrl` now matches each template's current preview (allMatch true).

## Remaining / follow-up
- Email 3 "40% higher approval rate / 16 months" claims remain unsubstantiated (Ed instructed to accept as truth for now — not changed).
- **No cohort imported** for either vertical yet. Enrollment order = assign per-vertical sender field, then apply enroll tag.
- Nicotine templates remain 12px without the `<main>` wrapper (pre-existing); optionally reconcile later.
- Nothing committed. Temp scripts/backups were created under `.playwright-mcp/` (gitignored) and deleted after use.
