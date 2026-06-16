#!/usr/bin/env bash
# VEX Tools Installer — Unix/macOS
# Usage: bash install.sh [--profile NAME] [--dry-run] [--uninstall]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_VEX_HOME="$HOME/.vex"
VEX_HOME="${VEX_HOME:-$DEFAULT_VEX_HOME}"
PROFILE="${PROFILE:-developer}"
COMPONENTS="${COMPONENTS:-all}"
DRY_RUN=false
UNINSTALL=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[vex]${NC} $*"; }
ok()    { echo -e "${GREEN}[vex]${NC} $*"; }
warn()  { echo -e "${YELLOW}[vex]${NC} $*"; }
err()   { echo -e "${RED}[vex]${NC} $*" >&2; }

if command -v python3 &>/dev/null && python3 -c "import sys" 2>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python -c "import sys" 2>/dev/null; then
    PYTHON_CMD="python"
else
    err "Python is required but not found."
    exit 1
fi

backup_file() {
    local path="$1"
    if [[ -f "$path" ]]; then
        cp "$path" "$path.bak"
    fi
}

shell_quote() {
    printf '%q' "$1"
}

get_includes() {
    local profile="$1"
    cd "$SCRIPT_DIR" || exit 1
    "$PYTHON_CMD" -c "
import json, sys
try:
    with open('config/profiles.json') as f:
        data = json.load(f)
    profiles = data.get('profiles', {})
    if '$profile' not in profiles:
        print(f\"Error: Profile '{'$profile'}' not found in profiles.json\", file=sys.stderr)
        sys.exit(1)
    for item in profiles['$profile'].get('include', []):
        print(item)
except Exception as e:
    print(f\"Error parsing profiles.json: {e}\", file=sys.stderr)
    sys.exit(1)
"
}

validate_profile() {
    if [[ ! "$PROFILE" =~ ^[A-Za-z0-9._-]+$ ]]; then
        err "Invalid profile name: $PROFILE"
        exit 1
    fi
    # Check if we can get includes without error
    if ! get_includes "$PROFILE" >/dev/null; then
        exit 1
    fi
}

filter_includes() {
    local profile="$1"
    cd "$SCRIPT_DIR" || exit 1
    COMPONENTS="$COMPONENTS" "$PYTHON_CMD" -c "
import json, os, sys

valid_components = {
    'adapters', 'agents', 'commands', 'config', 'contexts',
    'hooks', 'marketplace', 'rules', 'skills', 'tools'
}
components = os.environ.get('COMPONENTS', 'all')
selected = None

if components != 'all':
    parts = [part.strip() for part in components.split(',')]
    if any(not part for part in parts):
        print('Error: --components contains an empty component', file=sys.stderr)
        sys.exit(1)
    unknown = sorted(set(parts) - valid_components)
    if unknown:
        print(f\"Error: Unknown component(s): {', '.join(unknown)}\", file=sys.stderr)
        sys.exit(1)
    selected = set(parts)

try:
    with open('config/profiles.json') as f:
        data = json.load(f)
    profiles = data.get('profiles', {})
    if '$profile' not in profiles:
        print(f\"Error: Profile '{'$profile'}' not found in profiles.json\", file=sys.stderr)
        sys.exit(1)
    for item in profiles['$profile'].get('include', []):
        component = item.split('/', 1)[0]
        if selected is None or component in selected:
            print(item)
except Exception as e:
    print(f\"Error parsing profiles.json: {e}\", file=sys.stderr)
    sys.exit(1)
"
}

validate_components() {
    if ! filter_includes "$PROFILE" >/dev/null; then
        exit 1
    fi
}

validate_vex_home() {
    if [[ "$VEX_HOME" == *$'\n'* || "$VEX_HOME" == *$'\r'* ]]; then
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
  --profile NAME     Install for specific profile (default: developer)
  --components LIST  Install selected components only (default: all)
                     Example: --components agents,skills,rules
  --dry-run          Show what would be done without making changes
  --uninstall        Remove VEX tools
  --help             Show this help message

Environment:
  VEX_HOME          VEX home directory (default: ~/.vex)
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)  PROFILE="$2"; shift 2 ;;
        --components) COMPONENTS="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        --help)     usage ;;
        *)          err "Unknown option: $1"; exit 1 ;;
    esac
done

validate_profile
validate_components
validate_vex_home

TOOLS_DEST="$VEX_HOME/tools"

print_dry_run_install() {
    warn "DRY RUN — no changes will be made"
    echo ""
    echo "Would install components for profile: $PROFILE"
    echo "Selected components: $COMPONENTS"
    echo ""

    local includes
    includes=$(filter_includes "$PROFILE" | tr -d '\r')

    for item in $includes; do
        if [[ -f "$SCRIPT_DIR/$item" ]]; then
            echo "Would copy file: $item -> $VEX_HOME/$item"
        elif [[ -d "$SCRIPT_DIR/$item" ]]; then
            echo "Would copy dir:  $item/ -> $VEX_HOME/$item/"
        else
            echo "Warning: Component not found: $item"
        fi
    done

    echo ""
    echo "Would add to PATH:"
    echo "  $TOOLS_DEST"
    echo ""
    echo "Would create wrapper scripts in $TOOLS_DEST"
}

copy_component() {
    local item="$1"
    local src="$SCRIPT_DIR/$item"
    local dest="$VEX_HOME/$item"

    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        backup_file "$dest"
        cp "$src" "$dest"
    elif [[ -d "$src" ]]; then
        mkdir -p "$dest"
        cp -R "$src/." "$dest/"
    else
        warn "Component not found, skipping: $item"
    fi
}

create_wrapper() {
    local name="$1"
    cat > "$TOOLS_DEST/$name" <<WRAPPER
#!/usr/bin/env bash
exec "$PYTHON_CMD" "$TOOLS_DEST/${name}.py" "\$@"
WRAPPER
    chmod +x "$TOOLS_DEST/$name"
}

do_install() {
    info "Installing VEX tools..."
    info "  Profile:    $PROFILE"
    info "  Components: $COMPONENTS"
    info "  VEX Home:   $VEX_HOME"
    info "  Source:     $SCRIPT_DIR"

    if $DRY_RUN; then
        print_dry_run_install
        return 0
    fi

    local includes
    includes=$(filter_includes "$PROFILE" | tr -d '\r')

    for item in $includes; do
        copy_component "$item"
    done

    # Create wrappers for any python scripts in tools/
    if [[ -d "$TOOLS_DEST" ]]; then
        for py_file in "$TOOLS_DEST"/*.py; do
            if [[ -f "$py_file" ]]; then
                name="$(basename "$py_file" .py)"
                create_wrapper "$name"
            fi
        done
        chmod +x "$TOOLS_DEST"/*.py
    fi

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
        if [[ -d "$TOOLS_DEST" ]]; then
            for py_file in "$TOOLS_DEST"/*.py; do
                if [[ -f "$py_file" ]]; then
                    name="$(basename "$py_file" .py)"
                    ln -sf "$TOOLS_DEST/$name" "/usr/local/bin/$name" 2>/dev/null || true
                fi
            done
        fi
    fi

    echo ""
    ok "Installation complete!"
    echo ""
    echo "  VEX Home:    $VEX_HOME/"
    echo "  Profile:     $PROFILE"
    echo "  Components:  $COMPONENTS"
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
        echo "Would remove installed components for profile $PROFILE"
        echo "Selected components: $COMPONENTS"
        echo "  (config and data in $VEX_HOME preserved, unless explicitly removed)"
        return 0
    fi

    validate_uninstall_target

    local includes
    includes=$(filter_includes "$PROFILE" | tr -d '\r')

    for item in $includes; do
        if [[ -e "$VEX_HOME/$item" ]]; then
            rm -rf "$VEX_HOME/$item"
            ok "Removed $VEX_HOME/$item"
        fi
    done

    # Remove symlinks in /usr/local/bin
    if [[ -d "$TOOLS_DEST" ]]; then
        for py_file in "$TOOLS_DEST"/*.py; do
            if [[ -f "$py_file" ]]; then
                name="$(basename "$py_file" .py)"
                if [[ -L "/usr/local/bin/$name" ]]; then
                    rm -f "/usr/local/bin/$name"
                    ok "Removed /usr/local/bin/$name"
                fi
            fi
        done
    fi

    info "Preserved remaining config and data in: $VEX_HOME/"
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
