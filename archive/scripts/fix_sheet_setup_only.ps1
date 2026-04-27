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

function Get-Workflow {
  param([string]$Id)
  Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$Id"
}

function Put-Workflow {
  param([object]$Workflow)
  $body = [ordered]@{
    name        = $Workflow.name
    nodes       = $Workflow.nodes
    connections = $Workflow.connections
    settings    = $Workflow.settings
  }
  Invoke-RestMethod -Method Put -Uri "$baseUrl/workflows/$($Workflow.id)" -Headers $headers -ContentType 'application/json' -Body ($body | ConvertTo-Json -Depth 100)
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

function Get-ExecutionByWorkflow {
  param([string]$WorkflowId)
  Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions?workflowId=$WorkflowId&limit=5&includeData=true"
}

$setup = Get-Workflow -Id $setupWorkflowId

$setup.connections = [ordered]@{}
Set-Conns -Workflow $setup -From 'When Executed by Another Workflow' -OutputIndex 0 -Targets @(
  (New-Conn 'Store Setup Input')
)
Set-Conns -Workflow $setup -From 'Store Setup Input' -OutputIndex 0 -Targets @(
  (New-Conn 'Create content_queue')
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

$updatedSetup = Put-Workflow -Workflow $setup

Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null

$latest = $null
for ($i = 0; $i -lt 18; $i++) {
  Start-Sleep -Seconds 5
  $execs = Get-ExecutionByWorkflow -WorkflowId $generatorWorkflowId
  $latest = $execs.data | Sort-Object id -Descending | Select-Object -First 1
  if ($latest.status -in @('success','error','crashed','canceled')) { break }
}

$generatorRun = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions/$($latest.id)?includeData=true"
$runData = $generatorRun.data.resultData.runData

$setupExecs = Get-ExecutionByWorkflow -WorkflowId $setupWorkflowId
$latestSetup = $setupExecs.data | Sort-Object id -Descending | Select-Object -First 1
$setupRun = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/executions/$($latestSetup.id)?includeData=true"
$setupData = $setupRun.data.resultData.runData

[pscustomobject]@{
  setup_workflow_name = $updatedSetup.name
  setup_execution_status = $latestSetup.status
  generator_execution_id = $latest.id
  generator_execution_status = $latest.status
  content_queue_exists = if ($setupData.'Create content_queue') { $true } else { $false }
  content_queue_headers = if ($setupData.'Append content_queue headers') { $setupData.'Append content_queue headers'[0].executionStatus } else { $null }
  publish_log_exists = if ($setupData.'Create publish_log') { $true } else { $false }
  publish_log_headers = if ($setupData.'Append publish_log headers') { $setupData.'Append publish_log headers'[0].executionStatus } else { $null }
  telegram_actions_exists = if ($setupData.'Create telegram_actions') { $true } else { $false }
  telegram_actions_headers = if ($setupData.'Append telegram_actions headers') { $setupData.'Append telegram_actions headers'[0].executionStatus } else { $null }
  improvement_log_exists = if ($setupData.'Create improvement_log') { $true } else { $false }
  improvement_log_headers = if ($setupData.'Append improvement_log headers') { $setupData.'Append improvement_log headers'[0].executionStatus } else { $null }
  append_content_queue_status = if ($runData.'Append Content Queue') { $runData.'Append Content Queue'[0].executionStatus } else { $null }
} | ConvertTo-Json -Depth 20
