---
paths:
  - "**/*.go"
---
# Golang Patterns

> Extends `rules/common/development-workflow.md` with golang patterns.

## Preferred Patterns

- Prefer package-level cohesion, interface adapters, errgroup for bounded concurrency, and explicit cancellation.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
