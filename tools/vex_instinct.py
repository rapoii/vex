"""Learn reusable VEX instincts from recorded sessions."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def vex_home() -> Path:
    return Path(os.environ.get("VEX_HOME", Path.home() / ".claude")).expanduser()


def db_path() -> Path:
    return vex_home() / "vex-sessions.db"


def instincts_path() -> Path:
    return vex_home() / "vex-instincts.json"


def envelope(ok: bool, command: str, data: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
    return {"ok": ok, "command": command, "data": data, "error": error}


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def load_instincts() -> list[dict[str, Any]]:
    path = instincts_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("instincts", []))


def save_instincts(instincts: list[dict[str, Any]]) -> None:
    path = instincts_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"instincts": instincts}, indent=2, sort_keys=True), encoding="utf-8")


def load_tool_sequences() -> list[list[str]]:
    if not db_path().exists():
        return []
    with sqlite3.connect(db_path()) as conn:
        rows = conn.execute("SELECT session_id, tool, success FROM events WHERE tool IS NOT NULL ORDER BY session_id, timestamp, id").fetchall()
    by_session: dict[str, list[str]] = {}
    for session_id, tool, success in rows:
        if success:
            by_session.setdefault(str(session_id), []).append(str(tool))
    return list(by_session.values())


def extract_instincts() -> list[dict[str, Any]]:
    sequences = load_tool_sequences()
    counts: Counter[tuple[str, ...]] = Counter()
    for sequence in sequences:
        for index in range(max(0, len(sequence) - 2)):
            counts[tuple(sequence[index : index + 3])] += 1
        if len(sequence) and len(sequence) < 3:
            counts[tuple(sequence)] += 1

    instincts = []
    for pattern, count in counts.most_common():
        if count < 1:
            continue
        title = " -> ".join(pattern)
        confidence = min(0.95, 0.55 + (count * 0.2))
        instincts.append(
            {
                "id": f"tool-{slug(title)}",
                "kind": "tool_sequence",
                "title": f"Use {title} workflow",
                "confidence": round(confidence, 2),
                "rule": f"When context matches, consider workflow: {title}.",
                "evidence": {"frequency": count, "sessions_scanned": len(sequences)},
            }
        )
    return instincts


def cmd_learn(args: argparse.Namespace) -> int:
    existing = {item["id"]: item for item in load_instincts()}
    learned = extract_instincts()
    merged = {**existing, **{item["id"]: item for item in learned}}
    instincts = sorted(merged.values(), key=lambda item: item.get("confidence", 0), reverse=True)
    save_instincts(instincts)
    data = {"learned": len(learned), "instincts": learned}
    print_json(envelope(True, "instinct learn", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    instincts = load_instincts()
    data = {"instincts": instincts}
    print_json(envelope(True, "instinct list", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def cmd_forget(args: argparse.Namespace) -> int:
    instincts = [item for item in load_instincts() if item.get("id") != args.instinct]
    save_instincts(instincts)
    print_json(envelope(True, "instinct forget", {"forgotten": args.instinct})) if args.json else print(f"Forgot {args.instinct}")
    return 0


def safe_rule_filename(instinct_id: str) -> str:
    clean = slug(instinct_id)
    if not clean:
        raise ValueError("invalid instinct id")
    return f"{clean}.md"


def cmd_apply(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    applied = 0
    for instinct in load_instincts():
        if float(instinct.get("confidence", 0)) < args.min_confidence:
            continue
        target = output_dir / safe_rule_filename(str(instinct["id"]))
        target.write_text(
            f"---\nname: {instinct['id']}\ndescription: Learned VEX instinct with confidence {instinct['confidence']}\nmetadata:\n  type: generated-instinct\n---\n\n{instinct['rule']}\n",
            encoding="utf-8",
        )
        applied += 1
    data = {"applied": applied, "output_dir": str(output_dir)}
    print_json(envelope(True, "instinct apply", data)) if args.json else print(json.dumps(data, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Learn reusable VEX instincts")
    sub = parser.add_subparsers(dest="command", required=True)
    learn = sub.add_parser("learn")
    learn.add_argument("--json", action="store_true")
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true")
    apply = sub.add_parser("apply")
    apply.add_argument("--json", action="store_true")
    apply.add_argument("--min-confidence", type=float, default=0.8)
    apply.add_argument("--output-dir", default=str(REPO_ROOT / "rules" / "generated-instincts"))
    forget = sub.add_parser("forget")
    forget.add_argument("instinct")
    forget.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "learn":
        return cmd_learn(args)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "apply":
        return cmd_apply(args)
    if args.command == "forget":
        return cmd_forget(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
