# Executive Report MQL & Account Statistics - 2026-08-17

## Scope

Resolve user feedback on the Executive Report MQL panel (Total MQLs, MQLs converted to SQL, Current MQLs) and enable account-level social reach/impressions after confirming the Instagram reconnect state. No outbound social messages were sent.

## Instagram Reconnect Answer

- The GHL Social Planner Instagram account `transparent.ecom` is connected and healthy: `isExpired=false`, `hasStatisticsPermissions=true`, expires 2026-10-13, refreshed 2026-08-17 04:35.
- The current GHL PIT now authenticates `POST /social-media-posting/statistics` (it returned 401 on 2026-08-04). This unblocked account statistics without needing the previously empty GHL OAuth token row. Verified 7-day: 60 impressions, 11 reach, 14 likes for Instagram; 30-day all-platform: 1,821 impressions, 4,018 reach.

## MQL Feedback

- Before: the panel showed `Active MQLs = Total MQLs = 137` for both 7d and 30d because it counted only snapshots of the Warm Qualified (MQL) stage and ignored that some had moved on.
- Actual live breakdown (opportunity snapshots in `report_raw_ghl_opportunities`):
  - Total MQLs (ever in Warm Qualified (MQL), stage `3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2` in pipeline `FRjpDZ1HWj3UPgczsu3t`): 137
  - Converted to SQL (also entered Sales Outreach pipeline `dhdlf3O4tymxFtHk4aqq`): 48
  - Current MQLs awaiting sales (never in Sales Outreach): 89
  - 30-day window: 119 entered MQLs, 44 converted; 7-day window: 0 entered, 0 converted.

## Implementation

- **Table**: `report_ghl_social_statistics` added to `postgres/reporting-bootstrap.sql` and created in the report `postgres` database (the `n8n` database also briefly held a copy; that copy was dropped after the ingest was repointed). Columns: window_start, window_end, scope (`all` or platform), platform, posts, likes, followers, impressions, reach, comments, saves, source, loaded_at. Unique on (window_start, window_end, scope).
- **Workflow**: `LT - GHL Social Statistics Ingest` (`veg9jbN1P67Xmqy8`, active version `bee234fb-5234-4fb4-88e9-4dd611b937fb`). Daily 06:00 America/Los_Angeles, Config node holds the GHL PIT, `Fetch Statistics` calls `/social-media-posting/statistics` for completed 7/30/90-day windows (profileIds from the connected accounts), `Write Statistics` upserts rows via direct `pg` to the `postgres` database. Verification execution `760249` stored 12 rows.
- **Executive Summary** (`Bukc0mgOD2r7V6ED`, version `e4fa3d18-1a61-47db-b255-d34e20051d7f`):
  - `socialPosts` CTE now reads `report_ghl_social_statistics` for the selected window and returns `totalReach`, `totalImpressions`, `accountPosts`, `accountLikes`, `accountFollowers`, `accountComments`, `statisticsAvailable`, and `statisticsAsOf`. `totalSaves` stays null (endpoint does not return saves).
  - `mqlSummary` CTE replaced with `mql_keys` (ever MQL), `mql_first` (first MQL date), `mql_conversion` (first Sales Outreach date), and `mql_summary` returning `totalMqls`, `totalEver`, `convertedToSql`, `currentMqls`, `awaitingSales`, `active`, `enteredMqls`, `convertedThisPeriod`, `asOfDate`.
- **Frontend** build `2026-08-17-v27-social-mql`: MQL panel now shows Total MQLs, MQLs Converted to SQL, Current MQLs (awaiting Sales), Entered This Period, Converted This Period; Social panel labels reach/impressions/posts/likes/followers as GHL account statistics. Small-screen `overflow-x: clip` guard added.

## Verification

- 7-day API: placements 8, reach 45, impressions 159, account posts 4; MQL 137/48/89, entered 0, converted 0.
- 30-day API: placements 23, reach 4,018, impressions 1,821, account posts 10; MQL 137/48/89, entered 119, converted 44.
- Browser at 1440px and 390px: all report API calls HTTP 200, no console errors, no page-level horizontal overflow.

## Note

The statistics endpoint groups longer ranges by week and returns rolled-up window totals; the ingest stores exact completed-window totals for the 7/30/90-day presets. Custom ranges without an exact stored window return N/A for account statistics rather than fabricated values.
