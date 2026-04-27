param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$workflowId = 'DGMQEgFXqzeS3sJ5'

$w = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$workflowId"
$node = $w.nodes | Where-Object { $_.name -eq 'Run Sheet Setup' } | Select-Object -First 1
if (-not $node) { throw 'Run Sheet Setup node not found' }

$node.parameters | Add-Member -MemberType NoteProperty -Name mode -Value 'all' -Force
$node.parameters.options = @{ waitForSubWorkflow = $true }

$body = [ordered]@{
  name        = $w.name
  nodes       = $w.nodes
  connections = $w.connections
  settings    = @{}
}

Invoke-RestMethod -Method Put -Headers $headers -ContentType 'application/json' -Uri "$baseUrl/workflows/$workflowId" -Body ($body | ConvertTo-Json -Depth 100) | Out-Null

Invoke-WebRequest -Method Post -Uri 'http://43.201.227.194:5678/webhook/factory-run-now' -ContentType 'application/json' -Body '{}' | Out-Null
