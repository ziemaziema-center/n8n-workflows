param()

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiLine = (Get-Content (Join-Path $root 'build_queue_system.ps1') | Select-String -SimpleMatch '[string]$ApiKey = "').Line
$apiKey = (($apiLine -replace '.*= "','') -replace '"$','').Trim()

$headers = @{ 'X-N8N-API-KEY' = $apiKey }
$baseUrl = 'http://43.201.227.194:5678/api/v1'
$workflowId = 'DGMQEgFXqzeS3sJ5'

$w = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/workflows/$workflowId"

$selected = $w.nodes | Where-Object { $_.name -in @('Run Sheet Setup','Append Content Queue','Normalize Content Unit','Generate Cover Image','Merge Cover') } | Select-Object name,type,typeVersion,parameters
$selected | ConvertTo-Json -Depth 20
