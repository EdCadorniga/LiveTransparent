# Sales and Marketing Roadmap

## KPI Framework

### Lead Generation
- Qualified outbound leads per week
- Open / response rates in sequences
- Appointment show rate

### Next Week Report Plan
- Add sequence-event ingest so we can show real sequence performance instead of only enrollments.
- Tighten landing-page and form tracking so we can trust the matched funnel by landing page.
- [x] Show a short summary of the most visited pages on the website using the landing-page rollup we already have.

### Conversion
- Lead → MQL → SQL conversion rate
- SQL → Proposal → Close rate
- Pipeline velocity (days between stages)
- Stage-by-stage opportunity movement (moved-in / moved-out per stage)
- Opportunity cycle length (days from first stage to close)

### Operational Efficiency
- % of outbound automated vs manual
- Lead scoring accuracy (hit rate among top scores)
- Sales cycle length changes

### Revenue Impact
- Pipeline contribution per month
- ROI of tools + sequences

---

## Current State

| System | Status |
|--------|--------|
| GoHighLevel (GHL) | Production — CRM, pipeline, routing, reporting |
| Apollo.io | Production — enrichment, outbound sequences |
| Meta Ads API | Validated — attribution-first reporting live |
| GA4 | Live — sessions, channels, engagement |
| GSC | Live — Search Console clicks, impressions, CTR, position |
| Clay | Planned — Phase 2 |
| n8n Orchestration | Production — all report workflows active |

---

## Executive Report Data Sources

The executive report (`reports/embed/executive/index.html`) surfaces data from:

| Source | Workflow | Data |
|--------|----------|------|
| GHL Contacts | `LT - GHL Daily Leads Ingest` | Contacts, UTM fields, warm source, routing metadata |
| GHL Opportunities | `LT - GHL Daily Sales Ingest` | Pipeline stages, closed-won revenue |
| GHL Calls | `LT - GHL Daily Calls Ingest` | Voice call logs: status, direction, duration |
| GHL Appointments | `LT - GHL Daily Appointments Ingest` | Calendar events: booked, showed, no-show |
| GA4 Sessions | `LT - GA4 Daily Ingest` | Sessions, users, engagement by channel/landing page |
| GSC Search | `LT - GSC Daily Ingest` | Clicks, impressions, CTR, average position, queries, pages |
| Attribution Bridge | `LT - Report Attribution Bridge` | Traffic → contact matching |
| Daily Rollups | `LT - Report Daily Rollups` | Aggregated summary, channel, UTM, landing page tables |
| Executive API | `LT - Report Executive Summary API` | JSON served to embed via n8n webhook |
| Email Events | `LT - Email Event Ingest` | Opens, clicks, bounces, unsubscribes, spam complaints |
| LinkedIn State | `linkedin_connection_state` | Connection funnel: ready → requested → connected → DM → completed |
| Vapi Voice | `voice_call_attempt` + `voice_call_queue` | Call outcomes by campaign, pending queue distribution |
| MQL/SQL | `report_raw_ghl_opportunities` + `report_raw_ghl_contacts` | MQL (Warm pipeline Qualified stage), AI-qualified cannabis promotion to Sales Outreach, SQL (tagged contacts) |
| AI Qualification / SDR Routing | Janvi assessment + GHL owner fields | Qualified cannabis -> Sales Outreach; owner alignment or Jason/Marc 50/50 fallback; pending/unverified -> Vapi Warm |

### GHL Custom Fields Captured for Reporting
- `UTM Source First/Last`, `UTM Medium First/Last`, `UTM Campaign First/Last`, `UTM Content First/Last`, `UTM Term First/Last`, `UTM Landing Page First/Last`
- `Warm Source`, `Warm Trigger Type`, `Lead Temperature`
- `LT Last Routing Channel`, `LT Last Routing Reason`, `LT Last Routed At`
- `LT Route Lock Until`, `LT Routing Priority`, `LT Last Event Fingerprint`, `LT Last Event At`

