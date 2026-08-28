# Partnership Campaign Audit Plan

**Created:** 2026-07-31 | **Status:** Historical audit plan; reporting attribution and native partnership report configuration were completed after the original findings | **Auditor:** LLM via n8n-lt MCP + SSH + GHL MCP + direct GHL REST PIT check

---

## Context

The Partnership Marketing pipeline was fully deployed on 2026-07-31: 131 contacts imported, 7 n8n workflows created and published, 3 existing LinkedIn workflows patched, 4 email templates created, Campaign Channel Summary SQL updated, Executive Report frontend deployed as build \2026-07-31-v10-partnership\. A lightweight 9-point audit confirmed workflows active, versions matched, GHL contacts correct, and no regressions.

This deeper audit verifies the pipeline end-to-end across three layers: n8n execution, Postgres data integrity, and reporting (Executive Report API, Campaign Channel Summary endpoint, frontend deployment, GHL native report, and GHL assets).

**Historical findings at audit time:**
- Reply Poller initially used `POST /conversations/search`; this was later corrected to supported `GET /conversations/search` and published on `736386a2-a7d2-434d-b9ba-72026e49c98b`.
- Partnership state was initially bootstrapped empty; the LinkedIn dispatcher now seeds it before fetching ready rows.
- The root `GHL_PIT` was verified against `GET /locations/{locationId}` and `GET /contacts/` with HTTP 200. This resolves the assumption that GHL REST access is unavailable; it does not resolve the separate Firebase/browser report-builder session problem.
- The Partnership Email Dispatcher sent 10 live emails in execution `281334`, all successful and written to `partnership_release_log`.
- The Partnership LinkedIn Dispatcher sent 10 live connection requests in execution `281366`, all profile resolutions and invites successful. The Unipile lookup was corrected to `GET /users/{identifier}?account_id={account_id}` before the test.
- The normal LinkedIn dispatcher batch size was restored to 30 after the controlled test.

**Credentials:** n8n API key (\\\), GHL PIT(s), VPS SSH key at \C:\Users\edmon\.ssh\local-upload\.

---
## Phase 1 -- Execution History (P0)

Check whether dispatchers have fired and what happened.

| Check | How | Expected |
|-------|-----|----------|
| Email Dispatcher | search_executions on Xshck23cKo1yXL9D, limit 5 | >=1 run at 11am ET Mon-Fri, status success |
| LinkedIn Dispatcher | search_executions on crKIsaL5k3YBfqDZ, limit 5 | Status success. 0 ready contacts = empty queue ok. |
| LinkedIn DM Sequence | search_executions on nspggypNF245xzeL, limit 5 | Status success. 0 connected contacts early on. |
| Reply Poller | search_executions on 0SQ7tTk03okegp9V, limit 5 | Status success. Check checked/replied/skipped. |
| Reply Backfill | search_executions on QfJ2EZcc7lZwNgxj, limit 3 | Status success. Partnership rows in samples. |
| Acceptance Checker | search_executions on 3ttEvr5NMcQCS4Hp, limit 3 | Likely zero (no Unipile events yet). |
| Unipile New Messages | search_executions on 7o5EBdvwAuIaWW7k, limit 3 | Likely zero. |
| Any errors? | Filter by status: [error, crashed] across all 10 | Zero expected. If errors, includeData:true. |

**Critical:** For email dispatcher executions, get details with includeData:true. Look at Dispatch Emails node output -- verify status_breakdown shows sent>0, and Write Release Log received items.

---

## Phase 2 -- Postgres Data Integrity (P0)

SSH to VPS (89.117.21.29, root, key C:\Users\edmon\.ssh\local-upload):
`ash
ssh -i C:\Users\edmon\.ssh\local-upload root@89.117.21.29
`

| Check | Command | Expected |
|-------|---------|----------|
| Container name | docker ps \| grep -i postgres | Find actual container name |
| Tables exist | docker exec <pg> psql -U n8n -d n8n -c "\dt partnership*" | Both tables listed |
| Row counts | SELECT 'release_log' as tbl, count(*) FROM partnership_release_log UNION ALL SELECT 'li_state', count(*) FROM partnership_linkedin_connection_state | Depends on dispatcher runs |
| Schema vs bootstrap | \d partnership_release_log and \d partnership_linkedin_connection_state | Matches postgres/partnership-bootstrap.sql |
| Status values | SELECT status, count(*) FROM partnership_release_log GROUP BY status | Should be 'sent' if dispatcher ran |
| No orphans | SELECT * FROM partnership_linkedin_connection_state WHERE source_key != 'partnership' | Zero rows |
| Indexes | SELECT indexname FROM pg_indexes WHERE tablename LIKE 'partnership%' | 7 indexes (4 state + 3 log) |

