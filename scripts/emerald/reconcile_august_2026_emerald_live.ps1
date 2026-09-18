param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dir = Join-Path $root 'Contacts added August 25 2026\cleaned'
if (-not $env:GHL_PIT) { throw 'GHL_PIT is not set' }
$locationId = if ($env:GHL_LOCATION_ID) { $env:GHL_LOCATION_ID } else { 'Zwz4relUXVPxx8uohnjV' }
$base = 'https://services.leadconnectorhq.com'
$headers = @{ Authorization = "Bearer $env:GHL_PIT"; Version = '2021-07-28'; Accept = 'application/json'; 'Content-Type' = 'application/json' }
function T([object]$v) { if ($null -eq $v) { '' } else { $v.ToString().Trim().ToLowerInvariant() } }
function Request([string]$method, [string]$uri, [object]$body) {
    for ($attempt=1; $attempt -le 5; $attempt++) {
        try {
            $args = @{ Method=$method; Uri=$uri; Headers=$headers }
            if ($null -ne $body) { $args.Body = ($body | ConvertTo-Json -Depth 20 -Compress) }
            return Invoke-RestMethod @args
        } catch {
            $status = $_.Exception.Response.StatusCode.value__
            if ($status -notin @(429,502,503,504) -or $attempt -eq 5) { throw }
            if ($status -eq 429) { Start-Sleep -Seconds ($attempt * 2) } else { Start-Sleep -Seconds 60 }
        }
    }
}
function PoolFor($category) { if ($category -eq 'Brand') { 'brands_pool' } elseif ($category -eq 'Agency') { 'agency_pool' } else { 'dispensaries_pool' } }
function QueueFor($category) { if ($category -eq 'Dispensaries') { 'Enrollment Queue - DAN - Dispensaries' } else { 'Enrollment Queue - Emerald - Executives MSO' } }
# GHL stores these five AURI addresses as additional emails on Amy Lund's existing
# contact. Do not create or mutate that contact; the duplicate response is expected.
$knownAdditionalEmailDuplicates = @(
    'hstanislawski@auri.org', 'adoering@auri.org', 'aostlund@auri.org',
    'aowens@auri.org', 'aharguth@auri.org'
)
function Blocked($c) {
    $tags=@($c.tags|ForEach-Object{T $_})
    foreach($tag in $tags){ if($tag -in @('do not contact','do not nurture','unsubscribed','opted out','partner_do_not_contact','simpletext_stop') -or $tag -like 'seq emerald -*' -or $tag -eq 'seq enrolled - emerald'){ return $true } }
    return $false
}

$live=@();$url="$base/contacts/?locationId=$([uri]::EscapeDataString($locationId))&limit=100&query=august_2026_emerald_contact"
while($url){$page=Request 'GET' $url $null;$live+=@($page.contacts);$url=$page.meta.nextPageUrl}
$byId=@{};$byEmail=@{}
foreach($c in $live){foreach($f in @($c.customFields)){if($f.id -eq 'R0wbDRyzZz34PMlQSRWN' -and (T $f.value)){$byId[(T $f.value)]=$c}};if($c.email){$byEmail[(T $c.email)]=$c};foreach($e in @($c.additionalEmails)){if($e){$byEmail[(T $e)]=$c}}}
$sources=@(
    @{File='August_2026_Emerald_Brand_GHL_Import.csv';Category='Brand'},
    @{File='August_2026_Emerald_Agency_GHL_Import.csv';Category='Agency'},
    @{File='August_2026_Emerald_Dispensaries_GHL_Import.csv';Category='Dispensaries'}
)
$rows=@();foreach($s in $sources){$rows+=Import-Csv (Join-Path $dir $s.File)|ForEach-Object{[pscustomobject]@{Category=$s.Category;Id=(T $_.Em_Emerald_Contact_ID);Email=(T $_.Email);First=$_.'First Name';Last=$_.'Last Name';Phone=$_.Phone;Company=$_.'Company Name';Website=$_.Website;City=$_.City;State=$_.State}}}
$actions=@();$unmatched=@();$blocked=0
foreach($r in $rows){if($knownAdditionalEmailDuplicates -contains $r.Email){continue};$c=$null;if($byId.ContainsKey($r.Id)){$c=$byId[$r.Id]}elseif($byEmail.ContainsKey($r.Email)){$c=$byEmail[$r.Email]};if($c){if(Blocked $c){$blocked++;continue};$tags=@($c.tags|ForEach-Object{T $_});$pool=PoolFor $r.Category;$queue=QueueFor $r.Category;if($tags -notcontains $pool){$actions+=[pscustomobject]@{Action='pool';Id=$c.id;Tag=$pool;Email=$r.Email}};if($tags -notcontains (T $queue)){$actions+=[pscustomobject]@{Action='queue';Id=$c.id;Tag=$queue;Email=$r.Email}}}else{$unmatched+=$r}}
if($Apply){foreach($r in $unmatched){$check=Request 'GET' ($base+'/contacts/?locationId='+[uri]::EscapeDataString($locationId)+'&limit=20&query='+[uri]::EscapeDataString($r.Email)) $null;if(@($check.contacts).Count){continue};$pool=PoolFor $r.Category;$queue=QueueFor $r.Category;$body=@{locationId=$locationId;firstName=$r.First;lastName=$r.Last;email=$r.Email;companyName=$r.Company;website=$r.Website;city=$r.City;state=$r.State;source='August 2026 Emerald Contacts';tags=@($queue,'emerald','august_2026_emerald_contact',$pool);customFields=@(@{id='R0wbDRyzZz34PMlQSRWN';fieldValue=$r.Id})};if($r.Phone){$body.phone=$r.Phone};try{Request 'POST' ($base+'/contacts/') $body|Out-Null;Write-Output "created $($r.Email)"}catch{Write-Warning "create failed $($r.Email): $($_.Exception.Message)"};Start-Sleep -Milliseconds 100};foreach($group in @($actions|Group-Object Id)){ $tags=@($group.Group|ForEach-Object Tag|Sort-Object -Unique);try{Request 'POST' ($base+'/contacts/'+$group.Name+'/tags') @{tags=$tags}|Out-Null;Add-Content -LiteralPath (Join-Path $dir 'August_2026_Emerald_Tag_Success.log') -Value ((Get-Date).ToString('o')+" `t$($group.Name) `t$($tags -join ',')")}catch{Write-Warning "tag failed $($group.Name): $($_.Exception.Message)"}}}
$actionTypes=@{};foreach($a in $actions){$type=$a.Tag;if(!$actionTypes.ContainsKey($type)){$actionTypes[$type]=0};$actionTypes[$type]++}
[ordered]@{Mode=if($Apply){'APPLY'}else{'DRY_RUN'};LiveTagged=$live.Count;SourceRows=$rows.Count;Unmatched=$unmatched.Count;ExactEmailCandidates=$unmatched.Email.Count;Blocked=$blocked;TagActions=$actions.Count;ActionTags=$actionTypes}|ConvertTo-Json -Depth 5
