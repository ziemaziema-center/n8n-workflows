param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = $apiLine -replace '.*= "',' ' -replace '"$',''
$apiKey = $apiKey.Trim()

$headers = @{
  'X-N8N-API-KEY' = $apiKey
}

$baseUrl = 'http://43.201.227.194:5678/api/v1'
$setupWorkflowId = 'FipYh2cg4CXocUu5'
$generatorWorkflowId = 'DGMQEgFXqzeS3sJ5'
$sheetDoc = [pscustomobject]@{
  __rl = $true
  mode = 'id'
  value = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q'
}

function Set-CodeNode {
  param(
    [object]$Workflow,
    [string]$Name,
    [string]$Code
  )

  $node = $Workflow.nodes | Where-Object { $_.name -eq $Name } | Select-Object -First 1
  if (-not $node) { throw "Missing node: $Name" }
  $node.parameters.jsCode = $Code
}

function New-HeaderSchema {
  param([string[]]$Fields)
  $Fields | ForEach-Object {
    [pscustomobject]@{
      id = $_
      displayName = $_
      required = $false
      defaultMatch = $false
      display = $true
      type = 'string'
      canBeUsedToMatch = $true
      removed = $false
    }
  }
}

function New-AppendHeadersNode {
  param(
    [string]$Name,
    [string]$SheetName,
    [int]$X,
    [int]$Y,
    [string[]]$Fields
  )

  [pscustomobject]@{
    id = [guid]::NewGuid().Guid
    name = $Name
    type = 'n8n-nodes-base.googleSheets'
    typeVersion = 4
    position = @($X, $Y)
    credentials = @{
      googleApi = @{
        id = '0qLoNOqd9HAUAPaN'
        name = 'Google Sheets account'
      }
    }
    parameters = @{
      authentication = 'serviceAccount'
      resource = 'sheet'
      operation = 'append'
      documentId = $sheetDoc
      sheetName = @{
        __rl = $true
        mode = 'name'
        value = $SheetName
      }
      columns = @{
        mappingMode = 'autoMapInputData'
        value = @{}
        matchingColumns = @()
        schema = (New-HeaderSchema -Fields $Fields)
        attemptToConvertTypes = $false
        convertFieldsToString = $false
      }
      options = @{}
    }
  }
}

function New-Connection {
  param([string]$Target)
  [pscustomobject]@{ node = $Target; type = 'main'; index = 0 }
}

function Invoke-WorkflowPut {
  param([object]$Workflow)

  $body = [ordered]@{
    name        = $Workflow.name
    nodes       = $Workflow.nodes
    connections = $Workflow.connections
    settings    = $Workflow.settings
  }

  Invoke-RestMethod -Method Put -Uri "$baseUrl/workflows/$($Workflow.id)" -Headers $headers -ContentType 'application/json' -Body ($body | ConvertTo-Json -Depth 100)
}

function Get-ExecutionByWorkflow {
  param([string]$WorkflowId)
  Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions?workflowId=$WorkflowId&limit=5&includeData=true"
}

$setup = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$setupWorkflowId"

Set-CodeNode -Workflow $setup -Name 'Seed content_queue headers' -Code @'
return [{ json: {
  content_id: "content_id",
  platform: "platform",
  title: "title",
  body: "body",
  subtitles: "subtitles",
  source_url: "source_url",
  hashtags: "hashtags",
  image_url: "image_url",
  video_url: "video_url",
  time_slot: "time_slot",
  status: "status",
  telegram_message_id: "telegram_message_id"
} }];
'@

Set-CodeNode -Workflow $setup -Name 'Seed publish_log headers' -Code @'
return [{ json: {
  content_id: "content_id",
  publish_id: "publish_id",
  platform: "platform",
  success: "success",
  error: "error",
  timestamp: "timestamp"
} }];
'@

Set-CodeNode -Workflow $setup -Name 'Seed telegram_actions headers' -Code @'
return [{ json: {
  content_id: "content_id",
  action: "action",
  timestamp: "timestamp"
} }];
'@

