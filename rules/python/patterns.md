---
paths:
  - "**/*.py"
---
# Python Patterns

> Extends `rules/common/development-workflow.md` with python patterns.

## Preferred Patterns

- Prefer repository/service seams for IO-heavy code, pytest fixtures, dependency injection by parameters, and package modules by feature.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
