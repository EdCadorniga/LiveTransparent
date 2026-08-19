# Session Handoff: Company Instagram Page DM Delivery

Updated: 2026-08-18

> **Superseded in part by `docs/sessions/2026-08-18-instagram-company-page-dm-priority.md`.** The company-page DM sender is now LIVE (`IeovbYnhCsetXS89`, active and published), with brands-first send priority (dan_brands=1, dan_dispensaries=2, partnerships=3) and a Message-1-first strategy. The contract, audience selectors, GHL field plan, and guardrails below remain authoritative.

Treat live n8n and the deployed Postgres state as authoritative. The repository contains the current bootstrap, import, identity-validation, association, and dry-run workflow sources, but none of the new workflows are published.

## Next Agent: Start Here

The Postgres state model, source import, fail-closed Unipile identity validator, GHL association bridge, and Message 1 dry-run dispatcher now exist. No live Instagram message was sent, and no new workflow is active or published.

1. Read `repomix-output.md`, `AGENTS.md`, this handoff, `plan.md`, and the first 180 lines of `Project Status and Next Steps.md`.
2. Read `docs/strategy/unipile-ghl-bidirectional-integration.md`, especially `Company Instagram Page Outreach Contract (2026-08-14)` and the existing inbound/outbound bridge sections.
3. Fetch live state before mutation. Live n8n is the source of truth; repository workflow snapshots may be stale.
4. Continue identity validation in controlled manual batches and resolve the remaining Partnership GHL associations without fuzzy automatic matching.
5. Add the live GHL tag/conversation suppression check to a no-send validation path.
6. Ask for explicit approval before creating, publishing, or manually executing any live Instagram send action.

## Implementation Status: 2026-08-16

