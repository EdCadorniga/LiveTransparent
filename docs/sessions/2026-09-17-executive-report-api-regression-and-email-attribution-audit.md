# Executive Report API Regression + Email Attribution Live-State Audit

Date: 2026-09-17
Type: read-only audit. No workflow, CRM record, campaign, sender, database, or deployment was mutated.
Trigger: audit of the Executive Summary API, Campaign Channel Summary, Email Event Ingest,
Newsletter tracking/event workflows, DAN/Emerald/Partnership dispatchers, and the
GHL-triggered mass-email pipeline.

## 1. Headline finding (CRITICAL)

**The Executive Summary API is broken and will fail on every invocation.**

- Workflow: `LT - Report Executive Summary API` (`Bukc0mgOD2r7V6ED`), active,
  `versionId == activeVersionId == e84eff79-922e-4b7e-a17c-3fe28b4c12a8`.
- Failing execution: `958610`, status `error`, started `2026-09-17T14:56:45Z`.
- Last known-good executions: `956097` / `956096`, status `success`, `2026-09-16T19:44:20Z`.
- There is no successful invocation after the 2026-09-17 edits.

### Root cause

PostgreSQL error raised on the `Query Summary` node:

```
column reference "contact_id" is ambiguous
```

The CTE `email_campaign_attribution` (added 2026-09-17) joins two relations that both expose
`contact_id`:

```sql
FROM email_send_rows s
LEFT JOIN email_unique_campaign_contacts u ON u.contact_id = s.contact_id
LEFT JOIN "Email_Events" e ON e.contact_id = s.contact_id AND e.event_ts >= $1::date AND e.event_ts < ($2::date + INTERVAL '1 day')
```

Five unqualified `contact_id` references remain in that CTE select list:

| Select-list line | Expression | Ambiguity |
| --- | --- | --- |
| 9 | `COUNT(DISTINCT contact_id) FILTER (WHERE sent_count = 1) AS unique_recipients` | `s.contact_id` vs `e.contact_id` |
| 14 | `COUNT(DISTINCT contact_id) FILTER (WHERE sent_count = 1)` twice (open_rate guard and denominator) | same |
| 15 | `COUNT(DISTINCT contact_id) FILTER (WHERE sent_count = 1)` twice (click_rate guard and denominator) | same |

`sent_count`, `campaign_key`, and `campaign_group` resolve unambiguously (they exist only on
the send-ledger side). Only `contact_id` needs qualifying.

### Safe fix (draft-only until approved)

Qualify the five bare references as `s.contact_id` inside `email_campaign_attribution`.
No data change, no schema change, no backfill. Then:

1. Re-read the workflow and confirm the edit landed on the draft.
2. Invoke the endpoint once (`GET /webhook/lt-report-executive-summary?range=30d`) and confirm
   HTTP 200 with a populated body BEFORE publishing.
3. Publish, then re-verify `versionId == activeVersionId`.

### Why the regression escaped

`docs/sessions/2026-09-17-executive-report-email-attribution.md` records this change and states
"No production or manual workflow executions were launched during this change." The publish was
verified by version comparison only; the new SQL was never executed. One post-publish
invocation would have caught it. Treat any publish that includes SQL or Code changes as
requiring one executed smoke test as part of the change itself.

Version history for `Bukc0mgOD2r7V6ED` (retention is only 3 versions):

| versionId | created |
| --- | --- |
| `e84eff79-922e-4b7e-a17c-3fe28b4c12a8` | 2026-09-17T14:16:11.980Z (active, broken) |
| `a30adb0e-0aaa-498b-b839-5618fecc140c` | 2026-09-17T14:15:28.086Z |
| `a3e1660f-7bd3-4157-8e5c-b55e5d2aa923` | 2026-08-04T05:53:28.358Z |

The 2026-08-25 version `f49277bb` referenced in AGENTS.md is not retained. Recovery is the
targeted `s.contact_id` fix, not a version restore.
## 2. Verified live state (2026-09-17)

Every active in-scope workflow reports `versionId == activeVersionId`.

