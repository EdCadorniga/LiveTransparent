param(
  [string]$WorkbookPath = "Cold-outreach contacts.xlsx",
  [string]$OutputDir = "cold-outreach-prep"
)

$ErrorActionPreference = "Stop"

function To-SnakeCase {
  param([string]$Name)
  if ([string]::IsNullOrWhiteSpace($Name)) { return "" }
  $n = $Name.Trim().ToLowerInvariant()
  $n = [regex]::Replace($n, "[^a-z0-9]+", "_")
  $n = [regex]::Replace($n, "^_+|_+$", "")
  return $n
}

function Normalize-Tags {
  param(
    [string]$TagsValue,
    [string]$DefaultTag
  )
  if ([string]::IsNullOrWhiteSpace($TagsValue)) { return $DefaultTag }
  $parts = $TagsValue -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } | Select-Object -Unique
  if (-not $parts -or $parts.Count -eq 0) { return $DefaultTag }
  return ($parts -join ", ")
}

function Get-FirstNonEmpty {
  param(
    [pscustomobject]$Row,
    [string[]]$Keys
  )
  foreach ($k in $Keys) {
    $v = [string]$Row.$k
    if (-not [string]::IsNullOrWhiteSpace($v)) { return $v.Trim() }
  }
  return ""
}

function Sanitize-SheetFilePart {
  param([string]$SheetName)
  return (To-SnakeCase $SheetName)
}

$resolvedWorkbook = Resolve-Path $WorkbookPath
$baseOut = Join-Path (Resolve-Path ".") $OutputDir
$ghlOut = Join-Path $baseOut "ghl"
$pgOut = Join-Path $baseOut "postgres"
$reportOut = Join-Path $baseOut "reports"

New-Item -ItemType Directory -Force -Path $ghlOut | Out-Null
New-Item -ItemType Directory -Force -Path $pgOut | Out-Null
New-Item -ItemType Directory -Force -Path $reportOut | Out-Null

$connStr = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=$($resolvedWorkbook.Path);Extended Properties='Excel 12.0 Xml;HDR=YES;IMEX=1'"
$conn = New-Object System.Data.OleDb.OleDbConnection($connStr)
$conn.Open()

