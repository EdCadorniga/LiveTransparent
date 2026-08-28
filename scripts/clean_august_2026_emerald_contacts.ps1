$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$inputDir = Join-Path $root 'Contacts added August 25 2026'
$outputDir = Join-Path $inputDir 'cleaned'
if (-not (Test-Path -LiteralPath $inputDir)) { throw "Input directory not found: $inputDir" }
if (-not (Test-Path -LiteralPath $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }

function Normalize-Text([object]$Value) {
    if ($null -eq $Value) { return '' }
    return $Value.ToString().Trim().ToLowerInvariant()
}

function Normalize-Phone([object]$Value) {
    if ($null -eq $Value) { return '' }
    $digits = ($Value.ToString() -replace '\D', '')
    if ($digits.Length -eq 10) { $digits = '1' + $digits }
    if ($digits.Length -lt 10) { return '' }
    if ($digits.Length -eq 11 -and $digits.StartsWith('1')) { return '+' + $digits }
    if ($digits.Length -gt 15) { return '' }
    if ($digits.Length -gt 11) { return '+' + $digits }
    return ''
}

function First-DelimitedValue([object]$Value, [scriptblock]$Normalizer) {
    if ($null -eq $Value) { return '' }
    foreach ($part in ($Value.ToString() -split '[,|]')) {
        $normalized = & $Normalizer $part
        if ($normalized) { return $normalized }
    }
    return ''
}

function Invoke-GhlPage([string]$Uri) {
    $headers = @{
        Authorization = "Bearer $env:GHL_PIT"
        Version = '2021-07-28'
        Accept = 'application/json'
        'Content-Type' = 'application/json'
    }
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try { return Invoke-RestMethod -Method Get -Uri $Uri -Headers $headers }
        catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -ne 429 -or $attempt -eq 5) { throw }
            Start-Sleep -Seconds ($attempt * 2)
        }
    }
}

if (-not $env:GHL_PIT) { throw 'GHL_PIT is not set' }
$locationId = if ($env:GHL_LOCATION_ID) { $env:GHL_LOCATION_ID } else { 'Zwz4relUXVPxx8uohnjV' }
$baseUri = 'https://services.leadconnectorhq.com/contacts/'
$existing = [System.Collections.Generic.List[object]]::new()
$seenCursors = [System.Collections.Generic.HashSet[string]]::new()
$startAfter = $null
$startAfterId = $null

while ($true) {
    $query = "locationId=$([uri]::EscapeDataString($locationId))&limit=100"
    if ($null -ne $startAfter) { $query += "&startAfter=$startAfter&startAfterId=$([uri]::EscapeDataString($startAfterId))" }
    $response = Invoke-GhlPage ($baseUri + '?' + $query)
    $page = @($response.contacts)
    if ($page.Count -eq 0) { break }
    foreach ($contact in $page) { $existing.Add($contact) }
    if ($page.Count -lt 100) { break }
    $cursor = @($page[-1].startAfter)
    if ($cursor.Count -lt 2) { throw 'GHL response did not provide a pagination cursor' }
    $cursorKey = "$($cursor[0])|$($cursor[1])"
    if (-not $seenCursors.Add($cursorKey)) { throw "Repeated GHL pagination cursor: $cursorKey" }
    $startAfter = $cursor[0]
    $startAfterId = $cursor[1]
}

$existingEmails = [System.Collections.Generic.HashSet[string]]::new()
$existingPhones = [System.Collections.Generic.HashSet[string]]::new()
$existingEmeraldIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($contact in $existing) {
    $email = Normalize-Text $contact.email
    if ($email) { [void]$existingEmails.Add($email) }
    foreach ($additional in @($contact.additionalEmails)) {
        $additionalEmail = Normalize-Text $additional
        if ($additionalEmail) { [void]$existingEmails.Add($additionalEmail) }
    }
    $phone = Normalize-Phone $contact.phone
    if ($phone) { [void]$existingPhones.Add($phone) }
    foreach ($field in @($contact.customFields)) {
        $fieldValue = Normalize-Text $field.value
        if ($field.id -eq 'R0wbDRyzZz34PMlQSRWN' -and $fieldValue) { [void]$existingEmeraldIds.Add($fieldValue) }
    }
}

$fileRules = @(
    @{ File = 'Brand.csv'; Category = 'Brand'; Tag = 'brands_pool'; Rank = 1 },
    @{ File = 'Agency.csv'; Category = 'Agency'; Tag = 'agency_pool'; Rank = 2 },
    @{ File = 'Dispensaries (1).csv'; Category = 'Dispensaries'; Tag = 'dispensaries_pool'; Rank = 3 }
)
$sourceRows = [System.Collections.Generic.List[object]]::new()
$rowNumber = 0
foreach ($rule in $fileRules) {
    foreach ($row in (Import-Csv -LiteralPath (Join-Path $inputDir $rule.File))) {
        $rowNumber++
        $primaryEmail = Normalize-Text $row.'Primary Email'
        $email = if ($primaryEmail) { $primaryEmail } else { First-DelimitedValue $row.'All Known Emails' ${function:Normalize-Text} }
        $primaryPhone = Normalize-Phone $row.'Primary Phone'
        $phone = if ($primaryPhone) { $primaryPhone } else { First-DelimitedValue $row.'All Known Phones' ${function:Normalize-Phone} }
        $sourceRows.Add([pscustomobject]@{
            RowNumber = $rowNumber
            SourceFile = $rule.File
            Category = $rule.Category
            PoolTag = $rule.Tag
            Rank = $rule.Rank
            EmeraldContactId = Normalize-Text $row.'Emerald Contact ID'
            FirstName = $row.'First Name'
            LastName = $row.'Last Name'
            Email = $email
            Phone = $phone
            City = $row.'Contact City'
            State = $row.'Contact State'
            CompanyName = $row.'Company Name(s)'
            Website = $row.'Company Primary Website'
            Title = $row.Titles
            Roles = $row.Roles
            Seniorities = $row.Seniorities
            AllKnownEmails = $row.'All Known Emails'
            AllKnownPhones = $row.'All Known Phones'
            LinkedIn = $row.'Contact LinkedIn URL(s)'
            LocationNames = $row.'Location Display Name(s)'
            EmeraldLocationIds = $row.'Emerald Location id(s)'
        })
    }
}

