#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

$envFile = '.env'
if (-Not (Test-Path $envFile)) {
  Write-Error '.env not found in repository root'
  exit 1
}
$envText = Get-Content $envFile -Raw
if ($envText -match 'N8N_API_KEY_LT=(.+)') {
  $apiKey = $Matches[1].Trim()
} else {
  Write-Error 'N8N_API_KEY_LT not found in .env'
  exit 1
}

$apiBase = 'https://automations.livetransparent.com'
$headers = @{ 'x-n8n-api-key' = $apiKey }
$workflows = @('Q3Ivnwe4z2Y3cD7A','AEi1VCzkLvaYFr4U')
$backupDir = Join-Path 'n8n' 'backups'
if (-Not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir | Out-Null }

function Replace-SendBlock($js, $workflowId) {
  $pattern = '(?s)const\s+sendRes\s*=\s*await\s+apiRequest\.call\(this,\s*\{.*?\};\s*\n\s*\}\s*\n\s*if\s*\(!sendRes\.ok\)\s*\{.*?\}\s*\n\s*const\s+providerResponse\s*=\s*sendRes\.data\s*\|\|\s*\{\s*\}'
  if (-not ([regex]::IsMatch($js,$pattern))) {
    $pattern2 = '(?s)const\s+sendRes\s*=\s*await\s+apiRequest\.call\(this,\s*\{.*?\}\);\s*\n.*?const\s+providerResponse\s*=\s*sendRes\.data\s*\|\|\s*\{\s*\}'
    if (-not ([regex]::IsMatch($js,$pattern2))) { return $null }
    $pattern = $pattern2
  }
  $snippet = @'
// --- Idempotent send via central n8n webhook (inserted) ---
const webhookUrl = "' + $apiBase + '/webhook/lt-sms-send";
const webhookPayload = {
  contact_id: resolvedContact?.contactId || '',
  phone: contactPhone,
  workflow_id: "' + $workflowId + '",
  template_id: resolvedTemplateKey || templateKeyInput || '',
  message_body: text,
  simulate: true
};
const webhookRes = await apiRequest.call(this, { method: 'POST', url: webhookUrl, headers: { 'Content-Type': 'application/json' }, body: webhookPayload });
if (!webhookRes.ok) {
  return [{ json: { ok: false, dryRun: false, error: 'idempotent_webhook_error', message: 'Failed to call idempotent webhook', details: webhookRes.data || webhookRes } }];
}
const whData = webhookRes.data || {};
if (whData.status === 'duplicate') {
  return [{ json: { ok: false, dryRun: false, error: 'duplicate_send', message: 'Duplicate suppressed by idempotency layer', sent_at: whData.sent_at || null } }];
}
const providerResponse = whData.provider_response || whData;
const providerMessageId = providerResponse?.id || providerResponse?.messageId || '';
// --- end idempotent send ---
'@
  $new = [regex]::Replace($js,$pattern,$snippet)
  return $new
}

foreach ($id in $workflows) {
  try {
    Write-Host "Fetching workflow $id"
    $wf = Invoke-RestMethod -Method Get -Uri "${apiBase}/rest/workflows/$id" -Headers $headers
    $backupPath = Join-Path $backupDir "$id.json"
    $wf | ConvertTo-Json -Depth 99 | Out-File -FilePath $backupPath -Encoding UTF8
    Write-Host "Backed up to $backupPath"
    $nodes = $wf.activeVersion.nodes
    $patched = $false
    for ($i=0; $i -lt $nodes.Count; $i++) {
      $node = $nodes[$i]
      if ($node.name -and $node.name -match '(?i)validate' -and $node.name -match '(?i)send') {
        if ($node.parameters.jsCode) {
          $orig = $node.parameters.jsCode
          $updated = Replace-SendBlock $orig $id
          if ($updated -ne $null -and $updated -ne $orig) {
            $nodes[$i].parameters.jsCode = $updated
            $patched = $true
            Write-Host "Patched node '$($node.name)' in workflow $id"
          } else { Write-Warning "Could not patch node '$($node.name)' in workflow $id (pattern not found)" }
        } elseif ($node.parameters.functionCode) {
          $orig = $node.parameters.functionCode
          $updated = Replace-SendBlock $orig $id
          if ($updated -ne $null -and $updated -ne $orig) {
            $nodes[$i].parameters.functionCode = $updated
            $patched = $true
            Write-Host "Patched function node '$($node.name)' in workflow $id"
          } else { Write-Warning "Could not patch function node '$($node.name)' in workflow $id (pattern not found)" }
        }
      }
    }
    if (-not $patched) { Write-Warning "No patches applied to workflow $id; skipping update"; continue }
    if ($wf.activeVersion) { $wf.activeVersion.nodes = $nodes } else { $wf.nodes = $nodes }
    $json = $wf | ConvertTo-Json -Depth 99
    Write-Host "Updating workflow $id"
    $resp = Invoke-RestMethod -Method Put -Uri "${apiBase}/rest/workflows/$id" -Headers $headers -Body $json -ContentType 'application/json'
    Write-Host "Updated workflow $id"
  } catch {
    Write-Error ("Error processing {0}: {1}" -f $id, $_)
  }
}

# Import idempotent workflow
$importPath = 'n8n/workflows/lt-sms-idempotent.json'
if (Test-Path $importPath) {
  Write-Host "Importing idempotent workflow from $importPath"
  $body = Get-Content $importPath -Raw
  try {
    $created = Invoke-RestMethod -Method Post -Uri "${apiBase}/rest/workflows" -Headers $headers -Body $body -ContentType 'application/json'
    Write-Host "Imported workflow id: $($created.id) name: $($created.name)"
  } catch { Write-Error "Failed to import idempotent workflow: $_" }
} else { Write-Warning "$importPath not found; skipped import" }

# Run stubbed smoke test (post twice)
$testPayload = @{ contact_id = 'test-contact-1'; phone = '3105551212'; workflow_id = 'Q3Ivnwe4z2Y3cD7A'; template_id = 'sms_1'; message_body = 'Smoke test'; simulate = $true } | ConvertTo-Json
Write-Host 'Calling webhook first time...'
try { $r1 = Invoke-RestMethod -Method Post -Uri "${apiBase}/webhook/lt-sms-send" -Body $testPayload -ContentType 'application/json'; Write-Host "Response1:"; $r1 | ConvertTo-Json -Depth 5 | Write-Host } catch { Write-Error "Webhook call1 error: $_" }
Start-Sleep -Seconds 1
Write-Host 'Calling webhook second time...'
try { $r2 = Invoke-RestMethod -Method Post -Uri "${apiBase}/webhook/lt-sms-send" -Body $testPayload -ContentType 'application/json'; Write-Host "Response2:"; $r2 | ConvertTo-Json -Depth 5 | Write-Host } catch { Write-Error "Webhook call2 error: $_" }
