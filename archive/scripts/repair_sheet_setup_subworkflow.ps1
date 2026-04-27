param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{
  'X-N8N-API-KEY' = $apiKey
}

$baseUrl = 'http://43.201.227.194:5678/api/v1'
$setupWorkflowId = 'FipYh2cg4CXocUu5'
$generatorWorkflowId = 'DGMQEgFXqzeS3sJ5'
$docId = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q'

function Get-Workflow {
  param([string]$WorkflowId)
  Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$WorkflowId"
}

function Put-Workflow {
  param([object]$Workflow)

  $body = [ordered]@{
    name        = $Workflow.name
    nodes       = $Workflow.nodes
    connections = $Workflow.connections
    settings    = @{}
  }

  Invoke-RestMethod -Method Put -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$($Workflow.id)" -Body ($body | ConvertTo-Json -Depth 100)
}

function New-Conn {
  param([string]$Target)
  [pscustomobject]@{ node = $Target; type = 'main'; index = 0 }
}

function Set-Conns {
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

function Find-Node {
  param([object]$Nodes, [string]$Name)
  $Nodes | Where-Object { $_.name -eq $Name } | Select-Object -First 1
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

function New-CreateSheetNode {
  param(
    [string]$Name,
    [string]$Title,
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
      documentId = @{
        __rl = $true
        value = $docId
        mode = 'id'
      }
      title = $Title
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
      documentId = @{
        __rl = $true
        value = $docId
        mode = 'id'
      }
      sheetName = @{
        __rl = $true
        value = $SheetName
        mode = 'name'
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

function Ensure-Node {
  param([object]$Workflow, [object]$Node)
  $existing = Find-Node -Nodes $Workflow.nodes -Name $Node.name
  if ($existing) {
    foreach ($k in $Node.PSObject.Properties.Name) {
      $existing.$k = $Node.$k
    }
    return $existing
  }

  $Workflow.nodes += $Node
  return $Node
}

# 1) Patch the setup subworkflow.
$setup = Get-Workflow $setupWorkflowId

$trigger = Find-Node -Nodes $setup.nodes -Name 'Setup Webhook'
if ($trigger) {
  $trigger.name = 'When Executed by Another Workflow'
  $trigger.type = 'n8n-nodes-base.executeWorkflowTrigger'
  $trigger.typeVersion = 1.1
  $trigger.parameters = @{
    inputSource = 'passthrough'
  }
  if ($trigger.PSObject.Properties.Name -contains 'webhookId') {
    $trigger.PSObject.Properties.Remove('webhookId')
  }
}

$storeNode = [pscustomobject]@{
  id = [guid]::NewGuid().Guid
  name = 'Store Setup Input'
  type = 'n8n-nodes-base.code'
  typeVersion = 2
  position = @(240, 160)
  parameters = @{
    jsCode = @'
const store = $getWorkflowStaticData('global');
store.pending_content_items = JSON.stringify(items.map((item) => item.json));

return items;
'@
  }
}

$restoreNode = [pscustomobject]@{
  id = [guid]::NewGuid().Guid
  name = 'Restore Setup Input'
  type = 'n8n-nodes-base.code'
  typeVersion = 2
  position = @(1600, 640)
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

Ensure-Node -Workflow $setup -Node $storeNode | Out-Null
Ensure-Node -Workflow $setup -Node $restoreNode | Out-Null

$seedContentQueue = Find-Node -Nodes $setup.nodes -Name 'Seed content_queue headers'
$seedContentQueue.parameters.jsCode = @'
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

$seedPublishLog = Find-Node -Nodes $setup.nodes -Name 'Seed publish_log headers'
$seedPublishLog.parameters.jsCode = @'
return [{ json: {
  content_id: "content_id",
  publish_id: "publish_id",
  platform: "platform",
  success: "success",
  error: "error",
  timestamp: "timestamp"
} }];
'@

$seedTelegram = Find-Node -Nodes $setup.nodes -Name 'Seed telegram_actions headers'
$seedTelegram.parameters.jsCode = @'
return [{ json: {
  content_id: "content_id",
  action: "action",
  timestamp: "timestamp"
} }];
'@

$seedImprove = Find-Node -Nodes $setup.nodes -Name 'Seed improvement_log headers'
$seedImprove.parameters.jsCode = @'
return [{ json: {
  period: "period",
  suggestion: "suggestion",
  approved: "approved",
  applied_version: "applied_version"
} }];
'@

Set-Conns -Workflow $setup -From 'When Executed by Another Workflow' -OutputIndex 0 -Targets @(
  (New-Conn 'Store Setup Input')
)
Set-Conns -Workflow $setup -From 'Store Setup Input' -OutputIndex 0 -Targets @(
  (New-Conn 'Switch Setup State')
)

$switchSetup = [pscustomobject]@{
  id = [guid]::NewGuid().Guid
  name = 'Switch Setup State'
  type = 'n8n-nodes-base.switch'
  typeVersion = 3.4
  position = @(480, 160)
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

Ensure-Node -Workflow $setup -Node $switchSetup | Out-Null

$createContentQueue = New-CreateSheetNode -Name 'Create content_queue' -Title 'content_queue' -X 720 -Y 80
$appendContentQueueHeaders = New-AppendHeadersNode -Name 'Append content_queue headers' -SheetName 'content_queue' -X 960 -Y 80 -Fields @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')
$createPublishLog = New-CreateSheetNode -Name 'Create publish_log' -Title 'publish_log' -X 720 -Y 240
$appendPublishLogHeaders = New-AppendHeadersNode -Name 'Append publish_log headers' -SheetName 'publish_log' -X 960 -Y 240 -Fields @('content_id','publish_id','platform','success','error','timestamp')
$createTelegramActions = New-CreateSheetNode -Name 'Create telegram_actions' -Title 'telegram_actions' -X 720 -Y 400
$appendTelegramHeaders = New-AppendHeadersNode -Name 'Append telegram_actions headers' -SheetName 'telegram_actions' -X 960 -Y 400 -Fields @('content_id','action','timestamp')
$createImproveLog = New-CreateSheetNode -Name 'Create improvement_log' -Title 'improvement_log' -X 720 -Y 560
$appendImproveHeaders = New-AppendHeadersNode -Name 'Append improvement_log headers' -SheetName 'improvement_log' -X 960 -Y 560 -Fields @('period','suggestion','approved','applied_version')

Ensure-Node -Workflow $setup -Node $createContentQueue | Out-Null
Ensure-Node -Workflow $setup -Node $appendContentQueueHeaders | Out-Null
Ensure-Node -Workflow $setup -Node $createPublishLog | Out-Null
Ensure-Node -Workflow $setup -Node $appendPublishLogHeaders | Out-Null
Ensure-Node -Workflow $setup -Node $createTelegramActions | Out-Null
Ensure-Node -Workflow $setup -Node $appendTelegramHeaders | Out-Null
Ensure-Node -Workflow $setup -Node $createImproveLog | Out-Null
Ensure-Node -Workflow $setup -Node $appendImproveHeaders | Out-Null

Set-Conns -Workflow $setup -From 'Switch Setup State' -OutputIndex 0 -Targets @(
  (New-Conn 'Create content_queue')
)
Set-Conns -Workflow $setup -From 'Switch Setup State' -OutputIndex 1 -Targets @(
  (New-Conn 'Restore Setup Input')
)
Set-Conns -Workflow $setup -From 'Create content_queue' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed content_queue headers')
)
Set-Conns -Workflow $setup -From 'Seed content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append content_queue headers')
)
Set-Conns -Workflow $setup -From 'Append content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create publish_log')
)
Set-Conns -Workflow $setup -From 'Create publish_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed publish_log headers')
)
Set-Conns -Workflow $setup -From 'Seed publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append publish_log headers')
)
Set-Conns -Workflow $setup -From 'Append publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create telegram_actions')
)
Set-Conns -Workflow $setup -From 'Create telegram_actions' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed telegram_actions headers')
)
Set-Conns -Workflow $setup -From 'Seed telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append telegram_actions headers')
)
Set-Conns -Workflow $setup -From 'Append telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create improvement_log')
)
Set-Conns -Workflow $setup -From 'Create improvement_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed improvement_log headers')
)
Set-Conns -Workflow $setup -From 'Seed improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append improvement_log headers')
)
Set-Conns -Workflow $setup -From 'Append improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Restore Setup Input')
)

