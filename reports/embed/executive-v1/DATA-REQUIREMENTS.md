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
| SQL sources | SQLs classified by booking path: SDR or calendar link; show SDR name or calendar link name + UTM | `sqlBookingBreakdown` from the V1 facts API | Classify every SQL into exactly one of the two paths; coverage is always 100%. A calendar-link booking without UTM remains classified as Calendar link and is flagged `Missing UTM` for tracking repair. Never show an Unknown source bucket. |
| New contacts — how added | Contacts by acquisition/addition mechanism | GHL contacts, source fields, backfill classifier, campaign/import markers | Define LinkedIn backfill, Apollo upload, form, manual/other buckets without double counting |
| Meetings — who & where | Contact, SDR/owner, booking link/calendar | Appointments snapshot plus contact/opportunity owner mapping | Verify appointment-to-contact and originating-SDR attribution; expose Unassigned; keep the headline KPI distinct-contact based for Cameron |
| Meeting outcomes | Showed, no-show, cancelled, rescheduled | GHL appointment statuses | Do not infer Showed; current status-update gap may require Unavailable or clearly labelled 0 |
| Pipeline to work | Qualified/open work remaining this period | Opportunity snapshot/stage data | Define “qualified” and “remaining”; avoid mixing active snapshot with created-in-period |
| Lead-source coverage | Attributed / total and percentage | `leadSourceCoverage` | Coverage denominator must match MQL/SQL cards |
| Speed-to-lead / follow-up | Response time from inbound LinkedIn DM, inbound call, or marketing-email reply to the next outbound event on the same channel; unmatched inbound count | `lt_exec_v1_response_sla`, materialized from LinkedIn activity, `Email_Events` + marketing send ledgers, and GHL call outcomes | Match by contact/channel and later timestamp; publish average/median only with response denominator; do not call unmatched records “overdue” until a business target is configured |

SQL booking-path and email Trigger Link attribution implementation plan: [`docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md`](../../../docs/sessions/2026-10-09-sql-booking-and-triggerlink-attribution-plan.md). This requires a fresh readback of appointment creator/booker fields, calendars, campaign Trigger Links, and existing attribution workflows before implementation.

## P1 — layout and channel story

## Feedback extension — funnel, movement, retargeting, and Priority

- Funnel order is opportunities, MQLs, SQLs, meetings, closed won/lost, and revenue. Closed-by-source keeps referral and other valid sources in the denominator; residuals are `Unknown / Unattributed`.
- Weekly flow uses distinct contact IDs for new leads and distinct opportunity IDs for stage movement. Current stage distribution is a snapshot, not a period-entry count.
- Vertical reporting groups by the GHL contact `Vertical` field (not campaign name/source). For the next weekly report, show reconciled performance by vertical and retain `Unclassified` for missing/unmatched field values. Validate each metric's source, distinctness rule, and selected-window date basis; unsupported or stale metrics remain unavailable.
- Retargeting is queue visibility only: eligible contacts, latest click/audience touch, suppression/reply state, and next action. It does not authorize a send.
- Inbound response speed retains the same-channel SLA contract. It is not MQL-to-first-call.
- Priority is `Sales Outreach` stage `be636da7-3c15-48ab-b589-c75bcd6f9955`; closed opportunities are protected and retries are keyed by contact plus source event.

## Feedback-retention checklist

