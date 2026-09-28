# Executive Report V1 feedback contract

This contract extends V1 without changing `/embed/executive/`. It is the interface between the facts API, the report UI, and the eventual Priority routing workflow.

## Shared rules

- Every metric uses the selected `America/Los_Angeles` window and returns `basis`, `distinctness`, `date_rule`, `freshness`, and `source_health` metadata.
- Missing, stale, or incomplete sources render `Unavailable`; they never become zero.
- Contacts are distinct by canonical GHL contact ID. Opportunities and stage movement are distinct by opportunity ID unless a field says `contact_metric: true`.
- Closed opportunities are never reopened or moved by Priority routing.
- `Unknown`, `Unattributed`, `Unassigned`, and `Unclassified` remain real buckets in every breakdown.

## Facts API additions

The V1 facts payload may contain these top-level objects. An object is considered available only when `available: true` and its health is ready.

```json
{
  "funnel": {
    "available": true,
    "opportunities_created": 0,
    "mqls_entered": 0,
    "sqls_entered": 0,
    "mql_to_sql_rate": null,
    "closed_won_sqls": 0,
    "closed_lost_sqls": 0,
    "sql_to_closed_rate": null,
    "revenue": null,
    "basis": "distinct opportunity_id; first observed stage entry; LA dates",
    "source_health": "ready"
  },
  "closedBySource": [{
    "source": "Unknown / Unattributed", "sqls": 0, "won": 0, "lost": 0,
    "revenue": null, "coverage": "partial"
  }],
  "weeklyLeadFlow": [{
    "week_start": "2026-09-21", "new_contacts": 0, "mqls_entered": 0,
    "sqls_entered": 0, "later_stage_entries": 0, "current_stage_distribution": []
  }],
  "verticalPerformance": [{
    "vertical": "Unclassified", "leads": 0, "sends": 0, "responses": 0,
    "meetings": 0, "sqls": 0, "won": 0, "lost": 0, "revenue": null
  }],
  "retargeting": {
    "available": true, "eligible": 0, "latest_touchpoints": [],
    "suppressed_or_replied": 0, "next_action_pending": 0,
    "send_authorized": false
  },
  "priority": {
    "available": true, "stage_id": null, "stage_name": "Priority",
    "open_count": 0, "created_in_window": 0,
    "by_source": [], "routing_health": "not_configured"
  }
}
```

The existing same-channel response-SLA definition remains authoritative. The UI label is **Inbound response speed**, not MQL-to-call speed.

## Priority routing contract

The canonical pipeline is `Sales Outreach` (`dhdlf3O4tymxFtHk4aqq`). The live Priority stage is now verified at position 1 with GHL stage ID `be636da7-3c15-48ab-b589-c75bcd6f9955`. Workflow publication must use this exact ID and re-read the pipeline after publication.

Qualifying events are: identifiable inbound call, inbound voicemail disposition, identifiable Unipile LinkedIn DM/reply, and qualifying human email reply. Bounces, unsubscribe notices, and automated provider events are excluded. Each accepted event writes an immutable audit row keyed by `(contact_id, source_event_id)` with channel (`call`, `voicemail`, `linkedin`, or `email`), event timestamp, routing reason, prior opportunity ID/stage, resulting opportunity ID/stage, owner, and outcome.

Routing is an upsert-and-move operation:

1. Resolve the contact using the existing inbound handler.
2. Search open `Sales Outreach` opportunities for that contact.
3. Move the existing open opportunity to Priority, preserving owner and attribution; otherwise create one Priority opportunity.
4. Never reopen or move a closed opportunity.
5. A retry with the same contact and source event is a no-op.

Priority is excluded from cold-outbound sequence eligibility. This report-only visibility does not authorize sending.

## Acceptance fixtures

The API and routing tests must cover: first event, duplicate event retry, existing open opportunity, no opportunity, closed opportunity, unknown contact, excluded email event, conflicting owner data, and two different events for the same contact. Each fixture must assert exact IDs and no duplicate opportunity creation.
