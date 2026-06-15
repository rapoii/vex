---
paths:
  - "**/*.vue"
---
# Vue Patterns

> Extends `rules/common/development-workflow.md` with vue patterns.

## Preferred Patterns

- Prefer composables for reusable behavior, scoped slots for flexible rendering, route-level data loading, and watchers only for side effects.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
