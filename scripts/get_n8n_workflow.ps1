Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$key = [regex]::Match($envText,'N8N_API_KEY_LT=(.+)')
if (-not $key.Success) { Write-Error "N8N_API_KEY_LT not found in .env"; exit 1 }
$apiKey = $key.Groups[1].Value.Trim()
if ($args.Count -lt 1) { Write-Host "Usage: pwsh scripts/get_n8n_workflow.ps1 <workflowId>"; exit 1 }
$workflowId = $args[0]
$url = "https://automations.livetransparent.com/api/v1/workflows/$workflowId"
try {
    $resp = Invoke-RestMethod -Uri $url -Method Get -Headers @{ 'X-N8N-API-KEY' = $apiKey } -ErrorAction Stop
    $out = $resp | ConvertTo-Json -Depth 10
    $out | Out-File -FilePath (Join-Path $scriptDir "workflow_$workflowId.json") -Encoding UTF8
    Write-Host "Workflow written to scripts/workflow_$workflowId.json"
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    if ($_.Exception.Response -ne $null) {
        try { $stream = $_.Exception.Response.GetResponseStream(); $reader = New-Object System.IO.StreamReader($stream); $text = $reader.ReadToEnd(); Write-Host $text } catch { Write-Host $_.Exception.Message }
    } else { Write-Host $_.Exception.Message }
    exit 2
}
