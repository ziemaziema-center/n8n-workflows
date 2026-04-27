param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = ($apiLine -replace '.*= "','') -replace '"$',''
$apiKey = $apiKey.Trim()

$headers = @{
  'X-N8N-API-KEY' = $apiKey
}

$baseUrl = 'http://43.201.227.194:5678/api/v1'
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

function New-CreateSheetNode {
  param(
    [string]$Name,
    [string]$SheetTitle,
    [int]$X,
    [int]$Y
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
      operation = 'create'
      documentId = $sheetDoc
      title = $SheetTitle
      options = @{}
    }
  }
}

function New-Connection {
  param([string]$Target)
  [pscustomobject]@{ node = $Target; type = 'main'; index = 0 }
}

function Set-Connections {
  param(
    [object]$Workflow,
    [string]$From,
    [int]$OutputIndex,
    [object[]]$Targets
  )

  $conn = $Workflow.connections.$From
  if ($null -eq $conn) {
    $conn = [pscustomobject]@{}
    $Workflow.connections | Add-Member -MemberType NoteProperty -Name $From -Value $conn -Force
  }
  if ($null -eq $conn.main) {
    $conn | Add-Member -MemberType NoteProperty -Name main -Value @() -Force
  }
  while ($conn.main.Count -le $OutputIndex) { $conn.main += ,@() }
  $conn.main[$OutputIndex] = @($Targets)
}

function Invoke-WorkflowPut {
  param([object]$Workflow)

  $body = [ordered]@{
    name        = $Workflow.name
    nodes       = $Workflow.nodes
    connections = $Workflow.connections
    settings    = @{}
  }

  Invoke-RestMethod -Method Put -Uri "$baseUrl/workflows/$($Workflow.id)" -Headers $headers -ContentType 'application/json' -Body ($body | ConvertTo-Json -Depth 100)
}

function Get-LatestExecution {
  param([string]$WorkflowId)
  $exec = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions?workflowId=$WorkflowId&limit=5&includeData=true"
  $exec.data | Sort-Object id -Descending | Select-Object -First 1
}

$workflow = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$generatorWorkflowId"