- Deployed `instagram_company_dm_state`, `instagram_company_dm_send_log`, `instagram_company_dm_run`, and `instagram_inbound_reply_events` to the `n8n` database. The initial bootstrap accidentally targeted the container default database; `scripts/apply_instagram_company_dm_bootstrap.py` now explicitly targets `n8n`.
- Imported 412 populated source rows from the approved Google Sheet into 379 globally unique page candidates: 76 Partnerships, 245 Brands, and 58 Dispensaries. Global duplicate-handle count is zero.
- Source import workflow: `LT - Instagram Company Page Source Import` (`iQ80zfEH3JiulLNv`), inactive/unpublished, version `b66c1409-1d3a-415c-b064-d3dd0367903c`. Successful import execution: `757050`.
- Identity validator: `LT - Instagram Company Page Identity Validator` (`HpgL5E5CcHKqz7Oi`), inactive/unpublished, version `726bca16-007b-4ca4-83ce-75eb4e648f3e`. It uses documented Unipile fields only: exact `public_identifier`, `provider_id`, `provider_messaging_id`, `profile_type`, and `category`.
- Identity policy: `BUSINESS` can validate; `PERSONNAL` is rejected; `PROFESSIONNAL` requires review; username/provider mismatches and 404/422 resolution failures are rejected. Provider/retry errors remain fail-closed candidates.
- Controlled identity executions `757097`, `757106`, `757117`, and `757121` performed no send-capable action. Current result: 42 validated Partnerships, 12 review-required Partnerships, and 22 rejected Partnerships; Brand and Dispensary validation remains pending.
- Deterministic pool association linked 174 Brand pages to 689 GHL contacts and 47 Dispensary pages to 70 GHL contacts. This uses exact normalized company names and source-list boundaries.
- GHL Partnership association workflow: `LT - Instagram Company Page GHL Association` (`6ILxRR6ZAVngGPD1`), inactive/unpublished, version `fc2fe189-e91e-4dc5-bd67-462bede35941`. Execution `757138` fetched 130 already-tagged GHL contacts and exact-matched 26 Partnership pages to 34 contacts; 50 Partnership pages remain unresolved. It performs no GHL writes.
- Dry-run dispatcher: `LT - Instagram Company Page Message 1 Dispatcher (Dry Run)` (`1iEqGs5IxEuD5rrS`), inactive/unpublished, version `6a0482b9-a9c3-4f06-a443-3ff5d8caff00`. It has no provider POST/send action and hard-fails unless `dryRun=true` and `firstWeekMessage1Only=true`.
- Dry-run execution `757139`: 42 priority-ordered Partnership previews, 19 locally eligible after identity/association/local-ledger checks, 23 unassociated, zero sends. Every preview still requires a successful live GHL tag/conversation suppression check before it can become live-eligible.
- Five-send test workflow: `LT - Instagram Company Page Five Send Test` (`27NLAovEaClxCAuI`), inactive/unpublished, version `568130e2-f3df-4916-84ef-dae88575a7a0`. It is manual-only, lifetime-capped at five successful sends, daily-capped at 45, blocks weekends, reserves send idempotency before provider calls, checks every associated GHL contact for suppression tags and inbound conversations, and defaults back to `preflightOnly=true`.
- Preflight execution `758994` cleared exactly five Partnership pages with zero skips/errors and zero sends: Vaping360.com, Tricycle Day, TNMNews.com, MedicateOH & MedicateKY, and Marijuana Moment.
- Approved live execution `758995` sent zero messages. Unipile rejected all provider calls with HTTP 401 before message creation. The same stale credential also produced 20 retryable 401 profile lookups in identity execution `759001`, confirming an account-level access-token problem rather than recipient rejection.
- The 19 failed pre-send reservations from execution `758995` were removed only after confirming `providerAccepted=false` for every attempt. `instagram_company_dm_send_log` has zero successful test sends and the test workflow is back in preflight mode.
- Current blocker: generate a valid Unipile access token from the same dashboard/application as Instagram account `F2UprZ8aQc6Qm9CYYWU6cg`, and confirm the account remains connected. Do not retry live sends until both `GET /users/{identifier}` and the five-candidate preflight pass with the replacement token.
- Inbound reply branch in active `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`) persists/deduplicates replies, suppresses matching company state, and independently alerts Slack. Current active version: `6767c629-4a5a-47d3-be0a-1160de1700a6`.
- No company-level GHL custom fields were created or populated. Existing contact-level Instagram fields remain untouched.
- No live Instagram test or production send has been approved or performed.

## User Decisions

- Approved DM copy is final and must not be changed.
- The recipient is the company Instagram page, not the employee represented by the GHL contact.
- Use the existing Unipile Instagram connection: `F2UprZ8aQc6Qm9CYYWU6cg`.
- Instagram is phase one. Facebook Messenger is deferred to the native GHL Messenger path.
- Contacts may continue receiving DAN, Emerald, Partnership email, or LinkedIn outreach unless a reply/suppression rule blocks the social sequence.
- Any prior reply/response from any associated contact stops this social company-page sequence.
- Reply-check and identity-resolution errors fail closed and skip the send.
- Cadence: Message 1 on the first eligible weekday; Messages 2 and 3 two business days apart; never send weekends.
- Lifecycle is stored in Postgres. Do not add lifecycle tags.
- Test Instagram first; do not add Facebook delivery until its native GHL path is independently verified.

## Audience Selectors

| Campaign | GHL selector | Approved document |
|---|---|---|
| DAN Brands | `brands_pool` | `Instagram and FB DM - Dispensary Attribution Network (Brands).docx` |
| DAN Dispensaries | `dispensaries_pool` | `INSTAGRAM and FB DM - Dispensary Attribution Network (Dispensaries).docx` |
| Partnerships | `partner_candidate_email` OR `partner_candidate_linkedin` | `INSTAGRAM and FB DM - Partnerships Campaign.docx` |

The approved Google Sheet now supplies Partnership Instagram handles directly. Facebook remains ignored for phase one. GHL contact association is incomplete for 50 Partnership pages and remains a live-send blocker for those rows.

## Source Data Audit

Primary files:

