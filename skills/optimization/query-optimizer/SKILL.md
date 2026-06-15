---
    name: query-optimizer
    description: Improve database queries with indexes, plans, batching, pagination, and transaction scope.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Slow query", "N+1 issue", "Database performance"]
    ---

    # Query Optimizer

    Improve database queries with indexes, plans, batching, pagination, and transaction scope.

    ## When to Activate

    - Slow query
- N+1 issue
- Database performance

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/query-optimizer src/api` — apply workflow to specific path.
    - `/query-optimizer failing checkout test` — focus on named issue.
    - `/query-optimizer` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `token-budget-advisor`
- `model-routing-optimizer`
- `context-window-manager`
- `performance-audit`

