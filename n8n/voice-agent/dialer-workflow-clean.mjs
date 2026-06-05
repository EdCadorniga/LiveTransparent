import { workflow, node, trigger, expr, newCredential } from '@n8n/workflow-sdk';

const cronTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Cron - Queue Poll',
    position: [0, 240],
    parameters: { rule: { interval: [{ field: 'minutes', minutesInterval: 1 }] } }
  },
  output: [{}]
});

const timezoneHelpers = `
function zonedParts(timeZone, date) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone,
    hour12: false,
    weekday: 'short',
    hour: '2-digit',
    day: '2-digit',
    minute: '2-digit',
  }).formatToParts(date);
  const map = {};
  for (const part of parts) {
    if (part.type !== 'literal') map[part.type] = part.value;
  }
  return {
    day: map.weekday || '',
    hour: Number(map.hour || 0),
    minute: Number(map.minute || 0),
  };
}

function isBusinessHoursInZone(timeZone, date, startHour, endHour) {
  const parts = zonedParts(timeZone, date);
  const dayIndex = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[parts.day] ?? -1;
  return dayIndex >= 1 && dayIndex <= 5 && parts.hour >= startHour && parts.hour < endHour;
}
`;

const businessHours = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Business Hours',
    position: [240, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `${timezoneHelpers}\nconst now = new Date();\nconst inBusinessHours = isBusinessHoursInZone('America/Chicago', now, 9, 17);\nreturn [{ json: { business_hours_status: inBusinessHours ? 'inside' : 'outside' } }];`
    }
  },
  output: [{ business_hours_status: 'inside' }]
});

const codeBusinessHoursGuard = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Business Hours Guard',
    position: [480, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const status = $json.business_hours_status;\nif (status === 'outside') {\n  return [];\n}\nreturn [{ json: $json }];"
    }
  },
  output: [{ business_hours_status: 'inside' }]
});

const config = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    position: [600, 240],
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: 'workflowName', name: 'workflowName', type: 'string', value: 'LT - Voice Agent V1 Outbound Dialer (Vapi)' },
          { id: 'ghlApiBaseUrl', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: 'ghlApiKey', name: 'ghlApiKey', type: 'string', value: 'pit-b278b3ad-96bd-41fb-ba03-9f927039eb28' },
          { id: 'vapiApiBaseUrl', name: 'vapiApiBaseUrl', type: 'string', value: 'https://api.vapi.ai' },
          { id: 'vapiApiKey', name: 'vapiApiKey', type: 'string', value: '2fa39f7d-28d8-4b43-aca9-3330461c56db' }
        ]
      }
    }
  },
  output: [{
    workflowName: 'LT - Voice Agent V1 Outbound Dialer (Vapi)',
    ghlApiBaseUrl: 'https://services.leadconnectorhq.com',
    ghlApiKey: '***',
    vapiApiBaseUrl: 'https://api.vapi.ai',
    vapiApiKey: '***'
  }]
});

const fetchQueueItem = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Postgres - Fetch Next Queue Item',
    position: [720, 240],
    parameters: {
      operation: 'executeQuery',
      query: "WITH eligible AS (\n  SELECT queue_id, attempt_count, created_at\n  FROM voice_call_queue\n  WHERE status = 'pending'\n    AND dnc = false\n    AND attempt_count < max_attempts\n    AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())\n    AND (locked_at IS NULL OR locked_at < NOW() - INTERVAL '15 minutes')\n), min_attempt AS (\n  SELECT MIN(attempt_count) AS attempt_count\n  FROM eligible\n)\nSELECT queue_id\nFROM eligible\nWHERE attempt_count = (SELECT attempt_count FROM min_attempt)\nORDER BY created_at ASC\nLIMIT 1",
      options: {}
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ queue_id: '', contact_id: '', first_name: '', phone_e164: '', campaign_id: '', lead_timezone: '', max_attempts: 0, attempt_count: 0 }]
});

const getGhlContact = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'HTTP - Get GHL Contact',
    position: [960, 240],
    parameters: {
      method: 'GET',
      url: expr('https://services.leadconnectorhq.com/contacts/{{ $json.contact_id }}'),
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $(\"Config\").item.json.ghlApiKey }}') },
          { name: 'Version', value: '2023-02-21' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      options: { response: { response: { responseFormat: 'json' } } }
    }
  },
  output: [{ contact: { id: '', phone: '' } }]
});

