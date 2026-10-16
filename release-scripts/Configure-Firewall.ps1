$ErrorActionPreference = 'Stop'
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $PSCommandPath + '"'
    $process = Start-Process powershell.exe -Verb RunAs -WindowStyle Hidden -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw 'Firewall setup failed. Run this file as administrator.' }
    Write-Host 'Radmin firewall rule configured.' -ForegroundColor Green
    exit
}
$vpn = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like '*Radmin*' -and $_.IPAddress -like '26.*' } | Select-Object -First 1
if (-not $vpn) { throw 'Enable Radmin VPN first.' }
$name = 'ArcaneIndustry-Radmin-25565'
Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -Name $name -DisplayName 'Arcane Industry - Radmin VPN only' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 25565 -LocalAddress $vpn.IPAddress -RemoteAddress 26.0.0.0/8 -InterfaceAlias $vpn.InterfaceAlias -Profile Any | Out-Null
