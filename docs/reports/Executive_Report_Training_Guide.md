# LiveTransparent Executive Report
## Training Document and Quick Reference Guide
Updated: August 6, 2026

This guide explains what each visible card in the Executive Report means, how to present it, and where the common interpretation risks are. It matches the live dashboard glossary, the users-based funnel cards, and the trailing-day range presets.

# Part I: Report Sections -- Quick Explanations
Use this section when reviewing the report with someone who needs the fastest possible explanation.

- KPI Row: The six cards at the top summarize the selected date window: Recorded Visits, Contacts, Opportunities, Meetings, Closed Won, and Revenue. Recorded visits are the visits GA4 captured in the selected window. Contacts is CRM volume. It is normal for these to differ because a contact is not always created by a form.
- Traffic and Channels: This panel shows where website traffic came from and how much volume each channel produced. Channel Breakdown is a GA4 traffic summary, not a contact summary. Channel Detail connects traffic to contact generation when the data exists.
- Meta Ads: This panel is attribution-first. It shows Meta-tagged visits and downstream contacts, opportunities, and booked meetings. It does not depend on spend to be useful. Treat it as a performance and attribution view, not a ROAS view.
- Acquisition Sources: This is the contact-level source view. It shows where contacts originated from the CRM bridge and source fields. If someone asks where the acquisition source view is, this is the section to open.
- Top Pages: This is a short website page summary based on the landing-page rollup we already capture. It shows the pages that received the most recorded visits, plus form and opportunity activity when available.
- Funnel and Attribution: This panel now uses Users as the primary denominator for the conversion cards. User -> Form and User -> Contact are the main funnel rates. The attribution coverage card next to it is a separate diagnostic panel that tells you whether contacts can be matched back to traffic and sales.
- Capture Gaps: This is an absolute-volume panel. It shows Recorded Visits, Forms, Contacts, Opportunities, Meetings, and Closed Won side by side. Do not read it as a perfectly linear funnel because contacts can arrive from routing, manual CRM entry, imports, and follow-up as well as forms.
- Sales and Pipeline: This section provides the company-wide pipeline summary and active-opportunity view. It covers open deals, worked deals, stage movement, velocity, and sales quality. Use it when discussing pipeline health, not acquisition quality.
- UTM / Campaign Breakdown: This panel shows observed traffic rows by source, medium, campaign, content, term, and landing page. It is not a master list of every UTM ever created in GHL. A campaign will only appear here once the traffic or bridge data actually sees it.
- Campaign Channels: This table is the cross-channel campaign view. It shows named channel/campaign rows for DAN, Emerald, Partnership, SMS, LinkedIn, and Vapi, with channel-specific sends, engagement, replies, DMs, calls, qualification, and booked metrics where the source data exists. Use the All, Email, LinkedIn, SMS, and VAPI filters to focus on one channel.
- Outgoing Call Detail: This bottom-of-report table shows Vapi outbound call attempts for the seven most recent completed days. It is separate from the aggregate GHL Calls panel and includes contact ID/name fallback, phone, disposition, duration, first-attempt status, campaign, and on-demand recording playback. Use the sidebar Outgoing Calls bookmark to jump to it.
- Sales Detail / SDR Owner View: These cards use the same opportunity payload as the team summary. The owner view should be driven by canonical GHL user ID, not a hardcoded rep name.
- Social and Site: The Social Posts card shows the status of GHL Social Planner posts. Failed means the latest status is failed or error. The Site Traffic card shows GA4 traffic and engagement for the selected window.
- Source Health: This panel tells you whether the integrations are healthy, stale, blocked, or failed. Use it whenever you need to explain why a metric is zero or missing.

# Part 2: Part 2: Technical Deep Dive
This section explains how the report is assembled, what the live API returns, and how to read the payload without inventing new assumptions.

