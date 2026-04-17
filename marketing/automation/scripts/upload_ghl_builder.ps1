Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pitMatch = [regex]::Match($envText, 'GHL_PIT=(.+)')
if (-not $pitMatch.Success) { Write-Error "GHL_PIT not found in .env"; exit 1 }
$pit = $pitMatch.Groups[1].Value.Trim()

Write-Host "Using PIT: $($pit.Substring(0,10))..."

$locationId = 'Zwz4relUXVPxx8uohnjV'
$folderId = '69e0c9069af5986541802d88'
$sourceDir = Join-Path $scriptDir "..\email-templates\John Follow Up Emails" | Resolve-Path -ErrorAction Stop

function Post-BuilderTemplate($filePath) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($filePath)
    Write-Host "Uploading builder template: $name"
    $html = Get-Content $filePath -Raw -Encoding UTF8

    $bodyObj = @{ name = $name; type = 'html'; html = $html; folderId = $folderId; published = $true }
    $body = $bodyObj | ConvertTo-Json -Depth 10

 $uri = "https://services.leadconnectorhq.com/emails/public/v2/locations/$locationId/templates"

    try {
        $resp = Invoke-RestMethod -Uri $uri -Method Post -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -Body $body -ContentType 'application/json' -ErrorAction Stop
        Write-Host "Created: $($resp.id) - $name" -ForegroundColor Green
        return @{ success = $true; name = $name; response = $resp }
    } catch {
        Write-Host "Failed to upload $name :" -ForegroundColor Red
        Write-Host ($_.Exception.Message)
        if ($_.Exception.Response -ne $null) {
            try {
                $text = $_.Exception.Response.Content.ReadAsStringAsync().Result
                Write-Host $text
            } catch { Write-Host "(no response body)" }
        }
        return @{ success = $false; name = $name; error = $_ }
    }
}

$results = @()
Get-ChildItem -Path $sourceDir -Filter *.html | ForEach-Object {
    $results += Post-BuilderTemplate $_.FullName
    Start-Sleep -Milliseconds 300
}

Write-Host "Upload finished. Summary:" -ForegroundColor Cyan
$results | ForEach-Object {
    if ($_.success) { Write-Host "OK: $($_.name) -> id=$($_.response.id)" -ForegroundColor Green } else { Write-Host "ERR: $($_.name) -> $($_.error)" -ForegroundColor Red }
}

$results | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $scriptDir "upload_builder_results.json") -Encoding UTF8
Write-Host "Results written to: $(Join-Path $scriptDir 'upload_builder_results.json')"
