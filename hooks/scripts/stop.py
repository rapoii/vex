import datetime
import json
import sys
from pathlib import Path
from typing import Any

CLAUDE_DIR = Path.home() / ".claude"
TOOL_LOG_PATH = CLAUDE_DIR / "vex-tool-usage.jsonl"
SUMMARY_PATH = CLAUDE_DIR / "vex-session-summary.json"
FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def read_payload() -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_tool_log() -> list[dict[str, Any]]:
    if not TOOL_LOG_PATH.exists():
        return []

    records: list[dict[str, Any]] = []
    with TOOL_LOG_PATH.open("r", encoding="utf-8", errors="replace") as file:
        for line in file:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def parse_timestamp(value: Any) -> datetime.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=datetime.timezone.utc)


def changed_files(payload: dict[str, Any], records: list[dict[str, Any]]) -> list[str]:
    files: set[str] = set()
    for key in ("files_changed", "changed_files"):
        value = payload.get(key)
        if isinstance(value, list):
            files.update(str(item) for item in value if item)

    for record in records:
        if record.get("tool") not in FILE_TOOLS:
            continue
        path = record.get("file_path") or record.get("path")
        if path:
            files.add(str(path))
    return sorted(files)


def duration_seconds(payload: dict[str, Any], records: list[dict[str, Any]]) -> float | None:
    raw = payload.get("duration") or payload.get("duration_seconds")
    if isinstance(raw, int | float):
        return float(raw)

    timestamps = [parsed for record in records if (parsed := parse_timestamp(record.get("timestamp")))]
    if len(timestamps) < 2:
        return None
    return (max(timestamps) - min(timestamps)).total_seconds()


def main() -> int:
    payload = read_payload()
    records = read_tool_log()
    tools: dict[str, int] = {}
    for record in records:
        tool = str(record.get("tool", "unknown"))
        tools[tool] = tools.get(tool, 0) + 1

    summary = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "duration": duration_seconds(payload, records),
        "tools_used": tools,
        "files_changed": changed_files(payload, records),
    }

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
