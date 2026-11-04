# Active-name exception guard and credential-reference read — 2026-11-04

**Method:** direct read-only GETs against n8n-lt for the ten IDs in the active-name exception register. The audit emitted only the names of Config assignments, selected nonsecret scalar values (`defaultDryRun`, candidate/batch limits), credential type/name references, trigger metadata, and static endpoint host/path. It did not emit secret values, allowlist contents, arbitrary node parameters, or execution payloads. No workflow was executed, toggled, or changed.

All ten definitions returned active and unarchived with matching draft/active version IDs in this read. All observed entry triggers were enabled. Credential references are inventory names only; their validity/authorization was not tested.

| ID | Safe scalar values observed | Operational implication / remaining check |
|---|---|---|
| `0jDKgG8VvmfyORQn` | `defaultDryRun=true` | Webhook ingest is not disabled by that guard; caller authentication and write acceptance not verified. |
| `8UXlpoMJnQ229AuG` | `defaultDryRun=false`, `candidateLimit=250` | **Scheduled active release path is live-send/enrollment capable. Do not run or toggle.** Rate/safety-buffer semantics and recent release-log acceptance need review. Postgres reference name: `Postgres account`. |
| `CfpedDQWxoJLEMdL` | No dry-run scalar in the allowlisted Config fields | Webhook processes provider events and has GHL/DB write paths. The n8n credential references include `Postgres account`, `LT Sales Navigator Unipile V2 API (verified)`, and `LT Sales Navigator GHL OAuth2`; provider subscription/OAuth health remain unverified. |
| `Q3Ivnwe4z2Y3cD7A` | `defaultDryRun=true` | SMS sender currently guarded by dry-run per the selected Config scalar; auth/caller and provider reconciliation remain unverified. Credential/reference names include managed Postgres and workflow Config keys. |
| `ToMOV6FElZD4ezZN` | No dry-run scalar in the allowlisted Config fields | Scheduled Meta ingest writes to Postgres; latest execution evidence is separately recorded in the continuation addendum. Duplicate/overlap with the other Meta ingest path remains open. |
| `ZiYEBuP7xdddhnUB` | No dry-run scalar in the allowlisted Config fields | Active GET/POST gateway; POST path can send to Unipile. Config has OAuth/provider key fields, but only their names were read. Portal callback/install state remains unverified. |
| `b41Sas8FVVrytZrl` | `defaultDryRun=true`, `maxPerRun=200`, `maxPerSenderPerDay=2333` | Active scheduled dispatcher but currently dry-run by the selected scalar; recipient allowlist contents and queue state were not read. Postgres credential reference name: `Postgres account`. |
| `t5frjtbuKzVZI294` | No dry-run scalar in the allowlisted Config fields | Active webhook intake has Postgres campaign-write path; GHL caller identity and request acceptance remain unknown. |
| `toUG1yPDmFG48KEP` | `defaultDryRun=false`, `candidateLimit=85` | **Scheduled active DAN release path is live-send/enrollment capable. Do not run or toggle.** Current rate/selection guard semantics and recent release-log acceptance need review. Postgres reference name: `Postgres account`. |
| `vRXRFC6IwIxUME2k` | `defaultDryRun=true`, `maxRecipientsPerCampaign=0` | Active scheduled queue builder is currently guarded by dry-run per the selected scalar. The meaning of zero and recipient-selection state were not revalidated in this read. Postgres reference name: `Postgres account`. |

**Acceptance remains partial:** this is not a full guard audit. Code-node logic was not emitted or independently traced, exact schedule expressions/timezones were not yet extracted, allowlist content was deliberately excluded, and no send/write acceptance test was performed. The `defaultDryRun=false` results mean only that those current Config booleans are false; they do not prove a send occurred in the sampled executions. Preserve current live state and keep this evidence read-only.

## Schedule fields — read-only continuation

Exact `Schedule Trigger` parameters and workflow-level `settings.timezone` were extracted from fresh n8n-lt GETs on 2026-11-04. Values are recorded as configured; this is not proof of when n8n actually schedules/fires them.

| Workflow ID | Trigger parameter | Workflow timezone | Note |
|---|---|---|---|
| `8UXlpoMJnQ229AuG` Emerald release | `rule.interval=[{field:"hours"}]` | `UTC` | Interval has no explicit `hoursInterval` value in the returned definition; actual cadence is unresolved. Do not infer hourly from the node label/history. |
| `ToMOV6FElZD4ezZN` Meta Ads ingest | `rule.interval=[{field:"minutes",minutesInterval:1440}]` | `UTC` | Definition says 1,440-minute interval; do not modify based on historical schedule concerns. |
| `b41Sas8FVVrytZrl` mass-email dispatcher | `rule.interval=[{field:"minutes",minutesInterval:5}]` | `America/Los_Angeles` | Active trigger, currently `defaultDryRun=true` per guard audit. |
| `toUG1yPDmFG48KEP` DAN release | `rule.interval=[{field:"minutes",minutesInterval:30}]` | `UTC` | Active trigger, currently `defaultDryRun=false`; live-send capable. |
| `vRXRFC6IwIxUME2k` mass-email queue | `rule.interval=[{field:"minutes",minutesInterval:5}]` | `America/Los_Angeles` | Active trigger, currently `defaultDryRun=true` per guard audit. |

No trigger was run or toggled. The Emerald schedule's incomplete-looking interval needs a separate read-only runtime/schedule-registration investigation; no production change is authorized by this observation.
