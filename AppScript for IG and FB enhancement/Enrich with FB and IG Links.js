/**
 * Read-only source enrichment for company Instagram and Facebook candidates.
 *
 * This does not write GHL fields or send messages. It extracts normalized
 * candidates from the source URL columns so they can be reviewed and later
 * validated against Unipile/native Messenger before any outreach.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Social Enrichment')
    .addItem('Extract IG/FB candidates', 'extractSocialCandidates')
    .addItem('Research next 4.5-minute batch', 'researchUnresolvedRows')
    .addToUi();
}

var OPENROUTER_DEFAULT_MODEL = 'deepseek/deepseek-v4-flash';
var OPENROUTER_MAX_ROWS_PER_RUN = 0; // 0 means no contact-count limit.
var OPENROUTER_MAX_RUNTIME_MS = 270000;
var OPENROUTER_PROMPT_VERSION = 'v2';
var OPENROUTER_SLEEP_MS = 300;
var TARGET_SHEET_NAME = 'brand_pool - IG & FB';
var RESEARCH_TRIGGER_HANDLER = 'researchUnresolvedRows';

function getProcessingSheet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(TARGET_SHEET_NAME);
  if (!sheet) throw new Error('Sheet not found: ' + TARGET_SHEET_NAME);
  return sheet;
}

function startAutomaticProcessing() {
  getProcessingSheet();
  stopAutomaticProcessing();
  researchUnresolvedRows();
}

function processEntireList() {
  stopAutomaticProcessing();
  researchUnresolvedRows();
}

function stopAutomaticProcessing() {
  ScriptApp.getProjectTriggers().forEach(function(trigger) {
    if (trigger.getHandlerFunction() === RESEARCH_TRIGGER_HANDLER) {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function reportRun(message) {
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (error) {
    Logger.log(message);
  }
}

function extractSocialCandidates() {
  var sheet = getProcessingSheet();
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    throw new Error('The active sheet must contain a header row and at least one data row.');
  }

  var headers = values[0].map(function(header) {
    return normalizeHeader(String(header));
  });
  var sourceIndexes = findSourceColumns(headers);
  if (!sourceIndexes.length) {
    SpreadsheetApp.getUi().alert(
      'No approved non-LinkedIn URL columns were found. Use Research unresolved rows with OpenRouter for this sheet.'
    );
    return;
  }

  var outputColumns = [
    'Candidate Company Instagram Username',
    'Candidate Company Instagram Profile URL',
    'Candidate Company Facebook Page Handle',
    'Candidate Company Facebook Page URL',
    'Social Candidate Status',
    'Social Candidate Sources'
  ];
  var outputIndexes = ensureColumns(sheet, values[0], outputColumns);
  var output = [];

  for (var rowIndex = 1; rowIndex < values.length; rowIndex++) {
    var urls = [];
    sourceIndexes.forEach(function(columnIndex) {
      urls = urls.concat(extractUrls(
        String(values[rowIndex][columnIndex] || ''),
        headers[columnIndex]
      ));
    });

    var instagram = uniqueCandidates(urls.map(extractInstagram).filter(Boolean));
    var facebook = uniqueCandidates(urls.map(extractFacebook).filter(Boolean));
    var status = getCandidateStatus(instagram, facebook);
    var sources = uniqueCandidates(urls.map(function(candidate) {
      return candidate.sourceColumn + ': ' + candidate.platform;
    }).filter(Boolean));

    output.push([
      instagram.length === 1 ? instagram[0].handle : '',
      instagram.length === 1 ? instagram[0].url : '',
      facebook.length === 1 ? facebook[0].handle : '',
      facebook.length === 1 ? facebook[0].url : '',
      status,
      sources.join(', ')
    ]);
  }

  outputIndexes.forEach(function(columnIndex, outputIndex) {
    if (output.length) {
      sheet.getRange(2, columnIndex + 1, output.length, 1)
        .setValues(output.map(function(row) { return [row[outputIndex]]; }));
    }
  });
  SpreadsheetApp.getUi().alert('Social candidates extracted for ' + output.length + ' rows.');
}

function normalizeHeader(value) {
  return value.toLowerCase().replace(/[\u2018\u2019]/g, "'").replace(/[^a-z0-9]+/g, ' ').trim();
}

function findSourceColumns(headers) {
  var names = [
    'company non linkedin url s',
    'company non linkedin urls',
    'location non linkedin url s',
    'location non linkedin urls',
    'contact non linkedin url s',
    'contact non linkedin urls'
  ];
  return headers.reduce(function(indexes, header, index) {
    if (names.indexOf(header) !== -1) indexes.push(index);
    return indexes;
  }, []);
}

function ensureColumns(sheet, currentHeaders, names) {
  var headers = currentHeaders.map(function(header) {
    return normalizeHeader(String(header));
  });
  names.forEach(function(name) {
    var index = headers.indexOf(normalizeHeader(name));
    if (index === -1) {
      index = headers.length;
      headers.push(normalizeHeader(name));
      sheet.getRange(1, index + 1).setValue(name);
    }
  });
  return names.map(function(name) { return headers.indexOf(normalizeHeader(name)); });
}

function extractUrls(value, sourceColumn) {
  var matches = value.match(/https?:\/\/[^\s,;|]+/gi) || [];
  return matches.map(function(url) {
    return {
      url: normalizeUrl(url.replace(/[\])}>.,!?]+$/, '')),
      sourceColumn: sourceColumn
    };
  }).filter(function(candidate) { return candidate.url; });
}

function normalizeUrl(url) {
  var cleaned = url.trim().replace(/[?#].*$/, '').replace(/\/+$/, '');
  return cleaned.replace(/^http:\/\//i, 'https://').replace(/^https:\/\/www\./i, 'https://');
}

function extractInstagram(candidate) {
  var match = candidate.url.match(/^https:\/\/(?:www\.)?instagram\.com\/([^/]+)/i);
  if (!match) return null;
  var handle = match[1].replace(/^@/, '').toLowerCase();
  if (!handle || /^(p|reel|reels|tv|stories|explore|accounts|direct|about|privacy|terms)$/i.test(handle)) return null;
  if (!/^[a-z0-9._]+$/i.test(handle)) return null;
  return {
    handle: handle,
    url: 'https://www.instagram.com/' + handle,
    platform: 'instagram',
    sourceColumn: candidate.sourceColumn
  };
}

function extractFacebook(candidate) {
  var match = candidate.url.match(/^https:\/\/(?:[a-z]+\.)?(?:facebook\.com|fb\.com)\/([^/]+)/i);
  if (!match) return null;
  var handle = match[1].replace(/^@/, '').toLowerCase();
  if (!handle || /^(profile\.php|people|groups|share|sharer|dialog|plugins|events|marketplace|watch|reel|reels|stories|login)$/i.test(handle)) return null;
  if (!/^[a-z0-9._-]+$/i.test(handle)) return null;
  return {
    handle: handle,
    url: 'https://www.facebook.com/' + handle,
    platform: 'facebook',
    sourceColumn: candidate.sourceColumn
  };
}

function uniqueCandidates(candidates) {
  var seen = Object.create(null);
  return candidates.filter(function(candidate) {
    var key = String(candidate.handle || candidate).toLowerCase();
    if (seen[key]) return false;
    seen[key] = true;
    return true;
  });
}

function getCandidateStatus(instagram, facebook) {
  if (instagram.length > 1 || facebook.length > 1) return 'ambiguous';
  if (instagram.length || facebook.length) return 'candidate_found_review_required';
  return 'unresolved';
}

function researchUnresolvedRows() {
  var apiKey = PropertiesService.getScriptProperties().getProperty('OPENROUTER_API_KEY');
  if (!apiKey) throw new Error('Script property OPENROUTER_API_KEY is not configured.');

  var sheet = getProcessingSheet();
  deduplicateResearchColumns(sheet);
  var lastRow = sheet.getLastRow();
  var lastColumn = sheet.getLastColumn();
  var values = lastRow && lastColumn
    ? sheet.getRange(1, 1, lastRow, lastColumn).getValues()
    : [];
  if (values.length < 2) throw new Error('The active sheet must contain data rows.');

  var headers = values[0].map(function(header) { return normalizeHeader(String(header)); });
  var businessIndex = 0;
  var instagramIndex = findFirstColumn(headers, ['instagram handle']);
  var facebookIndex = findFirstColumn(headers, ['facebook handle']);
  var tagIndex = findFirstColumn(headers, ['ghl tag']);
  var trackingIndexes = ensureColumns(sheet, values[0], [
    'Social Research Status',
    'Social Research Sources'
  ]);
  var statusIndex = trackingIndexes[0];
  var sourceIndex = trackingIndexes[1];
  var sourceIndexes = findSourceColumns(headers);
  if (headers[businessIndex] !== 'business name') {
    throw new Error('Column A must be named Business Name.');
  }
  if (instagramIndex === -1 || facebookIndex === -1) {
    throw new Error('The sheet must contain Instagram handle and Facebook handle columns.');
  }

  var researched = 0;
  var skipped = 0;
  var blankBusinessNames = 0;
  var scanned = 0;
  var startedAt = Date.now();
  for (
    var rowIndex = 1;
    rowIndex < values.length &&
      (!OPENROUTER_MAX_ROWS_PER_RUN || researched < OPENROUTER_MAX_ROWS_PER_RUN) &&
      Date.now() - startedAt < OPENROUTER_MAX_RUNTIME_MS;
    rowIndex++
  ) {
    scanned++;
    var existingInstagram = String(values[rowIndex][instagramIndex] || '').trim();
    var existingFacebook = String(values[rowIndex][facebookIndex] || '').trim();
    var existingStatus = String(values[rowIndex][statusIndex] || '').trim().toLowerCase();
    var existingSource = sourceIndex < values[rowIndex].length
      ? String(values[rowIndex][sourceIndex] || '').trim().toLowerCase()
      : '';
    if (
      existingInstagram ||
      existingFacebook ||
      isResearchComplete(existingStatus) ||
      isResearchComplete(existingSource)
    ) {
      skipped++;
      continue;
    }

    var companyName = String(values[rowIndex][businessIndex] || '').trim();
    var ghlTag = tagIndex === -1 ? '' : String(values[rowIndex][tagIndex] || '').trim();
    if (!companyName) {
      blankBusinessNames++;
      continue;
    }

    var sourceUrls = [];
    sourceIndexes.forEach(function(columnIndex) {
      sourceUrls = sourceUrls.concat(extractUrls(
        String(values[rowIndex][columnIndex] || ''),
        headers[columnIndex]
      ).map(function(candidate) { return candidate.url; }));
    });

    var result = queryOpenRouter(apiKey, companyName, '', sourceUrls, ghlTag);
    var instagram = normalizeResearchResult(
      result.instagram_username || result.instagram_url,
      'instagram'
    );
    var facebook = normalizeResearchResult(
      result.facebook_page_handle || result.facebook_page_url,
      'facebook'
    );
    if (!existingInstagram && instagram) sheet.getRange(rowIndex + 1, instagramIndex + 1).setValue(instagram.handle);
    if (!existingFacebook && facebook) sheet.getRange(rowIndex + 1, facebookIndex + 1).setValue(facebook.handle);
    sheet.getRange(rowIndex + 1, statusIndex + 1).setValue(
      instagram || facebook
        ? 'candidate_found_review_required'
        : 'openrouter_no_match_' + OPENROUTER_PROMPT_VERSION
    );
    sheet.getRange(rowIndex + 1, sourceIndex + 1).setValue(
      instagram || facebook
        ? 'openrouter_web_research_' + OPENROUTER_PROMPT_VERSION
        : 'openrouter_no_match_' + OPENROUTER_PROMPT_VERSION
    );
    researched++;
    Utilities.sleep(OPENROUTER_SLEEP_MS);
  }
  var message =
    'OpenRouter researched ' + researched + ' rows; skipped ' + skipped +
    ' completed rows; skipped ' + blankBusinessNames +
    ' blank Business Name rows; scanned through sheet row ' + (scanned + 1) +
    ' in ' + Math.round((Date.now() - startedAt) / 1000) + ' seconds.';
  reportRun(message);
  if (researched === 0) stopAutomaticProcessing();
}

function deduplicateResearchColumns(sheet) {
  var lastColumn = sheet.getLastColumn();
  if (!lastColumn) return;

  var headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];
  var targetNames = ['social research sources', 'social research status'];
  targetNames.forEach(function(targetName) {
    var indexes = [];
    headers.forEach(function(header, index) {
      if (normalizeHeader(String(header)) === targetName) indexes.push(index);
    });
    if (indexes.length < 2) return;

    var primaryIndex = indexes[0];
    var rowCount = Math.max(sheet.getLastRow() - 1, 0);
    if (rowCount) {
      var primaryValues = sheet.getRange(2, primaryIndex + 1, rowCount, 1).getValues();
      indexes.slice(1).forEach(function(duplicateIndex) {
        var duplicateValues = sheet.getRange(2, duplicateIndex + 1, rowCount, 1).getValues();
        var merged = primaryValues.map(function(row, rowIndex) {
          return [row[0] || duplicateValues[rowIndex][0]];
        });
        sheet.getRange(2, primaryIndex + 1, rowCount, 1).setValues(merged);
        primaryValues = merged;
      });
    }

    indexes.slice(1).reverse().forEach(function(duplicateIndex) {
      sheet.deleteColumn(duplicateIndex + 1);
    });
    headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  });
}

function findFirstColumn(headers, names) {
  for (var index = 0; index < names.length; index++) {
    var found = headers.indexOf(names[index]);
    if (found !== -1) return found;
  }
  return -1;
}

function isResearchComplete(status) {
  return [
    'candidate_found_review_required',
    'ambiguous',
    'openrouter_no_match_v2'
  ].indexOf(status) !== -1;
}

function queryOpenRouter(apiKey, companyName, locationName, sourceUrls, ghlTag) {
  var prompt = [
    'Research the official public Instagram account and Facebook Page for this company.',
    'Company: ' + companyName,
    'Location: ' + locationName,
    'GHL Tag: ' + (ghlTag || 'none'),
    'Known source URLs: ' + (sourceUrls.join(', ') || 'none'),
    '',
    'Use web search, not memory. Search at least these variations when needed:',
    '- the exact company name plus Instagram',
    '- the exact company name plus Facebook',
    '- the exact company name plus official website',
    '- the company name plus cannabis, dispensary, or brand when relevant',
    'Inspect the official website and cross-check links from the company website or consistent branding.',
    'Return the strongest supported official company-page candidate even if confidence is moderate.',
    'Reject employee, founder, personal, fan, directory, reseller, and unrelated similarly named profiles.',
    'Do not infer a Facebook Messenger PSID or invent a handle when no credible candidate exists.',
    'Return JSON only with this exact shape:',
    '{"instagram_username":null,"instagram_url":null,"facebook_page_handle":null,"facebook_page_url":null,"confidence":"high|medium|low|none","reason":"short evidence-based explanation"}',
    'Use null when the official page cannot be verified.'
  ].join('\n');

  var response = UrlFetchApp.fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + apiKey,
      'HTTP-Referer': 'https://livetransparent.com',
      'X-Title': 'LiveTransparent Social Enrichment'
    },
    payload: JSON.stringify({
      model: PropertiesService.getScriptProperties().getProperty('OPENROUTER_MODEL') || OPENROUTER_DEFAULT_MODEL,
      plugins: [{ id: 'web' }],
      temperature: 0,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: [
          'You are a careful company social-profile research assistant.',
          'You have web search available and must use it for every company.',
          'Prefer official website links and matching branding over directory listings.',
          'Never fabricate handles or confuse a person with a company page.',
          'A plausible but not fully verified result may be returned with medium or low confidence for human review.'
        ].join(' ') },
        { role: 'user', content: prompt }
      ]
    }),
    muteHttpExceptions: true
  });
  var status = response.getResponseCode();
  var body = response.getContentText();
  if (status < 200 || status >= 300) throw new Error('OpenRouter request failed (' + status + '): ' + body.slice(0, 500));

  var parsed = JSON.parse(body);
  var content = parsed.choices && parsed.choices[0] && parsed.choices[0].message && parsed.choices[0].message.content;
  if (!content) throw new Error('OpenRouter returned no message content.');
  content = String(content).replace(/^```json\s*/i, '').replace(/\s*```$/, '').trim();
  return JSON.parse(content);
}

function normalizeResearchResult(value, platform) {
  if (!value || typeof value !== 'string') return null;
  var handle = value.trim().replace(/^@/, '').replace(/^https?:\/\/[^/]+\//i, '').split(/[/?#]/)[0].toLowerCase();
  if (!handle) return null;
  var valid = platform === 'instagram' ? /^[a-z0-9._]+$/i.test(handle) : /^[a-z0-9._-]+$/i.test(handle);
  if (!valid) return null;
  return {
    handle: handle,
    url: platform === 'instagram'
      ? 'https://www.instagram.com/' + handle
      : 'https://www.facebook.com/' + handle
  };
}