try {
  $schema = $conn.GetOleDbSchemaTable([System.Data.OleDb.OleDbSchemaGuid]::Tables, $null)
  if (-not $schema -or $schema.Rows.Count -eq 0) {
    throw "No worksheets found in workbook."
  }

  $sheetRowsMap = @{}
  $allRows = @()
  $originalHeaders = @()

  foreach ($sheet in $schema.Rows) {
    $sheetTableName = [string]$sheet.TABLE_NAME
    $sheetName = $sheetTableName.Trim("'")
    $defaultTag = switch ($sheetName) {
      "100m+$" { "100M+, cold-outreach" }
      "10-100m$" { "10-100M, cold-outreach" }
      default { "cold-outreach" }
    }
    $sourceSegment = switch ($sheetName) {
      "100m+$" { "100M+" }
      "10-100m$" { "10-100M" }
      default { $sheetName }
    }

    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT * FROM [$sheetTableName]"
    $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($cmd)
    $dt = New-Object System.Data.DataTable
    [void]$adapter.Fill($dt)

    if ($dt.Columns.Count -eq 0) {
      $sheetRowsMap[$sheetName] = @()
      continue
    }

    if ($originalHeaders.Count -eq 0) {
      foreach ($col in $dt.Columns) { $originalHeaders += [string]$col.ColumnName }
    }

    $rowsForSheet = @()
    $sheetRowNumber = 1
    foreach ($r in $dt.Rows) {
      $sheetRowNumber++
      $obj = [ordered]@{}
      foreach ($col in $dt.Columns) {
        $raw = $r[$col.ColumnName]
        if ($raw -is [System.DBNull]) { $raw = "" }
        $obj[[string]$col.ColumnName] = [string]$raw
      }

      $obj["Tags"] = Normalize-Tags -TagsValue ([string]$obj["Tags"]) -DefaultTag $defaultTag
      $rowObj = [pscustomobject]$obj
      $phone = Get-FirstNonEmpty -Row $rowObj -Keys @("Mobile Phone", "Corporate Phone", "Work Direct Phone", "Home Phone", "Other Phone")

      $obj["Phone"] = $phone
      $obj["source_sheet"] = $sheetName
      $obj["source_segment"] = $sourceSegment
      $obj["_sheet_row_number"] = $sheetRowNumber

      $outRow = [pscustomobject]$obj
      $rowsForSheet += $outRow
      $allRows += $outRow
    }

    $sheetRowsMap[$sheetName] = $rowsForSheet
  }

  $allRowsArray = @($allRows)
  if ($allRowsArray.Count -eq 0) {
    throw "No data rows found in workbook."
  }

  $ghlColumns = @(
    "First Name", "Last Name", "Email", "Phone",
    "Company Name", "Title", "Website",
    "City", "State", "Country",
    "Company Address", "Company City", "Company State", "Company Country",
    "Company Phone", "Person Linkedin Url", "Company Linkedin Url",
    "Facebook Url", "Twitter Url",
    "Industry", "# Employees", "Annual Revenue",
    "Tags", "source_sheet", "source_segment"
  )

  $pgWorkflowColumns = @($originalHeaders + @("source_sheet", "source_segment"))

  $snakeCaseMap = @{}
  foreach ($col in $pgWorkflowColumns) {
    $snake = To-SnakeCase $col
    if ($snakeCaseMap.ContainsKey($snake)) {
      $i = 2
      while ($snakeCaseMap.ContainsKey("${snake}_$i")) { $i++ }
      $snake = "${snake}_$i"
    }
    $snakeCaseMap[$col] = $snake
  }
  $pgSnakeColumns = @($pgWorkflowColumns | ForEach-Object { $snakeCaseMap[$_] })

  foreach ($sheetName in $sheetRowsMap.Keys) {
    $safe = Sanitize-SheetFilePart $sheetName
    $rows = @($sheetRowsMap[$sheetName])
    if ($rows.Count -eq 0) { continue }
    $rows |
      Select-Object -Property $ghlColumns |
      Export-Csv -Path (Join-Path $ghlOut "cold-outreach-$safe.ghl.csv") -NoTypeInformation -Encoding UTF8
    $rows |
      Select-Object -Property $pgWorkflowColumns |
      Export-Csv -Path (Join-Path $pgOut "cold-outreach-$safe.workflow-input.csv") -NoTypeInformation -Encoding UTF8

    $snakeRows = foreach ($row in $rows) {
      $o = [ordered]@{}
      foreach ($src in $pgWorkflowColumns) {
        $dst = $snakeCaseMap[$src]
        $o[$dst] = [string]$row.$src
      }
      [pscustomobject]$o
    }
    $snakeRows |
      Select-Object -Property $pgSnakeColumns |
      Export-Csv -Path (Join-Path $pgOut "cold-outreach-$safe.snake_case.csv") -NoTypeInformation -Encoding UTF8
  }

  $allRowsArray |
    Select-Object -Property $ghlColumns |
    Export-Csv -Path (Join-Path $ghlOut "cold-outreach-all.ghl.csv") -NoTypeInformation -Encoding UTF8

  $allRowsArray |
    Select-Object -Property $pgWorkflowColumns |
    Export-Csv -Path (Join-Path $pgOut "cold-outreach-all.workflow-input.csv") -NoTypeInformation -Encoding UTF8

  $allSnakeRows = foreach ($row in $allRowsArray) {
    $o = [ordered]@{}
    foreach ($src in $pgWorkflowColumns) {
      $dst = $snakeCaseMap[$src]
      $o[$dst] = [string]$row.$src
    }
    [pscustomobject]$o
  }
  $allSnakeRows |
    Select-Object -Property $pgSnakeColumns |
    Export-Csv -Path (Join-Path $pgOut "cold-outreach-all.snake_case.csv") -NoTypeInformation -Encoding UTF8

  $seen = @{}
  $dedupRows = @()
  $dupReport = @()

  foreach ($row in $allRowsArray) {
    $emailRaw = [string]$row.Email
    $key = if ([string]::IsNullOrWhiteSpace($emailRaw)) {
      "NO_EMAIL::$([string]$row.source_sheet)::$([string]$row._sheet_row_number)"
    } else {
      $emailRaw.Trim().ToLowerInvariant()
    }

    if (-not $seen.ContainsKey($key)) {
      $seen[$key] = $row
      $dedupRows += $row
      $dupReport += [pscustomobject]@{
          email_key = $key
          email = [string]$row.Email
          action = "kept"
          source_sheet = [string]$row.source_sheet
          sheet_row_number = [string]$row._sheet_row_number
          first_name = [string]$row."First Name"
          last_name = [string]$row."Last Name"
          tags = [string]$row.Tags
          kept_source_sheet = [string]$row.source_sheet
          kept_sheet_row_number = [string]$row._sheet_row_number
        }
    }
    else {
      $kept = $seen[$key]
      $dupReport += [pscustomobject]@{
          email_key = $key
          email = [string]$row.Email
          action = "dropped_duplicate"
          source_sheet = [string]$row.source_sheet
          sheet_row_number = [string]$row._sheet_row_number
          first_name = [string]$row."First Name"
          last_name = [string]$row."Last Name"
          tags = [string]$row.Tags
          kept_source_sheet = [string]$kept.source_sheet
          kept_sheet_row_number = [string]$kept._sheet_row_number
        }
    }
  }

  $dedupRowsArray = @($dedupRows)
  $dedupRowsArray |
    Select-Object -Property $ghlColumns |
    Export-Csv -Path (Join-Path $ghlOut "cold-outreach-all.dedup-email.ghl.csv") -NoTypeInformation -Encoding UTF8

  $dedupRowsArray |
    Select-Object -Property $pgWorkflowColumns |
    Export-Csv -Path (Join-Path $pgOut "cold-outreach-all.dedup-email.workflow-input.csv") -NoTypeInformation -Encoding UTF8

  $dedupSnakeRows = foreach ($row in $dedupRowsArray) {
    $o = [ordered]@{}
    foreach ($src in $pgWorkflowColumns) {
      $dst = $snakeCaseMap[$src]
      $o[$dst] = [string]$row.$src
    }
    [pscustomobject]$o
  }
  $dedupSnakeRows |
    Select-Object -Property $pgSnakeColumns |
    Export-Csv -Path (Join-Path $pgOut "cold-outreach-all.dedup-email.snake_case.csv") -NoTypeInformation -Encoding UTF8

  @($dupReport) |
    Export-Csv -Path (Join-Path $reportOut "cold-outreach-duplicate-email-report.csv") -NoTypeInformation -Encoding UTF8

  $statusCounts = $allRowsArray | Group-Object "Email Status" | Sort-Object Count -Descending | ForEach-Object {
    [pscustomobject]@{
      email_status = [string]$_.Name
      count = [int]$_.Count
    }
  }
  $statusCounts | Export-Csv -Path (Join-Path $reportOut "cold-outreach-email-status-summary.csv") -NoTypeInformation -Encoding UTF8

  $summary = [ordered]@{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    workbook = $resolvedWorkbook.Path
    total_rows = $allRowsArray.Count
    dedup_rows = $dedupRowsArray.Count
    duplicate_rows = ($allRowsArray.Count - $dedupRowsArray.Count)
    unique_email_keys = $seen.Keys.Count
    sheets = @(
      @{
        name = "100m+$"
        rows = @($sheetRowsMap["100m+$"]).Count
        tag_default = "100M+, cold-outreach"
      },
      @{
        name = "10-100m$"
        rows = @($sheetRowsMap["10-100m$"]).Count
        tag_default = "10-100M, cold-outreach"
      }
    )
    outputs = @{
      ghl_dir = $ghlOut
      postgres_dir = $pgOut
      report_dir = $reportOut
    }
  }
  $summary | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $reportOut "cold-outreach-prep-summary.json") -Encoding UTF8
}
finally {
  $conn.Close()
}

Write-Output "Prepared CSV artifacts under: $baseOut"
