---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.tsx"
  - "**/*.jsx"
---
# Web Patterns

> Extends `rules/common/development-workflow.md` with web patterns.

## Preferred Patterns

- Prefer progressive enhancement, CSS custom properties, responsive container queries, image dimensions, and CSP-aware third-party usage.
- Reuse established libraries and local conventions before custom infrastructure.
- Keep boundaries clear between UI, domain logic, IO, and persistence.
- Add tests at the level where behavior can fail.
