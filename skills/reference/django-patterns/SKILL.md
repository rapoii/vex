---
    name: django-patterns
    description: Build Django apps with service boundaries, ORM discipline, migrations, DRF, and security defaults.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: reference
      triggers: ["Django models/views", "DRF APIs", "Migrations or settings"]
    ---

    # Django Patterns

    Build Django apps with service boundaries, ORM discipline, migrations, DRF, and security defaults.

    ## When to Activate

    - Django models/views
- DRF APIs
- Migrations or settings

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/django-patterns src/api` — apply workflow to specific path.
    - `/django-patterns failing checkout test` — focus on named issue.
    - `/django-patterns` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `react-patterns`
- `vue-patterns`
- `fastapi-patterns`
- `docker-patterns`

