# Plan Pointer

> **Before reading this file, first review `repomix-output.md` for full system architecture, blueprints, and roadmaps.** This plan tracks active work items; it does not repeat the architecture.

- Canonical status: [Project Status and Next Steps.md](./Project%20Status%20and%20Next%20Steps.md)
- Active work now spans the **Emerald email campaign** (activated 2026-07-07), voice, reporting, LinkedIn outreach, Instagram outreach, and the upcoming SimpleTexting SMS campaign.

## Vapi Campaign Rollout

### GHL Tag IDs

| Tag | ID |
|-----|----|
| vapi_campaign_brand | exfU7DXbFF1c314Z1QXQ |
| vapi_campaign_dispensary | FiYEwJdMSIyKZa059wRY |
| vapi_already_called | HhkfhzocuEdOFOxeeHu2 |

### Quality Gate (PENDING)

Manual test call per assistant (Alex + Jordan) via Vapi dashboard BEFORE enabling dialer or intake poller. Verify persona, tools fire, end-of-call report delivers, dispositions correct.

### Active Queue (Imported Pool Only)

| Contact | Campaign | Company |
|---------|----------|---------|
| Oxa0BTBbPi6JkPXGQIeT | Dispensary | AYR Cannabis Dispensary - Ocala |
| 2AthxJS3uMoGWxnVU9v7 | Brand | Miss Grass |
| FA2Cd923b7YzmJBdfByX | Brand | Local Grove |
| DkDogBpdJhH1gX8pauNP | Dispensary | Northern Green Canada |

Dedup confirmed across classifier, feeder, enqueue, and dequeue. 5 legacy non-imported campaign rows moved to `failed` to keep first batch isolated.

### Phase 4 — Activation Order (Ready after quality gate)

1. LT - Call Outcome Ingest (capture results)
2. LT - Voice Queue Enqueue (accept queue rows)
3. LT - Voice Agent V1 Outbound Dialer (place calls)
4. LT - Voice Agent V1 Vapi Callback + Tools (process results)
5. LT - Voice Dequeue Next (serve next call)
6. LT - Voice Queue Vapi Intake Poller (only after test batch passes)

### Remaining Operational Items

- Move remaining secrets out of workflow Config nodes into credentials or env-backed config.
- Verify Vapi dashboard still points all tools and end-of-call webhook to canonical callback URL.
- Diagnose Apollo phone-enrichment callback URL zero deliveries since 2026-05-13.
- Deploy staged SimpleTexting SMS workflows.
- Retry blocked GSC ingest workflow.
- Build Meta Ads ingest for spend, clicks, impressions, and cost metrics.
