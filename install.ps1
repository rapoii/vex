# VEX Tools Installer — Windows (PowerShell)
# Usage: .\install.ps1 [-Profile NAME] [-DryRun] [-Uninstall]

param(
    [string]$Profile = "default",
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VexHome = if ($env:VEX_HOME) { $env:VEX_HOME } else { Join-Path $env:USERPROFILE ".vex" }
$ProfileDir = Join-Path $env:USERPROFILE ".hermes\profiles\$Profile"
$ToolsDest = Join-Path $VexHome "tools"
$ConfigDest = Join-Path $VexHome "config"
$AdaptersDest = Join-Path $VexHome "adapters"
$MarketplaceDest = Join-Path $VexHome "marketplace"
$SkillsDest = Join-Path $ProfileDir "skills"
$Tools = @(
    "vex.py",
    "vex_skill_gen.py",
    "vex_cost.py",
    "vex_memory.py",
    "vex_sessions.py",
    "vex_security.py",
    "vex_instinct.py",
    "vex_hooks.py",
    "vex_optimize.py"
)

function Write-Info { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Cyan }
function Write-Ok   { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Green }
function Write-Warn { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Yellow }
function Write-Err  { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Red }

function Backup-File {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        Copy-Item -LiteralPath $Path -Destination "$Path.bak" -Force
    }
}

if ($Help) {
    @"

VEX Tools Installer

Usage:
  .\install.ps1 [OPTIONS]

Options:
  -Profile NAME    Install for specific profile (default: default)
  -DryRun          Show what would be done without making changes
  -Uninstall       Remove VEX tools
  -Help            Show this help message

Environment:
  `$env:VEX_HOME    VEX home directory (default: ~\.vex)

"@ | Write-Host
    exit 0
}

function Write-DryRunInstall {
    Write-Warn "DRY RUN - no changes will be made"
    ""
    "Would create directories:"
    "  $ToolsDest"
    "  $ConfigDest"
    "  $AdaptersDest"
    "  $MarketplaceDest"
    "  $SkillsDest"
    ""
    "Would copy tools:"
    foreach ($Tool in $Tools) {
        "  tools/$Tool -> $ToolsDest/"
    }
    ""
    "Would copy directories:"
    "  config/      -> $ConfigDest/"
    "  adapters/    -> $AdaptersDest/"
    "  marketplace/ -> $MarketplaceDest/"
    ""
    "Would add to PATH:"
    "  $ToolsDest"
    ""
    "Would create wrappers:"
    foreach ($Tool in $Tools) {
        $Name = [IO.Path]::GetFileNameWithoutExtension($Tool)
        "  $ToolsDest\$Name.cmd"
        "  $ToolsDest\$Name.ps1"
    }
}

function Copy-DirectoryContents {
    param(
        [string]$Source,
        [string]$Destination
    )
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

function New-ToolWrapper {
    param([string]$Name)
    $CmdPath = Join-Path $ToolsDest "$Name.cmd"
    $Ps1Path = Join-Path $ToolsDest "$Name.ps1"
    $PyFile = Join-Path $ToolsDest "$Name.py"

    @"
@echo off
python "$PyFile" %*
"@ | Set-Content -Path $CmdPath -Encoding ASCII

    @"
#!/usr/bin/env pwsh
python "$PyFile" @args
"@ | Set-Content -Path $Ps1Path -Encoding UTF8
}

function Install-VexTools {
    Write-Info "Installing VEX tools..."
    Write-Info "  Profile:    $Profile"
    Write-Info "  VEX Home:   $VexHome"
    Write-Info "  Source:     $ScriptDir"

    if ($DryRun) {
        Write-DryRunInstall
        return
    }

    New-Item -ItemType Directory -Force -Path $ToolsDest | Out-Null
    New-Item -ItemType Directory -Force -Path $ConfigDest | Out-Null
    New-Item -ItemType Directory -Force -Path $AdaptersDest | Out-Null
    New-Item -ItemType Directory -Force -Path $MarketplaceDest | Out-Null
    New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null

    foreach ($Tool in $Tools) {
        Backup-File (Join-Path $ToolsDest $Tool)
        Copy-Item (Join-Path $ScriptDir "tools\$Tool") $ToolsDest -Force
    }

    Copy-DirectoryContents (Join-Path $ScriptDir "config") $ConfigDest
    Copy-DirectoryContents (Join-Path $ScriptDir "adapters") $AdaptersDest
    Copy-DirectoryContents (Join-Path $ScriptDir "marketplace") $MarketplaceDest

    foreach ($Tool in $Tools) {
        New-ToolWrapper ([IO.Path]::GetFileNameWithoutExtension($Tool))
    }

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$ToolsDest*") {
        $newPath = "$ToolsDest;$currentPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$ToolsDest;$env:Path"
        Write-Ok "Added $ToolsDest to user PATH"
    } else {
        Write-Info "PATH already includes $ToolsDest"
    }

    $currentVexHome = [Environment]::GetEnvironmentVariable("VEX_HOME", "User")
    if (-not $currentVexHome) {
        [Environment]::SetEnvironmentVariable("VEX_HOME", $VexHome, "User")
        $env:VEX_HOME = $VexHome
        Write-Ok "Set VEX_HOME environment variable"
    }

    ""
    Write-Ok "Installation complete!"
    ""
    "  Tools:       $ToolsDest"
    "  Config:      $ConfigDest"
    "  Adapters:    $AdaptersDest"
    "  Marketplace: $MarketplaceDest"
    "  Profile:     $Profile"
    ""
    "  Quick start (restart terminal first):"
    "    vex --help"
    "    vex_cost report"
    "    vex_memory scan"
    ""
    "  Or run directly:"
    "    python $ToolsDest\vex.py --help"
}

function Uninstall-VexTools {
    Write-Info "Uninstalling VEX tools..."

    if ($DryRun) {
        Write-Warn "DRY RUN - no changes will be made"
        ""
        "Would remove:"
        "  $ToolsDest"
        "  $AdaptersDest"
        "  $MarketplaceDest"
        "  (config and data in $VexHome preserved)"
        return
    }

    foreach ($Path in @($ToolsDest, $AdaptersDest, $MarketplaceDest)) {
        if (Test-Path $Path) {
            Remove-Item -Recurse -Force $Path -Confirm:$false
            Write-Ok "Removed $Path"
        } else {
            Write-Warn "Directory not found: $Path"
        }
    }

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -like "*$ToolsDest*") {
        $newPath = ($currentPath -split ";" | Where-Object { $_ -ne $ToolsDest }) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Ok "Removed $ToolsDest from PATH"
    }

    Write-Info "Preserved config and data directory: $VexHome"
    Write-Info "To fully remove: Remove-Item -Recurse -Force $VexHome"

    ""
    Write-Ok "Uninstallation complete."
}

if ($Uninstall) {
    Uninstall-VexTools
} else {
    Install-VexTools
}
