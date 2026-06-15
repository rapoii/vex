---
paths:
  - "**/*"
---
# Code Review

VEX baseline rule. Apply unless a language-specific rule overrides it.

## Requirements

- Review full files, not only hunks.
- Sort findings by CRITICAL, HIGH, MEDIUM, LOW.
- Include file:line, impact, and fix.
- Block on critical security/data-loss issues.

## Enforcement

- Prefer repo-owned tooling.
- Keep changes minimal and reversible.
- State validation evidence before calling work complete.
