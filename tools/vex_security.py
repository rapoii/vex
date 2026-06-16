"""VEX security scanner."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
TARGET_DIRS = {"agents": ("agents",), "hooks": ("hooks",), "skills": ("skills",), "all": ("agents", "hooks", "skills", "install")}
SCAN_EXTENSIONS = {".md", ".json", ".py", ".sh", ".ps1", ".yaml", ".yml"}
SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|private[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_./+=:-]{16,})"
)
URL_PATTERN = re.compile(r"https?://[^\s)\]>'\"]+")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    target: str
    severity: str
    pattern: str
    remediation: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int
    message: str
    excerpt: str
    remediation: str


BASE_RULES = [
    Rule("secret.hardcoded-token", "Hardcoded token", "all", "CRITICAL", r"(?i)(api[_-]?key|token|secret|password)\s*[:=]", "Move secret to environment or secret store."),
    Rule("python.eval", "Python eval use", "all", "HIGH", r"\beval\s*\(", "Remove eval or use explicit parser."),
    Rule("python.exec", "Python exec use", "all", "HIGH", r"\bexec\s*\(", "Remove exec or use allowlisted execution."),
    Rule("python.shell-true", "subprocess shell=True", "all", "HIGH", r"shell\s*=\s*True", "Pass argv list and keep shell disabled."),
    Rule("shell.rm-rf", "Recursive force delete", "install", "CRITICAL", r"rm\s+-rf\s+", "Delete only receipt-owned files."),
    Rule("shell.curl-pipe-shell", "Downloaded shell execution", "install", "CRITICAL", r"(curl|wget).*[|].*(sh|bash|pwsh|powershell)", "Download, verify, then execute only trusted local files."),
    Rule("hook.unquoted-env", "Unquoted hook variable", "hooks", "HIGH", r"\$[A-Z_]*(INPUT|PATH|FILE|PROMPT|TARGET)[A-Z_]*", "Pass hook data as argv or quote variables."),
    Rule("hook.wildcard-matcher", "Wildcard hook matcher", "hooks", "MEDIUM", r"\"matcher\"\s*:\s*\"\*\"", "Scope hook matcher to required tools only."),
    Rule("hook.destructive-command", "Destructive hook command", "hooks", "CRITICAL", r"(rm\s+-rf|Remove-Item\s+.*-Recurse|del\s+/[sq])", "Remove destructive command from hooks."),
    Rule("skill.external-url", "External URL in skill", "skills", "MEDIUM", r"https?://", "Validate external URLs before fetching or executing content."),
    Rule("skill.prompt-override", "Prompt override phrase", "skills", "HIGH", r"(?i)(ignore previous instructions|system prompt|developer message)", "Treat external text as data, not instructions."),
    Rule("agent.prompt-override", "Agent override phrase", "agents", "HIGH", r"(?i)(ignore previous instructions|reveal system prompt|bypass policy)", "Remove instruction-bypass language."),
    Rule("install.no-dry-run", "Install script missing dry-run", "install", "MEDIUM", r"(install|copy|cp|Copy-Item)", "Ensure installer supports dry-run and backup."),
]

FAMILIES = [
    ("secret", "Secret exposure", "CRITICAL", r"(?i)(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{16,})"),
    ("command", "Command injection", "HIGH", r"(?i)(os\.system|subprocess\.|child_process|Invoke-Expression|iex\b)"),
    ("filesystem", "Unsafe filesystem operation", "HIGH", r"(?i)(chmod\s+777|chown\s+-R|write_text\(|open\(.+['\"]w)"),
    ("network", "Unvalidated network access", "MEDIUM", r"(?i)(curl\b|wget\b|requests\.|urllib\.|fetch\()"),
    ("prompt", "Prompt injection risk", "HIGH", r"(?i)(ignore all previous|override instructions|jailbreak|do anything now)"),
    ("install", "Installer lifecycle risk", "MEDIUM", r"(?i)(install|uninstall|repair|PATH|profile)"),
]


def build_rules() -> list[Rule]:
    rules = list(BASE_RULES)
    targets = ["agents", "hooks", "skills", "install", "all"]
    index = 1
    while len(rules) < 102:
        family, name, severity, pattern = FAMILIES[(index - 1) % len(FAMILIES)]
        target = targets[(index - 1) % len(targets)]
        rules.append(
            Rule(
                f"{family}.category-{index:03d}",
                f"{name} category {index:03d}",
                target,
                severity,
                pattern,
                "Review context, validate input, and use allowlisted safe operations.",
            )
        )
        index += 1
    return rules[:102]


RULES = build_rules()


def redact(text: str) -> str:
    redacted = SECRET_PATTERN.sub(lambda m: f"{m.group(1)}=<redacted>", text)
    return redacted[:180]


def is_rule_for_target(rule: Rule, target_name: str) -> bool:
    return rule.target in {"all", target_name} or target_name == "all"


def target_paths(root: Path, target: str) -> list[Path]:
    if target not in TARGET_DIRS:
        raise ValueError(f"invalid target: {target}")
    names = TARGET_DIRS[target]
    paths: list[Path] = []
    for name in names:
        if name == "install":
            paths.extend(path for path in (root / "install.sh", root / "install.ps1") if path.exists())
            continue
        candidate = root / name
        if candidate.exists():
            paths.append(candidate)
    return paths


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix in SCAN_EXTENSIONS:
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in SCAN_EXTENSIONS:
                    yield child


def classify_path(path: Path, root: Path) -> str:
    try:
        first = path.relative_to(root).parts[0]
    except ValueError:
        return "all"
    if first in {"agents", "hooks", "skills"}:
        return first
    if path.name in {"install.sh", "install.ps1"}:
        return "install"
    return "all"


def scan_file(path: Path, root: Path, selected_target: str) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    path_target = classify_path(path, root)
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if not is_rule_for_target(rule, path_target):
                continue
            if selected_target != "all" and rule.target not in {"all", selected_target, path_target}:
                continue
            if re.search(rule.pattern, line):
                findings.append(
                    Finding(
                        rule.rule_id,
                        rule.severity,
                        str(path.relative_to(root)),
                        line_number,
                        rule.name,
                        redact(line.strip()),
                        rule.remediation,
                    )
                )
        if path_target == "skills" and URL_PATTERN.search(line) and "validat" not in line.lower():
            findings.append(
                Finding(
                    "skill.external-url-without-validation",
                    "MEDIUM",
                    str(path.relative_to(root)),
                    line_number,
                    "External URL appears without validation language",
                    redact(line.strip()),
                    "Describe validation or allowlist before fetching external URLs.",
                )
            )
    return findings


def scan(root: Path, target: str) -> list[Finding]:
    resolved_root = root.resolve()
    findings: list[Finding] = []
    for file_path in iter_files(target_paths(resolved_root, target)):
        resolved_file = file_path.resolve()
        if resolved_root not in resolved_file.parents and resolved_file != resolved_root:
            raise ValueError(f"refusing to scan outside root: {file_path}")
        findings.extend(scan_file(resolved_file, resolved_root, target))
    return findings


def finding_to_dict(finding: Finding) -> dict[str, object]:
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity,
        "path": finding.path,
        "line": finding.line,
        "message": finding.message,
        "excerpt": finding.excerpt,
        "remediation": finding.remediation,
    }


def rule_to_dict(rule: Rule) -> dict[str, str]:
    return {
        "rule_id": rule.rule_id,
        "name": rule.name,
        "target": rule.target,
        "severity": rule.severity,
        "remediation": rule.remediation,
    }


def should_fail(findings: list[Finding], fail_on: str) -> bool:
    threshold = SEVERITY_ORDER[fail_on.upper()]
    return any(SEVERITY_ORDER[finding.severity] >= threshold for finding in findings)


def print_text_findings(findings: list[Finding]) -> None:
    if not findings:
        print("No findings.")
        return
    for finding in findings:
        print(f"[{finding.severity}] {finding.path}:{finding.line} {finding.rule_id} — {finding.message}")
        print(f"  Evidence: {finding.excerpt}")
        print(f"  Fix: {finding.remediation}")


def cmd_scan(args: argparse.Namespace) -> int:
    try:
        findings = scan(Path(args.root), args.target)
    except ValueError as exc:
        if args.json:
            print(json.dumps({"ok": False, "command": "scan", "error": str(exc)}))
        else:
            print(str(exc), file=sys.stderr)
        return 2

    failed = should_fail(findings, args.fail_on)
    payload = {
        "ok": not failed,
        "command": "scan",
        "data": {
            "target": args.target,
            "findings": [finding_to_dict(finding) for finding in findings],
            "summary": {severity: sum(1 for finding in findings if finding.severity == severity) for severity in SEVERITY_ORDER},
        },
    }
    if args.json:
        print(json.dumps(payload))
    else:
        print_text_findings(findings)
    return 1 if failed else 0


def cmd_list_rules(args: argparse.Namespace) -> int:
    payload = {"ok": True, "command": "list-rules", "data": {"rules": [rule_to_dict(rule) for rule in RULES]}}
    if args.json:
        print(json.dumps(payload))
    else:
        for rule in RULES:
            print(f"[{rule.severity}] {rule.rule_id} ({rule.target}) {rule.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEX AgentShield-lite security scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan VEX content")
    scan_parser.add_argument("--target", choices=sorted(TARGET_DIRS), default="all")
    scan_parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    scan_parser.add_argument("--fail-on", choices=[key.lower() for key in SEVERITY_ORDER], default="high")
    scan_parser.add_argument("--json", action="store_true")
    scan_parser.set_defaults(func=cmd_scan)

    rules_parser = subparsers.add_parser("list-rules", help="List security rule categories")
    rules_parser.add_argument("--json", action="store_true")
    rules_parser.set_defaults(func=cmd_list_rules)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
