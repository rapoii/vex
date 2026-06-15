---
    name: migration-workflow
    description: Plan safe migrations with compatibility windows, backfills, verification, and rollback.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["Schema migration", "Framework upgrade", "Breaking config change"]
    ---

    # Migration Workflow

    Plan safe migrations with compatibility windows, backfills, verification, and rollback.

    ## When to Activate

    - Schema migration
- Framework upgrade
- Breaking config change

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/migration-workflow src/api` — apply workflow to specific path.
    - `/migration-workflow failing checkout test` — focus on named issue.
    - `/migration-workflow` — infer scope from current diff or task.

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

