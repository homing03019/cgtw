# Register Windows Task Scheduler job: auto-start Cursor worker at user logon (hidden).
# Run once as the interactive user (double-click or elevated PowerShell):
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-agent-worker-task.ps1
#
# Remove task:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-agent-worker-task.ps1 -Uninstall

param(
    [string]$TaskName = 'CursorAgent-cgtw-win',
    [string]$WorkerName = 'cgtw-win',
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot 'start-agent-worker.ps1'

if (-not (Test-Path -LiteralPath $StartScript)) {
    throw "Missing $StartScript"
}

if ($Uninstall) {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task: $TaskName"
    } else {
        Write-Host "Task not found: $TaskName"
    }
    exit 0
}

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`" -WorkerName `"$WorkerName`"" `
    -WorkingDirectory $Root

# At logon for current user; allow ~30s after login for network/desktop readiness.
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Auto-start Cursor My Machines worker ($WorkerName) for D:\cgtw at user logon." `
    -Force | Out-Null

Write-Host "Installed scheduled task: $TaskName"
Write-Host "  Trigger : At logon ($env:USERNAME)"
Write-Host "  Script  : $StartScript"
Write-Host "  Worker  : $WorkerName"
Write-Host ""
Write-Host "Test now (hidden background):"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$StartScript`""
Write-Host ""
Write-Host "Uninstall:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Uninstall"
