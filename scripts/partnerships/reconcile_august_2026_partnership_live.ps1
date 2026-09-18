param([switch]$Apply)
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$dir = Join-Path $root 'Contacts added August 25 2026\Partnership contacts August 26 2026 1'
if (-not $env:GHL_PIT) { throw 'GHL_PIT is not set' }
$locationId = if ($env:GHL_LOCATION_ID) { $env:GHL_LOCATION_ID } else { 'Zwz4relUXVPxx8uohnjV' }
$base = 'https://services.leadconnectorhq.com'
$headers = @{ Authorization = "Bearer $env:GHL_PIT"; Version = '2021-07-28'; Accept = 'application/json'; 'Content-Type' = 'application/json' }
$linkedinFieldId = 'jE6P7IRuB6usZDFOMxrg'
$requiredTags = @('partner_candidate_email', 'partner_candidate_linkedin')
$vapiSelectorTags = @('vapi_campaign_brand', 'vapi_campaign_dispensary')

function T([object]$v) { if ($null -eq $v) { '' } else { $v.ToString().Trim().ToLowerInvariant() } }
function Request([string]$method, [string]$uri, [object]$body) {
    for ($attempt = 1; $attempt -le 6; $attempt++) {
        try {
            $args = @{ Method = $method; Uri = $uri; Headers = $headers }
            if ($null -ne $body) { $args.Body = ($body | ConvertTo-Json -Depth 20 -Compress) }
            return Invoke-RestMethod @args
        } catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -notin @(429, 502, 503, 504) -or $attempt -eq 6) { throw }
            Start-Sleep -Seconds ([Math]::Min(15, $attempt * 2))
        }
    }
}
function Tags($c) { @($c.tags | ForEach-Object { T $_ }) }
function ExactContact($email) {
    $uri = $base + '/contacts/?locationId=' + [uri]::EscapeDataString($locationId) + '&limit=20&query=' + [uri]::EscapeDataString($email)
    $result = Request 'GET' $uri $null
    @($result.contacts) | Where-Object {
        (T $_.email) -eq $email -or ((@($_.additionalEmails) | ForEach-Object { T $_ }) -contains $email)
    } | Select-Object -First 1
}
function HasLinkedIn($c) {
    @($c.customFields) | Where-Object { $_.id -eq $linkedinFieldId -and (T $_.value) } | Select-Object -First 1
}

$emailRows = @(Import-Csv (Join-Path $dir 'partner_candidate_email.csv'))
$linkedinRows = @(Import-Csv (Join-Path $dir 'partner_candidate_linkedin.csv'))
$linkedinByName = @{}
foreach ($r in $linkedinRows) {
    $key = (([string]$r.'First Name').Trim() + ' ' + ([string]$r.'Last Name').Trim()).Trim().ToLowerInvariant()
    $linkedinByName[$key] = $r
}

$rows = @()
foreach ($r in $emailRows) {
    $nameKey = (([string]$r.'First Name').Trim() + ' ' + ([string]$r.'Last Name').Trim()).Trim().ToLowerInvariant()
    $li = $linkedinByName[$nameKey]
    $rows += [pscustomobject]@{
        First = ([string]$r.'First Name').Trim()
        Last = ([string]$r.'Last Name').Trim()
        Email = T $r.Email
        Company = ([string]$r.'Company Name').Trim()
        Website = ([string]$r.Website).Trim()
        City = ([string]$r.City).Trim()
        State = ([string]$r.State).Trim()
        Country = ([string]$r.Country).Trim()
        LinkedIn = if ($li) { ([string]$li.'Person Linkedin Url').Trim() } else { '' }
    }
}

$duplicateEmails = @($rows | Group-Object Email | Where-Object { $_.Name -and $_.Count -gt 1 })
$duplicateEmailSet = @{}
foreach ($group in $duplicateEmails) { $duplicateEmailSet[$group.Name] = $true }

