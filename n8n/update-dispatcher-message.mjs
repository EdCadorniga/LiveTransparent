import { workflow, node, trigger } from '@n8n/workflow-sdk';

const newMessage = "Hi {first_name}, I'm Cameron co-founder of Transparent eCom. We help brands in regulated industries advertise on social/search without restrictions and at scale. Are you currently running ads on social/search?";

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Schedule Trigger',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '0 15-21 * * 1-5' }] } },
    position: [0, 0]
  },
  output: [{}]
});

const configNode = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Config',
    parameters: {
      assignments: {
        assignments: [
          { id: 'wfn', name: 'workflowName', type: 'string', value: 'LT - GHL LinkedIn Connect Dispatcher' },
          { id: 'loc', name: 'locationId', type: 'string', value: 'Zwz4relUXVPxx8uohnjV' },
          { id: 'gBase', name: 'ghlApiBaseUrl', type: 'string', value: 'https://services.leadconnectorhq.com' },
          { id: 'gKey', name: 'ghlApiKey', type: 'string', value: 'pit-b278b3ad-96bd-41fb-ba03-9f927039eb28' },
          { id: 'uBase', name: 'unipileApiBaseUrl', type: 'string', value: 'https://api42.unipile.com:17256/api/v1' },
          { id: 'uKey', name: 'unipileApiKey', type: 'string', value: 'Mb1oWs6Z.YZWq+uQp/V4DPMLf2UN6i9bbS2IqGX/MDJ4y3DExshc=' },
          { id: 'uAcct', name: 'unipileAccountId', type: 'string', value: 'V9eiHiDpRmCtan0YNdzsQw' },
          { id: 'tag', name: 'ghlSuccessTag', type: 'string', value: 'linkedin_connection_requested' },
          { id: 'cfName', name: 'linkedinCustomFieldName', type: 'string', value: 'Apollo Person Linkedin URL' },
          { id: 'maxQ', name: 'maxQueueSize', type: 'number', value: 50 },
          { id: 'maxB', name: 'batchSize', type: 'number', value: 10 },
          { id: 'dRun', name: 'defaultDryRun', type: 'boolean', value: false },
          { id: 'msg', name: 'defaultMessage', type: 'string', value: newMessage }
        ]
      }
    },
    position: [224, 96]
  },
  output: [{}]
});

const dispatchCode = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Dispatch LinkedIn Requests',
    parameters: { jsCode: 'placeholder' },
    position: [448, 96]
  },
  output: [{}]
});

const resultNode = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Result',
    parameters: {
      assignments: {
        assignments: [
          { id: 'qf', name: 'queue_found', type: 'number', value: '={{ $json.queue_found }}' },
          { id: 'bs', name: 'batch_size', type: 'number', value: '={{ $json.batch_size }}' },
          { id: 's', name: 'sent', type: 'number', value: '={{ $json.sent }}' },
          { id: 'dr', name: 'dry_runs', type: 'number', value: '={{ $json.dry_runs }}' },
          { id: 'f', name: 'failed', type: 'number', value: '={{ $json.failed }}' },
          { id: 'st', name: 'sent_today', type: 'number', value: '={{ $json.sent_today }}' },
          { id: 'n', name: 'note', type: 'string', value: '={{ $json.note }}' }
        ]
      }
    },
    position: [672, 96]
  },
  output: [{}]
});

const manualTrigger = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'Manual Trigger', position: [0, 192] },
  output: [{}]
});

export default workflow('S32vc8pjJIBZZHLK', 'LT - GHL LinkedIn Connect Dispatcher')
  .add(scheduleTrigger)
  .to(configNode)
  .to(dispatchCode)
  .to(resultNode)
  .add(manualTrigger)
  .to(configNode);
