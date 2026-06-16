import json
import os
import sys
from pathlib import Path

MAX_BYTES = 1_048_576


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def content_size(payload: dict) -> int:
    content = payload.get("tool_input", {}).get("content", "")
    if not isinstance(content, str):
        return 0
    return len(content.encode("utf-8"))


def file_path(payload: dict) -> Path | None:
    path = payload.get("tool_input", {}).get("file_path", "")
    if not isinstance(path, str) or not path:
        return None
    return Path(path)


def main() -> int:
    payload = read_payload()
    path = file_path(payload)

    if path and path.exists():
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        if size > MAX_BYTES:
            print(f"[VEX] BLOCKED: {path} is {size} bytes, over 1MB limit", file=sys.stderr)
            return 1

    size = content_size(payload)
    if size > MAX_BYTES:
        display_path = path if path else "<stdin content>"
        print(f"[VEX] BLOCKED: {display_path} content is {size} bytes, over 1MB limit", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
