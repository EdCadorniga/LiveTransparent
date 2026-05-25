param(
    [string]$ContactId = 'test-contact-id',
    [string]$Phone = '+17144696406',
    [string]$Message = 'Test message from GHL workflow',
    [string]$TemplateKey = '',
    [string]$CampaignKey = 'ghl_manual_sms',
    [string]$ExternalId = '',
    [switch]$DryRun
)

Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$webhookUrl = 'https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms'
$headers = @{ 'x-lt-webhook-key' = 'Lt9Qv2Xm'; 'Content-Type' = 'application/json' }
$resolvedExternalId = if ($ExternalId) { $ExternalId } else { "${ContactId}:$(Get-Date -Format yyyyMMddHHmmss)" }

$payload = @{
    contactId = $ContactId
    contactPhone = $Phone
    campaignKey = $CampaignKey
    externalId = $resolvedExternalId
    source = 'ghl_workflow'
    dryRun = [bool]$DryRun
    contact = @{
        first_name = 'Test'
        last_name = 'User'
        email = 'test@example.com'
    }
}

if ($TemplateKey) {
    $payload.templateKey = $TemplateKey
} else {
    $payload.message = $Message
}

Write-Host "Sending GHL-shaped SMS request to $webhookUrl"
Write-Host "Contact: $ContactId / $Phone"

try {
    $body = $payload | ConvertTo-Json -Depth 10
    $resp = Invoke-RestMethod -Uri $webhookUrl -Method Post -Headers $headers -Body $body -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Response:`n" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10 | Write-Host
    $outPath = Join-Path $scriptDir "ghl_simpletexting_webhook_response.json"
    $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath $outPath -Encoding UTF8
    Write-Host "Saved response to $outPath"
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { Write-Host $_.Exception.Message }
    } else { Write-Host $_.Exception.Message }
    exit 1
}
