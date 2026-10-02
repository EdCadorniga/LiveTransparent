"""Patch LT - Executive Report V1 Facts API (oxYDg6XnRBKhl1Xd).

Two reporting-only fixes, no CRM writes:

1. Band 1 funnel `opportunities_created` was counting every opportunity
   *observed* in any snapshot during the window (e.g. 11,461 for 30d) instead
   of opportunities *created* in the window (1,387). We now count by the raw
   creation date (same expression as the authoritative GHL count).

2. Add `pipelineToWork`: distinct contacts currently on open Sales Outreach
   opportunities in the New or Qualified stages, from the latest raw snapshot.

Usage:
  python scripts/social-reporting/patch_v1_funnel_and_pipeline_to_work.py            # dry run
  python scripts/social-reporting/patch_v1_funnel_and_pipeline_to_work.py --apply    # PUT + publish
  python scripts/social-reporting/patch_v1_funnel_and_pipeline_to_work.py --dump-sql out.sql
"""

import json, os, re, sys, urllib.request
from pathlib import Path

HOST = "https://automations.livetransparent.com"
WF_ID = "oxYDg6XnRBKhl1Xd"
NEW_STAGE = "3529dd3d-cab0-4279-967c-1aea203de4fb"
QUALIFIED_STAGE = "91517911-3eee-45a0-b432-e36209495c16"
SALES_OUTREACH = "dhdlf3O4tymxFtHk4aqq"
ROOT = Path(__file__).resolve().parents[2]


