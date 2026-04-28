import { workflow, node } from '@n8n/workflow-sdk';

export default workflow('patch-sequencer-inputs', 'Patch Sequencer Inputs')
  .editNode('When Executed by Another Workflow', (n) => ({
    ...n,
    workflowInputs: [
      {
        name: 'contactData',
        type: 'json',
        default: {},
      },
    ],
    alwaysOutputData: true,
  }));
