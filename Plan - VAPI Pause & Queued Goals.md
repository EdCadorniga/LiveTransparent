# Plan - VAPI Pause & Queued Goals

Last updated: 2026-06-05 (marketing email pause added)

## Context

On 2026-06-05, after completing the Apollo API key rotation and the reaper work, the
owner requested:

1. Pause all VAPI activity (no calls placed, no callbacks processed).
2. Pause all marketing-related email workflows (CSV imports, intake routing, campaign ingestion).
3. Document the queued goals so the work resumes cleanly in a future session.

The 6 VAPI workflows and 9 marketing-email workflows are now unpublished (no live
executions). The GHL-side infrastructure (reaper, Apollo V3/V4 callbacks, contact
updates) and the lead-intake forms remain active.

## Paused VAPI Workflows (idempotent pause)

| Workflow | ID | Action | Status before | Status after |
|----------|----|--------|---------------|--------------|
| LT - Voice Agent V1 Vapi Callback + Tools | `fx4UvKUWbqJEY3LK` | Unpublished | Active | Inactive |
| LT - Voice Agent V1 Outbound Dialer (Vapi) | `r7UjWLndmc6EqEUW` | Unpublished | Active | Inactive |
| LT - Voice Queue Vapi Intake Poller | `bYk1Ai6MJLyhTsDZ` | Unpublished | Active | Inactive |
| LT - Voice Queue Enqueue | `XzcpOBi9YcIhJPck` | Unpublished | Active | Inactive |
| LT - Voice Dequeue Next | `KsBMFcz1YpBGrjDW` | Unpublished | Active | Inactive |
| LT - Call Outcome Ingest | `PUCfTZBANSPcgS0c` | Unpublished | Active | Inactive |

## Paused Marketing Email Workflows (idempotent pause)

| Workflow | ID | Action | Status before | Status after |
|----------|----|--------|---------------|--------------|
| GHL Warm Intake - Email Outbound Tag (Webhook) | `J4B0n0QeSeOeqAci` | Unpublished | Active | Inactive |
| GHL Warm Intake - Email Inbound Tag (Webhook) | `SmMf8QIfysuxQJbG` | Unpublished | Active | Inactive |
| LT - Cold Outreach CSV -> GHL Import (DryRun, Staged) | `T28iLcm4Hszo19MG` | Unpublished | Active | Inactive |
| LT - Cold Outreach CSV -> Postgres Ingest (Staged) | `kVCTmy1m8fEyP6Q7` | Unpublished | Active | Inactive |
| LT - Emerald CSV -> GHL Import (DryRun, Staged) | `BLr1x1HKdgM1Xfxk` | Unpublished | Active | Inactive |
| LT - Emerald CSV -> Postgres Ingest (Staged) | `mSegmpMUd0DRwFEx` | Unpublished | Active | Inactive |
| LT - Emerald Campaign Snapshot -> Postgres Ingest (Staged) | `0jDKgG8VvmfyORQn` | Unpublished | Active | Inactive |
| LT - Emerald Intro Sent -> P2 Queue Dispatcher (Staged) | `dMDbLSzPSSrHo1wK` | Unpublished | Active | Inactive |
| LT - Emerald Executive SSO -> Company Sync (Staged) | `GHVYyYmhfNiZ7bbN` | Unpublished | Active | Inactive |

### Important caveat - GHL sequences still send

Pausing these n8n workflows stops CSV imports, contact routing, and intake tagging,
but the actual GHL email sequences live in the GHL UI and continue to send on
schedule for any contact already enrolled. To stop outbound marketing email entirely
in GHL, manually pause or delete the active email sequences in
`https://app.gohighlevel.com/` for location `Zwz4relUXVPxx8uohnjV`. This is a
separate step outside of n8n and is the owner's responsibility.

## Workflows that remain ACTIVE (not VAPI, not email outreach)

- `LT - Apollo Queued Timeout Reaper` (`RL5ZyUoshSPbmVA1`) — GHL-only, hourly, flips stuck contacts to `callback_timeout`.
- `GHL Apollo Phone Enrichment - Callback Handler V4` (`U7c6byTLXAMgcS75`) — receives Apollo's callback deliveries to GHL (if any resume).
- `GHL Apollo Phone Enrichment - Callback Handler V3` (`YaWizRnw7XmkcvZH`) — V3 backup callback handler.
- `Apollo Phone Enrichment Intake V3` (`WuxgTa0EEL1mb2SA`) — accepts intake requests, calls Apollo `POST /v1/people/match`, sets `queued` status.
- `Sheet First` (`WmKAhG7mIaXonNsh`) — Apollo enrichment via sheet import.
- LinkedIn outreach workflows (still active):
  - `LT - LinkedIn Connection State Sync (Unipile)` (`ceaKnz6E3onQrZpt`)
  - `LT - LinkedIn Connection State Upsert` (`Old7ZvyVYgFaJgDr`)
  - `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`)
  - `LT - GHL LinkedIn Connect Dispatcher` (`fXxw5lanZcDmUrst`)
  - `LT - LinkedIn DM Sequence (Unipile)` (`d0tEtijajisIsYcs`)
  - `LT - LinkedIn Connection Request (Unipile) (Internal Test)` (`Zt8p2aYtIuY0HK18`)
