Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Live send test to n8n SimpleTexting webhook
$webhookUrl = 'https://automations.livetransparent.com/webhook/lt-simpletexting-send-sms'
$headers = @{ 'x-lt-webhook-key' = 'Lt9Qv2Xm'; 'Content-Type' = 'application/json' }

# Test payload - replace number and templateKey as needed
$payload = @{ 
    contactId = '';
    contactPhone = '+17144696406';
    templateKey = 'john_sms4';
    contact = @{ first_name = 'Live'; last_name = 'Test'; email = 'test@example.com' };
    dryRun = $false
}

Write-Host "Sending live SMS test to $($payload.contactPhone) using template $($payload.templateKey)"
try {
    $body = $payload | ConvertTo-Json -Depth 10
    $resp = Invoke-RestMethod -Uri $webhookUrl -Method Post -Headers $headers -Body $body -ContentType 'application/json' -ErrorAction Stop
    Write-Host "Response:`n" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 10 | Write-Host
    $outPath = Join-Path $scriptDir "live_webhook_response.json"
    $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath $outPath -Encoding UTF8
    Write-Host "Saved response to $outPath"
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    if ($_.Exception.Response -ne $null) {
        try { $text = $_.Exception.Response.Content.ReadAsStringAsync().Result; Write-Host $text } catch { Write-Host $_.Exception.Message }
    } else { Write-Host $_.Exception.Message }
    exit 1
}
