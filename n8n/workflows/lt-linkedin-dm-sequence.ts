import { workflow, node, trigger, newCredential } from '@n8n/workflow-sdk';
import { SOCIAL_OUTREACH_TEMPLATES } from './social_outreach_templates';

const schedule = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '0 12-22 * * 1-5' }] } },
    position: [240, 300],
  },
  output: [{}],
});

const manual = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [240, 480] },
  output: [{}],
});

const config = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: '1', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: '2', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: '3', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: '4', name: 'ghlApiKey', type: 'string', value: 'pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86' },
          { id: '5', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: '6', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: '7', name: 'stateUpsertUrl', type: 'string', value: 'https://automations.livetransparent.com/webhook/lt-linkedin-connection-state-upsert' },
          { id: '8', name: 'templateVariant', type: 'string', value: 'v2' },
        ],
      },
    },
    position: [500, 380],
  },
  output: [{ json: {} }],
});

const ensureTable = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Ensure Table Exists',
    parameters: {
      operation: 'executeQuery',
      query: `CREATE TABLE IF NOT EXISTS linkedin_connection_state (
  ghl_contact_id            TEXT PRIMARY KEY,
  location_id               TEXT NOT NULL,
  unipile_account_id        TEXT NOT NULL DEFAULT '',
  linkedin_profile_url      TEXT NOT NULL DEFAULT '',
  linkedin_public_identifier TEXT NOT NULL DEFAULT '',
  linkedin_provider_id      TEXT NOT NULL DEFAULT '',
  connection_request_tag    TEXT NOT NULL DEFAULT 'linkedin_connection_requested',
  connection_status         TEXT NOT NULL DEFAULT 'requested',
  request_sent_at           TIMESTAMPTZ,
  connected_at              TIMESTAMPTZ,
  dm_sequence_started_at    TIMESTAMPTZ,
  last_checked_at           TIMESTAMPTZ,
  request_message           TEXT,
  request_message_hash      TEXT,
  sequence_step             INTEGER NOT NULL DEFAULT 0,
  payload_json              JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json             JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);`,
    },
    credentials: { postgres: newCredential('Postgres account') },
    position: [740, 380],
  },
  output: [{}],
});

const query = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Find Contacts Ready for DM',
    parameters: {
      operation: 'executeQuery',
      query: `SELECT
  ghl_contact_id,
  linkedin_provider_id,
  linkedin_public_identifier,
  connection_status,
  connected_at,
  dm_sequence_started_at,
  sequence_step,
  payload_json
FROM linkedin_connection_state
WHERE connection_status = 'connected'
  AND COALESCE(payload_json->>'dm_conversation_status', 'idle') <> 'active'
  AND (
    (sequence_step = 0 AND dm_sequence_started_at IS NULL)
    OR (sequence_step = 1 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '3 days')
    OR (sequence_step = 2 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '7 days')
    OR (sequence_step = 3 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '10 days')
    OR (sequence_step = 4 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '14 days')
  )
ORDER BY sequence_step ASC, dm_sequence_started_at ASC NULLS FIRST
LIMIT 20;`,
    },
    credentials: { postgres: newCredential('Postgres account') },
    alwaysOutputData: true,
    position: [980, 380],
  },
  output: [{ ghl_contact_id: 'contact-123' }],
});

