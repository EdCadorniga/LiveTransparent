param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$inputDir = Join-Path $root 'Contacts added August 25 2026'
$outputDir = Join-Path $inputDir 'cleaned'
if (-not (Test-Path -LiteralPath $inputDir)) { throw "Input directory not found: $inputDir" }
if (-not $env:GHL_PIT) { throw 'GHL_PIT is not set' }
$locationId = if ($env:GHL_LOCATION_ID) { $env:GHL_LOCATION_ID } else { 'Zwz4relUXVPxx8uohnjV' }
$base = 'https://services.leadconnectorhq.com'

function T([object]$v) { if ($null -eq $v) { '' } else { $v.ToString().Trim().ToLowerInvariant() } }
function P([object]$v) {
    if ($null -eq $v) { return '' }
    $d = $v.ToString() -replace '\D',''
    if ($d.Length -eq 10) { $d = '1' + $d }
    if ($d.Length -eq 11 -and $d.StartsWith('1')) { return '+' + $d }
    if ($d.Length -gt 11 -and $d.Length -le 15) { return '+' + $d }
    ''
}
function First([object]$v, [scriptblock]$fn) {
    if ($null -eq $v) { return '' }
    foreach ($part in ($v.ToString() -split '[,|]')) { $x = & $fn $part; if ($x) { return $x } }
    ''
}
function Request([string]$method, [string]$uri, [object]$body) {
    $headers = @{ Authorization = "Bearer $env:GHL_PIT"; Version = '2021-07-28'; Accept = 'application/json'; 'Content-Type' = 'application/json' }
    for ($attempt=1; $attempt -le 5; $attempt++) {
        try {
            $args = @{ Method=$method; Uri=$uri; Headers=$headers }
            if ($null -ne $body) { $args.Body = ($body | ConvertTo-Json -Depth 20 -Compress) }
            return Invoke-RestMethod @args
        } catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -ne 429 -or $attempt -eq 5) { throw }
            Start-Sleep -Seconds ($attempt * 2)
        }
    }
}
function FetchContacts {
    $all = [System.Collections.Generic.List[object]]::new(); $after=$null; $afterId=$null; $seen=[System.Collections.Generic.HashSet[string]]::new()
    while ($true) {
        $q = "locationId=$([uri]::EscapeDataString($locationId))&limit=100"
        if ($null -ne $after) { $q += "&startAfter=$after&startAfterId=$([uri]::EscapeDataString($afterId))" }
        $r = Request 'GET' ($base + '/contacts/?' + $q) $null; $page=@($r.contacts); if (!$page.Count) { break }
        foreach($c in $page){$all.Add($c)}; if($page.Count -lt 100){break}
        $cur=@($page[-1].startAfter); if($cur.Count -lt 2){throw 'Missing GHL cursor'}; $key="$($cur[0])|$($cur[1])"; if(!$seen.Add($key)){throw 'Repeated GHL cursor'}; $after=$cur[0];$afterId=$cur[1]
    }
    $all
}

$existing = @(FetchContacts)
$emails=[Collections.Generic.HashSet[string]]::new();$phones=[Collections.Generic.HashSet[string]]::new();$ids=[Collections.Generic.HashSet[string]]::new();$byId=@{};$byEmail=@{}
foreach($c in $existing){
    $e=T $c.email;if($e){[void]$emails.Add($e);$byEmail[$e]=$c};foreach($a in @($c.additionalEmails)){$x=T $a;if($x){[void]$emails.Add($x);$byEmail[$x]=$c}}
    $p=P $c.phone;if($p){[void]$phones.Add($p)}
    foreach($f in @($c.customFields)){if($f.id -eq 'R0wbDRyzZz34PMlQSRWN' -and (T $f.value)){$id=T $f.value;[void]$ids.Add($id);$byId[$id]=$c}}
}
$blocked = @('do not contact','do not nurture','unsubscribed','opted out','partner_do_not_contact','simpletext_stop','seq enrolled - emerald','seq emerald -','emerald campaign completed')
function IsBlocked($c) { $tags=@($c.tags|ForEach-Object{T $_}); foreach($b in $blocked){if($b.EndsWith('-')){if(@($tags|Where-Object{$_ -like "$b*"}).Count){return $true}}elseif($tags -contains $b){return $true}}; $false }

