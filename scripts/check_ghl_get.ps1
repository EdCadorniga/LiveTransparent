Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$envPath = Join-Path $scriptDir "..\.env" | Resolve-Path -ErrorAction Stop
$envText = Get-Content $envPath -Raw
$pitMatch = [regex]::Match($envText, 'GHL_PIT=(.+)')
if (-not $pitMatch.Success) { Write-Error "GHL_PIT not found in .env"; exit 1 }
$pit = $pitMatch.Groups[1].Value.Trim()
Write-Host "Using PIT: $($pit)"
$uri = 'https://services.leadconnectorhq.com/locations/Zwz4relUXVPxx8uohnjV/templates?type=email&limit=1'
try {
    $resp = Invoke-RestMethod -Uri $uri -Method Get -Headers @{ Authorization = "Bearer $pit"; Version = '2021-07-28'; Accept = 'application/json' } -ErrorAction Stop
    Write-Host "Success — response:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    try {
        $body = $_.Exception.Response.GetResponseStream() | ForEach-Object { [System.IO.StreamReader]::new($_).ReadToEnd() }
        Write-Host $body
    } catch {
        Write-Host $_.Exception.Message
    }
    exit 2
}