DB name is n8n, user is n8n (confirmed from pgAzUqpwOiGkGXzO credential).

---

## Phase 3 -- Campaign Channel Summary Endpoint (P0)

Bridge between Postgres data and Executive Report frontend.

| Check | How | Expected |
|-------|-----|----------|
| Endpoint live | curl https://automations.livetransparent.com/webhook/lt-report-campaign-channel-summary?range=7d | HTTP 200, JSON |
| Partnership email row | Find campaignChannelBreakdown entry with campaign: "Partnership emails" | Row present with email_sent count; currently 10 for the verified 7-day window |
| Partnership LinkedIn row | Find campaignChannelBreakdown entry with campaign: "Partnership LinkedIn" | Historical requirement: row must contain the 10 live invite events. This was later implemented through `linkedin_activity_events`. |
| Status filter | SQL uses WHERE status = 'sent' -- Dispatcher writes 'sent' | Values match |
| Email events | Partnership opens/clicks if Email_Events has partnership entries | Check email_event_rows CTE LIKE '%partnership%' |

**Known concern:** Partnership emails sent via POST /conversations/messages (inline HTML, not GHL templates). GHL may not fire Email Event webhooks for custom-sent emails the same way. If missing from Email_Events, opens/clicks won't appear.

---
## Phase 4 -- Executive Report API (P1)

Check whether Bukc0mgOD2r7V6ED has been updated for partnership data.

| Check | How | Expected |
|-------|-----|----------|
| Workflow details | get_workflow_details on Bukc0mgOD2r7V6ED | Read SQL nodes for partnership |
| emailsSent section | Look for partnership_release_log in daily rollup SQL | Likely NOT present -- was not updated |
| LinkedIn funnel | Look for partnership_linkedin_connection_state in linkedinFunnel CTE | Likely NOT present |
| Campaign channels | May fetch from Campaign Channel Summary or own SQL | Check both paths |

**Historical finding:** At audit time, the Executive Report exposed the overall LinkedIn invite count and Partnership email row but not a Partnership LinkedIn row. This was subsequently resolved with durable partnership-scoped `linkedin_activity_events`; the current selected-window campaign row shows 17 invites and 3 verified replies.

---

## Phase 5 -- Frontend Deployment Verification (P1)

| Check | How | Expected |
|-------|-----|----------|
| Build stamp | SSH, check deployed index.html | Shows 2026-07-31-v10-partnership |
| Footer mention | Grep for "partnership" in deployed HTML | Footer mentions partnerships |
| Container | docker ps \| grep reports then docker exec <c> head -8 /usr/share/nginx/html/index.html | Build stamp matches local |
| Campaign rendering | Verify frontend fetches and renders partnership row | Row visible in Campaign Channels table |

---
## Phase 6 -- GHL Assets (P1)

| Check | How | Expected |
|-------|-----|----------|
| Contact tags | GHL MCP search partner_candidate_email (98) + partner_candidate_linkedin (127) | Counts match |
| Owner | Sample 5 contacts, verify assignedTo | Janvi (ck6TRlU3wnTmMxuVpn5F) |
| LinkedIn URLs | Sample 5 LinkedIn-only contacts, check Apollo Person Linkedin URL | URLs present |
| Pipeline | ghl_official_opportunities_get-pipelines | tQkFYrHjALgoLz6oq0uz with 4 stages |
| Stage IDs | Verify stage names vs Reply Poller IDs | newLeadStageId ccc3d423-... = "New Partner Lead" |
| Templates | ghl_official_emails_fetch-template parentId 6a6b768aa43d24a7ce1514f1 | 4 templates returned |
| Template HTML | webfetch each previewUrl | Content matches dispatcher Code node HTML |

---

## Phase 7 -- n8n Workflow Deep Inspection (P1)

Pre-audit confirmed all 7 partnership + 3 patched workflows: versionId == activeVersionId, all active.

