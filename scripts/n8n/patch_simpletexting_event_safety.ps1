$ErrorActionPreference = 'Stop'

$line = Get-Content -LiteralPath '.env' | Where-Object { $_ -match '^N8N_API_KEY_LT=' } | Select-Object -First 1
if (-not $line) { throw 'N8N_API_KEY_LT missing from .env' }
$key = $line.Substring('N8N_API_KEY_LT='.Length).Trim().Trim('"')
$headers = @{ 'X-N8N-API-KEY' = $key; 'Content-Type' = 'application/json' }
$base = 'https://automations.livetransparent.com/api/v1/workflows/'

function Get-Wf($id) {
  Invoke-RestMethod -Method Get -Uri ($base + $id) -Headers $headers
}

function Put-Wf($w) {
  $settings = @{}
  if ($w.settings) {
    foreach ($p in $w.settings.PSObject.Properties) {
      if ($p.Name -ne 'availableInMCP') { $settings[$p.Name] = $p.Value }
    }
  }
  $payload = @{ name = $w.name; nodes = $w.nodes; connections = $w.connections; settings = $settings }
  $json = $payload | ConvertTo-Json -Depth 100 -Compress
  Invoke-RestMethod -Method Put -Uri ($base + $w.id) -Headers $headers -Body $json
}

function New-CodeNode($name, $code, $position) {
  [pscustomobject]@{
    id = [guid]::NewGuid().ToString()
    name = $name
    type = 'n8n-nodes-base.code'
    typeVersion = 2
    position = $position
    parameters = @{ jsCode = $code }
  }
}

function New-PostgresNode($name, $position) {
  [pscustomobject]@{
    id = [guid]::NewGuid().ToString()
    name = $name
    type = 'n8n-nodes-base.postgres'
    typeVersion = 2.6
    position = $position
    parameters = @{
      operation = 'executeQuery'
      query = @'
WITH lock AS (
  SELECT pg_advisory_xact_lock(hashtextextended($4, 0)) AS acquired
), claimed AS (
  INSERT INTO "SimpleTexting_Campaign_Event_Log"
    (ghl_contact_id, campaign_key, event_type, provider_message_id, details)
  SELECT
    COALESCE(NULLIF($1, ''), 'unresolved:' || md5($4)),
    $2,
    $3,
    $4,
    $5::jsonb
  FROM lock
  WHERE NOT EXISTS (
    SELECT 1
    FROM "SimpleTexting_Campaign_Event_Log"
    WHERE campaign_key = $2
      AND event_type = $3
      AND provider_message_id = $4
  )
  RETURNING id
)
SELECT EXISTS(SELECT 1 FROM claimed) AS "newEvent", $4 AS "eventKey";
'@
      options = @{
        queryBatching = 'single'
        queryReplacement = '={{ [ $json.eventContactId || "", $json.campaignKey || "simpletexting_campaign_v1", $json.eventType, $json.eventKey, JSON.stringify($json.eventPayload || {}) ] }}'
      }
    }
  }
}

function New-IfNode($name, $leftExpression, $position) {
  [pscustomobject]@{
    id = [guid]::NewGuid().ToString()
    name = $name
    type = 'n8n-nodes-base.if'
    typeVersion = 2.2
    position = $position
    parameters = @{
      conditions = @{
        options = @{ caseSensitive = $true; leftValue = ''; typeValidation = 'strict'; version = 2 }
        conditions = @(@{
          leftValue = $leftExpression
          rightValue = $true
          operator = @{ type = 'boolean'; operation = 'true'; id = ([guid]::NewGuid().ToString()) }
        })
      }
      options = @{}
    }
  }
}

function Set-MainConnection($w, $from, $outputs) {
  $groups = New-Object System.Collections.ArrayList
  foreach ($output in @($outputs)) { [void]$groups.Add(@($output)) }
  $value = $groups.ToArray()
  $property = $w.connections.PSObject.Properties[$from]
  if ($property) { $property.Value.main = $value }
  else { $w.connections | Add-Member -NotePropertyName $from -NotePropertyValue ([pscustomobject]@{ main = $value }) }
}

