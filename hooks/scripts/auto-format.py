#!/usr/bin/env python3
"""Best-effort PostToolUse formatter hook."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


FORMATTERS = {
    ".py": ([sys.executable, "-m", "black"], "black"),
    ".js": (["prettier", "--write"], "prettier"),
    ".ts": (["prettier", "--write"], "prettier"),
    ".go": (["gofmt", "-w"], "gofmt"),
    ".rs": (["rustfmt"], "rustfmt"),
}


def file_path_from_payload(payload: dict[str, object]) -> Path | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return None
    return Path(file_path)


def formatter_available(command: str) -> bool:
    if command == "black":
        return shutil.which("black") is not None
    return shutil.which(command) is not None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        path = file_path_from_payload(payload)
        if path is None:
            return 0
        formatter = FORMATTERS.get(path.suffix.lower())
        if formatter is None:
            return 0
        command, executable = formatter
        if not formatter_available(executable):
            return 0
        subprocess.run([*command, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