const processNode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Send DM Sequence Messages',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const TEMPLATE_REGISTRY = ${JSON.stringify(SOCIAL_OUTREACH_TEMPLATES)};
        var CFG = (function() {
          var c = $node['Config'].json || {};
          return {
            unipileApiBaseUrl: String(c.unipileApiBaseUrl || 'https://api42.unipile.com:17256/api/v1').replace(/\\/+$/, ''),
            unipileApiKey: String(c.unipileApiKey || '').trim(),
            unipileAccountId: String(c.unipileAccountId || '').trim(),
            ghlApiBaseUrl: String(c.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\\/+$/, ''),
            ghlApiKey: String(c.ghlApiKey || '').trim(),
            locationId: String(c.locationId || '').trim(),
            stateUpsertUrl: String(c.stateUpsertUrl || '').trim(),
            templateVariant: String(c.templateVariant || 'v1').trim().toLowerCase(),
          };
        })();

        var MESSAGES = (TEMPLATE_REGISTRY.linkedin[CFG.templateVariant] || TEMPLATE_REGISTRY.linkedin.v1);

        function clean(v) {
          if (v == null) return '';
          if (typeof v === 'string') return v.trim();
          if (typeof v === 'number' || typeof v === 'boolean') return String(v);
          return '';
        }

        function describeError(err) {
          if (err instanceof Error) return err.stack || err.message || err.name || 'Unknown error';
          if (typeof err === 'string') return err;
          if (err && typeof err === 'object') {
            var parts = [];
            if ('message' in err && err.message) parts.push(String(err.message));
            if ('statusCode' in err) parts.push('statusCode=' + String(err.statusCode));
            var body = (err && err.response && err.response.body) || err.body || err.data;
            if (body) {
              if (typeof body === 'string') parts.push('body=' + body);
              else { try { parts.push('body=' + JSON.stringify(body)); } catch(e) { parts.push('body=' + String(body)); } }
            }
            if (parts.length) return parts.join(' | ');
            try { return JSON.stringify(err); } catch(e) { return String(err); }
          }
          return String(err);
        }

        function unipileReq(method, url, body, extraH) {
          if (extraH === undefined) extraH = {};
          var opts = { method: method, url: url, headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, json: true };
          for (var k in extraH) {
            if (extraH.hasOwnProperty(k)) opts.headers[k] = extraH[k];
          }
          if (body !== undefined) opts.body = body;
          return this.helpers.httpRequest(opts).then(function(d) {
            return { ok: true, data: d };
          }).catch(function(err) {
            var sc = (err && err.statusCode) || null;
            var data = (err && err.response && err.response.body) || (err && err.message) || err;
            return { ok: false, sc: sc, data: data };
          });
        }

        function getGhlContact(contactId) {
          if (!contactId) return Promise.resolve({ firstName: 'there' });
          return this.helpers.httpRequest({
            method: 'GET',
            url: CFG.ghlApiBaseUrl + '/contacts/' + encodeURIComponent(contactId),
            headers: { Authorization: 'Bearer ' + CFG.ghlApiKey, Version: '2021-07-28', Accept: 'application/json' },
            json: true,
          }).then(function(resp) {
            var name = String((resp && resp.contact && resp.contact.firstName) || (resp && resp.firstName) || 'there').trim();
            return { firstName: name || 'there' };
          }).catch(function() {
            return { firstName: 'there' };
          });
        }

        var inputItems = [];
        if (typeof $input === 'object' && $input !== null) {
          if (typeof $input.all === 'function') {
            inputItems = $input.all();
          } else if ($json) {
            inputItems = [{ json: $json }];
          }
        }

        var results = [];

        function processNext(index) {
          if (index >= inputItems.length) {
            var sent = results.filter(function(r) { return r.status === 'sent'; }).length;
            var skipped = results.filter(function(r) { return r.status === 'skipped'; }).length;
            var failed = results.filter(function(r) { return r.status === 'dm_failed' || r.status === 'state_upsert_failed'; }).length;
            return [{ json: {
              total: results.length,
              sent: sent,
              skipped: skipped,
              failed: failed,
              results: results,
            } }];
          }

          var d = inputItems[index].json || {};
          var contactId = clean(d.ghl_contact_id);
          var providerId = clean(d.linkedin_provider_id);
          var step = Number(d.sequence_step || 0);
          var newStep = step + 1;
          var self = this;

          if (!contactId || !providerId) {
            results.push({ contactId: contactId, providerId: providerId, step: step, status: 'skipped', reason: 'missing_contact_or_provider' });
            return processNext.call(self, index + 1);
          }

          if (newStep < 1 || newStep >= MESSAGES.length || !MESSAGES[newStep]) {
            results.push({ contactId: contactId, step: step, status: 'skipped', reason: 'no_message_for_step_' + step });
            return processNext.call(self, index + 1);
          }

          var msgTemplate = MESSAGES[newStep];

          return getGhlContact.call(self, contactId).then(function(contact) {
            var firstName = clean(contact.firstName || 'there');
            var message = msgTemplate.replace(/\\{first_name\\}/gi, firstName);

            return unipileReq.call(self, 'POST', CFG.unipileApiBaseUrl + '/chats', {
              account_id: CFG.unipileAccountId,
              attendees_ids: [providerId],
              text: message,
            }, { 'X-API-KEY': CFG.unipileApiKey });
          }).then(function(chatResp) {
            if (!chatResp.ok) {
              results.push({ contactId: contactId, step: step, newStep: newStep, status: 'dm_failed', error: describeError(chatResp.data) });
              return processNext.call(self, index + 1);
            }

            var chatId = clean((chatResp.data && chatResp.data.chat_id) || (chatResp.data && chatResp.data.id) || '');

            var upsertBody = {
              ghl_contact_id: contactId,
              location_id: CFG.locationId,
              connection_status: 'connected',
              sequence_step: newStep,
              source_workflow_name: 'LT - LinkedIn DM Sequence (Unipile)',
              source_key: 'contact:' + contactId + ':step_' + newStep,
              payload_json: { last_chat_id: chatId, last_message_step: newStep, sent_at: new Date().toISOString() },
              metadata_json: { source: 'dm_sequence', step: newStep },
            };
            if (step === 0) {
              upsertBody.dm_sequence_started_at = new Date().toISOString();
            }

            return self.helpers.httpRequest({
              method: 'POST',
              url: CFG.stateUpsertUrl,
              headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
              body: upsertBody,
              json: true,
            }).then(function() {
              results.push({ contactId: contactId, step: step, newStep: newStep, status: 'sent', chatId: chatId });
              return processNext.call(self, index + 1);
            }).catch(function(stateErr) {
              results.push({ contactId: contactId, step: step, newStep: newStep, status: 'state_upsert_failed', chatId: chatId, error: describeError(stateErr) });
              return processNext.call(self, index + 1);
            });
          }).catch(function(err) {
            results.push({ contactId: contactId, step: step, status: 'error', error: describeError(err) });
            return processNext.call(self, index + 1);
          });
        }

        return processNext.call(this, 0);
      `.trim(),
    },
    position: [980, 380],
  },
  output: [{ json: { total: 0, sent: 0, skipped: 0, failed: 0 } }],
});

const result = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Result',
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: 't', name: 'total', type: 'number', value: '={{ $json.total }}' },
          { id: 's', name: 'sent', type: 'number', value: '={{ $json.sent }}' },
          { id: 'sk', name: 'skipped', type: 'number', value: '={{ $json.skipped }}' },
          { id: 'f', name: 'failed', type: 'number', value: '={{ $json.failed }}' },
        ],
      },
    },
    position: [1220, 380],
  },
  output: [{ json: { total: 0, sent: 0, skipped: 0, failed: 0 } }],
});

export default workflow('lt-linkedin-dm-sequence', 'LT - LinkedIn DM Sequence (Unipile)')
  .add(schedule)
  .to(config)
  .to(ensureTable)
  .to(query)
  .to(processNode)
  .to(result)
  .add(manual)
  .to(config);
