---
    name: performance-audit
    description: Find bottlenecks across runtime, queries, rendering, bundles, and network paths.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Slow app", "Perf regression", "Optimization pass"]
    ---

    # Performance Audit

    Find bottlenecks across runtime, queries, rendering, bundles, and network paths.

    ## When to Activate

    - Slow app
- Perf regression
- Optimization pass

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/performance-audit src/api` — apply workflow to specific path.
    - `/performance-audit failing checkout test` — focus on named issue.
    - `/performance-audit` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `token-budget-advisor`
- `model-routing-optimizer`
- `context-window-manager`
- `bundle-optimizer`

