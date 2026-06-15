---
paths:
  - "**/*.py"
  - "**/settings*.py"
  - "**/models.py"
  - "**/views.py"
---
# Django Coding Style

> Extends `rules/common/coding-style.md` with django guidance.

## Requirements

- Use thin views, service/query boundaries, safe migrations, ORM select_related/prefetch_related, and settings by environment.
- Keep modules cohesive and testable.
- Prefer explicit names over comments.
- Validate data entering from users, files, network, or environment.
