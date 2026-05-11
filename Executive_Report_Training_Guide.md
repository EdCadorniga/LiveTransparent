# LiveTransparent Executive Report
## Training Document and Quick Reference Guide
Updated: May 12, 2026

This guide explains what each visible card in the Executive Report means, how to present it, and where the common interpretation risks are. It matches the live dashboard glossary, the users-based funnel cards, and the trailing-day range presets.

# Part I: Report Sections -- Quick Explanations
Use this section when reviewing the report with someone who needs the fastest possible explanation.

- KPI Row: The six cards at the top summarize the selected date window: Recorded Visits, Contacts, Opportunities, Meetings, Closed Won, and Revenue. Recorded visits are the visits GA4 captured in the selected window. Contacts is CRM volume. It is normal for these to differ because a contact is not always created by a form.
- Traffic and Channels: This panel shows where website traffic came from and how much volume each channel produced. Channel Breakdown is a GA4 traffic summary, not a contact summary. Channel Detail connects traffic to contact generation when the data exists.
- Meta Ads: This panel is attribution-first. It shows Meta-tagged visits and downstream contacts, opportunities, and booked meetings. It does not depend on spend to be useful. Treat it as a performance and attribution view, not a ROAS view.
- Acquisition Sources: This is the contact-level source view. It shows where contacts originated from the CRM bridge and source fields. If someone asks where the acquisition source view is, this is the section to open.
- Funnel and Attribution: This panel now uses Users as the primary denominator for the conversion cards. User -> Form and User -> Contact are the main funnel rates. The attribution coverage card next to it is a separate diagnostic panel that tells you whether contacts can be matched back to traffic and sales.
- Capture Gaps: This is an absolute-volume panel. It shows Recorded Visits, Forms, Contacts, Opportunities, Meetings, and Closed Won side by side. Do not read it as a perfectly linear funnel because contacts can arrive from routing, manual CRM entry, imports, and follow-up as well as forms.
- Sales and Pipeline: This section provides the company-wide pipeline summary and active-opportunity view. It covers open deals, worked deals, stage movement, velocity, and sales quality. Use it when discussing pipeline health, not acquisition quality.
- UTM / Campaign Breakdown: This panel shows observed traffic rows by source, medium, campaign, content, term, and landing page. It is not a master list of every UTM ever created in GHL. A campaign will only appear here once the traffic or bridge data actually sees it.
- Sales Detail / John's Deals: These cards use the same opportunity payload as the team summary. The difference is presentation: one is a team-wide view and the other is a deal-centred view. If a stakeholder asks what the difference is, the safe answer is that the source data is the same.
- Social and Site: The Social Posts card shows the status of GHL Social Planner posts. Failed means the latest status is failed or error. The Site Traffic card shows GA4 traffic and engagement for the selected window.
- Source Health: This panel tells you whether the integrations are healthy, stale, blocked, or failed. Use it whenever you need to explain why a metric is zero or missing.

# Part 2: Part 2: Technical Deep Dive
This section explains how the report is assembled, what the live API returns, and how to read the payload without inventing new assumptions.

- Architecture: the dashboard is a static HTML and JavaScript SPA at reports.livetransparent.com. It calls a single n8n webhook at `/api/report/executive/summary` and renders the response client-side.
- Request contract: the report reads `view`, `range`, `from`, `to`, `embed`, and `locationId` query parameters. The current preset ranges are trailing complete days ending yesterday.
- Response shape: the API returns `summary`, `channelBreakdown`, `utmBreakdown`, `metaAttribution`, `contactSources`, `pipelineDropoff`, `stageDropoff`, `stageVelocity`, `appointments`, and `health`.
- Response shape: the API also returns the active-opportunity fields used by the report, including `activeOpportunityCount`, `workedOpportunityCount`, `stageMoverCount`, and `opportunityStageBreakdown`.
- Funnel basis: the primary funnel rates now use Users as the denominator where possible. This means the dashboard is treating unique visitors as the main traffic audience, not raw GA4 session counts.
- Source status: GSC Daily Ingest is now live and verified in n8n. Older notes that describe Search Console as blocked are stale and should be treated as historical.
- Attribution logic: Acquisition Sources, UTM / Campaign Breakdown, and Attribution Coverage all depend on observed traffic and bridge data. They should be read as live data quality and attribution outputs, not as a perfect campaign registry.
- Operational rule: when a metric looks wrong, check Source Health first. The report separates stale data from business performance so the reader does not draw the wrong conclusion.

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
| Meetings | Booked appointments or discovery calls in the selected window. | These are GHL appointments when available. |
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
| Channel Breakdown | GA4 traffic volume by channel. | This is traffic reporting, not lead reporting. |
| UTM / Campaign Breakdown | Observed traffic rows by UTM fields. | This is not a registry of every UTM ever created in GHL. |
| Social Posts Failed | Posts whose latest status is failed or error in the selected window. | This is status-based, not a hidden count of all broken posts. |
| Sales Team Summary | The company-wide opportunity summary. | Use this for the broad sales picture. |
| John's Deals | The same opportunity payload shown as a deal-centred view. | Use this when the conversation is about individual deal movement. |
| 7d / 30d / 90d | Trailing complete-day presets ending yesterday. | Example: if you click 7d on Tuesday, you see the previous Tuesday through Monday. |

