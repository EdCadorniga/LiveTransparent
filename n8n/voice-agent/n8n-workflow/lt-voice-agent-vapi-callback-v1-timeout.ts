import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const codeDetectJs = `const body = $json.body || $json;
const message = body.message || body;
const call = message.call || body.call || {};
const assistantId = String(call.assistantId || call.assistant_id || '').trim();
const callId = String(call.id || body.id || body.callId || message.callId || '').trim();
const status = String(message.status || call.status || body.status || '').toLowerCase();
const eventType = String(message.type || body.type || '').toLowerCase();
const isToolCall = !!(body.tool && body.tool.name);
const isStatusUpdate = eventType === 'status-update';
const controlUrl = String((call.monitor && call.monitor.controlUrl) || call.controlUrl || body.controlUrl || '').trim();
const trackedAssistants = ['43f379ff-bb7e-4cd4-96f1-7299832dbc4b', '3f9bbfd2-efa6-4381-81e6-26f2452d28f1'];
const isTrackedAssistant = trackedAssistants.includes(assistantId);
return [{ json: { _isToolCall: isToolCall, _isStatusUpdate: isStatusUpdate, _raw: body, event_type: isToolCall ? 'tool' : isStatusUpdate ? 'status-update' : 'callback', call_id: callId, assistant_id: assistantId, call_status: status, control_url: controlUrl, is_tracked_assistant: isTrackedAssistant } }];`;

const codeToolJs = `const raw = $json._raw;
const tool = raw.tool || {};
const params = tool.parameters || {};
const meta = raw.metadata || {};
const toolName = String(tool.name || '').toLowerCase();
const contactId = String(params.ghl_contact_id || params.contact_id || meta.contact_id || '').trim();
const queueId = String(meta.queue_id || params.queue_id || '').trim();
const callId = String(meta.call_id || params.call_id || '').trim();
const s = (v) => String(v ?? '').replace(/'/g, "''").trim();
return [{ json: { tool_name: toolName, contact_id: contactId, queue_id: queueId, call_id: callId, route_update: toolName === 'update_lead_status', route_dnc: toolName === 'add_to_dnc', route_log: toolName === 'log_call_outcome', route_notify: toolName === 'notify_sales', route_referral: toolName === 'report_referral', disposition: s(params.disposition || ''), notes: s(params.notes || ''), follow_up_at: params.followUpAt || params.follow_up_at || null, reason: s(params.reason || ''), lead_name: s(params.lead_name || params.leadName || ''), company: s(params.company || '') } }];`;

const codeEndCallJs = `const raw = $json._raw;
const body = raw.message || raw;
const call = body.call || raw.call || {};
const artifact = raw.artifact || {};
const analysis = raw.analysis || {};
const meta = (call.assistantOverrides && call.assistantOverrides.metadata) || call.metadata || {};
const contactId = String(meta.contact_id || '').trim();
const queueId = String(meta.queue_id || '').trim();
const status = String(call.status || body.status || raw.status || '').toLowerCase();
const endedReason = String(call.endedReason || body.endedReason || '').toLowerCase();
const successEvaluation = !!analysis.successEvaluation;
const summary = String(analysis.summary || artifact.summary || '').trim();
const recordingUrl = artifact.recordingUrl || call.recordingUrl || '';
const callId = String(call.id || body.id || raw.id || '').trim();
const store = this.getWorkflowStaticData('global');
store.voiceCallTimers = store.voiceCallTimers || {};
if (callId) {
  const state = store.voiceCallTimers[callId] || { callId };
  state.ended = true;
  state.endedAt = new Date().toISOString();
  state.lastStatus = status || state.lastStatus || '';
  store.voiceCallTimers[callId] = state;
}
let disposition = 'failed';
if (status.includes('ended') || status.includes('completed')) {
  if (endedReason.includes('customer-did-not-answer') || endedReason.includes('no-answer')) disposition = 'no_answer';
  else if (endedReason.includes('voicemail')) disposition = 'voicemail';
  else disposition = successEvaluation ? 'qualified_booked' : 'connected';
}
return [{ json: { contact_id: contactId, queue_id: queueId, call_id: callId, disposition, summary: summary || 'No summary returned by Vapi.', recording_url: recordingUrl } }];`;