- Architecture: the dashboard is a static HTML and JavaScript SPA at reports.livetransparent.com. It calls the n8n executive summary proxy at `/api/report/executive/summary`, the outgoing-call proxy at `/api/report/executive/outgoing-calls`, and a separate campaign summary webhook at `/webhook/lt-report-campaign-channel-summary`; all render client-side. The public host serves build `2026-08-01-v12-campaign-breakdown` with the current campaign table, channel filters, and outgoing-call detail section.
- Request contract: the report reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query parameters. The current preset ranges are trailing complete days ending yesterday.
- Response shape: the API returns `summary`, `channelBreakdown`, `utmBreakdown`, `metaAttribution`, `contactSources`, `topPages`, `pipelineDropoff`, `stageDropoff`, `stageVelocity`, `appointments`, `health`, `linkedinFunnel`, `vapiCampaignBreakdown`, `vapiQueueDistribution`, `mqlSummary`, `sqlContacts`, `poolDistribution`, `emailsSent`, `emailsOpened`, `emailsClicked`, `emailsBounced`, `emailsUnsubscribed`, `emailsComplained`, `emailOpenRate`, `emailClickRate`, and `emailBounceRate`.
- Response shape: the API also returns the active-opportunity fields used by the report, including `activeOpportunityCount`, `workedOpportunityCount`, `stageMoverCount`, and `opportunityStageBreakdown`.
- Campaign response shape: the campaign summary returns `window` and `campaignChannelBreakdown` rows containing `channel`, `campaign`, SMS metrics, email metrics and rates, LinkedIn DM/reply metrics, and Vapi outcome metrics. DAN attribution uses release logs; Emerald uses bucket/enrollment data; Partnership uses `partnership_release_log`; SMS uses `campaign_key`; LinkedIn uses activity events joined to Brand/Dispensary source pools plus a zero-safe `Partnership LinkedIn` catalog row; and Vapi uses queue campaign IDs. Dynamic source campaigns remain visible as additional rows.
- Outgoing-call response shape: `/api/report/executive/outgoing-calls` returns `{ calls, total, limit, offset, range }`. Each call includes `call_id`, `contact_id`, `contact_name`, `contact_phone`, `number_name`, `started_at`, `ended_at`, `call_status`, `disposition`, `duration_seconds`, `recording_url`, `first_time`, and `marketing_campaign`. The n8n source is `LT - Report Outgoing Calls Detail` (`VXFHc8IrF9DDEEdj`), which queries `voice_call_attempt` joined to `voice_call_queue` and latest contact snapshots.
- Funnel basis: the primary funnel rates now use Users as the denominator where possible. This means the dashboard is treating unique visitors as the main traffic audience, not raw GA4 session counts.
- Source status: GSC Daily Ingest is active but currently blocked because its Google OAuth credential requires reconnection. Treat Search Console metrics as unavailable until a successful ingest execution is verified.
- Attribution logic: Acquisition Sources, UTM / Campaign Breakdown, and Attribution Coverage all depend on observed traffic and bridge data. They should be read as live data quality and attribution outputs, not as a perfect campaign registry.
- Operational rule: when a metric looks wrong, check Source Health first. The report separates stale data from business performance so the reader does not draw the wrong conclusion.
- Vapi campaign-gating note: the Executive Report currently shows downstream Vapi campaign outcomes and queue distribution, but not the upstream classifier's AI/domain acceptance counts. For classifier operations, use `LT - Campaign Contact Classifier` (`IduCoT5YOs0g2faT`) execution summaries and the Postgres table `vapi_qualified_domains`.

## Metric Definitions
Use these definitions when presenting the dashboard. If a visible metric is not defined here, it should be treated as incomplete until the definition is added.

