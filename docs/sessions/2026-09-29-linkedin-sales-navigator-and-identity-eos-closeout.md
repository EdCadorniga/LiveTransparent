# LinkedIn Sales Navigator and Identity EOS Closeout — 2026-09-29

## Objective

Use the personal LinkedIn provider name for personal LinkedIn outreach, mirror outbound LinkedIn activity into GHL Conversations, and prepare a safe transition of campaign messaging to LinkedIn Sales Navigator while excluding Cameron's personal and hiring conversations.

## Completed

- Confirmed Alexis Mora's authoritative GHL record: contact `RGjMxzMqOR2L14ao8qmg`, `firstName=Alexis`, company `A.MORA Marketing`, email `alexis@amoramarketing.co`, and LinkedIn URL `alexistaylormora`.
- No authoritative source was found for the historical `Angel` greeting. It may have come from stale/provider data or an earlier bad value; the original execution evidence is not available.
- Personal LinkedIn connection dispatcher now requires a non-empty LinkedIn provider first name and uses that name for outbound copy instead of GHL's first name.
- Personal LinkedIn DM sequence now requires a non-empty provider first name and uses it for outbound copy.
- Partnership/company LinkedIn paths remain GHL-based and were not changed by the personal-name preference.
- Outbound mirror helpers were moved to top-level Code-node scope after catching an insertion defect during review.
- Outbound mirrors use `/conversations/messages`; the inbound bridge continues to use `/conversations/messages/inbound`.
- Published live workflow versions, each verified by REST readback with `versionId == activeVersionId`:
  - Personal dispatcher `fXxw5lanZcDmUrst`: `ca663633-143f-4312-9cc3-d0a4ac262661`
  - Personal DM sequence `d0tEtijajisIsYcs`: `96f7cf60-97c2-4f35-ba13-20ebf9d49ef1`
  - Partnership dispatcher `crKIsaL5k3YBfqDZ`: `44c4ed5f-d5e3-4c75-94f0-1ac21cd7355e`
  - Partnership DM sequence `nspggypNF245xzeL`: `9c04b07a-812d-4755-850d-125cadec8c7a`
- Researched official Unipile documentation. Sales Navigator linking is selected in the Hosted Auth configuration (`products: ["classic", "sales_navigator"]`), not by choosing an API version in Cameron's browser screen. Sales Navigator uses provider recipient IDs beginning `ACw...`; Unipile v2 account IDs begin `acc_...`; `li_a` is a premium LinkedIn cookie used only for cookie authentication.

## Not Done / Acceptance Boundary

- No live LinkedIn invitation or DM was sent.
- No historical reconciliation or backfill was run for Alexis or the broader LinkedIn population. Missing DM-sequence messages, connection requests, and connection approvals still need a scoped, deduplicated import.
- The current Unipile connection is legacy `/api/v1` with a non-`acc_...` account ID. Read-only attempts to use the documented v2 inbox endpoint did not establish v2 access. Do not switch production routing until a Sales Navigator-capable v2 account and `SALES_NAVIGATOR_PRIMARY` inbox are verified.
- Cameron's personal and hiring conversations are not yet classified by a durable allowlist/exclusion model. Do not infer personal status from message text with AI.
- No Unipile account registration or Hosted Auth link was created during this session. Cameron must complete authentication directly in Unipile; do not request or store `li_at`, `li_a`, cookies, or API secrets in project artifacts.

## Next Steps

1. Generate a Unipile Hosted Auth link with `products: ["classic", "sales_navigator"]` using the correct Unipile application/API context, or have Unipile support migrate/provision the account.
2. Have Cameron authenticate directly in Hosted Auth. Preserve the existing Classic connection until the new account is verified.
3. Read-only verify the returned `acc_...` account, `SALES_NAVIGATOR_PRIMARY`, Sales Navigator chat history, and `ACw...` recipient resolution.
4. Add campaign-only routing metadata and a durable personal/hiring exclusion list before changing outbound senders.
5. Change new campaign conversations to the Sales Navigator inbox-start endpoint with a required subject; use existing chat IDs for follow-up messages.
6. Build a read-only historical candidate report, then import only missing canonical DM-sequence, connection-request, and connection-approval records after explicit scope review.
7. Run one approved non-broad live test only after the account and routing checks pass.

## Repository State

- New local scripts include `scripts/linkedin/audit_live_linkedin_send_nodes.py`, `scripts/linkedin/patch_live_linkedin_identity_conversations.py`, `scripts/linkedin/prefer_personal_linkedin_first_name.py`, `scripts/linkedin/repair_live_linkedin_mirror_scope.py`, `scripts/linkedin/repair_outbound_mirror_endpoint.py`, and `scripts/linkedin/repair_live_linkedin_mirror_endpoint.py`.
- The worktree contains unrelated pre-existing changes and untracked artifacts. Do not stage the entire worktree; stage only intended LinkedIn scripts or documentation after review.
- `git diff --check` passed with existing LF-to-CRLF warnings only.
