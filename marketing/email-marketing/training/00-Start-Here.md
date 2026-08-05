# Live Transparent Sales Training Docs

This folder is the simple version of the CRM and workflow guides.

Use these files in this order:

1. `01-Pipeline-Training-Guide.md`
2. `02-Daily-Quick-Reference.md`
3. `03-MQL-and-Booking-Rules.md`
4. `04-Email-Open-Follow-Up-Process.md`
5. `05-Website-Visitor-Leads.md`
6. `06-GHL-Automations-Guide.md`

Who this is for:

- New sales hires
- SDRs
- Closers who use GHL every day

What this folder is for:

- Learn the pipeline
- Learn when a lead is ready for sales
- Learn what tags and alerts matter
- Learn what to do each day in GHL
- Learn the current system status:
  - n8n is on `2.33.3` (current production target; recurring workflows use native Schedule Trigger nodes)
  - do not manually refresh/update node versions unless an admin runbook says to
- Learn the website hero consent rule:
  - `T&C 1` = non-marketing SMS consent
  - `T&C 2` = marketing SMS consent
  - these are built-in GHL form consent elements, not separate contact custom fields
- Learn the regulated ads booking rule:
  - only `Regulated Ads On Social/Search` / normalized keys `regulated-ads` or `regulated-ads-on-social-search` get `SQL`
  - only that booking should trigger the `#leads` Slack alert
  - only that booking should move or create the opportunity in `Sales -> Discovery Scheduled`

What this folder is not for:

- Deep technical setup
- n8n build steps
- API details
- admin-only workflow wiring

Simple rule:

- If you are working a lead in GHL, use this folder first.
- If you need backend or admin details, use the original docs in `GHL Live Transparent CRM`.
