import re

with open('install.ps1', 'r') as f:
    content = f.read()

backup_func = """
$ToolsDest = Join-Path $ClaudeHome "tools"
$null = New-Item -ItemType Directory -Force -Path $ToolsDest

function Backup-File {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$FilePath.$timestamp.bak"
        Copy-Item $FilePath -Destination $backupPath -Force
        Write-Host "Created backup: $backupPath"
    }
}
"""

content = content.replace('\n$ToolsDest = Join-Path $ClaudeHome "tools"\n$null = New-Item -ItemType Directory -Force -Path $ToolsDest\n', backup_func)

# We can just use replace instead of regex to avoid escape issues
content = content.replace('Copy-Item (Join-Path $ScriptDir "AGENTS.md") $DocsDest -Force', 'Backup-File (Join-Path $DocsDest "AGENTS.md")\n    Copy-Item (Join-Path $ScriptDir "AGENTS.md") $DocsDest -Force')
content = content.replace('Copy-Item (Join-Path $ScriptDir "SOUL.md") $DocsDest -Force', 'Backup-File (Join-Path $DocsDest "SOUL.md")\n    Copy-Item (Join-Path $ScriptDir "SOUL.md") $DocsDest -Force')
content = content.replace('Copy-Item (Join-Path $ScriptDir "CLAUDE.md") $ClaudeHome -Force', 'Backup-File (Join-Path $ClaudeHome "CLAUDE.md")\n    Copy-Item (Join-Path $ScriptDir "CLAUDE.md") $ClaudeHome -Force')

content = content.replace('Copy-Item (Join-Path $ScriptDir "config\models.json") $ConfigDest -Force', 'Backup-File (Join-Path $ConfigDest "models.json")\n    Copy-Item (Join-Path $ScriptDir "config\models.json") $ConfigDest -Force')
content = content.replace('Copy-Item (Join-Path $ScriptDir "config\stacks.json") $ConfigDest -Force', 'Backup-File (Join-Path $ConfigDest "stacks.json")\n    Copy-Item (Join-Path $ScriptDir "config\stacks.json") $ConfigDest -Force')

content = content.replace('Copy-Item (Join-Path $ScriptDir "tools\vex_skill_gen.py") $ToolsDest -Force', 'Backup-File (Join-Path $ToolsDest "vex_skill_gen.py")\n    Copy-Item (Join-Path $ScriptDir "tools\vex_skill_gen.py") $ToolsDest -Force')
content = content.replace('Copy-Item (Join-Path $ScriptDir "tools\vex_cost.py") $ToolsDest -Force', 'Backup-File (Join-Path $ToolsDest "vex_cost.py")\n    Copy-Item (Join-Path $ScriptDir "tools\vex_cost.py") $ToolsDest -Force')
content = content.replace('Copy-Item (Join-Path $ScriptDir "tools\vex_memory.py") $ToolsDest -Force', 'Backup-File (Join-Path $ToolsDest "vex_memory.py")\n    Copy-Item (Join-Path $ScriptDir "tools\vex_memory.py") $ToolsDest -Force')

with open('install.ps1', 'w') as f:
    f.write(content)
print("install.ps1 updated")
