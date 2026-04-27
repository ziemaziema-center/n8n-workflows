param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$docId = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q'

function New-HeaderSchema([string[]]$Fields) {
  @($Fields | ForEach-Object {
    [ordered]@{
      id = $_
      displayName = $_
      required = $false
      defaultMatch = $false
      display = $true
      type = 'string'
      canBeUsedToMatch = $true
      removed = $false
    }
  })
}

function New-CreateSheetNode([string]$Name, [string]$Title, [int]$X, [int]$Y) {
  [ordered]@{
    id = [guid]::NewGuid().Guid
    name = $Name
    type = 'n8n-nodes-base.googleSheets'
    typeVersion = 4
    position = @($X, $Y)
    credentials = [ordered]@{
      googleApi = [ordered]@{
        id = '0qLoNOqd9HAUAPaN'
        name = 'Google Sheets account'
      }
    }
    parameters = [ordered]@{
      authentication = 'serviceAccount'
      resource = 'sheet'
      operation = 'create'
      documentId = [ordered]@{
        __rl = $true
        value = $docId
        mode = 'id'
      }
      title = $Title
    }
  }
}

function New-AppendHeadersNode([string]$Name, [string]$SheetName, [int]$X, [int]$Y, [string[]]$Fields) {
  [ordered]@{
    id = [guid]::NewGuid().Guid
    name = $Name
    type = 'n8n-nodes-base.googleSheets'
    typeVersion = 4
    position = @($X, $Y)
    credentials = [ordered]@{
      googleApi = [ordered]@{
        id = '0qLoNOqd9HAUAPaN'
        name = 'Google Sheets account'
      }
    }
    parameters = [ordered]@{
      authentication = 'serviceAccount'
      resource = 'sheet'
      operation = 'append'
      documentId = [ordered]@{
        __rl = $true
        value = $docId
        mode = 'id'
      }
      sheetName = [ordered]@{
        __rl = $true
        value = $SheetName
        mode = 'name'
      }
      columns = [ordered]@{
        mappingMode = 'autoMapInputData'
        value = [ordered]@{}
        matchingColumns = @()
        schema = @(New-HeaderSchema -Fields $Fields)
        attemptToConvertTypes = $false
        convertFieldsToString = $false
      }
      options = [ordered]@{}
    }
  }
}

$workflow = [ordered]@{
  name = '00_Sheet_Setup_fixed'
  nodes = @(
    [ordered]@{
      id = [guid]::NewGuid().Guid
      name = 'Setup Webhook'
      type = 'n8n-nodes-base.webhook'
      typeVersion = 2
      position = @(240, 160)
      parameters = [ordered]@{
        httpMethod = 'POST'
        path = 'sheet-setup-run-fixed'
        responseMode = 'lastNode'
        options = [ordered]@{}
      }
    },
    (New-CreateSheetNode -Name 'Create content_queue' -Title 'content_queue' -X 520 -Y 160),
    [ordered]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed content_queue headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 160)
      parameters = [ordered]@{
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
    [ordered]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed publish_log headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 320)
      parameters = [ordered]@{
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
    [ordered]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed telegram_actions headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 480)
      parameters = [ordered]@{
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
    [ordered]@{
      id = [guid]::NewGuid().Guid
      name = 'Seed improvement_log headers'
      type = 'n8n-nodes-base.code'
      typeVersion = 2
      position = @(760, 640)
      parameters = [ordered]@{
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
  connections = [ordered]@{
    'Setup Webhook' = [ordered]@{
      main = @(@(@{ node = 'Create content_queue'; type = 'main'; index = 0 }))
    }
    'Create content_queue' = [ordered]@{
      main = @(@(@{ node = 'Seed content_queue headers'; type = 'main'; index = 0 }))
    }
    'Seed content_queue headers' = [ordered]@{
      main = @(@(@{ node = 'Append content_queue headers'; type = 'main'; index = 0 }))
    }
    'Append content_queue headers' = [ordered]@{
      main = @(@(@{ node = 'Create publish_log'; type = 'main'; index = 0 }))
    }
    'Create publish_log' = [ordered]@{
      main = @(@(@{ node = 'Seed publish_log headers'; type = 'main'; index = 0 }))
    }
    'Seed publish_log headers' = [ordered]@{
      main = @(@(@{ node = 'Append publish_log headers'; type = 'main'; index = 0 }))
    }
    'Append publish_log headers' = [ordered]@{
      main = @(@(@{ node = 'Create telegram_actions'; type = 'main'; index = 0 }))
    }
    'Create telegram_actions' = [ordered]@{
      main = @(@(@{ node = 'Seed telegram_actions headers'; type = 'main'; index = 0 }))
    }
    'Seed telegram_actions headers' = [ordered]@{
      main = @(@(@{ node = 'Append telegram_actions headers'; type = 'main'; index = 0 }))
    }
    'Append telegram_actions headers' = [ordered]@{
      main = @(@(@{ node = 'Create improvement_log'; type = 'main'; index = 0 }))
    }
    'Create improvement_log' = [ordered]@{
      main = @(@(@{ node = 'Seed improvement_log headers'; type = 'main'; index = 0 }))
    }
    'Seed improvement_log headers' = [ordered]@{
      main = @(@(@{ node = 'Append improvement_log headers'; type = 'main'; index = 0 }))
    }
  }
  settings = [ordered]@{}
}

$created = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows" -Body ($workflow | ConvertTo-Json -Depth 100)
Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$($created.id)/activate" -Body (@{ versionId = $created.versionId } | ConvertTo-Json) | Out-Null
Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/sheet-setup-run-fixed' -ContentType 'application/json' -Body '{}' | Out-Null
