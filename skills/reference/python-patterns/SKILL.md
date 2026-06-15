---
    name: python-patterns
    description: Use Python typing, packaging, testing, logging, and dependency patterns for production code.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: reference
      triggers: ["Python module work", "CLI/service code", "Packaging changes"]
    ---

    # Python Patterns

    Use Python typing, packaging, testing, logging, and dependency patterns for production code.

    ## When to Activate

    - Python module work
- CLI/service code
- Packaging changes

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/python-patterns src/api` — apply workflow to specific path.
    - `/python-patterns failing checkout test` — focus on named issue.
    - `/python-patterns` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `react-patterns`
- `vue-patterns`
- `django-patterns`
- `fastapi-patterns`

