"""Add campaign-level email attribution to the live Executive Summary workflow.

This changes only the report query and publishes the resulting workflow through
the n8n REST API. It does not execute the workflow or send email.
"""

import json
import os
import ssl
import urllib.request


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKFLOW_ID = "Bukc0mgOD2r7V6ED"


def load_env():
    values = {}
    with open(os.path.join(PROJECT_ROOT, ".env"), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = load_env()
api_key = env.get("N8N_API_KEY_LT") or env.get("n8n_API_Key")
host = (env.get("N8N_HOST") or "https://automations.livetransparent.com").rstrip("/")
if not host.startswith("http"):
    host = "https://" + host
if not api_key:
    raise SystemExit("N8N_API_KEY_LT is missing")


def request(path, method="GET", body=None):
    payload = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        host + path,
        data=payload,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=context) as response:
        return json.loads(response.read().decode("utf-8"))


workflow = request(f"/api/v1/workflows/{WORKFLOW_ID}")
nodes = workflow["nodes"]
build_query = next(node for node in nodes if node.get("name") == "Build Query")
js_code = build_query["parameters"]["jsCode"]

if "email_campaign_attribution AS (" not in js_code:
    schema_sql = """
ALTER TABLE \"DAN_Release_Log\" ADD COLUMN IF NOT EXISTS campaign_key TEXT;
ALTER TABLE \"Emerald_Release_Log\" ADD COLUMN IF NOT EXISTS campaign_key TEXT;
ALTER TABLE partnership_release_log ADD COLUMN IF NOT EXISTS campaign_key TEXT;
ALTER TABLE newsletter_send_log ADD COLUMN IF NOT EXISTS campaign_key TEXT;
""".strip()
    if "SET jit=off;" in js_code:
        js_code = js_code.replace("SET jit=off;", "SET jit=off;\n" + schema_sql, 1)
    else:
        raise SystemExit("Build Query does not contain the expected SET jit=off prefix")

    attribution_cte = r"""
email_send_rows AS (
  SELECT
    COALESCE(NULLIF(campaign_key, ''), CASE WHEN campaign = 'brands' THEN 'dan_brands' WHEN campaign = 'dispensaries' THEN 'dan_dispensaries' ELSE 'dan_' || COALESCE(NULLIF(campaign, ''), 'unknown') END) AS campaign_key,
    'DAN'::text AS campaign_group,
    contact_id,
    release_date::timestamptz AS sent_at,
    CASE WHEN LOWER(COALESCE(status, '')) IN ('sent', 'queued') THEN 1 ELSE 0 END AS sent_count,
    0 AS failed_count
  FROM "DAN_Release_Log"
  WHERE release_date >= $1::date AND release_date < ($2::date + INTERVAL '1 day')
  UNION ALL
  SELECT
    COALESCE(NULLIF(campaign_key, ''), 'emerald_' || COALESCE(NULLIF(bucket, ''), 'unknown')),
    'Emerald'::text,
    ghl_contact_id,
    release_date::timestamptz,
    CASE WHEN LOWER(COALESCE(status, '')) IN ('sent', 'queued') THEN 1 ELSE 0 END,
    0
  FROM "Emerald_Release_Log" e
  WHERE release_date >= $1::date AND release_date < ($2::date + INTERVAL '1 day')
  UNION ALL
  SELECT
    COALESCE(NULLIF(campaign_key, ''), 'partnership_email'),
    'Partnership'::text,
    ghl_contact_id,
    release_date::timestamptz,
    CASE WHEN LOWER(COALESCE(status, '')) = 'sent' THEN 1 ELSE 0 END,
    0
  FROM partnership_release_log
  WHERE release_date >= $1::date AND release_date < ($2::date + INTERVAL '1 day')
  UNION ALL
  SELECT
    COALESCE(NULLIF(campaign_key, ''), 'newsletter_' || week_key),
    'Newsletter'::text,
    ghl_contact_id,
    sent_at,
    CASE WHEN LOWER(COALESCE(status, '')) = 'sent' THEN 1 ELSE 0 END,
    CASE WHEN LOWER(COALESCE(status, '')) IN ('failed', 'invalid_email') THEN 1 ELSE 0 END
  FROM newsletter_send_log
  WHERE COALESCE(sent_at, created_at) >= $1::date AND COALESCE(sent_at, created_at) < ($2::date + INTERVAL '1 day')
),
email_unique_campaign_contacts AS (
  SELECT contact_id
  FROM email_send_rows
  WHERE NULLIF(contact_id, '') IS NOT NULL
  GROUP BY contact_id
  HAVING COUNT(DISTINCT campaign_key) = 1
),
email_campaign_attribution AS (
  SELECT COALESCE(jsonb_agg(row_to_json(t) ORDER BY t.sent DESC, t.campaign_key), '[]'::jsonb) AS items
  FROM (
    SELECT
      campaign_key,
      campaign_group,
      SUM(sent_count)::int AS sent,
      SUM(failed_count)::int AS failed,
      COUNT(DISTINCT s.contact_id) FILTER (WHERE sent_count = 1)::int AS unique_recipients,
      COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('opened', 'open') AND u.contact_id IS NOT NULL)::int AS opened_unique,
      COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('clicked', 'click') AND u.contact_id IS NOT NULL)::int AS clicked_unique,
      COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('bounced', 'bounce', 'soft_bounce', 'hard_bounce') AND u.contact_id IS NOT NULL)::int AS bounced_unique,
      COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('unsubscribed', 'unsubscribe') AND u.contact_id IS NOT NULL)::int AS unsubscribed_unique,
      CASE WHEN COUNT(DISTINCT s.contact_id) FILTER (WHERE sent_count = 1) = 0 THEN NULL ELSE ROUND(100.0 * COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('opened', 'open') AND u.contact_id IS NOT NULL) / COUNT(DISTINCT s.contact_id) FILTER (WHERE sent_count = 1), 2) END AS open_rate,
      CASE WHEN COUNT(DISTINCT s.contact_id) FILTER (WHERE sent_count = 1) = 0 THEN NULL ELSE ROUND(100.0 * COUNT(DISTINCT e.contact_id) FILTER (WHERE LOWER(COALESCE(e.event_type, '')) IN ('clicked', 'click') AND u.contact_id IS NOT NULL) / COUNT(DISTINCT s.contact_id) FILTER (WHERE sent_count = 1), 2) END AS click_rate
    FROM email_send_rows s
    LEFT JOIN email_unique_campaign_contacts u ON u.contact_id = s.contact_id
    LEFT JOIN "Email_Events" e ON e.contact_id = s.contact_id AND e.event_ts >= $1::date AND e.event_ts < ($2::date + INTERVAL '1 day')
    GROUP BY campaign_key, campaign_group
  ) t
),
email_attribution_coverage AS (
  SELECT jsonb_build_object(
    'sendRows', COUNT(*)::int,
    'campaignKeyRows', COUNT(*) FILTER (WHERE NULLIF(campaign_key, '') IS NOT NULL AND campaign_key NOT LIKE '%unknown%')::int,
    'unknownCampaignRows', COUNT(*) FILTER (WHERE campaign_key LIKE '%unknown%')::int,
    'uniqueRecipients', COUNT(DISTINCT NULLIF(contact_id, ''))::int,
    'unambiguousRecipients', (SELECT COUNT(*)::int FROM email_unique_campaign_contacts),
    'basis', 'send_ledger_campaign_key_with_unambiguous_contact_event_fallback'
  ) AS payload
  FROM email_send_rows
),
""".strip()
    marker = "),summary AS ("
    if marker not in js_code:
        raise SystemExit("Build Query does not contain the expected summary CTE marker")
    js_code = js_code.replace(marker, ")," + attribution_cte + "summary AS (", 1)

    final_marker = "'opportunityStageBreakdown', COALESCE((SELECT items FROM opportunity_stage_breakdown), '[]'::json)) AS payload;"
    final_replacement = "'opportunityStageBreakdown', COALESCE((SELECT items FROM opportunity_stage_breakdown), '[]'::json), 'emailCampaignAttribution', COALESCE((SELECT items FROM email_campaign_attribution), '[]'::jsonb), 'emailAttributionCoverage', COALESCE((SELECT to_jsonb(payload) FROM email_attribution_coverage), '{}'::jsonb)) AS payload;"
    if final_marker not in js_code:
        raise SystemExit("Build Query does not contain the expected final response marker")
    js_code = js_code.replace(final_marker, final_replacement, 1)

js_code = js_code.replace(
    "COALESCE(NULLIF(campaign_key, ''), CASE WHEN NULLIF(email_campaign, '') IS NOT NULL THEN 'emerald_' || regexp_replace(lower(email_campaign), '[^a-z0-9]+', '_', 'g') ELSE 'emerald_' || COALESCE(NULLIF(bucket, ''), 'unknown') END)",
    "COALESCE(NULLIF(campaign_key, ''), 'emerald_' || COALESCE(NULLIF(bucket, ''), 'unknown'))",
)
build_query["parameters"]["jsCode"] = js_code

settings = dict(workflow.get("settings") or {})
settings.pop("availableInMCP", None)
payload = {
    "name": workflow["name"],
    "nodes": nodes,
    "connections": workflow["connections"],
    "settings": settings,
}
updated = request(f"/api/v1/workflows/{WORKFLOW_ID}", method="PUT", body=payload)
print(json.dumps({
    "workflowId": WORKFLOW_ID,
    "name": updated.get("name"),
    "versionId": updated.get("versionId"),
    "activeVersionId": updated.get("activeVersionId"),
    "changed": "email_campaign_attribution AS (" in js_code,
}, indent=2))