$created = 0; $existing = 0; $tagged = 0; $linkedInUpdated = 0; $vapiTagsRemoved = 0; $skippedDuplicates = 0; $errors = 0
$actions = @()
foreach ($r in $rows) {
    if ($duplicateEmailSet.ContainsKey($r.Email)) {
        $skippedDuplicates++
        $actions += [pscustomobject]@{ action = 'skip_shared_email'; email = $r.Email; name = "$($r.First) $($r.Last)" }
        continue
    }

    try { $contact = ExactContact $r.Email } catch {
        $errors++
        $actions += [pscustomobject]@{ action = 'error_lookup'; email = $r.Email; name = "$($r.First) $($r.Last)"; error = $_.Exception.Message }
        continue
    }

    if ($contact) {
        $existing++
        if ($Apply) {
            try {
                Request 'POST' ($base + '/contacts/' + $contact.id + '/tags') @{ tags = $requiredTags } | Out-Null
                $tagged++
                $removeVapi = @(Tags $contact | Where-Object { $_ -in $vapiSelectorTags })
                if ($removeVapi.Count -gt 0) {
                    Request 'DELETE' ($base + '/contacts/' + $contact.id + '/tags') @{ tags = $removeVapi } | Out-Null
                    $vapiTagsRemoved += $removeVapi.Count
                }
                if ($r.LinkedIn -and -not (HasLinkedIn $contact)) {
                    Request 'PUT' ($base + '/contacts/' + $contact.id) @{ customFields = @(@{ id = $linkedinFieldId; fieldValue = $r.LinkedIn }) } | Out-Null
                    $linkedInUpdated++
                }
                $actions += [pscustomobject]@{ action = 'tag_existing'; email = $r.Email; ghl_id = $contact.id; name = "$($r.First) $($r.Last)" }
            } catch {
                $errors++
                $actions += [pscustomobject]@{ action = 'error_update'; email = $r.Email; ghl_id = $contact.id; error = $_.Exception.Message }
            }
        } else {
            $actions += [pscustomobject]@{ action = 'would_tag_existing'; email = $r.Email; ghl_id = $contact.id; name = "$($r.First) $($r.Last)" }
        }
    } elseif ($Apply) {
        $body = @{
            locationId = $locationId
            firstName = $r.First
            lastName = $r.Last
            email = $r.Email
            companyName = $r.Company
            website = $r.Website
            city = $r.City
            state = $r.State
            country = $r.Country
            source = 'August 2026 Partnership Contacts'
            tags = $requiredTags
        }
        if ($r.LinkedIn) { $body.customFields = @(@{ id = $linkedinFieldId; fieldValue = $r.LinkedIn }) }
        try {
            $newContact = Request 'POST' ($base + '/contacts/') $body
            $created++
            $actions += [pscustomobject]@{ action = 'created'; email = $r.Email; ghl_id = $newContact.contact.id; name = "$($r.First) $($r.Last)" }
        } catch {
            $errors++
            $actions += [pscustomobject]@{ action = 'error_create'; email = $r.Email; name = "$($r.First) $($r.Last)"; error = $_.Exception.Message }
        }
    } else {
        $actions += [pscustomobject]@{ action = 'would_create'; email = $r.Email; name = "$($r.First) $($r.Last)" }
    }
    Start-Sleep -Milliseconds 150
}

if ($Apply) { $actions | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dir 'August_2026_Partnership_Action_Log.json') -Encoding UTF8 }
[ordered]@{
    Mode = if ($Apply) { 'APPLY' } else { 'DRY_RUN' }
    SourceRows = $rows.Count
    UniqueEmails = @($rows.Email | Where-Object { $_ } | Sort-Object -Unique).Count
    SharedEmailRowsSkipped = $skippedDuplicates
    SharedEmailGroups = $duplicateEmails.Count
    ExistingExactEmailContacts = $existing
    Created = $created
    TaggedExisting = $tagged
    LinkedInUrlsAdded = $linkedInUpdated
    VapiSelectorTagsRemoved = $vapiTagsRemoved
    Errors = $errors
    VapiTagsApplied = 0
} | ConvertTo-Json -Depth 5