- The requested funnel sequence is Opportunities → MQL → SQL → Closed, with New contacts outside the funnel denominator. The Band 1 detail must show both the raw MQL→SQL count and its percentage, plus SQL→Closed percentage; closed SQLs and revenue may be empty when there are no closed records.
- Meetings and meeting outcomes are intended to become one rep-level card containing count, showed, no-show, and rescheduled. Until GHL appointment statuses are reliable, showed/no-show must remain unavailable rather than inferred.
- Closed by source must include referral and other valid source values, and its totals must reconcile to closed SQLs/revenue. Unknown/Unattributed is a residual, not silently dropped coverage.
- Weekly movement must show unique/new leads fed in and how they moved through MQL, SQL, and later stages. Intake counts and current-stage distributions must remain separate measures.
- Retargeting must surface newsletter-audience contacts and clickers as a deduplicated, suppression-aware read-only queue. It does not authorize a send.
- Lead-source coverage means attributed MQL/SQL rows divided by the matching MQL/SQL denominator; it is not limited to paid marketing SQLs. Referral counts when present, and incomplete source snapshots must remain visible.
- Speed-to-lead remains same-channel inbound response time, not MQL→first phone call. Internal-note review is read-only; SLA targets, automatic tasks, CRM note creation, and outbound follow-up remain outside the approved scope.
- New contacts must keep LinkedIn backfill separately identifiable so backfill does not inflate the ordinary new-contact count.

| Mockup area | Required values | Likely source |
|---|---|---|
| Outbound total strip | Emails, LinkedIn messages, SMS, voicemails, newsletters | Campaign Channel Summary plus channel ledgers |
| Email campaign table | Sent, delivered, opened, clicked, replied, bounced | Email send/event ledgers and Campaign Channel Summary |
| LinkedIn campaign table | Invites, accepted, messages delivered, opened if available, replied | `linkedin_activity_events` and campaign attribution |
| SMS table | Sent, delivered, replies, failed | SimpleTexting event ledger / campaign summary |
| Voicemail table | Latest custom disposition per unique contact; voicemail drops/left and callback-requested counts | `voice_call_attempt.disposition`, materialized into `lt_exec_v1_call_facts` |
| SDR performance strip/table | Calls attempted, connected, no answer, busy/failed, wrong number; per SDR effort and outputs | GHL native call-report snapshot when captured; otherwise `report_raw_ghl_calls` / V1 call facts |
| Social media strip/table | Posts, impressions, reach, engagement, followers by channel | GHL Social Planner post ledger and account statistics |
| Action queue | MQL response SLA, stale contracts/proposals, overdue follow-ups | GHL opportunity/task/activity timestamps plus agreed SLA rules |

## Known data gaps to surface early

1. Appointment outcomes are not reliable until GHL status is updated after meetings; do not manufacture showed/no-show values.
2. Social reach, impressions, saves, and follower statistics may be unavailable when the GHL OAuth/statistics source is not authenticated.
3. Selecting the voicemail custom disposition is the business rule for “voicemail left”; drops sent and delivered therefore use the same latest-disposition unique-contact count. Callback-requested counts use explicit callback dispositions.
4. Response speed is now collected from durable same-channel event timestamps. A response-time target is still not configured, so the report shows unmatched inbound events rather than inventing an overdue threshold.
5. Email engagement must show coverage and use unique-recipient rates where possible; missing provider events must not be presented as zero engagement.
6. GHL's native per-SDR call widgets use `dateAdded`, `direction=outbound`, and `userId`, with the checked native report in `Asia/Manila`. The captured 2026-09-20..2026-09-26 snapshot is exact for that period only. HighLevel publicly documents `GET /conversations/messages/export` with `channel=Call`, date bounds, and cursor pagination; the current PIT can read it, but its exact-week outbound rows/statuses did not reconcile to native widget totals. The authenticated Call Reporting UI's private calls endpoint did match the exact-week widget counts, but that endpoint returned HTTP 401 with the GHL PIT and is undocumented. Do not build an automated dependency on the private UI endpoint; request supported access or use a supported export. Keep documented-export values incomplete until reconciled.

## Acceptance checks before V1 review

- API response is non-empty JSON and all required source-health rows are ready or visibly flagged.
- Headline numbers reconcile to the corresponding breakdowns.
- MQL/SQL/contacts/opportunities use documented distinctness and period rules.
- Meeting totals reconcile to the appointment table and SDR rows.
- Channel totals reconcile to the campaign tables, with unattributed activity shown separately.
- No unavailable source is rendered as a trustworthy zero.
- Desktop and approximately 390px mobile layouts have no horizontal overflow.
- The existing Executive Report remains unchanged and still renders from its original path.