const checkPhone = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Check Phone',
    position: [1200, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `${timezoneHelpers}\nconst queueCtx = $('Postgres - Fetch Next Queue Item').item.json;\nconst body = $json;\nconst ghlContact = body.contact || body;\nconst ghlPhone = ghlContact.phone || '';\nconst fallbackPhone = queueCtx.phone_e164 || '';\nconst phone = ghlPhone || fallbackPhone;\nconst isValidE164 = /^\\+[1-9]\\d{6,14}$/.test(phone);\nconst validPhone = isValidE164 ? phone : '';\nconst ghlContactId = String(ghlContact.id || queueCtx.contact_id || '').trim();\nconst tags = Array.isArray(ghlContact.tags) ? ghlContact.tags : [];\nconst hasQueueRemovalTag = tags.some(tag => {\n  if (typeof tag === 'string') return ['vapi_voicemail', 'vapi_qualified'].includes(tag.toLowerCase());\n  if (tag && typeof tag === 'object') {\n    const value = tag.name || tag.label || tag.tag || tag.id || '';\n    return ['vapi_voicemail', 'vapi_qualified'].includes(String(value).toLowerCase());\n  }\n  return false;\n});\nconst tz = queueCtx.lead_timezone || ghlContact.timezone || '';\nconst now = new Date();\nlet outside_hours = false;\nif (tz) {\n  try {\n    outside_hours = !isBusinessHoursInZone(tz, now, 9, 17);\n  } catch (e) {\n    outside_hours = !isBusinessHoursInZone('America/Chicago', now, 12, 14);\n  }\n} else {\n  outside_hours = !isBusinessHoursInZone('America/Chicago', now, 12, 14);\n}\nreturn [{ json: { ...queueCtx, ghl_contact_id: ghlContactId, phone_e164: hasQueueRemovalTag ? '' : validPhone, phone_source: ghlPhone ? 'ghl' : 'queue', outside_hours, skip_reason: hasQueueRemovalTag ? 'queue_removal_tag_present' : '' } }];`
    }
  },
  output: [{ phone_e164: '', phone_source: '', outside_hours: false }]
});

const switchPhoneMissing = node({
  type: 'n8n-nodes-base.switch',
  version: 3.4,
  config: {
    name: 'Switch - Phone Missing',
    position: [1440, 240],
    parameters: {
      rules: {
        values: [
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3
              },
              conditions: [
                {
                  leftValue: '={{$json.phone_e164}}',
                  rightValue: '',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-phone-missing'
                }
              ],
              combinator: 'and'
            }
          }
        ]
      },
      options: {}
    }
  }
});

const releaseLock = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Postgres - Release Lock',
    position: [1680, 40],
    parameters: {
      operation: 'executeQuery',
      query: "UPDATE voice_call_queue SET locked_at = NULL, lock_owner = NULL, attempt_count = GREATEST(attempt_count - 1, 0), status = CASE WHEN COALESCE(NULLIF($2, ''), '') = 'queue_removal_tag_present' THEN 'completed' ELSE status END, updated_at = NOW() WHERE queue_id = $1;",
      options: { queryReplacement: expr('{{ [$json.queue_id, $json.skip_reason || ""] }}') }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ queue_id: '' }]
});

const endNoPhone = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'End - No Phone',
    position: [1920, 40],
    parameters: { mode: 'manual' }
  },
  output: [{}]
});

const switchContactHours = node({
  type: 'n8n-nodes-base.switch',
  version: 3.4,
  config: {
    name: 'Switch - Contact Hours',
    position: [1680, 360],
    parameters: {
      rules: {
        values: [
          {
            conditions: {
              options: {
                caseSensitive: true,
                leftValue: '',
                typeValidation: 'strict',
                version: 3
              },
              conditions: [
                {
                  leftValue: '={{$json.outside_hours}}',
                  rightValue: 'true',
                  operator: { type: 'string', operation: 'equals' },
                  id: 'switch-outside-hours'
                }
              ],
              combinator: 'and'
            }
          }
        ]
      },
      options: {}
    }
  }
});

const releaseLockTz = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Postgres - Release Lock (Timezone)',
    position: [1920, 480],
    parameters: {
      operation: 'executeQuery',
      query: "UPDATE voice_call_queue SET locked_at = NULL, lock_owner = NULL, attempt_count = GREATEST(attempt_count - 1, 0), updated_at = NOW() WHERE queue_id = $1;",
      options: { queryReplacement: expr('{{ $json.queue_id }}') }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ queue_id: '' }]
});

const endOutsideContactHours = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'End - Outside Contact Hours',
    position: [2160, 480],
    parameters: { mode: 'manual' }
  },
  output: [{}]
});

