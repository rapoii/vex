---
    name: docker-compose
    description: Compose local services with health checks, named volumes, networks, and production-safe boundaries.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: automation
      triggers: ["Local dev stack", "Integration test services", "Compose debugging"]
    ---

    # Docker Compose

    Compose local services with health checks, named volumes, networks, and production-safe boundaries.

    ## When to Activate

    - Local dev stack
- Integration test services
- Compose debugging

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/docker-compose src/api` — apply workflow to specific path.
    - `/docker-compose failing checkout test` — focus on named issue.
    - `/docker-compose` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `ci-cd-setup`
- `github-actions`
- `pre-commit-hooks`
- `release-automation`

