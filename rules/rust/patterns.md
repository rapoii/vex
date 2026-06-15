---
paths:
  - "**/*.rs"
---
# Rust Patterns

> Extends `rules/common/development-workflow.md` with rust patterns.

## Preferred Patterns

- Prefer newtypes for domain IDs, trait bounds at edges, builder only when construction is genuinely complex, and property tests for parsers.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