---

## Active Pipelines

| Pipeline | Stages |
|----------|--------|
| Warm | New → Qualified (MQL) → Routed to Outreach → Nurture Active → Disqualified |
| Sales Outreach | New → Attempting Contact → 2nd attempt → 3rd attempt → Engaged → Meeting Requested → Booked → Unresponsive |
| Sales | Discovery Scheduled → Discovery Completed → Proposal Sent → Negotiation → Closed Won / Closed Lost |

### Qualification and Work Queue Boundary
- Warm is the unassigned intake and AI-verification layer.
- Only Janvi's explicit `qualified cannabis business` result promotes a contact/opportunity into `Sales Outreach -> New`.
- SDRs work in Sales Outreach; they do not receive ordinary Warm assignments.
- Vapi calls AI-pending/unverified Warm contacts and excludes AI-qualified or explicitly rejected/non-cannabis contacts.
- A Vapi warm transfer is manually claimed by the answering SDR and then promoted into Sales Outreach.
- Cameron's Regulated Ads calendar is used for bookings and does not determine SDR assignment.

---

## Phase 1 — Live (Now → +90 days)

### Stack
- **GHL** — CRM, pipeline, routing, warm lead management
- **Apollo.io** — Enrichment, outbound sequences, SDR motion
- **Meta Ads** — Attribution-first reporting via GA4 UTM + GHL bridge
- **n8n** — All ingestion, bridge, rollup, and alerting orchestration

### Why GHL + Apollo
- Faster hiring (reps can operate in one tool)
- Faster pipeline (built-in routing eliminates manual handoffs)
- Lower cognitive load (scoring + routing automated)
- Gets reps + ops aligned quickly

### What to Test
- Messaging variants per vertical
- Offer framing by company size / industry
- Channel routing (which warm sources convert best)

### Key Constraints
- Enforce quality filters: titles, industries, revenue bands
- Don't let Apollo become spammy — enforce cadence limits
- Use GHL scoring + routing immediately — don't manual-tag

---

## Phase 2 — Planned (Once outbound proves ROI)

### Add Clay — precision layer on top of Apollo

Clay handles:
- Enterprise / strategic accounts
- Founder-led brands
- Platforms, MSOs, aggregators
- High-intent, high-context outreach

Apollo continues doing:
- Broad outbound
- SDR motion
- Volume coverage

### Clay Use Cases
- "Top 500 cannabis brands" — targeted account list
- "Brands spending on Meta but blocked" — retargeting pool
- "Recently funded alternative wellness brands" — funded signal

---

## Deferred / Blocked

| Item | Status | Notes |
|------|--------|-------|
| GSC Daily Ingest | Active | Search Console access granted; workflow healthy |
| Meta Ads raw spend ingest | Deferred | Attribution-first path live; spend reporting deferred |
| Clay integration | Planned Phase 2 | Not started |
| Matched funnel by landing page | Planned | Needs tighter landing-page and form tracking first |
| Sequence event performance | Planned next week | Need open, reply, click, bounce, and unsubscribe events from Apollo sequences |
| GHL → LinkedIn automation | Planned | LinkedIn connect dispatcher active; full workflow deferred |
| GHL Calls & Appointments Ingest | Active | Appointments ingest live (`yWZVSqEcjTbMT3kG`, calendar `SrtXcFVyea7pFl3nTiIK`); Calls ingest live from GHL Conversations |
| Pipeline stage velocity (days per stage) | Active | `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`) calculates this by combining pipeline history events with the previous stage record for each opportunity |

---

## Report Data Contract

