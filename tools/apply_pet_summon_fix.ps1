# Apply petSummonContract fixes + restore vanilla AOE magic, then restart cgmsv.
# Run from D:\cgtw (PowerShell):
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\apply_pet_summon_fix.ps1

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$FixDropPy = Join-Path $Root 'tools\fix_pet_summon_contract_drop.py'
$FixMagicPy = Join-Path $Root 'tools\fix_restore_vanilla_aoe_magic.py'

$LuaCandidates = @(
    'C:\cgmsv_26.5c\gmsv\lua\modules\petSummonContract.lua',
    'D:\cgmsv_26.5c\gmsv\lua\modules\petSummonContract.lua',
    (Join-Path $Root 'server_mirror\lua\modules\petSummonContract.lua')
)

$LuaPath = $null
foreach ($p in $LuaCandidates) {
    if (Test-Path -LiteralPath $p) {
        $LuaPath = $p
        break
    }
}
if (-not $LuaPath) {
    Write-Error "petSummonContract.lua not found. Checked:`n$($LuaCandidates -join "`n")"
}

Write-Host "Patching: $LuaPath"
& python $FixPy --lua $LuaPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# --- restart cgmsv ---
$GmsvRoots = @('C:\cgmsv_26.5c', 'D:\cgmsv_26.5c')
$GmsvRoot = $GmsvRoots | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $GmsvRoot) {
    Write-Warning "cgmsv root not found; patch applied but server not restarted."
    exit 0
}

Write-Host "Stopping cgmsv processes..."
Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match 'gmsv' } |
    ForEach-Object {
        Write-Host "  stop $($_.ProcessName) pid=$($_.Id)"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

$ExeCandidates = @(
    (Join-Path $GmsvRoot 'gmsv.exe'),
    (Join-Path $GmsvRoot 'gmsv\gmsv.exe'),
    (Join-Path $GmsvRoot 'gmsv\GMSV.exe')
)
$Exe = $ExeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Exe) {
  $Exe = Get-ChildItem -Path $GmsvRoot -Filter 'gmsv*.exe' -Recurse -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
}
if (-not $Exe) {
    Write-Warning "gmsv.exe not found under $GmsvRoot; patch applied, please restart cgmsv manually."
    exit 0
}

$Wd = Split-Path -Parent $Exe
Write-Host "Starting: $Exe (cwd=$Wd)"
Start-Process -FilePath $Exe -WorkingDirectory $Wd
Write-Host "Done. Test monster drop + summon card tooltip in game."