| Check | How | Expected |
|-------|-----|----------|
| API key consistency | Check apiKey/ghlApiKey in each Config node | pit-48a3b580 (partnership) or \.GHL_PIT (patched). No blanks. |
| Timezone alignment | Schedule Trigger timezone | Email: America/New_York, LinkedIn: America/Chicago, DM Seq: America/Chicago |
| Error handling | onError on HTTP request nodes | continueRegularOutput or continueErrorOutput |
| Reply Poller pipeline | Hardcoded pipelineId/newLeadStageId | tQkFYrHjALgoLz6oq0uz / ccc3d423-...-064458910eba |
| LinkedIn Dispatcher upsert URL | Config stateUpsertUrl | .../webhook/lt-linkedin-connection-state-upsert |
| Reply Backfill routing (QfJ2) | Route Partnership node: source_table check | Matches SQL alias |
| Acceptance Checker UNION | Find LinkedIn State Row SQL | UNION ALL with NOT EXISTS guard |
| Unipile New Messages (7o5) | Check for partnership routing | Similar UNION + dedicated update node |
| DM Sequence suppression | Send DM Sequence Messages code | dm_conversation_status=active skip, step>=4 complete |
| DM Sequence terminal | step>=4 branch | Should apply partner_linkedin_sequence_completed tag |

---
## Phase 8 -- GHL Native Custom Report (P2, browser-only)

 Requires authenticated GHL browser/Firebase session. Custom Report ID: `6a67dce4a51a4360c60963a3`. The authenticated session was restored and the report was verified in the GHL UI on 2026-07-31. The GHL PIT remains valid for REST CRM access, but it cannot be substituted for the report-builder browser session and the supported API/SDK does not expose widget-layout mutation.

| Check | How | Expected |
|-------|-----|----------|
| Report access | Navigate to `/v2/location/Zwz4relUXVPxx8uohnjV/reporting/reports/view/6a67dce4a51a4360c60963a3` | Pass: report loads with 11 widgets and editable controls |
| Shared date range | Inspect report date range and widget overrides | Pass: report range is `Last week`, Jul 19-25, 2026; widgets show shared report range with no per-widget override |
| Pipeline filterable? | Inspect `Campaign Opportunities` conditions | **Fail: no conditions configured; title is not a Partnership Pipeline filter** |
| Email filters | Inspect Accepted, Opened, Clicked, and Hard bounced conditions | Pass: filters are Accepted, Opened, Clicked, and Hard bounced respectively |
| SMS/call filters | Inspect SMS and call conditions | Pass: SMS is Direction=Outbound; calls are Direction=Outgoing |
| Tags available? | Inspect `Contacts by tag` conditions | **Gap: no conditions configured; widget shows general tag counts, not partnership tags** |
| Partnership metrics | Inspect all widget titles and filters | **Gap: no partnership-specific widget or `partner_*` filter is configured; native GHL has no Unipile activity source** |

API doesn't expose widget mutation. The browser route still reports an HTTP 404 at the document level and the page logs unrelated GHL integration/Firebase errors, but the authenticated SPA renders the report and its data successfully. The remaining work is UI configuration: add Partnership Pipeline and partnership-tag filters, then save and re-verify. Do not guess undocumented report endpoints.

---

## Phase 9 -- End-to-End Dry Run Tests (P2)

Safe tests. Set defaultDryRun: true before running, restore to false after.

### 9A. Email Dispatcher Dry Run
1. update_workflow on Xshck23cKo1yXL9D: set defaultDryRun to true
2. execute_workflow (manual)
3. Verify Dispatch Emails shows status: "planned" items
4. Verify Summary shows correct status_breakdown
5. Restore defaultDryRun: false

### 9B. LinkedIn Dispatcher Dry Run
1. Same pattern on crKIsaL5k3YBfqDZ
2. Verify counts (0 if state table empty)
3. Restore defaultDryRun: false

### 9C. Reply Webhook Test
1. Find real partnership contact with partner_email_queued tag (search GHL)
2. execute_workflow on mRDw57IHtnQe4wOo with webhook: {"contact_id":"<id>","channel":"email","pipeline_id":"tQkFYrHjALgoLz6oq0uz","new_lead_stage_id":"ccc3d423-ff86-46b4-bd53-064458910eba"}
3. Verify: status ok, tags_applied [partner_replied], opportunity_created true
4. Verify GHL: partner_replied tag, opportunity in Partnership Pipeline
5. **CLEAN UP**: Remove test tag and opportunity

### 9D. Acceptance Checker
Hard without real Unipile event. Verify via Phase 7 logic inspection + monitor real events after LinkedIn dispatcher sends invites.

---

## Phase 10 -- Documentation Sync (P3)

The detailed reporting gap inventory and field-level requirements are maintained in `docs/reports/Reporting Gaps and Requirements.md`.

After all findings collected:

| File | Update |
|------|--------|
| AGENTS.md | Add audit results under Partnership Marketing |
| Project Status and Next Steps.md | Update Remaining with findings |
| plan.md | Add audit completion entry |
| reports/embed/executive/index.html | Re-deploy if mismatch |
| This file | Mark completed with findings summary |