Minimum v1 output from the executive report:
- [x] GA4 sessions by channel
- [x] GA4 landing pages
- [x] GHL contacts created
- [x] GHL opportunities created
- [x] GHL closed-won revenue
- [x] Funnel efficiency rates (session→contact, contact→opp, opp→meeting, meeting→won)
- [x] Attribution coverage rates (source fields, bridge match, sale match)
- [x] Meta attribution panel (GA4 UTM + GHL bridge)
- [x] Pipeline stage velocity (avg days per stage, per-opp timeline)
- [x] Sales Detail panel (win rate, deals by stage, pipeline value)
- [x] GSC clicks and impressions
- [x] Email campaign metrics (sent, opened, clicked, bounced, unsubscribed, complained) — added 2026-07-21
- [x] Email engagement rates (open rate, click rate, bounce rate) — added 2026-07-21
- [x] LinkedIn outreach funnel (ready → requested → connected → DM active → completed) — added 2026-07-21
- [x] Vapi voice campaign breakdown (calls by campaign, answered, qualified, booked) — added 2026-07-21
- [x] Vapi queue distribution (pending calls by campaign) — added 2026-07-21
- [x] MQL summary (active + total opportunities in Warm/Qualified MQL) — added 2026-07-21
- [x] SQL contacts count (contacts with SQL tag) — added 2026-07-21
- [x] Pool distribution (brands, dispensaries, vapi brand/dispensary pool tags) — added 2026-07-21
- [x] Stage mover count (fixed from 0 to 93 via stage ID resolution) — added 2026-07-21
- [ ] Meta raw spend/clicks/impressions (deferred)
- [ ] Matched funnel by landing page (after tracking is tightened)

### Pipeline Movement Tracking

| Metric | Status | Notes |
|--------|--------|-------|
| Stage counts by day | Working | `report_stage_daily_summary.stage_count` |
| Moved-in count | Working | Computed via LAG window comparing previous day's stage count |
| Moved-out count | Working | Computed via LAG window comparing previous day's stage count |
| Won/lost counts | Working | From opportunity status mapping |
| Pipeline history raw events | Captured | `report_raw_ghl_pipeline_history` table populated by GHL Daily Sales Ingest |
| Stage-by-stage velocity | Live | Computed by `LT - Report Pipeline Velocity` using pipeline history events plus the previous stage for each opportunity; writes to `report_stage_velocity_summary` and `report_opp_stage_timeline` |
| Opportunity cycle length | Live | Now computed from actual event timestamps via `report_opp_stage_timeline.days_in_stage` |
| True stage transition timestamps | Live | `report_opp_stage_timeline` has `entered_at` / `exited_at` per opportunity per stage |

**Resolved**: Pipeline velocity (avg days between stages) is now computed from actual pipeline history event timestamps by `LT - Report Pipeline Velocity` (`iFfwh0jpYUZoDhDR`). The workflow uses a query that compares each stage event to the previous stage event for the same opportunity, then writes to `report_stage_velocity_summary` (14 stages across 3 pipelines) and `report_opp_stage_timeline` (50,522 rows). Runs daily at 24h interval.

Additional reporting requests that would be sub sections under the main section and can be covered in calls more in depth by team leads
Sales (john)
- Total calls by status → Available via `report_raw_ghl_calls` and the Calls & Conversations panel in the Executive Report
- Total meetings and if they showed → Available via `report_raw_ghl_appointments` (ingested by `LT - GHL Daily Appointments Ingest`, calendar `SrtXcFVyea7pFl3nTiIK`)
- Contract closed and pending → Available via Sales Detail panel and Deal Stage Pipeline in executive report
- Win rate (closed won / closed total) → Available in Sales Quality panel

Social and site (chella)
- Social engagement: comments, reactions etc. → Needs Meta/Facebook Graph API (not in GHL)
- Website visits and traffic source → Already available via GA4 + channel breakdown
- Interactions on website: page visited, form fills etc. → Already available via GA4 landing pages + GHL forms

Next-week follow-up
- Sequence reporting → add event-level ingest for opens, replies, clicks, bounces, and unsubscribes so the report shows sequence performance, not just enrollments.
- Landing pages → preserve page URL and UTM fields consistently on every link and form so a matched funnel by landing page becomes reliable.
- Website pages → show the most visited pages as a short summary using the landing-page rollup while the deeper funnel tracking is being tightened.
