$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$vpn = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like '*Radmin*' -and $_.IPAddress -like '26.*' } | Select-Object -First 1
if (-not $vpn) { throw 'Enable Radmin VPN first. No Radmin IPv4 address found.' }
if (Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 25565 is already in use. Stop the other server first.' }
$properties = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'server.properties'))
$properties = [regex]::Replace($properties, '(?m)^server-ip=.*$', 'server-ip=' + $vpn.IPAddress)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'server.properties'), $properties, [Text.Encoding]::ASCII)
Write-Host ('Friends connect to: ' + $vpn.IPAddress + ':25565') -ForegroundColor Green
Write-Host 'Wait for Done. To save and stop, type: stop'
& (Join-Path $PSScriptRoot 'runtime/java21/bin/java.exe') '@user_jvm_args.txt' '@libraries/net/neoforged/neoforge/21.1.259/win_args.txt' 'nogui'
