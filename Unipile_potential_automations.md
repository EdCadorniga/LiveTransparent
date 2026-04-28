# Unipile Potential Automations

These are potential automations we want to do using Unipile for our regulated-industry advertising business.

---

## 1. InMail Campaigns

**Purpose:** Send sponsored LinkedIn messages directly to prospects who aren't connected.

**Use Case:** Great for reaching decision-makers who don't accept connection requests.

**Implementation:**
- Build a GHL automation that triggers when a new lead enters the system
- Send an InMail campaign with a personalized message
- Track responses and tag leads based on engagement

---

## 2. List Building & Enrichment

**Purpose:** Search LinkedIn for ideal prospects and enrich them with contact info.

**Use Case:** Find marketing directors at cannabis brands, CBD companies, or other regulated industries.

**Implementation:**
- Create a scheduled workflow that searches for targets by title/industry
- Enrich profiles with email, phone, company size
- Auto-create/update GHL contacts with enriched data
- Tag by campaign stage and priority score

---

## 3. Competitor Audience Targeting

**Purpose:** Find people who follow or engage with competitor pages.

**Use Case:** Target prospects who are already interested in regulated-industry advertising solutions.

**Implementation:**
- Monitor competitor LinkedIn pages for followers
- Build targeted outreach lists from engaged users
- Send personalized messages highlighting our unique capabilities
- Track conversion rates vs. cold outreach

---

## 4. Event-Based Outreach

**Purpose:** Trigger outreach when prospects post about challenges or attend events.

**Use Case:** Reach out when someone posts about "getting banned from Meta ads" or industry events.

**Implementation:**
- Monitor LinkedIn for keywords like "restricted", "banned", "compliance"
- Trigger automated outreach within 24 hours
- Personalize message based on their specific pain point
- Schedule follow-up tasks in GHL

---

## 5. Multi-Step Sequences

**Purpose:** Automate a 3-5 step sequence with timed follow-ups.

**Use Case:** Connection → follow-up message → InMail → break-up message.

**Implementation:**
- Day 0: Send connection request
- Day 3: If accepted, send follow-up message
- Day 7: If no response, send InMail
- Day 14: If still no response, send break-up message
- Track acceptance/response rates at each stage

---

## 6. Lead Scoring & Prioritization

**Purpose:** Score prospects based on profile signals.

**Use Case:** Prioritize hot leads for manual follow-up.

**Implementation:**
- Score based on job seniority (executive = high score)
- Score based on company size (larger = higher score)
- Score based on engagement rate (active poster = higher score)
- Auto-route high-score leads to sales team in GHL
- Low-score leads go into nurture sequence

---

## 7. CRM Sync & Tagging

**Purpose:** Auto-create/update GHL contacts and track engagement history.

**Use Case:** Keep GHL in sync with LinkedIn outreach activities.

**Implementation:**
- Webhook listener for Unipile events (connection accepted, message replied)
- Auto-create GHL contact if not exists
- Tag by campaign stage (connected, replied, scheduled, etc.)
- Log all outreach history in GHL notes
- Trigger GHL automations based on engagement

---

## 8. A/B Testing Message Variations

**Purpose:** Test different hooks and automatically route better performers.

**Use Case:** Test "Mood case study" vs. "compliance guarantee" messaging.

**Implementation:**
- Create multiple message variants in template registry
- Split outreach 50/50 to test groups
- Track acceptance/response rates per variant
- Auto-switch to winner after statistical significance
- Log results in GHL for future reference

---

## 9. Analytics & Attribution Dashboard

**Purpose:** Track connection acceptance rates, response rates, and downstream conversions.

**Use Case:** Measure ROI of LinkedIn outreach campaigns.

**Implementation:**
- Export Unipile metrics to Postgres or BigQuery
- Build dashboard showing:
  - Connections sent / accepted rate
  - Response rate by message variant
  - Meetings booked from LinkedIn
  - Leads created from LinkedIn
  - Revenue attributed to LinkedIn
- Sync metrics to GHL reports

---

## 10. Team Account Management

**Purpose:** Manage multiple LinkedIn accounts with centralized reporting.

**Use Case:** One account for John, one for Cameron, one for sales team.

**Implementation:**
- Use Unipile's team features for multiple accounts
- Centralized reporting dashboard
- Permission-based access (sales vs. marketing)
- Auto-rotate accounts to avoid rate limits
- Track performance per account/rep

---

## Bonus: GHL Automation Integration

**Purpose:** Trigger GHL automations based on Unipile events.

**Use Case:** Automatically move leads through sales pipeline.

**Implementation:**
- Webhook endpoint in GHL for Unipile events
- On connection accepted: Add to "Hot Lead" campaign
- On message replied: Schedule follow-up call task
- On meeting booked: Create calendar event + send prep email
- On no response after X days: Add to nurture sequence

---

## Next Steps

1. **Priority 1:** Implement CRM Sync & Tagging (already partially done via webhook)
2. **Priority 2:** Build Multi-Step Sequences for John's outreach
3. **Priority 3:** Set up Lead Scoring & Prioritization
4. **Priority 4:** Create Analytics Dashboard for ROI tracking

Each automation can be implemented incrementally, starting with the webhook infrastructure already in place.
