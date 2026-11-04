# Active-name exception read-only continuation — 2026-11-04

**Method:** direct read-only GETs against `https://automations.livetransparent.com/api/v1` using only the locally configured n8n-lt API key. Read workflow definitions and up to five execution-list metadata rows per workflow (`includeData=false`). No execution payloads or node parameter/credential values were returned or recorded. No workflow was run, toggled, or changed.

All ten IDs in the [original exception register](n8n-active-name-exceptions-2026-11-04.md) were freshly read. Each remains API-active, unarchived, and at matching draft/active version IDs. A second read confirms every webhook/schedule trigger found is `disabled=false`; exact webhook paths/methods are included below for webhook-triggered items. This is a point-in-time read, not proof of business safety or provider delivery.

| Workflow ID | Trigger / schedule evidence | Recent execution metadata returned | Guard acceptance |
|---|---|---|---|
| `0jDKgG8VvmfyORQn` | POST `/lt-emerald-campaign-postgres-intake` | No rows returned by the queried list endpoint | Guard value and caller unverified |
| `8UXlpoMJnQ229AuG` | Schedule trigger | Five most recent returned rows were `success`; newest observed `2026-11-04T15:00:13Z` | `DryRun Safe` node name only; guard value, caps, and release-log writes unverified |
| `CfpedDQWxoJLEMdL` | POST `/lt-unipile-sales-navigator-new-messages` | Five most recent returned rows were `success`; newest observed `2026-11-04T10:49:43Z` | Claim/dedup node names observed; provider subscription and OAuth health unverified |
| `Q3Ivnwe4z2Y3cD7A` | POST `/lt-simpletexting-send-sms` | No rows returned by the queried list endpoint | Auth/send guard value and provider reconciliation unverified |
| `ToMOV6FElZD4ezZN` | Schedule and manual triggers | Three most recent returned rows were `success`; newest observed `2026-11-04T13:31:04Z` | Duplicate/overlap with the other Meta ingest path unverified |
| `ZiYEBuP7xdddhnUB` | GET and POST `/lt-sales-navigator-provider` | No rows returned by the queried list endpoint | Callback-vs-provider route purpose remains as in the original register; portal config unverified |
| `b41Sas8FVVrytZrl` | Schedule and manual triggers | Five most recent returned rows were `success`; newest observed `2026-11-04T15:20:07Z` | Dry-run/allowlist/cap values not inspected; these successes do not prove send or no-send behavior |
| `t5frjtbuKzVZI294` | POST `/lt-email-template-trigger-stage` | No rows returned by the queried list endpoint | Request validation node name observed; GHL caller identity and acceptance unverified |
| `toUG1yPDmFG48KEP` | Schedule and manual triggers | Five most recent returned rows were `success`; newest observed `2026-11-04T15:00:37Z` | `DryRun Safe` node name only; current send/cap configuration unverified |
| `vRXRFC6IwIxUME2k` | Schedule and manual triggers | Five most recent returned rows were `success`; newest observed `2026-11-04T15:20:18Z` | Dry-run/recipient selection values not inspected |

**Limits and next action:** execution rows were metadata-only and the query was capped at five; this does not establish the latest error or behavior inside executions. Empty results are recorded as “no rows returned,” not “no executions.” Workflow schedules were identified by trigger type/node name, but exact cron expressions, timezones, runtime guards, credential references, caller identities, and write/send acceptance remain open. Continue with a credential-safe parameter-name/reference audit and literal caller scan; obtain GHL/provider evidence only through authorized read-only surfaces. Do not execute or toggle any workflow to fill gaps.
