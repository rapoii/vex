#!/usr/bin/env python3
"""VEX Session Summary Hook — generates session end summary."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    summary = {
        "event": "session_end",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": os.environ.get("VEX_PROJECT", os.getcwd()),
        "model": os.environ.get("VEX_MODEL", "unknown"),
        "pid": os.getpid(),
    }

    log_dir = Path.home() / ".claude"
    log_file = log_dir / "vex-sessions.jsonl"

    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        starts = [json.loads(l) for l in lines if '"session_start"' in l]
        if starts:
            last = starts[-1]
            start_time = datetime.fromisoformat(last["timestamp"])
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            summary["duration_seconds"] = round(duration)
            summary["started_at"] = last["timestamp"]

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary) + "\n")

    print(json.dumps({"status": "ok", "summary": summary}))

if __name__ == "__main__":
    main()
