---
paths:
  - "**/*.ts"
  - "**/*.html"
---
# Angular Patterns

> Extends `rules/common/development-workflow.md` with angular patterns.

## Preferred Patterns

- Prefer smart/container and presentational splits, signal inputs/outputs where supported, resolvers for route data, and harnesses for component tests.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
