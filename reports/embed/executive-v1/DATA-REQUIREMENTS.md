# Executive Report V1 data requirements

The supplied mockup defines the presentation flow. Its numbers are illustrative; the V1 report must calculate real values for one shared reporting window and must not silently convert missing data into zero.

## Shared rules

- Use one selected date window across all sections, with the reporting timezone applied consistently.
- Preserve the existing `7d`, `30d`, `90d`, and custom-period controls where practical.
- Show the selected period and freshness/source-health context.
- Use explicit `Unknown`, `Unattributed`, `Unassigned`, and `Unavailable` buckets.
- Treat HTTP 200 with an empty report body as a failure.
- Every metric needs a short definition and a source note in the UI or glossary.
- Validate that totals reconcile across headline cards, breakdowns, and tables before review.

## P0 — trustworthy numbers

| Mockup area | Required real values | Current source / status | Validation needed |
|---|---|---|---|
| Headline row | New MQLs, new SQLs, MQL→SQL, unique Cameron booking contacts, new contacts, opportunities created | Executive Summary API plus V1 appointment facts | Count distinct non-empty contact IDs for Cameron-assigned bookings in the selected window; cancellation/reschedule appointment rows for the same contact count once |
| Opportunities by source | Opportunities grouped by source/campaign | Executive Summary attribution and campaign/source payloads | Distinct opportunity IDs; exclude classified historical backfill contacts where required |
| MQL sources | MQLs by originating source | `leadSourceBreakdown` / `leadSourceCoverage` | Display coverage and Unknown / Unattributed rather than implying full attribution |
| SQL sources | SQLs by originating source | `leadSourceBreakdown` / `leadSourceCoverage` | Reconcile sum of rows to SQL denominator |
| New contacts — how added | Contacts by acquisition/addition mechanism | GHL contacts, source fields, backfill classifier, campaign/import markers | Define LinkedIn backfill, Apollo upload, form, manual/other buckets without double counting |
| Meetings — who & where | Contact, SDR/owner, booking link/calendar | Appointments snapshot plus contact/opportunity owner mapping | Verify appointment-to-contact and originating-SDR attribution; expose Unassigned; keep the headline KPI distinct-contact based for Cameron |
| Meeting outcomes | Showed, no-show, cancelled, rescheduled | GHL appointment statuses | Do not infer Showed; current status-update gap may require Unavailable or clearly labelled 0 |
| Pipeline to work | Qualified/open work remaining this period | Opportunity snapshot/stage data | Define “qualified” and “remaining”; avoid mixing active snapshot with created-in-period |
| Lead-source coverage | Attributed / total and percentage | `leadSourceCoverage` | Coverage denominator must match MQL/SQL cards |
| Speed-to-lead / follow-up | Response time from inbound LinkedIn DM, inbound call, or marketing-email reply to the next outbound event on the same channel; unmatched inbound count | `lt_exec_v1_response_sla`, materialized from LinkedIn activity, `Email_Events` + marketing send ledgers, and GHL call outcomes | Match by contact/channel and later timestamp; publish average/median only with response denominator; do not call unmatched records “overdue” until a business target is configured |

## P1 — layout and channel story

## Feedback extension — funnel, movement, retargeting, and Priority

- Funnel order is opportunities, MQLs, SQLs, meetings, closed won/lost, and revenue. Closed-by-source keeps referral and other valid sources in the denominator; residuals are `Unknown / Unattributed`.
- Weekly flow uses distinct contact IDs for new leads and distinct opportunity IDs for stage movement. Current stage distribution is a snapshot, not a period-entry count.
- Vertical reporting uses the canonical vertical/source field and retains `Unclassified`; unsupported metrics are unavailable.
- Retargeting is queue visibility only: eligible contacts, latest click/audience touch, suppression/reply state, and next action. It does not authorize a send.
- Inbound response speed retains the same-channel SLA contract. It is not MQL-to-first-call.
- Priority is `Sales Outreach` stage `be636da7-3c15-48ab-b589-c75bcd6f9955`; closed opportunities are protected and retries are keyed by contact plus source event.

| Mockup area | Required values | Likely source |
|---|---|---|
| Outbound total strip | Emails, LinkedIn messages, SMS, voicemails, newsletters | Campaign Channel Summary plus channel ledgers |
| Email campaign table | Sent, delivered, opened, clicked, replied, bounced | Email send/event ledgers and Campaign Channel Summary |
| LinkedIn campaign table | Invites, accepted, messages delivered, opened if available, replied | `linkedin_activity_events` and campaign attribution |
| SMS table | Sent, delivered, replies, failed | SimpleTexting event ledger / campaign summary |
| Voicemail table | Latest custom disposition per unique contact; voicemail drops/left and callback-requested counts | `voice_call_attempt.disposition`, materialized into `lt_exec_v1_call_facts` |
| SDR performance strip/table | Calls attempted, connected, no answer, busy/failed, wrong number; per SDR effort and outputs | GHL call records, Vapi call ledger, appointments, SDR performance payload |
| Social media strip/table | Posts, impressions, reach, engagement, followers by channel | GHL Social Planner post ledger and account statistics |
| Action queue | MQL response SLA, stale contracts/proposals, overdue follow-ups | GHL opportunity/task/activity timestamps plus agreed SLA rules |

## Known data gaps to surface early

1. Appointment outcomes are not reliable until GHL status is updated after meetings; do not manufacture showed/no-show values.
2. Social reach, impressions, saves, and follower statistics may be unavailable when the GHL OAuth/statistics source is not authenticated.
3. Selecting the voicemail custom disposition is the business rule for “voicemail left”; drops sent and delivered therefore use the same latest-disposition unique-contact count. Callback-requested counts use explicit callback dispositions.
4. Response speed is now collected from durable same-channel event timestamps. A response-time target is still not configured, so the report shows unmatched inbound events rather than inventing an overdue threshold.
5. Email engagement must show coverage and use unique-recipient rates where possible; missing provider events must not be presented as zero engagement.
6. SDR call-input metrics need one agreed call source and deduplication rule before they are combined with booked/SQL/MQL outputs.

## Acceptance checks before V1 review

- API response is non-empty JSON and all required source-health rows are ready or visibly flagged.
- Headline numbers reconcile to the corresponding breakdowns.
- MQL/SQL/contacts/opportunities use documented distinctness and period rules.
- Meeting totals reconcile to the appointment table and SDR rows.
- Channel totals reconcile to the campaign tables, with unattributed activity shown separately.
- No unavailable source is rendered as a trustworthy zero.
- Desktop and approximately 390px mobile layouts have no horizontal overflow.
- The existing Executive Report remains unchanged and still renders from its original path.
