---
name: security-scanning
description: Run VEX AgentShield-lite security scans for agents, hooks, skills, and install scripts.
---

# Security Scanning

Use this skill before committing changes to agents, hooks, skills, installers, adapters, or lifecycle commands.

## Commands

```bash
python tools/vex_security.py scan --target all
python tools/vex_security.py scan --target agents
python tools/vex_security.py scan --target hooks
python tools/vex_security.py scan --target skills
python tools/vex_security.py scan --target all --json
python tools/vex_security.py list-rules
```

## Targets

- `agents`: agent definitions and prompt-safety patterns.
- `hooks`: hook commands, shell injection, destructive operations.
- `skills`: external URLs, prompt-injection language, unsafe references.
- `all`: agents, hooks, skills, and install lifecycle scripts.

## Severity handling

- `CRITICAL`: stop, fix before continuing.
- `HIGH`: fix before merge or release.
- `MEDIUM`: review context and fix when touching same area.
- `LOW`: informational hardening.

## Workflow

1. Run `python tools/vex_security.py scan --target all`.
2. Fix CRITICAL and HIGH findings.
3. Re-run scanner.
4. Use `security-reviewer` for hooks, installers, file operations, subprocess, secrets, or network access.

Scanner is a local AgentShield-lite guardrail. It does not replace manual security review.
