param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$setupWorkflowId = 'FipYh2cg4CXocUu5'

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

$w = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$setupWorkflowId"

$store = $w.nodes | Where-Object { $_.name -eq 'Store Setup Input' } | Select-Object -First 1
if (-not $store) { throw 'Missing node: Store Setup Input' }
$store.parameters.jsCode = @'
const store = $getWorkflowStaticData('global');
store.pending_content_items = JSON.stringify(items.map((item) => item.json));

const sheetSetupState = store.sheet_setup_done ? 'continue' : 'setup';
return [{ json: { sheet_setup_state: sheetSetupState } }];
'@

$restore = $w.nodes | Where-Object { $_.name -eq 'Restore Setup Input' } | Select-Object -First 1
if (-not $restore) { throw 'Missing node: Restore Setup Input' }
$restore.parameters.jsCode = @'
const store = $getWorkflowStaticData('global');
const pending = JSON.parse(store.pending_content_items || '[]');
store.sheet_setup_done = true;
delete store.pending_content_items;

return pending.map((row) => ({ json: row }));
'@

$w.connections = [ordered]@{}
Set-Conns -Workflow $w -From 'When Executed by Another Workflow' -OutputIndex 0 -Targets @(
  (New-Conn 'Store Setup Input')
)
Set-Conns -Workflow $w -From 'Store Setup Input' -OutputIndex 0 -Targets @(
  (New-Conn 'Switch Setup State')
)
Set-Conns -Workflow $w -From 'Switch Setup State' -OutputIndex 0 -Targets @(
  (New-Conn 'Create content_queue')
)
Set-Conns -Workflow $w -From 'Switch Setup State' -OutputIndex 1 -Targets @(
  (New-Conn 'Restore Setup Input')
)
Set-Conns -Workflow $w -From 'Create content_queue' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed content_queue headers')
)
Set-Conns -Workflow $w -From 'Seed content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append content_queue headers')
)
Set-Conns -Workflow $w -From 'Append content_queue headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create publish_log')
)
Set-Conns -Workflow $w -From 'Create publish_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed publish_log headers')
)
Set-Conns -Workflow $w -From 'Seed publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append publish_log headers')
)
Set-Conns -Workflow $w -From 'Append publish_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create telegram_actions')
)
Set-Conns -Workflow $w -From 'Create telegram_actions' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed telegram_actions headers')
)
Set-Conns -Workflow $w -From 'Seed telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append telegram_actions headers')
)
Set-Conns -Workflow $w -From 'Append telegram_actions headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Create improvement_log')
)
Set-Conns -Workflow $w -From 'Create improvement_log' -OutputIndex 0 -Targets @(
  (New-Conn 'Seed improvement_log headers')
)
Set-Conns -Workflow $w -From 'Seed improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Append improvement_log headers')
)
Set-Conns -Workflow $w -From 'Append improvement_log headers' -OutputIndex 0 -Targets @(
  (New-Conn 'Restore Setup Input')
)

$body = [ordered]@{
  name        = $w.name
  nodes       = $w.nodes
  connections = $w.connections
  settings    = @{}
}

Invoke-RestMethod -Method Put -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$setupWorkflowId" -Body ($body | ConvertTo-Json -Depth 100) | Out-Null