if (-not ($workflow.nodes | Where-Object { $_.name -eq 'Prepare Sheet Setup' })) {
  $prepareSheetSetup = [pscustomobject]@{
    id = [guid]::NewGuid().Guid
    name = 'Prepare Sheet Setup'
    type = 'n8n-nodes-base.code'
    typeVersion = 2
    position = @(-320, 144)
    parameters = @{
      jsCode = @'
const store = $getWorkflowStaticData('global');
if (!store.sheet_setup_done) {
  store.pending_content_items = JSON.stringify(items.map((item) => item.json));
}

return items.map((item) => ({
  json: {
    ...item.json,
    sheet_setup_state: store.sheet_setup_done ? 'continue' : 'setup'
  }
}));
'@
    }
  }

  $switchSheetSetup = [pscustomobject]@{
    id = [guid]::NewGuid().Guid
    name = 'Switch Sheet Setup'
    type = 'n8n-nodes-base.switch'
    typeVersion = 3.4
    position = @(-80, 144)
    parameters = @{
      rules = @{
        values = @(
          @{
            conditions = @{
              options = @{
                caseSensitive = $true
                typeValidation = 'strict'
                version = 1
              }
              conditions = @(
                @{
                  leftValue = '={{$json.sheet_setup_state}}'
                  rightValue = 'setup'
                  operator = @{
                    type = 'string'
                    operation = 'equals'
                  }
                }
              )
              combinator = 'and'
            }
            renameOutput = $true
            outputKey = 'setup'
          },
          @{
            conditions = @{
              options = @{
                caseSensitive = $true
                typeValidation = 'strict'
                version = 1
              }
              conditions = @(
                @{
                  leftValue = '={{$json.sheet_setup_state}}'
                  rightValue = 'continue'
                  operator = @{
                    type = 'string'
                    operation = 'equals'
                  }
                }
              )
              combinator = 'and'
            }
            renameOutput = $true
            outputKey = 'continue'
          }
        )
      }
      options = @{}
    }
  }

  $markSetupComplete = [pscustomobject]@{
    id = [guid]::NewGuid().Guid
    name = 'Mark Sheet Setup Complete'
    type = 'n8n-nodes-base.code'
    typeVersion = 2
    position = @(1280, 640)
    parameters = @{
      jsCode = @'
const store = $getWorkflowStaticData('global');
const pending = JSON.parse(store.pending_content_items || '[]');
store.sheet_setup_done = true;
delete store.pending_content_items;

return pending.map((row) => ({ json: row }));
'@
    }
  }

  $newNodes = @(
    $prepareSheetSetup,
    $switchSheetSetup,
    (New-CreateSheetNode -Name 'Create content_queue' -SheetTitle 'content_queue' -X 160 -Y 80),
    (New-AppendHeadersNode -Name 'Seed content_queue headers' -SheetName 'content_queue' -X 400 -Y 80 -Fields @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')),
    (New-AppendHeadersNode -Name 'Append content_queue headers' -SheetName 'content_queue' -X 640 -Y 80 -Fields @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')),
    (New-CreateSheetNode -Name 'Create publish_log' -SheetTitle 'publish_log' -X 160 -Y 240),
    (New-AppendHeadersNode -Name 'Seed publish_log headers' -SheetName 'publish_log' -X 400 -Y 240 -Fields @('content_id','publish_id','platform','success','error','timestamp')),
    (New-AppendHeadersNode -Name 'Append publish_log headers' -SheetName 'publish_log' -X 640 -Y 240 -Fields @('content_id','publish_id','platform','success','error','timestamp')),
    (New-CreateSheetNode -Name 'Create telegram_actions' -SheetTitle 'telegram_actions' -X 160 -Y 400),
    (New-AppendHeadersNode -Name 'Seed telegram_actions headers' -SheetName 'telegram_actions' -X 400 -Y 400 -Fields @('content_id','action','timestamp')),
    (New-AppendHeadersNode -Name 'Append telegram_actions headers' -SheetName 'telegram_actions' -X 640 -Y 400 -Fields @('content_id','action','timestamp')),
    (New-CreateSheetNode -Name 'Create improvement_log' -SheetTitle 'improvement_log' -X 160 -Y 560),
    (New-AppendHeadersNode -Name 'Seed improvement_log headers' -SheetName 'improvement_log' -X 400 -Y 560 -Fields @('period','suggestion','approved','applied_version')),
    (New-AppendHeadersNode -Name 'Append improvement_log headers' -SheetName 'improvement_log' -X 640 -Y 560 -Fields @('period','suggestion','approved','applied_version')),
    $markSetupComplete
  )

  foreach ($node in $newNodes) {
    $existing = $workflow.nodes | Where-Object { $_.name -eq $node.name } | Select-Object -First 1
    if ($existing) {
      $existing.parameters = $node.parameters
      $existing.position = $node.position
      $existing.type = $node.type
      $existing.typeVersion = $node.typeVersion
      if ($node.credentials) { $existing.credentials = $node.credentials }
    } else {
      $workflow.nodes += $node
    }
  }
}

# Fix the existing setup workflow style code nodes in case they are still referenced.
Set-CodeNode -Workflow $workflow -Name 'Normalize Content Unit' -Code (($workflow.nodes | Where-Object { $_.name -eq 'Normalize Content Unit' } | Select-Object -First 1).parameters.jsCode)

# Ensure the setup bridge is connected before content queue append.
Set-Connections -Workflow $workflow -From 'Normalize Content Unit' -OutputIndex 0 -Targets @(
  (New-Connection 'Prepare Sheet Setup')
  (New-Connection 'Generate Cover Image')
  (New-Connection 'Merge Cover')
)
Set-Connections -Workflow $workflow -From 'Prepare Sheet Setup' -OutputIndex 0 -Targets @(
  (New-Connection 'Switch Sheet Setup')
)
Set-Connections -Workflow $workflow -From 'Switch Sheet Setup' -OutputIndex 0 -Targets @(
  (New-Connection 'Create content_queue')
)
Set-Connections -Workflow $workflow -From 'Switch Sheet Setup' -OutputIndex 1 -Targets @(
  (New-Connection 'Append Content Queue')
)
Set-Connections -Workflow $workflow -From 'Create content_queue' -OutputIndex 0 -Targets @(
  (New-Connection 'Seed content_queue headers')
)
Set-Connections -Workflow $workflow -From 'Seed content_queue headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Append content_queue headers')
)
Set-Connections -Workflow $workflow -From 'Append content_queue headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Create publish_log')
)
Set-Connections -Workflow $workflow -From 'Create publish_log' -OutputIndex 0 -Targets @(
  (New-Connection 'Seed publish_log headers')
)
Set-Connections -Workflow $workflow -From 'Seed publish_log headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Append publish_log headers')
)
Set-Connections -Workflow $workflow -From 'Append publish_log headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Create telegram_actions')
)
Set-Connections -Workflow $workflow -From 'Create telegram_actions' -OutputIndex 0 -Targets @(
  (New-Connection 'Seed telegram_actions headers')
)
Set-Connections -Workflow $workflow -From 'Seed telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Append telegram_actions headers')
)
Set-Connections -Workflow $workflow -From 'Append telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Create improvement_log')
)
Set-Connections -Workflow $workflow -From 'Create improvement_log' -OutputIndex 0 -Targets @(
  (New-Connection 'Seed improvement_log headers')
)
Set-Connections -Workflow $workflow -From 'Seed improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Append improvement_log headers')
)
Set-Connections -Workflow $workflow -From 'Append improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Connection 'Mark Sheet Setup Complete')
)
Set-Connections -Workflow $workflow -From 'Mark Sheet Setup Complete' -OutputIndex 0 -Targets @(
  (New-Connection 'Append Content Queue')
)

$updatedWorkflow = Invoke-WorkflowPut -Workflow $workflow

try {
  Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger generator workflow: $($_.Exception.Message)"
}

$latest = $null
for ($i = 0; $i -lt 12; $i++) {
  Start-Sleep -Seconds 5
  $latest = Get-LatestExecution -WorkflowId $generatorWorkflowId
  if ($latest.status -in @('success','error','crashed','canceled')) { break }
}

if (-not $latest) {
  throw 'No generator execution found after triggering the workflow.'
}

$executionDetail = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions/$($latest.id)?includeData=true"

[pscustomobject]@{
  workflow_name = $updatedWorkflow.name
  workflow_id = $updatedWorkflow.id
  latest_execution_id = $latest.id
  latest_execution_status = $latest.status
  append_content_queue_failed = ($executionDetail.data.resultData.runData.'Append Content Queue' -ne $null -and $executionDetail.data.resultData.runData.'Append Content Queue'.error -ne $null)
  append_content_queue_error = if ($executionDetail.data.resultData.runData.'Append Content Queue') { $executionDetail.data.resultData.runData.'Append Content Queue'[0].error.message } else { $null }
  sheet_setup_done = if ($executionDetail.data.resultData.runData.'Mark Sheet Setup Complete') { $true } else { $false }
} | ConvertTo-Json -Depth 20
