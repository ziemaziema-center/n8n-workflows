param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$workflowId = 'rTEHwsKpV3ClVlBU'

function New-Conn {
  param([string]$Target)
  @{ node = $Target; type = 'main'; index = 0 }
}

$w = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$workflowId"

$w.connections = [ordered]@{
  'Setup Webhook' = @{ main = @(@(New-Conn 'Create content_queue')) }
  'Create content_queue' = @{ main = @(@(New-Conn 'Seed content_queue headers')) }
  'Seed content_queue headers' = @{ main = @(@(New-Conn 'Append content_queue headers')) }
  'Append content_queue headers' = @{ main = @(@(New-Conn 'Create publish_log')) }
  'Create publish_log' = @{ main = @(@(New-Conn 'Seed publish_log headers')) }
  'Seed publish_log headers' = @{ main = @(@(New-Conn 'Append publish_log headers')) }
  'Append publish_log headers' = @{ main = @(@(New-Conn 'Create telegram_actions')) }
  'Create telegram_actions' = @{ main = @(@(New-Conn 'Seed telegram_actions headers')) }
  'Seed telegram_actions headers' = @{ main = @(@(New-Conn 'Append telegram_actions headers')) }
  'Append telegram_actions headers' = @{ main = @(@(New-Conn 'Create improvement_log')) }
  'Create improvement_log' = @{ main = @(@(New-Conn 'Seed improvement_log headers')) }
  'Seed improvement_log headers' = @{ main = @(@(New-Conn 'Append improvement_log headers')) }
}

$body = [ordered]@{
  name        = $w.name
  nodes       = $w.nodes
  connections = $w.connections
  settings    = @{}
}

Invoke-RestMethod -Method Put -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$workflowId" -Body ($body | ConvertTo-Json -Depth 100) | Out-Null
