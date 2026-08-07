$ErrorActionPreference = 'Stop'

$lines = Get-Content -LiteralPath '.env'
$apiLine = $lines | Where-Object { $_ -match '^N8N_API_KEY_LT=' } | Select-Object -First 1
$encryptionLine = $lines | Where-Object { $_ -match '^N8N_ENCRYPTION_KEY=' } | Select-Object -First 1
if (-not $apiLine -or -not $encryptionLine) { throw 'Required n8n secrets are missing from .env' }
$apiKey = $apiLine.Substring('N8N_API_KEY_LT='.Length).Trim().Trim('"')
$encryptionKey = $encryptionLine.Substring('N8N_ENCRYPTION_KEY='.Length).Trim().Trim('"')
$headers = @{ 'X-N8N-API-KEY' = $apiKey; 'Content-Type' = 'application/json' }
$base = 'https://automations.livetransparent.com/api/v1/workflows/'

function Derive-Secret($purpose) {
  $sha = [Security.Cryptography.SHA256]::Create()
  $bytes = [Text.Encoding]::UTF8.GetBytes("${encryptionKey}:simpletext:$purpose")
  return ([Convert]::ToBase64String($sha.ComputeHash($bytes))).TrimEnd('=').Replace('+','-').Replace('/','_')
}

$sendSecret = Derive-Secret 'internal-send-v2'
$eventSecret = Derive-Secret 'provider-events-v2'
$intakeSecret = Derive-Secret 'warm-intake-v2'

function Get-Wf($id) { Invoke-RestMethod -Method Get -Uri ($base + $id) -Headers $headers }
function Put-Wf($w) {
  $settings = @{}
  if ($w.settings) {
    foreach ($p in $w.settings.PSObject.Properties) {
      if ($p.Name -ne 'availableInMCP') { $settings[$p.Name] = $p.Value }
    }
  }
  $payload = @{ name = $w.name; nodes = $w.nodes; connections = $w.connections; settings = $settings }
  $json = $payload | ConvertTo-Json -Depth 100 -Compress
  Invoke-RestMethod -Method Put -Uri ($base + $w.id) -Headers $headers -Body $json
}
function Set-Assignment($node, $name, $value, $type = 'string') {
  $assignments = $node.parameters.assignments.assignments
  $existing = $assignments | Where-Object name -eq $name
  if ($existing) { $existing.value = $value }
  else {
    $assignments += [pscustomobject]@{ id = [guid]::NewGuid().ToString(); name = $name; type = $type; value = $value }
    $node.parameters.assignments.assignments = $assignments
  }
}
function Add-Header($node, $name, $value) {
  $parameters = $node.parameters.headerParameters.parameters
  if (-not $parameters) { $parameters = @() }
  $existing = $parameters | Where-Object name -eq $name
  if ($existing) { $existing.value = $value }
  else { $node.parameters.headerParameters.parameters = @($parameters) + [pscustomobject]@{ name = $name; value = $value } }
}

