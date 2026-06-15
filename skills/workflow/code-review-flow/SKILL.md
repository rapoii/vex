---
    name: code-review-flow
    description: Review diffs with severity ordering, full-file context, and actionable fixes.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["Before merge or PR", "After non-trivial code changes", "When correctness/security confidence matters"]
    ---

    # Code Review Flow

    Review diffs with severity ordering, full-file context, and actionable fixes.

    ## When to Activate

    - Before merge or PR
- After non-trivial code changes
- When correctness/security confidence matters

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/code-review-flow src/api` — apply workflow to specific path.
    - `/code-review-flow failing checkout test` — focus on named issue.
    - `/code-review-flow` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `tdd-workflow`
- `bug-fix-flow`
- `feature-development`
- `pr-workflow`

