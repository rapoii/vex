"""
VEX Unified CLI
"""
import argparse
import subprocess
import sys
import json
import os
import py_compile
import shutil
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
    "sessions": ("python", TOOLS_DIR / "vex_sessions.py"),
    "instinct": ("python", TOOLS_DIR / "vex_instinct.py"),
    "hooks": ("python", TOOLS_DIR / "vex_hooks.py"),
    "optimize": ("python", TOOLS_DIR / "vex_optimize.py"),
    "dashboard": ("python", REPO_ROOT / "dashboard" / "server.py"),
    "install": ("bash", REPO_ROOT / "install.sh"),
    "repair": ("python", TOOLS_DIR / "vex_repair.py"),
    "uninstall": ("python", TOOLS_DIR / "vex_uninstall.py"),
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

def add_check(checks, name, ok, detail=None, value=None):
    check = {"name": name, "ok": bool(ok)}
    if detail is not None:
        check["detail"] = detail
    if value is not None:
        check["value"] = value
    checks.append(check)
    return bool(ok)


def json_file_valid(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return True, json.load(file), "valid"
    except Exception as error:
        return False, None, str(error)


def hook_script_paths(hooks_config):
    paths = []
    hooks = hooks_config.get("hooks", {}) if isinstance(hooks_config, dict) else {}
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                command = hook.get("command", "") if isinstance(hook, dict) else ""
                parts = command.split()
                for part in parts:
                    if part.startswith("hooks/scripts/"):
                        paths.append(REPO_ROOT / part)
    return paths


def count_files(directory, pattern):
    if not directory.exists():
        return 0
    return sum(1 for path in directory.rglob(pattern) if path.is_file())


def cmd_doctor(args):
    """Check VEX installation health."""
    is_json = getattr(args, "json", False)

    checks = []
    ok = True
    claude_dir = Path.home() / ".claude"

    ok &= add_check(checks, "claude_dir_exists", claude_dir.exists())
    for check_name, path in {
        "AGENTS_md_exists": "AGENTS.md",
        "skills_dir_exists": "skills",
        "commands_dir_exists": "commands",
        "rules_dir_exists": "rules",
        "hooks_dir_exists": "hooks",
    }.items():
        ok &= add_check(checks, check_name, (claude_dir / path).exists())

    ok &= add_check(checks, "python_tools_importable", True)
    config_valid = True
    for conf_file in ["settings.json", "plugin.json"]:
        path = claude_dir / conf_file
        if path.exists():
            valid, _, _ = json_file_valid(path)
            config_valid &= valid
    ok &= add_check(checks, "config_json_valid", config_valid)
    ok &= add_check(checks, "config_dir", (REPO_ROOT / "config").exists())
    add_check(checks, "claude_md", (REPO_ROOT / "CLAUDE.md").exists())

    hooks_valid, hooks_config, hooks_detail = json_file_valid(REPO_ROOT / "hooks" / "hooks.json")
    ok &= add_check(checks, "hooks_json_valid", hooks_valid, hooks_detail)
    hook_paths = hook_script_paths(hooks_config or {})
    missing_hooks = [str(path.relative_to(REPO_ROOT)) for path in hook_paths if not path.exists()]
    ok &= add_check(checks, "hook_scripts_exist", not missing_hooks, ", ".join(missing_hooks) if missing_hooks else "all referenced scripts exist", len(hook_paths))

    invalid_adapters = []
    for path in sorted((REPO_ROOT / "adapters").glob("*.json")):
        valid, _, detail = json_file_valid(path)
        if not valid:
            invalid_adapters.append(f"{path.name}: {detail}")
    ok &= add_check(checks, "adapters_json_valid", not invalid_adapters, "; ".join(invalid_adapters) if invalid_adapters else "valid")

    catalog_valid, _, catalog_detail = json_file_valid(REPO_ROOT / "marketplace" / "catalog.json")
    ok &= add_check(checks, "marketplace_catalog_json_valid", catalog_valid, catalog_detail)

    try:
        py_compile.compile(str(REPO_ROOT / "dashboard" / "server.py"), doraise=True)
        dashboard_ok = True
        dashboard_detail = "syntax ok"
    except py_compile.PyCompileError as error:
        dashboard_ok = False
        dashboard_detail = str(error)
    ok &= add_check(checks, "dashboard_server_py_compile", dashboard_ok, dashboard_detail)

    usage = shutil.disk_usage(REPO_ROOT)
    add_check(checks, "disk_usage_available", True, "bytes", {"total": usage.total, "used": usage.used, "free": usage.free})
    add_check(checks, "agents_count", True, value=count_files(REPO_ROOT / "agents", "*.md"))
    add_check(checks, "skills_count", True, value=count_files(REPO_ROOT / "skills", "SKILL.md"))
    add_check(checks, "rules_count", True, value=count_files(REPO_ROOT / "rules", "*.md"))

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
        status = "OK" if check["ok"] else "ERROR"
        detail = f" — {check['detail']}" if "detail" in check else ""
        print(f"{icon} [{status}] {check['name']}{detail}")

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

        # Forward global flags
        forward_args = []
        if args.json:
            forward_args.append("--json")
        if getattr(args, "yes", False):
            forward_args.append("--yes")

        # Build full command
        full_cmd = [cmd_runner, cmd_target] + list(cmd_extra) + forward_args + unknown_args

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
