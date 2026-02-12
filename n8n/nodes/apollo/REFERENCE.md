# Apollo Node Reference (Workflow Test)

This reference tracks the 10 Apollo.io HTTP Request nodes added to n8n workflow `Workflow Test` (`X2QOdM9xh2rFokps86sGQ`).

## Runtime Notes
- n8n version observed: `2.6.4`
- Node used: `n8n-nodes-base.httpRequest`
- Node `typeVersion`: `4.4`
- All Apollo nodes are currently `disabled: true`
- Auth header expression used:
  - `Bearer {{$env.APOLLO_API_KEY || $json.apollo_api_key || ''}}`

## Node Map
1. `Apollo 01 - People API Search`
   - `POST https://api.apollo.io/api/v1/mixed_people/api_search`
2. `Apollo 02 - People Enrichment`
   - `POST https://api.apollo.io/api/v1/people/match`
3. `Apollo 03 - Bulk People Enrichment`
   - `POST https://api.apollo.io/api/v1/people/bulk_match`
4. `Apollo 04 - Organization Search`
   - `POST https://api.apollo.io/api/v1/mixed_companies/search`
5. `Apollo 05 - Organization Enrichment`
   - `GET https://api.apollo.io/api/v1/organizations/enrich?domain=...`
6. `Apollo 06 - Bulk Org Enrichment`
   - `POST https://api.apollo.io/api/v1/organizations/bulk_enrich`
7. `Apollo 07 - Search Contacts`
   - `POST https://api.apollo.io/api/v1/contacts/search`
8. `Apollo 08 - Create Contact`
   - `POST https://api.apollo.io/api/v1/contacts`
9. `Apollo 09 - Search Accounts`
   - `POST https://api.apollo.io/api/v1/accounts/search`
10. `Apollo 10 - Add Contacts to Sequence`
   - `POST https://api.apollo.io/api/v1/emailer_campaigns/{sequence_id}/add_contact_ids`

## Source Docs
- https://docs.apollo.io/reference/people-api-search
- https://docs.apollo.io/reference/people-enrichment
- https://docs.apollo.io/reference/bulk-people-enrichment
- https://docs.apollo.io/reference/organization-search
- https://docs.apollo.io/reference/organization-enrichment
- https://docs.apollo.io/reference/bulk-organization-enrichment
- https://docs.apollo.io/reference/search-for-contacts
- https://docs.apollo.io/reference/create-a-contact
- https://docs.apollo.io/reference/search-for-accounts
- https://docs.apollo.io/reference/add-contacts-to-sequence
