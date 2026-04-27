param()

$ErrorActionPreference = 'Stop'

$sshKey = 'C:\Users\minho\Downloads\n8n-key.pem'
$remoteHost = 'ubuntu@43.201.227.194'

function Invoke-Ssh {
  param([string]$Command)
  ssh -i $sshKey $remoteHost $Command
}

Write-Host 'BETTER-SQLITE3'
Invoke-Ssh 'docker exec n8n node -e "try { console.log(require.resolve(\"better-sqlite3\")) } catch (e) { console.error(\"ERR\", e.message); process.exit(1) }"'
