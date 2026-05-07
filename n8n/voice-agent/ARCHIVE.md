# Voice Agent Archive

This file records retired or non-production voice workflows and exports so future readers do not confuse them with the current production pair.

## Production workflows
- `LT - Voice Agent V1 Outbound Dialer (Vapi)` (`orJrDqR6hQjgPLpg`)
- `LT - Voice Agent V1 Vapi Callback + Tools` (`fx4UvKUWbqJEY3LK`)

## Archived n8n workflows
- `LT - Voice Agent V1 Vapi Callback + Tools Copy` (`R1gTdLkbjJUPAr6u`) - archived after validation
- `LT - Voice Agent IF Test` (`cd3Gv3llKB8XOUgg`) - archived test workflow
- `LT - Voice Agent Switch Test` (`pMMPwm2RLjuYqjZ7`) - archived test workflow
- `LT - Voice Agent Switch Branch Test` (`Qdl2a9KMJnIw745d`) - archived test workflow

## Historical local exports
- `n8n-workflow/lt-voice-agent-v1.json` - legacy outbound dialer export
- `n8n-workflow/lt-voice-agent-vapi-callback-v1.json` - legacy split callback export
- `n8n-workflow/lt-voice-agent-vapi-callback-v1-merged.json` - source export for the current merged callback/tool workflow
- `n8n-workflow/lt-voice-agent-vapi-callback-v1-backup-2026-05-07.json` - backup snapshot created during the merge

## How to read this archive
- If a workflow ID appears above, it is not part of the production set.
- Production voice traffic should always flow through the merged callback URL and the outbound dialer listed above.
