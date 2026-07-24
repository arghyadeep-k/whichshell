# Install whichshell onto PATH (Windows).
#
# Usage:
#   irm https://raw.githubusercontent.com/arghyadeep-k/whichshell/main/install.ps1 | iex
# or, from a local checkout:
#   .\install.ps1

$ErrorActionPreference = "Stop"

$RepoRaw = "https://raw.githubusercontent.com/arghyadeep-k/whichshell/main"
$DestDir = if ($env:WHICHSHELL_INSTALL_DIR) { $env:WHICHSHELL_INSTALL_DIR } else { Join-Path $env:USERPROFILE "bin" }

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

$LocalSource = Join-Path $PSScriptRoot "whichshell"
if ($PSScriptRoot -and (Test-Path $LocalSource)) {
    Copy-Item -Path $LocalSource -Destination (Join-Path $DestDir "whichshell.py") -Force
} else {
    Invoke-WebRequest -Uri "$RepoRaw/whichshell" -OutFile (Join-Path $DestDir "whichshell.py")
}

$ShimPath = Join-Path $DestDir "whichshell.cmd"
Set-Content -Path $ShimPath -Value "@echo off`r`npython `"%~dp0whichshell.py`" %*" -Encoding ASCII

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Warning "python was not found on PATH; whichshell requires Python 3 to run."
}

Write-Host "Installed whichshell to $DestDir"

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($UserPath -split ";") -notcontains $DestDir) {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$DestDir", "User")
    $env:Path = "$env:Path;$DestDir"
    Write-Host "Added $DestDir to your User PATH. Open a new terminal, then run: whichshell"
} else {
    Write-Host "Run: whichshell"
}
