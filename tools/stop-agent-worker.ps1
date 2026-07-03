# Stop hidden Cursor My Machines worker started by start-agent-worker.ps1
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\stop-agent-worker.ps1

$ErrorActionPreference = 'SilentlyContinue'
$Root = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $Root 'Log\agent-worker.pid'

if (-not (Test-Path -LiteralPath $PidFile)) {
    Write-Host 'No pid file found. Worker may not be running.'
    exit 0
}

$pidText = Get-Content -LiteralPath $PidFile | Select-Object -First 1
if ($pidText) {
    Stop-Process -Id ([int]$pidText) -Force
    Write-Host "Stopped worker launcher pid=$pidText"
}

# Also stop child agent processes if still alive.
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match 'cursor-agent\\agent\.(ps1|cmd)|agent worker start' } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force
        Write-Host "Stopped pid=$($_.ProcessId)"
    }

Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
Write-Host 'Done.'
