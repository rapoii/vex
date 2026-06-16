"""Analyze and reduce token usage for VEX workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any


FILLER_WORDS = {"please", "just", "really", "basically", "actually", "simply", "kindly", "comprehensive"}
ARCHITECTURE_TERMS = {"architecture", "architect", "migration", "design", "system", "strategy"}
CODING_TERMS = {"implement", "fix", "test", "refactor", "code", "build"}
EXPLORATION_TERMS = {"search", "classify", "summarize", "scan", "list", "grep", "find"}


def vex_home() -> Path:
    return Path(os.environ.get("VEX_HOME", Path.home() / ".claude")).expanduser()


def db_path() -> Path:
    return vex_home() / "vex-sessions.db"


def envelope(ok: bool, command: str, data: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
    return {"ok": ok, "command": command, "data": data, "error": error}


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def slim_prompt(prompt: str) -> str:
    words = prompt.split()
    kept = [word for word in words if re.sub(r"[^a-z]", "", word.lower()) not in FILLER_WORDS]
    return " ".join(kept)


def choose_model(task: str) -> dict[str, Any]:
    words = {re.sub(r"[^a-z]", "", word.lower()) for word in task.split()}
    if words & ARCHITECTURE_TERMS:
        return {"model": "opus", "reason": "Architecture or migration task needs deepest reasoning."}
    if words & EXPLORATION_TERMS and not (words & CODING_TERMS):
        return {"model": "haiku", "reason": "Exploration/classification task can use lower-cost model."}
    return {"model": "sonnet", "reason": "Coding or validation task fits balanced coding model."}


def analyze_usage() -> dict[str, Any]:
    if not db_path().exists():
        return {"sessions": 0, "tokens_total": 0, "tokens_in": 0, "tokens_out": 0, "cost": 0.0}
    with sqlite3.connect(db_path()) as conn:
        row = conn.execute("SELECT COUNT(*), COALESCE(SUM(tokens_in), 0), COALESCE(SUM(tokens_out), 0), COALESCE(SUM(cost), 0) FROM sessions").fetchone()
    return {"sessions": row[0], "tokens_total": row[1] + row[2], "tokens_in": row[1], "tokens_out": row[2], "cost": row[3]}


def cmd_analyze(args: argparse.Namespace) -> int:
    data = analyze_usage()
    print_json(envelope(True, "optimize analyze", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    task = args.task or ""
    data = choose_model(task)
    data["prompt_tip"] = "Remove duplicated context, keep exact files/errors, and ask for one output shape."
    print_json(envelope(True, "optimize suggest", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def cmd_slim(args: argparse.Namespace) -> int:
    prompt = args.prompt
    slimmed = slim_prompt(prompt)
    data = {"prompt": slimmed, "before_words": len(prompt.split()), "after_words": len(slimmed.split())}
    print_json(envelope(True, "optimize slim", data)) if args.json else print(slimmed)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize VEX token usage")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("--json", action="store_true")
    suggest = sub.add_parser("suggest")
    suggest.add_argument("--task", default="")
    suggest.add_argument("--json", action="store_true")
    slim = sub.add_parser("slim")
    slim.add_argument("prompt")
    slim.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "analyze":
        return cmd_analyze(args)
    if args.command == "suggest":
        return cmd_suggest(args)
    if args.command == "slim":
        return cmd_slim(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
