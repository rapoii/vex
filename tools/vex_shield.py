from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAST_SCAN = ".vex-shield-last-scan.json"
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_LINE_CHARS = 8192
TARGETS = {
    "agents": ("agents",),
    "hooks": ("hooks",),
    "skills": ("skills",),
    "tools": ("tools",),
    "all": ("agents", "hooks", "skills", "tools"),
}
SCAN_EXTENSIONS = {".md", ".json", ".py", ".sh", ".ps1", ".yaml", ".yml", ".toml", ".txt"}
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
REDACT_PATTERNS = [
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9-]{10,})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z_-]{35})"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_-]{20,})"),
    re.compile(r"(?i)((?:api[_-]?key|token|secret|password|private[_-]?key)\s*[:=]\s*['\"]?)([^'\"\s]{8,})"),
]

RULE_DEFS = {
    "SECRETS": [
        ("SEC001", "CRITICAL", r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key material detected", "Remove key from repository, rotate it, and load from secret storage."),
        ("SEC002", "CRITICAL", r"\bAKIA[0-9A-Z]{16}\b", "AWS access key detected", "Remove key, rotate AWS credential, and use environment or IAM role."),
        ("SEC003", "CRITICAL", r"\bAIza[0-9A-Za-z_-]{35}\b", "Google API key detected", "Remove key, rotate credential, and restrict key scope."),
        ("SEC004", "CRITICAL", r"\bghp_[A-Za-z0-9_]{20,}\b", "GitHub token detected", "Remove token, revoke it, and load from secure runtime config."),
        ("SEC005", "CRITICAL", r"\bgithub_pat_[A-Za-z0-9_]{20,}\b", "GitHub fine-grained token detected", "Remove token, revoke it, and load from secure runtime config."),
        ("SEC006", "CRITICAL", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token detected", "Remove token, revoke it, and use secret storage."),
        ("SEC007", "HIGH", r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+", "Slack webhook URL detected", "Remove webhook URL, rotate it, and read from secret storage."),
        ("SEC008", "HIGH", r"https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+", "Discord webhook URL detected", "Remove webhook URL, rotate it, and read from secret storage."),
        ("SEC009", "HIGH", r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "Hardcoded password assignment", "Remove password literal and read from environment or secret store."),
        ("SEC010", "HIGH", r"(?i)\b(?:api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_./+=:-]{16,}['\"]", "Hardcoded secret-like assignment", "Remove secret literal and load it at runtime."),
        ("SEC011", "HIGH", r"(?i)[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@", "Basic-auth credential in URL", "Remove inline credentials and use authenticated client config."),
        ("SEC012", "MEDIUM", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT literal detected", "Avoid committing live tokens; use fixtures that cannot authenticate."),
        ("SEC013", "HIGH", r"(?i)\.env(?:\.local|\.prod|\.production)?", "Environment file reference", "Ensure environment files with secrets are not committed or loaded into prompts."),
        ("SEC014", "HIGH", r"(?i)AWS_SECRET_ACCESS_KEY\s*[:=]", "AWS secret access key assignment", "Remove AWS secret and rotate credential."),
        ("SEC015", "MEDIUM", r"(?i)client_secret\s*[:=]", "OAuth client secret assignment", "Read OAuth secret from secure runtime config."),
        ("SEC016", "MEDIUM", r"(?i)private[_-]?key\s*[:=]", "Private key variable assignment", "Keep private keys outside repository files."),
        ("SEC017", "MEDIUM", r"(?i)bearer\s+[A-Za-z0-9_./+=:-]{16,}", "Bearer token literal", "Remove bearer token and load from secure runtime config."),
        ("SEC018", "MEDIUM", r"(?i)authorization\s*[:=]\s*['\"]", "Authorization header literal", "Build auth headers from runtime credentials."),
        ("SEC019", "LOW", r"(?i)(sample|example|dummy).*?(password|secret|token)", "Example credential text", "Keep examples obviously fake and non-authenticating."),
        ("SEC020", "LOW", r"(?i)(password|secret|token).*?(changeme|replace_me|TODO)", "Placeholder credential", "Replace placeholders with documented environment variable names."),
    ],
    "PERMISSIONS": [
        ("PERM001", "HIGH", r"\bchmod\s+777\b", "World-writable chmod", "Use least-privilege permissions such as 600 or 755."),
        ("PERM002", "HIGH", r"\bchmod\s+-R\s+777\b", "Recursive world-writable chmod", "Avoid recursive broad permissions; scope exact paths and modes."),
        ("PERM003", "HIGH", r"(?i)icacls\s+[^\n]*Everyone:F", "Windows Everyone full-control grant", "Grant access only to required user or group."),
        ("PERM004", "MEDIUM", r"\bchmod\s+666\b", "World-writable file mode", "Use owner-writable file permissions."),
        ("PERM005", "HIGH", r"\bchown\s+-R\b", "Recursive ownership change", "Avoid recursive ownership changes; target exact files."),
        ("PERM006", "MEDIUM", r"\bsudo\b", "Privilege elevation command", "Avoid privileged commands unless explicitly required and reviewed."),
        ("PERM007", "MEDIUM", r"(?i)runas\b", "Windows privilege elevation command", "Avoid privileged commands unless explicitly required and reviewed."),
        ("PERM008", "HIGH", r"(?i)Remove-Item\s+[^\n]*-Recurse[^\n]*-Force", "Forced recursive removal", "Delete only confirmed owned files and avoid broad recursion."),
        ("PERM009", "CRITICAL", r"\brm\s+-rf\s+(?:/|~|\$HOME)\b", "Recursive deletion of root or home", "Never run destructive deletion against root or home paths."),
        ("PERM010", "MEDIUM", r"(?i)os\.chmod\([^\n]*0o?777", "World-writable chmod in Python", "Use least-privilege mode values."),
        ("PERM011", "MEDIUM", r"(?i)stat\.S_IWOTH", "World-writable permission bit", "Avoid granting write access to other users."),
        ("PERM012", "MEDIUM", r"(?i)umask\s+000", "Permissive umask", "Use restrictive umask for generated files."),
        ("PERM013", "HIGH", r"(?i)del\s+/[sq]\s+", "Recursive quiet deletion", "Avoid broad quiet deletion; target exact files."),
        ("PERM014", "LOW", r"(?i)mktemp\s+-u", "Unsafe temp-name generation", "Create temp files atomically with safe temp APIs."),
        ("PERM015", "MEDIUM", r"(?i)open\([^\n]*['\"]w", "Direct writable file open", "Validate destination path before writing files."),
        ("PERM016", "MEDIUM", r"(?i)write_text\(", "Direct file write", "Validate destination path before writing files."),
        ("PERM017", "MEDIUM", r"(?i)Path\.home\(\)", "Home directory access", "Avoid writing outside project scope unless user approved."),
    ],
    "HOOKS": [
        ("HOOK001", "HIGH", r"\beval\s*\(", "eval use in hook path", "Remove eval and parse explicit data structures."),
        ("HOOK002", "HIGH", r"\bexec\s*\(", "exec use in hook path", "Remove exec and call explicit functions."),
        ("HOOK003", "HIGH", r"shell\s*=\s*True", "subprocess shell=True", "Pass argv list and keep shell disabled."),
        ("HOOK004", "HIGH", r"(?i)Invoke-Expression|\biex\b", "PowerShell expression execution", "Avoid dynamic command evaluation."),
        ("HOOK005", "CRITICAL", r"(?i)(curl|wget)[^\n]*\|[^\n]*(sh|bash|pwsh|powershell)", "Downloaded script execution", "Download, verify, then execute trusted local files only."),
        ("HOOK006", "HIGH", r"(?i)os\.system\(", "os.system command execution", "Use safe subprocess argv calls without shell."),
        ("HOOK007", "HIGH", r"(?i)subprocess\.[A-Za-z_]+\([^\n]*\+", "Concatenated subprocess command", "Build command arguments as fixed lists."),
        ("HOOK008", "HIGH", r"(?i)command\s*[:=][^\n]*\$[A-Z_]*(INPUT|PROMPT|FILE|PATH|TARGET)", "Hook command uses unquoted input variable", "Pass hook data through stdin JSON or argv safely."),
        ("HOOK009", "MEDIUM", r"(?i)json\.load\(sys\.stdin\)[^\n]*except[^\n]*pass", "Hook ignores stdin parse errors", "Fail closed or warn when hook input cannot be parsed."),
        ("HOOK010", "HIGH", r"(?i)except\s+json\.JSONDecodeError[^\n]*(return\s+\{\}|pass)", "Malformed hook JSON allowed", "Fail closed for malformed hook JSON in security gates."),
        ("HOOK011", "MEDIUM", r"(?i)requests\.|urllib\.|httpx\.|curl\b|wget\b", "Network access in hook", "Avoid network calls in hooks unless explicitly reviewed."),
        ("HOOK012", "CRITICAL", r"(?i)(rm\s+-rf|Remove-Item\s+[^\n]*-Recurse|del\s+/[sq])", "Destructive command in hook", "Remove destructive command from hook path."),
        ("HOOK013", "MEDIUM", r"\"matcher\"\s*:\s*\"\*\"", "Wildcard hook matcher", "Scope hook matcher to required tools."),
        ("HOOK014", "HIGH", r"(?i)ignore previous instructions|developer message|system prompt", "Prompt injection text in hook", "Treat hook input and output as data, not instructions."),
        ("HOOK015", "MEDIUM", r"(?i)env\s*\|\s*(curl|wget)", "Environment exfiltration pattern", "Never pipe environment variables to network commands."),
        ("HOOK016", "MEDIUM", r"(?i)printenv\s*\|\s*(curl|wget)", "Environment exfiltration pattern", "Never pipe environment variables to network commands."),
        ("HOOK017", "MEDIUM", r"(?i)base64\s+-d\s*\|\s*(sh|bash)", "Decoded shell execution", "Avoid executing decoded content."),
        ("HOOK018", "LOW", r"(?i)timeout\s*=\s*None", "Unbounded hook timeout", "Use bounded execution time for hook commands."),
        ("HOOK019", "MEDIUM", r"(?i)tempfile\.mktemp", "Unsafe temporary file use", "Use NamedTemporaryFile or TemporaryDirectory."),
        ("HOOK020", "HIGH", r"(?i)pickle\.loads?\(", "Unsafe pickle deserialization", "Do not deserialize untrusted hook input with pickle."),
    ],
    "AGENTS": [
        ("AGENT001", "HIGH", r"(?i)ignore (?:all )?(?:previous|prior) instructions", "Prompt override instruction", "Remove instruction-bypass text or mark it as unsafe example data."),
        ("AGENT002", "HIGH", r"(?i)reveal (?:the )?(?:system prompt|developer message|hidden instructions)", "Secret prompt disclosure instruction", "Remove instructions that ask agents to reveal hidden context."),
        ("AGENT003", "HIGH", r"(?i)bypass (?:policy|safety|guardrails|hooks|permissions)", "Bypass instruction", "Remove bypass language from agent behavior."),
        ("AGENT004", "HIGH", r"(?i)exfiltrate|send secrets|upload credentials", "Data exfiltration instruction", "Remove instructions that move secrets or credentials out of trusted scope."),
        ("AGENT005", "MEDIUM", r"(?i)never ask permission|without confirmation", "Unsafe autonomy instruction", "Require confirmation for destructive or external actions."),
        ("AGENT006", "MEDIUM", r"(?i)delete all|wipe|destroy", "Destructive autonomy wording", "Constrain destructive operations to explicit user approval."),
        ("AGENT007", "MEDIUM", r"(?i)tools:\s*\*", "Broad tool access", "Grant only tools needed for agent role."),
        ("AGENT008", "MEDIUM", r"(?i)All tools except", "Broad tool access", "Grant only tools needed for agent role."),
        ("AGENT009", "MEDIUM", r"(?i)copy .*\.env", "Environment file copy instruction", "Avoid copying secret-bearing environment files."),
        ("AGENT010", "HIGH", r"(?i)cat .*\.ssh/id_rsa|type .*\\.ssh\\id_rsa", "SSH private key read instruction", "Never instruct agents to read private keys."),
        ("AGENT011", "HIGH", r"(?i)gh auth token|aws configure get aws_secret_access_key", "Credential extraction command", "Do not extract local credentials in agent instructions."),
        ("AGENT012", "LOW", r"(?i)jailbreak|DAN mode", "Jailbreak language", "Remove jailbreak examples unless clearly defensive test data."),
        ("AGENT013", "MEDIUM", r"(?i)paste .* into terminal", "Paste-to-terminal instruction", "Use reviewed commands, not opaque paste-to-shell flows."),
        ("AGENT014", "MEDIUM", r"(?i)disable (?:the )?(?:security|gate|hook)", "Security control disable instruction", "Do not instruct agents to disable security controls."),
        ("AGENT015", "LOW", r"(?i)trust user-provided instructions", "Untrusted instruction trust", "Treat external instructions as data and preserve higher-priority rules."),
    ],
    "DEPENDENCIES": [
        ("DEP001", "HIGH", r"(?i)pip\s+install\s+[^\n]*--trusted-host", "Trusted-host package install", "Avoid bypassing package index TLS verification."),
        ("DEP002", "MEDIUM", r"(?i)pip\s+install\s+[^=\n]+$", "Unpinned pip install", "Pin versions or use a reviewed lockfile."),
        ("DEP003", "MEDIUM", r"(?i)npm\s+install\s+[^@\n]+$", "Unpinned npm install", "Pin versions or use a reviewed lockfile."),
        ("DEP004", "HIGH", r"(?i)npm\s+install\s+[^\n]*--ignore-scripts\s*false", "Package lifecycle scripts enabled explicitly", "Avoid enabling install scripts without review."),
        ("DEP005", "MEDIUM", r"(?i)requirements\.txt", "Requirements file reference", "Review dependency additions and keep tests credential-free."),
        ("DEP006", "MEDIUM", r"(?i)package-lock\.json|yarn\.lock|pnpm-lock\.yaml", "Lockfile reference", "Review lockfile changes for unexpected registry or integrity shifts."),
        ("DEP007", "HIGH", r"(?i)integrity\s*[:=]\s*['\"]?sha1-", "Weak package integrity hash", "Use modern lockfile integrity metadata."),
        ("DEP008", "MEDIUM", r"(?i)registry\.npmjs\.org/.*/-/.+\.tgz", "Direct npm tarball URL", "Prefer package manager lockfiles with integrity checks."),
        ("DEP009", "MEDIUM", r"(?i)pypi\.org/packages/.+\.tar\.gz", "Direct PyPI artifact URL", "Prefer package manager lockfiles with hashes."),
        ("DEP010", "HIGH", r"(?i)setup\.py\s+install", "Legacy setup.py install", "Use reviewed build tooling and pinned dependencies."),
        ("DEP011", "HIGH", r"(?i)dependency_links", "Deprecated dependency links", "Avoid dependency links; use reviewed indexes and pinned versions."),
        ("DEP012", "MEDIUM", r"(?i)git\+https?://", "Git dependency reference", "Pin Git dependencies to immutable commit SHAs."),
        ("DEP013", "MEDIUM", r"(?i)latest", "Floating latest version", "Pin dependency versions explicitly."),
        ("DEP014", "LOW", r"(?i)leftpad|cross-env-shell|event-stream", "High-risk dependency name reference", "Review similarly named packages for typosquatting or prior compromise."),
        ("DEP015", "LOW", r"(?i)devDependency|optionalDependency", "Dependency manifest surface", "Review optional and development dependencies during package changes."),
    ],
    "SUPPLY_CHAIN": [
        ("SC001", "CRITICAL", r"(?i)(curl|wget)[^\n]*\|[^\n]*(sh|bash|pwsh|powershell)", "Curl or wget piped to shell", "Download, verify signature or checksum, then execute reviewed file."),
        ("SC002", "HIGH", r"(?i)raw\.githubusercontent\.com[^\n]*(sh|bash|ps1|py)", "Raw GitHub script execution risk", "Pin source, verify checksum, and avoid direct execution."),
        ("SC003", "HIGH", r"(?i)preinstall\s*[:=]", "preinstall lifecycle script", "Avoid package lifecycle scripts or make them auditable."),
        ("SC004", "HIGH", r"(?i)postinstall\s*[:=]", "postinstall lifecycle script", "Avoid package lifecycle scripts or make them auditable."),
        ("SC005", "MEDIUM", r"(?i)install\.sh", "Shell installer reference", "Ensure installer supports dry-run and explicit confirmation."),
        ("SC006", "MEDIUM", r"(?i)install\.ps1", "PowerShell installer reference", "Ensure installer supports dry-run and explicit confirmation."),
        ("SC007", "HIGH", r"(?i)PATH\s*=.*\$PWD|PATH\s*=.*\.:", "PATH hijack pattern", "Avoid prepending writable directories to PATH."),
        ("SC008", "HIGH", r"(?i)__import__\([^\n]*(input|payload|name)", "Dynamic import from input", "Map input to allowlisted modules only."),
        ("SC009", "HIGH", r"(?i)importlib\.import_module\([^\n]*(input|payload|name)", "Dynamic import from input", "Map input to allowlisted modules only."),
        ("SC010", "MEDIUM", r"(?i)self[-_ ]?update", "Self-update behavior", "Verify updates cryptographically and require user confirmation."),
        ("SC011", "HIGH", r"(?i)download[^\n]*(execute|run)", "Download-and-execute flow", "Separate download, verification, and execution steps."),
        ("SC012", "MEDIUM", r"(?i)checksum\s*[:=]\s*['\"]?['\"]?", "Empty checksum field", "Require non-empty checksums for downloaded artifacts."),
        ("SC013", "HIGH", r"(?i)signature\s*[:=]\s*false", "Signature verification disabled", "Require signed packages or verified checksums."),
        ("SC014", "MEDIUM", r"(?i)tar\s+.*\|\s*(sh|bash)", "Archive piped to shell", "Extract and inspect archives before executing content."),
        ("SC015", "MEDIUM", r"(?i)hook[s]?/.+\.(py|sh|ps1)", "Hook script path reference", "Review hook writes and require explicit install confirmation."),
    ],
}


def build_rules():
    rules = []
    targets = {
        "SECRETS": ("agents", "hooks", "skills", "tools"),
        "PERMISSIONS": ("hooks", "tools"),
        "HOOKS": ("hooks",),
        "AGENTS": ("agents", "skills"),
        "DEPENDENCIES": ("tools", "hooks", "skills"),
        "SUPPLY_CHAIN": ("hooks", "skills", "tools"),
    }
    for category, definitions in RULE_DEFS.items():
        for rule_id, severity, pattern, message, fix in definitions:
            rules.append({
                "rule_id": rule_id,
                "category": category,
                "severity": severity,
                "pattern": re.compile(pattern),
                "pattern_text": pattern,
                "message": message,
                "fix_suggestion": fix,
                "targets": targets[category],
            })
    if len(rules) != 102:
        raise RuntimeError(f"expected 102 rules, got {len(rules)}")
    return rules


RULES = build_rules()


def redact(text):
    value = text[:MAX_LINE_CHARS]
    for pattern in REDACT_PATTERNS:
        value = pattern.sub(lambda match: match.group(1) + "<redacted>" if len(match.groups()) > 1 else "<redacted>", value)
    return value[:240]


def summary(findings):
    data = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        data[finding["severity"]] += 1
    data["total"] = len(findings)
    return data


def category_summary():
    categories = []
    for category in RULE_DEFS:
        categories.append(category)
    return categories


def rule_for_json(rule):
    return {
        "rule_id": rule["rule_id"],
        "category": rule["category"],
        "severity": rule["severity"],
        "targets": list(rule["targets"]),
        "message": rule["message"],
        "fix_suggestion": rule["fix_suggestion"],
    }


def target_paths(root, target):
    paths = []
    for name in TARGETS[target]:
        path = (root / name).resolve()
        if path.exists():
            paths.append(path)
    return paths


def iter_files(paths, root):
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    files.append(child)
    for path in sorted(files, key=lambda item: str(item).lower()):
        resolved = path.resolve()
        if root != resolved and root not in resolved.parents:
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def classify(path, root):
    try:
        first = path.resolve().relative_to(root).parts[0]
    except ValueError:
        return "all"
    return first if first in {"agents", "hooks", "skills", "tools"} else "all"


def should_skip_line(line):
    lowered = line.lower()
    fake_words = ("example", "sample", "dummy", "placeholder", "changeme", "replace_me", "test-token", "fake")
    return any(word in lowered for word in fake_words)


def scan_file(path, root):
    category = classify(path, root)
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [{
            "severity": "LOW",
            "rule_id": "READ001",
            "file": str(path.relative_to(root)),
            "line": 0,
            "message": f"Could not read file: {exc}",
            "fix_suggestion": "Check file permissions and rerun scan.",
        }]
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line[:MAX_LINE_CHARS]
        skip_low_confidence_secret = should_skip_line(line)
        for rule in RULES:
            if category not in rule["targets"]:
                continue
            if skip_low_confidence_secret and rule["category"] == "SECRETS" and rule["severity"] != "CRITICAL":
                continue
            if rule["pattern"].search(line):
                findings.append({
                    "severity": rule["severity"],
                    "rule_id": rule["rule_id"],
                    "file": str(path.relative_to(root)),
                    "line": line_number,
                    "message": rule["message"],
                    "fix_suggestion": rule["fix_suggestion"],
                })
    return findings


def scan(root, target):
    root = root.resolve()
    findings = []
    for path in iter_files(target_paths(root, target), root):
        findings.extend(scan_file(path, root))
    return findings


def save_last_scan(root, payload):
    path = root / LAST_SCAN
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_last_scan(root):
    path = root / LAST_SCAN
    if not path.exists():
        raise FileNotFoundError(f"last scan not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("last scan file is invalid")
    return data


def scan_payload(root, target, mode):
    findings = scan(root, target)
    payload = {
        "tool": "vex_shield",
        "mode": mode,
        "target": target,
        "root": str(root.resolve()),
        "summary": summary(findings),
        "findings": findings,
    }
    save_last_scan(root.resolve(), payload)
    return payload


def command_scan(args):
    root = Path(args.root).resolve()
    payload = scan_payload(root, args.target, "scan")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_ci(args):
    root = Path(args.root).resolve()
    payload = scan_payload(root, "all", "ci")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload["summary"]["CRITICAL"] else 0


def command_rules(args):
    counts = {}
    for category in RULE_DEFS:
        counts[category] = len(RULE_DEFS[category])
    payload = {
        "tool": "vex_shield",
        "summary": {
            "total_rules": len(RULES),
            "categories": category_summary(),
            "counts": counts,
        },
        "rules": [rule_for_json(rule) for rule in RULES],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_report(args):
    try:
        payload = load_last_scan(Path(args.root).resolve())
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"vex_shield report failed: {exc}", file=sys.stderr)
        return 2
    findings = payload.get("findings", [])
    lines = ["# VEX Shield Security Report", "", f"Target: {payload.get('target', 'unknown')}", ""]
    report_summary = payload.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    for severity in SEVERITIES:
        lines.append(f"- {severity}: {report_summary.get(severity, 0)}")
    lines.append(f"- TOTAL: {report_summary.get('total', len(findings))}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if not findings:
        lines.append("No findings.")
    else:
        for finding in findings:
            rule = next((item for item in RULES if item["rule_id"] == finding.get("rule_id")), None)
            category = rule["category"] if rule else "UNKNOWN"
            lines.append(f"- [{finding.get('severity')}] {category} {finding.get('rule_id')} {finding.get('file')}:{finding.get('line')} — {finding.get('message')}")
            lines.append(f"  - Fix: {finding.get('fix_suggestion')}")
    print("\n".join(lines))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="VEX Shield standalone security auditor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan project files")
    scan_parser.add_argument("--target", choices=sorted(TARGETS), default="all")
    scan_parser.add_argument("--root", default=os.fspath(ROOT))
    scan_parser.set_defaults(func=command_scan)

    report_parser = subparsers.add_parser("report", help="Generate markdown report from last scan")
    report_parser.add_argument("--root", default=os.fspath(ROOT))
    report_parser.set_defaults(func=command_report)

    ci_parser = subparsers.add_parser("ci", help="Run CI scan; exit 1 if CRITICAL findings exist")
    ci_parser.add_argument("--root", default=os.fspath(ROOT))
    ci_parser.set_defaults(func=command_ci)

    rules_parser = subparsers.add_parser("rules", help="List all 102 security rules")
    rules_parser.set_defaults(func=command_rules)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(json.dumps({"tool": "vex_shield", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
