# Executive Report Email Attribution

## Implemented

On 2026-09-17, durable campaign keys were added to the live email ledgers:

- DAN: `dan_brands` and `dan_dispensaries`
- Emerald: `emerald_<bucket>`
- Partnership: `partnership_email`
- Newsletter: `newsletter_<week_key>`

The sender release-log writes now populate `campaign_key`, and existing rows are
backfilled when the table-ensure nodes run. The Executive Summary workflow now
returns `emailCampaignAttribution` and `emailAttributionCoverage` in addition to
the existing aggregate email metrics.

The report assigns sends from durable ledger keys. Engagement events are only
attached to a campaign when the recipient maps to one campaign in the selected
window; ambiguous recipients remain unattributed rather than being guessed.

## Live Workflows

| Workflow | ID | Published version |
| --- | --- | --- |
| DAN dispatcher | `toUG1yPDmFG48KEP` | `3f5b124b-595e-4573-b75e-a6d7ba93cc70` |
| Emerald dispatcher | `8UXlpoMJnQ229AuG` | `c63eaa03-8907-47a0-820a-c4143f89949a` |
| Partnership dispatcher | `Xshck23cKo1yXL9D` | `9d8520bf-bb5e-49e5-9deb-a718e7283b42` |
| Newsletter prep | `vvPdJMzBJMgcf5I9` | `80ae911a-73aa-4832-ac55-dcc421400b46` |
| Newsletter dispatcher | `vru7OtCkDnPJkWt2` | `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff` |
| Executive Summary API | `Bukc0mgOD2r7V6ED` | `da17ea49-6473-4e33-9df5-9d93bf6cf273` |

No production or manual workflow executions were launched during this change.
The implementation does not reconstruct ambiguous historical attribution.

## Follow-up work completed 2026-09-17

- Newsletter Dispatcher now derives the newest pending newsletter week from `newsletter_send_log`, discovers the matching GHL builder by week key, and constructs the claim SQL dynamically. It fails closed when the pending week has no matching builder.
- Campaign Channel Summary now honors explicit `Email_Events.campaign_key` values and maps the live Emerald event labels (`Emerald Cannabis Ads` and `WL - Event - Emerald Email Event Ingest - *`) to `Emerald - Email Event`.
- Email Event Ingest now captures `message_id`, `provider_message_id`, `source_event_id`, `campaign_key`, and `sender_email` for new events, with idempotent column guards.
- A follow-up regression occurred because the new `Email_Events.campaign_key` column made bare `campaign_key` references in the Executive Summary attribution CTE ambiguous. The CTE was corrected to use `s.campaign_key` and `s.campaign_group`.
- Final Executive Summary version: `da17ea49-6473-4e33-9df5-9d93bf6cf273`. Final Newsletter Dispatcher version: `88c53670-6e0a-4f2d-a4c4-3f27ca3ffdff`. Campaign Channel Summary: `9bcb5e46-f2a4-484a-ad6e-7761c6538cef`. Email Event Ingest: `e57c2664-f0f1-484f-b3a6-32bba41ff125`.
- Verification returned HTTP 200 with a 36,184-byte populated Executive Summary response. The embed-query request produced current values including 1,855 visits, 2,131 contacts, 2,929 opportunities, 9 meetings, and populated email metrics.
- No sender workflow was manually executed and no email was sent. HTTP 200 with an empty body must be treated as an API failure, not as valid zero data.
