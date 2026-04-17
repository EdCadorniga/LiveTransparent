Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pitMatch = [regex]::Match($envText, 'GHL_PIT=(.+)')
if (-not $pitMatch.Success) { Write-Error "GHL_PIT not found in .env"; exit 1 }
$pit = $pitMatch.Groups[1].Value.Trim()

if ($args.Count -lt 1) { Write-Host "Usage: pwsh scripts/patch_ghl_template.ps1 <templateId>"; exit 1 }
$templateId = $args[0]

$locationId = 'Zwz4relUXVPxx8uohnjV'
$folderId = '69e0c9069af5986541802d88'
$htmlPath = Join-Path $scriptDir "..\email-templates\John Follow Up Emails\John1.html" | Resolve-Path -ErrorAction Stop
$html = Get-Content $htmlPath -Raw -Encoding UTF8

$bodyObj = @{ name = "John1"; type = 'html'; html = $html; folderId = $folderId; published = $true; editorType = 'builder' }
$body = $bodyObj | ConvertTo-Json -Depth 20

$uri = "https://services.leadconnectorhq.com/emails/public/v2/locations/$locationId/templates/$templateId"
Write-Host "PATCHing template $templateId at $uri"
try {
    $resp = Invoke-RestMethod -Uri $uri -Method Patch -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -Body $body -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Updated template: $($resp.id)" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10 | Out-File (Join-Path $scriptDir "patch_result.json") -Encoding UTF8
    Write-Host "Result saved to scripts/patch_result.json"
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { Write-Host $_.Exception.Message }
    } else { Write-Host $_.Exception.Message }
    exit 2
}