| Workflow | ID | Active version | Last execution |
| --- | --- | --- | --- |
| Executive Summary API | `Bukc0mgOD2r7V6ED` | `e84eff79-922e-4b7e-a17c-3fe28b4c12a8` | **error** 2026-09-17T14:56:45Z |
| Campaign Channel Summary | `MvPLbUAN9IIQikxb` | `36c871e0-c4c0-47b1-8b10-f5944a2bad2d` | success 2026-09-16T21:01:56Z |
| Email Event Ingest | `ZrqFN8qLKO8eVHDc` | `40c61586-e462-43dd-bddd-004d4b0b796d` | success 2026-09-17T14:43:43Z |
| Newsletter Open Pixel | `HkTQ9mqwHcpg3AIM` | `dbe9725c-9e70-472c-8a3d-a30a71e3a3eb` | active |
| Newsletter Click Track | `HZ8ndNF4p80PrQjf` | `672c4fcb-dd1c-4c92-8c01-7461910e9419` | active |
| Newsletter Unsubscribe | `RvYusUSGB79K2e2k` | `c1ee71ca-6df6-4de8-a4f5-9428fc863e5a` | active |
| Newsletter Contact Prep | `vvPdJMzBJMgcf5I9` | `80ae911a-73aa-4832-ac55-dcc421400b46` | schedule only |
| Newsletter Dispatcher | `vru7OtCkDnPJkWt2` | `056472a2-f172-4a9b-beac-6d27d4628212` | success 2026-09-17T15:24:00Z |
| DAN dispatcher | `toUG1yPDmFG48KEP` | `3f5b124b-595e-4573-b75e-a6d7ba93cc70` | success 2026-09-17T15:30:37Z |
| Emerald dispatcher | `8UXlpoMJnQ229AuG` | `c63eaa03-8907-47a0-820a-c4143f89949a` | success 2026-09-17T15:00:13Z |
| Partnership Email Dispatcher | `Xshck23cKo1yXL9D` | `9d8520bf-bb5e-49e5-9deb-a718e7283b42` | success 2026-09-17T15:00:00Z |
| Partnership Reply Poller | `0SQ7tTk03okegp9V` | `332930dd-d50a-4456-9138-39a0ec7c2e8f` | **error** 2026-09-17T13:25:34Z |
| Mass intake | `t5frjtbuKzVZI294` | `9523da34-9306-462b-b24f-72594a62a023` | none recorded |
| Mass queue | `vRXRFC6IwIxUME2k` | `714b2d22-777c-4006-a233-d7e0fa6eb930` | success 2026-09-17T15:30:18Z (dry-run) |
| Mass dispatcher | `b41Sas8FVVrytZrl` | `bf892c33-edca-416d-9b74-cff2ccea9fdf` | success 2026-09-17T15:30:07Z (dry-run) |
| Mass open / click / provider tracking | `J7xZH6BBnoXEQsoB`, `TbYFpB80xSlRZ6gy`, `f87KRQ1Slhs9VUxJ` | inactive, no active version | n/a |

In-flight check: no executions in `new`, `running`, `waiting`, or `crashed`.

A cluster of workflows was modified 2026-09-17 14:09-14:17Z (three dispatchers, newsletter
prep + dispatcher, Exec Summary). Only the Exec Summary regressed; the others executed
successfully afterwards.

Confirmed live control values (no secrets recorded):

- Newsletter dispatcher `defaultDryRun = false` (LIVE sending), `maxPerRun = 130`.
- Mass dispatcher `defaultDryRun = true`, `maxPerRun = 200`, `maxPerSenderPerDay = 2333`.
- Newsletter + mass sender pools both `cameron@livetransparent.co,cameron@livetransparent.agency,cameron@livetransparent.org`.

## 3. API Regression Resolution (2026-09-17)