def env():
    d = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def call(method="GET", payload=None):
    key = os.environ.get("N8N_LT_API_KEY") or env()["N8N_LT_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{HOST}/api/v1/workflows/{WF_ID}",
        data=body,
        method=method,
        headers={
            "X-N8N-API-KEY": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


OLD_FUNNEL_OPP = (
    "    'opportunities_created',(SELECT COUNT(DISTINCT opportunity_id)::int "
    "FROM feedback_opps WHERE observed_date BETWEEN $1::date AND $2::date),\n"
)
NEW_FUNNEL_OPP = (
    "    'opportunities_created',(SELECT COUNT(DISTINCT opportunity_id)::int "
    "FROM feedback_opps WHERE created_date BETWEEN $1::date AND $2::date),\n"
)

OLD_OBS = (
    "    o.report_date::date AS observed_date,o.loaded_at\n"
    "  FROM report_raw_ghl_opportunities o WHERE NULLIF(o.source_key,'') IS NOT NULL\n"
)
NEW_OBS = (
    "    (COALESCE(NULLIF(o.dimensions_json->>'source_created_at','')::timestamptz,\n"
    "              NULLIF(o.payload_json->>'createdAt','')::timestamptz,\n"
    "              NULLIF(o.payload_json->>'dateAdded','')::timestamptz,\n"
    "              o.report_date::timestamptz) AT TIME ZONE 'America/Los_Angeles')::date AS created_date,\n"
    "    o.report_date::date AS observed_date,o.loaded_at\n"
    "  FROM report_raw_ghl_opportunities o WHERE NULLIF(o.source_key,'') IS NOT NULL\n"
)

OLD_BASIS = (
    "    'basis','distinct opportunity_id; first observed stage entry/latest outcome; America/Los_Angeles dates',\n"
)
NEW_BASIS = (
    "    'basis','opportunities counted by creation date; MQL/SQL by first observed stage entry; America/Los_Angeles dates',\n"
)

PIPELINE_CTES = (
    ", latest_open_sales_outreach AS (\n"
    "  SELECT DISTINCT ON (o.source_key)\n"
    "    NULLIF(o.source_key,'') AS opportunity_id,\n"
    "    COALESCE(NULLIF(o.dimensions_json->>'pipeline_id',''), NULLIF(o.payload_json->>'pipelineId','')) AS pipeline_id,\n"
    "    COALESCE(NULLIF(o.dimensions_json->>'pipeline_stage_id',''), NULLIF(o.payload_json->>'pipelineStageId','')) AS stage_id,\n"
    "    COALESCE(NULLIF(o.payload_json->>'status',''), NULLIF(o.dimensions_json->>'status',''), 'open') AS opp_status,\n"
    "    COALESCE(NULLIF(o.dimensions_json->>'contact_id',''),NULLIF(o.dimensions_json->>'contact.id',''),"
    "NULLIF(o.payload_json->>'contactId',''),NULLIF(o.payload_json->>'contact_id','')) AS contact_id\n"
    "  FROM report_raw_ghl_opportunities o\n"
    "  WHERE NULLIF(o.source_key,'') IS NOT NULL\n"
    "  ORDER BY o.source_key, o.report_date DESC, o.loaded_at DESC\n"
    "), pipeline_to_work_open AS (\n"
    "  SELECT * FROM latest_open_sales_outreach\n"
    f"  WHERE pipeline_id='{SALES_OUTREACH}'\n"
    "    AND COALESCE(opp_status,'open')='open'\n"
    f"    AND stage_id IN ('{NEW_STAGE}','{QUALIFIED_STAGE}')\n"
    "), pipeline_to_work AS (\n"
    "  SELECT jsonb_build_object(\n"
    f"    'pipeline_id','{SALES_OUTREACH}',\n"
    f"    'new_stage_id','{NEW_STAGE}',\n"
    f"    'qualified_stage_id','{QUALIFIED_STAGE}',\n"
    f"    'new_contacts',(SELECT COUNT(DISTINCT l.contact_id)::int FROM pipeline_to_work_open l WHERE l.stage_id='{NEW_STAGE}'),\n"
    f"    'qualified_contacts',(SELECT COUNT(DISTINCT l.contact_id)::int FROM pipeline_to_work_open l WHERE l.stage_id='{QUALIFIED_STAGE}'),\n"
    "    'total_contacts',(SELECT COUNT(DISTINCT l.contact_id)::int FROM pipeline_to_work_open l),\n"
    "    'total_open_opportunities',(SELECT COUNT(*)::int FROM pipeline_to_work_open),\n"
    "    'basis','distinct contacts on open Sales Outreach opportunities currently in New or Qualified (latest raw snapshot)',\n"
    "    'source_health','report_raw_ghl_opportunities'\n"
    "  ) AS payload\n"
    ")\n"
)

OUT_ANCHOR = "  'window', jsonb_build_object('from',$1::date,'to',$2::date),\n"
OUT_NEW = "  'pipelineToWork', (SELECT payload FROM pipeline_to_work),\n" + OUT_ANCHOR


def patch(code):
    checks = {
        "created_date": "created_date," in code or "AS created_date," in code,
        "pipeline_cte": "pipeline_to_work AS (" in code,
        "out_field": "'pipelineToWork'" in code,
    }
    if checks["created_date"] and checks["pipeline_cte"] and checks["out_field"]:
        return code, "already-patched"

    # 1. feedback_opps creation date
    if OLD_OBS in code:
        code = code.replace(OLD_OBS, NEW_OBS, 1)
    else:
        raise RuntimeError("feedback_opps observed_date anchor not found")

    # 2. funnel opportunities_created
    if OLD_FUNNEL_OPP in code:
        code = code.replace(OLD_FUNNEL_OPP, NEW_FUNNEL_OPP, 1)
    else:
        raise RuntimeError("funnel opportunities_created anchor not found")

    # 3. funnel basis label
    if OLD_BASIS in code:
        code = code.replace(OLD_BASIS, NEW_BASIS, 1)

    # 4. pipeline-to-work CTEs before response_events
    anchor = ", response_events AS ("
    if anchor not in code:
        raise RuntimeError("response_events anchor not found")
    code = code.replace(anchor, PIPELINE_CTES + anchor, 1)

    # 5. output field
    if OUT_ANCHOR not in code:
        raise RuntimeError("window output anchor not found")
    code = code.replace(OUT_ANCHOR, OUT_NEW, 1)

    return code, "patched"


def extract_sql(code):
    m = re.search(r"const queryText = `\n(.*?)\n`;", code, re.S)
    if not m:
        raise RuntimeError("could not extract queryText")
    return m.group(1)


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    dump = None
    if "--dump-sql" in args:
        dump = args[args.index("--dump-sql") + 1]

    wf = call()
    if wf.get("versionId") != wf.get("activeVersionId"):
        raise RuntimeError("draft is not active; refusing to patch")
    node = next(n for n in wf["nodes"] if n.get("name") == "Build V1 Facts Query")
    code, status = patch(node["parameters"]["jsCode"])
    print("status:", status)

    if dump:
        from_str, to_str = "2026-09-02", "2026-10-01"
        sql = extract_sql(code).replace("$1", f"'{from_str}'").replace("$2", f"'{to_str}'")
        Path(dump).write_text(sql, encoding="utf-8")
        print("wrote sql:", dump)

    if not apply:
        print("dry run complete; pass --apply to save")
        return

    if status == "already-patched":
        print("nothing to do")
        return

    node["parameters"]["jsCode"] = code
    settings = {k: v for k, v in (wf.get("settings") or {}).items() if k != "availableInMCP"}
    saved = call("PUT", {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": settings})
    print(json.dumps({"versionId": saved.get("versionId"), "activeVersionId": saved.get("activeVersionId"), "active": saved.get("active")}, indent=2))


if __name__ == "__main__":
    main()
