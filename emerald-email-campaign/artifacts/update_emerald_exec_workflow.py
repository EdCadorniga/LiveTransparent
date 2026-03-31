import pathlib
import requests
import textwrap


BASE = "https://automations.livetransparent.com/api/v1"
WORKFLOW_ID = "GHVYyYmhfNiZ7bbN"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODQyYTM2NDctZjMwZi00NzcxLThkNmMtNjM5Mjg0YmQ0MWVkIiwiaWF0IjoxNzc0NTYwMzU3LCJleHAiOjE3ODIyODQ0MDB9.bsrDA-as3_JNXSoBI5x-i7zeaXTf1yeC9nxhRzmPJf4"

ROOT = pathlib.Path(__file__).resolve().parent
PREP_JS = (ROOT / "emerald_exec_company_sync_prepare.js").read_text(encoding="utf-8")
FINALIZE_JS = (ROOT / "emerald_exec_company_sync_finalize.js").read_text(encoding="utf-8")
WORKFLOW_NOTE = textwrap.dedent(
    """
    LT - Emerald Executive SSO -> Company Sync (Staged)

    Purpose
    - Process the executive SSO queue in Postgres.
    - Group contacts by company/domain so research is reused across the same company.
    - Find or create the matching GHL contact per row.
    - Fill missing GHL email/phone only when the value is verified from GHL or source data.
    - Cache company-level research in Postgres for future reuse.

    Research Flow
    - Prepare evidence from the company website and cache rows.
    - Send the evidence to OpenRouter for company research generation.
    - Validate and normalize the research output locally before finalizing writes.

    Important Rules
    - Do not infer company geography from the contact's own location.
    - Do not overwrite existing GHL fields when a value already exists.
    - Keep company-level research snippets short, factual, and source-backed.

    Current Live Behavior
    - active: true
    - OpenRouter is configured through the n8n credential "OpenRouter account" for research only.
    - Validation runs inside a local Code node to avoid network timeouts.
    - This workflow is a batch worker for executive SSO records and updates both GHL and Postgres.
    - Trigger cadence can be adjusted separately from the data logic.
    - The current working batch is capped at 10 contacts.
    """
).strip()


