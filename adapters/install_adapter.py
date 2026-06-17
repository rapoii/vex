"""Install VEX assets into supported harnesses."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTERS_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILE = "developer"
VEX_RECEIPT_DIR = ".vex"


@dataclass(frozen=True)
class Action:
    kind: str
    source: str | None
    target: str
    description: str


def json_envelope(ok: bool, command: str, data: dict | None = None, error: str | None = None) -> str:
    payload: dict[str, object] = {"ok": ok, "command": command}
    if data is not None:
        payload["data"] = data
    if error is not None:
        payload["error"] = error
    return json.dumps(payload)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def adapter_paths() -> list[Path]:
    return sorted(path for path in ADAPTERS_DIR.glob("*.json") if path.name != "package.json")


def load_adapters() -> dict[str, dict]:
    adapters = {}
    for path in adapter_paths():
        payload = load_json(path)
        adapters[payload["id"]] = payload
    return adapters


def load_profiles() -> dict:
    return load_json(REPO_ROOT / "config" / "profiles.json")["profiles"]


def resolve_target_dir(raw_target_dir: str | None, adapter: dict) -> Path:
    raw = raw_target_dir or adapter["install"]["defaultTarget"]
    expanded = Path(os.path.expanduser(raw))
    resolved = expanded.resolve()
    cwd = Path.cwd().resolve()
    home = Path.home().resolve()
    if raw_target_dir == ".." or ".." in Path(raw).parts:
        raise ValueError(f"refusing target path with traversal: {raw}")
    if raw_target_dir is None:
        return resolved
    if resolved != cwd and cwd not in resolved.parents and home not in resolved.parents:
        raise ValueError(f"refusing target outside current project or home: {resolved}")
    return resolved


def profile_entries(profile_name: str) -> list[str]:
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ValueError(f"unknown profile: {profile_name}")
    return list(profiles[profile_name]["include"])


def source_exists(entry: str) -> bool:
    root = entry.split("/", 1)[0]
    return (REPO_ROOT / root).exists()


def build_install_plan(adapter: dict, profile_name: str, target_dir: Path) -> list[Action]:
    entries = [entry for entry in profile_entries(profile_name) if source_exists(entry)]
    actions: list[Action] = [Action("create_dir", None, str(target_dir), "Create harness target directory")]
    for entry in entries:
        root = entry.split("/", 1)[0]
        source = REPO_ROOT / root
        mapping = adapter["fileMapping"].get(root, root)
        if mapping == "unsupported":
            continue
        target = target_dir / mapping.split("*", 1)[0].rstrip("/")
        actions.append(Action("copy", str(source), str(target), f"Install {root} for {adapter['id']}"))
    actions.append(Action("write_receipt", None, str(target_dir / VEX_RECEIPT_DIR / "install-receipt.json"), "Record VEX ownership receipt"))
    return actions


def action_to_dict(action: Action) -> dict[str, str | None]:
    return {
        "kind": action.kind,
        "source": action.source,
        "target": action.target,
        "description": action.description,
    }


def execute_actions(actions: list[Action], dry_run: bool) -> None:
    if dry_run:
        return
    receipt_files = []
    for action in actions:
        target = Path(action.target)
        if action.kind == "create_dir":
            target.mkdir(parents=True, exist_ok=True)
        elif action.kind == "copy" and action.source:
            source = Path(action.source)
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                for child in source.rglob("*"):
                    if child.is_file():
                        relative = child.relative_to(source)
                        destination = target / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(child, destination)
                        receipt_files.append(str(destination))
            elif source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                receipt_files.append(str(target))
        elif action.kind == "write_receipt":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({"owner": "vex", "files": receipt_files}, indent=2), encoding="utf-8")


def detect_harnesses() -> list[dict[str, object]]:
    checks = {
        "claude-code": Path.home() / ".claude",
        "cursor": Path.cwd() / ".cursor",
        "codex": Path.cwd() / "AGENTS.md",
        "gemini-cli": Path.cwd() / ".gemini",
        "copilot-cli": Path.cwd() / ".github" / "copilot-instructions.md",
        "opencode": Path.cwd() / ".opencode",
        "zed": Path.cwd() / ".zed",
        "factory-droid": Path.home() / ".factory-droid",
    }
    return [{"id": key, "detected": value.exists(), "path": str(value)} for key, value in checks.items()]


def cmd_list(args: argparse.Namespace) -> int:
    adapters = load_adapters()
    data = {
        "adapters": [
            {"id": adapter_id, "harness": adapter["harness"], "detected": next(item["detected"] for item in detect_harnesses() if item["id"] == adapter_id)}
            for adapter_id, adapter in sorted(adapters.items())
        ]
    }
    if args.json:
        print(json_envelope(True, "list", data))
    else:
        for adapter in data["adapters"]:
            marker = "yes" if adapter["detected"] else "no"
            print(f"{adapter['id']} ({adapter['harness']}) detected={marker}")
    return 0


def selected_adapter(name: str) -> dict:
    adapters = load_adapters()
    if name not in adapters:
        raise ValueError(f"unknown adapter: {name}")
    return adapters[name]


def cmd_install(args: argparse.Namespace) -> int:
    try:
        adapter = selected_adapter(args.adapter)
        target_dir = resolve_target_dir(args.target_dir, adapter)
        actions = build_install_plan(adapter, args.profile, target_dir)
        execute_actions(actions, args.dry_run)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        if args.json:
            print(json_envelope(False, "install", error=str(exc)))
        else:
            print(str(exc), file=sys.stderr)
        return 1

    data = {"adapter": args.adapter, "profile": args.profile, "dry_run": args.dry_run, "actions": [action_to_dict(action) for action in actions]}
    if args.json:
        print(json_envelope(True, "install", data))
    else:
        print(f"Adapter: {args.adapter}")
        print(f"Profile: {args.profile}")
        for action in actions:
            print(f"{action.kind}: {action.target}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    checks = [
        {"name": "adapter_configs", "ok": all(path.exists() for path in adapter_paths())},
        {"name": "profiles_json", "ok": (REPO_ROOT / "config" / "profiles.json").exists()},
        {"name": "harness_detection", "ok": True, "detected": detect_harnesses()},
    ]
    ok = all(check["ok"] for check in checks)
    if args.json:
        print(json_envelope(ok, "doctor", {"checks": checks}))
    else:
        for check in checks:
            print(f"{'ok' if check['ok'] else 'fail'} {check['name']}")
    return 0 if ok else 1


def cmd_repair(args: argparse.Namespace) -> int:
    adapter = selected_adapter(args.adapter)
    target_dir = resolve_target_dir(args.target_dir, adapter)
    actions = build_install_plan(adapter, args.profile, target_dir)
    data = {"adapter": args.adapter, "profile": args.profile, "dry_run": args.dry_run, "actions": [action_to_dict(action) for action in actions]}
    if args.json:
        print(json_envelope(True, "repair", data))
    else:
        for action in actions:
            print(f"repair {action.kind}: {action.target}")
    if not args.dry_run:
        execute_actions(actions, dry_run=False)
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    adapter = selected_adapter(args.adapter)
    target_dir = resolve_target_dir(args.target_dir, adapter)
    receipt = target_dir / VEX_RECEIPT_DIR / "install-receipt.json"
    actions = [Action("remove_receipt_owned", str(receipt), str(target_dir), "Remove only files listed in VEX receipt")]
    if not args.dry_run and receipt.exists():
        payload = load_json(receipt)
        for file_name in payload.get("files", []):
            path = Path(file_name)
            if path.exists() and target_dir in path.resolve().parents:
                path.unlink()
        receipt.unlink()
    data = {"adapter": args.adapter, "dry_run": args.dry_run, "actions": [action_to_dict(action) for action in actions]}
    if args.json:
        print(json_envelope(True, "uninstall", data))
    else:
        for action in actions:
            print(f"uninstall {action.kind}: {action.target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install VEX into supported harnesses")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.set_defaults(func=cmd_doctor)

    for command, func in (("install", cmd_install), ("repair", cmd_repair), ("uninstall", cmd_uninstall)):
        sub = subparsers.add_parser(command)
        sub.add_argument("adapter")
        sub.add_argument("--profile", default=DEFAULT_PROFILE)
        sub.add_argument("--target-dir")
        sub.add_argument("--dry-run", action="store_true")
        sub.add_argument("--json", action="store_true")
        sub.set_defaults(func=func)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        if getattr(args, "json", False):
            print(json_envelope(False, args.command, error=str(exc)))
        else:
            print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
