$ErrorActionPreference = 'Stop'

$envText = Get-Content .env -Raw
if ($envText -notmatch 'N8N_API_KEY_LT=(.+)') {
  throw 'N8N_API_KEY_LT missing'
}
$apiKey = $Matches[1].Trim()
$headers = @{ 'X-N8N-API-KEY' = $apiKey }

$workflowId = 'S32vc8pjJIBZZHLK'
$workflowUrl = "https://automations.livetransparent.com/api/v1/workflows/$workflowId"
$wf = Invoke-RestMethod -Method Get -Uri $workflowUrl -Headers $headers
$active = $wf.activeVersion
if (-not $active) { $active = $wf }

$nodes = @($active.nodes)
$dispatch = $nodes | Where-Object { $_.name -eq 'Dispatch LinkedIn Requests' } | Select-Object -First 1
if (-not $dispatch) { throw 'Dispatch LinkedIn Requests node not found' }

$branch = @'
const sourceRows = $input.all().map((item) => item.json || {});
if (sourceRows.length > 0) {
  const eligible = [];
  for (const row of sourceRows) {
    if (eligible.length >= CFG.maxQueueSize) break;
    const contactId = clean(row.ghl_contact_id || row.contactId || row.id || '');
    const liUrl = clean(row.linkedin_profile_url || row.liUrl || '');
    const providerId = clean(row.linkedin_provider_id || row.providerId || '');
    const identifier = clean(row.linkedin_public_identifier || row.identifier || linkedinId(liUrl));
    const firstName = clean(row.firstName || row.first_name || row.payload_json?.firstName || 'there');
    const connectionStatus = clean(row.connection_status || '').toLowerCase();
    if (!contactId || !liUrl || connectionStatus !== 'ready') continue;
    eligible.push({ id: contactId, firstName, liUrl, providerId, identifier, payload: row });
  }

  const results = [];
  let sentCount = 0;
  let dailySentCount = 0;
  if (typeof this.getWorkflowStaticData === "function") {
    const prev = this.getWorkflowStaticData("global");
    const today = new Date().toISOString().slice(0, 10);
    dailySentCount = prev.date === today ? Number(prev.sentToday || 0) : 0;
    if (dailySentCount >= CFG.dailyLimit) {
      return [{ json: {
        queue_found: eligible.length,
        batch_size: 0,
        sent: 0,
        dry_runs: 0,
        failed: 0,
        sent_today: dailySentCount,
        results: [],
        scanned: sourceRows.length,
        note: "DAILY LIMIT REACHED - no invites sent",
      } }];
    }
  }

  for (const contact of eligible) {
    if (sentCount >= CFG.batchSize) break;
    if (dailySentCount >= CFG.dailyLimit) break;

    let providerId = clean(contact.providerId || '');
    const id = clean(contact.identifier || linkedinId(contact.liUrl));
    if (!id) { results.push({ contactId: contact.id, status: 'skipped', reason: 'invalid_url' }); continue; }

    if (!providerId) {
      const profile = await unipileReq('GET', CFG.unipileApiBaseUrl + '/users/' + encodeURIComponent(id) + '?account_id=' + encodeURIComponent(CFG.unipileAccountId), undefined, { 'X-API-KEY': CFG.unipileApiKey });
      providerId = clean(profile.data?.provider_id || profile.data?.providerId || profile.data?.id || '');
      if (!profile.ok || !providerId) {
        results.push({ contactId: contact.id, firstName: contact.firstName, liUrl: contact.liUrl, identifier: id, providerId, status: CFG.defaultDryRun ? 'dry_run' : 'profile_failed', profileOk: profile.ok, profileError: clean(profile.data?.detail || profile.data?.title || profile.data?.message || '') });
        continue;
      }
    }

    const requestSentAt = new Date().toISOString();
    const msgRaw = CFG.defaultMessage.replace(/\{first_name\}/gi, contact.firstName || 'there');
    const msg = msgRaw.length > 300 ? msgRaw.slice(0, 300) : msgRaw;
    const inv = await unipileReq('POST', CFG.unipileApiBaseUrl + '/users/invite', { account_id: CFG.unipileAccountId, provider_id: providerId, ...(msg ? { message: msg } : {}) }, { 'X-API-KEY': CFG.unipileApiKey });
    let stateSyncOk = false;
    let stateSyncError = '';

    if (inv.ok) {
      try {
        await this.helpers.httpRequest({ method: 'POST', url: CFG.ghlApiBaseUrl + '/contacts/' + encodeURIComponent(contact.id) + '/tags', headers: { Authorization: 'Bearer ' + CFG.ghlApiKey, Version: '2021-07-28', 'Content-Type': 'application/json' }, body: { tags: [CFG.successTag] }, json: true });
      } catch (e) { }
      try {
        await this.helpers.httpRequest({
          method: 'POST',
          url: CFG.connectionStateUpsertUrl,
          headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
          body: {
            ghl_contact_id: contact.id,
            location_id: CFG.locationId,
            unipile_account_id: CFG.unipileAccountId,
            linkedin_profile_url: contact.liUrl,
            linkedin_public_identifier: id,
            linkedin_provider_id: providerId,
            connection_request_tag: CFG.successTag,
            connection_status: 'requested',
            request_sent_at: requestSentAt,
            request_message: msg,
            sequence_step: 0,
            source_workflow_name: CFG.workflowName,
            source_key: 'contact:' + contact.id,
            payload_json: {
              contactId: contact.id,
              firstName: contact.firstName,
              liUrl: contact.liUrl,
              identifier: id,
              providerId,
              status: 'sent',
              inviteOk: true,
              source: 'postgres_queue',
            },
            metadata_json: {
              source: 'dispatcher',
              workflow: CFG.workflowName,
            },
          },
          json: true,
        });
        stateSyncOk = true;
      } catch (stateErr) {
        stateSyncError = describeError(stateErr);
      }
    }

    if (inv.ok) sentCount += 1;
    if (inv.ok) dailySentCount += 1;
    results.push({ contactId: contact.id, firstName: contact.firstName, liUrl: contact.liUrl, identifier: id, providerId, status: inv.ok ? 'sent' : 'invite_failed', inviteOk: inv.ok, stateSyncOk, stateSyncError, requestSentAt });
  }

  const sent = results.filter((r) => r.status === 'sent').length;
  const dryRuns = results.filter((r) => r.status === 'dry_run').length;
  const failed = results.filter((r) => r.status !== 'sent' && r.status !== 'dry_run').length;

  const today = new Date().toISOString().slice(0, 10);
  let dailySent = sent;
  if (typeof this.getWorkflowStaticData === 'function') {
    const prev = this.getWorkflowStaticData('global');
    dailySent = (prev.date === today ? (prev.sentToday || 0) : 0) + sent;
    prev.date = today;
    prev.sentToday = dailySent;
  }

  return [{ json: {
    queue_found: eligible.length,
    batch_size: sent,
    sent,
    dry_runs: dryRuns,
    failed,
    sent_today: dailySent,
    results,
    scanned: sourceRows.length,
    note: CFG.defaultDryRun ? 'DRY RUN MODE - no invites sent' : (sent + ' invites sent'),
  } }];
}
'@