function Add-EventSafety($w, $kind) {
  $validateName = switch ($kind) {
    'inbound' { 'Validate + Normalize Reply' }
    'delivery' { 'Validate + Normalize Delivery' }
    'unsubscribe' { 'Validate + Normalize Unsubscribe' }
  }
  $upsertName = switch ($kind) {
    'inbound' { 'Upsert SMS State' }
    'delivery' { 'Upsert Delivery State' }
    'unsubscribe' { 'Upsert Unsubscribe State' }
  }

  $safetyNames = @('Build Event Key', 'Claim Event', 'IF - New Event', 'Restore Event Input', 'Duplicate Event Response', 'IF - Contact Resolved', 'Unresolved Event Response')
  $w.nodes = @($w.nodes | Where-Object { $_.name -notin $safetyNames })
  foreach ($safetyName in $safetyNames) {
    $property = $w.connections.PSObject.Properties[$safetyName]
    if ($property) { $w.connections.PSObject.Properties.Remove($safetyName) }
  }

  $buildCode = switch ($kind) {
    'inbound' {
@'
const root = $json || {};
const body = root.body || root;
const values = body.values || {};
const clean = (v) => String(v ?? '').trim();
const digits = (v) => clean(v).replace(/\D/g, '');
const normalize = (v) => {
  const d = digits(v);
  return d.length === 11 && d.startsWith('1') ? d.slice(1) : d;
};
const hash = (value) => {
  let h = 2166136261;
  for (let i = 0; i < value.length; i++) h = Math.imul(h ^ value.charCodeAt(i), 16777619);
  return (h >>> 0).toString(16);
};
const messageId = clean(values.messageId || body.messageId || body.message_id || body.id || body.smid);
const phone = normalize(values.contactPhone || body.contactPhone || body.from || body.phone || body.mobile || body.senderPhone);
const contactId = clean(values.contactId || body.contactId || body.ghlContactId || body.externalGhlContactId);
const message = clean(values.text || body.text || body.message || body.smsBody);
const timestamp = clean(values.timestamp || body.receivedAt || body.timestamp || body.createdAt || body.date);
const eventKey = messageId ? `inbound:${messageId}` : `inbound:${hash(JSON.stringify({ phone, contactId, message, timestamp }))}`;
return [{ json: { ...root, eventType: 'inbound_reply', eventKey, eventContactId: contactId, campaignKey: 'simpletexting_campaign_v1', eventPayload: { phone, contactId, messageId, timestamp } } }];
'@
    }
    'delivery' {
@'
const root = $json || {};
const body = root.body || root;
const values = body.values || {};
const clean = (v) => String(v ?? '').trim();
const digits = (v) => clean(v).replace(/\D/g, '');
const normalize = (v) => { const d = digits(v); return d.length === 11 && d.startsWith('1') ? d.slice(1) : d; };
const hash = (value) => { let h = 2166136261; for (let i = 0; i < value.length; i++) h = Math.imul(h ^ value.charCodeAt(i), 16777619); return (h >>> 0).toString(16); };
const messageId = clean(values.messageId || body.messageId || body.message_id || body.id || body.smsid);
const status = clean(values.status || body.status || body.deliveryStatus || body.state || body.messageStatus || 'unknown').toLowerCase();
const phone = normalize(values.contactPhone || body.contactPhone || body.to || body.phone || body.mobile || body.destination);
const contactId = clean(values.contactId || body.contactId || body.ghlContactId || body.externalContactId);
const timestamp = clean(values.timestamp || body.deliveredAt || body.timestamp || body.updatedAt || body.date);
const eventKey = messageId ? `delivery:${messageId}:${status}` : `delivery:${hash(JSON.stringify({ phone, contactId, status, timestamp }))}`;
return [{ json: { ...root, eventType: 'delivery_event', eventKey, eventContactId: contactId, campaignKey: clean(values.campaignKey || body.campaignKey || 'simpletexting_campaign_v1'), eventPayload: { phone, contactId, messageId, status, timestamp } } }];
'@
    }
    'unsubscribe' {
@'
const root = $json || {};
const body = root.body || root;
const values = body.values || {};
const clean = (v) => String(v ?? '').trim();
const digits = (v) => clean(v).replace(/\D/g, '');
const normalize = (v) => { const d = digits(v); return d.length === 11 && d.startsWith('1') ? d.slice(1) : d; };
const hash = (value) => { let h = 2166136261; for (let i = 0; i < value.length; i++) h = Math.imul(h ^ value.charCodeAt(i), 16777619); return (h >>> 0).toString(16); };
const eventId = clean(values.eventId || body.eventId || body.event_id || values.messageId || body.messageId || body.id);
const phone = normalize(values.phone || values.contactPhone || body.phone || body.mobile || body.from || body.contactPhone);
const contactId = clean(values.contactId || body.contactId || body.ghlContactId || body.externalContactId);
const keyword = clean(values.keyword || body.keyword || body.reply || body.reason || 'STOP').toUpperCase();
const timestamp = clean(values.timestamp || body.unsubscribedAt || body.timestamp || body.createdAt || body.date);
const eventKey = eventId ? `unsubscribe:${eventId}` : `unsubscribe:${hash(JSON.stringify({ phone, contactId, keyword, timestamp }))}`;
return [{ json: { ...root, eventType: 'unsubscribe_event', eventKey, eventContactId: contactId, campaignKey: clean(values.campaignKey || body.campaignKey || 'simpletexting_campaign_v1'), eventPayload: { phone, contactId, eventId, keyword, timestamp } } }];
'@
  }
}

$restoreCode = @'
const original = $('Build Event Key').item.json || {};
return [{ json: { ...original, newEvent: $json.newEvent === true, eventKey: $json.eventKey } }];
'@
$duplicateCode = @'
return [{ json: { ok: true, duplicateIgnored: true, eventKey: $json.eventKey || '', nextStep: 'duplicate_event_ignored' } }];
'@
$unresolvedCode = @'
return [{ json: { ...$json, ok: true, unresolved: true, nextStep: 'unresolved_contact_ignored', error: 'contact_not_resolved' } }];
'@

  $build = New-CodeNode 'Build Event Key' $buildCode @(220, 120)
  $claim = New-PostgresNode 'Claim Event' @(440, 120)
  $newIf = New-IfNode 'IF - New Event' '={{ $json.newEvent }}' @(660, 120)
  $restore = New-CodeNode 'Restore Event Input' $restoreCode @(880, 80)
  $duplicate = New-CodeNode 'Duplicate Event Response' $duplicateCode @(880, 180)
  $contactIf = New-IfNode 'IF - Contact Resolved' '={{ !!$json.contactId }}' @(1100, 80)
  $unresolved = New-CodeNode 'Unresolved Event Response' $unresolvedCode @(1320, 180)
  $existingUpsert = $w.nodes | Where-Object name -eq $upsertName
  if ($existingUpsert.credentials) { $claim | Add-Member -NotePropertyName credentials -NotePropertyValue $existingUpsert.credentials }
  $w.nodes = @($w.nodes) + @($build, $claim, $newIf, $restore, $duplicate, $contactIf, $unresolved)

  Set-MainConnection $w 'Config' @(@{ node = 'Build Event Key'; type = 'main'; index = 0 })
  Set-MainConnection $w 'Build Event Key' @(@{ node = 'Claim Event'; type = 'main'; index = 0 })
  Set-MainConnection $w 'Claim Event' @(@{ node = 'IF - New Event'; type = 'main'; index = 0 })
  Set-MainConnection $w 'IF - New Event' @(@{ node = 'Restore Event Input'; type = 'main'; index = 0 }), @(@{ node = 'Duplicate Event Response'; type = 'main'; index = 0 })
  Set-MainConnection $w 'Restore Event Input' @(@{ node = $validateName; type = 'main'; index = 0 })
  Set-MainConnection $w $validateName @(@{ node = 'IF - Contact Resolved'; type = 'main'; index = 0 })
  Set-MainConnection $w 'IF - Contact Resolved' @(@{ node = $upsertName; type = 'main'; index = 0 }), @(@{ node = 'Unresolved Event Response'; type = 'main'; index = 0 })

  $validate = $w.nodes | Where-Object name -eq $validateName
  $marker = switch ($kind) {
    'inbound' { 'const resolvedContact = await resolveGhlContact.call(this, from, explicitGhlContactId);' }
    'delivery' { 'const resolvedContact = await resolveGhlContact.call(this, to, contactId);' }
    'unsubscribe' { 'const resolvedContact = await resolveGhlContact.call(this, phone, contactId);' }
  }
$guard = @'
if (!resolvedContact.contactId) {
  return [{ json: { ...$json, ok: true, unresolved: true, nextStep: 'unresolved_contact_ignored', error: 'contact_not_resolved' } }];
}
'@
  if (-not $validate.parameters.jsCode.Contains('unresolved_contact_ignored')) {
    $validate.parameters.jsCode = $validate.parameters.jsCode.Replace($marker, $marker + "`n" + $guard)
  }

  $upsert = $w.nodes | Where-Object name -eq $upsertName
  $query = [string]$upsert.parameters.query
  $query = [regex]::Replace($query, ',\r?\ninsert_event AS \(.*?\r?\n\)\r?\nSELECT', "`nSELECT", [System.Text.RegularExpressions.RegexOptions]::Singleline)
  $upsert.parameters.query = $query
  return $w
}

$configs = @(
  @{ id = 'i0pROHpFtN4LYR0Q'; kind = 'inbound' },
  @{ id = 'AEi1VCzkLvaYFr4U'; kind = 'delivery' },
  @{ id = 'IyBKMkpYQ7pa0C8V'; kind = 'unsubscribe' }
)

foreach ($item in $configs) {
  $workflow = Add-EventSafety (Get-Wf $item.id) $item.kind
  $saved = Put-Wf $workflow
  [pscustomobject]@{ id = $saved.id; name = $saved.name; versionId = $saved.versionId; activeVersionId = $saved.activeVersionId; active = $saved.active } | ConvertTo-Json -Compress
}
