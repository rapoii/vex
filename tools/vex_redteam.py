from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

MAX_FILE_BYTES = 2 * 1024 * 1024
SCAN_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".jinja", ".j2", ".sql", ".sh", ".ps1", ".json", ".yaml", ".yml", ".env", ".txt", ".md"}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

RULES = [
    {
        "id": "RT-SQL-001",
        "category": "SQL injection",
        "pattern": r"(?i)(execute|query|raw)\s*\([^\n]*(\+|%|\.format\(|f['\"])",
        "risk": "HIGH",
        "fix": "Use parameterized queries or ORM bind parameters.",
    },
    {
        "id": "RT-XSS-001",
        "category": "XSS",
        "pattern": r"(?i)(innerHTML\s*=|dangerouslySetInnerHTML|document\.write\()",
        "risk": "HIGH",
        "fix": "Render text with escaping or sanitize trusted HTML with an allowlist sanitizer.",
    },
    {
        "id": "RT-PATH-001",
        "category": "Path traversal",
        "pattern": r"(?i)(open|read_text|write_text|send_file|FileResponse)\s*\([^\n]*(request|input|param|args|query|filename|path)",
        "risk": "HIGH",
        "fix": "Resolve paths under an allowlisted base directory and reject paths outside it.",
    },
    {
        "id": "RT-SECRET-001",
        "category": "Hardcoded secrets",
        "pattern": r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
        "risk": "CRITICAL",
        "fix": "Remove secret, rotate credential, and load value from environment or secret manager.",
    },
    {
        "id": "RT-EVAL-001",
        "category": "Unsafe eval",
        "pattern": r"(?i)\b(eval|exec)\s*\(",
        "risk": "HIGH",
        "fix": "Replace dynamic execution with explicit parsing or allowlisted dispatch.",
    },
    {
        "id": "RT-SHELL-001",
        "category": "Command injection",
        "pattern": r"(?i)(shell\s*=\s*True|os\.system\(|subprocess\.[a-z_]+\([^\n]*(\+|f['\"]|\.format\())",
        "risk": "HIGH",
        "fix": "Pass fixed argv lists to subprocess with shell disabled.",
    },
]


def should_scan(path: Path) -> bool:
    if path.name.startswith(".vex-"):
        return False
    if path.suffix.lower() not in SCAN_EXTENSIONS and not path.name.startswith(".env"):
        return False
    try:
        return path.stat().st_size <= MAX_FILE_BYTES
    except OSError:
        return False


def iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if should_scan(target) else []
    files = []
    for path in target.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file() and should_scan(path):
            files.append(path)
    return sorted(files, key=lambda item: str(item).lower())


def red_agent_scan(path: Path, root: Path) -> list[dict]:
    findings = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [{
            "rule_id": "RT-READ-001",
            "category": "Read error",
            "file": relative_path(path, root),
            "line": 0,
            "evidence": str(exc),
            "risk": "LOW",
        }]
    compiled = [(rule, re.compile(rule["pattern"])) for rule in RULES]
    for line_number, line in enumerate(lines, 1):
        sample = line[:500]
        for rule, pattern in compiled:
            if pattern.search(sample):
                findings.append({
                    "rule_id": rule["id"],
                    "category": rule["category"],
                    "file": relative_path(path, root),
                    "line": line_number,
                    "evidence": redact(sample),
                    "risk": rule["risk"],
                })
    return findings


def blue_agent_fix(finding: dict) -> str:
    rule = next((item for item in RULES if item["id"] == finding.get("rule_id")), None)
    if rule:
        return rule["fix"]
    return "Review file access and reduce exposed attack surface."


def auditor_score(finding: dict) -> str:
    risk = str(finding.get("risk", "LOW")).upper()
    return risk if risk in SEVERITY_ORDER else "LOW"


def redact(value: str) -> str:
    patterns = [
        re.compile(r"(?i)((?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?)([^'\"\s]{8,})"),
        re.compile(r"(?i)(ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"),
    ]
    redacted = value.strip()
    for pattern in patterns:
        redacted = pattern.sub(lambda match: match.group(1) + "<redacted>" if len(match.groups()) > 1 else "<redacted>", redacted)
    return redacted[:240]


def relative_path(path: Path, root: Path) -> str:
    try:
        return os.fspath(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return os.fspath(path)


def summarize(findings: list[dict]) -> dict:
    counts = {severity: 0 for severity in SEVERITY_ORDER}
    for finding in findings:
        counts[finding["risk"]] += 1
    counts["total"] = len(findings)
    return counts


def scan(target: Path) -> dict:
    root = target.resolve() if target.is_dir() else target.resolve().parent
    findings = []
    for path in iter_files(target):
        findings.extend(red_agent_scan(path, root))
    for finding in findings:
        finding["risk"] = auditor_score(finding)
        finding["fix_suggestion"] = blue_agent_fix(finding)
    findings.sort(key=lambda item: (SEVERITY_ORDER[item["risk"]], item["file"], item["line"], item["rule_id"]))
    return {
        "tool": "vex_redteam",
        "mode": "quick",
        "target": os.fspath(target),
        "summary": summarize(findings),
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEX red/blue team analyzer")
    parser.add_argument("--target", default=".", help="File or directory to scan")
    parser.add_argument("--depth", choices=["quick"], default="quick")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = scan(Path(args.target))
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except (OSError, re.error, ValueError) as exc:
        print(json.dumps({"tool": "vex_redteam", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
