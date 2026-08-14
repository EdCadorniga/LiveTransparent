# Session Handoff: Company Instagram Page DM Delivery

Updated: 2026-08-14

`repomix-output.md` was not regenerated in this session because the `packlive` command was unavailable in the current PowerShell environment. Treat the handoff and the four linked documentation files as the authoritative session record until a later session successfully refreshes the repomix artifact.

## Next Agent: Start Here

This session completed planning and documentation only. No GHL custom fields, Postgres tables, contacts, or outbound workflows were created or mutated for this workstream. The next agent should implement the company-page enrichment and Instagram delivery plan, not republish the old Instagram sender.

1. Read `repomix-output.md`, `AGENTS.md`, this handoff, `plan.md`, and the first 180 lines of `Project Status and Next Steps.md`.
2. Read `docs/strategy/unipile-ghl-bidirectional-integration.md`, especially `Company Instagram Page Outreach Contract (2026-08-14)` and the existing inbound/outbound bridge sections.
3. Fetch live state before mutation: GHL contact custom fields, existing Instagram mappings, active Unipile/GHL bridge workflows, and current workflow versions. Live n8n is the source of truth; repository workflow snapshots may be stale.
4. Build the read-only source extraction/matching/review step first. Do not start with a sender workflow or live message.
5. Ask for explicit approval before any live Instagram test or production send.

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

Partnership source files currently do not contain reliable Instagram/Facebook URL fields and require separate enrichment before activation.

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