---

## Execution Order

P0 (immediate):
  1. Execution history (10 workflows)
  2. Postgres data integrity (VPS SSH)
  3. Campaign Channel Summary endpoint

P1 (next):
  4. Executive Report API SQL audit
  5. Frontend deployment verification
  6. GHL assets (contacts, pipeline, templates)
  7. n8n workflow deep inspection

P2 (safe to defer):
  8. GHL native Custom Report (browser-only)
  9. End-to-end dry run tests

P3 (after findings):
  10. Documentation sync

---

## Key Reference Map

| Component | ID |
|-----------|----|
| Partnership Email Dispatcher | Xshck23cKo1yXL9D |
| Partnership LinkedIn Dispatcher | crKIsaL5k3YBfqDZ |
| Partnership LinkedIn DM Sequence | nspggypNF245xzeL |
| Partnership Reply Handler | mRDw57IHtnQe4wOo |
| Partnership Reply Poller | 0SQ7tTk03okegp9V |
| Partnership Bulk Import | zmrYrUjVcyXaS7PJ |
| Partnership LinkedIn URL Update | ew6uQQnAjgCbjeGn |
| Acceptance Checker (patched) | 3ttEvr5NMcQCS4Hp |
| Reply Backfill (patched) | QfJ2EZcc7lZwNgxj |
| Unipile New Messages (patched) | 7o5EBdvwAuIaWW7k |
| Campaign Channel Summary | MvPLbUAN9IIQikxb |
| Executive Report API | Bukc0mgOD2r7V6ED |
| GHL Custom Report | 6a67dce4a51a4360c60963a3 |
| GHL Partnership Pipeline | tQkFYrHjALgoLz6oq0uz |
| GHL Email Template Folder | 6a6b768aa43d24a7ce1514f1 |
| Partnership credential | configured in the live workflow; value intentionally omitted |
| Postgres tables | partnership_release_log, partnership_linkedin_connection_state |
| Frontend build | 2026-07-31-v10-partnership |
| Frontend container | reports-livetransparent (VPS 89.117.21.29) |
| VPS SSH key | C:\Users\edmon\.ssh\local-upload |

---

## Audit Results (2026-07-31)

### P0 Results

- Phase 1 found recent successful Email Dispatcher runs, but the latest scheduled run was an empty run: `candidates_found=0`, `sent=0`. A controlled dry run after repair found 98 candidates and planned 60 without sending email.
- Initial scheduled failures were traced to doubled SQL quotes in the partnership LinkedIn dispatcher and DM sequence, blocked `$env` access in the Reply Poller, a missing `updated_at` reference in the Reply Backfill UNION, and an unguarded release-log summary insert.
- The live fixes were published and manually verified. Reply Poller execution `277792` returned `checked=0`, `replied=0`, and no errors. Reply Backfill execution `277793` reached its query successfully with no pending rows. Email dry run `277810` returned `sent=0`, `planned=60`, `errors=0`.
- Phase 2 confirmed both partnership tables exist with the bootstrap schema. Both tables currently contain zero rows, there are zero orphan state rows, and the database has nine indexes including primary-key indexes.
- Phase 3 returned HTTP 200 and the `Partnership emails` row. It correctly reports zero sent/opened/clicked values while the release log is empty.

### P1 Findings and Remediation

- The Executive Summary API (`Bukc0mgOD2r7V6ED`) now unions `partnership_release_log` into its email cohort and `partnership_linkedin_connection_state` into its LinkedIn funnel. The live workflow is published at version `1e88538b-4221-443a-8668-9a0b1ff5439e`; the public endpoint returns HTTP 200.
- The report host was rebuilt and recreated on the VPS from commit `8620a18`. `https://reports.livetransparent.com/embed/executive/index.html` now exposes build stamp `2026-07-31-v10-partnership` and the partnership footer text.
- All 131 partnership contacts are now assigned to Janvi (`ck6TRlU3wnTmMxuVpn5F`); the owner repair completed with zero failures and a follow-up dry run reported 131 aligned, 0 unassigned, and 0 conflicting owners.
- The Partnership Pipeline and four email templates are present. The campaign-summary workflow is published and returns the expected catalog row.

### Deferred P2 Checks

- GHL Native Custom Report browser verification is complete. The report loads in the authenticated GHL UI, but its `Campaign Opportunities` and `Contacts by tag` widgets are unfiltered and therefore do not yet represent partnership-only metrics.
- Live LinkedIn invite and live email sends were intentionally not executed. The LinkedIn dispatcher remains a send-capable workflow and requires a separate approved production smoke test.

