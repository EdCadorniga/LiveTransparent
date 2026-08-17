"""Apply the audited social reporting definitions to the live Executive Summary."""

from fix_executive_report_metrics import WORKFLOW_IDS, node_map, request, update_workflow


SOCIAL_POSTS_CTE = r"""social_posts AS (
  SELECT jsonb_build_object(
    'countBasis', 'platform_placements',
    'engagementBasis', 'latest_post_ledger',
    'statisticsAvailable', COUNT(*) FILTER (WHERE
      insights ?| ARRAY['saves', 'save', 'reach', 'impressions']
      OR payload_json ?| ARRAY['saves', 'save', 'reach', 'impressions']
      OR COALESCE(payload_json->'insights', '{}'::jsonb) ?| ARRAY['saves', 'save', 'reach', 'impressions']
    ) > 0,
    'totalPosts', COUNT(*)::int,
    'facebookCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'facebook')::int,
    'instagramCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'instagram')::int,
    'linkedinCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'linkedin')::int,
    'publishedCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(status, '')) = 'published')::int,
    'failedCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(status, '')) IN ('failed', 'error'))::int,
    'totalLikes', COALESCE(SUM(COALESCE(NULLIF(insights->>'likes', '')::int, NULLIF(insights->>'like', '')::int, 0)), 0)::int,
    'totalComments', COALESCE(SUM(COALESCE(NULLIF(insights->>'comments', '')::int, NULLIF(insights->>'comment', '')::int, 0)), 0)::int,
    'totalShares', COALESCE(SUM(COALESCE(NULLIF(insights->>'shares', '')::int, NULLIF(insights->>'share', '')::int, 0)), 0)::int,
    'totalSaves', CASE WHEN COUNT(*) FILTER (WHERE
      insights ?| ARRAY['saves', 'save'] OR payload_json ?| ARRAY['saves', 'save']
      OR COALESCE(payload_json->'insights', '{}'::jsonb) ?| ARRAY['saves', 'save']
    ) > 0 THEN COALESCE(SUM(COALESCE(
      NULLIF(insights->>'saves', '')::int, NULLIF(insights->>'save', '')::int,
      NULLIF(payload_json->>'saves', '')::int, NULLIF(payload_json->>'save', '')::int,
      NULLIF(payload_json->'insights'->>'saves', '')::int, NULLIF(payload_json->'insights'->>'save', '')::int, 0
    )), 0)::int ELSE NULL END,
    'totalReach', CASE WHEN COUNT(*) FILTER (WHERE
      insights ? 'reach' OR payload_json ? 'reach' OR COALESCE(payload_json->'insights', '{}'::jsonb) ? 'reach'
    ) > 0 THEN COALESCE(SUM(COALESCE(
      NULLIF(insights->>'reach', '')::int, NULLIF(payload_json->>'reach', '')::int,
      NULLIF(payload_json->'insights'->>'reach', '')::int, 0
    )), 0)::int ELSE NULL END,
    'totalImpressions', CASE WHEN COUNT(*) FILTER (WHERE
      insights ? 'impressions' OR payload_json ? 'impressions' OR COALESCE(payload_json->'insights', '{}'::jsonb) ? 'impressions'
    ) > 0 THEN COALESCE(SUM(COALESCE(
      NULLIF(insights->>'impressions', '')::int, NULLIF(payload_json->>'impressions', '')::int,
      NULLIF(payload_json->'insights'->>'impressions', '')::int, 0
    )), 0)::int ELSE NULL END,
    'latestLoadedAt', MAX(loaded_at),
    'latestPublishedAt', MAX(published_at)
  ) AS payload
  FROM report_raw_ghl_social_posts
  WHERE DATE(COALESCE(published_at, created_at, loaded_at)) BETWEEN $1::date AND $2::date
),"""


LINKEDIN_FUNNEL_CTE = r"""linkedin_funnel AS (
  SELECT jsonb_build_object(
    'readyCount', COUNT(*) FILTER (WHERE connection_status = 'ready')::int,
    'requestedCount', COUNT(*) FILTER (WHERE connection_status IN ('requested', 'requested_pending'))::int,
    'requestedSentCount', COUNT(*) FILTER (WHERE connection_status = 'requested')::int,
    'requestedPendingCount', COUNT(*) FILTER (WHERE connection_status = 'requested_pending')::int,
    'connectedCount', COUNT(*) FILTER (WHERE connection_status = 'connected')::int,
    'followerMessagedCount', COUNT(*) FILTER (WHERE connection_status = 'follower_messaged')::int,
    'dmActiveCount', COUNT(*) FILTER (WHERE connection_status = 'connected' AND sequence_step >= 1 AND sequence_step < 4 AND COALESCE(payload_json->>'dm_conversation_status', '') <> 'active')::int,
    'dmCompletedCount', COUNT(*) FILTER (WHERE connection_status = 'completed' OR sequence_step >= 4)::int,
    'otherStateCount', COUNT(*) FILTER (WHERE connection_status NOT IN ('ready', 'requested', 'requested_pending', 'connected', 'completed', 'follower_messaged'))::int,
    'totalInState', COUNT(*)::int
  ) AS payload
  FROM (
    SELECT connection_status, sequence_step, payload_json FROM linkedin_connection_state
    UNION ALL
    SELECT connection_status, sequence_step, payload_json FROM partnership_linkedin_connection_state
  ) linkedin_state
),"""


def replace_cte(code: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = code.index(start_marker)
    end = code.index(end_marker, start)
    return code[:start] + replacement + code[end:]


def main() -> None:
    workflow = request(WORKFLOW_IDS["executive"])
    if workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError("Refusing to patch an unpublished Executive Summary draft")

    build_query = node_map(workflow)["Build Query"]
    code = str(build_query["parameters"]["jsCode"])
    code = replace_cte(code, "social_posts AS (", "calls AS (", SOCIAL_POSTS_CTE)
    code = replace_cte(code, "linkedin_funnel AS (", "linkedin_weekly_activity AS (", LINKEDIN_FUNNEL_CTE)
    build_query["parameters"]["jsCode"] = code

    updated = update_workflow(workflow)
    print({
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
        "active": updated.get("active"),
    })


if __name__ == "__main__":
    main()
