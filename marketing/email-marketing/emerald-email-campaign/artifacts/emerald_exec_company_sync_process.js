const cfg = $item(0).$node['Config'].json || {};
const payload = $items('Prepare Company Groups').map((i) => i.json || {})[0] || {};
const cacheRows = $items('Fetch Company Cache Rows').map((i) => i.json || {});

function str(v) {
  const s = String(v ?? '').trim();
  return s || '';
}
function sqlLit(v) {
  if (v === null || v === undefined || v === '') return 'NULL';
  if (typeof v === 'number') return Number.isFinite(v) ? String(v) : 'NULL';
  if (typeof v === 'boolean') return v ? 'TRUE' : 'FALSE';
  if (typeof v === 'object') return `'${JSON.stringify(v).replace(/'/g, "''")}'::jsonb`;
  return `'${String(v).replace(/'/g, "''")}'`;
}
function normalizeDomain(value) {
  return str(value).toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].replace(/[^a-z0-9.-]/g, '');
}
function normalizePhone(phoneRaw, countryHint) {
  const raw = str(phoneRaw);
  if (!raw) return '';
  const keepPlus = raw.startsWith('+');
  let digits = raw.replace(/\D+/g, '');
  if (!digits) return '';
  if (keepPlus) return `+${digits}`;
  if (digits.length === 10 && String(countryHint || '').toUpperCase() === 'US') return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`;
  return `+${digits}`;
}
function normalizeLinkedinUrl(v) {
  const s = String(v ?? '').trim();
  if (!s) return '';
  try {
    const u = new URL(s);
    const host = u.hostname.toLowerCase();
    if (host === 'linkedin.com' || host.endsWith('.linkedin.com')) return s;
  } catch {}
  return '';
}
const STATE_MAP = {
  AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas', CA: 'California', CO: 'Colorado', CT: 'Connecticut', DE: 'Delaware', FL: 'Florida', GA: 'Georgia', HI: 'Hawaii', ID: 'Idaho', IL: 'Illinois', IN: 'Indiana', IA: 'Iowa', KS: 'Kansas', KY: 'Kentucky', LA: 'Louisiana', ME: 'Maine', MD: 'Maryland', MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota', MS: 'Mississippi', MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada', NH: 'New Hampshire', NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York', NC: 'North Carolina', ND: 'North Dakota', OH: 'Ohio', OK: 'Oklahoma', OR: 'Oregon', PA: 'Pennsylvania', RI: 'Rhode Island', SC: 'South Carolina', SD: 'South Dakota', TN: 'Tennessee', TX: 'Texas', UT: 'Utah', VT: 'Vermont', VA: 'Virginia', WA: 'Washington', WV: 'West Virginia', WI: 'Wisconsin', WY: 'Wyoming', DC: 'District of Columbia',
};
const STATE_ABBRS = Object.keys(STATE_MAP);
const CANNABIS_TERMS = ['cannabis', 'marijuana', 'dispensary', 'weed', 'thc', 'hemp', 'edibles', 'flower', 'pre-roll', 'preroll', 'vape', 'vapes', 'concentrate', 'extract', 'rosin', 'tincture', 'gummies', 'cbd', 'menu', 'products', 'store'];
const MAX_WEBSITE_PAGES = Number(cfg.websiteMaxPages || 3);
const MAX_WEBSITE_CHARS = Number(cfg.websiteMaxChars || 7000);
const openRouterBaseUrl = String(cfg.openRouterBaseUrl || 'https://openrouter.ai/api/v1').replace(/\/$/, '');
const openRouterApiKey = str(cfg.openRouterApiKey);
const researchModel = str(cfg.researchModel || 'meta-llama/llama-3.1-8b-instruct');
const validatorModel = str(cfg.validatorModel || 'openai/gpt-5-mini');
const ghlHeaders = {
  Authorization: `Bearer ${cfg.apiKey}`,
  Version: '2021-07-28',
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ method, url, path, body, headers, json = true }) {
  const req = { method, headers, json };
  req.url = url || `${String(cfg.apiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, '')}${path}`;
  if (body !== undefined) req.body = body;
  try {
    const data = await doHttpRequest.call(this, req);
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      status: err?.statusCode || err?.httpCode || err?.cause?.statusCode || 500,
      data: err?.response?.body || err?.message || err,
    };
  }
}
async function ghlGet(path) {
  return await apiRequest.call(this, { method: 'GET', path, headers: ghlHeaders });
}
async function ghlPost(path, body) {
  return await apiRequest.call(this, { method: 'POST', path, headers: ghlHeaders, body });
}
async function ghlPut(path, body) {
  return await apiRequest.call(this, { method: 'PUT', path, headers: ghlHeaders, body });
}
async function fetchText(url) {
  try {
    const res = await fetch(url, {
      headers: {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
        accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
      redirect: 'follow',
    });
    if (!res.ok) return '';
    return await res.text();
  } catch {
    return '';
  }
}
function stripHtml(html) {
  return String(html || '')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim();
}
function extractLinks(html, baseUrl) {
  const out = [];
  const base = new URL(baseUrl);
  const re = /href=["']([^"']+)["']/gi;
  let m;
  while ((m = re.exec(html || ''))) {
    const href = String(m[1] || '').trim();
    if (!href || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#') || href.startsWith('javascript:')) continue;
    try {
      const abs = new URL(href, baseUrl);
      if (abs.hostname !== base.hostname) continue;
      const path = abs.pathname.toLowerCase();
      if (/(about|contact|locations|location|stores?|dispensary|menu|product|products|shop|brands?|cannabis|weed|hemp|thc)/.test(path)) out.push(abs.toString());
    } catch {}
  }
  return Array.from(new Set(out)).slice(0, MAX_WEBSITE_PAGES - 1);
}
function detectState(text) {
  const hay = String(text || '').toUpperCase();
  for (const abbr of STATE_ABBRS) {
    const name = STATE_MAP[abbr].toUpperCase();
    if (new RegExp(`\\b${abbr}\\b\\s+\\d{5}`).test(hay) || hay.includes(` ${name} `)) return STATE_MAP[abbr];
  }
  return '';
}
function detectCannabisSignals(text) {
  const hay = String(text || '').toLowerCase();
  return CANNABIS_TERMS.filter((term) => hay.includes(term)).slice(0, 6);
}
function firstUrl(value) {
  const raw = String(value || '').trim();
  if (!raw) return '';
  const parts = raw.split(/[\s,;|]+/).map((p) => p.trim()).filter(Boolean);
  const candidate = parts.find((p) => /^https?:\/\//i.test(p) || /^[a-z0-9.-]+\.[a-z]{2,}/i.test(p));
  return candidate || '';
}
function extractContactId(payload) {
  return String(payload?.contact?.id || payload?.id || payload?.contactId || '').trim();
}
function asContacts(payload) {
  if (Array.isArray(payload?.contacts)) return payload.contacts;
  if (Array.isArray(payload?.data?.contacts)) return payload.data.contacts;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload)) return payload;
  return [];
}
function buildContactSearchQuery(row, companyName) {
  return str(row.full_name || [row.first_name, row.last_name].filter(Boolean).join(' ') || companyName || row.record_key || row.emerald_row_id);
}
function isMissing(v) { return v === null || v === undefined || String(v).trim() === ''; }
function allowedResearchText(text) {
  const bad = ['probably', 'maybe', 'likely', 'appears to be', 'seems to be'];
  const hay = String(text || '').toLowerCase();
  return !bad.some((b) => hay.includes(b));
}
function deterministicSnippet(companyName, state, signals) {
  if (!state || !signals.length) return '';
  return `Based on our research into ${companyName}'s ${state} market presence, the site shows active cannabis-related product marketing. For a company like ${companyName}, that usually means stable, compliant visibility matters if you want to keep momentum.`;
}
async function openRouterChat(model, messages) {
  if (!openRouterApiKey) return null;
  const res = await apiRequest.call(this, {
    method: 'POST',
    url: `${openRouterBaseUrl}/chat/completions`,
    headers: {
      Authorization: `Bearer ${openRouterApiKey}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'HTTP-Referer': 'https://automations.livetransparent.com',
      'X-Title': 'LiveTransparent Emerald Research',
    },
    body: { model, messages, temperature: 0, response_format: { type: 'json_object' } },
  });
  if (!res.ok) return null;
  const content = res.data?.choices?.[0]?.message?.content || '';
  if (!content) return null;
  try { return JSON.parse(content); } catch { return null; }
}
function buildCompanyResearch(company, cacheHit) {
  const cache = cacheHit || {};
  const base = {
    company_domain_key: company.company_domain_key,
    company_name: company.company_name || cache.company_name || '',
    company_operating_state: cache.company_operating_state || '',
    company_operating_market_note: cache.company_operating_market_note || '',
    company_cannabis_marketing_signal: cache.company_cannabis_marketing_signal || '',
    company_research_snippet: cache.company_research_snippet || '',
    company_research_confidence: cache.company_research_confidence || 'low',
    company_research_source: cache.company_research_source || '',
    company_research_last_verified_at: cache.company_research_last_verified_at || '',
  };
  const companyName = base.company_name || company.company_name || company.company_domain_key;
  const urls = [];
  for (const row of company.rows) {
    const u = firstUrl(row.company_non_linkedin_urls) || firstUrl(row.location_non_linkedin_urls) || firstUrl(row.company_linkedin_urls) || firstUrl(row.location_linkedin_urls);
    if (u) urls.push(u.startsWith('http') ? u : `https://${u}`);
  }
  const uniqueUrls = Array.from(new Set(urls)).slice(0, MAX_WEBSITE_PAGES);
  return { companyName, urls: uniqueUrls, base };
}
async function researchCompany(company, cacheHit) {
  const cache = cacheHit || {};
  if (cache && ['high', 'medium'].includes(String(cache.company_research_confidence || '').toLowerCase())) {
    return {
      companyName: cache.company_name || company.company_name || company.company_domain_key,
      company_operating_state: str(cache.company_operating_state),
      company_operating_market_note: str(cache.company_operating_market_note),
      company_cannabis_marketing_signal: str(cache.company_cannabis_marketing_signal),
      company_research_snippet: str(cache.company_research_snippet),
      company_research_confidence: str(cache.company_research_confidence || 'medium'),
      company_research_source: str(cache.company_research_source || 'cache'),
      cache,
    };
  }

  const researchSeed = buildCompanyResearch(company, cache);
  const evidencePages = [];
  for (const url of researchSeed.urls.slice(0, MAX_WEBSITE_PAGES)) {
    const html = await fetchText(url);
    if (!html) continue;
    const text = stripHtml(html).slice(0, MAX_WEBSITE_CHARS);
    evidencePages.push({ url, text, title: (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '').replace(/\s+/g, ' ').trim() });
    if (evidencePages.length < MAX_WEBSITE_PAGES) {
      for (const link of extractLinks(html, url).slice(0, MAX_WEBSITE_PAGES - evidencePages.length)) {
        const linkedHtml = await fetchText(link);
        if (!linkedHtml) continue;
        evidencePages.push({ url: link, text: stripHtml(linkedHtml).slice(0, MAX_WEBSITE_CHARS), title: (linkedHtml.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '').replace(/\s+/g, ' ').trim() });
        if (evidencePages.length >= MAX_WEBSITE_PAGES) break;
      }
    }
    if (evidencePages.length >= MAX_WEBSITE_PAGES) break;
  }

  const combinedText = [researchSeed.companyName, ...evidencePages.map((p) => `${p.title} ${p.text} ${p.url}`)].join(' | ');
  const state = detectState(combinedText);
  const cannabisSignals = detectCannabisSignals(combinedText);
  const hasCompanyName = combinedText.toLowerCase().includes(researchSeed.companyName.toLowerCase());
  const confidence = state && cannabisSignals.length && hasCompanyName ? 'high' : ((state || cannabisSignals.length) ? 'medium' : 'low');
  const marketNote = state ? `Website evidence ties ${researchSeed.companyName} to ${state}.` : '';
  const signalText = cannabisSignals.length ? cannabisSignals.join(', ') : '';
  const deterministic = {
    companyName: researchSeed.companyName,
    company_operating_state: state,
    company_operating_market_note: marketNote,
    company_cannabis_marketing_signal: signalText,
    company_research_snippet: deterministicSnippet(researchSeed.companyName, state, cannabisSignals),
    company_research_confidence: confidence,
    company_research_source: evidencePages.length ? 'website+heuristic' : 'no_website_evidence',
    cache: null,
  };

  if (!openRouterApiKey || confidence === 'low') return deterministic;

  const researchPayload = {
    company_name: researchSeed.companyName,
    company_domain_key: company.company_domain_key,
    evidence_pages: evidencePages.map((p) => ({ url: p.url, title: p.title, text: p.text.slice(0, 3500) })),
    deterministic,
    rules: [
      'Use only evidence provided.',
      'Do not infer company geography from the contact state.',
      'If operating state is not explicit in evidence, leave it blank.',
      'If cannabis-product marketing is not explicit, leave the signal blank.',
      'Output JSON only.',
    ],
  };

  const researchJson = await openRouterChat.call(this, researchModel, [
    { role: 'system', content: 'You are a factual company research synthesizer. Return JSON only with keys: company_operating_state, company_operating_market_note, company_cannabis_marketing_signal, company_research_snippet, company_research_confidence, company_research_source.' },
    { role: 'user', content: JSON.stringify(researchPayload) },
  ]);

  let final = deterministic;
  if (researchJson && typeof researchJson === 'object') {
    final = {
      companyName: researchSeed.companyName,
      company_operating_state: str(researchJson.company_operating_state || deterministic.company_operating_state),
      company_operating_market_note: str(researchJson.company_operating_market_note || deterministic.company_operating_market_note),
      company_cannabis_marketing_signal: str(researchJson.company_cannabis_marketing_signal || deterministic.company_cannabis_marketing_signal),
      company_research_snippet: str(researchJson.company_research_snippet || deterministic.company_research_snippet),
      company_research_confidence: str(researchJson.company_research_confidence || deterministic.company_research_confidence),
      company_research_source: str(researchJson.company_research_source || 'website+llm'),
      cache: null,
    };
  }

  const validated = await openRouterChat.call(this, validatorModel, [
    { role: 'system', content: 'Validate that the JSON is supported by the evidence and contains no unsupported claims. Return JSON only with the same keys, blanking any unsupported values.' },
    { role: 'user', content: JSON.stringify({ evidence_pages: evidencePages, candidate: final }) },
  ]);

  if (validated && typeof validated === 'object') {
    final = {
      companyName: researchSeed.companyName,
      company_operating_state: str(validated.company_operating_state || final.company_operating_state),
      company_operating_market_note: str(validated.company_operating_market_note || final.company_operating_market_note),
      company_cannabis_marketing_signal: str(validated.company_cannabis_marketing_signal || final.company_cannabis_marketing_signal),
      company_research_snippet: str(validated.company_research_snippet || final.company_research_snippet),
      company_research_confidence: str(validated.company_research_confidence || final.company_research_confidence),
      company_research_source: str(validated.company_research_source || 'website+llm+validator'),
      cache: null,
    };
  }

  if (!allowedResearchText(final.company_research_snippet)) final.company_research_snippet = '';
  return final;
}
function buildCompanyUpsertSql(company, research) {
  const rowIds = company.rows.map((r) => Number(r.emerald_row_id)).filter((n) => Number.isFinite(n));
  const rowCases = (field, valueFn, useExisting = false) => {
    const cases = company.rows.map((row) => {
      const v = valueFn(row);
      const lit = useExisting ? `COALESCE(NULLIF(${field}, ''), ${sqlLit(v)})` : sqlLit(v);
      return `WHEN ${Number(row.emerald_row_id)} THEN ${lit}`;
    }).join(' ');
    return `CASE id ${cases} ELSE ${field} END`;
  };

  const companyResearchSql = {
    company_domain_key: company.company_domain_key,
    company_name: research.companyName || company.company_name || company.company_domain_key,
    company_research_snippet: research.company_research_snippet || '',
    company_operating_state: research.company_operating_state || '',
    company_operating_market_note: research.company_operating_market_note || '',
    company_cannabis_marketing_signal: research.company_cannabis_marketing_signal || '',
    company_research_confidence: research.company_research_confidence || 'low',
    company_research_source: research.company_research_source || '',
    company_research_last_verified_at: new Date().toISOString(),
  };

  const idCase = rowCases('ghl_contact_id', (row) => row.ghl_contact_id || '');
  const methodCase = rowCases('ghl_contact_match_method', (row) => row.ghl_contact_match_method || '');
  const statusCase = rowCases('ghl_contact_sync_status', (row) => row.ghl_contact_sync_status || 'synced');
  const errorCase = rowCases('ghl_contact_sync_error', (row) => row.ghl_contact_sync_error || '');
  const emailCase = rowCases('primary_email', (row) => row.resolved_email || row.email || '', true);
  const phoneCase = rowCases('primary_phone', (row) => row.resolved_phone || row.phone || '', true);

  return `WITH cache_upsert AS (\n  INSERT INTO \"Emerald_Company_Research_Cache\" (\n    company_domain_key,\n    company_name,\n    company_research_snippet,\n    company_operating_state,\n    company_operating_market_note,\n    company_cannabis_marketing_signal,\n    company_research_confidence,\n    company_research_source,\n    company_research_last_verified_at,\n    created_at,\n    updated_at\n  ) VALUES (\n    ${sqlLit(companyResearchSql.company_domain_key)},\n    ${sqlLit(companyResearchSql.company_name)},\n    ${sqlLit(companyResearchSql.company_research_snippet)},\n    ${sqlLit(companyResearchSql.company_operating_state)},\n    ${sqlLit(companyResearchSql.company_operating_market_note)},\n    ${sqlLit(companyResearchSql.company_cannabis_marketing_signal)},\n    ${sqlLit(companyResearchSql.company_research_confidence)},\n    ${sqlLit(companyResearchSql.company_research_source)},\n    ${sqlLit(companyResearchSql.company_research_last_verified_at)},\n    NOW(),\n    NOW()\n  )\n  ON CONFLICT (company_domain_key) DO UPDATE SET\n    company_name = EXCLUDED.company_name,\n    company_research_snippet = EXCLUDED.company_research_snippet,\n    company_operating_state = EXCLUDED.company_operating_state,\n    company_operating_market_note = EXCLUDED.company_operating_market_note,\n    company_cannabis_marketing_signal = EXCLUDED.company_cannabis_marketing_signal,\n    company_research_confidence = EXCLUDED.company_research_confidence,\n    company_research_source = EXCLUDED.company_research_source,\n    company_research_last_verified_at = EXCLUDED.company_research_last_verified_at,\n    updated_at = NOW()\n)\nUPDATE \"Emerald_Contacts\"\nSET\n  company_domain_key = ${sqlLit(company.company_domain_key)},\n  company_name = COALESCE(NULLIF(company_name, ''), ${sqlLit(companyResearchSql.company_name)}),\n  company_research_snippet = ${sqlLit(companyResearchSql.company_research_snippet)},\n  company_operating_state = ${sqlLit(companyResearchSql.company_operating_state)},\n  company_operating_market_note = ${sqlLit(companyResearchSql.company_operating_market_note)},\n  company_cannabis_marketing_signal = ${sqlLit(companyResearchSql.company_cannabis_marketing_signal)},\n  company_research_confidence = ${sqlLit(companyResearchSql.company_research_confidence)},\n  company_research_source = ${sqlLit(companyResearchSql.company_research_source)},\n  company_research_last_verified_at = ${sqlLit(companyResearchSql.company_research_last_verified_at)},\n  ghl_contact_id = ${idCase},\n  ghl_contact_match_method = ${methodCase},\n  ghl_contact_sync_status = ${statusCase},\n  ghl_contact_sync_error = ${errorCase},\n  primary_email = ${emailCase},\n  primary_phone = ${phoneCase},\n  updated_at = NOW()\nWHERE id IN (${rowIds.join(', ')});\n`;\n}
async function resolveGhlContact(row, companyName) {
  const fullName = buildContactSearchQuery(row, companyName);
  const payload = {
    firstName: str(row.first_name || ''),
    lastName: str(row.last_name || ''),
    name: str(row.full_name || fullName),
    email: str(row.email || ''),
    phone: str(row.phone || ''),
    companyName: str(row.company_name || companyName || ''),
    website: firstUrl(row.company_non_linkedin_urls) || firstUrl(row.location_non_linkedin_urls),
    city: str(row.contact_city || ''),
    state: str(row.contact_state || ''),
    source: str(cfg.sourceLabel || 'emerald_executive_sso'),
  };
  const standard = Object.fromEntries(Object.entries(payload).filter(([, v]) => !isMissing(v)));

  let contactId = str(row.ghl_contact_id || '');
  let matchMethod = contactId ? 'cached_ghl_contact_id' : '';
  let syncStatus = 'synced';
  let syncError = '';
  let resolvedEmail = str(row.email || '');
  let resolvedPhone = str(row.phone || '');

  if (!contactId) {
    const tries = [];
    if (resolvedEmail) tries.push({ type: 'email', res: await ghlGet.call(this, `/contacts/search/duplicate?locationId=${encodeURIComponent(cfg.locationId)}&email=${encodeURIComponent(resolvedEmail)}`) });
    if (!contactId && resolvedPhone) tries.push({ type: 'phone', res: await ghlGet.call(this, `/contacts/search/duplicate?locationId=${encodeURIComponent(cfg.locationId)}&number=${encodeURIComponent(resolvedPhone)}`) });
    if (!contactId && fullName) tries.push({ type: 'name', res: await ghlGet.call(this, `/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(fullName)}&limit=20`) });
    if (!contactId && companyName) tries.push({ type: 'company', res: await ghlGet.call(this, `/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(companyName)}&limit=20`) });

    for (const attempt of tries) {
      if (!attempt.res?.ok) continue;
      const data = attempt.res.data || {};
      if (attempt.type === 'email' || attempt.type === 'phone') {
        if (data?.contact?.id) {
          contactId = str(data.contact.id);
          matchMethod = `${attempt.type}_duplicate`;
          break;
        }
      } else {
        const matches = asContacts(data);
        const want = fullName.toLowerCase();
        const exact = matches.find((c) => {
          const fn = str(`${c.firstName || ''} ${c.lastName || ''}`).toLowerCase();
          const nm = str(c.contactName || c.name || '').toLowerCase();
          return fn === want || nm === want || str(c.companyName || '').toLowerCase() === str(companyName || '').toLowerCase();
        }) || matches[0];
        if (exact?.id) {
          contactId = str(exact.id);
          matchMethod = `${attempt.type}_search`;
          break;
        }
      }
    }
  }

  if (contactId) {
    const getRes = await ghlGet.call(this, `/contacts/${encodeURIComponent(contactId)}`);
    const contact = getRes.ok ? (getRes.data?.contact || getRes.data || {}) : {};
    const updatePayload = {};
    if (isMissing(contact.firstName) && payload.firstName) updatePayload.firstName = payload.firstName;
    if (isMissing(contact.lastName) && payload.lastName) updatePayload.lastName = payload.lastName;
    if (isMissing(contact.name) && payload.name) updatePayload.name = payload.name;
    if (isMissing(contact.email) && payload.email) updatePayload.email = payload.email;
    if (isMissing(contact.phone) && payload.phone) updatePayload.phone = payload.phone;
    if (isMissing(contact.companyName) && payload.companyName) updatePayload.companyName = payload.companyName;
    if (isMissing(contact.website) && payload.website) updatePayload.website = payload.website;
    if (isMissing(contact.city) && payload.city) updatePayload.city = payload.city;
    if (isMissing(contact.state) && payload.state) updatePayload.state = payload.state;
    if (Object.keys(updatePayload).length) {
      const upd = await ghlPut.call(this, `/contacts/${encodeURIComponent(contactId)}`, updatePayload);
      if (!upd.ok) {
        syncStatus = 'error';
        syncError = str(upd.data?.message || JSON.stringify(upd.data));
      }
    }
    resolvedEmail = resolvedEmail || str(contact.email || '');
    resolvedPhone = resolvedPhone || str(contact.phone || '');
  } else {
    const createPayload = { locationId: cfg.locationId, ...standard };
    let resp = null;
    if (resolvedEmail || resolvedPhone) {
      resp = await ghlPost.call(this, '/contacts/upsert', createPayload);
      matchMethod = 'upsert';
    } else {
      resp = await ghlPost.call(this, '/contacts/', createPayload);
      matchMethod = 'create_without_unique_identifier';
    }
    if (!resp.ok) {
      syncStatus = 'error';
      syncError = str(resp.data?.message || JSON.stringify(resp.data));
    } else {
      contactId = extractContactId(resp.data);
      matchMethod = matchMethod || 'create';
      const contactObj = resp.data?.contact || resp.data || {};
      resolvedEmail = resolvedEmail || str(contactObj.email || '');
      resolvedPhone = resolvedPhone || str(contactObj.phone || '');
    }
  }

  if (!contactId) {
    syncStatus = 'error';
    syncError = syncError || 'No GHL contact id returned';
  }

  return { contactId, matchMethod, syncStatus, syncError, resolvedEmail, resolvedPhone };
}

const companyItems = Array.isArray(payload.companies) ? payload.companies : [];
const cacheByKey = new Map(cacheRows.map((r) => [normalizeDomain(r.company_domain_key), r]));
const outputs = [];

for (const company of companyItems) {
  const cached = cacheByKey.get(normalizeDomain(company.company_domain_key)) || null;
  const research = await researchCompany.call(this, company, cached);
  const rowResults = [];

  for (const row of company.rows) {
    const result = await resolveGhlContact.call(this, row, research.companyName || company.company_name || company.company_domain_key);
    rowResults.push({
      emerald_row_id: Number(row.emerald_row_id),
      ghl_contact_id: result.contactId,
      ghl_contact_match_method: result.matchMethod,
      ghl_contact_sync_status: result.syncStatus,
      ghl_contact_sync_error: result.syncError,
      resolved_email: result.resolvedEmail,
      resolved_phone: result.resolvedPhone,
    });
  }

  const companyForSql = {
    company_domain_key: company.company_domain_key,
    company_name: research.companyName || company.company_name || company.company_domain_key,
    rows: rowResults,
  };

  outputs.push({
    json: {
      company_domain_key: company.company_domain_key,
      company_name: companyForSql.company_name,
      rowCount: company.rows.length,
      cacheHit: !!cached,
      research_confidence: research.company_research_confidence,
      company_operating_state: research.company_operating_state || '',
      company_operating_market_note: research.company_operating_market_note || '',
      company_cannabis_marketing_signal: research.company_cannabis_marketing_signal || '',
      company_research_snippet: research.company_research_snippet || '',
      company_research_source: research.company_research_source || '',
      syncSql: buildCompanyUpsertSql(companyForSql, research),
    }
  });
}

return outputs.length ? outputs : [{ json: { ok: true, batchCount: 0, companyCount: 0, note: 'No pending executive SSO rows found.' } }];
