# SDR Registry And Routing Contract

## Purpose

Make SDR onboarding data-driven instead of requiring workflow edits, template copies, or hardcoded names. This is a design contract only until the authoritative qualification and Sales Outreach promotion workflow is confirmed.

## Canonical Registry

Maintain one active SDR record per GHL user:

| Field | Purpose |
|---|---|
| `ghl_user_id` | Native GHL owner ID and primary key |
| `display_name` | Human-facing name |
| `email` | Sender and reply identity |
| `phone` | Human follow-up number |
| `email_signature` | Rendered signature or GHL user signature reference |
| `vapi_assistant_id` | Optional voice assistant mapping |
| `calendar_id` | Optional booking calendar mapping |
| `active` | Whether the SDR receives new assignments |
| `routing_weight` | Relative allocation weight; default `1` |
| `routing_version` | Prevents retries from changing historical assignments |

The registry must use GHL user IDs, not display names or email addresses, for ownership decisions.

## Routing Rules

1. Do not assign SDRs during ordinary Warm intake or channel micro-automations.
2. Resolve ownership only when the authoritative qualification workflow promotes a record to `Sales Outreach -> New`.
3. If only one of contact owner or opportunity owner exists, align the missing owner.
4. If both owners match, preserve the assignment.
5. If owners conflict, flag the conflict and do not overwrite automatically.
6. If neither owner exists, select from active registry members using a transactional weighted round-robin or deterministic contact-ID hash.
7. Persist the decision before any SDR-specific outbound action.
8. Retries and webhook replays must return the existing assignment and must not consume another allocation slot.

## Identity Resolution

Every outbound channel should resolve the assigned GHL user ID through the registry immediately before sending:

- Email: assigned-user merge fields or a verified owner-specific sender configuration.
- SMS: owner-specific message identity, sender label, and reply routing.
- Vapi: owner metadata and prompt variables; transfer and booking remain separate concerns.
- LinkedIn/Instagram: owner for notification and follow-up, independent of the shared transport account.
- Reporting: owner ID, display name, assignment source, and routing version.

If the owner is missing, inactive, or absent from the registry, fail closed for SDR-specific outbound actions and create an operational error rather than falling back to a hardcoded rep.

## Adding An SDR

1. Create and verify the GHL user, permissions, email, phone, signature, and calendar access.
2. Add one active registry row with a routing weight.
3. Configure optional Vapi assistant and booking mappings.
4. Run owner, sender, signature, reply, and reporting smoke tests.
5. Enable the row only after the qualification-to-Sales-Outreach promotion path is confirmed.
6. Do not edit every workflow or duplicate every template for the new SDR.

## Required Audit Fields

Store the following on the assignment event or routing log:

- Contact ID
- Opportunity ID, when present
- Previous contact owner
- Previous opportunity owner
- Assigned GHL user ID
- Assignment source and trigger
- Routing version
- Idempotency key
- Assignment timestamp
- Conflict or fallback reason

## Current Status

- The six Jason-named email templates now use `{{user.email_signature}}` and no longer hardcode the signature body.
- The six template names remain Jason-specific to preserve existing sequence references; renaming them is a separate migration.
- Live `Jason Followup Emails and SMS` (`f6b44e34-779e-4959-b41d-b05641f134e7`) remains published at version 38. Authenticated inspection confirmed all 7 Send Email actions already use owner-driven sender fields: `From Name = {{opportunity.owner}} from Transparent eCom` and `From Email = {{user.email}}`.
- The six templates in `Jason Follow Up Emails` still use `Jason from Transparent eCom <jason@livetransparent.com>` as literal fallback metadata. The remaining requirement is to verify or set Jason as the workflow-level fallback user in the UI. The template API rejects merge fields in `fromEmail`, so no template metadata change is needed.
- DAN, Emerald, and other marketing templates still contain Cameron-specific signatures/sender configuration. They appear to be campaign-brand identity rather than SDR-owner identity, but that boundary must be explicitly confirmed before changing them.
- SimpleTexting and some social/Vapi paths still contain channel-specific identity or compatibility literals and are not yet registry-driven.
- The published `LT - Opportunity Owner Alignment` workflow (`b26326a5-77af-4df8-8d86-3f636e73afe0`, version 7) synchronizes contact owner, opportunity owner, custom opportunity owner, and routing audit fields for Jason and Marc. This is owner alignment, not a generic qualification allocator.
- The live qualification source and promotion result contract are still unresolved.
- Existing active workflows still contain channel-specific identity assumptions and must be migrated to this registry before a third SDR is activated.

## Opportunity Owner Synchronization Contract

When an opportunity owner changes, the canonical sync must update these fields together:

1. Contact native owner: `contact.assignedTo` set to the selected GHL user ID.
2. Opportunity native owner: `opportunity.assignedTo` set to the same GHL user ID.
3. Opportunity custom owner: `opportunity.owner` (`Wpg7FGrQTgAY1GoKcdEJ`) set to the canonical SDR display name.
4. Contact routing timestamp: `LT Last Routed At` (`aJ3LMhy5fZzh10WoykZ6`) set to the synchronization time.
5. Contact routing reason: `LT Last Routing Reason` (`FQv9wyl2JrMkpf1GPprP`) set to the owner-sync reason.
6. Contact routing channel: `LT Last Routing Channel` (`IPzJpFLekz9TDi4nWBaV`) set to the source event/channel.

The existing `LT - Micro - Email Open Counter + Assignment to Jason` workflow is not a complete implementation of this contract: its published branches hardcode opportunity custom-owner values (`Jason` and `John`) and do not update the native contact owner. The `Email Open 3x - Assigned Kevin` tag is a campaign guard, not an authoritative owner field, and should not be used as the owner source of truth.