| Metric | Definition | Presenter note |
|---|---|---|
| Recorded Visits | GA4 recorded visits in the selected window. | Traffic volume only. One person can generate multiple recorded visits. |
| Users | Unique visitors in the selected window. | This is the primary denominator for the funnel cards. |
| Contacts | New CRM contacts created in the selected window. | Contacts are not 1:1 with forms. |
| Forms | Tracked form submissions in the selected window. | This is the submission count, not total contacts. |
| Opportunities | New deals or sales opportunities created in the selected window. | Use this as pipeline creation, not acquisition volume. |
| Active Opportunities | Open opportunities in the latest snapshot. | This is the current open-deal count, not the number of new deals created in the window. |
| Worked Opportunities | Open opportunities updated or moved stage during the selected window. | This is the best current proxy for deals that were actively worked. |
| Stage Movers | Open opportunities that changed stage at least once during the selected window. | Use this to see which deals progressed, even if no new deal was created. |
| LinkedIn Funnel | Connection state distribution: ready, requested, connected, DM active, completed. | Tracks LinkedIn outreach pipeline health. |
| Vapi Campaigns | Voice AI call outcomes by campaign. | Shows answered rate, qualified calls, and booked meetings per campaign. |
| Vapi Queue | Pending outbound calls grouped by campaign. | Shows how many contacts are queued for each Vapi campaign. |
| Vapi Campaign Eligibility | Upstream Brand/Dispensary campaign-gating workflow. | Not currently returned as a dashboard metric; inspect n8n classifier executions and `vapi_qualified_domains` for selection, acceptance, writes, and domain-match activity. |
| MQL Summary | Active and total opportunities in the Warm pipeline Qualified (MQL) stage. | Tracks marketing-qualified lead volume. |
| AI Qualification | Janvi assessment outcomes for cannabis-business verification. | Distinguishes qualified, pending/unverified, and rejected contacts. Do not confuse this with the separate DeepSeek Vapi campaign-eligibility gate. |
| Sales Outreach Queue | Contacts/opportunities promoted after explicit AI cannabis qualification. | Measures SDR work-queue volume and owner assignment source. |
| SQL Contacts | Contacts with the SQL (Sales Qualified Lead) tag. | Counts contacts promoted to sales-qualified status. |
| Pool Distribution | Contact counts by pool tag (brands, dispensaries, Vapi campaigns). | Shows audience segment sizes. |
| Email Campaigns | Sent, opened, clicked, bounced, unsubscribed, and spam complaint counts. | Tracks email campaign performance across all senders. |
| Campaign Channels | Named campaign rows across email, LinkedIn, SMS, and Vapi. | Use this for cross-channel campaign comparisons; zero or null values can indicate missing source events rather than no business activity. |
| Email Rates | Open rate, click rate, and bounce rate. | Computed from email event metrics. |
| Meetings | Booked appointments or discovery calls in the selected window. | These are GHL appointments when available. |
| Calls | GHL conversation call logs and status breakdown. | Use this for answered, missed, voicemail, inbound, and outbound call activity. |
| Outgoing Call Detail | Vapi outbound call attempts from `voice_call_attempt` for the seven most recent completed days. | Use this for row-level disposition, timing, campaign, first-attempt, and recording review; it is not the aggregate GHL Calls panel. |
| Call Duration | Rounded seconds from `ended_at - started_at`; missing end time uses `started_at`. | A zero value can represent a call attempt with no elapsed provider duration, not necessarily a successful conversation. |
| First Time | True only when no earlier `voice_call_attempt` exists for the contact. | This is a database-history flag, not a selected-window-only flag. |
| Closed Won | Deals marked as won. | Use this for outcome reporting, not top-of-funnel conversion. |
| Revenue | Total dollar value of closed-won deals. | This is reported revenue, not spend or profit. |
| User -> Form | Unique users divided by form submissions in the selected window. | Primary traffic-to-lead capture rate. |
| User -> Contact | Unique users divided by CRM contacts created in the selected window. | Primary traffic-to-contact conversion rate. |
| Contact -> Opportunity | Contacts that became opportunities in the selected window. | Contact-safe and not inflated by multiple opportunities per contact. |
| Opportunity -> Meeting | Opportunities that resulted in a booked meeting. | Use this to understand sales handoff quality. |
| Meeting -> Won | Meetings that closed as won. | Use this as a late-stage close measure. |
| Attribution Coverage | A diagnostic view of whether contacts have usable source fields, bridge matches, and sale matches. | This measures data completeness, not business performance. |
| Contacts Created in Window | New contacts created in the selected window. | This is the denominator for attribution coverage. |
| Source Coverage | Contacts with usable source fields. | This tells you whether attribution can be read from the CRM record. |
| Bridge Matched | Contacts linked to a GA4 session. | This tells you whether traffic can be tied back to the CRM contact. |
| Sale Matched | Contacts linked to an opportunity. | This tells you whether the contact carries through to sales. |
| Acquisition Sources | The visible contact-level source / medium / campaign section. | Use this when someone wants to know where contacts came from. |
| Top Pages | The short website page summary based on the landing-page rollup. | Use this when someone wants to know which pages are getting the most recorded visits. |
| Channel Breakdown | GA4 traffic volume by channel. | This is traffic reporting, not lead reporting. |
| UTM / Campaign Breakdown | Observed traffic rows by UTM fields. | This is not a registry of every UTM ever created in GHL. |
| Social Posts Failed | Posts whose latest status is failed or error in the selected window. | This is status-based, not a hidden count of all broken posts. |
| Sales Team Summary | The company-wide opportunity summary. | Use this for the broad sales picture. |
| SDR Owner View | The same opportunity payload shown as a deal-centred view. | Use this when the conversation is about individual owner or deal movement. |
| 7d / 30d / 90d | Trailing complete-day presets ending yesterday. | Example: if you click 7d on Tuesday, you see the previous Tuesday through Monday. |