### Re-audit Findings (2026-07-31)

- The corrected published LinkedIn dispatcher and DM sequence passed safe manual executions `277974` and `277975`; both stopped after successful empty PostgreSQL reads and did not send anything.
- Historical scheduled executions `277633` and `277645` failed because the published SQL at that time contained doubled quotes around `ready` and `connected`. The current published versions use valid SQL, but the scheduled path still needs monitoring after its next production tick.
- The previous `POST /contacts/search` concern was resolved by replacing partnership candidate/active-contact reads with paginated `GET /contacts/` and explicit failure handling. Direct PIT checks now return HTTP 200 for location and contacts access.
- `partnership_linkedin_connection_state` was initially empty. The LinkedIn dispatcher now runs `Seed Partnership State` before its ready-queue read and has 127 seeded `ready` rows.

### August 2026 Cohort Enrollment (2026-08-27)

- The August 26 partnership source files were reconciled as one 431-person cohort. There were 429 unique emails; two shared-email groups (four rows) were skipped for manual resolution.
- 404 new GHL contacts were created. All 427 actionable contacts were tagged with `partner_candidate_email` and `partner_candidate_linkedin`; all 404 new contacts were additionally tagged `august_26_partnership_contact`.
- Three existing contacts received missing person LinkedIn URLs. No Vapi selector tags were applied, and no terminal Vapi outcome tags were changed.
- The active Email Dispatcher and LinkedIn Dispatcher will process the cohort on their existing schedules. No manual outbound execution was performed during enrollment.
- Reconciliation scripts: `scripts/reconcile_august_2026_partnership_live.ps1` and `scripts/tag_august_26_partnership_contacts.ps1`. Final source-tag verification: 404/404 tagged, zero errors.
- `partnership_release_log` has zero rows and no contacts currently have `partner_email_queued`, which is expected while live email sending is withheld. The scheduled email run `277632` reported zero candidates, but its result cannot distinguish an empty queue from the swallowed contacts-search failure.
- Partnership workflows contain provider/API secrets and the protected state-upsert secret directly in Set/Code node configuration and fallback literals. This is an operational security gap even though the values are redacted from this report; they should move to managed credentials or protected runtime configuration and be rotated after migration.
- The native GHL Custom Report was verified through the authenticated browser session. The report contains 11 widgets across opportunities, email, SMS, calls, contacts, appointments, and social posts; partnership-specific filters are still missing.

### Gap Remediation (2026-07-31)

- Replaced partnership email candidate lookup with paginated `GET /contacts/`, with explicit failure handling. Safe execution `278070` found 98 candidates and planned 60; it sent 0.
- Replaced Reply Poller active-contact lookup with paginated `GET /contacts/`, with explicit failure handling. Safe execution `278071` completed with `checked=0`, `replied=0`, and no errors.
- Added `Seed Partnership State` to the LinkedIn dispatcher. It populated 127 partnership state rows from the 127 LinkedIn-tagged contacts before the ready-queue fetch.
- Replaced LinkedIn candidate lookup with paginated `GET /contacts/` and explicit failure handling. Safe execution `278203` found 100 candidate rows, planned 30 requests, and sent 0.
- Set partnership Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence `defaultDryRun=true` during remediation. Live outbound activation remains an explicit follow-up decision.
- DM safe execution `278342` completed successfully with no sends.
- Direct GHL PIT verification returned HTTP 200 for the authorized location and contacts endpoints using the required Bearer/Version headers.
- All modified workflows were republished with matching draft and active versions after the REST updates.
- Added an existing-state lookup before LinkedIn seeding so recurring runs do not rewrite all 127 rows. Validation execution `278675` found `existing=127`, `seeded=0`, and completed the full dry-run path successfully.
- Post-remediation scheduled executions at 20:00 (`278513`, `278515`, `278634`, and `278611`) completed successfully; no errors were recorded after the fixes.
- Re-audited all 7 partnership workflows: each is active with `versionId == activeVersionId`. Corrected hourly dispatcher interval definitions to explicit weekday cron schedules, fixed the DM terminal completion scan, and corrected the shared Acceptance Checker state-upsert header. Safe smoke executions `281269` (email), `281268` (LinkedIn), and `281270` (DM) succeeded; all outbound paths remain dry-run.
- User-approved live activation completed after the audit: Email Dispatcher, LinkedIn Dispatcher, and LinkedIn DM Sequence now have `defaultDryRun=false`; drafts were published and verified active. No manual post-activation execution was run to avoid creating an unscheduled live batch.