- `data/Brands.csv`: 3,668 rows; 3,224 rows with Instagram URL occurrences; 2,799 with Facebook URL occurrences.
- `data/Dispensaries.csv`: 10,200 rows; 6,875 rows with Instagram URL occurrences; 6,431 with Facebook URL occurrences.
- `Partnership Marketing/Content Partnerships - Email - Consolidated List.csv`: no Instagram/Facebook URL fields.
- `Partnership Marketing/Content Partnerships - Linkedln - Consolidated List.csv`: no Instagram/Facebook URL fields.
- `Partnership Marketing/partnership_master.json`: partnership contact/tag data, no reliable company-page social URL source.

Relevant Brands/Dispensaries columns:

- `Company non-LinkedIn URL(s)`
- `Location non-LinkedIn URL(s)`
- `Contact non-LinkedIn URL(s)`
- `Company Name(s)`
- `Location Display Name(s)`
- `Emerald Contact ID`

The counts above are preliminary URL occurrences, not validated company-page counts. Normalize, deduplicate, reject malformed/unrelated URLs, and classify personal versus company pages before writing GHL or sending.

## GHL Field Contract

Existing contact-level Instagram fields are protected. They are used by the active inbound bridge and must not receive company-page values:

| Field | ID |
|---|---|
| Instagram Username | `8k6vF61VBIysdIXXFQD5` |
| Instagram Profile URL | `beGMXoidqHdYqAQDORWX` |
| Instagram Profile Provider ID | `fYYUrFLABP5l0w7RdK7Y` |
| Instagram Chat Attendee ID | `SQdQw0MNvk8uQbr4yDZU` |
| Instagram Chat ID | `ab6euY7qo5klhUSe7VWu` |

Create these eight new contact custom fields, all type `TEXT`, with exact names:

- `Company Instagram Username`
- `Company Instagram Profile URL`
- `Company Instagram Profile Provider ID`
- `Company Instagram Chat Attendee ID`
- `Company Instagram Chat ID`
- `Company Facebook Page URL`
- `Company Facebook Page ID`
- `Company Facebook Messenger PSID`

`Apollo Facebook URL` is contact-level Apollo data and must not be repurposed. `Company Facebook Page URL` and `Company Facebook Page ID` are reference/enrichment values only. A Facebook Messenger PSID may only be captured from an eligible native GHL Messenger interaction; never infer it from a public URL or Page ID.

## Matching and Enrichment Plan

Match source rows to GHL in this order:

1. Emerald Contact ID.
2. Source-file/import metadata.
3. Exact normalized email.
4. Exact normalized phone.
5. Company plus contact name as a review-only fallback.

The enrichment workflow must:

- Extract Instagram/Facebook URLs from company, location, and contact non-LinkedIn URL fields.
- Normalize URLs by removing protocol differences, `www`, tracking query strings such as `fbclid`, fragments, and trailing slashes.
- Extract the candidate Instagram username.
- Resolve the candidate through Unipile account `F2UprZ8aQc6Qm9CYYWU6cg`.
- Require an Instagram account-type/company-page validation signal.
- Reject personal, unrelated, ambiguous, duplicate-conflict, and unresolved profiles.
- Preserve original `Em_*Non_LinkedIn_URLs` source metadata.
- Update only the new `Company ...` fields after review approval.
- Produce explicit `matched`, `unresolved`, `ambiguous`, `personal_profile`, `conflict`, and `duplicate` outputs.

Multiple GHL contacts can map to one company page. Deduplicate by normalized handle plus Unipile account. Retain all associated GHL IDs and one primary attribution contact in Postgres. Do not use company-name fuzzy matching as an automatic write or send decision.

## Authoritative State

Create a dedicated Postgres identity/state model, proposed name `instagram_company_dm_state`. It must be separate from `instagram_conversation_map`.

Minimum state fields:

- `campaign_key`: `dan_brands`, `dan_dispensaries`, or `partnerships`.
- `platform`: `instagram`.
- Unipile account ID, profile/provider ID, normalized username, profile URL, chat attendee ID, and chat ID.
- Company name and source tag.
- Primary GHL contact ID and associated GHL contact IDs.
- `message_step`, `sequence_status`, `started_at`, `last_sent_at`, and `next_due_at`.
- Last platform message ID and message hash.
- Reply/suppression status and timestamps.
- Failure reason, resolution method/confidence, workflow run ID, and audit timestamps.

Recommended constraints:

```text
UNIQUE (campaign_key, unipile_account_id, instagram_profile_provider_id)
UNIQUE (campaign_key, instagram_profile_provider_id, message_step)
```

Use direct `require('pg')` transactions for state writes. Do not use n8n Postgres v2.5/v2.6 `queryReplacement` for this new persistence path because of the documented commit/binding defect.

## Eligibility and Suppression

Before Message 1, require:

- Correct audience tag.
- Validated company Instagram page.
- Validated Unipile profile/provider identity.
- No existing completed/active state for the same campaign/page.
- No previous Instagram inbound/reply evidence for the page.
- No prior reply from any associated GHL contact in relevant GHL, email, LinkedIn, or social state.
- No campaign/suppression condition on any associated contact.

Any reply from any associated contact sets the company-page state to `replied`, records `reply_detected_at`, clears `next_due_at`, and prevents future social sends. A company-page reply suppresses this social sequence; it does not automatically stop independent email or LinkedIn campaigns unless those systems have their own reply evidence.

## Live Infrastructure to Reuse

- Unipile Instagram account: `F2UprZ8aQc6Qm9CYYWU6cg`.
- Active inbound bridge: `LT - Instagram Unipile New Messages` (`pISlgYUsyJIrLuJd`), webhook `/webhook/lt-unipile-instagram-new-messages`.
- Active GHL custom provider: `Instagram via Unipile`, ID `6a58a1193cdfc36997580a68`.
- Active outbound router: `LT - Social Provider Outbound Router` (`kqIi8i1RjFAZKrK3`), webhook `/webhook/lt-social-provider-outbound`.
- Existing contact-level map: `instagram_conversation_map`.
- Existing GHL inbound bridge posts `type: "Custom"` with `conversationProviderId` and `altId`; do not add dummy phone/email values.

Do not republish `LT - Instagram DM Sequence (Unipile)` (`iCnY6ccdHhfJg3sf`). It used the LinkedIn Unipile account and old `instagram_dm_state` model, and it is not a company-page sender.

## Implementation Sequence

1. Fetch live GHL custom-field state and confirm none of the eight exact field names already exist.
2. Build read-only source extraction, matching, normalization, and review outputs.
3. Review representative company-page classifications and unresolved/conflict samples.
4. Create the eight GHL company-level fields.
5. Resolve approved company Instagram profiles through Unipile.
6. Update only the new company fields and preserve existing contact-level fields.
7. Create/import `instagram_company_dm_state` with direct-`pg` persistence.
8. Build the shared scheduled dispatcher with campaign-specific templates and exact approved copy.
9. Run a five-page dry-run sample for Brands and Dispensaries.
10. Obtain explicit approval and run one controlled live Instagram test per campaign.
11. Verify profile/chat/message IDs, GHL mapping, state persistence, idempotency, and reply suppression.
12. Publish and activate the weekday dispatcher only after all gates pass.

No production send has been approved or performed for this workstream as of this handoff.

## Non-Negotiable Guardrails

- Do not change the approved message text.
- Do not send to personal Instagram profiles.
- Do not repurpose existing contact-level Instagram fields.
- Do not infer a Facebook Messenger PSID from a public Facebook URL/Page ID.
- Do not use `instagram_conversation_map` as campaign state.
- Do not manually execute any live sender without explicit approval.
- Fetch live state before every mutation and verify state after it.
- After workflow mutation, verify `versionId == activeVersionId`; publish if necessary.
- Preserve unrelated dirty-worktree changes.
- Do not commit secrets, tokens, captured credential-bearing responses, or source artifacts containing secrets.
