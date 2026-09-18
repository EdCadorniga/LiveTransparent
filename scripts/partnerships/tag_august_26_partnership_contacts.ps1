param([switch]$Apply)
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$tag = 'august_26_partnership_contact'
$source = 'August 2026 Partnership Contacts'
$locationId = if ($env:GHL_LOCATION_ID) { $env:GHL_LOCATION_ID } else { 'Zwz4relUXVPxx8uohnjV' }
$base = 'https://services.leadconnectorhq.com'
if (-not $env:GHL_PIT) { throw 'GHL_PIT is not set' }
$headers = @{ Authorization = "Bearer $env:GHL_PIT"; Version = '2021-07-28'; Accept = 'application/json'; 'Content-Type' = 'application/json' }

function Request([string]$method, [string]$uri, [object]$body) {
    for ($attempt = 1; $attempt -le 6; $attempt++) {
        try {
            $args = @{ Method = $method; Uri = $uri; Headers = $headers }
            if ($null -ne $body) { $args.Body = ($body | ConvertTo-Json -Compress) }
            return Invoke-RestMethod @args
        }
        catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -notin @(429, 502, 503, 504) -or $attempt -eq 6) { throw }
            Start-Sleep -Seconds ([Math]::Min(15, $attempt * 2))
        }
    }
}

$contacts = @()
$startAfter = $null
$startAfterId = ''
do {
    $uri = $base + '/contacts/?locationId=' + [uri]::EscapeDataString($locationId) + '&query=partner_candidate_email&limit=100'
    if ($null -ne $startAfter) { $uri += '&startAfter=' + [uri]::EscapeDataString($startAfter) + '&startAfterId=' + [uri]::EscapeDataString($startAfterId) }
    $page = Request 'GET' $uri $null
    $contacts += @($page.contacts | Where-Object { $_.source -eq $source })
    $cursor = @($page.contacts)[-1].startAfter
    if (@($page.contacts).Count -lt 100 -or $cursor.Count -lt 2) { break }
    $startAfter = $cursor[0]
    $startAfterId = $cursor[1]
    Start-Sleep -Milliseconds 250
} while ($true)
$created = @($contacts | Sort-Object id -Unique)
$alreadyTagged = @($created | Where-Object { @($_.tags) -contains $tag }).Count
$updated = 0
$errors = 0
foreach ($row in $created) {
    if ($Apply) {
        try { Request 'POST' ($base + '/contacts/' + $row.id + '/tags') @{ tags = @($tag) } | Out-Null; $updated++ }
        catch { $errors++ }
        Start-Sleep -Milliseconds 150
    }
}
[ordered]@{
    Mode = if ($Apply) { 'APPLY' } else { 'DRY_RUN' }
    NewContacts = $created.Count
    Tag = $tag
    AlreadyTagged = $alreadyTagged
    MissingTag = $created.Count - $alreadyTagged
    Updated = $updated
    Errors = $errors
} | ConvertTo-Json
