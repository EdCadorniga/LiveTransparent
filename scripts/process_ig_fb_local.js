/*
 * Local Instagram/Facebook enrichment worker.
 *
 * Uses the existing clasp OAuth token for Google Sheets and the local
 * OPENROUTER_KEY_FOR_IG_AND_FB value for research. It has no contact-count or
 * Apps Script execution-time limit; each completed row is written immediately.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

const SPREADSHEET_ID = '19vRrNXxj2FmxxCKc-xGufk7mnMELgctE53urNY6VUg8';
const SHEET_NAME = 'brand_pool - IG & FB';
const MODEL = 'deepseek/deepseek-v4-flash';
const SLEEP_MS = 300;
const PROMPT_VERSION = 'v2';

function loadEnvValue(name) {
  const envPath = path.join(process.cwd(), '.env');
  if (!fs.existsSync(envPath)) return process.env[name] || '';
  const line = fs.readFileSync(envPath, 'utf8').split(/\r?\n/).find((entry) => {
    return entry.trim().startsWith(name + '=');
  });
  if (!line) return process.env[name] || '';
  return line.slice(name.length + 1).trim().replace(/^['"]|['"]$/g, '');
}

function readClaspAuth() {
  const authPath = path.join(os.homedir(), '.clasprc.json');
  const auth = JSON.parse(fs.readFileSync(authPath, 'utf8'));
  const token = auth.tokens && auth.tokens.default;
  if (!token || !token.refresh_token) throw new Error('No clasp refresh token was found.');
  return token;
}

async function getAccessToken() {
  const token = readClaspAuth();
  if (token.access_token && Number(token.expiry_date || 0) > Date.now() + 60000) {
    return token.access_token;
  }
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: token.client_id,
      client_secret: token.client_secret,
      refresh_token: token.refresh_token,
      grant_type: 'refresh_token'
    })
  });
  if (!response.ok) throw new Error('Google token refresh failed: ' + await response.text());
  return (await response.json()).access_token;
}

async function sheetsRequest(accessToken, url, options) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Authorization: 'Bearer ' + accessToken,
      ...(options && options.headers)
    }
  });
  if (!response.ok) throw new Error('Google Sheets request failed (' + response.status + '): ' + await response.text());
  return response.status === 204 ? null : response.json();
}

function quoteSheetName(name) {
  return "'" + name.replace(/'/g, "''") + "'";
}

function columnName(index) {
  let name = '';
  for (let value = index + 1; value > 0; value = Math.floor((value - 1) / 26)) {
    name = String.fromCharCode(65 + ((value - 1) % 26)) + name;
  }
  return name;
}

function normalizeHeader(value) {
  return String(value).toLowerCase().replace(/[\u2018\u2019]/g, "'").replace(/[^a-z0-9]+/g, ' ').trim();
}

function findHeader(headers, name) {
  return headers.findIndex((header) => normalizeHeader(header) === name);
}

async function getSheet(accessToken) {
  const url = 'https://sheets.googleapis.com/v4/spreadsheets/' + SPREADSHEET_ID +
    '?fields=sheets(properties(sheetId,title))';
  const data = await sheetsRequest(accessToken, url, { method: 'GET' });
  const sheet = (data.sheets || []).find((entry) => entry.properties.title === SHEET_NAME);
  if (!sheet) throw new Error('Sheet not found: ' + SHEET_NAME);
  return sheet.properties;
}

async function readValues(accessToken) {
  const range = encodeURIComponent(quoteSheetName(SHEET_NAME) + '!A:Z');
  const url = 'https://sheets.googleapis.com/v4/spreadsheets/' + SPREADSHEET_ID +
    '/values/' + range + '?majorDimension=ROWS';
  const data = await sheetsRequest(accessToken, url, { method: 'GET' });
  return data.values || [];
}

async function writeValues(accessToken, updates) {
  if (!updates.length) return;
  const url = 'https://sheets.googleapis.com/v4/spreadsheets/' + SPREADSHEET_ID +
    '/values:batchUpdate';
  await sheetsRequest(accessToken, url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ valueInputOption: 'RAW', data: updates })
  });
}

async function deleteColumns(accessToken, sheetId, indexes) {
  if (!indexes.length) return;
  const url = 'https://sheets.googleapis.com/v4/spreadsheets/' + SPREADSHEET_ID + ':batchUpdate';
  await sheetsRequest(accessToken, url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requests: indexes.sort((a, b) => b - a).map((index) => ({
      deleteDimension: {
        range: { sheetId, dimension: 'COLUMNS', startIndex: index, endIndex: index + 1 }
      }
    })) })
  });
}

async function deduplicateResearchColumns(accessToken, sheetId, values) {
  const headers = values[0] || [];
  const duplicateGroups = ['social research sources', 'social research status'].map((name) => {
    return headers.reduce((indexes, header, index) => {
      if (normalizeHeader(header) === name) indexes.push(index);
      return indexes;
    }, []);
  });
  const updates = [];
  const removeIndexes = [];
  duplicateGroups.forEach((indexes) => {
    if (indexes.length < 2) return;
    const primary = indexes[0];
    const merged = values.slice(1).map((row) => [row[primary] || indexes.slice(1).map((index) => row[index] || '').find(Boolean) || '']);
    updates.push({
      range: quoteSheetName(SHEET_NAME) + '!' + columnName(primary) + '2:' + columnName(primary) + (values.length),
      values: merged
    });
    removeIndexes.push(...indexes.slice(1));
  });
  await writeValues(accessToken, updates);
  await deleteColumns(accessToken, sheetId, removeIndexes);
}

function parseModelContent(content) {
  const cleaned = String(content).replace(/^```json\s*/i, '').replace(/\s*```$/, '').trim();
  return JSON.parse(cleaned);
}

function normalizeHandle(value, platform) {
  if (!value || typeof value !== 'string') return '';
  const handle = value.trim().replace(/^@/, '').replace(/^https?:\/\/[^/]+\//i, '').split(/[/?#]/)[0].toLowerCase();
  const valid = platform === 'instagram' ? /^[a-z0-9._]+$/i : /^[a-z0-9._-]+$/i;
  return valid.test(handle) ? handle : '';
}

async function research(apiKey, businessName, tag) {
  const prompt = [
    'Research the official public Instagram account and Facebook Page for this company.',
    'Company: ' + businessName,
    'GHL Tag: ' + (tag || 'none'),
    '',
    'Use web search for every company. Search the exact name plus Instagram, Facebook, official website, cannabis, dispensary, and brand variations when relevant.',
    'Inspect the official website and cross-check links and branding.',
    'Reject employee, personal, fan, directory, reseller, and unrelated similarly named profiles.',
    'Return the strongest supported company-page candidates for human review. Never invent a handle.',
    'Return JSON only: {"instagram_username":null,"facebook_page_handle":null,"confidence":"high|medium|low|none","reason":"short evidence"}'
  ].join('\n');
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + apiKey,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://livetransparent.com',
      'X-Title': 'LiveTransparent Social Enrichment'
    },
    body: JSON.stringify({
      model: MODEL,
      plugins: [{ id: 'web' }],
      temperature: 0,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: 'You are a cautious company social-profile research assistant with web search.' },
        { role: 'user', content: prompt }
      ]
    })
  });
  if (!response.ok) throw new Error('OpenRouter failed (' + response.status + '): ' + await response.text());
  const data = await response.json();
  const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
  if (!content) throw new Error('OpenRouter returned no content.');
  return parseModelContent(content);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const apiKey = loadEnvValue('OPENROUTER_KEY_FOR_IG_AND_FB');
  if (!apiKey) throw new Error('OPENROUTER_KEY_FOR_IG_AND_FB was not found in .env or the environment.');
  const accessToken = await getAccessToken();
  const sheet = await getSheet(accessToken);
  let values = await readValues(accessToken);
  if (values.length < 2) throw new Error('The target sheet has no data rows.');

  await deduplicateResearchColumns(accessToken, sheet.sheetId, values);
  values = await readValues(accessToken);
  const headers = values[0] || [];
  const businessIndex = 0;
  const instagramIndex = findHeader(headers, 'instagram handle');
  const facebookIndex = findHeader(headers, 'facebook handle');
  const tagIndex = findHeader(headers, 'ghl tag');
  const sourceIndex = findHeader(headers, 'social research sources');
  const statusIndex = findHeader(headers, 'social research status');
  if (normalizeHeader(headers[0]) !== 'business name') throw new Error('Column A must be Business Name.');
  if (instagramIndex < 0 || facebookIndex < 0 || sourceIndex < 0 || statusIndex < 0) {
    throw new Error('Required target columns are missing after cleanup.');
  }

  let processed = 0;
  let skipped = 0;
  for (let rowIndex = 1; rowIndex < values.length; rowIndex++) {
    const row = values[rowIndex];
    const instagram = String(row[instagramIndex] || '').trim();
    const facebook = String(row[facebookIndex] || '').trim();
    const marker = String(row[sourceIndex] || row[statusIndex] || '').trim().toLowerCase();
    if (instagram || facebook || marker === 'openrouter_no_match_v2' || marker === 'candidate_found_review_required') {
      skipped++;
      continue;
    }
    const businessName = String(row[businessIndex] || '').trim();
    if (!businessName) continue;
    const tag = tagIndex < 0 ? '' : String(row[tagIndex] || '').trim();
    try {
      const result = await research(apiKey, businessName, tag);
      const nextInstagram = normalizeHandle(result.instagram_username, 'instagram');
      const nextFacebook = normalizeHandle(result.facebook_page_handle, 'facebook');
      const status = nextInstagram || nextFacebook ? 'candidate_found_review_required' : 'openrouter_no_match_v2';
      await writeValues(accessToken, [
        ...(nextInstagram && !instagram ? [{ range: quoteSheetName(SHEET_NAME) + '!' + columnName(instagramIndex) + (rowIndex + 1), values: [[nextInstagram]] }] : []),
        ...(nextFacebook && !facebook ? [{ range: quoteSheetName(SHEET_NAME) + '!' + columnName(facebookIndex) + (rowIndex + 1), values: [[nextFacebook]] }] : []),
        { range: quoteSheetName(SHEET_NAME) + '!' + columnName(statusIndex) + (rowIndex + 1), values: [[status]] },
        { range: quoteSheetName(SHEET_NAME) + '!' + columnName(sourceIndex) + (rowIndex + 1), values: [[status === 'candidate_found_review_required' ? 'openrouter_web_research_v' + PROMPT_VERSION : status]] }
      ]);
      processed++;
      console.log('Processed row ' + (rowIndex + 1) + ': ' + businessName + ' -> ' + status);
    } catch (error) {
      console.error('Failed row ' + (rowIndex + 1) + ' (' + businessName + '): ' + error.message);
    }
    await sleep(SLEEP_MS);
  }
  console.log('Completed. Processed: ' + processed + ', skipped: ' + skipped + ', total rows: ' + (values.length - 1));
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exitCode = 1;
});