const codeTimerStateJs = `const store = this.getWorkflowStaticData('global');
store.voiceCallTimers = store.voiceCallTimers || {};
const now = new Date().toISOString();
const callId = String($json.call_id || '').trim();
const assistantId = String($json.assistant_id || '').trim();
const controlUrl = String($json.control_url || '').trim();
const status = String($json.call_status || '').toLowerCase();
const tracked = !!$json.is_tracked_assistant;
if (!callId || !tracked) {
  return [{ json: { ...$json, action: 'skip', timer_state: 'untracked' } }];
}
const state = store.voiceCallTimers[callId] || { callId };
state.lastStatus = status;
state.lastEventAt = now;
state.assistantId = assistantId || state.assistantId || '';
state.controlUrl = controlUrl || state.controlUrl || '';
if (status === 'ended') {
  state.ended = true;
  state.endedAt = now;
  store.voiceCallTimers[callId] = state;
  return [{ json: { ...$json, action: 'skip', timer_state: 'ended' } }];
}
if (status !== 'in-progress') {
  store.voiceCallTimers[callId] = state;
  return [{ json: { ...$json, action: 'skip', timer_state: 'ignored' } }];
}
if (state.ended || state.timersScheduled) {
  store.voiceCallTimers[callId] = state;
  return [{ json: { ...$json, action: 'skip', timer_state: state.ended ? 'ended' : 'duplicate' } }];
}
state.timersScheduled = true;
state.startedAt = now;
state.backgroundMessageSent = false;
state.endCallSent = false;
state.ended = false;
store.voiceCallTimers[callId] = state;
return [{ json: { ...$json, action: 'schedule', timer_state: 'scheduled' } }];`;

const codeWarnCheckJs = `const store = this.getWorkflowStaticData('global');
store.voiceCallTimers = store.voiceCallTimers || {};
const callId = String($json.call_id || '').trim();
const state = callId ? (store.voiceCallTimers[callId] || {}) : {};
if (!callId || !state.timersScheduled || state.ended || state.backgroundMessageSent) {
  return [{ json: { ...$json, action: 'skip', timer_state: state.ended ? 'ended' : 'skip' } }];
}
state.backgroundMessageSent = true;
state.backgroundMessageSentAt = new Date().toISOString();
store.voiceCallTimers[callId] = state;
return [{ json: { ...$json, action: 'warn', timer_state: 'warn-ready' } }];`;

const codeEndCheckJs = `const store = this.getWorkflowStaticData('global');
store.voiceCallTimers = store.voiceCallTimers || {};
const callId = String($json.call_id || '').trim();
const state = callId ? (store.voiceCallTimers[callId] || {}) : {};
if (!callId || !state.timersScheduled || state.ended || state.endCallSent || !String($json.control_url || state.controlUrl || '').trim()) {
  return [{ json: { ...$json, action: 'skip', timer_state: state.ended ? 'ended' : 'skip' } }];
}
state.endCallSent = true;
state.endCallSentAt = new Date().toISOString();
store.voiceCallTimers[callId] = state;
return [{ json: { ...$json, action: 'end', timer_state: 'end-ready', control_url: String($json.control_url || state.controlUrl || '').trim() } }];`;

const webhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook - Vapi',
    parameters: {
      httpMethod: 'POST',
      path: 'voice-callback',
      responseMode: 'responseNode',
      options: {},
    },
    position: [240, 340],
  },
  output: [{ body: { type: 'status-update', status: 'in-progress', call: { id: 'call_123', assistantId: '43f379ff-bb7e-4cd4-96f1-7299832dbc4b', monitor: { controlUrl: 'https://api.vapi.ai/call/call_123/control' } } } }],
});

const detect = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Detect Tool vs Callback',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeDetectJs },
    position: [480, 340],
  },
  output: [{ json: { event_type: 'tool', call_id: 'call_123', assistant_id: '43f379ff-bb7e-4cd4-96f1-7299832dbc4b' } }],
});

const toolCheck = node({
  type: 'n8n-nodes-base.if',
  version: 2.2,
  config: {
    name: 'If - Is Tool Call',
    parameters: {
      conditions: {
        conditions: [
          {
            value1: '={{$json._isToolCall}}',
            value2: true,
            operator: { type: 'boolean', operation: 'isTrue' },
          },
        ],
        combinator: 'and',
        options: {
          caseSensitive: true,
          leftValue: '',
          typeValidation: 'strict',
          version: 1,
        },
      },
      options: {},
    },
    position: [720, 340],
  },
  output: [{ json: { _isToolCall: true } }, { json: { _isToolCall: false } }],
});

