# Apollo C-Suite and Marketing September 2026 GHL Import Closeout

Date: 2026-09-17

## Scope

Reconcile the Apollo VP contact batch from `Apollo_VP_Contacts.csv`, apply the required tag, and create missing opportunities in GHL. No broad GHL CSV import was initiated by the assistant; the operator performed the prepared CSV imports. The assistant performed the later direct tag/upsert reconciliation and opportunity creation requested in chat.

Location: `Zwz4relUXVPxx8uohnjV`

Required tag: `Apollo_CSuite_and_Marketing_Sep2026` (GHL displays the normalized lowercase form on contact records.)

## Contact preparation and import history

- Source contained 485 rows.
- Eight exact-email matches were identified during preparation; 477 rows were placed in the new-contact import candidate.
- The initial GHL import log reported 445 successes and 32 phone-in-use errors. The 32 collision rows were prepared with `Phone` blank and the original number moved to `Em_All_Known_Phones`, then successfully retried by the operator.
- A later 121-row email/tag-only update import did not produce the expected tag count. Generic GHL tag search showed 364 contacts at the start of this closeout, not the expected source cohort.
- The assistant directly reconciled 114 source emails that were absent from the tag-search result using email-based GHL upserts, omitting phone values to avoid recreating phone-collision errors. All 114 upserts returned contact IDs and were tagged successfully; the operation log reports zero errors.
- GHL’s aggregate tag search remained incomplete/lagging after the direct updates and reported 395 contacts on the final check. This is a search/list count, not proof that the full source cohort is absent from contact records.

## Opportunity creation

The requested pipeline and stage were resolved live:

- Pipeline: `Sales Outreach` — `dhdlf3O4tymxFtHk4aqq`
- Stage: `New` — `3529dd3d-cab0-4279-967c-1aea203de4fb`

For the 395 contacts currently returned by the tag search, the idempotent opportunity pass searched for any existing opportunity before creating one:

- 361 contacts have an opportunity in `Sales Outreach -> New`.
- 25 contacts already had an opportunity elsewhere and were left unchanged, consistent with the “if one does not exist yet” instruction.
- Nine transient 400 responses were caused by concurrent creation races; follow-up contact-specific searches confirmed those contacts already had the requested `Sales Outreach -> New` opportunity.
- No duplicate opportunities were created by the final reconciled state.

Opportunity audit log: `data/runs/2026-09-16-apollo-vp-ghl/apollo_tag_opportunity_create_log.csv`

## Relevant artifacts

- Prepared new-contact CSV: `data/runs/2026-09-16-apollo-vp-ghl/Apollo_VP_Contacts_Sep2026_GHL_New_Contacts_Import.csv`
- Phone-collision retry CSV: `data/runs/2026-09-16-apollo-vp-ghl/Apollo_VP_Contacts_Sep2026_GHL_Phone_Collision_Retry.csv`
- 114-contact direct upsert log: `data/runs/2026-09-16-apollo-vp-ghl/apollo_114_upsert_log.csv`
- Opportunity creation log: `data/runs/2026-09-16-apollo-vp-ghl/apollo_tag_opportunity_create_log.csv`
- Opportunity creation script: `local-scripts/create_apollo_tag_opportunities.ps1`

## Remaining caveat

The GHL contact tag search does not currently return the full 476 email-bearing source rows. Do not use the visible tag count alone as a complete source-cohort reconciliation. If the remaining contacts must be recovered, perform a separate exact-email/contact-ID reconciliation and review any records that are not addressable by the GHL contact APIs before creating additional opportunities.
