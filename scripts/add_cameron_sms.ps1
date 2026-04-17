Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$apiKeyMatch = [regex]::Match($envText,'N8N_API_KEY_LT=(.+)')
if (-not $apiKeyMatch.Success) { Write-Error "N8N_API_KEY_LT not found in .env"; exit 1 }
$apiKey = $apiKeyMatch.Groups[1].Value.Trim()

$workflowId = 'Q3Ivnwe4z2Y3cD7A'
$workflowUrl = "https://automations.livetransparent.com/api/v1/workflows/$workflowId"

Write-Host "Fetching workflow $workflowId"
try {
    $wf = Invoke-RestMethod -Uri $workflowUrl -Method Get -Headers @{ 'X-N8N-API-KEY' = $apiKey } -ErrorAction Stop
} catch {
    Write-Error "Failed to fetch workflow: $($_.Exception.Message)"
    exit 1
}

$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$backupDir = Join-Path $scriptDir "..\backups"
if (-not (Test-Path $backupDir)) { New-Item -Path $backupDir -ItemType Directory | Out-Null }
$backupPath = Join-Path $backupDir "workflow_$workflowId`_$timestamp.json"
$wf | ConvertTo-Json -Depth 50 | Out-File -FilePath $backupPath -Encoding UTF8
Write-Host "Saved workflow backup to $backupPath"

# Work against activeVersion if present
$active = $wf.activeVersion ?? $wf
$nodes = $active.nodes

$configNode = $nodes | Where-Object { $_.name -eq 'Config' -or $_.id -eq 'config' } | Select-Object -First 1
if (-not $configNode) { Write-Error "Config node not found in workflow"; exit 1 }
Write-Host "Found Config node (id=$($configNode.id), name=$($configNode.name))"

$assignments = $configNode.parameters.assignments.assignments
$templateEntry = $assignments | Where-Object { $_.name -eq 'templateRegistryJson' } | Select-Object -First 1
if (-not $templateEntry) { Write-Error "templateRegistryJson entry not found in Config node"; exit 1 }

$currentJsonStr = $templateEntry.value
if ([string]::IsNullOrWhiteSpace($currentJsonStr)) { $currentJson = @{} } else { try { $currentJson = $currentJsonStr | ConvertFrom-Json -ErrorAction Stop } catch { Write-Error "Failed parsing existing templateRegistryJson"; exit 1 } }

Write-Host "Adding cameron_sms1 to templateRegistryJson"

$cameronEntry = @{
    name = 'Cameron SMS 1 - Site Check'
    message = "Hi, Cameron here—co-founder of Transparent eCom. Saw you checked out our site. If ads have been an issue, I can show you what’s working. Got 10 mins?"
}

if ($currentJson.PSObject.Properties.Name -contains 'cameron_sms1') {
    Write-Host "Key cameron_sms1 already exists — it will be overwritten" -ForegroundColor Yellow
}

$currentJson | Add-Member -NotePropertyName 'cameron_sms1' -NotePropertyValue $cameronEntry -Force

$newJsonStr = ($currentJson | ConvertTo-Json -Depth 50)
$templateEntry.value = $newJsonStr

# Prepare updated workflow payload
$putPayload = @{
    name = $wf.name
    nodes = $active.nodes
    connections = $active.connections
    settings = $active.settings ?? @{}
}

$putBody = $putPayload | ConvertTo-Json -Depth 50

Write-Host "Patching workflow with new template registry..."
try {
    $putUrl = $workflowUrl
    $resp = Invoke-RestMethod -Uri $putUrl -Method Put -Headers @{ 'X-N8N-API-KEY' = $apiKey; 'Content-Type' = 'application/json' } -Body $putBody -ErrorAction Stop
    Write-Host "Workflow patched successfully." -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $scriptDir "workflow_cameron_patch_result.json") -Encoding UTF8
    Write-Host "Patch result saved to scripts/workflow_cameron_patch_result.json"
} catch {
    Write-Error "Failed to patch workflow: $($_.Exception.Message)"
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { }
    }
    Write-Host "Restoring from backup..."
    $backupContent = Get-Content $backupPath -Raw
    try {
        Invoke-RestMethod -Uri $putUrl -Method Put -Headers @{ 'X-N8N-API-KEY' = $apiKey; 'Content-Type' = 'application/json' } -Body $backupContent -ErrorAction Stop
        Write-Host "Restored workflow from backup." -ForegroundColor Yellow
    } catch {
        Write-Error "Failed to restore workflow from backup: $($_.Exception.Message)"
    }
    exit 1
}

Write-Host "Running dry-run test for cameron_sms1"
$webhookUrl = 'https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms'
$headers = @{ 'x-lt-webhook-key' = 'Lt9Qv2Xm'; 'Content-Type' = 'application/json' }
$testBody = @{ contactId = 'test-cam'; contactPhone = '15555551212'; templateKey = 'cameron_sms1'; contact = @{ first_name = 'Test'; last_name = 'Cameron'; email = 'test@example.com' }; dryRun = $true } | ConvertTo-Json -Depth 10
try {
    $testResp = Invoke-RestMethod -Uri $webhookUrl -Method Post -Headers $headers -Body $testBody -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Dry-run response:" -ForegroundColor Green
    $testResp | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $scriptDir "cameron_webhook_test_result.json") -Encoding UTF8
    Write-Host "Dry-run result saved to scripts/cameron_webhook_test_result.json"
} catch {
    Write-Error "Dry-run webhook failed: $($_.Exception.Message)"
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { }
    }
    exit 1
}

Write-Host "Done. cameron_sms1 added and dry-run executed."
