---
paths:
  - "**/*.py"
  - "**/settings*.py"
  - "**/models.py"
  - "**/views.py"
---
# Django Patterns

> Extends `rules/common/development-workflow.md` with django patterns.

## Preferred Patterns

- Prefer custom QuerySets/managers for query reuse, DRF serializers for API boundaries, Celery for background work, and transaction.atomic for multi-write invariants.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
