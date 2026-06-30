$ErrorActionPreference = 'SilentlyContinue'
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

$loop = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoProfile', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass',
    '-File', (Join-Path $Root 'AutoYesLoop.ps1')
) -PassThru

Start-Sleep -Milliseconds 800

$le = 'D:\CGOLD\Locale.Emulator\LEProc.exe'
$guid = '4b489d63-4a01-481f-8af0-f499c2dc8fc1'
$exe = Join-Path $Root 'cg2d.exe'
$args = @(
    '-runas', $guid, $exe,
    'updated', '3Ddevice:4', 'windowmode', '/width:800', '/height:600', 'musicon', 'soundon',
    'IP:0:149.104.11.130:9030'
)

Start-Process -FilePath $le -ArgumentList $args -WorkingDirectory $Root | Out-Null

if ($loop) {
    Wait-Process -Id $loop.Id -Timeout 50 -ErrorAction SilentlyContinue
    Stop-Process -Id $loop.Id -Force -ErrorAction SilentlyContinue
}
