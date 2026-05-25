# LiveTransparent Agent Notes

## Project Context
- Deployed on a VPS via Coolify: containers `n8n` (`automations.livetransparent.com`) and `reports` (`reports.livetransparent.com`). Containers reach each other over Coolify's internal network.
- `bookstack/` and `qdrant/` prepared but not deployed.
- n8n target version: `2.19.5`. Canonical MCP: `n8n-lt` (confirmed working).

## Working Assumptions
- Prefer Coolify internal service-to-service communication where possible.
- Canonical public n8n host: `automations.livetransparent.com` (webhooks, editor, MCP).
- Config centralized in root `.env` (n8n/.env consolidated). Env vars set in Coolify; root `.env` is reference copy.

## Agent Tooling
- Codex config: `C:\Users\edmon\.codex\config.toml`.
- Prefer `n8n-lt` MCP or direct API calls before browser-based approaches.
- GHL MCP: primary `ghl_official`, secondary `ghl_katwill_*`.

## GHL & n8n Rules
- Prefer runbooks in `GHL Live Transparent CRM/` before workflow changes.
- Verify live state after every mutation. Fetch first, patch second. Audit live workflow + recent execution before declaring a fix.
- Preserve graph integrity: keep existing node IDs, keep connections map aligned.
- Use `Config` nodes for secrets/constants when env access is blocked or unreliable.
- Voice automations: prefer `Switch` over `IF`. Use raw JSON import for dialer patches (preserves Switch nodes). Expressions: `={{ ... }}` with `$('Node').item.json.field`.
- Report end-to-end validation: leads ingest → attribution bridge → daily rollups → executive summary.

## Live Systems

### Voice AI (Vapi + n8n) — Phase 2
- **Phone**: `+1 (562) 534 1977` (`bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4`)
- **Vapi Assistant ID**: `3f9bbfd2-efa6-4381-81e6-26f2452d28f1` (successEvaluation enabled)
- **All webhooks** → `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`
- **Env vars in `.env`**: `VAPI_PHONE_NUMBER_ID`, `GHL_LOCATION_ID=Zwz4relUXVPxx8uohnjV`, `GHL_API_KEY` aliases `GHL_PIT`

| Workflow | ID | Status |
|----------|----|--------|
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Active — merged callback + 4 tools |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Active — queue dialer, contact-TZ-aware, 72h cooldown |
| LT - Voice Queue Vapi Intake Poller | `bYk1Ai6MJLyhTsDZ` | Active — polls `vapi_queue`, E.164 phone bypass |
| LT - Voice Queue Enqueue | `XzcpOBi9YcIhJPck` | Active — webhook enqueue (allows NULL phone) |
| LT - Voice Dequeue Next | `KsBMFcz1YpBGrjDW` | Active — webhook dequeue → Vapi call |
| LT - Call Outcome Ingest | `PUCfTZBANSPcgS0c` | Active — GHL call webhooks → Postgres + Slack |

**Dialer pipeline**: Cron (Mon-Fri 9am-5pm CT) → fetch+lock → guard → HTTP GET GHL contact → Code check phone (fallback: GHL contact timezone → CT 12-2pm safe window) → HTTP POST Vapi call → Postgres Mark Attempted (attempt_count+1, next_attempt_at=NOW+72h) → GHL note.
**Intake pipeline**: Cron 10min → search GHL `vapi_queue` → enqueue if valid E.164, otherwise skip based on enrichment status.

**4 tools in callback** (`fx4UvKUWbqJEY3LK`):
| Tool | Action |
|------|--------|
| `update_lead_status` | GHL tag + Postgres disposition update |
| `add_to_dnc` | `voice_call_queue.dnc=true` + GHL DNC tag |
| `log_call_outcome` | Upsert `voice_call_attempt` with disposition/notes/followUpAt |
| `notify_sales` | Slack `#leads` alert |

**vapi_* tag inventory** (applied by `fx4UvKUWbqJEY3LK`):
| Tag | When |
|-----|------|
| `vapi_call_attempted` | `update_lead_status` called during call |
| `vapi_dnc` | `add_to_dnc` tool invoked |
| `vapi_human_answered` | Human answered (base enrichment) |
| `vapi_interested` | Human + `successEvaluation=true` |
| `vapi_not_interested` | Human + `successEvaluation=false` |
| `vapi_interest_unknown` | Human answered, couldn't gauge (silence/short) |
| `vapi_voicemail` / `vapi_voicemail_left` / `vapi_no_answer` / `vapi_busy` / `vapi_wrong_number` / `vapi_contact_disconnected` | End-of-call event by outcome |

