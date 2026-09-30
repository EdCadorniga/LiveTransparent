# EOS Closeout — LinkedIn Inbound Duplicate Contact Race

Date: 2026-09-30
Status: Workflow patch published; runtime verification and CRM reconciliation remain open.

## Objective

Investigate duplicate Ian Lange contacts in GHL and fix the LinkedIn inbound workflow so concurrent events for one LinkedIn identity do not create multiple contacts.

## Confirmed cause and impact

The two records `qYSqY56e0UHPTjqUUTiG` and `DcBoUBEiNrC1Zh0sWg0M` have the same name, LinkedIn profile URL/provider identity, source, tags, and location. They were created at `2026-09-29T22:12:50.852Z` and `2026-09-29T22:12:51.270Z`.

Executions `1068352` and `1068355` processed two distinct inbound events for the same LinkedIn profile/chat, 585 ms apart. Both saw `mapped_ghl_contact_id=null` and returned `contact_resolution=created_new_contact`. The first event was attachment-only; the second carried Ian's full message. The contact mapping was written after GHL contact creation, leaving a race window.

Each contact now has a separate open opportunity: `VrFHG3ljyiLYL3eh0emV` belongs to `qYSqY56e0UHPTjqUUTiG`; `ASSrfoX1boNTMnggZySZ` belongs to `DcBoUBEiNrC1Zh0sWg0M`. Read-only inspection found the full message on `DcBo...` and the attachment-only event on `qYSq...`. Neither contact, opportunity, nor conversation was changed during this work.

## Live change

Workflow `LT - LinkedIn Unipile New Messages` (`7o5EBdvwAuIaWW7k`) now claims a unique Postgres identity row keyed by normalized LinkedIn provider ID (profile URL fallback) before contact resolution.

- One concurrent execution owns a newly inserted identity claim.
- A competing execution waits for an existing contact and reuses it; timeout returns an error without creating a second contact.
- The owner resolves the claim to its contact in the existing map-upsert step. Errors without a contact release the owner claim. Unfinished claims can be reclaimed after five minutes.
- Published active version: `b9dbffa7-79fc-408d-9d40-7a999a0f2ccc`; final read-only GET confirmed `active=true` and `versionId == activeVersionId`.
- Modified nodes: `Build Lookup Map SQL`, `Create LinkedIn Contact and Add Inbound Message`, and `Build Upsert Map SQL`.

## Verification limits

The live workflow was re-read after publication. Its claim table SQL, wait timeout branch, claim update SQL, inbound-message path, and active/published version were confirmed present. No live Unipile event or GHL message was triggered.

An attempted local JavaScript syntax check was rejected by command policy. No syntax test was accepted, and no execution has exercised the claim behavior. Treat the fix as published but not runtime-verified until an isolated verification covers claim owner, concurrent waiter, reuse, create failure, and stale-claim recovery without sending LinkedIn messages or creating uncontrolled CRM data.

## Security follow-up

The earlier execution inspection returned credential material in saved node output, and the live workflow's contact node has a hardcoded GHL credential. Do not copy credentials into artifacts. Treat the exposed values as compromised: rotate/revoke affected GHL credentials, replace workflow literals with the approved credential mechanism, and inspect whether saved execution data can be pruned safely. Do not record secret values in this handoff.

## Next session order

1. Rotate/revoke exposed GHL credentials and remove hardcoded credential literals from the workflow; verify all affected workflow paths after replacement.
2. Perform offline SQL and JavaScript validation. Design an isolated, controlled claim verification that cannot send LinkedIn messages or create additional production contacts; inspect each claim transition.
3. Review Ian's two conversation histories and select the canonical contact. Then reconcile the two opportunities and any mappings/ledgers before asking to merge or remove records.
4. Re-read the workflow's active version and inspect a safe verification execution before declaring the duplicate-creation fix runtime-accepted.

Do not trigger a live LinkedIn event, merge/delete either contact, or close/remove either opportunity without explicit approval. Preserve existing local worktree edits; do not stage unrelated changes.
