$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$apiKeyMatch = Select-String -Path .env -Pattern '^N8N_API_KEY_LT='
if (-not $apiKeyMatch) {
  throw 'N8N_API_KEY_LT not found in .env'
}
$apiKey = $apiKeyMatch.Line.Split('=', 2)[1]
$headers = @{
  'X-N8N-API-KEY' = $apiKey
  'Content-Type' = 'application/json'
}

$workflowId = 'Bukc0mgOD2r7V6ED'
$backupPath = Join-Path $root 'Backup of all n8n workflows\Bukc0mgOD2r7V6ED__LT_-_Report_Executive_Summary_API.json'

function Update-ReportWorkflow([object]$workflow) {
  $buildNode = $workflow.nodes | Where-Object { $_.name -eq 'Build Query' } | Select-Object -First 1
  $shapeNode = $workflow.nodes | Where-Object { $_.name -eq 'Shape Response' } | Select-Object -First 1
  if (-not $buildNode -or -not $shapeNode) {
    throw 'Could not find Build Query or Shape Response nodes.'
  }

  $buildCode = [string]$buildNode.parameters.jsCode
  if ($buildCode -notmatch 'vapi_weekly AS') {
    $weeklyCtes = @'
),
vapi_weekly AS (
  SELECT jsonb_build_object(
    'totalCalls', COUNT(*)::int,
    'answeredCalls', COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) IN ('connected', 'qualified_booked'))::int,
    'missedCalls', COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) IN ('no_answer', 'voicemail', 'busy', 'wrong_number', 'contact_disconnected', 'failed'))::int,
    'qualifiedCalls', COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) = 'qualified_booked')::int,
    'voicemailCalls', COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) = 'voicemail')::int,
    'handoffRequiredCalls', COUNT(*) FILTER (WHERE handoff_required = true)::int,
    'bookingAttemptedCalls', COUNT(*) FILTER (WHERE booking_attempted = true)::int,
    'bookedCalls', COUNT(*) FILTER (WHERE LOWER(COALESCE(booking_result, '')) = 'booked')::int,
    'answeredRate', CASE WHEN COUNT(*) = 0 THEN 0::numeric(10,4) ELSE ROUND(COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) IN ('connected', 'qualified_booked'))::numeric / NULLIF(COUNT(*), 0), 4) END,
    'missedRate', CASE WHEN COUNT(*) = 0 THEN 0::numeric(10,4) ELSE ROUND(COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) IN ('no_answer', 'voicemail', 'busy', 'wrong_number', 'contact_disconnected', 'failed'))::numeric / NULLIF(COUNT(*), 0), 4) END,
    'qualifiedRate', CASE WHEN COUNT(*) = 0 THEN 0::numeric(10,4) ELSE ROUND(COUNT(*) FILTER (WHERE LOWER(COALESCE(disposition, '')) = 'qualified_booked')::numeric / NULLIF(COUNT(*), 0), 4) END
  ) AS payload
  FROM voice_call_attempt
  WHERE created_at >= NOW() - INTERVAL '7 days'
),
vapi_weekly_breakdown AS (
  SELECT COALESCE(json_agg(row_to_json(t) ORDER BY t.call_count DESC), '[]'::json) AS items
  FROM (
    SELECT
      COALESCE(NULLIF(LOWER(disposition), ''), 'unknown') AS disposition,
      COUNT(*)::int AS call_count,
      COUNT(*) FILTER (WHERE handoff_required = true)::int AS handoff_required_count,
      COUNT(*) FILTER (WHERE booking_attempted = true)::int AS booking_attempted_count,
      COUNT(*) FILTER (WHERE LOWER(COALESCE(booking_result, '')) = 'booked')::int AS booked_count
    FROM voice_call_attempt
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY COALESCE(NULLIF(LOWER(disposition), ''), 'unknown')
  ) t
),
'@
    $buildCode = [regex]::Replace($buildCode, [regex]::Escape("),`ncontact_cohort AS ("), $weeklyCtes + "`ncontact_cohort AS (")
  }

  $buildCode = [regex]::Replace($buildCode, "\)\r?\ncontact_cohort AS \(", "),`ncontact_cohort AS (")

  $buildCode = $buildCode -replace "'vapiTimezoneBuckets', \(SELECT payload FROM vapi_timezone_buckets\)", "'vapiTimezoneBuckets', (SELECT payload FROM vapi_timezone_buckets),`n      'vapiWeeklyPerformance', (SELECT payload FROM vapi_weekly),`n      'vapiWeeklyBreakdown', (SELECT items FROM vapi_weekly_breakdown)"
  $buildNode.parameters.jsCode = $buildCode

  $shapeCode = [string]$shapeNode.parameters.jsCode
  if ($shapeCode -notmatch 'var vapiWeeklyPerformance =') {
    $shapeCode = $shapeCode -replace "var vapiTimezoneBuckets = \(data\.vapiTimezoneBuckets && Object\.keys\(data\.vapiTimezoneBuckets\)\.length > 0\) \? data\.vapiTimezoneBuckets : \(summary\.vapiTimezoneBuckets \|\| \{\}\);", "var vapiTimezoneBuckets = (data.vapiTimezoneBuckets && Object.keys(data.vapiTimezoneBuckets).length > 0) ? data.vapiTimezoneBuckets : (summary.vapiTimezoneBuckets || {});`n          var vapiWeeklyPerformance = (data.vapiWeeklyPerformance && Object.keys(data.vapiWeeklyPerformance).length > 0) ? data.vapiWeeklyPerformance : (summary.vapiWeeklyPerformance || {});`n          var vapiWeeklyBreakdown = Array.isArray(data.vapiWeeklyBreakdown) ? data.vapiWeeklyBreakdown : (Array.isArray(summary.vapiWeeklyBreakdown) ? summary.vapiWeeklyBreakdown : []);"
    $shapeCode = $shapeCode -replace "const socialPosts = payload\.socialPosts \|\| \{\}; return", "const vapiWeeklyPerformance = (payload.vapiWeeklyPerformance && Object.keys(payload.vapiWeeklyPerformance).length > 0) ? payload.vapiWeeklyPerformance : (summary.vapiWeeklyPerformance || {});`nconst vapiWeeklyBreakdown = Array.isArray(payload.vapiWeeklyBreakdown) ? payload.vapiWeeklyBreakdown : (Array.isArray(summary.vapiWeeklyBreakdown) ? summary.vapiWeeklyBreakdown : []);`nconst socialPosts = payload.socialPosts || {}; return"
  }
  $shapeCode = $shapeCode -replace "opportunityStageBreakdown } \}\];", "opportunityStageBreakdown, vapiWeeklyPerformance, vapiWeeklyBreakdown } }];"
  $shapeNode.parameters.jsCode = $shapeCode

  return $workflow
}

$workflow = Invoke-RestMethod -Uri "https://automations.livetransparent.com/api/v1/workflows/$workflowId" -Headers $headers
$workflow = Update-ReportWorkflow $workflow

 $putPayload = @{
  name = $workflow.name
  nodes = $workflow.nodes
  connections = $workflow.connections
  settings = $workflow.settings ?? @{}
}
$body = $putPayload | ConvertTo-Json -Depth 100
Invoke-RestMethod -Method Put -Uri "https://automations.livetransparent.com/api/v1/workflows/$workflowId" -Headers $headers -Body $body | Out-Null

$backup = Get-Content -LiteralPath $backupPath -Raw | ConvertFrom-Json -Depth 100
$backup = Update-ReportWorkflow $backup
($backup | ConvertTo-Json -Depth 100) | Set-Content -LiteralPath $backupPath -Encoding utf8

Write-Host "Updated workflow $workflowId and synced backup."
