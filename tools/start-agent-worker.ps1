# Start Cursor My Machines worker in a hidden background process.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\start-agent-worker.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\start-agent-worker.ps1 -Force

param(
    [string]$WorkerName = 'cgtw-win',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$AgentDir = Join-Path $env:LOCALAPPDATA 'cursor-agent'
$AgentPs1 = Join-Path $AgentDir 'agent.ps1'
$AgentCmd = Join-Path $AgentDir 'agent.cmd'
$LogDir = Join-Path $Root 'Log'
$LogFile = Join-Path $LogDir 'agent-worker.log'
$PidFile = Join-Path $LogDir 'agent-worker.pid'

function Write-Log([string]$Message) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    if (-not (Test-Path -LiteralPath $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

function Get-AgentLauncher() {
    if (Test-Path -LiteralPath $AgentCmd) { return $AgentCmd }
    if (Test-Path -LiteralPath $AgentPs1) { return $AgentPs1 }
    throw "Cursor agent CLI not found. Run: irm 'https://cursor.com/install?win32=true' | iex"
}

function Test-WorkerRunning() {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $false }
    $pidText = (Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if (-not $pidText) { return $false }
    $proc = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
    if (-not $proc) { return $false }
    return $true
}

if ((Test-WorkerRunning) -and -not $Force) {
    $existingPid = Get-Content -LiteralPath $PidFile | Select-Object -First 1
    Write-Log "Worker already running (pid=$existingPid). Use -Force to restart."
    exit 0
}

if ($Force -and (Test-Path -LiteralPath $PidFile)) {
    $oldPid = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($oldPid) {
        Stop-Process -Id ([int]$oldPid) -Force -ErrorAction SilentlyContinue
        Write-Log "Stopped previous worker pid=$oldPid"
    }
}

$launcher = Get-AgentLauncher
$workerArgs = "worker start --name `"$WorkerName`" --worker-dir `"$Root`""
$inner = "& '$launcher' $workerArgs *>> '$LogFile'"

Write-Log "Starting worker name=$WorkerName dir=$Root"
$proc = Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -PassThru -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-Command', $inner
)

Set-Content -LiteralPath $PidFile -Value $proc.Id -Encoding ASCII
Write-Log "Worker launcher started (pid=$($proc.Id)). Log: $LogFile"
Write-Log "Use https://cursor.com/agents and select machine: $WorkerName"