$updatedSetup = Put-Workflow $setup

# 2) Patch the parent workflow to call the sub-workflow before appending to content_queue.
$generator = Get-Workflow $generatorWorkflowId

$prepareSetup = [pscustomobject]@{
  id = [guid]::NewGuid().Guid
  name = 'Prepare Sheet Setup'
  type = 'n8n-nodes-base.code'
  typeVersion = 2
  position = @(-320, 144)
  parameters = @{
    jsCode = @'
const store = $getWorkflowStaticData('global');

return items.map((item) => ({
  json: {
    ...item.json,
    sheet_setup_state: store.sheet_setup_done ? 'continue' : 'setup'
  }
}));
'@
  }
}

$executeSetup = [pscustomobject]@{
  id = [guid]::NewGuid().Guid
  name = 'Run Sheet Setup'
  type = 'n8n-nodes-base.executeWorkflow'
  typeVersion = 1.2
  position = @(-80, 144)
  parameters = @{
    workflowId = @{
      __rl = $true
      mode = 'list'
      value = $setupWorkflowId
      cachedResultName = '00_Sheet_Setup'
    }
    workflowInputs = @{
      mappingMode = 'defineBelow'
      value = @{}
      matchingColumns = @()
      schema = @()
      attemptToConvertTypes = $false
      convertFieldsToString = $true
    }
    options = @{}
  }
}

