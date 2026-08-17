# Executive Report Social Accuracy - 2026-08-17

## Scope

Audit GHL Social Planner placements, account-statistics availability, LinkedIn/Instagram outreach ledgers, live state distributions, and Executive Report presentation. No outbound social messages were sent.

## Verified Sources

- Official GHL Social Planner post API for `2026-08-10` through `2026-08-16`.
- `report_raw_ghl_social_posts`, refreshed by `LT - GHL Daily Social Ingest`.
- `linkedin_connection_state` plus `partnership_linkedin_connection_state`.
- `linkedin_activity_events` and `instagram_activity_events`.
- Executive Summary and Campaign Channel public report APIs.

## Findings

1. The report's 8 social rows were correct but ambiguously labeled as posts. They are platform/account placements: 6 LinkedIn and 2 Instagram. The official GHL post API returns the same 8 IDs and the same 3 total likes.
2. Reach, impressions, and saves were serialized as zero even though the post payloads do not contain those fields. Zero incorrectly implied measured account analytics.
3. LinkedIn `requestedCount` counted only status `requested` and omitted 1,245 atomically claimed `requested_pending` rows. Live state also contains 100 `follower_messaged` rows that were not visible in the snapshot.
4. The active OAuth row contains an empty access token. PIT access cannot call the statistics endpoint. An exact-range OAuth workflow could not be made reliable and was unpublished and archived rather than serving cached values.
5. The social ingest used an old GHL API version, fetched only GHL's default 10-post page, and always reported zero processed rows because Postgres output items contain `{success:true}` rather than the original `post_id`. This left older engagement values stale; the initial 30-day comparison showed 15 report likes versus 18 from GHL.

## Applied Fixes

- Executive Summary `Bukc0mgOD2r7V6ED`, version `bc4856aa-e640-4477-a9fc-3ed14ae53707`:
  - Adds `countBasis: platform_placements` and `engagementBasis: latest_post_ledger`.
  - Returns null for saves/reach/impressions when their source keys are absent.
  - Adds source freshness timestamps and `statisticsAvailable`.
  - Groups `requested` plus `requested_pending` into Requested while preserving both subcounts.
  - Adds `followerMessagedCount` and `otherStateCount`.
- Social ingest `QZoqCaTwDhbym80O`, version `2ed24c59-1fc8-40ae-bdb0-aba9744a37a1`:
  - Uses API version `2021-07-28`.
  - Paginates all placements in the supported 366-day report horizon in 100-row pages.
  - Throws on provider fetch failure instead of routing an error item into the Postgres upsert.
  - Refreshes all mutable post fields on conflict.
  - Reports the actual number of successful upserts.
- Executive Report build `2026-08-17-v26-social-reporting-accuracy`:
  - Labels counts as placements and ledger engagement.
  - Renders missing account statistics as N/A.
  - Displays LinkedIn Requested, Follower Messaged, and Total State Rows.
  - Clarifies snapshot versus selected-window ledger semantics.
  - Contains long labels and wide tables without page-level mobile overflow.

## Verification

- Social ingest manual execution `759065`: success, 229 posts refreshed; 250 total historical rows retained.
- Live 7-day Executive Summary:
  - Placements 8; published 8; LinkedIn 6; Instagram 2; likes 3.
  - Saves, reach, impressions: null.
  - LinkedIn Ready 10,469; Requested 1,365; Connected 2,040; Follower Messaged 100; Total 13,977.
  - Selected-window LinkedIn requests 2; replies 2; unique responders 2.
  - Instagram ledger DMs/replies/events 0/0/0 with explicit ledger coverage.
- Live 30-day Executive Summary now matches the official GHL post API: 23 placements, 18 likes, 0 comments, 1 share, 3 failed; platform counts are Facebook 2, Instagram 6, LinkedIn 15.
- The 90-day preset and exact custom-window request both returned HTTP 200 with the same null-safe metric contract.
- Browser verification at 1440px and 390px: all Executive Report API calls returned HTTP 200, no console errors, and no page-level horizontal overflow.

## Remaining Blocker

Reconnect a valid GHL agency OAuth credential and persist a non-empty active token before adding exact-range account reach, impression, and save analytics. Until then, N/A is the authoritative report value.
