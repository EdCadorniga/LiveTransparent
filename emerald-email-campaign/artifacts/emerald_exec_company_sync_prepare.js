const cfg = $item(0).$node['Config'].json || {};
const payload = $items('Prepare Company Groups').map((i) => i.json || {})[0] || {};
const cacheRows = $items('Fetch Company Cache Rows').map((i) => i.json || {});

function str(v) {
  const s = String(v ?? '').trim();
  return s || '';
}
function normalizeDomain(value) {
  return str(value).toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].replace(/[^a-z0-9.-]/g, '');
}
function domainFromEmail(email) {
  const value = str(email).toLowerCase();
  const idx = value.lastIndexOf('@');
  return idx > -1 ? normalizeDomain(value.slice(idx + 1)) : '';
}
function firstUrl(value) {
  const raw = String(value || '').trim();
  if (!raw) return '';
  const parts = raw.split(/[\s,;|]+/).map((p) => p.trim()).filter(Boolean);
  const candidate = parts.find((p) => /^https?:\/\//i.test(p) || /^[a-z0-9.-]+\.[a-z]{2,}/i.test(p));
  return candidate || '';
}
function domainFromUrl(value) {
  const raw = str(value);
  if (!raw) return '';
  const normalized = raw.startsWith('http') ? raw : `https://${raw}`;
  const withoutScheme = normalized.replace(/^https?:\/\//i, '');
  return normalizeDomain(withoutScheme.split('/')[0]);
}

const STATE_MAP = {
  AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas', CA: 'California', CO: 'Colorado', CT: 'Connecticut', DE: 'Delaware', FL: 'Florida', GA: 'Georgia', HI: 'Hawaii', ID: 'Idaho', IL: 'Illinois', IN: 'Indiana', IA: 'Iowa', KS: 'Kansas', KY: 'Kentucky', LA: 'Louisiana', ME: 'Maine', MD: 'Maryland', MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota', MS: 'Mississippi', MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada', NH: 'New Hampshire', NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York', NC: 'North Carolina', ND: 'North Dakota', OH: 'Ohio', OK: 'Oklahoma', OR: 'Oregon', PA: 'Pennsylvania', RI: 'Rhode Island', SC: 'South Carolina', SD: 'South Dakota', TN: 'Tennessee', TX: 'Texas', UT: 'Utah', VT: 'Vermont', VA: 'Virginia', WA: 'Washington', WV: 'West Virginia', WI: 'Wisconsin', WY: 'Wyoming', DC: 'District of Columbia',
};
const STATE_ABBRS = Object.keys(STATE_MAP);
const CANNABIS_TERMS = [
  'cannabis', 'marijuana', 'dispensary', 'dispensaries', 'weed', 'thc', 'hemp', 'cbd',
  'edibles', 'flower', 'pre-roll', 'preroll', 'vape', 'vapes', 'concentrate', 'extract',
  'rosin', 'tincture', 'gummies', 'menu', 'products', 'store', 'retail', 'retailer',
  'medical cannabis', 'adult-use', 'recreational', 'cultivation', 'cultivator', 'license',
  'licensed', 'delivery', 'strain', 'budtender',
];
const INSTITUTION_TERMS = ['university', 'college', 'school', 'faculty', 'campus', 'institute', 'academy'];
const BUSINESS_OVERRIDE_TERMS = [
  'dispensary', 'dispensaries', 'cannabis', 'hemp', 'thc', 'cbd', 'retail', 'retailer',
  'store', 'shop', 'brands', 'brand', 'operator', 'operations', 'holdings', 'labs',
  'cultivation', 'licensed', 'delivery', 'medical cannabis', 'adult-use', 'recreational',
];
const MAX_WEBSITE_PAGES = Number(cfg.websiteMaxPages || 3);
const MAX_WEBSITE_CHARS = Number(cfg.websiteMaxChars || 7000);

function isAcademicDomain(domain) {
  const d = normalizeDomain(domain);
  return !!d && (
    d.endsWith('.edu') ||
    d.endsWith('.ac.uk') ||
    d.endsWith('.edu.au') ||
    d.endsWith('.ac.nz') ||
    d.endsWith('.ac.jp') ||
    d.endsWith('.edu.mx') ||
    d.includes('.edu.')
  );
}

function textHasAny(text, terms) {
  const hay = str(text).toLowerCase();
  return terms.some((term) => hay.includes(term));
}

function companyLooksInstitutional(companyName, domain) {
  return isAcademicDomain(domain) || textHasAny(companyName, INSTITUTION_TERMS);
}
function looksLikeResearchableDomain(value) {
  const domain = normalizeDomain(value);
  return !!domain && domain.includes('.') && !isAcademicDomain(domain);
}
function isReusableCache(cache) {
  const source = str(cache?.company_research_source).toLowerCase();
  const state = str(cache?.company_operating_state);
  const snippet = str(cache?.company_research_snippet);
  const signal = str(cache?.company_cannabis_marketing_signal);
  if (source !== 'website+heuristic') return false;
  return !!(state && (snippet || signal));
}

function resolveBusinessUrl(company) {
  const rows = Array.isArray(company.rows) ? company.rows : [];
  for (const row of rows) {
    const url = firstUrl(row.company_non_linkedin_urls) || firstUrl(row.location_non_linkedin_urls);
    if (url) return url.startsWith('http') ? url : `https://${url}`;
  }
  return '';
}

function hasBusinessOverrideSignal(company, businessUrl) {
  const companyName = str(company.company_name || '');
  if (businessUrl && !isAcademicDomain(domainFromUrl(businessUrl))) return true;
  if (textHasAny(companyName, BUSINESS_OVERRIDE_TERMS)) return true;
  const rows = Array.isArray(company.rows) ? company.rows : [];
  return rows.some((row) => {
    const hay = [
      row.company_name,
      row.company_non_linkedin_urls,
      row.location_non_linkedin_urls,
      row.company_linkedin_urls,
      row.location_linkedin_urls,
    ].map((v) => str(v)).join(' | ');
    return textHasAny(hay, BUSINESS_OVERRIDE_TERMS);
  });
}

async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function fetchText(url) {
  try {
    const res = await doHttpRequest.call(this, {
      method: 'GET',
      url,
      headers: {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.0',
        accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
      json: false,
      encoding: 'text',
      followRedirect: true,
      timeout: 15000,
    });
    return typeof res === 'string' ? res : String(res || '');
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
  const baseDomain = domainFromUrl(baseUrl);
  const baseRoot = /^https?:\/\//i.test(baseUrl)
    ? baseUrl.replace(/^(https?:\/\/[^/]+).*$/i, '$1')
    : `https://${baseDomain}`;
  const re = /href=["']([^"']+)["']/gi;
  let m;
  while ((m = re.exec(html || ''))) {
    const href = String(m[1] || '').trim();
    if (!href || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#') || href.startsWith('javascript:')) continue;
    let abs = '';
    if (/^https?:\/\//i.test(href)) abs = href;
    else if (href.startsWith('/')) abs = `${baseRoot}${href}`;
    else abs = `${baseRoot}/${href.replace(/^\.?\//, '')}`;
    const absDomain = domainFromUrl(abs);
    if (!absDomain || absDomain !== baseDomain) continue;
    const path = abs.replace(/^https?:\/\/[^/]+/i, '').toLowerCase();
    if (/(about|about-us|contact|contacts|locations|location|stores?|dispensary|dispensaries|menu|product|products|shop|brands?|brand|company|team|leadership|management|our-story|services|solutions|industries|compliance|regulatory|cannabis|weed|hemp|thc|cbd|medical|recreational|licensed|license|cultivation|delivery)/.test(path)) out.push(abs);
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
function deterministicSnippet(companyName, state, signals) {
  if (!state || !signals.length) return '';
  return `Based on our research into ${companyName}'s ${state} market presence, the site shows active cannabis-related product marketing. For a company like ${companyName}, that usually means stable, compliant visibility matters if you want to keep momentum.`;
}
function researchConfidence(state, cannabisSignals, companyName, combinedText) {
  const hasCompanyName = combinedText.toLowerCase().includes(companyName.toLowerCase());
  if (state && cannabisSignals.length && hasCompanyName) return 'high';
  if (state || cannabisSignals.length) return 'medium';
  return 'low';
}
function buildResearchSeed(company, cacheHit) {
  const cache = cacheHit || {};
  const companyName = cache.company_name || company.company_name || company.company_domain_key;
  const urls = [];
  for (const row of company.rows) {
    const u = firstUrl(row.company_non_linkedin_urls) || firstUrl(row.location_non_linkedin_urls) || firstUrl(row.company_linkedin_urls) || firstUrl(row.location_linkedin_urls);
    if (u) urls.push(u.startsWith('http') ? u : `https://${u}`);
  }
  if (!urls.length && looksLikeResearchableDomain(company.company_domain_key) && !isReusableCache(cache)) {
    urls.push(`https://${normalizeDomain(company.company_domain_key)}`);
  }
  const uniqueUrls = Array.from(new Set(urls)).slice(0, MAX_WEBSITE_PAGES);
  return {
    companyName,
    urls: uniqueUrls,
    cache,
    base: {
      company_domain_key: company.company_domain_key,
      company_name: companyName,
      company_operating_state: cache.company_operating_state || '',
      company_operating_market_note: cache.company_operating_market_note || '',
      company_cannabis_marketing_signal: cache.company_cannabis_marketing_signal || '',
      company_research_snippet: cache.company_research_snippet || '',
      company_research_confidence: cache.company_research_confidence || 'low',
      company_research_source: cache.company_research_source || '',
      company_research_last_verified_at: cache.company_research_last_verified_at || '',
    },
  };
}

async function researchCompany(company, cacheHit) {
  const seed = buildResearchSeed(company, cacheHit);
  const cacheReusable = isReusableCache(seed.cache);
  const emailDomain = domainFromEmail(company.rows?.[0]?.email || '');
  const businessUrl = resolveBusinessUrl(company);
  const institutional = companyLooksInstitutional(seed.companyName, emailDomain || company.company_domain_key);
  const businessOverride = hasBusinessOverrideSignal(company, businessUrl);
  if (cacheReusable) {
    return {
      companyName: seed.companyName,
      evidencePages: [],
      deterministic: {
        companyName: seed.companyName,
        company_operating_state: seed.cache.company_operating_state || '',
        company_operating_market_note: seed.cache.company_operating_market_note || '',
        company_cannabis_marketing_signal: seed.cache.company_cannabis_marketing_signal || '',
        company_research_snippet: seed.cache.company_research_snippet || '',
        company_research_confidence: seed.cache.company_research_confidence || 'low',
        company_research_source: seed.cache.company_research_source || '',
      },
      researchMode: 'cache_only',
      cache: seed.cache,
    };
  }
  if (institutional && !businessOverride) {
    return {
      companyName: seed.companyName,
      evidencePages: [],
      deterministic: {
        companyName: seed.companyName,
        company_operating_state: '',
        company_operating_market_note: '',
        company_cannabis_marketing_signal: '',
        company_research_snippet: '',
        company_research_confidence: 'low',
        company_research_source: 'skipped_institutional_domain',
      },
      researchMode: 'skip_institutional',
      cache: seed.cache,
    };
  }
  const evidencePages = [];
  for (const url of seed.urls.slice(0, MAX_WEBSITE_PAGES)) {
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

  const combinedText = [seed.companyName, ...evidencePages.map((p) => `${p.title} ${p.text} ${p.url}`)].join(' | ');
  const state = detectState(combinedText);
  const cannabisSignals = detectCannabisSignals(combinedText);
  const confidence = researchConfidence(state, cannabisSignals, seed.companyName, combinedText);
  const marketNote = state ? `Website evidence ties ${seed.companyName} to ${state}.` : '';
  const signalText = cannabisSignals.length ? cannabisSignals.join(', ') : '';
  const deterministic = {
    companyName: seed.companyName,
    company_operating_state: state,
    company_operating_market_note: marketNote,
    company_cannabis_marketing_signal: signalText,
    company_research_snippet: deterministicSnippet(seed.companyName, state, cannabisSignals),
    company_research_confidence: confidence,
    company_research_source: evidencePages.length ? 'website+heuristic' : 'no_website_evidence',
  };

  return {
    companyName: seed.companyName,
    evidencePages,
    deterministic,
    researchMode: evidencePages.length
      ? 'website'
      : 'deterministic_only',
    cache: seed.cache,
  };
}

function buildResearchMessages(company) {
  const payload = {
    company_name: company.companyName,
    company_domain_key: company.company_domain_key,
    evidence_pages: company.evidencePages.map((p) => ({ url: p.url, title: p.title, text: p.text.slice(0, 3500) })),
    deterministic: company.deterministic,
    rules: [
      'Use only evidence provided.',
      'Do not infer company geography from the contact state.',
      'If operating state is not explicit in evidence, leave it blank.',
      'If cannabis-product marketing is not explicit, leave the signal blank.',
      'Output JSON only.',
    ],
  };

  return [
    { role: 'system', content: 'You are a factual company research synthesizer. Return compact JSON only with keys: company_operating_state, company_operating_market_note, company_cannabis_marketing_signal, company_research_snippet, company_research_confidence, company_research_source. Do not explain. Do not reason step-by-step. Do not add commentary. If evidence is weak, leave fields blank and keep the snippet very short.' },
    { role: 'user', content: JSON.stringify(payload) },
  ];
}

const companyItems = Array.isArray(payload.companies) ? payload.companies : [];
const cacheByKey = new Map(cacheRows.map((r) => [normalizeDomain(r.company_domain_key), r]));
const outputs = [];

for (const company of companyItems) {
  const cached = cacheByKey.get(normalizeDomain(company.company_domain_key)) || null;
  const research = await researchCompany.call(this, company, cached);
  const rowCount = Array.isArray(company.rows) ? company.rows.length : 0;

  outputs.push({
    json: {
      company_domain_key: company.company_domain_key,
      company_name: company.company_name || research.companyName || company.company_domain_key,
      rowCount,
      cacheHit: isReusableCache(cached),
      cacheRowExists: !!cached,
      cached_company_research_confidence: cached?.company_research_confidence || '',
      evidencePages: research.evidencePages,
      deterministic: research.deterministic,
      researchMessages: buildResearchMessages({
        company_domain_key: company.company_domain_key,
        companyName: research.companyName || company.company_name || company.company_domain_key,
        evidencePages: research.evidencePages,
        deterministic: research.deterministic,
      }),
      rows: company.rows,
      companyCacheRow: cached || null,
      researchMode: research.researchMode,
    },
  });
}

return outputs.length ? outputs : [{ json: { ok: true, batchCount: 0, companyCount: 0, note: 'No pending executive SSO rows found.' } }];