const buildVapiBody = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Vapi Body',
    position: [1920, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const data = $input.all()[0].json;\nreturn [{\n  json: {\n    body: {\n      phoneNumberId: 'bd4ba248-a2b4-4738-b701-7c6a5ebb5bb4',\n      customer: { number: data.phone_e164 },\n      assistantId: '3f9bbfd2-efa6-4381-81e6-26f2452d28f1',\n      assistantOverrides: {\n        variableValues: {\n          contact_id: data.contact_id,\n          ghl_contact_id: data.ghl_contact_id || data.contact_id,\n          queue_id: data.queue_id,\n          campaign_id: data.campaign_id,\n          lead_timezone: data.lead_timezone || '',\n          first_name: data.first_name || ''\n        },\n        metadata: {\n          source: 'n8n-outbound-dialer',\n          contact_id: data.contact_id,\n          ghl_contact_id: data.ghl_contact_id || data.contact_id,\n          queue_id: data.queue_id,\n          campaign_id: data.campaign_id\n        }\n      }\n    }\n  }\n}];"
    }
  },
  output: [{ body: '{}' }]
});

const startVapiCall = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'HTTP - Start Vapi Call',
    position: [2160, 240],
    parameters: {
      method: 'POST',
      url: expr('https://api.vapi.ai/call'),
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $(\"Config\").item.json.vapiApiKey }}') },
          { name: 'Content-Type', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("={{ $('Build Vapi Body').item.json.body }}"),
      options: {}
    }
  },
  output: [{ id: '', status: '' }]
});

const restoreContext = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Code - Restore Queue Context',
    position: [2400, 240],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: "const ctx = $('Postgres - Fetch Next Queue Item').item.json;\nconst contact = $('Code - Check Phone').item.json || {};\nreturn [{ json: { ...ctx, ghl_contact_id: contact.ghl_contact_id || ctx.contact_id, vapi_response: $json } }];"
    }
  },
      output: [{ queue_id: '', contact_id: '', ghl_contact_id: '', vapi_response: {} }]
});

const markAttempted = node({
  type: 'n8n-nodes-base.postgres',
  version: 2.6,
  config: {
    name: 'Postgres - Mark Attempted',
    position: [2640, 240],
    parameters: {
      operation: 'executeQuery',
      query: "UPDATE voice_call_queue SET locked_at = NULL, lock_owner = NULL, attempt_count = attempt_count + 1, last_attempt_at = NOW(), next_attempt_at = NOW() + INTERVAL '3 days', updated_at = NOW() WHERE queue_id = $1;",
      options: { queryReplacement: expr('{{ $json.queue_id }}') }
    },
    credentials: { postgres: newCredential('Postgres account') }
  },
  output: [{ queue_id: '', contact_id: '' }]
});

const createCallNote = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'GHL - Create Call Note',
    position: [2880, 240],
    parameters: {
      method: 'POST',
      url: expr('={{ \"https://services.leadconnectorhq.com/contacts/\" + ($json.ghl_contact_id || $json.contact_id || $(\"Code - Check Phone\").item.json.ghl_contact_id || $(\"Code - Check Phone\").item.json.contact_id || $(\"Postgres - Fetch Next Queue Item\").item.json.contact_id || \"\") + \"/notes\" }}'),
      sendHeaders: true,
      headerParameters: {
        parameters: [
          { name: 'Authorization', value: expr('Bearer {{ $(\"Config\").item.json.ghlApiKey }}') },
          { name: 'Version', value: '2023-02-21' },
          { name: 'Content-Type', value: 'application/json' },
          { name: 'Accept', value: 'application/json' }
        ]
      },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('={{ { body: "AI outbound Vapi call started. queue_id=" + $json.queue_id + ", contact_id=" + ($json.ghl_contact_id || $json.contact_id || $(\"Code - Check Phone\").item.json.ghl_contact_id || $(\"Code - Check Phone\").item.json.contact_id || $(\"Postgres - Fetch Next Queue Item\").item.json.contact_id || \"\") } }}'),
      options: {}
    }
  },
  output: [{ id: '' }]
});

export default workflow('dialer-v3-switch', 'LT - Voice Agent V1 Outbound Dialer (Vapi)')
  .add(cronTrigger)
  .to(businessHours)
  .to(codeBusinessHoursGuard)
  .to(config)
  .to(fetchQueueItem)
  .to(getGhlContact)
  .to(checkPhone)
  .to(switchPhoneMissing
    .output(0).to(releaseLock.to(endNoPhone))
    .output(1).to(switchContactHours
      .output(0).to(releaseLockTz.to(endOutsideContactHours))
      .output(1).to(buildVapiBody.to(startVapiCall).to(restoreContext).to(markAttempted).to(createCallNote))
    )
  );
