import re

with open('install.sh', 'r') as f:
    content = f.read()

# Add backup function
backup_func = """
# Setup tools directory
TOOLS_DEST="$HOME/.claude/tools"
mkdir -p "$TOOLS_DEST"

# Backup helper
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        cp "$file" "${file}.${timestamp}.bak"
        echo "Created backup: ${file}.${timestamp}.bak"
    fi
}
"""

content = content.replace('\n# Setup tools directory\nTOOLS_DEST="$HOME/.claude/tools"\nmkdir -p "$TOOLS_DEST"\n', backup_func)

# Add backups before cp
content = content.replace('cp "$SCRIPT_DIR/tools/vex_skill_gen.py" "$TOOLS_DEST/"', 'backup_file "$TOOLS_DEST/vex_skill_gen.py"\n    cp "$SCRIPT_DIR/tools/vex_skill_gen.py" "$TOOLS_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/tools/vex_cost.py" "$TOOLS_DEST/"', 'backup_file "$TOOLS_DEST/vex_cost.py"\n    cp "$SCRIPT_DIR/tools/vex_cost.py" "$TOOLS_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/tools/vex_memory.py" "$TOOLS_DEST/"', 'backup_file "$TOOLS_DEST/vex_memory.py"\n    cp "$SCRIPT_DIR/tools/vex_memory.py" "$TOOLS_DEST/"')

# Handle AGENTS.md, SOUL.md etc 
content = content.replace('cp "$SCRIPT_DIR/AGENTS.md" "$DOCS_DEST/"', 'backup_file "$DOCS_DEST/AGENTS.md"\ncp "$SCRIPT_DIR/AGENTS.md" "$DOCS_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/SOUL.md" "$DOCS_DEST/"', 'backup_file "$DOCS_DEST/SOUL.md"\ncp "$SCRIPT_DIR/SOUL.md" "$DOCS_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DEST/"', 'backup_file "$CLAUDE_DEST/CLAUDE.md"\ncp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/config/models.json" "$CONFIG_DEST/"', 'backup_file "$CONFIG_DEST/models.json"\ncp "$SCRIPT_DIR/config/models.json" "$CONFIG_DEST/"')
content = content.replace('cp "$SCRIPT_DIR/config/stacks.json" "$CONFIG_DEST/"', 'backup_file "$CONFIG_DEST/stacks.json"\ncp "$SCRIPT_DIR/config/stacks.json" "$CONFIG_DEST/"')

with open('install.sh', 'w') as f:
    f.write(content)
print("install.sh updated")
