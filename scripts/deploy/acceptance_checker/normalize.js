function clean(v) {
  if (v === undefined || v === null) return '';
  return String(v).trim();
}
function first() {
  for (const value of arguments) {
    const s = clean(value);
    if (s) return s;
  }
  return '';
}
function tryParseJson(text) {
  const s = clean(text);
  if (!s) return null;
  const candidates = [s];
  try { candidates.push(decodeURIComponent(s.replace(/\+/g, ' '))); } catch (e) {}
  for (const candidate of candidates) {
    if (!/^[\[{]/.test(candidate)) continue;
    try { return JSON.parse(candidate); } catch (e) {}
  }
  return null;
}
function formPayloadText(value) {
  if (!value || typeof value !== 'object') return '';
  const container = value.body && typeof value.body === 'object' ? value.body : value;
  const entries = Object.entries(container);
  if (!entries.length || !clean(entries[0][0]).startsWith('{')) return '';
  let text = entries.map(([key, val], index) => {
    const suffix = val === undefined || val === null || String(val) === '' ? '' : '=' + String(val);
    return (index === 0 ? '' : '&') + String(key) + suffix;
  }).join('');
  try { text = decodeURIComponent(text.replace(/\+/g, ' ')); } catch (e) {}
  return text;
}
function rawFormText(value) {
  if (!value || typeof value !== 'object') return '';
  const container = value.body && typeof value.body === 'object' ? value.body : value;
  const keys = Object.keys(container);
  if (keys.length === 1 && clean(keys[0]).startsWith('{')) return String(keys[0]);
  return formPayloadText(value);
}
function unwrap(value) {
  let current = value;
  for (let i = 0; i < 5; i += 1) {
    if (!current || typeof current !== 'object') break;
    if (current.body && typeof current.body === 'object') { current = current.body; continue; }
    if (current.data && typeof current.data === 'object') { current = current.data; continue; }
    const keys = Object.keys(current);
    if (keys.length === 1 && clean(keys[0]).startsWith('{')) {
      const restored = String(keys[0]) + String(current[keys[0]] ?? '');
      const parsed = tryParseJson(keys[0]) || tryParseJson(restored);
      if (parsed && typeof parsed === 'object') { current = parsed; continue; }
    }
    break;
  }
  return current;
}
function decodeJsonString(raw) {
  try { return JSON.parse('"' + raw + '"'); } catch (e) { return raw.replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t').replace(/\\"/g, '"').replace(/\\\\/g, '\\'); }
}
function extractString(source, key, fromIndex) {
  const start = Math.max(0, Number(fromIndex || 0));
  const marker = new RegExp('"' + key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '"\\s*:\\s*"', 'g');
  marker.lastIndex = start;
  const match = marker.exec(source);
  if (!match) return '';
  let raw = '';
  let escaped = false;
  for (let i = marker.lastIndex; i < source.length; i += 1) {
    const ch = source[i];
    if (!escaped && ch === '"') return decodeJsonString(raw);
    raw += ch;
    if (escaped) escaped = false;
    else if (ch === '\\') escaped = true;
  }
  return decodeJsonString(raw);
}
function malformedAttendee(source) {
  const attendeesAt = source.indexOf('"attendees"');
  const senderAt = source.indexOf('"sender"');
  const segment = attendeesAt >= 0 ? source.slice(attendeesAt, senderAt > attendeesAt ? senderAt : source.length) : '';
  return {
    attendee_provider_id: extractString(segment, 'attendee_provider_id'),
    attendee_name: extractString(segment, 'attendee_name'),
    attendee_profile_url: extractString(segment, 'attendee_profile_url'),
    attendee_public_identifier: extractString(segment, 'attendee_public_identifier'),
    attendee_network_distance: extractString(segment, 'network_distance'),
  };
}
function malformedFallback(source) {
  const attendee = malformedAttendee(source);
  return {
    event: extractString(source, 'event'),
    account_id: extractString(source, 'account_id'),
    account_type: extractString(source, 'account_type'),
    chat_id: extractString(source, 'chat_id'),
    timestamp: extractString(source, 'timestamp'),
    is_sender: /"is_sender"\s*:\s*true/i.test(source),
    user_provider_id: extractString(source, 'user_provider_id'),
    user_public_identifier: extractString(source, 'user_public_identifier'),
    user_profile_url: extractString(source, 'user_profile_url'),
    user_full_name: extractString(source, 'user_full_name'),
    attendees: [attendee],
    malformed_payload: source,
  };
}
function parseDate(v) {
  const s = clean(v);
  if (!s) return '';
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? s : d.toISOString();
}
const config = $node['Config'].json || {};
const rawText = rawFormText($json || {});
const unwrapped = unwrap($json || {});
let body = unwrapped && typeof unwrapped === 'object' ? unwrapped : {};
if (!body.event && !body.type && rawText) body = malformedFallback(rawText);
const attendees = Array.isArray(body.attendees) ? body.attendees : [];
const attendee = attendees.find((value) => value && value.attendee_specifics && value.attendee_specifics.network_distance !== 'SELF') || attendees[0] || {};
const eventType = first(body.event, body.type, body.action, body.name) || 'new_relation';
const providerId = first(attendee.attendee_provider_id, attendee.provider_id, attendee.attendee_id, body.user_provider_id, body.provider_id);
const publicIdentifier = first(attendee.attendee_public_identifier, body.user_public_identifier, body.public_identifier, body.publicIdentifier);
const eventProfileUrl = first(attendee.attendee_profile_url, body.user_profile_url, body.profile_url, body.profileUrl);
let relation = { ok: false, error: 'no_identifier', data: null };
const relationTarget = first(providerId, publicIdentifier);
if (relationTarget) {
  const relationUrl = String(config.UNIPILE_API_BASE_URL || '').replace(/\/$/, '') + '/users/' + encodeURIComponent(relationTarget) + '?account_id=' + encodeURIComponent(config.UNIPILE_ACCOUNT_ID || '');
  try {
    const relationData = await this.helpers.httpRequest({
      method: 'GET',
      url: relationUrl,
      headers: { 'X-API-KEY': String(config.UNIPILE_API_KEY || ''), Accept: 'application/json' },
      json: true,
      timeout: 15000,
    });
    relation = { ok: true, data: relationData };
  } catch (e) {
    const msg = (e && (e.message || (e.response && e.response.body && e.response.body.message))) || String(e);
    relation = { ok: false, error: String(msg).slice(0, 300), data: null };
  }
}
const profile = relation.ok && relation.data ? relation.data : {};
const networkDistance = clean(profile.network_distance);
const isRelationship = profile.is_relationship === true;
const isConnected = isRelationship || /FIRST_DEGREE/i.test(networkDistance);
const resolvedProviderId = first(profile.provider_id, providerId);
const resolvedIdentifier = first(profile.public_identifier, publicIdentifier);
const resolvedProfileUrl = first(resolvedIdentifier ? 'https://www.linkedin.com/in/' + resolvedIdentifier : '', eventProfileUrl);
const acceptedAt = profile.connected_at ? parseDate(new Date(Number(profile.connected_at)).toISOString()) : parseDate(first(body.timestamp, body.created_at, body.createdAt));
const now = new Date().toISOString();
return [{
  json: {
    event_type: eventType,
    is_relation_event: eventType === 'new_relation',
    is_sender: body.is_sender === true,
    unipile_account_id: first(body.account_id, body.accountId, config.UNIPILE_ACCOUNT_ID),
    linkedin_provider_id: resolvedProviderId,
    linkedin_public_identifier: resolvedIdentifier,
    linkedin_profile_url: resolvedProfileUrl,
    attendee_name: first(profile.first_name ? (clean(profile.first_name) + ' ' + clean(profile.last_name)).trim() : '', attendee.attendee_name, body.user_full_name),
    is_connected: isConnected,
    is_relationship: isRelationship,
    network_distance: networkDistance,
    relation_checked: relation.ok,
    verify_error: relation.ok ? '' : relation.error,
    accepted_at: acceptedAt || now,
    raw_body: body,
  },
}];