$rules=@(@{File='Brand.csv';Category='Brand';Pool='brands_pool';Rank=1;Queue='Enrollment Queue - Emerald - Executives MSO'},@{File='Agency.csv';Category='Agency';Pool='agency_pool';Rank=2;Queue='Enrollment Queue - Emerald - Executives MSO'},@{File='Dispensaries (1).csv';Category='Dispensaries';Pool='dispensaries_pool';Rank=3;Queue='Enrollment Queue - DAN - Dispensaries'})
$rows=[Collections.Generic.List[object]]::new();$n=0
foreach($rule in $rules){foreach($r in (Import-Csv (Join-Path $inputDir $rule.File))){$n++;$e=T $r.'Primary Email';if(!$e){$e=First $r.'All Known Emails' ${function:T}};$p=P $r.'Primary Phone';if(!$p){$p=First $r.'All Known Phones' ${function:P}};$rows.Add([pscustomobject]@{Row=$n;Rank=$rule.Rank;Category=$rule.Category;Pool=$rule.Pool;Queue=$rule.Queue;Id=T $r.'Emerald Contact ID';First=$r.'First Name';Last=$r.'Last Name';Email=$e;Phone=$p;Company=$r.'Company Name(s)';Website=$r.'Company Primary Website';City=$r.'Contact City';State=$r.'Contact State';Title=$r.Titles;Source=$rule.File})}}

$claimedId=[Collections.Generic.HashSet[string]]::new();$claimedEmail=[Collections.Generic.HashSet[string]]::new();$claimedPhone=[Collections.Generic.HashSet[string]]::new();$clean=[Collections.Generic.List[object]]::new();$phoneNew=[Collections.Generic.List[object]]::new();$skips=[Collections.Generic.List[object]]::new()
foreach($r in ($rows|Sort-Object Rank,Row)){
    if(!$r.Email -and !$r.Phone){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='missing_email_and_phone';Category=$r.Category});continue}
    if(!$r.Email){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='missing_email_for_email_campaign';Category=$r.Category});continue}
    if($r.Id -and $ids.Contains($r.Id)){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='existing_emerald_id';Category=$r.Category});continue}
    if($r.Email -and $emails.Contains($r.Email)){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='existing_email';Category=$r.Category});continue}
    if($r.Id -and $claimedId.Contains($r.Id)){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='duplicate_source_id';Category=$r.Category});continue}
    if($r.Email -and $claimedEmail.Contains($r.Email)){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='duplicate_source_email';Category=$r.Category});continue}
    if($r.Phone -and $claimedPhone.Contains($r.Phone)){$skips.Add([pscustomobject]@{Id=$r.Id;Email=$r.Email;Reason='duplicate_source_phone';Category=$r.Category});continue}
    if($r.Id){[void]$claimedId.Add($r.Id)};if($r.Email){[void]$claimedEmail.Add($r.Email)};if($r.Phone){[void]$claimedPhone.Add($r.Phone)}
    if($r.Phone -and $phones.Contains($r.Phone)){$phoneNew.Add($r)}else{$clean.Add($r)}
}

$actions=[Collections.Generic.List[object]]::new();$pending=0;$suppressed=0;$notImported=0;$missingClean=[Collections.Generic.List[object]]::new()
foreach($r in $clean){$c=$null;if($r.Id -and $byId.ContainsKey($r.Id)){$c=$byId[$r.Id]}elseif($r.Email -and $byEmail.ContainsKey($r.Email)){$c=$byEmail[$r.Email]};if($null -eq $c){$notImported++;$missingClean.Add($r);continue};if(IsBlocked $c){$suppressed++;continue};$tags=@($c.tags|ForEach-Object{T $_});$poolTag=T $r.Pool;if($tags -notcontains $poolTag){$actions.Add([pscustomobject]@{Action='add_pool_tag';ContactId=$c.id;Email=$c.email;SourceEmail=$r.Email;PoolTag=$r.Pool;Category=$r.Category})};if($tags -notcontains (T $r.Queue)){$actions.Add([pscustomobject]@{Action='add_queue_tag';ContactId=$c.id;Email=$c.email;SourceEmail=$r.Email;QueueTag=$r.Queue;Category=$r.Category})}}
$created=0;$duplicateRejected=0;$createErrors=0
foreach($r in $phoneNew){$actions.Add([pscustomobject]@{Action='create_email_only';ContactId='';Email=$r.Email;SourceEmail=$r.Email;QueueTag=$r.Queue;Category=$r.Category;First=$r.First;Last=$r.Last;Company=$r.Company;Website=$r.Website;City=$r.City;State=$r.State;Id=$r.Id})}
foreach($r in $missingClean){$actions.Add([pscustomobject]@{Action='create_missing';ContactId='';Email=$r.Email;SourceEmail=$r.Email;QueueTag=$r.Queue;PoolTag=$r.Pool;Category=$r.Category;First=$r.First;Last=$r.Last;Phone=$r.Phone;Company=$r.Company;Website=$r.Website;City=$r.City;State=$r.State;Id=$r.Id})}