const immediateAck = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - Immediate Ack',
    parameters: {
      respondWith: 'json',
      responseBody: '={\"ok\": true, \"event_type\": \"{{ $json.event_type || \\\"\\\" }}\", \"call_id\": \"{{ $json.call_id || \\\"\\\" }}\", \"assistant_id\": \"{{ $json.assistant_id || \\\"\\\" }}\"}',
      options: {},
    },
    position: [960, 620],
  },
});

const statusCheck = node({
  type: 'n8n-nodes-base.if',
  version: 2.2,
  config: {
    name: 'If - Is Status Update',
    parameters: {
      conditions: {
        conditions: [
          {
            value1: '={{$json._isStatusUpdate}}',
            value2: true,
            operator: { type: 'boolean', operation: 'isTrue' },
          },
        ],
        combinator: 'and',
        options: {
          caseSensitive: true,
          leftValue: '',
          typeValidation: 'strict',
          version: 1,
        },
      },
      options: {},
    },
    position: [960, 500],
  },
  output: [{ json: { _isStatusUpdate: true } }, { json: { _isStatusUpdate: false } }],
});

const timerState = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Prepare Timer State',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeTimerStateJs },
    position: [1200, 500],
  },
  output: [{ json: { action: 'schedule', timer_state: 'scheduled' } }],
});

const timerCheck = node({
  type: 'n8n-nodes-base.if',
  version: 2.2,
  config: {
    name: 'If - Should Start Timers',
    parameters: {
      conditions: {
        conditions: [
          {
            value1: '={{$json.action}}',
            value2: 'schedule',
            operator: { type: 'string', operation: 'equals' },
          },
        ],
        combinator: 'and',
        options: {
          caseSensitive: true,
          leftValue: '',
          typeValidation: 'strict',
          version: 1,
        },
      },
      options: {},
    },
    position: [1440, 500],
  },
  output: [{ json: { action: 'schedule' } }, { json: { action: 'skip' } }],
});

const waitWarn = node({
  type: 'n8n-nodes-base.wait',
  version: 1.1,
  config: {
    name: 'Wait - 465 Seconds',
    parameters: {
      resume: 'timeInterval',
      amount: 465,
      unit: 'seconds',
    },
    position: [1680, 500],
  },
  output: [{ json: { waited: 465 } }],
});

const warnCheck = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Prepare Background Warning',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeWarnCheckJs },
    position: [1920, 500],
  },
  output: [{ json: { action: 'warn', timer_state: 'warn-ready' } }],
});

const warnHttp = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'HTTP - Send Background Warning',
    parameters: {
      method: 'POST',
      url: '=https://api.vapi.ai/call/{{ $json.call_id }}/background-messages',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: '=Bearer {{ $env.VAPI_PRIVATE_KEY || $env.VAPI_API_KEY }}' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"messages\":[{\"role\":\"system\",\"content\":\"Time limit: 15 seconds remaining. Wrap up now and end the call by 8:00. Do not mention this time limit to the customer.\"}]}',
      options: {},
    },
    position: [2160, 500],
  },
  output: [{ json: { ok: true } }],
});

const waitEnd = node({
  type: 'n8n-nodes-base.wait',
  version: 1.1,
  config: {
    name: 'Wait - 15 Seconds',
    parameters: {
      resume: 'timeInterval',
      amount: 15,
      unit: 'seconds',
    },
    position: [2400, 500],
  },
  output: [{ json: { waited: 15 } }],
});

const endCheck = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Prepare Hard Stop',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeEndCheckJs },
    position: [2640, 500],
  },
  output: [{ json: { action: 'end', timer_state: 'end-ready' } }],
});

const endHttp = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'HTTP - Force End Call',
    parameters: {
      method: 'POST',
      url: '={{ $json.control_url }}',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"type\":\"end-call\"}',
      options: {},
    },
    position: [2880, 500],
  },
  output: [{ json: { ok: true } }],
});

const toolNormalize = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Normalize Tool Call',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeToolJs },
    position: [960, 180],
  },
  output: [{ json: { tool_name: 'update_lead_status', contact_id: '' } }],
});

