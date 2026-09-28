# SimpleTexting SMS/MMS Routing Closeout — 2026-09-24

## Outcome

The live SimpleTexting path now classifies GHL provider outbound messages from `attachments[]`. Text-only messages remain SMS; one hosted HTTPS attachment requests MMS; an MMS provider rejection is converted into one SMS containing the hosted media link.

## Live changes

- `LT - SimpleTexting SMS Send (Webhook, Staged)` (`Q3Ivnwe4z2Y3cD7A`), active version `47de44fe-d1bf-4f3d-8040-a70f759466a1`:
  - accepts `attachments`, `mediaItems`, or `media_items`;
  - validates HTTPS media URLs and rejects multiple attachments in v1;
  - forwards `media_items`, `mode`, and `fallback_text` to the idempotent boundary;
  - mirrors successful media URLs into GHL Conversations.
- `LT - SimpleTexting Provider Outbound Router` (`f4VoO1lBWkYRcQai`), active version `444e2709-b6c1-4e61-9087-2e79387e8648`:
  - carries GHL provider attachments through the canonical send route;
  - preserves provider validation, GHL suppression, E.164 normalization, and response classification.
- `LT - SMS Idempotent Send` (`gwaEpWDpTIwsafi8`), active version `52eefd2a-70be-41c9-a60a-2fce0f037929`:
  - includes media URL, mode, and fallback text in the dedupe hash;
  - calls SimpleTexting with `MMS_PREFERRED` plus `mediaItems`;
  - attempts one `AUTO` URL-bearing SMS only when the MMS request fails;
  - persists the provider response with delivery-mode and fallback metadata.

## Verification

- Exact pre-change workflow definitions were backed up as `local-archive/n8n/workflows/*-before-simpletexting-mms-20260924T112004Z.json`.
- All three workflows are active and `versionId == activeVersionId`.
- Live dry-run checks passed for text-only, one attachment, and two-attachment rejection.
- Python compilation, wrapped n8n JavaScript syntax checks, and `git diff --check` passed.
- No provider API send, live MMS, fallback send, campaign activation, or sender schedule change was performed.

## Remaining validation

An explicitly approved internal live test is still needed to confirm whether the current SimpleTexting account accepts the media payload as MMS. If it rejects the request, inspect the same execution for the `SMS_LINK_FALLBACK` result and provider message ID.
