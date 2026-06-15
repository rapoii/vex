---
paths:
  - "**/*.rs"
---
# Rust Coding Style

> Extends `rules/common/coding-style.md` with rust guidance.

## Requirements

- Use Result/Option deliberately, borrow instead of clone, keep unsafe isolated, and model invariants in types.
- Keep modules cohesive and testable.
- Prefer explicit names over comments.
- Validate data entering from users, files, network, or environment.