$actions | Export-Csv (Join-Path $outputDir 'August_2026_Emerald_Enrollment_Actions.csv') -NoTypeInformation -Encoding UTF8
$skips | Export-Csv (Join-Path $outputDir 'August_2026_Emerald_Enrollment_Skips.csv') -NoTypeInformation -Encoding UTF8
$summary=[ordered]@{Mode=if($Apply){'APPLY'}else{'DRY_RUN'};GhlContacts=$existing.Count;SourceRows=$rows.Count;ImportedCleanCandidates=$clean.Count;ImportedNotYetFound=$notImported;SuppressedExisting=$suppressed;PoolTagActions=@($actions|Where-Object Action -eq 'add_pool_tag').Count;QueueTagActions=@($actions|Where-Object Action -eq 'add_queue_tag').Count;EmailOnlyContactsToCreate=@($actions|Where-Object Action -in @('create_email_only','create_missing')).Count;SkipRows=$skips.Count;OutputDirectory=$outputDir};$summary|ConvertTo-Json
if(-not $Apply){return}
foreach($a in $actions){
    if($a.Action -eq 'add_pool_tag'){Request 'POST' ($base + '/contacts/' + $a.ContactId + '/tags') @{tags=@($a.PoolTag)}|Out-Null;Start-Sleep -Milliseconds 250;continue}
    if($a.Action -eq 'add_queue_tag'){Request 'POST' ($base + '/contacts/' + $a.ContactId + '/tags') @{tags=@($a.QueueTag)}|Out-Null;Start-Sleep -Milliseconds 250;continue}
    $lookup=Request 'GET' ($base+'/contacts/?locationId='+[uri]::EscapeDataString($locationId)+'&limit=20&query='+[uri]::EscapeDataString($a.Email)) $null
    if(@($lookup.contacts).Count){$duplicateRejected++;Start-Sleep -Milliseconds 250;continue}
    $tags=@($a.QueueTag,'emerald','august_2026_emerald_contact',$(if($a.PoolTag){$a.PoolTag}else{$a.Category.ToLowerInvariant()+'_pool'}))
    $body=@{locationId=$locationId;firstName=$a.First;lastName=$a.Last;email=$a.Email;companyName=$a.Company;website=$a.Website;city=$a.City;state=$a.State;source='August 2026 Emerald Contacts';tags=$tags;customFields=@(@{id='R0wbDRyzZz34PMlQSRWN';fieldValue=$a.Id})}
    if($a.Phone){$body.phone=$a.Phone}
    try{$createdContact=Request 'POST' ($base+'/contacts/') $body;$created++}catch{$message=$_.Exception.Message;$detail='';try{$detail=(($_.ErrorDetails.Message)|Out-String).Trim()}catch{};if($message -match 'duplicated contacts|already exists|additionalEmail|duplicate'){ $duplicateRejected++ }else{$createErrors++;Add-Content -LiteralPath (Join-Path $outputDir 'August_2026_Emerald_Create_Errors.log') -Value ("$($a.Email): $message $detail")}};Start-Sleep -Milliseconds 350
}
"APPLIED queue tags: $(@($actions|Where-Object Action -eq 'add_queue_tag').Count); created email-only contacts: $created; duplicate skips: $duplicateRejected; other errors: $createErrors"