- The five ambiguous `contact_id` expressions in `email_campaign_attribution` were qualified as `s.contact_id`.
- `Shape Response` was also updated to project `emailCampaignAttribution` and `emailAttributionCoverage`; the SQL fields were otherwise being dropped before the public response.
- The workflow was published at active version `4816fea0-3722-4d59-b552-bc84a616e948`; fresh REST verification confirmed `versionId == activeVersionId`.
- Public smoke test: `GET https://reports.livetransparent.com/api/report/executive/summary?range=30d` returned HTTP 200 with a 36,184-byte body, 8 attribution rows, and coverage metadata: `sendRows=78,729`, `campaignKeyRows=78,729`, `uniqueRecipients=26,350`, `unknownCampaignRows=0`, `unambiguousRecipients=271`.
- Sample attribution output included `newsletter_2026-08-24` with `sent=43,486`, `failed=1,351`, and `unique_recipients=24,811`.
- No production sender workflow was executed and no email was sent. The first follow-up pass is now deployed: Newsletter Dispatcher dynamically selects the newest pending week and matching builder; Campaign Channel Summary preserves explicit campaign keys and maps the live Emerald event labels; Email Event Ingest captures message ID, provider message ID, source event ID, campaign key, and sender email. DAN event automations still require explicit wiring; historical attribution remains conservative where a recipient maps to multiple campaigns.

## 4. Follow-up implementation verification (2026-09-17)

- Newsletter Dispatcher `vru7OtCkDnPJkWt2`: active/published version `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff`; `versionId == activeVersionId`. `Fetch Newsletter Template` reads pending week keys from `newsletter_send_log`, selects the newest pending week, finds the matching newsletter builder by week key, and fails closed when the builder is absent. `Build Fetch Bucket SQL` uses the active and prior pending week dynamically; it contains no hardcoded historical week keys.
- Campaign Channel Summary `MvPLbUAN9IIQikxb`: active/published version `9bcb5e46-f2a4-484a-ad6e-7761c6538cef`; `versionId == activeVersionId`. The query adds idempotent attribution-column guards and maps `campaign_id = Emerald Cannabis Ads` plus `WL - Event - Emerald Email Event Ingest - *` to `Emerald - Email Event`, while honoring an explicit stored `campaign_key` first.
- Email Event Ingest `ZrqFN8qLKO8eVHDc`: active/published version `e57c2664-f0f1-484f-b3a6-32bba41ff125`; `versionId == activeVersionId`. New events persist `message_id`, `provider_message_id`, `source_event_id`, `campaign_key`, and `sender_email`; the insert applies the column guards idempotently.
- Public regression check: `GET https://reports.livetransparent.com/api/report/executive/summary?range=30d` returned HTTP 200, 36,184 bytes, 8 attribution rows, `sendRows=78,729`, `campaignKeyRows=78,729`, `unknownCampaignRows=0`, `uniqueRecipients=26,350`, and `unambiguousRecipients=271`.
- Safety boundary: no production sender workflow was manually executed; no email was sent. The dynamic newsletter code will act on the next scheduled run, but this change was not used as a send test.

## 5. Follow-up regression and repair (2026-09-17)

- Adding the durable `Email_Events.campaign_key` column exposed a second SQL ambiguity in the Executive Summary attribution CTE: the existing bare `campaign_key` and `campaign_group` references became ambiguous after `Email_Events` gained the same column name.
- Symptom: Query Summary executions `958878` and later failed with `column reference "campaign_key" is ambiguous`; the public endpoint could return HTTP 200 with an empty body. The frontend catches failed fetches and therefore displayed loading/zero placeholders instead of surfacing the API failure.
- Repair: qualified the attribution CTE projection and grouping as `s.campaign_key` and `s.campaign_group`. Published Executive Summary version `da17ea49-6473-4e33-9df5-9d93bf6cf273`; read-back confirmed `versionId == activeVersionId`.
- Verification: `GET https://reports.livetransparent.com/api/report/executive/summary?view=overview&range=30d&embed=1` returned HTTP 200 with 36,184 bytes. The latest Executive Summary execution succeeded and returned current values including 1,855 recorded visits, 2,131 contacts, 2,929 opportunities, 9 meetings, and email metrics. No sender workflow or email was executed.
- Operational lesson: validate both HTTP status and non-empty JSON body, and treat `200 + zero bytes` as an API failure. The report query remains slow (roughly one to two minutes), so the embed should eventually receive a visible loading/error state or a backend cache rather than silently rendering zero-like placeholders.
