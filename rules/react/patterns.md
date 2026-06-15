---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---
# React Patterns

> Extends `rules/common/development-workflow.md` with react patterns.

## Preferred Patterns

- Prefer compound components for shared UI state, hooks for reusable behavior, React Query/SWR for server state, and URL state for shareable filters.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