def main() -> None:
    r = requests.get(f"{BASE}/workflows/{WORKFLOW_ID}", headers={"X-N8N-API-KEY": API_KEY}, timeout=60)
    r.raise_for_status()
    wf = r.json()

    def node(name: str) -> dict:
      for item in wf["nodes"]:
        if item["name"] == name:
          return item
      raise KeyError(name)

    def node_any(*names: str) -> dict:
        for candidate in names:
            try:
                return node(candidate)
            except KeyError:
                continue
        raise KeyError(names[0] if names else 'node')

    config = node("Config")
    assignments = config["parameters"]["assignments"]["assignments"]
    assignments[:] = [a for a in assignments if a.get("name") != "openRouterApiKey"]
    existing = {a["name"] for a in assignments}
    for item in [
        {"id": "or_base", "name": "openRouterBaseUrl", "type": "string", "value": "https://openrouter.ai/api/v1"},
        {"id": "or_model", "name": "researchModel", "type": "string", "value": "meta-llama/llama-3.1-8b-instruct"},
        {"id": "or_validator", "name": "validatorModel", "type": "string", "value": "qwen/qwen-2.5-7b-instruct"},
        {"id": "website_pages", "name": "websiteMaxPages", "type": "number", "value": 3},
        {"id": "website_chars", "name": "websiteMaxChars", "type": "number", "value": 7000},
        {"id": "research_field", "name": "researchFieldName", "type": "string", "value": "emerald_exec_sso_ai_research"},
        {"id": "company_name_emails_field", "name": "companyNameForEmailsFieldName", "type": "string", "value": "Company Name for Emails"},
        {"id": "company_state_field", "name": "companyOperatingStateFieldName", "type": "string", "value": "Em_Company_Operating_State"},
        {"id": "company_snippet_field", "name": "companyResearchSnippetFieldName", "type": "string", "value": "Em_Company_Research_Snippet"},
        {"id": "company_market_note_field", "name": "companyMarketNoteFieldName", "type": "string", "value": "Em_Company_Market_Note"},
        {"id": "cannabis_signal_field", "name": "cannabisMarketingSignalFieldName", "type": "string", "value": "Em_Cannabis_Marketing_Signal"},
        {"id": "email4_ready_field", "name": "email4ReadyFieldName", "type": "string", "value": "Em_Email4_Personalization_Ready"},
        {"id": "email4_reason_field", "name": "email4ReasonFieldName", "type": "string", "value": "Em_Email4_Personalization_Reason"},
    ]:
        if item["name"] not in existing:
            assignments.append(item)
    for a in assignments:
        if a.get("name") == "validatorModel":
            a["value"] = "qwen/qwen-2.5-7b-instruct"
        if a.get("name") == "batchLimit":
            a["value"] = 10

    node("Ensure Executive SSO Research Cache Table")["parameters"]["query"] = textwrap.dedent(
        '''
        CREATE TABLE IF NOT EXISTS "Emerald_Company_Research_Cache" (
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
        ALTER TABLE "Emerald_Campaign_Contacts" ADD COLUMN IF NOT EXISTS emerald_exec_sso_ai_research TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_domain_key TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_name TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_non_linkedin_urls TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_linkedin_urls TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS location_non_linkedin_urls TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_research_snippet TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_operating_state TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_operating_market_note TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_cannabis_marketing_signal TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_research_confidence TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_research_source TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS company_research_last_verified_at TIMESTAMPTZ;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS emerald_exec_sso_ai_research TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_match_method TEXT;
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_sync_status TEXT DEFAULT 'pending';
        ALTER TABLE "Emerald_Contacts" ADD COLUMN IF NOT EXISTS ghl_contact_sync_error TEXT;
        '''
    ).strip()

    node("Fetch Executive SSO Candidates")["parameters"]["query"] = textwrap.dedent(
        '''
        SELECT
          e.id AS emerald_row_id,
          e.record_key,
          e.first_name,
          e.last_name,
          e.full_name,
          COALESCE(NULLIF(e.primary_email, ''), NULLIF(e.raw_payload->>'Primary Email', ''), NULLIF(e.raw_payload->>'primary_email', ''), NULLIF(e.raw_payload->>'email', '')) AS email,
          COALESCE(NULLIF(e.primary_phone, ''), NULLIF(e.raw_payload->>'Primary Phone', ''), NULLIF(e.raw_payload->>'primary_phone', ''), NULLIF(e.raw_payload->>'phone', '')) AS phone,
          COALESCE(NULLIF(e.company_name, ''), NULLIF(e.raw_payload->>'Company Name(s)', ''), NULLIF(e.raw_payload->>'company_name', ''), NULLIF(e.raw_payload->>'companyName', '')) AS company_name,
          COALESCE(NULLIF(e.company_non_linkedin_urls, ''), NULLIF(e.raw_payload->>'Company non-LinkedIn URL(s)', ''), NULLIF(e.raw_payload->>'company_non_linkedin_urls', '')) AS company_non_linkedin_urls,
          COALESCE(NULLIF(e.company_linkedin_urls, ''), NULLIF(e.raw_payload->>'Company LinkedIn URL(s)', ''), NULLIF(e.raw_payload->>'company_linkedin_urls', '')) AS company_linkedin_urls,
          COALESCE(NULLIF(e.location_non_linkedin_urls, ''), NULLIF(e.raw_payload->>'Location non-LinkedIn URL(s)', ''), NULLIF(e.raw_payload->>'location_non_linkedin_urls', '')) AS location_non_linkedin_urls,
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
          e.emerald_exec_sso_ai_research,
          e.ghl_contact_id,
          e.ghl_contact_match_method,
          e.ghl_contact_sync_status,
          e.ghl_contact_sync_error
        FROM "Emerald_Contacts" e
        WHERE (
            LOWER(COALESCE(e.tags::text, '')) LIKE '%seq enrolled - emerald%'
            OR LOWER(COALESCE(e.tags::text, '')) LIKE '%seq emerald - executives sso%'
            OR LOWER(COALESCE(e.tags::text, '')) LIKE '%enrollment queue - emerald - executives sso%'
          )
          AND (
            COALESCE(e.ghl_contact_sync_status, 'pending') NOT IN ('synced')
          )
          AND LOWER(COALESCE(e.emerald_exec_sso_ai_research, '')) <> 'done'
        ORDER BY e.id ASC
        LIMIT {{$item(0).$node["Config"].json.batchLimit}};
        '''
    ).strip()

    node("Prepare Company Groups")["parameters"]["jsCode"] = textwrap.dedent(
        '''
        const rows = $items('Fetch Executive SSO Candidates').map((i) => i.json || {});

        function str(v) {
          const s = String(v ?? '').trim();
          return s || '';
        }
        function normalizeDomain(value) {
          return str(value).toLowerCase().replace(/^https?:\\/\\//, '').replace(/^www\\./, '').split('/')[0].replace(/[^a-z0-9.-]/g, '');
        }
        function domainFromEmail(email) {
          const value = str(email).toLowerCase();
          const idx = value.lastIndexOf('@');
          return idx > -1 ? value.slice(idx + 1) : '';
        }
        function firstUrl(value) {
          const raw = String(value || '').trim();
          if (!raw) return '';
          const parts = raw.split(/[\\s,;|]+/).map((p) => p.trim()).filter(Boolean);
          const candidate = parts.find((p) => /^https?:\\/\\//i.test(p) || /^[a-z0-9.-]+\\.[a-z]{2,}/i.test(p));
          return candidate || '';
        }
        function domainFromUrl(value) {
          const raw = str(value);
          if (!raw) return '';
          const normalized = raw.startsWith('http') ? raw : `https://${raw}`;
          const withoutScheme = normalized.replace(/^https?:\\/\\//i, '');
          return normalizeDomain(withoutScheme.split('/')[0]);
        }

        const genericDomains = new Set([
          'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
          'aol.com', 'live.com', 'proton.me', 'protonmail.com', 'me.com', 'mail.com',
          'twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com',
          'tiktok.com', 'youtube.com',
        ]);

        function companyKey(row) {
          const emailDomain = normalizeDomain(domainFromEmail(row.email));
          if (emailDomain && !genericDomains.has(emailDomain)) return emailDomain;

          const url = firstUrl(row.company_non_linkedin_urls) || firstUrl(row.location_non_linkedin_urls);
          if (url) {
            return domainFromUrl(url);
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
            note: 'Companies are grouped by non-generic domain first, then company URL, then company name fallback.',
          }
        }];
        '''
    ).strip()

    node("Build Cache Lookup Query")["parameters"]["jsCode"] = textwrap.dedent(
        '''
        const payload = $item(0).$node['Prepare Company Groups'].json || {};
        const keys = Array.isArray(payload.companyDomainKeys) ? payload.companyDomainKeys : [];
        const sql = keys.length
          ? `WITH keys AS (
              SELECT unnest(ARRAY[${keys.map((key) => `'${String(key).replace(/'/g, "''")}'`).join(', ')}]::text[]) AS company_domain_key
            )
            SELECT
              k.company_domain_key,
              c.company_name,
              c.company_research_snippet,
              c.company_operating_state,
              c.company_operating_market_note,
              c.company_cannabis_marketing_signal,
              c.company_research_confidence,
              c.company_research_source,
              c.company_research_last_verified_at,
              c.created_at,
              c.updated_at
            FROM keys k
            LEFT JOIN "Emerald_Company_Research_Cache" c
              ON c.company_domain_key = k.company_domain_key;`
          : `SELECT NULL::text AS company_domain_key WHERE FALSE;`;
        return [{ json: { cacheLookupSql: sql } }];
        '''
    ).strip()

    nodes = wf["nodes"]
    trigger = node_any("Schedule Trigger", "Manual Trigger")
    trigger["name"] = "Schedule Trigger"
    trigger["type"] = "n8n-nodes-base.scheduleTrigger"
    trigger["typeVersion"] = 1.2
    trigger["parameters"] = {"rule": {"interval": [{"field": "minutes", "minutesInterval": 5}]}}
    trigger["position"] = [-272, -16]
    if not any(n.get("type") == "n8n-nodes-base.stickyNote" and n.get("name") == "Company Sync Note" for n in nodes):
        nodes.insert(0, {
            "parameters": {
                "content": WORKFLOW_NOTE,
                "height": 720,
                "width": 640,
            },
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-640, -720],
            "id": "company_sync_note",
            "name": "Company Sync Note",
        })
    prepare_node = node_any("Process Company Sync", "Prepare Company Research")
    prepare_node["name"] = "Prepare Company Research"
    node("Prepare Company Research")["parameters"]["jsCode"] = PREP_JS

    parse_research = {
        "parameters": {
            "jsCode": textwrap.dedent(
                '''
                const currentItem = $input.item || { json: $json || {} };
                const src = currentItem.json || {};
                const pairedIndex = Number(
                  currentItem?.pairedItem?.item ??
                  currentItem?.pairedItem ??
                  0,
                );
                const prep = ($items('Prepare Company Research')[pairedIndex] || {}).json || {};
                const content = src?.choices?.[0]?.message?.content || src?.message?.content || '';
                let researchJson = null;
                try {
                  researchJson = content ? JSON.parse(content) : null;
                } catch {
                  researchJson = null;
                }
                return {
                  ...prep,
                  research_raw: src,
                  research_content: content,
                  research_json: researchJson,
                };
                '''
            ).strip(),
        },
        "id": "parse_research_response",
        "name": "Parse Research Response",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1888, 260],
    }

    needs_research_node = {
        "parameters": {
            "conditions": {
                "string": [
                    {
                        "value1": "={{$json.researchMode}}",
                        "operation": "equal",
                        "value2": "website",
                    }
                ]
            }
        },
        "id": "needs_research",
        "name": "Needs Research?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1464, 260],
    }

    research_node = {
        "parameters": {
            "method": "POST",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Accept", "value": "application/json"},
                    {"name": "HTTP-Referer", "value": "https://automations.livetransparent.com"},
                    {"name": "X-Title", "value": "LiveTransparent Emerald Research"},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ { model: $item(0).$node[\"Config\"].json.researchModel, messages: $json.researchMessages, temperature: 0, response_format: { type: 'json_object' } } }}",
            "options": {
                "timeout": 30000,
            },
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "openRouterApi",
        },
        "id": "openrouter_research",
        "name": "OpenRouter Research",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.4,
        "position": [1680, 260],
        "credentials": {
            "openRouterApi": {
                "id": "JuE4C7PLHTAeBkze",
                "name": "OpenRouter account",
            },
        },
        "continueOnFail": True,
    }

    validate_node = {
        "parameters": {
            "jsCode": textwrap.dedent(
                '''
                const items = $input.all();

                return items.map((item) => {
                  const src = item.json || {};
                  const candidate = (src.research_json && typeof src.research_json === 'object')
                    ? src.research_json
                    : ((src.deterministic && typeof src.deterministic === 'object') ? src.deterministic : {});
                  const evidencePages = Array.isArray(src.evidencePages) ? src.evidencePages : [];
                  const candidateSource = String(candidate.company_research_source || '').trim().toLowerCase();
                  const preserveCandidateWithoutEvidence = candidateSource === 'website+heuristic' || candidateSource === 'skipped_institutional_domain';
                  const keys = Object.keys(candidate).filter((k) => k !== 'evidence_pages');
                  const cleaned = {};

                  for (const key of keys) {
                    if (evidencePages.length === 0) {
                      if (preserveCandidateWithoutEvidence) {
                        const value = candidate[key];
                        cleaned[key] = value === null || value === undefined ? '' : value;
                      } else if (key === 'company_research_confidence') {
                        cleaned[key] = candidate.company_research_confidence || 'low';
                      } else if (key === 'company_research_source') {
                        cleaned[key] = candidate.company_research_source || 'no_website_evidence';
                      } else {
                        cleaned[key] = '';
                      }
                      continue;
                    }

                    const value = candidate[key];
                    cleaned[key] = value === null || value === undefined ? '' : value;
                  }

                  return {
                    json: {
                      id: 'local-validator-short-circuit',
                      object: 'chat.completion',
                      created: Math.floor(Date.now() / 1000),
                      model: 'local/deterministic-validator',
                      provider: 'n8n-code',
                      choices: [
                        {
                          index: 0,
                          finish_reason: 'stop',
                          native_finish_reason: 'stop',
                          message: {
                            role: 'assistant',
                            content: JSON.stringify(cleaned),
                            refusal: null,
                            reasoning: null,
                          },
                        },
                      ],
                      usage: {
                        prompt_tokens: 0,
                        completion_tokens: 0,
                        total_tokens: 0,
                        cost: 0,
                        is_byok: false,
                        prompt_tokens_details: { cached_tokens: 0, cache_write_tokens: 0, audio_tokens: 0, video_tokens: 0 },
                        cost_details: { upstream_inference_cost: 0, upstream_inference_prompt_cost: 0, upstream_inference_completions_cost: 0 },
                        completion_tokens_details: { reasoning_tokens: 0, image_tokens: 0, audio_tokens: 0 },
                      },
                    },
                    pairedItem: item.pairedItem ?? { item: 0 },
                  };
                });
                '''
            ).strip(),
        },
        "id": "openrouter_validate",
        "name": "OpenRouter Validate",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2096, 260],
    }

    node("Prepare Company Research")["parameters"]["jsCode"] = PREP_JS
    if not any(n["name"] == "Parse Research Response" for n in nodes):
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "Prepare Company Research")
        nodes.insert(idx + 1, parse_research)
    else:
        node("Parse Research Response")["parameters"]["jsCode"] = parse_research["parameters"]["jsCode"]
    if not any(n["name"] == "Needs Research?" for n in nodes):
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "Prepare Company Research")
        nodes.insert(idx + 1, needs_research_node)
    if not any(n["name"] == "OpenRouter Research" for n in nodes):
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "Needs Research?")
        nodes.insert(idx, research_node)
    else:
        research = node("OpenRouter Research")
        research["parameters"]["options"] = {"timeout": 30000}
        research["continueOnFail"] = True
    if not any(n["name"] == "OpenRouter Validate" for n in nodes):
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "OpenRouter Research")
        nodes.insert(idx + 2, validate_node)
    else:
        validate = node("OpenRouter Validate")
        validate["parameters"] = validate_node["parameters"]
        validate["type"] = validate_node["type"]
        validate["typeVersion"] = validate_node["typeVersion"]
        validate["position"] = validate_node["position"]
        validate.pop("credentials", None)
    if not any(n["name"] == "Finalize Company Sync" for n in nodes):
        finalize = {
            "parameters": {
                "jsCode": FINALIZE_JS,
            },
            "id": "finalize_company_sync",
            "name": "Finalize Company Sync",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [2304, 260],
        }
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "Persist Company Sync Results")
        nodes.insert(idx, finalize)
    else:
        node("Finalize Company Sync")["parameters"]["jsCode"] = FINALIZE_JS

    node("Summarize")["parameters"]["jsCode"] = textwrap.dedent(
        '''
        const items = $items('Finalize Company Sync').map((i) => i.json || {});
        const totals = items.reduce((acc, item) => {
          acc.companyCount += 1;
          acc.rowCount += Number(item.rowCount || 0);
          if (item.cacheHit) acc.cacheHits += 1; else acc.cacheMisses += 1;
          if (String(item.research_confidence || '').toLowerCase() === 'high') acc.highConfidence += 1;
          if (String(item.research_confidence || '').toLowerCase() === 'medium') acc.mediumConfidence += 1;
          return acc;
        }, { companyCount: 0, rowCount: 0, cacheHits: 0, cacheMisses: 0, highConfidence: 0, mediumConfidence: 0 });
        return [{ json: { ok: true, ...totals, note: 'Company research cached in Postgres and GHL contacts were found/created/updated per row.' } }];
        '''
    ).strip()

    persist = {
        "parameters": {
            "operation": "executeQuery",
            "query": "={{$json.syncSql}}",
            "options": {},
        },
        "id": "persist_company_sync",
        "name": "Persist Company Sync Results",
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.6,
        "position": [2048, 260],
        "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}},
    }

    if not any(n["name"] == persist["name"] for n in nodes):
        idx = next(i for i, n in enumerate(nodes) if n["name"] == "Summarize")
        nodes.insert(idx, persist)

    wf["connections"] = {
        "Schedule Trigger": {"main": [[{"node": "Config", "type": "main", "index": 0}]]},
        "Config": {"main": [[{"node": "Ensure Executive SSO Research Cache Table", "type": "main", "index": 0}]]},
        "Ensure Executive SSO Research Cache Table": {"main": [[{"node": "Fetch Executive SSO Candidates", "type": "main", "index": 0}]]},
        "Fetch Executive SSO Candidates": {"main": [[{"node": "Prepare Company Groups", "type": "main", "index": 0}]]},
        "Prepare Company Groups": {"main": [[{"node": "Build Cache Lookup Query", "type": "main", "index": 0}]]},
        "Build Cache Lookup Query": {"main": [[{"node": "Fetch Company Cache Rows", "type": "main", "index": 0}]]},
        "Fetch Company Cache Rows": {"main": [[{"node": "Prepare Company Research", "type": "main", "index": 0}]]},
        "Prepare Company Research": {"main": [[{"node": "Needs Research?", "type": "main", "index": 0}]]},
        "Needs Research?": {
            "main": [
                [{"node": "Parse Research Response", "type": "main", "index": 0}],
                [{"node": "OpenRouter Research", "type": "main", "index": 0}],
            ]
        },
        "OpenRouter Research": {"main": [[{"node": "Parse Research Response", "type": "main", "index": 0}]]},
        "Parse Research Response": {"main": [[{"node": "OpenRouter Validate", "type": "main", "index": 0}]]},
        "OpenRouter Validate": {"main": [[{"node": "Finalize Company Sync", "type": "main", "index": 0}]]},
        "Finalize Company Sync": {"main": [[{"node": "Persist Company Sync Results", "type": "main", "index": 0}]]},
        "Persist Company Sync Results": {"main": [[{"node": "Summarize", "type": "main", "index": 0}]]},
    }

    payload = {
        "name": wf["name"],
        "nodes": nodes,
        "connections": wf["connections"],
        "settings": {},
    }
    put = requests.put(
        f"{BASE}/workflows/{WORKFLOW_ID}",
        headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    print(put.status_code)
    print(put.text[:4000])


if __name__ == "__main__":
    main()
