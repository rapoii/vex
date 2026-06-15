---
    name: release-workflow
    description: Coordinate release readiness, changelog, versioning, smoke tests, and rollback notes.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: workflow
      triggers: ["Cutting release", "Preparing deploy candidate", "Validating release branch"]
    ---

    # Release Workflow

    Coordinate release readiness, changelog, versioning, smoke tests, and rollback notes.

    ## When to Activate

    - Cutting release
- Preparing deploy candidate
- Validating release branch

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/release-workflow src/api` — apply workflow to specific path.
    - `/release-workflow failing checkout test` — focus on named issue.
    - `/release-workflow` — infer scope from current diff or task.

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

