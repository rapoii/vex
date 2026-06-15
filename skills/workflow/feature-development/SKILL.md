---
    name: feature-development
    description: Plan, test, build, review, and verify feature work end to end.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["New user-facing capability", "Multi-file implementation", "Feature with API/UI/test impact"]
    ---

    # Feature Development

    Plan, test, build, review, and verify feature work end to end.

    ## When to Activate

    - New user-facing capability
- Multi-file implementation
- Feature with API/UI/test impact

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/feature-development src/api` — apply workflow to specific path.
    - `/feature-development failing checkout test` — focus on named issue.
    - `/feature-development` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `tdd-workflow`
- `code-review-flow`
- `bug-fix-flow`
- `pr-workflow`