# Part 3: How to Present the Report

- Contacts are not always created by forms. Routing, manual CRM entry, imports, and follow-up can also create contacts, which is why the contact count does not always line up with form submissions.
- The GA4 term `sessions` is not the same phrase everyone uses for website visits, so this report labels the metric `Recorded Visits` to make the meaning clear.
- The UTM breakdown is a view of what the data actually observed, not a master campaign catalog of everything ever created in GHL.
- Acquisition Sources is the contact-level section. It is the right place to go when the question is where contacts came from.
- Sales Team and SDR Owner View use the same opportunity payload. The difference is only the lens: one is the team view and the other is the deal-centred view.
- Calls and Conversations show GHL call records grouped by status. That is the place to explain call activity without mixing it up with SMS or appointments.
- A social post marked Failed means the latest recorded status is failed or error. It is a status value from the ingest, not a subjective review of the post.
- The date range is a trailing complete-day window ending yesterday. That means the selected range always points to finished days, not a click-day-dependent calendar block.
- Active opportunities are the open deals in the latest snapshot. Worked opportunities are the open deals that were updated or moved stage inside the selected window, and stage movers are the ones that actually changed stage.

# Part 4: Naming Standards for Measured Variables
Naming standards matter because the report can only group what is named consistently. This section should be read as part of the measurement contract, not as optional marketing style guidance.

The UTM fields themselves are standard. The exact naming pattern we use for campaigns, ad sets, ads, and landing pages is our internal house standard so the data stays readable and groupable.

That means the tracking fields are not the problem. The important part is making sure every ad link, landing page, and contact intake path writes into those fields the same way every time.

- Use one naming pattern across campaigns, ad sets, ads, UTMs, and landing pages so the report can group traffic without manual cleanup.
- For campaigns, use a stable pattern such as `{brand}-{channel}-{objective}-{audience}-{geo}-{date}`.
- For ad sets, use `{brand}-{campaign}-{audience}-{geo}-{date}` so the ad set always inherits the campaign context.
- For ads, use `{brand}-{campaign}-{adset}-{creative}-{format}-{date}` so the creative, placement format, and launch date are readable without opening the platform.
- For UTMs, keep source, medium, campaign, content, and term consistent with the paid naming system. Do not let ad names and UTM values drift apart.
- For landing pages, use a slug that reflects the offer or funnel step, then keep the UTM fields as the variable layer instead of encoding everything into the URL path.
- For measured variables, prefer a short controlled vocabulary for audience, geo, objective, and creative format. Avoid free-form phrasing that will fragment reporting.
- If a naming field is used in reporting, treat it as a data contract. Changing it should be a conscious decision, not an individual preference.

# Part 5: Improvement Suggestions
These are split into two groups:

- `Safe now` means we can add it to the report or guide without deleting or rewriting the current records.
- `Needs more setup` means it still should not destroy data, but it may need extra coordination or a small amount of historical cleanup.

None of the `Safe now` items require us to erase or rewrite existing records. They either change the wording, add a clearer explanation, or show information we already have.

## Safe now

The report already has UTM capture fields in GHL. The practical improvement is to make sure every ad, page, and contact path writes into those fields the same way every time.

