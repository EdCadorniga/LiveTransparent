Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pit = [regex]::Match($envText,'GHL_PIT=(.+)').Groups[1].Value.Trim()
if ($args.Count -lt 1) { Write-Host "Usage: pwsh scripts/get_template.ps1 <templateId>"; exit 1 }
$templateId = $args[0]
$locationId = 'Zwz4relUXVPxx8uohnjV'
$uri = "https://services.leadconnectorhq.com/emails/public/v2/locations/$locationId/templates/$templateId"
try {
    $resp = Invoke-WebRequest -Uri $uri -Method Get -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28' } -UseBasicParsing -ErrorAction Stop
    $content = $resp.Content
    $content | Out-File (Join-Path $scriptDir "template_fetch_raw.json") -Encoding UTF8
    Write-Host "Template fetched to scripts/template_fetch_raw.json"
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    try { $r = $_.Exception.Response; $s = $r.GetResponseStream(); $reader = New-Object System.IO.StreamReader($s); $text = $reader.ReadToEnd(); Write-Host $text } catch { Write-Host $_.Exception.Message }
}
