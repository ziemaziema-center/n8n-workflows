param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$docId = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q'

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

$workflow = [pscustomobject]@{
  name = '00_Sheet_Setup'
  nodes = @(
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Setup Webhook'
      type = 'n8n-nodes-base.webhook'
      typeVersion = 2
      position = @(240, 160)
      parameters = @{
        httpMethod = 'POST'
        path = 'sheet-setup-run'
        responseMode = 'lastNode'
        options = @{}
      }
    },
    (New-CreateSheetNode -Name 'Create content_queue' -Title 'content_queue' -X 520 -Y 160),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed content_queue headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 160)
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
    (New-AppendHeadersNode -Name 'Append content_queue headers' -SheetName 'content_queue' -X 1000 -Y 160 -Fields @('content_id','platform','title','body','subtitles','source_url','hashtags','image_url','video_url','time_slot','status','telegram_message_id')),
    (New-CreateSheetNode -Name 'Create publish_log' -Title 'publish_log' -X 520 -Y 320),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed publish_log headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 320)
      parameters = @{
        jsCode = @'
return [{ json: {
  content_id: "content_id",
  publish_id: "publish_id",
  platform: "platform",
  success: "success",
  error: "error",
  timestamp: "timestamp"
} }];
'@
      }
    },
    (New-AppendHeadersNode -Name 'Append publish_log headers' -SheetName 'publish_log' -X 1000 -Y 320 -Fields @('content_id','publish_id','platform','success','error','timestamp')),
    (New-CreateSheetNode -Name 'Create telegram_actions' -Title 'telegram_actions' -X 520 -Y 480),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed telegram_actions headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 480)
      parameters = @{
        jsCode = @'
return [{ json: {
  content_id: "content_id",
  action: "action",
  timestamp: "timestamp"
} }];
'@
      }
    },
    (New-AppendHeadersNode -Name 'Append telegram_actions headers' -SheetName 'telegram_actions' -X 1000 -Y 480 -Fields @('content_id','action','timestamp')),
    (New-CreateSheetNode -Name 'Create improvement_log' -Title 'improvement_log' -X 520 -Y 640),
    [pscustomobject]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed improvement_log headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 640)
      parameters = @{
        jsCode = @'
return [{ json: {
  period: "period",
  suggestion: "suggestion",
  approved: "approved",
  applied_version: "applied_version"
} }];
'@
      }
    },
    (New-AppendHeadersNode -Name 'Append improvement_log headers' -SheetName 'improvement_log' -X 1000 -Y 640 -Fields @('period','suggestion','approved','applied_version'))
  )
  connections = [ordered]@{}
  settings = @{}
}

Set-Conns -Workflow $workflow -From 'Setup Webhook' -OutputIndex 0 -Targets @(
  (New-Conn 'Create content_queue')
)
Set-Conns -Workflow $workflow -From 'Create content_queue' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed content_queue headers')
)
Set-Conns -Workflow $workflow -From 'Seed content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append content_queue headers')
)
Set-Conns -Workflow $workflow -From 'Append content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create publish_log')
)
Set-Conns -Workflow $workflow -From 'Create publish_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed publish_log headers')
)
Set-Conns -Workflow $workflow -From 'Seed publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append publish_log headers')
)
Set-Conns -Workflow $workflow -From 'Append publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create telegram_actions')
)
Set-Conns -Workflow $workflow -From 'Create telegram_actions' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed telegram_actions headers')
)
Set-Conns -Workflow $workflow -From 'Seed telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append telegram_actions headers')
)
Set-Conns -Workflow $workflow -From 'Append telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create improvement_log')
)
Set-Conns -Workflow $workflow -From 'Create improvement_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed improvement_log headers')
)
Set-Conns -Workflow $workflow -From 'Seed improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append improvement_log headers')
)

$body = [ordered]@{
  name        = $workflow.name
  nodes       = $workflow.nodes
  connections = $workflow.connections
  settings    = $workflow.settings
}

$created = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows" -Body ($body | ConvertTo-Json -Depth 100)
Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$($created.id)/activate" -Body (@{ versionId = $created.versionId } | ConvertTo-Json) | Out-Null
Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/sheet-setup-run' -ContentType 'application/json' -Body '{}' | Out-Null
