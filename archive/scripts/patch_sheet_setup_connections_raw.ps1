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

$raw = (Invoke-WebRequest -UseBasicParsing -Headers $headers -Uri "$baseUrl/workflows/$setupWorkflowId").Content
$workflow = $raw | ConvertFrom-Json

$workflow.connections = [ordered]@{
  'When Executed by Another Workflow' = [ordered]@{ main = @(@(@{ node = 'Store Setup Input'; type = 'main'; index = 0 })) }
  'Store Setup Input' = [ordered]@{ main = @(@(@{ node = 'Switch Setup State'; type = 'main'; index = 0 })) }
  'Switch Setup State' = [ordered]@{
    main = @(
      @(@(@{ node = 'Create content_queue'; type = 'main'; index = 0 })),
      @(@(@{ node = 'Restore Setup Input'; type = 'main'; index = 0 }))
    )
  }
  'Create content_queue' = [ordered]@{ main = @(@(@{ node = 'Seed content_queue headers'; type = 'main'; index = 0 })) }
  'Seed content_queue headers' = [ordered]@{ main = @(@(@{ node = 'Append content_queue headers'; type = 'main'; index = 0 })) }
  'Append content_queue headers' = [ordered]@{ main = @(@(@{ node = 'Create publish_log'; type = 'main'; index = 0 })) }
  'Create publish_log' = [ordered]@{ main = @(@(@{ node = 'Seed publish_log headers'; type = 'main'; index = 0 })) }
  'Seed publish_log headers' = [ordered]@{ main = @(@(@{ node = 'Append publish_log headers'; type = 'main'; index = 0 })) }
  'Append publish_log headers' = [ordered]@{ main = @(@(@{ node = 'Create telegram_actions'; type = 'main'; index = 0 })) }
  'Create telegram_actions' = [ordered]@{ main = @(@(@{ node = 'Seed telegram_actions headers'; type = 'main'; index = 0 })) }
  'Seed telegram_actions headers' = [ordered]@{ main = @(@(@{ node = 'Append telegram_actions headers'; type = 'main'; index = 0 })) }
  'Append telegram_actions headers' = [ordered]@{ main = @(@(@{ node = 'Create improvement_log'; type = 'main'; index = 0 })) }
  'Create improvement_log' = [ordered]@{ main = @(@(@{ node = 'Seed improvement_log headers'; type = 'main'; index = 0 })) }
  'Seed improvement_log headers' = [ordered]@{ main = @(@(@{ node = 'Append improvement_log headers'; type = 'main'; index = 0 })) }
  'Append improvement_log headers' = [ordered]@{ main = @(@(@{ node = 'Restore Setup Input'; type = 'main'; index = 0 })) }
}

$updateBody = [ordered]@{
  name        = $workflow.name
  nodes       = $workflow.nodes
  connections = $workflow.connections
  settings    = $workflow.settings
}

Invoke-WebRequest -UseBasicParsing -Method Put -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$setupWorkflowId" -Body ($updateBody | ConvertTo-Json -Depth 100) | Out-Null

try {
  Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
} catch {
  throw "Failed to trigger generator workflow: $($_.Exception.Message)"
}

$latest = $null
for ($i = 0; $i -lt 20; $i++) {
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
  latest_execution_id = $latest.id
  latest_execution_status = $latest.status
  append_content_queue_status = if ($runData.'Append Content Queue') { $runData.'Append Content Queue'[0].executionStatus } else { $null }
  setup_workflow_status = if ($runData.'Run Sheet Setup') { $runData.'Run Sheet Setup'[0].executionStatus } else { $null }
} | ConvertTo-Json -Depth 20
