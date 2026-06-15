---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# Typescript Patterns

> Extends `rules/common/development-workflow.md` with typescript patterns.

## Preferred Patterns

- Prefer discriminated unions, schema validation at boundaries, async/await with handled errors, and shared types only where ownership is clear.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
