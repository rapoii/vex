"""
VEX Unified CLI
"""
import argparse
import subprocess
import sys
import json
import os
from pathlib import Path

# Compute absolute paths
TOOLS_DIR = Path(__file__).parent.resolve()
REPO_ROOT = TOOLS_DIR.parent.resolve()

COMMAND_MAP = {
    "skill": ("python", TOOLS_DIR / "vex_skill_gen.py"),
    "scan": ("python", TOOLS_DIR / "vex_skill_gen.py", "scan"),
    "generate": ("python", TOOLS_DIR / "vex_skill_gen.py", "generate"),
    "cost": ("python", TOOLS_DIR / "vex_cost.py"),
    "memory": ("python", TOOLS_DIR / "vex_memory.py"),
    "dashboard": ("python", REPO_ROOT / "dashboard" / "server.py"),
    "install": ("bash", REPO_ROOT / "install.sh"),
}

def print_json(data):
    print(json.dumps(data))

def cmd_status(args):
    """Show VEX system status."""
    is_json = getattr(args, "json", False)

    status_data = {
        "ok": True,
        "command": "status",
        "data": {
            "root": str(REPO_ROOT),
            "tools_dir": str(TOOLS_DIR)
        }
    }

    if is_json:
        print_json(status_data)
        return 0

    print(f"\033[1;36mVEX System Status\033[0m")
    print(f"Root: {REPO_ROOT}")
    print(f"Tools: {TOOLS_DIR}")
    return 0

def cmd_doctor(args):
    """Check VEX installation health."""
    is_json = getattr(args, "json", False)

    checks = []
    ok = True

    # Check config/manifests exist
    config_dir = REPO_ROOT / "config"
    has_config = config_dir.exists()
    checks.append({"name": "config_dir", "ok": has_config})
    if not has_config: ok = False

    # Check if inside repo
    claude_md = REPO_ROOT / "CLAUDE.md"
    has_claude_md = claude_md.exists()
    checks.append({"name": "claude_md", "ok": has_claude_md})

    data = {
        "ok": ok,
        "command": "doctor",
        "data": {"checks": checks}
    }

    if is_json:
        print_json(data)
        return 0 if ok else 1

    print(f"\033[1;36mVEX Doctor\033[0m")
    for check in checks:
        icon = "✅" if check["ok"] else "❌"
        print(f"{icon} {check['name']}")

    return 0 if ok else 1

def cmd_update(args):
    """Pull latest and reinstall."""
    is_json = getattr(args, "json", False)

    if not is_json:
        print("\033[1;34mUpdating VEX...\033[0m")

    try:
        import shutil
        npm_cmd = shutil.which("npm") or ("npm.cmd" if os.name == "nt" else "npm")
        git_cmd = shutil.which("git") or ("git.exe" if os.name == "nt" else "git")

        result_git = subprocess.run([git_cmd, "pull"], cwd=REPO_ROOT)
        if result_git.returncode != 0:
            if is_json:
                print_json({"ok": False, "command": "update", "error": "git pull failed"})
            return result_git.returncode

        result_npm = subprocess.run([npm_cmd, "install"], cwd=REPO_ROOT)
        if result_npm.returncode != 0:
            if is_json:
                print_json({"ok": False, "command": "update", "error": "npm install failed"})
            return result_npm.returncode

        if is_json:
            print_json({"ok": True, "command": "update"})
        return 0
    except Exception as e:
        if is_json:
            print_json({"ok": False, "command": "update", "error": str(e)})
        else:
            print(f"\033[1;31mUpdate Error:\033[0m {e}", file=sys.stderr)
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="VEX — Vareva ECC Extended",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # We want to support flags before or after the command.
    # To do this cleanly, we can add global arguments to a parent parser.
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json", action="store_true", help="Output JSON envelope")
    parent_parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")
    parent_parser.add_argument("--verbose", action="store_true", help="Show debug output")

    parser = argparse.ArgumentParser(
        description="VEX — Vareva ECC Extended",
        formatter_class=argparse.RawTextHelpFormatter,
        parents=[parent_parser]
    )

    subparsers = parser.add_subparsers(dest="command", help="VEX Commands")

    # Core internal commands
    subparsers.add_parser("status", help="Show VEX system status", parents=[parent_parser])
    subparsers.add_parser("doctor", help="Check VEX installation health", parents=[parent_parser])
    subparsers.add_parser("update", help="Update VEX to latest version", parents=[parent_parser])

    # Wrapped commands
    for cmd in COMMAND_MAP.keys():
        subparsers.add_parser(cmd, help=f"Run {cmd} tool", parents=[parent_parser])

    # Parse known args so we can pass the rest to the wrappers
    args, unknown_args = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "doctor":
        sys.exit(cmd_doctor(args))
    elif args.command == "update":
        sys.exit(cmd_update(args))

    # Dispatch wrapped command
    if args.command in COMMAND_MAP:
        mapping = COMMAND_MAP[args.command]
        cmd_runner = mapping[0]
        cmd_target = str(mapping[1])
        cmd_extra = mapping[2:] if len(mapping) > 2 else ()

        # Build full command
        full_cmd = [cmd_runner, cmd_target] + list(cmd_extra) + unknown_args

        if args.verbose:
            print(f"[VEX] Dispatching: {' '.join(full_cmd)}", file=sys.stderr)

        # Run process
        try:
            result = subprocess.run(full_cmd, cwd=REPO_ROOT)
            sys.exit(result.returncode)
        except Exception as e:
            if args.json:
                print_json({
                    "ok": False,
                    "command": args.command,
                    "error": str(e)
                })
            else:
                print(f"\033[1;31mVEX Execution Error:\033[0m {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