Set-CodeNode -Workflow $setup -Name 'Seed improvement_log headers' -Code @'
return [{ json: {
  period: "period",
  suggestion: "suggestion",
  approved: "approved",
  applied_version: "applied_version"
} }];
'@

$contentFields = @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')
$publishFields = @('content_id','publish_id','platform','success','error','timestamp')
$actionFields = @('content_id','action','timestamp')
$improveFields = @('period','suggestion','approved','applied_version')

$nodes = @(
  (New-AppendHeadersNode -Name 'Append content_queue headers' -SheetName 'content_queue' -X 1020 -Y 160 -Fields $contentFields),
  (New-AppendHeadersNode -Name 'Append publish_log headers' -SheetName 'publish_log' -X 1020 -Y 320 -Fields $publishFields),
  (New-AppendHeadersNode -Name 'Append telegram_actions headers' -SheetName 'telegram_actions' -X 1020 -Y 480 -Fields $actionFields),
  (New-AppendHeadersNode -Name 'Append improvement_log headers' -SheetName 'improvement_log' -X 1020 -Y 640 -Fields $improveFields)
)

foreach ($node in $nodes) {
  $existing = $setup.nodes | Where-Object { $_.name -eq $node.name } | Select-Object -First 1
  if ($existing) {
    $existing.parameters = $node.parameters
    $existing.position = $node.position
    $existing.type = $node.type
    $existing.typeVersion = $node.typeVersion
    $existing.credentials = $node.credentials
  } else {
    $setup.nodes += $node
  }
}

$setup.connections = [ordered]@{
  'Setup Webhook' = [pscustomobject]@{
    main = @(@(New-Connection 'Create content_queue'))
  }
  'Create content_queue' = [pscustomobject]@{
    main = @(@(New-Connection 'Seed content_queue headers'))
  }
  'Seed content_queue headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Append content_queue headers'))
  }
  'Append content_queue headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Create publish_log'))
  }
  'Create publish_log' = [pscustomobject]@{
    main = @(@(New-Connection 'Seed publish_log headers'))
  }
  'Seed publish_log headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Append publish_log headers'))
  }
  'Append publish_log headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Create telegram_actions'))
  }
  'Create telegram_actions' = [pscustomobject]@{
    main = @(@(New-Connection 'Seed telegram_actions headers'))
  }
  'Seed telegram_actions headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Append telegram_actions headers'))
  }
  'Append telegram_actions headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Create improvement_log'))
  }
  'Create improvement_log' = [pscustomobject]@{
    main = @(@(New-Connection 'Seed improvement_log headers'))
  }
  'Seed improvement_log headers' = [pscustomobject]@{
    main = @(@(New-Connection 'Append improvement_log headers'))
  }
}

$updatedSetup = Invoke-WorkflowPut -Workflow $setup

$activateBody = @{ versionId = $updatedSetup.versionId } | ConvertTo-Json
try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/workflows/$setupWorkflowId/activate" -Headers $headers -ContentType 'application/json' -Body $activateBody | Out-Null
} catch {
  throw "Failed to activate setup workflow: $($_.Exception.Message)"
}

try {
  Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/sheet-setup-run' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger setup webhook: $($_.Exception.Message)"
}

Start-Sleep -Seconds 8

$setupExecutions = Get-ExecutionByWorkflow -WorkflowId $setupWorkflowId
$latestSetup = $setupExecutions.data | Sort-Object id -Descending | Select-Object -First 1

try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/workflows/$setupWorkflowId/deactivate" -Headers $headers | Out-Null
} catch {
  # best effort
}

try {
  Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger generator workflow: $($_.Exception.Message)"
}

Start-Sleep -Seconds 10

$generatorExecutions = Get-ExecutionByWorkflow -WorkflowId $generatorWorkflowId
$latestGenerator = $generatorExecutions.data | Sort-Object id -Descending | Select-Object -First 1

[pscustomobject]@{
  setup_workflow_active = $false
  setup_execution_id    = $latestSetup.id
  setup_execution_status = $latestSetup.status
  generator_execution_id = $latestGenerator.id
  generator_execution_status = $latestGenerator.status
} | ConvertTo-Json -Depth 10
