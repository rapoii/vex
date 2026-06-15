---
    name: bug-fix-flow
    description: Reproduce, isolate, patch, and verify defects without speculative rewrites.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["Failing test or user-reported defect", "Production regression", "Unclear runtime error"]
    ---

    # Bug Fix Flow

    Reproduce, isolate, patch, and verify defects without speculative rewrites.

    ## When to Activate

    - Failing test or user-reported defect
- Production regression
- Unclear runtime error

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/bug-fix-flow src/api` — apply workflow to specific path.
    - `/bug-fix-flow failing checkout test` — focus on named issue.
    - `/bug-fix-flow` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `tdd-workflow`
- `code-review-flow`
- `feature-development`
- `pr-workflow`

