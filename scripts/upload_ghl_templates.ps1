<#
Uploads HTML email templates in email-templates/John Follow Up Emails/ to GoHighLevel
Uses GHL_PIT from the repo .env file.

Run: pwsh -File scripts/upload_ghl_templates.ps1
#>

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $root "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -ErrorAction Stop | Out-String

$pitMatch = [regex]::Match($envText, 'GHL_PIT=(.+)')
if (-not $pitMatch.Success) {
    Write-Error "GHL_PIT not found in .env"
    exit 1
}
$pit = $pitMatch.Groups[1].Value.Trim()

$locationId = 'Zwz4relUXVPxx8uohnjV'
$folderId = '69e0c9069af5986541802d88'
$sourceDir = Join-Path $root "..\email-templates\John Follow Up Emails" | Resolve-Path -ErrorAction Stop

Write-Host "Using PIT: $($pit.Substring(0,10))..." -ForegroundColor Cyan
Write-Host "Uploading templates from: $sourceDir"

function Post-Template($filePath) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($filePath)
    Write-Host "Uploading template: $name"
    $html = Get-Content $filePath -Raw -Encoding UTF8

    $body = @{ 
        name = $name
        html = $html
        folderId = $folderId
        type = 'email'
        published = $true
    } | ConvertTo-Json -Depth 10

    $uri = "https://services.leadconnectorhq.com/locations/$locationId/templates"

    try {
        $resp = Invoke-RestMethod -Uri $uri -Method Post -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -Body $body -ContentType 'application/json' -ErrorAction Stop
        Write-Host "Created: $($resp.id) - $name" -ForegroundColor Green
        return @{ success = $true; name = $name; response = $resp }
    } catch {
        Write-Error "Failed to upload $name : $_"
        return @{ success = $false; name = $name; error = $_ }
    }
}

$results = @()
Get-ChildItem -Path $sourceDir -Filter *.html | ForEach-Object {
    $results += Post-Template $_.FullName
    Start-Sleep -Milliseconds 300
}

Write-Host "Upload finished. Summary:" -ForegroundColor Cyan
$results | ForEach-Object {
    if ($_.success) { Write-Host "OK: $($_.name) -> id=$($_.response.id)" -ForegroundColor Green } else { Write-Host "ERR: $($_.name) -> $($_.error)" -ForegroundColor Red }
}

$jsonOut = $results | ConvertTo-Json -Depth 10
$outPath = Join-Path $root "..\scripts\upload_results.json"
$jsonOut | Out-File -FilePath $outPath -Encoding UTF8
Write-Host "Results written to $outPath"
