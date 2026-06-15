---
    name: tdd-workflow
    description: Drive RED/GREEN/REFACTOR loops with regression-first tests and explicit validation gates.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["New feature with clear behavior", "Bug fix needing regression coverage", "Refactor where behavior must remain stable"]
    ---

    # Tdd Workflow

    Drive RED/GREEN/REFACTOR loops with regression-first tests and explicit validation gates.

    ## When to Activate

    - New feature with clear behavior
- Bug fix needing regression coverage
- Refactor where behavior must remain stable

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/tdd-workflow src/api` — apply workflow to specific path.
    - `/tdd-workflow failing checkout test` — focus on named issue.
    - `/tdd-workflow` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `code-review-flow`
- `bug-fix-flow`
- `feature-development`
- `pr-workflow`