### Report Pipelines (all active unless noted)
| Workflow | ID | Notes |
|----------|----|-------|
| GHL Daily Leads Ingest | `osIJOgBmWITF5Yuv` | |
| GHL Daily Sales Ingest | `aYT5oHcgmBALzHy5` | |
| GHL Daily Calls Ingest | `SqNQ0BYaTdcqyt1l` | Inactive — GHL endpoint 404 |
| GHL Daily Appointments Ingest | `yWZVSqEcjTbMT3kG` | calendarId `SrtXcFVyea7pFl3nTiIK` |
| GHL Daily Social Ingest | `QZoqCaTwDhbym80O` | 5 accounts |
| GA4 Daily Ingest | `6pCSGzFmrMDFL5Yq` | 6 channels flowing |
| GA4 Traffic Rollup Bridge | `0P2AZcQYWYZjXbRi` | |
| GSC Daily Ingest | `xHqmCC1vOeZ11gCd` | |
| GSC Rollup Bridge | `fOVBHwti9rC3qrLV` | Daily 04:00 UTC → `report_daily_summary.gsc_*` |
| Report Attribution Bridge | `Y0TU7Il71JswxOBp` | |
| Report Daily Rollups | `EUeOiRttoVLQ9zF9` | Owns dedupe patches, GA clobber fix |
| Report Executive Summary API | `Bukc0mgOD2r7V6ED` | Funnel-efficiency metrics live |
| Report QA and Alerts | `M5mXcDTFSko6EdHb` | |
| Report Config Sync | `aomO3Z4AXJIgEvvN` | |
| Report Publish Refresh | `3gXztCnBEN6sGINb` | |
| Report Postgres Bootstrap Apply | `3XHThUiUSNa4sTb9` | |
| Report Pipeline Velocity | `iFfwh0jpYUZoDhDR` | 14 stages, 3 pipelines, 50k+ rows |
| GHL Executive Report Menu Sync | `8YtaPmPnTXUkBDAd` | Inactive — one-time provision |

### Other Live Systems
- **SimpleTexting**: SMS Send, Delivery Events, Inbound Reply, Unsubscribe webhooks active. Pool Dispatcher / Campaign Sequencer inactive by design.
- **Unipile/LinkedIn**: `LT - GHL LinkedIn Connect Dispatcher` (`S32vc8pjJIBZZHLK`) active, Mon-Fri 10am-4pm EST, 10/run, 50/day cap.
- **GHL warm intake/routing**, **Apollo enrichment**, **Emerald/Cold outreach** — all active.
- **Meta Ads API**: Live via system user token against `act_2186975138800404`. `META_TOKEN` and `META_AD_ACCOUNT_ID` in `.env`. Historical data from `act_975543647768982` / `act_24843211111954088` via staged ingest.

### Known Data Issues
- `closed_won = 0` is genuine (no won deals yet).
- Attribution coverage: 97 cohort contacts, 46.4% bridge match, 100% opportunity match coverage.
- 30-day `contact_to_opportunity_rate = 0` — no new contacts in window matching through to opportunities.
- GA4: 6 channels flowing (Email, Organic Social, Direct, Organic Search, Unassigned, Referral). Rollups preserve GA-backed rows (clobber fix live).

## Paths & Layout
- Docker/service assets under their folders (`n8n/`, `postgres/`, `reports/`). Marketing assets under `marketing/`.
- Future-phase: `bookstack/`, `qdrant/`.
- Agent source code for dialer: `n8n/voice-agent/dialer-workflow-clean.mjs`.

## Key File Map
| File | Purpose |
|------|---------|
| `.env` | Root secrets reference (n8n, GHL, SimpleTexting, Unipile, GA4, Meta, Vapi) |
| `LiveTransparent Report Plan.md` | Report build plan |
| `GHL Live Transparent CRM/` | Operating snapshot, data contract, runbooks |
| `postgres/reporting-bootstrap.sql` | Reporting schema |
| `n8n/docker-compose.yml` | n8n service definition |
| `n8n/voice-agent/` | Voice agent specs, prompt policy, schema, workflow JSON, runbooks |
| `reports/embed/executive/index.html` | Executive report SPA |
| `reports/nginx.conf` | Nginx config (/api/report/ → n8n webhook) |
| `Backup of all n8n workflows/` | 45 canonical workflow backups (1 per live WF) |
| `Project Specifications.md` | Architecture spec, data contracts, guardrails |
| `plan.md` | Remaining implementation plan + future phases |

## Next Steps
1. **Voice hardening**: move remaining secrets out of workflow `Config` nodes → credentials/env-backed config. Keep raw JSON import path for dialer patches.
2. **Report enrichment**: richer contact-capture panel (counts + conversion rates by channel/landing page); matched funnel views by channel/campaign/landing page.
3. **Meta attribution**: expose Meta-tagged visits + downstream activity in Executive Report (spend-independent).
4. **Nurture automation**: build `WL - Nurture - 14 Day` workflow (apply `LT Nurture Active` tag, 14-day sequence, skip if tag present).
5. **GSC**: keep Search Console credential valid; pipeline fully live (raw queries + daily rollup into `report_daily_summary.gsc_*`).
6. **Cross-report**: intersect GHL `Bad Data Reasons` custom field with `vapi_*` tags to identify misclassified contacts.
