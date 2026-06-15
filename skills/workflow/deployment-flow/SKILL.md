---
    name: deployment-flow
    description: Ship changes with environment checks, smoke tests, observability, and rollback criteria.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["Deploy request", "Post-deploy validation", "Infra/app rollout"]
    ---

    # Deployment Flow

    Ship changes with environment checks, smoke tests, observability, and rollback criteria.

    ## When to Activate

    - Deploy request
- Post-deploy validation
- Infra/app rollout

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/deployment-flow src/api` — apply workflow to specific path.
    - `/deployment-flow failing checkout test` — focus on named issue.
    - `/deployment-flow` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `tdd-workflow`
- `code-review-flow`
- `bug-fix-flow`
- `feature-development`

