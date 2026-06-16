import datetime
import json
import sys
from pathlib import Path
from typing import Any

LOG_PATH = Path.home() / ".claude" / "vex-tool-usage.jsonl"


def read_payload() -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def first_value(payload: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in payload:
            return payload[name]
    return None


def success_value(payload: dict[str, Any]) -> bool:
    value = first_value(payload, ("success", "ok"))
    if isinstance(value, bool):
        return value
    if payload.get("error") or payload.get("exception"):
        return False
    result = payload.get("result") or payload.get("tool_response") or payload.get("response")
    if isinstance(result, dict):
        if isinstance(result.get("success"), bool):
            return bool(result["success"])
        if result.get("error"):
            return False
    return True


def duration_value(payload: dict[str, Any]) -> int | float | None:
    value = first_value(payload, ("duration", "duration_ms", "elapsed_ms", "tool_duration_ms"))
    return value if isinstance(value, int | float) else None


def tool_value(payload: dict[str, Any]) -> str:
    value = first_value(payload, ("tool_name", "tool", "name"))
    return str(value) if value else "unknown"


def main() -> int:
    payload = read_payload()
    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool": tool_value(payload),
        "duration": duration_value(payload),
        "success": success_value(payload),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