| Suggestion | Why we need it | Data impact |
|---|---|---|
| Show the exact date window at the top of the report. | People should not have to guess whether a range means a calendar week or a trailing window. | No historical data changes. |
| Keep the metric definitions inside the report and the guide. | Everyone should read the same meaning for each card, not a different guess. | No historical data changes. |
| Show a short summary of the most visited pages. | Leadership can quickly see which pages are drawing the most attention without opening a separate analytics tool. | Uses the landing-page rollup we already have. |
| Show user-based conversion rates directly in the report. | This makes the funnel easier to understand because the rate is shown instead of calculated in someone's head. | Uses the numbers already collected. |
| Define active deals, worked deals, and stage movers in plain language. | This removes confusion about whether the report is counting new deals, open deals, or deals that were actually touched. | Uses current opportunity records. |
| Add a simple drilldown for failed social posts. | Management can see which posts failed and why instead of only seeing a total. | No historical data changes. |
| Show search performance in the report when the team wants to review organic search. | It gives leadership one place to see search demand, clicks, and impressions. | No historical data changes. |
| Show a short summary of the most visited pages. | Leadership can quickly see which pages are drawing the most attention without opening a separate analytics tool. | Uses the landing-page rollup we already have. |
| Add an owner filter if `SDR Owner View` is meant to show one rep's pipeline only. | Use the stable GHL user ID and preserve an explicit conflict/unassigned state. | No historical data changes. |
| Standardize names for campaigns, ad sets, ads, UTMs, and landing pages going forward. | Clean names make the report group results correctly and reduce manual cleanup. The existing `UTM Source First/Last`, `UTM Medium First/Last`, `UTM Campaign First/Last`, `UTM Content First/Last`, `UTM Term First/Last`, and landing page fields are already there to hold this data. The pattern itself is our house standard, built on common UTM fields. | Past records stay as-is; future records improve. |
| Keep a master list of the campaigns and UTMs we intentionally launched. | This helps the team tell the difference between something we launched on purpose and something the report never saw, and it makes it easier to check whether the existing UTM fields were filled correctly. | No historical data changes. |
| Add a note about how contacts can be created. | It explains why contacts may come from forms, routing, manual entry, imports, or follow-up. | No historical data changes. |

## Needs More Setup

| Suggestion | Why we need it | Data impact |
|---|---|---|
| Count a deal as worked when notes or updates are added, even if the stage does not change. | Right now, some active work may not show up unless the deal itself changed stage or was updated in a way the report can see. | Still additive, but it needs a clearer rule for what counts as work. |
| Add a cleaner match between contacts and sales when the contact record is incomplete. | This helps reduce the `Unknown` bucket and makes attribution easier to trust. | Still additive, but it may need extra matching rules. |
| Keep the report and the guide using the same definitions. | That prevents the dashboard and the training guide from drifting apart over time. | No historical data changes, but it needs a small maintenance process. |

# Part 6: Current Guardrails

- Treat the glossary in the dashboard as the immediate source of truth for visible cards.
- Use Users-based funnel rates for primary interpretation, and use Recorded Visits only as traffic context.
- Use the attribution coverage card to diagnose data quality separately from business performance.
- Use Source Health whenever a metric unexpectedly drops to zero or looks stale.

# Appendix A: Naming Templates
These examples are intentionally simple and machine-readable. The main goal is to keep campaign, ad set, ad, and UTM values aligned so reporting can aggregate them without manual cleanup.

| Layer | Example pattern | Example |
|---|---|---|
| Meta campaign | `{brand}-{channel}-{objective}-{audience}-{geo}-{date}` | `lt-meta-leads-intake-broad-us-2026-05` |
| Meta ad set | `{brand}-{campaign}-{audience}-{geo}-{date}` | `lt-meta-intake-broad-us-2026-05` |
| Meta ad | `{brand}-{campaign}-{adset}-{creative}-{format}-{date}` | `lt-meta-intake-broad-carousel-01-2026-05` |
| Google Ads campaign | `{brand}-{channel}-{objective}-{geo}-{date}` | `lt-google-search-book-demo-us-2026-05` |
| Google Ads ad group | `{brand}-{campaign}-{keyword-theme}-{geo}-{date}` | `lt-google-search-book-demo-high-intent-us-2026-05` |
| Google Ads ad | `{brand}-{campaign}-{adgroup}-{creative}-{format}-{date}` | `lt-google-search-book-demo-rsa-01-2026-05` |
| UTM source / medium / campaign | `utm_source=...&utm_medium=...&utm_campaign=...` | `utm_source=facebook&utm_medium=paid_social&utm_campaign=lt-meta-leads-intake-broad-us-2026-05` |
| UTM content | `{creative or placement identifier}` | `carousel-01` |
| Landing page slug | `/{offer-or-step}` | `/book-demo` |
