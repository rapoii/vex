#!/usr/bin/env bash
# VEX Tools Installer — Unix/macOS
# Usage: bash install.sh [--profile NAME] [--dry-run] [--uninstall]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_VEX_HOME="$HOME/.vex"
VEX_HOME="${VEX_HOME:-$DEFAULT_VEX_HOME}"
PROFILE="${PROFILE:-developer}"
DRY_RUN=false
UNINSTALL=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOOLS=(
    vex.py
    vex_skill_gen.py
    vex_cost.py
    vex_memory.py
    vex_sessions.py
    vex_security.py
    vex_instinct.py
    vex_hooks.py
    vex_optimize.py
)

info()  { echo -e "${BLUE}[vex]${NC} $*"; }
ok()    { echo -e "${GREEN}[vex]${NC} $*"; }
warn()  { echo -e "${YELLOW}[vex]${NC} $*"; }
err()   { echo -e "${RED}[vex]${NC} $*" >&2; }

backup_file() {
    local path="$1"
    if [[ -f "$path" ]]; then
        cp "$path" "$path.bak"
    fi
}

shell_quote() {
    printf '%q' "$1"
}

validate_profile() {
    if [[ ! "$PROFILE" =~ ^[A-Za-z0-9._-]+$ ]]; then
        err "Invalid profile name: $PROFILE"
        exit 1
    fi
}

validate_vex_home() {
    if [[ "$VEX_HOME" == *$'\n'* || "$VEX_HOME" == *$'\r'* || "$VEX_HOME" == *$'\0'* ]]; then
        err "Invalid VEX_HOME: control characters are not allowed"
        exit 1
    fi
}

validate_uninstall_target() {
    local default_resolved
    local actual_resolved
    default_resolved="$(cd "$(dirname "$DEFAULT_VEX_HOME")" && pwd)/$(basename "$DEFAULT_VEX_HOME")"
    actual_resolved="$(cd "$(dirname "$VEX_HOME")" && pwd)/$(basename "$VEX_HOME")"
    if [[ "$actual_resolved" != "$default_resolved" ]]; then
        err "Refusing uninstall for custom VEX_HOME without manual removal: $VEX_HOME"
        exit 1
    fi
}

usage() {
    cat <<EOF
VEX Tools Installer

Usage:
  bash install.sh [OPTIONS]

Options:
  --profile NAME    Install for specific profile (default: developer)
  --dry-run         Show what would be done without making changes
  --uninstall       Remove VEX tools
  --help            Show this help message

Environment:
  VEX_HOME          VEX home directory (default: ~/.vex)
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)  PROFILE="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        --help)     usage ;;
        *)          err "Unknown option: $1"; exit 1 ;;
    esac
done

validate_profile
validate_vex_home

PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE"
TOOLS_DEST="$VEX_HOME/tools"
CONFIG_DEST="$VEX_HOME/config"
ADAPTERS_DEST="$VEX_HOME/adapters"
MARKETPLACE_DEST="$VEX_HOME/marketplace"
SKILLS_DEST="$PROFILE_DIR/skills"

print_dry_run_install() {
    warn "DRY RUN — no changes will be made"
    echo ""
    echo "Would create directories:"
    echo "  $TOOLS_DEST"
    echo "  $CONFIG_DEST"
    echo "  $ADAPTERS_DEST"
    echo "  $MARKETPLACE_DEST"
    echo "  $SKILLS_DEST"
    echo ""
    echo "Would copy tools:"
    for tool in "${TOOLS[@]}"; do
        echo "  tools/$tool -> $TOOLS_DEST/"
    done
    echo ""
    echo "Would copy directories:"
    echo "  config/      -> $CONFIG_DEST/"
    echo "  adapters/    -> $ADAPTERS_DEST/"
    echo "  marketplace/ -> $MARKETPLACE_DEST/"
    echo ""
    echo "Would add to PATH:"
    echo "  $TOOLS_DEST"
    echo ""
    echo "Would create wrapper scripts:"
    for tool in "${TOOLS[@]}"; do
        local name="${tool%.py}"
        echo "  $TOOLS_DEST/$name"
    done
}