# Part 3: How to Present the Report

- Do not assume contacts are created by forms. That is the most common interpretation mistake in this report.
- Do not assume the GA4 term `sessions` is the same phrase everyone uses for website visits. In this report, we call that metric `Recorded Visits` to make the label explicit.
- Do not treat the UTM breakdown as a master campaign catalog. It only shows what the data actually observed.
- If someone asks about Acquisition Sources, point them to the dedicated section rather than the channel breakdown.
- If someone asks about Sales Team vs Johns Deals, explain that the payload is the same and the difference is the lens.
- If someone asks why a social post is marked Failed, define it as a status value from the ingest, not a subjective judgment.
- If someone asks what the date range means, say it is trailing complete days ending yesterday, not a click-day-dependent calendar block.
- If someone asks what counts as an active opportunity, say the report now separates open opportunities from worked opportunities and stage movers. Active means open in the latest snapshot; worked means updated or moved stage in the window.

# Part 4: Naming Standards for Measured Variables
Naming standards matter because the report can only group what is named consistently. This section should be read as part of the measurement contract, not as optional marketing style guidance.

- Use one naming pattern across campaigns, ad sets, ads, UTMs, and landing pages so the report can group traffic without manual cleanup.
- For campaigns, use a stable pattern such as `{brand}-{channel}-{objective}-{audience}-{geo}-{date}`.
- For ad sets, use `{brand}-{campaign}-{audience}-{geo}-{date}` so the ad set always inherits the campaign context.
- For ads, use `{brand}-{campaign}-{adset}-{creative}-{format}-{date}` so the creative, placement format, and launch date are readable without opening the platform.
- For UTMs, keep source, medium, campaign, content, and term consistent with the paid naming system. Do not let ad names and UTM values drift apart.
- For landing pages, use a slug that reflects the offer or funnel step, then keep the UTM fields as the variable layer instead of encoding everything into the URL path.
- For measured variables, prefer a short controlled vocabulary for audience, geo, objective, and creative format. Avoid free-form phrasing that will fragment reporting.
- If a naming field is used in reporting, treat it as a data contract. Changing it should be a conscious decision, not an individual preference.

# Part 5: Improvement Suggestions
These are the most useful next improvements if the report needs to become easier to review or harder to misread.

| Priority | Suggestion | Why it helps |
|---|---|---|
| High | Move the range definition into the summary API response. | That makes the trailing-day rule a source-of-truth value instead of just UI copy. |
| High | Emit user-based conversion rates server-side. | The dashboard currently computes them from summary fields; moving them into the API removes ambiguity and keeps the docs aligned with the payload. |
| High | Return a metric glossary object from the API. | This lets the UI and the training guide use the same definitions without drift. |
| High | Define active-opportunity criteria server-side and expose touched/stage-moved counts. | This removes ambiguity about whether the report is counting open deals, worked deals, or only new deal creation. |
| High | Standardize naming for ads, ad sets, campaigns, and other measured variables. | Use consistent, machine-readable patterns so reporting can group traffic correctly. For example: campaigns = {brand}-{channel}-{objective}-{audience}-{geo}-{date}; ad sets = {brand}-{campaign}-{audience}-{geo}-{date}; ads = {brand}-{campaign}-{adset}-{creative}-{format}-{date}. Apply the same discipline to UTM source, medium, campaign, content, and landing page slugs. |
| Medium | Add a true owner-scoped sales filter if Johns Deals is meant to be owner-specific. | Right now the report presents the same opportunity payload in two lenses; a real owner filter would make the distinction explicit. |
| Medium | Add a campaign registry or created-UTM catalog. | This would answer the common question of why a GHL-created UTM does not appear in observed traffic. |
| Medium | Add a note-level activity join if "worked" must include touches that do not change stage. | Notes-only activity can be missed if the underlying opportunity row is not updated in a way the report can see. |
| Medium | Add Search Console surfacing once organic search should be reviewed in the executive view. | GSC is live in the data layer now, so the reporting surface can expose clicks, impressions, and query data when the team is ready. |
| Medium | Add a social failure drilldown by post ID and error message. | That would make the Failed count actionable instead of only descriptive. |
| Medium | Expose range metadata in the header. | Show the exact from/to dates so reviewers do not infer a calendar week incorrectly. |
| Low | Add a short onboarding note about contact capture paths. | This would explain why forms, routing, manual entry, imports, and follow-up can all create contacts. |

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
