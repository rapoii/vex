#!/usr/bin/env python3
"""Block prompts that appear to contain secrets."""

from __future__ import annotations

import json
import re
import sys


PATTERNS = [
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bghp_[A-Za-z0-9_]{36,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Slack bot token", re.compile(r"\bxoxb-[A-Za-z0-9-]{20,}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("password assignment", re.compile(r"(?i)\b(password|passwd|pwd)\s*=\s*['\"][^'\"\s]{8,}['\"]")),
]


def extract_prompt(payload: dict[str, object]) -> str:
    for key in ("prompt", "message", "input"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    prompt = extract_prompt(payload)
    found = [name for name, pattern in PATTERNS if pattern.search(prompt)]
    if found:
        print(f"Secret scanner blocked prompt: possible {', '.join(found)} detected.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
