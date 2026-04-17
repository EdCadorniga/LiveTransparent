Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pitMatch = [regex]::Match($envText,'GHL_PIT=(.+)')
if (-not $pitMatch.Success) { Write-Error "GHL_PIT not found in .env"; exit 1 }
$pit = $pitMatch.Groups[1].Value.Trim()
if ($args.Count -lt 1) { Write-Host "Usage: pwsh scripts/get_ghl_workflow.ps1 <workflowId>"; exit 1 }
$workflowId = $args[0]
$locationId = 'Zwz4relUXVPxx8uohnjV'
 $listUrl = 'https://services.leadconnectorhq.com/workflows?locationId=' + $locationId
Write-Host "Listing workflows for location $locationId"
try {
    $listResp = Invoke-RestMethod -Uri $listUrl -Method Get -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -ErrorAction Stop
    $listPath = Join-Path $scriptDir "..\backups\ghl_workflows_list_$locationId.json"
    $listResp | ConvertTo-Json -Depth 50 | Out-File -FilePath $listPath -Encoding UTF8
    Write-Host "Saved workflows list to $listPath"
} catch {
    Write-Error "Failed to list workflows: $($_.Exception.Message)"
}

$url = 'https://services.leadconnectorhq.com/workflows/' + $workflowId + '?locationId=' + $locationId
Write-Host "Fetching GHL workflow $workflowId"
try {
    $resp = Invoke-RestMethod -Uri $url -Method Get -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -ErrorAction Stop
    $outPath = Join-Path $scriptDir "..\backups\ghl_workflow_$workflowId.json"
    $resp | ConvertTo-Json -Depth 50 | Out-File -FilePath $outPath -Encoding UTF8
    Write-Host "Saved GHL workflow to $outPath"
} catch {
    Write-Error "Failed to fetch GHL workflow: $($_.Exception.Message)"
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { }
    }
    exit 1
}
