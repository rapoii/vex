from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "hooks" / "gate-guard-rules.json"


def load_rules(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("rules config must be a JSON object")
    return data


def read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("hook payload must be a JSON object")
    return data


def command_from_payload(payload: dict) -> str:
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", "")
    return command if isinstance(command, str) else ""


def normalize_rules(config: dict, key: str) -> list[dict]:
    legacy_key = "block_patterns" if key == "block" else "warn_patterns"
    entries = config.get(key, config.get(legacy_key, []))
    if not isinstance(entries, list):
        raise ValueError(f"{key} rules must be a list")
    rules = []
    for index, entry in enumerate(entries, 1):
        if isinstance(entry, str):
            rules.append({"id": f"{key}-{index}", "pattern": entry, "message": entry})
        elif isinstance(entry, dict):
            pattern = entry.get("pattern")
            if not isinstance(pattern, str):
                raise ValueError(f"{key} rule {index} missing pattern")
            rules.append({
                "id": str(entry.get("id", f"{key}-{index}")),
                "pattern": pattern,
                "message": str(entry.get("message", pattern)),
            })
        else:
            raise ValueError(f"{key} rule {index} must be object or string")
    return rules


def first_match(command: str, rules: list[dict]) -> dict | None:
    for rule in rules:
        if re.search(rule["pattern"], command):
            return rule
    return None


def decision_for(command: str, config: dict) -> tuple[str, str]:
    block = first_match(command, normalize_rules(config, "block"))
    if block:
        return "block", f"{block['id']}: {block['message']}"
    warn = first_match(command, normalize_rules(config, "warn"))
    if warn:
        return "warn", f"{warn['id']}: {warn['message']}"
    return "allow", "No gate-guard rules matched"


def emit(decision: str, reason: str) -> int:
    print(json.dumps({"decision": decision, "reason": reason}, sort_keys=True))
    if decision == "block":
        print(f"BLOCKED: {reason}", file=sys.stderr)
        return 1
    if decision == "warn":
        print(f"WARNING: {reason}", file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEX gate guard for destructive commands")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to gate guard rules JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = read_payload()
        config = load_rules(Path(args.config))
        command = command_from_payload(payload)
        decision, reason = decision_for(command, config)
        return emit(decision, reason)
    except (OSError, json.JSONDecodeError, ValueError, re.error) as exc:
        return emit("block", f"gate guard error: {exc}")


if __name__ == "__main__":
    sys.exit(main())
