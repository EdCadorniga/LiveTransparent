import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "emerald-executive-sso-company-sync-staged.json"


def build_workflow() -> dict:
    """Starter scaffold for the Emerald executive SSO company-sync workflow.

    This version establishes the ingestion/cache shape and leaves the research
    provider wiring (Firecrawl/Exa + LLM validator) as the next iteration.
    """

    process_js = r"""
const rows = $items('Fetch Executive SSO Candidates').map((i) => i.json || {});

function str(v) {
  const s = String(v ?? '').trim();
  return s || '';
}

function domainFromEmail(email) {
  const value = str(email).toLowerCase();
  const idx = value.lastIndexOf('@');
  return idx > -1 ? value.slice(idx + 1) : '';
}

function normalizeDomain(value) {
  return str(value).toLowerCase().replace(/^www\./, '').replace(/[^a-z0-9.-]/g, '');
}

const genericDomains = new Set([
  'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
  'aol.com', 'live.com', 'proton.me', 'protonmail.com', 'me.com',
]);

function companyKey(row) {
  const emailDomain = normalizeDomain(domainFromEmail(row.email));
  if (emailDomain && !genericDomains.has(emailDomain)) return emailDomain;
  const url = str(row.company_non_linkedin_urls || row.location_non_linkedin_urls);
  if (url) {
    try {
      return normalizeDomain(new URL(url.startsWith('http') ? url : `https://${url}`).hostname);
    } catch {
      return normalizeDomain(url);
    }
  }
  return `name::${str(row.company_name).toLowerCase() || row.record_key || row.emerald_row_id}`;
}

const groups = new Map();
for (const row of rows) {
  const key = companyKey(row);
  if (!groups.has(key)) {
    groups.set(key, { company_domain_key: key, company_name: str(row.company_name), rows: [] });
  }
  groups.get(key).rows.push(row);
}

return [{
  json: {
    batchCount: rows.length,
    companyCount: groups.size,
    companyDomainKeys: Array.from(groups.keys()),
    companies: Array.from(groups.values()),
    note: 'Scaffold only: the retrieval + validator step will be wired next.'
  }
}];
"""

    return {
        "name": "LT - Emerald Executive SSO -> Company Sync (Staged)",
        "description": "Scaffold for executive SSO company sync, GHL contact reconciliation, and reusable company research caching.",
        "active": False,
        "isArchived": False,
        "nodes": [
            {
                "parameters": {
                    "rule": {"interval": [{"field": "hours"}]}
                },
                "id": "schedule",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [260, 260],
            },
            {
                "parameters": {
                    "assignments": {
                        "assignments": [
                            {"id": "location", "name": "locationId", "type": "string", "value": "Zwz4relUXVPxx8uohnjV"},
                            {"id": "base", "name": "apiBaseUrl", "type": "string", "value": "https://services.leadconnectorhq.com"},
                            {"id": "apikey", "name": "apiKey", "type": "string", "value": "pit-8a0de81d-3555-4909-a8eb-afecd3794828"},
                            {"id": "dry", "name": "defaultDryRun", "type": "boolean", "value": True},
                            {"id": "source", "name": "sourceLabel", "type": "string", "value": "emerald_executive_sso"},
                            {"id": "table", "name": "sourceTable", "type": "string", "value": "Emerald_Campaign_Contacts"},
                            {"id": "cache", "name": "companyCacheTable", "type": "string", "value": "Emerald_Company_Research_Cache"},
                            {"id": "batch", "name": "batchLimit", "type": "number", "value": 250},
                            {"id": "queue", "name": "queueTag", "type": "string", "value": "Enrollment Queue - Emerald - Executives SSO"},
                            {"id": "research", "name": "researchModel", "type": "string", "value": "meta-llama/llama-3.1-8b-instruct"},
                            {"id": "validator", "name": "validatorModel", "type": "string", "value": "openai/gpt-5-mini"},
                        ]
                    },
                    "includeOtherFields": True,
                    "options": {}
                },
                "id": "config",
                "name": "Config",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.4,
                "position": [520, 260],
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": """CREATE TABLE IF NOT EXISTS "Emerald_Company_Research_Cache" (
  company_domain_key TEXT PRIMARY KEY,
  company_name TEXT,
  company_research_snippet TEXT,
  company_operating_state TEXT,
  company_operating_market_note TEXT,
  company_cannabis_marketing_signal TEXT,
  company_research_confidence TEXT,
  company_research_source TEXT,
  company_research_last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_domain_key TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_research_snippet TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_operating_state TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_operating_market_note TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_cannabis_marketing_signal TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_research_confidence TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_research_source TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS company_research_last_verified_at TIMESTAMPTZ;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_match_method TEXT;
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_sync_status TEXT DEFAULT 'pending';
ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_sync_error TEXT;
""",
                    "options": {}
                },
                "id": "ensure_cache",
                "name": "Ensure Executive SSO Research Cache Table",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [780, 260],
                "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": """SELECT
  e.id AS emerald_row_id,
  e.record_key,
  e.first_name,
  e.last_name,
  e.full_name,
  e.email,
  e.phone,
  e.company_name,
  e.company_non_linkedin_urls,
  e.location_non_linkedin_urls,
  e.contact_city,
  e.contact_state,
  e.source_file,
  e.tags,
  e.raw_payload,
  e.company_domain_key,
  e.company_research_snippet,
  e.company_operating_state,
  e.company_operating_market_note,
  e.company_cannabis_marketing_signal,
  e.company_research_confidence,
  e.company_research_source,
  e.company_research_last_verified_at,
  e.ghl_contact_id,
  e.ghl_contact_match_method,
  e.ghl_contact_sync_status,
  e.ghl_contact_sync_error
FROM "Emerald_Campaign_Contacts" e
WHERE COALESCE(e.bucket, '') = 'executives_sso'
  AND COALESCE(e.release_status, 'pending') <> 'released'
ORDER BY e.id ASC
LIMIT {{$item(0).$node["Config"].json.batchLimit}};
""",
                    "options": {}
                },
                "id": "fetch_candidates",
                "name": "Fetch Executive SSO Candidates",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [1030, 260],
                "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
            },
            {
                "parameters": {
                    "jsCode": process_js,
                },
                "id": "prepare_companies",
                "name": "Prepare Company Groups",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1280, 260],
            },
            {
                "parameters": {
                    "jsCode": r"""
const payload = $item(0).$node['Prepare Company Groups'].json || {};
const keys = Array.isArray(payload.companyDomainKeys) ? payload.companyDomainKeys : [];
const sql = keys.length
  ? `SELECT * FROM "Emerald_Company_Research_Cache" WHERE company_domain_key = ANY(ARRAY[${keys.map((key) => `'${String(key).replace(/'/g, "''")}'`).join(', ')}]);`
  : `SELECT company_domain_key FROM "Emerald_Company_Research_Cache" WHERE FALSE;`;
return [{ json: { cacheLookupSql: sql } }];
""",
                },
                "id": "build_cache_lookup",
                "name": "Build Cache Lookup Query",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1530, 260],
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": "={{$json.cacheLookupSql}}",
                    "options": {}
                },
                "id": "fetch_cache",
                "name": "Fetch Company Cache Rows",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [1770, 260],
                "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
            },
            {
                "parameters": {
                    "jsCode": "return [{ json: { ok: true, note: 'Process Company Sync will be wired in the next pass after the cache/research provider is finalized.' } }];"
                },
                "id": "process_sync",
                "name": "Process Company Sync",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2010, 260],
            },
            {
                "parameters": {
                    "jsCode": "const payload = $items('Prepare Company Groups').map((i) => i.json || {})[0] || {};\nreturn [{ json: { ok: true, batchCount: payload.batchCount || 0, companyCount: payload.companyCount || 0, note: 'Scaffold complete; wire the final research + GHL sync step next.' } }];"
                },
                "id": "summarize",
                "name": "Summarize",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2250, 260],
            },
        ],
        "connections": {
            "Schedule Trigger": {"main": [[{"node": "Config", "type": "main", "index": 0}]]},
            "Config": {"main": [[{"node": "Ensure Executive SSO Research Cache Table", "type": "main", "index": 0}]]},
            "Ensure Executive SSO Research Cache Table": {"main": [[{"node": "Fetch Executive SSO Candidates", "type": "main", "index": 0}]]},
            "Fetch Executive SSO Candidates": {"main": [[{"node": "Prepare Company Groups", "type": "main", "index": 0}]]},
            "Prepare Company Groups": {"main": [[{"node": "Build Cache Lookup Query", "type": "main", "index": 0}]]},
            "Build Cache Lookup Query": {"main": [[{"node": "Fetch Company Cache Rows", "type": "main", "index": 0}]]},
            "Fetch Company Cache Rows": {"main": [[{"node": "Process Company Sync", "type": "main", "index": 0}]]},
            "Process Company Sync": {"main": [[{"node": "Summarize", "type": "main", "index": 0}]]},
        },
        "settings": {},
    }


def main() -> None:
    workflow = build_workflow()
    OUTPUT_PATH.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(OUTPUT_PATH), "name": workflow["name"], "nodes": len(workflow["nodes"])}, indent=2))


if __name__ == "__main__":
    main()
