import { workflow, node, trigger, newCredential } from '@n8n/workflow-sdk';

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
  AND connected_at IS NOT NULL
  AND COALESCE(linkedin_provider_id, '') <> ''
  AND COALESCE(payload_json->>'source', metadata_json->>'source', '') <> 'relation_backfill'
  AND COALESCE(payload_json->>'dm_conversation_status', 'idle') <> 'active'
  AND (
    (sequence_step = 0 AND dm_sequence_started_at IS NULL)
    OR (sequence_step = 1 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '3 days')
    OR (sequence_step = 2 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '7 days')
    OR (sequence_step = 3 AND dm_sequence_started_at IS NOT NULL AND dm_sequence_started_at <= NOW() - INTERVAL '10 days')
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
      jsCode: `const TEMPLATE_REGISTRY = {
  linkedin: {
    invite: "Hi {first_name}, I'm Cameron co-founder of Transparent eCom. We help brands in regulated industries advertise on social/search without restrictions and at scale. Are you currently running ads on social/search?",
    v2: [
      null,
      "Most cannabis brands still can't run Meta/Google ads the way mainstream brands can.\n\nFor a lot of teams, the issue isn't performance - it's access. Accounts getting restricted or shut down before anything can scale.\n\nWe help operators get live on Meta through compliant ad accounts, then build a setup designed to stay live and grow more reliably across brands.\n\nIf Meta or Google is a channel you're looking to open up, I'd love to connect - happy to share how other operators are making it work.\n\nWorth a quick chat?",
      "One of the most common constraints we see with cannabis teams is not being able to fully activate paid social and search.\n\nIt's rarely a strategy problem. It's infrastructure - not having a setup that lets you launch and keep things running without constant interruptions.\n\nWe work with teams to open up these channels properly, then build a structure that supports ongoing execution without the resets.\n\nIf this sounds familiar, I'd love to show you how other operators are handling it.\n\nWorth a 15-minute call?",
      "Most cannabis operators still can't use paid social and search the way mainstream brands can.\n\nThat usually means there's a revenue channel sitting unused - not because demand isn't there, but because teams can't get it live or keep it running.\n\nWe help operators unlock these channels through compliant infrastructure, then keep them running so revenue stays more consistent over time.\n\nIf this is something you're looking into, I'd love to share how other operators are doing it.\n\nWorth a 15-minute call?",
      "Most cannabis brands still can't run Meta ads in a way they can rely on.\n\nWhen ads get restricted or taken down, traffic slows and sales follow - which makes it hard to keep things consistent across locations.\n\nWe help operators get live on Meta through compliant ad accounts, then keep things running so traffic and sales stop getting disrupted.\n\nIf you want Meta working consistently, I'd love to show you how other multi-location brands are doing it.\n\nWorth a 15-minute call?",
    ],
  },
};
TEMPLATE_REGISTRY.linkedin.v1 = TEMPLATE_REGISTRY.linkedin.v2;

function sanitizeMessage(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/\u00A0/g, ' ')
    .replace(/\u0393\u00C7[\u00D6\u00FF]/g, "'")
    .replace(/\u0393\u00C7[\u00A3\u00A5]/g, '"')
    .replace(/\u0393\u00C7[\u00F4\u00F6]/g, '-')
    .replace(/\u0393\u00C7\u00AA/g, '...')
    .replace(/\u00E2\u20AC[\u02DC\u2122]/g, "'")
    .replace(/\u00E2\u20AC[\u0153\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u009D]/g, '"')
    .replace(/\u00E2\u20AC[\u201C\u0094]/g, '-')
    .replace(/\u00E2\u20AC\u00A6/g, '...');
}

function sanitizeTemplateRegistry(value) {
  if (typeof value === 'string') return sanitizeMessage(value);
  if (Array.isArray(value)) {
    for (var i = 0; i < value.length; i += 1) value[i] = sanitizeTemplateRegistry(value[i]);
    return value;
  }
  if (value && typeof value === 'object') {
    Object.keys(value).forEach(function(key) { value[key] = sanitizeTemplateRegistry(value[key]); });
  }
  return value;
}

        var CFG = (function() {
          var c = $node['Config'].json || {};
          return {
            unipileApiBaseUrl: String(c.unipileApiBaseUrl || 'https://api42.unipile.com:17256/api/v1').replace(/\/+$/, ''),
            unipileApiKey: String(c.unipileApiKey || '').trim(),
            unipileAccountId: String(c.unipileAccountId || '').trim(),
            ghlApiBaseUrl: String(c.ghlApiBaseUrl || 'https://services.leadconnectorhq.com').replace(/\/+$/, ''),
            ghlApiKey: String(c.ghlApiKey || '').trim(),
            locationId: String(c.locationId || '').trim(),
            stateUpsertUrl: String(c.stateUpsertUrl || '').trim(),
            templateVariant: String(c.templateVariant || 'v1').trim().toLowerCase(),
          };
        })();

        sanitizeTemplateRegistry(TEMPLATE_REGISTRY);
        var MESSAGES = (TEMPLATE_REGISTRY.linkedin[CFG.templateVariant] || TEMPLATE_REGISTRY.linkedin.v1);
        var DM_COMPLETE_TAG = 'linkedin_dm_sequence_completed';

        function clean(v) {
          if (v == null) return '';
          if (typeof v === 'string') return v.trim();
          if (typeof v === 'number' || typeof v === 'boolean') return String(v);
          return '';
        }

        function extractConversationItems(resp) {
          if (!resp) return [];
          if (Array.isArray(resp.conversations)) return resp.conversations;
          if (Array.isArray(resp.items)) return resp.items;
          if (Array.isArray(resp.data?.conversations)) return resp.data.conversations;
          if (Array.isArray(resp.data?.items)) return resp.data.items;
          if (Array.isArray(resp.data)) return resp.data;
          return [];
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

        function hasInboundConversation(contactId) {
          if (!contactId) return Promise.resolve({ blocked: true, reason: 'missing_contact_id' });
          return this.helpers.httpRequest({
            method: 'GET',
            url: CFG.ghlApiBaseUrl + '/conversations/search?contactId=' + encodeURIComponent(contactId) + '&lastMessageDirection=inbound&status=all&limit=1',
            headers: {
              Authorization: 'Bearer ' + CFG.ghlApiKey,
              Version: '2021-07-28',
              Accept: 'application/json',
              'Content-Type': 'application/json',
            },
            json: true,
          }).then(function(resp) {
            var conversations = extractConversationItems(resp);
            return { blocked: conversations.length > 0, reason: conversations.length > 0 ? 'inbound_conversation' : '' };
          }).catch(function() {
            return { blocked: true, reason: 'conversation_check_failed' };
          });
        }

        function addGhlTags(contactId, tags) {
          return this.helpers.httpRequest({
            method: 'POST',
            url: CFG.ghlApiBaseUrl + '/contacts/' + encodeURIComponent(contactId) + '/tags',
            headers: {
              Authorization: 'Bearer ' + CFG.ghlApiKey,
              Version: '2021-07-28',
              Accept: 'application/json',
              'Content-Type': 'application/json',
            },
            body: { tags: tags },
            json: true,
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

        var hasRealWork = inputItems.some(function(item) {
          var d = item && item.json ? item.json : {};
          var payload = d.payload_json && typeof d.payload_json === 'object' ? d.payload_json : {};
          return !!clean(d.ghl_contact_id) || !!clean(d.linkedin_provider_id) || !!clean(d.linkedin_public_identifier) || !!clean(payload.providerId || payload.provider_id || payload.identifier || '');
        });
        if (!hasRealWork) {
          return [{ json: { total: 0, sent: 0, skipped: 0, failed: 0, results: [] } }];
        }

        var results = [];

        async function processNext(index) {
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
          var payload = d.payload_json && typeof d.payload_json === 'object' ? d.payload_json : {};
          var contactId = clean(d.ghl_contact_id);
          var publicIdentifier = clean(d.linkedin_public_identifier || payload.identifier || payload.linkedin_public_identifier || '');
          var providerId = clean(d.linkedin_provider_id || payload.providerId || payload.provider_id || '');
          var step = Number(d.sequence_step || 0);
          var newStep = step + 1;
          var self = this;

          if (!contactId) {
            results.push({ contactId: contactId, providerId: providerId, step: step, status: 'skipped', reason: 'missing_contact_or_provider' });
            return processNext.call(self, index + 1);
          }

          if (!providerId && publicIdentifier) {
            const profileResp = await unipileReq.call(self, 'GET', CFG.unipileApiBaseUrl + '/users/' + encodeURIComponent(publicIdentifier) + '?account_id=' + encodeURIComponent(CFG.unipileAccountId), undefined, { 'X-API-KEY': CFG.unipileApiKey });
            providerId = clean(profileResp.data && (profileResp.data.provider_id || profileResp.data.providerId || profileResp.data.id) || '');
            if (!profileResp.ok || !providerId) {
              results.push({ contactId: contactId, providerId: providerId, publicIdentifier: publicIdentifier, step: step, status: 'skipped', reason: 'missing_contact_or_provider', profileOk: profileResp.ok });
              return processNext.call(self, index + 1);
            }
          }

          if (!providerId) {
            results.push({ contactId: contactId, providerId: providerId, publicIdentifier: publicIdentifier, step: step, status: 'skipped', reason: 'missing_contact_or_provider' });
            return processNext.call(self, index + 1);
          }

          var inbound = await hasInboundConversation.call(self, contactId);
          if (inbound.blocked) {
            results.push({ contactId: contactId, providerId: providerId, publicIdentifier: publicIdentifier, step: step, status: 'skipped', reason: inbound.reason || 'contact_replied' });
            return processNext.call(self, index + 1);
          }

          if (newStep < 1 || newStep >= MESSAGES.length || !MESSAGES[newStep]) {
            if (step >= 4) {
              var completedAt = new Date().toISOString();
              try {
                await addGhlTags.call(self, contactId, [DM_COMPLETE_TAG]);

                var completionUpsertBody = {
                  ghl_contact_id: contactId,
                  location_id: CFG.locationId,
                  connection_status: 'completed',
                  sequence_step: newStep,
                  source_workflow_name: 'LT - LinkedIn DM Sequence (Unipile)',
                  source_key: 'contact:' + contactId + ':completed',
                  payload_json: Object.assign({}, payload, {
                    dm_sequence_status: 'completed',
                    dm_sequence_completed_at: completedAt,
                    last_message_step: step,
                  }),
                  metadata_json: { source: 'dm_sequence', step: step, completed: true },
                };

                await self.helpers.httpRequest({
                  method: 'POST',
                  url: CFG.stateUpsertUrl,
                  headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
                  body: completionUpsertBody,
                  json: true,
                });

                results.push({ contactId: contactId, step: step, newStep: newStep, status: 'completed', completedAt: completedAt, tag: DM_COMPLETE_TAG });
                return processNext.call(self, index + 1);
              } catch (completionErr) {
                results.push({ contactId: contactId, step: step, newStep: newStep, status: 'completion_failed', error: describeError(completionErr) });
                return processNext.call(self, index + 1);
              }
            }

            results.push({ contactId: contactId, step: step, status: 'skipped', reason: 'no_message_for_step_' + step });
            return processNext.call(self, index + 1);
          }

          var msgTemplate = MESSAGES[newStep];

          function continueWithProvider(profileResp) {
            return getGhlContact.call(self, contactId).then(function(contact) {
              var firstName = clean(contact.firstName || 'there');
              if ((!firstName || firstName === 'there') && profileResp && profileResp.ok && profileResp.data) {
                firstName = clean(profileResp.data.first_name || profileResp.data.firstName || 'there');
              }
              var message = sanitizeMessage(msgTemplate.replace(/\\{first_name\\}/gi, firstName));

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

          return continueWithProvider.call(self, null);
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