- Instagram outreach workflows (still active):
  - `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`)
  - `LT - Instagram DM State Upsert` (`enkF6Y25bvzVSPr0`)
- SimpleTexting SMS workflows (still active; some staged):
  - `LT - SimpleTexting Campaign Sequencer (Staged)` (`7mSiivR3NhtLIcNz`)
  - `LT - SimpleTexting Pool Dispatcher (Staged)` (`usxYXSuc4ahw40V3`)
  - `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`)
  - `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`) — live
  - `LT - SimpleTexting Inbound Reply (Webhook)` (`i0pROHpFtN4LYR0Q`)
  - `LT - SimpleTexting Unsubscribe Events (Webhook)` (`IyBKMkpYQ7pa0C8V`)
  - `LT - SimpleTexting Delivery Events (Webhook)` (`AEi1VCzkLvaYFr4U`)
- Warm intake routing (still active for new leads):
  - `GHL Warm Intake - Add Intake Tag (Webhook)` (`OowP3sAd8c9paSKf`)
  - `GHL Warm Intake - SMS Tag (Webhook)` (`5nYzp9DgQUopzWhR`)
  - `GHL Warm Intake - Referral Tag (Webhook)` (`6lp8sIS3YMB1t9Ri`)
  - `GHL - MQL Tag -> Ensure Warm Qualified Opportunity (Webhook)` (`MI91SutAbAj3QSXp`)
- Reporting workflows (still active).
- Website lead intake forms (still active).
- Slack notification webhooks (still active).

## Resumption Playbook

To bring marketing email workflows back online after a future agent session:

1. Re-publish the 9 paused workflows in this order (independent, but matches the
   data flow):
   1. `GHVYyYmhfNiZ7bbN` (Executive SSO -> Company Sync)
   2. `mSegmpMUd0DRwFEx` (Emerald CSV -> Postgres Ingest)
   3. `kVCTmy1m8fEyP6Q7` (Cold Outreach CSV -> Postgres Ingest)
   4. `BLr1x1HKdgM1Xfxk` (Emerald CSV -> GHL Import)
   5. `T28iLcm4Hszo19MG` (Cold Outreach CSV -> GHL Import)
   6. `0jDKgG8VvmfyORQn` (Emerald Campaign Snapshot -> Postgres Ingest)
   7. `dMDbLSzPSSrHo1wK` (Emerald Intro Sent -> P2 Queue Dispatcher)
   8. `SmMf8QIfysuxQJbG` (Email Inbound Tag) — resume reply handling
   9. `J4B0n0QeSeOeqAci` (Email Outbound Tag) — resume outbound routing
2. Re-enable any GHL email sequences that were paused in the GHL UI.
3. Trigger a small test through the Emerald CSV -> GHL Import endpoint and confirm
   the contact lands in the expected stage and gets the email-outbound tag.

To bring VAPI back online after a future agent session:

1. Review this plan and the `Project Status and Next Steps.md` voice section.
2. Re-verify the Vapi dashboard still points all tools and the end-of-call webhook
   to `https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`.
3. Publish the 6 paused workflows in this order (each is independent but the order
   matches the call lifecycle):
   1. `KsBMFcz1YpBGrjDW` (Dequeue Next) — required for outbound
   2. `XzcpOBi9YcIhJPck` (Enqueue) — required to feed Dequeue
   3. `PUCfTZBANSPcgS0c` (Call Outcome Ingest) — required to close the loop
   4. `fx4UvKUWbqJEY3LK` (Vapi Callback + Tools) — required for inbound callbacks
   5. `bYk1Ai6MJLyhTsDZ` (Intake Poller) — feeds Enqueue from vapi_queue tag
   6. `r7UjWLndmc6EqEUW` (Outbound Dialer) — places the actual calls
4. Run the poller once manually and confirm it picks up a contact and routes it
   through the dialer.

## Queued Goals (in priority order)

### Goal A - VAPI Dialer: Em_All_Known_Phones Fallback

**Why**: The current dialer (`r7UjWLndmc6EqEUW`) only uses the primary GHL `phone`
field. Many contacts (especially after CSV imports) have a known phone in the
`Em_All_Known_Phones` custom field (`F8iUFGsA8CqdzEzjY3Eh`, LARGE_TEXT) but no
primary `phone`. We need to fall back to the parsed list when primary is empty.

**Where to edit**: `n8n/voice-agent/dialer-workflow-clean.mjs`, the
`Code - Check Phone` node. JSON export lives at
`n8n/voice-agent/dialer-workflow-clean.json` and legacy backup at
`n8n/voice-agent/workflow-1ogCy-DIALER-EXPORT.json`. Active deployed workflow
is `r7UjWLndmc6EqEUW`.

