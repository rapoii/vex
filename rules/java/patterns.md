---
paths:
  - "**/*.java"
---
# Java Patterns

> Extends `rules/common/development-workflow.md` with java patterns.

## Preferred Patterns

- Prefer controller-service-repository boundaries, DTO mapping at edges, Bean Validation, and integration tests for persistence.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