# Public campaign send webhook: authenticate before template/provider work.
$w = Get-Wf 'Q3Ivnwe4z2Y3cD7A'
$cfg = $w.nodes | Where-Object name -eq 'Config'
Set-Assignment $cfg 'authHeaderName' 'x-lt-simpletexting-key'
Set-Assignment $cfg 'authHeaderValue' $sendSecret
$sendCode = $w.nodes | Where-Object name -eq 'Validate + Send SMS'
$marker = 'const cfg = src;'
$auth = @"
const incomingHeaders = src.headers || {};
const expectedWebhookKey = String(cfg.authHeaderValue || '').trim();
const incomingWebhookKey = String(incomingHeaders['x-lt-simpletexting-key'] || incomingHeaders['X-LT-SimpleTexting-Key'] || '').trim();
if (!expectedWebhookKey || incomingWebhookKey !== expectedWebhookKey) return [{ json: { ok: false, error: 'unauthorized' } }];
"@
if (-not $sendCode.parameters.jsCode.Contains('x-lt-simpletexting-key')) { $sendCode.parameters.jsCode = $sendCode.parameters.jsCode.Replace($marker, $marker + "`n" + $auth) }
$out = $w.nodes | Where-Object name -eq 'Mirror to GHL Conversations'
$out.parameters.options.onError = 'continueRegularOutput'
$saved = Put-Wf $w
[pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress

# Internal callers authenticate to the campaign send webhook.
$w = Get-Wf 'dUyOfxllvkxZavaw'; Add-Header ($w.nodes | Where-Object name -eq 'Send Claimed SMS Step') 'x-lt-simpletexting-key' $sendSecret; $saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
$w = Get-Wf '7mSiivR3NhtLIcNz'; Set-Assignment ($w.nodes | Where-Object name -eq 'Config') 'sendAuthHeaderValue' $sendSecret; $saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
$w = Get-Wf 'dZQLlbTLkpE1843X'; Set-Assignment ($w.nodes | Where-Object name -eq 'Config') 'sendAuthHeaderValue' $sendSecret; $saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress

# Idempotent boundary and its internal callers share the internal-send secret.
$w = Get-Wf 'gwaEpWDpTIwsafi8'
$prepare = $w.nodes | Where-Object name -eq 'Prepare Request'
$marker = "const body = (src.body && typeof src.body === 'object') ? src.body : src;"
$auth = "`nconst incomingHeaders = src.headers || {};`nconst expectedWebhookKey = '$sendSecret';`nconst incomingWebhookKey = String(incomingHeaders['x-lt-simpletexting-key'] || incomingHeaders['X-LT-SimpleTexting-Key'] || '').trim();`nif (!expectedWebhookKey || incomingWebhookKey !== expectedWebhookKey) return [{ json: { authRejected: true } }];"
if (-not $prepare.parameters.jsCode.Contains('expectedWebhookKey')) { $prepare.parameters.jsCode = $prepare.parameters.jsCode.Replace($marker, $marker + $auth) }
else { $prepare.parameters.jsCode = [regex]::Replace($prepare.parameters.jsCode, "return \[\{ json: \{ status: 'error', error: 'unauthorized' \} \}\];", "return [{ json: { authRejected: true } }];") }
$claim = $w.nodes | Where-Object name -eq 'Claim Send'
if (-not $claim.parameters.query.Contains('$6::boolean')) {
  $claim.parameters.query = $claim.parameters.query.Replace('VALUES ($1, $2, $3, $4, $5)', 'SELECT $1, $2, $3, $4, $5 WHERE $6::boolean')
  $claim.parameters.query = $claim.parameters.query.Replace('AND provider_response IS NOT NULL', 'AND $6::boolean AND provider_response IS NOT NULL')
  $claim.parameters.query = $claim.parameters.query.Replace("SELECT`n  CASE WHEN EXISTS(SELECT 1 FROM ins)", "SELECT`n  `$6::boolean AS authorized,`n  CASE WHEN EXISTS(SELECT 1 FROM ins)")
  $claim.parameters.options.queryReplacement = '={{ [ $json.contact_id || null, $json.phone || null, $json.workflow_id || null, $json.template_id || null, $json.message_hash || null, $json.authRejected !== true ] }}'
}
if (-not $claim.parameters.query.Contains('AS authorized')) {
  $claim.parameters.query = [regex]::Replace($claim.parameters.query, 'SELECT\s+CASE WHEN EXISTS\(SELECT 1 FROM ins\)', "SELECT`n  `$6::boolean AS authorized,`n  CASE WHEN EXISTS(SELECT 1 FROM ins)")
}
$finalize = $w.nodes | Where-Object name -eq 'Finalize Send'
if (-not $finalize.parameters.jsCode.Contains('row.authorized === false')) { $finalize.parameters.jsCode = $finalize.parameters.jsCode.Replace("if (!row.inserted) {", "if (row.authorized === false) return [{ json: { status: 'error', error: 'unauthorized', provider_response: null } }];`n`nif (!row.inserted) {") }
$saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress

$w = Get-Wf 'Q3Ivnwe4z2Y3cD7A'; $code = $w.nodes | Where-Object name -eq 'Validate + Send SMS'; $code.parameters.jsCode = $code.parameters.jsCode.Replace("headers: { 'Content-Type': 'application/json' },", "headers: { 'Content-Type': 'application/json', 'x-lt-simpletexting-key': '$sendSecret' },"); $saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
$w = Get-Wf 'f4VoO1lBWkYRcQai'; $code = $w.nodes | Where-Object name -eq 'Process Provider Outbound'; $code.parameters.jsCode = $code.parameters.jsCode.Replace("'Content-Type': 'application/json',", "'Content-Type': 'application/json',`n      'x-lt-simpletexting-key': '$sendSecret',"); $saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress

# Provider event webhooks authenticate before contact resolution or side effects.
foreach ($item in @(@{ id = 'i0pROHpFtN4LYR0Q'; marker = 'const raw    = $json || {};'; authType = 'inbound' }, @{ id = 'AEi1VCzkLvaYFr4U'; marker = 'const src = $json || {};'; authType = 'event' }, @{ id = 'IyBKMkpYQ7pa0C8V'; marker = 'const src = $json || {};'; authType = 'event' })) {
  $w = Get-Wf $item.id
  $cfg = $w.nodes | Where-Object name -eq 'Config'
  Set-Assignment $cfg 'authHeaderName' 'x-lt-simpletexting-event-key'
  Set-Assignment $cfg 'authHeaderValue' $eventSecret
  $code = $w.nodes | Where-Object { $_.name -like 'Validate + Normalize*' }
  if ($item.authType -eq 'inbound') {
    $auth = "`nconst incomingHeaders = raw.headers || {};`nconst expectedEventKey = String(raw.authHeaderValue || '').trim();`nconst incomingEventKey = String(incomingHeaders['x-lt-simpletexting-event-key'] || incomingHeaders['X-LT-SimpleTexting-Event-Key'] || '').trim();`nif (!expectedEventKey || incomingEventKey !== expectedEventKey) return [{ json: { ok: false, error: 'unauthorized' } }];"
    if (-not $code.parameters.jsCode.Contains('expectedEventKey')) { $code.parameters.jsCode = $code.parameters.jsCode.Replace($item.marker, $item.marker + $auth) }
  }
  $saved = Put-Wf $w
  [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
}

# Reject provider events before the deduplication claim can write an audit row.
foreach ($id in @('i0pROHpFtN4LYR0Q','AEi1VCzkLvaYFr4U','IyBKMkpYQ7pa0C8V')) {
  $w = Get-Wf $id
  $build = $w.nodes | Where-Object name -eq 'Build Event Key'
  $marker = 'const root = $json || {};'
  $auth = "`nconst incomingHeaders = root.headers || {};`nconst expectedEventKey = String(root.authHeaderValue || '').trim();`nconst incomingEventKey = String(incomingHeaders['x-lt-simpletexting-event-key'] || incomingHeaders['X-LT-SimpleTexting-Event-Key'] || '').trim();`nif (!expectedEventKey || incomingEventKey !== expectedEventKey) return [{ json: { ...root, authRejected: true, ok: false, error: 'unauthorized', eventType: 'auth_rejected', eventKey: 'unauthorized', eventContactId: '', campaignKey: 'simpletexting_campaign_v1', eventPayload: {} } }];"
  if ($build.parameters.jsCode.Contains('return [];')) { $build.parameters.jsCode = $build.parameters.jsCode.Replace('return [];', "return [{ json: { ...root, authRejected: true, ok: false, error: 'unauthorized', eventType: 'auth_rejected', eventKey: 'unauthorized', eventContactId: '', campaignKey: 'simpletexting_campaign_v1', eventPayload: {} } }];") }
  elseif ($build.parameters.jsCode.Contains('authRejected') -and -not $build.parameters.jsCode.Contains("eventType: 'auth_rejected'")) { $build.parameters.jsCode = $build.parameters.jsCode.Replace("return [{ json: { ...root, authRejected: true, ok: false, error: 'unauthorized' } }];", "return [{ json: { ...root, authRejected: true, ok: false, error: 'unauthorized', eventType: 'auth_rejected', eventKey: 'unauthorized', eventContactId: '', campaignKey: 'simpletexting_campaign_v1', eventPayload: {} } }];") }
  elseif (-not $build.parameters.jsCode.Contains('authRejected')) { $build.parameters.jsCode = $build.parameters.jsCode.Replace($marker, $marker + $auth) }
  $claim = $w.nodes | Where-Object name -eq 'Claim Event'
  if (-not $claim.parameters.query.Contains('$6::boolean')) {
    $claim.parameters.query = $claim.parameters.query.Replace("FROM lock`n  WHERE NOT EXISTS", "FROM lock`n  WHERE `$6::boolean`n    AND NOT EXISTS")
    $claim.parameters.options.queryReplacement = '={{ [ $json.eventContactId || "", $json.campaignKey || "simpletexting_campaign_v1", $json.eventType, $json.eventKey, JSON.stringify($json.eventPayload || {}), $json.authRejected !== true ] }}'
  }
  if (-not $claim.parameters.query.Contains('AS "authorized"')) { $claim.parameters.query = $claim.parameters.query.Replace('SELECT EXISTS(SELECT 1 FROM claimed)', 'SELECT $6::boolean AS "authorized", EXISTS(SELECT 1 FROM claimed)') }
  $duplicate = $w.nodes | Where-Object name -eq 'Duplicate Event Response'
  $duplicate.parameters.jsCode = "if (`$json.authorized === false) return [{ json: { ok: false, error: 'unauthorized' } }];`nreturn [{ json: { ok: true, duplicateIgnored: true, eventKey: `$json.eventKey || '', nextStep: 'duplicate_event_ignored' } }];"
  $saved = Put-Wf $w
  [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
}

# Active GHL SMS intake is protected separately; the caller must send this header.
$w = Get-Wf '5nYzp9DgQUopzWhR'
$cfg = $w.nodes | Where-Object name -eq 'Config'
Set-Assignment $cfg 'authHeaderName' 'x-lt-simpletexting-intake-key'
Set-Assignment $cfg 'authHeaderValue' $intakeSecret
$code = $w.nodes | Where-Object name -eq 'Resolve Contact + Add Intake Tag'
$marker = 'const body = src.body || {};'
$auth = "`nconst incomingHeaders = src.headers || {};`nconst expectedIntakeKey = String(cfg.authHeaderValue || '').trim();`nconst incomingIntakeKey = String(incomingHeaders['x-lt-simpletexting-intake-key'] || incomingHeaders['X-LT-SimpleTexting-Intake-Key'] || '').trim();`nif (!expectedIntakeKey || incomingIntakeKey !== expectedIntakeKey) return [{ json: { ok: false, error: 'unauthorized' } }];"
if (-not $code.parameters.jsCode.Contains('expectedIntakeKey')) { $code.parameters.jsCode = $code.parameters.jsCode.Replace($marker, $marker + $auth) }
$saved = Put-Wf $w; [pscustomobject]@{ id = $saved.id; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId } | ConvertTo-Json -Compress
