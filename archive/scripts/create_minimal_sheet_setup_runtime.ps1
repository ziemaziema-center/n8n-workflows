param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{
  'X-N8N-API-KEY' = $apiKey
}

$baseUrl = 'http://43.201.227.194:5678/api/v1'
$generatorWorkflowId = 'DGMQEgFXqzeS3sJ5'
$docId = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q'

function Invoke-Json {
  param(
    [ValidateSet('GET','POST','PUT')]
    [string]$Method,
    [string]$Uri,
    [object]$Body = $null
  )

  if ($null -eq $Body) {
    return Invoke-RestMethod -Method $Method -Headers $headers -Uri $Uri
  }

  return Invoke-RestMethod -Method $Method -Headers $headers -ContentType 'application/json' -Uri $Uri -Body ($Body | ConvertTo-Json -Depth 100)
}

function Get-Workflow {
  param([string]$Id)
  Invoke-Json -Method GET -Uri "$baseUrl/workflows/$Id"
}

function Put-Workflow {
  param([object]$Workflow)
  $body = [ordered]@{
    name        = $Workflow.name
    nodes       = $Workflow.nodes
    connections = $Workflow.connections
    settings    = @{}
  }
  Invoke-Json -Method PUT -Uri "$baseUrl/workflows/$($Workflow.id)" -Body $body
}

function New-Conn {
  param([string]$Target)
  [pscustomobject]@{ node = $Target; type = 'main'; index = 0 }
}

function Find-Node {
  param([object]$Nodes, [string]$Name)
  $Nodes | Where-Object { $_.name -eq $Name } | Select-Object -First 1
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
  param([string]$Name, [string]$Title, [int]$X, [int]$Y)
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
  param([string]$Name, [string]$SheetName, [int]$X, [int]$Y, [string[]]$Fields)
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

$setupWorkflow = [pscustomobject]@{
  name = '00_Sheet_Setup_runtime'
  nodes = @(
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'When Executed by Another Workflow'
      type = 'n8n-nodes-base.executeWorkflowTrigger'
      typeVersion = 1.1
      position = @(240, 160)
      parameters = @{
        inputSource = 'passthrough'
      }
    },
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Store Setup Input'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(480, 160)
      parameters = @{
        jsCode = @'
const store = $getWorkflowStaticData('global');
store.pending_content_items = JSON.stringify(items.map((item) => item.json));

return items;
'@
      }
    },
    (New-CreateSheetNode -Name 'Create content_queue' -Title 'content_queue' -X 720 -Y 160),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed content_queue headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(960, 160)
      parameters = @{
        jsCode = @'
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
      }
    },
    (New-AppendHeadersNode -Name 'Append content_queue headers' -SheetName 'content_queue' -X 1200 -Y 160 -Fields @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Restore Setup Input'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(1440, 160)
      parameters = @{
        jsCode = @'
const store = $getWorkflowStaticData('global');
const pending = JSON.parse(store.pending_content_items || '[]');
delete store.pending_content_items;

return pending.map((row) => ({ json: row }));
'@
      }
    }
  )
  connections = [ordered]@{}
  settings = @{}
}

Set-Conns -Workflow $setupWorkflow -From 'When Executed by Another Workflow' -OutputIndex 0 -Targets @(
  (New-Conn 'Store Setup Input')
)
Set-Conns -Workflow $setupWorkflow -From 'Store Setup Input' -OutputIndex 0 -Targets @(
  (New-Conn 'Create content_queue')
)
Set-Conns -Workflow $setupWorkflow -From 'Create content_queue' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed content_queue headers')
)
Set-Conns -Workflow $setupWorkflow -From 'Seed content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append content_queue headers')
)
Set-Conns -Workflow $setupWorkflow -From 'Append content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Restore Setup Input')
)

$createdSetup = Invoke-Json -Method POST -Uri "$baseUrl/workflows" -Body $setupWorkflow
$setupWorkflowId = $createdSetup.id

$generator = Get-Workflow -Id $generatorWorkflowId

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
      cachedResultName = '00_Sheet_Setup_runtime'
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

if (-not (Find-Node -Nodes $generator.nodes -Name 'Run Sheet Setup')) {
  $generator.nodes += $executeSetup
}

Set-Conns -Workflow $generator -From 'Normalize Content Unit' -OutputIndex 0 -Targets @(
  (New-Conn 'Run Sheet Setup')
  (New-Conn 'Generate Cover Image')
  (New-Conn 'Merge Cover')
)
Set-Conns -Workflow $generator -From 'Run Sheet Setup' -OutputIndex 0 -Targets @(
  (New-Conn 'Append Content Queue')
)

$updatedGenerator = Put-Workflow -Workflow $generator

try {
  Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger generator workflow: $($_.Exception.Message)"
}

$latest = $null
for ($i = 0; $i -lt 15; $i++) {
  Start-Sleep -Seconds 5
  $execs = Invoke-Json -Method GET -Uri "$baseUrl/executions?workflowId=$generatorWorkflowId&limit=5&includeData=true"
  $latest = $execs.data | Sort-Object id -Descending | Select-Object -First 1
  if ($latest.status -in @('success','error','crashed','canceled')) { break }
}

$details = Invoke-Json -Method GET -Uri "$baseUrl/executions/$($latest.id)?includeData=true"
$runData = $details.data.resultData.runData

[pscustomobject]@{
  setup_workflow_id = $setupWorkflowId
  setup_workflow_name = $createdSetup.name
  generator_workflow_id = $generatorWorkflowId
  latest_execution_id = $latest.id
  latest_execution_status = $latest.status
  setup_subworkflow_status = if ($runData.'Run Sheet Setup') { $runData.'Run Sheet Setup'[0].executionStatus } else { $null }
  append_content_queue_status = if ($runData.'Append Content Queue') { $runData.'Append Content Queue'[0].executionStatus } else { $null }
} | ConvertTo-Json -Depth 20
