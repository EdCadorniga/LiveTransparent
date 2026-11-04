# Read-only n8n-lt and Coolify follow-up — 2026-11-05

This fresh point-in-time check supplements, and does not replace, the [2026-11-04 n8n inventory](n8n-workflow-inventory-2026-11-04.md), [active-name exception register](n8n-active-name-exceptions-2026-11-04.md), [host census](coolify-host-inventory-2026-11-04.md), and [Coolify configuration evidence](coolify-configuration-2026-11-04.md).

## Method and safety

- Reviewed `docs/transition/verify_readonly.py` and `inventory_n8n_readonly.py` before running them. The n8n helper performs only HTTP GETs against the hard-coded `https://automations.livetransparent.com/api/v1` n8n-lt endpoint. The verifier reads definitions and emits allowlisted workflow metadata, not parameters or credential values.
- The verifier's host phase runs read-only `docker ps`, `docker inspect`, bounded `find` metadata listings, and `docker compose config --format json` parsing. It emits mount/network metadata, backup-file metadata, environment variable names, and selected generated-Compose metadata. It does not read saved Coolify resource definitions, extract backups, or perform changes.
- No workflow was executed or toggled. No n8n/GHL/CRM/provider/ledger state was changed. No service, backup, or repository artifact was changed.

## Ten DRAFT/STAGED/TEMP-name exceptions

Fresh n8n-lt GETs returned all ten as `active=true`, `archived=false`, with enabled triggers and matching draft/active version IDs. This verifies only the returned workflow metadata and trigger enablement; it does not establish current caller health, delivery, guards, or safe send behavior.

| Workflow ID | Draft and active version | Enabled trigger metadata |
|---|---|---|
| `0jDKgG8VvmfyORQn` | `70326727-ce6c-4a63-b320-d7b2826dcda0` | POST `lt-emerald-campaign-postgres-intake` |
| `8UXlpoMJnQ229AuG` | `c63eaa03-8907-47a0-820a-c4143f89949a` | Schedule Trigger enabled; interval details not read in this bounded check |
| `CfpedDQWxoJLEMdL` | `dd6b78e3-5bd5-4ce4-90f1-ecb82f2b66ed` | POST `lt-unipile-sales-navigator-new-messages` |
| `Q3Ivnwe4z2Y3cD7A` | `b69a183e-273a-43f9-b06d-b2bd1575543b` | POST `lt-simpletexting-send-sms` |
| `ToMOV6FElZD4ezZN` | `2ffc62df-c126-4a99-a6b2-0adfed8608f4` | Schedule Trigger enabled; interval details not read in this bounded check |
| `ZiYEBuP7xdddhnUB` | `66019014-f467-4bea-ac1c-d47f6dbfbd07` | GET and POST `lt-sales-navigator-provider` |
| `b41Sas8FVVrytZrl` | `bf892c33-edca-416d-9b74-cff2ccea9fdf` | Schedule Trigger enabled; interval details not read in this bounded check |
| `t5frjtbuKzVZI294` | `9523da34-9306-462b-b24f-72594a62a023` | POST `lt-email-template-trigger-stage` |
| `toUG1yPDmFG48KEP` | `3f5b124b-595e-4573-b75e-a6d7ba93cc70` | Schedule Trigger enabled; interval details not read in this bounded check |
| `vRXRFC6IwIxUME2k` | `714b2d22-777c-4006-a233-d7e0fa6eb930` | Schedule Trigger enabled; interval details not read in this bounded check |

Do not infer dry-run, caller, or send safety from names or this metadata. Continue to preserve each workflow's current state; no rename or remediation is authorized by this read.

## Coolify and recovery metadata

- Host metadata again listed 13 running containers. n8n and its external runner remained on the shared/private networks; Postgres remained on the shared/stack networks. This metadata read did not inspect logs or application data.
- Generated n8n Compose parsed to image `n8nio/n8n:2.44.6`; generated Postgres Compose parsed to `postgres:17.7`. The generated reports Compose listed only `coolify`, while Docker network metadata listed both `coolify` and `coolify-shared`. This is a repeated observation of drift, not a change request.
- The bounded backup metadata search returned the previously documented root-only pre-upgrade set. It does not establish scheduled backup coverage, archive integrity, off-host copies, encryption-key custody, or restore readiness. Existing backups were not opened or changed; restore remains untested.
- This verifier does not read Coolify's saved resource definitions. Saved/generated/repository drift, full route ownership, backup schedule/owner, and recovery acceptance therefore remain open.

## Outcome and next action

This read strengthens the dated observations but does not close exception acceptance or hosting/recovery checks. Keep caller/guard acceptance, saved Coolify configuration, route ownership, backup coverage, and restore explicitly partial or blocked. Any restore test, service change, or production workflow change needs separate scoped approval.