Ensure-Node -Workflow $generator -Node $prepareSetup | Out-Null
Ensure-Node -Workflow $generator -Node $executeSetup | Out-Null

Set-Conns -Workflow $generator -From 'Normalize Content Unit' -OutputIndex 0 -Targets @(
  (New-Conn 'Run Sheet Setup')
  (New-Conn 'Generate Cover Image')
  (New-Conn 'Merge Cover')
)
Set-Conns -Workflow $generator -From 'Run Sheet Setup' -OutputIndex 0 -Targets @(
  (New-Conn 'Append Content Queue')
)

$updatedGenerator = Put-Workflow $generator

# 3) Trigger the generator once and wait for the execution to settle.
try {
  Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger generator workflow: $($_.Exception.Message)"
}

$latest = $null
for ($i = 0; $i -lt 15; $i++) {
  Start-Sleep -Seconds 5
  $execs = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions?workflowId=$generatorWorkflowId&limit=5&includeData=true"
  $latest = $execs.data | Sort-Object id -Descending | Select-Object -First 1
  if ($latest.status -in @('success','error','crashed','canceled')) { break }
}

if (-not $latest) {
  throw 'No generator execution found after triggering the workflow.'
}

$details = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions/$($latest.id)?includeData=true"
$runData = $details.data.resultData.runData

[pscustomobject]@{
  setup_workflow = $updatedSetup.name
  generator_workflow = $updatedGenerator.name
  latest_execution_id = $latest.id
  latest_execution_status = $latest.status
  append_content_queue_status = if ($runData.'Append Content Queue') { $runData.'Append Content Queue'[0].executionStatus } else { $null }
  setup_node_status = if ($runData.'Run Sheet Setup') { $runData.'Run Sheet Setup'[0].executionStatus } else { $null }
} | ConvertTo-Json -Depth 20
