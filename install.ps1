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
$SkillsDest = Join-Path $ProfileDir "skills"

function Write-Info { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Cyan }
function Write-Ok   { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Green }
function Write-Warn { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Yellow }
function Write-Err  { param($Msg) Write-Host "[vex] $Msg" -ForegroundColor Red }

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

function Install-VexTools {
    Write-Info "Installing VEX tools..."
    Write-Info "  Profile:    $Profile"
    Write-Info "  VEX Home:   $VexHome"
    Write-Info "  Source:     $ScriptDir"

    if ($DryRun) {
        Write-Warn "DRY RUN - no changes will be made"
        ""
        "Would create directories:"
        "  $ToolsDest"
        "  $ConfigDest"
        "  $SkillsDest"
        ""
        "Would copy:"
        "  tools/vex-skill-gen.py -> $ToolsDest/"
        "  tools/vex-cost.py      -> $ToolsDest/"
        "  tools/vex-memory.py    -> $ToolsDest/"
        "  config/stacks.json     -> $ConfigDest/"
        "  config/models.json     -> $ConfigDest/"
        ""
        "Would add to PATH:"
        "  $ToolsDest"
        ""
        "Would create batch wrappers:"
        "  $ToolsDest/vex-skill-gen.cmd"
        "  $ToolsDest/vex-cost.cmd"
        "  $ToolsDest/vex-memory.cmd"
        return
    }

    # Create directories
    New-Item -ItemType Directory -Force -Path $ToolsDest | Out-Null
    New-Item -ItemType Directory -Force -Path $ConfigDest | Out-Null
    New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null

    # Copy tools
    Copy-Item (Join-Path $ScriptDir "tools\vex-skill-gen.py") $ToolsDest -Force
    Copy-Item (Join-Path $ScriptDir "tools\vex-cost.py") $ToolsDest -Force
    Copy-Item (Join-Path $ScriptDir "tools\vex-memory.py") $ToolsDest -Force

    # Copy config
    Copy-Item (Join-Path $ScriptDir "config\stacks.json") $ConfigDest -Force
    Copy-Item (Join-Path $ScriptDir "config\models.json") $ConfigDest -Force

    # Create batch wrapper scripts
    $tools = @("vex-skill-gen", "vex-cost", "vex-memory")
    foreach ($tool in $tools) {
        $cmdPath = Join-Path $ToolsDest "$tool.cmd"
        $pyFile = Join-Path $ToolsDest "$tool.py"
        @"
@echo off
python "$pyFile" %*
"@ | Set-Content -Path $cmdPath -Encoding ASCII

        # Also create PowerShell wrapper
        $ps1Path = Join-Path $ToolsDest "$tool.ps1"
        @"
#!/usr/bin/env pwsh
python "$pyFile" @args
"@ | Set-Content -Path $ps1Path -Encoding UTF8
    }

    # Add to user PATH if not already present
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$ToolsDest*") {
        $newPath = "$ToolsDest;$currentPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$ToolsDest;$env:Path"
        Write-Ok "Added $ToolsDest to user PATH"
    } else {
        Write-Info "PATH already includes $ToolsDest"
    }

    # Set VEX_HOME environment variable
    $currentVexHome = [Environment]::GetEnvironmentVariable("VEX_HOME", "User")
    if (-not $currentVexHome) {
        [Environment]::SetEnvironmentVariable("VEX_HOME", $VexHome, "User")
        $env:VEX_HOME = $VexHome
        Write-Ok "Set VEX_HOME environment variable"
    }

    ""
    Write-Ok "Installation complete!"
    ""
    "  Tools:     $ToolsDest"
    "  Config:    $ConfigDest"
    "  Profile:   $Profile"
    ""
    "  Quick start (restart terminal first):"
    "    vex-skill-gen scan          # Scan sessions for patterns"
    "    vex-cost report             # View cost report"
    "    vex-memory scan             # Build knowledge graph"
    "    vex-cost models             # View model pricing"
    ""
    "  Or run directly:"
    "    python $ToolsDest\vex-skill-gen.py scan"
}

function Uninstall-VexTools {
    Write-Info "Uninstalling VEX tools..."

    if ($DryRun) {
        Write-Warn "DRY RUN - no changes will be made"
        ""
        "Would remove:"
        "  $ToolsDest"
        "  (config and data in $VexHome preserved)"
        return
    }

    if (Test-Path $ToolsDest) {
        Remove-Item -Recurse -Force $ToolsDest
        Write-Ok "Removed $ToolsDest"
    } else {
        Write-Warn "Tools directory not found: $ToolsDest"
    }

    # Remove from PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -like "*$ToolsDest*") {
        $newPath = ($currentPath -split ";" | Where-Object { $_ -ne $ToolsDest }) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Ok "Removed $ToolsDest from PATH"
    }

    Write-Info "Preserved data directory: $VexHome"
    Write-Info "To fully remove: Remove-Item -Recurse -Force $VexHome"

    ""
    Write-Ok "Uninstallation complete."
}

# Main
if ($Uninstall) {
    Uninstall-VexTools
} else {
    Install-VexTools
}
