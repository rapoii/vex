#!/usr/bin/env python3
"""VEX Session Start Hook — records session start metadata."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    session = {
        "event": "session_start",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": os.environ.get("VEX_PROJECT", os.getcwd()),
        "model": os.environ.get("VEX_MODEL", "unknown"),
        "pid": os.getpid(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
    }

    log_dir = Path.home() / ".claude"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "vex-sessions.jsonl"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(session) + "\n")

    print(json.dumps({"status": "ok", "session": session}))

if __name__ == "__main__":
    main()