$js = [string]$dispatch.parameters.jsCode
$pattern = 'const eligible = \[\];\s*let scanned = 0;\s*try \{'
$replacement = "const eligible = [];`r`nlet scanned = 0;`r`ntry {`r`n$branch"
$js = [regex]::Replace($js, $pattern, $replacement, 1)
if ($js -notmatch 'sourceRows\.length > 0') {
  throw 'Failed to inject Postgres queue branch'
}
$dispatch.parameters.jsCode = $js

$queueNode = [pscustomobject]@{
  id = 'c8d86f1f-0c1e-4a0f-9f84-queuepostgres'
  name = 'Fetch Ready Queue'
  type = 'n8n-nodes-base.postgres'
  typeVersion = 2.6
  position = @(448, 96)
  parameters = [pscustomobject]@{
    operation = 'executeQuery'
    query = @'
SELECT
  ghl_contact_id,
  connection_status,
  linkedin_profile_url,
  linkedin_public_identifier,
  linkedin_provider_id,
  request_sent_at,
  payload_json,
  metadata_json,
  created_at,
  updated_at
FROM linkedin_connection_state
WHERE connection_status = 'ready'
  AND COALESCE(linkedin_profile_url, '') <> ''
ORDER BY updated_at ASC, created_at ASC
LIMIT 500;
'@
  }
  credentials = [pscustomobject]@{
    postgres = [pscustomobject]@{
      id = 'pgAzUqpwOiGkGXzO'
      name = 'Postgres account'
    }
  }
}

$schedule = $nodes | Where-Object { $_.name -eq 'Schedule Trigger' } | Select-Object -First 1
$manual = $nodes | Where-Object { $_.name -eq 'Manual Trigger' } | Select-Object -First 1
$config = $nodes | Where-Object { $_.name -eq 'Config' } | Select-Object -First 1
$result = $nodes | Where-Object { $_.name -eq 'Result' } | Select-Object -First 1
if (-not $schedule -or -not $manual -or -not $config -or -not $result) {
  throw 'Required nodes missing'
}

$newNodes = @($schedule, $manual, $config, $queueNode, $dispatch, $result)
$connections = [pscustomobject]@{
  'Schedule Trigger' = [pscustomobject]@{
    main = @(@(@{ node = 'Config'; type = 'main'; index = 0 }))
  }
  'Manual Trigger' = [pscustomobject]@{
    main = @(@(@{ node = 'Config'; type = 'main'; index = 0 }))
  }
  'Config' = [pscustomobject]@{
    main = @(@(@{ node = 'Fetch Ready Queue'; type = 'main'; index = 0 }))
  }
  'Fetch Ready Queue' = [pscustomobject]@{
    main = @(@(@{ node = 'Dispatch LinkedIn Requests'; type = 'main'; index = 0 }))
  }
  'Dispatch LinkedIn Requests' = [pscustomobject]@{
    main = @(@(@{ node = 'Result'; type = 'main'; index = 0 }))
  }
}

$putPayload = [ordered]@{
  name = $wf.name
  nodes = $newNodes
  connections = $connections
  settings = @{
    saveExecutionProgress = $true
    saveManualExecutions = $true
    saveDataErrorExecution = 'all'
    saveDataSuccessExecution = 'all'
    executionTimeout = 3600
    timezone = 'UTC'
    executionOrder = 'v1'
  }
}

$body = $putPayload | ConvertTo-Json -Depth 100
$resp = Invoke-RestMethod -Method Put -Uri $workflowUrl -Headers $headers -Body $body -ContentType 'application/json'
[pscustomobject]@{
  name = $resp.name
  active = $resp.active
  updatedAt = $resp.updatedAt
  versionId = $resp.versionId
} | ConvertTo-Json -Depth 5
