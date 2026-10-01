// n8n Code node source for the gateway's safe POST validation branch.
// The V2 map lookup/send remains a separate downstream implementation step.
const input = $input.first()?.json || {};
const cfg = $items('Config')[0]?.json || {};
const respond = (status, error, extra = {}) => [{ json: { status, response: { ok: false, error, ...extra } } }];
const query = input.query && typeof input.query === 'object' ? input.query : {};

// OAuth grants are managed by the dedicated encrypted n8n OAuth2 credential.
if (query.code || query.error) {
  return respond(409, 'oauth_connection_managed_by_n8n_credential');
}

const headerBag = input.headers && typeof input.headers === 'object' ? input.headers : {};
const signature = String(headerBag['x-ghl-signature'] || headerBag['X-GHL-Signature'] || '');
const raw = typeof input.rawBody === 'string'
  ? input.rawBody
  : (Buffer.isBuffer(input.rawBody) ? input.rawBody.toString('utf8') : '');
if (!signature || !raw) return respond(401, 'signature_or_raw_body_missing');

const publicKey = `-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAi2HR1srL4o18O8BRa7gVJY7G7bupbN3H9AwJrHCDiOg=\n-----END PUBLIC KEY-----`;
let validSignature = false;
try {
  validSignature = require('crypto').verify(
    null,
    Buffer.from(raw, 'utf8'),
    publicKey,
    Buffer.from(signature, 'base64'),
  );
} catch {
  validSignature = false;
}
if (!validSignature) return respond(401, 'invalid_signature');

let body;
try {
  body = JSON.parse(raw);
} catch {
  return respond(400, 'malformed_json');
}

const contactId = String(body.contactId || '').trim();
const messageId = String(body.messageId || '').trim();
const locationId = String(body.locationId || '').trim();
const message = String(body.message || '').trim();
if (!cfg.ghlLocationId || locationId !== cfg.ghlLocationId) return respond(403, 'location_mismatch');
if (String(body.type || '').toUpperCase() !== 'SMS') return respond(400, 'unsupported_message_type');
if (!contactId || !messageId || !message) return respond(400, 'missing_required_fields');
if (Array.isArray(body.attachments) && body.attachments.length) return respond(400, 'attachments_not_supported');

// This guard intentionally stays closed until the exact GHL-contact-to-V2-chat
// map query and Unipile send node are wired and reviewed.
return respond(503, 'v2_map_lookup_and_send_not_wired');
