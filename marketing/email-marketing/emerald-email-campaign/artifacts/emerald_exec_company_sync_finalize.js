const currentItem = $input.item || { json: $json || {} };
const pairedIndex = Number(
  currentItem?.pairedItem?.item ??
  currentItem?.pairedItem ??
  0,
);
const cfg = $item(0).$node['Config'].json || {};
const prep = ($items('Prepare Company Research')[pairedIndex] || {}).json || {};
const parsedResearch = ($items('Parse Research Response')[pairedIndex] || {}).json || {};
const companyItems = Array.isArray(prep.rows) ? [prep] : [];
const researchFieldName = String(cfg.researchFieldName || 'emerald_exec_sso_ai_research').trim();
const companyNameForEmailsFieldName = String(cfg.companyNameForEmailsFieldName || 'Company Name for Emails').trim();
const companyOperatingStateFieldName = String(cfg.companyOperatingStateFieldName || 'Em_Company_Operating_State').trim();
const companyResearchSnippetFieldName = String(cfg.companyResearchSnippetFieldName || 'Em_Company_Research_Snippet').trim();
const companyMarketNoteFieldName = String(cfg.companyMarketNoteFieldName || 'Em_Company_Market_Note').trim();
const cannabisMarketingSignalFieldName = String(cfg.cannabisMarketingSignalFieldName || 'Em_Cannabis_Marketing_Signal').trim();
const email4ReadyFieldName = String(cfg.email4ReadyFieldName || 'Em_Email4_Personalization_Ready').trim();
const email4ReasonFieldName = String(cfg.email4ReasonFieldName || 'Em_Email4_Personalization_Reason').trim();

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
function domainFromEmail(email) {
  const v = str(email).toLowerCase();
  const i = v.lastIndexOf('@');
  if (i < 0) return '';
  return normalizeDomain(v.slice(i + 1));
}
const genericDomains = new Set([
  'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
  'aol.com', 'live.com', 'proton.me', 'protonmail.com', 'me.com', 'mail.com',
  'twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com',
  'tiktok.com', 'youtube.com',
]);
const institutionalTerms = ['university', 'college', 'school', 'faculty', 'campus', 'institute', 'academy'];
const cannabisTerms = ['cannabis', 'marijuana', 'dispensary', 'weed', 'thc', 'hemp', 'cbd', 'edibles', 'flower', 'preroll', 'pre-roll', 'vape', 'concentrate', 'rosin', 'tincture', 'gummies', 'retail'];
function isGenericDomain(domain) {
  return genericDomains.has(normalizeDomain(domain));
}
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
function isInstitutionalCompany(companyDomainKey, companyName) {
  return isAcademicDomain(companyDomainKey) || institutionalTerms.some((term) => str(companyName).toLowerCase().includes(term));
}
function textHasCannabisTerms(value) {
  const hay = str(value).toLowerCase();
  return cannabisTerms.some((term) => hay.includes(term));
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
function firstUrl(value) {
  const raw = String(value || '').trim();
  if (!raw) return '';
  const parts = raw.split(/[\s,;|]+/).map((p) => p.trim()).filter(Boolean);
  const candidate = parts.find((p) => /^https?:\/\//i.test(p) || /^[a-z0-9.-]+\.[a-z]{2,}/i.test(p));
  return candidate || '';
}
function isMissing(v) { return v === null || v === undefined || String(v).trim() === ''; }
function allowedResearchText(text) {
  const bad = ['probably', 'maybe', 'likely', 'appears to be', 'seems to be'];
  const hay = String(text || '').toLowerCase();
  return !bad.some((b) => hay.includes(b));
}

async function doHttpRequest(options) {
  if (typeof $httpRequest === 'function') return await $httpRequest(options);
  if (this?.helpers?.httpRequest) return await this.helpers.httpRequest(options);
  throw new Error('HTTP helper not available');
}
async function apiRequest({ baseUrl, method, path, headers, body, fullUrl, json = true }) {
  const resolvedBase = str(baseUrl || cfg.apiBaseUrl || 'https://services.leadconnectorhq.com');
  const options = { method, url: fullUrl || `${resolvedBase.replace(/\/$/, '')}${path}`, headers, json };
  if (body !== undefined) options.body = body;
  try {
    const data = await doHttpRequest.call(this, options);
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      status: err?.statusCode || err?.httpCode || err?.cause?.statusCode || 500,
      data: err?.response?.body || err?.message || err,
    };
  }
}

const ghlHeaders = {
  Authorization: `Bearer ${cfg.apiKey}`,
  Version: '2021-07-28',
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

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

let contactFieldIds = null;
async function ensureContactFieldIds() {
  if (contactFieldIds) return contactFieldIds;
  const cf = await apiRequest.call(this, { method: 'GET', path: `/locations/${encodeURIComponent(cfg.locationId)}/customFields?model=contact`, headers: ghlHeaders });
  if (!cf.ok) throw new Error(`Failed custom fields lookup: ${JSON.stringify(cf.data)}`);
  const arr = Array.isArray(cf.data?.customFields)
    ? cf.data.customFields
    : Array.isArray(cf.data?.data?.customFields)
      ? cf.data.data.customFields
      : Array.isArray(cf.data?.data)
        ? cf.data.data
        : [];
  const findId = (fieldName, required = false) => {
    const id = arr.find((f) => String(f?.name || '').trim() === fieldName)?.id || '';
    if (!id && required) throw new Error(`Missing GHL field: ${fieldName}`);
    return id;
  };
  contactFieldIds = {
    researchDone: findId(researchFieldName, true),
    companyNameForEmails: findId(companyNameForEmailsFieldName, false),
    companyOperatingState: findId(companyOperatingStateFieldName, false),
    companyResearchSnippet: findId(companyResearchSnippetFieldName, false),
    companyMarketNote: findId(companyMarketNoteFieldName, false),
    cannabisMarketingSignal: findId(cannabisMarketingSignalFieldName, false),
    email4Ready: findId(email4ReadyFieldName, false),
    email4Reason: findId(email4ReasonFieldName, false),
  };
  return contactFieldIds;
}

function determineEmail4Eligibility(companyDomainKey, companyName, rows, research) {
  const source = str(research.company_research_source).toLowerCase();
  const state = str(research.company_operating_state);
  const snippet = str(research.company_research_snippet);
  const signal = str(research.company_cannabis_marketing_signal);
  const combinedText = [
    companyDomainKey,
    companyName,
    signal,
    research.company_operating_market_note,
    snippet,
    ...(Array.isArray(rows)
      ? rows.map((row) => [
          row.company_name,
          row.company_non_linkedin_urls,
          row.location_non_linkedin_urls,
          row.company_linkedin_urls,
          row.location_linkedin_urls,
        ].map((v) => str(v)).join(' | '))
      : []),
  ].join(' | ');
  const hasCannabisContext = !!signal || textHasCannabisTerms(combinedText);
  if (source === 'skipped_institutional_domain') return { ready: 'No', reason: 'institutional_domain' };
  if (source !== 'website+heuristic') return { ready: 'No', reason: 'insufficient_website_evidence' };
  if (!state) return { ready: 'No', reason: 'missing_operating_state' };
  if (!snippet) return { ready: 'No', reason: 'missing_company_snippet' };
  if (!hasCannabisContext) return { ready: 'No', reason: 'no_cannabis_or_marketing_signal' };
  return { ready: 'Yes', reason: 'ready' };
}

function buildResearchCustomFields(fieldIds, companyName, research, email4Eligibility) {
  const out = [];
  const pushValue = (id, value, allowEmpty = false) => {
    if (!id) return;
    const stringValue = String(value ?? '').trim();
    if (!stringValue && !allowEmpty) return;
    out.push({ id, value: stringValue });
  };
  pushValue(fieldIds.researchDone, 'done', true);
  pushValue(fieldIds.companyNameForEmails, companyName, false);
  pushValue(fieldIds.companyOperatingState, research.company_operating_state || '', false);
  pushValue(fieldIds.companyResearchSnippet, research.company_research_snippet || '', false);
  pushValue(fieldIds.companyMarketNote, research.company_operating_market_note || '', false);
  pushValue(fieldIds.cannabisMarketingSignal, research.company_cannabis_marketing_signal || '', false);
  pushValue(fieldIds.email4Ready, email4Eligibility?.ready || 'No', true);
  pushValue(fieldIds.email4Reason, email4Eligibility?.reason || 'unknown', true);
  return out;
}

function getValidatedResearch() {
  const candidate = $json?.choices?.[0]?.message?.content || $json?.message?.content || '';
  if (!candidate) return null;
  try {
    return JSON.parse(candidate);
  } catch {
    return null;
  }
}

function normalizeResearch(source, fallback) {
  const out = {
    company_operating_state: str(source?.company_operating_state || fallback?.company_operating_state || ''),
    company_operating_market_note: str(source?.company_operating_market_note || fallback?.company_operating_market_note || ''),
    company_cannabis_marketing_signal: str(source?.company_cannabis_marketing_signal || fallback?.company_cannabis_marketing_signal || ''),
    company_research_snippet: str(source?.company_research_snippet || fallback?.company_research_snippet || ''),
    company_research_confidence: str(source?.company_research_confidence || fallback?.company_research_confidence || 'low'),
    company_research_source: str(source?.company_research_source || fallback?.company_research_source || ''),
  };
  if (!allowedResearchText(out.company_research_snippet)) out.company_research_snippet = '';
  return out;
}

function buildCompanyUpsertSql(company, research) {
  const rowIds = company.rows.map((r) => Number(r.emerald_row_id)).filter((n) => Number.isFinite(n));
  const rowCases = (field, valueFn) => {
    const cases = company.rows.map((row) => `WHEN ${Number(row.emerald_row_id)} THEN ${sqlLit(valueFn(row))}`).join(' ');
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
  const emailCase = rowCases('primary_email', (row) => row.resolved_email || row.email || '');
  const phoneCase = rowCases('primary_phone', (row) => row.resolved_phone || row.phone || '');
  const researchCase = rowCases('emerald_exec_sso_ai_research', () => 'done');

  return `WITH cache_upsert AS (
  INSERT INTO "Emerald_Company_Research_Cache" (
    company_domain_key,
    company_name,
    company_research_snippet,
    company_operating_state,
    company_operating_market_note,
    company_cannabis_marketing_signal,
    company_research_confidence,
    company_research_source,
    company_research_last_verified_at,
    created_at,
    updated_at
  ) VALUES (
    ${sqlLit(companyResearchSql.company_domain_key)},
    ${sqlLit(companyResearchSql.company_name)},
    ${sqlLit(companyResearchSql.company_research_snippet)},
    ${sqlLit(companyResearchSql.company_operating_state)},
    ${sqlLit(companyResearchSql.company_operating_market_note)},
    ${sqlLit(companyResearchSql.company_cannabis_marketing_signal)},
    ${sqlLit(companyResearchSql.company_research_confidence)},
    ${sqlLit(companyResearchSql.company_research_source)},
    ${sqlLit(companyResearchSql.company_research_last_verified_at)},
    NOW(),
    NOW()
  )
  ON CONFLICT (company_domain_key) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    company_research_snippet = EXCLUDED.company_research_snippet,
    company_operating_state = EXCLUDED.company_operating_state,
    company_operating_market_note = EXCLUDED.company_operating_market_note,
    company_cannabis_marketing_signal = EXCLUDED.company_cannabis_marketing_signal,
    company_research_confidence = EXCLUDED.company_research_confidence,
    company_research_source = EXCLUDED.company_research_source,
    company_research_last_verified_at = EXCLUDED.company_research_last_verified_at,
    updated_at = NOW()
)
UPDATE "Emerald_Contacts"
SET
  company_domain_key = ${sqlLit(company.company_domain_key)},
  company_name = COALESCE(NULLIF(company_name, ''), ${sqlLit(companyResearchSql.company_name)}),
  company_research_snippet = ${sqlLit(companyResearchSql.company_research_snippet)},
  company_operating_state = ${sqlLit(companyResearchSql.company_operating_state)},
  company_operating_market_note = ${sqlLit(companyResearchSql.company_operating_market_note)},
  company_cannabis_marketing_signal = ${sqlLit(companyResearchSql.company_cannabis_marketing_signal)},
  company_research_confidence = ${sqlLit(companyResearchSql.company_research_confidence)},
  company_research_source = ${sqlLit(companyResearchSql.company_research_source)},
  company_research_last_verified_at = ${sqlLit(companyResearchSql.company_research_last_verified_at)},
  ghl_contact_id = ${idCase},
  ghl_contact_match_method = ${methodCase},
  ghl_contact_sync_status = ${statusCase},
  ghl_contact_sync_error = ${errorCase},
  emerald_exec_sso_ai_research = ${researchCase},
  primary_email = ${emailCase},
  primary_phone = ${phoneCase},
  updated_at = NOW()
WHERE id IN (${rowIds.join(', ')});
`;
}

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
  const contactFieldIds = await ensureContactFieldIds.call(this);

  let contactId = str(row.ghl_contact_id || '');
  let matchMethod = contactId ? 'cached_ghl_contact_id' : '';
  let syncStatus = 'synced';
  let syncError = '';
  let resolvedEmail = str(row.email || '');
  let resolvedPhone = str(row.phone || '');
  const researchCustomFields = buildResearchCustomFields(contactFieldIds, companyName, parsedResearch?.research_json || {}, email4Eligibility);

  if (!contactId) {
    const tries = [];
    if (resolvedEmail) tries.push({ type: 'email', res: await apiRequest.call(this, { method: 'GET', path: `/contacts/search/duplicate?locationId=${encodeURIComponent(cfg.locationId)}&email=${encodeURIComponent(resolvedEmail)}`, headers: ghlHeaders }) });
    if (!contactId && resolvedPhone) tries.push({ type: 'phone', res: await apiRequest.call(this, { method: 'GET', path: `/contacts/search/duplicate?locationId=${encodeURIComponent(cfg.locationId)}&number=${encodeURIComponent(resolvedPhone)}`, headers: ghlHeaders }) });
    if (!contactId && fullName) tries.push({ type: 'name', res: await apiRequest.call(this, { method: 'GET', path: `/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(fullName)}&limit=20`, headers: ghlHeaders }) });
    if (!contactId && companyName) tries.push({ type: 'company', res: await apiRequest.call(this, { method: 'GET', path: `/contacts/?locationId=${encodeURIComponent(cfg.locationId)}&query=${encodeURIComponent(companyName)}&limit=20`, headers: ghlHeaders }) });

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
    const getRes = await apiRequest.call(this, { method: 'GET', path: `/contacts/${encodeURIComponent(contactId)}`, headers: ghlHeaders });
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
      const upd = await apiRequest.call(this, { method: 'PUT', path: `/contacts/${encodeURIComponent(contactId)}`, headers: ghlHeaders, body: updatePayload });
      if (!upd.ok) {
        syncStatus = 'error';
        syncError = str(upd.data?.message || JSON.stringify(upd.data));
      }
    }
    if (syncStatus === 'synced') {
      const researchDone = await apiRequest.call(this, {
        method: 'PUT',
        path: `/contacts/${encodeURIComponent(contactId)}`,
        headers: ghlHeaders,
        body: { customFields: researchCustomFields },
      });
      if (!researchDone.ok) {
        syncStatus = 'error';
        syncError = str(researchDone.data?.message || JSON.stringify(researchDone.data));
      }
    }
    resolvedEmail = resolvedEmail || str(contact.email || '');
    resolvedPhone = resolvedPhone || str(contact.phone || '');
  } else {
    const createPayload = { locationId: cfg.locationId, ...standard };
    let resp = null;
    if (resolvedEmail || resolvedPhone) {
      resp = await apiRequest.call(this, { method: 'POST', path: '/contacts/upsert', headers: ghlHeaders, body: createPayload });
      matchMethod = 'upsert';
    } else {
      resp = await apiRequest.call(this, { method: 'POST', path: '/contacts/', headers: ghlHeaders, body: createPayload });
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
      if (contactId && syncStatus === 'synced') {
        const researchDone = await apiRequest.call(this, {
          method: 'PUT',
          path: `/contacts/${encodeURIComponent(contactId)}`,
          headers: ghlHeaders,
          body: { customFields: researchCustomFields },
        });
        if (!researchDone.ok) {
          syncStatus = 'error';
          syncError = str(researchDone.data?.message || JSON.stringify(researchDone.data));
        }
      }
    }
  }

  if (!contactId) {
    syncStatus = 'error';
    syncError = syncError || 'No GHL contact id returned';
  }

  return { contactId, matchMethod, syncStatus, syncError, resolvedEmail, resolvedPhone };
}

async function listCompanyContactsForPropagation(companyDomainKey, companyName) {
  const byId = new Map();
  const terms = [];
  const domain = normalizeDomain(companyDomainKey);
  if (domain && !isGenericDomain(domain)) terms.push(domain);
  const company = str(companyName);
  if (company) terms.push(company);

  for (const term of terms) {
    let startAfterId = '';
    for (let page = 0; page < 20; page += 1) {
      const q = [
        `locationId=${encodeURIComponent(cfg.locationId)}`,
        `query=${encodeURIComponent(term)}`,
        'limit=100',
      ];
      if (startAfterId) q.push(`startAfterId=${encodeURIComponent(startAfterId)}`);
      const res = await apiRequest.call(this, {
        method: 'GET',
        path: `/contacts/?${q.join('&')}`,
        headers: ghlHeaders,
      });
      if (!res.ok) break;
      const list = asContacts(res.data);
      if (!list.length) break;
      for (const c of list) {
        const id = str(c.id);
        if (!id) continue;
        byId.set(id, c);
      }
      startAfterId = str(list[list.length - 1]?.id || '');
      if (!startAfterId || list.length < 100) break;
    }
  }

  const out = [];
  const normalizedCompany = str(companyName).toLowerCase();
  const normalizedDomain = normalizeDomain(companyDomainKey);
  for (const c of byId.values()) {
    const emailDomain = domainFromEmail(c.email || c.emailAddress || '');
    const cCompany = str(c.companyName || c.company || '').toLowerCase();
    const domainMatch = normalizedDomain && !isGenericDomain(normalizedDomain) && emailDomain === normalizedDomain;
    const companyMatch = normalizedCompany && cCompany && cCompany === normalizedCompany;
    if (domainMatch || companyMatch) out.push(c);
  }
  return out;
}

async function syncResearchForCompanyContacts(contacts, customFields) {
  let updated = 0;
  let failed = 0;
  const failedIds = [];
  for (const c of contacts) {
    const id = str(c.id);
    if (!id) continue;
    const upd = await apiRequest.call(this, {
      method: 'PUT',
      path: `/contacts/${encodeURIComponent(id)}`,
      headers: ghlHeaders,
      body: { customFields },
    });
    if (upd.ok) updated += 1;
    else {
      failed += 1;
      failedIds.push(id);
    }
  }
  return { updated, failed, failedIds };
}

function parseOpenRouterResponse(resp) {
  const content = resp?.choices?.[0]?.message?.content || resp?.message?.content || '';
  if (!content) return null;
  try {
    return JSON.parse(content);
  } catch {
    return null;
  }
}

const original = prep;
const researchFromParse = parsedResearch?.research_json || null;
const researchFromValidate = parseOpenRouterResponse($json);
const finalResearch = normalizeResearch(researchFromValidate || researchFromParse, original.deterministic || {});
const companyName = str(original.company_name || original.companyName || finalResearch.companyName || original.company_domain_key);
const companyRows = Array.isArray(original.rows) ? original.rows : [];
const email4Eligibility = determineEmail4Eligibility(original.company_domain_key, companyName, companyRows, finalResearch);

const rowResults = [];
for (const row of companyRows) {
  const result = await resolveGhlContact.call(this, row, companyName);
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

const allRowsSynced = rowResults.length > 0 && rowResults.every((r) => str(r.ghl_contact_sync_status).toLowerCase() === 'synced');
let propagatedDoneUpdated = 0;
let propagatedDoneFailed = 0;
let propagatedDoneCandidates = 0;
let propagatedDoneAttempted = false;
const shouldSkipPropagation =
  email4Eligibility.ready !== 'Yes' ||
  (
    isInstitutionalCompany(original.company_domain_key, companyName) &&
    !finalResearch.company_operating_state &&
    !finalResearch.company_research_snippet &&
    String(finalResearch.company_research_source || '').toLowerCase() !== 'website+heuristic'
  );
if (allRowsSynced && !shouldSkipPropagation) {
  const contactFieldIds = await ensureContactFieldIds.call(this);
  const companyContacts = await listCompanyContactsForPropagation.call(this, original.company_domain_key, companyName);
  propagatedDoneCandidates = companyContacts.length;
  const customFields = buildResearchCustomFields(contactFieldIds, companyName, finalResearch, email4Eligibility);
  const result = await syncResearchForCompanyContacts.call(this, companyContacts, customFields);
  propagatedDoneUpdated = result.updated;
  propagatedDoneFailed = result.failed;
  propagatedDoneAttempted = true;
}

const syncSql = buildCompanyUpsertSql({
  company_domain_key: original.company_domain_key,
  company_name: companyName,
  rows: rowResults,
}, {
  companyName,
  ...finalResearch,
});

return {
  json: {
    company_domain_key: original.company_domain_key,
    company_name: companyName,
    rowCount: companyRows.length,
    cacheHit: !!original.cacheHit,
    research_confidence: finalResearch.company_research_confidence,
    company_operating_state: finalResearch.company_operating_state || '',
    company_operating_market_note: finalResearch.company_operating_market_note || '',
    company_cannabis_marketing_signal: finalResearch.company_cannabis_marketing_signal || '',
    company_research_snippet: finalResearch.company_research_snippet || '',
    company_research_source: finalResearch.company_research_source || '',
    email4_personalization_ready: email4Eligibility.ready,
    email4_personalization_reason: email4Eligibility.reason,
    propagated_done_attempted: propagatedDoneAttempted,
    propagated_done_candidates: propagatedDoneCandidates,
    propagated_done_updated: propagatedDoneUpdated,
    propagated_done_failed: propagatedDoneFailed,
    syncSql,
  },
};