**Plan**:
1. Read the current `Code - Check Phone` node body to confirm field shape.
2. Pull a few sample contacts with `Em_All_Known_Phones` populated to see actual
   value formats (e.g. `+1 562 555 1234`, `562-555-1234`, multi-line).
3. Add a helper that:
   - reads `Em_All_Known_Phones` from the contact custom fields,
   - parses with the regex `/\+?\d[\d\s().-]{7,}\d/g`,
   - returns the first valid E.164 candidate (or `null`),
   - logs `phone_source: "primary" | "em_all_known" | "none"` for downstream use.
4. Add the phone source to the post-call GHL note so the outcome is auditable.
5. Update the dialer workflow via the SDK pattern in the existing
   `intake-poller-update.mjs` and publish.
6. Verify with a test call against a contact that has only `Em_All_Known_Phones`
   populated.

**Estimated effort**: 30-60 minutes. Low risk; field shape is well-known.

### Goal B - Investigate V4 Callback Root Cause

**Why**: The V4 callback URL
`https://automations.livetransparent.com/webhook/ghl-apollo-phone-enrichment-callback-v4`
(`U7c6byTLXAMgcS75`) has had **zero** Apollo deliveries since 2026-05-13. The
reaper handles the staleness but the root cause is still unknown. Possibilities:
- Apollo dashboard webhook configuration was disabled or rotated.
- A signed-secret / IP allowlist change on our side broke Apollo's outbound POST.
- Apollo's webhook delivery log shows 4xx/5xx responses.

**Plan**:
1. Pull Apollo dashboard webhook configuration and delivery log.
2. Compare the expected `webhook_url` (currently
   `https://automations.livetransparent.com/webhook/ghl-apollo-phone-enrichment-callback-v4`)
   against what Apollo has on file.
3. Synthetic POST verification (already done 2026-06-05 — execution `75179`
   returned 200) confirms the endpoint itself is healthy.
4. If the Apollo-side delivery is missing, re-register the webhook with the
   correct URL and secret.
5. If 4xx is returned by Apollo, check Coolify/nginx logs and n8n webhook
   auth settings.

**Estimated effort**: 20-40 minutes once Apollo dashboard access is available.

### Goal C - Reaper Defensive Retry

**Why**: The reaper's first run had 1 transient GHL 400 on the 500th sequential
PUT (Joey Evans). The write actually went through (GHL dateUpdated confirms),
but the reaper's error log falsely reports `update_failed`. We should add:
- Short retry with exponential backoff on 5xx (not 4xx).
- Better error categorization: distinguish "transient" from "permanent" failures
  (e.g. 4xx with malformed payload vs 5xx).
- Possibly chunk the PUT loop with `setTimeout(50ms)` between calls to avoid
  rate-limit pressure.

**Estimated effort**: 20-30 minutes. Low risk; the existing payload is correct.

### Goal D - Secrets Out of Config Nodes

**Why**: Apollo API key, GHL API key, and webhook secrets all live in plain-text
`Config` Set nodes. Anyone with n8n viewer access can see them. Move to n8n
credentials or env-backed config.

**Plan**:
1. Inventory Config nodes across all live workflows that contain a secret.
2. For each, create an n8n credential of the appropriate type
   (`httpHeaderAuth` for webhook keys, `httpBasicAuth` or similar for APIs).
3. Replace inline values with `={{ $credentials.<name>.<field> }}` expressions.
4. Verify with `GET /api/v1/workflows/{id}` that no plain-text secret remains.

**Estimated effort**: 45-90 minutes. Medium risk; credential misconfig breaks
the workflow until fixed.

### Goal E - Vapi Dashboard Verification

**Why**: Re-verify the Vapi dashboard (assistant `3f9bbfd2-efa6-4381-81e6-26f2452d28f1`)
points all 4 tools and the end-of-call webhook at
`https://automations.livetransparent.com/webhook/lt-voice-agent-vapi-callback`.

**Plan**: Open the Vapi dashboard, confirm each tool's endpoint, confirm
end-of-call webhook URL. If any drift, fix in Vapi.

**Estimated effort**: 10 minutes. Zero risk.

## Reference Files

- [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
  - canonical live state
- [AGENTS.md](./AGENTS.md)
  - operating guide, including the new MCP `n8n-lt` `updateNodeParameters` gotcha
- [repomix-output.md](./repomix-output.md)
  - regenerate via `. $PROFILE && packlive` after significant work
- `n8n/workflows/lt-apollo-queued-timeout-reaper.ts` — reaper source
- `n8n/voice-agent/dialer-workflow-clean.mjs` — VAPI dialer source (edit for Goal A)
- `n8n/voice-agent/intake-poller-update.mjs` — VAPI poller source (reference pattern)
