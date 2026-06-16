"""Control VEX hook profiles at runtime."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = REPO_ROOT / "hooks" / "profiles.json"
ALLOWED_RUNTIME_KEYS = {"profile", "disabled_hooks"}


def vex_home() -> Path:
    return Path(os.environ.get("VEX_HOME", Path.home() / ".claude")).expanduser()


def runtime_path() -> Path:
    return vex_home() / "hook-runtime.json"


def envelope(ok: bool, command: str, data: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
    return {"ok": ok, "command": command, "data": data, "error": error}


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def load_profiles() -> dict[str, Any]:
    return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))


def load_runtime() -> dict[str, Any]:
    path = runtime_path()
    if not path.exists():
        return {"profile": os.environ.get("VEX_HOOK_PROFILE", "standard"), "disabled_hooks": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(data) - ALLOWED_RUNTIME_KEYS
    if unknown:
        raise ValueError(f"Unknown runtime keys: {', '.join(sorted(unknown))}")
    return {"profile": data.get("profile", "standard"), "disabled_hooks": list(data.get("disabled_hooks", []))}


def save_runtime(runtime: dict[str, Any]) -> None:
    path = runtime_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runtime, indent=2, sort_keys=True), encoding="utf-8")


def env_disabled_hooks() -> set[str]:
    raw = os.environ.get("VEX_DISABLED_HOOKS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def resolve_profile(name: str | None = None) -> dict[str, Any]:
    config = load_profiles()
    runtime = load_runtime()
    profile_name = name or os.environ.get("VEX_HOOK_PROFILE") or runtime.get("profile") or "standard"
    profiles = config["profiles"]
    if profile_name not in profiles:
        raise KeyError(profile_name)
    disabled = set(runtime.get("disabled_hooks", [])) | env_disabled_hooks()
    definitions = config["hook_definitions"]
    resolved: dict[str, list[dict[str, Any]]] = {}
    for event, hook_names in profiles[profile_name].get("hooks", {}).items():
        active = []
        for hook_name in hook_names:
            if hook_name in disabled:
                continue
            active.append({**definitions[hook_name]})
        resolved[event] = active
    return {"profile": profile_name, "description": profiles[profile_name]["description"], "hooks": resolved, "disabled_hooks": sorted(disabled)}


def cmd_profile_list(args: argparse.Namespace) -> int:
    profiles = sorted(load_profiles()["profiles"].keys())
    data = {"profiles": profiles}
    print_json(envelope(True, "hooks profile list", data)) if args.json else print("\n".join(profiles))
    return 0


def cmd_profile_show(args: argparse.Namespace) -> int:
    try:
        data = resolve_profile(args.name)
    except KeyError as exc:
        print_json(envelope(False, "hooks profile show", None, {"code": "PROFILE_NOT_FOUND", "message": str(exc)}))
        return 1
    except ValueError as exc:
        print_json(envelope(False, "hooks profile show", None, {"code": "INVALID_RUNTIME_CONTROLS", "message": str(exc)}))
        return 1
    print_json(envelope(True, "hooks profile show", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def cmd_profile_set(args: argparse.Namespace) -> int:
    profiles = load_profiles()["profiles"]
    if args.name not in profiles:
        print_json(envelope(False, "hooks profile set", None, {"code": "PROFILE_NOT_FOUND", "message": args.name}))
        return 1
    runtime = load_runtime()
    next_runtime = {**runtime, "profile": args.name}
    save_runtime(next_runtime)
    print_json(envelope(True, "hooks profile set", next_runtime)) if args.json else print(f"Hook profile set to {args.name}")
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    runtime = load_runtime()
    disabled = sorted(set(runtime.get("disabled_hooks", [])) | {args.hook_name})
    next_runtime = {**runtime, "disabled_hooks": disabled}
    save_runtime(next_runtime)
    print_json(envelope(True, "hooks disable", next_runtime)) if args.json else print(f"Disabled {args.hook_name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Control VEX hooks")
    sub = parser.add_subparsers(dest="command", required=True)
    profile = sub.add_parser("profile")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)
    list_cmd = profile_sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true")
    show = profile_sub.add_parser("show")
    show.add_argument("name", nargs="?")
    show.add_argument("--json", action="store_true")
    set_cmd = profile_sub.add_parser("set")
    set_cmd.add_argument("name")
    set_cmd.add_argument("--json", action="store_true")
    disable = sub.add_parser("disable")
    disable.add_argument("hook_name")
    disable.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "profile" and args.profile_command == "list":
        return cmd_profile_list(args)
    if args.command == "profile" and args.profile_command == "show":
        return cmd_profile_show(args)
    if args.command == "profile" and args.profile_command == "set":
        return cmd_profile_set(args)
    if args.command == "disable":
        return cmd_disable(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