copy_directory() {
    local source_dir="$1"
    local dest_dir="$2"
    mkdir -p "$dest_dir"
    cp -R "$source_dir/." "$dest_dir/"
}

create_wrapper() {
    local name="$1"
    cat > "$TOOLS_DEST/$name" <<WRAPPER
#!/usr/bin/env bash
exec python3 "$TOOLS_DEST/${name}.py" "\$@"
WRAPPER
    chmod +x "$TOOLS_DEST/$name"
}

do_install() {
    info "Installing VEX tools..."
    info "  Profile:    $PROFILE"
    info "  VEX Home:   $VEX_HOME"
    info "  Source:     $SCRIPT_DIR"

    if $DRY_RUN; then
        print_dry_run_install
        return 0
    fi

    mkdir -p "$TOOLS_DEST" "$CONFIG_DEST" "$ADAPTERS_DEST" "$MARKETPLACE_DEST" "$SKILLS_DEST"

    for tool in "${TOOLS[@]}"; do
        backup_file "$TOOLS_DEST/$tool"
        cp "$SCRIPT_DIR/tools/$tool" "$TOOLS_DEST/"
    done

    copy_directory "$SCRIPT_DIR/config" "$CONFIG_DEST"
    copy_directory "$SCRIPT_DIR/adapters" "$ADAPTERS_DEST"
    copy_directory "$SCRIPT_DIR/marketplace" "$MARKETPLACE_DEST"

    for tool in "${TOOLS[@]}"; do
        create_wrapper "${tool%.py}"
    done

    chmod +x "$TOOLS_DEST"/*.py

    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [[ -n "$SHELL_RC" ]]; then
        if ! grep -q "$TOOLS_DEST" "$SHELL_RC" 2>/dev/null; then
            quoted_tools_dest="$(shell_quote "$TOOLS_DEST")"
            quoted_vex_home="$(shell_quote "$VEX_HOME")"
            cat >> "$SHELL_RC" <<PATH

# VEX Tools (added by vex installer)
export PATH="$quoted_tools_dest:\$PATH"
export VEX_HOME=$quoted_vex_home
PATH
            ok "Added $TOOLS_DEST to PATH in $SHELL_RC"
        else
            info "PATH already includes $TOOLS_DEST"
        fi
    fi

    if [[ -d "/usr/local/bin" ]] && [[ -w "/usr/local/bin" ]]; then
        for tool in "${TOOLS[@]}"; do
            name="${tool%.py}"
            ln -sf "$TOOLS_DEST/$name" "/usr/local/bin/$name" 2>/dev/null || true
        done
    fi

    echo ""
    ok "Installation complete!"
    echo ""
    echo "  Tools:       $TOOLS_DEST/"
    echo "  Config:      $CONFIG_DEST/"
    echo "  Adapters:    $ADAPTERS_DEST/"
    echo "  Marketplace: $MARKETPLACE_DEST/"
    echo "  Profile:     $PROFILE"
    echo ""
    echo "  Quick start:"
    echo "    vex --help"
    echo "    vex_cost report"
    echo "    vex_memory scan"
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
        echo "  $ADAPTERS_DEST/"
        echo "  $MARKETPLACE_DEST/"
        echo "  (config and data in $VEX_HOME preserved)"
        return 0
    fi

    validate_uninstall_target

    for path in "$TOOLS_DEST" "$ADAPTERS_DEST" "$MARKETPLACE_DEST"; do
        if [[ -d "$path" ]]; then
            rm -rf "$path"
            ok "Removed $path"
        else
            warn "Directory not found: $path"
        fi
    done

    for tool in "${TOOLS[@]}"; do
        name="${tool%.py}"
        if [[ -L "/usr/local/bin/$name" ]]; then
            rm -f "/usr/local/bin/$name"
            ok "Removed /usr/local/bin/$name"
        fi
    done

    info "Preserved config and data directory: $VEX_HOME/"
    info "To fully remove: rm -rf $VEX_HOME"

    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    if [[ -n "$SHELL_RC" ]] && grep -q "VEX Tools" "$SHELL_RC" 2>/dev/null; then
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
