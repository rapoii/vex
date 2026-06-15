---
paths:
  - "**/*"
---
# Security

VEX baseline rule. Apply unless a language-specific rule overrides it.

## Requirements

- Never hardcode secrets.
- Use parameterized queries.
- Prevent XSS and path traversal.
- Keep error messages free of sensitive data.

## Enforcement

- Prefer repo-owned tooling.
- Keep changes minimal and reversible.
- State validation evidence before calling work complete.
