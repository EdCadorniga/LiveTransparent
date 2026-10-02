// LT - LinkedIn Connected Tag Sync - idempotent daily tag reconciliation
// Ensures GHL contacts for connected/completed LinkedIn state rows carry
// linkedin_connected (main) / partner_linkedin_connected (partnership).
// Read-mostly: GET then conditional POST. Sends no LinkedIn messages.
const { Client } = require('pg');

const cfg = $item(0).$node['Config'].json || {};
const ghlApiBaseUrl = String(cfg.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/$/, '');
const ghlApiKey = String(cfg.ghlApiKey || '').trim();
const mainTag = String(cfg.mainTag || 'linkedin_connected').trim();
const partnerTag = String(cfg.partnerTag || 'partner_linkedin_connected').trim();
const maxPerRun = Number(cfg.maxPerRun || 800);
const delayMs = Number(cfg.delayMs || 120);
const dryRun = cfg.dryRun === true || String(cfg.dryRun) === 'true';
if (!ghlApiKey) throw new Error('Missing GHL api key in Config');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const clean = (v) => (v == null ? '' : String(v).trim());
const statusOf = (err) => Number(
  (err && (err.statusCode || err.httpCode || err.status
    || (err.response && (err.response.statusCode || err.response.status || (err.response.body && err.response.body.statusCode)))
    || (err.cause && err.cause.statusCode))) || 0
) || 0;
const stats = { scanned: 0, already: 0, tagged: 0, failed: 0, not_found: 0, errors: 0, error_sample: [] };

async function httpReq(method, url, headers, body) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      const opts = { method, url, headers, json: true, timeout: 30000 };
      if (body !== undefined) opts.body = body;
      return { ok: true, status: 200, data: await this.helpers.httpRequest(opts) };
    } catch (err) {
      const status = statusOf(err);
      const transient = status === 429 || (status >= 500 && status <= 599) || status === 0;
      if (!transient || attempt === 3) {
        return { ok: false, status, data: clean(err && (err.message || (err.response && err.response.body))) };
      }
      await sleep(400 * (attempt + 1));
    }
  }
  return { ok: false, status: 599, data: 'retry_exhausted' };
}

const UNION_SQL = `
WITH base AS (
  SELECT ghl_contact_id AS cid, connection_status, false AS partnership
  FROM linkedin_connection_state
  WHERE connection_status IN ('connected','completed') AND ghl_contact_id NOT LIKE 'linkedin:%'
  UNION ALL
  SELECT i.ghl_contact_id AS cid, s.connection_status, false AS partnership
  FROM linkedin_connection_state s
  JOIN linkedin_contact_profile_index i
    ON (i.normalized_profile_slug = s.linkedin_public_identifier
        OR (COALESCE(s.linkedin_provider_id, '') <> '' AND s.linkedin_provider_id = ANY(i.linkedin_provider_ids)))
  WHERE s.connection_status IN ('connected','completed') AND s.ghl_contact_id LIKE 'linkedin:%'
  UNION ALL
  SELECT ghl_contact_id AS cid, connection_status, true AS partnership
  FROM partnership_linkedin_connection_state
  WHERE connection_status IN ('connected','completed') AND ghl_contact_id NOT LIKE 'linkedin:%'
)
SELECT cid, bool_or(partnership) AS partnership, bool_or(connection_status = 'completed') AS completed
FROM base
WHERE cid IS NOT NULL AND cid <> '' AND cid NOT LIKE 'linkedin:%'
GROUP BY cid
ORDER BY cid
LIMIT $1;
`;

const client = new Client({
  host: String(cfg.pgHost || 'postgres'),
  port: Number(cfg.pgPort || 5432),
  database: String(cfg.pgDatabase || 'postgres'),
  user: String(cfg.pgUser || 'postgres'),
  password: String(cfg.pgPassword || ''),
});

let rows = [];
try {
  await client.connect();
  const res = await client.query(UNION_SQL, [maxPerRun]);
  rows = res.rows || [];
} finally {
  try { await client.end(); } catch (e) { /* ignore */ }
}

for (const row of rows) {
  stats.scanned += 1;
  const cid = clean(row.cid);
  const tag = row.partnership === true ? partnerTag : mainTag;
  const got = await httpReq.call(this, 'GET', `${ghlApiBaseUrl}/contacts/${encodeURIComponent(cid)}`, {
    Authorization: `Bearer ${ghlApiKey}`, Version: '2021-07-28', Accept: 'application/json',
  });
  if (got.status === 404) { stats.not_found += 1; await sleep(delayMs); continue; }
  if (!got.ok) {
    stats.errors += 1;
    if (stats.error_sample.length < 10) stats.error_sample.push({ cid, stage: 'get', status: got.status, error: String(got.data).slice(0, 160) });
    await sleep(delayMs); continue;
  }
  const contact = got.data && got.data.contact ? got.data.contact : got.data;
  const tags = new Set(Array.isArray(contact && contact.tags) ? contact.tags : []);
  if (tags.has(tag)) { stats.already += 1; await sleep(Math.min(delayMs, 60)); continue; }
  if (dryRun) { stats.tagged += 1; await sleep(Math.min(delayMs, 60)); continue; }
  const added = await httpReq.call(this, 'POST', `${ghlApiBaseUrl}/contacts/${encodeURIComponent(cid)}/tags`, {
    Authorization: `Bearer ${ghlApiKey}`, Version: '2021-07-28', Accept: 'application/json', 'Content-Type': 'application/json',
  }, { tags: [tag] });
  const newTags = new Set(Array.isArray(added.data && added.data.tags) ? added.data.tags : []);
  if ((added.status === 200 || added.status === 201) && (newTags.size === 0 || newTags.has(tag))) {
    stats.tagged += 1;
  } else {
    stats.failed += 1;
    if (stats.error_sample.length < 10) stats.error_sample.push({ cid, stage: 'tag', status: added.status, error: String(added.data).slice(0, 160) });
  }
  await sleep(delayMs);
}

return [{ json: {
  ok: stats.errors === 0 && stats.failed === 0,
  scanned: stats.scanned,
  already_tagged: stats.already,
  tagged: stats.tagged,
  failed: stats.failed,
  not_found: stats.not_found,
  errors: stats.errors,
  dry_run: dryRun,
  error_sample: stats.error_sample,
} }];
