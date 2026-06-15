---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# Typescript Coding Style

> Extends `rules/common/coding-style.md` with typescript guidance.

## Requirements

- Use explicit public API types, avoid any, narrow unknown, model impossible states with unions.
- Keep modules cohesive and testable.
- Prefer explicit names over comments.
- Validate data entering from users, files, network, or environment.
