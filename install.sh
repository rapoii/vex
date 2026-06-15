#!/usr/bin/env bash
# VEX Tools Installer — Unix/macOS
# Usage: bash install.sh [--profile NAME] [--dry-run] [--uninstall]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VEX_HOME="${VEX_HOME:-$HOME/.vex}"
PROFILE="${PROFILE:-default}"
DRY_RUN=false
UNINSTALL=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[vex]${NC} $*"; }
ok()    { echo -e "${GREEN}[vex]${NC} $*"; }
warn()  { echo -e "${YELLOW}[vex]${NC} $*"; }
err()   { echo -e "${RED}[vex]${NC} $*" >&2; }

usage() {
    cat <<EOF
VEX Tools Installer

Usage:
  bash install.sh [OPTIONS]

Options:
  --profile NAME    Install for specific profile (default: default)
  --dry-run         Show what would be done without making changes
  --uninstall       Remove VEX tools
  --help            Show this help message

Environment:
  VEX_HOME          VEX home directory (default: ~/.vex)
EOF
    exit 0
}

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)  PROFILE="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        --help)     usage ;;
        *)          err "Unknown option: $1"; exit 1 ;;
    esac
done

PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
TOOLS_DEST="$VEX_HOME/tools"
CONFIG_DEST="$VEX_HOME/config"
SKILLS_DEST="$PROFILE_DIR/skills"

do_install() {
    info "Installing VEX tools..."
    info "  Profile:    $PROFILE"
    info "  VEX Home:   $VEX_HOME"
    info "  Source:     $SCRIPT_DIR"

    if $DRY_RUN; then
        warn "DRY RUN — no changes will be made"
        echo ""
        echo "Would create directories:"
        echo "  $TOOLS_DEST"
        echo "  $CONFIG_DEST"
        echo "  $SKILLS_DEST"
        echo ""
        echo "Would copy:"
        echo "  tools/vex_skill_gen.py -> $TOOLS_DEST/"
        echo "  tools/vex_cost.py      -> $TOOLS_DEST/"
        echo "  tools/vex_memory.py    -> $TOOLS_DEST/"
        echo "  config/stacks.json     -> $CONFIG_DEST/"
        echo "  config/models.json     -> $CONFIG_DEST/"
        echo ""
        echo "Would add to PATH:"
        echo "  $TOOLS_DEST"
        echo ""
        echo "Would create wrapper scripts at:"
        echo "  $TOOLS_DEST/vex_skill_gen"
        echo "  $TOOLS_DEST/vex_cost"
        echo "  $TOOLS_DEST/vex_memory"
        return 0
    fi

    # Create directories
    mkdir -p "$TOOLS_DEST" "$CONFIG_DEST" "$SKILLS_DEST"

    # Copy tools
    backup_file "$TOOLS_DEST/vex_skill_gen.py"
    cp "$SCRIPT_DIR/tools/vex_skill_gen.py" "$TOOLS_DEST/"
    backup_file "$TOOLS_DEST/vex_cost.py"
    cp "$SCRIPT_DIR/tools/vex_cost.py" "$TOOLS_DEST/"
    backup_file "$TOOLS_DEST/vex_memory.py"
    cp "$SCRIPT_DIR/tools/vex_memory.py" "$TOOLS_DEST/"

    # Copy config
    backup_file "$CONFIG_DEST/stacks.json"
cp "$SCRIPT_DIR/config/stacks.json" "$CONFIG_DEST/"
    backup_file "$CONFIG_DEST/models.json"
cp "$SCRIPT_DIR/config/models.json" "$CONFIG_DEST/"

    # Create wrapper scripts
    for tool in vex_skill_gen vex_cost vex_memory; do
        cat > "$TOOLS_DEST/$tool" <<WRAPPER
#!/usr/bin/env bash
exec python3 "$TOOLS_DEST/${tool}.py" "\$@"
WRAPPER
        chmod +x "$TOOLS_DEST/$tool"
    done

    chmod +x "$TOOLS_DEST"/*.py

    # Check if PATH already includes tools
    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [[ -n "$SHELL_RC" ]]; then
        if ! grep -q "$TOOLS_DEST" "$SHELL_RC" 2>/dev/null; then
            cat >> "$SHELL_RC" <<PATH

# VEX Tools (added by vex installer)
export PATH="$TOOLS_DEST:\$PATH"
export VEX_HOME="$VEX_HOME"
PATH
            ok "Added $TOOLS_DEST to PATH in $SHELL_RC"
        else
            info "PATH already includes $TOOLS_DEST"
        fi
    fi

    # Create symlink for current session
    if [[ -d "/usr/local/bin" ]] && [[ -w "/usr/local/bin" ]]; then
        for tool in vex_skill_gen vex_cost vex_memory; do
            ln -sf "$TOOLS_DEST/$tool" "/usr/local/bin/$tool" 2>/dev/null || true
        done
    fi

    echo ""
    ok "Installation complete!"
    echo ""
    echo "  Tools:     $TOOLS_DEST/"
    echo "  Config:    $CONFIG_DEST/"
    echo "  Profile:   $PROFILE"
    echo ""
    echo "  Quick start:"
    echo "    vex_skill_gen scan          # Scan sessions for patterns"
    echo "    vex_cost report             # View cost report"
    echo "    vex_memory scan             # Build knowledge graph"
    echo "    vex_cost models             # View model pricing"
    echo ""
    echo "  Add to current shell:"
    echo "    export PATH=\"$TOOLS_DEST:\$PATH\""
}

do_uninstall() {
    info "Uninstalling VEX tools..."

    if $DRY_RUN; then
        warn "DRY RUN — no changes will be made"
        echo ""
        echo "Would remove:"
        echo "  $TOOLS_DEST/"
        echo "  (config and data in $VEX_HOME preserved)"
        return 0
    fi

    # Remove tools
    if [[ -d "$TOOLS_DEST" ]]; then
        rm -rf "$TOOLS_DEST"
        ok "Removed $TOOLS_DEST"
    else
        warn "Tools directory not found: $TOOLS_DEST"
    fi

    # Remove symlinks
    for tool in vex_skill_gen vex_cost vex_memory; do
        if [[ -L "/usr/local/bin/$tool" ]]; then
            rm -f "/usr/local/bin/$tool"
            ok "Removed /usr/local/bin/$tool"
        fi
    done

    # Note: keep data directory
    info "Preserved data directory: $VEX_HOME/"
    info "To fully remove: rm -rf $VEX_HOME"

    # Remove PATH entry from shell rc
    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    if [[ -n "$SHELL_RC" ]] && grep -q "VEX Tools" "$SHELL_RC" 2>/dev/null; then
        # Create temp file without the VEX block
        sed '/# VEX Tools/,/^$/d' "$SHELL_RC" > "$SHELL_RC.vex.tmp"
        mv "$SHELL_RC.vex.tmp" "$SHELL_RC"
        ok "Removed PATH entry from $SHELL_RC"
    fi

    echo ""
    ok "Uninstallation complete."
}

if $UNINSTALL; then
    do_uninstall
else
    do_install
fi