$exclusions = [System.Collections.Generic.List[object]]::new()
function Add-Exclusion($row, [string]$reason) {
    $exclusions.Add([pscustomobject]@{
        SourceFile = $row.SourceFile
        SourceRow = $row.RowNumber
        EmeraldContactId = $row.EmeraldContactId
        FirstName = $row.FirstName
        LastName = $row.LastName
        Email = $row.Email
        Phone = $row.Phone
        CompanyName = $row.CompanyName
        Reason = $reason
    })
}

# First winner per Emerald ID, email, or phone, with Brand > Agency > Dispensaries precedence.
$winners = [System.Collections.Generic.List[object]]::new()
$claimedIds = [System.Collections.Generic.HashSet[string]]::new()
$claimedEmails = [System.Collections.Generic.HashSet[string]]::new()
$claimedPhones = [System.Collections.Generic.HashSet[string]]::new()
$ordered = $sourceRows | Sort-Object Rank, RowNumber
foreach ($row in $ordered) {
    if (-not $row.Email -and -not $row.Phone) { Add-Exclusion $row 'missing_email_and_phone'; continue }
    if ($row.EmeraldContactId -and $existingEmeraldIds.Contains($row.EmeraldContactId)) { Add-Exclusion $row 'existing_emerald_contact_id'; continue }
    if ($row.Email -and $existingEmails.Contains($row.Email)) { Add-Exclusion $row 'existing_email'; continue }
    if ($row.Phone -and $existingPhones.Contains($row.Phone)) { Add-Exclusion $row 'existing_phone'; continue }
    if ($row.EmeraldContactId -and $claimedIds.Contains($row.EmeraldContactId)) { Add-Exclusion $row 'duplicate_source_emerald_contact_id'; continue }
    if ($row.Email -and $claimedEmails.Contains($row.Email)) { Add-Exclusion $row 'duplicate_source_email'; continue }
    if ($row.Phone -and $claimedPhones.Contains($row.Phone)) { Add-Exclusion $row 'duplicate_source_phone'; continue }
    if ($row.EmeraldContactId) { [void]$claimedIds.Add($row.EmeraldContactId) }
    if ($row.Email) { [void]$claimedEmails.Add($row.Email) }
    if ($row.Phone) { [void]$claimedPhones.Add($row.Phone) }
    $winners.Add($row)
}

$outputColumns = @('First Name','Last Name','Email','Phone','City','State','Company Name','Website','Tags','Em_Emerald_Contact_ID','Em_Source_File','Em_All_Known_Emails','Em_All_Known_Phones','Em_Contact_LinkedIn_URLs','Em_Roles','Em_Seniorities','Em_Location_Display_Names','Em_Emerald_Location_IDs','Title')
foreach ($rule in $fileRules) {
    $path = Join-Path $outputDir ("August_2026_Emerald_{0}_GHL_Import.csv" -f $rule.Category)
    $rows = foreach ($row in ($winners | Where-Object Category -eq $rule.Category)) {
        [pscustomobject][ordered]@{
            'First Name' = $row.FirstName
            'Last Name' = $row.LastName
            Email = $row.Email
            Phone = $row.Phone
            City = $row.City
            State = $row.State
            'Company Name' = $row.CompanyName
            Website = $row.Website
            Tags = "$($row.PoolTag),emerald,august_2026_emerald_contact"
            Em_Emerald_Contact_ID = $row.EmeraldContactId
            Em_Source_File = $row.SourceFile
            Em_All_Known_Emails = $row.AllKnownEmails
            Em_All_Known_Phones = $row.AllKnownPhones
            Em_Contact_LinkedIn_URLs = $row.LinkedIn
            Em_Roles = $row.Roles
            Em_Seniorities = $row.Seniorities
            Em_Location_Display_Names = $row.LocationNames
            Em_Emerald_Location_IDs = $row.EmeraldLocationIds
            Title = $row.Title
        }
    }
    $rows | Export-Csv -LiteralPath $path -NoTypeInformation -Encoding UTF8
}

$exclusions | Export-Csv -LiteralPath (Join-Path $outputDir 'August_2026_Emerald_Exclusions.csv') -NoTypeInformation -Encoding UTF8
[pscustomobject]@{
    GhlContactsFetched = $existing.Count
    SourceRows = $sourceRows.Count
    CleanRows = $winners.Count
    ExcludedRows = $exclusions.Count
    CleanBrand = @($winners | Where-Object Category -eq 'Brand').Count
    CleanAgency = @($winners | Where-Object Category -eq 'Agency').Count
    CleanDispensaries = @($winners | Where-Object Category -eq 'Dispensaries').Count
    OutputDirectory = $outputDir
} | ConvertTo-Json
