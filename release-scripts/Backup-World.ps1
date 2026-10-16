$ErrorActionPreference = 'Stop'
if (Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue) { throw 'Stop the server with stop before making a backup.' }
$world = Join-Path $PSScriptRoot 'world'
if (-not (Test-Path -LiteralPath $world)) { throw 'No world yet. Start the server first.' }
$backups = Join-Path $PSScriptRoot 'backups'
New-Item -ItemType Directory -Path $backups -Force | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$target = Join-Path $backups ('world-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip')
[IO.Compression.ZipFile]::CreateFromDirectory($world, $target)
Write-Host ('Backup saved: ' + $target) -ForegroundColor Green
