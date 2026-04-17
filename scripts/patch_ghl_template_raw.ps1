Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pit = [regex]::Match($envText,'GHL_PIT=(.+)').Groups[1].Value.Trim()
if ($args.Count -lt 1) { Write-Host "Usage: pwsh scripts/patch_ghl_template_raw.ps1 <templateId>"; exit 1 }
$templateId = $args[0]
$locationId = 'Zwz4relUXVPxx8uohnjV'
$folderId = '69e0c9069af5986541802d88'
$html = Get-Content -Raw (Join-Path $scriptDir "..\email-templates\John Follow Up Emails\John1.html")
$body = @{ name='John1'; type='html'; html=$html; folderId=$folderId; published=$true; editorType='html' } | ConvertTo-Json -Depth 20
$uri = "https://services.leadconnectorhq.com/emails/public/v2/locations/$locationId/templates/$templateId"
Write-Host "PATCH -> $uri"
try {
    $resp = Invoke-WebRequest -Uri $uri -Method Patch -Headers @{ Authorization = "Bearer $pit"; Version='2021-07-28' } -Body $body -ContentType 'application/json' -UseBasicParsing -ErrorAction Stop
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host $resp.Content
} catch {
    Write-Host "Request failed with status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    try { $c = $_.Exception.Response.GetResponseStream(); $reader = New-Object System.IO.StreamReader($c); $text = $reader.ReadToEnd(); Write-Host $text } catch { Write-Host $_.Exception.Message }
}
