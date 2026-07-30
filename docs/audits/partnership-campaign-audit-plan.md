# Partnership Campaign Audit Plan

**Created:** 2026-07-31 | **Status:** P1 remediation completed; P2 browser-only checks deferred | **Auditor:** LLM via n8n-lt MCP + SSH + GHL MCP

---

## Context

The Partnership Marketing pipeline was fully deployed on 2026-07-31: 131 contacts imported, 7 n8n workflows created and published, 3 existing LinkedIn workflows patched, 4 email templates created, Campaign Channel Summary SQL updated, Executive Report frontend deployed as build \2026-07-31-v10-partnership\. A lightweight 9-point audit confirmed workflows active, versions matched, GHL contacts correct, and no regressions.

This deeper audit verifies the pipeline end-to-end across three layers: n8n execution, Postgres data integrity, and reporting (Executive Report API, Campaign Channel Summary endpoint, frontend deployment, GHL native report, and GHL assets).

**Key known risks:**
- Reply Poller uses \GET /conversations/search\ -- GHL API may require \POST\.
- Postgres tables were bootstrapped but may have 0 rows (dispatchers hadn't fired at deployment).
- Two API keys: \pit-48a3b580\ (partnership) and \\.GHL_PIT\ (patched workflows).

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
| Partnership row | Find campaignChannelBreakdown entry with campaign: "Partnership emails" | Row present with email_sent count |
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

**Expected finding:** Executive Report API likely does NOT include partnership data yet. The Campaign Channel Summary was updated but the main Executive Report API SQL was not. If confirmed, follow-up task.

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

Requires authenticated GHL browser session. Custom Report ID: 6a67dce4a51a4360c60963a3.

| Check | How | Expected |
|-------|-----|----------|
| Report access | Navigate to report in GHL UI | Report loads (was 404+Firebase errors last check) |
| Pipeline filterable? | Widget config -- "Partnership Pipeline" available? | Confirms or denies |
| Tags available? | partner_* tags in contact/opportunity filters? | Confirms or denies |
| Add widget? | Attempt to add widget scoped to Partnership Pipeline | Note restrictions |

API doesn't expose widget mutation. If 404 persists, escalate to GHL support.

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

- GHL Native Custom Report browser verification remains blocked: the authenticated report URL returns HTTP 404 with Firebase token/permission errors.
- Live LinkedIn invite and live email sends were intentionally not executed. The LinkedIn dispatcher remains a send-capable workflow and requires a separate approved production smoke test.
