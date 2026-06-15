---
    name: github-actions
    description: Author GitHub Actions workflows with least privilege, caching, matrix jobs, and secure secrets handling.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: automation
      triggers: [".github/workflows edits", "Action permissions", "CI matrix setup"]
    ---

    # Github Actions

    Author GitHub Actions workflows with least privilege, caching, matrix jobs, and secure secrets handling.

    ## When to Activate

    - .github/workflows edits
- Action permissions
- CI matrix setup

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/github-actions src/api` — apply workflow to specific path.
    - `/github-actions failing checkout test` — focus on named issue.
    - `/github-actions` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `ci-cd-setup`
- `docker-compose`
- `pre-commit-hooks`
- `release-automation`