const toolSwitch = node({
  type: 'n8n-nodes-base.switch',
  version: 3.4,
  config: {
    name: 'Switch - Route Tool',
    parameters: {
      rules: {
        values: [
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3,
              },
              conditions: [
                {
                  leftValue: '={{$json.tool_name}}',
                  rightValue: 'update_lead_status',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-update-lead-status',
                },
              ],
              combinator: 'and',
            },
          },
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3,
              },
              conditions: [
                {
                  leftValue: '={{$json.tool_name}}',
                  rightValue: 'add_to_dnc',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-add-to-dnc',
                },
              ],
              combinator: 'and',
            },
          },
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3,
              },
              conditions: [
                {
                  leftValue: '={{$json.tool_name}}',
                  rightValue: 'log_call_outcome',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-log-call-outcome',
                },
              ],
              combinator: 'and',
            },
          },
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3,
              },
              conditions: [
                {
                  leftValue: '={{$json.tool_name}}',
                  rightValue: 'notify_sales',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-notify-sales',
                },
              ],
              combinator: 'and',
            },
          },
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3,
              },
              conditions: [
                {
                  leftValue: '={{$json.tool_name}}',
                  rightValue: 'report_referral',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-report-referral',
                },
              ],
              combinator: 'and',
            },
          },
        ],
      },
      options: {},
    },
    position: [1200, 180],
  },
  output: [
    { json: { tool_name: 'update_lead_status' } },
    { json: { tool_name: 'add_to_dnc' } },
    { json: { tool_name: 'log_call_outcome' } },
    { json: { tool_name: 'notify_sales' } },
    { json: { tool_name: 'report_referral' } },
    { json: { tool_name: 'fallback' } },
  ],
});

const pgStatus = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.5,
  config: {
    name: 'Postgres - Update Status',
    parameters: {
      operation: 'executeQuery',
      query: "UPDATE voice_call_queue SET status = 'completed', updated_at = now() WHERE queue_id = nullif('{{ $json.queue_id }}', '')::uuid;",
    },
    position: [1480, -80],
  },
  output: [{ json: { ok: true } }],
});

const ghlTags = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL - Update Tags',
    parameters: {
      method: 'PUT',
      url: '=https://services.leadconnectorhq.com/contacts/{{ $(\"Code - Normalize Tool Call\").item.json.contact_id }}/tags',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: '=Bearer {{ $env.GHL_API_KEY }}' },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"tags\":[\"AI Call Attempted\"]}',
      options: {},
    },
    position: [1760, -80],
  },
  output: [{ json: { ok: true } }],
});

const pgDnc = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.5,
  config: {
    name: 'Postgres - Set DNC',
    parameters: {
      operation: 'executeQuery',
      query: "UPDATE voice_call_queue SET dnc = true, status = 'completed', updated_at = now() WHERE queue_id = nullif('{{ $json.queue_id }}', '')::uuid;",
    },
    position: [1480, 20],
  },
  output: [{ json: { ok: true } }],
});

const ghlDnc = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL - DNC Tag',
    parameters: {
      method: 'PUT',
      url: '=https://services.leadconnectorhq.com/contacts/{{ $(\"Code - Normalize Tool Call\").item.json.contact_id }}/tags',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: '=Bearer {{ $env.GHL_API_KEY }}' },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"tags\":[\"do_not_call\"]}',
      options: {},
    },
    position: [1760, 20],
  },
  output: [{ json: { ok: true } }],
});

const pgLog = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.5,
  config: {
    name: 'Postgres - Log Outcome',
    parameters: {
      operation: 'executeQuery',
      query: "INSERT INTO voice_call_attempt (call_id, queue_id, contact_id, provider_call_id, idempotency_key, disposition, summary, follow_up_at, handoff_required, updated_at)\nVALUES (\n  nullif('{{ $json.call_id }}', '')::uuid,\n  nullif('{{ $json.queue_id }}', '')::uuid,\n  '{{ $json.contact_id }}',\n  '{{ $json.call_id }}',\n  '{{ $json.call_id }}:{{ $json.disposition }}',\n  '{{ $json.disposition }}',\n  '{{ $json.notes }}',\n  {{ $json.follow_up_at ? \"'\" + $json.follow_up_at + \"'\" : \"null\" }},\n  false,\n  now()\n)\nON CONFLICT (idempotency_key) DO UPDATE SET disposition = EXCLUDED.disposition, summary = EXCLUDED.summary, updated_at = now();",
    },
    position: [1480, 120],
  },
  output: [{ json: { ok: true } }],
});

const slackLead = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'HTTP - Slack #leads',
    parameters: {
      method: 'POST',
      url: '={{$env.SLACK_WEBHOOK_URL}}',
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"text\": \"*Voice AI Lead Alert*\\n*Name:* \" + ($json.lead_name || \"Unknown\") + \"\\n*Company:* \" + ($json.company || \"N/A\") + \"\\n*Disposition:* \" + ($json.disposition || \"N/A\") + \"\\n*Notes:* \" + ($json.notes || \"None\") + \"\\n*Contact ID:* \" + ($json.contact_id || \"N/A\")}',
      options: {},
    },
    position: [1480, 220],
  },
  output: [{ json: { ok: true } }],
});

