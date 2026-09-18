"""Add account-level social statistics and MQL conversion metrics to the Executive Summary (Bukc0mgOD2r7V6ED)."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


BASE_URL = "https://automations.livetransparent.com/api/v1/workflows/"
EXECUTIVE_ID = "Bukc0mgOD2r7V6ED"
ALLOWED_SETTINGS = {
    "executionOrder",
    "timezone",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "saveManualExecutions",
    "saveExecutionProgress",
    "executionTimeout",
    "callerPolicy",
    "errorWorkflow",
    "binaryMode",
}

WARM_PIPELINE = "FRjpDZ1HWj3UPgczsu3t"
MQL_STAGE = "3b3bd98d-cbb9-4c50-8cf3-b4eba29061c2"
SALES_OUTREACH_PIPELINE = "dhdlf3O4tymxFtHk4aqq"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY_LT") or load_env().get("N8N_API_KEY_LT", "")
    if not key:
        raise RuntimeError("N8N_API_KEY_LT is required")
    return key


def request(workflow_id: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + workflow_id,
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def replace_between(code: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str:
    start = code.find(start_marker)
    if start < 0:
        raise RuntimeError(f"{label}: start marker not found")
    end = code.find(end_marker, start + 1)
    if end < 0:
        raise RuntimeError(f"{label}: end marker not found")
    return code[:start] + replacement + code[end:]


SOCIAL_POSTS_CTE = """social_posts AS (
  SELECT jsonb_build_object(
    'countBasis', 'platform_placements',
    'engagementBasis', 'latest_post_ledger',
    'statisticsBasis', 'ghl_social_planner_account_window',
    'statisticsAvailable', COALESCE((SELECT (s.reach IS NOT NULL OR s.impressions IS NOT NULL) FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1), false),
    'totalPosts', COUNT(*)::int,
    'facebookCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'facebook')::int,
    'instagramCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'instagram')::int,
    'linkedinCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(platform, '')) = 'linkedin')::int,
    'publishedCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(status, '')) = 'published')::int,
    'failedCount', COUNT(*) FILTER (WHERE LOWER(COALESCE(status, '')) IN ('failed', 'error'))::int,
    'totalLikes', COALESCE(SUM(COALESCE(NULLIF(insights->>'likes', '')::int, NULLIF(insights->>'like', '')::int, 0)), 0)::int,
    'totalComments', COALESCE(SUM(COALESCE(NULLIF(insights->>'comments', '')::int, NULLIF(insights->>'comment', '')::int, 0)), 0)::int,
    'totalShares', COALESCE(SUM(COALESCE(NULLIF(insights->>'shares', '')::int, NULLIF(insights->>'share', '')::int, 0)), 0)::int,
    'totalSaves', NULL::int,
    'totalReach', (SELECT s.reach FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'totalImpressions', (SELECT s.impressions FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'accountPosts', (SELECT s.posts FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'accountLikes', (SELECT s.likes FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'accountFollowers', (SELECT s.followers FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'accountComments', (SELECT s.comments FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all' LIMIT 1),
    'statisticsAsOf', (SELECT MAX(s.loaded_at) FROM report_ghl_social_statistics s WHERE s.window_start = $1::date AND s.window_end = $2::date AND s.scope = 'all'),
    'latestLoadedAt', MAX(loaded_at),
    'latestPublishedAt', MAX(published_at)
  ) AS payload
  FROM report_raw_ghl_social_posts
  WHERE DATE(COALESCE(published_at, created_at, loaded_at)) BETWEEN $1::date AND $2::date
),
"""

MQL_CTES = f"""mql_keys AS (
  SELECT DISTINCT source_key
  FROM report_raw_ghl_opportunities
  WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id', ''), NULLIF(payload_json->>'pipelineId', ''), '') = '{WARM_PIPELINE}'
    AND COALESCE(NULLIF(dimensions_json->>'pipeline_stage_id', ''), NULLIF(payload_json->>'pipelineStageId', ''), '') = '{MQL_STAGE}'
),
mql_first AS (
  SELECT source_key, MIN(report_date) AS first_mql_date
  FROM report_raw_ghl_opportunities
  WHERE COALESCE(NULLIF(dimensions_json->>'pipeline_id', ''), NULLIF(payload_json->>'pipelineId', ''), '') = '{WARM_PIPELINE}'
    AND COALESCE(NULLIF(dimensions_json->>'pipeline_stage_id', ''), NULLIF(payload_json->>'pipelineStageId', ''), '') = '{MQL_STAGE}'
  GROUP BY source_key
),
mql_conversion AS (
  SELECT source_key, MIN(report_date) AS first_so_date
  FROM report_raw_ghl_opportunities
  WHERE source_key IN (SELECT source_key FROM mql_keys)
    AND COALESCE(NULLIF(dimensions_json->>'pipeline_id', ''), NULLIF(payload_json->>'pipelineId', ''), '') = '{SALES_OUTREACH_PIPELINE}'
  GROUP BY source_key
),
mql_summary AS (
  SELECT jsonb_build_object(
    'totalMqls', (SELECT count(*) FROM mql_keys),
    'totalEver', (SELECT count(*) FROM mql_keys),
    'convertedToSql', (SELECT count(*) FROM mql_keys k JOIN mql_conversion c ON c.source_key = k.source_key),
    'currentMqls', (SELECT count(*) FROM mql_keys k LEFT JOIN mql_conversion c ON c.source_key = k.source_key WHERE c.source_key IS NULL),
    'awaitingSales', (SELECT count(*) FROM mql_keys k LEFT JOIN mql_conversion c ON c.source_key = k.source_key WHERE c.source_key IS NULL),
    'active', (SELECT count(*) FROM mql_keys k LEFT JOIN mql_conversion c ON c.source_key = k.source_key WHERE c.source_key IS NULL),
    'enteredMqls', (SELECT count(*) FROM mql_keys k JOIN mql_first f ON f.source_key = k.source_key WHERE f.first_mql_date BETWEEN $1::date AND $2::date),
    'convertedThisPeriod', (SELECT count(*) FROM mql_conversion c WHERE c.first_so_date BETWEEN $1::date AND $2::date),
    'asOfDate', $2::date
  ) AS payload
),
"""


def node_map(workflow: dict) -> dict[str, dict]:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def update_workflow(workflow: dict) -> dict:
    settings = {key: value for key, value in (workflow.get("settings") or {}).items() if key in ALLOWED_SETTINGS}
    payload = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": settings,
    }
    return request(workflow["id"], method="PUT", payload=payload)


def main() -> None:
    workflow = request(EXECUTIVE_ID)
    if workflow.get("versionId") != workflow.get("activeVersionId"):
        raise RuntimeError("Refusing to patch an unpublished Executive Summary draft")

    build_query = node_map(workflow)["Build Query"]
    code = str(build_query["parameters"]["jsCode"])
    code = replace_between(code, "social_posts AS (", "calls AS (", SOCIAL_POSTS_CTE, "socialPosts")
    code = replace_between(code, "mql_history AS (", "sql_contacts AS (", MQL_CTES, "mqlSummary")
    build_query["parameters"]["jsCode"] = code

    updated = update_workflow(workflow)
    print(json.dumps({
        "id": updated.get("id"),
        "versionId": updated.get("versionId"),
        "activeVersionId": updated.get("activeVersionId"),
        "active": updated.get("active"),
    }))


if __name__ == "__main__":
    main()