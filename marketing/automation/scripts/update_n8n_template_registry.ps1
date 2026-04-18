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
$backupDir = Join-Path $scriptDir "..\backups" | Resolve-Path -ErrorAction SilentlyContinue
if (-not $backupDir) { New-Item -Path (Join-Path $scriptDir "..\backups") -ItemType Directory | Out-Null; $backupDir = Join-Path $scriptDir "..\backups" }
$backupPath = Join-Path $backupDir "workflow_$workflowId`_$timestamp.json"
$wf | ConvertTo-Json -Depth 50 | Out-File -FilePath $backupPath -Encoding UTF8
Write-Host "Saved workflow backup to $backupPath"

# Locate the Config node in activeVersion.nodes (fallback to nodes)
$active = $wf.activeVersion ?? $wf
$nodes = $active.nodes

$configNode = $nodes | Where-Object { $_.name -eq 'Config' -or $_.id -eq 'config' } | Select-Object -First 1
if (-not $configNode) { Write-Error "Config node not found in workflow"; exit 1 }

Write-Host "Found Config node (id=$($configNode.id), name=$($configNode.name))"

# Find templateRegistryJson assignment
$assignments = $configNode.parameters.assignments.assignments
$templateEntry = $assignments | Where-Object { $_.name -eq 'templateRegistryJson' } | Select-Object -First 1
if (-not $templateEntry) { Write-Error "templateRegistryJson entry not found in Config node"; exit 1 }

$currentJsonStr = $templateEntry.value
if ([string]::IsNullOrWhiteSpace($currentJsonStr)) { $currentJson = @{} } else { try { $currentJson = $currentJsonStr | ConvertFrom-Json -ErrorAction Stop } catch { Write-Error "Failed parsing existing templateRegistryJson"; exit 1 } }

Write-Host "Merging new john_sms templates into templateRegistryJson"

$newEntries = @{
    john_sms1 = @{ name = 'John SMS 1 - Initial Outreach'; message = "Hi this is John, just gave you a call. Saw you were interested in learning about ads for regulated industries on social/search.\n\nWe run ads for Mood, Cookies, and more! Interested in learning how?" }
    john_sms2 = @{ name = 'John SMS 2 - Locked Out?'; message = "Hey {{contact.first_name}}! Are you locked out of ads, or just avoiding them because of the horror stories?\n\nI can show you how top regulated-industry brands are doing it in 10 mins." }
    john_sms3 = @{ name = 'John SMS 3 - Scale Year'; message = "Hi {{contact.first_name}} this could be the year you scale your brand on social/search! Interested in how we do it for Mood, Cookies, and more?" }
    john_sms4 = @{ name = 'John SMS 4 - Last Follow-up'; message = "Hi {{contact.first_name}}—last follow-up on ads for regulated industries. Is it timing, or is there a better contact?" }
    john_sms5 = @{ name = 'John SMS 5 - Engaged Follow-up'; message = "Good chatting about ads for regulated industries earlier—based on what you shared, this looks like a strong fit.\n\nWe’re onboarding a few brands this month—grab a time here: {{trigger_link.nqLFBlEsdm7qccr8Yyog}}" }
}

foreach ($k in $newEntries.Keys) {
    if ($currentJson.PSObject.Properties.Name -contains $k) {
        Write-Host "Overwriting existing key: $k" -ForegroundColor Yellow
    }
    $currentJson | Add-Member -NotePropertyName $k -NotePropertyValue $newEntries[$k] -Force
}

$newJsonStr = ($currentJson | ConvertTo-Json -Depth 50)

# Update the config node assignment value
$templateEntry.value = $newJsonStr

# Prepare updated workflow payload for PUT — use active.nodes and active.connections
$putPayload = @{
    name = $wf.name
    nodes = $active.nodes
    connections = $active.connections
    settings = @{}
}

$putBody = $putPayload | ConvertTo-Json -Depth 50

Write-Host "Patching workflow with updated templateRegistryJson..."
try {
    $putUrl = "https://automations.livetransparent.com/api/v1/workflows/$workflowId"
    $resp = Invoke-RestMethod -Uri $putUrl -Method Put -Headers @{ 'X-N8N-API-KEY' = $apiKey } -Body $putBody -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Workflow patched successfully." -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $scriptDir "workflow_patch_result.json") -Encoding UTF8
    Write-Host "Patch result saved to scripts/workflow_patch_result.json"
} catch {
    Write-Error "Failed to patch workflow: $($_.Exception.Message)"
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { }
    }
    Write-Host "Restoring from backup..."
    $backupContent = Get-Content $backupPath -Raw
    try {
        Invoke-RestMethod -Uri $putUrl -Method Put -Headers @{ 'X-N8N-API-KEY' = $apiKey } -Body $backupContent -ContentType 'application/json' -ErrorAction Stop
        Write-Host "Restored workflow from backup." -ForegroundColor Yellow
    } catch {
        Write-Error "Failed to restore workflow from backup: $($_.Exception.Message)"
    }
    exit 1
}

Write-Host "Now running a dry-run test webhook against the workflow endpoint"
$webhookUrl = 'https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms'
$headers = @{ 'x-lt-webhook-key' = 'Lt9Qv2Xm'; 'Content-Type' = 'application/json' }
$testBody = @{ contactId = 'test-1'; contactPhone = '15555551212'; templateKey = 'john_sms1'; contact = @{ first_name = 'Test'; last_name = 'User'; email = 'test@example.com' }; dryRun = $true } | ConvertTo-Json -Depth 10
try {
    $testResp = Invoke-RestMethod -Uri $webhookUrl -Method Post -Headers $headers -Body $testBody -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Dry-run webhook response:" -ForegroundColor Green
    $testResp | ConvertTo-Json -Depth 10 | Write-Host
    $testResp | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $scriptDir "webhook_test_result.json") -Encoding UTF8
    Write-Host "Dry-run result saved to scripts/webhook_test_result.json"
} catch {
    Write-Error "Dry-run webhook failed: $($_.Exception.Message)"
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { }
    }
    exit 1
}

Write-Host "Done. Template registry updated and test webhook executed."