const endNormalize = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Normalize End Of Call',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: codeEndCallJs },
    position: [960, 500],
  },
  output: [{ json: { contact_id: '', queue_id: '', call_id: '', disposition: 'failed' } }],
});

const insertAttempt = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.5,
  config: {
    name: 'Postgres - Insert Attempt',
    parameters: {
      operation: 'executeQuery',
      query: "INSERT INTO voice_call_attempt (call_id, queue_id, contact_id, provider_call_id, idempotency_key, disposition, summary, transcript_url, recording_url)\nVALUES (\n  nullif('{{ $json.call_id }}', '')::uuid,\n  nullif('{{ $json.queue_id }}', '')::uuid,\n  '{{ $json.contact_id }}',\n  '{{ $json.call_id }}',\n  '{{ $json.call_id }}:{{ $json.disposition }}',\n  '{{ $json.disposition }}',\n  '{{ $json.summary.replace(/'/g, \"''\") }}',\n  '',\n  '{{ $json.recording_url }}'\n)\nON CONFLICT (idempotency_key) DO NOTHING;",
    },
    position: [1240, 500],
  },
  output: [{ json: { ok: true } }],
});

const ghlNote = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL - Contact Note',
    parameters: {
      method: 'POST',
      url: '=https://services.leadconnectorhq.com/contacts/{{ $(\"Code - Normalize End Of Call\").item.json.contact_id }}/notes',
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: '=Bearer {{ $env.GHL_API_KEY }}' },
          { name: 'Version', value: '2021-07-28' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' },
        ],
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: '={\"body\":\"AI call completed. Disposition: {{ $(\"Code - Normalize End Of Call\").item.json.disposition }}\\nSummary: {{ $(\"Code - Normalize End Of Call\").item.json.summary || \"n/a\" }}\\nRecording: {{ $(\"Code - Normalize End Of Call\").item.json.recording_url || \"n/a\" }}\"}',
      options: {},
    },
    position: [1520, 500],
  },
  output: [{ json: { ok: true } }],
});

const respondTool = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.3,
  config: {
    name: 'Respond - 200',
    parameters: {
      respondWith: 'json',
      responseBody: '={\"ok\": true, \"contact_id\": \"{{ $(\"Code - Normalize Tool Call\").item.json.contact_id || \\\"\\\" }}\", \"queue_id\": \"{{ $(\"Code - Normalize Tool Call\").item.json.queue_id || \\\"\\\" }}\", \"tool\": \"{{ $(\"Code - Normalize Tool Call\").item.json.tool_name || \\\"\\\" }}\"}',
      options: {},
    },
    position: [1920, 300],
  },
});

export default workflow('fx4UvKUWbqJEY3LK', 'LT - Voice Agent V1 Vapi Callback + Tools')
  .add(webhook)
  .to(detect)
  .add(detect)
  .to(toolCheck.output(0).to(toolNormalize))
  .add(toolCheck.output(1).to(immediateAck))
  .add(toolCheck.output(1).to(statusCheck))
  .add(toolNormalize)
  .to(toolSwitch)
  .add(toolSwitch.output(0).to(pgStatus))
  .add(toolSwitch.output(1).to(pgDnc))
  .add(toolSwitch.output(2).to(pgLog))
  .add(toolSwitch.output(3).to(slackLead))
  .add(toolSwitch.output(4).to(endNormalize))
  .add(pgStatus)
  .to(ghlTags)
  .add(ghlTags)
  .to(respondTool)
  .add(pgDnc)
  .to(ghlDnc)
  .add(ghlDnc)
  .to(respondTool)
  .add(pgLog)
  .to(respondTool)
  .add(slackLead)
  .to(respondTool)
  .add(statusCheck.output(0).to(timerState))
  .add(statusCheck.output(1).to(endNormalize))
  .add(timerState)
  .to(timerCheck)
  .add(timerCheck.output(0).to(waitWarn))
  .add(waitWarn)
  .to(warnCheck)
  .add(warnCheck)
  .to(warnHttp)
  .add(warnHttp)
  .to(waitEnd)
  .add(waitEnd)
  .to(endCheck)
  .add(endCheck)
  .to(endHttp)
  .add(endNormalize)
  .to(insertAttempt)
  .add(insertAttempt)
  .to(ghlNote)
  .add(immediateAck)
  .add(respondTool);
